from django.http import HttpResponse
from django.db.models import Q
from django.http import FileResponse

from rest_framework.decorators import api_view, permission_classes, renderer_classes
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticatedOrReadOnly

from rest_framework.renderers import JSONRenderer
from rest_framework.parsers import JSONParser
from rest_framework.views import APIView

from phenotypedb.models import Phenotype, Study, PhenotypeValue
from phenotypedb.serializers import PhenotypeListSerializer, StudyListSerializer
from phenotypedb.serializers import PhenotypeValueSerializer, ReducedPhenotypeValueSerializer

from phenotypedb.renderer import PhenotypeListRenderer, StudyListRenderer, PhenotypeValueRenderer, PhenotypeMatrixRenderer, IsaTabFileRenderer
from phenotypedb.renderer import PLINKRenderer
from utils.isa_tab import export_isatab

import scipy as sp
import scipy.stats as stats

import re,os,array

# based on this https://doeidoei.wordpress.com/2009/10/22/regular-expression-to-match-a-doi-digital-object-identifier/
#doi_regex = r"10.\d{4,9}\/[-._;()/:A-Za-z0-9]+"
# () cauases issues in REST Django swagger
doi_regex = r"10.\d{4,9}\/[-._;/:A-Za-z0-9]+"

doi_pattern = re.compile(doi_regex)

'''
Search Endpoint
'''
@api_view(['GET'])
@permission_classes((IsAuthenticatedOrReadOnly,))
def search(request,query_term=None,format=None):
    """
    Search for a phenotype or study
    ---
    parameters:
        - name: query_term
          description: the search term
          required: true
          type: string
          paramType: path

    serializer: PhenotypeListSerializer
    omit_serializer: false

    produces:
        - text/csv
        - application/json
    """
    if request.method == "GET":
        if query_term==None:
            studies = Study.objects.all()
            phenotypes = Phenotype.objects.all()
        else:
            studies = Study.objects.filter(name__icontains=query_term)
            phenotypes = Phenotype.objects.filter(Q(name__icontains=query_term) |
                                                  Q(to_term__id__icontains=query_term) |
                                                  Q(to_term__name__icontains=query_term))
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
def phenotype_list(request,format=None):
    """
    List all available phenotypes
    ---
    serializer: PhenotypeListSerializer
    omit_serializer: false

    produces:
        - text/csv
        - application/json
    """
    phenotypes = Phenotype.objects.all()
    
    if request.method == "GET":
        serializer = PhenotypeListSerializer(phenotypes,many=True)
        return Response(serializer.data)


'''
Detail information about phenotype
'''
@api_view(['GET'])
@permission_classes((IsAuthenticatedOrReadOnly,))
@renderer_classes((PhenotypeListRenderer,JSONRenderer))
def phenotype_detail(request,q,format=None):
    """
    Detailed information about the phenotype
    ---
    parameters:
        - name: q
          description: the id or doi of the phenotype
          required: true
          type: string
          paramType: path

    serializer: PhenotypeListSerializer
    omit_serializer: false

    produces:
        - text/csv
        - application/json

    """
    doi = _is_doi(q)
    try:
        if doi:
            phenotype = Phenotype.objects.get(doi=q)
        else:
            phenotype = Phenotype.objects.get(pk=int(q))
    except:
        return HttpResponse(status=404)

    if request.method == "GET":
        serializer = PhenotypeListSerializer(phenotype,many=False)
        return Response(serializer.data)


'''
Get all phenotype values
'''
@api_view(['GET'])
@permission_classes((IsAuthenticatedOrReadOnly,))
@renderer_classes((PhenotypeValueRenderer,JSONRenderer,PLINKRenderer,))
def phenotype_value(request,q,format=None):
    """
    List of the phenotype values
    ---
    parameters:
        - name: q
          description: the id or doi of the phenotype
          required: true
          type: string
          paramType: path

    serializer: PhenotypeValueSerializer
    omit_serializer: false

    produces:
        - text/csv
        - application/json
    """
    doi = _is_doi(q)
    try:
        if doi:
            phenotype = Phenotype.objects.get(doi=q)
        else:
            phenotype = Phenotype.objects.get(pk=int(q))
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
def study_list(request,format=None):
    """
    List all available studies
    ---

    serializer: StudyListSerializer
    omit_serializer: false

    produces:
        - text/csv
        - application/json
    """
    studies = Study.objects.all()
    if request.method == "GET":
        serializer = StudyListSerializer(studies,many=True)
        return Response(serializer.data)


