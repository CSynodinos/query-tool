#!/usr/bin/env python3
from __future__ import annotations

import os, json, inspect
import numpy as np
import pandas as pd
from pathlib import Path
from scripts.ini_parser import ini_handler

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
    """Parses  through a .json file and writes into a pandas dataframe.

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

class json_db:
    """Convert .json file to database file. sqlite3 and postgres4 are the supported sql distributions.
    """

    db_supp_types = ("sqlite", "postgres")

    def __init__(self, db_type, jsonf) -> None:
        self.db_type = db_type
        self.jsonf = jsonf
        self.db_name = _fl_nm_parser(flstr = self.jsonf, f_type = "db")

    @classmethod
    def __repr__(cls) -> str:
        params = inspect.getfullargspec(__class__).args
        params.remove("self")
        return params

    @classmethod
    def __dir__(cls, only_added = False) -> list:
        """Display function attributes.

        Args:
            * `only_added` (bool, optional): Choose whether to display only the specified attributes. Defaults to False.

        Returns:
            list: List of attributes.
        """

        all_att = list(cls.__dict__.keys())
        if not only_added:
            return all_att
        else:
            default_atts = ['__module__', '__doc__', '__dict__', '__weakref__']
            all_att = [x for x in all_att if x not in default_atts]
            return all_att

    @staticmethod
    def _json_to_sqlite(jsonf: str, db_name: str) -> str:
        """Convert .json file contents to a sqlite3 database.

        Args:
            * `jsonf` (str): .json file name/path.
            * `db_name` (str): Name of .db file.

        Returns:
            str: Database name.
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

    @staticmethod
    def _json_to_postgres(jsonf: str) -> str:
        """Convert .json file contents to a postgres4 database.

        Args:
            * `jsonf` (str): .json file name/path.

        Returns:
            str: Database name.
        """

        lst_dir = os.listdir(os.getcwd())
        for i in lst_dir:
            if not i.endswith('.ini'):
                continue
            else:
                inifl = i
                break
        try:
            inifl
        except NameError:
            print('No .ini file was found in the current working directory.')

        def db_items(dictionary: dict, index: int) -> str:  # Get a dictionary item through its index and store it as a string.
            return list(dictionary.items())[index][1]

        import psycopg2

        # Parse .ini to get db info
        db_info = ini_handler(ini = 'anini.ini')._ini_to_dict()
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
            TypeError: When selected database is not supported.
        """

        if not dbtp in cls.db_supp_types:
            raise TypeError(f'Database engine {dbtp} is not supported. Supported database engines are: {", ".join(cls.db_supp_types)}')

    def invoker(self) -> str:
        """Invoker method for running the requested database generator.
        """

        self._supp_db(dbtp = self.db_type)
        if self.db_type == "sqlite":
            invoked = self._json_to_sqlite(jsonf = self.jsonf, db_name = self.db_name)
            return invoked
        elif self.db_type == "postgres":
            invoked = self._json_to_postgres(jsonf = self.jsonf)
            return invoked
