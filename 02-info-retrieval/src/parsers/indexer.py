import xml.dom.minidom
from typing import Tuple, List, Dict, DefaultDict
import logging
import utils
from collections import defaultdict
import math
import json

logging.getLogger(__name__).addHandler(logging.NullHandler())


def __read_raw_query_file(input_path: str, docs: Dict[int, int]) -> DefaultDict[int, int]:
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
                abstract = utils.normalize_text(abstract, stopwords=True)
                term = [term.strip() for term in abstract.split(" ")]
                terms = set(term)
                most_freq_term = max(terms, key=term.count)
                docs[record_num] = term.count(most_freq_term)
    return docs


def docs_max_term_freq(input_paths: List[str]) -> Dict[int, int]:
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
    docs = defaultdict(list)
    for input_path in input_paths:
        docs = __read_raw_query_file(input_path.strip(), docs)

    return docs


def write_model(terms: Dict[str, List[int]], max_terms: Dict[int, int], output_path: str) -> None:
    docs = defaultdict(lambda: defaultdict(float))
    total_documents = len(list(max_terms.values()))
    for term, doc_numbers in terms.items():
        doc_num = set(doc_numbers)
        for doc in doc_num:
            docs[term][doc] = (doc_numbers.count(doc) / max_terms[doc]) * \
                math.log(total_documents / len(doc_num))

    with open(output_path, "w", encoding="utf-8") as file:
        json.dump(docs, file)
