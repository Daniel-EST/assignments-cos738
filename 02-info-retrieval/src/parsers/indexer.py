import json
import logging
import math
from collections import defaultdict
from typing import List

import parsers.inverted_list


logging.getLogger(__name__).addHandler(logging.NullHandler())


def write_model(input_paths: List[str], output_path_inverted_list: str, output_path_model: str) -> None:
    """
    Calculates the weight of each term for each document using the TF-IDF formula,
    and writes a dictionary of document-term weights to a JSON file.

    Args:
    - input_paths (List[str]): A list of paths to input XML files containing documents to process.
    - output_path_inverted_list (str): The path to write the output CSV file containing the inverted index.
    - output_path_model (str): The path to write the output JSON file containing the document-term weights.

    Returns:
    - None
    """
    inverted_list, max_freq_in_document = parsers.inverted_list.parse(
        input_paths, output_path_inverted_list)
    docs = defaultdict(lambda: defaultdict(float))
    total_documents = len(list(max_freq_in_document.values()))
    for term, doc_numbers in inverted_list.items():
        doc_num = set(doc_numbers)
        for doc in doc_num:
            docs[doc][term] = (doc_numbers.count(doc) / max_freq_in_document[doc]) * \
                math.log(total_documents / len(doc_num))

    logging.info("INDEXER - Saving TF-IDF model file as %s", output_path_model)
    with open(output_path_model, "w", encoding="utf-8") as file:
        json.dump(docs, file, sort_keys=True, indent=2)
