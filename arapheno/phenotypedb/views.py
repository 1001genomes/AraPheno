from django.shortcuts import get_object_or_404, render
from django.http import HttpResponseRedirect
from django.core.urlresolvers import reverse
from django.views.generic import ListView, DetailView
from django.views.generic.detail import SingleObjectMixin
from models import Phenotype, Study, Accession
from django.db.models import Count

# Create your views here.

class PhenotypeList(ListView):
    model = Phenotype
    context_object_name = 'phenotype_list'    
    paginate_by = 20


class PhenotypeDetail(DetailView):
    model = Phenotype

    def get_context_data(self, **kwargs):
        context = super(PhenotypeDetail, self).get_context_data(**kwargs)
        context['pheno_acc_infos'] = self.object.phenotypevalue_set.prefetch_related('obs_unit__accession')
        context['geo_chart_data'] = Accession.objects.filter(observationunit__phenotypevalue__phenotype_id=1).values('country').annotate(count=Count('country'))
        return context

class StudyList(ListView):
    queryset = Study.objects.all().annotate(phenotype_count=Count('phenotype'))
    context_object_name = 'study_list'
    paginate_by = 20


class StudyDetail(SingleObjectMixin, ListView):
    template_name = 'phenotypedb/study_detail.html'
    paginate_by = 20

    def get(self, request, *args, **kwargs):
        self.object = self.get_object(queryset=Study.objects.all())
        return super(StudyDetail, self).get(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super(StudyDetail, self).get_context_data(**kwargs)
        context['study'] = self.object
        context['to_data'] = self.object.phenotype_set.values('to_term').annotate(count=Count('to_term'))
        context['eo_data'] = self.object.phenotype_set.values('eo_term').annotate(count=Count('eo_term'))
        context['uo_data'] = self.object.phenotype_set.values('uo_term').annotate(count=Count('uo_term'))
        return context

    def get_queryset(self):
        return self.object.phenotype_set.all()
