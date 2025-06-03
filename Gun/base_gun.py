import pygame
import pygame.transform

class BaseGun:
    """
    base gun, no specialities
    """
    
    """
    Init the gun with magazine size, speed, damage
    Args:
        magazine_size (int): self explanatory
        bullet_speed (float): used to send bullet speed
        damage (int, optional): damage, default 1
        projectile_type (str, optional): type of projectile, default 'standard_bullet'
    """
    def __init__(self, magazine_size, x, y, sprite, damage=10, projectile_type='standard_bullet'):
        self.magazine_size = magazine_size
        self.sprite = sprite
        self.current_bullets = magazine_size
        self.damage = damage
        self.x = x
        self.y = y
        self.projectile_type = projectile_type
    
    
    """
    Update the position of the gun.
    Args:
        x (int): x position
        y (int): y position
    Precondition: The gun has a position.
    Postcondition: The gun has updated its position.
    Returns: None
    """
    def update_pos(self, x, y):

        self.x = x
        self.y = y

    """
    Reloads
    Precondition: The gun has a magazine size and current bullets.
    Postcondition: The gun has reloaded its magazine.
    Returns: None
    """
    def reload(self):
        self.current_bullets = self.magazine_size
        print("Gun reloaded.")

    """
    Shoots a projectile towards the target coordinates.
    Args:
        target_x (int): The x-coordinate of the target.
        target_y (int): The y-coordinate of the target.
    Precondition: The gun may or may not have bullets left.
    Postcondition: If bullets are available, current bullets are decremented.
    Returns: A dictionary containing projectile information if a shot is fired, otherwise None.
    """
    def shoot(self, target_x, target_y):
        if self.current_bullets <= 0:
            self.reload()
            return None
        
        self.current_bullets -= 1
        
        return {
            'gun_x': self.x+25,
            'gun_y': self.y+25,
            'target_x': target_x,
            'target_y': target_y,
            'projectile_type': self.projectile_type,
            'damage': self.damage
        }
        
    def draw(self, screen, m_x, m_y):
        if self.sprite:
            if m_x > self.x:
                image = pygame.image.load(self.sprite)
                image = pygame.transform.scale(image, (25, 25))
                screen.blit(image, (self.x+20, self.y+10))
            else:
                image = pygame.image.load(self.sprite)
                image = pygame.transform.scale(image, (25, 25))
                image = pygame.transform.flip(image, True, False)
                screen.blit(image, (self.x, self.y+10))
        else:
            pygame.draw.rect(screen, (0, 255, 0), (self.x, self.rect.y, 25, 25))
         
        