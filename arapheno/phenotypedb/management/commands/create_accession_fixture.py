from django.core.management.base import BaseCommand, CommandError
from utils.data_io import parseAccessionFile, convertAccessionsToJson
import json



class Command(BaseCommand):
    help = 'Retrieve Accessions data and create fixture'

    def add_arguments(self, parser):
        parser.add_argument('filename')
        parser.add_argument('outputfile')

    def handle(self, *args, **options):
        filename = options['filename']
        outputfile = options['outputfile']
        try: 
            accessions = convertAccessionsToJson(parseAccessionFile(filename))
            with open(outputfile,'w') as f:
                json.dump(accessions,f)
        except Exception as err:
            raise CommandError('Error creating fixture. Reason: %s' % str(err))
        self.stdout.write(self.style.SUCCESS('Successfully created fixture for "%s"' % filename))