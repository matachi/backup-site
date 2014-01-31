# Backup Site

Download a website's files over FTP and the SQL database's tables and rows.

License: [MIT License](LICENSE)

## Make a backup of a site's files over FTP

The site's complete file structure will with the instructions below be
downloaded to the directory backup.

1. Open [config.ini](config.ini) and add your FTP details.
2. `$ ./fileexporter.py

Run `$ ./fileexporter.py --help` to see examples and instructions on how to use
the script.

[Click here](#test-ftp-backup-functionality-locally) to scroll down to the
section where a guide on how
to set up, run and test `fileexporter.py` locally.

## Make a backup of a site's SQL database on a shared host with PHP support

### Create an API key

First, generate an API key, for example with the following terminal command:

    $ cat /dev/urandom | tr -dc A-Za-z0-9 | head -c 50; echo

Paste the key into [config.ini](config.ini) under `[sqlexport]` at the setting
`api_key`.

Then, calculate the sha256 hash sum of the key, for example with:

    $ echo -n APIKEY | sha256sum

Paste the hashed key into [sqlexport.php](sqlexport.php) where
`$sha256_api_key` is set.

### Upload the API to the host

Upload [sqlexport.php](sqlexport.php) to the host, for example with FileZilla.
If you have WordPress installed on the server, by putting the file in
WordPress's root directory you won't have to configure any database settings
since the file will try to use the database settings from `wp-config.php` if
present. Otherwise you will also need to specify your database settings in
[sqlexport.php](sqlexport.php).

### Make a backup

    $ ./sqlexporter.py

Running this script will do the following things:

1. Make a directory named sql.
2. Create necessary files inside the directory for creating the tables and
   inserting the rows into the tables.
3. Create a .tar.gz file of the sql directory with the current date and time as
   filename.
4. Remove the directory sql.

## Test FTP backup functionality locally

Build Docker image:

    $ sudo docker build -t backup-site/ftp .

Start a new container:

    $ sudo docker run -i -t -p 127.0.0.1:21:21 backup-site/ftp

To connect to the FTP, run `$ ftp localhost` and login with the username `root`
and password `pass`.

To test the [fileexporter.py](fileexporter.py) script, run:

    $ ./fileexporter.py -r /var/lib dpkg/alternatives pam

This will download the files from within the directories
`/var/lib/dpkg/alternatives/pam` and `/var/lib/pam` to a directory called
`ftp`.

If you are interested in only one directory:

    $ ./fileexporter.py /var/lib/dpkg

or:

    $ ./fileexporter.py -r /var/lib/dpkg

These two wi
