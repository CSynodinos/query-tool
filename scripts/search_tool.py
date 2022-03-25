#!/usr/bin/env python3
from __future__ import annotations

import re, csv
import pandas as pd
import os
import inspect

class RegexError(Exception):
    """Custom exception class for non-existant patterns.
    """

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
            return 'RegexError has been raised'

class search_tools:
    """_summary_

    Raises:
        RegexError: _description_

    Returns:
        _type_: _description_
    """

    txt_ext = ('.txt', '.ini', '.fasta')
    sp_ext = ('.csv', '.tsv')

    def __init__(self, fl: str, pattern: str) -> None:
        self.fl = fl
        self.pattern = pattern

    def __repr__(self) -> str:
        params = inspect.getfullargspec(__class__).args
        params.remove("self")
        return f'{__class__.__name__}({params[0]} = "{self.fl}", {params[1]} = "{self.pattern}")'

    @classmethod
    def _fl_parser(cls, fl: str, pat: str) -> (list | dict):
        
        assert fl, 'No file name or path was provided.'
        assert pat, 'No pattern was provided.'

        if fl.endswith(cls.txt_ext):
            data_found = []
            with open(fl, "r") as txt:
                lines = txt.readlines()
                txt.seek(0)
                for index, line in enumerate(lines):
                    ln_index = str(index)+': '+line
                    ln_index = ln_index.replace('\n', '')
                    data_found.append(ln_index)

        elif fl.endswith(cls.sp_ext):
            data_found = {}
            with open(fl, "r", encoding = 'utf-8-sig') as csv_file:
                csv_reader = csv.reader(csv_file, delimiter = ',')
                headers = []
            
                # loop through csv and get the first row (headers)
                for row in csv_reader:
                    headers.append(row)
                    break
                headers = [item for elem in headers for item in elem]

                db_name = "tmp.db"

            import sqlite3
            con = sqlite3.connect(db_name)
            cur = con.cursor()
            pd.read_csv(fl).to_sql("Table_1", con, 
                                        if_exists = 'replace', index = False)
            for i in headers:
                statement = f"SELECT * FROM Table_1 WHERE {i} LIKE '{pat}';"
                cur.execute(statement)
                result = cur.fetchall() # get all matches from column i
                if len(result) == 0:
                    continue
                else:
                    temp_lst = []
                    for x in result:
                        temp_lst = x
                        for k in temp_lst:
                            if k in pat:
                                data_found[i] = k
            os.remove(db_name) # Remove tmp db file.
        return data_found

    def _get_matches(self) -> dict:
        
        parser_out = self._fl_parser(fl = self.fl, pat = self.pattern)
        found = {}
        if isinstance(parser_out, list):
            lst_str = ''.join(parser_out)
            a = re.findall(self.pattern, lst_str)
            if len(a) == 0:
                raise RegexError(f"pattern: {self.pattern}, doesn't exist!")
            for i in parser_out:
                if re.search(self.pattern, i):
                    key, value = i.split(':', 1)
                    key = key.strip()
                    value = value.strip()
                    found[key] = value
        else:
            return parser_out
        return found