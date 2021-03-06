# -*- coding: utf-8 -*-
# Generated by Django 1.9.7 on 2019-07-29 12:33
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('phenotypedb', '0020_auto_20190630_1614'),
    ]

    operations = [
        migrations.CreateModel(
            name='Genotype',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=255)),
                ('type', models.PositiveSmallIntegerField(choices=[(0, 'SNP chip'), (1, 'Full sequence'), (2, 'Imputed full sequence'), (3, 'RNA sequence')], db_index=True)),
                ('accessions', models.ManyToManyField(blank=True, null=True, to='phenotypedb.Accession')),
            ],
        ),
        migrations.AlterField(
            model_name='phenotype',
            name='type',
            field=models.PositiveSmallIntegerField(blank=True, choices=[(0, 'Quantitative'), (1, 'Categorical'), (2, 'Binary')], db_index=True, null=True),
        ),
    ]
