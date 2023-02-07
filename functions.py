import config
import pandas as pd
import mysql.connector as mysql

config.salt = b'4\xa8y\x8e\xca\xfb\x7f\x8e\xd5\x97v\x14\xc7[Z\xd0'


def u_time(arg1):
    config.label_time = arg1

def u_regr(arg1):
    config.regr = arg1

def u_start(arg1):
    config.on_start = arg1

def u_load(arg1):
    config.on_load = arg1

def u_user(arg1):
    config.user = arg1

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
