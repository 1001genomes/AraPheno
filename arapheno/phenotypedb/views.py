"""
View definitions for AraPheno
"""
from django.conf import settings
from django.core.mail import EmailMessage
from django.core.urlresolvers import reverse, reverse_lazy
from django.db.models import Count
from django.http import HttpResponseRedirect
from django.shortcuts import render
from django.views.generic import DetailView
from django.views.generic.edit import DeleteView, UpdateView
from django_tables2 import RequestConfig

from phenotypedb.forms import (CorrelationWizardForm, PhenotypeUpdateForm,
                               StudyUpdateForm, UploadFileForm)
from phenotypedb.models import (Accession, OntologyTerm, Phenotype, Study,
                                Submission)
from phenotypedb.tables import (AccessionTable, CurationPhenotypeTable,
                                PhenotypeTable, ReducedPhenotypeTable,
                                StudyTable)
from scipy.stats import shapiro


# Create your views here.

def list_phenotypes(request):
    """
    Displays table of all published phenotypes
    """
    table = PhenotypeTable(Phenotype.objects.published(), order_by="-name")
    RequestConfig(request, paginate={"per_page":20}).configure(table)
    return render(request, 'phenotypedb/phenotype_list.html', {"phenotype_table":table})


class PhenotypeDetail(DetailView):
    """
    Detailed view for a single phenotype
    """
    model = Phenotype

    def get_context_data(self, **kwargs):
        context = super(PhenotypeDetail, self).get_context_data(**kwargs)
        context['pheno_acc_infos'] = self.object.phenotypevalue_set.prefetch_related('obs_unit__accession')
        context['geo_chart_data'] = Accession.objects.filter(observationunit__phenotypevalue__phenotype_id=1).values('country').annotate(count=Count('country'))
        context['values'] = self.object.phenotypevalue_set.all().values_list("value", flat=True)
        context['shapiro'] = "%.2e"%shapiro(context['values'])[1]
        return context

def list_studies(request):
    """
    Displays table of all published studies
    """
    table = StudyTable(Study.objects.published(), order_by="-name")
    RequestConfig(request, paginate={"per_page":20}).configure(table)
    return render(request, 'phenotypedb/study_list.html', {"study_table":table})


def detail_study(request, pk=None):
    """
    Detailed view of a single study
    """
    study = Study.objects.published().get(id=pk)
    phenotype_table = ReducedPhenotypeTable(Phenotype.objects.published().filter(study__id=pk), order_by="-name")
    RequestConfig(request, paginate={"per_page":20}).configure(phenotype_table)
    variable_dict = {}
    variable_dict["phenotype_table"] = phenotype_table
    variable_dict["study"] = study
    variable_dict['to_data'] = study.phenotype_set.values('to_term__name').annotate(count=Count('to_term__name'))
    variable_dict['eo_data'] = study.phenotype_set.values('eo_term__name').annotate(count=Count('eo_term__name'))
    variable_dict['uo_data'] = study.phenotype_set.values('uo_term__name').annotate(count=Count('uo_term__name'))
    return render(request, 'phenotypedb/study_detail.html', variable_dict)

def correlation_wizard(request):
    """
    Shows the correlation wizard form
    """
    wizard_form = CorrelationWizardForm()
    if "phenotype_search" in request.POST:
        query = request.POST.getlist("phenotype_search")
        query = ",".join(map(str,query))
        return HttpResponseRedirect("/correlation/" + query + "/")
    return render(request, 'phenotypedb/correlation_wizard.html', {"phenotype_wizard":wizard_form})

def correlation_results(request, ids=None):
    """
    Shows the correlation result
    """
    return render(request, 'phenotypedb/correlation_results.html', {"phenotype_ids":ids})

def list_accessions(request):
    """
    Displays table with all accessions
    """
    table = AccessionTable(Accession.objects.all(), order_by="-name")
    RequestConfig(request, paginate={"per_page":20}).configure(table)
    return render(request, 'phenotypedb/accession_list.html', {"accession_table":table})


