import logging
import time

from db_manager import DbManager
from user import User


class MessageDAO:
    db = DbManager("mail.json")

    @classmethod
    def save_message(cls, username, message_data):
        """Save  message to user's (recipient's) inbox file"""
        try:
            if not isinstance(message_data, dict):
                raise TypeError("Message data must be in a dictionary format")
            if not isinstance(username, str) or not username.strip():
                raise ValueError("Invalid recipient (username)")
            required_msg_fields = {"timestamp", "sender name", "sender email", "content"}
            missing_fields = required_msg_fields - message_data.keys()
            if missing_fields:
                raise ValueError(f"Missing required fields: {missing_fields}")
            cls.db.save(username, message_data)
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
            return cls.db.get(username)
        except (TypeError, ValueError, KeyError) as e:
            logging.error(f"Failed to retrieve messages for user: {username}: {e}")
            raise


MessageDAO.save_message("lemon", {"timestamp": time.time(), "sender name": "joanna",
                          "sender email": "joannak@mail.com", "content": "Hi there!"})
