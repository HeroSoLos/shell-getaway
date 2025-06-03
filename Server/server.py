import socket
from _thread import *
from utils import *
from config import SERVER_IP
from Gun.projectile import Projectile # Import Projectile class
import math # For vector calculations
import threading # For locking

server = SERVER_IP
port = 5555
projectile_lock = threading.Lock() # Lock for synchronizing access to projectiles

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

try:
    s.bind((server, port))
except socket.error as e:
    str(e)

s.listen(2)
print("Waiting for a connection...")

game_state = {
    "players": [(0, 0, 100), (100, 100, 100)], # (x, y, health)
    "projectiles": [] # Will store Projectile objects
}

next_projectile_id = 0 # Global for unique projectile IDs

def threaded_client(conn, player):
    global next_projectile_id # Declare usage of global variable
    try:
        # Initial send: only the player's own data (or other relevant initial state)
        # The client will expect other_player data and projectiles in the regular updates.
        # Send initial game state including client's own player data, other player's data, and empty projectiles list.
        my_player_data = game_state["players"][player]
        other_player_id = 1 - player
        # Ensure other_player_id is valid, especially if player 1 connects before player 0 state is fully set (though less likely with sequential currentPlayer)
        other_player_data = game_state["players"][other_player_id] if 0 <= other_player_id < len(game_state["players"]) else (0,0,100)


        initial_data_for_client = {
            "my_player": my_player_data,
            "other_player": other_player_data,
            "projectiles": [] # Initially no projectiles
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
            data = read_pos(raw_data) # data is now a dict or list/tuple (or None if JSON error)

            if data is None: # JSON decoding error
                print(f"Invalid JSON data received from player {player}: {raw_data}")
                continue

            if isinstance(data, dict) and data.get('action') == 'shoot':
                # This is a shoot command
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
                    # damage = details.get('damage') # Store if needed, or handle based on type

                    if start_x is not None and start_y is not None and target_x is not None and target_y is not None:
                        dir_x = target_x - start_x
                        dir_y = target_y - start_y
                        magnitude = math.sqrt(dir_x**2 + dir_y**2)
                        
                        projectile_speed = 10 # Default speed

                        if magnitude == 0: # Avoid division by zero
                            vx, vy = 0, projectile_speed # Default upwards or a configurable default
                        else:
                            norm_dir_x = dir_x / magnitude
                            norm_dir_y = dir_y / magnitude
                            vx = norm_dir_x * projectile_speed
                            vy = norm_dir_y * projectile_speed
                        
                        radius = 5 # Default radius

                        new_projectile = Projectile(id=proj_id, x=start_x, y=start_y, 
                                                    vx=vx, vy=vy, radius=radius, 
                                                    owner_id=owner_id, projectile_type=proj_type)
                        game_state["projectiles"].append(new_projectile)
                        print(f"Created projectile {proj_id} for player {player}")
                    else:
                        print(f"Missing details in shoot command from player {player}")
                else:
                    print(f"Shoot command from player {player} missing 'details'.")

            elif isinstance(data, (list, tuple)): # Assuming player position update (x, y, health)
                # Basic validation for player data structure
                if len(data) == 3:
                    try:
                        # Ensure data can be converted to the expected types if necessary,
                        # though json.loads should handle numbers appropriately.
                        pos_data = (float(data[0]), float(data[1]), float(data[2]))
                        game_state["players"][player] = pos_data
                    except (ValueError, TypeError) as e:
                        print(f"Invalid position data format from player {player}: {data}, error: {e}")
                else:
                    print(f"Invalid position data structure from player {player}: {data}")
            
            else: # Unknown data type
                print(f"Unknown data type received from player {player}: {type(data)}, data: {data}")

            # Projectile Update, Boundary Checks, and Collision Detection Logic
            # This logic should ideally run once per server tick, not per client message if messages are frequent.
            # However, for this structure, we'll place it here.
            # Consider a separate game loop thread on the server for a more robust simulation.
            
            projectiles_to_remove = []
            with projectile_lock: # Ensure only one thread modifies projectiles/player health at a time
                # Update projectiles and check boundaries
                for proj in game_state["projectiles"][:]: # Iterate over a copy for safe removal
                    proj.update()
                    # Boundary checks (example values)
                    screen_width = 600 
                    screen_height = 300
                    if not (-50 < proj.position[0] < screen_width + 50 and \
                            -50 < proj.position[1] < screen_height + 50):
                        if proj not in projectiles_to_remove:
                           projectiles_to_remove.append(proj)
                        print(f"Projectile {proj.id} removed due to boundary.")
                        continue # No need to check collision if out of bounds
                    
                    # Collision detection with players
                    player_width = 50  # Assuming Player.WIDTH
                    player_height = 50 # Assuming Player.HEIGHT
                    projectile_damage = 10 # Fixed damage for now

                    for player_idx, player_data in enumerate(game_state["players"]):
                        player_pos_x, player_pos_y, player_health = player_data
                        
                        # Simple AABB collision for player
                        player_rect_x_start = player_pos_x
                        player_rect_x_end = player_pos_x + player_width
                        player_rect_y_start = player_pos_y
                        player_rect_y_end = player_pos_y + player_height

                        # Projectile center
                        proj_center_x = proj.position[0]
                        proj_center_y = proj.position[1]

                        # Check collision (point-in-rect for projectile center)
                        collided = (player_rect_x_start < proj_center_x < player_rect_x_end and \
                                    player_rect_y_start < proj_center_y < player_rect_y_end)

                        if collided:
                            if proj.owner_id != player_idx: # Cannot shoot self
                                new_health = player_health - projectile_damage
                                game_state["players"][player_idx] = (player_pos_x, player_pos_y, max(0, new_health))
                                print(f"Player {player_idx} hit by projectile {proj.id}. Health: {new_health}")
                                if proj not in projectiles_to_remove:
                                    projectiles_to_remove.append(proj)
                                break # Projectile hits one player at most and is removed
                
                # Remove projectiles marked for removal
                for proj_to_remove in projectiles_to_remove:
                    if proj_to_remove in game_state["projectiles"]:
                        game_state["projectiles"].remove(proj_to_remove)

            # Prepare data to send to the client
            # The 'player' variable in threaded_client is the index of the current player for this thread
            my_current_health = game_state["players"][player][2] # Get current player's health after potential updates
            
            other_player_id = 1 - player
            if 0 <= other_player_id < len(game_state["players"]):
                reply_other_player_data = game_state["players"][other_player_id]
            else:
                reply_other_player_data = (0.0, 0.0, 100.0) # Fallback
            
            # Serialize projectile data for sending
            projectiles_data_for_client = []
            with projectile_lock: # Access game_state["projectiles"] under lock
                for p_obj in game_state["projectiles"]:
                    projectiles_data_for_client.append((
                        p_obj.id,
                        round(p_obj.position[0], 2), # Round floats for smaller strings
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
            # print(f"Player {player} state update. Sending my_health: {my_current_health}, other_player: {reply_other_player_data}, projectiles: {len(projectiles_data_for_client)}")
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