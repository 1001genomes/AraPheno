from django.shortcuts import get_object_or_404, render
from django.http import HttpResponseRedirect
from django.core.urlresolvers import reverse
from django.views.generic import ListView, DetailView
from django.views.generic.detail import SingleObjectMixin
from models import Phenotype, Study, Accession
from tables import PhenotypeTable, ReducedPhenotypeTable, StudyTable, AccessionTable
from forms import CorrelationWizardForm
from home.forms import GlobalSearchForm
from django.db.models import Count

from django_tables2 import RequestConfig

from scipy.stats import shapiro

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
        context['values'] = self.object.phenotypevalue_set.all().values_list("value",flat=True)
        context['shapiro'] = "%.2e"%shapiro(context['values'])[1]
        return context

def StudyList(request):
    table = StudyTable(Study.objects.all(),order_by="-name")
    RequestConfig(request,paginate={"per_page":20}).configure(table)
    return render(request,'phenotypedb/study_list.html',{"study_table":table})


def StudyDetail(request,pk=None):
    study = Study.objects.get(id=pk)
    phenotype_table = ReducedPhenotypeTable(Phenotype.objects.filter(study__id=pk),order_by="-name")
    RequestConfig(request,paginate={"per_page":20}).configure(phenotype_table)
    variable_dict = {}
    variable_dict["phenotype_table"] = phenotype_table
    variable_dict["study"] = study
    variable_dict['to_data'] = study.phenotype_set.values('to_term__name').annotate(count=Count('to_term__name'))
    variable_dict['eo_data'] = study.phenotype_set.values('eo_term__name').annotate(count=Count('eo_term__name'))
    variable_dict['uo_data'] = study.phenotype_set.values('uo_term__name').annotate(count=Count('uo_term__name'))
    return render(request,'phenotypedb/study_detail.html',variable_dict)

def CorrelationWizard(request):
    wizard_form = CorrelationWizardForm()
    if "phenotype_search" in request.POST:
        query = request.POST.getlist("phenotype_search")
        query = ",".join(map(str,query))
        return HttpResponseRedirect("/correlation/" + query + "/")
    return render(request,'phenotypedb/correlation_wizard.html',{"phenotype_wizard":wizard_form})

def CorrelationResults(request,ids=None):
    return render(request,'phenotypedb/correlation_results.html',{"phenotype_ids":ids})
    
def AccessionList(request):
    table = AccessionTable(Accession.objects.all(),order_by="-name")
    RequestConfig(request,paginate={"per_page":20}).configure(table)
    return render(request,'phenotypedb/accession_list.html',{"accession_table":table})


def AccessionDetail(request,pk=None):
    accession = Accession.objects.get(id=pk)
    phenotype_table = PhenotypeTable(Phenotype.objects.filter(phenotypevalue__obs_unit__accession_id=pk),order_by="-id")
    RequestConfig(request,paginate={"per_page":20}).configure(phenotype_table)
    variable_dict = {}
    variable_dict["phenotype_table"] = phenotype_table
    variable_dict["object"] = accession
    phenotypes = Phenotype.objects.filter(phenotypevalue__obs_unit__accession_id=pk)
    variable_dict['phenotype_count'] = phenotypes.count()
    variable_dict['to_data'] = phenotypes.values('to_term__name').annotate(count=Count('to_term__name'))
    variable_dict['eo_data'] = phenotypes.values('eo_term__name').annotate(count=Count('eo_term__name'))
    variable_dict['uo_data'] = phenotypes.values('uo_term__name').annotate(count=Count('uo_term__name'))
    return render(request,'phenotypedb/accession_detail.html',variable_dict)