'''
Get detailed information about study
'''
@api_view(['GET'])
@permission_classes((IsAuthenticatedOrReadOnly,))
@renderer_classes((StudyListRenderer,JSONRenderer))
def study_detail(request,q,format=None):
    """
    Retrieve detailed information about the study
    ---

    serializer: StudyListSerializer
    omit_serializer: false

    produces:
        - text/csv
        - application/json
    """
    doi = _is_doi(q)
    try:
        if doi:
            study = Study.objects.get(doi=q)
        else:
            study = Study.objects.get(pk=int(q))
    except:
        return HttpResponse(status=404)

    if request.method == "GET":
        serializer = StudyListSerializer(study,many=False)
        return Response(serializer.data)


'''
List all phenotypes for study id/doi
'''
@api_view(['GET'])
@permission_classes((IsAuthenticatedOrReadOnly,))
@renderer_classes((PhenotypeListRenderer,JSONRenderer,))
def study_all_pheno(request,q=None,format=None):
    """
    List all phenotypes for a study
    ---

    serializer: PhenotypeListSerializer
    omit_serializer: false

    produces:
        - text/csv
        - application/json
    """
    doi = _is_doi(q)
    try:
        if doi:
            study = Study.objects.get(doi=q)
        else:
            study = Study.objects.get(pk=int(q))
    except:
        return HttpResponse(status=404)

    if request.method == "GET":
        serializer = PhenotypeListSerializer(study.phenotype_set.all(),many=True)
        return Response(serializer.data)

'''
List phenotype value matrix for entire study
'''
@api_view(['GET'])
@permission_classes((IsAuthenticatedOrReadOnly,))
@renderer_classes((PhenotypeMatrixRenderer,JSONRenderer))
def study_phenotype_value_matrix(request,q,format=None):
    """
    Phenotype value matrix for entire study
    ---
    parameters:
        - name: q
          description: the primary id or doi of the study
          required: true
          type: string
          paramType: path

    produces:
        - text/csv
        - application/json
    """
    doi = _is_doi(q)
    try:
        if doi:
            study = Study.objects.get(doi=q)
        else:
            study = Study.objects.get(pk=int(q))
    except:
        return HttpResponse(status=404)

    if request.method == "GET":
        df = study.value_as_dataframe()
        data = _convert_dataframe_to_list(df)
        return Response(data)

