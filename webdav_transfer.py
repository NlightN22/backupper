import subprocess
import os.path

from config_parser import Config
from system_runner import Runner
from logger import Logger
# check path
runner = Runner()

class WebdavTransferer():
    def __init__(self, config: Config, logger_in: Logger = "") -> None:
        if logger_in == "":
            self.logger = Logger()
        else:
            self.logger = logger_in
        self.mount_uri = config.backup_cloud_uri
        self.mount_path = config.backup_cloud_path
        self.test_mode = config.test_mode
        self.max_tries_to_mount = 2
        self.error_status = False
        pass

    def copy_to_webdav(self, backup_file_pattern):
        """ Copy backup files to cloud
        Get backup file patter like: /tmp/backup/myservername_datetime.tar.gz
        """
        if self.error_status:
            return 1
        self.logger.log("Check path: {}".format(self.mount_path))
        count = 1
        while count <= self.max_tries_to_mount:
            if self.__is_path_exist(self.mount_path):
                self.logger.log("Path {} is exist.".format(self.mount_path))
                break
            self.logger.error("Path {} does not exist. Try to mount: {}/{}".format(self.mount_path, count, self.max_tries_to_mount))
            self.__mount_webdav()
            count += 1

        if self.__is_path_exist(self.mount_path):
            return self.__copy_files_to_mount_path(self.mount_path, backup_file_pattern)
        else:
            self.error_status = True
            self.logger.error("Can't copy, \"{}\" does not exist.".format(self.mount_path))
            return 1
        
    def __copy_files_to_mount_path(self,mount_path, backup_file_pattern):
        command_to_copy = "cp {}* {}".format(backup_file_pattern, mount_path)
        if self.test_mode:
            self.logger.log("Run {}".format(command_to_copy))
            return 0
        return runner.run(command_to_copy)

    def __is_path_exist(self,mount_path: str):
        return os.path.exists(mount_path)

    def __mount_webdav(self):
        # command to mount: mount -t davfs https://cloud.yousite.ru/remote.php/dav/files/username /mnt/cloud/
        command_to_mount = "mount -t davfs {} {}".format(self.mount_uri, self.mount_path)
        try:
            subprocess.check_output(command_to_mount, stderr=subprocess.STDOUT, text=True, timeout=5, shell=True)
            self.logger.log("Mount {}".format(self.mount_path))
            return 0
        except subprocess.CalledProcessError or subprocess.TimeoutExpired:
            self.logger.error("Can't mount webdav {} to {}. Command or permissions not correct.".format(self.mount_uri, self.mount_path))
            return 1

        # TODO delete
        # result = runner.run(command_to_mount)
        # if result != 0:
        #     logger.error("Result of mount: {}".format(result))
        # return result