# -*- coding: utf-8 -*-
from threading import Thread
import socket



IP = '0.0.0.0'
PORT = 1500
QUEUE_SIZE = 10
LOGIN_MESSAGE = "+OK POP3 server ready\r\n"
USER_EXIST = "+OK User accepted\r\n"
NO_SUCH_FILE = "-ERR no such message, only {0} messages in maildrop\r\n"
NO_SUCH_USER = "-ERR no such email adress\r\n"
SING_OFF = "+OK dewey POP3 server signing off\r\n"

def receive(client_socket, func):
    """
    :param func: the exit funcsion of the while loop.
    :param client_socket: the comm socket
    :return: the data thet was recived from the socket
    """
    #FIXME: add return none if timeout (add timeout) cann end the prog with sys.exit()
    data = ""
    while func(data):
        data += client_socket.recv(1)
    log2.log("RECV:" + data, 1)
    return data

def login(client_socket):
    client_socket.sendall(LOGIN_MESSAGE)
    log2.log("SEND:" + LOGIN_MESSAGE, 1)
    data = receive(client_socket, lambda m: "\r\n" not in m)
    if data[:4] == "USER":
        user = data[data.find(" ") + 1:data.find("\r\n")]
        while not database.is_have(user):
            client_socket.sendall(NO_SUCH_USER)
            log2.log("SEND:" + NO_SUCH_USER, 1)
            data = receive(client_socket, lambda m: "\r\n" not in m)
            user = data[data.find(" ") + 1:data.find("\r\n")]

        client_socket.sendall(USER_EXIST)
        log2.log("SEND:" + USER_EXIST, 1)
        return user, "+OK"
    else:
        return None, "unvalid request"



def HendelClient(client_socket, client_address):
    try:
        user, eror = login(client_socket)
        if eror != "+OK":
            client_socket.sendall("-ERR" + eror)
            log2.log("-ERR" + eror)
            return
        user_data = database.get_user_data(user)
        print user_data
        data = receive(client_socket, lambda m: "\r\n" not in m)
        if not data == "STAT\r\n":
            client_socket.sendall("-ERR" + eror)
            log2.log("-ERR" + eror)
            return
        responce = "+OK "
        responce += str(user_data.get_emails_num())
        responce += " massages ("
        responce += str(user_data.get_emails_sum_length())
        responce += ")\r\n"
        client_socket.sendall(responce)
        log2.log("SEND:" + responce, 1)
        data = receive(client_socket, lambda m: "\r\n" not in m)
        while data != "QUIT\r\n":
            if data[:4] == "LIST":
                if data == "LIST\r\n":
                    responce = "+OK "
                    responce += str(user_data.get_emails_num())
                    responce += " massages ("
                    responce += str(user_data.get_emails_sum_length())
                    responce += ")"
                    client_socket.sendall(responce)
                    log2.log("SEND:" + responce, 1)
                elif any(char.isdigit() for char in data):
                    print 'LIST x'
                    index = filter(lambda char: char.isdigit(), data)
                    index = int(index)
                    if user_data.IsExistRecive(index):
                        responce = "+OK "
                        responce += str(index)
                        responce += " massages ("
                        responce += str(user_data.get_email_length(index))
                        responce += ")"
                        client_socket.sendall(responce)
                        log2.log("SEND:" + responce, 1)
                    else:
                        responce = NO_SUCH_FILE.format(user_data.get_emails_num())
                        client_socket.sendall(responce)
                        log2.log("SEND:" + responce, 1)
            elif data[:4] == "RETR" and any(char.isdigit() for char in data):
                index = filter(lambda char: char.isdigit(), data)
                index = int(index)
                print index
                if not user_data.IsExistRecive(index):
                    responce = NO_SUCH_FILE.format(user_data.get_emails_num())
                    client_socket.sendall(responce)
                    log2.log("SEND:" + responce, 1)
                else:
                    responce = "+OK "
                    responce += str(user_data.get_email_length(index))
                    responce += " octets\r\n"
                    client_socket.sendall(responce)
                    log2.log("SEND:" + responce, 1)
                    email = user_data.get_email(index)
                    print email
                    client_socket.sendall(email)
                    log2.log("SEND:" + email, 1)

            elif data == "":
                pass
            data = receive(client_socket, lambda m: "\r\n" not in m)
    finally:
        client_socket.sendall(SING_OFF)
        log2.log("SEND:"+SING_OFF, 1)
        client_socket.close()






def main2(d, l):
    """
    Add Documentation here
    """
    global database
    database = d
    global log2
    log2 = l
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        server_socket.bind((IP, PORT))
        server_socket.listen(QUEUE_SIZE)
        log2.log("Listening for connections on port %d" % PORT, 2)

        while True:
            client_socket, client_address = server_socket.accept()
            thread = Thread(target=HendelClient, args=(client_socket, client_address))
            log2.log("new connection from " + str(client_address), 2)
            thread.start()
    except socket.error as err:
        log2.log('received socket exception - ' + str(err), 3)
    finally:
        server_socket.close()


if __name__ == '__main__':
    pass