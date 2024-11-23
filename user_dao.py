import hashlib
from db_manager import DbManager


class UserDAO:

    @staticmethod
    def hash_password(password):
        """Return a hashed version of the password."""
        return hashlib.sha256(password.encode()).hexdigest()

    @staticmethod
    def user_exists(username):
        """Check if a user exists in the database."""
        return DbManager.get(username) is not None

    @staticmethod
    def get_user(username):
        """Retrieve user data."""
        return DbManager.get(username)

    @staticmethod
    def save_user(user_data):
        """Save user data."""
        username = user_data.get("username")
        if username:
            DbManager.save(username, user_data)

    @staticmethod
    def delete_user(username):
        """Delete a user."""
        DbManager.delete(username)