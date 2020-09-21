from django.core.management.base import BaseCommand
from results.search_index import SearchIndexWrapper


class Command(BaseCommand):
    help = "Calibrate the database search index"

    def handle(self, *args, **options):
        try:
            index = SearchIndexWrapper()
            index.calibrate()

        except Exception:
            pass