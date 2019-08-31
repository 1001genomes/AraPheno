"""
Autocomplete Light Registry for global search
"""
from autocomplete_light import shortcuts as autocomplete_light
from phenotypedb.models import Accession, Phenotype, Study, OntologyTerm, RNASeq
from django.db.models import Count


class GlobalSearchAutocomplete(autocomplete_light.AutocompleteGenericBase):
    """
    Global search autocomplete configuration class
    """
    choices = (Phenotype.objects.published(),
               Study.objects.published(),
               Accession.objects.all(),
               OntologyTerm.objects.all())
    search_fields = (('name', 'to_term__id', 'to_term__name',), #phenotype search field
                     ('name',), #study search field
                     ('name',), #Accession search field
                     ('name',), #Ontology searhc field
                     ) 

    attrs = {'placeholder':'Search a phenotype, study, trait ontology (e.g. type FRI for phenotype, Atwell for study, or concentration for ontology) or accession name',
             'data-autocomplete-minimum-characters':1}

    widget_attrs = {'data-widget-maximum-values':1, 'class':'', 'style':'width:95%;height:50px'}

    #Individual Choice Render Format
    choice_html_format = u"<span class='block' data-value='%s'>%s</span>"

    #Render Choide
    def choice_html(self, choice):
        return self.choice_html_format % (self.choice_value(choice), self.choice_label(choice))

    #Render Autocomplete HTML for different search results
    def autocomplete_html(self):
        html = ""
        for choice in self.choices_for_request():
            if isinstance(choice, Phenotype):
                html += ("<a href='phenotype/%d'>%s</a>" % (choice.id, self.choice_html(choice)))
            elif isinstance(choice, Study):
                html += ("<a href='study/%d'>%s</a>" % (choice.id, self.choice_html(choice)))
            elif isinstance(choice, Accession):
                html += ("<a href='accession/%d'>%s</a>" % (choice.id, self.choice_html(choice)))
            elif isinstance(choice, OntologyTerm):
                html += ("<a href='ontology/%s/%s'>%s</a>" % (choice.source.acronym,choice.id, self.choice_html(choice)))
        return html

autocomplete_light.register(GlobalSearchAutocomplete)

class RNASeqGlobalSearchAutocomplete(autocomplete_light.AutocompleteGenericBase):
    """
    Global search autocomplete configuration class
    """
    studies = Study.objects.published().annotate(pheno_count=Count('phenotype')).annotate(rna_count=Count('rnaseq'))
    studies = studies.filter(pheno_count=0).filter(rna_count__gt=0)

    choices = (RNASeq.objects,
               studies,
               Accession.objects.all(),)
    search_fields = (('name',), #rnaseq search field
                     ('name',), #study search field
                     ('name',), #Accession search field
                     )

    attrs = {'placeholder':'Search a phenotype, study, trait ontology (e.g. type FRI for phenotype, Atwell for study, or concentration for ontology) or accession name',
             'data-autocomplete-minimum-characters':1}

    widget_attrs = {'data-widget-maximum-values':1, 'class':'', 'style':'width:95%;height:50px'}

    #Individual Choice Render Format
    choice_html_format = u"<span class='block' data-value='%s'>%s</span>"

    #Render Choide
    def choice_html(self, choice):
        return self.choice_html_format % (self.choice_value(choice), self.choice_label(choice))

    #Render Autocomplete HTML for different search results
    def autocomplete_html(self):
        html = ""
        for choice in self.choices_for_request():
            if isinstance(choice, RNASeq):
                html += ("<a href='rnaseq/%d'>%s</a>" % (choice.id, self.choice_html(choice)))
            elif isinstance(choice, Study):
                html += ("<a href='study/%d'>%s</a>" % (choice.id, self.choice_html(choice)))
            elif isinstance(choice, Accession):
                html += ("<a href='accession/%d'>%s</a>" % (choice.id, self.choice_html(choice)))
        return html

autocomplete_light.register(RNASeqGlobalSearchAutocomplete)
