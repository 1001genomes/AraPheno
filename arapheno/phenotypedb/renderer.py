from rest_framework_csv.renderers import CSVRenderer

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
    header = ['accession_id','accession_name','accession_cs_number','accession_longitude',
              'accession_latitude','accession_country','phenotype_value']
