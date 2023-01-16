import os
import time
from logger import Logger
from config_parser import Config

class Deleter:
    def __init__(self) -> None:
        self.logger = Logger()
        self.config = Config()

    def delete_backup(self, path: str, days: int):
        return self.__delete_files_by_date(days, path)
    
    def __delete_files_by_date(self, storage_time: int, path: str):
        if self.__is_path_exist(path):
            files = [os.path.join(path, filename) for filename in os.listdir(path)]
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
