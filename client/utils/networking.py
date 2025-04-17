import socket, _thread, time, ast, numpy as np, glm, os.path
from json import load, dump
from utils import mesh

class server_states:
    in_lobby = 0
    in_game = 1

class spawnpoint:
    def __init__(self, pos:glm.vec3, team:bool):
        self.pos = pos
        self.team = team

    def spawn(self, my_player):
        my_player.position = self.pos

class NetworkClient:
    def __init__(self, window_class, player_renderer_class, packet_rate : float = 0.01):
        self.socket = socket.socket()
        if os.path.isfile("NetworkSettings.json"):
            with open("NetworkSettings.json") as networkSettings:
                self.networkSettings = load(networkSettings)
        else:
            with open("NetworkSettings.json", "w") as networkSettings:
                self.networkSettings = {
                    "ip":"127.0.0.1",
                    "port":42069
                }
                dump(self.networkSettings, networkSettings)

        self.socket.connect((self.networkSettings["ip"], self.networkSettings["port"]))
        
        self.renderer_class = player_renderer_class

        self.window = window_class

        self.packet_rate = packet_rate

        self.map = None
        self.lights_in_map = []

        self.red_spawnpoints = []
        self.blue_spawnpoints = []

        msg = self.socket.recv(1024).decode()

        self.sending = []

        packet = self.socket.recv(1024).decode()
        packet = packet.split(",")

        max_player_count = int(packet[0].split("|")[1])
        self.player_idx = int(packet[1].split("|")[1])
        self.team = packet[2].split("|")[1]

        for i in range(max_player_count):
            self.window.network_player_renderers.append(i)

        _thread.start_new_thread(self.start_sending, ())

    def add_to_sending(self, sendable_data : bytes):
        self.sending.append(sendable_data)

    def vote_on_map(self, map:str):
        packet = "voted|%s"%map
        self.socket.send(packet.encode())

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
                            "position": glm.vec3(*ast.literal_eval(packet[4])),
                            "color": glm.vec3(*ast.literal_eval(packet[2])),
                            "intensity": 0.00004*float(packet[3]),
                            "constant": 0.00002*float(packet[3]),
                            "linear": 0.09,
                            "quadratic": 0.032
                        }
                    ) 

                elif packet[0] == "spawnpoint":
                    if ast.literal_eval(packet[2]):
                        self.blue_spawnpoints.append(
                            spawnpoint(
                                glm.vec3(
                                    *ast.literal_eval(packet[1])
                                ),
                                True
                            )
                        )

                    elif not ast.literal_eval(packet[2]):
                        self.red_spawnpoints.append(
                            spawnpoint(
                                glm.vec3(
                                    *ast.literal_eval(packet[1])
                                ),
                                False
                            )
                        )

        return self.map, self.lights_in_map
    
    def get_server_state(self):
        self.socket.send("getServerState".encode())

        msg = self.recv_spec_packet("serverState")
        return int(msg[1])
    
    def recv_spec_packet(self, packet_type):
        msg = self.socket.recv(1024).decode()
        msg = msg.split(",")
        for packet in msg:
            packet = packet.split("|")
            if packet[0] == packet_type:
                return packet
            
        packet = self.recv_spec_packet(packet_type)
        return packet

    def send_chat_msg(self, msg:str):
        packet = "chatmsg::"+msg+","
        self.socket.send(packet.encode())
    
    def get_maps(self):
        self.socket.send("getServerMaps".encode())

        msg = self.socket.recv(1024).decode()
        return msg

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

                elif packet[0] == "connection":
                    packet[1] = int(packet[1])
                    self.window.to_create.append(packet[1:])

                elif packet[0] == "playerDisconnect":
                    player_id = int(packet[1])
                    self.window.network_player_renderers[player_id] = player_id
                    print("Player %i lost connection!"%player_id)
                
                elif "chatmsg" in packet[0]:
                    msg = packet[0].split("::")
                    self.window.create_chat_msg(msg[1])