'''
Corrleation Matrix for selected phenotypes 
'''
@api_view(['GET'])
@permission_classes((IsAuthenticatedOrReadOnly,))
@renderer_classes((JSONRenderer,))
def phenotype_correlations(request,q=None):
    """
    Return data for phenotype-phenotype correlations and between phenotype accession overlap
    ---
    serializer: JSONRenderer

    produces:
        - application/json
    """
    #id string to list
    pids = map(int,q.split(","))
    pheno_dict = {}
    for i,pid in enumerate(pids):
        try:
            phenotype = Phenotype.objects.get(pk=pid)
        except:
            return Response({'message':'FAILED','not_found':pid})
        pheno_acc_infos = phenotype.phenotypevalue_set.prefetch_related('obs_unit__accession')
        values = sp.array(pheno_acc_infos.values_list('value',flat=True))
        samples = sp.array(pheno_acc_infos.values_list('obs_unit__accession__id',flat=True))
        name = str(phenotype.name.replace("<i>","").replace("</i>","") + " (" + str(phenotype.study.name) + ")")
        pheno_dict[str(phenotype.name) + "_" + str(phenotype.study.name) + "_" + str(i)] = {'samples':samples,
                                                                                            'y':values,
                                                                                            'name':name,
                                                                                            'id':str(phenotype.id)}
                                                                                            #str(phenotype.name) + "_" + str(phenotype.study.name) + "_" + str(i)}
    #compute correlation matrix
    corr_mat = sp.ones((len(pheno_dict),len(pheno_dict))) * sp.nan
    spear_mat = sp.ones((len(pheno_dict),len(pheno_dict))) * sp.nan
    pheno_keys = pheno_dict.keys()
    axes_data = []
    scatter_data = []
    sample_data = []
    slabels = {}
    for i,pheno1 in enumerate(pheno_keys):
        axes_data.append({"label":pheno_dict[pheno1]['name'],
                          "index":str(i),
                          "pheno_id":str(pheno_dict[pheno1]['id'])})
        samples1 = pheno_dict[pheno1]['samples']
        y1 = pheno_dict[pheno1]['y']
        #store scatter data
        scatter_data.append({"label":pheno_dict[pheno1]['name'],
                             "pheno_id":str(pheno_dict[pheno1]['id']),
                             "samples": samples1.tolist(),
                             "values":y1.tolist()})
        
        for j,pheno2 in enumerate(pheno_keys):
            samples2 = pheno_dict[pheno2]['samples']
            y2 = pheno_dict[pheno2]['y']
            #match accessions
            ind = (sp.reshape(samples1,(samples1.shape[0],1))==samples2).nonzero()
            y_tmp = y1[ind[0]]
            y2 = y2[ind[1]]
            if y1.shape[0]>0 and y2.shape[0]>0:
                corr_mat[i][j] = stats.pearsonr(y_tmp.flatten(),y2.flatten())[0]
                spear_mat[i][j] = stats.spearmanr(y_tmp.flatten(),y2.flatten())[0]
            #compute sample intersections
            if pheno1==pheno2:
                continue
            if pheno1 + "_" + pheno2 in slabels:
                continue
            if pheno2 + "_" + pheno1 in slabels:
                continue
            slabels[pheno1 + "_" + pheno2] = True
            A = samples1.shape[0]
            B = samples2.shape[0]
            C = sp.intersect1d(samples1,samples2).shape[0]
            sample_data.append({"labelA":pheno_dict[pheno1]['name'],
                                "labelA_id":pheno_dict[pheno1]['id'],
                                "labelB":pheno_dict[pheno2]['name'],
                                "labelB_id":pheno_dict[pheno2]['id'],
                                "A":A, "B":B, "C":C})
    data = {}
    data['axes_data'] = axes_data
    data['scatter_data'] = scatter_data
    data['sample_data'] = sample_data
    data['corr_mat'] = str(corr_mat.tolist()).replace("nan","NaN")
    data['spear_mat'] = str(spear_mat.tolist()).replace("nan","NaN")
    
    if request.method == "GET":
        return Response(data)


'''
Returns ISA-TAB archive
'''
@api_view(['GET'])
@permission_classes((IsAuthenticatedOrReadOnly,))
@renderer_classes((IsaTabFileRenderer,JSONRenderer))
def study_isatab(request,q,format=None):
    """
    Generate ISA-TAB archive for a study
    ---
    parameters:
        - name: q
          description: the primary id or doi of the study
          required: true
          type: string
          paramType: path

    produces:
        - application/zip
    """
    doi = _is_doi(q)
    try:
        if doi:
            study = Study.objects.get(doi=q)
        else:
            study = Study.objects.get(pk=int(q))
    except:
        return HttpResponse(status=404)

    isa_tab_file = export_isatab(study)
    zip_file = open(isa_tab_file, 'rb')
    response = FileResponse(zip_file,content_type='application/zip')
    #response = HttpResponse(FileWrapper(zip_file), content_type='application/zip',content_transfer_encoding='binary')
    response.setdefault('Content-Transfer-Encoding','binary')
    response['Content-Disposition'] = 'attachment; filename="isatab_study_%s.zip"' % study.id
    os.unlink(isa_tab_file)
    return response



def _convert_dataframe_to_list(df):
    df_pivot = df.pivot(index='obs_unit_id',columns='phenotype_name', values='value').fillna('')
    data = []
    headers = df_pivot.columns.tolist()
    for obs_unit_id,row in df_pivot.iterrows():
        info = df.ix[obs_unit_id]
        accession_id = info.accession_id
        accession_name = info.accession_name
        csv_row = {'obs_unit_id':obs_unit_id,'accession_id':accession_id,'accession_name':accession_name}
        for i,value in enumerate(row.values):
            csv_row[headers[i]] = value
        data.append(csv_row)
    return data



def _is_doi(term):
    return doi_pattern.match(term)
