import json
import logging
from logging.handlers import RotatingFileHandler
import os
import sys
import select
import socket
from communication import CommunicationProtocol
from display import Display
from utilities import clr_screen

if os.name == "nt":
    import msvcrt


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
            self.message_queue = []
            self.awaiting_input = False
            logging.basicConfig(handlers=[RotatingFileHandler('client.log', maxBytes=5 * 1024 * 1024, backupCount=5)],
                                level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')
        except socket.error as e:
            logging.error(f"Failed to initialize socket: {e}")
            raise

    def connect(self):
        try:
            self.client_sock.connect((self.host, self.port))
            self.client_sock.setblocking(False)
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

    def handle_response(self):
        """
        Receive and process a message from the server.
        """
        try:
            message = self.com_protocol.receive()
            if message.get("status") == "ready_for_input":
                self.awaiting_input = True
                return message
            elif message.get("message") or message.get("data"):
                Display.display_message(message)
            return message
        except BrokenPipeError as e:
            logging.error("Server has closed the connection")
            raise ConnectionError("Server connection closed") from e
        except ConnectionResetError as e:
            logging.error("Connection to server was forcefully closed")
            raise ConnectionError("Lost connection to server") from e
        except ValueError as e:
            logging.error(f"Received invalid message format: {e}")
            raise RuntimeError(f"Invalid message received from server: {e}") from e

    def display_prompt(self):
        """Display the input prompt if we're awaiting input."""
        if self.awaiting_input:
            print(">>: ", end='', flush=True)
            self.awaiting_input = False

    @staticmethod
    def check_windows_input():
        """Check for input on Windows systems."""
        if msvcrt.kbhit():
            return msvcrt.getch().decode()
        return None

    def run(self):
        try:
            self.connect()
            input_line = ""
            while True:
                try:
                    if os.name == "nt":
                        readable, _, exceptional = select.select([self.client_sock], [], [self.client_sock], 0.1)
                        if not input_line:
                            self.display_prompt()
                        key_input = self.check_windows_input()
                        if key_input:
                            if key_input == '\r':
                                print()
                                if input_line.lower() == "close":
                                    self.client_sock.close()
                                    return
                                self.send(input_line)
                                input_line = ""
                                self.awaiting_input = False
                            elif key_input == '\b':
                                if input_line:
                                    input_line = input_line[:-1]  # Remove last character
                                    print('\b \b', end='', flush=True)
                            else:
                                if key_input.isprintable():
                                    input_line += key_input
                                    print(key_input, end='', flush=True)
                                # clr_screen() # turn on in final
                    else:
                        readable, _, exceptional = select.select([self.client_sock, sys.stdin], [], [self.client_sock])

                        self.display_prompt()

                        for source in readable:
                            if source == sys.stdin:
                                request = input().strip()
                                if request.lower() == "close":
                                    self.client_sock.close()
                                    return
                                self.send(request)
                                self.awaiting_input = False

                    if self.client_sock in readable:
                        self.handle_response()

                    if exceptional:
                        print("Connection to the server has been lost!")
                        break

                except (RuntimeError, ValueError) as e:
                    print(f"Error: {e}")
                    logging.error(f"Error processing server response: {e}")
                    continue
                except ConnectionError as e:
                    logging.error(f"Connection to the host has been lost: {e}")
                    break
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
