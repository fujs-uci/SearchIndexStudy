from django.core.management.base import BaseCommand
from results.models import Movies, MovieGenres, ProductionCompanies, Keywords, Casts, Crews
import pandas as pd
import numpy as np
import ast


class Command(BaseCommand):
    help = "Loads the file into the database."

    _accepted_columns = {
        1: ['id', 'keywords'],
        2: ['cast', 'crew', 'id'],
        3: ['adult', 'belongs_to_collection', 'budget', 'genres', 'homepage', 'id', 'imdb_id', 'original_language',
            'original_title', 'overview', 'popularity', 'poster_path', 'production_companies', 'production_countries',
            'release_date', 'revenue', 'runtime', 'spoken_languages', 'status', 'tagline', 'title', 'video',
            'vote_average', 'vote_count'],
    }

    def _check(self, num, file):
        """
        3 specific Dataset files are required to run this application
        :param num: int representing the unique file
        :param file: the file path passed through the parser's arguments
        :return: panda dataframe
        """
        df = pd.read_csv(file, low_memory=False)
        if list(df.columns) == self._accepted_columns[num]:
            return df.replace({np.nan: ""})
        else:
            raise Exception('Could not match file. {}'.format(file.split("\\")[-1]))

    def _gen_movies(self, df):
        """
        Bulk create Movie Objects
        :param df: df[['id', 'original_title', 'overview', 'tagline', 'title']]
        :return: None
        """
        bc = list(map(lambda x: Movies(id=x[1][0],
                                       original_title=x[1][1],
                                       overview=x[1][2],
                                       tagline=x[1][3],
                                       title=x[1][4]), df.iterrows()))

        Movies.objects.bulk_create(bc, ignore_conflicts=True)

    def _gen_movie_m2m(self, df, mobject):
        """
        Bulk create Movie's m2m relationships (MovieGenres, ProoductionCompanies, Keywords)
        :param df: df[['id', 'name']]
        :param mobject: Movie's m2m model
        :return: None
        """
        # len(df) * 3 = total db queries; has to be a better way
        for count, item in df.iterrows():
            m_id, insert = item[0], item[1]
            pc_list = ast.literal_eval(insert)
            pc_id_list = [x['id'] for x in pc_list]
            m_obj = Movies.objects.get(id=int(m_id))
            bc = list(map(lambda x: mobject(id=x['id'], name=x['name']), pc_list))

            mobject.objects.bulk_create(bc, ignore_conflicts=True)
            if mobject == MovieGenres:
                m_obj.moviegenres_set.add(*mobject.objects.filter(id__in=pc_id_list))
            elif mobject == ProductionCompanies:
                m_obj.productioncompanies_set.add(*mobject.objects.filter(id__in=pc_id_list))
            elif mobject == Keywords:
                m_obj.keywords_set.add(*mobject.objects.filter(id__in=pc_id_list))

    def _gen_credits(self, df):
        """
        Bulk create Cast and Crew
        :param df: df[['id', 'cast', 'crew']]
        :return: None
        """
        for count, item in df.iterrows():
            raw_cast, raw_crew, m_id = item[0], item[1], item[2]

            cast_list = ast.literal_eval(raw_cast)
            crew_list = ast.literal_eval(raw_crew)
            cast_id_list = [x['id'] for x in cast_list]
            crew_id_list = [x['id'] for x in crew_list]

            m_obj = Movies.objects.get(id=int(m_id))

            cast_obj = list(map(lambda x: Casts(id=x['id'], character=x['character'], name=x['name']),
                                cast_list))
            crew_obj = list(map(lambda x: Crews(id=x['id'], department=x['department'], job=x['job'], name=x['name']),
                                crew_list))

            Casts.objects.bulk_create(cast_obj, ignore_conflicts=True)
            Crews.objects.bulk_create(crew_obj, ignore_conflicts=True)

            m_obj.casts_set.add(*Casts.objects.filter(id__in=cast_id_list))
            m_obj.crews_set.add(*Crews.objects.filter(id__in=crew_id_list))

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

            # Bulk create Movies
            self._gen_movies(df_movies[['id', 'original_title', 'overview', 'tagline', 'title']])
            # Bulk create MovieGenres
            self._gen_movie_m2m(df_movies[['id', 'genres']], MovieGenres)
            # Bulk create ProductionCompanies
            self._gen_movie_m2m(df_movies[['id', 'production_companies']], ProductionCompanies)
            # Bulk create Keywords
            self._gen_movie_m2m(df_keywords, Keywords)
            # Bulk create credits
            self._gen_credits(df_credits)

        except Exception as e:
            pass
