# Imports
import pygame
from Player.Player import *
from Gun.base_gun import *
from Physics import *
from Server.utils import *
from Server.network import *
from Gun.projectile import Projectile
from Gun.compressor import Compressor
# pygame setup
pygame.init()
kill_streak_font = pygame.font.SysFont(None, 30)
screen = pygame.display.set_mode((900, 600))
camera_offset_x = 0
camera_offset_y = 0
screen_width = screen.get_width()
screen_height = screen.get_height()
clock = pygame.time.Clock()
running = True

# Weapon instances for local player
primary_gun_local_player_instance = BaseGun(magazine_size=10, x=0, y=0, sprite="assets/sniper.png", reload_time=60, shoot_cooldown=6, projectile_type='standard_bullet', weapon_type_id="sniper")
secondary_gun_local_player_instance = Compressor(10, 0, 0, sprite="assets/Compressor.png", reload_time=10, shoot_cooldown=10, damage=10, projectile_type='compressor_shot', weapon_type_id="compressor")


# Object setup
n = Network()
Physics = Physics()

# Initial player setup using data from server
initial_state = n.get_initial_state()
my_player_id = None
player_objects = {}
local_player = None
current_all_player_streaks = {}

if initial_state and "my_id" in initial_state:
    my_player_id = initial_state["my_id"]
    my_data = initial_state.get("my_player")
    if my_data:
        p_obj = Player(health=my_data[2], 
                       move_speed=5, 
                       primary_gun=primary_gun_local_player_instance, 
                       secondary_gun=secondary_gun_local_player_instance, 
                       screen=screen, 
                       player=None, 
                       sprite="assets/Egg_sprite.png")
        p_obj.position = list(my_data[:2])
        p_obj.rect.topleft = tuple(p_obj.position)
        player_objects[my_player_id] = p_obj
        print(f"Local player {my_player_id} created. Pos: {p_obj.position}, Health: {p_obj.health}")


    if "other_players" in initial_state:
        for other_id, other_data in initial_state["other_players"].items():
            if other_id == my_player_id: continue 
            other_player_primary_gun = BaseGun(magazine_size=10, x=0, y=0, sprite="assets/sniper.png", reload_time=60, shoot_cooldown=6, projectile_type='standard_bullet', weapon_type_id="sniper")
            other_player_secondary_gun = Compressor(10, 0, 0, sprite="assets/RPG.png", reload_time=10, shoot_cooldown=10, damage=10, projectile_type='compressor_shot', weapon_type_id="compressor")
            op_obj = Player(health=other_data[2], 
                            move_speed=5, 
                            primary_gun=other_player_primary_gun, 
                            secondary_gun=other_player_secondary_gun, 
                            screen=screen, 
                            player=None, 
                            sprite="assets/Egg_sprite.png")
            op_obj.position = list(other_data[:2])
            op_obj.rect.topleft = tuple(op_obj.position)
            player_objects[other_id] = op_obj
            print(f"Initial other player {other_id} created. Pos: {op_obj.position}, Health: {op_obj.health}")
else:
    print("Failed to get initial state or player ID from server. Exiting.")
    running = False

if my_player_id is not None and my_player_id in player_objects:
    local_player = player_objects[my_player_id]
else:
    print("Local player object could not be initialized. Exiting.")
    running = False

