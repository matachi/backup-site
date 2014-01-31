#!/usr/bin/env python3
"""
@author Daniel "MaTachi" Jonsson
@copyright Daniel "MaTachi" Jonsson
@license MIT License
"""
import configparser
from optparse import OptionParser
import os
from dunhamftp import DunhamFtp


class MyOptionParser(OptionParser):
    def format_epilog(self, formatter):
        return self.epilog


def main():
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

    with DunhamFtp(config['ftp']['host'], config['ftp']['username'],
                   config['ftp']['password']) as ftp:

        base_dir = os.path.join(os.path.dirname(__file__), 'ftp')

        # If no args are specified, download everything from -r instead
        if len(args) == 0:
            args.append('')

        for arg in args:
            if len(arg) > 0 and arg[0] == '/':
                arg = arg[1:]
            from_dir = os.path.join(options.root, arg)
            to_dir = os.path.join(base_dir, arg)
            ftp.save_files_in_directory(from_dir, to_dir)

if __name__ == '__main__':
    main()