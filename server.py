# -*- coding: utf-8 -*-
"""
author; Adi Bleyer
Date: 52/5/18
description: mai server, the lanch file of the servers
"""
from log import LogFile
from log import Database
from log import defult_start
from threading import Thread
from SMTP_Server import main_loop
from POP3_server import main2


def main():
    """
    the main server script.
    create the database and run both of the servers
    """
    database = Database("data.txt")
    log1 = LogFile("smtp.log", '%(thread)d %(levelname)s:%(message)s')
    defult_start(database)
    log2 = LogFile("pop3.log", '%(thread)d %(levelname)s:%(message)s')
    thread = Thread(target=main_loop, args=(database, log1))
    thread2 = Thread(target=main2, args=(database, log2))

    thread.start()
    thread2.start()


if __name__ == '__main__':
    main()
