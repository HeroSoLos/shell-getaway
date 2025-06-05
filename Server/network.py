import socket
from Server.utils import *
from Server.config import SERVER_IP

"""anti large packet crasher"""
def recv_until_newline(sock):
    data = b""
    while True:
        chunk = sock.recv(2048)
        if not chunk:
            break
        data += chunk
        if b"\n" in chunk:
            break
    return data.decode("utf-8").strip()

class Network:
    """Network class to handle client-server communication for the game.
    
    client: A socket object for network communication.
    server: The IP address of the game server.
    port: The port number for the game server.
    addr: A tuple containing the server IP and port.
    initial_game_state: The initial game state received from the server upon connection.
    """
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
    
    """
    Connects to the game server and retrieves the initial game state.
    
    Precondition: The server is running and reachable at the specified address.
    Postcondition: The client is connected to the server and has received the initial game state.
    
    Returns: None if connection fails, otherwise sets initial_game_state with the server's response.
    """
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
    
    """
    Sends data to the server and receives the game state.
    Args:
        data_to_server: Can be player position list [x,y,health] or a shoot command dict.
    
    Precondition: The client is connected to the server.
    Postcondition: The server processes the data and returns the updated game state.
    Returns: The full game state dictionary from the server or None on error.
    """
    def send(self, data_to_server):
        try:
            if self.initial_game_state is None:
                print("Socket is not connected or initial connection failed. Attempting to reconnect...")
                self.connect()
                if self.initial_game_state is None:
                    return {"other_player": (0.0,0.0,100.0,0,0), "projectiles": []} 
            
            self.client.send(str.encode(make_pos(data_to_server)))
            
            reply_string = recv_until_newline(self.client)
            
            game_state_from_server = read_pos(reply_string)
            
            if not isinstance(game_state_from_server, dict):
                print(f"Warning: Received data from server is not a dictionary: {game_state_from_server}")
                return {"other_player": (0.0,0.0,100.0,0,0), "projectiles": []}

            return game_state_from_server
            
        except socket.error as e:
            print(f"Socket error during send/recv: {e}")
            return {"other_player": (0.0,0.0,100.0,0,0), "projectiles": []}
        except Exception as e:
            print(f"An unexpected error occurred in send: {e}")
            return {"other_player": (0.0,0.0,100.0,0,0), "projectiles": []}
