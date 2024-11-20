import json
import socket
from datetime import datetime, timedelta
from time import sleep
from user import User
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
        self.version = "1.1.0"
        self.build_date = "2023-05-13"
        self.start_time = datetime.now()
        self.user = None
        self.user_commands = None
        self.admin_commands = None
        self.connection = None
        self.address = None

    def start_server(self):
        with self.server_sock as s:
            s.bind((self.host, self.port))
            s.listen()
            print(f"Listening on {self.host}:{self.port}")
            self.connection, self.address = s.accept()
            print(f"Accepted connection from {self.address[0]}:{self.address[1]}")
            self.user_commands = load_menu_config("login_menu", "logged_out", "user")
            self.send({"status": "success",
                       "message": f"Successfully connected to: {self.host}",
                       "data": self.user_commands,
                       "event_type": "info"
                       })

    def send(self, msg):
        try:
            message = json.dumps(msg).encode("utf-8")
            message_len = len(message).to_bytes(4, byteorder="big")
            self.connection.sendall(message_len + message)
        except json.decoder.JSONDecodeError:
            print("Invalid message format")
            exit()

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
                           "data": "",
                           "event": ""})
                exit()
            data = b"".join(msg_parts)
            message = json.loads(data.decode("utf-8").strip())
            return message

    def sign_up(self):
        while True:
            self.send({"status": "success",
                       "message": "Enter username: ",
                       "data": {},
                       "event": ""})
            username = self.receive()["message"]
            self.send({"status": "success",
                       "message": "Enter password: ",
                       "data": {},
                       "event": ""})
            password = self.receive()["message"]
            self.send(({"status": "success",
                        "message": "Enter email address: ",
                        "data": {},
                        "event": ""}))
            email = self.receive()["message"]
            if User.add(username, password, email):
                # self.user_commands = load_menu_config("login_menu", "logged_out", "user")
                self.send({"status": "success",
                           "message": "Sign up successful!",
                           "data": self.user_commands,
                           "event": ""})
                break
            else:
                self.send({"status": "error",
                           "message": "Username already in use!",
                           "data": {},
                           "event": ""})
                continue

    def log_in(self):
        # after login data input incorrectly and then correctly keeps displaying error
        # problem most likely on client side (processing messages with no input expected)
        while True:
            self.send({"status": "success",
                       "message": "Enter username: ",
                       "data": {},
                       "event": ""})
            user_name = self.receive()["message"]
            self.send({"status": "success",
                       "message": "Enter password: ",
                       "data": {},
                       "event": ""})
            password = self.receive()["message"]
            self.user = User.log_in(user_name, password)
            if self.user is not None:
                self.send({"status": "success",
                           "message": "Logged in successfully!",
                           "data": {},
                           "event": ""})
                self.display_main_menu()
                break
            else:
                self.send({"status": "error",
                           "message": "Incorrect username or password!",
                           "data": {},
                           "event": ""})

    def log_out(self):
        self.user = None
        self.send({"status": "success",
                   "message": "You have been successfully logged out!",
                   "data": {},
                   "event": ""})
        self.display_main_menu()

    def calculate_uptime(self):
        request_time = datetime.now()
        time_diff = (request_time - self.start_time).seconds
        uptime_val = str(timedelta(seconds=time_diff))
        return uptime_val

    def get_users(self, username=None):  # remove??
        user_data = User.get(username)
        self.send({"status": "success",
                   "message": "",
                   "data": user_data,
                   "event": ""})

    def get_user_input(self, fields):
        user_data = {}
        for field in fields:
            self.send({"status": "success",
                       "message": f"Enter {field}: ",
                       "data": {},
                       "event": ""})
            user_data[field] = self.receive()["message"]
        return user_data

    def display_main_menu(self):
        """Displays the main menu based on user role."""
        if not self.user:
            self.user_commands = load_menu_config("login_menu", "logged_out", "user")
            self.send({"status": "success",
                       "message": "Please log in or register",
                       "data": self.user_commands,
                       "event": ""})
        elif self.user.role == "admin":
            self.admin_commands = load_menu_config("login_menu", "logged_in", "admin")
            self.send({"status": "success",
                       "message": "Admin Main Menu",
                       "data": self.admin_commands,
                       "event": ""})
        elif self.user.role == "user":
            self.user_commands = load_menu_config("login_menu", "logged_in", "user")
            self.send({"status": "success",
                       "message": "User Main Menu",
                       "data": self.user_commands,
                       "event": ""})

    def manage_users(self):
        while True:
            # self.admin_commands = load_menu_config("manage_users_menu", "logged_in", "admin")
            # user_menu_commands = {"add": "add new account",
            #                       "delete": "remove account",
            #                       "show": "show selected user record",
            #                       "show all": "show all users",
            #                       "return": "return to previous screen "}
            self.send({"status": "success",
                       "message": "User management",
                       "data": self.admin_commands,
                       "event": ""})
            command = self.receive()["message"]
            if command.casefold() in self.admin_commands.keys():
                match command:
                    case "add":
                        required_fields = ["username", "password", "email", "user role"]
                        user_data = self.get_user_input(required_fields)
                        if User.add(user_data["username"], user_data["password"], user_data["email"],
                                    user_data["user role"]):
                            self.send({"status": "success",
                                       "message": f"User {user_data['username']} added successfully!",
                                       "data": {},
                                       "event": ""})
                        else:
                            self.send({"status": "error",
                                       "message": "Operation failed!",
                                       "data": {},
                                       "event": ""})  # specify the error
                        continue
                    case "delete":
                        self.send({"status": "success",
                                   "message": "Enter username: ",
                                   "data": {},
                                   "event": ""})
                        username = self.receive()["message"]
                        self.send({"status": "success",
                                   "message": f"Are you sure you want to delete user {username}? Y/N",
                                   "data": {},
                                   "event": ""})
                        client_reply = self.receive()["message"]
                        if client_reply.upper() == "Y":
                            if User.remove(username):
                                self.send({"status": "success",
                                           "message": f"User {username} deleted successfully!",
                                           "data": {},
                                           "event": ""})
                            else:
                                continue
                            continue

                    case "show":
                        self.send({"status": "success",
                                   "message": "Enter username: ",
                                   "data": {},
                                   "event": ""})
                        username = self.receive()["message"]
                        self.get_users(username)
                    case "show all":
                        self.get_users()
                        continue
                    case "return":
                        self.send({"status": "success",
                                   "message": "",
                                   "data": {},
                                   "event": "exit_to_main_menu"})
                        break
        self.display_main_menu()

    def run_user_commands(self, command):
        if command.casefold() in self.user_commands.keys():
            match command:
                case "inbox":
                    print("This is your inbox")
                case "help":
                    self.send({"status": "success",
                               "message": "This server can run the following commands: ",
                               "data": self.user_commands,
                               "event": ""})
                case "sign out":
                    self.log_out()
                case "disconnect":
                    pass
        else:
            self.send({"status": "error",
                       "message": "Unknown request (user commands)!",
                       "data": {},
                       "event": ""})

    def run_admin_commands(self, command):
        if command.casefold() in self.admin_commands.keys():
            match command:
                case "info":
                    self.send({"status": "success",
                               "message": f"version: {self.version}, build: {self.build_date}",
                               "data": {},
                               "event": ""})
                case "uptime":
                    uptime = self.calculate_uptime()
                    self.send({"status": "success",
                               "message": f"server uptime (hh:mm:ss): {uptime}",
                               "data": {},
                               "event": ""})
                case "help":
                    self.send({"status": "success",
                               "message": "This server can run the follwing commands: ",
                               "data": self.admin_commands,
                               "event": ""})
                case "close":
                    print("Shutting down...")
                    sleep(2)
                    self.connection.close()
                    exit()
                case "users":
                    self.manage_users()
                case "inbox":
                    pass
                case "sign out":
                    self.log_out()
        else:
            self.send({"status":"error",
                       "message": "Unknown request(admin commands)!",
                       "data": {},
                       "event": ""})

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
                                self.sign_up()
                    else:
                        self.send({"status": "error",
                                   "message": "Unknown request (run loop)!",
                                   "data": {},
                                   "event": ""})
                else:
                    if self.user.role == "user":
                        self.user_commands = load_menu_config("login_menu", "logged_in", "user")
                        self.run_user_commands(client_msg)
                    elif self.user.role == "admin":
                        self.admin_commands = load_menu_config("login_menu", "logged_in", "admin")
                        self.run_admin_commands(client_msg)
            except ConnectionError:
                print("Connection has been lost!")
                exit()
            except Exception as e:
                print(e)
                exit()


if __name__ == "__main__":
    server = Server(65000)
    server.run()

# refactor client-server communication protocol
# handle client behaviour when server sends a message but no response is expected - e.g.:
# # status: Used to indicate a status like "success", "error", or "exit_submenu".
# # message: General user-facing messages.
# # data: Any data or additional information the client needs.
# to return error messages (user already exists, error when operation failed, etc.) - user model

# sending messages - 5 messages per inbox for regular user, no limit for admin
# limit exceeded alert for the sender
# message len limit - 255 chars

# refactor the app to use select
