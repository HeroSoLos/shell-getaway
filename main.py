# Imports
import pygame
from Player.Player import *
from Gun.base_gun import *
from Physics import *
from Server.utils import *
from Server.network import *
from Gun.projectile import Projectile # Import Projectile class
# pygame setup
pygame.init()
screen = pygame.display.set_mode((600, 300))#1280, 720
clock = pygame.time.Clock()
running = True

# Object setup
n = Network()
Physics = Physics()
# Create unique gun instances if they are to have different states (e.g. projectile_type)
# For now, assuming BaseGun is primarily for stats and the shoot() method.
# Player's gun is set in Player.__init__
# gun = BaseGun(magazine_size=10, x=0, y=0, sprite="assets/sniper.png") 

# Initial player setup using data from server
initial_state = n.get_initial_state() # Returns a dict: {"my_player": (x,y,h), "other_player": (x,y,h), "projectiles": []}
my_initial_pos = (50, 50) # Default if server data fails
my_initial_health = 100
other_initial_pos = (100, 100)
other_initial_health = 100

if initial_state:
    if "my_player" in initial_state and initial_state["my_player"]:
        my_initial_pos = initial_state["my_player"][:2]
        my_initial_health = initial_state["my_player"][2]
    if "other_player" in initial_state and initial_state["other_player"]:
        other_initial_pos = initial_state["other_player"][:2]
        other_initial_health = initial_state["other_player"][2]
else:
    print("Failed to get initial state from server. Using defaults.")

# Player objects
# Pass projectile_type to BaseGun if you want different guns to shoot different things
player_gun = BaseGun(magazine_size=10, x=0, y=0, sprite="assets/sniper.png", projectile_type='standard_bullet')
p = Player(health=my_initial_health, move_speed=5, gun=player_gun, screen=screen, player=None, sprite="assets/Egg_sprite.png")
p.position = list(my_initial_pos) # Player position is a list

# p2 (other player)
# Gun for p2 is not strictly needed on client unless for display, server handles its shots.
# For simplicity, let's assume p2 uses a default gun visually or not shown.
p2_gun = BaseGun(magazine_size=10, x=0, y=0, sprite="assets/sniper.png") 
p2 = Player(health=other_initial_health, move_speed=5, gun=p2_gun, screen=screen, player=None, sprite="assets/Egg_sprite.png")
p2.position = list(other_initial_pos)
p.player = p2 # For local interactions if any, or targetting logic (though server is authoritative)


# Game loop
while running:
    # Get mouse position once per frame, if needed for aiming or UI
    # For shooting, it's better to get it at the moment of click inside event loop.
    # m_x, m_y = pygame.mouse.get_pos() 

    # Default data to send is player's current state (position and health)
    # Ensure p.position is up-to-date before this if movement happens before event processing
    data_to_send = [p.position[0], p.position[1], p.health]

    # Event handling
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1: # Left mouse click
                m_x, m_y = pygame.mouse.get_pos() # Get mouse position at the time of click
                shoot_command_details = p.shoot(m_x, m_y) # Player.shoot now calls gun.shoot
                if shoot_command_details:
                    # If gun.shoot returned details (i.e., a shot was possible),
                    # prepare a shoot action command for the server.
                    data_to_send = {"action": "shoot", "details": shoot_command_details}
                    # print(f"Client: Prepared shoot command: {data_to_send}") # For debugging
                # else:
                    # print("Client: Gun.shoot returned None (e.g., no ammo). No shoot command sent.") # For debugging

    # fill the screen with a color to wipe away anything from last frame
    screen.fill("white")

    # Game Rendering
    
    # Borders Collosions
    if p.position[1] < 0:
        p.position = (p.position[0], 0)
        p.velocity[1] = 0
    if p.position[1] > screen.get_height() - 50:
        p.position = (p.position[0], screen.get_height() - 50)
        p.velocity[1] = 0
    if p.position[0] < 0:
        p.position = (0, p.position[1])
        p.velocity[0] = 0
    if p.position[0] > screen.get_width() - 50:
        p.position = (screen.get_width() - 50, p.position[1])
        p.velocity[0] = 0
    

    # Update player position based on input
    keys = pygame.key.get_pressed()
    direction = [0, 0]
    if keys[pygame.K_LEFT]:
        direction[0] = -.1
    if keys[pygame.K_RIGHT]:
        direction[0] = .1
    if keys[pygame.K_UP]:
        direction[1] = -.1
    if keys[pygame.K_r]:
        p.health = 100
        p2.health = 100
    p.update_velocity(direction)
    
    
    Physics.applyGravity([p])
    p.update_position()
    
    
    # Physics and Position updates for local player (p) should happen before sending its state
    Physics.applyGravity([p]) # Assuming this modifies p.velocity or p.position
    p.update_position() # Updates p.position from its velocity, and gun position
    
    # Now, data_to_send is either the shoot command (if occurred) or default player state
    # Update data_to_send with the most current player state if it's not a shoot command
    if not (isinstance(data_to_send, dict) and data_to_send.get("action") == "shoot"):
        data_to_send = [p.position[0], p.position[1], p.health]

    # Send data (either position update or shoot command) to server and get game state
    current_game_state = n.send(data_to_send) 

    if current_game_state:
        # Update current player's health (as confirmed/updated by server after any event)
        if "my_player_updated_health" in current_game_state: # Key for current player's health
            p.health = current_game_state["my_player_updated_health"]

        # Update other player's state from "other_player" key
        if "other_player" in current_game_state and current_game_state["other_player"]:
            p2_server_data = current_game_state["other_player"] # This is a tuple (x,y,health)
            p2.position[0] = p2_server_data[0]
            p2.position[1] = p2_server_data[1]
            p2.health = p2_server_data[2]
            p2.rect.topleft = (p2.position[0], p2.position[1]) # Update rect for drawing

        # Render projectiles
        if "projectiles" in current_game_state:
            for proj_data in current_game_state["projectiles"]:
                if len(proj_data) == 7: # (id, x, y, vx, vy, projectile_type, owner_id)
                    proj_id, proj_x, proj_y, proj_vx, proj_vy, proj_type, owner_id = proj_data
                    Projectile.draw(screen, pygame, proj_x, proj_y, proj_vx, proj_vy, proj_type)
                else:
                    print(f"Received malformed projectile data: {proj_data}")
    else:
        print("Warning: Failed to receive game state from server.")

    # Get current mouse position for local player's gun aiming
    # This should be done each frame for rendering the local player's gun correctly.
    m_x_render, m_y_render = pygame.mouse.get_pos()

    # Draw local player
    if p.health > 0:
        p.draw(m_x_render, m_y_render) # p.draw uses mouse coords for gun direction
    
    # Draw other player
    if p2.health > 0:
        # For p2, gun direction relative to mouse is not applicable,
        # so pass its own position or 0,0 if gun direction isn't drawn based on mouse.
        # Assuming p2.draw can handle this (e.g., draws gun in a default forward direction or based on its movement)
        p2.draw(p2.position[0], p2.position[1]) 

    pygame.display.flip()

    # Time/FPS control
    clock.tick(60)  # limits FPS to 60

pygame.quit()