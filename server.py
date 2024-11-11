import json
import socket
from datetime import datetime, timedelta
from prettytable import PrettyTable
from time import sleep
from user import User


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
        self.user_commands = \
            {
                "logged_out": {
                    "log in": "log in to an existing account",
                    "register": "create a new account",
                    "disconnect": "disconnect"
                },
                "is_logged_in": {
                    "sign out": "log out",
                    "inbox": "go to inbox",
                    "help": "display available commands"
                }
            }
        self.admin_commands = \
            {
                "is_logged_in": {
                    "close": "stop server and client",
                    "help": "display available commands",
                    "inbox": "go to inbox",
                    "info": "display server version and build date",
                    "sign out": "log out",
                    "uptime": "display server uptime",
                    "users": "see registered users",
                }
            }
        self.connection = None
        self.address = None
        self.db = "users.json"

    def start_server(self):
        with self.server_sock as s:
            s.bind((self.host, self.port))
            s.listen()
            print(f"Listening on {self.host}:{self.port}")
            self.connection, self.address = s.accept()
            print(f"Accepted connection from {self.address[0]}:{self.address[1]}")
            self.send([{"message1": f"Successfully connected to: {self.host}"},
                       {"message2": self.user_commands["logged_out"]}])

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
                self.send([{"error": "Invalid message format: missing header!"}])
                exit()
            data = b"".join(msg_parts)
            message = json.loads(data.decode("utf-8").strip())
            return message

    def sign_up(self):
        while True:
            self.send([{"message": "Enter username: "}])
            username = self.receive()["message"]
            self.send([{"message": "Enter password: "}])
            password = self.receive()["message"]
            self.send([{"message": "Enter email: "}])
            email = self.receive()["message"]
            print()
            if User.add(username, password, email):
                self.send([{"message1": "Sign up successful!"},
                           {"message2": self.user_commands["logged_out"]}])
                break
            else:
                self.send([{"error": "Username already in use!"}])
                print("\n")
                continue

    def log_in(self):
        while True:
            self.send([{"message": "Enter username: "}])
            user_name = self.receive()["message"]
            self.send([{"message": "Enter password: "}])
            password = self.receive()["message"]
            print("\n\n")
            self.user = User.log_in(user_name, password)
            if self.user is not None:
                if self.user.role == "user":
                    self.send(
                        [{"message1": "Logged in successfully!"}, {"message2": self.user_commands["is_logged_in"]}])
                elif self.user.role == "admin":
                    self.send(
                        [{"message1": "Logged in successfully!"}, {"message2": self.admin_commands["is_logged_in"]}])
                break
            else:
                self.send([{"error": "Incorrect username or password!"}])
                print("\n")
                continue

    def log_out(self):
        self.user = None
        self.send([{"message1": "You have been successfully logged out!"},
                   {"message2": self.user_commands["logged_out"]}])

    def calculate_uptime(self):
        request_time = datetime.now()
        time_diff = (request_time - self.start_time).seconds
        uptime_val = str(timedelta(seconds=time_diff))
        return uptime_val

    def get_users(self, username=None):  # this should show up in the client terminal
        user_data = User.get(username)
        self.send(user_data)
        # users_table = PrettyTable()
        # users_table.field_names = [key.capitalize() for user in user_data for key in user.keys()]
        # users_table.align[users_table.field_names[0]] = "l"
        # users_table.align[users_table.field_names[1]] = "c"
        # users_table.align[users_table.field_names[2]] = "c"
        # users_table.align[users_table.field_names[3]] = "r"
        # for user in user_data:
        #     users_table.add_row(list(user.values())[:4])
        # print(users_table)

    def get_user_input(self, fields):
        user_data = {}
        for field in fields:
            self.send([{"message": f"Enter {field}: "}])
            user_data[field] = self.receive()["message"]
        return user_data

    def manage_users(self):
        while True:
            user_menu_commands = {"add": "add new account",
                                  "delete": "remove account",
                                  "show": "show selected user record",
                                  "show all": "show all users",
                                  "return": "return to previous screen "}
            self.send([{"message1": "Manage users"},
                       {"message2": user_menu_commands}])
            command = self.receive()["message"]
            if command.casefold() in user_menu_commands.keys():
                match command:
                    case "add":
                        required_fields = ["username", "password", "email", "user role"] #validate if username already used
                        user_data = self.get_user_input(required_fields)
                        if User.add(user_data["username"], user_data["password"], user_data["email"],
                                    user_data["user role"]):
                            self.send([{"message": f"User {user_data['username']} added successfully!"}])
                        else:
                            self.send([{"error": "Operation failed!"}])  # specify the error
                        continue
                    case "delete":
                        self.send([{"message": "Enter username: "}])
                        username = self.receive()["message"]
                        self.send([{"message": f"Are you sure you want to delete user {username}? Y/N"}])
                        client_reply = self.receive()["message"]
                        if client_reply.upper() == "Y":
                            if User.remove(username):
                                self.send([{"message": f"User {username} deleted successfully!"}])
                            else:
                                continue
                            continue

                    case "show":  # should send data, and client should display in format desired
                        self.send([{"message": "Enter username: "}])
                        username = self.receive()["message"]
                        self.get_users(username)
                        continue
                    case "show all":
                        self.get_users()
                        continue
                    case "return":
                        break # doesn't work as expected

    def run_user_commands(self, command):
        if command.casefold() in self.user_commands["is_logged_in"].keys():
            match command:
                case "inbox":
                    print("This is your inbox")
                case "help":
                    self.send([{"message": self.user_commands["is_logged_in"]}])
                case "sign out":
                    self.log_out()
                case "disconnect":
                    pass
        else:
            self.send([{"error": "Unknown request (user commands)!"}])

    def run_admin_commands(self, command):
        if command.casefold() in self.admin_commands["is_logged_in"].keys():
            match command:
                case "info":
                    self.send([{"message": f"version: {self.version}, build: {self.build_date}"}])
                case "uptime":
                    uptime = self.calculate_uptime()
                    self.send([{"message": f"server uptime (hh:mm:ss): {uptime}"}])
                case "help":
                    self.send([{"message": self.admin_commands["is_logged_in"]}])
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
            self.send([{"error": "Unknown request(admin commands)!"}])

    def run(self):
        self.start_server()
        while True:
            try:
                client_msg = self.receive()["message"]
                if not self.user or not self.user.is_logged_in:
                    if client_msg in self.user_commands["logged_out"].keys():
                        match client_msg:
                            case "log in":
                                self.log_in()
                            case "register":
                                self.sign_up()
                    else:
                        self.send([{"error": 'Unknown request (run loop)!'}])
                else:
                    if self.user.role == "user":
                        self.run_user_commands(client_msg)
                    elif self.user.role == "admin":
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

# user management (add, remove, log in)
# sending messages - 5 messages per inbox for regular user, no limit for admin
# limit exceeded alert for the sender
# message len limit - 255 chars
