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
        queries_path = config["DEFAULT"]["LEIA"]
        parsed_queries_path = config["DEFAULT"]["CONSULTAS"]
        expected_path = config["DEFAULT"]["ESPERADOS"]
        query.parse(queries_path, parsed_queries_path,
                    expected_path, steemer=False)
        # query.parse(queries_path, parsed_queries_path,
        #             expected_path, steemer=True)

    if kwargs["create_inverted_list"] and not kwargs["run_indexer"]:
        config.read(kwargs["config_gli"])
        documents_paths = config["DEFAULT"]["LEIA"]
        inverted_list_path = config["DEFAULT"]["ESCREVA"]
        documents_paths = documents_paths.split(",")
        documents_paths = list(
            filter(lambda document_path: document_path.strip()
                   != "", documents_paths)
        )

        inverted_list.parse(documents_paths, inverted_list_path, steemer=False)
        # inverted_list.parse(documents_paths, inverted_list_path, steemer=True)

    if kwargs["run_indexer"]:
        config.read(kwargs["config_gli"])
        inverted_list_path = config["DEFAULT"]["ESCREVA"]

        config.read(kwargs["config_index"])
        documents_paths = config["DEFAULT"]["LEIA"]
        model_path = config["DEFAULT"]["ESCREVA"]
        documents_paths = documents_paths.split(",")
        documents_paths = list(
            filter(lambda input_path: input_path.strip() != "", documents_paths)
        )
        indexer.write_model(
            documents_paths, inverted_list_path, model_path, steemer=False)
        # indexer.write_model(
        #     documents_paths, inverted_list_path, model_path, steemer=True)

    if kwargs["search"]:
        config.read(kwargs["config_busca"])
        queries_path = config["DEFAULT"]["CONSULTAS"]
        results_path = config["DEFAULT"]["RESULTADOS"]
        model_path = config["DEFAULT"]["MODELO"]
        search.retrieve_documents(
            queries_path, results_path, model_path, steemer=False)
        # search.retrieve_documents(
        #     queries_path, results_path, model_path, steemer=True)

    if kwargs["evaluate"]:
        config.read(kwargs["config_avaliacao"])
        expected_path = config["DEFAULT"]["ESPERADOS"]
        retrieved_path = config["DEFAULT"]["RESULTADOS"]
        max_results = int(config["DEFAULT"]["MAX"])
        evaluate.interpoloated_average_precision_11_point_graph(
            retrieved_path, expected_path, "NOSTEEMER"
        )
        evaluate.interpoloated_average_precision_11_point_graph(
            retrieved_path, expected_path, "STEEMER"
        )
        plt.legend()
        plt.show()
        plt.clf()

        evaluate.f1_score(retrieved_path, expected_path,
                          "NOSTEEMER", max_results)
        evaluate.f1_score(retrieved_path, expected_path,
                          "STEEMER", max_results)

        evaluate.precision_at_n(retrieved_path, expected_path, 5, "NOSTEEMER")
        evaluate.precision_at_n(retrieved_path, expected_path, 5, "STEEMER")

        evaluate.precision_at_n(retrieved_path, expected_path, 10, "NOSTEEMER")
        evaluate.precision_at_n(retrieved_path, expected_path, 10, "STEEMER")

        evaluate.r_precision_histogram(
            [retrieved_path, retrieved_path],
            [expected_path, expected_path],
            max_results,
            ["NOSTEEMER", "STEEMER"]
        )
        plt.show()
        plt.clf()

        evaluate.mean_average_precision(
            retrieved_path, expected_path, max_results, "NOSTEEMER")
        evaluate.mean_average_precision(
            retrieved_path, expected_path, max_results, "STEEMER")

        evaluate.mean_reciprocal_rank(
            retrieved_path, expected_path, 10, max_results, "NOSTEEMER")
        evaluate.mean_reciprocal_rank(
            retrieved_path, expected_path, 10, max_results, "STEEMER")

        evaluate.discounted_cumulative_gain(
            retrieved_path, expected_path, max_results, "NOSTEEMER")
        evaluate.discounted_cumulative_gain(
            retrieved_path, expected_path, max_results, "STEEMER")

        evaluate.normalized_dicounted_comulative_gain(
            retrieved_path, expected_path, max_results, "NOSTEEMER")
        evaluate.normalized_dicounted_comulative_gain(
            retrieved_path, expected_path, max_results, "STEEMER")

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
