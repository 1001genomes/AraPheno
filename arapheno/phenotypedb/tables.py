import django_tables2 as tables
from django_tables2.utils import A
from .models import Phenotype
from django.utils.safestring import mark_safe

class PhenotypeTable(tables.Table):
    name = tables.LinkColumn("phenotype_detail",args=[A('id')],text=lambda record: record.name,verbose_name="Phenotype Name",order_by="name")
    study = tables.LinkColumn("study_detail",args=[A('study.id')],text=lambda record: record.study.name,verbose_name="Study",order_by="study.name")
    to = tables.Column(accessor="to_term.name",verbose_name="Trait Ontology (TO)",order_by="to_term.name")
    eo = tables.Column(accessor="eo_term.name",verbose_name="Environmental Ontoloy (EO)",order_by="eo_term.name")
    uo = tables.Column(accessor="uo_term.name",verbose_name="Unit Ontology (UO)",order_by="uo_term.name")

    ''' # Too many links in table might be confusing
    def render_to(self,record):
        try:
           return mark_safe('<a href="' + record.to_term.get_info_url() + '" target="_blank">' + str(record.to_term.name) + '</a>')
        except:
            return record.to_term.name
    
    def render_eo(self,record):
        try:
            return mark_safe('<a href="' + record.eo_term.get_info_url() + '" target="_blank">' + str(record.eo_term.name) + '</a>')
        except:
            return record.eo_term.name
    
    def render_uo(self,record):
        try:
            return mark_safe('<a href="' + record.uo_term.get_info_url() + '" target="_blank">' + str(record.uo_term.name) + '</a>')
        except:
            return record.uo_term.name
    '''

    class Meta:
        attrs = {"class": "striped"}

class ReducedPhenotypeTable(tables.Table):
    name = tables.LinkColumn("phenotype_detail",args=[A('id')],text=lambda record: record.name,verbose_name="Phenotype Name",order_by="name")
    to = tables.Column(accessor="to_term.name",verbose_name="Trait Ontology (TO)",order_by="to_term.name")
    eo = tables.Column(accessor="eo_term.name",verbose_name="Environmental Ontoloy (EO)",order_by="eo_term.name")
    uo = tables.Column(accessor="uo_term.name",verbose_name="Unit Ontology (UO)",order_by="uo_term.name")
    
    ''' # Too many links in table might be confusing
    def render_to(self,record):
        try:
           return mark_safe('<a href="' + record.to_term.get_info_url() + '" target="_blank">' + str(record.to_term.name) + '</a>')
        except:
            return record.to_term.name
    
    def render_eo(self,record):
        try:
            return mark_safe('<a href="' + record.eo_term.get_info_url() + '" target="_blank">' + str(record.eo_term.name) + '</a>')
        except:
            return record.eo_term.name
    
    def render_uo(self,record):
        try:
            return mark_safe('<a href="' + record.uo_term.get_info_url() + '" target="_blank">' + str(record.uo_term.name) + '</a>')
        except:
            return record.uo_term.name
    '''
    class Meta:
        attrs = {"class": "striped"}


class StudyTable(tables.Table):
    name = tables.LinkColumn("study_detail",args=[A('id')],text=lambda record: record.name,verbose_name="Study Name",order_by="name")
    description = tables.Column(accessor="description",verbose_name="Description",order_by="description")
    phenotypes = tables.Column(accessor="count_phenotypes",verbose_name="#Phenotypes",order_by="phenotype")
    
    #def render_phenotypes(self,record):
    #    return mark_safe("#" + str(record.phenotype_set.count()))

    class Meta:
        attrs = {"class": "striped"}


class PublicationTable(tables.Table):
    doi =  tables.TemplateColumn('<a href="{{record.url}}" target="_blank">{{record.doi}}</a>')
    pubmed =  tables.TemplateColumn('<a href="{{record.url}}" target="_blank">{{record.doi}}</a>')
    journal = tables.Column(accessor="journal",verbose_name="Journal",order_by="journal")
    volume = tables.Column(accessor="volume",verbose_name="Volume",order_by="volume")
    pub_year = tables.Column(accessor="pub_year",verbose_name="Year",order_by="pub_year")
    title = tables.Column(accessor="title",verbose_name="Title",order_by="title")

    class Meta:
        attrs = {"class": "striped"}
