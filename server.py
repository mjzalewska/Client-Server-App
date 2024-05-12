import json
import socket
from datetime import datetime, timedelta
from time import sleep

"""
Serwer ma obsługiwać następujące polecenia (i zwracać odpowiedź w JSONie).
""uptime"" - zwraca czas życia serwera
""info"" - zwraca numer wersji serwera, datę jego utworzenia
""help"" - zwraca listę dostępnych komend z krótkim opisem (tych komend, z tej listy, którą właśnie czytasz, czyli inaczej, komend realizowanych przez serwer)
""stop"" - zatrzymuje jednocześnie serwer i klienta
"""


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
            "stop": "stop server and client",
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
            self.send(f"Successfully connected to {self.host}")

    def send(self, msg):
        self.connection.send(bytes(json.dumps(msg), "utf-8"))

    def receive(self):
        message = json.loads(self.connection.recv(1024).decode("utf-8"))
        return message

    def calculate_uptime(self):
        request_time = datetime.now()
        time_diff = (request_time - self.start_time).seconds
        uptime_val = str(timedelta(seconds=time_diff))
        return uptime_val

    def run(self):
        self.start_server()
        while True:
            client_msg = self.receive()
            if client_msg in self.commands.keys():
                match client_msg:
                    case "info":
                        self.send({"version": self.version, "build": self.build_date})
                        print("Sent info")
                    case "uptime":
                        uptime = self.calculate_uptime()
                        self.send(uptime)
                        print("Sent uptime")
                    case "help":
                        self.send(self.commands)
                        print("Sent commands")
                    case "close":
                        self.send("Shutting connection...")
                        print("Shutting down...")
                        sleep(2)
                        self.connection.shutdown(socket.SHUT_RDWR)
                        self.connection.close()
            else:
                self.send("Invalid request")


if __name__ == "__main__":
    server = Server(65000)
    server.run()

# error handling in send, receive, start???
# message delimiting
# send two consecutive messages
