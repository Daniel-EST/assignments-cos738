import csv
import json
import logging

from typing import List, Dict, Tuple

import numpy as np

import utils

logging.getLogger(__name__).addHandler(logging.NullHandler())


def __read_parsed_query_file(input_path: str) -> Dict[int, str]:
    logging.info(
        "SEARCH PARSER - Reading queries file %s", input_path
    )
    queries = {}
    with open(input_path, "r", encoding="utf-8") as file:
        reader = csv.DictReader(file, delimiter=";")
        for row in reader:
            queries[int(row["QueryNumber"])] = utils.normalize_text(
                row["QueryText"]).split(" ")
    return queries


def __read_model(input_path: str) -> Dict[str, Dict[str, float]]:
    logging.info(
        "SEARCH PARSER - Reading model file %s", input_path
    )
    with open(input_path, "r", encoding="utf-8") as file:
        model = json.load(file)
    return model


def __calc_weights(query: List[str], document: Dict[str, float]) -> np.array:
    weights = []
    for term in query:
        try:
            weights.append(document[term])
        except KeyError:
            weights.append(0)

    return np.array(weights)


def __calc_similarity(query_weights: np.array, document_weights: np.array) -> float:
    a = document_weights.dot(query_weights)
    b = (np.linalg.norm(document_weights) * np.linalg.norm(query_weights))
    if b == 0:
        return 0
    return a/b


def __results(query: List[str], model: Dict[str, Dict[str, float]]) -> List[Tuple[int, float]]:
    documents_similarity = {}
    query_weights = np.array([1] * len(query))
    for doc, weights in model.items():
        document_weights = __calc_weights(query, weights)
        documents_similarity[doc] = __calc_similarity(
            query_weights, document_weights)

    results = sorted(documents_similarity.items(),
                     key=lambda x: x[1], reverse=True)
    return results


def retrieve_documents(queries_path: str, output_path: str, model_path: str) -> None:
    queries = __read_parsed_query_file(queries_path.strip())
    model = __read_model(model_path.strip())
    logging.info(
        "SEARCH PARSER - Saving query results fiel as %s", output_path
    )
    utils.write_to_csv(output_path, ["QueryNumber", "Result"], [])
    for i, query in queries.items():
        results = __results(query, model)
        rank = 0
        for doc, result in results:
            if result > 0:
                utils.write_to_csv(output_path, [], [
                    (i, [int(doc), rank, result])
                ], mode="a")
                rank += 1
