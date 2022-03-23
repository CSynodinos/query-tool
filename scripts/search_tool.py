from __future__ import annotations

import re, csv, sqlite3
import pandas as pd
import os

class RegexError(Exception):
    """Custom exception class for non-existant patterns."""

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
    def __init__(self, fl: str, pattern: str) -> None:
        self.fl = fl
        self.pattern = pattern

    def _fl_parser(self) -> (list | dict):
        
        assert self.fl
        txt_ext = ('.txt', '.ini', '.fasta')
        if self.fl.endswith(txt_ext):
            data_found = []
            with open(self.fl, "r") as txt:
                lines = txt.readlines()
                txt.seek(0)
                for index, line in enumerate(lines):
                    ln_index = str(index)+': '+line
                    ln_index = ln_index.replace('\n', '')
                    data_found.append(ln_index)

        elif self.fl.endswith('.csv'):
            data_found = {}
            with open(self.fl, "r", encoding = 'utf-8-sig') as csv_file:
                csv_reader = csv.reader(csv_file, delimiter = ',')
                headers = []
            
                # loop through csv and get the first row (headers)
                for row in csv_reader:
                    headers.append(row)
                    break
                headers = [item for elem in headers for item in elem]

                db_name = f"{self.fl.rsplit('.', 1)[0]}.db"
                if not len(os.path.split(db_name)[0]) == 0:
                    db_name = os.path.split(db_name)[1]

            con = sqlite3.connect(db_name) # change to 'sqlite:///your_filename.db'
            cur = con.cursor()
            pd.read_csv(self.fl).to_sql("Table_1", con, 
                                        if_exists = 'replace', index = False)
            for i in headers:
                statement = f"SELECT * FROM Table_1 WHERE {i} LIKE '{self.pattern}';"
                cur.execute(statement)
                result = cur.fetchall() # get all matches from column i
                if len(result) == 0:
                    continue
                else:
                    temp_lst = []
                    for x in result:
                        temp_lst = x
                        for k in temp_lst:
                            if k in self.pattern:
                                data_found[i] = k
        return data_found

    def _get_matches(self) -> dict:
        
        parser_out = self._fl_parser()
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
            found = parser_out
        return found