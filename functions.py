import config
import pandas as pd
import mysql.connector as mysql
import sqlite3
from PyQt6.QtCore import  QDate, QTime

from Crypto.PublicKey import RSA
from Crypto.Cipher import PKCS1_OAEP, AES

config.salt = b'4\xa8y\x8e\xca\xfb\x7f\x8e\xd5\x97v\x14\xc7[Z\xd0'

config.pubKey = x = b'-----BEGIN PUBLIC KEY-----\nMIGfMA0GCSqGSIb3DQEBAQUAA4GNADCBiQKBgQCkw+2UyXgxMG0qetT9q9Oflx9A\n3KUnnJ+9F0q4TJgnpD0DP9F53yU8AmBca49cPT/4Hc7s60yGk8f8m0+wE8hEOXcL\nXMulYx+JeJcWdJhUW9pJWDFWFeC0lBPLihBHOkAHi8aCZ1m5ccSmTzQUDeLIYFQs\nZ2vkgVwxulOYRBx+UQIDAQAB\n-----END PUBLIC KEY-----'


key = RSA.import_key(config.pubKey)
    
cipher = PKCS1_OAEP.new(key)

    
def u_time(arg1):
    config.label_time = arg1

def u_sregr(arg1):
    config.sregr = arg1
def u_regr_data(arg1):
    config.regr_data = arg1
    
def u_reg_complete(arg1):
    config.reg_complete = arg1     
def u_regr(arg1):
    config.regr = arg1
    
def u_sqdb():
    if config.sqdb == 'msgDb':
       config.sqdb = config.sqdb + '_' +  config.user + '.db'
    #print(config.sqdb)    
def u_start(arg1):
    config.on_start = arg1

def u_load(arg1):
    config.on_load = arg1

def u_user(arg1):
    config.user = arg1
    #u_sqdb()
    #print(config.sqdb)
def u_pwd(argv1):
    global key, cipher
    config.pwd = cipher.encrypt(argv1.encode())
    
def u_alias(arg1):
    config.alias = arg1

def u_friend(arg1):
    config.friend = arg1
def u_msg1(arg1):
    config.msg1 = arg1
def u_msg(arg1):
    config.msg = arg1
    config.msg1 = arg1
    #print(config.msg1)
    if arg1 != '':
        msgx = arg1.split(':')
        #print(msgx)
        if ( msgx[0] == 'FRIEND' or msgx[0] == 'ROOM' ) and (msgx[1] == config.user or msgx[2] == config.user):
            #print(msgx)
            qdate = QDate.currentDate()
            current_time = QTime.currentTime()
            try:
           
              conn = sqlite3.connect(config.sqdb)
              date_str = "'" + qdate.toString('yyyy-MM-dd') + ' ' + current_time.toString('hh:mm:ss')+ "'"
          #    print(date_str)
              conn.execute("INSERT INTO msgs (id, msgfr, username, recvr, msg, status, datesent) "
                       "VALUES ('" + msgx[4] + "', '" + msgx[0] + "', '" + msgx[1] + "', '" + msgx[2] + "', '" +  msgx[3] + "', 'DELV', " + date_str + ')')
              conn.commit()
              
            except Exception as e:
                print(str(e))  
def u_room(arg1):
    config.room = arg1

def get_fiends(arg1):
    t1 =  arg1
    t1 = repr(str(t1))
    #print(config.sqdb)
    conn = sqlite3.connect(config.sqdb)
    cursor = conn.execute("SELECT * from tbfriends where username = %s " %(t1))

    records = cursor.fetchall()
    df = pd.DataFrame(records)
    config.frnd_itms = len(df)
    for ind in df.index:
        config.friends.append([df[2][ind]])
  
def get_rooms(arg1):
    t1 =  arg1
    t1 = repr(str(t1))
    
    conn = sqlite3.connect(config.sqdb)
 
    cursor = conn.execute("SELECT room FROM `tbrooms` WHERE username = %s or  friends = %s group by room  " %(t1, t1))
 
    records = cursor.fetchall()
    df1 = pd.DataFrame(records)

    for ind in df1.index:
        config.rooms.append([df1[0][ind]])

def user_found(argv1):
    config.user_found = argv1
def get_messages(arg1):
    t1 =  'FRIEND'
    t1 = repr(str(t1))
    t2 = arg1
    t2 = repr(str(t2))
    config.msgs = []
    conn = sqlite3.connect(config.sqdb)
 
    cursor = conn.execute("SELECT * FROM `msgs`  WHERE username = %s and msgfr = %s" %(t2, t1))
 
    records = cursor.fetchall()
    df1 = pd.DataFrame(records)

    for ind in df1.index:
        config.msgs.append([df1[2][ind] + ':' + df1[4][ind]])    