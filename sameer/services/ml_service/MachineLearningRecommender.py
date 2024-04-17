import asyncio
import pandas as pd

from Sameer.services.ml_service import ml_utils

from sklearn.feature_extraction.text import CountVectorizer
from sklearn.metrics.pairwise import cosine_similarity


class MLRecommender:
    def __init__(self):
        self.model = ml_utils.load_pickle_model("notebooks/pickels/best_svd_model.pkl")
        self.ratings_df = pd.read_csv("data/ratings_df.csv")
        self.weighted_df = pd.read_csv("data/weighted_df.csv")
        self.movies_df = pd.read_csv("data/movies_df.csv")

    def __get_user_rating_predictions(self, user_ratings):
        predictions = []
        for _, row in user_ratings.iterrows():
            pred = self.model.predict(row["userId"], row["movieId"]).est
            predictions.append((row["movieId"], pred))
        return predictions

    def __get_top_collab_movies(self, predictions, number_of_movies):
        return [
            x[0]
            for x in sorted(predictions, key=lambda x: x[1], reverse=True)[
                :number_of_movies
            ]
        ]

    async def __get_similarity_matrix(self):
        count = CountVectorizer(stop_words="english")
        count_matrix = count.fit_transform(self.movies_df["bag_of_words"])
        sim_mat = await cosine_similarity(count_matrix, count_matrix)
        return sim_mat

    def __aget_similarity_matrix(self):
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        sim_mat = loop.run_until_complete(self.__get_similarity_matrix())
        loop.close()
        return sim_mat

    def __get_similar_movies(self, last_watched_movieId, number_of_movies):
        """
        Get a list of similar movies based on the last watched movie.

        Parameters:
        last_watched_movieId (int): The ID of the last watched movie.
        n (int): The number of similar movies to return.

        Returns:
        list: A list of movie IDs of similar movies.

        """
        sim_mat = self.__aget_similarity_matrix()
        if last_watched_movieId in self.movies_df["id"].values:
            watched_movie_idx = self.movies_df[
                self.movies_df["id"] == last_watched_movieId
            ].index[0]
            similar_movies = list(enumerate(sim_mat[watched_movie_idx]))
            sorted_similar_movies = sorted(
                similar_movies, key=lambda x: x[1], reverse=True
            )[1 : number_of_movies + 1]
            return [self.movies_df.iloc[i[0]]["id"] for i in sorted_similar_movies]
        else:
            print(f"Movie ID {last_watched_movieId} not found in movies_df.")
            return []

    def __get_weighted_scores(self, movie_ids):
        """
        Fetches the weighted scores for a list of movie IDs.

        Parameters:
        - movie_ids (list): A list of movie IDs for which to fetch the weighted scores.
        - weighted_df (pandas.DataFrame): The weighted DataFrame containing weighted scores.

        Returns:
        - weighted_scores (dict): A dictionary mapping movie IDs to their corresponding weighted scores.
        """
        self.weighted_df = self.weighted_df.loc[
            ~self.weighted_df.index.duplicated(keep="first")
        ]

        weighted_scores = {
            movie_id: (
                self.weighted_df.loc[movie_id]["score"]
                if movie_id in self.weighted_df.index
                else 0
            )
            for movie_id in movie_ids
        }

        return weighted_scores

    def __combine_scores(collab_weighted_scores, content_weighted_scores):
        """
        Combines collaborative and content-based weighted scores for movies.

        Parameters:
        - collab_weighted_scores (dict): A dictionary containing movie IDs as keys and collaborative weighted scores as values.
        - content_weighted_scores (dict): A dictionary containing movie IDs as keys and content-based weighted scores as values.

        Returns:
        - combined_scores (dict): A dictionary containing movie IDs as keys and combined scores as values, where the combined score is calculated as the sum of 0.5 times the collaborative weighted score and 0.5 times the content-based weighted score.
        """
        combined_scores = {}
        for movie_id, score in collab_weighted_scores.items():
            combined_scores[movie_id] = combined_scores.get(movie_id, 0) + 0.5 * score
        for movie_id, score in content_weighted_scores.items():
            combined_scores[movie_id] = combined_scores.get(movie_id, 0) + 0.5 * score
        return combined_scores

    def hybrid_recommendation(self, user_id, number_of_movies=10):
        """
        Generates hybrid movie recommendations for a given user.

        Parameters:
            user_id (int): The ID of the user for whom recommendations are generated.
            n (int, optional): The number of recommendations to generate. Defaults to 10.

        Returns:
            list: A list of movie IDs representing the top recommended movies for the user.
        """
        user_ratings = self.ratings_df[self.ratings_df["userId"] == user_id]
        rating_predictions = self.__get_user_rating_predictions(user_ratings)
        top_collab_movies = self.__get_top_collab_movies(
            rating_predictions, number_of_movies
        )
        last_watched_movieId = user_ratings.iloc[-1]["movieId"]
        top_content_movies = self.__get_similar_movies(
            last_watched_movieId, number_of_movies
        )
        collab_weighted_scores = self.__get_weighted_scores(
            top_collab_movies, self.weighted_df
        )
        content_weighted_scores = self.__get_weighted_scores(
            top_content_movies, self.weighted_df
        )
        combined_scores = self.__combine_scores(
            collab_weighted_scores, content_weighted_scores
        )
        sorted_movies = sorted(
            combined_scores.keys(), key=lambda x: combined_scores[x], reverse=True
        )
        return sorted_movies[:number_of_movies]


if __name__ == "__main__":
    model = MLRecommender()
    print(model.hybrid_recommendation(235))
