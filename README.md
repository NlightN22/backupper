# Backupper v0.1

Create backups at linux systems. Autocopy to remote storages, autoclear old backups by dates.
- First create all local and remote folders. 
- Make sure that you have access to them from user that run script.
- Configure config.ini file.
- Copy all this files to local folder.
- Allow exec for main.py.
- Start main.py manually to check script work.
- Add main.py to /etc/crontab.

## Addition
You can set davfs cache to zero if don't have enough free space at /etc/davfs2/davfs2.conf.
Set:
cache_size 0
delay_upload 0
