import logging
import time
from datetime import datetime

from message_dao import MessageDAO


class Message:
    def __init__(self):
        self.chars_limit = 255
        self.inbox_limit = 5

    def compose(self, recipient, to_email, subject, body):
        """Compose a new message"""
        date = datetime.now()
        timestamp = (date.day, date.month, date.year, date.time().strftime("%H:%M:%S"))
        if not all(isinstance(param, str) for param in [recipient, to_email, subject, body, timestamp]):
            raise TypeError("All parameters must be strings")
        if not all(param.strip() for param in [recipient, to_email]):
            raise ValueError("Recipient name and email cannot be empty")
        if len(body) > self.chars_limit:
            raise ValueError("Message exceeds 255 characters")
        try:
            message_data = {
                "recipient": recipient,
                "email": to_email,
                "subject": subject,
                "body": body,
                "timestamp": timestamp
            }
            return message_data
        except (TypeError, ValueError) as e:
            logging.error(f"The following error occurred when composing new message: {e}")
            raise

    def read(self):
        """Read the contents of a selected message"""
        pass

    def delete(self, username,message_id):
        """Delete a single message from inbox"""
        if not message_id.isdigit():
            raise TypeError("Message index must be an integer")
        if not message_id.strip():
            raise ValueError("Message index cannot be empty")
        if message_id > self.inbox_limit:
            raise KeyError("Message not found!")
        try:
            MessageDAO.delete_message(username, message_id)
            return True
        except(TypeError, ValueError, KeyError) as e:
            logging.error(f"Failed to delete message: {e}")
            raise

    def save(self):
        """Save message to recipient mailbox"""
        pass

    def get_inbox(self):
        """Get the contents of user mailbox"""
        pass



# check if user record already exists - of not make one
# if records exists - updaate with new message
# add message no to the record either on display or when rertireved from the db