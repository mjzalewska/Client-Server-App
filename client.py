import json
import logging
import socket

from communication import CommunicationProtocol
from display import Display
from utilities import clr_screen


class Client:
    def __init__(self, host, port, client_sock=None):
        try:
            self.host = host
            self.port = port
            if client_sock is None:
                self.client_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            else:
                self.client_sock = client_sock
            self.com_protocol = CommunicationProtocol(self.client_sock)
        except socket.error as e:
            logging.error(f"Failed to initialize socket: {e}")
            raise

    def connect(self):
        try:
            self.client_sock.connect((self.host, self.port))
        except ConnectionRefusedError as e:
            logging.error(f"Connection refused: {e}")
            raise
        except socket.error as e:
            logging.error(f"Failed to connect: {e}")
            raise

    def send(self, message, status="success", data=None):
        """
        Send messages with proper formatting and error handling.
        Handles business logic for message formatting and error responses.
        """
        try:
            message_to_send = self.com_protocol.format_message(message, status=status, data=data)
            self.com_protocol.send(message_to_send)
        except ConnectionError as e:
            logging.error(f"Connection lost: {e}")
            raise
        except Exception as e:
            logging.error(f"Invalid message format: {e}")
            error_message = self.com_protocol.format_message(str(e), status="error")
            self.com_protocol.send(error_message)

    def receive(self):
        msg_parts = []
        bytes_recv = 0
        header = self.client_sock.recv(4)
        if not header:
            raise ValueError
        while True:
            try:
                msg_len = int.from_bytes(header[0:4], byteorder="big")
                while bytes_recv < msg_len:
                    msg_part = self.client_sock.recv(min(msg_len - bytes_recv, 1024))
                    if not msg_part:
                        break
                    msg_parts.append(msg_part)
                    bytes_recv += len(msg_part)
            except ValueError:
                self.send({"status": "error",
                           "message": "Invalid message format: missing header!",
                           "data": {},
                           "event": ""})
                exit()
            data = b"".join(msg_parts)
            message = json.loads(data.decode("utf-8").strip())
            return message

    def run(self):
        try:
            self.connect()
            while True:
                try:
                    server_response = self.receive()
                    Display.display_message(server_response)
                    if server_response.get("event") == "info":
                        continue
                    else:
                        request = input(">>: ")
                        print()
                        if request == "close":
                            self.client_sock.close()
                            break
                        else:
                            self.send(request)
                    # clr_screen() # turn on in final
                except ConnectionError as e:
                    logging.error(f"Connection to the host has been lost: {e}")
                    raise
                except KeyError as e:
                    logging.error(f"Invalid server response format: {e}")
                    raise ValueError(f"Server sent invalid response: missing {e}")
                except json.JSONDecodeError as e:
                    logging.error(f"Invalid JSON in server response: {e}")
                    raise
        finally:
            self.client_sock.close()


if __name__ == "__main__":
    client = Client("127.0.0.1", 65000)
    client.run()
