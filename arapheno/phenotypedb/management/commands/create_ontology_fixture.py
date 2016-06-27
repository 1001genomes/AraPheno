from django.core.management.base import BaseCommand, CommandError
from utils.data_io import parse_ontology_file, convert_ontologies_to_json
import json

class Command(BaseCommand):
    help = 'Create ontology fixture'

    def add_arguments(self, parser):
        parser.add_argument('filename')
        parser.add_argument('outputfile')
        parser.add_argument('--source',
            dest='ontology_source',
            choices=['TO','EO','UO'],
            required=True,
            help='Specify ontology source')

    def handle(self, *args, **options):

        filename = options['filename']
        outputfile = options['outputfile']
        ontology_source = options['ontology_source']
        try:
            ontologies = convert_ontologies_to_json(parse_ontology_file(filename),ontology_source)
            with open(outputfile,'w') as f:
                json.dump(ontologies,f)
        except Exception as err:
            raise CommandError('Error creating fixture. Reason: %s' % str(err))
        self.stdout.write(self.style.SUCCESS('Successfully created fixture for "%s"' % filename))