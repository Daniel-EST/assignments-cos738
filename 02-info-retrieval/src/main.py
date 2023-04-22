from typing import TextIO
import logging
import argparse
import utils

import os
import configparser

from parsers import query, inverted_list


logging.basicConfig(
    format="%(levelname)s: %(message)s",
    level=logging.INFO
)


def main(**kwargs):
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
    input_paths = list(filter(lambda input_path: input_path.strip() != "", input_paths))
    inverted_list.parse(input_paths, output_path)

    # for key, value in kwargs.items():
    #     print("The value of {} is {}".format(key, value))


if __name__ == "__main__":
    parser = argparse.ArgumentParser()

    parser.add_argument("--plaintext", type=str, default="",
                        help="your secret plaintext, use a double-quotes if necessary")
    # parser.add_argument("--context", type=str, default="", help="context used for steganography, use a double-quotes if necessary")
    # parser.add_argument("--encrypt", type=str, default="arithmetic", choices=["arithmetic", "utf8"])
    # parser.add_argument("--encode", type=str, default="bins", choices=["bins", "huffman", "arithmetic", "saac"])
    # parser.add_argument("--lm", type=str, default="gpt2")
    # parser.add_argument("--device", type=str, default="0", help="your gpu device id")
    # parser.add_argument("--block_size", type=int, default=4, help="block_size for bin/huffman encoding method")
    # parser.add_argument("--precision", type=int, default=26, help="precision for arithmetic encoding method")
    # parser.add_argument("--temp", type=float, default=1.0, help="temperature for arithemtic/huffman encoding method")
    # parser.add_argument("--topK", type=int, default=50, help="topK for arithemtic encoding method")
    # parser.add_argument("--nucleus", type=float, default=0.95, help="neclues for adaptive arithemtic encoding method")
    # parser.add_argument("--delta", type=float, default=0.01, help="delta for adaptive arithemtic encoding method")
    args = vars(parser.parse_args())

    main(**args)
