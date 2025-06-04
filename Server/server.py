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
import random


server = SERVER_IP
port = 5555
projectile_lock = threading.Lock()
game_state_lock = threading.Lock()

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

try:
    s.bind((server, port))
except socket.error as e:
    print(f"CRITICAL: Socket bind error: {e}", file=sys.stderr) 
    sys.exit(1)

try:
    s.listen()
except Exception as e:
    print(f"CRITICAL: Error during socket listen: {e}", file=sys.stderr)
    sys.exit(1)

print("Waiting for a connection...", file=sys.stderr) 

game_state = {
    # "players": [(0, 0, 100, 0, 0), (100, 100, 100, 0, 0)], # (x, y, health)
    "players": {},
    "projectiles": [],
    "kill_streaks": {}
}

next_projectile_id = 0 
player_id_lock = threading.Lock()
next_player_id_counter = 0

def threaded_client(conn, player_id):
    global next_projectile_id
    try:
        with game_state_lock:
            if player_id not in game_state["players"]:
                print(f"Player {player_id} not found in game_state at thread start.")
                conn.close()
                return
            my_player_data = game_state["players"][player_id]
            
            other_players_initial_data = {}
            for p_id, p_data in game_state["players"].items():
                if p_id != player_id:
                    other_players_initial_data[p_id] = p_data

        initial_data_for_client = {
            "my_id": player_id,
            "my_player": my_player_data,
            "other_players": other_players_initial_data,
            "projectiles": [],
            "all_kill_streaks": game_state["kill_streaks"].copy()
        }
        conn.send(str.encode(make_pos(initial_data_for_client)))
    
    except Exception as e:
        print(f"Error sending initial data to client for player {player_id}: {e}")
        conn.close()
        return
    
    while True:
        respawn_events_this_tick = {}
        try:
            raw_data = conn.recv(2048).decode("utf-8")
            if not raw_data:
                print(f"Player {player_id} disconnected (no data).")
                break

            print(f"Raw data from player {player_id}: {raw_data}")
            data = read_pos(raw_data)

            if data is None:
                print(f"Invalid JSON data received from player {player_id}: {raw_data}")
                continue

            if isinstance(data, dict) and data.get('action') == 'shoot':
                # print("shoot attempted")
                details = data.get('details')
                if details:
                    print(f"Player {player_id} shoot command: {details}")
                    with projectile_lock:
                        next_projectile_id += 1
                        proj_id = next_projectile_id
                    owner_id = player_id
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
                        with projectile_lock:
                            new_projectile = Projectile(id=proj_id, x=start_x, y=start_y, 
                                                        vx=vx, vy=vy, radius=radius, 
                                                        owner_id=owner_id, damage=damage, projectile_type=proj_type)
                            game_state["projectiles"].append(new_projectile)
                        print(f"Created projectile {proj_id} for player {player_id}")
                    else:
                        print(f"Missing details in shoot command from player {player_id}")
                else:
                    print(f"Shoot command from player {player_id} missing 'details'.")

            elif isinstance(data, (list, tuple)):
                # print("updating info attempted")
                if len(data) == 5:
                    try:
                        with game_state_lock:
                            if player_id in game_state["players"]:
                                current_health = game_state["players"][player_id][2]
                                game_state["players"][player_id] = (float(data[0]), float(data[1]), current_health, float(data[3]), float(data[4]))
                            else:
                                print(f"Player {player_id} not found for position update, likely disconnected.")
                                break
                    except (ValueError, TypeError) as e:
                        print(f"Invalid position data format from player {player_id}: {data}, error: {e}")
                else:
                    print(f"Invalid position data structure from player {player_id}: {data}")
            
            else:
                print(f"Unknown data type received from player {player_id}: {type(data)}, data: {data}")

            
            projectiles_to_remove = []
            with projectile_lock:
                current_projectiles = game_state["projectiles"][:]
            
            for proj in current_projectiles:
                proj.update()
                screen_width = 600 
                screen_height = 300
                if not (-3000 < proj.position[0] < 3000 and \
                        -3000 < proj.position[1] < 3000):
                    if proj not in projectiles_to_remove:
                        projectiles_to_remove.append(proj)
                    print(f"Projectile {proj.id} removed due to boundary.")
                    continue
                    
                player_width = 50
                player_height = 50
                projectile_damage = proj.damage

                with game_state_lock:
                    active_player_ids_for_collision = list(game_state["players"].keys())
                    for p_id_collision in active_player_ids_for_collision:
                        if p_id_collision not in game_state["players"]:
                            continue
                        player_data = game_state["players"][p_id_collision]
                        player_pos_x, player_pos_y, player_health, _m_x, _m_y = player_data
                        
                        player_rect_x_start = player_pos_x
                        player_rect_x_end = player_pos_x + player_width
                        player_rect_y_start = player_pos_y
                        player_rect_y_end = player_pos_y + player_height

                        proj_center_x = proj.position[0]
                        proj_center_y = proj.position[1]

                        collided = (player_rect_x_start < proj_center_x < player_rect_x_end and \
                                    player_rect_y_start < proj_center_y < player_rect_y_end)

                        if collided:
                            if proj.owner_id != p_id_collision:
                                new_health = player_health - projectile_damage
                                if new_health <= 0:
                                    killer_id = proj.owner_id
                                    killed_id = p_id_collision
                                    
                                    game_state["players"][killed_id] = (player_pos_x, player_pos_y, 100, _m_x, _m_y)

                                    if killer_id != killed_id: # No self-kill streak
                                        game_state["kill_streaks"][killer_id] = game_state["kill_streaks"].get(killer_id, 0) + 1
                                    
                                    game_state["kill_streaks"][killed_id] = 0

                                    new_x_respawn = random.uniform(-2000, 2000)
                                    new_y_respawn = random.uniform(-2000, 2000)
                                    # print(f"DEBUG SERVER: Player {killed_id} died. Generated respawn coords: ({new_x_respawn}, {new_y_respawn}). Storing for respawn event.", file=sys.stderr)
                                    respawn_events_this_tick[killed_id] = [new_x_respawn, new_y_respawn]
                                    
                                    print(f"Player {killed_id} killed by {killer_id}. Health set to 100. Respawn event generated for ({new_x_respawn}, {new_y_respawn}).")
                                else:
                                    game_state["players"][p_id_collision] = (player_pos_x, player_pos_y, new_health, _m_x, _m_y)
                                    print(f"Player {p_id_collision} hit by projectile {proj.id}. Health: {new_health}")
                                
                                if proj not in projectiles_to_remove:
                                    projectiles_to_remove.append(proj)
            with projectile_lock:    
                for proj_to_remove in projectiles_to_remove:
                    if proj_to_remove in game_state["projectiles"]:
                        game_state["projectiles"].remove(proj_to_remove)

            my_current_health = -1
            other_players_update_data = {}
            
            with game_state_lock:
                if player_id in game_state["players"]:
                    my_current_health = game_state["players"][player_id][2]
                    for p_id_update, p_data_update in game_state["players"].items():
                        if p_id_update != player_id:
                            other_players_update_data[p_id_update] = p_data_update
                else:
                    print(f"Player {player_id} disconnected before sending update packet.")
                    break 
            
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
                "my_id": player_id,
                "my_player_updated_health": my_current_health,
                "other_players": other_players_update_data,
                "projectiles": projectiles_data_for_client,
                "all_kill_streaks": game_state["kill_streaks"].copy(),
                "event_for_me": None
            }

            my_event_data_for_packet = respawn_events_this_tick.get(player_id)
            if my_event_data_for_packet is not None:
                data_to_send_client["event_for_me"] = {
                    "type": "respawn",
                    "pos": my_event_data_for_packet
                }
                # print(f"DEBUG SERVER: Sending 'event_for_me' to player {player_id}: {{'type': 'respawn', 'pos': {my_event_data_for_packet}}}", file=sys.stderr)
                print(f"Player {player_id} has a respawn event: {data_to_send_client['event_for_me']}")
            
            current_streaks_for_log = data_to_send_client['all_kill_streaks']
            print(f"Player {player_id} state update. Sending my_health: {my_current_health}, all_kill_streaks: {current_streaks_for_log}, other_players: {len(other_players_update_data)}, projectiles: {len(projectiles_data_for_client)}, event: {data_to_send_client['event_for_me']}")
            conn.sendall(str.encode(make_pos(data_to_send_client)))

        except socket.error as e:
            print(f"Socket error for player {player_id}: {e}")
            break
        
        except Exception as e:
            print(f"Error in player {player_id}'s thread: {e}")
            import traceback
            traceback.print_exc()
            break
    
    print(f"Player {player_id} lost connection.")
    with game_state_lock:
        if player_id in game_state["players"]:
            del game_state["players"][player_id]
            print(f"Player {player_id} removed from game_state. Total players: {len(game_state['players'])}")
        if player_id in game_state["kill_streaks"]:
            del game_state["kill_streaks"][player_id]
            print(f"Kill streak data for player {player_id} removed.")
    conn.close()

while True:
    conn, addr = s.accept()
    print("Connected to: ", addr)
    
    current_id = -1
    with player_id_lock:
        current_id = next_player_id_counter
        next_player_id_counter += 1
    
    initial_x, initial_y, initial_health, initial_mouse_x, initial_mouse_y = 50, 50, 100, 0, 0
    with game_state_lock:
        game_state["players"][current_id] = (initial_x, initial_y, initial_health, initial_mouse_x, initial_mouse_y)
        game_state["kill_streaks"][current_id] = 0
        print(f"Player {current_id} connected. Total players: {len(game_state['players'])}. Kill streak initialized.")

    start_new_thread(threaded_client, (conn, current_id))