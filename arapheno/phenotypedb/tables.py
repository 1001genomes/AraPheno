"""
Tables for django-table2
"""
from django.db.models import Count
import django_tables2 as tables
from django_tables2.utils import A
from django.utils.safestring import mark_safe
import numpy as np


class ReducedPhenotypeTable(tables.Table):
    """
    Table that is displayed in the Study detail view
    """
    name = tables.LinkColumn("phenotype_detail", args=[A('id')], text=lambda record: record.name, verbose_name="Phenotype Name", order_by="name")
    to = tables.Column(accessor="to_term.name", verbose_name="Trait Ontology (TO)", order_by="to_term.name")
    eo = tables.Column(accessor="eo_term.name", verbose_name="Environmental Ontoloy (EO)", order_by="eo_term.name")
    uo = tables.Column(accessor="uo_term.name", verbose_name="Unit Ontology (UO)", order_by="uo_term.name")
    values = tables.Column(accessor="num_values", verbose_name="# values", order_by="num_values")

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


class PhenotypeTable(ReducedPhenotypeTable):
    """
    Table that is displayed in the general phenotype list view
    """
    study = tables.LinkColumn("study_detail", args=[A('study.id')], text=lambda record: record.study.name, verbose_name="Study", order_by="study.name")

    class Meta:
        attrs = {"class": "striped"}


class AccessionPhenotypeTable(PhenotypeTable):
    """
    Table that is displayed in the accession detial view
    """
    value = tables.Column(empty_values=(),verbose_name='Value (mean)', orderable=False)

    def __init__(self, accession_id, *args, **kwargs):
        super(AccessionPhenotypeTable, self).__init__(*args, **kwargs)
        self.accession_id = accession_id

    def render_value(self,record):
        values = record.get_values_for_acc(self.accession_id)
        if not values:
            return "N/A"
        return str(np.mean(values))
class ReducedRNASeqTable(tables.Table):
    """
    Table that is displayed in the Study detail view
    """
    name = tables.LinkColumn("rnaseq_detail", args=[A('id')], text=lambda record: record.name, verbose_name="Gene", order_by="name")
    condition = tables.Column(accessor="growth_conditions", verbose_name="Growth conditions", order_by="growth_conditions")

    class Meta:
        attrs = {"class": "striped", "is_rnaseq": True}

class RNASeqTable(ReducedRNASeqTable):
    """
    Table that is displayed in the general RNASeq list view
    """
    study = tables.LinkColumn("study_detail", args=[A('study.id')], text=lambda record: record.study.name, verbose_name="Study", order_by="study.name")

class StudyTable(tables.Table):
    """
    Table that is displayed in the study list view
    """
    name = tables.LinkColumn("study_detail", args=[A('id')], text=lambda record: record.name, verbose_name="Study Name", order_by="name")
    description = tables.Column(accessor="description", verbose_name="Description", order_by="description")
    phenotypes = tables.Column(accessor="count_phenotypes", verbose_name="#Phenotypes", order_by="phenotype")
    update_date = tables.DateTimeColumn(accessor="update_date", verbose_name="Date Added", order_by="update_date",format="M/d/Y")

    class Meta:
        attrs = {"class": "striped"}

class RNASeqStudyTable(tables.Table):
    """
    Table that is displayed in the study list view
    """
    name = tables.LinkColumn("study_detail", args=[A('id')], text=lambda record: record.name, verbose_name="Study Name", order_by="name")
    description = tables.Column(accessor="description", verbose_name="Description", order_by="description")
    phenotypes = tables.Column(accessor="rna_count", verbose_name="#RNASeqs", order_by="rnaseq")
    update_date = tables.DateTimeColumn(accessor="update_date", verbose_name="Date Added", order_by="update_date",format="M/d/Y")


    class Meta:
        attrs = {"class": "striped",  "is_rnaseq": True}



