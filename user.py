import hashlib

from db_manager import DbManager


class User:
    def __init__(self, username, password_hash, email, role="user"):
        self.username = username
        self.password_hash = password_hash
        self.email = email
        self.role = role
        self.inbox = []
        self.is_logged_in = False

    @classmethod
    def does_user_exist(cls, username):
        if DbManager.fetch(username):
            return True
        else:
            return False

    @classmethod
    def log_in(cls, username, password):
        if cls.does_user_exist(username):
            user_data = DbManager.fetch(username)[0]
            if user_data["password_hash"] == cls.hash_password(password):
                user = cls(**user_data)
                user.is_logged_in = True
                return user
        else:
            return None
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
    def remove(cls, username):
        if DbManager.fetch(username):
            DbManager.remove(username)
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
