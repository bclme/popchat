import config
import pandas as pd
import mysql.connector as mysql
import hashlib
from Crypto.PublicKey import RSA
from Crypto.Cipher import PKCS1_OAEP, AES
from PyQt6.QtCore import  QDate, QTime
config.salt = b'4\xa8y\x8e\xca\xfb\x7f\x8e\xd5\x97v\x14\xc7[Z\xd0'

config.privKey = b'-----BEGIN RSA PRIVATE KEY-----\nMIICWwIBAAKBgQCkw+2UyXgxMG0qetT9q9Oflx9A3KUnnJ+9F0q4TJgnpD0DP9F5\n3yU8AmBca49cPT/4Hc7s60yGk8f8m0+wE8hEOXcLXMulYx+JeJcWdJhUW9pJWDFW\nFeC0lBPLihBHOkAHi8aCZ1m5ccSmTzQUDeLIYFQsZ2vkgVwxulOYRBx+UQIDAQAB\nAoGARBR/DS0IIE8RtG1Hp7+BdF5luA/ToB/78w52PdvMPQkEety6SgC1qmuS9G0v\nMd5PGc77SvLYznyutEZacXdjFn+5tA5e8b7fVrGoS53pHMhiAW3qTy+bItyt+qQP\nh9Hj5cLUXuAuItDM5CpISvkdqKcC9aXhhG2yIadyex4MY+8CQQDDqZAjJtlmN962\n61kJQihJJueSuBjSjjCcgu4cpGFU2y0KHruRBPjx5ZRJg3HvWzq4vrmr80pJJdhm\nhoe1vEG3AkEA15M4eOceJroiBhUPdfcOpNZQnlVPTSRBHz/CVANf+y/x3UFW/GaZ\nuKN4YA2UQGozs5pgchv3y2LW1oK2DSigNwJAaE+uuz7L6fXhM023EvuFNLKcBJlH\nCoGpotcekICGL1IF6f5GauLmwTdu3d5I0J2nabSskeJLeUHG46nXEelCcwJAe1Ci\n4D5M+BhHeDU55+AQh2h1K21fdKBFhEujrQ1VLUoKz+cdjDpguscAB+ocoRBfTOEF\nRKENCVIb1Q9mdnaD1wJATmc3q5HG8z4q56L5FLLZt9/II/wptpXTDRoro4nIDRKv\nf2TFTSHvPYzLGt6H1tWxc7FucLkFxHtZDasK8B1jdA==\n-----END RSA PRIVATE KEY-----'

key = RSA.import_key(config.privKey)
cipher = PKCS1_OAEP.new(key)

def u_time(arg1):
    config.label_time = arg1

def u_regr(arg1):
    config.regr = arg1
    
def u_regr_data(arg1):
    config.regr_data = arg1
    
def u_start(arg1):
    config.on_start = arg1

def u_load(arg1):
    config.on_load = arg1

def u_user(arg1):
    config.user = arg1

def u_pwd(argv1):
    global key, cipher  
  
    try:
      config.pwd = cipher.decrypt(argv1)  
 
      config.pwd = str(config.pwd)
      z= len(config.pwd)-1
      config.pwd = config.pwd[2:z]
      #print(config.pwd)
    except Exception as err:
        #print(str(err))  
        #print(config.pwd)
        pass
    
def u_alias(arg1):
    config.alias = arg1

def u_friend(arg1):
    config.friend = arg1

def u_msg(arg1):
    config.msg = arg1

def u_room(arg1):
    config.room = arg1

def get_fiends(arg1):
    t1 =  arg1
    t1 = repr(str(t1))
    db = mysql.connect(
             host = config.host,
             user = config.user1,
             passwd = config.passwd,
             database = config.database,
             raise_on_warnings= True
          )
    cursor = db.cursor()
    query = "SELECT * FROM tbfriends where username = %s " %(t1)
    cursor.execute(query)
    records = cursor.fetchall()
    df = pd.DataFrame(records)
    for ind in df.index:
        config.friends.append([df[2][ind]])
    cursor.close()
    db.close()
def get_rooms(arg1):
    t1 =  arg1
    t1 = repr(str(t1))
    db = mysql.connect(
             host = config.host,
             user = config.user1,
             passwd = config.passwd,
             database = config.database,
             raise_on_warnings= True
          )
    cursor = db.cursor()
    query = "SELECT room FROM `tbrooms` WHERE username = %s or  friends = %s group by room  " %(t1, t1)
    cursor.execute(query)
    records = cursor.fetchall()
    df1 = pd.DataFrame(records)

    for ind in df1.index:
        config.rooms.append([df1[0][ind]])
    cursor.close()
    db.close()
