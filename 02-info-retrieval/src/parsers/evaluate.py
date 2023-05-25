import logging
import csv
import statistics
import math
from collections import defaultdict
from typing import Dict, List

import matplotlib.pyplot as plt
from nltk.metrics import precision, recall, f_measure

import utils

logging.getLogger(__name__).addHandler(logging.NullHandler())


def __read_retrieved_documents(path: str) -> defaultdict:
    results = defaultdict(list)
    with open(path, "r", encoding="utf-8") as csv_file:
        rows = csv.DictReader(csv_file, delimiter=";")
        for row in rows:
            result = eval(row["Result"])
            results[int(row["QueryNumber"])].append({
                "Document": int(result[0]),
                "Rank": int(result[1]),
                "Similarity": float(result[2])
            })
    return results


def __read_expected_documents(path: str) -> defaultdict:
    expected = defaultdict(list)
    with open(path, "r", encoding="utf-8") as csv_file:
        rows = csv.DictReader(csv_file, delimiter=";")
        for row in rows:
            expected[int(row["QueryNumber"])].append({
                "Document": int(row["DocNumber"]),
                "Votes": int(row["DocVotes"])
            })
    return expected


def interpoloated_average_precision_11_point_graph(retrieved_path: str, expected_path: str, label: str, color: str) -> None:
    logging.info(
        "EVALUATION - Plotting 11-Point Interpolated Average Precision")
    retrieved = __read_retrieved_documents(retrieved_path)
    expected = __read_expected_documents(expected_path)
    precisions = defaultdict(list)
    recalls = defaultdict(list)
    interpolations = []

    for query, documents in expected.items():
        reference = set(map(lambda x: x["Document"], documents))
        for i in range(len(retrieved[query])):
            test = set(map(lambda x: x["Document"], retrieved[query][:i+1]))
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

    plt.plot(eleven_points, interpolation_mean, "--", color=color, label=label)
    plt.plot(eleven_points, interpolation_mean, ".", color=color)
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
        reference = set(map(lambda x: x["Document"], documents))
        lim = min(len(documents), max_results)
        test = set(map(lambda x: x["Document"], retrieved[query][:lim]))
        scores.append(
            f_measure(reference, test)
        )

    mean_f1 = statistics.mean(scores)
    utils.write_to_csv(
        f"./avalia/f1-score_{label}.csv", ["label", "f1_score"], [(label, mean_f1)])
    logging.info(
        "EVALUATION - %s's F1-Score: %.02f", label, mean_f1
    )


def precision_at_n(retrieved_path: str, expected_path: str, n: int, label: str) -> Dict[str, List[int]]:
    logging.info(
        "EVALUATION - Calculating %s's P@%d", label, n
    )
    retrieved = __read_retrieved_documents(retrieved_path)
    expected = __read_expected_documents(expected_path)
    precisions = {}
    for query, documents in expected.items():
        reference = set(map(lambda x: x["Document"], documents))
        lim = min(len(documents), n)
        test = set(map(lambda x: x["Document"], retrieved[query][:lim]))
        precisions[query] = precision(reference, test)

    utils.write_to_csv(f"./avalia/p@{n}_{label}.csv", ["label", "query", "precision"], [
                       (label, query, p)for query, p in precisions.items()])
    for query, p in precisions.items():
        logging.info(
            "EVALUATION - %s's P@%d Q%d: %.02f", label, n, query, p
        )
    return precisions


def r_precision(retrieved_path: str, expected_path: str, r: int, label: str) -> Dict[str, List[int]]:
    logging.info(
        "EVALUATION - Calculating %s's R-precision", label
    )
    retrieved = __read_retrieved_documents(retrieved_path)
    expected = __read_expected_documents(expected_path)
    r_precisions = {}
    for query, documents in expected.items():
        reference = set(map(lambda x: x["Document"], documents))
        lim = min(len(documents), r)
        test = set(map(lambda x: x["Document"], retrieved[query][:lim]))
        correct = list(filter(lambda x: x in reference, test))
        r_precisions[query] = len(correct)/len(test)

    for query, r in r_precisions.items():
        logging.info(
            "EVALUATION - %s's R-precision Q%d: %.02f", label, query, r
        )
    return r_precisions


