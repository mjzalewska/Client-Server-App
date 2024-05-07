import json
import socket


# class Client:
#     def __init__(self, host, port, client_sock=None):
#         self.host = host
#         self.port = port
#         if client_sock is None:
#             self.client_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
#         else:
#             self.client_sock = client_sock
#         self.msg = None
#
#     def connect(self):
#         self.client_sock.connect((self.host, self.port))
#         print("Connected to server!")
#
#     def send_message(self, msg):
#         self.client_sock.sendall(bytes(json.dumps(msg), encoding="utf-8"))
#
#     def receive_message(self):
#         self.msg = (json.loads(self.client_sock.recv(1024).decode("utf-8")))
#
#     def print_to_terminal(self):
#         for key, value in self.msg.items():
#             print(f"\n{key}: {value}")
#
#
# client = Client("127.0.0.1", 65000)
# client.connect()

host = "127.0.0.1"
port = 65000
client_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client_sock.connect((host, port))
msg = client_sock.recv(1024).decode("utf-8")
decoded_msg = (json.loads(msg))
print(decoded_msg)

valid_requests = ["info", "help", "uptime", "close"]
# when close called need to break out of the main loop
# winn err 10057
while True:
    client_request = input("Enter command: ")
    while True:
        try:
            if client_request in valid_requests:
                client_sock.send(bytes(json.dumps(client_request), "utf-8"))
                server_response = (json.loads(client_sock.recv(1024).decode("utf-8")))
                print(server_response)
                break
            else:
                raise ValueError
        except ValueError:
            print("Invalid request. Choose 'info', 'help', 'uptime', 'close' ")
            break


    # for command, descr in msg.items():
    #     print(f"{command} - {descr}")
    #     while True:
    #         client_msg = input("Enter command: ").lower()
    #         if client_msg not in msg.keys():
    #             print("Invalid choice")
    #         else:
    #             client_sock.send(json.dumps(client_msg))


    # client.receive_message()
    # client.print_to_terminal()
    # choice = input("Enter command: ").lower()
    # if choice not in client.msg.keys():
    #     print("Choose another option")
    # else:
    #     client.send_message(choice)



