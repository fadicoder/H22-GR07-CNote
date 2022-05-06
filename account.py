import enum
import string
import random
import mysql.connector
import re
from notes import Notes
from os import getenv


class Error(enum.Enum):
    No_Error = 0
    Pwd_Not_Matched = 1
    Pwd_Too_Short = 2
    Pwd_Too_Long = 3
    Confirm_Pwd_Error = 4
    Invalid_Pwd = 5
    Username_Too_Short = 6
    Username_Too_Long = 7
    Same_Username = 8
    Already_Taken_Username = 9
    Prohibited_Chars_User = 10
    Prohibited_Chars_Pwd = 11
    Connection_Error = 12

    def get_desc(self):
        if self == self.No_Error:
            return ''
        if self == self.Pwd_Not_Matched:
            return "Nom d'utilisateur ou mot de passe invalide"
        if self == self.Pwd_Too_Short:
            return 'Le mot de passe doit contenir au moins 8 caractères'
        if self == self.Pwd_Too_Long:
            return "Le mot de passe ne doit pas dépasser 30 caractères"
        if self == self.Username_Too_Short:
            return "Le nom d'utilisateur doit contenir au moins 8 caractères"
        if self == self.Username_Too_Long:
            return "Le nom d'utilisateur ne doit pas dépasser 30 caractères"
        if self == self.Already_Taken_Username:
            return "Le nom d'utilisateur est déjà pris"
        if self == self.Connection_Error:
            return "Erreur de connection à mysql. \nVeuillez vérifier la valeur de HOST dans .env"
        if self == self.Same_Username:
            return "Le nouveau nom d'utilisateur est identique à l'ancien"
        if self == self.Prohibited_Chars_User:
            return "Le nom d'utilisateur ne peut pas contenir les caractères:\n @, *, ^, \", ', \\, /, (, ) ou espace"
        if self == self.Prohibited_Chars_Pwd:
            return "Le mot de passe ne peut pas contenir les caractères:\n @, *, ^, \", ', \\, /, (, ) ou espace"
        if self == self.Confirm_Pwd_Error:
            return "La confirmation du mot de passe est erronée"
        return 'Erreur inconnue: \nVeuillez contacter le soutien technique'


