import logging
import xml.dom.minidom
from collections import defaultdict
from typing import Dict, List, Tuple, DefaultDict

import utils

logging.getLogger(__name__).addHandler(logging.NullHandler())


def __read_raw_documents_file(input_path: str, inverted_list: Dict[str, List[int]], max_freq_in_document: Dict[int, float], steemer: bool = False) -> Tuple[DefaultDict[str, List[int]], DefaultDict[int, float]]:
    """
    Read an XML file and extract terms from the abstracts or extracts.

    Args:
    - input_path (str): the path to the XML file to read
    - inverted_list (Dict[str, List[int]]): the dictionary of terms and their record numbers
    - max_freq_in_document (Dict[int, float]): the dictionary of record numbers and their maximum frequency of occurrence

    Returns:
    - Tuple[Dict[str, List[int]], Dict[int, float]]: a tuple of the inverted list and the maximum frequency in each document
    """
    logging.info(
        "INVERTED LIST PARSER - Reading file %s", input_path
    )
    with xml.dom.minidom.parse(input_path) as doc:
        logging.info("INVERTED LIST PARSER - Parsing file %s", input_path)
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
                abstract = utils.normalize_text(
                    abstract, stopwords=True, steemer=steemer)
                abstract = [term.strip() for term in abstract.split(" ")]
                terms = set(abstract)
                most_freq_term = max(terms, key=abstract.count)
                max_freq_in_document[record_num] = abstract.count(
                    most_freq_term
                )
                for term in abstract:
                    inverted_list[term].append(record_num)
                    logging.debug(
                        "INVERTED LIST - LIST: Term: %s; Documents: %s;", term, inverted_list[term]
                    )

    return inverted_list, max_freq_in_document


def __write_inverted_list_file(output_path: str, terms: List[Tuple]) -> None:
    """
    Write the inverted list to a CSV file.

    Args:
    - output_path (str): the path to the output CSV file
    - terms (List[Tuple]): the list of terms and their record numbers

    Returns:
    - None
    """
    logging.info("INVERTED LIST - Saving inverted list as %s", output_path)
    fieldnames = []
    terms = list(zip(terms, terms.values()))
    utils.write_to_csv(output_path, fieldnames, terms)


def parse(input_paths: List[str],  ouput_path: str, steemer: bool = False) -> Tuple[DefaultDict[str, List[int]], DefaultDict[int, float]]:
    """
    Parse one or more XML files containing documents, save the inverted list to a CSV file, and return two defaultdicts.

    The function reads one or more XML files containing documents, where each document consists of a number of fields.
    The function then constructs an inverted index, where each term in the documents is associated with a list of record numbers.
    Additionally, for each document, the maximum frequency of a term in that document is also calculated and stored.

    Args:
    - input_paths (List[str]): A list of paths to the input XML files.
    - output_path (str): The path to the output CSV file for the inverted list.

    Returns:
    - Tuple[DefaultDict[str, List[int]], DefaultDict[int, float]]: A tuple of two defaultdicts:
        - The first defaultdict maps terms to a list of record numbers.
        - The second defaultdict maps document numbers to their maximum term frequency.

    Example:
    >>> inverted_list, max_freq_in_document = parse(['./data/documents.xml'], './data/inverted_list.csv')
    """
    inverted_list = defaultdict(list)
    max_freq_in_document = defaultdict(lambda: defaultdict(float))
    for input_path in input_paths:
        inverted_list, max_freq_in_document = __read_raw_documents_file(
            input_path.strip(), inverted_list, max_freq_in_document, steemer
        )
    logging.info("INVERTED LIST - Inverted list found %d terms",
                 len(inverted_list.values()))
    __write_inverted_list_file(ouput_path, inverted_list)
    return inverted_list, max_freq_in_document
