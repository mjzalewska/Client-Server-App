import json
import socket
from datetime import datetime, timedelta
from time import sleep


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
        self.commands = {
            "info": "display server version and build date",
            "help": "display available commands",
            "close": "stop server and client",
            "uptime": "display server uptime"
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
            self.send({"Successfully connected to": self.host,
                       "Host commands": ", ".join([f"\n{key}: {value}" for key, value in self.commands.items()])})

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

    def run(self):
        self.start_server()
        while True:
            while True:
                try:
                    client_msg = self.receive()
                    if client_msg.casefold() in self.commands.keys():
                        match client_msg:
                            case "info":
                                self.send({"version": self.version, "build": self.build_date})
                            case "uptime":
                                uptime = self.calculate_uptime()
                                self.send({"server uptime (hh:mm:ss)": uptime})
                            case "help":
                                self.send(self.commands)
                            case "close":
                                print("Shutting down...")
                                sleep(2)
                                self.connection.close()
                                exit()
                    else:
                        self.send("Unknown request")
                except ConnectionError:
                    print("Connection to the host has been lost!")
                    exit()
                except Exception as e:
                    print(e)
                    exit()


if __name__ == "__main__":
    server = Server(65000)
    server.run()

