import logging
import socket
from datetime import datetime
from logging.handlers import RotatingFileHandler
from time import sleep
from communication import CommunicationProtocol
from menu import Menu
from user_model import User
from utilities import get_user_input


class Server:
    def __init__(self, port, server_sock=None):
        self.host = "127.0.0.1"
        self.port = port
        self.buffer = 1024
        try:
            if server_sock is None:
                self.server_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            else:
                self.server_sock = server_sock
        except socket.error as e:
            logging.error(f"Failed to create server socket: {e}")
            raise
        self.connection = None
        self.address = None
        self.com_protocol = None
        self.version = "1.1.0"
        self.build_date = "2023-12-03"
        self.start_time = datetime.now()
        self.user = None
        self.menu = Menu(self)
        logging.basicConfig(handlers=[RotatingFileHandler('server.log', maxBytes=5*1024*1024, backupCount=5)],
                            level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')

    def start_server(self):
        """
        Start the server and handle a single client connection.

        This method:
            1. Binds and starts listening on the specified port
            2. Accepts  client connection
            3. Sets up the communication protocol
            4. Sends the initial welcome message and available commands

        Raises:
            OSError: If binding or listening fails
            ConnectionError: If accepting the connection fails
        """
        try:
            self.server_sock.bind((self.host, self.port))
            self.server_sock.listen()
            print(f"Listening on {self.host}:{self.port}")
            self.connection, self.address = self.server_sock.accept()
            logging.info(f"Accepted connection from {self.address[0]}:{self.address[1]}")
            print(f"Accepted connection from {self.address[0]}:{self.address[1]}")
            self.com_protocol = CommunicationProtocol(self.connection)
            welcome_message = f"Connected to server at {self.host}"
            self.send(welcome_message, prompt=False)
        except OSError as e:
            logging.error(f"Server failed to start: {e}")
            raise
        except Exception as e:
            logging.error(f"An error occurred during server startup: {e}")
            raise

    def run_main_menu(self):
        """Initialize and display main menu"""
        self.menu.update_menu_state()

    def cleanup(self):
        """Cleans up resources after connection has been closed"""
        if self.connection:
            try:
                self.connection.close()
            except Exception as e:
                logging.error(f"Error closing connection: {e}")
        if self.server_sock:
            try:
                self.server_sock.close()
            except Exception as e:
                logging.error(f"Error closing server socket: {e}")

    def send(self, message, data=None, status="success", prompt=True):
        """
            Send messages with proper formatting and error handling.
            Handles business logic for message formatting and error responses.
        """
        try:
            if not message and not data:
                return
            message_to_send = self.com_protocol.format_message(message, data=data, status=status)
            self.com_protocol.send(message_to_send)

            if prompt and ((data and data[1] == "list") or (message and not data)): ### spr część (message and not data)
                ready_signal = self.com_protocol.format_message("", status="ready_for_input")
                self.com_protocol.send(ready_signal)

        except ConnectionError as e:
            logging.error(f"Connection lost: {e}")
            raise
        except Exception as e:
            logging.error(f"Invalid message format: {e}")
            error_message = self.com_protocol.format_message(str(e), status="error")
            self.com_protocol.send(error_message)

    def receive(self):
        """
        Receive and process a message from a client.
        """
        try:
            message = self.com_protocol.receive()
            return message

        except BrokenPipeError as e:
            logging.error(f"Client {self.address} has closed the connection")
            self.connection.close()
            raise ConnectionError("Client disconnected") from e

        except ConnectionResetError as e:
            logging.error(f"Connection to client {self.address} was forcefully closed")
            self.connection.close()
            raise ConnectionError("Client connection lost") from e

        except ValueError as e:
            logging.error(f"Received invalid message from client {self.address}: {e}")
            self.send("Invalid message format", status="error")
            raise RuntimeError(f"Invalid message received from client: {e}") from e

    def process_registration(self, required_fields):
        """Process new user registration"""
        try:
            user_data = get_user_input(self, required_fields)
            if User.register(username=user_data["username"], password=user_data["password"], email=user_data["email"]):
                self.send(f"User {user_data['username']} added successfully!") #, (self.user_commands, "list"))
        except ValueError as e:
            self.send(f"Registration failed: {e}", status="error")
            logging.info(f"New user signup failed for username: {user_data['username']}: {e}")
        except TypeError as e:
            self.send(f"Invalid input format!", status="error")
            logging.info(f"New user signup failed for username: {user_data['username']}: {e}")
        except OSError as e:
            self.send(f"Registration failed. Please try again later!", status="error")
            logging.info(f"New user signup failed for username {user_data['username']}  to the following error: {e}")

    def process_account_deletion(self, username):
        """Process user account removal"""
        try:
            self.send(f"Are you sure you want to delete user {username}? Y/N")
            if self.receive()["message"].upper() == "Y":
                if User.delete(username):
                    self.send(f"User {username} deleted successfully!", prompt=False)
            self.send("Operation has been cancelled!")
            return

        except KeyError:
            self.send(f"Operation failed - user not found!", status="error")
            logging.info(f"Account removal failed - user {username} not found")
        except ValueError as e:
            self.send(f"Operation failed - invalid username format!", status="error")
            logging.info(f"Account deletion failed - invalid input: {e}")
        except OSError as e:
            self.send(f"Operation failed! Please try again later", status="error")
            logging.info(f"Account removal failed due to the following error: {e}")

    def process_login(self):
        """Process user login"""
        while True:
            try:
                user_credentials = get_user_input(self, ["username", "password"])
                self.user = User.log_in(user_credentials["username"], user_credentials["password"])
                break
            except (KeyError, ValueError) as e:
                logging.info(f"Login failed: {e}")
                self.send("Incorrect username or password!", status="error", prompt=False)
            except (TypeError, AttributeError) as e:
                logging.error(f"Login failed due to system error: {e}")
                self.send("Incorrect input!", status="error", prompt=False)

    def process_logout(self):
        self.user = None
        self.send("You have been successfully logged out!", prompt=False)
        sleep(0.1)
        self.run_main_menu()

    def get_user_data(self, username=None):
        """Retrieve user information"""
        try:
            user_data = User.get(username)
            self.send("", (user_data, "tabular"))
        except KeyError as e:
            self.send(f"User {username} not found!", status="error")
            logging.info(f"Failed to retrieve user data - user not found: {e}")
        except ValueError as e:
            self.send(f"Invalid username format!", status="error")
            logging.info(f"Failed to retrieve user data - invalid data format: {e}")
        except OSError as e:
            self.send(f"Operation failed! Please try again later", status="error")
            logging.info(f"Failed to retrieve user data due to the following error: {e}")

    def run(self):
        try:
            self.start_server()
            self.run_main_menu()
            while True:
                try:
                    client_msg = self.receive()["message"]

                    if not self.menu.handle_command(client_msg):
                        continue
                except ConnectionAbortedError:
                    print("Client disconnected. Waiting for new connection...")
                    break
                except ConnectionError:
                    print("Connection has been lost!")
                    exit()
                except RuntimeError as e:
                    logging.error(f"Error processing message from {self.address}: {e}")
                    try:
                        self.send("An error occurred processing your request. Please try again.", status="error")
                        if not self.user or not self.user.is_logged_in:
                            self.menu.update_menu_state()
                    except ConnectionError:
                        logging.error(f"Could not send error message to client {self.address}")
                        break
        finally:
            self.cleanup()
            logging.info("Server shutdown complete")


if __name__ == "__main__":
    server = Server(55555)
    server.run()


# sending messages - 5 messages per inbox for regular user, no limit for admin
# limit exceeded alert for the sender
# message len limit - 255 chars

# data validation for email and password len
# hide chars when typing password?
# refactor the app to use select
