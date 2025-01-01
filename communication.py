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
            status: Message status - "success", "error" or "ready for input" (default: "success")
            data: Optional data payload (default: None)

        Returns:
            dict: A properly formatted message dictionary
        """
        if status not in ["success", "error", "ready_for_input"]:
            raise ValueError("Status must either be 'success', 'error' or 'ready for input'")
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
        Receives a complete message from the socket.
        The protocol expects:
        1. A 4-byte header containing message length
        2. The message body as JSON-encoded data

        Returns:
            Message: The received message

        Raises:
            BrokenPipeError: If peer closes connection
            ValueError: If message format is invalid
            ConnectionError: If connection is lost during transfer
            json.JSONDecodeError: If received data is not valid JSON
        """
        try:
            header = self.sock.recv(4)
            if not header:
                raise BrokenPipeError("Connection closed by peer")
            msg_len = int.from_bytes(header, byteorder="big")
            if msg_len <= 0:
                raise ValueError(f"Invalid message length: {msg_len}")
            data = bytearray()
            remaining = msg_len
            while remaining > 0:
                chunk = self.sock.recv(min(remaining, self.buffer_size))
                data.extend(chunk)
                remaining -= len(chunk)
            message = json.loads(data.decode("utf-8"))
            return message
        except (BrokenPipeError, ValueError, ConnectionError, json.JSONDecodeError) as e:
            logging.error(f"Error receiving message: {e}")
            raise
