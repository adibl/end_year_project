# -*- coding: utf-8 -*-
from Tkinter import *
import ScrolledText
from ttk import *
import socket
import time
import datetime
from log import LogFile

ENDINGS = ['.com', '.co.il']
SERVER_IP= "127.0.0.1"
SERVER_PORT = 20011
POP3_PORT = 1500


def login():
    print "log_in"
    window = Tk()
    window.title("login")
    window.minsize(300, 300)
    f = Frame(window)
    f.pack()
    l1 = Label(f, text='name: ')
    t1 = Entry(f, textvariable=StringVar())
    button1 = Button(f, text='Log-in', compound='bottom', command=f.quit)
    l1.pack()
    t1.pack()
    button1.pack()
    print 'window'
    f.mainloop()
    return (t1, f, window)

"""
def Sign_up(f, window):
    f.destroy()
    f =Frame(window)
    f.pack()
    l1 = Label(f, text='email:')
    l2 = Label(f, text='name: ')
    l3 = Label(f, text='pasword: ')
    t1 = Entry(f, textvariable=StringVar())
    t2 = Entry(f, show='*', textvariable=StringVar())
    t3 = Entry(f, textvariable=StringVar())
    button1 = Button(f, text='Sign-in', compound='bottom', command= lambda: check_valid(t1.get(), t2.get(), t3.get(), f, window))
    l1.pack()
    t1.pack()
    l2.pack()
    t2.pack()
    l3.pack()
    t3.pack()
    button1.pack()
    f.mainloop()
    """

def verify(email_box, client_socket):
    email = email_box.get()
    client_socket.sendall("USER " + email + "\r\n")
    log.log("USER " + email, 1)
    data = receive(client_socket, lambda d: "\r\n" not in d)
    return data[:3] == "+OK"

def wrong_email(f):
    l4 = Label(f, text="wrong Email adreses", foreground="red")
    l4.pack(side=BOTTOM)
    f.mainloop()



def POP3():
    name = 'adi'
    sender = 'aaa@aaa.com'
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        client_socket.connect((SERVER_IP, POP3_PORT))
        data = receive(client_socket, lambda data: "\r\n" not in data)
        if not data[:3] == "+OK":
            pass #FIXME:
        screen = login()
        while not verify(screen[0], client_socket):
            wrong_email(screen[0])
        screen[2].destroy()

        print 'login'
        client_socket.sendall("STAT\r\n")
        log.log("STAT\r\n", 1)
        data = receive(client_socket)
        emails = []
        for num in xrange(1,10,1):
            client_socket.sendall("RETR" + str(num) + "\r\n")
            log.log("RETR" + str(num) + "\r\n", 1)
            data = receive(client_socket, lambda data: "\r\n" not in data)
            if data[:3] != "+OK":
                break
            else:
                length = filter(lambda char: char.isdigit(), data)
                print length
                data = receive(client_socket, lambda d: "\r\n." not in d and "\n\n." not in d)
                print data
                emails.append(data)
        print emails
        #TODO: GUI thet give you the first 10 emails
    except socket.error as msg:
        print 'error in communication with server - ' + str(msg)
    finally:
        time.sleep(1)
        client_socket.close()


def check_valid(email):
    return '@' in email and any(end in email for end in ENDINGS)


def send_email_GUI():
    """
    GUI + send the input from user to ceck in the server and wait for responce
    :param client_socket: the comm socket
    """
    window = Tk()
    f = Frame(window)
    f.pack()
    window.title("send_email")
    window.minsize(1000, 1000)
    f =Frame(window)
    f.pack()
    l1 = Label(f, text='dest:')
    l2 = Label(f, text='head: ')
    l3 = Label(f, text='messege: ')
    t1 = Entry(f, textvariable=StringVar())
    t2 = Entry(f, textvariable=StringVar())
    t3 = ScrolledText.ScrolledText(f)
    button1 = Button(f, text='send mail', compound='bottom', command=f.quit)
    l1.pack()
    t1.pack()
    l2.pack()
    t2.pack()
    l3.pack()


    t3.pack()
    button1.pack()
    f.mainloop()
    return (t1, t2, t3, f)


def receive(client_socket, func=lambda data: "\r\n" not in data):
    """
    :param func: the exit funcsion of the while loop.
    :param client_socket: the comm socket
    :return: the data thet was recived from the socket
    FIXME: add return none if timeout (add timeout)
    """
    data = ""
    while func(data):
        data += client_socket.recv(1)
    log.log("RECV:" + data, 1)
    return data


def vaild_sender(client_socket, sender):
    """
    varify that the user email adres is ready to send email
    :param client_socket:
    :param sender: the email adress of the user
    :return: true if the email is good and the eror string otherwise
    """
    client_socket.sendall("MAIL FROM:" + "<" + sender + ">" + "\r\n")
    data = receive(client_socket, lambda d: "\r\n" not in d)
    if not data[:3] == "250":
        return data
    return True

def handshake(client_socket, sender):
    """
    varify the conection to the server
    :param client_socket: the comm socket
    :param sender: the email of the sender
    :return: true if the process ended and the eror string otherwise
    """
    data = receive(client_socket, lambda d: "\r\n" not in d)
    if not data[:3] == "220":
        return data
    client_socket.sendall("HELO " + sender[sender.find("@") + 1:] + "\r\n")
    data = receive(client_socket, lambda d: "\r\n" not in d)
    if not data[:3] == "250":
        return data
    return True


