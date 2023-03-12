import sys
import socket
import threading
import time
from PyQt6.QtCore import *
from PyQt6.QtGui import *
from PyQt6.QtWidgets import *
import sqlite3
import mysql.connector as mysql
import pandas as pd
import config
import functions as update
#import importlib
import re
import warnings

warnings.filterwarnings('ignore')
ex =''
exPopup = ''

class ChatWindow(QWidget):
    def __init__(self, *args, **kwargs):
        super(ChatWindow, self).__init__(*args, **kwargs)

        self.lbl_w = QLabel(config.friend)
        self.text_edit = QTextEdit()
        self.text_edit.setReadOnly(True)
        self.get_messages()
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
        timer1 = QTimer(self)
        timer1.timeout.connect(self.enterEvent1)
        timer1.start(55)
    def get_messages(self):
        update.get_messages(config.friend)
        for x in config.msgs:
           
            self.text_edit.append(x[0])
            
    def enterEvent1(self):
          if config.msg != '':
             msg = config.msg.split(':')
 
             if msg[0] == 'FRIEND' and msg[2] == config.user and msg[1] == self.lbl_w.text():
                self.text_edit.append(msg[1] + ':' + msg[3])
                update.u_msg('')
             elif msg[0] == 'JOIN':
                self.text_edit.append(msg[1] + ':' + msg[2])
 
                update.u_msg('')

    def send_message(self):

        message = self.line_edit.text()


        if message:
            frnd= self.lbl_w.text() + ':' + self.line_edit.text()
            message = 'FRIEND:{}:{}'.format(config.user, frnd)

            config.alias.send(message.encode('ascii'))
  
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
 
             if msg[0] == 'ROOM' and msg[2] == self.lbl_w.text() and msg[1] != config.user:
                self.text_edit.append(msg[1] + ':' + msg[3])
                update.u_msg('')

    def send_message(self):

        message = self.line_edit.text()
 
        if message:
            frnd= self.lbl_w.text() + ':' + self.line_edit.text()
            message = 'ROOM:{}:{}'.format(config.user, frnd)

            config.alias.send(message.encode('ascii'))
 
            self.text_edit.append(config.user + ':' + self.line_edit.text())
            self.line_edit.clear()

