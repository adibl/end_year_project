# -*- coding: utf-8 -*-
"""
author; Adi Bleyer
Date: 52/5/18
description: email client (SMTP/POP3)
"""
from Tkinter import *
import ScrolledText
from ttk import *
import socket
import time
import datetime
from log import LogFile
import tkMessageBox

ENDINGS = ['.com', '.co.il']
SERVER_IP = "127.0.0.1"
SERVER_PORT = 20011
POP3_PORT = 1500
START_EMAIL = "<"
END_EMAIL = ">"
SENDER_NAME = '"'


def login(client_socket):
    print "log_in"
    window = Tk()
    window.title("login")
    window.minsize(300, 300)
    f = Frame(window)
    f.pack()
    l1 = Label(f, text='email: ')
    t1 = Entry(f, textvariable=StringVar())
    l2 = Label(f, text='name: ')
    t2 = Entry(f, textvariable=StringVar())
    button1 = Button(f, text='Log-in', compound='bottom', command=f.quit)
    l1.pack()
    t1.pack()
    l2.pack()
    t2.pack()
    button1.pack()
    print 'window'
    f.mainloop()
    email = t1.get()
    if not verify(email, client_socket):
        l4 = Label(f, text="wrong Email adreses", foreground="red")
        l4.pack(side=BOTTOM)
        f.mainloop()
        email = t1.get()
        while not verify(email, client_socket):
            f.mainloop()
    global user_email
    user_email = email
    global user_name
    user_name = t2.get()
    window.destroy()


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


def verify(email, client_socket):
    client_socket.sendall("USER " + email + "\r\n")
    log.log("USER " + email, 1)
    data = receive(client_socket, lambda d: "\r\n" not in d)
    return data[:3] == "+OK"


def show_email(email, f, window, client_socket, is_valid):
    print email
    f.pack_forget()
    f2 = Frame(window)
    f2.pack(expand=True, fill=BOTH)
    l1 = Label(f2, text=email)
    l1.pack()
    l2 = Button(f2, text='return', command=f2.quit)
    l2.pack()
    if is_valid:
        f2.mainloop()
    else:
        sender_name = email.split('"')[1]
        sender_email = email[email.find('<') + 1:email.find('>')]
        ansear = tkMessageBox.askokcancel("Question", "This email is from " + sender_email + " named " + sender_name + 'are you sure thet this is his email?')
        if ansear:
            client_socket.sendall("AAAA+" + SENDER_NAME + sender_name + SENDER_NAME + " " + START_EMAIL + sender_email + END_EMAIL + "\r\n")
        else:
            client_socket.sendall("AAAA-" + SENDER_NAME + sender_name + SENDER_NAME + " " + START_EMAIL + sender_email + END_EMAIL + "\r\n")
        if ansear:
            f2.mainloop()
    f2.destroy()
    f.pack()


def update_GUI(emails, client_socket, window, f):
    f.pack_forget()
    f2 = Frame(window)
    f2.pack()
    for text_email in emails[0]:
        text = ''
        for line in text_email.splitlines():
            if 'subject' in line:
                text += line + '\r\n'
        for line in text_email.splitlines():
            if 'from' in line:
                text += line + '\r\n'
        l1 = Button(f2, text=text, command=lambda email2=text_email: show_email(email2, f2, window, client_socket, True))
        l1.pack()

    for text_email in emails[1]:
        text = ''
        for line in text_email.splitlines():
            if 'subject' in line:
                text += line + '\r\n'
        for line in text_email.splitlines():
            if 'from' in line:
                text += line + '\r\n'
        l1 = Button(f2, text=text, command=lambda email2=text_email: show_email(email2, f2, window, client_socket, False))
        l1.pack()

    l2 = Button(f2, text="send email", command=lambda: SMTP())
    l2.pack()
    l3 = Button(f2, text="refrese", command=lambda: update_GUI(get_emails(client_socket), client_socket, window, f2) and f2.quit())
    l3.pack()
    l4 = Button(f2, text='exit', command=f2.quit)
    l4.pack()
    f2.pack()
    f2.mainloop()
    f2.destroy()
    f.pack()
    f.quit()


