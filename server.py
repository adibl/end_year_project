# -*- coding: utf-8 -*-
from log import LogFile
from log import DataFile
from threading import Thread
from SMTP_Server import main_loop
from POP3_server import main2
import logging


def main():
    """
    Add Documentation here
    """



    database = DataFile("data.txt")
    log1 = LogFile("smtp.log", '%(thread)d %(levelname)s:%(message)s')
    log2 = LogFile("pop3.log", '%(levelname)s:%(message)s')
    thread = Thread(target=main_loop, args=(database, log1))
    thread2 = Thread(target=main2, args=(database, log2))

    thread.start()
    thread2.start()


if __name__ == '__main__':
    main()