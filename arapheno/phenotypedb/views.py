from django.shortcuts import get_object_or_404, render
from django.http import HttpResponseRedirect
from django.core.urlresolvers import reverse
from django.views.generic import ListView, DetailView
from django.views.generic.detail import SingleObjectMixin
from models import Phenotype, Study, Accession
from tables import PhenotypeTable, StudyTable
from home.forms import GlobalSearchForm
from django.db.models import Count

from django_tables2 import RequestConfig

# Create your views here.

def PhenotypeList(request):
    table = PhenotypeTable(Phenotype.objects.all(),order_by="-name")
    RequestConfig(request,paginate={"per_page":20}).configure(table)
    return render(request,'phenotypedb/phenotype_list.html',{"phenotype_table":table})


class PhenotypeDetail(DetailView):
    model = Phenotype

    def get_context_data(self, **kwargs):
        context = super(PhenotypeDetail, self).get_context_data(**kwargs)
        context['pheno_acc_infos'] = self.object.phenotypevalue_set.prefetch_related('obs_unit__accession')
        context['geo_chart_data'] = Accession.objects.filter(observationunit__phenotypevalue__phenotype_id=1).values('country').annotate(count=Count('country'))
        return context

def StudyList(request):
    #queryset = Study.objects.all().annotate(phenotype_count=Count('phenotype'))
    #context_object_name = 'study_list'
    #paginate_by = 20
    table = StudyTable(Study.objects.all(),order_by="-name")
    RequestConfig(request,paginate={"per_page":20}).configure(table)
    return render(request,'phenotypedb/study_list.html',{"study_table":table})


def StudyDetail(request,pk=None):
    study = Study.objects.get(id=pk)
    phenotype_table = PhenotypeTable(Phenotype.objects.filter(study__id=pk),order_by="-name")
    RequestConfig(request,paginate={"per_page":20}).configure(phenotype_table)
    variable_dict = {}
    variable_dict["phenotype_table"] = phenotype_table
    variable_dict["study"] = study
    variable_dict['to_data'] = study.phenotype_set.values('to_term').annotate(count=Count('to_term'))
    variable_dict['eo_data'] = study.phenotype_set.values('eo_term').annotate(count=Count('eo_term'))
    variable_dict['uo_data'] = study.phenotype_set.values('uo_term').annotate(count=Count('uo_term'))

    return render(request,'phenotypedb/study_detail.html',variable_dict)
