import configparser
import os
import re
from logger import Logger

logger = Logger()
class Config:
    current = configparser.ConfigParser()

    send_email: bool
    delete_log: bool
    send_log: bool
    email_to: str
    email_from: str
    email_subject: str
    email_body: str
    email_server: str
    email_pass: str

    backup_local_path: str

    backup_files: bool
    archive_name: str
    exclude_expr: list = []
    archive_path: str
    archive_size: str

    backup_mysql: bool
    all_databases: bool
    special_databases = []

    backup_to_cloud: bool
    backup_mount_path: str
    backup_cloud_path: str
    backup_cloud_uri: str


    autoclean_local: bool
    local_time: int

    autoclean_remote: bool
    remote_time: int

    script_name: str
    test_mode: bool

    config_name = "config.ini"

    def __init__(self) -> None:
        file_path = os.path.dirname(os.path.realpath(__file__))
        self.config_name = file_path + "/" + self.config_name
        result = self.current.read(self.config_name)
        if result == []:
            logger.error("Config file {} does not exist".format(self.config_name))
            exit(1)
        self.__validate_sections()
        self.__read_all_params()

    def __validate_sections(self):
        sections = ['E-mail params', 'Local params', 'Backup files params', 'Backup mysql params', 'Transfer to cloud params',
        'Autoclear local params', 'Autoclear remote params', 'Script params']
        for section in sections:
            result: bool = self.current.has_section(section)
            if result == False:
                logger.error("Section {} does not exist in {}".format(section, self.config_name))
                exit(1)

    def __read_all_params(self):
        section = 'E-mail params'
        self.send_email = self.__get_or_bool(section, 'send_email', True)
        self.delete_log = self.__get_or_bool(section, 'delete_log', False)
        self.send_log = self.__get_or_bool(section, 'send_log', True)
        if self.send_email:
            self.email_to = self.__get_or_error(section, 'email_to')
            self.email_from = self.__get_or_error(section, 'email_from')
            self.email_subject = self.__get_or_error(section, 'email_subject')
            self.email_body = self.__get_or_error(section, 'email_body')
            self.email_server = self.__get_or_error(section, 'email_server')
            self.email_pass = self.__get_or_error(section, 'email_pass')
        section = 'Local params'
        self.backup_local_path = self.__get_or_error(section, 'backup_local_path')
        section = 'Backup files params'
        self.backup_files = self.__get_or_bool(section, 'backup_files', True)
        if self.backup_files:
            self.archive_name = self.__get_or_error(section, 'archive_name')
            self.exclude_expr = self.__get_or_empty_list(section, 'exclude_expr')
            self.archive_path = self.__get_or_error(section, 'archive_path')
            self.archive_size = self.__get_or_default_str(section, 'archive_size')
        section = 'Backup mysql params'
        self.backup_mysql = self.__get_or_bool(section, 'backup_mysql', True)
        if self.backup_mysql:
            self.all_databases = self.__get_or_bool(section, 'all_databases', True)
            self.special_databases = self.__get_or_empty_list(section, 'special_databases')
        section = 'Transfer to cloud params'
        self.backup_to_cloud = self.__get_or_bool(section, 'backup_to_cloud', False)
        if self.backup_to_cloud:
            self.backup_mount_path = self.__get_or_error(section, 'backup_mount_path')
            self.backup_cloud_path = self.__get_or_default_str(section, 'backup_cloud_path', default=self.backup_mount_path)
            self.backup_cloud_uri = self.__get_or_error(section, 'backup_cloud_uri')
        section = 'Autoclear local params'
        self.autoclean_local = self.__get_or_bool(section, 'autoclean_local', True)
        if self.autoclean_local:
            self.local_time = self.__parse_storage_time(section, 'local_time')
        section = 'Autoclear remote params'
        self.autoclean_remote = self.__get_or_bool(section, 'autoclean_remote', True)
        if self.autoclean_remote:
            self.remote_time = self.__parse_storage_time(section, 'remote_time')
        section = 'Script params'
        self.script_name = self.__get_or_default_str(section, 'script_name', "backupper_0.1")
        self.test_mode = self.__get_or_bool(section, 'test_mode', False)

    def __get_or_default_str(self, section, param , default = ''):
        try:
            return self.current.get(section, param)
        except configparser.NoOptionError:
            return default

    def __get_or_empty_list(self, section, param , default = []):
        try:
            result: str = self.current.get(section, param)
            return self.__parse_list(result)
        except configparser.NoOptionError:
            return default

    def __parse_list(self, value: str):
        res_str = value.replace(" ", "")
        res_list = res_str.split(",")
        return res_list

    def __get_or_bool(self, section, param, default = False):
        try:
            return self.current.getboolean(section, param)
        except configparser.NoOptionError:
            return default

    def __get_or_null(self, section, param, default = 0):
        try:
            return self.current.getint(section, param)
        except configparser.NoOptionError:
            return default

    def __get_or_error(self, section, param):
        try:
            return self.current.get(section, param)
        except configparser.NoOptionError:
            logger.error("In section {} option {} does not exist".format(section, param))
            exit(1)

    def __parse_storage_time(self, section, param):
        """ Read time from config and convert it to seconds
        """
        try:
            get_time: str = self.current.get(section, param)
            time: int = re.findall("\d+", get_time)[0]
            last_char = get_time[-1]
            days_multiplier = 24 * 60 * 60
            minutes_multiplier = 60
            last_variants={
                "D" : days_multiplier,
                "M" : minutes_multiplier,
                "S" : 1
            }
            multiplier = last_variants.get(last_char, 0)
            if multiplier < 1: 
                raise Exception("Not correct last character at storage time")
            else:
                final = int(time) * int(multiplier)
                return int(final)
        except configparser.NoOptionError:
            return int(0)

if __name__ == "__main__":
    config = Config()
    print(config.__dict__)