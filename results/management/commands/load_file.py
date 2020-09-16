from django.core.management.base import BaseCommand
from results.models import Movies, MovieGenres, ProductionCompanies
import pandas as pd
import numpy as np
import ast


class Command(BaseCommand):
    help = "Loads the file into the database."

    _accepted_columns = {
        1: str(['id', 'keywords']),
        2: str(['cast', 'crew', 'id']),
        3: str(['adult', 'belongs_to_collection', 'budget', 'genres', 'homepage', 'id',
                'imdb_id', 'original_language', 'original_title', 'overview',
                'popularity', 'poster_path', 'production_companies',
                'production_countries', 'release_date', 'revenue', 'runtime',
                'spoken_languages', 'status', 'tagline', 'title', 'video',
                'vote_average', 'vote_count']),
    }

    def _check(self, num, file):
        """
        3 specific Dataset files are required to run this application
        :param num: int representing the unique file
        :param file: the file path passed through the parser's arguments
        :return: panda dataframe
        """
        df = pd.read_csv(file, low_memory=False)
        if str(list(df.columns)) == self._accepted_columns[num]:
            return df.replace({np.nan: None})
        else:
            raise Exception('Could not match file.')

    def _gen_movies(self, df):
        """
        Bulk create Movie Objects
        :param df: df[['id', 'original_title', 'overview', 'tagline', 'title']]
        :return: None
        """
        df = df.values.tolist()
        bc = list(map(lambda x: Movies(id=x[0],
                                       original_title=x[1],
                                       overview=x[2],
                                       tagline=x[3],
                                       title=x[4]), df))
        Movies.objects.bulk_create(bc)

    def _gen_movie_m2m(self, df, object):
        """
        Bulk create Movie's m2m relationships (MovieGenres, ProoductionCompanies
        :param df: df[['id', 'name']]
        :param object: Movie's m2m model
        :return: None
        """
        df = df.values.tolist()
        # Loop df
        #   each Model in df['field']
        #       create the Model
        #       For each created Model, add to Movie's m2m
        #
        # len(df) * 3 calls to db ; has to be a better way somehow
        for m_id, insert in df:
            pc_list = ast.literal_eval(insert)
            pc_id_list = [x['id'] for x in pc_list]
            m_obj = Movies.objects.get(id=int(m_id))
            bc = list(map(lambda x: object(id=x['id'], name=x['name']), pc_list))

            object.objects.bulk_create(bc, ignore_conflics=True)
            m_obj.add(*object.objects.filter(id__in=pc_id_list))

    def add_arguments(self, parser):
        """
        Add flags to the command
        :param parser: parser
        :return: None
        """
        parser.add_argument('--movies', nargs='?', required=True, help='movies_metadata.csv')
        parser.add_argument('--keywords', nargs='?', required=True, help='keywords.csv')
        parser.add_argument('--credits', nargs='?', required=True, help='credits.csv')

    def handle(self, *args, **options):
        """
        Take files, convert to models. Code is specific to Movie Dataset
        :param options: options['file'] are the csv files to convert to models
        :return: None
        """
        try:
            # Make sure the files passed are the correct files by matching the column names
            df_movies = self._check(3, options['movies'])
            df_keywords = self._check(1, options['keywords'])
            df_credits = self._check(2, options['credits'])

            # Todo convert these to models

            # Bulk create Movies
            self._gen_movies(df_movies[['id', 'original_title', 'overview', 'tagline', 'title']])
            # Bulk create MovieGenres
            self._gen_movie_m2m(df_movies[['id', 'genres']], MovieGenres)
            # Bulk create ProductionCompanies
            self._gen_movie_m2m(df_movies[['id', 'production_companies']], ProductionCompanies)

            print("Success")

        except Exception as e:
            print(e)
