#!/usr/bin/python
import os.path
from config_parser import Config
from logger import Logger
from emailer import Emailer
import backupper_files
from webdav_transfer import WebdavTransferer
from backupper_mysql_db import MySQLBackupper
from deleter import Deleter

config = Config()
logger = Logger()
deleter = Deleter()
webdav = WebdavTransferer(config)
backup_files = config.backup_files
backup_local_path = config.backup_local_path
backup_mysql = config.backup_mysql
send_email = config.send_email
backup_file_status = 0
backup_db_status = 0

def is_path_exist(path: str):
    return os.path.exists(path)

def copy_to_cloud(filename: str):
    if config.backup_to_cloud:
        logger.log("Try to copy backup files \"{}*\" to \"{}\"".format(filename, config.backup_cloud_path))
        try:
            result_copy = webdav.copy_to_webdav(filename)
            if result_copy != 0:
                logger.error("Error copy to cloud {}".format(result_copy))
            return False
        except Exception as e:
            logger.error(str(e))
            return False
    return True

def control_local_backup_path():
    if not is_path_exist(backup_local_path):
        logger.error("Local backup path {} does not exist".format(backup_local_path))
        exit(1)

if __name__ == "__main__":
    if backup_files:
        logger.log("Try to backup files at \"{}\"".format(config.archive_path))
        control_local_backup_path()
        archive_name, result = backupper_files.backup_files()
        if result != 0:
            backup_file_status = 1
            logger.error("Backup error {}".format(result))
        else:
            copy_to_cloud(archive_name)

    if backup_mysql:
        backupper_mysql_db = MySQLBackupper()
        if config.all_databases:
            logger.log("Try to backup all databases")
        else:
            logger.log("Try to backup databases {}".format(config.special_databases))
        control_local_backup_path()
        result_dict = backupper_mysql_db.backup_mysql()
        if result_dict != {}:
            for filename, result_db in result_dict.items():
                if result_db != 0:
                    backup_db_status = 1
                    logger.error("Backup error {} {}".format(filename, result_db))
                else:
                    copy_to_cloud(filename)

    if config.autoclean_local:
        logger.log("Try to delete old local files")
        try:
            deleter.delete_backup(config.backup_local_path, config.local_time)
        except Exception as e:
            logger.error(str(e))
    
    if config.backup_to_cloud and config.autoclean_remote:
        logger.log("Try to delete old remote files")
        if webdav.error_status == False:
            try:
                deleter.delete_backup(config.backup_cloud_path, config.remote_time)
            except Exception as e:
                logger.error(str(e))
        else:
            logger.log("Can't delete remote files - WebdavTransferer in error state")

    if send_email:
        logger.log("Try to send report to e-mail")
        try:
            emailer = Emailer()
            emailer.send_log_to_email()
        except Exception as e:
            logger.error(str(e))
            
    if backup_file_status != 0: exit(backup_file_status)
    if backup_db_status != 0: exit(backup_db_status)
    exit(0)