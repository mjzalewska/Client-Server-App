import json
import logging
import socket
from datetime import datetime, timedelta
from time import sleep

from communication import CommunicationProtocol
from user_model import User
from utilities import load_menu_config, get_user_input, calculate_uptime, format_server_info


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
        self.user_commands = None
        self.admin_commands = None
        logging.basicConfig(filename='server.log', level=logging.INFO,
                            format='%(asctime)s - %(levelname)s - %(message)s')

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
            self.user_commands = load_menu_config("login_menu", "logged_out", "user")
            welcome_message = f"Connected to server at {self.host}"
            self._send(welcome_message, (self.user_commands, "list"))

        except OSError as e:
            logging.error(f"Server failed to start: {e}")
            raise
        except Exception as e:
            logging.error(f"An error occurred during server startup: {e}")
            raise

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

    def _send(self, message, data=None, status="success"):
        """
            Send messages with proper formatting and error handling.
            Handles business logic for message formatting and error responses.
        """
        try:
            message_to_send = self.com_protocol.format_message(message, data=data, status=status, )
            self.com_protocol._send(message_to_send)
        except ConnectionError as e:
            logging.error(f"Connection lost: {e}")
            raise
        except Exception as e:
            logging.error(f"Invalid message format: {e}")
            error_message = self.com_protocol.format_message(str(e), status="error")
            self.com_protocol._send(error_message)

    def _receive(self):
        """
        Receive and process a message from a client.

        Returns:
        Message: The received message object

        Raises:
        ConnectionError: If the client connection is lost
        RuntimeError: If there are problems processing the message
        """
        try:
            message = self.com_protocol._receive()
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
            self._send("Invalid message format", status="error")
            raise RuntimeError(f"Invalid message received from client: {e}") from e

    def _process_registration(self, required_fields):
        """Process new user registration"""
        try:
            user_data = get_user_input(self, required_fields)
            if User.register(username=user_data["username"], password=user_data["password"], email=user_data["email"]):
                self._send("Registration successful!", (self.user_commands, "list"))
        except ValueError as e:
            self._send(f"Registration failed: {e}", status="error")
            logging.info(f"Registration failed - validation error: {e}")
        except TypeError as e:
            self._send(f"Invalid input format!", status="error")
            logging.info(f"Registration failed - invalid input: {e}")
        except OSError as e:
            self._send(f"Registration failed. Please try again later!", status="error")
            logging.info(f"Registration failed due to the following error: {e}")

    def _process_account_deletion(self, username):
        """Process user account removal"""
        try:
            self._send(f"Are you sure you want to delete user {username}? Y/N")
            if self._receive()["message"].upper() == "Y":
                if User.delete(username):
                    self._send(f"User {username} deleted successfully!")
            self._send("Operation has been cancelled!")
            return

        except KeyError:
            self._send(f"Operation failed - user not found!", status="error")
            logging.info(f"Account removal failed - user {username} not found")
        except ValueError as e:
            self._send(f"Operation failed - invalid username format!", status="error")
            logging.info(f"Account deletion failed - invalid input: {e}")
        except OSError as e:
            self._send(f"Operation failed! Please try again later", status="error")
            logging.info(f"Account removal failed due to the following error: {e}")

    def _process_login(self):
        """Process user login"""
        while True:
            try:
                user_credentials = get_user_input(self, ["username", "password"])
                self.user = User.log_in(user_credentials["username"], user_credentials["password"])
                self._send("Logged in successfully")
                self.run_main_menu()
                break
            except (KeyError, ValueError) as e:
                logging.info(f"Login failed: {e}")
                self._send("Incorrect username or password!", status="error")
            except (TypeError, AttributeError) as e:
                logging.error(f"Registration failed due to system error: {e}")
                self._send("Incorrect input!", status="error")

    def _process_logout(self):
        self.user = None
        self._send("You have been successfully logged out!")
        self.run_main_menu()

    def _get_user_data(self, username=None):
        """Retrieve user information"""
        try:
            user_data = User.get(username)
            self._send("", (user_data, "tabular"))
        except KeyError as e:
            self._send(f"User {username} not found!", status="error")
            logging.info(f"Failed to retrieve user data - user not found: {e}")
        except ValueError as e:
            self._send(f"Invalid username format!", status="error")
            logging.info(f"Failed to retrieve user data - invalid data format: {e}")
        except OSError as e:
            self._send(f"Operation failed! Please try again later", status="error")
            logging.info(f"Failed to retrieve user data due to the following error: {e}")

    def run_main_menu(self):
        """Displays the main menu based on user role."""
        if not self.user:
            self.user_commands = load_menu_config("login_menu", "logged_out", "user")
            self._send("Please log in or register", (self.user_commands, "list"))
        elif self.user.role == "admin":
            self.admin_commands = load_menu_config("login_menu", "logged_in", "admin")
            self._send("Admin Main Menu", (self.admin_commands, "list"))
        elif self.user.role == "user":
            self.user_commands = load_menu_config("login_menu", "logged_in", "user")
            self._send("User Main Menu", (self.user_commands, "list"))

    def run_manage_users_menu(self):
        while True:
            self.admin_commands = load_menu_config("manage_users_menu", "logged_in", "admin")
            self._send("User management menu", (self.admin_commands, "list"))
            command = self._receive()["message"]
            if command.casefold() in self.admin_commands.keys():
                match command.casefold():
                    case "add":
                        required_fields = ["username", "password", "email", "user role"]
                        user_data = get_user_input(self, required_fields)
                        if User.register(user_data["username"], user_data["password"], user_data["email"],
                                         user_data["user role"]):
                            self._send(f"User {user_data['username']} added successfully!")
                        else:
                            self._send("Operation failed!", status="error")
                            logging.error(f"New user signup failed for username: {user_data['username']}")
                    case "delete":
                        required_fields = ["username"]
                        username = get_user_input(self, required_fields)["username"]
                        self._process_account_deletion(username)
                    case "show":
                        self._send("Enter username: ")
                        username = self._receive()["message"]
                        self._get_user_data(username)
                    case "show all":
                        self._get_user_data()
                        continue
                    case "return":
                        self.admin_commands = load_menu_config("login_menu", "logged_in", "admin")
                        self._send("Admin Main Menu", (self.admin_commands, "list"))
                        return
                    case "help":
                        self._send("User management menu", (self.admin_commands, "list"))

            else:
                self._send("Unknown request. Choose correct command!", (self.admin_commands, "list"), status="error")
                logging.error(f"Bad request received from {self.address[0]}:{self.address[1]}")

    def run_user_menu(self, command):
        if command.casefold() in self.user_commands.keys():
            match command.casefold():
                case "inbox":
                    print("This is your inbox")
                case "info":
                    self._get_user_data(self.user.username)
                case "help":
                    self._send("This server can run the following commands: ", (self.user_commands, "list"))
                case "sign out":
                    self._process_logout()
                case "disconnect":
                    pass
        else:
            self._send("Unknown request. Choose correct command!", (self.user_commands, "list"), status="error")
            logging.error(f"Bad request received from {self.address[0]}:{self.address[1]}")

    def run_admin_menu(self, command):
        if command.casefold() in self.admin_commands.keys():
            match command.casefold():
                case "info":
                    self._send(f"version: {self.version}, build: {self.build_date}")
                case "uptime":
                    uptime = calculate_uptime(self.start_time)
                    self._send(f"server uptime (hh:mm:ss): {uptime}")
                case "help":
                    self._send("This server can run the following commands: ", (self.admin_commands, "list"))
                case "close":
                    print("Shutting down...")
                    sleep(2)
                    self.connection.close()
                    exit()
                case "users":
                    self.run_manage_users_menu()
                case "inbox":
                    pass
                case "sign out":
                    self._process_logout()
        else:
            self._send("Unknown request. Choose correct command!", (self.admin_commands, "list"), "error")
            logging.error(f"Bad request received from {self.address[0]}:{self.address[1]}")

    def run(self):
        try:
            self.start_server()
            while True:
                try:
                    client_msg = self._receive()["message"]
                    if not self.user or not self.user.is_logged_in:
                        self.user_commands = load_menu_config("login_menu", "logged_out", "user")
                        if client_msg in self.user_commands.keys():
                            match client_msg:
                                case "log in":
                                    self._process_login()
                                case "register":
                                    self._process_registration(["username", "password", "email"])
                        else:
                            self._send("Unknown request. Choose correct command!", (self.user_commands, "list"),
                                       "error")
                            logging.error(f"Bad request received from {self.address[0]}:{self.address[1]}")
                    else:
                        if self.user.role == "user":
                            self.run_user_menu(client_msg)
                        elif self.user.role == "admin":
                            self.run_admin_menu(client_msg)
                except ConnectionError:
                    print("Connection has been lost!")
                    exit()

                except RuntimeError as e:
                    logging.error(f"Error processing message from {self.address}: {e}")
                    try:
                        self._send("An error occurred processing your request. Please try again.", status="error")
                        if not self.user or not self.user.is_logged_in:
                            self._send("Available commands:", (self.user_commands, "list"))
                    except ConnectionError:
                        logging.error(f"Could not send error message to client {self.address}")
                        break
        finally:
            self.cleanup()
            logging.info("Server shutdown complete")


if __name__ == "__main__":
    server = Server(55555)
    server.run()

# manage users menu:
# - opóźnienie w przypadku wywoałania komend (od 1 do 3x)
# - problem z return


# sending messages - 5 messages per inbox for regular user, no limit for admin
# limit exceeded alert for the sender
# message len limit - 255 chars

# data validation for email and password len
# hide chars when typing password?
# to return error messages (user already exists, error when operation failed, etc.) - user model
# refactor the app to use select
