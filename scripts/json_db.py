#!/usr/bin/env python3
from __future__ import annotations

import os, json
import numpy as np
import pandas as pd
from pathlib import Path
from scripts.ini_parser import ini_handler

def _fl_nm_parser(flstr: str, f_type: str) -> str:
    """File name parser. Extracts the name of a file without the path and extension.
    Adds a different extension at the end of it.

    Args:
        * `flstr` (_type_: str): File name.
        * `f_type` (_type_: str): Extension type to return.

    Returns:
        _type_: str: Name of file without path and extension
    """

    nm = f"{flstr.rsplit('.', 1)[0]}.{f_type}"
    if not len(os.path.split(nm)[0]) == 0:
        nm = os.path.split(nm)[1]
    return nm

def __json_df_parser(jfl: str) -> pd.DataFrame:
    """Parses  through a .json file and writes into a pandas dataframe.

    Args:
        * `jfl` (_type_: str): .json file to parse.

    Returns:
        _type_: `pd.DataFrame`: A pandas dataframe containing the keys of a .json as columns and the values as rows.
    """

    with open(jfl) as f:
        data = json.load(f)
        data = dict((k.strip(), v.strip()) for k, v in data.items())    # Replace leading and trailing whitespace with ""
    return pd.DataFrame(data, index=[0])

def _df_parser(jsonf) -> tuple[list, list]:
    """.json to dataframe parser.

    Args:
        * `jsonf` (_type_: str): .json file to parse.

    Returns:
        _type_: `list`, `list`: Two lists containing all column names and row values as separate elements.
    """

    df = __json_df_parser(jfl = jsonf)
    cols = list(df.columns)
    rows = list(df.values)  # numpy array.
    rows = np.array(rows).tolist()[0]
    return cols, rows

class json_db:
    """Temp: convert .json to database. Target is sqlite3 and postgres4. Need to add a __repr__.
    """

    db_supp_types = ("sqlite", "postgres")

    def __init__(self, db_type, json_f) -> None:
        self.db_type = db_type
        self.jsonf = json_f
        self.db_name = _fl_nm_parser(flstr = self.jsonf, f_type = "db")

    @staticmethod
    def _json_to_sqlite(jsonf, db_name) -> None:
        
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

    @staticmethod
    def _json_to_postgres(jsonf):
        

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

        def db_items(dictionary: dict, index: int) -> str:
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
    def __supp_db(cls, dbtp: str) -> None:
        if not dbtp in cls.db_supp_types:
            raise TypeError(f'Database engine {dbtp} is not supported. Supported database engines are: {", ".join(cls.db_supp_types)}')

    def invoker(self) -> None:
        """Invoker method for running the requested database generator.
        """

        self.__supp_db(dbtp = self.db_type)
        if self.db_type == "sqlite":
            invoked = self._json_to_sqlite(jsonf = self.jsonf, db_name = self.db_name)
            return invoked
        elif self.db_type == "postgres":
            invoked = self._json_to_postgres(jsonf = self.jsonf)
            return invoked
