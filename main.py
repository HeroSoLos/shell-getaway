# Imports
import pygame
from Player.Player import *
from Gun.base_gun import *
from Physics import *
from Server.utils import *
from Server.network import *
from Gun.projectile import Projectile

# pygame setup
pygame.init()
screen = pygame.display.set_mode((600, 300))
clock = pygame.time.Clock()
running = True

# Object setup
n = Network()
Physics = Physics()

# Initial player setup using data from server
initial_state = n.get_initial_state()
my_initial_pos = (50, 50)
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
player_gun = BaseGun(magazine_size=10, x=0, y=0, sprite="assets/sniper.png", reload_time=60, shoot_cooldown=6, projectile_type='standard_bullet')
p = Player(health=my_initial_health, move_speed=5, gun=player_gun, screen=screen, player=None, sprite="assets/Egg_sprite.png")
p.position = list(my_initial_pos)

p2_gun = BaseGun(magazine_size=10, x=0, y=0, sprite="assets/sniper.png", reload_time=60, shoot_cooldown=6, projectile_type='standard_bullet')
p2 = Player(health=other_initial_health, move_speed=5, gun=p2_gun, screen=screen, player=None, sprite="assets/Egg_sprite.png")
# p2 = Player(health=other_initial_health, move_speed=5, gun=p2_gun, screen=screen, player=None)
p2.position = list(other_initial_pos)
p.player = p2

m_x = 0
m_y = 0
# Game loop
while running:
    data_to_send = [p.position[0], p.position[1], p.health, m_x, m_y]

    m_x, m_y = pygame.mouse.get_pos()
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:
                shoot_command_details = p.shoot(m_x, m_y)
                if shoot_command_details:
                    data_to_send = {"action": "shoot", "details": shoot_command_details}

    screen.fill("white")

    # Borders Collisions
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

    keys = pygame.key.get_pressed()
    direction = [0, 0]
    if keys[pygame.K_LEFT]:
        direction[0] = -.1
    if keys[pygame.K_RIGHT]:
        direction[0] = .1
    if keys[pygame.K_UP]:
        direction[1] = -.1
    p.update_velocity(direction)

    Physics.applyGravity([p])
    p.update_position()

    if not (isinstance(data_to_send, dict) and data_to_send.get("action") == "shoot"):
        data_to_send = [p.position[0], p.position[1], p.health, m_x, m_y]
        # data_to_send = [p.position[0], p.position[1], p.health]

    current_game_state = n.send(data_to_send)

    if current_game_state:
        if "my_player_updated_health" in current_game_state:
            p.health = current_game_state["my_player_updated_health"]

        if "other_player" in current_game_state and current_game_state["other_player"]:
            p2_server_data = current_game_state["other_player"]
            p2.position[0] = p2_server_data[0]
            p2.position[1] = p2_server_data[1]
            p2.health = p2_server_data[2]
            p2.rect.topleft = (p2.position[0], p2.position[1])
            p2.gun.update_pos(p2.rect.x, p2.rect.y)

        if "projectiles" in current_game_state:
            for proj_data in current_game_state["projectiles"]:
                if len(proj_data) == 7:
                    proj_id, proj_x, proj_y, proj_vx, proj_vy, proj_type, owner_id = proj_data
                    Projectile.draw(screen, pygame, proj_x, proj_y, proj_vx, proj_vy, proj_type)

    m_x_render, m_y_render = pygame.mouse.get_pos()

    if p.health > 0:
        p.draw(m_x_render, m_y_render)

    if p2.health > 0:
        # p2.draw(m_x_render, m_y_render)
        p2.draw(current_game_state["other_player"][3], current_game_state["other_player"][4]) # to be added

    pygame.display.flip()
    clock.tick(60)

pygame.quit()