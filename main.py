# Imports
import pygame
from Player.Player import *
from Gun.base_gun import *
from Physics import *

# pygame setup
pygame.init()
screen = pygame.display.set_mode((1280, 720))
clock = pygame.time.Clock()
running = True

# Object setup
Physics = Physics()
gun = BaseGun(magazine_size=10, bullet_speed=5)
player = Player(health=100, move_speed=5, gun=gun, screen=screen)


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
    if player.position[1] < 0:
        player.position[1] = 0
        player.velocity[1] = 0
    if player.position[1] > screen.get_height() - 50:
        player.position[1] = screen.get_height() - 50
        player.velocity[1] = 0
    
    # Update player position based on input
    keys = pygame.key.get_pressed()
    direction = [0, 0]
    if keys[pygame.K_LEFT]:
        direction[0] = -.1
    if keys[pygame.K_RIGHT]:
        direction[0] = .1
    if keys[pygame.K_UP]:
        direction[1] = -.1
    player.update_velocity(direction)

    
    
    
    Physics.applyGravity([player]) 
    player.update_position()
    player.draw()
    
    
    # Update
    pygame.display.flip()

    # Time/FPS control
    clock.tick(60)  # limits FPS to 60

pygame.quit()