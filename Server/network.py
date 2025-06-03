import socket
from Server.utils import *
from Server.config import SERVER_IP

class Network:
    def __init__(self):
        self.client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server = SERVER_IP
        self.port = 5555
        self.addr = (self.server, self.port)
        self.initial_game_state = None # Will store the initial dict from server
        self.connect()
    
    def get_initial_state(self):
        """Returns the initial game state received upon connection."""
        return self.initial_game_state
    
    def connect(self):
        try:
            self.client.connect(self.addr)
            raw_initial_data = self.client.recv(2048).decode("utf-8")
            self.initial_game_state = read_pos(raw_initial_data) # read_pos now uses json.loads
            print(f"Connected to server at {self.addr}. Initial state: {self.initial_game_state}")
            if not isinstance(self.initial_game_state, dict):
                print(f"Warning: Initial data from server is not a dictionary: {self.initial_game_state}")
                # Potentially set to a default error state or raise an error
        except socket.error as e:
            print(f"Connection error: {e}")
            self.initial_game_state = None # Ensure it's None on error
    
    def send(self, data_to_server):
        """
        Sends data to the server and receives the game state.
        data_to_server: Can be player position list [x,y,health] or a shoot command dict.
        Returns: The full game state dictionary from the server or None on error.
        """
        try:
            if self.initial_game_state is None: # Check if connection was successful initially
                print("Socket is not connected or initial connection failed. Attempting to reconnect...")
                self.connect()
                if self.initial_game_state is None:
                    # Return a default/error state if reconnect fails
                    return {"other_player": (0.0,0.0,100.0), "projectiles": []} 
            
            # Data validation can be more specific if needed based on type (list vs dict for shoot)
            # For now, make_pos (json.dumps) will handle dict or list.
            # print(f"Sending to server: {data_to_server}")
            self.client.send(str.encode(make_pos(data_to_server)))
            
            reply_string = self.client.recv(2048).decode()
            # print(f"Received raw from server: {reply_string}")
            
            game_state_from_server = read_pos(reply_string) # read_pos uses json.loads
            
            if not isinstance(game_state_from_server, dict):
                print(f"Warning: Received data from server is not a dictionary: {game_state_from_server}")
                # Fallback or error handling
                return {"other_player": (0.0,0.0,100.0), "projectiles": []}

            return game_state_from_server
            
        except socket.error as e:
            print(f"Socket error during send/recv: {e}")
            # Return a default/error state that matches expected structure
            return {"other_player": (0.0,0.0,100.0), "projectiles": []}
        except Exception as e: # Catch other potential errors like JSON decoding if read_pos fails
            print(f"An unexpected error occurred in send: {e}")
            return {"other_player": (0.0,0.0,100.0), "projectiles": []}
