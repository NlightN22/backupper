import subprocess
from datetime import datetime

from logger import Logger
from system_runner import Runner
from config_parser import Config
config = Config()
runner = Runner()

class MySQLBackupper:
    def __init__(self, logger_in: Logger = "") -> None:
        self.all_databases = config.all_databases
        self.special_databases = config.special_databases
        self.backup_local_path = config.backup_local_path
        if logger_in == "":
            self.logger = Logger()
        else:
            self.logger = logger_in

    def backup_mysql(self):
        """ Create dump of mysql databases
        return list of dictionary - filename pattern : result backup command
        """
        result_list: dict = {}
        db_list = self.get_all_dbs()
        if db_list == []:
            self.logger.error("Empty list of databases")
            return result_list

        if self.all_databases:
            self.logger.log("START dump for all databases")
            for db in db_list:
                result_list.update(self.make_dump(db))
            self.logger.log("END dump for all databases")
        else:
            self.logger.log("Check special databases: {} in current mysql list".format(self.special_databases))
            checked_list: list[str] = []
            for db in self.special_databases:
                if db in db_list:
                    checked_list.append(db)
                else:
                    self.logger.error("Can't find {} in current list of databases {}".format(db, db_list))
                    return result_list
            self.logger.log("START dump for existing databases: {}".format(checked_list))
            for db in checked_list:
                result_list.update(self.make_dump(db))
            self.logger.log("END dump for existing databases: {}".format(checked_list))
            self.logger.log("Return dump state: {}".format(result_list))
        return result_list

    def make_dump(self, db:str):
        test_mode = config.test_mode
        filename = self.backup_local_path + db + self.get_current_date_time()
        make_dump_command = "mysqldump {} > {}.sql".format(db, filename)
        if test_mode:
            self.logger.log("backup_mysql Run: {}".format(make_dump_command))
            result = 0
        else:
            result = runner.run(make_dump_command)
        self.logger.log("Result of dumping {} : {}".format(db,result))
        return {filename : result}

    def get_all_dbs(self):
        #get_db_command = "mysql -e 'show databases' -s --skip-column-names"
        get_db_command = "mysql -e 'show databases' -s --skip-column-names "
        try:
            result = subprocess.check_output(get_db_command, stderr=subprocess.STDOUT, universal_newlines=True, timeout=5, shell=True) 
            db_list = result.split("\n")
            while('' in db_list):
                db_list.remove('')
            self.logger.log("Get databases: {}".format(db_list))
            return db_list
        except subprocess.CalledProcessError or subprocess.TimeoutExpired:
            self.logger.error("Can't get list of databases. Command or permissions not correct.\n" + 
            "Check or create \".my.cnf\" in user directory with your credentials.\n" + 
            "Something like: \n" +
            "[client]\nuser=root\npassword=\'YouRSuperMysqlPassWord\'\nsocket=/var/lib/mysqld/mysqld.sock")
            return []

    def get_current_date_time(self):
        now = datetime.now()
        dt_string = now.strftime("_%d%m%Y_%H%M%S_")
        return dt_string