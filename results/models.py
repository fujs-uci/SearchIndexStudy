from django.db import models
import json


# Models Based on a movie dataset
# downloaded from https://www.kaggle.com/rounakbanik/the-movies-dataset


class SearchIndex(models.Model):
    id = models.AutoField(primary_key=True)
    term_freq = models.TextField(default="{}")
    doc_freq = models.TextField(default="{}")
    tfidf = models.TextField(default="{}")
    alpha = models.TextField(default="{}")

    class Meta:
        db_table = "searchindex"

    def get_term_freq(self):
        return json.loads(self.term_freq)

    def get_doc_freq(self):
        return json.loads(self.doc_freq)

    def get_tfidf(self):
        return json.loads(self.tfidf)

    def get_alpha(self):
        return json.loads(self.alpha)

    def set_term_freq(self, term_freq):
        self.term_freq = term_freq
        self.save()

    def set_doc_freq(self, doc_freq):
        self.doc_freq = doc_freq
        self.save()

    def set_tfidf(self, tfidf):
        self.tfidf = tfidf
        self.save()

    def set_alpha(self, alpha):
        self.alpha = alpha
        self.save()


class Movies(models.Model):
    """
    movies_metadata.csv
    """
    id = models.AutoField(primary_key=True)
    original_title = models.CharField(max_length=200)
    overview = models.TextField()
    tagline = models.TextField()
    title = models.CharField(max_length=200)

    class Meta:
        db_table = "searchindex_movies"

    def get_genres(self):
        movie_genres = self.moviegenres_set.all()
        return [genre.name for genre in movie_genres]

    def get_cast(self):
        movie_cast = self.casts_set.all()
        characters = movie_cast.values_list('character', flat=True)
        name = movie_cast.values_list('name', flat=True)
        return list(characters), list(name)

    def get_crew(self):
        movie_crew = self.crews_set.all()
        name = movie_crew.values_list('name', flat=True)
        return list(name)

    def get_keyword(self):
        movie_keywords = self.keywords_set.all()
        name = movie_keywords.values_list('name', flat=True)
        return list(name)

class MovieGenres(models.Model):
    """
    movies_metadata.genres
    """
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=100)
    movies = models.ManyToManyField('Movies')

    class Meta:
        db_table = "searchindex_genres"


class ProductionCompanies(models.Model):
    """
    movies_metadata.production_companies
    """
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=200)
    movies = models.ManyToManyField('Movies')

    class Meta:
        db_table = "searchindex_production_companies"


class Casts(models.Model):
    """
    credits.cast
    """
    id = models.AutoField(primary_key=True)
    character = models.CharField(max_length=200)
    name = models.CharField(max_length=200)
    movies = models.ManyToManyField('Movies')

    class Meta:
        db_table = "searchindex_casts"


class Crews(models.Model):
    """
    credits.crew
    """
    id = models.AutoField(primary_key=True)
    department = models.CharField(max_length=150)
    job = models.CharField(max_length=150)
    name = models.CharField(max_length=200)
    movies = models.ManyToManyField('Movies')

    class Meta:
        db_table = "searchindex_crews"


class Keywords(models.Model):
    """
    keywords.csv
    """
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=200)
    movies = models.ManyToManyField('Movies')

    class Meta:
        db_table = "searchindex_keywords"
