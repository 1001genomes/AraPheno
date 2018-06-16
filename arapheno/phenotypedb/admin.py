from django.contrib import admin
from django.contrib.contenttypes.admin import GenericTabularInline
from phenotypedb.models import Submission, Study, Phenotype, Curation, StudyCuration, PhenotypeCuration
from django.core.mail import EmailMessage
from django.conf import settings
from utils.datacite import submit_submission_to_datacite
from django.contrib.messages import INFO,WARNING, ERROR
from models import PUBLISHED

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
    actions = ['submit_to_datacite']

    def save_model(self, request, obj, form, change):
        super(SubmissionAdmin, self).save_model(request, obj, form, change)
        if change and 'status' in form.changed_data:
            email = EmailMessage(
                    obj.get_email_subject(),
                    obj.get_email_text(),
                    'uemit.seren@gmi.oeaw.ac.at',
                    [obj.email],
                    [settings.ADMINS[0][1]],
                    reply_to=['uemit.seren@gmi.oeaw.ac.at']
                )
            email.send(True)

    def study_name(self, submission):
        """Returns name of the study"""
        return submission.study.name

    def submit_to_datacite(self, request, queryset):
        success = []
        error = []
        for submission in queryset:        
            try:
                if submission.status == PUBLISHED:
                    submit_submission_to_datacite(submission)
                    subccess.append(submission)
            except Exception as err:
                error.append((submission, str(err)))
                
        if len(error) == 0:
            self.message_user(request, "Successuflly sent all selected submissions to datacite", level=INFO)
        else:
            msg = "Not all submissions could be sent to datacite. Following failed:<br>"
            for submission, err in error:
                msg += "<br>%s:%s"  % (submission, err)
            self.message_user(request, msg, level=WARNING)


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


