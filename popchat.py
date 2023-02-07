import sys
import socket
import threading
import time
from PyQt6.QtCore import *
from PyQt6.QtGui import *
from PyQt6.QtWidgets import *
import mysql.connector as mysql
import pandas as pd
import config
import functions as update
import warnings
warnings.filterwarnings('ignore')

class MdiSubWindow(QMdiSubWindow):

    def enterEvent(self, e):

        wtitle= self.windowTitle()

class ChatWindow(QWidget):
    def __init__(self, *args, **kwargs):
        super(ChatWindow, self).__init__(*args, **kwargs)

        self.lbl_w = QLabel(config.friend)
        self.text_edit = QTextEdit()
        self.text_edit.setReadOnly(True)
        self.line_edit = QLineEdit()
        self.line_edit.setPlaceholderText("Enter message here")
        self.send_button = QPushButton("Send")
        self.send_button.clicked.connect(self.send_message)
        layout = QVBoxLayout()
        layout.addWidget(self.lbl_w)
        layout.addWidget(self.text_edit)
        h_layout = QHBoxLayout()
        h_layout.addWidget(self.line_edit)
        h_layout.addWidget(self.send_button)
        layout.addLayout(h_layout)
        self.setLayout(layout)
        self.thread()
    def enterEvent(self, e):
          if config.msg != '':
             msg = config.msg.split(':')
             print(msg)
             if msg[0] == 'FRIEND' and msg[2] == config.user and msg[1] == self.lbl_w.text():
                self.text_edit.append(msg[1] + ':' + msg[3])
                update.u_msg('')
             elif msg[0] == 'JOIN':
                self.text_edit.append(msg[1] + ':' + msg[2])
                print(config.user)
                update.u_msg('')
             
    def send_message(self):

        message = self.line_edit.text()
        #print(str(alias) + ' - ' + str(user))

        if message:
            frnd= self.lbl_w.text() + ':' + self.line_edit.text()
            message = 'FRIEND:{}:{}'.format(config.user, frnd)

            config.alias.send(message.encode('ascii'))
            #self.line_edit.setText(message)
            self.text_edit.append(config.user + ':' + self.line_edit.text())
            self.line_edit.clear()

class ChatWindow_Room(QWidget):
    def __init__(self, *args, **kwargs):
        super(ChatWindow_Room, self).__init__(*args, **kwargs)

        self.lbl_w = QLabel(config.room)
        self.text_edit = QTextEdit()
        self.text_edit.setReadOnly(True)
        self.line_edit = QLineEdit()
        self.line_edit.setPlaceholderText("Enter message here")
        self.send_button = QPushButton("Send")
        self.send_button.clicked.connect(self.send_message)
        layout = QVBoxLayout()
        layout.addWidget(self.lbl_w)
        layout.addWidget(self.text_edit)
        h_layout = QHBoxLayout()
        h_layout.addWidget(self.line_edit)
        h_layout.addWidget(self.send_button)
        layout.addLayout(h_layout)
        self.setLayout(layout)
        self.thread()
    def enterEvent(self, e):
          if config.msg != '':
             msg = config.msg.split(':')
             print(msg)
             if msg[0] == 'ROOM' and msg[2] == self.lbl_w.text() and msg[1] != config.user:
                self.text_edit.append(msg[1] + ':' + msg[3])
                update.u_msg('')

    def send_message(self):

        message = self.line_edit.text()
        #print(str(alias) + ' - ' + str(user))

        if message:
            frnd= self.lbl_w.text() + ':' + self.line_edit.text()
            message = 'ROOM:{}:{}'.format(config.user, frnd)

            config.alias.send(message.encode('ascii'))
            #self.line_edit.setText(message)
            self.text_edit.append(config.user + ':' + self.line_edit.text())
            self.line_edit.clear()

