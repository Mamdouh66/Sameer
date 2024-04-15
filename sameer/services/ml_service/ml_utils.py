import pickle
import pandas as pd
import numpy as np

from math import sqrt

from sklearn.metrics import mean_squared_error
from surprise import Reader, Dataset, AlgoBase


def calculate_rmse(y_true: pd.Series, y_pred: pd.Series) -> float:
    return sqrt(mean_squared_error(y_true, y_pred))


def calculate_mse(y_true: pd.Series, y_pred: pd.Series) -> float:
    return mean_squared_error(y_true, y_pred)


def calculate_user_item_mean_rating(
    train_df: pd.DataFrame, test_df: pd.DataFrame
) -> pd.DataFrame:
    """
    Calculates the user-item mean rating for a given test set based on predicting a rating for a user-item pair
    as the average of the user's mean rating and the item's mean rating.

    Parameters:
    train_df (pandas.DataFrame): The training set DataFrame containing userId, movieId, and rating columns.
    test_df (pandas.DataFrame): The test set DataFrame containing userId, movieId, and rating columns.

    Returns:
    pandas.DataFrame: The test set DataFrame with additional columns for global mean rating, user mean rating,
    item mean rating, and user-item mean rating.
    """

    global_mean_rating = train_df["rating"].mean()
    test_df["global_mean_rating"] = global_mean_rating

    user_mean_ratings = train_df.groupby("userId")["rating"].mean().reset_index()
    item_mean_ratings = train_df.groupby("movieId")["rating"].mean().reset_index()

    test_df = pd.merge(test_df, user_mean_ratings, on="userId", how="left").rename(
        columns={"rating_y": "user_mean_rating", "rating_x": "rating"}
    )
    test_df = pd.merge(test_df, item_mean_ratings, on="movieId", how="left").rename(
        columns={"rating_y": "item_mean_rating", "rating_x": "rating"}
    )

    test_df["user_mean_rating"] = test_df["user_mean_rating"].fillna(global_mean_rating)
    test_df["item_mean_rating"] = test_df["item_mean_rating"].fillna(global_mean_rating)

    test_df["user_item_mean_rating"] = (
        test_df["user_mean_rating"] + test_df["item_mean_rating"]
    ) / 2

    return test_df


def calculate_weighted_mean_ratings(
    test_df: pd.DataFrame,
) -> tuple[pd.DataFrame, float, float]:
    """
    Calculates the weighted mean ratings for a given DataFrame.
    This model employs a weighted average of the user mean and item mean ratings.
    The weight ( w ) can be adjusted based on domain understanding.

    The formula is :
    prediction = w * User Mean Rating + (1 - w) * Item Mean Rating, where 0 <= w <= 1

    Args:
        test_df (pd.DataFrame): The DataFrame containing the necessary columns:
            - user_mean_rating: The mean rating for each user.
            - item_mean_rating: The mean rating for each item.
            - rating: The actual rating.

    Returns:
        tuple[pd.DataFrame, float, float]: A tuple containing the following:
            - test_df (pd.DataFrame): The updated DataFrame with the calculated weighted mean ratings.
            - best_w (float): The best weight value that resulted in the lowest RMSE.
            - best_rmse (float): The lowest RMSE achieved.

    """

    best_rmse = float("inf")
    best_w = 0

    for w in [i * 0.1 for i in range(11)]:
        test_df["weighted_mean_rating_tmp"] = (
            w * test_df["user_mean_rating"] + (1 - w) * test_df["item_mean_rating"]
        )
        rmse = calculate_rmse(test_df["rating"], test_df["weighted_mean_rating_tmp"])

        if rmse < best_rmse:
            best_rmse = rmse
            best_w = w

    test_df["weighted_mean_rating"] = (
        best_w * test_df["user_mean_rating"]
        + (1 - best_w) * test_df["item_mean_rating"]
    )
    test_df = test_df.drop(columns=["weighted_mean_rating_tmp"])

    return test_df, best_w, best_rmse


