from db_manager import DbManager


class User:
    def __init__(self):
        self.login = None
        self.passphrase = None
        self.role = "user"
        self.logged_in = False
        self.inbox = {}

    @staticmethod
    def does_user_exist(db, user_name):
        if DbManager.fetch(db, user_name):
            return True
        else:
            return False

    def log_in(self, db, user_name, password):
        if self.does_user_exist(db, user_name):
            if DbManager.fetch(db, user_name)["password"] == password:
                self.logged_in = True
                return True
        else:
            return False

    def log_out(self):
        self.logged_in = False

    @staticmethod
    def add(db, user_name, password):
        if DbManager.fetch(db, user_name) is None:
            DbManager.add(db, {user_name: {"password": password, "role": "user", "inbox": {}}})
            return True
        else:
            return False

    @staticmethod
    def remove(db, user_name):
        if DbManager.fetch(db, user_name):
            DbManager.remove(db, user_name)
            return True
        else:
            return False

# user = User()
# user.add("johnny_boy", "strongpass")