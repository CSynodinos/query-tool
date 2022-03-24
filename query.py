#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from scripts.query_parser import query_tool
from scripts.search_tool import fl_nm_parser


def args_parser(msg) -> argparse.Namespace:
    """Custom argument parser.
    Args:
        * `msg` ([type]: str): Description help message.
    Returns:
        [type]: Namespace of input arguments.
    """

    parser = argparse.ArgumentParser(description = msg, formatter_class = argparse.RawDescriptionHelpFormatter)
    parser.add_argument("-f", help = "Input file.")
    parser.add_argument("-p", help = "Pattern to look for.")
    parser.add_argument("-json", help = "Export into json file format.")
    parser.add_argument("-inf", help = "Optional argument: Display information about findings.")

    return parser.parse_args()

def main():
    message = "Regex Query Tool. Returns a python dictionary with keys being all the lines/columns that a pattern was found and the lines/cells themselves as values.\nSet -json option as True for writing the dictionary as a .json file"
    args = args_parser(msg = message)
    arguments = vars(args)
    f = arguments.get('f')
    p = arguments.get('p')
    info = arguments.get('inf')
    to_json = arguments.get('json')

    if info == "True" or info == "true" or info == "1":
        info = True
    elif info == "False" or info == "false" or info == "0" or info == None:
        info = False

    if to_json == "True" or to_json == "true" or to_json == "1":
        to_json = True
    elif to_json == "False" or to_json == "false" or to_json == "0" or to_json == None:
        to_json = False

    out = query_tool(fl = f, pattern = p).query(show_idx = info)
    if to_json:
        json_n = fl_nm_parser(flstr = f, f_type = "json")
        print(json_n)
        with open(json_n, 'w') as json_file:
            json.dump(out, json_file)
    return out

if __name__ == "__main__":
    main()