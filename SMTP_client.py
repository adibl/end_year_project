# -*- coding: utf-8 -*-
from Tkinter import *
import ScrolledText
from ttk import *
import socket
import time
import datetime
from log import log_file

ENDINGS = ['.com', '.co.il']
SERVER_IP= "127.0.0.1"
SERVER_PORT = 20011

def login():
    window = Tk()
    f = Frame(window)
    f.pack()
    window.title("login")
    window.minsize(300, 300)
    l1 = Label(f, text='name: ')
    l2 = Label(f, text='pasword: ')
    t1 = Entry(f, textvariable=StringVar())
    t2 = Entry(f, show='*', textvariable=StringVar())
    button1 = Button(f, text='Log-in', compound='bottom', command= lambda: verify(t1.get(), t2.get(), window))
    button2 = Button(f, text='Sign-in', compound='bottom', command= lambda: Sign_up(f, window))
    s1 = Scrollbar.pack(side=RIGHT, fill=Y)

    l1.pack()
    t1.pack()
    l2.pack()
    t2.pack()
    button1.pack()
    button2.pack()
    s1.pack()
    f.mainloop()

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

def check_valid(email):
    return '@' in email and any(end in email for end in ENDINGS)

def send_massege(dest, head, massege, f):
    if check_valid(dest):
        f.destroy()
        print massege
        return True
    l = Label(f, text="wrong Email adress", foreground="red")
    l.grid(row=0, column=2)
    return False

#unused def
def erores_GUI(erores, f):
    print erores
    l = Label(f, text="wrong Email adress", foreground="red")
    button1.configure(command=f.quit)
    #FIXME: cange buttom sedt funcsion to end the mainloop
    l.grid(row=0, column=2)
    f.mainloop()
    return t1.get()

def send_email_GUI(client_socket):
    """
    GUI + send the input from user to ceck in the server and wait for responce
    :param client_socket: the comm socket
    """
    window = Tk()
    f = Frame(window)
    f.pack()
    window.title("send_email")
    window.minsize(700, 700)
    f =Frame(window)
    f.pack()
    l1 = Label(f, text='dest:')
    l2 = Label(f, text='head: ')
    l3 = Label(f, text='messege: ')
    global t1 #FIXME: make it not global, may not do nothing wrong
    t1 = Entry(f, textvariable=StringVar())
    t2 = Entry(f, textvariable=StringVar())
    t3 = ScrolledText.ScrolledText(f)
    global button1 #FIXME: make it not global, may not do nothing wrong
    button1 = Button(f, text='send mail', compound='bottom', command=f.quit)
    l1.grid()
    t1.grid(row=0, column=1, sticky=W+E+N+S)
    l2.grid(row=1, column=0)
    t2.grid(row=1, column=1, sticky=W+E+N+S)
    l3.grid(column=1)
    t3.grid(column=0, columnspan=3)
    button1.grid(column=1)
    f.columnconfigure(0, weight=1, uniform='third')
    f.columnconfigure(1, weight=2, uniform='third')
    f.columnconfigure(2, weight=1, uniform='third')
    f.mainloop() #FIXME: make the text above to func thet return t and tuple of the botooms
    dests = t1.get().split(" ")
    while valid_destinasions(client_socket, dests) is not True:
        l4 = Label(f, text="wrong Email adress", foreground="red")
        l4.grid(row=0, column=2)
        f.mainloop()
        dests = t1.get().split(" ")
    email = ""
    for dest in dests:
            email += "To:" + "<" + dest + ">\r\n"
    email += "Date:" + str(datetime.datetime.now()) + "\r\n"
    email += "subject:" + t2.get() + "\r\n"
    email += t3.get(1.0, END)
    email += '\r\n.'
    return email


"""
def verify(user_name, password, window):
    print user_name
    print password
    if password == 'aaa' and user_name == 'aaa':
        window.destroy()
    else:
        m1 = Label(window, text='paswword or user name is wrong, enter again', foreground='red2')
        m1.pack()
        window.mainloop()
        """


def receive(client_socket, func):
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


