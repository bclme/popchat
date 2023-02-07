import socket
import threading
import time
import pandas as pd
#import multiprocessing as mp
import sys
from PyQt6.QtCore import *
from PyQt6.QtGui import *
from PyQt6.QtWidgets import *
import mysql.connector as mysql
import warnings
warnings.filterwarnings('ignore')

msg = ''
server = ''

aliases = []
users = []

alias = ''
class Window(QMainWindow):

    def __init__(self):
        super(Window, self).__init__()
        self.initUI()

    def initUI(self):

        widget = QWidget()
        self.setCentralWidget(widget)
        self.nick_edit = QLineEdit(self)
        self.nick_edit.setPlaceholderText("Enter your alias here")
        self.nick_edit.setVisible(True)
        self.conn_button = QPushButton("Connect")

        self.conn_button.setFixedWidth(60)
        self.conn_button.clicked.connect(self.connect_exec)
        self.dconn_button = QPushButton("DisConnect")

        self.dconn_button.setFixedWidth(70)
        self.dconn_button.clicked.connect(self.dconnect_exec)
        self.dconn_button.setEnabled(False)
        self.text_edit = QTextEdit(self)
        self.text_edit.setReadOnly(True)

        self.line_edit = QLineEdit()
        self.line_edit.setPlaceholderText("Enter message here")
        self.send_button = QPushButton("Send")
        self.send_button.clicked.connect(self.send_message)
        h_layout_conn = QHBoxLayout()

        h_layout_conn.addWidget(self.nick_edit)
        h_layout_conn.addWidget(self.conn_button)
        h_layout_conn.addWidget(self.dconn_button)

        layout = QVBoxLayout()
        layout.addLayout(h_layout_conn)
        layout.addWidget(self.text_edit)

        h_layout = QHBoxLayout()
        h_layout.addWidget(self.line_edit)
        h_layout.addWidget(self.send_button)
        layout.addLayout(h_layout)

        widget = QWidget()
        widget.setLayout(layout)
        self.setCentralWidget(widget)
        timer = QTimer(self)
        timer.timeout.connect(self.showtext)
        timer.start(50)
        self.thread()
        combo='Server'
        self.setGeometry(25, 45, 350, 400)
        self.setWindowTitle('Pop Chat')
        self.show()

    def showtext(self):
        global msg
        if msg != '' and msg != 'USER':
           self.text_edit.append(msg)
           msg = ''
        elif msg == 'USER':
             msg = ''

    def connect_exec(self):
        global msg
        if self.nick_edit.text() != '':
            self.worker = WorkerThread()
            self.worker.start()            

    def dconnect_exec(self):
        pass

    def send_message(self):
        pass

class WorkerThread(QThread):
   def run(self):
       global  msg, server
       server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
       server.bind(('0.0.0.0', 50505))
       server.listen()
       msg = 'Server is listening...'
       print(msg)
       receive()

def receive():
    global msg, alias
    while True:

        alias, address = server.accept()

        msg = "Connected with {}".format(str(address))
        
       # print(msg)
        time.sleep(0.06 )
        alias.send('USER'.encode('ascii'))
        user = alias.recv(1024).decode('ascii')
        users.append(user)
        aliases.append(alias)



        msg = "Alias is {}".format(user)
        
        broadcast("JOIN:{}: joined!".format(user, user).encode('ascii'))
        #alias.send('JOIN:{}:Connected to server!'.format(user).encode('ascii'))


        thread = threading.Thread(target=handle, args=(alias,))
        thread.start()

def broadcast(message):
 
    for alias in aliases:
        alias.send(message)

def handle(alias):
    while True:
        try:
            message = alias.recv(1024)
            message1 = message.decode('ascii') 
            print('Server:' + message1) 
            broadcast(message) 
        except Exception as err:
            print(err)
def msg_room(user, room, message):
   pass

def msg_user(user, message):
   pass

def main():
   app = QApplication(sys.argv)
   ex = Window()
   ex.show()
   sys.exit(app.exec())

if __name__ == '__main__':
   main()
