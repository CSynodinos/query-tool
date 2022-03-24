#!/usr/bin/env python3
from __future__ import annotations

import json
import numpy as np
import pandas as pd
from search_tool import fl_nm_parser
from pathlib import Path

def json_loader(jfl):
    with open(jfl) as f:
        data = json.load(f)
        data = dict((k.strip(), v.strip()) for k, v in data.items())    # Replace leading and trailing whitespace with ""
        data = {k.replace(' ', '_'): v for k, v in data.items()}    # Replace whitespace in keys and values with _
        data = {k.replace('__', '_'): v for k, v in data.items()}   # Replace double whitespace in keys and values with _

    return pd.DataFrame(data, index=[0])

def df_parser(jsonf):
    df = json_loader(jfl = jsonf)
    cols = list(df.columns)
    rows = list(df.values)
    rows = np.array(rows).tolist()[0]

    return cols, rows

class json_db:
    
    def __init__(self, db_type, json_f) -> None:
        self.db_type = db_type
        self.jsonf = json_f
        self.db_name = fl_nm_parser(flstr = self.jsonf, f_type = "db")

    def json_to_sqlite(self):
        
        import sqlite3
        cols, rows = df_parser(jsonf = self.jsonf)

        con = sqlite3.connect(self.db_name)
        cur = con.cursor()
        table_name = f'{Path(self.jsonf).stem}_table'
        cur.execute(f'''CREATE TABLE {table_name} (json_keys, json_values)''')

        # Iterate through cols and rows and add each cols values into json_keys column and each rows value into json_values column.
        for key, val in zip(cols, rows):
            cur.execute(f"INSERT INTO {table_name} (json_keys, json_values) VALUES (?,?)", (key,val))
        con.commit()

    ## Not yet ready.
    def json_to_postgres(self):
        
        from sqlalchemy import create_engine
        df = json_loader(jfl = self.jsonf)
        engine = create_engine(f"postgresql:///{self.db_name}")
        

if __name__ == "__main__":
    json_db(db_type = "sqlite", json_f = "Wuhan.json").json_to_sqlite()