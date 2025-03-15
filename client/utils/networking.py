import socket

class NetworkClient:
    def __init__(self, packet_rate : float = 0.01):
        self.socket = socket.socket()
        self.socket.connect(("127.0.0.1", 42069))

        msg = self.socket.recv(1024).decode()
        print(msg)

