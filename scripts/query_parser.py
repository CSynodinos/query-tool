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

    def query(self, show_idx = True, get_matches = False) -> (tuple[str, str] | str):
        matches = search_tools(fl = self.fl, pattern = self.pattern)._get_matches()
        print(f"There are {len(matches)} matches to the pattern {self.pattern}")
        if show_idx:
            keys = self._dict_parser(dictionary = matches)[0]
            if self.fl.endswith('.txt'):
                if len(keys) > 1:
                    print(f"Pattern can be found in lines: {keys}.")
                else:
                    print(f"Pattern can be found in line {keys}.")
            elif self.fl.endswith('.csv'):
                if len(keys) > 1:
                    print(f"Pattern can be found in columns: {keys}.")
                else:
                    print(f"Pattern can be found in column {keys}.")
        if get_matches:
            return self._dict_parser(dictionary = matches)[0], self._dict_parser(dictionary = matches)[1]
        else:
            return self._dict_parser(dictionary = matches)[0]
