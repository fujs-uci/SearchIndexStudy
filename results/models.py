from django.db import models

# Models Based on a movie dataset
# downloaded from https://www.kaggle.com/rounakbanik/the-movies-dataset


class SearchIndex(models.Model):
    pass


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
    movies = models.ForeignKey('Movies', on_delete=models.CASCADE)

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
    movies = models.ForeignKey('Movies', on_delete=models.CASCADE)

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
