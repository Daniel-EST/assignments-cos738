import argparse
import configparser
import logging

import matplotlib.pyplot as plt

from parsers import indexer, inverted_list, query, search, evaluate

logging.basicConfig(
    format="%(levelname)s: %(message)s",
    level=logging.INFO
)

config = configparser.ConfigParser()


def main(**kwargs) -> None:
    """
    Main function for information retrieval code using tf-idf.

    This function takes in keyword arguments (**kwargs) to perform several tasks related to information retrieval.
    The tasks performed by the function include parsing queries, creating an inverted list, running an indexer, and searching for results.
    The function reads configuration files to obtain the necessary input data for each task.

    If the 'parse_queries' flag is True, the function reads a configuration file to obtain query-related paths and passes them to the `parse` function from a `query` module.

    If the 'create_inverted_list' flag is True and the 'run_indexer' flag is False, the function reads a configuration file to obtain document-related paths and passes them to the `parse` function from an `inverted_list` module.

    If the 'run_indexer' flag is True, the function reads two configuration files to obtain document-related and index-related paths, and passes them to the `write_model` function from an `indexer` module.

    If the 'search' flag is True, the function reads a configuration file to obtain model-related, query-related, and result-related paths, and prints the values of these paths.

    Args:
        **kwargs: Keyword arguments to control the behavior of the function.

    Returns:
        None
    """
    logging.info("Program started")
    if kwargs["parse_queries"]:
        config.read(kwargs["config_pc"])
        queries_path = config["NOSTEEMER"]["LEIA"]
        parsed_queries_path = config["NOSTEEMER"]["CONSULTAS"]
        expected_path = config["NOSTEEMER"]["ESPERADOS"]
        query.parse(queries_path, parsed_queries_path,
                    expected_path, steemer=False)

        queries_path = config["STEEMER"]["LEIA"]
        parsed_queries_path = config["STEEMER"]["CONSULTAS"]
        expected_path = config["STEEMER"]["ESPERADOS"]
        query.parse(queries_path, parsed_queries_path,
                    expected_path, steemer=True)

    if kwargs["create_inverted_list"] and not kwargs["run_indexer"]:
        config.read(kwargs["config_gli"])
        documents_paths = config["NOSTEEMER"]["LEIA"]
        inverted_list_path = config["NOSTEEMER"]["ESCREVA"]
        documents_paths = documents_paths.split(",")
        documents_paths = list(
            filter(lambda document_path: document_path.strip()
                   != "", documents_paths)
        )
        inverted_list.parse(documents_paths, inverted_list_path, steemer=False)

        documents_paths = config["STEEMER"]["LEIA"]
        inverted_list_path = config["STEEMER"]["ESCREVA"]
        documents_paths = documents_paths.split(",")
        documents_paths = list(
            filter(lambda document_path: document_path.strip()
                   != "", documents_paths)
        )
        inverted_list.parse(documents_paths, inverted_list_path, steemer=True)

    if kwargs["run_indexer"]:
        config.read(kwargs["config_gli"])
        inverted_list_path = config["NOSTEEMER"]["ESCREVA"]

        config.read(kwargs["config_index"])
        documents_paths = config["NOSTEEMER"]["LEIA"]
        model_path = config["NOSTEEMER"]["ESCREVA"]
        documents_paths = documents_paths.split(",")
        documents_paths = list(
            filter(lambda input_path: input_path.strip() != "", documents_paths)
        )
        indexer.write_model(
            documents_paths, inverted_list_path, model_path, steemer=False)

        config.read(kwargs["config_gli"])
        inverted_list_path = config["STEEMER"]["ESCREVA"]

        config.read(kwargs["config_index"])
        documents_paths = config["STEEMER"]["LEIA"]
        model_path = config["STEEMER"]["ESCREVA"]
        documents_paths = documents_paths.split(",")
        documents_paths = list(
            filter(lambda input_path: input_path.strip() != "", documents_paths)
        )
        indexer.write_model(
            documents_paths, inverted_list_path, model_path, steemer=True)

    if kwargs["search"]:
        config.read(kwargs["config_busca"])
        queries_path = config["NOSTEEMER"]["CONSULTAS"]
        results_path = config["NOSTEEMER"]["RESULTADOS"]
        model_path = config["NOSTEEMER"]["MODELO"]
        search.retrieve_documents(
            queries_path, results_path, model_path, steemer=False)

        queries_path = config["STEEMER"]["CONSULTAS"]
        results_path = config["STEEMER"]["RESULTADOS"]
        model_path = config["STEEMER"]["MODELO"]
        search.retrieve_documents(
            queries_path, results_path, model_path, steemer=True)

    if kwargs["evaluate"]:
        config.read(kwargs["config_avaliacao"])
        NOSTEEMER_expected_path = config["NOSTEEMER"]["ESPERADOS"]
        NOSTEEMER_retrieved_path = config["NOSTEEMER"]["RESULTADOS"]
        NOSTEEMER_max_results = int(config["NOSTEEMER"]["MAX"])

        STEEMER_expected_path = config["STEEMER"]["ESPERADOS"]
        STEEMER_retrieved_path = config["STEEMER"]["RESULTADOS"]
        STEEMER_max_results = int(config["STEEMER"]["MAX"])

        max_results = max(NOSTEEMER_max_results, STEEMER_max_results)

        evaluate.interpoloated_average_precision_11_point_graph(
            NOSTEEMER_retrieved_path, NOSTEEMER_expected_path, "NOSTEEMER", "red"
        )
        evaluate.interpoloated_average_precision_11_point_graph(
            STEEMER_retrieved_path, STEEMER_expected_path, "STEEMER", "blue"
        )
        plt.legend()
        plt.savefig("./avalia/11pontos.jpeg")
        plt.clf()

        evaluate.f1_score(NOSTEEMER_retrieved_path, NOSTEEMER_expected_path,
                          "NOSTEEMER", max_results)
        evaluate.f1_score(STEEMER_retrieved_path, STEEMER_expected_path,
                          "STEEMER", max_results)

        evaluate.precision_at_n(NOSTEEMER_retrieved_path,
                                NOSTEEMER_expected_path, 5, "NOSTEEMER")
        evaluate.precision_at_n(STEEMER_retrieved_path,
                                STEEMER_expected_path, 5, "STEEMER")

        evaluate.precision_at_n(NOSTEEMER_retrieved_path,
                                NOSTEEMER_expected_path, 10, "NOSTEEMER")
        evaluate.precision_at_n(STEEMER_retrieved_path,
                                STEEMER_expected_path, 10, "STEEMER")

        evaluate.r_precision_histogram(
            [NOSTEEMER_retrieved_path, STEEMER_retrieved_path],
            [NOSTEEMER_expected_path, STEEMER_expected_path],
            max_results,
            ["NOSTEEMER", "STEEMER"]
        )
        plt.savefig("./avalia/histograma.jpeg")
        plt.clf()

        evaluate.mean_average_precision(
            NOSTEEMER_retrieved_path, NOSTEEMER_expected_path, max_results, "NOSTEEMER")
        evaluate.mean_average_precision(
            STEEMER_retrieved_path, STEEMER_expected_path, max_results, "STEEMER")

        evaluate.mean_reciprocal_rank(
            NOSTEEMER_retrieved_path, NOSTEEMER_expected_path, 10, max_results, "NOSTEEMER")
        evaluate.mean_reciprocal_rank(
            STEEMER_retrieved_path, STEEMER_expected_path, 10, max_results, "STEEMER")

        evaluate.discounted_cumulative_gain(
            NOSTEEMER_retrieved_path, NOSTEEMER_expected_path, max_results, "NOSTEEMER")
        evaluate.discounted_cumulative_gain(
            STEEMER_retrieved_path, STEEMER_expected_path, max_results, "STEEMER")

        evaluate.normalized_dicounted_comulative_gain(
            NOSTEEMER_retrieved_path, NOSTEEMER_expected_path, max_results, "NOSTEEMER")
        evaluate.normalized_dicounted_comulative_gain(
            STEEMER_retrieved_path, STEEMER_expected_path, max_results, "STEEMER")

    logging.info("End of program")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--config-pc", type=str,
                        default="./config/pc.cfg", help="Sets the config file path for pc")
    parser.add_argument("--config-gli", type=str,
                        default="./config/gli.cfg", help="Sets the config file path for gli")
    parser.add_argument("--config-index", type=str,
                        default="./config/index.cfg", help="Sets the config file path for index")
    parser.add_argument("--config-busca", type=str,
                        default="./config/busca.cfg", help="Sets the config file path for busca")
    parser.add_argument("--config-avaliacao", type=str,
                        default="./config/avaliacao.cfg", help="Sets the config file path for avaliacao")
    parser.add_argument("--parse-queries", type=bool,
                        default=True, help="Sets if it should parse queries")
    parser.add_argument("--create-inverted-list",
                        type=bool, default=False, help="Sets if it should create inverted list")
    parser.add_argument("--run-indexer", type=bool,
                        default=True, help="Sets if it should run indexer")
    parser.add_argument("--search", type=bool, default=True,
                        help="Sets if it should performe a query")
    parser.add_argument("--evaluate", type=bool, default=True,
                        help="Sets if it should performe a evaluation")
    parser.add_argument("-q", "--query", type=str,
                        default="", help="Text for a single query")
    args = vars(parser.parse_args())
    main(**args)
