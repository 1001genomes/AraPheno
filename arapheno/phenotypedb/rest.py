from django.http import HttpResponse
#from django.views.decorators.csrf import csrf_exempt
from rest_framework.decorators import api_view, permission_classes, renderer_classes
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticatedOrReadOnly

from rest_framework.renderers import JSONRenderer
from rest_framework.parsers import JSONParser
from rest_framework.views import APIView

from phenotypedb.models import Phenotype, Study
from phenotypedb.serializers import PhenotypeListSerializer, StudyListSerializer
from phenotypedb.serializers import PhenotypeValueSerializer

from phenotypedb.renderer import PhenotypeListRenderer, StudyListRenderer, PhenotypeValueRenderer

import re

#GLOBALS
id_regex = r"^[0-9]+$"
doi_regex = "(10\.[^/]+/([^(\s\>\"\<})])+)"

'''
Search Endpoint
'''
@api_view(['GET'])
@permission_classes((IsAuthenticatedOrReadOnly,))
def search(request,query_term=None,format=None):
    """
    Search for a phenotype or study
    Read-Only Response Supported
    """
    if request.method == "GET":
        if query_term==None:
            studies = Study.objects.all()
            phenotypes = Phenotype.objects.all()
        else:
            studies = Study.objects.filter(name__icontains=query_term)
            phenotypes = Phenotype.objects.filter(name__icontains=query_term)
        study_serializer = StudyListSerializer(studies,many=True)
        phenotype_serializer = PhenotypeListSerializer(phenotypes,many=True)
        return Response({'phenotype_search_results':phenotype_serializer.data,
                         'study_search_results':study_serializer.data})

'''
List all phenotypes 
'''
@api_view(['GET'])
@permission_classes((IsAuthenticatedOrReadOnly,))
@renderer_classes((PhenotypeListRenderer,JSONRenderer))
def phenotype_list(request,q=None,format=None):
    """
    List all available phenotypes
    Read-Only Response Supported
    """
    if not q==None:
        try:
            qfilter = re.search(id_regex,q).group(0)   
            phenotypes = Phenotype.objects.get(pk=qfilter)
            many = False
        except:
            try:
                qfilter = re.search(doi_regex,q).group(0)   
                phenotypes = Phenotype.objects.get(doi=qfilter)
                many = False
            except:
                return HttpResponse(status=404)
    else:
        phenotypes = Phenotype.objects.all()
        many = True
    
    if request.method == "GET":
        serializer = PhenotypeListSerializer(phenotypes,many=many)
        return Response(serializer.data)

'''
Detailed phenotype list via id
'''
@api_view(['GET'])
@permission_classes((IsAuthenticatedOrReadOnly,))
@renderer_classes((PhenotypeValueRenderer,JSONRenderer))
def phenotype_detail(request,q=None,format=None):
    """
    Details of phenotype
    Read-Only Response Supported
    """
    if q==None:
        return HttpResponse(status=404)

    try:
        qfilter = re.search(id_regex,q).group(0)   
        phenotype = Phenotype.objects.get(pk=qfilter)
    except:
        try:
            qfilter = re.search(doi_regex,q).group(0)   
            phenotype = Phenotype.objects.get(doi=qfilter)
        except:
            return HttpResponse(status=404)

    if request.method == "GET":
        pheno_acc_infos = phenotype.phenotypevalue_set.prefetch_related('obs_unit__accession')
        value_serializer = PhenotypeValueSerializer(pheno_acc_infos,many=True)
        return Response(value_serializer.data)

'''
List all studies
'''
@api_view(['GET'])
@permission_classes((IsAuthenticatedOrReadOnly,))
@renderer_classes((StudyListRenderer,JSONRenderer))
def study_list(request,q=None,format=None):
    """
    List all available studies
    Read-Only Response Supported
    """
    if not q==None:
        try:
            qfilter = re.search(id_regex,q).group(0)   
            studies = Study.objects.get(pk=qfilter)
            many = False
        except:
            try:
                qfilter = re.search(doi_regex,q).group(0)   
                studies = Study.objects.get(doi=qfilter)
                many = False
            except:
                return HttpResponse(status=404)
    else:
        studies = Study.objects.all()
        many = True

    if request.method == "GET":
        serializer = StudyListSerializer(studies,many=many)
        return Response(serializer.data)

'''
List all phenotypes for study id/doi
'''
@api_view(['GET'])
@permission_classes((IsAuthenticatedOrReadOnly,))
@renderer_classes((PhenotypeListRenderer,JSONRenderer))
def study_all_pheno(request,q=None,format=None):
    """
    Details of phenotype
    Read-Only Response Supported
    """
    try:
        qfilter = re.search(id_regex,q).group(0)   
        study = Study.objects.get(pk=qfilter)
        many = False
    except:
        try:
            qfilter = re.search(doi_regex,q).group(0)   
            study = Study.objects.get(doi=qfilter)
            many = False
        except:
            return HttpResponse(status=404)

    if request.method == "GET":
        serializer = PhenotypeListSerializer(study.phenotype_set.all(),many=True)
        return Response(serializer.data)

'''
List all phenotype values in big matrix for study id/doi
'''
@api_view(['GET'])
@permission_classes((IsAuthenticatedOrReadOnly,))
@renderer_classes((PhenotypeListRenderer,JSONRenderer))
def study_all_pheno_values(request,pk=None,doi=None,format=None):
    pass
