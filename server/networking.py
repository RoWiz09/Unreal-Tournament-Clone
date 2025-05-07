from server import modelLoader
from server.hitbox import hitbox

import socket, _thread, time, ast
import glm, os.path, random

class server_states:
    in_lobby = 0
    in_game = 1

class Server:
    def __init__(self, port:int = 42069, sending_rate : float = 0.05):
        # Creates the server socket
        self.socket = socket.socket()
        self.socket.bind(("0.0.0.0", port))

        # Sets the packet sending rate
        self.packet_rate = sending_rate

        # Initalizes server state
        self.server_state = server_states.in_lobby
        self.server_map = None

        self.get_maps = lambda : ["'"+map_file+"'" for map_file in os.listdir("maps\\") if map_file.endswith(".gltf")]
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
        self.player_hitboxes : list[hitbox] = []
        self.player_sockets : list[socket.socket] = []
        self.used_sockets : list[bool] = []

        self.get_socket_list = lambda : [
            self.player_sockets[p_socket] for p_socket in range(len(self.player_sockets)) 
            if self.player_sockets[p_socket] != (False, p_socket)
        ]

        # Initalizes the sending list
        self.sending = []
        self.weapon_spawners : list[modelLoader.weapon_spawnpoint] = []

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
        while True:
            client_socket, client_addr = self.socket.accept()
            print("accepted connection from " + str(client_addr))

            _thread.start_new_thread(self.client_thread, (client_socket,))

    def update_map(self):
        send_list = []
        if self.server_state == server_states.in_game:
            for weapon_spawner in self.weapon_spawners:
                pack = weapon_spawner.update()
                if pack:
                    for sock in range(len(self.player_sockets)):
                        if not self.used_sockets[sock]:
                            self.used_sockets[sock] = True
                            
                            pack_size_pack = "spawnSize|"
                            pack_size_pack += str(len(pack)) + ","

                            self.player_sockets[sock].send(pack_size_pack.encode())
                            
                            time.sleep(0.25)

                            self.player_sockets[sock].send(pack.encode())
                            
                            self.used_sockets[sock] = False

    def client_thread(self, client_socket : socket.socket):
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
        
        # Send the server data back to the client
        packet = "max_players."
        packet += str(self.max_players)

        self.send(client_socket, packet.encode())

        packet = "my_id."
        packet += str(player_idx)

        self.send(client_socket, packet.encode())

        packet = "my_team."
        packet += str(team)

        self.send(client_socket, packet.encode())
        
        # Send the new client's connection packet to all other clients
        packet = "connection."
        packet += str(player_idx)

        self.send_to_all_excluding(client_socket, packet.encode())

    def add_to_sending(self, sendable_data : bytes):
        """
            adds sendable data to the `sending` list
        """
        self.sending.append(sendable_data)

    def send_to_all_excluding(self, client_socket : socket.socket, data : bytes):
        """
            Sends `data` to all clients, excluding `client_socket`
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

        list(map(send, self.player_sockets))

    def send_to_all(self, data : bytes):
        """
            Sends `data` to all clients
        """
        
        def send(client):
            if client:
                if isinstance(client, socket.socket):

                    if len(data)%2 != 0:
                        data = data.decode().join("|").encode()

                    client.send("sp".encode())

                    for bytes in range(0, len(data), 2):
                        print(data[bytes:bytes+2])
                        client.send(data[bytes:bytes+2])

                    client.send("ep".encode())

        list(map(send, self.player_sockets))

    def send(self, client:socket.socket, data:bytes):
        """
            Sends `data` to `client`, two bytes at a time
        """

        print(data)

        if len(data)%2 != 0:
            data = data + "|".encode()

        print(data)

        client.send("sp".encode())
        for bytes in range(0, len(data), 2):
            client.send(data[bytes:bytes+2])
        client.send("ep".encode())
