from django.contrib import admin
from django.contrib.contenttypes.admin import GenericTabularInline
from phenotypedb.models import Submission, Study, Phenotype, Curation, StudyCuration, PhenotypeCuration

class StudyCurationInline(admin.StackedInline):
    model = StudyCuration
    can_delete = False
    extra = 0
    max_num = 0

class PhenotypeCurationInline(admin.StackedInline):
    model = PhenotypeCuration
    can_delete = False
    extra = 0
    max_num = 0

@admin.register(Submission)
class SubmissionAdmin(admin.ModelAdmin):
    list_display = ['study_name', 'fullname','status','submission_date','curation_date','update_date','publication_date']
    list_filter = ('status',)
    readonly_fields = ('study',)

    def study_name(self, submission):
        """Returns name of the study"""
        return submission.study.name



@admin.register(Study)
class StudyAdmin(admin.ModelAdmin):
    list_display = ['name', 'description', 'count_phenotypes','curation']
    readonly_fields = ('submission', 'species')
    inlines = [StudyCurationInline, ]


@admin.register(Phenotype)
class PhenotypeAdmin(admin.ModelAdmin):
    list_display = ['name','study','scoring', 'to_term','eo_term','uo_term','curation']
    readonly_fields = ('study',)
    inlines = [PhenotypeCurationInline, ]


