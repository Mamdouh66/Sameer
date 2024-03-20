import pandas as pd

from math import sqrt

from sklearn.metrics import mean_squared_error


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
