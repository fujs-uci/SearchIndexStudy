from django.core.management.base import BaseCommand
from results.models import Movies, MovieGenres, ProductionCompanies, Keywords, Casts, Crews


class Command(BaseCommand):
    help = "Get Database details."

    def handle(self, *args, **options):
        print("{}\n\tDatabase Details\n{}".format("#"*30, "#"*30))
        print("Movies: {}".format(Movies.objects.count()))
        print("MovieGenres: {}".format(MovieGenres.objects.count()))
        print("ProdComps: {}".format(ProductionCompanies.objects.count()))
        print("Keywords: {}".format(Keywords.objects.count()))
        print("Casts: {}".format(Casts.objects.count()))
        print("Crews: {}".format(Crews.objects.count()))
