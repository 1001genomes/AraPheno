from autocomplete_light import shortcuts as autocomplete_light

from phenotypedb.models import Phenotype, Study, Accession

class GlobalSearchAutocomplete(autocomplete_light.AutocompleteGenericBase):
    choices = (Phenotype.objects.all(),
               Study.objects.all(),
               Accession.objects.all())
    search_fields = (('name','to_term__id','to_term__name',), #phenotype search field
                     ('name',), #study search field
                     ('name',),) #Accession search field

    attrs = {'placeholder':'Search a phenotype, study, trait ontology (e.g. type FRI for phenotype, Atwell for study, or concentration for ontology) or accession name',
             'data-autocomplete-minimum-characters':1}

    widget_attrs={'data-widget-maximum-values':1,'class':'','style':'width:95%;height:50px'}
    
    #Individual Choice Render Format
    choice_html_format = u"<span class='block' data-value='%s'>%s</span>"
    
    #Render Choide
    def choice_html(self,choice):
        return self.choice_html_format % (self.choice_value(choice),self.choice_label(choice))

    #Render Autocomplete HTML for different search results
    def autocomplete_html(self):
        html = ""
        for choice in self.choices_for_request():
            if isinstance(choice,Phenotype):
                html += ("<a href='phenotype/%d'>%s</a>" % (choice.id,self.choice_html(choice)))
            elif isinstance(choice,Study):
                html += ("<a href='study/%d'>%s</a>" % (choice.id,self.choice_html(choice)))
            elif isinstance(choice,Accession):
                html +=("<a href='accession/%d'>%s</a>" % (choice.id,self.choice_html(choice)))
        return html

autocomplete_light.register(GlobalSearchAutocomplete)

