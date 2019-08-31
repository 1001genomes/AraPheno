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
import django_tables2 as tables

from phenotypedb.forms import (CorrelationWizardForm, PhenotypeUpdateForm,
                               StudyUpdateForm, UploadFileForm, SubmitFeedbackForm,
                               TransformationWizardForm)
from phenotypedb.models import (Accession, OntologyTerm, Phenotype, Study,
                                Submission, OntologySource, Genotype, RNASeq)
from phenotypedb.tables import (AccessionTable, CurationPhenotypeTable,
                                PhenotypeTable, ReducedPhenotypeTable,
                                StudyTable, AccessionPhenotypeTable,
                                RNASeqTable, RNASeqStudyTable)
from scipy.stats import shapiro
import json, itertools
from utils import calculate_phenotype_transformations


# Create your views here.

def list_phenotypes(request):
    """
    Displays table of all published phenotypes
    """
    table = PhenotypeTable(Phenotype.objects.published(), order_by="-name")
    RequestConfig(request, paginate={"per_page":20}).configure(table)
    return render(request, 'phenotypedb/phenotype_list.html', {"phenotype_table":table})

def list_rnaseqs(request):
    """
    Displays table of all published RNASeq
    """
    table = RNASeqTable(RNASeq.objects.all(), order_by="-name")
    RequestConfig(request, paginate={"per_page":50}).configure(table)
    return render(request, 'phenotypedb/rnaseq_data_list.html', {"rnaseq_table":table})

def list_rnaseq_studies(request):
    """
    Displays table of all published RNASeq
    """
    # Only keep rnaseq studies
    # studies = Study.objects.filter(phenotype__count=0)
    studies = Study.objects.annotate(pheno_count=Count('phenotype')).annotate(rna_count=Count('rnaseq'))
    studies = studies.filter(pheno_count=0).filter(rna_count__gt=0)
    table = RNASeqStudyTable(studies, order_by="-name")
    RequestConfig(request, paginate={"per_page":50}).configure(table)
    return render(request, 'phenotypedb/rnaseq_study_list.html', {"study_table":table})

class PhenotypeDetail(DetailView):
    """
    Detailed view for a single phenotype
    """
    model = Phenotype

    def get_context_data(self, **kwargs):
        context = super(PhenotypeDetail, self).get_context_data(**kwargs)
        context['pheno_acc_infos'] = self.object.phenotypevalue_set.select_related('obs_unit__accession')
        context['geo_chart_data'] = Accession.objects.filter(observationunit__phenotypevalue__phenotype_id=1).values('country').annotate(count=Count('country'))
        context['values'] = self.object.phenotypevalue_set.all().values_list("value", flat=True)
        context['shapiro'] = "%.2e"%shapiro(context['values'])[1]
        return context

class RNASeqDetail(DetailView):
    """
    Detailed view for a single RNASeq
    """
    model = RNASeq

    def get_context_data(self, **kwargs):
        context = super(RNASeqDetail, self).get_context_data(**kwargs)
        context['pheno_acc_infos'] = self.object.rnaseqvalue_set.select_related('obs_unit__accession')
        context['geo_chart_data'] = Accession.objects.filter(observationunit__rnaseqvalue__rnaseq_id=1).values('country').annotate(count=Count('country'))
        context['values'] = self.object.rnaseqvalue_set.all().values_list("value", flat=True)
        context['shapiro'] = "%.2e"%shapiro(context['values'])[1]
        return context

def list_studies(request):
    """
    Displays table of all published studies
    """
    table = StudyTable(Study.objects.published(), order_by="-update_date")
    RequestConfig(request, paginate={"per_page":20}).configure(table)
    return render(request, 'phenotypedb/study_list.html', {"study_table":table})


def detail_study(request, pk=None):
    """
    Detailed view of a single study
    """
    study = Study.objects.published().get(id=pk)
    # Check if RNASeq or Phenotypes:
    if len(Phenotype.objects.published().filter(study__id=pk)) > 0:
        phenotype_table = ReducedPhenotypeTable(Phenotype.objects.published().filter(study__id=pk), order_by="-name")
    else:
        phenotype_table = RNASeqTable(RNASeq.objects.filter(study__id=pk), order_by="-name")
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

def transformation_wizard(request):
    """
    Shows the transformation wizard form
    """
    wizard_form = TransformationWizardForm()
    if "phenotype_search" in request.POST:
        query = request.POST.getlist("phenotype_search")
        #query = ",".join(map(str,query))
        return HttpResponseRedirect("/phenotype/" + str(query[0]) + "/transformation/")
    return render(request, 'phenotypedb/transformation_wizard.html', {"transformation_wizard":wizard_form})

def transformation_results(request, pk):
    """
    SHow transformation result
    """
    phenotype = Phenotype.objects.get(id=pk)
    data = calculate_phenotype_transformations(phenotype)
    data['object'] = phenotype
    return render(request, 'phenotypedb/transformation_results.html', data)

def rnaseq_transformation_results(request, pk):
    """
    SHow transformation result
    """
    rnaseq = RNASeq.objects.get(id=pk)
    data = calculate_phenotype_transformations(rnaseq, rnaseq=True)
    data['object'] = rnaseq
    return render(request, 'phenotypedb/rnaseq_transformation_results.html', data)

