import os, csv
from django.core.management.base import BaseCommand, CommandError
from phenotypedb.rest import generate_database_dump
from django.db import transaction


class Command(BaseCommand):
    help = 'Generate database dump for download'


    def handle(self, *args, **options):
        try:
            generate_database_dump()
        except Exception as err:
            raise CommandError('Error generating database dump: %s' % str(err))
        self.stdout.write(self.style.SUCCESS('Successfully generated database dump'))