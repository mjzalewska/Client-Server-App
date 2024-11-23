from datetime import datetime
from user_dao import UserDAO


class User:
    def __init__(self, username, password, email, role="user", inbox=None):
        self.username = username
        self.password = password
        self.email = email
        self.role = role
        self.inbox = inbox if inbox else None
        self.is_logged_in = False

    @classmethod
    def log_in(cls, username, password):
        """Authenticate and return a user instance if credentials are valid."""
        user_data = UserDAO.get_user(username)
        if user_data and user_data["password_hash"] == UserDAO.hash_password(password):
            user = cls(**user_data)
            user.is_logged_in = True
            return user
        return None

    @classmethod
    def register(cls, username, password, email, role="user"):
        """Add a new user"""
        if not UserDAO.user_exists(username):
            user_data = {
                "username": username,
                "password_hash": UserDAO.hash_password(password),
                "email": email,
                "role": role
            }
            UserDAO.save_user(user_data)
            return True
        return False

    @classmethod
    def delete_account(cls, username):
        """Remove user account"""
        if UserDAO.user_exists(username):
            UserDAO.delete_user(username)
            return True
        return False

    def send_message(self, recipient, message):
        recipient_data = UserDAO.get_user(recipient)
        if recipient_data:
            date = datetime.now()
            day, month, year = date.day, date.month, date.year
            time = date.time().strftime("%H:%M:%S")
            recipient_data["inbox"][(day, month, year, time, self.username)] = message
            return True
        return False
