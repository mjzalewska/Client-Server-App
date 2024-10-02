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
        self.buffer = 1024

    def connect(self):
        self.client_sock.connect((self.host, self.port))

    def send(self, msg):
        self.client_sock.send(bytes(json.dumps(msg), "utf-8"))

    def receive(self):
        msg_parts = []
        bytes_rec = 0
        try:
            header = self.client_sock.recv(4)
            if not header:
                raise ValueError
            else:
                msg_len = int.from_bytes(header[0:4], byteorder="big")
                while bytes_rec < msg_len:
                    msg_part = self.client_sock.recv(min(msg_len - bytes_rec, self.buffer))
                    if not msg_part:
                        raise RuntimeError
                    msg_parts.append(msg_part)
                    bytes_rec += len(msg_part)
                data = b"".join(msg_parts)
                message = data.decode("utf-8").strip()
                return message

        except ValueError:
            print("Invalid message format: missing header!")
        except RuntimeError:
            print("Invalid message format: missing data!")

    @staticmethod
    def print_to_terminal(received_msg):
        for key, value in received_msg.items():
            print(f"{key}: {value}")
            print()

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
                server_response = self.receive()  # +57
                print(server_response)
                # self.print_to_terminal(server_response)
                request = input(">>: ")
                self.send(request)
                self.clr_screen()
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
