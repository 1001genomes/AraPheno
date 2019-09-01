import logging
import os
import zipfile
import tempfile
import csv
import shutil
import codecs
from phenotypedb.models import Study,Phenotype,PhenotypeValue,Publication, Accession, Species, Author, ObservationUnit, OntologyTerm
from django.db import transaction
import datetime
import codecs

from phenotypedb.renderer import IsaTabStudyRenderer, IsaTabAssayRenderer,IsaTabDerivedDataFileRenderer,IsaTabTraitDefinitionRenderer

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
            if (assay.metadata['Study Assay Measurement Type Term Accession Number'] not in ('23','0000023')):
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


def _create_publication(isatab_pub,type):
    publication = Publication()
    publication.doi = isatab_pub['%s Publication DOI' % type]
    publication.title = isatab_pub['%s Publication Title' % type]
    publication.author_order = isatab_pub['%s Publication Author List' %type]
    publication.pubmed_id = isatab_pub['%s PubMed ID' % type]
    return publication

def _get_accession_map(study):
    pass


def _parse_trait_def_file(trait_def_file,work_dir):
    trait_def_map = {}

    with codecs.open(os.path.join(work_dir,trait_def_file),'rb','utf-8') as f:
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
    with codecs.open(os.path.join(work_dir,derived_data_file),'rb','utf-8') as f:
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
        if len(s.design_descriptors) > 0:
            study.description = s.design_descriptors[0]['Study Design Type']
        study.species = Species.objects.get(pk=1)
        study.save()
        studies.append(study)
        # initialize publications
        pubs = {}
        for p in isatab.publications + s.publications:
            type = 'Investigation'
            if 'Study Publication DOI' in p:
                type = 'Study'
            doi_to_check = p['%s Publication DOI' % type]
            publication = pubs.get(doi_to_check,None)
            if publication is None:
                try:
                    publication = Publication.objects.get(doi=doi_to_check)
                except Publication.DoesNotExist:
                    publication = _create_publication(p,type)
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
                to_term = None
                eo_term = None
                uo_term = None
                if 'TO' in trait:
                    to_term = OntologyTerm.objects.filter(id=trait['TO'],source_id=1).first()
                if 'EO' in trait:
                    eo_term = OntologyTerm.objects.filter(id=trait['EO'],source_id=2).first()
                if 'UO' in trait:
                    uo_term = OntologyTerm.objects.filter(id=trait['UO'],source_id=3).first()
                phenotype = Phenotype(name=trait['Trait'],scoring=trait['Method'],to_term = to_term,eo_term=eo_term,uo_term=uo_term,study=study,species=study.species)
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
            if (a.metadata['Study Assay Measurement Type Term Accession Number'] not in ('23','0000023')):
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



def export_isatab(study):
    # create temorary folder
    folder = tempfile.mkdtemp()
    isatab_filename = tempfile.mkstemp()[1]

    # create the isatab files
    _create_isatab_files(study,folder)

    # zip it
    output_filename = shutil.make_archive(isatab_filename,"zip",folder)

    # remove temporary folder
    shutil.rmtree(folder)
    os.unlink(isatab_filename)
    return output_filename


def _create_isatab_files(study,folder):
    df,df_pivot = study.get_matrix_and_accession_map(column='phenotype_id')
    _create_investigation_file(study,folder)
    _create_study_file(study,df,df_pivot,folder)
    _create_assay_file(study,df,folder)
    _create_tdf_file(study,folder)
    _create_data_file(df_pivot,folder)
    pass

