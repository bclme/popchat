import socket
import threading
import time
import pandas as pd
import config
import importlib
import functions as update
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
        importlib.reload(socket)
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
       try:
           
         server.bind(('0.0.0.0', 50505))
         server.listen()
         
       except Exception as e:
          pass#print(str(e))

       msg = 'Server is listening...'
 
       receive()

def receive():
    global msg, alias, server
    while True:
       
       try:
           
          alias, address = server.accept()
          

  
          
          alias.send('USER'.encode('ascii'))
          
          user = alias.recv(5000).decode('ascii')
          #print('vtest')
          #print(user)
          if user == 'REGISTER':
             #print('test1') 
             time.sleep(0.06 )
             alias.send('OK'.encode('ascii'))
             regr = alias.recv(5000).decode('ascii')
             #print(regr)
             regr = regr.split(':') 
             time.sleep(0.06 )
             alias.send('OKPWD'.encode('ascii'))
             pwd = alias.recv(5000)
             #print(pwd)
             update.u_pwd(pwd)
             update.user_regr(regr, config.pwd)
             #print(config.regr_ok)
             if config.regr_ok == 'OK':
                 alias.send('REGCOMPLETE'.encode('ascii'))
             else:
                 alias.send(config.regr_ok.encode('ascii'))
          #print('xtest3')
          
          else:
            #user1 = user.split(' ~~ ')


            #print('vtest1')
            time.sleep(0.06 )
            alias.send('OK'.encode('ascii'))
          
            pwd = alias.recv(5000) 
                   
            update.u_pwd(pwd)
          
            #print(pwd)
            update.user_login(user, config.pwd)
          
            #print(config.login_ok)
            if config.login_ok == 'OK':
              
                alias.send('OKUSER'.encode('ascii'))
                users.append(user)
                aliases.append(alias)
                msg = "Connected with {}".format(str(address))             
                time.sleep(0.06 )
          
                msg = "Alias is {}".format(user)
          
                broadcast("JOIN:{}: joined!".format(user, user).encode('ascii'))
                #alias.send('JOIN:{}:Connected to server!'.format(user).encode('ascii'))


                thread = threading.Thread(target=handle, args=(alias,))
                thread.start()             
            elif config.login_ok == 'NOUSER':
                alias.send('NOUSER'.encode('ascii'))
                time.sleep(0.06 )
                alias.close() 
                #thread = threading.Thread(target=handle, args=(alias,))
                #thread.start()
            #print('test')
            #try:
              # msgssync = alias.recv(5000).decode('ascii')
              #print(msgssync)
              #if  msgssync == 'MSGSSYNC':
              #  update.get_sent_msgs(user)
              #  if len(config.msg_sent) != 0:
                    #print('test4')
              #      for x in config.msg_sent.index:
              #             alias.send(x.encode('ascii'))
            #except Exception as err:
            #     print(str(err))
            #     pass
       except Exception as err:
          #print(str(err))
          pass

def broadcast(message):

    for alias in aliases:
        try:
          #print('test')  
          alias.send(message)
        except:
          alias.close()

def handle(alias):
    while True:
        #print('test5')
        try:
            message = alias.recv(1024)
            msgx = message.decode('ascii')
            #print(msgx)
            vv = msgx.split(':')
            #print(vv[0])
            if vv[0] == 'MSGS':
                update.update_message(vv)
            elif vv[0] == 'MSGSSYNC':
                
                update.get_sent_msgs(vv[1])
                if len(config.msg_sent) != 0:
                  #print('test1')
                  for x in config.msg_sent:
                         alias.send(x[0].encode('ascii'))
                         #print(x[0])
            elif vv[0] == 'TBUSR':
                #print(vv[0])
                update.search_users(vv[1])
                if config.tbusr != '':
                    
                   alias.send(('TBUSR:' +config.tbusr).encode('ascii'))
            else:    
                update.save_message(msgx)
                message = msgx + ':' + str(config.msg_id) 
                #print(message)
                broadcast(message.encode('ascii'))
        except Exception as err:
            #print(str(err))
            pass
            
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
