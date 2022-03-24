from __future__ import annotations

import inspect
from scripts.search_tool import search_tools

class query_tool(search_tools):
    def __init__(self, fl: str, pattern: str) -> None:
        super().__init__(fl, pattern)

    def __repr__(self) -> str:
        params = inspect.getfullargspec(__class__).args
        params.remove("self")
        return f'{__class__.__name__}({params[0]} = "{self.fl}", {params[1]} = "{self.pattern}")'

    @staticmethod
    def _dict_parser(dictionary: dict) -> tuple[str, str]:
        keys = []
        values = []
        for key, value in dictionary.items():
            keys.append(key)
            values.append(value)

        keys = tuple(keys)
        keys = ", ".join(keys)
        values = tuple(values)
        values = ", ".join(values)
        return keys, values

    def query(self, show_idx = True) -> dict:
        matches = search_tools(fl = self.fl, pattern = self.pattern)._get_matches()
        keys, values = self._dict_parser(dictionary = matches)
        txt_ext = ('.txt', '.ini', '.fasta')
        if show_idx:
            print(f"There are {len(matches)} matches to the pattern {self.pattern}")
            if self.fl.endswith(txt_ext):
                if len(keys) > 1:
                    print(f"Pattern can be found on lines: {keys}.")
                else:
                    print(f"Pattern can be found on line {keys}.")
            elif self.fl.endswith('.csv'):
                if len(keys) > 1:
                    print(f"Pattern can be found on columns: {keys}.")
                else:
                    print(f"Pattern can be found on column {keys}.")

        out_dict = {}
        for key, value in zip(list(keys.split(",")), list(values.split(","))):
            if self.fl.endswith(txt_ext):
                key = f"Line {key}"
            elif self.fl.endswith(".csv"):
                key = f"column; {key}"
            out_dict[key] = value

        return out_dict
