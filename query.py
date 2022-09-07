#!/usr/bin/env python3
from __future__ import annotations

import argparse, os
from lib.query_parser import query_tool
from lib.json_db import json_db, _fl_nm_parser
from typing import Any, Final

def args_parser(msg: str) -> argparse.Namespace:
    """Custom argument parser.

    Args:
        * `msg` (_str_): Description help message.

    Returns:
        argparse.Namespace: Namespace of input arguments.
    """

    PARSER: Final[object] = argparse.ArgumentParser(description = msg, formatter_class = argparse.RawDescriptionHelpFormatter)
    PARSER.add_argument("-f", help = "Input file.")
    PARSER.add_argument("-p", help = "Pattern to look for. If the file is a txt type file, specify a string pattern. If the file is a .csv or .tsv file, specify a csv file containing the patterns to look for.")
    PARSER.add_argument("-o", help = "Optional argument: Output directory for .json file and sqlite3 .db file. Does not work on postgres 4")
    PARSER.add_argument("-json", action = 'store_true' , help = "Optional argument: Export into .json file format. Key is either the lines the pattern was found in (for .txt type files) or the columns (for .csv or .tsv files).")
    PARSER.add_argument("-jname", help = "Optional argument: If -json flag is set, this flag is used to give a name to the .json output file. Default is None.")
    PARSER.add_argument("-db", action = 'store_true', help = "Optional argument: Write the .json output file in a new database when option -json is used. If -pg option is not set, the database will be sqlite3")

    PARSER.add_argument("-pg", help = "Optional argument: Write the .json output file in a new postgres 4 database when option -json is used."
                        "This argument needs the name of the .ini file that has the postgres database information. Check the template.ini file "
                        "for more info for the .ini organization.")

    PARSER.add_argument("-inf", action = 'store_true', help = "Optional argument: Display information about findings in the stdout.")
    return PARSER.parse_args()

def bool_parser(var: Any) -> bool:
    """Check if parameter is boolean, if not, convert it to boolean.

    Args:
        * `var` (Any): variable to check for boolean.

    Raises:
        TypeError: Unable to convert to boolean.

    Returns:
        boolean: True if var is boolean, False if not.
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
    MESSAGE = ("\t\t\tRegex Query Tool\n\nReturns a python dictionary with keys being all the lines/columns" 
    "\nthat a pattern was found and the lines/cells themselves as values.\nSet -json "
    "option as True for writing the dictionary as a .json file.")

    ARGS_NAMESPACE: argparse.Namespace = args_parser(msg = MESSAGE)
    ARGUMENTS: dict[str, Any] = vars(ARGS_NAMESPACE)
    FILE: str | None = ARGUMENTS.get('f')
    PATTERN: str | None = ARGUMENTS.get('p')
    OUTPUT: str | None = ARGUMENTS.get('o')
    JSON: bool = ARGUMENTS.get('json')
    JSON_NAME: str | None = ARGUMENTS.get('jname')
    JSON_DB: bool = ARGUMENTS.get('db')
    JSON_POSTGRES: str | None = ARGUMENTS.get('pg')
    INFO: bool = ARGUMENTS.get('inf')

    out: dict = query_tool(fl = FILE, pattern = PATTERN).query_wrapper(show_idx = INFO)
    if JSON:
        if not JSON_NAME == None or JSON_NAME == 'None':
            json_n = _fl_nm_parser(flstr = JSON_NAME, f_type = "json")
        else:
            json_n = _fl_nm_parser(flstr = FILE, f_type = "json")

        import json
        if OUTPUT:
            if os.path.isdir(OUTPUT):
                json_n = os.path.join(OUTPUT, json_n)
            else:
                os.makedirs(OUTPUT)
                json_n = os.path.join(OUTPUT, json_n)

        with open(json_n, 'w') as json_file:
            json.dump(out, json_file, default = lambda o: o.__dict__, sort_keys = True, indent = 2)

        if JSON_DB:
            if not JSON_POSTGRES == None or JSON_POSTGRES == 'None':
                print('Insertion of .json keys and values into a postgres4 database.')
                output = json_db(db_type = 'postgres', jsonf = json_n, ini = JSON_POSTGRES).invoker(out = OUTPUT)
                print(f'Operation Complete! Data parsed into the {output} database.')
            else:
                print('Insertion of .json keys and values into a sqlite3 database.')
                json_db(db_type = 'sqlite', jsonf = json_n).invoker(out = OUTPUT)
                print('Operation Complete!')

    if not JSON:
        if JSON_DB:
            raise RuntimeError("Option -db was used without setting option -json as True.")

if __name__ == "__main__":
    main()