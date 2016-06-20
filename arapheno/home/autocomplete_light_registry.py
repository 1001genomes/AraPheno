from autocomplete_light import shortcuts as autocomplete_light

from phenotypedb.models import Phenotype, Study, Study

class GlobalSearchAutocomplete(autocomplete_light.AutocompleteGenericBase):
    choices = (Phenotype.objects.all(),
           Study.objects.all())
    search_fields = (('name',), #phenotype search field
                     ('name',)) #study search field

    attrs = {'placeholder':'Search a phenotype or study by name ...',
             'data-autocomplete-minimum-characters':1}

    widget_attrs={'data-widget-maximum-values':1,'class':'','style':'width:95%;height:50px'}

autocomplete_light.register(GlobalSearchAutocomplete)

'''
class GlobalSearchAutocomplete(autocomplete_light.AutocompleteModelBase):
    model = Phenotype
    search_fields = ['name']

    attrs = {'placeholder':'Search a phenotype or study by name ...',
             'data-autocomplete-minimum-characters':1}

    widget_attrs={'data-widget-maximum-values':1,'class':'modern_style autocomplete_style'}

autocomplete_light.register(GlobalSearchAutocomplete)
'''