class MainW(QMainWindow):

    def __init__(self, parent=None):
        super(MainW, self).__init__(parent)
        self.setGeometry(10, 35, 700, 450)
        #<<0>>
        layout1 = QHBoxLayout()
        layout2 = QVBoxLayout()
        self.mdi = QMdiArea()
        widget = QWidget()
        self.setCentralWidget(widget)
        self.frnlist = QListWidget(self)
        self.frnlist.resize(90, self.height()/2)
        self.frnlist.currentTextChanged.connect(self.text_changed)
        self.frnlist.itemClicked.connect(self.change_font_color)
        self.romlist = QListWidget(self)
        self.romlist.resize(90, self.height()/2)
        self.romlist.currentTextChanged.connect(self.room_changed)
        self.othlist = QListWidget(self)
        self.othlist.setFixedWidth(90)
        self.mdi.resize(10,self.height()-10)
        layout2.addWidget(self.frnlist)
        layout2.addWidget(self.romlist)
        layout1.addLayout( layout2 )
        layout1.addWidget(self.mdi)
        layout1.addWidget(self.othlist)
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
        
    def change_font_color(self, item):
        item.setForeground(QColor(0, 0, 0))
        
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
 
            if config.user_found == 'NOUSER': 
                update.user_found('')
                self.statusBar.showMessage("Invalid Credentials entered", 7000)
            if config.reg_complete == 'REGCOMPLETE':
                self.statusBar.showMessage("Registration completed", 7000)
                update.u_load(0)
                self.regr.close()
                self.show_login()
                update.u_reg_complete('')
                update.u_sregr('')
                config.alias.close()
            elif config.reg_complete != 'REGCOMPLETE' and config.reg_complete != '':
                self.statusBar.showMessage("Registration can not be completed. Check your entries.", 7000)
                update.u_reg_complete('')
                update.u_sregr('')
                config.alias.close()

            
    def show_login(self):
            self.subl = QMdiSubWindow()
            lblusr = QLabel('UserName', self.subl)
            lblusr.setStyleSheet('QLabel {background-color: transparent; color: black;}')
            lblusr.setGeometry(15, 45, 70, 30)
            self.subl.txtusr = QLineEdit('', self.subl)
            self.subl.txtusr.setGeometry(90, 45, 100, 30)
            lblpwd = QLabel('Password', self.subl)
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

    def setRegr1(self):
            update.u_load(0)
            self.regr.close()
            self.show_login()
            
    def setRegr(self):
            update.u_load(0)
            #self.regr.close()
            #self.show_login()
            
            if self.regr.txtname.text() == '':
                 self.statusBar.showMessage("Full Name is Required", 3000)
                 self.regr.txtname.setStyleSheet('QLineEdit {background-color: #ffe6e6; color: black;}')
                 self.regr.txtname.repaint()
                 time.sleep(1.5)
                 self.regr.txtname.setStyleSheet('QLineEdit {background-color: white; color: black;}')
                 return None
            
            if self.regr.txtmail.text() == '': 
                self.statusBar.showMessage("Email is Required", 3000)
                self.regr.txtmail.setStyleSheet('QLineEdit {background-color: #ffe6e6; color: black;}')
                self.regr.txtmail.repaint()
                time.sleep(1.5)
                self.regr.txtmail.setStyleSheet('QLineEdit {background-color: white; color: black;}')
                return None
            email_regex = re.search("[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}", self.regr.txtmail.text())
            if not email_regex: 
                #print(pwd_regex)
                self.statusBar.showMessage(("Wrong Email Format"), 3000)
                self.regr.txtmail.setStyleSheet('QLineEdit {background-color: #ffe6e6; color: black;}')
                self.regr.txtmail.repaint()
                time.sleep(1.5)
                self.regr.txtmail.setStyleSheet('QLineEdit {background-color: white; color: black;}')
                return None    
            if self.regr.txtusr.text() == '':
                self.statusBar.showMessage("User Name is Required", 3000)
                self.regr.txtusr.setStyleSheet('QLineEdit {background-color: #ffe6e6; color: black;}')
                self.regr.txtusr.repaint()
                time.sleep(1.5)
                self.regr.txtusr.setStyleSheet('QLineEdit {background-color: white; color: black;}')
                return None
            usr_regex = re.search("^(?![-._])(?!.*[_.-]{2})[\w.-]{6,30}(?<![-._])$", self.regr.txtusr.text())
            if not usr_regex: 
                #print(pwd_regex)
                self.statusBar.showMessage(("Wrong User Name Required Format"), 3000)
                self.regr.txtusr.setStyleSheet('QLineEdit {background-color: #ffe6e6; color: black;}')
                self.regr.txtusr.repaint()
                time.sleep(1.5)
                self.regr.txtusr.setStyleSheet('QLineEdit {background-color: white; color: black;}')
                return None     
            pwd_regex = re.search("^.*(?=.{8,})(?=.*\d)(?=.*[a-z])(?=.*[A-Z])(?=.*[@#$%^&+=]).*$", self.regr.txtpwd.text())
            if not pwd_regex: 
                #print(pwd_regex)               
                self.statusBar.showMessage(("Wrong Password Required Format"), 3000)
                self.regr.txtpwd.setStyleSheet('QLineEdit {background-color: #ffe6e6; color: black;}')
                self.regr.txtpwd.repaint()
                time.sleep(1.5)
                self.regr.txtpwd.setStyleSheet('QLineEdit {background-color: white; color: black;}')
                return None    
            if self.regr.txtpwd.text() != self.regr.txtpwd1.text():
                self.statusBar.showMessage("Passwords did not match", 3000)
                self.regr.txtpwd.setStyleSheet('QLineEdit {background-color: #ffe6e6; color: black;}')
                self.regr.txtpwd.repaint()
                self.statusBar.showMessage("Passwords did not match", 3000)
                self.regr.txtpwd1.setStyleSheet('QLineEdit {background-color: #ffe6e6; color: black;}')
                self.regr.txtpwd1.repaint()
                time.sleep(1.5)
                self.regr.txtpwd.setStyleSheet('QLineEdit {background-color: white; color: black;}')
                self.regr.txtpwd1.setStyleSheet('QLineEdit {background-color: white; color: black;}')
                return None
            update.u_regr_data('REGRN:' + self.regr.txtusr.text() + ':' + self.regr.txtmail.text() + ':' + self.regr.txtname.text())
            update.u_pwd(self.regr.txtpwd.text())
            update.u_sregr('X')
            try:   
                    update.u_alias(socket.socket(socket.AF_INET, socket.SOCK_STREAM)) 
                    config.alias.connect(('DESKTOP-IMR6DAM', 50505)) 
                    self.worker = WorkerThread()
                    self.worker.start()

            except Exception as err: 
                    print(str(err))                  
                    pass 
                

    def setReg(self):
            global on_load
            self.regr = QMdiSubWindow()
            lblname = QLabel('FullName', self.regr)
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
            self.regr.pblogin.clicked.connect(self.setRegr1)
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
               update.u_pwd(self.subl.txtpwd.text())              
               update.u_alias('')            
               #print('xtest')
               try:   
                    update.u_alias(socket.socket(socket.AF_INET, socket.SOCK_STREAM)) 
                    config.alias.connect(('DESKTOP-IMR6DAM', 50505)) 
                    self.worker = WorkerThread()
                    self.worker.start()

               except Exception as err: 
                    #print(str(err))                  
                    pass 
            else:
               self.statusBar.showMessage("Error: Enter an alias", 5000)

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
    def on_click_Srch(self):
        
        self.buildSearchPopup()
    def buildSearchPopup(self):
        global exPopup
        name = 'Lock Screen'
        exPopup = searchPopup(name)
        #print('test1')
        #self.exPopup.setGeometry(self.pos().x()+50, self.pos().y()+75, 300, 225)
        exPopup.move(self.pos().x()+75, self.pos().y()+75)
        exPopup.setFixedSize(350, 400)
        exPopup.show()
                  
    def manage_me(self, q):
        pass
        
    def manage_friends(self, q):
        #print('test')
        if q.text() == "Add":
            self.sub_add_friend = QMdiSubWindow()
            lbl1a =  QLabel('Username', self.sub_add_friend)
            lbl1a.setGeometry(25, 50, 60, 25)
            #lbl1a.setStyleSheet('QLabel {background-color: transparent; color: black;}')
            self.sub_add_friend.txtusr = QLineEdit('', self.sub_add_friend) 
            self.sub_add_friend.txtusr.setGeometry(95, 50, 150, 25)
            self.sub_add_friend.txtusr.textChanged.connect(self.on_text_changed)
            self.sub_add_friend.lbl1b =  QLabel(' ', self.sub_add_friend)
            self.sub_add_friend.lbl1b.setGeometry(70, 125, 180, 25)
            new_font = QFont("Arial Black", 14)
            self.sub_add_friend.lbl1b.setFont(new_font)
            pbSrch = QPushButton('...', self.sub_add_friend)
            pbSrch.setGeometry(250, 50, 30, 25)
            pbSrch.clicked.connect(self.on_click_Srch)
            self.sub_add_friend.pbSave = QPushButton('Add',  self.sub_add_friend)
            self.sub_add_friend.pbSave.setGeometry(205, 260, 75, 25)
            self.sub_add_friend.pbSave.setEnabled(False)
            pbCanc = QPushButton('Cancel', self.sub_add_friend)
            pbCanc.setGeometry(290, 260, 75, 25)
            pbCanc.clicked.connect(self.on_click_canc)
            self.sub_add_friend.pbSave.clicked.connect(self.on_click_usr_save)
            self.sub_add_friend.setGeometry(25, 25, 400, 300)
            self.mdi.addSubWindow(self.sub_add_friend)
            self.sub_add_friend.show()
    def on_text_changed(self):        
         self.sub_add_friend.pbSave.setEnabled(bool(self.sub_add_friend.txtusr.text())) 
            
    def on_click_usr_save(self):
        pass
    def on_click_canc(self):
        self.sub_add_friend.close()
        
    def manage_rooms(self, q):
        pass    
    def onClick_conn(self):
        pass
        
    def onClick_dcon(self):
        pass
