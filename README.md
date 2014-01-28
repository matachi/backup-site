# Backup Site

Download a website's files over FTP and the SQL database's tables and rows.

License: [MIT License](LICENSE)

## Make a backup of a site's files over FTP

The site's complete file structure will with the instructions below be
downloaded to the directory backup.

1. Open [config.ini](config.ini) and add your FTP details.
2. `mkdir backup && cd backup`
3. `./../backuper.py`

## Make a backup of a site's SQL database on a shared host with PHP support

### Create an API key

First, generate an API key, for example with the following terminal command:

   $ cat /dev/urandom | tr -dc A-Za-z0-9 | head -c 50; echo

Paste the key into <config.ini> under `[sqlexport]` at the setting `api_key`.

Then, calculate the sha256 hash sum of the key, for example with:

   $ echo -n APIKEY | sha256sum

Paste the hashed key into <sqlexport.php>.where `$sha256_api_key` is set.

### Upload the API to the host

Upload `sqlexport.php` to the host, for example with FileZilla. If you have
WordPress installed on the server, by putting the file in WordPress's root
directory you won't have to configure any database settings since the file will
try to use the database settings from `wp-config.php` if present. Otherwise you
will also need to specify your database settings in `sqlexport.php`.

### Make a backup

    $ ./dunhamftp.py

Running this script will do the following things:

1. Make a directory named sql.
2. Create necessary files inside the directory for creating the tables and
   inserting the rows into the tables.
3. Create a .tar.gz file of the sql directory with current date and time as
   name filename.
4. Remove the directory sql.
