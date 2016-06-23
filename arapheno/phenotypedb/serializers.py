from rest_framework import serializers

from phenotypedb.models import Phenotype,PhenotypeValue,Study
from phenotypedb.models import ObservationUnit



'''
Phenotype List Serializer Class (read-only: might be extended to also allow integration of new data)
'''
class PhenotypeListSerializer(serializers.ModelSerializer):
    study = serializers.SlugRelatedField(slug_field="name",read_only=True)
    species = serializers.SerializerMethodField()
    phenotype_id = serializers.SerializerMethodField()

    class Meta:
        model = Phenotype
        fields = ('species','phenotype_id','name','doi','study','scoring',
                  'source','type','growth_conditions',
                  'eo_term','to_term','uo_term',
                  'integration_date','number_replicates')
    
    def get_species(self,obj):
        return obj.species.genus + " " + obj.species.species + " (NCBI: " + str(obj.species.ncbi_id) + ")"
    
    def get_phenotype_id(self,obj):
        return obj.id

'''
Phenotype Value Serializer Class
'''
class PhenotypeValueSerializer(serializers.ModelSerializer):
    accession_name = serializers.SerializerMethodField()
    accession_id = serializers.SerializerMethodField()
    accession_cs_number = serializers.SerializerMethodField()
    accession_longitude = serializers.SerializerMethodField()
    accession_latitude = serializers.SerializerMethodField()
    accession_country = serializers.SerializerMethodField()
    phenotype_value = serializers.SerializerMethodField()
    obs_unit_id = serializers.SerializerMethodField()

    class Meta:
        model = PhenotypeValue
        fields = ('accession_id','accession_name','accession_cs_number','accession_longitude',
                  'accession_latitude','accession_country','phenotype_value','obs_unit_id')
    
    def get_accession_name(self,obj):
        return obj.obs_unit.accession.name
    
    def get_accession_id(self,obj):
        return obj.obs_unit.accession.id
    
    def get_accession_cs_number(self,obj):
        return obj.obs_unit.accession.cs_number
    
    def get_accession_longitude(self,obj):
        return obj.obs_unit.accession.longitude
    
    def get_accession_latitude(self,obj):
        return obj.obs_unit.accession.latitude
    
    def get_accession_country(self,obj):
        return obj.obs_unit.accession.country
    
    def get_phenotype_value(self,obj):
        return obj.value
    
    def get_obs_unit_id(self,obj):
        return obj.obs_unit.id

'''
Study List Serializer Class (read-only: might be extended to also allow integration of new data)
'''
class StudyListSerializer(serializers.ModelSerializer):
    phenotype_count = serializers.SerializerMethodField()

    class Meta:
        model = Study
        fields = ('name','description','phenotype_count')

    def get_phenotype_count(self,obj):
        return obj.phenotype_set.count()

