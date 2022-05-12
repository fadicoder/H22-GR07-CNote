import enum
import string
import random
import mysql.connector
import re
from notes import Notes
from os import getenv


class Error(enum.Enum):
    No_Error = 0
    Pwd_Empty = 1
    Pwd_Not_Matched = 2
    Pwd_Too_Short = 3
    Pwd_Too_Long = 4
    Confirm_Pwd_Error = 5
    Invalid_Pwd = 6
    Username_Empty = 7
    Username_Too_Short = 8
    Username_Too_Long = 9
    Same_Username = 10
    Already_Taken_Username = 11
    Prohibited_Chars_User = 12
    Prohibited_Chars_Pwd = 13
    Connection_Error = 14

    def get_desc(self):
        """
        Cette fonction affiche les messages d'erreurs possibles lors de la connection/creation de compte
        """
        if self == self.No_Error:
            return ''
        if self == self.Pwd_Not_Matched:
            return "Nom d'utilisateur ou mot de passe invalide"
        if self == self.Pwd_Empty:
            return 'Veuillez entrer un mot de passe'
        if self == self.Pwd_Too_Short:
            return 'Le mot de passe doit contenir au moins 8 caractères'
        if self == self.Pwd_Too_Long:
            return "Le mot de passe ne doit pas dépasser 30 caractères"
        if self == self.Username_Empty:
            return "Veuillez entrer un nom d'utilisateur"
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
    """
    Ceci est l'instance d'un compte
    """
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
        """
        Cette fonction se connecte à la base de donnée avec le super-user selon les infos dans le fichier .env
        """
        self.error = Error.No_Error

        try:
            self.mydb = mysql.connector.connect(user=getenv('USER_NAME'), password=getenv('PASSWORD'),
                                                host=getenv('HOST'), port=3306, database="CNoteServer")
        except mysql.connector.errors.DatabaseError:
            self.error = Error.Connection_Error
            return

        self.cursor = self.mydb.cursor()

    def get_error_desc(self):
        """
        Cette fonction va chercher l'erreur pour l'afficher si il y en a une
        """
        error_desc = self.error.get_desc()
        self.error = Error.No_Error
        return error_desc

    def log_in(self, username: str, pwd: str) -> bool:
        """
        Cette fonction tente de se connecter à un compte, sinon pointe vers les erreurs qui sont arrivées
        """
        if len(username) == 0:
            self.error = Error.Username_Empty
            return False

        if len(pwd) == 0:
            self.error = Error.Pwd_Empty
            return False

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


        # vérifier que le tableau des données exsiste
        self.cursor.execute(f"SELECT EXISTS (SELECT TABLE_NAME FROM information_schema.TABLES "
                            f"WHERE TABLE_NAME = '{username}_cnotes');")
        if self.cursor.fetchone()[0] == 0:  # Si pour une raison x le tableau n'est plus la, il faut le recréer
            self.cursor.execute(f"CREATE TABLE {username}_cnotes(id VARCHAR(32), body LONGTEXT);")
            self.cursor.execute(f"GRANT ALL PRIVILEGES ON cnoteserver.{username}_cnotes TO '{username}'@'localhost';")
            self.mydb.commit()


        # lire les données dans le tableau
        self.cursor.execute(f"SELECT id, body FROM cnoteserver.{username}_cnotes;")
        for element in self.cursor.fetchall():
            self.notes_lst.append(Notes(identification=element[0], account=self, notes_info=element[1]))

        return True

    def sign_up(self, username: str, pwd: str):
        """
        Cette fonction tente de créer un compte, sinon pointe vers les erreurs qui sont arrivées
        """
        if len(username) == 0:
            self.error = Error.Username_Empty
            return False

        if len(pwd) == 0:
            self.error = Error.Pwd_Empty
            return False

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
        """
        Cette fonction déconnecte l'utilisateur
        """
        self.mydb.disconnect()
        self.mydb = None
        self.cursor = None
        self.error = Error.No_Error
        self.notes_lst = []
        self.username = ''
        self.password = ''
        self.connect()

    def upload_notes(self, notes, notes_info: str):
        """
        Cette fonction envoie les notes dans le cloud lorsque l'utilisateur le demande et
        vérifie si elle est déja présente, si elle est, elle est mise à jour.
        :param notes : la note qui doit etre  envoyée
        :param notes_info : string extraite des notes
        """
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

    def delete_notes(self, notes):
        """
        Cette fonction supprime la note demandée de la base de données
        """
        if self.username == '':  # S'il n'y a pas de nom d'utilisateur, le compte est déconnecté
            return
        if notes not in self.notes_lst:
            return

        self.cursor.execute(f"DELETE FROM qwerqwer_cnotes WHERE id = '{notes.id}';")
        self.notes_lst.remove(notes)
        self.mydb.commit()

    def change_username(self, new_username):
        """
        Cette fonction tente de changer le nom d'utilisateur,
        sinon renvoie l'erreur qui s'est produite lors de la tentative
        """
        if self.username == '':
            self.error = Error.Connection_Error
            return False

        if len(new_username) == 0:
            self.error = Error.Username_Empty
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
        self.mydb.commit()
        return True

    def change_password(self, old_pwd, new_pwd, confirm_new_pwd):
        """
        Cette fonction tente de changer le mot de passe d'utilisateur,
        sinon renvoie l'erreur qui s'est produite lors de la tentative
        """
        if self.username == '':
            self.error = Error.Connection_Error
            return False
        if len(new_pwd) == 0 or len(old_pwd) == 0:
            self.error = Error.Pwd_Empty
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
        self.mydb.commit()
        return True

    def is_used_username(self, username):
        """
        Cette fonction vérifie et empeche d'utiliser deux fois le meme nom d'utilisateur
        """
        self.cursor.execute(f"SELECT user FROM mysql.user WHERE user = '{username}'")
        check_user = self.cursor.fetchone()

        if check_user is not None:  # Si nom d'utilisateur n'existe pas déjà
            self.error = Error.Already_Taken_Username
            return True
        return False

    def is_used_id(self, identification):
        """
        Cette fonction vérifie et empeche d'utiliser deux fois le meme id de notes
        """
        self.cursor.execute(f"SELECT id FROM cnoteserver.{self.username}_cnotes WHERE id = '{identification}';")
        check_id = self.cursor.fetchone()
        return check_id is not None

    def generate_id(self):
        """
        Cette fonction génère l'identifiant de la note uploadée
        """
        identification = ''.join(random.choices(string.ascii_letters + string.digits, k=32))
        while self.is_used_id(identification):
            identification = ''.join(random.choices(string.ascii_letters, k=32))
        return identification

    def is_signed_out(self):
        """
        Cette fonction vérifie si l'utilisateur est déconnecté
        """
        return self.username == ''
