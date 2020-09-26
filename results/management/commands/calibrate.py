from django.core.management.base import BaseCommand
from results.search_index import SearchIndexWrapper


class Command(BaseCommand):
    help = "Calibrate the database search index"

    def add_arguments(self, parser):
        """
        Add flags to the command
        :param parser: parser
        :return: None
        """
        parser.add_argument('--print', action='store_true', required=False, help='Print details')

    def handle(self, *args, **options):
        print_info = True if options.get('print') else False
        try:
            index = SearchIndexWrapper()
            index.calibrate(print_info=print_info)

        except Exception:
            pass
