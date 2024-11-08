import json
import socket
from utilities import clr_screen


class Client:
    def __init__(self, host, port, client_sock=None):
        self.host = host
        self.port = port
        if client_sock is None:
            self.client_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        else:
            self.client_sock = client_sock
        self.buffer = 1024

    def connect(self):
        self.client_sock.connect((self.host, self.port))

    def send(self, msg):
        try:
            message = json.dumps(msg).encode("utf-8")
            message_len = len(message).to_bytes(4, byteorder="big")
            self.client_sock.sendall(message_len + message)
        except json.decoder.JSONDecodeError:
            print("Invalid message format")
            exit()

    def receive(self):
        msg_parts = []
        bytes_recv = 0
        header = self.client_sock.recv(4)
        if not header:
            raise ValueError
        while True:
            try:
                msg_len = int.from_bytes(header[0:4], byteorder="big")
                while bytes_recv < msg_len:
                    msg_part = self.client_sock.recv(min(msg_len - bytes_recv, self.buffer))
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

    @staticmethod
    def print_to_terminal(received_msg):
        for item in received_msg:
            for key, value in item.items():
                if isinstance(value, dict):
                    for subkey, subvalue in value.items():
                        print(f"{subkey}: {subvalue}")
                else:
                    print(f"{value}")

    def run(self):
        self.connect()
        while True:
            try:
                server_response = self.receive()
                self.print_to_terminal(server_response)
                if "error" in server_response[0].keys():
                    request = input(">>: ")
                    self.send({"message": request})
                    continue
                else:
                    request = input(">>: ")
                    self.send({"message": request})
                # clr_screen() # turn on in final
                if request == "close":
                    self.client_sock.close()
                    break
            except ConnectionError:
                print("Connection to the host has been lost")
                exit()
            except Exception as e:
                print(e)
                exit()  ## remove in final


if __name__ == "__main__":
    client = Client("127.0.0.1", 65000)
    client.run()