def valid_destinasions(client_socket, destination):
    """
    varify with the server that the email adreses exzist
    :param client_socket: the comm socket
    :param destination: the email adres we want to send to
    :return: true if the email is good and list of the unvalid emails otherwise
    """
    unvalid_emails = []
    for dest in destination:
        client_socket.sendall("RCPT TO:" + "<" + dest + ">" + "\r\n")
        data = receive(client_socket, lambda data: "\r\n" not in data)
        if not data[:3] == "250":
            unvalid_emails.append(dest)
    if len(unvalid_emails) == 0:
        return True
    return unvalid_emails


def send_email(client_socket):
    """
    send the email for ceck perpeses
    :param client_socket: the comm socket
    """


    dest_box, subject_box, text_box, f = send_email_GUI()
    dests = dest_box.get().split(" ")
    unvalid_dests = valid_destinasions(client_socket, dests)
    while unvalid_dests is not True:
        l4 = Label(f, text="wrong Email adreses are:" + str(unvalid_dests)[1:-1], foreground="red")
        l4.pack()
        f.mainloop()
        dests = dest_box.get().split(" ")
        unvalid_dests = valid_destinasions(client_socket, dests)
    email = ""
    for dest in dests:
            email += "To:" + "<" + dest + ">\r\n"
    email += "Date:" + str(datetime.datetime.now()) + "\r\n"
    subject = subject_box.get()
    if subject == "":
        subject = "(no subject)"
    email += "subject:" + subject + "\r\n"
    email += text_box.get(1.0, END)
    email += '\r\n.'
    return email


def send_email2(masseges):
    """
    ceck script for the server. send and dont varify the return value from the server
    :param masseges: list of masseges to send
    :return: none
    """
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        client_socket.connect((SERVER_IP, SERVER_PORT))
        # send the message
        for m in masseges:
            time.sleep(0.1)
            client_socket.sendall(m)
            print m
    except socket.error as msg:
        print 'error in communication with server - ' + str(msg)
    finally:
        time.sleep(1)
        client_socket.close()


def thread_client():
    """
    prrove thet the server treading works
    """
    global log
    log = LogFile("client.log", '%(levelname)s:%(message)s')
    from threading import Thread
    for send in range(1, 10, 1):
        thread = Thread(target=send_email, args=("aaa@aaa.com", 'adib', "bbb@aaa.com", "text", "my first client"+ str(send)))
        thread.start()




def SMTP():
    """
    the main comm punc. connect to the server and do handshake
    """
    name = 'adi'
    sender = 'aaa@aaa.com'
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        client_socket.connect((SERVER_IP, SERVER_PORT))
        # send the message
        #TODO: add the pop3 here. if he press on the send email go on
        if not handshake(client_socket, sender):
            print "unvalid handshake"   #FIXME: and GUI interfase
        if not vaild_sender(client_socket, sender):
            print "unvalid email adress"   #FIXME: and GUI interfase
        email = "From:" + ' "' + name + '" ' + "<" + sender + ">" + "\r\n"
        email += send_email(client_socket)

        client_socket.sendall("DATA\r\n")
        data = receive(client_socket, lambda data: "\r\n" not in data)
        if not data[:3] == "354":
            print 'server error' #FIXME: and GUI interfase
        client_socket.sendall(email)
        data = receive(client_socket, lambda data: "\r\n" not in data)
        if not data[:3] == "250":
            print 'unvalid email' #FIXME: and GUI interfase
        print 'send'
    except socket.error as msg:
        print 'error in communication with server - ' + str(msg)
    finally:
        time.sleep(1)
        client_socket.close()

def main():
    """
    this is a ceack func
    """
    send_email2(["HELO relay.example.com\r\n", "MAIL FROM:<aaa@aaa.com>\r\n", "RCPT TO:<ccc@aaa.com>\r\n", "RCPT TO:<bbb@aaa.com>\r\n", "DATA\r\n", "From:<aaa@aaa.com>\r\nTo:<bbb@aaa.com>\r\nsubject:aa\r\nDate:123\r\nteast\r\n.\r\n", "QUIT\r\n"]) #yes- valid email sent
    send_email2(["HELO relay.example.com", "MAIL FROM:<ccc@aaa.com>\r\n", "MAIL FROM:<bbb@aaa.com>\r\n", "RCPT TO:<aaa@aaa.com>\r\n", "DATA\r\n", "From:<bbb@aaa.com>\r\nTo:<aaa@aaa.com>\r\nsubject:aa\r\nDate:123\r\neast\r\n.\r\n\r\n.\r\n", "QUIT\r\n"]) #yes -valid email sent
    send_email2(["HELO relay.example.com", "MAIL FROM:<bbb@aaa.com>\r\n", "RCPT TO:<aaa@aaa.com>\r\n", "QUIT\r\n"]) #yes unvalid
    send_email2(["HELO relay.example.\r\n", "QUIT\r\n"]) #yes
    send_email2(["QUIT\r\n"]) # yes
    send_email2(["GET HTTP1.1\r\n"]) #yes
    send_email2(["HELO relay.example.com", "MAIL FROM:<ccc@aaa.com>\r\n", "MAIL FROM:<bbb@aaa.com>\r\n",
               "RCPT TO:<aaa@aaa.com>\r\n", "DATA\r\n",
               "From:<bbb@aaa.com>\r\nTo:<aba@aaa.com>\r\nsubject:aa\r\nDate:123\r\nteast\r\n.\r\n\r\n.\r\n", "QUIT\r\n"])  # yes


if __name__ == '__main__':
    global log
    log = LogFile("client.log", '%(levelname)s:%(message)s')
    SMTP()
    POP3()