#!/usr/bin/env python3
from __future__ import annotations

import os, json
import numpy as np
import pandas as pd
from pathlib import Path

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

def __df_parser(jsonf) -> tuple[list, list]:
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

    def __init__(self, db_type, json_f) -> None:
        self.db_type = db_type
        self.jsonf = json_f
        self.db_name = _fl_nm_parser(flstr = self.jsonf, f_type = "db")

    @staticmethod
    def _json_to_sqlite(jsonf, db_name):
        
        import sqlite3
        cols, rows = __df_parser(jsonf = jsonf)

        con = sqlite3.connect(db_name)
        cur = con.cursor()
        table_name = f'{Path(jsonf).stem}_table'
        cur.execute(f'''CREATE TABLE {table_name} (json_keys, json_values)''')

        # Iterate through cols and rows and add each column values into json_keys column and each rows value into json_values column.
        for key, val in zip(cols, rows):
            cur.execute(f"INSERT INTO {table_name} (json_keys, json_values) VALUES (?,?)", (key,val))
        con.commit()

    ## Not yet ready.
    def _json_to_postgres(jsonf, db_name):
        
        from sqlalchemy import create_engine
        df = __json_df_parser(jfl = jsonf)
        engine = create_engine(f"postgresql:///{db_name}")
        con = engine.connect(db_name)

    ## Will act as an invoker of each json_to_db type function.
    ## May be worth adding functionality ot figure out the db type.
    def invoker(self):
        if self.db_type == "sqlite":
            self._json_to_sqlite(jsonf = self.jsonf, db_name = self.db_name)
        elif self.db_type == "postgres":
            pass
            #self._json_to_postgres(jsonf = self.jsonf, db_name = self.db_name)

if __name__ == "__main__":
    json_db(db_type = "sqlite", json_f = "example_files/patterns.json").invoker()