class PublicationTable(tables.Table):
    """
    Table of publications for each study
    """
    doi = tables.TemplateColumn('<a href="{{record.url}}" target="_blank">{{record.doi}}</a>')
    pubmed = tables.TemplateColumn('<a href="{{record.url}}" target="_blank">{{record.doi}}</a>')
    journal = tables.Column(accessor="journal", verbose_name="Journal", order_by="journal")
    volume = tables.Column(accessor="volume", verbose_name="Volume", order_by="volume")
    pub_year = tables.Column(accessor="pub_year", verbose_name="Year", order_by="pub_year")
    title = tables.Column(accessor="title", verbose_name="Title", order_by="title")

    class Meta:
        attrs = {"class": "striped"}


class AccessionTable(tables.Table):
    """
    Table that is displayed on the accession list view
    """
    id = tables.LinkColumn("accession_detail", args=[A('id')], text=lambda record: record.pk, verbose_name="ID", order_by="pk")
    name = tables.Column(accessor="name", verbose_name="Name", order_by="name")
    country = tables.Column(accessor="country", verbose_name="Country", order_by="country")
    sitename = tables.Column(accessor="sitename", verbose_name="Sitename", order_by="sitename")
    collector = tables.Column(accessor="collector", verbose_name="Collector", order_by="collector")
    longitude = tables.Column(accessor="longitude", verbose_name="Longitude", order_by="longitude")
    latitude = tables.Column(accessor="latitude", verbose_name="Latitude", order_by="latitude")
    cs_number = tables.URLColumn({"target":"_blank"},lambda record: record.cs_number, accessor="cs_number_url", verbose_name="CS Number", order_by="cs_number")
    genotypes = tables.ManyToManyColumn(accessor="genotype_set", transform=lambda genotype: genotype.name)
    number_of_phenotypes = tables.Column(accessor="count_phenotypes",verbose_name='# Phenotypes')

    class Meta:
        attrs = {"class": "striped"}

    def order_number_of_phenotypes(self,QuerySet,is_descending):
        QuerySet = QuerySet.annotate(count=Count('observationunit__phenotypevalue__phenotype',distinct=True)).order_by(('-' if is_descending else '') + 'count')
        return (QuerySet, True)


class StatusColumn(tables.Column):

    def render(self, value):
        if value == -1:
            icon = "schedule"
            cls = "unknown"
            tooltip = "Not reviewed yet"
        elif value:
            icon = "done"
            cls = "ok"
            tooltip = "No issues"
        else:
            icon = "error_outline"
            cls = "error"
            tooltip = "Issues found"
        return mark_safe('<i data-tooltip="%s" data-position="right" data-delay="50"  class="material-icons tooltipped %s">%s</i>' % (tooltip,cls,icon))

class CurationPhenotypeTable(tables.Table):
    """
    Table that is displayed in the sumbission/curation view
    """
    name = tables.LinkColumn("submission_phenotype_result", args=[A('study.submission.id'), A('id')], text=lambda record: record.name, verbose_name="Phenotype Name", order_by="name")
    to = tables.Column(accessor="to_term.name", verbose_name="Trait Ontology (TO)", order_by="to_term.name")
    eo = tables.Column(accessor="eo_term.name", verbose_name="Environmental Ontoloy (EO)", order_by="eo_term.name")
    uo = tables.Column(accessor="uo_term.name", verbose_name="Unit Ontology (UO)", order_by="uo_term.name")
    status = StatusColumn(accessor="curation_status",verbose_name="Status")


class OntologyTermTable(tables.Table):
    """
    Table that is displayed for ontology terms
    """
    name = tables.LinkColumn("ontology_detail", args=[A('source.acronym'), A('pk')], text=lambda record: record.name, verbose_name="Ontology Name", order_by="name")
    source = tables.LinkColumn("ontologysource_detail",args=[A('source.acronym')], text=lambda record: '%s (%s)' % (record.source.name, record.source.acronym),verbose_name='Source',order_by="source.name")
    definition = tables.Column(accessor="definition", verbose_name="Definition", order_by="definition")
    info = tables.TemplateColumn('<a target="_blank" href="{{record.get_info_url}}" >Infos</a>')

    class Meta:
        attrs = {"class": "striped"}
