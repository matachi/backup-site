#!/usr/bin/env python3

from concurrent import futures
import configparser
import os
import shutil
import tarfile
from datetime import datetime, time
import itertools
from sqlexport import SqlExport


class SqlExporter:
    """
    Contains methods to interact with the sqlexport.php API on the web server.

    @author Daniel "MaTachi" Jonsson
    @copyright Daniel "MaTachi" Jonsson
    @license MIT License
    """

    BASE_DIR = os.path.dirname(__file__)

    def __init__(self, api_key, url):
        """
        @type api_key: str
        @param api_key: The API key on the server to authenticate.
        @type url: str
        @param url: The URL to the API.
        """
        self.__sql_export = SqlExport(api_key, url)

    def __sql_dir(self):
        """
        Get directory path to where the SQL files should be stored. If the
        directory doesn't exist it will get created.

        @rtype: str
        @return: Path to the SQL directory.
        """
        sql_dir = os.path.join(self.BASE_DIR, 'sql')
        if not os.path.exists(sql_dir):
            os.makedirs(sql_dir)
        return sql_dir

    def create_tables(self):
        """
        Create a file inside the SQL dir named tables.sql containing CREATE
        TABLE instructions for recreating the SQL tables.
        """
        create_tables = self.__sql_export.get_create_table_statements()
        tables_file = os.path.join(self.__sql_dir(), 'tables.sql')
        with open(tables_file, 'w') as file:
            file.write('\n\n'.join(create_tables))

    def __get_insert_statements(self, table):
        """
        Get a list of INSERT INTO statements to recreate the data in the given
        table.

        @type table: str
        @param table: The table to pull data from.
        @rtype: list
        @return: Statements each consisting of 1000 values.
        """
        number_of_rows = self.__sql_export.count_rows(table)
        # SQL LIMIT strings
        limits = ['{}, {}'.format(start, 1000) for start in
                  range(0, number_of_rows, 1000)]
        with futures.ThreadPoolExecutor(max_workers=3) as executor:
            return executor.map(self.__sql_export.get_insert_into_statement,
                                itertools.repeat(table), limits)

    def insert_into_tables(self):
        """
        Create files inside the SQL dir, one for each SQL table, containing
        INSERT INTO statements for recreating the tables' rows.
        """
        tables = self.__sql_export.get_table_names()
        with futures.ThreadPoolExecutor(max_workers=5) as executor:
            # Dictionary of the tables and their list of statements
            table_statements = dict(
                (executor.submit(self.__get_insert_statements, table), table)
                for table in tables
            )
            # Save the statements to disk after they have been downloaded to
            # memory
            for statements in futures.as_completed(table_statements):
                table = table_statements[statements]
                filename = os.path.join(self.__sql_dir(), '%s.sql' % table)
                with open(filename, 'w') as file:
                    file.write('\n\n'.join(statements.result()))

    def compress_backup(self):
        """
        Make a .tar.gz file of the SQL directory with the current date and time
        as filename.
        """
        datetime_string = datetime.now().strftime('%Y-%m-%d %H:%M')
        tar_filename = '{}.tar.gz'.format(datetime_string)
        with tarfile.open(tar_filename, 'w:gz') as tar:
            tar.add(os.path.join(self.__sql_dir()),
                    arcname=os.path.basename(self.__sql_dir()))

    def delete_sql_directory(self):
        """
        Delete the SQL directory.
        """
        shutil.rmtree(self.__sql_dir())

    def do_backup(self):
        """
        Do a complete backup of the SQL database and save the data as a
        compressed folder.
        """
        self.create_tables()
        self.insert_into_tables()
        self.compress_backup()
        self.delete_sql_directory()


config = configparser.ConfigParser()
config.read(os.path.join(os.path.dirname(__file__), 'config.ini'))

if __name__ == '__main__':
    sqlexport_api_key = config['sqlexport']['api_key']
    sqlexport_url = config['sqlexport']['url']
    sql_exporter = SqlExporter(sqlexport_api_key, sqlexport_url)
    sql_exporter.do_backup()