def user_login(arg1, argv2):

    db = mysql.connect(
             host = config.host,
             user = config.user1,
             passwd = config.passwd,
             database = config.database,
             raise_on_warnings= True
          )
    cursor = db.cursor()
    t1 = arg1
    t2 = argv2
    #print(t2)
    t2 = hashlib.pbkdf2_hmac("sha256", t2.encode(), config.salt, 100000)
    t1 = repr(str(t1))
    t2 = repr(str(t2))
    #print(t2)
    #print(t1)
    query = "SELECT * FROM tbusr where username = %s and password  = %s" %(t1, t2)
    cursor.execute(query)
    records = cursor.fetchall()
    df1 = pd.DataFrame(records)
    #print(len(records))
    if len(df1)!= 0:
        config.login_ok = 'OK'
    else:
        config.login_ok = 'NOUSER'    
    
    cursor.close()
    db.close()  

def user_regr(arg1, argv2):

    db = mysql.connect(
             host = config.host,
             user = config.user1,
             passwd = config.passwd,
             database = config.database,
             raise_on_warnings= True
          )
    cursor = db.cursor()
    t1 = arg1[1]
    t2 = arg1[3]
    t3 = arg1[2]
    t4 = argv2
    #print(t4)
    #print(t2)
    t4 = hashlib.pbkdf2_hmac("sha256", t4.encode(), config.salt, 100000)
    #t1 = repr(str(t1))
    #t2 = repr(str(t2))
    #t3 = repr(str(t3))
    t4 = str(t4)
    try:
        #print(t1)
        sql = "INSERT INTO tbusr (username, fullname, password, email) VALUES (%s, %s, %s, %s)"
        val = (t1, t2, t4, t3)
        cursor.execute(sql, val)
    
        
        config.regr_ok = 'OK'
        
                
    
        cursor.close()
        db.close() 
    except Exception as e:
        
        config.regr_ok = str(e)
    
def save_message(argv1):
    qdate = QDate.currentDate()
    current_time = QTime.currentTime()
    date_str = "'" + qdate.toString('yyyy-MM-dd') + ' ' + current_time.toString('hh:mm:ss')+ "'"
    #print(date_str)
    db = mysql.connect(
             host = config.host,
             user = config.user1,
             passwd = config.passwd,
             database = config.database,
             raise_on_warnings= True
          )
    cursor = db.cursor()
    msgx = argv1.split(':')
    #print(msgx)
    try:
      sql = "INSERT INTO tbmessages (msgfr, username, recvr, msg, status, datesent) VALUES (%s, %s, %s, %s, %s, %s)"
      val = (msgx[0], msgx[1], msgx[2], msgx[3], 'SENT', date_str)
      cursor.execute(sql, val)
      t1 = repr(str(date_str))
      query = "SELECT * FROM tbmessages where datesent = %s" %(t1)
      cursor.execute(query)
      records = cursor.fetchall()
      df1 = pd.DataFrame(records)     
      
      if len(df1)!= 0:
          config.msg_id = df1[0][0] 
          #print(config.msg_id)        
      else:
          config.msg_id = 0
          
    except Exception as e:
        #print(str(e))
        pass  
    
    cursor.close()
    db.close()    
def update_message(arg1):
  try:  
    db = mysql.connect(
             host = config.host,
             user = config.user1,
             passwd = config.passwd,
             database = config.database,
             raise_on_warnings= True
          )
    cursor = db.cursor()
     
    #print(arg1[1])
    sql = "UPDATE tbmessages SET status = %s WHERE id = %s"
    val = (arg1[2], int(arg1[1]))
    cursor.execute(sql, val)
    db.commit()
  except Exception as e:
      #print(str(e))
      pass
      
def get_sent_msgs(arg1):
  try:  
    db = mysql.connect(
             host = config.host,
             user = config.user1,
             passwd = config.passwd,
             database = config.database,
             raise_on_warnings= True
          )
    cursor = db.cursor()  
    t1 = 'SENT'          
    t1 = repr(str(t1))
    t2 = repr(str(arg1))
    #print('test2')
    query = "SELECT * FROM tbmessages where status = %s and recvr = %s" %(t1, t2)
    cursor.execute(query)
    records = cursor.fetchall()
    df1 = pd.DataFrame(records)     
    config.msg_sent = []  
    if len(df1)!= 0:
        #print('test3')
        for ind in df1.index:
            mww = df1[1][ind] + ':' + df1[2][ind] + ':' + df1[3][ind] + ':' + df1[4][ind] + ':' + str(df1[0][ind])
            config.msg_sent.append([mww])
            #print(config.msg_id)        
  except Exception as e:
      pass
      #print(str(e))
def search_users(arg1):
  try:  
    db = mysql.connect(
             host = config.host,
             user = config.user1,
             passwd = config.passwd,
             database = config.database,
             raise_on_warnings= True
          )
    cursor = db.cursor()  
      
    #print(arg1)        
    
     
    query = "SELECT * FROM tbusr WHERE username LIKE '%" + arg1 + "%'"                  
    
    cursor.execute(query)
    records = cursor.fetchall()
    df1 = pd.DataFrame(records)     
    
    mww = '' 
    #print(len(df1)) 
    if len(df1)!= 0:
        #print('test3')
        for ind in df1.index:
            mww = mww + ':' + df1[1][ind] + '*'  + df1[2][ind]
        config.tbusr = mww
        #print(config.tbusr)
  except Exception as e:
      #print(str(e))
      pass           