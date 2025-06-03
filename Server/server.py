import sys
import os

current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(current_dir)
if project_root not in sys.path:
    sys.path.append(project_root)

import socket
from _thread import *
from utils import *
from config import SERVER_IP
from Gun.projectile import Projectile
import math
import threading


server = SERVER_IP
port = 5555
projectile_lock = threading.Lock()
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

try:
    s.bind((server, port))
except socket.error as e:
    str(e)

s.listen(2)
print("Waiting for a connection...")

game_state = {
    "players": [(0, 0, 100, 0, 0), (100, 100, 100, 0, 0)], # (x, y, health)
    "projectiles": []
}

next_projectile_id = 0 

def threaded_client(conn, player):
    global next_projectile_id
    try:
        my_player_data = game_state["players"][player]
        other_player_id = 1 - player

        other_player_data = game_state["players"][other_player_id] if 0 <= other_player_id < len(game_state["players"]) else (0,0,100,0,0)


        initial_data_for_client = {
            "my_player": my_player_data,
            "other_player": other_player_data,
            "projectiles": []
        }
        conn.send(str.encode(make_pos(initial_data_for_client)))
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

            if data is None:
                print(f"Invalid JSON data received from player {player}: {raw_data}")
                continue

            if isinstance(data, dict) and data.get('action') == 'shoot':
                details = data.get('details')
                if details:
                    print(f"Player {player} shoot command: {details}")
                    next_projectile_id += 1
                    proj_id = next_projectile_id
                    owner_id = player
                    proj_type = details.get('projectile_type', 'standard_bullet')
                    start_x = details.get('gun_x')
                    start_y = details.get('gun_y')
                    target_x = details.get('target_x')
                    target_y = details.get('target_y')
                    damage = details.get('damage')

                    if start_x is not None and start_y is not None and target_x is not None and target_y is not None:
                        dir_x = target_x - start_x
                        dir_y = target_y - start_y
                        magnitude = math.sqrt(dir_x**2 + dir_y**2)
                        
                        projectile_speed = 10

                        if magnitude == 0:
                            vx, vy = 0, projectile_speed
                        else:
                            norm_dir_x = dir_x / magnitude
                            norm_dir_y = dir_y / magnitude
                            vx = norm_dir_x * projectile_speed
                            vy = norm_dir_y * projectile_speed
                        
                        radius = 5

                        new_projectile = Projectile(id=proj_id, x=start_x, y=start_y, 
                                                    vx=vx, vy=vy, radius=radius, 
                                                    owner_id=owner_id, damage=damage, projectile_type=proj_type)
                        game_state["projectiles"].append(new_projectile)
                        print(f"Created projectile {proj_id} for player {player}")
                    else:
                        print(f"Missing details in shoot command from player {player}")
                else:
                    print(f"Shoot command from player {player} missing 'details'.")

            elif isinstance(data, (list, tuple)):
                if len(data) == 5:
                    try:
                        pos_data = (float(data[0]), float(data[1]), float(data[2]), float(data[3]), float(data[4]))
                        game_state["players"][player] = (pos_data[0], pos_data[1], game_state["players"][player][2], pos_data[3], pos_data[4])
                    except (ValueError, TypeError) as e:
                        print(f"Invalid position data format from player {player}: {data}, error: {e}")
                else:
                    print(f"Invalid position data structure from player {player}: {data}")
            
            else:
                print(f"Unknown data type received from player {player}: {type(data)}, data: {data}")

            
            projectiles_to_remove = []
            with projectile_lock:
                for proj in game_state["projectiles"][:]:
                    proj.update()
                    screen_width = 600 
                    screen_height = 300
                    if not (-50 < proj.position[0] < screen_width + 50 and \
                            -50 < proj.position[1] < screen_height + 50):
                        if proj not in projectiles_to_remove:
                           projectiles_to_remove.append(proj)
                        print(f"Projectile {proj.id} removed due to boundary.")
                        continue
                    
                    player_width = 50
                    player_height = 50
                    projectile_damage = proj.damage

                    for player_idx, player_data in enumerate(game_state["players"]):
                        player_pos_x, player_pos_y, player_health = player_data
                        
                        player_rect_x_start = player_pos_x
                        player_rect_x_end = player_pos_x + player_width
                        player_rect_y_start = player_pos_y
                        player_rect_y_end = player_pos_y + player_height

                        proj_center_x = proj.position[0]
                        proj_center_y = proj.position[1]

                        collided = (player_rect_x_start < proj_center_x < player_rect_x_end and \
                                    player_rect_y_start < proj_center_y < player_rect_y_end)

                        if collided:
                            if proj.owner_id != player_idx:
                                new_health = player_health - projectile_damage
                                game_state["players"][player_idx] = (player_pos_x, player_pos_y, max(0, new_health))
                                print(f"Player {player_idx} hit by projectile {proj.id}. Health: {new_health}")
                                if proj not in projectiles_to_remove:
                                    projectiles_to_remove.append(proj)
                                break
                
                for proj_to_remove in projectiles_to_remove:
                    if proj_to_remove in game_state["projectiles"]:
                        game_state["projectiles"].remove(proj_to_remove)

            my_current_health = game_state["players"][player][2]
            
            other_player_id = 1 - player
            if 0 <= other_player_id < len(game_state["players"]):
                reply_other_player_data = game_state["players"][other_player_id]
            else:
                reply_other_player_data = (0.0, 0.0, 100.0, 0.0, 0.0)
            
            projectiles_data_for_client = []
            with projectile_lock:
                for p_obj in game_state["projectiles"]:
                    projectiles_data_for_client.append((
                        p_obj.id,
                        round(p_obj.position[0], 2),
                        round(p_obj.position[1], 2),
                        round(p_obj.velocity[0], 2),
                        round(p_obj.velocity[1], 2),
                        p_obj.projectile_type,
                        p_obj.owner_id
                    ))

            data_to_send_client = {
                "my_player_updated_health": my_current_health,
                "other_player": reply_other_player_data,
                "projectiles": projectiles_data_for_client
            }
            print(f"Player {player} state update. Sending my_health: {my_current_health}, other_player: {reply_other_player_data}, projectiles: {len(projectiles_data_for_client)}")
            conn.sendall(str.encode(make_pos(data_to_send_client)))

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