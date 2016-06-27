from django.core.management.base import BaseCommand, CommandError
from utils.data_io import parseAccessionFile, convertAccessionsToJson, parse_country_map
import json



class Command(BaseCommand):
    help = 'Retrieve Accessions data and create fixture'

    def add_arguments(self, parser):
        parser.add_argument('filename')
        parser.add_argument('outputfile')
        parser.add_argument(
            '--country',
            dest='countryfile',
            default=None,
            help='Additional country file to convert country codes',
        )

    def handle(self, *args, **options):
        filename = options['filename']
        outputfile = options['outputfile']
        countryfile = options['countryfile']
        try: 
            country_map = {}
            if countryfile:
                country_map = parse_country_map(countryfile)
            accessions = convertAccessionsToJson(parseAccessionFile(filename),country_map)
            with open(outputfile,'w') as f:
                json.dump(accessions,f)
        except Exception as err:
            raise CommandError('Error creating fixture. Reason: %s' % str(err))
        self.stdout.write(self.style.SUCCESS('Successfully created fixture for "%s"' % filename))