import json
import socket
from datetime import datetime, timedelta
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
        self.user = User()
        self.commands = \
            {
                "all_users": {"logged_out": {
                    "sign in": "log in",
                    "register": "add a new account",
                },
                    "logged_in": {
                        "sign out": "log out",
                        "end": "disconnect",
                        "inbox": "display inbox",
                        "help": "display available commands"
                    }
                },
                "admin_only": {"logged_in": {
                    "info": "display server version and build date",
                    "close": "stop server and client",
                    "uptime": "display server uptime",
                    "users": "see registered users"}
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
                       {"message2": self.commands["all_users"]["logged_out"]}])

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
                print("Invalid message format: missing header!")
            data = b"".join(msg_parts)
            message = json.loads(data.decode("utf-8").strip())
            return message

    def calculate_uptime(self):
        request_time = datetime.now()
        time_diff = (request_time - self.start_time).seconds
        uptime_val = str(timedelta(seconds=time_diff))
        return uptime_val

    def run_admin_commands(self, command):
        if command.casefold() in self.commands["admin_only"].keys():
            match command:
                case "info":
                    self.send({"version": self.version, "build": self.build_date})
                case "uptime":
                    uptime = self.calculate_uptime()
                    self.send({"server uptime (hh:mm:ss)": uptime})
                case "help":
                    self.send(self.commands["admin_only"])
                case "close":
                    print("Shutting down...")
                    sleep(2)
                    self.connection.close()
                    exit()
                case "users":
                    # display all users, selected user
                    # remove selected user
                    # add user
                    pass
        else:
            self.send("Unknown request")

    def run(self):
        self.start_server()
        while True:
            while True:
                try:
                    client_msg = self.receive()["message"]
                    # differentiate available commands when logged in and logged out
                    if client_msg.casefold() in self.commands["all_users"]["logged_out"].keys():
                        match client_msg:
                            case "sign in":
                                self.send([{"message": "Enter username: "}])
                                user_name = self.receive()
                                self.send([{"message": "Enter password: "}])
                                password = self.receive()
                                if self.user.login(self.db, user_name, password):
                                    self.send([{"message1": "Logged in successfully"},
                                               {"message2": self.commands["logged_in"]}])
                                else:
                                    self.send([{"message": "Incorrect user name or password!"}])
                            case "sign out":
                                self.user.log_out()
                                self.send([{"message": "You have been logged out!"}])
                            # clr screen and show intro screen or close connection to server

                            case "register":
                                self.send([{"message": "Enter username: "}])
                                user_name = self.receive()["message"]
                                self.send([{"message": "Enter password: "}])
                                password = self.receive()["message"]
                                if self.user.add(self.db, user_name, password):
                                    self.send([{"message": "Sign up successful!"}])
                                else:
                                    self.send([{"message": "Username already in use!"}])

                            case "inbox":
                                print("This is your inbox!")

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
