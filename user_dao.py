import hashlib
import logging

from db_manager import DbManager


class UserDAO:

    @staticmethod
    def hash_password(password):
        """
        Return a hashed version of the password.

        Args:
            password (str): Password to hash

        Returns:
            str: Hashed password

        Raises:
            TypeError: If password is not a string
            ValueError: If password is empty
        """
        if not isinstance(password, str):
            raise TypeError("Password must be a string")
        if not password:
            raise ValueError("Password cannot be empty")
        try:
            return hashlib.sha256(password.encode()).hexdigest()
        except Exception as e:
            logging.error(f"Password hashing failed: {e}")
            raise ValueError("Failed to hash password") from e

    @staticmethod
    def user_exists(username):
        """
        Check if a user exists in the database.

        Args:
            username (str): Username to check

        Returns:
            bool: True if user exists, False otherwise

        Raises:
            TypeError: If username is not a string
            ValueError: If username is empty
        """
        if not isinstance(username, str):
            raise TypeError("Username must be a string")
        if not username.strip():
            raise ValueError("Username cannot be empty")
        try:
            return DbManager.get(username)[username] is not None
        except KeyError:
            return False
        except (Exception, ValueError) as e:
            logging.error(f"Error checking user existence: {e}")
            raise

    @staticmethod
    def get_user(username=None):
        """
        Retrieve user data.

        Args:
            username (str): Username to retrieve

        Returns:
            dict: User data or None if user doesn't exist

        Raises:
            TypeError: If username is not a string
            ValueError: If username is empty
            OSError: If database access fails
        """
        try:
            if username is None:
                return DbManager.get()
            else:
                if not isinstance(username, str):
                    raise TypeError("Username must be a string")
                if not username.strip():
                    raise ValueError("Username cannot be empty")
                return DbManager.get(username)
        except (ValueError, KeyError) as e:
            logging.error(f"Failed to retrieve user data: {e}")
            raise

    @staticmethod
    def save_user(user_data):
        """
        Save user data.

        Args:
            user_data (dict): User data to save containing username, password_hash,
                            email, and role

        Raises:
            TypeError: If user_data is not a dictionary
            ValueError: If required fields are missing or invalid
            OSError: If database operation fails
        """
        if not isinstance(user_data, dict):
            raise TypeError("User data must be a dictionary")

        required_fields = {"username", "password_hash", "email", "role"}
        missing_fields = required_fields - user_data.keys()
        if missing_fields:
            raise ValueError(f"Missing required fields: {missing_fields}")

        username = user_data.get("username")
        if not isinstance(username, str) or not username.strip():
            raise ValueError("Invalid username")

        try:
            data = {"password_hash": user_data.get("password_hash"),
                    "email": user_data.get("email"),
                    "role": user_data.get("role")}
            DbManager.save(username, data)
        except (ValueError, TypeError) as e:
            logging.error(f"Failed to save user data: {e}")
            raise

    @staticmethod
    def delete_user(username):
        """
        Delete a user.

        Args:
            username (str): Username to delete

        Raises:
            TypeError: If username is not a string
            ValueError: If username is empty
            KeyError: If user doesn't exist
            OSError: If database operation fails
        """
        if not isinstance(username, str):
            raise TypeError("Username must be a string")
        if not username.strip():
            raise ValueError("Username cannot be empty")
        try:
            DbManager.delete(username)
        except (KeyError, TypeError, ValueError) as e:
            logging.error(f"Failed to delete user {e}")
            raise
