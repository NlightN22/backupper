import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders
import os

from config_parser import Config
from logger import Logger

config = Config()

class Emailer:
    """ Send e-mail with attachment"""
    def __init__(self, logger_in: Logger = "") -> None:
        if logger_in == "":
            self.logger = Logger()
        else:
            self.logger = logger_in

        self.send_log=config.send_log
        self.delete_log = config.delete_log
        self.email_to=config.email_to
        self.email_from=config.email_from
        self.email_subject=config.email_subject
        self.email_server=config.email_server
        self.email_pass=config.email_pass
        self.test_mode=config.test_mode

    def send_log_to_email(self, body: str = "", log_filename_in: str = ""):
        if body == "":
            self.email_body = config.email_body
        else:
            self.email_body = body

        if log_filename_in == "":
            log_filename = self.logger.log_filename
        else:
            log_filename = log_filename_in
        if os.path.exists(log_filename):
            message = MIMEMultipart()
            message['From'] = self.email_from
            message['To'] = self.email_to
            message['Subject'] = self.email_subject
            message.attach(MIMEText(self.email_body, 'plain'))
            if self.send_log:
                message.attach(self.__attach_file(log_filename))
            my_message = message.as_string()
            if self.test_mode:
                self.logger.log("Send to server {} message {}".format(self.email_server, my_message))
            else:
                self.logger.log("START Send e-mail")
                self.__send_email(my_message)
                self.logger.log("END Send e-mail")
            if self.delete_log:
                self.logger.log("START delete log")
                if self.test_mode:
                    self.logger.log("Delete old log: {}".format(log_filename))
                else:
                    self.logger.clear_old_log(log_filename)
                self.logger.log("END delete log")
        else:
            self.logger.error("Logfile {} does not exist".format(log_filename))

    def __attach_file(self, file: str):
        attachment = open(file, 'rb')
        obj = MIMEBase('application','octet-stream')
        obj.set_payload((attachment).read())
        encoders.encode_base64(obj)
        obj.add_header('Content-Disposition',"attachment; filename="+ self.logger.scriptname + ".log")
        return obj

    def __send_email(self, my_message: str):
            email_session = smtplib.SMTP(self.email_server,587)
            email_session.starttls()
            email_session.login(self.email_from,self.email_pass)
            email_session.sendmail(self.email_from, self.email_to, my_message)
            email_session.quit()