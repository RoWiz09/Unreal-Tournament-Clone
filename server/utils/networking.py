import socket, _thread, time, ast
import glm

class Server:
    def __init__(self, sending_rate : float = 0.01):
        self.socket = socket.socket()
        self.socket.bind(("127.0.0.1", 25565))

        self.packet_rate = sending_rate

        self.max_players = 8
        self.socket.listen(self.max_players)

        self.players : list[glm.vec3] = []
        self.player_sockets : list[socket.socket] = []

        self.sending = []

        _thread.start_new_thread(self.start_sending, ())

    def update(self):
        client_socket, client_addr = self.socket.accept()

        _thread.start_new_thread(self.client_thread, (client_socket, client_addr))

    def client_thread(self, client_socket : socket.socket, client_addr):
        client_socket.send("welcome to the server!".encode())
        client_socket.send(str(self.max_players).encode())
        time.sleep(0.01)
        for player in range(self.max_players):
            try:
                if not self.players[player]:
                    player_idx = player
                    self.players[player] = glm.vec3(0,0,0)
                    self.player_sockets[player] = client_socket
                    break
            except:
                self.players.append(glm.vec3(0,0,0))
                self.player_sockets.append(client_socket)

                player_idx = player
                break

        packet = "connection|"
        packet += str(player_idx)
        self.send_to_all(client_socket, packet.encode())
        while True:
            try:
                msg = client_socket.recv(1024)
                msg = msg.decode()
                packets = msg.split(",")
                for packet in packets:
                    packet = packet.split("|")
                    if packet[0] == "playerPosTransformUpdate":
                        if len(packet) == 4:
                            self.players[player_idx].x = packet[1]
                            self.players[player_idx].y = packet[2]
                            self.players[player_idx].z = packet[3]

                    packet = "playerPosTransformUpdate|"
                    packet += str(player_idx) + "|"
                    packet += str(self.players[player_idx].x) + "|"
                    packet += str(self.players[player_idx].y) + "|"
                    packet += str(self.players[player_idx].z) + ","
                    self.send_to_all(client_socket, packet.encode())
            except:
                print("client disconnected!")
                self.player_sockets[player_idx] = None
                self.players[player_idx] = None
                quit()

    def add_to_sending(self, sendable_data : bytes):
        self.sending.append(sendable_data)

    def start_sending(self):
        while True:
            for socket in self.player_sockets:
                if socket:
                    for sendable in self.sending:
                        socket.send(sendable)

            self.sending = []

            time.sleep(self.packet_rate)

    def send_to_all(self, client_socket : socket.socket, data : bytes):
        for client in self.player_sockets:
            if client != client_socket and client:
                client.send(data) 
