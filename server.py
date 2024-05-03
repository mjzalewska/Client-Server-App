import json
import socket

"""
Serwer ma obsługiwać następujące polecenia (i zwracać odpowiedź w JSONie).
""uptime"" - zwraca czas życia serwera
""info"" - zwraca numer wersji serwera, datę jego utworzenia
""help"" - zwraca listę dostępnych komend z krótkim opisem (tych komend, z tej listy, którą właśnie czytasz, czyli inaczej, komend realizowanych przez serwer)
""stop"" - zatrzymuje jednocześnie serwer i klienta
"""


class Server:
    def __init__(self, port, version, server_sock=None):
        self.host = "127.0.0.1"
        self.port = port
        if server_sock is None:
            self.server_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.server_sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        else:
            self.server_sock = server_sock
        self.version = version
        self.uptime = 0
        self.commands = {
            "info": "display server version and build date",
            "help": "display available commands",
            "stop": "stop server and client",
            "uptime": "display server uptime"
        }
        self.connection = None
        self.address = None
        self.msg = None

    def connect(self):
        with self.server_sock as s:
            s.bind((self.host, self.port))
            s.listen()
            while True:
                self.connection, self.address = s.accept()
                print(f"Accepted connection from {self.address}")

    def receive_message(self):
        self.msg = (json.loads(self.connection.recv(1024).decode("utf-8")))
        for key, value in self.msg.items():
            print(f"\n{key}: {value}")

    def send_message(self, message):
        self.connection.sendall(bytes(json.dumps(message), encoding="utf-8"))

    def close_connection(self):
        self.server_sock.shutdown(socket.SHUT_RDWR)
        self.server_sock.close()


server = Server(65000, "1.0.0.")
server.connect()

