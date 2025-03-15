import socket, _thread

class Server:
    def __init__(self):
        self.socket = socket.socket()
        self.socket.bind(("127.0.0.1", 42069))

        self.socket.listen(8)

    def update(self):
        client_socket, client_addr = self.socket.accept()

        _thread.start_new_thread(self.client_thread, (client_socket, client_addr))

    def client_thread(self, client_socket : socket.socket, client_addr):
        client_socket.send("welcome to the server!".encode())