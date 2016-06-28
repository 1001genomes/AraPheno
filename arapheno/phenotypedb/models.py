from __future__ import unicode_literals
from django.utils.safestring import mark_safe

from django.db import models

'''
Species Model
'''
class Species(models.Model):
    ncbi_id = models.IntegerField(blank=True,null=True) #NCBI Taxonomy ID
    genus = models.CharField(max_length=255)  #Genus, e.g. Arabidopsis
    species = models.CharField(max_length=255) #Species, e.g. thaliana
    description = models.TextField(blank=True,null=True) #short species description


'''
Study Model
each phenotype is grouped into a study and a study is linked to a certain phenotype
'''
class Study(models.Model):
    name = models.CharField(max_length=255) #name of study/experiment
    description = models.TextField(blank=True,null=True) #short study description

    species = models.ForeignKey("Species") #foreign key to species
    publications = models.ManyToManyField("Publication",blank=True)
    
    def __unicode__(self):
        return u"%s (Study)" % (mark_safe(self.name))


'''
Accession Model
'''
class Accession(models.Model):
    name = models.CharField(max_length=255,db_index=True,blank=True,null=True) #accession name if available
    country = models.CharField(max_length=255,blank=True,null=True) #country of accession if available
    sitename = models.TextField(blank=True,null=True) #name of site if available
    collector = models.TextField(blank=True,null=True) #collector if available
    collection_date = models.DateTimeField(blank=True,null=True) #date of phenotype integration/submission
    longitude = models.FloatField(null=True,blank=True,db_index=True) #longitude of accession
    latitude = models.FloatField(null=True,blank=True,db_index=True) #latitude of accession
    cs_number = models.CharField(max_length=255,blank=True,null=True) # Stock center number
    species = models.ForeignKey("Species") #species foreign key    

'''
Observation unit
'''
class ObservationUnit(models.Model):
    accession = models.ForeignKey('Accession') 
    study = models.ForeignKey('Study')

'''
PhenotypeValue
'''
class PhenotypeValue(models.Model):
    
    value = models.FloatField()
    phenotype = models.ForeignKey('Phenotype')
    obs_unit = models.ForeignKey('ObservationUnit')



'''
Phenotype Model
'''
class Phenotype(models.Model):
    doi = models.CharField(max_length=255,db_index=True,null=True,blank=True) #DOI for phenotype
    name = models.CharField(max_length=255,db_index=True) #phenotype name
    scoring = models.TextField(blank=True,null=True) #how was the scoring of the phenotype done
    source = models.TextField(blank=True,null=True) #person who colleted the phenotype. or from which website was the phenotype
    type = models.CharField(max_length=255,blank=True,null=True) #type/category of the phenotype
    growth_conditions = models.TextField(blank=True,null=True) #description of the growth conditions of the phenotype
    shapiro_test_statistic = models.FloatField(blank=True,null=True) #Shapiro Wilk test for normality
    shapiro_p_value = models.FloatField(blank=True,null=True) #p-value of Shapiro Wilk test
    number_replicates = models.IntegerField(default=0) #number of replicates for this phenotype
    integration_date = models.DateTimeField(auto_now_add=True) #date of phenotype integration/submission
    
    eo_term = models.ForeignKey('OntologyTerm',related_name='eo_term',null=True,blank=True)
    uo_term = models.ForeignKey('OntologyTerm',related_name='uo_term',null=True,blank=True)
    to_term = models.ForeignKey('OntologyTerm',related_name='to_term',null=True,blank=True)
    species = models.ForeignKey('Species')
    study = models.ForeignKey('Study')
    dynamic_metainformations = models.ManyToManyField('PhenotypeMetaDynamic')

    def __unicode__(self):
        if self.to_term == None:
            return u"%s (Phenotype)" % (mark_safe(self.name))
        else:
            return u"%s (Phenotype, TO: %s ( %s ))" % (mark_safe(self.name),mark_safe(self.to_term.name),mark_safe(self.to_term.id))


'''
Dynamic Phenotype Meta-Information Model
'''
class PhenotypeMetaDynamic(models.Model):
    phenotype_meta_field = models.CharField(db_index=True, max_length=255) #field/key of the meta field
    phenotype_meta_value = models.TextField() #value of the meta information

    phenotype_public = models.ForeignKey('Phenotype',null=True,blank=True)


'''
Authos Model for Publications
'''
class Author(models.Model):
    firstname = models.CharField(max_length=100,blank=True,null=True) #firstname of author
    lastname = models.CharField(max_length=200,blank=True,null=True,db_index=True) #last name of author
    
    def __unicode__(self):
        return u'%s %s' % (self.firstname, self.lastname)


'''
Publication Model
'''
class Publication(models.Model):
    author_order = models.TextField() #order of author names
    publication_tag = models.CharField(max_length=255) #publication tag
    pub_year = models.IntegerField(blank=True,null=True) #year of publication
    title = models.CharField(max_length=255, db_index=True) #title of publication
    journal = models.CharField(max_length=255) #journal of puplication
    volume = models.CharField(max_length=255,blank=True,null=True) # volume of publication
    pages = models.CharField(max_length=255,blank=True,null=True) # pages
    doi = models.CharField(max_length=255, db_index=True,blank=True,null=True) #doi
    pubmed_id = models.CharField(max_length=255, db_index=True,blank=True,null=True) #pubmed id
    
    authors = models.ManyToManyField("Author") #author link

'''
Ontology Term
'''
class OntologyTerm(models.Model):
    id = models.CharField(max_length=50,primary_key=True)
    name = models.CharField(max_length=255)
    definition = models.TextField(blank=True,null=True)
    comment = models.TextField(blank=True,null=True)
    source = models.ForeignKey('OntologySource')

'''
Ontology Term
'''
class OntologySource(models.Model):
    acronym = models.CharField(max_length=50)
    name = models.CharField(max_length=255)
    url = models.URLField()
