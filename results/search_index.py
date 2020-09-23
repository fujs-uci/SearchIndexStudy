from .models import SearchIndex, Movies
import json
import time
from decimal import Decimal as _d, Context, ROUND_05UP
from math import log


class WordProcessor:
    """
    Enter in a corpus
    return a list of k-phrases
    """

    def __init__(self, k):
        self.k = k  # k is the maximum length for a phrase
        self.stop_words = ['a', 'able', 'about', 'across', 'after', 'all', 'almost', 'also', 'am', 'among', 'an', 'and',
                           'any', 'are', 'as', 'at', 'be', 'because', 'been', 'but', 'by', 'can', 'cannot', 'could',
                           'dear', 'did', 'do', 'does', 'either', 'else', 'ever', 'every', 'for', 'from', 'get', 'got',
                           'had', 'has', 'have', 'he', 'her', 'hers', 'him', 'his', 'how', 'however', 'i', 'if', 'in',
                           'into', 'is', 'it', 'its', 'just', 'least', 'let', 'like', 'likely', 'may', 'me', 'might',
                           'most', 'must', 'my', 'neither', 'no', 'nor', 'not', 'of', 'off', 'often', 'on', 'only',
                           'or', 'other', 'our', 'own', 'rather', 'said', 'say', 'says', 'she', 'should', 'since', 'so',
                           'some', 'than', 'that', 'the', 'their', 'them', 'then', 'there', 'these', 'they', 'this',
                           'tis', 'to', 'too', 'twas', 'us', 'wants', 'was', 'we', 'were', 'what', 'when', 'where',
                           'which', 'while', 'who', 'whom', 'why', 'will', 'with', 'would', 'yet', 'you', 'your']

    def tokenize(self, corpus):
        """
        Split the corpus by words, removing special characters & stop words
        generate addition k-phrases added to list, order matters
        len(corpus) = # words
        :param corpus: str
        :return: list of str
        """
        # Gonna do a ugly brute force method for the sake of getting this done
        k_phrases = []
        corpus_remove_stop = ["".join(char for char in word if char.isalnum()).lower()
                              for word in corpus.split(" ")
                              if word not in self.stop_words]
        for k in range(self.k):
            index = 0
            while index + k + 1 <= len(corpus_remove_stop):
                k_phrases.append(" ".join(corpus_remove_stop[index:index + k + 1]))
                index += 1

        return k_phrases

    def tokenize_character(self, list_corpus):
        """
        Character names are iconic and offer a lot of valuable information
        Processing the list of names separately
        For each name, remove useless info and get combination of name
        :param list_corpus: list of str
        :return: list of string
        """
        k_phrases = []
        for name in list_corpus:
            k_phrases += self.tokenize(name)
        return k_phrases