class searchPopup(QMainWindow):
    def __init__(self, name):
        super().__init__()        
        self.name = name
        #self.setGeometry(100, 100, 300, 350)
        self.setWindowFlags(Qt.WindowType.Window | Qt.WindowType.CustomizeWindowHint | Qt.WindowType.WindowStaysOnTopHint)
        self.initUI()

    def initUI(self):
        
        lblName = QLabel('Search Existing Users', self)
        lblName.setStyleSheet('QLabel {background-color: transparent; color: black;}')
        lblName.setGeometry(5, 5, 200, 30)
        lblusr =  QLabel('Username', self)
        lblusr.setStyleSheet('QLabel {background-color: transparent; color: black;}')
        lblusr.setGeometry(25, 50, 100, 30) 
        self.txtusr = QLineEdit('', self) 
        self.txtusr.setGeometry(90, 50, 150, 30) 
        pbusr =  QPushButton('', self)
        pbusr.setIcon(QIcon('magnifier-zoom.png'))
        pbusr.setGeometry(243, 50, 40, 30)
        pbusr.clicked.connect(self.onClick_pbusr)
        self.createTable()
        
        pb4 = QPushButton('Ok', self)
        pb4.setGeometry(140, 365, 70, 25)
        
        #pb4.clicked.connect(self.onClick_pb4)
        pb5 = QPushButton('Cancel', self)
        pb5.setGeometry(215, 365, 70, 25)
        pb5.clicked.connect(self.onClick_pb5)
    def onClick_pb5(self):
        self.close()
    def onClick_pbusr(self):
        if self.txtusr.text() != '':
           #print(self.txtusr.text()) 
           config.alias.send(('TBUSR:' + self.txtusr.text()).encode('ascii'))
   
    def createTable(self):
          self.tableWidget = QTableWidget(self)
          self.tableWidget.viewport().installEventFilter(self)
          #self.tableWidget.installEventFilter(self)
          #self.tableWidget.setEditTriggers(QTreeView.NoEditTriggers) 
          self.tableWidget.setRowCount(24)
          self.tableWidget.setColumnCount(2)
          self.tableWidget.setFixedSize(280, 270)
          self.tableWidget.move(25, 85)
          self.tableWidget.clear()
          self.tableWidget.setHorizontalHeaderLabels(['User', 'Name'])
          self.tableWidget.setSelectionMode(QAbstractItemView.SelectionMode.SingleSelection)
          self.tableWidget.SelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
          stylesheet = "::section{Background-color:rgb(179, 179, 179);color: white; bor  der-radius:14px;}"
          self.tableWidget.horizontalHeader().setStyleSheet(stylesheet)
          self.tableWidget.setStyleSheet('QTableWidget {background-color: white; color: black;}')
          delegate = Delegate(self.tableWidget)
          self.tableWidget.setItemDelegate(delegate) 
    def eventFilter(self, source, event):
          global sel_row
          global sel_row_clk, ex
          #if self.tableWidget.selectedIndexes() != []:
            
          if event.type() == QEvent.Type.MouseButtonDblClick:
                #if event.button() == QtCore.Qt.LeftButton:
            row = self.tableWidget.currentRow()
            col = self.tableWidget.currentColumn()
            if self.tableWidget.item(row, col) is not None:
                #print(str(row) + " " + str(col) + " " + self.tableWidget.item(row, col).text())
                sel_row = row + 1
                ex.sub_add_friend.txtusr.setText(self.tableWidget.item(row, col).text())
                ex.sub_add_friend.lbl1b.setText(self.tableWidget.item(row, 0).text() + ' - ' + self.tableWidget.item(row, 1).text())
                self.close()
              
          if event.type() == QEvent.Type.MouseButtonRelease:
             row = self.tableWidget.currentRow()
             col = self.tableWidget.currentColumn()
             if self.tableWidget.item(row, col) is not None:
                sel_row_clk = row + 1
                #print(sel_row_clk)
          return QObject.event(source, event) 
