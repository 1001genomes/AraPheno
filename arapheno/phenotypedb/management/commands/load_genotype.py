import os, csv
from django.core.management.base import BaseCommand, CommandError
from phenotypedb.models import Genotype, Accession
from django.db import transaction


class Command(BaseCommand):
    help = 'Import genotype to accession association'

    def add_arguments(self, parser):
        parser.add_argument('filename', help='filename of the file that contains the accession ids for the genotype')
        parser.add_argument('--genotype',
                            type=int,
                            default=None,
                            required=True,
                            help='Specify a primary key of the genotype to load the data for')

    @transaction.atomic
    def handle(self, *args, **options):
        filename = options['filename']
        genotype_id = options['genotype']
        try:
            if not os.path.exists(filename):
                raise Exception('Filename %s does not exist', filename)
            genotype = Genotype.objects.get(pk=int(genotype_id))
            accession_ids = set([])
            with open(filename, 'rb') as fh:
                reader = csv.reader(fh, delimiter=',')
                next(reader)
                for row in reader:
                    accession_ids.add(int(row[0]))
            for accession_id in accession_ids:
                accession = Accession.objects.get(pk=accession_id)
                genotype.accessions.add(accession)
            genotype.save()
        except Accession.DoesNotExist:
            raise CommandError('Error importing genotype file. Accession: %s not found' % row[0])
        except Exception as err:
            raise CommandError('Error importing genotype file. Reason: %s' % str(err))
        self.stdout.write(self.style.SUCCESS('Successfully imported %s accession for genotype "%s" ' % (len(accession_ids),genotype)))