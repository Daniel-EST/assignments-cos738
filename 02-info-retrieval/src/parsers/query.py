import xml.dom.minidom
from typing import Tuple, List
import logging
import utils
logging.getLogger(__name__).addHandler(logging.NullHandler())


def __read_raw_query_file(input_path: str) -> Tuple[List[Tuple]]:
    logging.info("QUERY PARSER: Reading \"LEIA\" file from %s", input_path)
    queries = []
    expected = []
    with xml.dom.minidom.parse(input_path) as doc:
        for query in doc.getElementsByTagName("QUERY"):
            query_number = query.getElementsByTagName(
                "QueryNumber"
            )[0].firstChild.nodeValue
            query_number = int(query_number.strip())

            query_text = query.getElementsByTagName(
                "QueryText"
            )[0].firstChild.nodeValue

            query_text = utils.normalize_text(query_text, stopwords=False)

            queries.append((query_number, query_text))

            documents = query.getElementsByTagName("Records")[0]
            for document in documents.getElementsByTagName("Item"):
                document_number = document.firstChild.nodeValue
                document_number = int(document_number.strip())

                document_score = document.getAttribute("score")
                document_score = int(document_score.strip())

                expected.append(
                    (query_number, document_number, document_score)
                )
    return queries, expected


def __write_query_file(output_path: str, queries: List[Tuple]) -> None:
    logging.info("QUERY PARSER: Saving \"CONSULTAS\" file at %s", output_path)
    fieldnames = ["QueryNumber", "QueryText"]
    utils.write_to_csv(output_path, fieldnames, queries)


def __write_expected_file(output_path: str, expected: List[Tuple]) -> None:
    logging.info("QUERY PARSER: Saving \"ESPERADOS\" file at %s", output_path)
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
