"""arapheno URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.9/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.conf.urls import url, include
    2. Add a URL to urlpatterns:  url(r'^blog/', include('blog.urls'))
"""
import autocomplete_light.shortcuts as al
import home.views
import phenotypedb.rest as rest
import phenotypedb.views
from django.conf.urls import include, url
from django.contrib import admin
from rest_framework.urlpatterns import format_suffix_patterns
from django.views.decorators.csrf import csrf_exempt
admin.autodiscover()
al.autodiscover()

ID_REGEX = r"[0-9]+"
REGEX_STUDY = ID_REGEX + "|" + rest.DOI_REGEX_STUDY
REGEX_PHENOTYPE = ID_REGEX + "|" + rest.DOI_REGEX_PHENOTYPE
UUID_REGEX = r"[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}"
ONTOLOGY_REGEX = r"(EO|TO|UO){1}:[0-9]*"
ONTOLOGY_SOURCE_REGEX = "(PECO|PTO|UO)"

urlpatterns = [
    url(r'^autocomplete/', include('autocomplete_light.urls')),
    url(r'^$', home.views.home, name="home"),
    url(ur'^search_results/$', home.views.SearchResults, name="searchresults"),
    url(ur'^search_results//$', home.views.SearchResults, name="searchresults"),
    url(ur'^search_results/(?P<query>.*)/$', home.views.SearchResults, name="searchresults"),
    url(r'^phenotypes/$', phenotypedb.views.list_phenotypes, name="phenotypes"),
    url(r'^correlation/$', phenotypedb.views.correlation_wizard, name="correlation-wizard"),
    url(r'^correlation/(?P<ids>[\d,]+)/$', phenotypedb.views.correlation_results, name="correlation-results"),
    url(r'^phenotype/(?P<pk>%s)/$' % ID_REGEX, phenotypedb.views.PhenotypeDetail.as_view(), name="phenotype_detail"),
    url(r'^studies/$', phenotypedb.views.list_studies, name="studies"),
    url(r'^accessions/$', phenotypedb.views.list_accessions, name="accessions"),
    url(r'^accession/(?P<pk>%s)/$' % ID_REGEX, phenotypedb.views.detail_accession, name="accession_detail"),
    url(r'^study/(?P<pk>%s)/$' % ID_REGEX, phenotypedb.views.detail_study, name="study_detail"),
    url(r'^ontology/$', phenotypedb.views.list_ontology_sources,name="ontologysource_list"),
    url(r'^ontology/(?P<acronym>%s)/$' % ONTOLOGY_SOURCE_REGEX, phenotypedb.views.detail_ontology_source,name="ontologysource_detail"),
    url(r'^ontology/(?P<acronym>%s)/(?P<term_id>%s)/$' % (ONTOLOGY_SOURCE_REGEX,ONTOLOGY_REGEX), phenotypedb.views.detail_ontology_source,name="ontology_detail"),
    url(r'^term/(?P<pk>%s)/$' % ONTOLOGY_REGEX, phenotypedb.views.detail_ontology_term,name="term_detail"),
    url(r'^term/$', phenotypedb.views.detail_ontology_term),
    url(r'^about/$', home.views.about),
    url(r'^links/$', home.views.links),
    url(r'^faq/$', home.views.faq),
    url(r'^faq/content/$', home.views.faqcontent),
    url(r'^faq/tutorials/$', home.views.faqtutorial),
    url(r'^faq/rest/$', home.views.faqrest),
    url(r'^faq/rest/swagger/', include('rest_framework_swagger.urls')),
    url(r'^faq/cite/$', home.views.faqcite),
    url(r'^faq/issue/$', home.views.faqissue),
    url(r'^feedback/$', phenotypedb.views.submit_feedback, name="feedback"),
    url(r'^submission/$', phenotypedb.views.upload_file, name="submission"),
    url(r'^submission/(?P<pk>%s)/$' % UUID_REGEX, phenotypedb.views.SubmissionStudyResult.as_view(), name="submission_study_result"),
    url(r'^submission/(?P<pk>%s)/delete/$' % UUID_REGEX, phenotypedb.views.SubmissionStudyDeleteView.as_view(), name="submission_delete"),
    url(r'^submission/(?P<pk>%s)/(?P<phenotype_id>%s)/$' % (UUID_REGEX, ID_REGEX), phenotypedb.views.SubmissionPhenotypeResult.as_view(), name="submission_phenotype_result"),
    url(r'^admin/', include(admin.site.urls))
]
'''
REST URLS
'''


