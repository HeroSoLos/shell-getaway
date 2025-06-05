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

"""
lots to explain and not a class so I won't write a java doc
In essence though, all the server side processes (health, request by players, collosions, projectile spawning, player tracking)
are handled here in this threaded client function.
"""
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
            
            ###########################
            # print(f"Raw data from player {player_id}: {raw_data}")
            
            data = read_pos(raw_data)

            if data is None:
                print(f"Invalid JSON data received from player {player_id}: {raw_data}")
                continue

            # ULTIMATE DEBUG LINE
            # print(f"Raw data from player {player_id}: {raw_data}") 

            actions_to_process = []
            if isinstance(data, list) and data and all(isinstance(item, dict) and 'action' in item for item in data):
                actions_to_process = data
            elif isinstance(data, dict) and 'action' in data:
                actions_to_process = [data] # convert list

            # Process acksions
            if actions_to_process:
                for action_item in actions_to_process:
                    if action_item.get('action') == 'shoot':
                        details = action_item.get('details')
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
                                print(details)
                                projectile_speed = details.get('projectile_speed', 10)
                                print("Projectile speed" + str(projectile_speed))
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
                                print(f"Created projectile {proj_id} for player {player_id} (Action: Shoot)") 
                            else:
                                print(f"Missing details in shoot command from player {player_id}: {details}")
                        else:
                            print(f"Shoot command from player {player_id} missing 'details': {action_item}")
                    
                    elif action_item.get('action') == 'switch_weapon':
                        new_weapon_id = action_item.get('weapon_id')
                        if new_weapon_id:
                            print(f"Player {player_id} switch weapon command to: {new_weapon_id}") 
                            with game_state_lock: 
                                if player_id in game_state["players"]:
                                    current_player_data = game_state["players"][player_id]
                                    px, py, phealth = current_player_data[0], current_player_data[1], current_player_data[2]
                                    mouse_x = current_player_data[3] if len(current_player_data) > 3 else 0
                                    mouse_y = current_player_data[4] if len(current_player_data) > 4 else 0
                                    
                                    game_state["players"][player_id] = (px, py, phealth, mouse_x, mouse_y, new_weapon_id)
                                    print(f"Player {player_id} successfully switched to weapon: {new_weapon_id}") 
                                else:
                                    print(f"Player {player_id} not found for weapon switch, likely disconnected.")
                        else:
                            print(f"Switch weapon command from player {player_id} missing 'weapon_id': {action_item}")
                    
                    elif action_item.get('action') == 'restore_health':
                        with game_state_lock:
                            if player_id in game_state["players"] and player_id in game_state["kill_streaks"]:
                                current_kills = game_state["kill_streaks"][player_id]
                                if current_kills >= 2:
                                    current_player_data = game_state["players"][player_id]
                                    px, py, _old_health, mouse_x, mouse_y, p_active_weapon_id = current_player_data
                                    
                                    game_state["players"][player_id] = (px, py, 100, mouse_x, mouse_y, p_active_weapon_id)
                                    game_state["kill_streaks"][player_id] = current_kills - 2
                                    print(f"Player {player_id} restored health. Kills updated to: {game_state['kill_streaks'][player_id]}")
                                else:
                                    print(f"Player {player_id} attempted to restore health but had insufficient kills: {current_kills}")
                            else:
                                print(f"Player {player_id} not found in game_state['players'] or game_state['kill_streaks'] for restore_health action.")
                    else:
                        print(f"Unknown action in action list/dict from player {player_id}: {action_item}")

            elif isinstance(data, (list, tuple)):
                if len(data) == 5 and \
                   all(isinstance(x, (int, float)) for x in [data[0], data[1], data[3], data[4]]) and \
                   isinstance(data[2], (int, float)): # [x,y,h,mx,my]
                    # print(f"Player {player_id} position update: {data}") # Optional log
                    try:
                        with game_state_lock: 
                            if player_id in game_state["players"]:
                                current_player_server_data = game_state["players"][player_id]
                                server_health = current_player_server_data[2] 
                                server_weapon_id = current_player_server_data[5] if len(current_player_server_data) > 5 else "sniper" 
                                
                                game_state["players"][player_id] = (float(data[0]), 
                                                                    float(data[1]), 
                                                                    server_health,  
                                                                    float(data[3]), 
                                                                    float(data[4]), 
                                                                    server_weapon_id)
                            else:
                                print(f"Player {player_id} not found for position update, likely disconnected before this point.")
                                break
                    except (ValueError, TypeError) as e:
                        print(f"Invalid position data format from player {player_id}: {data}, error: {e}")
                else:
                    if data: 
                        print(f"Received unhandled list/tuple data structure from player {player_id}: {data}")
            
            elif isinstance(data, dict):
                print(f"Received unhandled dictionary (not an action) from player {player_id}: {data}")
            
            else:
                if data is not None and data != []:
                    print(f"Unknown or unhandled data type received from player {player_id}: {type(data)}, data: {data}")
            
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
                        player_pos_x, player_pos_y, player_health, _m_x, _m_y, p_active_weapon_id = player_data
                        
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
                                    
                                    killed_player_current_weapon_id = game_state["players"][killed_id][5]
                                    game_state["players"][killed_id] = (player_pos_x, player_pos_y, 100, _m_x, _m_y, killed_player_current_weapon_id)

                                    if killer_id != killed_id:
                                        game_state["kill_streaks"][killer_id] = game_state["kill_streaks"].get(killer_id, 0) + 1
                                    
                                    game_state["kill_streaks"][killed_id] = 0

                                    new_x_respawn = random.uniform(-2000, 2000)
                                    new_y_respawn = random.uniform(-2000, 2000)
                                    print(f"DEBUG SERVER: Player {killed_id} died. Generated respawn coords: ({new_x_respawn}, {new_y_respawn}). Storing for respawn event.", file=sys.stderr)
                                    respawn_events_this_tick[killed_id] = [new_x_respawn, new_y_respawn]
                                    
                                    # game_state["players"][killed_id] already updated with new health and preserved weapon_id
                                    print(f"Player {killed_id} killed by {killer_id}. Health set to 100. Weapon ID {killed_player_current_weapon_id} preserved. Respawn event generated for ({new_x_respawn}, {new_y_respawn}).")
                                else:
                                    hit_player_current_weapon_id = game_state["players"][p_id_collision][5]
                                    game_state["players"][p_id_collision] = (player_pos_x, player_pos_y, new_health, _m_x, _m_y, hit_player_current_weapon_id)
                                    print(f"Player {p_id_collision} hit by projectile {proj.id}. Health: {new_health}. Weapon ID {hit_player_current_weapon_id} preserved.")
                                
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
            # print(f"Player {player_id} state update. Sending my_health: {my_current_health}, all_kill_streaks: {current_streaks_for_log}, other_players: {len(other_players_update_data)}, projectiles: {len(projectiles_data_for_client)}, event: {data_to_send_client['event_for_me']}")
            conn.sendall((make_pos(data_to_send_client) + "\n").encode())

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
    initial_weapon_id = "sniper"
    with game_state_lock:
        game_state["players"][current_id] = (initial_x, initial_y, initial_health, initial_mouse_x, initial_mouse_y, initial_weapon_id)
        game_state["kill_streaks"][current_id] = 0
        print(f"Player {current_id} connected. Initial weapon: {initial_weapon_id}. Total players: {len(game_state['players'])}. Kill streak initialized.")

    start_new_thread(threaded_client, (conn, current_id))