def detail_accession(request, pk=None):
    """
    Detailed view of a single accession
    """
    accession = Accession.objects.get(id=pk)
    phenotype_table = PhenotypeTable(Phenotype.objects.published().filter(phenotypevalue__obs_unit__accession_id=pk), order_by="-id")
    RequestConfig(request, paginate={"per_page":20}).configure(phenotype_table)
    variable_dict = {}
    variable_dict["phenotype_table"] = phenotype_table
    variable_dict["object"] = accession
    phenotypes = Phenotype.objects.published().filter(phenotypevalue__obs_unit__accession_id=pk)
    variable_dict['phenotype_count'] = phenotypes.count()
    variable_dict['to_data'] = phenotypes.values('to_term__name').annotate(count=Count('to_term__name'))
    variable_dict['eo_data'] = phenotypes.values('eo_term__name').annotate(count=Count('eo_term__name'))
    variable_dict['uo_data'] = phenotypes.values('uo_term__name').annotate(count=Count('uo_term__name'))
    return render(request, 'phenotypedb/accession_detail.html', variable_dict)


class SubmissionStudyDeleteView(DeleteView):
    """
    Confirm view for deleting a submission
    """
    model = Study
    success_url = reverse_lazy('home')
    template_name = 'phenotypedb/submission_confirm_delete.html'

    def get_context_data(self, **kwargs):
        context = super(SubmissionStudyDeleteView, self).get_context_data(**kwargs)
        context['submission'] = self.object.submission
        return context

    def get_object(self, queryset=None):
        return Study.objects.in_submission().get(submission__id=self.kwargs[self.pk_url_kwarg])


class SubmissionStudyResult(UpdateView):
    """
    Displays study information of a Submission
    Used by the user to update the study
    """
    model = Submission
    template_name = 'phenotypedb/submission_update_study_form.html'
    form_class = StudyUpdateForm

    def get_context_data(self, **kwargs):
        context = super(SubmissionStudyResult, self).get_context_data(**kwargs)
        phenotype_table = CurationPhenotypeTable(Phenotype.objects.in_submission().filter(study__id=self.object.id), order_by="-name")
        RequestConfig(self.request, paginate={"per_page":20}).configure(phenotype_table)
        context['curation_phenotype_table'] = phenotype_table
        context['submission'] = self.object.submission
        return context


    def get_object(self, queryset=None):
        return Study.objects.in_submission().get(submission__id=self.kwargs[self.pk_url_kwarg])


class SubmissionPhenotypeResult(UpdateView):
    """
    Displays phenotype information of a Submission
    Used by the user to update the phenotype
    """

    model = Submission
    template_name = 'phenotypedb/submission_update_phenotype_form.html'
    form_class = PhenotypeUpdateForm

    def get_context_data(self, **kwargs):
        context = super(SubmissionPhenotypeResult, self).get_context_data(**kwargs)
        context['submission'] = self.object.study.submission
        context['uo_terms'] = OntologyTerm.objects.uo_terms()
        context['to_terms'] = OntologyTerm.objects.to_terms()
        context['eo_terms'] = OntologyTerm.objects.eo_terms()
        return context


    def get_object(self, queryset=None):
        return Phenotype.objects.in_submission().get(study__submission__id=self.kwargs[self.pk_url_kwarg], pk=int(self.kwargs['phenotype_id']))



def upload_file(request):
    """
    View that is displayed for uploading a study/submission
    """
    if request.method == 'POST':
        form = UploadFileForm(request.POST, request.FILES)
        if form.is_valid():
            try:
                submission = form.save()
                email = EmailMessage(
                    'Study submitted to AraPheno',
                    submission.get_email_text(),
                    'uemit.seren@gmi.oeaw.ac.at',
                    [submission.email],
                    [settings.ADMINS[0][1]],
                    reply_to=['uemit.seren@gmi.oeaw.ac.at']
                )
                email.send(True)
                return HttpResponseRedirect('/submission/%s/' % submission.id)
            except Accession.DoesNotExist as err:
                form.add_error(None, 'Unknown accession with ID: %s' % err.args[-1])
            except Exception as err:
                form.add_error(None, str(err))
    else:
        form = UploadFileForm()
    return render(request, 'home/upload.html', {'form': form})
