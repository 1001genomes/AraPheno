import django_tables2 as tables
from django_tables2.utils import A
from .models import Phenotype
from django.utils.safestring import mark_safe

class PhenotypeTable(tables.Table):
    name = tables.LinkColumn("phenotype_detail",args=[A('id')],text=lambda record: record.name,verbose_name="Phenotype Name",order_by="name")
    study = tables.LinkColumn("study_detail",args=[A('study.id')],text=lambda record: record.study.name,verbose_name="Study",order_by="study.name")
    to = tables.Column(accessor="to_term",verbose_name="TO",order_by="to_term")
    eo = tables.Column(accessor="eo_term",verbose_name="EO",order_by="eo_term")
    uo = tables.Column(accessor="uo_term",verbose_name="UO",order_by="uo_term")
    
    class Meta:
        attrs = {"class": "striped"}

class StudyTable(tables.Table):
    name = tables.LinkColumn("study_detail",args=[A('id')],text=lambda record: record.name,verbose_name="Study Name",order_by="name")
    description = tables.Column(accessor="description",verbose_name="Description",order_by="description")
    #phenotypes = tables.Column(accessor="phenotype_set",verbose_name="# Phenotypes",order_by="phenotype_set")
    
    class Meta:
        attrs = {"class": "striped"}
