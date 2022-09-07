#!/usr/bin/env python3
from __future__ import annotations

import os, json
import numpy as np
import pandas as pd
from pathlib import Path
from lib.ini_parser import ini_handler
from lib.utils import dunders
from lib.exceptions import DBTypeError, InputflError

def _fl_nm_parser(flstr: str, f_type: str) -> str:
    """File name parser. Extracts the name of a file without the path and extension.
    Adds a different extension at the end of it.

    Args:
        * `flstr` (str): File name.
        * `f_type` (str): Extension type to return.

    Returns:
        str: Name of file without path and extension
    """

    nm = f"{flstr.rsplit('.', 1)[0]}.{f_type}"
    if not len(os.path.split(nm)[0]) == 0:
        nm = os.path.split(nm)[1]
    return nm

def __json_df_parser(jfl: str) -> pd.DataFrame:
    """Parses through a .json file and writes into a pandas dataframe.

    Args:
        * `jfl` (str): .json file to parse.

    Returns:
        pd.DataFrame: A pandas dataframe containing the keys of a .json as columns and the values as rows.
    """

    with open(jfl) as f:
        data = json.load(f)
        data = dict((k.strip(), v.strip()) for k, v in data.items())    # Replace leading and trailing whitespace with ""
    return pd.DataFrame(data, index=[0])

def _df_parser(jsonf: str) -> tuple[list, list]:
    """.json to dataframe parser.

    Args:
        * `jsonf` (str): .json file to parse.

    Returns:
        tuple[list, list]: Two lists containing all column names and row values as separate elements.
    """

    df = __json_df_parser(jfl = jsonf)
    cols = list(df.columns)
    rows = list(df.values)  # numpy array.
    rows = np.array(rows).tolist()[0]
    return cols, rows

class json_db(dunders):
    """Convert .json file to database file. sqlite3 and postgres4 are the supported sql distributions.

    Args:
        * `db_type` (str): _description_
        * `jsonf` (str): Name of .json file.
        * `ini` (str, optional): Name of .ini file for postgres parsing. Defaults to None.

    Raises:
        `InputflError`: Input file does not exist.
    """

    db_supp_types = ("sqlite", "postgres")

    def __init__(self, db_type, jsonf, ini = None) -> None:
        self.db_type = db_type
        self.jsonf = jsonf
        self.ini = ini
        if not self.ini == None:
            if not os.path.isfile(self.ini):
                raise InputflError(f'.ini file: {self.ini} does not exist.')

        self.db_name = _fl_nm_parser(flstr = self.jsonf, f_type = "db")
        super().__init__()

    @staticmethod
    def _json_to_sqlite(jsonf: str, db_name: str) -> str:
        """Convert .json file contents to a sqlite3 database.

        Args:
            * `jsonf` (str): .json file name/path.
            * `db_name` (str): Name of .db file.

        Returns:
            `str`: Database name.
        """

        import sqlite3
        cols, rows = _df_parser(jsonf = jsonf)

        con = sqlite3.connect(db_name)
        cur = con.cursor()
        table_name = f'{Path(jsonf).stem}_table'
        cur.execute(f'''CREATE TABLE {table_name} (json_keys, json_values)''')

        # Iterate through cols and rows and add each column values into json_keys column and each rows value into json_values column.
        for key, val in zip(cols, rows):
            cur.execute(f"INSERT INTO {table_name} (json_keys, json_values) VALUES (?,?)", (key,val))
        con.commit()
        return db_name

    def _json_to_postgres(self, jsonf: str) -> str:
        """Convert .json file contents to a postgres4 database.

        Args:
            * `jsonf` (str): .json file name/path.

        Returns:
            `str`: Database name.
        """

        def db_items(dictionary: dict, index: int) -> str:  # Get a dictionary item through its index and store it as a string.
            return list(dictionary.items())[index][1]

        import psycopg2

        # Parse .ini to get db info
        db_info = ini_handler(ini = self.ini)._ini_to_dict()
        pgdatabase = db_items(dictionary = db_info, index = 0)
        pguser = db_items(dictionary = db_info, index = 1)
        pgpassword = db_items(dictionary = db_info, index = 2)
        pghost = db_items(dictionary = db_info, index = 3)
        pgport = db_items(dictionary = db_info, index = 4)

        conn = psycopg2.connect(user = pguser, password = pgpassword)
        conn.autocommit = True
        cur = conn.cursor()

        # Create database and exit.
        cur.execute(f'''CREATE database {pgdatabase}''')
        conn.commit()
        conn.close()

        # Reconnect to created db and run commands.
        conn = psycopg2.connect(database = pgdatabase, user = pguser, password = pgpassword, host = pghost, port = pgport)
        conn.autocommit = True
        cur = conn.cursor()
        table_name = f'{Path(jsonf).stem}_table'
        cur.execute(f"""CREATE TABLE {table_name} (json_keys VARCHAR(255) UNIQUE NOT NULL, json_values VARCHAR(255) UNIQUE NOT NULL)""")
        cols, rows = _df_parser(jsonf = jsonf)

        # Iterate through cols and rows and add each column values into json_keys column and each rows value into json_values column.
        for key, val in zip(cols, rows):
            cur.execute(f"INSERT INTO {table_name} (json_keys, json_values) VALUES (%s,%s)", (key,val))
        conn.commit()
        conn.close()

        return pgdatabase

    @classmethod
    def _supp_db(cls, dbtp: str) -> None:
        """Check if user selected database type is supported by the current version of the tool.

        Args:
            * `dbtp` (str): Type of selected database.

        Raises:
            `DBTypeError`: When selected database is not supported.
        """

        if not dbtp in cls.db_supp_types:
            raise DBTypeError(f'Database engine {dbtp} is not supported. Supported database engines are: {", ".join(cls.db_supp_types)}')

    def invoker(self, out) -> str:
        """Invoker method for running the requested database generator.
        """

        func_dict = {'sqlite': self._json_to_sqlite,
                    'postgres': self._json_to_postgres}

        self._supp_db(dbtp = self.db_type)
        if self.db_type in func_dict:
            if out:
                self.db_name = os.path.join(out, self.db_name)
            if self.db_type == 'sqlite':
                invoked = func_dict[self.db_type](self.jsonf, db_name = self.db_name)
            else:
                invoked = func_dict[self.db_type](jsonf = self.jsonf)
            return invoked
        else:
            raise KeyError(f'{self.db_type} key is not present in the functions dictionary in the invoker method.')
