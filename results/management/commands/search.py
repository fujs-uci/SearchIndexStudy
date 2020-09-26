from django.core.management.base import BaseCommand
from results.search_index import SearchIndexWrapper
from results.models import Movies
import time


class Command(BaseCommand):
    help = "Command to start a search of the database using the Search Index"

    def handle(self, *args, **options):
        """
        Allow user to type a query and return a ranked result intil --quit is initialted
        :param args: None
        :param options: None
        :return: None
        """
        search_index = SearchIndexWrapper()
        while True:
            print("#" * 30)
            query = input("Query: ")
            start_time = time.time()

            if query == "--q":
                print("ending...")
                break
            else:
                movie_id = search_index.lookup(query, limit=5)
                print(movie_id)
                for movie in Movies.objects.filter(id__in=movie_id):
                    print(movie.title)
                print("results: {:.2f} s".format(time.time()-start_time))
                print("#" * 30)

