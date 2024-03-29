#!/usr/bin/env python3
from __future__ import annotations

from lib.search_tool import search_tools
from lib.utils import dunders


class query_tool(search_tools, dunders):
    """Query tool class containing methods to run queries for regex patterns in files.

    Args:
        * `fl` (str): Input file.
        * `pattern` (str): Input pattern.
    """

    def __init__(self, fl: str, pattern: str) -> None:
        super().__init__(fl, pattern)

    @staticmethod
    def _dict_parser(dictionary: dict) -> tuple[str, str]:
        """Dictionary parser.

        Args:
            * `dictionary` (dict): Dictionary object.

        Returns:
            `tuple[str, str]`: keys and values of a dictionary as separate strings.
        """

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

    def query_wrapper(self, show_idx) -> dict:
        """Run an SQL or txt file query. This method is a wrapper to the methods holding the queries.

        Args:
            * `show_idx` (bool): Shows regex information in stdout.

        Returns:
            `dict`: Keys are equal to file locations and values are matched information.
        """

        matches = self._get_matches()
        keys, values = self._dict_parser(dictionary = matches)

        if show_idx:
            print(f"There are {len(matches)} matches to the pattern: {self.pattern}")
            if self.fl.endswith(self.txt_ext):
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
            out_dict[key] = value
        return out_dict