def r_precision_histogram(retrieved_paths: List[str], expected_paths: List[str], r: int, labels: List[str]) -> None:
    logging.info(
        "EVALUATION - R-Precision Histogram"
    )

    r_precisions_01 = r_precision(
        retrieved_paths[0], expected_paths[0], r, labels[0])
    r_precisions_02 = r_precision(
        retrieved_paths[1], expected_paths[1], r, labels[1])

    r_precision_total = {}
    for query in r_precisions_01.keys():
        r_precision_total[query] = r_precisions_01[query] - \
            r_precisions_02[query]

    plt.bar(r_precision_total.keys(),
            r_precision_total.values(),
            width=0.75,
            color="blue",
            label=labels[0]
            )

    negative = dict(filter(lambda x: x[1] < 0, r_precision_total.items()))
    plt.bar(negative.keys(),
            negative.values(),
            width=0.75,
            color="red",
            label=labels[1]
            )

    plt.plot(
        r_precision_total.keys(),
        [0] * len(r_precision_total.keys()),
        "k--"
    )
    plt.legend()
    logging.info("EVALUATION - Plotted")


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
            reference = set(map(lambda x: x["Document"], documents))
            lim = min(len(documents), n+1)
            test = set(map(lambda x: x["Document"], retrieved[query][:lim]))
            p = precision(reference, test)
            if p > last_precision:
                precisions[query].append(p)
            last_precision = p

    mean_precisions = []
    for p in precisions.values():
        mean_precisions.append(statistics.mean(p))

    m = statistics.mean(mean_precisions)
    utils.write_to_csv(
        f"./avalia/map_{label}.csv", ["label", "map"], [(label, m)])
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
        reference = set(map(lambda x: x["Document"], expected_documents))
        lim = min(
            len(reference), max_n
        )
        for k, retrieved_document in enumerate(retrieved[query][:lim]):
            if k > max_k:
                reciprocal_ranks.append(0)
                break
            if retrieved_document["Document"] in reference:
                reciprocal_ranks.append(1/(k + 1))
                break

    mrr = statistics.mean(reciprocal_ranks)
    utils.write_to_csv(
        f"./avalia/mrr_{label}.csv", ["label", "mrr"], [(label, mrr)])
    logging.info(
        "EVALUATION - %s's MRR: %.02f", label, mrr
    )
    return mrr


def __calculate_discount(rank: int, i: int, dcg_1: int = 0) -> float:
    if i == 1:
        return rank
    return rank/math.log(i, 2) + dcg_1


def discounted_cumulative_gain(retrieved_path: str, expected_path: str, max_n: int, label: str) -> float:
    logging.info(
        "EVALUATION - Calculating %s's DCG", label
    )
    retrieved = __read_retrieved_documents(retrieved_path)
    expected = __read_expected_documents(expected_path)
    dcgs = defaultdict(list)
    for query, expected_documents in expected.items():
        reference = set(map(lambda x: x["Document"], expected_documents))
        # lim = min(
        #     len(expected_documents), max_n
        # )
        lim = max_n
        dcg_1 = 0
        for i, document in enumerate(retrieved[query][:lim]):
            doc_number = document["Document"]
            if doc_number in reference:
                a = filter(lambda x: x["Document"] ==
                           doc_number, expected_documents)
                b = list(map(lambda x: x["Votes"], a))[0]
                dcgs[query].append(__calculate_discount(b, i + 1, dcg_1))
                if i == 0:
                    dcg_1 = b
            else:
                dcgs[query].append(__calculate_discount(0, i + 1, dcg_1))
                if i == 0:
                    dcg_1 = 0

    mean_dcg = {}
    for query, dcg in dcgs.items():
        mean_dcg[query] = statistics.mean(dcg)

    utils.write_to_csv(
        f"./avalia/dcg-mean_{label}.csv", ["label", "query", "dcg"], [(label, query, dcg) for query, dcg in mean_dcg.items()])

    for query, mdcg in mean_dcg.items():
        logging.info(
            "EVALUATION - %s's DCG Q%.02f: %s", label, query, mdcg
        )

    return mean_dcg


def normalized_dicounted_comulative_gain(retrieved_path: str, expected_path: str, max_n: int, label: str) -> Dict[int, float]:
    logging.info(
        "EVALUATION - Calculating %s's DCG", label
    )
    retrieved = __read_retrieved_documents(retrieved_path)
    expected = __read_expected_documents(expected_path)
    ndcgs = defaultdict(float)
    for query, expected_documents in expected.items():
        reference = set(map(lambda x: x["Document"], expected_documents))
        lim = min(
            len(expected_documents), max_n
        )
        sorted_expected_documents = sorted(expected_documents,
                                           key=lambda x: x["Votes"], reverse=True)[:lim]
        idcg = 0
        for i, document in enumerate(sorted_expected_documents):
            idcg += __calculate_discount(document["Votes"], i + 1)
        dcg = 0
        for i, document in enumerate(retrieved[query][:lim]):
            doc_number = document["Document"]
            if doc_number in reference:
                a = filter(lambda x: x["Document"] ==
                           doc_number, expected_documents)
                b = list(map(lambda x: x["Votes"], a))[0]
                dcg += __calculate_discount(b, i + 1)
            else:
                dcg += __calculate_discount(0, i + 1)
        ndcgs[query] = dcg/idcg

    utils.write_to_csv(
        f"./avalia/ndcg_{label}.csv", ["label", "query", "ndcg"], [(label, query, ndcg) for query, ndcg in ndcgs.items()])

    for query, ndcg in ndcgs.items():
        logging.info(
            "EVALUATION - %s's nDCG Q%d: %.02f", label, query, ndcg
        )
    return ndcgs
