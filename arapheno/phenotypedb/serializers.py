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
    to_name = serializers.SerializerMethodField()
    to_definition = serializers.SerializerMethodField()
    to_comment = serializers.SerializerMethodField()
    to_source_acronym = serializers.SerializerMethodField()
    to_source_name = serializers.SerializerMethodField()
    to_source_url = serializers.SerializerMethodField()
    eo_name = serializers.SerializerMethodField()
    eo_definition = serializers.SerializerMethodField()
    eo_comment = serializers.SerializerMethodField()
    eo_source_acronym = serializers.SerializerMethodField()
    eo_source_name = serializers.SerializerMethodField()
    eo_source_url = serializers.SerializerMethodField()
    uo_name = serializers.SerializerMethodField()
    uo_definition = serializers.SerializerMethodField()
    uo_comment = serializers.SerializerMethodField()
    uo_source_acronym = serializers.SerializerMethodField()
    uo_source_name = serializers.SerializerMethodField()
    uo_source_url = serializers.SerializerMethodField()

    class Meta:
        model = Phenotype
        fields = ('species','phenotype_id','name','doi','study','scoring',
                  'source','type','growth_conditions',
                  'to_term','to_name','to_comment',
                  'to_definition','to_source_acronym','to_source_name','to_source_url',
                  'eo_term','eo_name','eo_comment',
                  'eo_definition','eo_source_acronym','eo_source_name','eo_source_url',
                  'uo_term','uo_name','uo_comment',
                  'uo_definition','uo_source_acronym','uo_source_name','uo_source_url',
                  'integration_date','number_replicates')
    
    def get_species(self,obj):
        return obj.species.genus + " " + obj.species.species + " (NCBI: " + str(obj.species.ncbi_id) + ")"
    
    def get_phenotype_id(self,obj):
        return obj.id

    def get_to_name(self,obj):
        try:
            return obj.to_term.name
        except:
            return ""
    
    def get_to_comment(self,obj):
        try:
            return obj.to_term.comment
        except:
            return ""
    
    def get_to_definition(self,obj):
        try:
            return obj.to_term.definition
        except:
            return ""
    
    def get_to_source_acronym(self,obj):
        try:
            return obj.to_term.source.acronym
        except:
            return ""
    
    def get_to_source_name(self,obj):
        try:
            return obj.to_term.source.name
        except:
            return ""
    
    def get_to_source_url(self,obj):
        try:
            return obj.to_term.source.url
        except:
            return ""
    
    def get_eo_name(self,obj):
        try:
            return obj.eo_term.name
        except:
            return ""
    
    def get_eo_comment(self,obj):
        try:
            return obj.eo_term.comment
        except:
            return ""
    
    def get_eo_definition(self,obj):
        try:
            return obj.eo_term.definition
        except:
            return ""
    
    def get_eo_source_acronym(self,obj):
        try:
            return obj.eo_term.source.acronym
        except:
            return ""
    
    def get_eo_source_name(self,obj):
        try:
            return obj.eo_term.source.name
        except:
            return ""
    
    def get_eo_source_url(self,obj):
        try:
            return obj.eo_term.source.url
        except:
            return ""
    
    def get_uo_name(self,obj):
        try:
            return obj.uo_term.name
        except:
            return ""
    
    def get_uo_comment(self,obj):
        try:
            return obj.uo_term.comment
        except:
            return ""
    
    def get_uo_definition(self,obj):
        try:
            return obj.uo_term.definition
        except:
            return ""
    
    def get_uo_source_acronym(self,obj):
        try:
            return obj.uo_term.source.acronym
        except:
            return ""
    
    def get_uo_source_name(self,obj):
        try:
            return obj.uo_term.source.name
        except:
            return ""
    
    def get_uo_source_url(self,obj):
        try:
            return obj.uo_term.source.url
        except:
            return ""

'''
Phenotype Value Serializer Class
'''
class PhenotypeValueSerializer(serializers.ModelSerializer):
    phenotype_name = serializers.SerializerMethodField()
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
        fields = ('phenotype_name','accession_id','accession_name','accession_cs_number','accession_longitude',
                  'accession_latitude','accession_country','phenotype_value','obs_unit_id')
    
    def get_phenotype_name(self,obj):
        try:
            return obj.phenotype.name
        except:
            return ""
    
    def get_accession_name(self,obj):
        try:
            return obj.obs_unit.accession.name
        except:
            return ""
    
    def get_accession_id(self,obj):
        try:
            return obj.obs_unit.accession.id
        except:
            return ""
    
    def get_accession_cs_number(self,obj):
        try:
            return obj.obs_unit.accession.cs_number
        except:
            return ""
    
    def get_accession_longitude(self,obj):
        try:
            return obj.obs_unit.accession.longitude
        except:
            return ""
    
    def get_accession_latitude(self,obj):
        try:
            return obj.obs_unit.accession.latitude
        except:
            return ""
    
    def get_accession_country(self,obj):
        try:
            return obj.obs_unit.accession.country
        except:
            return ""
    
    def get_phenotype_value(self,obj):
        try:
            return obj.value
        except:
            return ""
    
    def get_obs_unit_id(self,obj):
        try:
            return obj.obs_unit.id
        except:
            return ""


'''
Study List Serializer Class (read-only: might be extended to also allow integration of new data)
'''
class StudyListSerializer(serializers.ModelSerializer):
    phenotype_count = serializers.SerializerMethodField()

    class Meta:
        model = Study
        fields = ('name','description','phenotype_count')

    def get_phenotype_count(self,obj):
        try:
            return obj.phenotype_set.count()
        except:
            return ""

