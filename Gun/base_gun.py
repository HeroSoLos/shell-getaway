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
    """
    def __init__(self, magazine_size, x, y, sprite, damage=10):
        self.magazine_size = magazine_size
        self.sprite = sprite
        self.current_bullets = magazine_size 
        self.damage = damage
        self.x = x
        self.y = y
    
    
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
    Shoots a bullet in the specified direction.
    Args:
        direction (list): direction of bullet
    Precondition: The gun has bullets left.
    Postcondition: The gun has fired a bullet and decreased its current bullets.
    Returns: Bullet
    """
    def shoot(self, y, p2):
        if self.current_bullets <= 0:
            self.reload()
            return None
        self.current_bullets -= 1
        
        if p2.rect.collidepoint((p2.rect.x, y)):
            p2.health -= self.damage
        
        # print(f"Enemy Location: {p2.rect.center}")
        # print(f"Bullet Location: ({p2.position[0]}, {y})")
        # print(f"Player: {p2}")
        
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
         
        