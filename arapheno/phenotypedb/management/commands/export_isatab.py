from django.core.management.base import BaseCommand, CommandError
from utils.isa_tab import export_isatab
from phenotypedb.models import Study


class Command(BaseCommand):
    help = 'Export an ISA-TAB archive from the database'

    def add_arguments(self, parser):
        parser.add_argument('id')

    def handle(self, *args, **options):
        id = options['id']
        try:
            study = Study.objects.get(pk=id)
            isatab_filename  = export_isatab(study)
        except Exception as err:
            raise CommandError('Error exporting ISA-TAB file. Reason: %s' % str(err))
        self.stdout.write(self.style.SUCCESS('Successfully exported ISA-TAB archive to "%s"' % (isatab_filename)))