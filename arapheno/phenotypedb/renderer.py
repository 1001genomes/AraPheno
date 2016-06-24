from rest_framework_csv.renderers import CSVRenderer
from rest_framework import renderers

'''
Renderer class for alternative ordering of the CSV output
'''
class PhenotypeListRenderer(CSVRenderer):
    header = ['species','phenotype_id','name','doi','study','scoring',
              'source','type','growth_conditions',
              'eo_term','to_term','uo_term',
              'integration_date','number_replicates']

class StudyListRenderer(CSVRenderer):
    header = ['name','description','phenotype_count']
        
        
class PhenotypeValueRenderer(CSVRenderer):
    header = ['phenotype_name','accession_id','accession_name','accession_cs_number','accession_longitude',
              'accession_latitude','accession_country','phenotype_value','obs_unit_id']

class PhenotypeMatrixRenderer(CSVRenderer):
    header = ['species','phenotype_id','name','doi','study','scoring',
              'source','type','growth_conditions',
              'eo_term','to_term','uo_term',
              'integration_date','number_replicates','data']

'''
Custom File Renderer
'''
class PLINKRenderer(renderers.BaseRenderer):
    media_type = "application/plink"
    format = "plink"

    def render(self,data,media_type=None,renderer_context=None):
        if data is None:
            return "No Data Found"
        plink = "FID IID " + data[0]['phenotype_name'] + "\n"
        for element in data:
            if not ("accession_id" in element):
                return "Wrong Data Format"
            plink += str(element['accession_id']) + " " + str(element['accession_id']) + " " + str(element['phenotype_value']) + "\n"
        return plink
