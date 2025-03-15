from _thread import start_new_thread
from utils import networking

server = networking.Server()

def start_server_updates():
    while True:
        server.update()

start_new_thread(start_server_updates, ())
input()