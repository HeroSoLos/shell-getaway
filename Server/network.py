import socket
from Server.utils import *
from Server.config import SERVER_IP

class Network:
    def __init__(self):
        self.client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server = SERVER_IP
        self.port = 5555
        self.addr = (self.server, self.port)
        self.initial_game_state = None
        self.connect()
    
    def get_initial_state(self):
        """Returns the initial game state received upon connection."""
        return self.initial_game_state
    
    def connect(self):
        try:
            self.client.connect(self.addr)
            raw_initial_data = self.client.recv(2048).decode("utf-8")
            self.initial_game_state = read_pos(raw_initial_data)
            print(f"Connected to server at {self.addr}. Initial state: {self.initial_game_state}")
            if not isinstance(self.initial_game_state, dict):
                print(f"Warning: Initial data from server is not a dictionary: {self.initial_game_state}")
        except socket.error as e:
            print(f"Connection error: {e}")
            self.initial_game_state = None
    
    def send(self, data_to_server):
        """
        Sends data to the server and receives the game state.
        data_to_server: Can be player position list [x,y,health] or a shoot command dict.
        Returns: The full game state dictionary from the server or None on error.
        """
        try:
            if self.initial_game_state is None:
                print("Socket is not connected or initial connection failed. Attempting to reconnect...")
                self.connect()
                if self.initial_game_state is None:
                    return {"other_player": (0.0,0.0,100.0), "projectiles": []} 
            
            self.client.send(str.encode(make_pos(data_to_server)))
            
            reply_string = self.client.recv(2048).decode()
            
            game_state_from_server = read_pos(reply_string)
            
            if not isinstance(game_state_from_server, dict):
                print(f"Warning: Received data from server is not a dictionary: {game_state_from_server}")
                return {"other_player": (0.0,0.0,100.0), "projectiles": []}

            return game_state_from_server
            
        except socket.error as e:
            print(f"Socket error during send/recv: {e}")
            return {"other_player": (0.0,0.0,100.0), "projectiles": []}
        except Exception as e:
            print(f"An unexpected error occurred in send: {e}")
            return {"other_player": (0.0,0.0,100.0), "projectiles": []}
