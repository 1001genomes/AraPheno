"""
Models that are used in the database and application
"""
from __future__ import unicode_literals

import uuid
from datetime import datetime

import pandas as pd

from django.core.exceptions import PermissionDenied
from django.core.urlresolvers import reverse
from django.db import connection, models
from django.utils.safestring import mark_safe
from django.conf import settings

SUBMITTED = 0
IN_CURATION = 1
PUBLISHED = 2

STATUS_CHOICES = (
    (
        (SUBMITTED, 'Submitted'),
        (IN_CURATION, 'Curation'),
        (PUBLISHED, 'Published')
    )
)

class Species(models.Model):
    """
    Species model
    """
    ncbi_id = models.IntegerField(blank=True, null=True) #NCBI Taxonomy ID
    genus = models.CharField(max_length=255)  #Genus, e.g. Arabidopsis
    species = models.CharField(max_length=255) #Species, e.g. thaliana
    description = models.TextField(blank=True, null=True) #short species description

    def __unicode__(self):
        return u"%s %s (%s)" % (self.genus, self.species, self.ncbi_id)


class Curation(models.Model):
    """
    Curation model
    """
    correct = models.BooleanField()
    message = models.TextField(blank=True, null=True)
    timestamp = models.DateTimeField(auto_now_add=True)

    class Meta:
        abstract = True



class StudyCuration(Curation):
    """
    Curation for the study
    """
    study = models.OneToOneField('Study', primary_key=True,related_name="curation")

    def __unicode__(self):
        return u"%s: %s" % (self.study.name, "correct" if self.correct else "incorrect")


class PhenotypeCuration(Curation):
    """
    Curation for the phenotype
    """
    phenotype = models.OneToOneField('Phenotype', primary_key=True,related_name="curation")

    def __unicode__(self):
        return u"%s: %s" % (self.phenotype.name, "correct" if self.correct else "incorrect")


class StudyQuerySet(models.QuerySet):
    """
    Custom QuerySet for Study
    """

    def published(self):
        """
        Returns the published studies
        """
        return self.filter(submission__status=PUBLISHED)

    def curation(self):
        """
        Returns the studies that are being curated
        """
        return self.filter(submission__status=SUBMITTED)

    def submitted(self):
        """
        Returns the studies that have been submitted
        """
        return self.filter(submission__status=Curation)

    def in_submission(self):
        """
        Returns studies that are either being curated or submitted
        """
        return self.exclude(submission__status=PUBLISHED)


class Study(models.Model):
    """
    Study Model
    each phenotype is grouped into a study and a study is linked to a certain phenotype
    """
    name = models.CharField(max_length=255) #name of study/experiment
    description = models.TextField(blank=True, null=True) #short study description

    species = models.ForeignKey("Species") #foreign key to species
    publications = models.ManyToManyField("Publication", blank=True)
    update_date = models.DateTimeField(default=None, null=True, blank=True)
    objects = StudyQuerySet.as_manager()

    def value_as_dataframe(self):
        """
        Returns the PhenotypValue records for this study as a pandas dataframe
        """
        cursor = connection.cursor()
        cursor.execute("""
            SELECT v.id,o.id,o.accession_id,a.name,s.ncbi_id,p.id as phenotype_id,p.name as phenotype_name, v.value
            FROM phenotypedb_phenotypevalue as v
            LEFT JOIN phenotypedb_observationunit o ON v.obs_unit_id = o.id
            LEFT JOIN phenotypedb_phenotype as p ON p.id = v.phenotype_id
            LEFT JOIN phenotypedb_accession as a ON a.id = o.accession_id
            LEFT JOIN phenotypedb_species as s ON s.id = a.species_id
            WHERE p.study_id = %s ORDER BY o.accession_id,p.id ASC """ % self.id)
        data = pd.DataFrame(cursor.fetchall(),
                            columns=['id', 'obs_unit_id', 'accession_id', 'accession_name',
                                     'ncbi_id', 'phenotype_id', 'phenotype_name',
                                     'value']).set_index(['id'])
        return data

    def get_matrix_and_accession_map(self, column='phenotype_name'):
        """Returns both the dataframe and a matrix version of it"""
        data = self.value_as_dataframe()
        data.set_index(['obs_unit_id'], inplace=True)
        df_pivot = data.pivot(columns=column, values='value')
        data.drop(['value', 'phenotype_id', 'phenotype_name'], axis=1, inplace=True)
        data = data[~data.index.duplicated(keep='first')]
        return (data, df_pivot)

    @property
    def count_phenotypes(self):
        """Returns number of phenotypes"""
        return self.phenotype_set.count()

    def save(self, *args, **kwargs):
        self.update_date = datetime.now()
        super(Study, self).save(*args, **kwargs)


    def delete(self, using=None, keep_parents=False):
        if self.submission.status == PUBLISHED:
            raise PermissionDenied('Published studies can not be deleted')
        super(Study, self).delete(using=using, keep_parents=keep_parents)

    def get_absolute_url(self):
        """returns the submission page or study detail page"""
        if self.submission.status != 2:
            return reverse('submission_study_result', args=[str(self.submission.id)])
        else:
            return reverse('study_detail', args=[str(self.pk)])

    @property
    def doi_link(self):
        """Returns the DOI link to datacite"""
        return '%s/%s' % (settings.DATACITE_DOI_URL, self.doi)

    @property
    def doi(self):
        """Returns the DOI"""
        return '%s/study:%s' % (settings.DATACITE_PREFIX, self.id)

    def __unicode__(self):
        return u"%s (Study)" % (mark_safe(self.name))


