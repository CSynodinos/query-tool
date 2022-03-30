import os
import configparser
import psycopg2
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT


class ini_handler:
    """_summary_

    Returns:
        _type_: _description_
    """

    def __init__(self, ini):
        self.ini = ini

    @staticmethod
    def __ini_parser(ini):
        config = configparser.ConfigParser()
        config.read(ini)
        sections = config.sections()
        database = config[sections[0]]['database']
        pguser = config[sections[0]]['pguser']
        pgpswd = config[sections[0]]['pgpswd']
        pghost = config[sections[0]]['pghost']
        pgport = config[sections[0]]['pgport']

        return database, pguser, pgpswd, pghost, pgport

    def _ini_to_dict(self):
        database, pguser, pgpswd, pghost, pgport= self.__ini_parser(ini = self.ini)

        info_dict = {'database': database,
                    'pguser': pguser,
                    'pgpswd': pgpswd,
                    'pghost': pghost,
                    'pgport': pgport,
                    }

        return info_dict