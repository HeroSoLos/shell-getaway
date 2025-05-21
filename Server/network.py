import socket
from Server.utils import *

class Network:
    def __init__(self):
        self.client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server = "10.168.107.65"
        self.port = 5555
        self.addr = (self.server, self.port)
        self.pos = self.connect()
    
    def getPos(self):  
        return self.pos
    
    def connect(self):
        try:
            self.client.connect(self.addr)
            return self.client.recv(2048).decode("utf-8")
        except:
            pass
    
    def send(self, data):
        try:
            if not isinstance(data, tuple) or len(data) != 2:
                print(f"Invalid data format: {data}")
                return (0.0, 0.0)  # Default position if data is invalid
            print(f"Sending to server: {data}")
            self.client.send(str.encode(make_pos(data)))
            reply = self.client.recv(2048).decode()
            print(f"Received from server: {reply}")
            return read_pos(reply)
        except socket.error as e:
            print(f"Socket error: {e}")
            return (0.0, 0.0)
