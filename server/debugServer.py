import socket, _thread

client_sockets = []

me = socket.socket()
me.bind(("0.0.0.0", 42069))

me.listen(1)

def send_to_all(self, client_socket : socket.socket, data : bytes):
        """
        Sends `data` to all clients besides from `client_socket`
        """
        def send(client):
            if client != client_socket and client:
                if isinstance(client, socket.socket):
                    client.send("sp".encode())
                    for bytes in range(0, len(data), 2):
                        if len(data)-bytes < 2:
                            data.join("|".encode())
                        client.send(data[bytes:bytes+2])
                    client.send("ep".encode())

        list(map(send, client_sockets))

def client_thread(client_socket):
    print("test")
    send_to_all(None, None, "Hello|".encode())

while True:
    client_socket, client_addr = me.accept()
    client_sockets.append(client_socket)

    _thread.start_new_thread(client_thread, (client_socket,))
