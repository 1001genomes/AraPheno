"""
Some general IO related functions
"""
import os
import tempfile
import uuid
import logging
import zipfile
import numpy as np
import math
import requests

from django.db import transaction
from django.http import HttpResponseNotFound
from phenotypedb.models import (Accession, ObservationUnit, Phenotype,
                                PhenotypeValue, Species, Study, Submission, Publication)
from utils.data_io import parse_plink_file, parse_csv_file, parse_meta_information_file
from utils.isa_tab import parse_isatab, save_isatab
from utils import statistics
logger = logging.getLogger(__name__)



def import_study(fhandle):
    """
    Imports a study into the database using a file handle or filename
    """
    name, extension = os.path.splitext(fhandle.name)
    if extension in ('.zip', '.tar.gz'):
        study = import_isatab(fhandle)
    elif extension in ('.plink'):
        study = import_plink(fhandle, name)
    elif extension in ( '.csv'):
        study = import_csv(fhandle, name)
    else:
        raise Exception('Extension %s not supported' % extension)
    return study

def add_phenotype_ids(study, meta_information):
    """Add the phenotype ids to the meta-information list"""
    failed_phenotypes = []
    for phenotype_name, meta_info in meta_information.items():
        try:
            phenotype = study.phenotype_set.all().get(name=phenotype_name)
            meta_info['id'] =  phenotype.id
        except (Phenotype.DoesNotExist , Phenotype.MultipleObjectsReturned):
            failed_phenotypes.append(phenotype_name)
    return meta_information, failed_phenotypes


@transaction.atomic
def update_study(submission_id, fhandle):
    """
    Updates the meta information of the study
    """
    submission = Submission.objects.get(pk=submission_id)
    if submission.status == 2:
        raise Exception('Published submission can not be updated')
    study = submission.study
    meta_information = parse_meta_information_file(fhandle)
    meta_information, failed_phenotypes = add_phenotype_ids(study, meta_information)
    failed_phenotypes = []
    for phenotype_name, meta_info in meta_information.items():
        if 'id' in meta_info:
            phenotype = study.phenotype_set.all().get(pk=meta_info['id'])
            for key in ('Scoring', 'eo_term_id', 'to_term_id', 'uo_term_id', 'Type', 'growth_conditions'):
                if key in meta_info:
                    setattr(phenotype, key.lower(), meta_info[key])
            phenotype.save()
    if len(failed_phenotypes) > 0:
        logger.warn("%s phenotypes not found: %s", len(failed_phenotypes),','.join(failed_phenotypes))
    return failed_phenotypes



def import_isatab(fhandle):
    """
    Imports an ISA-TAB archive into the database using a file handle or filename
    """
    work_dir = tempfile.mkdtemp()
    # unzip to temporary folder
    with zipfile.ZipFile(fhandle, "r") as zhandle:
        zhandle.extractall(work_dir)
    isatab = parse_isatab(work_dir)
    if len(isatab.studies) > 1:
        raise Exception('Only 1 study per submission supported. ISA-TAB archive contains %s studies' % len(isatab.studies))
    studies = save_isatab(isatab)
    return studies[0]

def import_plink(fhandle, name):
    """
    Imports a PLINK file into the database using a file handle or filename
    """
    plink_data = parse_plink_file(fhandle)
    return save_plink_or_csv(plink_data, name)

def import_csv(fhandle, name):
    """
    Imports a CSV file into the database using a file handle or filename
    """
    csv_data = parse_csv_file(fhandle)
    return save_plink_or_csv(csv_data, name)


@transaction.atomic
def save_plink_or_csv(plink_data, name):
    """
    Saves the parsed plink data in a database
    """
    # TODO don't harcode species
    pmatrix, accession_ids, names = plink_data
    study = Study(name=name, species=Species.objects.get(pk=1))
    study.save()
    phenotypes = []
    for name in names:
        phenotype = Phenotype(name=name, scoring='', study=study, species=study.species)
        phenotype.save()
        phenotypes.append(phenotype)

    for acc_ix, accession_id in enumerate(accession_ids):
        try:
            obs_unit = ObservationUnit(study=study, accession=Accession.objects.get(pk=accession_id))
        except Accession.DoesNotExist as err:
            err.args += (accession_id,)
            raise err
        obs_unit.save()
        for i, name in enumerate(names):
            value = pmatrix[acc_ix][i]
            if not np.isnan(value):
                phenotype_value = PhenotypeValue(value=value, phenotype=phenotypes[i], obs_unit=obs_unit)
                phenotype_value.save()
    return study


def calculate_phenotype_transformations(phenotype, trans = None, rnaseq=False):
    """
    Calculates transformations for the phenotype
    """
    labels = []
    accessions = []
    values = []
    if rnaseq:
        iterator = phenotype.rnaseqvalue_set.all()
    else:
        iterator = phenotype.phenotypevalue_set.all()
    for item in iterator:
        accessions.append((item.obs_unit.accession.id, item.obs_unit.accession.name))
        labels.append("%s(%s)" % (item.obs_unit.accession.name, item.id))
        values.append(item.value)
    data = {'accessions': accessions}
    transformations = {}
    for transformation in statistics.SUPPORTED_TRANSFORMATIONS:
        if trans and trans != transformation:
            continue
        transformed_values = statistics.transform(values, transformation)
        if transformed_values is not None:
            if not np.any(np.iscomplex(transformed_values)):
                sp_pval = statistics.calculate_sp_pval(transformed_values.tolist())
                transformations[transformation] = {'values': zip(labels, transformed_values.tolist()), 'sp_pval': sp_pval}
                if sp_pval < 1 and sp_pval > 0:
                    transformations[transformation]['sp_score'] = -math.log10(sp_pval)
            else:
                transformations[transformation] = {'values': [], 'sp_pval':"not supported" }
    data['transformations'] = transformations
    return data


def remove_publication_from_study(study_id, doi):
    """
    Removes a publication from a study
    """
    publication = Publication.objects.get(doi=doi)
    study = Study.objects.get(pk=study_id)
    study.publications.remove(publication)

def add_publication_to_study(study, doi):
    """
    Adds a publication from a study
    """
    doi_data = _retrieve_publication_from_doi(doi)
    pub, created = Publication.objects.get_or_create(doi=doi)
    if created or pub.title == '':
        pub.volume = doi_data.get('volume',None)
        pub.pages = doi_data.get('page', None)
        pub.title = doi_data['title']
        pub.journal = doi_data['container-title']
        pub.pub_year = doi_data['issued']['date-parts'][0][0]
        pub.author_order = ', '.join([item.get('name', '%s %s' % (item.get('given',''), item.get('family',''))) for item in doi_data['author']])
        pub.save()
    study.publications.add(pub)

def _retrieve_publication_from_doi(doi):
    response = requests.get('https://doi.org/%s' % doi,
                            headers={'Accept': 'application/vnd.citationstyles.csl+json;q=1.0'})
    if response.status_code != 200:
        raise Exception('Publication with %s not found' % doi)
    return response.json()
