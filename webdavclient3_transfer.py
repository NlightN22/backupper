    
import os
from config_parser import Config
from logger import Logger
try:
    from webdav3.client import Client #pip install webdavclient3
except ModuleNotFoundError as e:
    Logger().error("webdav3.client not found please install it by command \'pip install webdavclient3\'")
    exit(1)

class WebdavTransfer():
    def __init__(self, config: Config) -> None:
        self.logger = Logger()
        options = {
            'webdav_hostname': config.cloud_hostname,
            'webdav_login':    config.cloud_login,
            'webdav_password': config.cloud_password
        }
        self.client = Client(options)
        self.error_status = False
        self.backup_cloud_path = config.backup_cloud_path

    def upload_to_remote(self, backup_file_pattern):
        """ Copy backup files to cloud
        Get backup file patter like: /tmp/backup/myservername_datetime.tar.gz
        """
        if self.error_status:
            return 1
        if self.client.check(self.backup_cloud_path):
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
        pass
    
    def __upload_files(self,backup_cloud_path, local_path):
        self.logger.log("Try to upload file: {}".format(local_path))
        try:
            self.client.upload_sync(remote_path=backup_cloud_path, local_path=local_path)
            return 0
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

