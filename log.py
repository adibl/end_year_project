"""
aotur: adi bleyer
date: 
"""

import logging
import datetime
import os
import threading

# remember to do assertsa
# update documentation


class log_file():
    def __init__(self, file_name, format):
        logging.basicConfig(filename=file_name, level=logging.DEBUG, format=format)
        global logger #FIXME: need to be self and not global
        logger = logging.getLogger()

        logger.info(datetime.datetime.now())
        global lock #FIXME: maby can be self.lock????
        lock = threading.Lock()

    def log(self, message, level):
        """
        :param message: the message to log
        :param level: the level of loggin between 1 to 5
        """
        with lock:
            print message
            if level == 1:
                logger.debug(str(message))
            elif level == 2:
                logger.info(str(message))
            elif level == 3:
                logger.warning(str(message))
            elif level == 4:
                logger.error(str(message))
            elif level == 5:
                logger.critical(str(message))
            else:
                print message


class file():
    def __init__(self, file_name):
        if not os.path.isfile(file_name):
            handel = open(file_name, 'w')
            handel.close()
            self.len = 0
        self.file_name = file_name
        self.len = os.stat(file_name).st_size
        self.adreses = {"aaa@aaa.com": [[], []], "bbb@aaa.com": [[], []]}
        print 'cc'


    def add(self, data):
        """
        add data to the database
        :param data:the data to add to the database
        """
        with lock:
            with open(self.file_name, 'a+') as handel:
                handel.write(data)
                self.len += len(data)

    def read_position(self, pos, length):
        """
        :param pos: the position to start reading
        :param length: the lengh of the messege to read
        """
        with open(self.file_name, 'r') as handel:
            handel.seek(pos)
            data = handel.read(length)
        print data


    def get_file_len(self):
        return self.len

    def add_email(self, email):
        """
        add the email to the database file and to the disionery
        :param email:the email opn list. the sender, list of resevers and the data.
        :return: add the email to the database and return his place in file, return the place of the email
        """
        place = self.add_to_database(email)
        self.add_to_dicsionery(place, email)
        return place


    def add_to_database(self, email):
        """
        add the email to the database file
        :param email:the email opn list. the sender, list of resevers and the data.
        :return: add the email to the database and return his place in file
        FIXME: what if the email not in list??
        """
        lengh = self.get_file_len()
        self.add(email[2])
        return lengh


    def add_to_dicsionery(self, place, email):
        """
        add the email place in file to the sender and the receivers
        :param place: the massage place in the file
        :param email: the email that is in the file
        :return: none
        """
        with lock:
            for dest in email[1]:
                self.adreses[dest][0].append((place, len(email)))
            self.adreses[email[0]][1].append((place, len(email)))
        print self.adreses

    def is_have(self, email):
        return email in self.adreses


def main():
    pass

if __name__ == '__main__':
    main()