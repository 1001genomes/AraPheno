"""
Command Line Function to submit a Study or Phenotype to Datacite
"""
from django.core.management.base import BaseCommand, CommandError
from phenotypedb.models import Phenotype, Study
from utils.datacite import generate_schema


class Command(BaseCommand):
    """
    Command Line Function to submit a Study or Phenotype to Datacite
    """

    help = 'Export an schema for a Study or Phenotype'

    def add_arguments(self, parser):
        parser.add_argument('id')
        parser.add_argument('--entity',
                            dest='entity',
                            choices=['study', 'phenotype'],
                            required=True,
                            help='Specify the entity to export')

    def handle(self, *args, **options):
        entity_id = options['id']
        entity = options['entity']
        try:
            if entity == 'study':
                obj = Study.objects.get(pk=entity_id)
            elif entity == 'phenotype':
                obj = Phenotype.objects.get(pk=entity_id)
            else:
                raise Exception('Entity %s not supported' % entity)
            schema_content = generate_schema(obj)
            self.stdout.write(schema_content)
        except Exception as err:
            raise CommandError('Error exporting schema file. Reason: %s' % str(err))
