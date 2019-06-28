from autocomplete_light import shortcuts as autocomplete_light

from phenotypedb.models import Phenotype

class PhenotypeCorrelationAutocomplete(autocomplete_light.AutocompleteModelBase):
    model = Phenotype
    search_fields = ['name']

    attrs = {'placeholder':' Search for phenotype by name ...',
             'data-autocomplete-minimum-characters':1}

    widget_attrs={'data-widget-maximum-values':10,
                  'data-widget-minimum-values':2,
                  'class':'','style':'width:100%;'}
    
    #Individual Choice Render Format
    choice_html_format = u"<span class='block' data-value='%s'>%s</span>"
    
    #Render Choide
    def choice_html(self,choice):
        #return self.choice_html_format % (self.choice_value(choice),self.choice_label(choice))
        return self.choice_html_format % (self.choice_value(choice),choice.name + " (Study: " + choice.study.name + ")")
    
autocomplete_light.register(PhenotypeCorrelationAutocomplete)

class PhenotypeTransformationAutocomplete(autocomplete_light.AutocompleteModelBase):
    model = Phenotype
    search_fields = ['name']

    attrs = {'placeholder':' Search for phenotype by name ...',
             'data-autocomplete-minimum-characters':1}

    widget_attrs={'data-widget-maximum-values':1,
                  'data-widget-minimum-values':1,
                  'class':'','style':'width:100%;'}
    
    #Individual Choice Render Format
    choice_html_format = u"<span class='block' data-value='%s'>%s</span>"
    
    #Render Choide
    def choice_html(self,choice):
        #return self.choice_html_format % (self.choice_value(choice),self.choice_label(choice))
        return self.choice_html_format % (self.choice_value(choice),choice.name + " (Study: " + choice.study.name + ")")
    
autocomplete_light.register(PhenotypeTransformationAutocomplete)
