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

    def _send(self, message, status="success", data=None):
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

    def _receive(self):
        """
        Receive and process a message from the server.

        Returns:
            Message: The received message object

        Raises:
            ConnectionError: If the connection to the server is lost
            RuntimeError: If there are problems processing the message
        """
        try:
            message = self.com_protocol.receive()
            return message

        except BrokenPipeError as e:
            logging.error("Server has closed the connection")
            self.client_sock.close()
            raise ConnectionError("Server connection closed") from e

        except ConnectionResetError as e:
            logging.error("Connection to server was forcefully closed")
            self.client_sock.close()
            raise ConnectionError("Lost connection to server") from e

        except ValueError as e:
            logging.error(f"Received invalid message format: {e}")
            raise RuntimeError(f"Invalid message received from server: {e}") from e

    def run(self):
        try:
            self.connect()
            while True:
                try:
                    server_response = self._receive()
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
                            self._send(request)
                    # clr_screen() # turn on in final
                except RuntimeError as e:
                    print(f"Error: {e}")
                    logging.error(f"Error processing server response: {e}")
                    continue
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
            logging.info("Client shutdown complete")


if __name__ == "__main__":
    client = Client("127.0.0.1", 55555)
    client.run()
