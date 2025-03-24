import socket, _thread, time, ast, numpy as np, glm
from utils import mesh

class NetworkClient:
    def __init__(self, window_class, player_renderer_class, packet_rate : float = 0.01):
        self.socket = socket.socket()
        self.socket.connect(("127.0.0.1", 42069))
        
        self.renderer_class = player_renderer_class

        self.window = window_class

        self.packet_rate = packet_rate

        self.map = None
        self.lights_in_map = []

        msg = self.socket.recv(1024).decode()
        print(msg)

        self.sending = []

        max_player_count = int(self.socket.recv(1024).decode())
        self.player_idx = self.socket.recv(1024).decode()
        for i in range(max_player_count):
            self.window.network_player_renderers.append(i)

        _thread.start_new_thread(self.start_sending, ())

    def add_to_sending(self, sendable_data : bytes):
        self.sending.append(sendable_data)

    def request_map(self):
        self.send("mapRequest,".encode())

        msg = self.socket.recv(1024).decode()
        packet = msg.split("|")
        if packet[0] == "mapSize":
            faces = self.socket.recv(int(packet[1])).decode()
            packets = faces.split("\\")
            for packet in packets:
                packet = packet.split("|")
                if packet[0] == "map":
                    faces = ast.literal_eval(packet[1])
                    faces = np.array(faces, dtype=np.float32)
                    self.map = faces
                elif packet[0] == "light":
                    self.lights_in_map.append(
                        {
                            "position": glm.vec3(*ast.literal_eval(packet[3])),
                            "color": glm.vec3(*ast.literal_eval(packet[2])),
                            "intensity": 30.0,
                            "constant": 10.0,
                            "linear": 0.09,
                            "quadratic": 0.032
                        }
                    )            

        return self.map, self.lights_in_map

    def send(self, packet : bytes):
        self.socket.send(packet)

    def start_sending(self):
        while True:
            for sendable in self.sending:
                self.socket.send(sendable)

            self.sending.clear()

            time.sleep(self.packet_rate)
    
    def start_reciving(self, renderer):
        while True:
            msg = self.socket.recv(1024).decode()
            msg = msg.split(",")

            for packet in msg:
                packet = packet.split("|")
                if packet[0] == "playerPosTransformUpdate":
                    player_id = int(packet[1])
                    if not isinstance(self.window.network_player_renderers[player_id], int):
                        self.window.network_player_renderers[player_id].pos.x = float(packet[2])
                        self.window.network_player_renderers[player_id].pos.y = float(packet[3])
                        self.window.network_player_renderers[player_id].pos.z = float(packet[4])

                    else:
                        if packet[1] != self.player_idx:
                            packet[1] = player_id
                            self.window.to_create.append(packet[1:])

                if packet[0] == "connection":
                    packet[1] = int(packet[1])
                    self.window.to_create.append(packet[1:])

                if packet[0] == "playerDisconnect":
                    player_id = int(packet[1])
                    self.window.network_player_renderers[player_id] = player_id
                    print("Player %i lost connection!"%player_id)