class MainW(QMainWindow):

    def __init__(self, parent=None):
        super(MainW, self).__init__(parent)
        self.setGeometry(10, 35, 600, 450)
        #<<0>>
        layout1 = QHBoxLayout()
        layout2 = QVBoxLayout()
        self.mdi = QMdiArea()
        widget = QWidget()
        self.setCentralWidget(widget)
        self.frnlist = QListWidget(self)
        self.frnlist.resize(90, self.height()/2)
        self.frnlist.currentTextChanged.connect(self.text_changed)
        self.romlist = QListWidget(self)
        self.romlist.resize(90, self.height()/2)
        self.romlist.currentTextChanged.connect(self.room_changed)
        self.mdi.resize(10,self.height()-10)
        layout2.addWidget(self.frnlist)
        layout2.addWidget(self.romlist)
        layout1.addLayout( layout2 )
        layout1.addWidget(self.mdi)
        widget = QWidget()
        widget.setLayout(layout1)
        self.setCentralWidget(widget)
        self.bar = self.menuBar()
        nMe = self.bar.addMenu("My Info")
        nMe.addAction("Dashboard")
        nMe.addAction("Profile")
        nMe.addAction("Timeline")
        nMe.addAction("Cluster")
        nMe.addSeparator()
        nMe.addAction("Logout")
        nMe.triggered[QAction].connect(self.manage_me)
        nFriends = self.bar.addMenu("Friends")
        nFriends.addAction("Add")
        nFriends.addAction("Display")
        nFriends.addAction("Update")
        nFriends.triggered[QAction].connect(self.manage_friends)
        nRooms = self.bar.addMenu("Rooms")
        nRooms.addAction("Add")
        nRooms.addAction("Display")
        nRooms.addAction("Update")
        nRooms.triggered[QAction].connect(self.manage_rooms)
        nWins = self.bar.addMenu("Chats")
        nWins.addAction("Tile")
        nWins.addAction("Cascade")
        nWins.triggered[QAction].connect(self.wclick)
        nSyst = self.bar.addMenu("System")
        nSyst.addAction("Preferences")
        nSyst.addAction("Settings")
        nSyst.addAction("About Popchat")
        nSyst.addSeparator()
        nSyst.addAction("Quit")
        nSyst.triggered[QAction].connect(self.about)
        self.statusBar = QStatusBar()
        self.setStatusBar(self.statusBar)
        self.statusBar.setFixedHeight(30)
        self.statusBar.showMessage("Ready", 5000)
        timer = QTimer(self)
        timer.timeout.connect(self.showTime)
        timer.start(1000)
        self.lbl_con = QLabel()
        self.statusBar.addPermanentWidget(self.lbl_con)
        self.lbl_con.move(30, 40)
        self.lbl_con.setFixedHeight(30)
        self.lbl_con.setText('Offline')
        self.lbl_tmr = QLabel()
        self.statusBar.addPermanentWidget(self.lbl_tmr)
        self.lbl_tmr.move(60, 40)
        self.lbl_tmr.setFixedHeight(30)
        self.toolbar1 = QToolBar("Connetion")
        self.toolbar1.setIconSize(QSize(30,30))
        self.addToolBar(self.toolbar1)
        conn_action = QAction(QIcon("network-status.png"), "&Connect", self)
        conn_action.setStatusTip("Connect")
        conn_action.triggered.connect(self.onClick_conn)
        conn_action.setCheckable(False)
        conn_action.setShortcut(QKeySequence("Ctrl+m"))
        self.toolbar1.addAction(conn_action)
        dcon_action = QAction(QIcon("network-status-offline.png"), "&Disonnect", self)
        dcon_action.setStatusTip("Disonnect")
        dcon_action.triggered.connect(self.onClick_dcon)
        dcon_action.setCheckable(False)
        dcon_action.setShortcut(QKeySequence("Ctrl+n"))
        self.toolbar1.addAction(dcon_action)
        self.thread()
        self.bar.setEnabled(False)
        self.toolbar1.setEnabled(False)
        update.u_start(0)

        self.setWindowTitle("Pop Chat")

    def showTime(self):
            if config.on_start == 0:
                self.show_login()
                update.u_start(1)
            current_time = QTime.currentTime()

            update.u_time(current_time.toString('hh:mm:ss'))
            self.lbl_tmr.setText(config.label_time)
            if config.regr == 1:
                update.u_regr(0)
                self.setReg()

    def show_login(self):

            self.subl= QMdiSubWindow()
            lblusr =  QLabel('UserName', self.subl)
            lblusr.setStyleSheet('QLabel {background-color: transparent; color: black;}')
            lblusr.setGeometry(15, 45, 70, 30)
            self.subl.txtusr = QLineEdit('', self.subl)
            self.subl.txtusr.setGeometry(90, 45, 100, 30)
            lblpwd =  QLabel('Password', self.subl)
            lblpwd.setStyleSheet('QLabel {background-color: transparent; color: black;}')
            lblpwd.setGeometry(15, 90, 70, 30)
            self.subl.txtpwd = QLineEdit('', self.subl)
            self.subl.txtusr.setPlaceholderText("Enter Username Here")
            self.subl.txtpwd.setPlaceholderText("Enter Password Here")
            self.subl.txtpwd.setGeometry(90, 90, 100, 30)
            self.subl.txtpwd.setEchoMode(QLineEdit.EchoMode.Password)
            self.subl.pblogin = QPushButton('Login', self.subl)
            self.subl.pblogin.setGeometry(70, 160, 50, 20)
            self.subl.pblogin.clicked.connect(self.setLogin)
            self.subl.pbReg = QPushButton('Register', self.subl)
            self.subl.pbReg.setGeometry(125, 160, 50, 20)
            self.subl.pbReg.clicked.connect(self.showReg)
            pbcanc = QPushButton('Cancel', self.subl)
            pbcanc.setGeometry(180, 160 , 50, 20)
            self.subl.setGeometry(65, 65,250, 200)
            self.subl.setWindowFlag(Qt.WindowType.FramelessWindowHint)
            self.mdi.addSubWindow(self.subl)

            self.subl.show()

    def showReg(self):

            self.subl.close()
            update.u_regr(1)

    def setRegr(self):
            update.u_load(0)
            self.regr.close()
            self.show_login()

    def setReg(self):
            global on_load
            self.regr= QMdiSubWindow()
            lblname =  QLabel('FullName', self.regr)
            lblname.setStyleSheet('QLabel {background-color: transparent; color: black;}')
            lblname.setGeometry(15, 45, 70, 30)
            self.regr.txtname = QLineEdit('', self.regr)
            self.regr.txtname.setGeometry(90, 45, 150, 30)
            self.regr.txtname.setPlaceholderText("Enter Fullname Here")
            lblmail =  QLabel('Email', self.regr)
            lblmail.setStyleSheet('QLabel {background-color: transparent; color: black;}')
            lblmail.setGeometry(15, 90, 70, 30)
            self.regr.txtmail = QLineEdit('', self.regr)
            self.regr.txtmail.setGeometry(90, 90, 150, 30)
            self.regr.txtmail.setPlaceholderText("Enter Email Here")
            lblusr =  QLabel('UserName', self.regr)
            lblusr.setStyleSheet('QLabel {background-color: transparent; color: black;}')
            lblusr.setGeometry(15, 135, 70, 30)
            self.regr.txtusr = QLineEdit('', self.regr)
            self.regr.txtusr.setGeometry(90, 135, 100, 30)
            lblpwd =  QLabel('Password', self.regr)
            lblpwd.setStyleSheet('QLabel {background-color: transparent; color: black;}')
            lblpwd.setGeometry(15, 180, 70, 30)
            self.regr.txtpwd = QLineEdit('', self.regr)
            self.regr.txtusr.setPlaceholderText("Enter Username Here")
            self.regr.txtpwd.setPlaceholderText("Enter Password Here")
            self.regr.txtpwd.setGeometry(90, 180, 100, 30)
            self.regr.txtpwd.setEchoMode(QLineEdit.EchoMode.Password)
            lblpwd1 =  QLabel('Reenter Pwd', self.regr)
            lblpwd1.setStyleSheet('QLabel {background-color: transparent; color: black;}')
            lblpwd1.setGeometry(15, 225, 70, 30)
            self.regr.txtpwd1 = QLineEdit('', self.regr)
            self.regr.txtpwd1.setPlaceholderText("ReEnter Password Here")
            self.regr.txtpwd1.setGeometry(90, 225, 100, 30)
            self.regr.txtpwd1.setEchoMode(QLineEdit.EchoMode.Password)
            self.regr.pblogin = QPushButton('Login', self.regr)
            self.regr.pblogin.setGeometry(70, 270, 50, 20)
            self.regr.pblogin.clicked.connect(self.setRegr)
            self.regr.pbReg = QPushButton('Register', self.regr)
            self.regr.pbReg.setGeometry(125, 270, 50, 20)
            self.regr.pbReg.clicked.connect(self.setRegr)
            pbcanc = QPushButton('Cancel', self.regr)
            pbcanc.setGeometry(180, 270 , 50, 20)
            update.u_load(1)
            self.regr.setGeometry(65, 65,280, 360)
            self.regr.setWindowFlag(Qt.WindowType.FramelessWindowHint)
            self.mdi.addSubWindow(self.regr)
            self.regr.show()
    def setLogin(self):
            if self.subl.txtusr.text() != '':
               user=self.subl.txtusr.text()
               update.u_user(user)
               try:
                    update.u_alias(socket.socket(socket.AF_INET, socket.SOCK_STREAM))
                    config.alias.connect(('DESKTOP-IMR6DAM', 50505))
                    self.lbl_con.setText('Online')
                    self.worker = WorkerThread()
                    self.worker.start()
                    self.bar.setEnabled(True)
                    self.toolbar1.setEnabled(True)
                    update.u_load(1)

                    update.get_fiends(self.subl.txtusr.text())
                    if len(config.friends)!=0:
                        for x in config.friends:
                          self.frnlist.addItems(x)
                    update.get_rooms(self.subl.txtusr.text())
                    if len(config.rooms)!=0:
                       for x in config.rooms:
                         self.romlist.addItems(x)
                    self.subl.close()

               except Exception as err:
                    self.statusBar.showMessage(str(err), 5000)
            else:
               self.statusBar.showMessage("Error: Enter a alias", 5000)

    def text_changed(self, s):
          update.u_friend(s)
          self.sub = QMdiSubWindow()
          self.sub.setWidget(ChatWindow())
          self.sub.setGeometry(5, 5, 250, 300)
          self.sub.setWindowTitle('friend:'+s)
          self.mdi.addSubWindow(self.sub)
          self.sub.show()

    def wclick(self, q):
            if q.text() == "Cascade":
                self.mdi.cascadeSubWindows()
            if q.text() == "Tile":
                self.mdi.tileSubWindows()
    def about(self, s):
            aboutm = QMessageBox()
            aboutm.setIcon(QMessageBox.Icon.Information)
            aboutm.setWindowTitle('Software Information')
            aboutm.setStyleSheet('QLabel {background-color: transparent; color: black;}')
            aboutm.setText("Title: Popchat \n Version: 1.00 \n Release Date: June 6, 2022")
            aboutm.setStandardButtons(QMessageBox.StandardButton.Ok)
            aboutm = aboutm.exec()

    def room_changed(self, s):
          update.u_room(s)
          self.sub1 = QMdiSubWindow()
          self.sub1.setWidget(ChatWindow_Room())
          self.sub1.setGeometry(5, 5, 250, 300)
          self.sub1.setWindowTitle('room:'+s)
          self.mdi.addSubWindow(self.sub1)
          self.sub1.show()
    def manage_me(self, q):
        pass
    def manage_friends(self, q):
        pass
    def manage_rooms(self, q):
        pass
    def onClick_conn(self):
        pass
    def onClick_dcon(self):
        pass

class WorkerThread(QThread):
   def run(self):
      while True:
            try:
                message = config.alias.recv(1024).decode('ascii')
                print('recieved by: ' + config.user + '--' + message)
                if message == 'USER':
                  config.alias.send(config.user.encode('ascii'))
                  message = ''
                else:
                  update.u_msg(message)
            except:
               pass
     # else:


def main():
   app = QApplication(sys.argv)
   ex = MainW()
   ex.show()
   sys.exit(app.exec())
if __name__ == '__main__':
   main()
