import json
import socket
from datetime import datetime
from time import sleep

"""
Serwer ma obsługiwać następujące polecenia (i zwracać odpowiedź w JSONie).
""uptime"" - zwraca czas życia serwera
""info"" - zwraca numer wersji serwera, datę jego utworzenia
""help"" - zwraca listę dostępnych komend z krótkim opisem (tych komend, z tej listy, którą właśnie czytasz, czyli inaczej, komend realizowanych przez serwer)
""stop"" - zatrzymuje jednocześnie serwer i klienta
"""

# class Server:
#     def __init__(self, port, version, server_sock=None):
#         self.host = "127.0.0.1"
#         self.port = port
#         if server_sock is None:
#             self.server_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
#         else:
#             self.server_sock = server_sock
#         self.version = version
#         self.build_date = "01.05.2024"
#         self.start_time = datetime.now().strftime("%Y-%m-%d %H:%M")
#         self.commands = {
#             "info": "display server version and build date",
#             "help": "display available commands",
#             "stop": "stop server and client",
#             "uptime": "display server uptime"
#         }
#         self.connection = None
#         self.address = None
#         self.msg = None
#
#     def connect(self):
#         with self.server_sock as s:
#             s.bind((self.host, self.port))
#             s.listen()
#             print(f"Listening on {self.host}:{self.port}")
#             while True:
#                 self.connection, self.address = s.accept()
#                 print(f"Accepted connection from {self.address[0]}:{self.address[1]}")
#                 # self.connection.send(json.dumps("Welcome. What would you like to do?"))
#                 self.connection.send(json.dumps(self.commands))
#
#     def receive_message(self):
#         self.msg = (json.loads(self.connection.recv(1024).decode("utf-8")))
#         for key, value in self.msg.items():
#             print(f"\n{key}: {value}")
#
#     def send_message(self, message):
#         self.connection.sendall(bytes(json.dumps(message), encoding="utf-8"))
#
#     def close_connection(self):
#         self.server_sock.shutdown(socket.SHUT_RDWR)
#         self.server_sock.close()
#
#
# server = Server(65000, "1.0.0.")
# server.connect()
# server.connection.send(json.dumps(server.commands))
# print("sent welcome message")
# while True:
#     client_msg = (json.loads(server.connection.recv(1024).decode("utf-8")))
#     match client_msg:
#         case "info":
#             response = f"server ver.: {server.version}\n build date: {datetime.today().strftime('%Y-%m-%d')}"
#             server.connection.sendall(bytes(json.dumps(response), encoding="utf-8"))
#             print("sent info")
#         case "uptime":
#             response = f"server uptime: uptime placeholder"
#             print("sent uptime")
#         case "help":
#             response = server.commands
#             server.connection.sendall(bytes(json.dumps(response), encoding="utf-8"))
#             print("sent all commands")
#         case "stop":
#             server.close_connection()
commands = {
    "info": "display server version and build date",
    "help": "display available commands",
    "close": "stop server and client",
    "uptime": "display server uptime"
}
welcome_msg = {"msg": "Welcome. Enter Command"}
host = "127.0.0.1"
port = 65000
ver = "1.0.0"
build_date = "2024-05-01"
server_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
with server_sock as s:
    s.bind((host, port))
    s.listen()
    start_time = datetime.now()
    print(f"Listening on {host}:{port}")
    while True:
        connection, address = s.accept()
        print(f"Accepted connection from {address[0]}:{address[1]}")
        initial_msg = welcome_msg.update(commands)
        print(initial_msg)
        connection.send(bytes(json.dumps(initial_msg), "utf-8"))
        while True:
            client_msg = (json.loads(connection.recv(1024).decode("utf-8")))
            if client_msg in commands.keys():
                match client_msg:
                    case "info":
                        connection.send(bytes(json.dumps({"version": ver, "build": build_date}), "utf-8"))
                        print("Sent info")
                    case "uptime":
                        connection.send(bytes(json.dumps("Sending uptime"), "utf-8"))
                        print("Sent uptime")
                    case "help":
                        connection.send(bytes(json.dumps(commands), "utf-8"))
                        print("Sent commands")
                    case "close":
                        connection.send(bytes(json.dumps("Shutting connection..."), "utf-8"))
                        print("Shutting down...")
                        sleep(2)
                        connection.shutdown(socket.SHUT_RDWR)
                        connection.close()
                        exit()

            else:
                connection.send(bytes(json.dumps("Invalid request"), "utf-8"))


def show_uptime():
    pass


# message delimiting
# calc uptime
# send two consecutive messages
