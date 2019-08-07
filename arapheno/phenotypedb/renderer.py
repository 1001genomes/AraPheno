from rest_framework_csv.renderers import CSVRenderer
from rest_framework import renderers

'''
Renderer class for alternative ordering of the CSV output
'''
class PhenotypeListRenderer(CSVRenderer):
    header = ['species','phenotype_id','name','doi','study','scoring',
              'source','type','growth_conditions',
              'integration_date','number_replicates',
              'to_term','to_name','to_definition','to_comment',
              'to_source_acronym','to_source_name','to_source_url'
              'eo_term','eo_name','eo_definition','eo_comment',
              'eo_source_acronym','eo_source_name','eo_source_url'
              'uo_term','uo_name','uo_definition','uo_comment',
              'uo_source_acronym','uo_source_name','uo_source_url']

class StudyListRenderer(CSVRenderer):
    header = ['id','name','description','phenotype_count']
<<<<<<< HEAD
        
        
=======


>>>>>>> de4bb8ac375f40ff2b2af80271799a435c1ecc13
class PhenotypeValueRenderer(CSVRenderer):
    header = ['phenotype_name','accession_id','accession_name','accession_cs_number','accession_longitude',
              'accession_latitude','accession_country','phenotype_value','obs_unit_id']

class TransformationRenderer(CSVRenderer):
    labels = {'obs_unit_id': 'replicate_id'}

    def render(self, data, media_type=None, renderer_context={}, writer_opts=None):
        headers = ['accession_id']
        for transformation in data['transformations']:
            headers.append(transformation)
        renderer_context['header'] = headers
        converted_data = []
        for ix, accession in enumerate(data['accessions']):
            row = {'accession_id': data['accessions'][ix][0]}
            for transformation, info in data['transformations'].items():
                row[transformation] = info['values'][ix][1]
            converted_data.append(row)
        return super(TransformationRenderer, self).render(converted_data, media_type, renderer_context,writer_opts)


class PhenotypeMatrixRenderer(CSVRenderer):
    labels = {'obs_unit_id':'replicate_id'}

    def render(self, data, media_type=None, renderer_context={}, writer_opts=None):
        if type(data) == list and len(data) > 0:
            renderer_context['header'] = self._get_sorted_headers(data[0].keys())
        return super(PhenotypeMatrixRenderer, self).render(data, media_type, renderer_context,writer_opts)


    def _get_sorted_headers(self,headers):
        headers.remove('obs_unit_id')
        headers.remove('accession_id')
        headers.remove('accession_name')
        headers.insert(0,'obs_unit_id')
        headers.insert(0,'accession_id')
        return headers

class AccessionListRenderer(CSVRenderer):
    header = ['pk','name','country','latitude','longitude',
              'collector','collection_date','cs_number','species']


class PLINKMatrixRenderer(PhenotypeMatrixRenderer):
    media_type = "application/plink"
    format = "plink"
    writer_opts = {'delimiter':' '}
    labels = {'obs_unit_id':'IID','accession_id':'FID'}


    def _get_sorted_headers(self,headers):
        headers.remove('obs_unit_id')
        headers.remove('accession_id')
        headers.remove('accession_name')
        headers.insert(0,'obs_unit_id')
        headers.insert(0,'accession_id')
        for i,header in enumerate(headers):
            headers[i] = header.replace(' ','_')
        return headers


'''
Custom File Renderer
'''
class PLINKRenderer(renderers.BaseRenderer):
    media_type = "application/plink"
    format = "plink"

    def render(self,data,media_type=None,renderer_context=None):
        if data is None:
            return "No Data Found"
        plink = "FID IID \"" + data[0]['phenotype_name'].replace(' ','_') + "\"\n"
        for element in data:
            if not ("accession_id" in element):
                return "Wrong Data Format"
            plink += str(element['accession_id']) + " " + str(element['accession_id']) + " " + str(element['phenotype_value']) + "\n"
        return plink

class IsaTabRenderer(CSVRenderer):

    def render(self, data, media_type=None, renderer_context={}, writer_opts=None):
        renderer_context['writer_opts'] = {'delimiter':'\t'}
        return super(IsaTabRenderer, self).render(data, media_type, renderer_context,writer_opts)


class IsaTabStudyRenderer(IsaTabRenderer):
    labels ={'source':'Source Name','organism':'Characteristics[Organism]','organism_ref':'Term Source REF',
    'ncbi_id':'Term Accession Number','accession_name':'Characteristics[Infraspecific name]',
    'accession_ref':'Term Source REF','accession_id':'Term Accession Number',
    'seed_origin':'Characteristics[Seed origin]','study_start':'Characteristics[Study start]',
    'study_duration':'Characteristics[Study duration]','growth_facility':'Characteristics[Growth facility]',
    'location':'Characteristics[Geographic location]','location_ref':'Term Source REF','location_id':'Term Accession Number','sample':'Sample Name'}

    header = ['source','organism','organism_ref','ncbi_id','accession_name',
    'accession_ref','accession_id','seed_origin','study_start','study_duration','growth_facility',
    'location','location_ref','location_id','sample']



class IsaTabAssayRenderer(IsaTabRenderer):
    header = ['sample','organism_part','organism_ref','organism_id','assay','raw_data_file','protocol_ref','trait_def_file','derived_data_file']
    labels = {'sample':'Sample Name','organism_part':'Characteristics[Organism Part]','organism_ref':'Term Source REF','organism_id':'Term Accession Number',
    'assay':'Assay Name','raw_data_file':'Raw Data File','protocol_ref':'Protocol REF','trait_def_file':'Parameter Value[Trait Definition File]','derived_data_file':'Derived Data File'}


class IsaTabTraitDefinitionRenderer(IsaTabRenderer):
    header= ['variable_id','trait','to_term_ref','to_term_id','method','method_ref','method_id','scale','scale_ref','scale_id']
    labels = {'variable_id':'Variable ID','trait':'Trait','to_term_ref':'Term Source REF','to_term_id':'Term Accession Number','method':'Method','method_ref':'Term Source REF','method_id':'Term Accession Number','scale':'Scale','scale_ref':'Term Source REF','scale_id':'Term Accession Number'}

class IsaTabDerivedDataFileRenderer(IsaTabRenderer):

    labels = {'assay':'Assay Name'}

    def render(self, data, media_type=None, renderer_context={}, writer_opts=None):
        if type(data) == list and len(data) > 0:
            renderer_context['header'] = self._get_sorted_headers(map(str,data[0].keys()))
        return super(IsaTabDerivedDataFileRenderer, self).render(data, media_type, renderer_context,writer_opts)


    def _get_sorted_headers(self,headers):
        headers.remove('assay')
        headers.insert(0,'assay')
        return headers

class IsaTabFileRenderer(renderers.BaseRenderer):
    media_type = "application/isatab"
    format = "isatab"

    def render(self,data,media_type=None,renderer_context=None):
        pass

class ZipFileRenderer(renderers.BaseRenderer):
    media_type = "application/zip"
    format = "zip"

    def render(self,data,media_type=None,renderer_context=None):
        pass