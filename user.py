import hashlib

from db_manager import DbManager


class User:
    def __init__(self, username, password_hash, email, role="user"):
        self.username = username
        self.password_hash = password_hash
        self.role = role
        self.email = email
        self.is_logged_in = False
        self.inbox = []

    @classmethod
    def does_user_exist(cls, user_name):
        if DbManager.fetch(user_name):
            return True
        else:
            return False

    @classmethod
    def log_in(cls, user_name, password):
        if cls.does_user_exist(user_name):
            user_data = DbManager.fetch(user_name)[0]
            if user_data["password"] == password:
                user = cls(**user_data)
                user.is_logged_in = True
                return True
        else:
            return False

    @classmethod
    def log_out(cls):
        cls.is_logged_in = False

    @staticmethod
    def hash_password(password):
        return hashlib.sha256(password.encode()).hexdigest()

    @classmethod
    def add(cls, username, password, email, role="user"):
        if not DbManager.fetch(username):
            password_hash = cls.hash_password(password)
            DbManager.add(
                {"username": username, "password_hash": password_hash, "email": email, "role": role, "inbox": []})
            return True
        else:
            return False

    @classmethod
    def remove(cls, user_name):
        if DbManager.fetch(user_name):
            DbManager.remove(user_name)
            return True
        else:
            return False

    @classmethod
    def get(cls, username=None):
        if username is None:
            users = DbManager.fetch()
        else:
            users = DbManager.fetch(username)
        return users

    def load_inbox(self):
        pass
