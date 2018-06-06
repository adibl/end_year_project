"""
author; Adi Bleyer
Date: 52/5/18
description: file with the database classes
"""
# TODO:pep8
import logging
import os
import threading


class LogFile(object):
    def __init__(self, file_name, forma):
        """
        :param file_name: the name of the log file (don't have to exist)
        :param forma: the log format.
        """
        self.logger = logging.getLogger(file_name[:-3])
        formatter = logging.Formatter(forma)
        file_handler = logging.FileHandler(file_name, mode='w')
        file_handler.setFormatter(formatter)
        stream_handler = logging.StreamHandler()
        stream_handler.setFormatter(formatter)
        self.logger.setLevel(logging.DEBUG)
        self.logger.addHandler(file_handler)
        self.logger.addHandler(stream_handler)
        self.lock = threading.Lock()

    def log(self, message, level):
        """
        :param message: the message to log
        :param level: the level of loggin between 1 to 5
        """
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
        """
        :param file_name: the name of the log file (don't have to exist)
        """
        if not os.path.isfile(file_name):
            handel = open(file_name, 'w')
            handel.close()
            self.length = 0
        self.file_name = file_name
        self.length = os.stat(file_name).st_size
        self.lock = threading.Lock()

    def add(self, data):
        """
        add data to the database at the end
        :param data:the data to add to the database
        """
        with self.lock:
            with open(self.file_name, 'ab') as handel:
                handel.write(data)
                self.length += len(data)

    def read_position(self, place, length):
        """
        :param place: the position to start reading
        :param length: the lengh of the messege to read
        """
        with open(self.file_name, 'rb') as handel:
            handel.seek(place)
            data = handel.read(length)
        return data

    def get_file_len(self):
        """
        :return the total length of all the massages in the mailbox
        """
        return self.length


class Database(object):
    def __init__(self, file_name):
        """
        :param file_name: the name of the data file (don't have to exist)
        """
        self.data_file = DataFile(file_name)
        self.adreses = {'bob@gmail.com': EmailData(self.data_file), "alice@gmail.com": EmailData(self.data_file), "alice,@gmail.com": EmailData(self.data_file)}
        self.lock = threading.Lock()

    def add_email(self, email):
        """
        add the email to the database file and to the dictionary
        :param email:the email opn list. the sender, list of receivers and the data (sender,[dests list],data)
        :return: add the email to the database and return his place in file, return the place of the email
        """
        place = self.add_to_database(email)
        self.add_to_dicsionery(place, email)
        return place

    def add_to_database(self, email):
        """
        add the email to the database file
        :param email:the email opn list. the sender, list of resevers and the data.
        :return: add the email to the database and return his place in started
        FIXME: what if the email not in list??
        """
        lengh = self.data_file.get_file_len()
        self.data_file.add(email[2])
        return lengh

    def add_to_dicsionery(self, place, email):
        """
        add the email place in file to the sender and the receivers
        :param place: the massage place in the file
        :param email: the email that is in the file
        :return: none
        """
        with self.lock:
            for dest in email[1]:
                self.adreses[dest].add_recive_email(place, len(email[2]))
            self.adreses[email[0]].add_sent_email(place, len(email[2]))

    def is_have(self, email):
        """
        :return true if the email isa in the database and false otherwise
        """
        return email in self.adreses

    def get_user_data(self, email):
        """
        :return the user data class for certain email
        """
        return self.adreses[email]


class EmailData(object):
    def __init__(self, data_file):
        """
        :param data_file: the file name for the database (don't have to exist)
        """
        self.data_file = data_file
        self.recive_emails = []  # arry of tuples (email place,email lengh)
        self.sent_emails = []
        self.vaild_names = {}

    def add_recive_email(self, place, length):
        """
        add email to the receive emails list
        :param place: the email start index at the file.
        :param length: the email length in bytes
        return: None
        """
        self.recive_emails.append((place, length))

    def add_sent_email(self, place, length):
        """
        add email to the send emails list
        :param place: the email start index at the file.
        :param length: the email length in bytes
        return: None
        """
        self.sent_emails.append((place, length))

    def get_emails_num(self):
        """
        return: the number of email in the receive mailbox
        """
        return len(self.recive_emails)

    def get_emails_sum_length(self):
        """
        return: the sum lengh of all the emails in the mailbox
        """
        return sum(b[1] for b in self.recive_emails)

    def get_email(self, place):
        """
        :param place: the place of the email in the top of the mailbox, 1 for the last email received
        return: return the email from place x in the mail box
        """
        return self.data_file.read_position(self.recive_emails[-place][0], self.recive_emails[-place][1])

    def get_emails(self):
        """
        return: list of all the recv emails
        """
        return self.recive_emails

    def is_exzist_recive(self, index):
        """
        :param: index: the mail index in the mailbox
        return if there is such email index on the mailbox
        """
        return len(self.recive_emails) >= index

    def get_email_length(self, index):
        """
        :param: index: the mail index in the mailbox
        :return the email length
        """
        return self.recive_emails[-index][1]

    def is_valid_email(self, sender_email, sender_name):
        """
        check if the email name combination is valid
        :param sender_name: the name
        :param sender_email: the email
        :return if the combination is valid (unknown, valid or invalid)
        """
        if sender_email in self.vaild_names and sender_name in self.vaild_names[sender_email][0]:
            return '+valid '
        if sender_email in self.vaild_names and sender_name in self.vaild_names[sender_email][1]:
            return '-unvalid '
        return '?unknown '

    def add_sender_name(self, sender_email, sender_name, is_valid):
        """
        add a sender email to sertain name
        :param sender_email: the email to add
        :param sender_name: the name to add
        :param is_valid: True if the name and email combination is valid and False otherwise
        :return None
        """
        if is_valid:
            place = 0
        else:
            place = 1
        if sender_email not in self.vaild_names:
            self.vaild_names[sender_email] = [[], []]
        self.vaild_names[sender_email][place].append(sender_name)

    def __str__(self):
        return str(self.recive_emails) + str(self.sent_emails)


def defult_start(database):
    email = 'from: "alice" <alice@gmail.com>\r\nto:<alice@gmail.com>\r\nto:<bob@gmail.com>\r\ndate:2018-05-23 18:22:48.295000\r\nsubject:hi\r\nhelow\r\n.'
    database.add_email(['alice@gmail.com', ['bob@gmail.com', 'alice@gmail.com'], email])
    email = 'from: "alice" <alice,@gmail.com>\r\nto:<bob@gmail.com>\r\nto:<alice,@gmail.com>\r\ndate:2018-05-23 18:22:48.295000\r\nsubject:hi\r\nfake email\r\n.'
    database.add_email(['alice,@gmail.com', ['bob@gmail.com', 'alice,@gmail.com'], email])


def main():
    """
    none
    """
    pass

if __name__ == '__main__':

    main()