#not in use
def send_email(sender, name, destinations, subject, massege, frame):
    """
    :param sender: the email sdress of the sender
    :param name: the name of the sender
    :param destinations: list of the destinations emails
    :param subject: the email subject
    :param massege: the email content
    :return: none
    #FIXME: make the print to reask the user
    """
    print sender
    print name
    print destinations
    destinations = destinations.split(" ")
    print destinations
    print subject
    print massege
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        client_socket.connect((SERVER_IP, SERVER_PORT))
        # send the message
        if not handshake(client_socket, sender):
            print "unvalid handshake"
        if not vaild_sender(client_socket, sender):
            print "unvalid email adress"
        email = "From:" + ' "' + name + '" ' + "<" + sender + ">" + "\r\n"
        unvalid_destinations = valid_destinasions(client_socket, destinations)

        while unvalid_destinations is not True:
            print 'unvalid dests'
            destinations = erores_GUI(unvalid_destinations, frame).split(" ")
            print 'quit'
            unvalid_destinations = valid_destinasions(client_socket, destinations)
            print unvalid_destinations

        print 'go over'
        for dest in destinations:
            email += "To:" + "<" + dest + ">\r\n"
        email += "Date:" + str(datetime.datetime.now()) + "\r\n"
        email += "subject:" + subject + "\r\n"
        email += massege
        email += '\r\n.'
        print email

        client_socket.sendall("DATA\r\n")
        data = receive(client_socket, lambda data: "\r\n" not in data)
        if not data[:3] == "354":
            print 'server error'
        client_socket.sendall(email)
        data = receive(client_socket, lambda data: "\r\n" not in data)
        if not data[:3] == "250":
            print 'unvalid email'
        print 'send'

    except socket.error as msg:
        print 'error in communication with server - ' + str(msg)
    finally:
        frame.destroy()
        time.sleep(1)
        while not receive(client_socket, lambda d:"\r\n" not in d)[:3] == "221":
            client_socket.send("QUIT\r\n")
        client_socket.close()


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
            time.sleep(0.5)
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
    log = log_file("client.log", '%(levelname)s:%(message)s')
    from threading import Thread
    for send in range(1, 10, 1):
        thread = Thread(target=send_email, args=("aaa@aaa.com", 'adib', "bbb@aaa.com", "text", "my first client"+ str(send)))
        thread.start()

def GUI():
    """
    the main comm punc. connect to the server and do handshake
    """
    name = 'adi'
    sender = 'aaa@aaa.com'
    global log
    log = log_file("client.log", '%(levelname)s:%(message)s')
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
        email += send_email_GUI(client_socket)

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
    send_email2(["HELO relay.example.com", "MAIL FROM:<ccc@aaa.com>\r\n", "MAIL FROM:<bbb@aaa.com>\r\n", "RCPT TO:<aaa@aaa.com>\r\n", "DATA\r\n", "From:<bbb@aaa.com>\r\nTo:<aaa@aaa.com>\r\ntsubject:aa\r\nDate:123\r\neast\r\n.\r\n\r\n.\r\n", "QUIT\r\n"]) #yes -valid email sent
    send_email2(["HELO relay.example.com", "MAIL FROM:<bbb@aaa.com>\r\n", "RCPT TO:<aaa@aaa.com>\r\n", "QUIT\r\n"]) #yes unvalid
    send_email2(["HELO relay.example.\r\n", "QUIT\r\n"]) #yes
    send_email2(["QUIT\r\n"]) # yes
    send_email2(["GET HTTP1.1\r\n"]) #yes
    send_email2(["HELO relay.example.com", "MAIL FROM:<ccc@aaa.com>\r\n", "MAIL FROM:<bbb@aaa.com>\r\n",
               "RCPT TO:<aaa@aaa.com>\r\n", "DATA\r\n",
               "From:<bbb@aaa.com>\r\nTo:<aba@aaa.com>\r\nsubject:aa\r\nDate:123\r\nteast\r\n.\r\n\r\n.\r\n", "QUIT\r\n"])  # yes but the server disconect the client without he sent QUIT and make him crush

    global log
    log = log_file("client.log", '%(levelname)s:%(message)s')
    send_email("aaa@aaa.com", 'adib', "bbb@aaa.com", "text", "my first client") # yes
    send_email("aaa@aaa.com", 'adib', "bbb@aaa.com ccc@aaa.com", "text", "my first client")


if __name__ == '__main__':
    GUI()