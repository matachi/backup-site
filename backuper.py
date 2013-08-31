#!/usr/bin/env python

import os
from ftplib import FTP

class AryaStarkFtp(FTP):
    """Extend ftplib.FTP with some extra functionality."""

    def __init__(self):
        super().__init__('FTP.EXAMPLE.COM', 'USERNAME', 'PASSWORD')

    def get_file_list(self):
        """Return a list of all files in the current folder."""
        listing = []
        self.retrlines('LIST', listing.append)
        # Remove the files . and ..
        listing = listing[2:]
        # Make a list of dictionaries containing the file/folder name and a
        # string that says if it's a file or a folder.
        # .split(None, 8) is necessary so filenames containing spaces aren't
        # splitted.
        listing = [{
                       'name': x.split(None, 8)[-1],
                       'dict': x[0] == 'd'
                   }
                   for x in listing]
        return listing

    def save_files_in_folder(self):
        """Save all files in the current folder.

        This method is using FTP's state and Python's working directory to keep
        track of the current location when recursively traversing the trees."""
        files = self.get_file_list()
        for f in files:
            if f['dict']:
                self.cwd(f['name'])
                os.mkdir(f['name'])
                os.chdir(f['name'])
                self.save_files_in_folder()
                self.cwd('..')
                os.chdir('..')
            else:
                self.save_file(f['name'])

    def save_file(self, filename):
        """Save the given file from FTP's cwd to Python's cwd."""
        with open(filename, 'wb') as f:
            self.retrbinary('RETR ' + filename, f.write)

ftp = AryaStarkFtp()
ftp.save_files_in_folder()
ftp.quit()
