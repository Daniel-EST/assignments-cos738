import logging
import xml.dom.minidom
from typing import List, Tuple

import utils

logging.getLogger(__name__).addHandler(logging.NullHandler())


def __read_raw_query_file(input_path: str) -> Tuple[List[Tuple]]:
    """
    Read an XML file containing queries and their expected results, and return a tuple with two lists:
    the parsed queries and their expected results.

    Args:
    - input_path (str): the path to the XML file to parse

    Returns:
    - Tuple[List[Tuple]]: a tuple containing two lists of tuples. The first list contains tuples with the query
      number and the normalized query text. The second list contains tuples with the query number, the document number,
      and the document score.

    Example:
    >>> queries, expected = __read_raw_query_file('queries.xml')
    """
    logging.info("QUERY PARSER - Reading file %s", input_path)
    queries = []
    expected = []
    with xml.dom.minidom.parse(input_path) as doc:
        logging.info("QUERY PARSER - Parsing %s", input_path)
        n_queries = 0
        for query in doc.getElementsByTagName("QUERY"):
            n_queries += 1
            query_number = query.getElementsByTagName(
                "QueryNumber"
            )[0].firstChild.nodeValue
            query_number = int(query_number.strip())

            query_text = query.getElementsByTagName(
                "QueryText"
            )[0].firstChild.nodeValue

            query_text = utils.normalize_text(query_text, stopwords=False)

            queries.append((query_number, query_text))
            logging.debug("QUERY PARSER - QUERIES FILE: QueryNumber: %d; QueryText: %s",
                          query_number, query_text)

            documents = query.getElementsByTagName("Records")[0]
            for document in documents.getElementsByTagName("Item"):
                document_number = document.firstChild.nodeValue
                document_number = int(document_number.strip())

                document_score = document.getAttribute("score")
                document_score = sum(map(lambda x: int(x) > 0, document_score))

                expected.append(
                    (query_number, document_number, document_score)
                )
                logging.debug("QUERY PARSER - EXPECTED FILE: QueryNumber: %d; DocNumber: %d; DocScore: %d;",
                              query_number, document_number, document_score)

    logging.info("QUERY PARSER - Total queries parsed: %d", n_queries)
    return queries, expected


def __write_query_file(output_path: str, queries: List[Tuple]) -> None:
    """
    Write a list of queries to a CSV file.

    Args:
        output_path (str): The output path of the CSV file.
        queries (List[Tuple]): A list of queries, where each query is a tuple containing two elements:
                            (query number, query text).

    Returns:
        None

    Saves:
        A CSV file at the output path containing the list of queries.

    The function takes a list of queries in the format described above, and saves them to a CSV file at the output path. The CSV file is saved using the ";" delimiter and the "\"" quote character. The queries are saved with the following field names: "QueryNumber" and "QueryText".

    Note that the function assumes that the queries are already in the correct format, and does not perform any error checking or validation.
    """
    logging.info(
        "QUERY PARSER - Saving parsed queries file as %s", output_path)
    fieldnames = ["QueryNumber", "QueryText"]
    utils.write_to_csv(output_path, fieldnames, queries)


def __write_expected_file(output_path: str, expected: List[Tuple]) -> None:
    """
    Write a list of expected results to a CSV file.

    Args:
        output_path (str): The output path of the CSV file.
        expected (List[Tuple]): A list of expected results, where each result is a tuple containing three elements:
                                (query number, document number, document votes).

    Returns:
        None

    Saves:
        A CSV file at the output path containing the list of expected results.

    The function takes a list of expected results in the format described above, and saves them to a CSV file at the output path. The CSV file is saved using the ";" delimiter and the "\"" quote character. The expected results are saved with the following field names: "QueryNumber", "DocNumber", and "DocVotes".

    Note that the function assumes that the expected results are already in the correct format, and does not perform any error checking or validation.
    """
    logging.info(
        "QUERY PARSER - Saving parsed expected documents file as %s", output_path)
    fieldnames = ["QueryNumber", "DocNumber", "DocVotes"]
    utils.write_to_csv(output_path, fieldnames, expected)


def parse(input_path: str,  ouput_query_path: str, ouput_expected_path: str) -> None:
    """
    Parse an XML file containing queries and their expected results.

    Args:
    - input_path (str): the path to the XML file to parse
    - ouput_query_path (str): the output path of the queries in csv file
    - ouput_expected_path (str): the output path of the expeced in csv file

    Returns:
    - None

    Saves:
    - Two CSV files named after the config file containing the parsed queries
      and their expected results, respectively.
    """
    queries, expected = __read_raw_query_file(input_path)
    __write_query_file(ouput_query_path, queries)
    __write_expected_file(ouput_expected_path, expected)
