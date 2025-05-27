# Imports
import pygame
from Player.Player import *
from Gun.base_gun import *
from Physics import *
from Server.utils import *
from Server.network import *
# pygame setup
pygame.init()
screen = pygame.display.set_mode((600, 300))#1280, 720
clock = pygame.time.Clock()
running = True

# Object setup
n = Network()
Physics = Physics()
gun = BaseGun(magazine_size=10, bullet_speed=5)
startPos = tuple(read_pos(n.getPos()))
p = Player(health=100, move_speed=5, gun=gun, screen=screen, sprite="assets/Egg_sprite.png")
p.position = startPos
p2 = Player(health=100, move_speed=5, gun=gun, screen=screen, sprite="assets/Egg_sprite.png")
p2.position = (0, 0)

# Game loop
while running:
    # Event handling
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    # fill the screen with a color to wipe away anything from last frame
    screen.fill("black")

    # Game Rendering
    
    # Borders Collosions
    if p.position[1] < 0:
        p.position = (p.position[0], 0)
        p.velocity[1] = 0
    if p.position[1] > screen.get_height() - 50:
        p.position = (p.position[0], screen.get_height() - 50)
        p.velocity[1] = 0

    # Update player position based on input
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
    
    
    # Send player position to server
    p2Pos = n.send(p.position)  # No need to call make_pos here, it's handled in Network.send
    p2.position = p2Pos
    
    # Update
    p.draw()
    p2.draw()
    pygame.display.flip()

    # Time/FPS control
    clock.tick(60)  # limits FPS to 60

pygame.quit()