def inbox_GUI(emails, client_socket):
    print emails
    window = Tk()
    window.title("inbox")
    window.minsize(1500, 1500)
    f = Frame(window)
    f.pack()
    for text_email in emails[0]:
        text = ''
        for line in text_email.splitlines():
            if 'subject' in line:
                text += line + '\r\n'
        for line in text_email.splitlines():
            if 'from' in line:
                text += line + '\r\n'
        l1 = Button(f, text=text, command=lambda email2=text_email: show_email(email2, f, window, client_socket, True))
        l1.pack()

    for text_email in emails[1]:
        text = ''
        for line in text_email.splitlines():
            if 'subject' in line:
                text += line + '\r\n'
        for line in text_email.splitlines():
            if 'from' in line:
                text += line + '\r\n'
        l1 = Button(f, text=text, command=lambda email2=text_email: show_email(email2, f, window, client_socket, False))
        l1.pack()

    l2 = Button(f, text="send email", command=lambda: SMTP())
    l2.pack()
    l3 = Button(f, text="refrese", command=lambda: update_GUI(get_emails(client_socket), client_socket, window, f) and f.quit())
    l3.pack()
    l4 = Button(f, text='exit', command=f.quit)
    l4.pack()
    f.mainloop()
    window.destroy()


def get_emails(client_socket):
    emails = []
    unknown_emails = []
    for num in xrange(1, 10, 1):
        client_socket.sendall("RETR" + str(num) + "\r\n")
        log.log("RETR" + str(num) + "\r\n", 1)
        data = receive(client_socket)
        if data[:3] != "+OK":
            break
        else:
            length = filter(lambda char: char.isdigit(), data)
            print length
            email = receive(client_socket, lambda d: "\r\n." not in d)

            if "?" in data:
                unknown_emails.append(email)
            elif "-" not in data:
                emails.append(email)
    print [emails, unknown_emails]
    return [emails, unknown_emails]


def POP3():
    name = 'adi'
    sender = 'aaa@aaa.com'
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        client_socket.connect((SERVER_IP, POP3_PORT))
        data = receive(client_socket)
        if not data[:3] == "+OK":
            tkMessageBox.showerror("Error", "server didn't connect")
            return
        login(client_socket)
        print 'login'
        client_socket.sendall("STAT\r\n")
        log.log("STAT\r\n", 1)
        data = receive(client_socket)
        if not data[:3] == "+OK":
            tkMessageBox.showerror("Error", "server fail")
            return
        emails = get_emails(client_socket)
        inbox_GUI(emails, client_socket)
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
    """
    window = Tk()
    f = Frame(window)
    f.pack()
    window.title("send_email")
    window.minsize(1000, 1000)
    f = Frame(window)
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
    return (t1, t2, t3, f, window)


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
    client_socket.sendall("MAIL FROM:" + START_EMAIL + sender + END_EMAIL + "\r\n")
    data = receive(client_socket)
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
    data = receive(client_socket)
    if not data[:3] == "220":
        return data
    client_socket.sendall("HELO " + sender[sender.find("@") + 1:] + "\r\n")
    data = receive(client_socket)
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
        client_socket.sendall("RCPT TO:" + START_EMAIL + dest + END_EMAIL + "\r\n")
        data = receive(client_socket)
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
    dest_box, subject_box, text_box, f, window = send_email_GUI()
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
        email += "To:" + START_EMAIL + dest + ">\r\n"
    email += "Date:" + str(datetime.datetime.now()) + "\r\n"
    subject = subject_box.get()
    if subject == "":
        subject = "(no subject)"
    email += "subject:" + subject + "\r\n"
    email += text_box.get(1.0, END)
    email += '\r\n.'
    window.destroy()
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
            time.sleep(0.2)
            client_socket.sendall(m)
    except socket.error as msg:
        print 'error in communication with server - ' + str(msg)
    finally:
        time.sleep(1)
        client_socket.close()


def SMTP():
    """
    the main comm punc. connect to the server and do handshake
    """
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        client_socket.connect((SERVER_IP, SERVER_PORT))
        # send the message
        if not handshake(client_socket, user_email):
            print "unvalid handshake"
            tkMessageBox.showerror("Error", "server didn't connect")
        if not vaild_sender(client_socket, user_email):
            print "unvalid email adress"
            tkMessageBox.showerror("Error", "your email is unvalid")
        email = "From:" + ' "' + user_name + '" ' + START_EMAIL + user_email + END_EMAIL + "\r\n"
        email += send_email(client_socket)

        client_socket.sendall("DATA\r\n")
        data = receive(client_socket)
        if not data[:3] == "354":
            print 'server error'
            tkMessageBox.showerror("Error", "client problem")
        client_socket.sendall(email)
        data = receive(client_socket)
        if not data[:3] == "250":
            print 'unvalid email'
            tkMessageBox.showerror("Error", "email can't send")
        print 'send'
    except socket.error as msg:
        print 'error in communication with server - ' + str(msg)
        tkMessageBox.showerror("Error", "the server cloze comm")
    finally:
        time.sleep(1)
        client_socket.close()


def main():
    """
    this is a ceack func
    """
    pass


if __name__ == '__main__':
    global log
    log = LogFile("client.log", '%(levelname)s:%(message)s')
    POP3()
