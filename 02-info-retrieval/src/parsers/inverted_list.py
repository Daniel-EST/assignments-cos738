import xml.dom.minidom
from typing import Tuple, List, Dict, DefaultDict
import logging
import utils
from collections import defaultdict

logging.getLogger(__name__).addHandler(logging.NullHandler())


def __read_raw_query_file(input_path: str, terms: Dict[str, List[int]]) -> DefaultDict[str, List[int]]:
    logging.info(
        "INVERTED LIST PARSER: Reading \"LEIA\" file from %s", input_path
    )
    with xml.dom.minidom.parse(input_path) as doc:
        for record in doc.getElementsByTagName("RECORD"):
            record_num = record.getElementsByTagName(
                "RECORDNUM"
            )[0].firstChild.nodeValue
            record_num = int(record_num.strip())

            abstract = record.getElementsByTagName(
                "ABSTRACT"
            )

            extract = record.getElementsByTagName(
                "EXTRACT"
            )

            if abstract:
                abstract = abstract[0].firstChild.nodeValue
            elif extract:
                abstract = extract[0].firstChild.nodeValue

            if abstract:
                abstract = utils.noramlize_text(abstract)
                abstract = abstract.split(" ")
                for term in abstract:
                    term = term.strip()
                    terms[term].append(record_num)
    return terms


def __write_inverted_list_file(output_path: str, terms: List[Tuple]) -> None:
    logging.info("QUERY PARSER: Saving \"ESCREVA\" file at %s", output_path)
    fieldnames = []
    terms = list(zip(terms, terms.values()))
    utils.write_to_csv(output_path, fieldnames, terms)


def parse(input_paths: List[str],  ouput_path: str) -> None:
    """
    Parse an XML file containing queries and their expected results.

    Args:
    - input_path (str): the path to the XML file to parse
    - ouput_path (str): the output path of the inverted list in csv file

    Returns:
    - None

    Saves:
    - One CSV files named after the config file containing the parsed queries
      and their expected results, respectively.
    """
    terms = defaultdict(list)
    for input_path in input_paths:
        terms = __read_raw_query_file(input_path.strip(), terms)
    __write_inverted_list_file(ouput_path, terms)
