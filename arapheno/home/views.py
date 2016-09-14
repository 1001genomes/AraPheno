from django.shortcuts import render
from django.http import HttpResponseRedirect
from django.db.models import Q

from forms import GlobalSearchForm

from phenotypedb.models import Study, Phenotype, Accession, OntologyTerm
from phenotypedb.tables import PhenotypeTable, StudyTable, AccessionTable, OntologyTermTable

from django_tables2 import RequestConfig

'''
Home View of AraPheno
'''
def home(request):
    search_form = GlobalSearchForm()
    if "global_search-autocomplete" in request.POST:
        query = request.POST.getlist('global_search-autocomplete')[0]
        return HttpResponseRedirect("search_results/%s/"%(query))
    return render(request,'home/home.html',{"search_form":search_form})

'''
About Information View of AraPheno
'''
def about(request):
    return render(request,'home/about.html',{})

'''
FAQ View of AraPhen
'''
def faq(request):
    return render(request,'home/faq.html',{})

'''
FAQ Content View of AraPhen
'''
def faqcontent(request):
    return render(request,'home/faqcontent.html',{})

'''
FAQ Tutorial Content View of AraPhen
'''
def faqtutorial(request):
    return render(request,'home/tutorials.html',{})

'''
FAQ REST Content View of AraPhen
'''
def faqrest(request):
    return render(request,'home/faqrest.html',{})

'''
FAQ Cite Content View of AraPhen
'''
def faqcite(request):
    return render(request,'home/faqcite.html',{})

'''
Search Result View for Global Search in AraPheno
'''
def SearchResults(request,query=None):
    if query==None:
        phenotypes = Phenotype.objects.all()
        studies = Study.objects.all()
        accessions = Accession.objects.all()
        ontologies = OntologyTerm.objects.all()
        download_url = "/rest/search"
    else:
        phenotypes = Phenotype.objects.filter(Q(name__icontains=query) |
                                              Q(to_term__id__icontains=query) |
                                              Q(to_term__name__icontains=query))
        studies = Study.objects.filter(name__icontains=query)
        accessions = Accession.objects.filter(name__icontains=query)
        ontologies = OntologyTerm.objects.filter(name__icontains=query)
        download_url = "/rest/search/" + str(query)
    
    phenotype_table = PhenotypeTable(phenotypes,order_by="-name")
    RequestConfig(request,paginate={"per_page":10}).configure(phenotype_table)
    
    study_table = StudyTable(studies,order_by="-name")
    RequestConfig(request,paginate={"per_page":10}).configure(study_table)

    accession_table = AccessionTable(accessions,order_by="-name")
    RequestConfig(request,paginate={"per_page":10}).configure(accession_table)

    ontologies_table = OntologyTermTable(ontologies,order_by="-name")
    RequestConfig(request,paginate={"per_page":10}).configure(ontologies_table)
    
    variable_dict = {}
    variable_dict['query'] = query
    variable_dict['nphenotypes'] = phenotypes.count()
    variable_dict['phenotype_table'] = phenotype_table
    variable_dict['accession_table'] = accession_table
    variable_dict['ontologies_table'] = ontologies_table
    variable_dict['study_table'] = study_table

    variable_dict['nstudies'] = studies.count()
    variable_dict['naccessions'] = accessions.count()
    variable_dict['nontologies'] = ontologies.count()
    variable_dict['download_url'] = download_url

    return render(request,'home/search_results.html',variable_dict)
