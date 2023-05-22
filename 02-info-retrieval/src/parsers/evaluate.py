import logging
import csv
import statistics
from collections import defaultdict
from typing import Dict, List

import matplotlib.pyplot as plt
from nltk.metrics import precision, recall, f_measure

logging.getLogger(__name__).addHandler(logging.NullHandler())


def __read_retrieved_documents(path: str) -> defaultdict:
    results = defaultdict(list)
    with open(path, "r", encoding="utf-8") as csv_file:
        rows = csv.DictReader(csv_file, delimiter=";")
        for row in rows:
            # result = row["Result"]
            # results[row["QueryNumber"]].append({
            #     "Document": result[0],
            #     "Rank": result[1],
            #     "Similarity": result[2]
            # })
            results[int(row["QueryNumber"])].append(
                eval(row["Result"])[0]
            )

    return results


def __read_expected_documents(path: str) -> defaultdict:
    expected = defaultdict(list)
    with open(path, "r", encoding="utf-8") as csv_file:
        rows = csv.DictReader(csv_file, delimiter=";")
        for row in rows:
            # expected[row["QueryNumber"]].append({
            #     "Document": row["DocNumber"],
            #     "Votes": row["DocVotes"]
            # })
            expected[int(row["QueryNumber"])].append(
                int(row["DocNumber"])
            )

    return expected


def interpoloated_average_precision_11_point_graph(retrieved_path: str, expected_path: str, label: str) -> None:
    logging.info(
        "EVALUATION - Plotting 11-Point Interpolated Average Precision")
    retrieved = __read_retrieved_documents(retrieved_path)
    expected = __read_expected_documents(expected_path)
    precisions = defaultdict(list)
    recalls = defaultdict(list)
    interpolations = []

    for query, documents in expected.items():
        reference = set(documents)
        for i in range(len(retrieved[query])):
            test = set(retrieved[query][:i+1])
            precisions[query].append(
                precision(reference, test)
            )
            recalls[query].append(
                recall(reference, test)
            )

    queries = set(expected.keys())
    eleven_points = [0, 0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1]
    for query in queries:
        inter = []
        for i, _ in enumerate(eleven_points):
            pr = zip(precisions[query], recalls[query])
            ri = filter(lambda x: x[1] >= eleven_points[i], pr)
            interpolation = max(list(map(lambda x: x[0], ri)), default=0)
            inter.append(interpolation)
        interpolations.append(inter)

    interpolation_mean = []
    for i, _ in enumerate(eleven_points):
        interpolation_mean.append(
            statistics.mean(
                list(map(lambda x: x[i], interpolations))
            )
        )

    plt.plot(eleven_points, interpolation_mean, "--", label=label)
    plt.plot(eleven_points, interpolation_mean, ".")
    plt.xlabel("Precision")
    plt.ylabel("Recall")
    plt.xlim(-0.05, 1.05)
    plt.ylim(-0.05, 1.05)
    logging.info("EVALUATION - Plotted")


def f1_score(retrieved_path: str, expected_path: str, label: str, max_results: int = 10) -> None:
    logging.info(
        "EVALUATION - Calculating %s's F1-Score", label
    )
    retrieved = __read_retrieved_documents(retrieved_path)
    expected = __read_expected_documents(expected_path)
    scores = []
    for query, documents in expected.items():
        reference = set(documents)
        lim = min(len(documents), max_results)
        test = set(retrieved[query][:lim])
        scores.append(
            f_measure(reference, test)
        )

    logging.info(
        "EVALUATION - %s's F1-Score: %.02f", label, statistics.mean(scores)
    )


def precision_at_n(retrieved_path: str, expected_path: str, n: int, label: str) -> Dict[str, List[int]]:
    logging.info(
        "EVALUATION - Calculating %s's P@%d", label, n
    )
    retrieved = __read_retrieved_documents(retrieved_path)
    expected = __read_expected_documents(expected_path)
    precisions = {}
    for query, documents in expected.items():
        reference = set(documents)
        lim = min(len(documents), n)
        test = set(retrieved[query][:lim])
        precisions[query] = precision(reference, test)

    for query, p in precisions.items():
        logging.info(
            "EVALUATION - %s's P@%d Q%d: %.02f", label, n, query, p
        )
    return precisions


def mean_average_precision(retrieved_path: str, expected_path: str, max_n: int, label: str) -> float:
    logging.info(
        "EVALUATION - Calculating %s's MAP", label
    )
    retrieved = __read_retrieved_documents(retrieved_path)
    expected = __read_expected_documents(expected_path)
    precisions = defaultdict(list)
    for n in range(max_n):
        last_precision = 0.0
        for query, documents in expected.items():
            reference = set(documents)
            lim = min(len(documents), n+1)
            test = set(retrieved[query][:lim])
            p = precision(reference, test)
            if p > last_precision:
                precisions[query].append(p)
            last_precision = p

    mean_precisions = []
    for p in precisions.values():
        mean_precisions.append(statistics.mean(p))

    m = statistics.mean(mean_precisions)
    logging.info(
        "EVALUATION - %s's MAP: %.02f", label, m
    )
    return m


def mean_reciprocal_rank(retrieved_path: str, expected_path: str, max_k: int, max_n: int, label: str) -> float:
    logging.info(
        "EVALUATION - Calculating %s's MRR", label
    )
    retrieved = __read_retrieved_documents(retrieved_path)
    expected = __read_expected_documents(expected_path)
    reciprocal_ranks = []
    for query, expected_documents in expected.items():
        lim = min(len(set(expected_documents)), max_n)
        for k, retrieved_document in enumerate(retrieved[query][:lim]):
            if k > max_k:
                reciprocal_ranks.append(0)
                break
            if retrieved_document in set(expected_documents):
                reciprocal_ranks.append(1/(k + 1))
                break

    mrr = statistics.mean(reciprocal_ranks)

    logging.info(
        "EVALUATION - %s's MRR: %.02f", label, mrr
    )
    return mrr
