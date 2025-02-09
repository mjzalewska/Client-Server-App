import logging
import time
from datetime import datetime
from message_dao import MessageDAO
from user_dao import UserDAO


class Message:
    def __init__(self):
        self.chars_limit = 255
        self.inbox_limit = 5

    def compose(self, recipient, sender, from_email, to_email, subject, body):
        """Compose a new message"""
        date = datetime.utcnow()
        timestamp = datetime.strftime(date, "%Y%m%d_%H%M%S")
        if not all(isinstance(param, str) for param in [recipient, sender, from_email, to_email, subject, body]):
            raise TypeError("All parameters must be strings")
        if not all(param.strip() for param in [recipient, to_email]):
            raise ValueError("Recipient name and email cannot be empty")
        if len(body) > self.chars_limit:
            raise ValueError("Message exceeds 255 characters")
        try:
            message_data = {
                "recipient": recipient,
                "sender": sender,
                "from_email": from_email,
                "to_email": to_email,
                "subject": subject,
                "body": body,
                "timestamp": timestamp
            }
            return message_data
        except (TypeError, ValueError) as e:
            logging.error(f"The following error occurred when composing new message: {e}")
            raise

    @staticmethod
    def read(username, message_id):
        """Read the contents of a selected message"""
        if not isinstance(username, str) or not username.strip():
            raise TypeError("Invalid username")
        if not UserDAO.user_exists(username):
            raise KeyError("User not found")
        if not message_id.isdigit():
            raise TypeError("Message index must be an integer")
        if not message_id.strip():
            raise ValueError("Message index cannot be empty")
        if message_id not in MessageDAO.get_all(username):
            raise KeyError("Message not found!")
        try:
            return MessageDAO.get_all(username)[message_id]
        except (TypeError, KeyError, ValueError) as e:
            logging.error(f"Failed to load message: {e}")
            raise

    @staticmethod
    def delete(username, message_id):
        """Delete a single message from inbox"""
        if not message_id.isdigit():
            raise TypeError("Message index must be an integer")
        if not message_id.strip():
            raise ValueError("Message index cannot be empty")
        if message_id not in MessageDAO.get_all(username):
            raise KeyError("Message not found!")
        try:
            MessageDAO.delete_message(username, message_id)
            return True
        except(TypeError, ValueError, KeyError) as e:
            logging.error(f"Failed to delete message: {e}")
            raise

    @staticmethod
    def save(recipient, message):
        """Save message to recipient mailbox"""
        if not isinstance(recipient, str):
            raise TypeError("Recipient name must be a string")
        if not recipient.strip():
            raise ValueError("Recipient cannot be empty")
        if not isinstance(message, dict):
            raise TypeError(f"Incorrect message format: {type(message)}")
        try:
            if not UserDAO.user_exists(recipient):
                raise KeyError(f"Recipient {recipient} not found")
            # if len(MessageDAO.get_all(recipient)) >= self.inbox_limit:
            #     raise ValueError("Inbox limit exceeded.")
            MessageDAO.save_message(recipient, message)
            return True
        except (TypeError, ValueError, KeyError) as e:
            logging.error(f"The following error appeared when saving the message to user {recipient} inbox")
            raise

    @staticmethod
    def get_inbox(username):
        """Get the contents of user mailbox"""
        if not isinstance(username, str) or not username.strip():
            raise TypeError("Invalid username")
        if not UserDAO.user_exists(username):
            raise KeyError("User not found")
        try:
            return MessageDAO.get_all(username)
        except(TypeError, KeyError) as e:
            logging.error(f"Failed to retiree messages from server: {e}")
            raise