def list_accessions(request):
    """
    Displays table with all accessions
    """
    # extra_columns = [item.name for item in Genotype.objects.all()]
    # import pdb; pdb.set_trace()
    # extra_columns =[]
    # template = '{{ record.has_genotype(genotype) }}<i class="material-icons dp48">check</i>'
    # for genotype in Genotype.objects.all():
    #     extra_columns.append((genotype.name, tables.TemplateColumn(template, extra_context={'genotype': genotype.pk} )))
    table = AccessionTable(Accession.objects.all(), order_by="-name")
    RequestConfig(request, paginate={"per_page":20}).configure(table)
    return render(request, 'phenotypedb/accession_list.html', {"accession_table":table})


def detail_accession(request, pk=None):
    """
    Detailed view of a single accession
    """
    accession = Accession.objects.get(id=pk)
    phenotype_table = AccessionPhenotypeTable(pk,Phenotype.objects.published().filter(phenotypevalue__obs_unit__accession_id=pk), order_by="-id")
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


def _get_ontology_terms(term,ids = None):
    if not ids:
        ids = [term.id]
    for t in term.children.all():
        ids.append(t.id)
        _get_ontology_terms(t,ids)
    return ids

def _get_db_field_from_source(source):
    if source.acronym == 'PECO':
        return 'eo_term'
    elif source.acronym == 'PTO':
        return 'to_term'
    elif source.acronym == 'UO':
        return 'uo_term'
    else:
        raise Exception('term %s unknown' % source.acronym)


def detail_ontology_term(request,pk=None):
    """
    Detailed view of Ontology
    """
    variable_dict = {}
    phenotypes = []
    if pk is not None:
        term = OntologyTerm.objects.get(pk=pk)
        variable_dict["object"] = term
        db_field = _get_db_field_from_source(term.source) + '_id__in'
        ids = _get_ontology_terms(term)
        #necessary because sqlite has a limit of 999 SQL variables
        ids = [ ids[i:i+500] for i in range(0, len(ids), 500) ]
        for sub in ids:
            kwargs = {db_field:sub}
            phenotypes.extend(Phenotype.objects.published().filter(**kwargs))
    variable_dict['phenotype_count'] = len(phenotypes)
    phenotype_table = PhenotypeTable(phenotypes, order_by="-name")
    RequestConfig(request, paginate={"per_page":20}).configure(phenotype_table)
    variable_dict["phenotype_table"] = phenotype_table
    return render(request, 'phenotypedb/ontologyterm_detail.html', variable_dict)


def list_ontology_sources(request):
    """
    Displays list of ontologies
    """
    return render(request, 'phenotypedb/ontologysource_list.html', {"objects":OntologySource.objects.all()})


def detail_ontology_source(request,acronym,term_id=None):
    """
    Detailed view of OntologySource
    """
    variable_dict = {}
    source = OntologySource.objects.get(acronym=acronym)
    variable_dict['object']  = source
    root_nodes = source.ontologyterm_set.filter(parents=None)
    tree = None
    if term_id is not None:
        tree = []
        term = OntologyTerm.objects.get(pk=term_id)
        tree = _get_tree_to_root(term,root_nodes)
    else:
        tree = [{'id':term.pk,'text':term.name,'children':True if term.children.count() > 0 else False} for term in root_nodes]
    variable_dict['tree'] = json.dumps(tree)
    return render(request, 'phenotypedb/ontologysource_detail.html', variable_dict)


def _get_tree_to_root(term,root_nodes):
    tree = []
    term_obj = {'id':term.id,'text':term.name,'state':{'selected':True},'children':True if term.children.count() > 0 else False}
    parents = term.parents.all()

    while len(parents) > 0:
        parent = parents[0]
        p_obj = {'id':parent.id,'text':parent.name,'children': [term_obj],'state':{'opened':True}}
        for t in parent.children.all():
            if t.id != term_obj['id']:
                p_obj['children'].append({'id':t.id,'text':t.name,'children':True if term.children.count() > 0 else False})
        parents = parent.parents.all()
        term = parent
        term_obj = p_obj

    for t in root_nodes:
        if t.id == term.id:
            tree.append(term_obj)
        else:
            tree.append({'id':t.id,'text':t.name,'children':True if t.children.count() > 0 else False})
    return tree




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
                    submission.get_email_subject(),
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


def submit_feedback(request):
    """
    View to submit issues and feedback
    """
    if request.method == 'POST':
        form = SubmitFeedbackForm(request.POST)
        if form.is_valid():
            try:
                firstname = form.cleaned_data['firstname']
                lastname = form.cleaned_data['lastname']
                from_email = form.cleaned_data['email']
                message = form.cleaned_data['message']
                email = EmailMessage(
                    subject='AraPheno-Feedback',
                    from_email=from_email,
                    to=['uemit.seren@gmi.oeaw.ac.at'],
                    body=message,
                    bcc=[settings.ADMINS[0][1]],
                    reply_to=['uemit.seren@gmi.oeaw.ac.at']
                )
                email.send(True)
                return HttpResponseRedirect('/feedback/success/')
            except Exception as err:
                form.add_error(None, str(err))
    else:
        form = SubmitFeedbackForm()
    return render(request, 'home/feedback.html', {'form': form})


def submit_feedback_success(request):
    return render(request, 'home/feedback_success.html')

def download(request):
    """
    Download data
    """
    return render(request, 'phenotypedb/download.html')
