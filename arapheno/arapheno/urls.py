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
from django.conf.urls import url,include
from django.contrib import admin

from rest_framework.urlpatterns import format_suffix_patterns

import home.views
import phenotypedb.views
import phenotypedb.rest as rest
from phenotypedb.rest import doi_regex

import autocomplete_light.shortcuts as al
al.autodiscover()

id_regex = r"[0-9]+"
regex =id_regex +"|" + doi_regex

urlpatterns = [
    url(r'^autocomplete/', include('autocomplete_light.urls')),
    url(r'^$',home.views.home),
    url(ur'search_results/$',home.views.SearchResults,name="searchresults"),
    url(ur'search_results//$',home.views.SearchResults,name="searchresults"),
    #url(r'search_results/(?P<query>[\w.@-_?!$&/\=]+)/$',home.views.SearchResults,name="searchresults"),
    url(ur'search_results/(?P<query>.*)/$',home.views.SearchResults,name="searchresults"),
    url(r'phenotypes/$',phenotypedb.views.PhenotypeList,name="phenotypes"),
    url(r'phenotype/(?P<pk>%s)/$' % id_regex,phenotypedb.views.PhenotypeDetail.as_view(),name="phenotype_detail"),
    url(r'studies/$',phenotypedb.views.StudyList,name="studies"),
    url(r'study/(?P<pk>%s)/$' % id_regex,phenotypedb.views.StudyDetail,name="study_detail"),
    url(r'about/$',home.views.about),
    url(r'faq/$',home.views.faq),
    url(r'faq/content/$',home.views.faqcontent),
    url(r'faq/tutorials/$',home.views.faqtutorial),
    url(r'faq/rest/$',home.views.faqrest),
    url(r'^faq/rest/swagger/',include('rest_framework_swagger.urls')),
    url(r'faq/cite/$',home.views.faqcite),
]
'''    
REST URLS
'''
restpatterns = [
    #search
    url(r'rest/search/$',rest.search),
    url(ur'rest/search/(?P<query_term>.*)/$',rest.search),

    # phenotype list
    url(r'rest/phenotype/list/$',rest.phenotype_list),

    # phenotype detail
    url(r'rest/phenotype/(?P<q>%s)/$' % regex,rest.phenotype_detail),

    url(r'rest/phenotype/(?P<q>%s)/values/$' %regex,rest.phenotype_value),

    url(r'rest/study/list/$',rest.study_list),
    url(r'rest/study/(?P<q>%s)/$' % regex,rest.study_detail),

    url(r'rest/study/(?P<q>%s)/phenotypes/$' %regex,rest.study_all_pheno),

    url(r'rest/study/(?P<q>%s)/values/$' % regex,rest.study_phenotype_value_matrix),

    url(r'rest/study/(?P<q>%s)/isatab/$' % regex,rest.study_isatab),

]
#extend restpatterns with suffix options
restpatterns = format_suffix_patterns(restpatterns,allowed=['json','csv','plink','zip'])
'''
Add REST patterns to urlpatterns
'''
urlpatterns += restpatterns

