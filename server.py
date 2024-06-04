import json
import socket
from datetime import datetime, timedelta
from time import sleep
from user import User


class Server:
    def __init__(self, port, server_sock=None):
        self.host = "127.0.0.1"
        self.port = port
        if server_sock is None:
            self.server_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        else:
            self.server_sock = server_sock
        self.version = "1.1.0"
        self.build_date = "2023-05-13"
        self.start_time = datetime.now()
        self.user = None
        self.admin_commands = {
            "info": "display server version and build date",
            "help": "display available admin_commands",
            "close": "stop server and client",
            "uptime": "display server uptime",
            "users": "see registered users"
        }
        if not self.user.logged_in:
            self.general_commands = {
                "sign in": "log in",
                "register": "add a new account"
            }
        else:
            self.general_commands = {
                "sign out": "log out",
                "inbox": "go to inbox"
            }
        self.connection = None
        self.address = None

    def start_server(self):
        with self.server_sock as s:
            s.bind((self.host, self.port))
            s.listen()
            print(f"Listening on {self.host}:{self.port}")
            self.connection, self.address = s.accept()
            print(f"Accepted connection from {self.address[0]}:{self.address[1]}")
            self.send({f"Successfully connected to": {self.host},
                       "Actions": ", ".join([f"\n{key}: {value}" for key, value in self.general_commands.items()])})

    def send(self, msg):
        try:
            self.connection.send(bytes(json.dumps(msg), "utf-8"))
        except json.decoder.JSONDecodeError:
            print("Invalid message format")
            exit()

    def receive(self):
        try:
            message = json.loads(self.connection.recv(1024).decode("utf-8"))
            return message
        except json.decoder.JSONDecodeError:
            print("Invalid message format")
            exit()

    def calculate_uptime(self):
        request_time = datetime.now()
        time_diff = (request_time - self.start_time).seconds
        uptime_val = str(timedelta(seconds=time_diff))
        return uptime_val

    def run_admin_commands(self, command):
        if command.casefold() in self.admin_commands.keys():
            match command:
                case "info":
                    self.send({"version": self.version, "build": self.build_date})
                case "uptime":
                    uptime = self.calculate_uptime()
                    self.send({"server uptime (hh:mm:ss)": uptime})
                case "help":
                    self.send(self.admin_commands)
                case "close":
                    print("Shutting down...")
                    sleep(2)
                    self.connection.close()
                    exit()
                case "users":
                    pass
        else:
            self.send("Unknown request")

    def run(self):
        self.start_server()
        self.user = User()
        while True:
            while True:
                try:
                    client_msg = self.receive()
                    if client_msg.casefold() in self.general_commands.keys():
                        match client_msg:
                            case "sign in":
                                self.send("Enter username: ")
                                user_name = self.receive()
                                self.send("Enter password: ")
                                password = self.receive()
                                if self.user.login(user_name, password):
                                    self.send({self.user.login: "Logged in successfully",
                                              "Actions": ", ".join([f"\n{key}: {value}" for key, value in
                                                                    self.general_commands.items()])})
                            case "sign out":
                                self.user.log_out()
                                self.send("You have been logged out!")
                            # show intro screen or close connection to server

                            case "register":
                                self.send("Enter username: ")
                                user_name = self.receive()
                                self.send("Enter password: ")
                                password = self.receive()
                                if self.user.add(user_name, password):
                                    self.send("Sign up successful!")

                            case "inbox":
                                pass

                            # show sign up screen - take input
                            # validate data
                            # when signed up go to user screen
                            # ask to reenter password
                    else:
                        self.send("Unknown request")

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
