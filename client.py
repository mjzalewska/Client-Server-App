import json
import socket
from os import system, name


class Client:
    def __init__(self, host, port, client_sock=None):
        self.host = host
        self.port = port
        if client_sock is None:
            self.client_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        else:
            self.client_sock = client_sock

    def connect(self):
        self.client_sock.connect((self.host, self.port))

    def send(self, msg):
        self.client_sock.send(bytes(json.dumps(msg), "utf-8"))

    def receive(self):
        message = json.loads(self.client_sock.recv(1024).decode("utf-8"))
        return message

    @staticmethod
    def print_to_terminal(received_msg):
        try:
            if isinstance(received_msg, dict):
                for key, value in received_msg.items():
                    print(f"{key}: {value}")
                print()
            elif isinstance(received_msg, str):
                print(received_msg)
                print()
            else:
                raise ValueError
        except ValueError:
            print("Invalid message format!")
            exit()

    @staticmethod
    def clr_screen():
        if name == 'nt':
            _ = system('cls')
        else:
            _ = system('clear')

    def run(self):
        self.connect()
        while True:
            try:
                server_response = self.receive()
                if server_response == "Invalid request":
                    raise ValueError
                else:
                    self.print_to_terminal(server_response)
                    request = input("Enter command: ")
                    self.send(request)
                    self.clr_screen()
                    if request == "close":
                        self.client_sock.shutdown(socket.SHUT_RDWR)
                        self.client_sock.close()
                        break
            except ValueError:
                print("Invalid request!")


if __name__ == "__main__":
    client = Client("127.0.0.1", 65000)
    client.run()

# server response + cls screen
# read multiple messages