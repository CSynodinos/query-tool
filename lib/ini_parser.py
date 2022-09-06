#!/usr/bin/env python3
from __future__ import annotations
import configparser, inspect

class ini_handler:
    """.ini file handler.

    Contains 2 methods, one internal parser and a dictionary generator method.

    `.ini file organisation`:

    * [HEADER]
    * database = a_db_name
    * pguser = a_username
    * pgpswd = a_password
    * pghost = a_host_address
    * pgport = a_port
    """

    def __init__(self, ini: str) -> None:
        self.ini = ini

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
    def __ini_parser(ini: str) -> tuple[str, str, str, str, str]:
        """Extracts contents of .ini file into a tuple of strings.
        5 strings are returned for 5 fields.

        Args:
            * `ini` (_str_): .ini file path/name.

        Returns:
            tuple: Tuple of strings for every returned value from the .ini file.
        """

        config = configparser.ConfigParser()
        config.read(ini)
        sections = config.sections()
        database = config[sections[0]]['database']
        pguser = config[sections[0]]['pguser']
        pgpswd = config[sections[0]]['pgpswd']
        pghost = config[sections[0]]['pghost']
        pgport = config[sections[0]]['pgport']

        return database, pguser, pgpswd, pghost, pgport

    def _ini_to_dict(self) -> dict:
        """Returns contents of .ini file into a python dictionary.
        5 fields, database name, username, password, host and port.

        Returns:
            dict: The python dictionary.
        """

        database, pguser, pgpswd, pghost, pgport= self.__ini_parser(ini = self.ini)
        info_dict = {'database': database,
                    'pguser': pguser,
                    'pgpswd': pgpswd,
                    'pghost': pghost,
                    'pgport': pgport,
                    }

        return info_dict