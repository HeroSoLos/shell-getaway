import pygame

class Platform:
    
    """
    Init Platform
    
    Args:
        id: self explain
        x, y: location
        width, height: size of platform
        sprite: image of sprite
    """
    def __init__(self, id, x, y, width, height, sprite=None):
        self.id = id
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.sprite = sprite
        
        self.rect = pygame.Rect(x, y, width, height)
    
    """
    Checks collosion against player rect
    
    Args:
        player_rect (pygame.Rect): The rectangle of other player
    Precondition: The platform has a rectangle and the player has a rectangle.
    Postcondition: The platform has checked for collision with the player.    
    Return T/F
    """
    def collosion_check(self, player_rect):
        if self.rect.colliderect(player_rect):
            return True
        
    