import logging
import socket
from datetime import datetime
from logging.handlers import RotatingFileHandler
from time import sleep
from communication import CommunicationProtocol
from menu import Menu
from user import User
from message import Message
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
        self.message = Message()
        self.menu = Menu(self)
        logging.basicConfig(handlers=[RotatingFileHandler('server.log', maxBytes=5 * 1024 * 1024, backupCount=5)],
                            level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')

    def start_server(self):
        """
        Start the server and handle a single client connection.
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
                self.connection.shutdown(socket.SHUT_RDWR)
                self.connection.close()
            except Exception as e:
                logging.error(f"Error closing client connection: {e}")
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

            if prompt:
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
        user_data = get_user_input(self, required_fields)
        try:
            if not self.user:
                if User.register(username=user_data["username"], password=user_data["password"],
                                 email=user_data["email"]):
                    self.send(f"User {user_data['username']} added successfully!", prompt=False)
            elif self.user.role == "admin":
                if User.register(username=user_data["username"], password=user_data["password"],
                                 email=user_data["email"], role=user_data["role"]):
                    self.send(f"User {user_data['username']} added successfully!", prompt=False)
        except ValueError as e:
            self.send(f"Registration failed: {e}", status="error")
            logging.info(f"New user signup failed for username: {user_data['username']}: {e}")
        except TypeError as e:
            self.send(f"Invalid input format!", status="error")
            logging.info(f"New user signup failed for username: {user_data['username']}: {e}")
        except OSError as e:
            self.send(f"Registration failed. Please try again later!", status="error")
            logging.info(f"New user signup failed for username {user_data['username']} due to the following error: {e}")

    def process_account_deletion(self, username):
        """Process user account removal"""
        try:
            self.send(f"Are you sure you want to delete user {username}? Y/N")
            if self.receive()["message"].upper() == "Y":
                if User.delete(username):
                    self.send(f"User {username} deleted successfully!")
            else:
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

    def get_user_data(self, username=None):
        """Retrieve single user information"""
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

    def get_all_users(self):
        """Retrieve and display data for all users"""
        try:
            user_data = User.get()
            if user_data:
                self.send("All Users:", (user_data, "tabular"))
            else:
                self.send("No users found in the system.")
        except Exception as e:
            logging.error(f"Failed to retrieve user data: {e}")
            self.send("Failed to retrieve user data", status="error")

    def get_user_inbox(self):
        """Retrieve contents of user inbox"""
        try:
            inbox_contents = self.message.get_inbox(self.user.username)
            self.send("Inbox: ", (inbox_contents, "inbox"))
        except TypeError as e:
            logging.error(f"Failed to retrieve inbox for user {self.user.username}:{e}")
            self.send(f"Could not display inbox for user {self.user.username}: invalid username format", status="error")
        except KeyError as e:
            logging.error(f"Failed to retrieve inbox for user {self.user.username}:{e}")
            self.send(f"Could not display inbox for user {self.user.username}: user not found", status="error")
        except Exception as e:
            logging.error(f"Failed to  retrieve inbox for user {self.user.username}: {e}")
            self.send(f" Failed to display inbox for user {self.user.username}", status="error")

    def process_writing_message(self, required_fields):
        message_data = get_user_input(self, required_fields)
        try:
            self.message.compose(recipient=message_data["recipient"], sender=self.user.username,
                                 from_email=self.user.email, to_email=message_data["to_email"],
                                 subject=message_data["subject"], body=message_data["body"])
        except ValueError as e:
            if "length error" in str(e):
                self.send(f"Message length limit ({self.message.chars_limit}chars) exceeded. Please try again",
                          status="error")
                logging.info(f"Failed to initialize new message: {e}")
            else:
                self.send("Recipient name and/or e-mail cannot be empty!", status="error")
                logging.info(f"Failed to initialize new message: {e}")
        except TypeError as e:
            self.send(f"Invalid data input format!", status="error")
            logging.info(f"Failed to initialize new message: {e}")
        except Exception as e:
            self.send("An unexpected error occurred. Please try again", status="error")
            logging.info(f"Failed to initialize new message: {e}")

    def process_reading_message(self, required_fields):
        message_id = get_user_input(self, required_fields)["id"]
        try:
            self.message.read(username=self.user.username, message_id=message_id)
        except TypeError as e:
            if "username" in str(e):
                self.send(f"Couldn't retrieve message. User {self.user.username} not found!", status="error")
                logging.info(f"Failed to retrieve message no {message_id} for user {self.user.username}:{e}")
            else:
                self.send(f"Error retrieving message. Message id must be an integer", status="error")
                logging.info(f"Failed to retrieve message no {message_id} for user {self.user.username}: {e}")
        except KeyError as e:
            if "User" in str(e):
                self.send(f"Couldn't retrieve message. User {self.user.username} not found!", status="error")
                logging.info(f"Failed to retrieve message no {message_id} for user {self.user.username}: {e}")
            else:
                self.send(f"Couldn't retrieve message. Message not found!", status="error")
                logging.info(f"Failed to retrieve message no {message_id} for user {self.user.username}:{e}")
        except ValueError as e:
            self.send("Message id field cannot be empty!", status="error")
            logging.info(f"Failed to retrieve message for user {self.user.username}: {e}")
        except Exception as e:
            self.send("An unexpected error occurred. Please try again", status="error")
            logging.info(f"Failed to retrieve message {message_id}: {e}")

    def process_deleting_message(self, required_fields):
        message_id = get_user_input(self, required_fields)["id"]
        try:
            self.message.delete(username=self.user.username, message_id=message_id)
        except TypeError as e:
            self.send("Could not delete message. Incorrect message id", status="error")
            logging.info(f"Failed to delete message: {e}")
        except ValueError as e:
            self.send("Message id cannot be empty", status="error")
            logging.info(f"Failed to delete message: {e}")
        except KeyError as e:
            self.send("Could not delete message. Message not found", status="error")
            logging.info(f"Failed to delete message: {e}")

    def run(self):
        try:
            self.start_server()
            self.run_main_menu()
            while True:
                try:
                    client_msg = self.receive()["message"]
                    if not client_msg:
                        logging.info("Client closed connection")
                        break
                    if not self.menu.handle_command(client_msg):
                        logging.info("Client requested shutdown - closing connection")
                        break
                except ConnectionError as e:
                    print(f"Connection has been lost: {e}")
                    break
                except RuntimeError as e:
                    logging.error(f"Error processing message from {self.address}: {e}")
                    try:
                        self.send("An error occurred processing your request. Please try again.", status="error")
                        if not self.user or not self.user.is_logged_in:
                            self.menu.update_menu_state()
                    except ConnectionError:
                        logging.error(f"Failed to send error message to client {self.address}")
                        break
                except Exception as e:
                    logging.error(f"Unexpected error: {e}")
                    try:
                        if self.connection and self.connection.fileno() != -1:
                            self.send("An error occurred. Please try again.", status="error")
                    except (ConnectionError, OSError) as e:
                        logging.error(f"Failed to send error message - connection lost: {e}")
                        break
                    except Exception as e:
                        logging.error(f"Failed to send error message - unexpected error: {e}")
                        break
        finally:
            self.cleanup()
            logging.info("Server shutdown complete")


if __name__ == "__main__":
    server = Server(55555)
    server.run()
