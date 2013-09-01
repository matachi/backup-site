#!/usr/bin/env python

import configparser
import os
import urllib.request
from ftplib import FTP

class AryaStarkFtp(FTP):
    """Extend ftplib.FTP with some extra functionality."""

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
                pass

    def save_file(self, filename):
        """Save the given file from FTP's cwd to Python's cwd."""
        with open(filename, 'wb') as f:
            self.retrbinary('RETR ' + filename, f.write)

    def delete_folder(self, foldername=None):
        """Delete all files in the specified folder or in the cwd on the
        FTP."""
        files = None

        if foldername:
            files = [{'name': foldername, 'dict': True}]
        else:
            files = self.get_file_list()

        for f in files:
            if f['dict']:
                self.cwd(f['name'])
                self.delete_folder()
                self.cwd('..')
                self.rmd(f['name'])
            else:
                self.delete(f['name'])
                pass

    def delete_wp_complete_backups(self):
        """Delete all backups made by WP Complete Backup."""
        self.cwd('/wp-content/plugins/wp-complete-backup/storage')
        files = self.get_file_list()
        for f in files:
            if f['dict']:
                self.delete_folder(f['name'])

    def make_wp_complete_backup(self, url):
        """Query the remote execution URL, which will make a database
        backup."""
        urllib.request.urlopen(url)

config = configparser.ConfigParser()
config.read('config.ini')

if config['backup'].getboolean('wp_complete_backup'):
    ftp = AryaStarkFtp(config['ftp']['host'], config['ftp']['username'],
                       config['ftp']['password'])
    if config['wp_complete_backup'].getboolean('delete_previous_backups'):
        ftp.delete_wp_complete_backups()
    ftp.make_wp_complete_backup(config['wp_complete_backup']['url'])
    ftp.quit()

if config['backup'].getboolean('ftp'):
    ftp = AryaStarkFtp(config['ftp']['host'], config['ftp']['username'],
                       config['ftp']['password'])
    ftp.save_files_in_folder()
    ftp.quit()
