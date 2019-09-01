"""
Form and ModelForm definitions
"""
import os,re


from autocomplete_light import shortcuts as autocomplete_light
from django import forms
from django.db import transaction
from phenotypedb.models import Phenotype, Study, Submission, OntologyTerm, PHENOTYPE_TYPE
from utils import import_study, update_study, add_phenotype_ids, add_publication_to_study
from utils.data_io import parse_meta_information_file

TEXT_WIDGET = forms.TextInput(attrs={'class':'validate'})
SUPPORTED_EXTENSION = ('.csv', '.plink', '.zip', '.tar.gz')

ONTOLOGY_ID_REGEX = re.compile(r'(.)*\(([\w]{2}:\d*)\)')

def _validate_file(value):
    extension = os.path.splitext(value.name)[1]
    if extension not in SUPPORTED_EXTENSION:
        raise forms.ValidationError(
            "Wrong file extension. Only %s supported" % ','.join(SUPPORTED_EXTENSION),
            params={'value':value})
    return value

class AutoCompleteModelChoiceField(forms.ModelChoiceField):
    """
    Uses the materializecss autocomplete field
    Needs to parse the string and extract the correct object
    """
    def __init__(self, queryset, empty_label="---------",
                 required=True, widget=None, label=None, initial=None,
                 help_text='', to_field_name=None, limit_choices_to=None,
                 *args, **kwargs):
        widget = forms.TextInput(attrs={'class': 'validate autocomplete'})
        super(AutoCompleteModelChoiceField,self).__init__(queryset, empty_label=empty_label, widget=widget)


    def to_python(self, value):
        match = re.match(ONTOLOGY_ID_REGEX,value)
        if match:
            value = match.group(2)
        if value in self.empty_values:
            return None
        try:
            key = self.to_field_name or 'pk'
            value = self.queryset.get(**{key: value})
        except (ValueError, TypeError, self.queryset.model.DoesNotExist):
            raise forms.ValidationError(self.error_messages['invalid_choice'], code='invalid_choice')
        return value

class CorrelationWizardForm(forms.Form):
    """
    Form for correlation wizard
    """
    # TODO comment out if you get an error during migration
    phenotype_search = autocomplete_light.MultipleChoiceField("PhenotypeCorrelationAutocomplete", required=False)

class TransformationWizardForm(forms.Form):
    """
    Form for correlation wizard
    """
    # TODO comment out if you get an error during migration
    phenotype_search = autocomplete_light.MultipleChoiceField("PhenotypeTransformationAutocomplete", required=False)

class UploadFileForm(forms.ModelForm):
    """
    Form for uploading a study
    """
    file = forms.FileField(validators=[_validate_file])

    class Meta:
        model = Submission
        fields = ['firstname', 'lastname', 'email']
        widgets = {
            'email': forms.EmailInput(attrs={'class':'validate', 'required':True}),
            'firstname': TEXT_WIDGET,
            'lastname': TEXT_WIDGET
        }

    @transaction.atomic
    def save(self, commit=True):
        submission = super(UploadFileForm, self).save(commit=False)
        # import study
        study = import_study(self.cleaned_data['file'])
        submission.study = study
        if commit:
            submission.save()
        return submission


class StudyUpdateForm(forms.ModelForm):
    """
    Form for updating study of a submission
    """
    file = forms.FileField(required=False)
    doi = forms.CharField(widget=forms.TextInput(attrs={'class':'validate', 'required':False}), required=False)
    class Meta:
        model = Study
        fields = ('name', 'description')
        widgets = {
            'name': TEXT_WIDGET,
            'description': forms.Textarea(attrs={'class': 'validate materialize-textarea', 'required':True})
        }

    def __init__(self, *args, **kwargs):
        super(StudyUpdateForm, self).__init__(*args,**kwargs)
        if self.instance.publications.count() > 0:
            self.fields['doi'].initial  = self.instance.publications.all()[0].doi


    @transaction.atomic
    def save(self, commit=True):
        study = super(StudyUpdateForm, self).save(commit)
        study.publications.clear()
        if self.cleaned_data['doi']:
            pub = add_publication_to_study(study, self.cleaned_data['doi'])
        if commit and self.cleaned_data['file']:
            failed_phenotypes = update_study(study.submission.id, self.cleaned_data['file'])
        return study

    def clean(self):
        cd = super(StudyUpdateForm, self).clean()
        try:
            if cd['file'] is not None:
                meta_information = parse_meta_information_file(cd['file'],close_handle=False)
            else:
                return cd
        except Exception as error:
            self.add_error('file', "Format is wrong")
            raise forms.ValidationError('Bulk-update file format is wrong')
        meta_information, failed_phenotypes = add_phenotype_ids(self.instance,meta_information)
        if len(failed_phenotypes) > 0:
            raise forms.ValidationError('Following phenotypes are not found: %s' % ', '.join(failed_phenotypes))
        return cd

class PhenotypeUpdateForm(forms.ModelForm):
    """
    Form for updating phenotype of a submission
    """

    eo_term = AutoCompleteModelChoiceField(OntologyTerm.objects.eo_terms(),empty_label=None)
    to_term = AutoCompleteModelChoiceField(OntologyTerm.objects.to_terms(),empty_label=None)
    uo_term = AutoCompleteModelChoiceField(OntologyTerm.objects.uo_terms(),empty_label=None)

    class Meta:
        model = Phenotype
        fields = ('name', 'scoring', 'type', 'growth_conditions', 'eo_term', 'to_term', 'uo_term')
        widgets = {
            'name': TEXT_WIDGET,
            'scoring': forms.Textarea(attrs={'class': 'validate materialize-textarea', 'required':True}),
            'growth_conditions': forms.Textarea(attrs={'class': 'validate materialize-textarea', 'required':True}),
            'source': TEXT_WIDGET,
            'type': forms.Select(choices=PHENOTYPE_TYPE)
        }

class SubmitFeedbackForm(forms.Form):
    email = forms.EmailField(widget=forms.EmailInput(attrs={'class':'validate', 'required':True}), required=True)
    firstname = forms.CharField(widget=forms.TextInput(attrs={'class':'validate', 'required':True}), required=True)
    lastname = forms.CharField(widget=forms.TextInput(attrs={'class':'validate', 'required':True}), required=True)
    message = forms.CharField(widget=forms.Textarea(attrs={'class':'validate materialize-textarea', 'required':True}), required=True)
