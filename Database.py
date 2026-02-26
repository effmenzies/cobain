from imports import *

class Database:
    def __init__(self):
        self.connect()
        #creates tables if not existing
        try:
            self.execute('''CREATE TABLE Users (username text NOT NULL, firstname text, lastname text, age integer, PRIMARY KEY(username))''')
            self.execute('''CREATE TABLE Log (username text NOT NULL, login_date datetime NOT NULL, chat_length datetime, PRIMARY KEY(username, login_date), FOREIGN KEY(username) REFERENCES Users(username))''')
            self.execute('''CREATE INDEX recent_logins ON Log(login_date DESC)''')
        except:
            pass

    def connect(self):
        self.connection = sqlite3.connect("user_data.db")
        self.cursor = self.connection.cursor()
        self.cursor.execute("PRAGMA foreign_keys = ON;")

    def disconnect(self, username):
        self.execute(f'''UPDATE Log SET chat_length = timediff(CURRENT_TIMESTAMP, login_date) WHERE chat_length IS NULL AND username = ?''',(username,))
        self.connection.close()

    def execute(self, query, parameter=None):
        self.cursor.execute(query, parameter or ())
        self.connection.commit()

    def new_user(self, username):
        self.execute(f'''SELECT * FROM Users WHERE username = ?;''',(username,))
        if self.cursor.fetchone():
            suggestion = self.gen_username(username)
            return suggestion, "Username already exists, try " + suggestion
        self.execute(f'''INSERT INTO Users (username) VALUES (?);''',(username,))
        self.execute(f'''INSERT INTO Log (username, login_date) VALUES (?, CURRENT_TIMESTAMP);''',(username,))
        return username, None
    
    def set_info(self, username, objects, info):
        columns = ", ".join(f"{o} = ?" for o in objects)
        query=f'''UPDATE Users SET {columns} WHERE username = ?'''
        self.execute(query, (*info, username))
        return True
    
    def get_info(self, username, objects, table="Users"):
        columns = ", ".join(objects)
        query=f'''SELECT {columns} from {table} WHERE username = ?'''
        self.execute(query, (username, ))
        return self.cursor.fetchall()

    def exists(self, username):
        self.execute(f'''SELECT * FROM Users WHERE username = ?;''',(username,))
        return True if self.cursor.fetchone() is not None else False

    def login(self,username):
        if self.exists(username):
            self.execute(f'''INSERT INTO Log (username, login_date) VALUES (?, CURRENT_TIMESTAMP);''',(username,))
            name = self.get_info(username, ["firstname"])[0][0]
            return username, name
        return None, None
    
    def gen_username(self, base):
        while self.exists(base):
            characters = string.ascii_letters + string.digits
            base += ''.join(rnd.choices(characters, k = rnd.randint(1,4)))
        return base
    
    def last_user(self):
        self.execute('''SELECT username FROM Log LIMIT 1''')
        username = self.cursor.fetchone()[0]
        self.execute('''SELECT firstname FROM Users WHERE username = ?''',(username,))
        name = self.cursor.fetchone()[0]
        return username, name