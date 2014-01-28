#!/usr/bin/env python

import configparser
import os
from ftplib import FTP


class DunhamFtp(FTP):
    """
    Extend ftplib.FTP with some extra functionality.
    """

    def get_file_list(self):
        """
        Return a list of all files in the current working directory.
        """
        files = []
        self.retrlines('LIST', files.append)
        # Remove the files . and ..
        files = files[2:]
        # Make a list of dictionaries containing the file/directory name and a
        # boolean that says if it's a file or a directory.
        # .split(None, 8) is necessary so filenames containing spaces aren't
        # splitted.
        files = [
            {
                'name': x.split(None, 8)[-1],
                'dir': x[0] == 'd'
            }
            for x in files]
        return files

    def save_files_in_directory(self):
        """
        Save all files in the current working directory (cwd).

        This method is using FTP's state and Python's working directory to keep
        track of the current location when recursively traversing the trees.
        """
        files = self.get_file_list()
        for f in files:
            if f['dir']:
                self.cwd(f['name'])
                os.mkdir(f['name'])
                os.chdir(f['name'])
                self.save_files_in_directory()
                self.cwd('..')
                os.chdir('..')
            else:
                self.save_file(f['name'])

    def save_file(self, filename):
        """
        Save the given file from FTP's cwd to Python's cwd.
        """
        with open(filename, 'wb') as f:
            self.retrbinary('RETR ' + filename, f.write)

    def remove_dir(self, dirname=None):
        """
        Delete all files in the specified directory or in the cwd on the
        FTP, and the directory itself.

        @type dirname: str
        @param dirname: Name of the directory.
        """
        if dirname:
            files = [{'name': dirname, 'dir': True}]
        else:
            files = self.get_file_list()

        for f in files:
            if f['dir']:
                self.cwd(f['name'])
                self.remove_dir()
                self.cwd('..')
                self.rmd(f['name'])
            else:
                self.delete(f['name'])


def main():
    config = configparser.ConfigParser()
    config.read(os.path.join(os.path.dirname(__file__), 'config.ini'))

    if config['backup'].getboolean('ftp'):
        ftp = DunhamFtp(config['ftp']['host'], config['ftp']['username'],
                           config['ftp']['password'])
        # Save all files in the FTP's root directory
        os.mkdir('ftp')
        os.chdir('ftp')
        ftp.save_files_in_directory()
        ftp.quit()

if __name__ == '__main__':
    main()
