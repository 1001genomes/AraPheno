"""
Some general IO related functions
"""
import os
import tempfile
import uuid
import zipfile
import numpy as np

from django.db import transaction
from phenotypedb.models import (Accession, ObservationUnit, Phenotype,
                                PhenotypeValue, Species, Study, Submission)
from utils.data_io import parse_plink_file
from utils.isa_tab import parse_isatab, save_isatab


def import_study(fhandle):
    """
    Imports a study into the database using a file handle or filename
    """
    name, extension = os.path.splitext(fhandle.name)
    if extension in ('.zip', '.tar.gz'):
        study = import_isatab(fhandle)
    elif extension in ('.plink', '.csv'):
        study = import_plink(fhandle, name)
    else:
        raise Exception('Extension %s not supported' % extension)
    return study




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
    return save_plink(plink_data, name)


@transaction.atomic
def save_plink(plink_data, name):
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