class Submission(models.Model):
    """
    Submission model
    Each Study has a submission attached to it
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    status = models.PositiveSmallIntegerField(choices=STATUS_CHOICES, default=SUBMITTED, db_index=True)
    submission_date = models.DateTimeField(auto_now_add=True)
    update_date = models.DateTimeField(null=True, blank=True)
    curation_date = models.DateTimeField(null=True, blank=True)
    publication_date = models.DateTimeField(null=True, blank=True)
    publisher = models.CharField(max_length=200)
    firstname = models.CharField(max_length=100) #firstname of author
    lastname = models.CharField(max_length=200) #last name of author
    email = models.CharField(max_length=200) #last name of author


    @property
    def fullname(self):
        """Returns name of the user"""
        return '%s %s' % (self.firstname,self.lastname)


    @property
    def submitted_class(self):
        """Returns css class of the submitted"""
        return self._get_class_for_status(0)

    @property
    def review_class(self):
        """Returns css class of the review"""
        return self._get_class_for_status(1)

    @property
    def published_class(self):
        """Returns css class of the published"""
        return self._get_class_for_status(2)


    def _get_class_for_status(self,status):
        return 'active' if status == self.status else ''

    def get_absolute_url(self):
        """returns the submission page or study detail page"""
        if self.status != 2:
            return reverse('submission_study_result', args=[str(self.id)])
        else:
            return reverse('study_detail', args=[str(self.study.id)])

    def status_text(self):
        """Returns the text version of the numeric status"""
        return STATUS_CHOICES[self.status][1]

    study = models.OneToOneField(
        Study,
        on_delete=models.CASCADE
    )

    def get_email_text(self):
        """returns the email body that will be sent upon submission"""
        return '''
        Dear %(firstname)s %(lastname)s,

        thank you for your submission.
        The "%(study_name)s" study will be curated by one of our admins
        and if it passes the quality assurance, it will be published.
        If there are issues (missing information), we will contact you.

        You can follow the curation process using following URL:
        http://%(submission_url)s/%(submission_id)s

        Thank you for your patience

        Best

        AraPheno Team
        ''' % {'firstname':self.firstname, 'lastname':self.lastname,
               'study_name':self.study.name, 'submission_url':'arapheno.1001genomes.org/submission',
               'submission_id':self.id}

    def __unicode__(self):
        return u'%s by %s %s' % (self.study.name, self.firstname, self.lastname)

class Accession(models.Model):
    """
    Accession models
    """
    name = models.CharField(max_length=255, db_index=True, blank=True, null=True) #accession name if available
    country = models.CharField(max_length=255, blank=True, null=True) #country of accession if available
    sitename = models.TextField(blank=True, null=True) #name of site if available
    collector = models.TextField(blank=True, null=True) #collector if available
    collection_date = models.DateTimeField(blank=True, null=True) #date of phenotype integration/submission
    longitude = models.FloatField(null=True, blank=True, db_index=True) #longitude of accession
    latitude = models.FloatField(null=True, blank=True, db_index=True) #latitude of accession
    cs_number = models.CharField(max_length=255, blank=True, null=True) # Stock center number
    species = models.ForeignKey("Species") #species foreign key


    @property
    def count_phenotypes(self):
        """Returns number of phenotypes"""
        return self.observationunit_set.values('phenotypevalue__phenotype').distinct().count()

    def __unicode__(self):
        return u"%s (Accession)" % (mark_safe(self.name))


class ObservationUnit(models.Model):
    """
    Observational unit model
    Physical plant. This is connected to both the Accession as well as the Study
    """
    accession = models.ForeignKey('Accession')
    study = models.ForeignKey('Study')


class PhenotypeValue(models.Model):
    """
    PhenotypeValue model
    The indivudal phenotype values. Connected to Phenotype and ObservationUnit
    """
    value = models.FloatField()
    phenotype = models.ForeignKey('Phenotype')
    obs_unit = models.ForeignKey('ObservationUnit')

class PhenotypeQuerySet(models.QuerySet):
    """
    Custom QuerySet for Phenotype querires
    """
    def published(self):
        """
        Returns the published phenotypes
        """
        return self.filter(study__submission__status=PUBLISHED)

    def curation(self):
        """
        Returns the phenotypes that are being curated
        """
        return self.filter(study__submission__status=SUBMITTED)

    def submitted(self):
        """
        Returns the phenotypes that have been submitted
        """
        return self.filter(study__submission__status=Curation)

    def in_submission(self):
        """
        Returns studies that are either being curated or submitted
        """
        return self.exclude(study__submission__status=PUBLISHED)

class Phenotype(models.Model):
    """
    Phenotype model
    """
    name = models.CharField(max_length=255, db_index=True) #phenotype name
    scoring = models.TextField(blank=True, null=True) #how was the scoring of the phenotype done
    source = models.TextField(blank=True, null=True) #person who colleted the phenotype. or from which website was the phenotype
    type = models.CharField(max_length=255, blank=True, null=True) #type/category of the phenotype
    growth_conditions = models.TextField(blank=True, null=True) #description of the growth conditions of the phenotype
    shapiro_test_statistic = models.FloatField(blank=True, null=True) #Shapiro Wilk test for normality
    shapiro_p_value = models.FloatField(blank=True, null=True) #p-value of Shapiro Wilk test
    number_replicates = models.IntegerField(default=0) #number of replicates for this phenotype
    integration_date = models.DateTimeField(auto_now_add=True) #date of phenotype integration/submission

    eo_term = models.ForeignKey('OntologyTerm', related_name='eo_term', null=True, blank=True)
    uo_term = models.ForeignKey('OntologyTerm', related_name='uo_term', null=True, blank=True)
    to_term = models.ForeignKey('OntologyTerm', related_name='to_term', null=True, blank=True)
    species = models.ForeignKey('Species')
    study = models.ForeignKey('Study')
    dynamic_metainformations = models.ManyToManyField('PhenotypeMetaDynamic',blank=True,null=True)
    objects = PhenotypeQuerySet.as_manager()
    update_date = models.DateTimeField(default=None, null=True, blank=True)



    def get_absolute_url(self):
        """returns the submission page or phenotype page"""
        if self.study.submission.status != 2:
            return reverse('submission_phenotype_result', args=[str(self.study.submission.id), str(self.id)])
        else:
            return reverse('phenotype_detail', args=[str(self.id)])


    @property
    def doi_link(self):
        """Returns the DOI link to datacite"""
        return '%s/%s' % (settings.DATACITE_DOI_URL, self.doi)

    @property
    def curation_status(self):
        """Returns the status of the curation"""
        if not hasattr(self,'curation') or self.study.submission.status == 0:
            return -1
        return self.curation.correct

    def get_values_for_acc(self,accession_id):
        """
        Retrieves the phenotype value for a specific accession
        """
        return self.phenotypevalue_set.filter(obs_unit__accession_id=accession_id).values_list("value", flat=True)


    @property
    def doi(self):
        """Returns the DOI"""
        return '%s/phenotype:%s' % (settings.DATACITE_PREFIX, self.id)
    #update_date = models.DateTimeField(default=None,null=True,blank=True)

    def __unicode__(self):
        if self.to_term is None:
            return u"%s (Phenotype)" % (mark_safe(self.name))
        else:
            return u"%s (Phenotype, TO: %s ( %s ))" % (mark_safe(self.name), mark_safe(self.to_term.name), mark_safe(self.to_term.id))


class PhenotypeMetaDynamic(models.Model):
    """
    Dynamic Phenotype Meta-Information Model
    """
    phenotype_meta_field = models.CharField(db_index=True, max_length=255) #field/key of the meta field
    phenotype_meta_value = models.TextField() #value of the meta information
    phenotype_public = models.ForeignKey('Phenotype', null=True, blank=True)

    def __unicode__(self):
        return u'%s: %s (%s)' % (self.phenotype_meta_field, self.phenotype_meta_value, self.phenotype_public.name)


class Author(models.Model):
    """
    Author model for Publication
    """
    firstname = models.CharField(max_length=100, blank=True, null=True) #firstname of author
    lastname = models.CharField(max_length=200, blank=True, null=True, db_index=True) #last name of author

    def __unicode__(self):
        return u'%s %s' % (self.firstname, self.lastname)


'''
Publication Model
'''
class Publication(models.Model):
    """
    Publication model
    """
    author_order = models.TextField() #order of author names
    publication_tag = models.CharField(max_length=255) #publication tag
    pub_year = models.IntegerField(blank=True, null=True) #year of publication
    title = models.CharField(max_length=255, db_index=True) #title of publication
    journal = models.CharField(max_length=255) #journal of puplication
    volume = models.CharField(max_length=255, blank=True, null=True) # volume of publication
    pages = models.CharField(max_length=255, blank=True, null=True) # pages
    doi = models.CharField(max_length=255, db_index=True, blank=True, null=True) #doi
    pubmed_id = models.CharField(max_length=255, db_index=True, blank=True, null=True) #pubmed id

    authors = models.ManyToManyField("Author") #author link

    def __unicode__(self):
        return u'%s (%s, %s)' % (self.title, self.journal, self.pub_year)


class OntologyTermQuerySet(models.QuerySet):
    """
    Custom OntologyTerm QuerySet
    """
    def to_terms(self):
        """Retrieve Trait-Ontology terms."""
        return self.filter(source_id=1)
    def eo_terms(self):
        """Retrieve Environment-Ontology terms."""
        return self.filter(source_id=2)
    def uo_terms(self):
        """Retrieve Unit-Ontology terms."""
        return self.filter(source_id=3)


class OntologyTerm(models.Model):
    """OntologyTerm model"""
    id = models.CharField(max_length=50, primary_key=True)
    name = models.CharField(max_length=255)
    definition = models.TextField(blank=True, null=True)
    comment = models.TextField(blank=True, null=True)
    source = models.ForeignKey('OntologySource')
    children = models.ManyToManyField('self', related_name='parents', symmetrical=False)
    
    objects = OntologyTermQuerySet.as_manager()

    def __unicode__(self):
        return '%s (%s)' % (self.name, self.id)

    def get_info_url(self):
        """return the url for more information about the OntologyTerm"""
        return 'https://bioportal.bioontology.org/ontologies/%s?p=classes&conceptid=http://purl.obolibrary.org/obo/%s' % (self.source.acronym, self.id.replace(':', '_'))


'''class OntologyTerm2Term(models.Model):
    """OntologyTerm Many To Many table """
    parent = models.ForeignKey("OntologyTerm",related_name="parent")
    child = models.ForeignKey("OntologyTerm",related_name="child")'''
     



class OntologySource(models.Model):
    """
    OntologySource model
    Type of the ontology (Trait, Environment, etc)
    """
    acronym = models.CharField(max_length=50)
    name = models.CharField(max_length=255)
    url = models.URLField()
    description = models.TextField(null=True)

    def __unicode__(self):
        return '%s (%s)' % (self.name, self.acronym)
