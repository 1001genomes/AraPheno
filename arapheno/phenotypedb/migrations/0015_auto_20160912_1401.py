# -*- coding: utf-8 -*-
# Generated by Django 1.9.7 on 2016-09-12 14:01
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('phenotypedb', '0014_auto_20160813_1433'),
    ]

    operations = [
        migrations.AddField(
            model_name='ontologyterm',
            name='children',
            field=models.ManyToManyField(related_name='parents', to='phenotypedb.OntologyTerm'),
        ),
        migrations.AlterField(
            model_name='phenotype',
            name='dynamic_metainformations',
            field=models.ManyToManyField(blank=True, null=True, to='phenotypedb.PhenotypeMetaDynamic'),
        ),
    ]
