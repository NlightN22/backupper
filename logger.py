import sys
import logging
import os

class Logger:
    scriptname="backupper_script"
    log_filename = '/var/log/' + scriptname + '.log'
    __log_formatter = logging.Formatter('%(levelname)s %(asctime)s :: %(message)s', 
                                    datefmt='%d/%m/%Y %H:%M:%S')
    #Setup File handler
    __file_handler = logging.FileHandler(log_filename)
    __file_handler.setFormatter(__log_formatter)
    __file_handler.setLevel(logging.INFO)
    #Setup Stream Handler (i.e. console)
    __stream_handler = logging.StreamHandler(sys.stdout)
    __stream_handler.setFormatter(__log_formatter)
    __stream_handler.setLevel(logging.INFO)
    #Get our logger
    __logger = logging.getLogger('root')
    __logger.setLevel(logging.INFO)
    #Add both Handlers
    __logger.addHandler(__file_handler)
    __logger.addHandler(__stream_handler)

    def log(self, message):
        self.__logger.info(message)
		
    def error(self, message):
        self.__logger.error(message)

    def clear_old_log(self, log_filename: str):
        if os.path.exists(log_filename):
            os.remove(log_filename)
            self.__logger.info("Old log file {} cleared".format(self.log_filename))