import json
import logging
import socket
from datetime import datetime, timedelta
from time import sleep

from communication import CommunicationProtocol
from user_model import User
from utilities import load_menu_config


class Server:
    def __init__(self, port, server_sock=None):
        self.host = "127.0.0.1"
        self.port = port
        self.buffer = 1024
        if server_sock is None:
            self.server_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        else:
            self.server_sock = server_sock
        self.com_protocol = None
        self.connection = None
        self.address = None
        self.version = "1.1.0"
        self.build_date = "2023-12-03"
        self.start_time = datetime.now()
        self.user = None
        self.user_commands = None
        self.admin_commands = None
        logging.basicConfig(filename='server.log', level=logging.INFO,
                            format='%(asctime)s - %(levelname)s - %(message)s')

    def start_server(self):
        with self.server_sock as s:
            s.bind((self.host, self.port))
            s.listen()
            print(f"Listening on {self.host}:{self.port}")
            self.connection, self.address = s.accept()
            self.com_protocol = CommunicationProtocol(self.connection)
            print(f"Accepted connection from {self.address[0]}:{self.address[1]}")
            self.user_commands = load_menu_config("login_menu", "logged_out", "user")
            self.send(f"Successfully connected to: {self.host}", (self.user_commands, "list"))

    def send(self, message, data=None, status="success"):
        """
            Send messages with proper formatting and error handling.
            Handles business logic for message formatting and error responses.
        """
        try:
            message_to_send = self.com_protocol.format_message(message, data=data, status=status, )
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
        header = self.connection.recv(4)
        if not header:
            raise ValueError
        while True:
            try:
                msg_len = int.from_bytes(header[0:4], byteorder="big")
                while bytes_recv < msg_len:
                    msg_part = self.connection.recv(min(msg_len - bytes_recv, self.buffer))
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

    def register(self, required_fields):
        user_data = self.get_user_input(required_fields)
        if User.register(user_data["username"], user_data["password"], user_data["email"]):
            self.send("Sign up successful!", (self.user_commands, "list"))
        else:
            self.send("Operation failed!", status="error")

    def log_in(self):
        while True:
            required_fields = ["username", "password"]
            user_data = self.get_user_input(required_fields)
            self.user = User.log_in(user_data["username"], user_data["password"])
            if self.user is not None:
                self.send("Logged in successfully!")
                self.run_main_menu()
                break
            else:
                self.send("Incorrect username or password!", status="error")
                logging.error(f"Failed login attempt for username: {user_data['username']}")

    def log_out(self):
        self.user = None
        self.send("You have been successfully logged out!")
        self.run_main_menu()

    def calculate_uptime(self):
        request_time = datetime.now()
        time_diff = (request_time - self.start_time).seconds
        uptime_val = str(timedelta(seconds=time_diff))
        return uptime_val

    def get_users(self, username=None):
        user_data = User.get(username)
        self.send("", (user_data, "tabular"))

    def get_user_input(self, fields):
        user_data = {}
        for field in fields:
            self.send(f"Enter {field}: ")
            user_data[field] = self.receive()["message"]
        return user_data

    def run_main_menu(self):
        """Displays the main menu based on user role."""
        if not self.user:
            self.user_commands = load_menu_config("login_menu", "logged_out", "user")
            self.send("Please log in or register", (self.user_commands, "list"))
        elif self.user.role == "admin":
            self.admin_commands = load_menu_config("login_menu", "logged_in", "admin")
            self.send("Admin Main Menu", (self.admin_commands, "list"))
        elif self.user.role == "user":
            self.user_commands = load_menu_config("login_menu", "logged_in", "user")
            self.send("User Main Menu", (self.user_commands, "list"))

    def run_manage_users_menu(self):
        while True:
            self.admin_commands = load_menu_config("manage_users_menu", "logged_in", "admin")
            self.send("User management menu", (self.admin_commands, "list"))
            command = self.receive()["message"]
            if command.casefold() in self.admin_commands.keys():
                match command.casefold():
                    case "add":
                        required_fields = ["username", "password", "email", "user role"]
                        user_data = self.get_user_input(required_fields)
                        if User.register(user_data["username"], user_data["password"], user_data["email"],
                                         user_data["user role"]):
                            self.send(f"User {user_data['username']} added successfully!")
                        else:
                            self.send("Operation failed!", status="error")
                            logging.error(f"New user signup failed for username: {user_data['username']}")
                    case "delete":
                        required_fields = ["username"]
                        username = self.get_user_input(required_fields)["username"]
                        self.send(f"Are you sure you want to delete user {username}? Y/N")
                        client_reply = self.receive()["message"]
                        if client_reply.upper() == "Y":
                            if User.delete_account(username):
                                self.send(f"User {username} deleted successfully!")
                            else:
                                self.send(f"User {username} does not exist!", status="error")  # update error message
                    case "show":
                        self.send("Enter username: ")
                        username = self.receive()["message"]
                        self.get_users(username)
                    case "show all":
                        self.get_users()
                        continue
                    case "return":
                        self.send("")  # change
                        return
                    case "help":
                        self.send("User management menu", (self.admin_commands, "list"))
                        self.admin_commands = load_menu_config("login_menu", "logged_in", "admin")
                        self.send("Admin Main Menu", (self.admin_commands, "list"))
            else:
                self.send("Unknown request. Choose correct command!", (self.admin_commands, "list"), status="error")
                logging.error(f"Bad request received from {self.address[0]}:{self.address[1]}")

    def run_user_menu(self, command):
        if command.casefold() in self.user_commands.keys():
            match command.casefold():
                case "inbox":
                    print("This is your inbox")
                case "info":
                    self.get_users(self.user.username)
                case "help":
                    self.send("This server can run the following commands: ", (self.user_commands, "list"))
                case "sign out":
                    self.log_out()
                case "disconnect":
                    pass
        else:
            self.send("Unknown request. Choose correct command!", (self.user_commands, "list"), status="error")
            logging.error(f"Bad request received from {self.address[0]}:{self.address[1]}")

    def run_admin_menu(self, command):
        if command.casefold() in self.admin_commands.keys():
            match command.casefold():
                case "info":
                    self.send(f"version: {self.version}, build: {self.build_date}")
                case "uptime":
                    uptime = self.calculate_uptime()
                    self.send(f"server uptime (hh:mm:ss): {uptime}")
                case "help":
                    self.send("This server can run the following commands: ", (self.admin_commands, "list"))
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
                    self.log_out()
        else:
            self.send("Unknown request. Choose correct command!", (self.admin_commands, "list"), "error")
            logging.error(f"Bad request received from {self.address[0]}:{self.address[1]}")

    def run(self):
        self.start_server()
        while True:
            try:
                client_msg = self.receive()["message"]
                if not self.user or not self.user.is_logged_in:
                    self.user_commands = load_menu_config("login_menu", "logged_out", "user")
                    if client_msg in self.user_commands.keys():
                        match client_msg:
                            case "log in":
                                self.log_in()
                            case "register":
                                self.register(["username", "password", "email"])
                    else:
                        self.send("Unknown request. Choose correct command!", (self.user_commands, "list"), "error")
                        logging.error(f"Bad request received from {self.address[0]}:{self.address[1]}")
                else:
                    if self.user.role == "user":
                        self.run_user_menu(client_msg)
                    elif self.user.role == "admin":
                        self.run_admin_menu(client_msg)
            except ConnectionError:
                print("Connection has been lost!")
                exit()
            except Exception as e:
                print(e)
                exit()


if __name__ == "__main__":
    server = Server(65000)
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
# refactor receive
# refactor the app to use select
