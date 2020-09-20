from django.core.management.base import BaseCommand
from results.search_index import search_index


class Command(BaseCommand):
    help = "Calibrate the database search index"

    def handle(self, *args, **options):
        pass