def load_data_into_surprise(
    train_df: pd.DataFrame, test_df: pd.DataFrame, reader: Reader
) -> tuple:
    """
    Loads the train and test data into Surprise Dataset objects.

    Parameters:
    train_df (pandas.DataFrame): The training set DataFrame containing userId, movieId, and rating columns.
    test_df (pandas.DataFrame): The test set DataFrame containing userId, movieId, and rating columns.

    Returns:
    tuple: A tuple containing the following:
        - trainset (surprise.Trainset): The training set in Surprise Dataset format.
        - testset (list): The test set in Surprise Dataset format.
    """
    train_data = Dataset.load_from_df(train_df, reader)
    test_data = Dataset.load_from_df(test_df, reader)

    trainset = train_data.build_full_trainset()
    testset = test_data.build_full_trainset().build_testset()

    return trainset, testset


def load_pickle_model(model_path: str) -> object:
    """
    Loads a pickled model from the specified path.

    Parameters:
    model_path (str): The path to the pickled model file.

    Returns:
    object: The loaded model object.
    """
    with open(model_path, "rb") as file:
        model = pickle.load(file)

    return model


def get_collaborative_rating(userId: int, movieId: int, model: AlgoBase):
    return model.predict(userId, movieId).est


def get_content_based_rating(
    userId: int,
    movieId: int,
    matrix_similarity: np.ndarray,
    movies_df: pd.DataFrame,
    model: AlgoBase,
):
    """
    Calculate the content-based rating for a given user and movie.

    Args:
        userId (int): The ID of the user.
        movieId (int): The ID of the movie.
        matrix_similarity (np.ndarray): The cosine similarity matrix.
        movies_df (pd.DataFrame): The DataFrame containing movie information.
        model (AlgoBase): The collaborative filtering model.

    Returns:
        float: The content-based rating for the user and movie.
    """
    sim_scores = sorted(
        list(enumerate(matrix_similarity[movieId])), key=lambda x: x[1], reverse=True
    )[1:11]
    movie_indices = [i[0] for i in sim_scores]
    similar_movies = movies_df.iloc[movie_indices]
    similar_movies["est"] = similar_movies["id"].apply(
        lambda x: model.predict(userId, x).est
    )
    return similar_movies["est"].mean()


def get_weighted_score(
    movieId: int,
    movies_df: pd.DataFrame,
    weighted_df: pd.DataFrame,
    default_score: float = 0,
):
    """
    Calculate the weighted score for a given movie.

    Parameters:
    - movieId (int): The ID of the movie.
    - movies_df (pd.DataFrame): The DataFrame containing movie information.
    - weighted_df (pd.DataFrame): The DataFrame containing weighted scores.
    - default_score (float): The default score to return if the movie ID is not found.

    Returns:
    - float: The weighted score of the movie, or the default score if the movie ID is not found.
    """
    return (
        weighted_df.loc[movies_df.loc[movieId, "id"], "score"]
        if movieId in movies_df.index
        and movies_df.loc[movieId, "id"] in weighted_df.index
        else default_score
    )


def hybrid_predicted_rating(
    userId: int,
    movieId: int,
    model: AlgoBase,
    similarity_matrix: np.ndarray,
    movies_df: pd.DataFrame,
    weighted_df: pd.DataFrame,
):
    """
    Calculates the hybrid predicted rating for a given user and movie using a combination of collaborative filtering,
    content-based filtering, and weighted scoring.

    Args:
        userId (int): The ID of the user.
        movieId (int): The ID of the movie.
        model (AlgoBase): The collaborative filtering model.
        similarity_matrix (np.ndarray): The cosine similarity matrix for content-based filtering.
        movies_df (pd.DataFrame): The DataFrame containing movie information.
        weighted_df (pd.DataFrame): The DataFrame containing weighted scores for movies.

    Returns:
        float: The hybrid predicted rating for the given user and movie.
    """
    collaborative_rating = get_collaborative_rating(userId, movieId, model)
    content_rating = get_content_based_rating(
        userId, movieId, similarity_matrix, movies_df, model
    )
    weighted_score = get_weighted_score(movieId, movies_df, weighted_df)

    final_rating = (
        (0.5 * collaborative_rating) + (0.2 * content_rating) + (0.3 * weighted_score)
    )
    return final_rating