class SearchIndexWrapper:
    """
    Search Index Wrapper:
        create the index
        calibrate the index
        return ranked results
    """
    @staticmethod
    def _create_or_get():
        """
        Makes sure there is only one instance of SearchIndex
        :return: SearchIndex
        """
        s_index = SearchIndex.objects.filter(id=1)
        if s_index.first() is None:
            return SearchIndex.objects.create(id=1)
        else:
            return s_index.first()

    @staticmethod
    def _default_alpha():
        """
        My default alpha settings
        Sets the priority of terms depending on where they are match in the movie corpus
        :return: str (json decodable)
        """
        alpha = {
            '0': 0.25,  # Movie.title
            '1': 0.20,  # Movie.original_title
            '2': 0.05,  # Movie.overview
            '3': 0.05,  # Movie.tagline
            '4': 0.05,  # Genre.name
            '6': 0.07,  # Cast.character
            '7': 0.07,  # Cast.name
            '8': 0.05,  # Crew.name
            '9': 0.15,  # Keyword.name
        }
        return json.dumps(alpha)

    def __init__(self):
        self.search_index = self._create_or_get()
        self.search_index.set_alpha(self._default_alpha())
        self.process = WordProcessor(k=3)
        self.total_movies = Movies.objects.count()

    def _tf(self, term_list):
        """
        turn the list into a dict where key = term and value = tf score
        :param term_list: list of str
        :return: dict(key=term:value=tf score)
        """
        # Can use collection.counter, but I want to implement counter
        tf_scores = dict()
        dec_con = Context(prec=6, rounding=ROUND_05UP)
        for x in term_list:
            tf_scores[x] = tf_scores[x] + 1 if tf_scores.get(x) else 1

        for x, y in tf_scores.items():
            tf_scores[x] = "{}".format(dec_con.create_decimal(_d(y)/_d(len(term_list))))

        return tf_scores

    def gen_term_freq(self):
        """
        For every movie, generate a dict of every term's frequency arranged by their corresponding alpha
        TF(movie, term) = count of terms / total terms in movie
        Final dict = {      movie_1:
                                {   alpha_1:  ie Movie title more important than keyword
                                        {   term_1: TermFrequency(),
                                            term_2: ...
                                        },
                                    alpha_2: ..
                                },
                            movie_2: ...
                        }
        :return None
        """
        term_freq_dict = dict()
        movies = Movies.objects.all()
        for movie in movies:
            cast_char, cast_name = movie.get_cast()
            movie_alpha = {
                '0': self._tf(self.process.tokenize(movie.title)),  # Movie.title
                '1': self._tf(self.process.tokenize(movie.original_title)),  # Movie.original_title
                '2': self._tf(self.process.tokenize(movie.overview)),  # Movie.overview
                '3': self._tf(self.process.tokenize(movie.tagline)),  # Movie.tagline
                '4': self._tf(movie.get_genres()),  # Genre.name
                '6': self._tf(self.process.tokenize_character(cast_char)),  # Cast.character
                '7': self._tf(cast_name),  # Cast.name
                '8': self._tf(movie.get_crew()),  # Crew.name
                '9': self._tf(movie.get_keyword()),  # Keyword.name
            }
            term_freq_dict[movie.id] = movie_alpha
        self.search_index.set_term_freq(json.dumps(term_freq_dict))

    def gen_doc_freq(self):
        """
        For each term, count how many movies contains this term
        DF(movie, term) = Total movies / (# of movies with term + 1)\
        IDF(movie, term) = log(Df(movie,term))
        doc_freq_dict = {   term_1: DF(),
                            term_2: ...
                        }
        :return None
        """

        # Loading term freq since it contains a corpus with k-phrases
        term_freq = self.search_index.get_term_freq()
        df_dict = dict()
        dec_con = Context(prec=6, rounding=ROUND_05UP)
        for movie in term_freq:
            # Collapse the dict so that for each movie, we have a set of unique k-phrases
            movie_alpha = set(y for x in term_freq[movie].values() for y in x.keys())
            # For each k-phrase, add it into df_dict as a key
            # and as a value keep count how many times it appears
            for term in movie_alpha:
                df_dict[term] = df_dict[term] + 1 if df_dict.get(term) else 1

        # df_dict should be populated with every unique k-phrase and the number movies that contain it
        # Calculate the IDF() = log(total movies / documents with term + 1)
        for term in df_dict:
            dec_df_score = dec_con.create_decimal(log(_d(self.total_movies)/_d(df_dict[term])))
            df_dict[term] = str(dec_df_score)

        self.search_index.set_doc_freq(json.dumps(df_dict))

    def gen_tfidf(self):
        """
        For every term, create a dict of movies and their tf-idf score
        TFIDF(movie, term) = TF(movie, term) * log(DF(movie,term))
        tfidf_dict = {  term_1:
                            {   movie_1: TFIDF(),
                                movie_2: ...
                            },
                        term_2: ...
                    }
        :return None
        """
        doc_freq = self.search_index.get_doc_freq()
        term_freq = self.search_index.get_term_freq()
        alpha_dict = self.search_index.get_alpha()
        dec_con = Context(prec=6, rounding=ROUND_05UP)

        # Create a tfidf_dict to hold each term's tf-idf index of movies it appears in
        tfidf_dict = dict()
        for term in doc_freq:
            tfidf_dict[term] = dict()

        # Generate the tf-idf score for each movie and place them in the tfidf_dict
        for movie in term_freq:
            for alpha in term_freq[movie]:
                for term in term_freq[movie][alpha]:
                    # we are getting every term's individual score that corresponds to a movie
                    term_tf = _d(term_freq[movie][alpha][term])
                    term_idf = _d(doc_freq[term])
                    term_alpha = _d(alpha_dict[alpha])
                    # generate the term's score for the movie it appears in
                    term_tf_idf = term_tf * term_idf * term_alpha
                    # add this score to a tfidf dict that we can use to rank
                    sum_term_tfidf = _d(tfidf_dict[term][movie]) + term_tf_idf if \
                        tfidf_dict[term].get(movie) else \
                        term_tf_idf
                    tfidf_dict[term][movie] = str(dec_con.create_decimal(sum_term_tfidf))

        self.search_index.set_tfidf(json.dumps(tfidf_dict))

    def calibrate(self, print_info=False):
        """
        Generate the term_freq, doc_freq, and tfidf. Store results as string in DB
        :return: boolean
        """
        print_info_str = ""

        # Gen term freq
        start_time = time.time()
        print_info_str += "{}\n\tTerm Frequency\n{}".format("#"*30, "#"*30)
        self.gen_term_freq()
        print_info_str += "Finished Term Frequency: {}".format(time.time()-start_time)

        # Gen doc freq
        start_time = time.time()
        print_info_str += "{}\n\tDoc Frequency\n{}".format("#" * 30, "#" * 30)
        self.gen_doc_freq()
        print_info_str += "Finished Doc Frequency: {}".format(time.time() - start_time)

        # Gen TFIDF
        start_time = time.time()
        print_info_str += "{}\n\tTF-IDF\n{}".format("#" * 30, "#" * 30)
        self.gen_tfidf()
        print_info_str += "Finished TF-IDF: {}".format(time.time() - start_time)

        # Print info
        if print_info:
            print(print_info_str)

    def lookup(self, query):
        """
        Given a query, return ranked results
        :param query: a str
        :return: sorted list of Movies
        """
        # extract the tfidf dict from search index
        # results_dict(key = movies, value = sum of returned scores)
        # for each k-phrase in the query
        #   tfidf[k-phrase] = dict of movies and scores
        #   for movie in tfidf[k-phrase]
        #       results_dict[movie] += tfidf[k-phrase][movie]
        # return results_dict sorted by score
        pass
