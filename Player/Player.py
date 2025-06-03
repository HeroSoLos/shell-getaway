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
    def __init__(self, health, move_speed, gun, screen, player, sprite=None):
        self.health = health
        self.move_speed = move_speed
        self.gun = gun
        self.screen = screen
        self.player = player
        self.sprite = sprite
        self.velocity = [0, 0]
        self.position = [0, 0]
        self.rect = pygame.Rect(0, 0, 50, 50)
    
    def __repr__(self):
        return f"Player(health={self.health}, move_speed={self.move_speed}, gun={self.gun}, sprite={self.sprite})"

    """
    Update velocity.
    Args:
        direction (list): Direction vector.
    Precondition: The player has a move speed.
    Postcondition: The player has updated its velocity.
    Returns: None
    """
    def update_velocity(self, direction):
        self.velocity[0] += direction[0] * self.move_speed
        self.velocity[1] += direction[1] * self.move_speed
        
    """
    Update position.
    Precondition: The player has a velocity.
    Postcondition: The player has updated its position.
    Returns: None
    """
    def update_position(self):
        self.position = (self.position[0]+self.velocity[0], self.position[1]+self.velocity[1])
        self.rect.x = self.position[0]
        self.rect.y = self.position[1]
        self.gun.update_pos(self.rect.x, self.rect.y)
    
    """
    Draw the player on the screen.
    Args:
        m_x (int): Mouse x-coordinate.
        m_y (int): Mouse y-coordinate.
    Precondition: The player has a sprite or a default shape.
    Postcondition: The player has been drawn on the screen.
    Returns: None
    """
    def draw(self, m_x, m_y):
        if self.sprite:
            image = pygame.image.load(self.sprite)
            image = pygame.transform.scale(image, (50, 50))
            self.screen.blit(image, (self.rect.x, self.rect.y))
            self.gun.draw(self.screen, m_x, m_y)
        else:
            pygame.draw.rect(self.screen, (255, 0, 0), (self.rect.x, self.rect.y, 50, 50))
            
        health_bar = pygame.Rect(self.rect.x, self.rect.y - 10, 50 * (self.health / 100), 5)
        pygame.draw.rect(self.screen, (0, 255, 0), health_bar)
            
    """
    Shoot a projectile towards the given target coordinates.
    Args:
        target_x (int): The x-coordinate of the target.
        target_y (int): The y-coordinate of the target.
    Precondition: The player has a gun.
    Postcondition: The gun may have fired a projectile.
    Returns: A dictionary with projectile details if shot, else None.
    """
    def shoot(self, target_x, target_y):
        if self.gun:
            return self.gun.shoot(target_x, target_y)
        return None



