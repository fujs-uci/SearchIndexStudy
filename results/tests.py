from django.core.management import call_command
from django.test import TestCase, TransactionTestCase
from results.models import Movies, MovieGenres, ProductionCompanies


##############################
#   Test Models
##############################
class ResultsModelsTestCase(TestCase):
    """
    Test model creation
    """

    def setUp(self):
        # Movies
        mov1 = Movies.objects.create(
            original_title="Movie 1",
            overview="Lorem ipsum dolor sit amet, consectetur adipiscing elit. Pellentesque odio.",
            tagline="Lorem ipsum dolor sit amet, consectetur adipiscing elit. Pellentesque odio.",
            title="The movie 1")
        mov2 = Movies.objects.create(
            original_title="Movie 2",
            overview="Lorem ipsum dolor sit amet, consectetur adipiscing elit. Pellentesque odio.",
            tagline="Lorem ipsum dolor sit amet, consectetur adipiscing elit. Pellentesque odio.",
            title="The movie 2")
        # MovieGenres
        genre1 = MovieGenres.objects.create(name="genre 1")
        genre2 = MovieGenres.objects.create(name="genre 2")
        mov1.moviegenres_set.add(genre1)
        mov2.moviegenres_set.add(genre1, genre2)
        # ProductionCompanies
        prodcomp1 = ProductionCompanies.objects.create(name='PC 1')
        prodcomp2 = ProductionCompanies.objects.create(name='PC 2')
        mov1.productioncompanies_set.add(prodcomp1, prodcomp2)
        mov2.productioncompanies_set.add(prodcomp2)

    def test_models_searchindex(self):
        pass

    def test_models_searchindex_movies(self):
        """
        Test the movie creation and assigning of m2m fields works correctly
        :return: None
        """
        mov1 = Movies.objects.get(id=1)
        mov1_genres = mov1.moviegenres_set.all()
        mov1_prodcomp = mov1.productioncompanies_set.all()
        # Movie
        self.assertIsNotNone(mov1)
        self.assertEquals(mov1.title, "The movie 1")
        # MovieGenre m2m
        self.assertEquals(mov1_genres.count(), 1)
        self.assertEquals(mov1_genres.first(), MovieGenres.objects.get(id=1))
        # ProductionCompany m2m
        self.assertEquals(mov1_prodcomp.count(), 2)
        self.assertEquals(mov1_prodcomp.first(), ProductionCompanies.objects.get(id=1))

    def test_models_searchindex_moviegenres(self):
        """
        Test the MovieGenres creation and m2m fields
        :return: None
        """
        genre1 = MovieGenres.objects.get(id=1)
        genre1_movies = genre1.movies.all()
        # MovieGenres
        self.assertIsNotNone(genre1)
        # MovieGenres m2m
        self.assertEquals(genre1_movies.count(), 2)
        self.assertEquals(genre1_movies.first(), Movies.objects.get(id=1))

    def test_models_searchindex_productioncompanies(self):
        """
        Test the ProductionCompanies creation and m2m fields
        :return: None
        """
        prodcomp1 = ProductionCompanies.objects.get(id=1)
        prodcomp1_movies = prodcomp1.movies.all()
        # ProductionCompanies
        self.assertIsNotNone(prodcomp1)
        # ProductionCompanies m2m
        self.assertEquals(prodcomp1_movies.count(), 1)
        self.assertEquals(prodcomp1_movies.first(), Movies.objects.get(id=1))

    def test_models_searchindex_casts(self):
        pass

    def test_models_searchindex_crews(self):
        pass

    def test_models_searchindex_keywords(self):
        pass


##############################
#   Test manage.py commands
##############################
class CommandsTestCase(TransactionTestCase):
    """
    Test manage.py commands
    """
    def test_load_file(self):
        """
        Testing manage.py load_file command
        Make sure that producing all models from loaded csv files are correct
        :return: None
        """
        args = [
            '--movies=C:\\Users\\fujus\\Documents\\searchindex_project\\dataset\\movies_metadata.csv',
            '--keywords=C:\\Users\\fujus\\Documents\\searchindex_project\\dataset\\keywords.csv',
            '--credits=C:\\Users\\fujus\\Documents\\searchindex_project\\dataset\\credits.csv'
        ]
        opts = {}
        call_command('load_file', *args, **opts)
