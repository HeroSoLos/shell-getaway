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
gun = BaseGun(magazine_size=10, x=0, y=0, bullet_speed=5)
startPos = tuple(read_pos(n.getPos()))
p = Player(health=100, move_speed=5, gun=gun, screen=screen, player=None, sprite="assets/Egg_sprite.png")
p.position = startPos
p2 = Player(health=100, move_speed=5, gun=gun, screen=screen, player=None, sprite="assets/Egg_sprite.png")
p2.position = (0, 0)
p.player = p2

# Game loop
while running:
    # Event handling
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:
                m_x, m_y = pygame.mouse.get_pos()
                p.shoot(m_y, p2)

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
    p.update_velocity(direction)
    
    
    Physics.applyGravity([p])
    p.update_position()
    
    
    # Send player position to server
    p2data = list(p.position)
    p2data.append(p2.health)
    p2Pos = n.send(p2data)
    p2.rect.x = p2Pos[0]
    p2.rect.y = p2Pos[1]
    p.health = p2Pos[2]
    
    # Update
    if p.health > 0:
        p.draw()
    if p2.health > 0:
        p2.draw()
    pygame.display.flip()

    # Time/FPS control
    clock.tick(60)  # limits FPS to 60

pygame.quit()