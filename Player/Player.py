import pygame

class Player:
    
    """
    Init the player with health, move speed, gun and sprite
    
    Args:
        health (float): health,
        move_speed (float): move speed,
        gun (BaseGun): gun,
        sprite (str, optional): sprite, default None, is a path to the image
    """
    def __init__(self, health, move_speed, gun, screen, sprite=None):
        self.health = health
        self.move_speed = move_speed
        self.gun = gun
        self.screen = screen
        self.sprite = sprite
        self.velocity = [0, 0]
        self.position = [0, 0]
        
    def __repr__(self):
        return f"Player(health={self.health}, move_speed={self.move_speed}, gun={self.gun}, sprite={self.sprite})"

    """
    Update velocity
    
    Precondition: The player has a move speed.
    Postcondition: The player has updated its velocity.
    Returns: None
    """
    def update_velocity(self, direction):
        self.velocity[0] += direction[0] * self.move_speed
        self.velocity[1] += direction[1] * self.move_speed
        
    """
    update position
    
    Precondition: The player has a velocity.
    Postcondition: The player has updated its position.
    Returns: None
    """
    def update_position(self):
        self.position[0] += self.velocity[0]
        self.position[1] += self.velocity[1]
    
    """
    Draw the player on the screen
    Precondition: The player has a sprite or a default shape.
    Postcondition: The player has been drawn on the screen.
    Returns: None
    """
    def draw(self):
        if self.sprite:
            image = pygame.image.load(self.sprite)
            self.screen.blit(image, (self.position[0], self.position[1]))
        else:
            pygame.draw.rect(self.screen, (255, 0, 0), (self.position[0], self.position[1], 50, 50))
        
    
        