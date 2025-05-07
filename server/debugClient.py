import socket, _thread

client_sockets = []

me = socket.socket()
me.connect(("127.0.0.1",42069))

while True:

    msg = me.recv(2).decode()

    if msg == "sp":
        packet = ""
        while True:
            packet_segment = me.recv(2).decode()
            if packet_segment == "ep":
                print(packet.strip("|"))
                break

            else:
                packet += packet_segment