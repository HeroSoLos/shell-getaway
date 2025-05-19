import socket

class Network:
    def __init__(self):
        self.client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server = "[redacted]"
        self.port = 5555
        self.addr = (self.server, self.port)
        self.id = self.connect()
        print("Connected to server with ID:", self.id)
        
    def connect(self):
        try:
            self.client.connect(self.addr)
            print("stuck1")
            return self.client.recv(2048).decode()
        except:
            print("Failed to connect to server.")
            pass
    
    def send(self, data):
        try:
            self.client.send(str.encode(data))
            reply = self.client.recv(2048).decode()
            return reply
        except socket.error as e:
            print(e)
        
n = Network()
print(n.send("hello"))
print(n.send("working"))