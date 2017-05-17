"""
Command Line function to remove a Study or Phenotype from datacite
"""
from django.core.management.base import BaseCommand, CommandError
from phenotypedb.models import Study, Phenotype
from utils.datacite import remove_from_datacite



class Command(BaseCommand):
    """
    Command to remove Study or Phenotype from datacite
    """
    help = 'Remove a Study or Phenotype from Datacite'

    def add_arguments(self, parser):
        parser.add_argument('entity', choices=['study', 'phenotype'],
                            help='Specify the entity to export')
        parser.add_argument('entity_id',
                            type=int,
                            help='Specify a primary key to submit a specific study or phenotype')

        parser.add_argument('--recursive',
                            dest="recursive",
                            type=bool,
                            default=True,
                            help='Specify wheather to delete also the sub-entitites')

    def handle(self, *args, **options):
        entity_id = options['entity_id']
        entity = options['entity']
        recursive  = options['recursive']
        try:
            entity = self._get_entities(entity, entity_id)
            failed_msg = None
            try:
                sub_entities_failed = remove_from_datacite(entity, recursive)
            except Exception as err:
                failed_msg = str(err)

            if failed_msg is not None:
                self.stdout.write(self.style.ERROR('Failed to remove %s (%s) from datacite' % (entity, entity_id)))
            else:
                if sub_entities_failed > 0:
                    self.stdout.write(self.style.WANRING('Successfully removed %s %s from datacite. But %s sub entities failed to remove' % (entity_id, entity, sub_entities_failed)))
                else:
                    self.stdout.write(self.style.SUCCESS('Successfully removed %s %s from datacite' % (entity_id, entity)))
        except Exception as err:
            raise CommandError('Error submitting %s to datacite. Reason: %s' % str(err))

    @classmethod
    def _get_entities(cls, entity, entity_id):
        if entity == 'study':
            model = Study.objects
        elif entity == 'phenotype':
            model = Phenotype.objects
        else: raise ValueError('Entity %s not supported' % entity)
        return model.get(pk=entity_id)
