import json
import socket
from datetime import datetime, timedelta
from time import sleep
from db_manager import DbManager


class Server:
    def __init__(self, port, server_sock=None):
        self.host = "127.0.0.1"
        self.port = port
        if server_sock is None:
            self.server_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        else:
            self.server_sock = server_sock
        self.version = "1.0.0"
        self.build_date = "2023-05-13"
        self.start_time = datetime.now()
        self.admin_commands = {
            "info": "display server version and build date",
            "help": "display available admin_commands",
            "close": "stop server and client",
            "uptime": "display server uptime"
        }
        self.general_commands = {
            "sign-in": "log in",
            "register": "add a new account",
            "sign-out": "log out"
        }
        self.connection = None
        self.address = None
        self.logged_in = False

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

    @staticmethod
    def does_user_exist(user_name):
        if DbManager.fetch(user_name):
            return True
        else:
            return False

    def log_in(self, user):
        user_name, password = user
        if self.does_user_exist(user_name):
            if DbManager.fetch(user_name)["password"] == password:
                self.logged_in = True
                self.send("Logged in successfully")
        else:
            self.send("Invalid user name or password")

    def log_out(self):
        self.logged_in = False
        self.send("Logged out successfully")

    def add_user(self):
        pass

    def remove_user(self):
        pass

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
        else:
            self.send("Unknown request")

    def run(self):
        self.start_server()
        while True:
            while True:
                try:
                    client_msg = self.receive()
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
# message len limit - 256 chars
