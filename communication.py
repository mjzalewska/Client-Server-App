import json
import logging


class CommunicationProtocol:
    def __init__(self, sock, buffer_size=1024):
        self.sock = sock
        self.buffer_size = buffer_size

    @staticmethod
    def format_message(message, status="success", data=None):
        """
        Creates a consistently formatted message dictionary for both success and error cases.
        Args:
            message: The main message content to be sent
            status: Message status - either "success" or "error" (default: "success")
            data: Optional data payload (default: None)

        Returns:
            dict: A properly formatted message dictionary
        """
        if status not in ["success", "error"]:
            raise ValueError("Status must either be 'success' or 'error'")
        return {
            "status": status,
            "message": message,
            "data": data if data is not None else ()
            }

    def send(self, msg):
        """
        Send a message following the application's protocol.
        Args:
            msg: A pre-formatted dictionary
        Raises:
            json.JSONDecodeError: If message cannot be encoded
            ConnectionError: If sending fails
            TypeError: when message is not a dictionary
        """
        if not isinstance(msg, dict):
            msg = self.format_message(msg)
        try:
            encoded_msg = json.dumps(msg).encode("utf-8")
            message_len = len(encoded_msg).to_bytes(4, byteorder="big")
            self.sock.sendall(message_len + encoded_msg)
        except json.JSONDecodeError as e:
            logging.error(f"Invalid message format: {e}")
            raise
        except ConnectionError as e:
            logging.error(f"Failed to send message: {e}")
            raise

    def receive(self):
        """
        Send a message following the application's protocol.
        Args:
            msg: Dictionary containing status, message, data, and event fields

        Raises:
            json.JSONDecodeError: If message cannot be encoded
            ConnectionError: If sending fails
        """
