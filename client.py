import json
import socket


class Client:
    def __init__(self, host, port, client_sock=None):
        self.host = host
        self.port = port
        if client_sock is None:
            self.client_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        else:
            self.client_sock = client_sock
        self.msg = None

    def connect(self):
        self.client_sock.connect((self.host, self.port))

    def send_message(self, msg):
        self.client_sock.sendall(bytes(json.dumps(msg), encoding="utf-8"))

    def receive_message(self):
        self.msg = (json.loads(self.client_sock.recv(1024).decode("utf-8")))
        for key, value in self.msg.items():
            print(f"\n{key}: {value}")


client = Client("127.0.0.1", 65000)
client.connect()

while True:
    client.receive_message()
    choice = input(">: ")
    if choice not in client.msg.keys():
        print("Choose another option")
    else:
        client.send_message(choice)



