"""
Command Line function to submit Study or Phenotype to datacite
"""
from django.core.management.base import BaseCommand, CommandError
from phenotypedb.models import Study, Phenotype
from utils.datacite import submit_to_datacite



class Command(BaseCommand):
    """
    Command to submit Study or Phenotype to datacite
    """
    help = 'Submit a Study or Phenotype to Datacite'

    def add_arguments(self, parser):
        parser.add_argument('entity', choices=['study', 'phenotype'],
                            help='Specify the entity to export')
        parser.add_argument('--id',
                            dest='entity_id',
                            type=int,
                            default=None,
                            help='Specify a primary key to submit a specific study or phenotype')

    def handle(self, *args, **options):
        entity_id = options['entity_id']
        entity = options['entity']
        try:
            entities = self._get_entities(entity, entity_id)
            success = []
            failed = []
            for entity in entities:
                try:
                    resp = submit_to_datacite(entity)
                    success.append((entity, resp))
                except Exception as err:
                    failed.append((entity, str(err)))
            if len(failed) == 0:
                self.stdout.write(self.style.SUCCESS('Successfully submitted %s %s to datacite' % (len(success), entity)))
            else:
                self.stdout.write(self.style.WARNING('Failed to submit %s of %s %s to datacite' % (len(failed), len(entities), entity)))
            for resp in failed:
                self.stdout.write(self.style.ERROR('%s: %s' % (resp[0], resp[1])))
            self.stdout.write('------------------------------------')
            for resp in success:
                self.stdout.write(self.style.SUCCESS('%s: %s' % (resp[0], resp[1])))

        except Exception as err:
            raise CommandError('Error submitting %s to datacite. Reason: %s' % str(err))

    @classmethod
    def _get_entities(cls, entity, entity_id=None):
        if entity == 'study':
            model = Study.objects
        elif entity == 'phenotype':
            model = Phenotype.objects
        else: raise ValueError('Entity %s not supported' % entity)
        if entity_id is not None:
            return [model.get(pk=entity_id)]
        else:
            return model.all()
