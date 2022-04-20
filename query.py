#!/usr/bin/env python3
from __future__ import annotations

import argparse
from scripts.query_parser import query_tool
from scripts.json_db import json_db, _fl_nm_parser

class InputflError(Exception):
    """Custom exception class for input files."""

    __module__ = 'builtins'

    def __init__(self, *args) -> None:
        if args:
            self.errmessage = args[0]
        else:
            self.errmessage = None

    def __repr__(self) -> str:
        if self.errmessage:
            return '{0} '.format(self.errmessage)
        else:
            return 'InputflError has been raised'

def args_parser(msg) -> argparse.Namespace:
    """Custom argument parser.

    Args:
        * `msg` (_str_): Description help message.

    Returns:
        _argparse.Namespace_: Namespace of input arguments.
    """

    parser = argparse.ArgumentParser(description = msg, formatter_class = argparse.RawDescriptionHelpFormatter)
    parser.add_argument("-f", help = "Input file.")
    parser.add_argument("-p", help = "Pattern to look for.")
    parser.add_argument("-json", help = "Optional argument: Export into .json file format.")
    parser.add_argument("-db", help = "Optional argument: Write the .json output file in a new database when option -json is used. If -pg option is not set, the database will be sqlite3")
    parser.add_argument("-pg", help = "Optional argument: Write the .json output file in a new postgres 4 database when option -json is used.")
    parser.add_argument("-inf", help = "Optional argument: Display information about findings.")
    return parser.parse_args()

def bool_parser(var: any) -> bool:
    """Check if parameter is boolean, if not, convert it to boolean.

    Args:
        * `var` (Any): variable to check for boolean.

    Raises:
        TypeError: Unable to convert to boolean.

    Returns:
        _bool_.
    """

    _true = ["true", "True", "1"]
    _false = ["false", "False", "0", None]
    if type(var) == bool:
        return var
    else:
        if var in _true:
            return True
        elif var in _false:
            return False
        else:
            raise TypeError(f"{var} must be true, True, 1, False, false, 0 or None.")

def main():
    message = ("\t\t\tRegex Query Tool\n\nReturns a python dictionary with keys being all the lines/columns" 
    "\nthat a pattern was found and the lines/cells themselves as values.\nSet -json "
    "option as True for writing the dictionary as a .json file.")

    args = args_parser(msg = message)
    arguments = vars(args)
    f = arguments.get('f')
    p = arguments.get('p')
    to_json = bool_parser(arguments.get('json'))
    json_to_db = bool_parser(arguments.get('db'))
    json_to_db_pg = bool_parser(arguments.get('pg'))
    info = bool_parser(arguments.get('inf'))

    out = query_tool(fl = f, pattern = p).query_wrapper(show_idx = info)
    if to_json:
        import json
        json_n = _fl_nm_parser(flstr = f, f_type = "json")
        with open(json_n, 'w') as json_file:
            json.dump(out, json_file)

        if json_to_db:
            if json_to_db_pg:
                print('Insertion of .json keys and values into a postgres4 database.')
                output = json_db(db_type = 'postgres', jsonf = json_n).invoker()
                print(f'Operation Complete! Data parsed into the {output} database.')
                return out
            else:
                print('Insertion of .json keys and values into a sqlite3 database.')
                json_db(db_type = 'sqlite', jsonf = json_n).invoker()
                print('Operation Complete!')
                return out
        else:
            return out

    if not to_json:
        if json_to_db:
            raise RuntimeError("Option -db was used without setting option -json as True.")
        else:
            return out

if __name__ == "__main__":
    main()