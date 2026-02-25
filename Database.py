from imports import *

from datetime import datetime

class Database:
    def __init__(self):
        self.connect()
        #create userInfo table if not existing
        try:
            self.execute('''CREATE TABLE Users (uid text primary key, name text, age integer, last_log datetime)''')
        except:
            pass

    def connect(self):
        self.connection = sqlite3.connect("data.db")
        self.cursor = self.connection.cursor()

    def disconnect(self):
        self.connection.close()

    def execute(self, query, parameter=None):
        if not parameter:
            self.cursor.execute(query)
        else: self.cursor.execute(query,parameter)
        self.connection.commit()

    def fetch(self,query,parameter=None):
        self.execute(query, parameter)
        return self.cursor.fetchone()
    
    def get_info(self,uid,object):
        query=f'''SELECT {object} from Users WHERE uid = ?'''
        self.execute(query, (uid, ))
        return self.cursor.fetchone()[0]

    def set_info(self, uid,object,info):
        query=f'''UPDATE Users SET {object} = ? WHERE uid = ?'''
        self.execute(query, (info, uid))
        return True

    def set_user(self):
        now = datetime.now()
        user = self.fetch(f'''SELECT * FROM Users ORDER BY last_log DESC LIMIT 1;''')
        if not user:
            first = True
            uid,name = self.new_user()
        else:
            uid,name = self.fetch(f'''SELECT uid, name FROM Users ORDER BY last_log DESC LIMIT 1;''')
            first = False
        return uid,name, first
    
    def new_user(self):
        now = datetime.now()
        uid = self.gen_username()
        exists = self.fetch(f'''SELECT * FROM Users WHERE uid = ?;''',(uid,))
        while exists: #unique username
            uid = self.gen_username()
            exists = self.fetch(f'''SELECT * FROM Users WHERE uid = ?;''',(uid,))
        self.execute(f'''INSERT INTO Users (uid, last_log) VALUES (?,?);''',(uid,now))
        return uid,None

    def login(self,uid):
        uid, name = self.fetch(f'''SELECT uid, name FROM Users WHERE uid = ?;''',(uid,))
        if uid:
            self.set_info(uid, 'last_log', datetime.now())
        return uid,name
    
    def gen_username(self):
        characters = string.ascii_letters + string.digits
        return ''.join(rnd.choices(characters, k=7))