# Required for this http://stackoverflow.com/a/20898410/356594
def method_dispatch(**table):
    def invalid_method(request, *args, **kwargs):
        logger.warning('Method Not Allowed (%s): %s', request.method, request.path,
            extra={
                'status_code': 405,
                'request': request
            }
        )
        return HttpResponseNotAllowed(table.keys())

    def d(request, *args, **kwargs):
        handler = table.get(request.method, invalid_method)
        return handler(request, *args, **kwargs)
    return d


restpatterns = [
    #search
    url(r'^rest/search/$', rest.search),
    url(ur'^rest/search/(?P<query_term>.*)/$', rest.search),

    # phenotype list
    url(r'^rest/phenotype/list/$', rest.phenotype_list),

    # phenotype detail
    url(r'^rest/phenotype/(?P<q>%s)/$' % REGEX_PHENOTYPE, rest.phenotype_detail),

    url(r'^rest/phenotype/(?P<q>%s)/values/$' % REGEX_PHENOTYPE, rest.phenotype_value),
    url(r'^rest/phenotype/(?P<q>%s)/similar/$' % REGEX_PHENOTYPE, rest.phenotype_similar_list),

    url(r'^rest/study/list/$', rest.study_list),
    url(r'^rest/study/(?P<q>%s)/$' % REGEX_STUDY, rest.study_detail),

    url(r'^rest/study/(?P<q>%s)/phenotypes/$' % REGEX_STUDY, rest.study_all_pheno),

    url(r'^rest/study/(?P<q>%s)/values/$' % REGEX_STUDY, rest.study_phenotype_value_matrix),

    url(r'^rest/study/(?P<q>%s)/isatab/$' % REGEX_STUDY, rest.study_isatab),

    url(r'^rest/correlation/(?P<q>[\d,]+)/$', rest.phenotype_correlations),

    url(r'^rest/accession/list/$', rest.accession_list),

    url(r'^rest/accession/phenotypes/$', rest.accessions_phenotypes),

    url(r'^rest/accession/(?P<pk>%s)/$'% ID_REGEX, rest.accession_detail),

    url(r'^rest/accession/(?P<pk>%s)/phenotypes/$' % ID_REGEX, rest.accession_phenotypes),

    url(r'rest/submission/$', rest.submit_study),

    url(r'rest/submission/(?P<pk>%s)/$' % UUID_REGEX, rest.submission_infos,name='submission_infos'),

    url(r'rest/submission/(?P<pk>%s)/delete$' % UUID_REGEX, rest.delete_submission),

    #url(r'rest/submission/(?P<pk>%s)/(?P<phenotype_id>%s)/$' term_id% (UUID_REGEX, ID_REGEX), rest.submission_phenotype_infos),

    url(r'rest/terms/(?P<acronym>%s)/$' % ONTOLOGY_SOURCE_REGEX, rest.ontology_tree_data,name='ontology_tree_root'),

    url(r'rest/terms/(?P<term_id>%s)/$' % ONTOLOGY_REGEX, rest.ontology_tree_data,name='ontology_tree_children')
    #url(r'rest/ontology/(?P<pk>%s)/(?P<term_id>%s)' % ID_REGEX )

]
#extend restpatterns with suffix options
restpatterns = format_suffix_patterns(restpatterns, allowed=['json', 'csv', 'plink', 'zip'])
'''
Add REST patterns to urlpatterns
'''
urlpatterns += restpatterns
