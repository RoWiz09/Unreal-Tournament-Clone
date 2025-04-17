from utils import modelLoader

import socket, _thread, time, ast
import glm, os.path, random

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
        self.server_state = server_states.in_lobby
        self.server_map = None

        self.get_maps = lambda : ["'"+map_file+"'" for map_file in os.listdir(".") if map_file.endswith(".gltf")]
        self.get_voted_maps = lambda : {map : 0 for map in self.get_maps()}

        self.maps = self.get_maps()
        self.map_votes = self.get_voted_maps()

        # Sets the max players
        self.max_players = 9
        if self.max_players % 2 != 0:
            print("Invalid max player count: %i. The player count must be even." % self.max_players)
            self.max_players -= 1

        self.red_team = []
        self.blue_team = []

        self.socket.listen(self.max_players)

        # Initalizes the player list
        self.players : list[tuple[bool, int]] = []
        self.player_sockets : list[socket.socket] = []
        self.used_sockets : list[bool] = []

        self.get_socket_list = lambda : [
            self.player_sockets[p_socket] for p_socket in range(len(self.player_sockets)) 
            if self.player_sockets[p_socket] != (False, p_socket)
        ]

        # Initalizes the sending list
        self.sending = []

        self.voted_players = 0

        # Starts the sending thread
        #_thread.start_new_thread(self.start_sending, ())

    def lobby_handler(self):
        if self.voted_players == len(self.get_socket_list()) and len(self.get_socket_list())>=1:
            self.server_map = self.get_most_voted_map().replace("'","")
            self.server_state = server_states.in_game

    def get_most_voted_map(self):
        last_greatest_vote = 0
        winning_maps = [""]

        for v_map in self.map_votes.keys():
            if self.map_votes[v_map] > last_greatest_vote:
                last_greatest_vote = self.map_votes[v_map]
                winning_maps[0] = v_map

        return winning_maps[random.randint(0,len(winning_maps)-1)]

    def update(self):
        client_socket, client_addr = self.socket.accept()

        _thread.start_new_thread(self.client_thread, (client_socket,))

    def client_thread(self, client_socket : socket.socket):
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
                    self.used_sockets[player] = False
                    break
            except:
                player_idx = player

                self.players.append((True, player_idx))
                self.player_sockets.append(client_socket)
                self.used_sockets.append(False)
                break
        else:
            client_socket.close()
            print("Denied connection, the server is full")
            quit()

        if len(self.red_team) == self.max_players/2:
            self.blue_team.append(player_idx)
            team = "Red"

        elif len(self.blue_team) == self.max_players/2:
            self.red_team.append(player_idx)
            team = "Blue"

        else:
            if random.randint(0,1) == 1:
                self.blue_team.append(player_idx)
                team = "Blue"
            else:
                self.red_team.append(player_idx)
                team = "Red"
        
        # Send the playerID back to the client
        packet:str = "max_players|"
        packet += str(self.max_players)+","
        packet += "my_id|"
        packet += str(player_idx)+","
        packet += "my_team|"
        packet += str(team)+","
        client_socket.send(packet.encode())
        
        # Send the new client's connection packet to all other clients
        packet = "connection|"
        packet += str(player_idx)+","

        self.send_to_all(client_socket, packet.encode())

        sending = []

        while True:
            try:
                # Let's not leak memory, shall we?
                sending.clear()

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
                            sending.append(packet.encode())

                    elif packet[0] == "getServerState":
                        self.used_sockets[player_idx] = True
                        packet = "serverState|"+str(self.server_state)
                        client_socket.send(packet.encode())
                        self.used_sockets[player_idx] = False

                    elif packet[0] == "getServerMaps":
                        self.used_sockets[player_idx] = True
                        client_socket.send(",".join(self.maps).encode())
                        self.used_sockets[player_idx] = False

                    elif packet[0] == "voted":
                        if "'"+packet[1]+"'" in self.map_votes:
                            self.map_votes["'"+packet[1]+"'"] += 1
                            self.voted_players += 1

                        self.lobby_handler()
                    
                    elif "chatmsg" in packet[0]:
                        msg = packet[0].split("::")
                        self.send_to_all(client_socket, str("chatmsg::"+msg[1]).encode())
                    
                    elif packet[0] == "mapRequest":
                        self.used_sockets[player_idx] = True
                        if self.server_state == server_states.in_game:
                            server_map, lights, spawnpoints = modelLoader.load_gltf(self.server_map.removesuffix(".gltf"))
                            packet = "map|"
                            packet += str(server_map)+"\\"
                            for light in lights:
                                packet += light.to_packet()

                            for spawnpoint in spawnpoints:
                                packet += spawnpoint.to_packet()

                            map_size_packet = "mapSize|"
                            map_size_packet += str(len(packet.encode()))
                            client_socket.send(map_size_packet.encode())

                            time.sleep(0.25)

                            client_socket.send(packet.encode())

                        self.used_sockets[player_idx] = False

                self.send_to_all_list(client_socket,sending)

            except Exception as e:
                # Reset the server slot for this player
                print("client disconnected!")
                self.player_sockets[player_idx] = (False, player_idx)
                self.players[player_idx] = (False, player_idx)
                
                #print(e)

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
            if not self.used_sockets[self.player_sockets.index(client)]:
                if client != client_socket and client:
                    if isinstance(client, socket.socket):
                        client.send(data) 

    def send_to_all_list(self, client_socket : socket.socket, data : list[bytes]):
        """
        Sends `data` to all clients besides from `client_socket`
        """
        for client in self.player_sockets:
            if not self.used_sockets[self.player_sockets.index(client)]:
                for packet in data:
                    if client != client_socket and client:
                        if isinstance(client, socket.socket):
                            client.send(packet)
