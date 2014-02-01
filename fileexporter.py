#!/usr/bin/env python3
"""
@author Daniel "MaTachi" Jonsson
@copyright Daniel "MaTachi" Jonsson
@license MIT License
"""
from concurrent import futures
import configparser
from optparse import OptionParser
import os
from dunhamftp import DunhamFtp


class MyOptionParser(OptionParser):
    def format_epilog(self, formatter):
        return self.epilog


def main():
    """
    Parse launch options, read settings from the config file and initialize the
    file exporting.
    """
    usage = 'usage: %prog [options] [arg1 arg2]'
    description = 'Export files from a FTP, configured in `config.ini` to a ' \
                  'local directory `ftp`.'
    epilog = '''
Example commands:
    $ ./fileexporter.py
    $ ./fileexporter.py /
    $ ./fileexporter.py /var/lib/dpkg
    $ ./fileexporter.py -r /var/lib/dpkg
    $ ./fileexporter.py -r /var/lib dpkg/alternatives pam
'''
    parser = MyOptionParser(usage=usage, description=description, epilog=epilog)
    parser.add_option('-r', '--root', dest='root', default='/', metavar='PATH',
                      help='root directory on the FTP to backup from')
    options, args = parser.parse_args()

    config = configparser.ConfigParser()
    config.read(os.path.join(os.path.dirname(__file__), 'config.ini'))

    file_exporter = FileExporter(options.root, args, config['ftp']['host'],
                                 config['ftp']['username'],
                                 config['ftp']['password'])
    file_exporter.download_files()


class FileExporter():

    def __init__(self, root, directories, host, username, password):
        """
        @param root: Root directory on the FTP.
        @param directories: Which directories to download files from, relative
                            to the root.
        @param host: Host address to the FTP.
        @param username: FTP username.
        @param password: FTP password.
        """
        self.__root = root
        self.__directories = directories
        self.__host = host
        self.__username = username
        self.__password = password

    def __get_file_list(self):
        """
        Get a list of the files on the FTP that are in the directories specified
        in the constructor.

        @rtype: list
        @return: List of unique files.
        """
        files = []
        with DunhamFtp(self.__host, self.__username, self.__password) as ftp:
            ftp.encoding = 'utf8'
            # If no directories are specified, download everything from -r
            # instead
            if len(self.__directories) == 0:
                self.__directories.append('')

            for directory in self.__directories:
                if len(directory) > 0 and directory[0] == '/':
                    directory = directory[1:]
                from_dir = os.path.join(self.__root, directory)
                files = files + ftp.get_files_in_directory(from_dir)
        return list(set(files))

    @staticmethod
    def __filter_out_existing_files(files_to_save):
        """
        Remove files from `files` that already exists on the hard drive.

        @type files_to_save: list
        @param files_to_save: A list of tuples where the the first element is
                              an absolute path to a file on the FTP, and the
                              second element is a local absolute path to save
                              the file as.
        """
        files_not_downloaded = []
        for file in files_to_save:
            if not os.path.exists(file[1]):
                files_not_downloaded.append(file)
        return files_not_downloaded

    def download_files(self):
        """
        Start download of the files in the directories specified in the class'
        constructor.
        """
        # Where to save the files
        to_dir = os.path.join(os.path.dirname(__file__), 'ftp')

        # List of files on the FTP
        file_list = self.__get_file_list()
        # What the files should be saved as locally
        save_as = [os.path.join(to_dir, f[1:]) for f in file_list]
        # List of tuples of a FTP file and what is should be saved as
        files_to_save = list(zip(file_list, save_as))
        files_to_save = self.__filter_out_existing_files(files_to_save)
        # Split the list into 10 about equally large sizes
        groups = self.split_list(files_to_save, 10)
        # Download each group in a separate thread
        with futures.ThreadPoolExecutor(max_workers=10) as executor:
            return executor.map(self.save_files, groups)

    def save_files(self, files_to_save):
        """
        Save a group of files.

        @type files_to_save: list
        @param files_to_save: A list of tuples where the the first element is
                              an absolute path to a file on the FTP, and the
                              second element is a local absolute path to save
                              the file as.
        """
        with DunhamFtp(self.__host, self.__username, self.__password) as ftp:
            ftp.encoding = 'utf8'
            for file, save_as in files_to_save:
                ftp.save_file(file, save_as)

    @staticmethod
    def split_list(array, indices):
        """
        For example:

            >>> FileExporter.split_list(list(range(10)), 3)
            [[0, 3, 6, 9], [1, 4, 7], [2, 5, 8]]

        @type array: list
        @param array: A list to split.
        @type indices: int
        @param indices: How many groups it should be splitted into.
        @return: A list of `indices` number of lists.
        """
        return [array[i::indices] for i in range(indices)]

if __name__ == '__main__':
    main()