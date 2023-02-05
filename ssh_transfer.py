import os
from config_parser import Config
from logger import Logger
from system_runner import Runner

class SshTransfer():
    def __init__(self, config: Config) -> None:
        self.logger = Logger()
        self.ssh_username = config.ssh_username
        self.ssh_hostname = config.ssh_hostname
        self.backup_cloud_path = config.backup_cloud_path
        self.runner = Runner()
        self.error_status = False

    def upload_to_remote(self, backup_file_pattern):
        """ Copy backup files to cloud
        Get backup file pattern like: /tmp/backup/myservername_datetime.tar.gz
        Return error status Int
        """
        if self.error_status:
            return 1
        if self.__check_connection_and_path(self.backup_cloud_path):
            total_result = 0
            folder_string, file_pattern_string = self.__get_local_folder_and_file_pattern(backup_file_pattern)
            files = self.__get_files_in_directory(folder_string, file_pattern_string)
            for file in files:
                result = self.__upload_files(self.backup_cloud_path, file)
                if result == 1:
                    total_result = 1
            return total_result
        else:
            self.logger.error("Can't copy, \"{}\" does not exist.".format(self.backup_cloud_path))
        self.error_status = True
        return 1

    def delete_from_remote(self, path: str, seconds: int):
        """
        Get path to check, get days in seconds
        Return result in Int. 0 - ok, other - not ok
        """
        minutes = seconds / 60 # convert to minutes
        command_to_delete = "ssh {}@{} 'find {} -maxdepth 1 -mmin +{} -delete'".format(self.ssh_username, self.ssh_hostname, path, minutes)
        result = self.runner.run(command_to_delete)
        return result

    def __check_connection_and_path(self, remote_path):
        command_to_check = "ssh {}@{} '[ -d {} ]'".format(self.ssh_username, self.ssh_hostname, remote_path)
        result = self.runner.run(command_to_check)
        if result == 0:
            return True
        return False
    
    def __upload_files(self,backup_cloud_path, local_path):
        self.logger.log("Try to upload file: {}".format(local_path))
        try:
            command_to_upload = "rsync -avz ssh {} {}@{}:{}".format(local_path, self.ssh_username, self.ssh_hostname, backup_cloud_path)
            result = self.runner.run(command_to_upload)
            return result
        except Exception as e:
            self.logger.error(str(e))
            return 1

    def __get_local_folder_and_file_pattern(self, in_string):
        try:
            last_index = in_string.rfind("/") + 1
            folder_string = in_string[: last_index]
            file_pattern_string = in_string[last_index :-1]
            return folder_string, file_pattern_string
        except ValueError as e:
            self.logger.error("Can't find \"/\" at backup_file_pattern")
            raise e

    def __get_files_in_directory(self, folder_string, file_pattern_string):
        files = [ i for i in (os.path.join(folder_string, filename) 
                for filename in os.listdir(folder_string)) 
                if os.path.isfile(i) and i.__contains__(file_pattern_string)]
        return files
