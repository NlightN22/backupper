from datetime import datetime

from system_runner import Runner
from logger import Logger
from config_parser import Config

# printf 'n file-%02d.tar\n' {2..100} | tar --tape-length=500M -cf /mnt/cloud/file-01.tar \
# --exclude=*bitrix-backup.tar.gz --exclude=/media --exclude=/dev --exclude=/mnt --exclude=/proc --exclude=/sys --exclude=/tmp --exclude=swapfile \
# --exclude=/var/cache --exclude=/home/bitrix/www/bitrix/backup --exclude=*.sql --exclude=*.zip --exclude=*.tar.gz \
# /

config = Config()
runner = Runner()
def backup_files(logger_in: Logger = ""):
    """ Create backup of files
    Return result of backup command in Int
    and pattern of backup filenames
    """
    if logger_in == "":
        logger = Logger()
    else:
        logger = logger_in
    archive_name = config.archive_name
    archive_size = config.archive_size
    backup_local_path = config.backup_local_path
    archive_path = config.archive_path
    exclude_expr = config.exclude_expr
    test_mode = config.test_mode
        
    combine_exclude = map(lambda x: " --exclude=" + x + " ", exclude_expr )
    command_exclude: str = ' '.join(combine_exclude)

    archive_name: str = backup_local_path + archive_name + get_current_date_time()
    if archive_size and not archive_size.isspace():

        command_slice = "printf 'n {}%02d.tar\\n' {2..100} | tar --tape-length={} -cf {}.tar".format(archive_name, archive_size, archive_name)
        command = command_slice + command_exclude + archive_path
    else:
        command_no_slice = "tar -czf {}.tar".format(archive_name)
        command = command_no_slice + command_exclude + archive_path
    if test_mode:
        logger.log("backup_files Run: {}".format(command))
        return archive_name, 0 
    else:
        result = runner.run(command, exclude_errors=["Removing leading"])
        return archive_name, result

def get_current_date_time():
    now = datetime.now()
    dt_string = now.strftime("_%d_%m_%Y_%H_%M_%S")
    return dt_string