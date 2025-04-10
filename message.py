import logging
from datetime import datetime
from message_dao import MessageDAO
from user_dao import UserDAO


class Message:
    def __init__(self):
        self.chars_limit = 255
        self.inbox_limit = 5
        self.body = ""

    def send(self):
        pass

    def compose(self, recipient, sender, from_email, to_email, subject):
        """Compose a new message"""
        date = datetime.utcnow()
        timestamp = datetime.strftime(date, "%Y-%m-%d H:%M:%S")
        body = self._write_message()
        if not all(param.strip() for param in [recipient, to_email]):
            raise ValueError("Empty parameter error: recipient name and email cannot be empty")
        if not all(isinstance(param, str) for param in [recipient, sender, from_email, to_email, subject, body]):
            raise TypeError("All parameters must be strings")
        if len(body) > self.chars_limit:
            raise ValueError(f"Message length error: message exceeds {self.chars_limit} characters")
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

    def _write_message(self):
        """Write a message with a character limit."""
        try:
            while True:
                remaining = self.chars_limit - len(self.body)
                print(f"({remaining} chars remaining) >>:  ", end="", flush=True)
                line = input()
                if not line:
                    if self.body:
                        print(f"\nFinal message: {self.body}\n")
                        confirm = input("Send this message? (y/n): ").lower()
                        if confirm == 'y':
                            return self.body
                        continue
                elif len(self.body) + len(line) + 1 <= self.chars_limit:
                    self.body += line + "\n"
                elif remaining > 0:
                    self.body += line + "\n"
                else:
                    raise ValueError(f"Message length error: {self.chars_limit} character limit exceeded.")
        except ValueError as e:
            logging.error(f"Error initializing new message: {e}")
            raise

    @staticmethod
    def read(username, message_num):
        """Read the contents of a selected message"""
        if not isinstance(username, str) or not username.strip():
            raise TypeError("Invalid username")
        if not UserDAO.user_exists(username):
            raise KeyError("User not found")
        if not message_num.strip():
            raise ValueError("Message index cannot be empty")
        if not message_num.isdigit():
            raise TypeError("Message index must be an integer")
        messages = MessageDAO.get_all(username)

        try:
            message_id = Message._convert_email_id_to_email_num(
                messages_dict=messages,
                username=username,
                message_num=message_num
            )
            if message_id not in messages[username]:
                raise KeyError("Message not found!")
            return messages[username][message_id]
        except (TypeError, KeyError, ValueError) as e:
            logging.error(f"Failed to load message: {e}")
            raise

    @staticmethod
    def delete(username, message_num):
        """Delete a single message from inbox"""
        if not isinstance(username, str) or not username.strip():
            raise TypeError("Invalid username")
        if not UserDAO.user_exists(username):
            raise KeyError("User not found")
        if not message_num.strip():
            raise ValueError("Message index cannot be empty")
        if not message_num.isdigit():
            raise TypeError("Message index must be an integer")
        messages = MessageDAO.get_all(username)
        try:
            message_id = Message._convert_email_id_to_email_num(
                messages_dict=messages,
                username=username,
                message_num=message_num
            )
            if message_id not in messages[username]:
                raise KeyError("Message not found!")
            MessageDAO.delete_message(username, message_id)
            return True
        except(TypeError, ValueError, KeyError) as e:
            logging.error(f"Failed to delete message: {e}")
            raise

    def save(self, recipient, email):
        """Save message to recipient mailbox"""
        if not recipient.strip():
            raise ValueError("Recipient cannot be empty")
        if not isinstance(recipient, str):
            raise TypeError("Recipient name must be a string")
        if not isinstance(email, dict):
            raise TypeError(f"Incorrect message format: {type(email)}")
        try:
            if not UserDAO.user_exists(recipient):
                raise KeyError(f"Recipient {recipient} not found")
            if len(MessageDAO.get_all(recipient)[recipient]) >= self.inbox_limit:
                raise ValueError("Inbox limit exceeded.")
            MessageDAO.save_message(recipient, email)
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
            logging.error(f"Failed to retrieve messages from server: {e}")
            raise

    @staticmethod
    def _convert_email_id_to_email_num(messages_dict, username, message_num=None, message_id=None):
        mapping = {str(num + 1): item for num, item in enumerate(list(messages_dict[username].keys()))}
        if message_num is not None and message_id is not None:
            raise ValueError("Parameters specified incorrectly")
        elif message_num is None and message_id is None:
            raise ValueError("Parameters specified incorrectly. Both parameters cannot be empty")
        try:
            if message_num is not None:
                for num in mapping.keys():
                    if num == message_num:
                        return mapping[num]
            elif message_id is not None:
                for num, id_num in mapping.items():
                    if id_num == message_id:
                        return num
        except ValueError:
            logging.error(f"Parameters specified incorrectly for method:"
                          f"{Message._convert_email_id_to_email_num.__name__}")


# message = Message()
# my_message = message.compose("ula_cebula", "jane", "cebula@mail.com", "jane.f@mail.com", "Wanna hang out tomorrow?")
# print(my_message)
