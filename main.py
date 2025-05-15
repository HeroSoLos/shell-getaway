# Imports
import pygame

# pygame setup
pygame.init()
screen = pygame.display.set_mode((1280, 720))
clock = pygame.time.Clock()
running = True

# Game loop
while running:
    # Event handling
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    # fill the screen with a color to wipe away anything from last frame
    screen.fill("black")

    # Game Rendering

    # Update
    pygame.display.flip()

    # Time/FPS control
    clock.tick(60)  # limits FPS to 60

pygame.quit()