class Delegate(QStyledItemDelegate):
    def createEditor(self, parent, option, index):
        if index.data() == "100":
            return super(Delegate, self).createEditor(parent, option, index)
                            
class WorkerThread(QThread):
   def run(self):
      global ex, exPopup
      while True:
            try:
             
                #print('xtest1')  
                message = config.alias.recv(6000).decode('ascii')
                #print(message)
                if config.sregr == '':
                
                   if message == 'USER':
                  
                     msg = config.user 
                  
                     config.alias.send(msg.encode('ascii'))
                     message = ''
                  
                   elif message == 'OK': 
                      
                        config.alias.send(config.pwd)                                  
                      
                   elif message == 'OKUSER': 
                        try:
                          #print('xtest2')
                          update.u_sqdb()  
                          #update.user_found(message)                        
                          update.get_fiends(config.user)
                          update.get_rooms(config.user)
                          update.u_load(1)
                          try:
                              ex.bar.setEnabled(True)
                              ex.toolbar1.setEnabled(True) 
                          
                          
                              if len(config.friends)!=0:
                                   for x in config.friends:
                                     ex.frnlist.addItems(x)
                              #update.user_found('')
                              ex.lbl_con.setText('Online')
                          
                              ex.subl.close() 
                          except Exception as e:
                              #print(str(e)) 
                              pass  
                          
                          if len(config.rooms)!=0:
                             for x in config.rooms:
                                 ex.romlist.addItems(x)
                          mww = 'MSGSSYNC:'+ config.user
                          config.alias.send(mww.encode('ascii'))
                        except Exception as e:
                            #print(str(e)) 
                            pass 
                          
                   elif message == 'NOUSER': 
                     update.user_found(message)
                     #ex.statusBar.showMessage("Invalid Credentials entered", 7000) 
                     #update.user_found('')
                             
                   else:
                     #print(message[0:5])
                     if message[0:5] != 'TBUSR':  
                         update.u_msg(message)
                         #print(config.msg1)
                         if config.msg1 != '':
                           xx = config.msg1.split(':')
                           #print(xx)
                    
                           #print(xx[2] + '  --  ' + config.user) 
                           if xx[2] == config.user:
                              vv = 'MSGS:' + str(xx[4]) + ':DELV'
                              config.alias.send(vv.encode('ascii'))
                           update.u_msg1('')
                           if xx[0] == 'FRIEND':
                             y = 0
                             #print('test1')
                             #print(config.friends)
                             for x in config.friends:
                               #print(x)
                               #print(ex.frnlist.item(y).text())
                               if ex.frnlist.item(y).text() == xx[1]:
                                   ex.frnlist.item(y).setForeground(QColor(255, 0, 0))
                               y += 1
                     else:
                          #print('yes')
                          try:
                              msv_vv = message.split('::')
                              msv_vv1 = msv_vv[1].split(':')
                              y = 0
                              exPopup.tableWidget.clear()
                              exPopup.tableWidget.setHorizontalHeaderLabels(['User', 'Name'])
                              for ind in msv_vv1: 
                                  ind1 = ind.split('*')                                
                                  v =  ind1[0]
                                  #print(v)
                                  it = QTableWidgetItem(v)
                                  exPopup.tableWidget.setItem(y, 0, it)
                                  vv =  ind1[1]
                                  #print(vv)
                                  it = QTableWidgetItem(vv)
                                  exPopup.tableWidget.setItem(y, 1, it)
                                  #exPopup.tableWidget.repaint()
                                  y += 1
                          except Exception as e:
                                  #print(str(e))
                                  pass
                                                
                else:
                    #print('test')
                    if message == 'USER':
                        #print('xtest')
                        #update.u_sregr('')
                        config.alias.send('REGISTER'.encode('ascii'))
                    elif message == 'OK':  
                        #print('xtest1')
                        #print(config.regr_data) 
                                           
                        config.alias.send(config.regr_data.encode('ascii')) 
                    elif message == 'OKPWD':  
                        #print('xtest2')                    
                        config.alias.send(config.pwd)    
                    elif message == 'REGCOMPLETE':
                        #print('xtest3')
                        cc = config.regr_data.split(':')
                        try:
                           conn = sqlite3.connect('msgDb_' + cc[1] + '.db')
                           c = conn.cursor()
                           table_name = 'msgs'
                           sql = 'create table if not exists ' + table_name + ' (id integer, msgfr varchar, username varchar, recvr varchar, msg char, status char, datesent datetime)'
                           c.execute(sql)
                        
                           table_name = 'tbfriends'
                           sql = 'create table if not exists ' + table_name + ' (id integer, username char, friends char)'
                           c.execute(sql)
                           table_name = 'tbrooms'
                           sql = 'create table if not exists ' + table_name + ' (id integer, room char, username char, friends char)'
                           c.execute(sql)
                        except Exception as e:
                            #print(e)
                            pass   
                        
                        update.u_reg_complete(message)
                    else:
                        #print('xtest4')
                        update.u_reg_complete(message)              
                  
            except Exception as err:
               #print(str(err))
               pass
     # else:


def main():
    global ex
    app = QApplication(sys.argv)
    ex = MainW()
    ex.show()
    sys.exit(app.exec())

if __name__ == '__main__':
    main()
    
