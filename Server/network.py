import socket
from Server.utils import *
from Server.config import SERVER_IP

class Network:
    def __init__(self):
        self.client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server = SERVER_IP
        self.port = 5555
        self.addr = (self.server, self.port)
        self.pos = None
        self.connect()
    
    def getPos(self):  
        return self.pos
    
    def connect(self):
        try:
            self.client.connect(self.addr)
            self.pos = self.client.recv(2048).decode("utf-8")
            print(f"Connected to server at {self.addr}")
        except socket.error as e:
            print(f"Connection error: {e}")
            self.pos = None
    
    def send(self, data):
        try:
            if not self.pos:
                print("Socket is not connected. Attempting to reconnect...")
                self.connect()
                if not self.pos:
                    return (0.0, 0.0)
            
            if not isinstance(data, tuple) or len(data) != 2:
                print(f"Invalid data format: {data}")
                return (0.0, 0.0)
            
            print(f"Sending to server: {data}")
            self.client.send(str.encode(make_pos(data)))
            reply = self.client.recv(2048).decode()
            print(f"Received from server: {reply}")
            return read_pos(reply)
        except socket.error as e:
            print(f"Socket error: {e}")
            return (0.0, 0.0)