def _create_investigation_file(study,folder):

    ontology_reference = """ONTOLOGY SOURCE REFERENCE
Term Source Name	OBI	EFO	UO	NCBITaxon	PO	GMI_accessions
Term Source File	http://data.bioontology.org/ontologies/OBI	http://data.bioontology.org/ontologies/EFO	http://purl.obolibrary.org/obo/UO	http://data.bioontology.org/ontologies/NCBITAXON	http://data.bioontology.org/ontologies/PO	http://gwas.gmi.oeaw.ac.at/#/taxonomy/1/passports?alleleAssayId=0
Term Source Version	23	118		6	10
Term Source Description	Ontology for Biomedical Investigations	Experimental Factor Ontology	Unit Ontology	National Center for Biotechnology Information (NCBI) Organismal Classification	Plant Ontology	Cataloque of Arabidopsis accessions at GMI
"""

    investigation = """INVESTIGATION
Investigation Identifier\tstudy%(study_id)s
Investigation Title\t%(study_name)s
Investigation Description\t%(study_description)s
Investigation Submission Date\t%(study_submission_date)s
Investigation Public Release Date\t%(study_publication_date)s
Comment [Created with configuration]    isaconfig-phenotyping-basic
Comment [Last Opened With Configuration]	isaconfig-phenotyping-basic
""" % ({'study_id':study.id,'study_name':study.name,
'study_description':study.description,'study_submission_date':datetime.datetime.now(),
'study_publication_date':datetime.datetime.now()})






    investigation_publications = """INVESTIGATION PUBLICATIONS
Investigation PubMed ID
Investigation Publication DOI
Investigation Publication Author List
Investigation Publication Title
Investigation Publication Status
Investigation Publication Status Term Accession Number
Investigation Publication Status Term Source REF
"""

    investigation_contacts="""INVESTIGATION CONTACTS
Investigation Person Last Name
Investigation Person First Name
Investigation Person Mid Initials
Investigation Person Email
Investigation Person Phone
Investigation Person Fax
Investigation Person Address
Investigation Person Affiliation
Investigation Person Roles
Investigation Person Roles Term Accession Number
Investigation Person Roles Term Source REF
"""


    pubmed_ids = []
    dois =  []
    authors = []
    titles = []
    status = []
    status_terms = []
    status_refs = []
    for pub in study.publications.all():
        pubmed_ids.append(pub.pubmed_id)
        dois.append(pub.doi)
        authors.append(pub.author_order)
        titles.append(pub.title)
        status.append('published')
        status_terms.append('1796')
        status_refs.append('EFO')


    study_info = """STUDY
Study Identifier\tstudy%(study_id)s
Study Title\t%(study_name)s
Study Description\t
Study Submission Date\t%(study_submission_date)s
Study Public Release Date\t%(study_publication_date)s
Study File Name\ts_study%(study_id)s.txt
STUDY DESIGN DESCRIPTORS
Study Design Type\t%(study_description)s
Study Design Type Term Accession Number\t
Study Design Type Term Source REF\t
""" % ({'study_id':study.id,'study_name':study.name,
'study_description':study.description,'study_submission_date':datetime.datetime.now(),
'study_publication_date':datetime.datetime.now()})

    study_publications = """STUDY PUBLICATIONS
Study PubMed ID\t%(pubmed_ids)s
Study Publication DOI\t%(dois)s
Study Publication Author List\t%(authors)s
Study Publication Title\t%(titles)s
Study Publication Status\t%(status)s
Study Publication Status Term Accession Number\t%(status_terms)s
Study Publication Status Term Source REF\t%(status_refs)s
Study FACTORS
Study Factor Name
Study Factor Type
Study Factor Type Term Accession Number
Study Factor Type Term Source REF
""" % {'pubmed_ids':'\t'.join(pubmed_ids),'dois':'\t'.join(dois),'authors':'\t'.join(authors),
'titles':'\t'.join(authors),'status':'\t'.join(status),'status_terms':'\t'.join(status_terms),'status_refs':'\t'.join(status_refs)}

    assays = """STUDY ASSAYS
Study Assay File Name\ta_study%(study_id)s.txt
Study Assay Measurement Type	phenotyping
Study Assay Measurement Type Term Accession Number	23
Study Assay Measurement Type Term Source REF	OBI
Study Assay Technology Type
Study Assay Technology Type Term Accession Number
Study Assay Technology Type Term Source REF
Study Assay Technology Platform
STUDY PROTOCOLS
Study Protocol Name	Data transformation
Study Protocol Type	Data transformation
Study Protocol Type Term Accession Number
Study Protocol Type Term Source REF
Study Protocol Description
Study Protocol URI
Study Protocol Version
Study Protocol Parameters Name	Trait Definition File
Study Protocol Parameters Name Term Accession Number
Study Protocol Parameters Name Term Source REF
Study Protocol Components Name
Study Protocol Components Type
Study Protocol Components Type Term Accession Number
Study Protocol Components Type Term Source REF
STUDY CONTACTS
Study Person Last Name
Study Person First Name
Study Person Mid Initials
Study Person Email
Study Person Phone
Study Person Fax
Study Person Address
Study Person Affiliation
Study Person Roles
Study Person Roles Term Accession Number
Study Person Roles Term Source REF
""" % {'study_id':study.id}

    investigation_content = ontology_reference + investigation + investigation_publications + investigation_contacts + study_info + study_publications + assays
    investigation_filename = os.path.join(folder,'i_investigation.txt')
    with open(investigation_filename,'w') as f:
        f.write(investigation_content.encode('utf-8'))
    return investigation_filename


