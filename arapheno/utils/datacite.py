"""
Functions to generate the schema for datacite
"""
#from django.template import Template
from django.template.loader import render_to_string
from django.conf import settings
from phenotypedb.models import Study, Phenotype, PUBLISHED
import requests

def generate_schema(obj):
    """
    Creates XML schema for submitting a study/phenotype to datacite
    """
    if isinstance(obj, Study):
        entity = 'study'
    elif isinstance(obj, Phenotype):
        entity = 'phenotype'
    else:
        raise ValueError('Entity %s not supported' % obj)
    context = {entity:obj}
    return render_to_string('%s_template.xml' % entity, context)

def submit_submission_to_datacite(submission):
    """Register the study and phenotypes of a submission in datacite"""
    if submission.status != PUBLISHED:
        raise Exception("Can only submit to datacite if submission is published")
    study = submission.study
    submit_to_datacite(study)
    for phenotype in study.phenotype_set.all():
        submit_to_datacite(phenotype)

def submit_to_datacite(obj):
    """
    Register a Study or Phenotype with datacite
    """
    auth = (settings.DATACITE_USERNAME, settings.DATACITE_PASSWORD)
    url = settings.DOI_BASE_URL + obj.get_absolute_url()
    data = 'doi=%s\nurl=%s' % (obj.doi, url)
    metadata = generate_schema(obj)

    # if successful send metadata
    response = requests.post('%s/metadata' % settings.DATACITE_REST_URL,
                             auth=auth, data=metadata.encode('utf-8'),
                             headers={'Content-Type':'application/xml;charset=UTF-8'})
    if response.status_code != 201:
        raise Exception('Submitting metadata failed %s' % response.text)


    # send first doi request
    response = requests.post('%s/doi' % settings.DATACITE_REST_URL,
                             auth=auth, data=data,
                             headers={'Content-Type':'text/plain;charset=UTF-8'})

    if response.status_code != 201:
        raise Exception('Creating DOI failed: %s' % response.text)

    return response.text

def remove_from_datacite(obj, recursive):
    """
    Remove a Study or Phenotype with datacite
    """
    auth = (settings.DATACITE_USERNAME, settings.DATACITE_PASSWORD)
    url = settings.DOI_BASE_URL + obj.get_absolute_url()

    failed_sub_entities = 0
    if recursive and isinstance(obj,Study):
        phenotypes = obj.phenotype_set.all()
        try:
            for phenotype in phenotypes:
                remove_from_datacite(phenotype,True)
        except Exception as err:
            failed_sub_entities = failed_sub_entities + 1


    # if successful send metadata
    response = requests.delete('%s/metadata/%s' % (settings.DATACITE_REST_URL,obj.doi),
                             auth=auth,
                             headers={'Content-Type':'application/xml;charset=UTF-8'})
    if response.status_code != 200:
        raise Exception('Making dataset inactive failed %s' % response.text)

    return failed_sub_entities
