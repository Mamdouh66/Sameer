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


def calculate_weighted_mean_ratings(test_df: pd.DataFrame) -> pd.DataFrame:
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
        pd.DataFrame: The DataFrame with an additional column 'weighted_mean_rating',
        which contains the calculated weighted mean ratings.

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
    return test_df
