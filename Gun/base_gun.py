class Bullet:
    """
    Self explanatory
    """
    
    """
    Init the bullet with movement type, speed, and direction.
    Args:
        movement_type (str): hitscan or projectile or homing, etc.
        speed (float): self explanatory
        direction (list): vector showing dir
    """
    def __init__(self, movement_type, speed, direction):
        self.movement_type = movement_type
        self.speed = speed
        self.direction = direction

    """
    like a toString
    Returns: string representation of the bullet
    """
    def __repr__(self):
        return f"Bullet(speed={self.speed}, direction={self.direction})"

    """
    Move the bullet
    
    Precondition: The bullet has a speed and direction.
    Postcondition: The bullet has moved in the direction of its speed.
    Returns: None   
    """
    def move(self):
        # Implement movement logic here tomorrow - andrew
        pass
    
    
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
    def __init__(self, magazine_size, bullet_speed, damage=1):
        self.magazine_size = magazine_size
        self.bullet_speed = bullet_speed
        self.current_bullets = magazine_size 
        self.damage = damage

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
    def shoot(self, direction) -> Bullet:
        if self.current_bullets <= 0:
            self.reload()
            return None
        self.current_bullets -= 1
        bullet = Bullet(self.bullet_speed, direction)
        return bullet