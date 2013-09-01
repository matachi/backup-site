# Backup Site

Download a website's files over FTP and the SQL database's tables and rows.

License: [GNU GPL version 3 or later](LICENSE)

## Make a backup of a site's files

The site's complete file structure will with the instructions below be
downloaded to the directory backup.

1. Open [config.ini](config.ini) and add your FTP details.
2. `mkdir backup && cd backup`
3. `./../backuper.py`

## Make a backup of a WordPress installation, including both files and database, on a shared host

[WP Complete Backup](http://wordpress.org/plugins/wp-complete-backup/) will
make a database backup and save it in its plugin folder. Then will the complete
file structure be downloaded over FTP, including WP Complete Backup's backup of
the database. Not the prettiest solution, but it works fine if you are using a
shared host.

1. Install [WP Complete
   Backup](http://wordpress.org/plugins/wp-complete-backup/) on your WordPress
blog.
2. Open the settings for WP Complete Backup, add your IP address and copy the
   API key.
3. Open [config.ini](config.ini), add your FTP details, configure the WP
   Complete Backup settings and set `backup.wp_complete_backup` to `yes`.
4. `mkdir backup && cd backup`
5. `./../backuper.py`

