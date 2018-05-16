"""
aotur: adi bleyer
date: 
"""

import logging
import os
import threading
# remember to do assertsa
# update documentation


class LogFile(object):
    def __init__(self, file_name, forma):
        self.logger = logging.getLogger(file_name[:-3])
        formatter = logging.Formatter('%(asctime)s : %(message)s')
        fileHandler = logging.FileHandler(file_name, mode='w')
        fileHandler.setFormatter(formatter)
        streamHandler = logging.StreamHandler()
        streamHandler.setFormatter(formatter)

        self.logger.setLevel(logging.DEBUG)

        self.logger.addHandler(fileHandler)
        self.logger.addHandler(streamHandler)
        self.lock = threading.Lock()

    def log(self, message, level):
        """
        :param message: the message to log
        :param level: the level of loggin between 1 to 5
        """
        print message
        with self.lock:
            if level == 1:
                self.logger.debug(str(message))
            elif level == 2:
                self.logger.info(str(message))
            elif level == 3:
                self.logger.warning(str(message))
            elif level == 4:
                self.logger.error(str(message))
            elif level == 5:
                self.logger.critical(str(message))
            else:
                print message


class DataFile(object):
    def __init__(self, file_name):
        if not os.path.isfile(file_name):
            handel = open(file_name, 'w')
            handel.close()
            self.length = 0
        self.file_name = file_name
        self.length = os.stat(file_name).st_size
        self.adreses = {'bbb@aaa.com': EmailData(), "aaa@aaa.com": EmailData()}
        self.lock = threading.Lock()

    def add(self, data):
        """
        add data to the database
        :param data:the data to add to the database
        """
        with self.lock:
            with open(self.file_name, 'a+') as handel:
                handel.write(data)
                self.length += len(data)

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
        return self.length

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
        print "aa" + str(email)
        with self.lock:
            for dest in email[1]:
                self.adreses[dest].add_recive_email(place, len(email[2]))
            self.adreses[email[0]].add_sent_email(place, len(email[2]))
        print self.adreses

    def is_have(self, email):
        return email in self.adreses

    def GetUserData(self, email):
        print type(self.adreses[email])
        return self.adreses[email]


class EmailData(object):
    def __init__(self):
        self.recive_emails = []
        self.sent_emails = []

    def add_recive_email(self, place, length):
        self.recive_emails.append((place, length))
        print "add" + str(self.recive_emails)

    def add_sent_email(self, place, length):
        self.sent_emails.append((place, length))

    def get_emails_num(self):
        return len(self.recive_emails)

    def get_emails_sum_length(self):
        return sum(b[1] for b in self.recive_emails)

    def get_email(self, place):
        return self.recive_emails[-place]

    def get_emails(self):
        return self.recive_emails

    def IsExistRecive(self, index):
        return len(self.recive_emails) >= index

    def get_email_length(self, index):
        return self.recive_emails[-index][1]

    def __str__(self):
        return str(self.recive_emails) + str(self.sent_emails)



def main():
    pass

if __name__ == '__main__':
    main()