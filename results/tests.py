from django.core.management import call_command
from django.test import TestCase, TransactionTestCase
from results.models import Movies, MovieGenres, ProductionCompanies, Keywords, SearchIndex, Casts, Crews
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
        # Keywords
        keywords1 = Keywords.objects.create(name='movie one')
        keywords2 = Keywords.objects.create(name='mov 1')
        mov1.keywords_set.add(keywords1, keywords2)
        # Casts
        casts1 = Casts.objects.create(character="Charcter 1", name="Actor")
        casts2 = Casts.objects.create(character="Character 2", name="Actress")
        mov1.casts_set.add(casts1, casts2)
        mov2.casts_set.add(casts2)
        # Crews
        crews1 = Crews.objects.create(department="directing", name="crew 1", job="director")
        crews2 = Crews.objects.create(department="writing", name="crew 2", job="screen writer")
        mov1.crews_set.add(crews1)
        mov2.crews_set.add(crews2)

    def test_models_searchindex_movies(self):
        """
        Test the movie creation and assigning of m2m fields works correctly
        :return: None
        """
        mov1 = Movies.objects.filter(id=1).first()
        # Movie
        self.assertIsNotNone(mov1)
        self.assertEquals(mov1.title, "The movie 1")

        mov1_genres = mov1.moviegenres_set.all()
        mov1_prodcomp = mov1.productioncompanies_set.all()
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
        genre1 = MovieGenres.objects.filter(id=1).first()
        # MovieGenres
        self.assertIsNotNone(genre1)

        genre1_movies = genre1.movies.all()
        # MovieGenres m2m
        self.assertEquals(genre1_movies.count(), 2)
        self.assertEquals(genre1_movies.first(), Movies.objects.get(id=1))

    def test_models_searchindex_productioncompanies(self):
        """
        Test the ProductionCompanies creation and m2m fields
        :return: None
        """
        prodcomp1 = ProductionCompanies.objects.filter(id=1).first()
        # ProductionCompanies
        self.assertIsNotNone(prodcomp1)

        prodcomp1_movies = prodcomp1.movies.all()
        # ProductionCompanies m2m
        self.assertEquals(prodcomp1_movies.count(), 1)
        self.assertEquals(prodcomp1_movies.first(), Movies.objects.get(id=1))

    def test_models_searchindex_casts(self):
        """
        Test Casts creation and m2m fields
        :return: None
        """
        cast1 = Casts.objects.filter(id=1).first()
        cast2 = Casts.objects.filter(id=2).first()
        # Casts
        self.assertIsNotNone(cast1)
        self.assertIsNotNone(cast2)

        cast1_mov = cast1.movies.all()
        cast2_mov = cast2.movies.all()
        # Casts m2m
        self.assertEquals(cast1_mov.count(), 1)
        self.assertEquals(cast2_mov.count(), 2)

    def test_models_searchindex_crews(self):
        """
        Test Crews creation and m2m fields
        :return: None
        """
        crew1 = Crews.objects.filter(id=1).first()
        crew2 = Crews.objects.filter(id=2).first()
        # Crews
        self.assertIsNotNone(crew1)
        self.assertIsNotNone(crew2)

        crew1_mov = crew1.movies.all()
        crew2_mov = crew2.movies.all()
        # Crews m2m
        self.assertEquals(crew1_mov.count(), 1)
        self.assertEquals(crew2_mov.count(), 1)

    def test_models_searchindex_keywords(self):
        """
        Test Keywords creation and m2m fields
        :return: None
        """
        keyword1 = Keywords.objects.filter(id=1).first()
        keyword2 = Keywords.objects.filter(id=2).first()
        # Keywords
        self.assertIsNotNone(keyword1)
        self.assertIsNotNone(keyword2)

        keyword1_mov = keyword1.movies.all()
        keyword2_mov = keyword2.movies.all()
        # Keywords m2m
        self.assertEquals(keyword1_mov.count(), 1)
        self.assertEquals(keyword2_mov.count(), 0)


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
        :return: None
        """
        # Known record to have cast and crew models
        movie = Movies.objects.get(id=862)
        m_cast = movie.casts_set.all()
        m_crew = movie.crews_set.all()

        self.assertIsNot(m_cast.count(), 0)
        self.assertIsNot(m_crew.count(), 0)


##############################
#   Test Search Index Wrapper
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
        self.index.calibrate()

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
        search_index_obj = self.index.search_index
        self.assertIsNot(len(search_index_obj.get_term_freq()), 0)
        self.assertIsNot(len(search_index_obj.get_doc_freq()), 0)
        self.assertIsNot(len(search_index_obj.get_tfidf()), 0)

    def test_search_index_ranked_results(self):
        """
        Test search index lookup
        :return: None
        """
        # Search Title
        results_title = self.index.lookup("Toy Story")
        self.assertEquals(results_title, ['862'])
        # Search Character
        results_character = self.index.lookup("buzz lightyear")
        self.assertEquals(results_character, ['862'])
        # Search Actor Name
        results_actor = self.index.lookup("Tom Hanks")
        self.assertEquals(results_actor, ['862'])
