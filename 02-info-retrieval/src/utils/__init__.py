"""
A collection of utility functions for common tasks.

This module contains various helper functions for common programming tasks, such as string manipulation, file handling, and data processing. These functions can be used across different projects and can help improve code reusability and readability.

Functions:
- get_config_path(file: str) -> str:
    Returns the path to the configuration file with the given file name.
- strip_accents(s: str) -> str:
    Strip accents and diacritical marks from a string.

Example usage:
-------------
import utils

# Get the path to a configuration file
config_path = utils.get_config_path("my_config.ini")

# Strip accents from a string
text = "Héllo, Wórld!"
stripped_text = utils.strip_accents(text)
print(stripped_text)  # Output: "Hello, World!"
"""

from typing import List, Tuple
import unicodedata
import re
import csv


def get_config_path(file: str) -> str:
    """
    Returns the path to the configuration file with the given file name.

    Args:
    - file (str): the name of the configuration file to look for

    Returns:
    - str: the absolute path to the configuration file with the given name,
    assuming that the file is located in the './config/' directory
    """
    return f"./config/{file}"


def strip_accents(s: str) -> str:
    """
    Strip accents and diacritical marks from a string.

    Args:
    - s (str): the string to process

    Returns:
    - str: A new string with all accents and diacritical marks removed.

    Example:
    >>> strip_accents("àáâãäåæçèéêëìíîïðñòóôõöøùúûüýþÿ")
    'aaaaaaaeceeeeiiiiðnoooooøuuuuyþy'
    """
    return ''.join(c for c in unicodedata.normalize('NFD', s) if unicodedata.category(c) != 'Mn')


def strip_special_characters(s: str) -> str:
    # return s.translate(str.maketrans("", "", string.punctuation))
    return re.sub(r"[^a-zA-Z]+", " ", s)


def get_stopwords():
    with open("./utils/stopwords.txt", "r", encoding="utf-8") as file:
        return file.read()


def remove_stopwords(s: str) -> str:
    stopwords = get_stopwords()
    s = " ".join(term if term.lower()
                 not in stopwords else "" for term in s.split(" "))
    return s


def normalize_text(s: str, stopwords: bool = True) -> str:
    s = s.upper()
    s = strip_special_characters(s)
    if stopwords:
        s = remove_stopwords(s)
    s = strip_accents(s)
    s = s.replace("\n", " ")
    s = re.sub(r" +", " ", s)
    return s.strip()


def write_to_csv(output_path: str, fieldnames: List[str], values: List[Tuple]) -> None:
    with open(output_path, "w", encoding="utf-8") as file:
        writer = csv.writer(file, delimiter=";", quotechar="\"")
        if fieldnames:
            writer.writerow(fieldnames)
        writer.writerows(values)
