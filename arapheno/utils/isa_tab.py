import logging
import os
import zipfile
import tempfile
import csv
import shutil
import codecs
import pdb
from phenotypedb.models import Study,Phenotype,PhenotypeValue,Publication, Accession, Species, Author, ObservationUnit
from django.db import transaction

logger = logging.getLogger(__name__)

def parse_isatab(filename):
    """Parses either an isa-tab zip or folder"""
    
    from bcbio import isatab

    # check if filename is a folder or a zip
    if not os.path.exists(filename):
        raise Exception('File or folder %s does not exist',filename)
    
    if not os.path.isdir(filename):
        work_dir = tempfile.mkdtemp()
        # unzip to temporary folder
        with zipfile.ZipFile(filename, "r") as z:
            z.extractall(work_dir)
    else:
        work_dir = filename    
    
    # parse
    rec = isatab.parse(work_dir)
    # parse trait def file and raw data file
    for s in rec.studies:
        s.trait_def_map = {}
        s.derived_data_map = {}
        for assay in s.assays:
            if (assay.metadata['Study Assay Measurement Type Term Accession Number'] != '23'):
                continue
            for sample_id,assay_data in assay.nodes.items():
                derived_data_file = assay_data.metadata['Derived Data File'][0]
                trait_def_file = assay_data.metadata['Parameter Value[Trait Definition File]'][0].Trait_Definition_File
                
                # check if we already loaded the trait def file
                if trait_def_file not in s.trait_def_map:
                    s.trait_def_map[trait_def_file] = _parse_trait_def_file(trait_def_file,work_dir)
                
                # check if we already loaded the derived data matrix
                if derived_data_file not in s.derived_data_map:
                    s.derived_data_map[derived_data_file] = _parse_derived_data_file(derived_data_file,work_dir)
    # remove temporary folder
    
    if filename != work_dir:
        shutil.rmtree(work_dir)
    return rec


def _create_publication(isatab_pub):
    publication = Publication()
    publication.doi = isatab_pub['Study Publication DOI']
    publication.title = isatab_pub['Study Publication Title']
    publication.author_order = isatab_pub['Study Publication Author List']
    publication.pubmed_id = isatab_pub['Study PubMed ID']
    return publication

def _get_accession_map(study):
    pass


def _parse_trait_def_file(trait_def_file,work_dir):
    trait_def_map = {}

    with codecs.open(os.path.join(work_dir,trait_def_file),'rb','utf-16') as f:
        reader = csv.reader(f,dialect="excel-tab")
        header = next(reader)
        method_ix = header.index('Method')
        trait_ix = header.index('Trait')
        eo_ix, to_ix, uo_ix  = [-1,-1,-1]
        for row in reader:
            if eo_ix == -1:
                try:
                    eo_ix = row.index('EO')
                except ValueError:
                    pass
            if to_ix == -1:
                try:
                    to_ix = row.index('TO')
                except ValueError:
                    pass
            if uo_ix == -1:
                try:
                    uo_ix = row.index('UO')
                except ValueError:
                    pass    
            tr = {'Trait':row[trait_ix],'Method':row[method_ix],'EO':None,'TO':None,'UO':None}
            if (eo_ix > 0): tr['EO'] = row[eo_ix+1]
            if (to_ix > 0): tr['TO'] = row[to_ix+1]
            if (uo_ix > 0): tr['UO'] = row[uo_ix+1]
            trait_def_map[row[0]] = tr 
    return trait_def_map

def _get_index_for_term(row,term):
    return row.index(term)

def _parse_derived_data_file(derived_data_file,work_dir):
    derived_data_map = {}
    with codecs.open(os.path.join(work_dir,derived_data_file),'rb','utf-16') as f:
        reader = csv.DictReader(f,dialect="excel-tab")
        for row in reader:
            assay_name = row['Assay Name']
            del row['Assay Name']
            derived_data_map[assay_name] = row
    return derived_data_map


@transaction.atomic
def save_isatab(isatab):
    """Converts isatab to db objects"""
    studies = []
    for s in isatab.studies:
        # Initialize Publication
        study = Study()
        study.name = s.metadata['Study Title']
        study.description = s.design_descriptors[0]['Study Design Type']
        study.species = Species.objects.get(pk=1)
        studies.append(study.save())
        # initialize publications
        pubs = {}
        for p in s.publications:
            doi_to_check = p['Study Publication DOI']
            publication = pubs.get(doi_to_check,None)
            if publication is None:
                try:
                    publication = Publication.objects.get(doi=doi_to_check)
                except Publication.DoesNotExist:
                    publication = _create_publication(p)
                    publication.save();
                pubs[doi_to_check] = publication
            study.publications.add(publication)
        accession_map = s.nodes
        obs_map = {}
        phenotype_map  = {}
        # create the phenotype map
        for trait_def_file,trait_def_data in s.trait_def_map.items():
            pheno_map = {}
            for trait_id,trait in trait_def_data.items():
                phenotype = Phenotype(name=trait['Trait'],scoring=trait['Method'],to_term = trait.get('TO',None),eo_term=trait.get('EO',None),uo_term=trait.get('UO',None),study=study,species=study.species)
                phenotype.save()
                pheno_map[trait_id] = phenotype
            phenotype_map[trait_def_file] = pheno_map 
        for sample_id,sample in s.nodes.items():
            # avoid duplicates because nodes will also contain source- entries 
            if not sample_id.startswith('sample-'):
                continue
            accession_id = int(sample.metadata['Characteristics[Infraspecific name]'][0].Term_Accession_Number)
            obs_unit = ObservationUnit(study=study,accession=Accession.objects.get(pk=accession_id))
            obs_unit.save()
            obs_map[sample_id] = obs_unit 
        for a in s.assays:
            # ignore if it's not a phenotyping assay
            if (a.metadata['Study Assay Measurement Type Term Accession Number'] != '23'):
                continue            
            for sample_id,assay_data in a.nodes.items():
                # will contain additional nodes unrelated to samples
                if not sample_id.startswith('sample-'):
                    continue
                derived_data_file = assay_data.metadata['Derived Data File'][0]
                trait_def_file = assay_data.metadata['Parameter Value[Trait Definition File]'][0].Trait_Definition_File
                assay_id = assay_data.metadata['Assay Name'][0].Assay_Name
                phen_row = {k:float(v) for k,v in s.derived_data_map[derived_data_file][assay_id].iteritems() if v != ''}
                obs_unit = obs_map[sample_id]
                for phenotype_id, value in phen_row.iteritems():
                    phenotype = phenotype_map[trait_def_file][phenotype_id]
                    phenotype_value = PhenotypeValue(value=value,phenotype=phenotype,obs_unit = obs_unit)
                    phenotype_value.save()
    return studies
