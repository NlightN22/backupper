import subprocess
import os.path
import time

from config_parser import Config
from system_runner import Runner
from logger import Logger
runner = Runner()

class Davfs2Transfer():
    def __init__(self, config: Config, logger_in: Logger = "") -> None:
        if logger_in == "":
            self.logger = Logger()
        else:
            self.logger = logger_in

        if config.backup_to_cloud:
            self.mount_uri = config.backup_cloud_uri
            self.mount_path = config.backup_mount_path
            self.cloud_path = config.backup_cloud_path
        self.test_mode = config.test_mode
        self.max_tries_to_mount = 2
        self.error_status = False
        pass

    def upload_to_remote(self, backup_file_pattern):
        """ Copy backup files to cloud
        Get backup file patter like: /tmp/backup/myservername_datetime.tar.gz
        """
        if self.error_status:
            return 1
        #self.logger.log("Check path: {}".format(self.mount_path))
        if self.__is_path_exist(self.mount_path):
            count = 1
            while count <= self.max_tries_to_mount:
                if self.__is_mounted():
                    # self.logger.log("Mount URI {} is exist.".format(self.mount_uri))
                    break
                self.logger.error("Mount URI {} does not exist. Try to mount: {}/{}".format(self.mount_uri, count, self.max_tries_to_mount))
                self.__mount_webdav()
                count += 1
            if self.__is_mounted():
                if self.__is_path_exist(self.cloud_path):
                    self.error_status = False
                    return self.__copy_files_to_mount_path(self.cloud_path, backup_file_pattern)
                else:
                    self.logger.error("Can't copy, \"{}\" does not exist.".format(self.cloud_path))
            else:
                self.logger.error("Can't copy, \"{}\" does not exist.".format(self.mount_uri))
        else:
            self.logger.error("Can't copy, \"{}\" does not exist.".format(self.mount_path))
        self.error_status = True
        return 1

    def delete_from_remote(self, path: str, seconds: int):
        """
        Get path to check, get days in seconds
        Return result in Int. 0 - ok, other - not ok
        """
        return self.__delete_files_by_date(seconds, path)
       
    def __copy_files_to_mount_path(self,mount_path, backup_file_pattern):
        command_to_copy = "cp {}* {}".format(backup_file_pattern, mount_path)
        if self.test_mode:
            self.logger.log("Run {}".format(command_to_copy))
            return 0
        return runner.run(command_to_copy)

    def __is_mounted(self, mount_uri_in: str = ""):
        if mount_uri_in == "":
            mount_uri = self.mount_uri
        else:
            mount_uri = mount_uri_in
        check_command = "mount -l | grep {}".format(mount_uri)
        result = subprocess.run(check_command, shell=True)
        if result.returncode != 0: return False 
        else: return True

    def __mount_webdav(self):
        # command to mount: mount -t davfs https://cloud.yousite.ru/remote.php/dav/files/username /mnt/cloud/
        command_to_mount = "mount -t davfs {} {}".format(self.mount_uri, self.mount_path)
        timeout = 5
        try:
            subprocess.check_output(command_to_mount, stderr=subprocess.STDOUT, universal_newlines=True, timeout=timeout, shell=True)
            self.logger.log("Mount {}".format(self.mount_path))
            return 0
        except subprocess.TimeoutExpired as e:
            if e.stderr != None: self.logger.error(">>> {}".format(e.stderr))
            if e.stdout != None: self.logger.error(">>> {}".format(e.stdout))
            self.logger.error("Can't mount webdav {} to {}. Timeout: {}s.".format(self.mount_uri, self.mount_path, timeout))
            self.logger.log("Maybe you need to add you credentials at \"/etc/davfs2/secrets\"")
            self.logger.log("Try to mount manually without input your credential by command:\n{}".format(command_to_mount))
        except subprocess.CalledProcessError as e:
            if e.stderr != None: self.logger.error(">>> {}".format(e.stderr))
            if e.stdout != None: self.logger.error(">>> {}".format(e.stdout))
            self.logger.error("Can't mount webdav {} to {}. Command or permissions not correct.".format(self.mount_uri, self.mount_path))
            return 1

    def __delete_files_by_date(self, storage_time: int, path: str):
        if self.__is_path_exist(path):
            files = [ i for i in (os.path.join(path, filename) for filename in os.listdir(path)) if os.path.isfile(i)]
            now = time.time()
            if self.config.test_mode:
                self.logger.log("Files {} at {}".format(files, path))
            if files == []:
                self.logger.log("Folder {} is empty".format(path))
                return 0
            for file in files:
                file_time = os.stat(file).st_mtime
                diff = int(now) - int(file_time)
                if self.config.test_mode:
                    self.logger.log("Now: {} File time:{}".format(now, file_time, storage_time, file))
                    self.logger.log("diff: {} > storage_time:{}".format(diff, storage_time))
                if diff > storage_time:
                    if self.config.test_mode:
                        self.logger.log("Run remove file {}".format(file))
                    else:
                        os.remove(file)
                        self.logger.log("Remove file {}".format(file))
            return 0
        else:
            self.logger.error("Path {} does not exist. Can not delete files".format(path))
            return 1
    
    def __is_path_exist(self, path: str):
        return os.path.exists(path)