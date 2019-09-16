from rest_framework import serializers

from phenotypedb.models import Phenotype,PhenotypeValue,Study, Accession, OntologyTerm, OntologySource
from phenotypedb.models import ObservationUnit, Submission, StudyCuration, PhenotypeCuration, Curation

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
    num_values = serializers.SerializerMethodField()


    class Meta:
        model = Phenotype
        fields = ('species','phenotype_id','name','doi','study','scoring',
                  'type','growth_conditions',
                  'to_term','to_name','to_comment',
                  'to_definition','to_source_acronym','to_source_name','to_source_url',
                  'eo_term','eo_name','eo_comment',
                  'eo_definition','eo_source_acronym','eo_source_name','eo_source_url',
                  'uo_term','uo_name','uo_comment',
                  'uo_definition','uo_source_acronym','uo_source_name','uo_source_url',
                  'integration_date', 'num_values', 'number_replicates')

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

    def get_num_values (self, obj):
        try:
            return obj.num_values
        except:
            return ""


class AccessionPhenotypesSerializer(serializers.Serializer):

    def __init__(self, *args, **kwargs):
        super(AccessionPhenotypesSerializer, self).__init__(*args, **kwargs)

    def to_representation(self, obj):
        data = {}
        for acc_id,phen_data in obj.iteritems():
            data[acc_id] = PhenotypeListSerializer(phen_data,many=True).data
        return data


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
            try:
                return obj.rnaseq.name
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
        fields = ('id','name','description','phenotype_count')

    def get_phenotype_count(self,obj):
        try:
            return obj.phenotype_set.count()
        except:
            return ""

'''
Reduced Phenotype Value Serializer Class
'''
class ReducedPhenotypeValueSerializer(serializers.ModelSerializer):
    accession_id = serializers.SerializerMethodField()
    phenotype_value = serializers.SerializerMethodField()

    class Meta:
        model = PhenotypeValue
        fields = ('accession_id','phenotype_value')

    def get_accession_id(self,obj):
        try:
            return obj.obs_unit.accession.id
        except:
            return ""

    def get_phenotype_value(self,obj):
        try:
            return obj.value
        except:
            return ""


'''
Accession List Serializer Class (read-only: might be extended to also allow integration of new data)
'''
class AccessionListSerializer(serializers.ModelSerializer):
    species = serializers.SerializerMethodField()
    genotypes = serializers.SerializerMethodField()
    count_phenotypes = serializers.SerializerMethodField()

    class Meta:
        model = Accession
        fields = ('pk','name','country','sitename','collector','collection_date','longitude','latitude','cs_number','species', 'genotypes', 'count_phenotypes')

    def get_genotypes(self, obj):
        try:
            return [{'id': genotype.pk, 'name': genotype.name } for genotype in obj.genotype_set.all()]
        except:
            return ""

    def get_species(self,obj):
        try:
            return '%s %s' % (obj.species.genus, obj.species.species)
        except:
            return ""

    def get_count_phenotypes(self,obj):
        try:
            return obj.count_phenotypes
        except:
            return ""


class StudyCurationSerializer(serializers.ModelSerializer):

    class Meta:
        model = StudyCuration
        fields = ('correct','message')

class PhenotypeCurationSerializer(serializers.ModelSerializer):

    class Meta:
        model = PhenotypeCuration
        fields = ('correct','message')

class SubmissionPhenotypeSerializer(serializers.HyperlinkedModelSerializer):
    #rest_url = serializers.HyperlinkedIdentityField(view_name='submission_infos')
    #html_url = serializers.HyperlinkedIdentityField(view_name='submission_study_result')
    curation = PhenotypeCurationSerializer(many=False, read_only=True)

    class Meta:
        model = Phenotype
        fields = ('name','scoring','growth_conditions','to_term','eo_term','uo_term','curation')

class SubmissionStudySerializer(serializers.HyperlinkedModelSerializer):
    #rest_url = serializers.HyperlinkedIdentityField(view_name='submission_infos')
    #html_url = serializers.HyperlinkedIdentityField(view_name='submission_study_result')
    curation = StudyCurationSerializer(many=False, read_only=True)
    phenotype_set = SubmissionPhenotypeSerializer(many=True,read_only=True)

    class Meta:
        model = Study
        fields = ('name','description','curation','phenotype_set')


class SubmissionDetailSerializer(serializers.HyperlinkedModelSerializer):
    rest_url = serializers.HyperlinkedIdentityField(view_name='submission_infos')
    html_url = serializers.HyperlinkedIdentityField(view_name='submission_study_result')
    study = SubmissionStudySerializer(many=False,read_only=True)

    class Meta:
        model = Submission
        fields = ('pk','firstname','submission_date','update_date','curation_date','lastname','email','status','rest_url','html_url','study')


class OntologySourceSerializer(serializers.ModelSerializer):

     class Meta:
        model = OntologySource
        fields = ('pk','name','acronym','description')

class OntologyTermListSerializer(serializers.ModelSerializer):

    source = serializers.SerializerMethodField()

    class Meta:
        model = OntologyTerm
        fields = ('pk','name','definition','comment','source')

    def get_source(self,obj):
        return '%s (%s)' % (obj.source.name, obj.source.acronym)



#class SubmissionUploadDetailSerializer(serializers.Model)
