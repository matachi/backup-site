import configparser
import json
import os
import urllib.parse
import urllib.request


class SqlExporter:
    """
    Contains methods to interact with the sqlexport.php API on the web server.

    @author Daniel "MaTachi" Jonsson
    @copyright Daniel "MaTachi" Jonsson
    @license MIT License
    """

    def __init__(self, api_key, url):
        """
        @type api_key: str
        @param api_key: The API key on the server to authenticate.
        @type url: str
        @param url: The URL to the API.
        """
        self.__api_key = api_key
        self.__url = url

    def __create_params(self, **params):
        """
        Create a URL params string.

        For example if `params` is {'a': 'b', 'c': 'd'} then the return value is
        "a=b&c=d".

        @type params: dict
        @param params: The parameters to be passed.
        @rtype: str
        """
        values = {
            'key': self.__api_key,
        }
        values.update(params)
        return urllib.parse.urlencode(values)

    def __create_url(self, **params):
        """
        Get an URL to the API containing the specified params.

        @type params: dict
        @param params: Parameters except for the key.
        @rtype: str
        @return: A complete URL to call.
        """
        params = self.__create_params(**params)
        return '{}?{}'.format(self.__url, params)

    @staticmethod
    def __decode_response(response):
        """
        Take a response from urlopen and returns a native Python object.
        """
        return json.loads(response.read().decode('utf-8'))

    def __query(self, **params):
        url = self.__create_url(**params)
        response = urllib.request.urlopen(url)
        return self.__decode_response(response)

    def get_table_names(self):
        """
        Get a list of the database's table names.
        """
        return self.__query(function='tables')

    def get_create_table_statements(self):
        """
        Get a list of statements to create the database's tables.
        """
        return self.__query(function='create_tables')

    def count_rows(self, table):
        """
        Return the number of rows that exists in the given table.

        @type table: str
        @param table: Name of the SQL table.
        """
        return self.__query(function='count_rows', table=table)

    def get_insert_into_statements(self, table, limit):
        """
        Return INSERT INTO statements to recreate the table's data.

        @type table: str
        @param table: Name of the SQL table.
        @type limit: str
        @param limit: An SQL LIMIT on which rows to return.
        """
        return self.__query(function='insert_into', table=table, limit=limit)

config = configparser.ConfigParser()
config.read(os.path.join(os.path.dirname(__file__), 'config.ini'))

if __name__ == '__main__':
    sqlexport_api_key = config['sqlexport']['api_key']
    sqlexport_url = config['sqlexport']['url']
    sql_exporter = SqlExporter(sqlexport_api_key, sqlexport_url)
    print(sql_exporter.get_insert_into_statements('wp_comments', '100,100'))
