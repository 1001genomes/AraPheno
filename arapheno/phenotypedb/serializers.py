from rest_framework import serializers
from phenotypedb.models import Phenotype,Study

'''
Phenotype List Serializer Class (read-only: might be extended to also allow integration of new data)
'''
class PhenotypeListSerializer(serializers.ModelSerializer):
    study = serializers.SlugRelatedField(slug_field="name",read_only=True)

    class Meta:
        model = Phenotype
        fields = ('doi','name','study','eo_term','to_term','uo_term')

'''
Phenotype Detail Serializer Class (read-only: might be extended to also allow integration of new data)
'''
class PhenotypeDetailSerializer(serializers.ModelSerializer):
    study = serializers.SlugRelatedField(slug_field="name",read_only=True)
    
    class Meta:
        model = Phenotype
        fields = ('doi','name','study',
                  'scoring','source','type',
                  'growth_conditions','eo_term','to_term',
                  'uo_term')

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
