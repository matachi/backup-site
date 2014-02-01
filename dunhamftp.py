#!/usr/bin/env python3
import os
from ftplib import FTP


class DunhamFtp(FTP):
    """
    Extend ftplib.FTP with some extra functionality.

    @author Daniel "MaTachi" Jonsson
    @copyright Daniel "MaTachi" Jonsson
    @license MIT License
    """

    def get_file_list(self, directory):
        """
        Return a list of all files in `directory` or the current working
        directory (cwd).

        @type directory: str
        @param directory: Path to a directory to list files from.
        @rtype: list
        @return: A list of dictionaries with the keys `path` to the str
                 file/directory path and `dir` to the boolean if it's a
                 directory.
        """
        files = []
        if directory:
            cmd = 'LIST {}'.format(directory)
        else:
            cmd = 'LIST'
        self.retrlines(cmd, files.append)

        # Remove the files . and ..
        files = files[2:]
        # Make a list of dictionaries containing the file/directory name and a
        # boolean that says if it's a file or a directory.
        # .split(None, 8) is necessary so filenames containing spaces aren't
        # splitted.
        files = [
            {
                'path': os.path.join(directory, f.split(None, 8)[-1]),
                'dir': f[0] == 'd'
            }
            for f in files]
        return files

    def get_files_in_directory(self, from_dir):
        """
        Get a list of all files in `from_dir` and its subdirectories.

        @type from_dir: str
        @param from_dir: Directory on the FTP to get files from.
        @return
        """
        files = self.get_file_list(from_dir)
        file_list = []
        for f in files:
            if f['dir']:
                file_list = file_list + self.get_files_in_directory(f['path'])
            else:
                file_list.append(f['path'])
        return file_list

    def save_file(self, path, save_as):
        """
        Save the file `path` from the FTP as `save_as` locally.

        @type path: str
        @param path: File path to a file on the FTP.
        @type save_as: str
        @param save_as: Local file path to save the file as.
        """
        save_as_dir = os.path.dirname(save_as)
        if not os.path.exists(save_as_dir):
            os.makedirs(save_as_dir)

        print(save_as)
        with open(save_as, 'wb') as f:
            self.retrbinary('RETR ' + path, f.write)

    def remove_dir(self, dirname=None):
        """
        Delete all files in the specified directory or in the cwd on the
        FTP, and the directory itself.

        @type dirname: str
        @param dirname: Name of the directory.
        """
        if dirname:
            files = [{'path': dirname, 'dir': True}]
        else:
            files = self.get_file_list()

        for f in files:
            if f['dir']:
                self.cwd(f['path'])
                self.remove_dir()
                self.cwd('..')
                self.rmd(f['path'])
            else:
                self.delete(f['path'])
