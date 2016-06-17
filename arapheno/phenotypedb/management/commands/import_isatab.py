from django.core.management.base import BaseCommand, CommandError
from utils.isa_tab import parse_isatab, save_isatab


class Command(BaseCommand):
    help = 'Import an ISA-TAB archive into the database'

    def add_arguments(self, parser):
        parser.add_argument('filename')

    def handle(self, *args, **options):
        filename = options['filename']
        try: 
            isatab  = parse_isatab(filename)
            import pdb
            pdb.set_trace()
            studies = save_isatab(isatab)
        except Exception as err:
            raise CommandError('Error importing ISA-TAB file. Reason: %s' % str(err))
        self.stdout.write(self.style.SUCCESS('Successfully imported ISA-TAB archive "%s" under following id %s' % (filename,studies)))