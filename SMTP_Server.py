"""
author; Adi Bleyer
Date: 52/5/18
description: the SMTP server
"""
import socket
from threading import Thread


IP = '0.0.0.0'
PORT = 20011
QUEUE_SIZE = 10
READ_SIZE = 1


DOMINS = ".com"
SENDER_HEADER = "MAIL FROM:"
DEST_HEADER = "RCPT TO:"
HELO_OPTIONS = ["HELO"]

DESTINATION_INVALID = "515 - Destination mailbox address invalid\r\n"
BAD_REQUEST = "500 - Bad Request\r\n"
END_COMM = "221 - Domain service closing transmission channel\r\n"
READY = "220 - Domain service ready\r\n"
COMPLETED_SUCCESSFULLY = "250 - Requested mail action completed and OK\r\n"
START_DATA = "354 - Start mail input; end with .\r\n"
TIMEOUT = 15
START_SEND = "DATA"
END_COMM = "QUIT"


def receive(client_socket, func=lambda data: "\r\n" not in data):
    """
    :param func: the exit funcsion of the while loop.
    :param client_socket: the comm socket
    :return: the data thet was recived from the socket
    """
    data = ""
    while func(data):
        data += client_socket.recv(1)
    log.log("RECV:" + data, 1)
    return data


def hendel_client(client_socket, aa):
    """
    handel sending email client.
    :param client_socket: the current client socket
    :param data: the data thet was get from the user befor
    :return: true if the conecsion cloze and false other
    """
    try:
        if not handshake(client_socket):
            client_socket.close()
            return
        while True:
            data2 = receive(client_socket)
            log.log("RECV:" + data2, 1)
            if ":" in data2:
                email = get_email(client_socket, data2)
                if email is not False:
                    place = database.add_email(email)
                    log.log("gat email from " + email[0] + " in place " + str(place), 2)
                else:
                    client_socket.close()
                    return
            elif data2[:4] == END_COMM:
                client_socket.sendall(END_COMM)
                log.log("SEND" + END_COMM, 1)
                client_socket.close()
                return
    except socket.error as err:
        log.log("socket eror" + str(err), 3)
        client_socket.close()


def handshake(client_socket):
    """
    do the handshake according to the SMTP protocol
    :param client_socket: the current client socket
    :return: return true if handshake seceded and false if not
    """
    client_socket.send(READY)
    log.log("SEND:" + READY, 1)
    data = receive(client_socket)
    if data[:4] in HELO_OPTIONS:
        client_socket.send(COMPLETED_SUCCESSFULLY)
        log.log("SEND:" + COMPLETED_SUCCESSFULLY, 1)
    elif data[:4] == END_COMM:
        client_socket.send(END_COMM)
        log.log("SEND:" + END_COMM, 1)
        return False
    else:
        return False
    return True


def filter_massege(sender, dests, data):
    """
    :param sender: the sender email address
    :param dests: the receivers email address
    :param data: the email content
    :return: return true if the email headers maches to the pretend and false otherwise
    """
    is_valid = True
    is_sender = False
    is_date = False
    is_subject = False
    for line in data.split("\r\n"):
        if ":" in line:
            if "from" in line and "<" in line and ">" in line:
                is_sender = line[line.find("<") + 1:line.find(">")] == sender
            elif ("to:" in line or "cc" in line) and "<" in line and ">" in line:
                dest = line[line.find("<") + 1:line.find(">")]
                is_valid = is_valid and (dest in dests or database.is_have(dest))
            is_date = is_date or "date" in line
            is_subject = is_subject or "subject" in line
    return is_valid and is_sender and is_date and is_subject


def get_email(client_socket, data):
    """
    get all the email parameters from user
    :param client_socket:  the client socket
    :param data: the data thet was already receved
    :return: false if ther was a problem and list if the email is ready.
    FIXME: endless while loops
    """
    data = data
    if SENDER_HEADER not in data:
        return False
    sender = data[data.find("<")+1:data.find(">")]
    while not database.is_have(sender):
        client_socket.send(DESTINATION_INVALID)
        log.log("SEND:" + DESTINATION_INVALID, 1)
        data = receive(client_socket)
        if SENDER_HEADER not in data:
            return False
        sender = data[data.find("<") + 1:data.find(">")]
    client_socket.send(COMPLETED_SUCCESSFULLY)
    log.log("SEND:" + COMPLETED_SUCCESSFULLY, 1)

    data = ""
    dests = []
    while not data[:4] == START_SEND:
        data = receive(client_socket)
        if data[:len(DEST_HEADER)] == DEST_HEADER:
            ds = data[data.find("<")+1:data.find(">")]
            if database.is_have(ds):
                dests.append(ds)
                client_socket.send(COMPLETED_SUCCESSFULLY)
                log.log("SEND:" + COMPLETED_SUCCESSFULLY, 1)
            else:
                client_socket.send(DESTINATION_INVALID)
                log.log("SEND:" + DESTINATION_INVALID, 1)
        elif data[:4] == START_SEND and len(dests) > 0:
            client_socket.send(START_DATA)
            log.log("SEND:" + START_DATA, 1)
        elif data[:4] == END_COMM:
            return False                    # problem becose it wont QUIT
        else:
            client_socket.send(BAD_REQUEST)
            log.log("SEND:" + BAD_REQUEST, 1)
    data = ""
    while not data[-3:] == "\r\n.":
        data += client_socket.recv(1)
        data = data.lower()
    log.log("RECV:" + data, 1)
    if not filter_massege(sender, dests, data):
        client_socket.send(BAD_REQUEST)
        log.log("SEND:" + BAD_REQUEST, 1)
        return False
    client_socket.send(COMPLETED_SUCCESSFULLY)
    log.log("SEND:" + COMPLETED_SUCCESSFULLY, 1)

    return [sender, dests, data]


def main_loop(d, l):
    """
    the main server loop, waits for messages from clients and acts according
    :return: None, endless loop
    """
    global database
    database = d
    global log
    log = l
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        server_socket.bind((IP, PORT))
        server_socket.listen(QUEUE_SIZE)
        log.log("Listening for connections on port %d" % PORT, 2)
        while True:
            client_socket, client_address = server_socket.accept()
            client_socket.settimeout(TIMEOUT)
            thread = Thread(target=hendel_client, args=(client_socket, client_address))
            log.log("new connection from " + str(client_address), 2)
            thread.start()
    except socket.error as err:
        log.log('received socket exception - ' + str(err), 3)
    finally:
        server_socket.close()


def main():
    """
    Add Documentation here
    """


if __name__ == '__main__':
    pass
