from db_manager import DbManager


class User:
    def __init__(self, login, passphrase, role):
        self.login = login
        self.passphrase = passphrase
        self.role = role
        self.logged_in = False
        self.inbox = {}

    @staticmethod
    def does_user_exist(user_name):
        if DbManager.fetch(user_name):
            return True
        else:
            return False

    def log_in(self, user):
        user_name, password = user
        if self.does_user_exist(user_name):
            if DbManager.fetch(user_name)["password"] == password:
                self.logged_in = True

    def log_out(self):
        self.logged_in = False

    @staticmethod
    def add(user):
        user_name, password = user
        if DbManager.fetch(user_name) is None:
            DbManager.add({user_name: {"password": password, "role": "user"}})
            return True
        else:
            return False

    @staticmethod
    def remove(user):
        user_name = user[0]
        if DbManager.fetch(user_name):
            DbManager.remove(user_name)
            return True
        else:
            return False