class Account:

    PROHIBITED_SYMBOLS = re.compile('[@*\'" \\\\()^/]')

    def __init__(self):

        self.mydb = None
        self.cursor = None
        self.error = Error.No_Error
        self.notes_lst = []
        self.username = ''
        self.password = ''
        self.connect()

    def connect(self):

        self.error = Error.No_Error

        try:
            self.mydb = mysql.connector.connect(user=getenv('USERNAME'), password=getenv('PASSWORD'),
                                                host=getenv('Host'), port=3306, database="CNoteServer")
        except mysql.connector.errors.DatabaseError:
            self.error = Error.Connection_Error
            return

        self.cursor = self.mydb.cursor()

    def get_error_desc(self):
        error_desc = self.error.get_desc()
        self.error = Error.No_Error
        return error_desc

    def log_in(self, username: str, pwd: str) -> bool:
        try:
            self.mydb = mysql.connector.connect(user=username, passwd=pwd, host=getenv('Host'),
                                                port=3306, database="CNoteServer")
            self.cursor = self.mydb.cursor()
            self.error = Error.No_Error
            self.username = username
            self.password = pwd

        except mysql.connector.errors.ProgrammingError:
            self.error = Error.Pwd_Not_Matched
            return False
        except mysql.connector.errors.DatabaseError:
            self.error = Error.Connection_Error
            return False

        self.cursor.execute(f"SELECT id, body FROM cnoteserver.{username}_cnotes;")
        for element in self.cursor.fetchall():
            self.notes_lst.append(Notes(identification=element[0], account=self, notes_info=element[1]))

        return True

    def sign_up(self, username: str, pwd: str):

        if len(username) < 8:
            self.error = Error.Username_Too_Short
            return False

        if len(username) > 30:
            self.error = Error.Username_Too_Long

        if len(pwd) < 8:
            self.error = Error.Pwd_Too_Short
            return False

        if len(pwd) > 30:
            self.error = Error.Pwd_Too_Long
            return False

        if re.search(Account.PROHIBITED_SYMBOLS, username) is not None:
            self.error = Error.Prohibited_Chars_User
            return False

        if re.search(Account.PROHIBITED_SYMBOLS, pwd) is not None:
            self.error = Error.Prohibited_Chars_Pwd
            return False

        if self.error == Error.Connection_Error:
            self.connect()
            if self.error == Error.Connection_Error:
                return False

        if self.is_used_username(username):
            return

        self.cursor.execute(f"CREATE USER '{username}'@'localhost' IDENTIFIED BY '{pwd}';")
        self.cursor.execute(f"GRANT ALL PRIVILEGES ON *.* TO '{username}'@localhost IDENTIFIED BY '{pwd}';")
        self.cursor.execute(f"CREATE TABLE {username}_cnotes(id VARCHAR(32), body LONGTEXT);")
        self.cursor.execute(f"GRANT ALL PRIVILEGES ON notes TO '{username}'@'localhost';")
        self.cursor.execute(f"GRANT ALL PRIVILEGES ON cnoteserver.{username}_cnotes TO '{username}'@'localhost';")
        self.mydb.commit()
        return True

    def sign_out(self):
        self.mydb.disconnect()
        self.mydb = None
        self.cursor = None
        self.error = Error.No_Error
        self.notes_lst = []
        self.username = ''
        self.password = ''
        self.connect()

    def upload_notes(self, notes, notes_info: str):

        if self.username == '':  # S'il n'y a pas de nom d'utilisateur, le compte est déconnecté
            return

        notes_info = notes_info.replace("'", r"\'")

        if self.is_used_id(notes.id):
            sql = f"UPDATE cnoteserver.{self.username}_cnotes SET body = '{notes_info}' WHERE id = '{notes.id}';"

        else:
            sql = f"INSERT INTO {self.username}_cnotes(id, body) VALUES ('{notes.id}', '{notes_info}');"
            self.notes_lst.append(notes)

        self.cursor.execute(sql)
        self.mydb.commit()

    def change_username(self, new_username):
        if self.username == '':
            self.error = Error.Connection_Error
            return False
        if len(new_username) < 8:
            self.error = Error.Username_Too_Short
            return False
        if len(new_username) > 30:
            self.error = Error.Username_Too_Long
            return False
        if self.username == new_username:
            self.error = Error.Same_Username
            return False
        if re.search(Account.PROHIBITED_SYMBOLS, new_username) is not None:
            self.error = Error.Prohibited_Chars_User
            return False
        if self.is_used_username(new_username):
            self.error = Error.Already_Taken_Username
            return False

        self.cursor.execute(f"RENAME USER '{self.username}'@'localhost' TO '{new_username}'@'localhost';")
        self.cursor.execute(f"ALTER TABLE {self.username}_cnotes RENAME TO {new_username}_cnotes;")
        self.username = new_username
        return True

    def change_password(self, old_pwd, new_pwd, confirm_new_pwd):
        if self.username == '':
            self.error = Error.Connection_Error
            return False
        if self.password != old_pwd:
            self.error = Error.Invalid_Pwd
            return False
        if len(new_pwd) < 8:
            self.error = Error.Pwd_Too_Short
            return False
        if len(new_pwd) > 30:
            self.error = Error.Pwd_Too_Long
            return False
        if new_pwd != confirm_new_pwd:
            self.error = Error.Confirm_Pwd_Error
            return False
        if re.search(Account.PROHIBITED_SYMBOLS, new_pwd) is not None:
            self.error = Error.Prohibited_Chars_Pwd
            return False
        self.cursor.execute(f"ALTER USER '{self.username}'@'localhost' IDENTIFIED BY '{new_pwd}';")
        self.password = new_pwd
        return True

    def is_used_username(self, username):
        self.cursor.execute(f"SELECT user FROM mysql.user WHERE user = '{username}'")
        check_user = self.cursor.fetchone()

        if check_user is not None:  # Si nom d'utilisateur n'existe pas déjà
            self.error = Error.Already_Taken_Username
            return True
        return False

    def is_used_id(self, identification):
        self.cursor.execute(f"SELECT id FROM cnoteserver.{self.username}_cnotes WHERE id = '{identification}';")
        check_id = self.cursor.fetchone()
        return check_id is not None

    def generate_id(self):
        identification = ''.join(random.choices(string.ascii_letters + string.digits, k=32))
        while self.is_used_id(identification):
            identification = ' '.join(random.choices(string.ascii_letters, k=32))
        return identification