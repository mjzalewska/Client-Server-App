import hashlib
from datetime import datetime
import logging
from db_manager import DbManager
from user_dao import UserDAO


class MessageDAO:
    db = DbManager("mail.json")

    @classmethod
    def create_inbox(cls, username):
        cls.db.save(username, {})

    @classmethod
    def generate_message_id(cls, message_data):
        now = datetime.now()
        date_time = now.strftime("%m%d%Y%H%M%S")
        sender = message_data.get("sender")
        try:
            return hashlib.sha1((date_time + sender).encode()).hexdigest()
        except Exception as e:
            logging.error(f"Failed to generate message id: {e}")
            raise

    @classmethod
    def save_message(cls, username, message_data):
        """Save  message to user's (recipient's) inbox file"""
        try:
            if not isinstance(message_data, dict):
                raise TypeError("Message data must be in a dictionary format")
            if not isinstance(username, str) or not username.strip():
                raise ValueError("Invalid recipient (username)")
            message_id = cls.generate_message_id(message_data)
            required_msg_fields = {"recipient", "sender", "from_email", "to_email", "subject", "body", "timestamp"}
            missing_fields = required_msg_fields - message_data.keys()
            if missing_fields:
                raise ValueError(f"Missing required fields: {missing_fields}")
            user_inbox = cls.get_all(username)
            user_inbox[username][message_id] = message_data
            cls.db.save(username, user_inbox[username])
        except (ValueError, TypeError) as e:
            logging.error(f"Failed to save message from user {username}: {e}")
            raise

    @classmethod
    def delete_message(cls, username, message_id):
        """Delete a specific message from inbox"""
        try:
            if not isinstance(username, str):
                raise TypeError("Username must be a string")
            if not isinstance(message_id, int):
                raise TypeError("Message id must be an integer")
            if not username.strip():
                raise ValueError("Username cannot be empty")
            if not str(message_id).strip():
                raise ValueError("Message id cannot be empty")
            cls.db.delete(username[message_id])
        except (TypeError, ValueError, KeyError) as e:
            logging.error(f"Failed to delete message {message_id} due to the following error: {e}")
            raise

    @classmethod
    def get_all(cls, username):
        """Retrieve inbox content for a given user"""
        try:
            if not isinstance(username, str):
                raise TypeError("Username must be a string")
            if not username.strip():
                raise ValueError("Username cannot be empty")
            if not UserDAO.user_exists(username):
                raise KeyError("User does not exist")
            inbox = cls.db.get(username)
            if not inbox:
                inbox = {username: {}}
            return inbox
        except (TypeError, ValueError, KeyError) as e:
            logging.error(f"Failed to retrieve messages for user: {username}: {e}")
            raise
