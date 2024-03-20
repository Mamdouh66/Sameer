import numpy as np
import pandas as pd
import ast


def extend_list_from_column(df, column_name, target_list, key="name"):
    """
    Extends a target list with values extracted from a specified column in a DataFrame.

    Parameters:
    - df: pandas DataFrame
        The DataFrame containing the column from which values will be extracted.
    - column_name: str
        The name of the column from which values will be extracted.
    - target_list: list
        The list to be extended with the extracted values.
    - key: str, optional (default='name')
        The key used to extract values from the column. Only applicable if the column contains dictionaries.

    Returns:
    None
    """
    temp_df = (
        df[column_name]
        .fillna("[]")
        .apply(ast.literal_eval)
        .apply(lambda x: [i[key] for i in x] if isinstance(x, list) else [])
    )
    for i in temp_df:
        if i:
            target_list.extend(i)


def get_director(crew):
    """
    Returns the name of the director from a list of dictionaries.

    Parameters:
    crew (list): A list of dictionaries containing information about crew members.

    Returns:
    str: The name of the director, or np.nan if no director is found.
    """
    return next((i["name"] for i in crew if i["job"] == "Director"), np.nan)


def get_list(lst):
    """
    Returns a list of names extracted from a list of dictionaries.

    Args:
        lst (list): A list of dictionaries.

    Returns:
        list: A list of names extracted from the dictionaries. If the length of the list is greater than 3, only the first 3 names are returned.

    """
    if isinstance(lst, list):
        names = [i["name"] for i in lst]
        return names[:3] if len(names) > 3 else names
    return []


def clean_text_data(text_cols):
    """
    Cleans the input data by converting strings to lowercase and removing spaces.

    Parameters:
    text_cols (str or list): The input data to be cleaned.

    Returns:
    str or list: The cleaned data.

    """
    if isinstance(text_cols, list):
        return [str.lower(i.replace(" ", "")) for i in text_cols]
    else:
        if isinstance(text_cols, str):
            return str.lower(text_cols.replace(" ", ""))
        else:
            return ""


def create_bag_of_words(cols):
    """
    Creates a bag of words representation for a given movie.

    Args:
        cols (dict): A dictionary containing movie information.

    Returns:
        str: A string representing the bag of words for the movie.
    """
    return " ".join(
        cols["keywords"] + cols["cast"] + [cols["director"]] + cols["genres"]
    )
