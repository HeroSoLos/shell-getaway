import pygame
import pygame.transform
import math

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
    def __init__(self, magazine_size, x, y, sprite, reload_time, shoot_cooldown, damage=10, projectile_type='standard_bullet'):
        self.magazine_size = magazine_size
        self.sprite = sprite
        self.current_bullets = magazine_size
        self.x = x
        self.y = y
        self.reload_time=reload_time
        self.shoot_cooldown=shoot_cooldown
        self.damage = damage
        self.projectile_type = projectile_type
        
        self.reload_counter = 0
        self.shoot_cooldown = 0
    
    
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
        self.reload_counter += 1
        self.shoot_cooldown += 1
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
        # reload
        if self.current_bullets <= 0:
            self.reload()
            self.reload_counter = 0
            return None
        
        if not (self.reload_counter <= self.reload_time) and not (self.shoot_cooldown <= self.shoot_cooldown):
            self.shoot_cooldown = 0
            self.current_bullets -= 1
            
            return {
                'gun_x': self.x+25,
                'gun_y': self.y+25,
                'target_x': target_x,
                'target_y': target_y,
                'projectile_type': self.projectile_type,
                'damage': self.damage
            }
    
    """
    Draw the gun on the screen.
    Args:
        screen (screen): screen to draw it on
        m_x (int): Mouse x-coordinate.
        m_y (int): Mouse y-coordinate.
    Precondition: The gun has a sprite or a default shape.
    Postcondition: The gun has been drawn on the screen.
    Returns: None
    """
    def draw(self, screen, m_x, m_y):
        if self.sprite:
            gun_pivot_x = self.x + 25
            gun_pivot_y = self.y + 25
            angle_rad = math.atan2(m_y - gun_pivot_y, m_x - gun_pivot_x)
            angle_deg = math.degrees(angle_rad)
            original_image = pygame.image.load(self.sprite)
            scaled_image = pygame.transform.scale(original_image, (50, 50))
            rotated_image = pygame.transform.rotate(scaled_image, -angle_deg)
            if m_x < self.x+25:
                new_rect = rotated_image.get_rect(center=(gun_pivot_x-15, gun_pivot_y))
            else:
                new_rect = rotated_image.get_rect(center=(gun_pivot_x+15, gun_pivot_y))
            screen.blit(rotated_image, new_rect.topleft)
        else:
            pygame.draw.rect(screen, (0, 255, 0), (self.x, self.rect.y, 50, 50))
         
        