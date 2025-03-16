import socket, _thread, time
from utils import mesh

class NetworkClient:
    def __init__(self, window_class, player_renderer_class, packet_rate : float = 0.01):
        self.socket = socket.socket()
        self.socket.connect(("127.0.0.1", 42069))
        
        self.renderer_class = player_renderer_class

        self.window = window_class

        self.packet_rate = packet_rate

        msg = self.socket.recv(1024).decode()
        print(msg)

        self.sending = []

        max_player_count = int(self.socket.recv(1024).decode())
        for i in range(max_player_count):
            self.window.network_player_renderers.append(i)

        _thread.start_new_thread(self.start_sending, ())
        _thread.start_new_thread(self.start_reciving, (self.window,))

    def add_to_sending(self, sendable_data : bytes):
        self.sending.append(sendable_data)

    def send(self, packet : bytes):
        self.socket.send(packet)

    def start_sending(self):
        while True:
            for sendable in self.sending:
                self.socket.send(sendable)

            self.sending.clear()

            time.sleep(self.packet_rate)
    
    def start_reciving(self, window):
        msg = self.socket.recv(1024).decode()
        msg = msg.split(",")

        for packet in msg:
            print(packet)
            packet = packet.split("|")
            if packet[0] == "playerPosTransformUpdate":
                player_id = int(packet[1])
                if not isinstance(window.network_player_renderers[player_id], int):
                    window.network_player_renderers[player_id].pos.x = float(packet[2])
                    window.network_player_renderers[player_id].pos.y = float(packet[3])
                    window.network_player_renderers[player_id].pos.z = float(packet[4])
                
                else:
                    window.network_player_renderers[player_id] = self.renderer_class(self, mesh.get_cube())

                    window.network_player_renderers[player_id].pos.x = float(packet[2])
                    window.network_player_renderers[player_id].pos.y = float(packet[3])
                    window.network_player_renderers[player_id].pos.z = float(packet[4])