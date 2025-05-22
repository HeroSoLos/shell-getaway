import socket
from _thread import *
from utils import *
from config import SERVER_IP

server = SERVER_IP
port = 5555

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

try:
    s.bind((server, port))
except socket.error as e:
    str(e)

s.listen(2)
print("Waiting for a connection...")

pos = [(0, 0), (100, 100)]
def threaded_client(conn, player):
    try:
        conn.send(str.encode(make_pos(pos[player])))
    except Exception as e:
        print(f"Error sending initial data to client: {e}")
        conn.close()
        return
    
    while True:
        try:
            raw_data = conn.recv(2048).decode("utf-8")
            if not raw_data:
                print(f"Player {player} disconnected (no data).")
                break

            print(f"Raw data from player {player}: {raw_data}")
            data = read_pos(raw_data)
            if data == (0.0, 0.0) and raw_data != "0.0,0.0":
                print(f"Invalid data received from player {player}: {raw_data}")
                continue  # Skip processing invalid data

            pos[player] = data

            reply = pos[1 - player] if player in (0, 1) else (0.0, 0.0)
            print(f"Received from player {player}: {data}, Sending: {reply}")

            conn.sendall(str.encode(make_pos(reply)))
        except Exception as e:
            print(f"Error in player {player}'s thread: {e}")
            break
    
    print(f"Player {player} lost connection.")
    conn.close()

currentPlayer = 0
while True:
    conn, addr = s.accept()
    print("Connected to: ", addr)
    start_new_thread(threaded_client, (conn, currentPlayer))
    currentPlayer += 1