m_x, m_y = 0, 0
# Game loop
while running:
    m_x_screen, m_y_screen = pygame.mouse.get_pos()
    m_x = m_x_screen + camera_offset_x
    m_y = m_y_screen + camera_offset_y
    data_to_send = None
    if local_player:
        data_to_send = [local_player.position[0], local_player.position[1], local_player.health, m_x, m_y]
    
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if local_player:
            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1: # Left mouse button
                    shoot_command_details = local_player.shoot(local_player, m_x, m_y)
                    if shoot_command_details:
                        data_to_send = {"action": "shoot", "details": shoot_command_details}
            elif event.type == pygame.KEYDOWN:
                switched_weapon_id = None
                if event.key == pygame.K_1:
                    switched_weapon_id = local_player.switch_weapon(0)
                    print(f"Switched to {switched_weapon_id}")
                    data_to_send = {"action": "switch_weapon", "weapon_id": switched_weapon_id}
                elif event.key == pygame.K_2:
                    switched_weapon_id = local_player.switch_weapon(1)
                    print(f"Switched to {switched_weapon_id}")
                    data_to_send = {"action": "switch_weapon", "weapon_id": switched_weapon_id}

    # move and collosion stuff
    if local_player:
        if local_player.position[1] < -3000:
            local_player.position = (local_player.position[0], -3000)
            local_player.velocity[1] = 0
        if local_player.position[1] > 3000 - 50:
            local_player.position = (local_player.position[0], 3000 - 50)
            local_player.velocity[1] = 0
        if local_player.position[0] < -3000:
            local_player.position = (-3000, local_player.position[1])
            local_player.velocity[0] = 0
        if local_player.position[0] > 3000 - 50:
            local_player.position = (3000 - 50, local_player.position[1])
            local_player.velocity[0] = 0

        keys = pygame.key.get_pressed()
        direction = [0, 0]
        if keys[pygame.K_LEFT]:
            direction[0] = -.1
        if keys[pygame.K_RIGHT]:
            direction[0] = .1
        if keys[pygame.K_UP]:
            direction[1] = -.1
        if keys[pygame.K_DOWN]:
            direction[1] = .1
        if keys[pygame.K_q]: # This was for testing compressor directly, might be removed or kept.
            # If kept, it should use the active gun if compressor is selected.
            # For now, assuming it's for testing and might not align with new weapon switching.
            # local_player.gun.shoot(local_player, m_x, m_y) # This would use the active gun
            pass # Decided to comment out direct compressor test via Q for now.
        local_player.update_velocity(direction)
        
        Physics.applyFriction(local_player)
        Physics.capVelocity(local_player)
        # Physics.applyGravity([local_player])
        local_player.update_position()

        if local_player:
            camera_offset_x = local_player.position[0] - screen_width / 2
            camera_offset_y = local_player.position[1] - screen_height / 2
        
        if not isinstance(data_to_send, dict):
            data_to_send = [local_player.position[0], local_player.position[1], local_player.health, m_x, m_y]

    current_game_state = n.send(data_to_send)
    # print(current_game_state)
    if current_game_state:
        current_all_player_streaks = current_game_state.get("all_kill_streaks", {})
        if local_player:
            if "my_player_updated_health" in current_game_state:
                local_player.health = current_game_state["my_player_updated_health"]
            if my_player_id is not None:
                local_player.kill_streak = current_all_player_streaks.get(str(my_player_id), 0)
            
            my_event = current_game_state.get("event_for_me")
            # if my_event is not None:
                # print(f"DEBUG CLIENT: Received event_for_me = {my_event}", file=sys.stderr)

            if my_event and isinstance(my_event, dict):
                event_type = my_event.get("type")
                if event_type == "respawn":
                    new_pos = my_event.get("pos")
                    if isinstance(new_pos, (list, tuple)) and len(new_pos) == 2:
                        local_player.position[0] = new_pos[0]
                        local_player.position[1] = new_pos[1]
                        local_player.rect.x = local_player.position[0]
                        local_player.rect.y = local_player.position[1]
                        local_player.health = 100 # Ensure health is full on respawn
                        print(f"Local player respawn event processed. New position: {local_player.position}")
                else:
                    pass
                    # print(f"DEBUG CLIENT: Received event_for_me of unexpected type or structure: {my_event}", file=sys.stderr)
            elif my_event is not None:
                pass
                # print(f"DEBUG CLIENT: Received event_for_me with unexpected structure (not a dict or type missing): {my_event}", file=sys.stderr)


        server_other_players_data = current_game_state.get("other_players", {})
        # print(server_other_players_data) #######################
        current_client_other_player_ids = {pid for pid in player_objects.keys() if pid != my_player_id}
        server_player_ids = set(server_other_players_data.keys())

        for pid_to_remove in current_client_other_player_ids - server_player_ids:
            if pid_to_remove in player_objects:
                del player_objects[pid_to_remove]
                print(f"Removed player {pid_to_remove}")

        for pid_server, p_data_server in server_other_players_data.items():
            if pid_server == my_player_id:
                continue
            
            if pid_server in player_objects: 
                player_to_update = player_objects[pid_server]
                player_to_update.position = list(p_data_server[:2])
                player_to_update.health = p_data_server[2]
                player_to_update.rect.topleft = tuple(player_to_update.position)
                
                if len(p_data_server) > 5:
                    active_weapon_id_from_server = p_data_server[5]
                    if player_to_update.primary_gun and active_weapon_id_from_server == player_to_update.primary_gun.weapon_type_id:
                        player_to_update.switch_weapon(0)
                    elif player_to_update.secondary_gun and active_weapon_id_from_server == player_to_update.secondary_gun.weapon_type_id:
                        player_to_update.switch_weapon(1)
            else: # New player
                new_player_primary_gun = BaseGun(magazine_size=10, x=0, y=0, sprite="assets/sniper.png", reload_time=60, shoot_cooldown=6, projectile_type='standard_bullet', weapon_type_id="sniper")
                new_player_secondary_gun = Compressor(10, 0, 0, sprite="assets/RPG.png", reload_time=10, shoot_cooldown=10, damage=10, projectile_type='compressor_shot', weapon_type_id="compressor")
                new_p_obj = Player(health=p_data_server[2], 
                                   move_speed=5, 
                                   primary_gun=new_player_primary_gun, 
                                   secondary_gun=new_player_secondary_gun, 
                                   screen=screen, 
                                   player=None, 
                                   sprite="assets/Egg_sprite.png")
                new_p_obj.position = list(p_data_server[:2])
                new_p_obj.rect.topleft = tuple(new_p_obj.position)
                player_objects[pid_server] = new_p_obj
                print(f"Added new player {pid_server}")
                
                if len(p_data_server) > 5:
                    active_weapon_id_from_server = p_data_server[5]
                    if new_p_obj.primary_gun and active_weapon_id_from_server == new_p_obj.primary_gun.weapon_type_id:
                        new_p_obj.switch_weapon(0)
                    elif new_p_obj.secondary_gun and active_weapon_id_from_server == new_p_obj.secondary_gun.weapon_type_id:
                        new_p_obj.switch_weapon(1)
        
        screen.fill("white")
        if "projectiles" in current_game_state:
            for proj_data in current_game_state["projectiles"]:
                if len(proj_data) == 7: # id, x, y, vx, vy, type, owner_id
                    Projectile.draw(screen, pygame, proj_data[1] - camera_offset_x, proj_data[2] - camera_offset_y, proj_data[3], proj_data[4], proj_data[5])
    else:
        screen.fill("white")

    for pid_draw, p_obj_draw in player_objects.items():
        if p_obj_draw.health > 0:
            if pid_draw == my_player_id:
                p_obj_draw.draw(m_x, m_y, camera_offset_x, camera_offset_y) 
            else:
                remote_player_server_data = server_other_players_data.get(pid_draw)
                if remote_player_server_data and len(remote_player_server_data) >= 5:
                    p_obj_draw.draw(remote_player_server_data[3], remote_player_server_data[4], camera_offset_x, camera_offset_y)
                else:
                    p_obj_draw.draw(int(p_obj_draw.rect.centerx), int(p_obj_draw.rect.centery - 20), camera_offset_x, camera_offset_y)
            
            player_id_for_streak = pid_draw
            streak_count = current_all_player_streaks.get(str(player_id_for_streak), 0)
            streak_text_content = f"Kills:{streak_count}"
            text_render_surface = kill_streak_font.render(streak_text_content, True, (0, 0, 0))
            
            text_rect = text_render_surface.get_rect(centerx=p_obj_draw.rect.centerx - camera_offset_x, 
                                                     top=p_obj_draw.rect.y + 75 - camera_offset_y + 5)
            screen.blit(text_render_surface, text_rect)

    if local_player:
        arrow_margin = 20
        arrow_points_template = [(0, 0), (-15, -7), (-15, 7)]

        local_player_screen_center_x = screen_width / 2
        local_player_screen_center_y = screen_height / 2

        for pid_other, p_obj_other in player_objects.items():
            if pid_other == my_player_id or p_obj_other.health <= 0:
                continue

            other_world_x = p_obj_other.position[0] + p_obj_other.rect.width / 2
            other_world_y = p_obj_other.position[1] + p_obj_other.rect.height / 2
            
            other_screen_x = other_world_x - camera_offset_x
            other_screen_y = other_world_y - camera_offset_y

            is_off_screen = not (0 <= other_screen_x < screen_width and 0 <= other_screen_y < screen_height)

            if is_off_screen:
                angle_rad = math.atan2(other_screen_y - local_player_screen_center_y, other_screen_x - local_player_screen_center_x)
                edge_distance = min(local_player_screen_center_x, local_player_screen_center_y) - arrow_margin
                
                arrow_base_x = local_player_screen_center_x + math.cos(angle_rad) * edge_distance
                arrow_base_y = local_player_screen_center_y + math.sin(angle_rad) * edge_distance

                arrow_base_x = max(arrow_margin, min(arrow_base_x, screen_width - arrow_margin))
                arrow_base_y = max(arrow_margin, min(arrow_base_y, screen_height - arrow_margin))

                rotated_points = []
                for x_tpl, y_tpl in arrow_points_template:
                    rot_x = x_tpl * math.cos(angle_rad) - y_tpl * math.sin(angle_rad)
                    rot_y = x_tpl * math.sin(angle_rad) + y_tpl * math.cos(angle_rad)
                    rotated_points.append((rot_x + arrow_base_x, rot_y + arrow_base_y))
                
                pygame.draw.polygon(screen, (255, 100, 0), rotated_points)
    
    pygame.display.flip()
    clock.tick(60)

pygame.quit()