from django.core.management import call_command
from django.test import TestCase, TransactionTestCase
from results.models import Movies, MovieGenres, ProductionCompanies, Keywords, SearchIndex
from results.search_index import SearchIndexWrapper
from os import path


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

    def setUp(self):
        args = [
            '--movies=C:\\Users\\fujus\\Documents\\searchindex_project\\dataset\\movies_metadata_test.csv',
            '--keywords=C:\\Users\\fujus\\Documents\\searchindex_project\\dataset\\keywords_test.csv',
            '--credits=C:\\Users\\fujus\\Documents\\searchindex_project\\dataset\\credits_test.csv'
        ]
        opts = {}
        call_command('load_file', *args, **opts)

    def test_load_file_movies(self):
        """
        Testing manage.py load_file command
        Make sure that producing all models from --movies loaded csv files are correct
        :return: None
        """
        # first entry in csv file exists
        movie = Movies.objects.filter(id=862).first()
        self.assertIsNotNone(movie)
        # the movie genres are correct
        movie_genres = movie.moviegenres_set.all()
        self.assertEquals(movie_genres.count(), 3)
        self.assertEquals(movie_genres.first().id, 16)
        # the production companies are correct
        movie_prodcomp = movie.productioncompanies_set.all()
        self.assertEquals(movie_prodcomp.count(), 1)
        self.assertEquals(movie_prodcomp.first().id, 3)

    def test_load_file_keywords(self):
        """
        Testing manage.py load_file command
        Make sure that producing all models from --keywords loaded csv files are correct
        :return: None
        """
        # Movie keywords that exist in csv, exist in database models
        testing_exist = [
            (862, 9, 931, "jealousy"),
            (184402, 2, 154802, "silent film"),
            (174650, 2, 2626, "exorcism")
        ]
        for test_data in testing_exist:
            movie = Movies.objects.get(id=test_data[0])
            movie_keywords = movie.keywords_set.all()
            self.assertEquals(movie_keywords.count(), test_data[1])
            self.assertEquals(movie_keywords.first().id, test_data[2])
            self.assertEquals(movie_keywords.first().name, test_data[3])
        # Movies with no keywords have no keywords in models
        testing_none = [141210, 117500, 61888]
        for test_data in testing_none:
            movie = Movies.objects.get(id=test_data)
            movie_keywords = movie.keywords_set.all()
            self.assertEquals(movie_keywords.count(), 0)

    def test_load_file_credits(self):
        """
        Testing manage.py load_file command
        Make sure that producing all models from --credits loaded csv files are correct
        :return:
        """
        # Known record to have cast and crew models
        movie = Movies.objects.get(id=862)
        m_cast = movie.casts_set.all()
        m_crew = movie.crews_set.all()

        self.assertIsNot(m_cast.count(), 0)
        self.assertIsNot(m_crew.count(), 0)


##############################
#   Test Search Index Wrapper
#   and Calibrate command
##############################
class SearchIndexTestCase(TransactionTestCase):
    """
    Test search_index.py
    """
    def setUp(self):
        args = [
            '--movies=C:\\Users\\fujus\\Documents\\searchindex_project\\dataset\\movies_metadata_test.csv',
            '--keywords=C:\\Users\\fujus\\Documents\\searchindex_project\\dataset\\keywords_test.csv',
            '--credits=C:\\Users\\fujus\\Documents\\searchindex_project\\dataset\\credits_test.csv'
        ]
        opts = {}
        call_command('load_file', *args, **opts)
        self.index = SearchIndexWrapper()
        self.search_index = SearchIndex.objects.all()

    def test_search_index(self):
        """
        Test search index object in db
        :return: None
        """
        self.assertEquals(self.search_index.count(), 1)
        self.assertEquals(self.index.search_index, self.search_index.first())

    def test_search_index_calibrate(self):
        """
        Test calibrate
        :return: None
        """
        search_index_obj = self.search_index.first()
        self.index.calibrate()
        self.assertIsNot(search_index_obj.get_term_freq(), dict())
        self.assertIsNot(search_index_obj.get_doc_freq(), dict())
        self.assertIsNot(search_index_obj.get_tfidf(), dict())