def _create_study_file(study,df,df_pivot,folder):
    renderer = IsaTabStudyRenderer()
    organism = '%s %s' % (study.species.genus,study.species.species)
    ncbi_id = study.species.ncbi_id

    data = []
    for obs_unit_id,row in df_pivot.iterrows():
        info = df.ix[obs_unit_id]
        accession_id = info.accession_id
        accession_name = info.accession_name
        csv_row = {'source':'source%s' % accession_id ,'organism':organism,'organism_ref':'NCBITaxon','ncbi_id':ncbi_id,
        'accession_name':accession_name,'accession_ref':'GMI_accessions','accession_id':accession_id,
        'sample':'sample%s' % obs_unit_id}
        data.append(csv_row)
    content = renderer.render(data)

    study_filename = os.path.join(folder,'s_study%s.txt' % study.id)
    with open(study_filename,'w') as f:
        f.write(content)
    return study_filename

def _create_assay_file(study,df,folder):
    renderer = IsaTabAssayRenderer()
    data = []
    for obs_unit_id,row in df.iterrows():
        csv_row = {'sample':'sample%s' % obs_unit_id ,'assay':'assay%s' % obs_unit_id,
        'protocol_ref':'Data transformation','trait_def_file':'tdf.txt','derived_data_file':'d_data.txt'}
        data.append(csv_row)
    content = renderer.render(data)

    assay_filename = os.path.join(folder,'a_study%s.txt' % study.id)
    with open(assay_filename,'w') as f:
        f.write(content)
    return assay_filename



def _create_tdf_file(study,folder):
    renderer = IsaTabTraitDefinitionRenderer()
    data = []
    for phenotype in study.phenotype_set.all():
        row = {'variable_id':phenotype.id,'trait':phenotype.name,'method':phenotype.scoring}
        if phenotype.to_term:
            row['to_term_ref'] = phenotype.to_term.source.acronym
            row['to_term_id'] = phenotype.to_term.id
        if phenotype.uo_term:
            row['scale'] = phenotype.uo_term.name
            row['scale_ref'] = phenotype.uo_term.source.acronym
            row['scale_id'] = phenotype.uo_term.id

        data.append(row)

    content = renderer.render(data)

    tdf_filename = os.path.join(folder,'tdf.txt')
    with open(tdf_filename,'w') as f:
        f.write(content)
    return tdf_filename

def _create_data_file(df_pivot,folder):
    df_empty = df_pivot.fillna('')
    renderer = IsaTabDerivedDataFileRenderer()
    data = []
    headers = map(str,df_empty.columns.tolist())
    for obs_unit_id,row in df_empty.iterrows():
        csv_row = {'assay':'assay%s'% obs_unit_id}
        for i,value in enumerate(row.values):
            csv_row[headers[i]] = value
        data.append(csv_row)

    content = renderer.render(data)

    data_filename = os.path.join(folder,'d_data.txt')
    with open(data_filename,'w') as f:
        f.write(content)
    return data_filename
