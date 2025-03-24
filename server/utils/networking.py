from utils import modelLoader

import socket, _thread, time, ast
import glm

class server_states:
    in_lobby = 0
    in_game = 1

class Server:
    def __init__(self, sending_rate : float = 0.05):
        # Creates the server socket
        self.socket = socket.socket()
        self.socket.bind(("0.0.0.0", 42069))

        # Sets the packet sending rate
        self.packet_rate = sending_rate

        # Initalizes server state
        self.server_state = server_states.in_game
        self.server_map = input("what map do you want to play? ")
        
        # Sets the max players
        self.max_players = 8
        self.socket.listen(self.max_players)

        # Initalizes the player list
        self.players : list[tuple[bool, int]] = []
        self.player_sockets : list[socket.socket] = []

        # Initalizes the sending list
        self.sending = []

        # Starts the sending thread
        _thread.start_new_thread(self.start_sending, ())

    def update(self):
        client_socket, client_addr = self.socket.accept()

        _thread.start_new_thread(self.client_thread, (client_socket, client_addr))

    def client_thread(self, client_socket : socket.socket, client_addr):
        client_socket.send("welcome to the server!".encode())
        time.sleep(0.01)

        player_idx = False

        # get the client's playerID
        for player in range(self.max_players):
            try:
                if self.players[player][0] == False:
                    player_idx = player
                    self.players[player] = (True, player_idx)
                    self.player_sockets[player] = client_socket
                    break
            except:
                player_idx = player

                self.players.append((True, player_idx))
                self.player_sockets.append(client_socket)
                break
        else:
            quit("Denied connection, the server is full")
        
        # Send the playerID back to the client
        packet:str = "max_players"
        packet += str(self.max_players)+","
        packet += "my_id"
        packet += str(player_idx)+","
        client_socket.send(packet.encode())
        
        # Send the new client's connection packet to all other clients
        packet = "connection|"
        packet += str(player_idx)
        self.send_to_all(client_socket, packet.encode())

        while True:
            try:
                # Recive the packet sent by the player
                msg = client_socket.recv(1024)
                msg = msg.decode()

                # Split all packets sent
                packets = msg.split(",")

                for packet in packets:
                    packet = packet.split("|")

                    # Player Position update packet handling
                    if packet[0] == "playerPosTransformUpdate":
                        if len(packet) == 4:
                            pos = glm.vec3(float(packet[1]),float(packet[2]),float(packet[3]))

                            # Send new player position to all clients
                            packet = "playerPosTransformUpdate|"
                            packet += str(player_idx) + "|"
                            packet += str(pos.x) + "|"
                            packet += str(pos.y) + "|"
                            packet += str(pos.z) + ","
                            self.add_to_sending(packet.encode())
                    
                    if packet[0] == "mapRequest":
                        print("requested map!")
                        if self.server_state == server_states.in_game:
                            server_map, lights = modelLoader.load_gltf(self.server_map)
                            print(server_map)
                            packet = "map|"
                            packet += str(server_map)+"\\"
                            for light in lights:
                                packet += light.to_packet()

                            map_size_packet = "mapSize|"
                            map_size_packet += str(len(packet.encode()))
                            client_socket.send(map_size_packet.encode())

                            time.sleep(0.25)

                            print("sent map size")

                            client_socket.send(packet.encode())

            except Exception as e:
                # Reset the server slot for this player
                print("client disconnected!")
                self.player_sockets[player_idx] = (False, player_idx)
                self.players[player_idx] = (False, player_idx)

                print(e)
                
                # Tell all players that this player left the server
                packet = "playerDisconnect|"
                packet += str(player_idx)+","
                self.send_to_all(client_socket, packet.encode())

                # Exit the thread
                quit()

    def add_to_sending(self, sendable_data : bytes):
        """
            adds sendable data to the `sending` list
        """
        self.sending.append(sendable_data)

    def start_sending(self):
        while True:
            for socket in self.player_sockets:
                for sendable in self.sending:
                    try:
                        socket.send(sendable)
                    except:
                        continue

            self.sending = []

            time.sleep(self.packet_rate)

    def send_to_all(self, client_socket : socket.socket, data : bytes):
        """
        Sends `data` to all clients besides from `client_socket`
        """
        for client in self.player_sockets:
            if client != client_socket and client:
                if isinstance(client, socket.socket):
                    client.send(data) 
