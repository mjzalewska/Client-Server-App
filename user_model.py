import logging
from datetime import datetime
from user_dao import UserDAO


class User:
    def __init__(self, username, password_hash, email, role="user", inbox=None):
        self.username = username
        self.password_hash = password_hash
        self.email = email
        self.role = role
        self.inbox = inbox if inbox else None
        self.is_logged_in = False

    @classmethod
    def log_in(cls, username, password):
        """Authenticate and return a user instance if credentials are valid.

        Args:
        username (str): Username
        password (str): Password

        Returns:
            User: A new User instance with is_logged_in set to True if authentication succeeds

        Raises:
            TypeError: If username or password are not strings.
            ValueError: If password is empty or incorrect.
            KeyError: If user with provided username doesn't exist.
            AttributeError: If user data in database is corrupted or in wrong format.
        """
        if not isinstance(username, str):
            raise TypeError("Username must be a string")
        if not isinstance(password, str):
            raise TypeError("Password must be a string")
        user_data = UserDAO.get_user(username)
        if not user_data:
            raise KeyError(f"User {username} not found")
        try:
            stored_data = user_data[username]
            if stored_data is None:
                raise KeyError(f"User {username} not found")
            if stored_data['password_hash'] != UserDAO.hash_password(password):
                raise ValueError("Invalid password")
            user = cls(username=username, **stored_data)
            user.is_logged_in = True
            return user
        except KeyError as e:
            logging.error(f"User lookup failed: {e}")
            raise
        except (TypeError, AttributeError) as e:
            logging.error(f"Corrupted user data: {e}")
            raise ValueError("Invalid user data format")

    @classmethod
    def register(cls, username, password, email, role="user"):
        """
    Add a new user.

    Args:
        username (str): Username
        password (str): Password
        email (str): Email
        role (str, optional): User role. Defaults to "user"

    Returns:
        bool: True if registration successful

    Raises:
        ValueError: If any parameter is invalid
        TypeError: If parameters are of wrong type
    """
        if not all(isinstance(param, str) for param in [username, password, email, role]):
            raise TypeError("All parameters must be strings")
        if not all(param.strip() for param in [username, password, email]):
            raise ValueError("Parameters cannot be empty")
        if role not in ["user", "admin"]:
            raise ValueError("Invalid role")

        try:
            if UserDAO.user_exists(username):
                raise ValueError(f"User {username} already exists")
            user_data = {
                "username": username,
                "password_hash": UserDAO.hash_password(password),
                "email": email,
                "role": role
            }
            UserDAO.save_user(user_data)
            return True
        except (TypeError, ValueError, OSError) as e:
            logging.error(f"User registration failed: {e}")
            raise

    @classmethod
    def delete(cls, username):
        """
        Remove user account.

        Args:
            username (str): Username to delete

        Returns:
            bool: True if deletion successful

        Raises:
            ValueError: If username is invalid
            KeyError: If user doesn't exist
        """
        if not isinstance(username, str) or not username.strip():
            raise ValueError("Invalid username")

        try:
            if not UserDAO.user_exists(username):
                raise KeyError(f"User {username} does not exist")
            UserDAO.delete_user(username)
            return True
        except (ValueError, KeyError) as e:
            logging.error(f"Account deletion failed: {e}")
            raise

    @staticmethod
    def get(username=None):
        """
        Fetch user record.

        Args:
            username (str, optional): Username to fetch

        Returns:
            dict: User data

        Raises:
            KeyError: If user doesn't exist
            ValueError: If username is invalid
        """
        try:
            if username is not None:
                if not isinstance(username, str) or not username.strip():
                    raise ValueError("Invalid username")
                data = UserDAO.get_user(username)
                if not data:
                    raise KeyError(f"User {username} not found")
                return data
            return UserDAO.get_user()
        except (ValueError, KeyError) as e:
            logging.error(f"Failed to retrieve user data: {e}")
            raise

    def send_message(self, recipient, message):
        """
        Send a message to another user.

        Args:
            recipient (str): Username of recipient
            message (str): Message content

        Returns:
            bool: True if message sent successfully

        Raises:
            ValueError: If parameters are invalid
            KeyError: If recipient doesn't exist
        """
        if not isinstance(recipient, str) or not recipient.strip():
            raise TypeError("Recipient name must be a string")
        if not isinstance(message, str) or not message.strip():
            raise ValueError("Invalid message")
        if len(message) > 255:
            raise ValueError("Message exceeds 255 characters")
        try:
            recipient_data = UserDAO.get_user(recipient)
            if not recipient_data:
                raise KeyError(f"Recipient {recipient} not found")
            date = datetime.now()
            timestamp = (date.day, date.month, date.year,
                         date.time().strftime("%H:%M:%S"))
            if "inbox" not in recipient_data[recipient]:
                recipient_data[recipient]["inbox"] = {}
            recipient_data["inbox"][timestamp][self.username] = message
            UserDAO.save_user(recipient_data)
            return True
        except (KeyError, ValueError) as e:
            logging.error(f"Failed to send message: {e}")
            raise
