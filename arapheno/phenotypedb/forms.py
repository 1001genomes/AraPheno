from django import forms

from autocomplete_light import shortcuts as autocomplete_light

class CorrelationWizardForm(forms.Form):
    phenotype_search = autocomplete_light.MultipleChoiceField("PhenotypeCorrelationAutocomplete")
