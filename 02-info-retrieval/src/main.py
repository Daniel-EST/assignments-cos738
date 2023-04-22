import logging
import argparse
import utils

import configparser

from parsers import query, inverted_list


logging.basicConfig(
    format="%(levelname)s: %(message)s",
    level=logging.INFO
)


def main(**kwargs) -> None:
    config = configparser.ConfigParser()
    config.read(utils.get_config_path("pc.cfg"))
    input_path = config["DEFAULT"]["LEIA"]
    output_queries_path = config["DEFAULT"]["CONSULTAS"]
    output_expected_path = config["DEFAULT"]["ESPERADOS"]
    query.parse(input_path, output_queries_path, output_expected_path)

    config.read(utils.get_config_path("gli.cfg"))
    input_paths = config["DEFAULT"]["LEIA"]
    output_path = config["DEFAULT"]["ESCREVA"]
    input_paths = input_paths.split(",")
    input_paths = list(
        filter(lambda input_path: input_path.strip() != "", input_paths)
    )
    inverted_list.parse(input_paths, output_path)

    # for key, value in kwargs.items():
    #     print("The value of {} is {}".format(key, value))


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    args = vars(parser.parse_args())
    main(**args)
