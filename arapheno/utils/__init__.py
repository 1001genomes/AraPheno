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

from django.db import transaction
from phenotypedb.models import (Accession, ObservationUnit, Phenotype,
                                PhenotypeValue, Species, Study, Submission)
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


def calculate_phenotype_transformations(phenotype, trans = None):
    """
    Calculates transformations for the phenotype
    """
    labels = []
    accessions = []
    values = []
    for item in phenotype.phenotypevalue_set.all():
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
            sp_pval = statistics.calculate_sp_pval(transformed_values.tolist())
            transformations[transformation] = {'values': zip(labels, transformed_values.tolist()), 'sp_pval': sp_pval}
            if sp_pval < 1 and sp_pval > 0:
                transformations[transformation]['sp_score'] = -math.log10(sp_pval)
    data['transformations'] = transformations
    return data
