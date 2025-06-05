from Gun.base_gun import BaseGun
import math

class Compressor(BaseGun):
    """
    used for velocity changing movement
    """
    """
    Init the gun with magazine size, speed, damage
    Args:
        magazine_size (int): self explanatory
        x (int): x position of the gun
        y (int): y position of the gun
        sprite (str): path to the gun sprite
        reload_time (int): time to reload the gun
        shoot_cooldown (int): time between shots
        projectile_speed (int): speed of the projectile, default 10
        damage (int, optional): damage, default 1
        projectile_type (str, optional): type of projectile, default 'standard_bullet'
        weapon_type_id (str, optional): specific identifier for the weapon type, default 'base_gun'
    """
    def __init__(self, magazine_size, x, y, sprite, reload_time, shoot_cooldown, damage=10, projectile_type='standard_bullet', weapon_type_id='compressor'):
        super().__init__(magazine_size, x, y, sprite, reload_time, shoot_cooldown, damage, projectile_type, weapon_type_id)

    """
    Shoots the gun
    Args:
        player (object): the player object that is shooting
        targetx (int): x coordinate of the target
        targety (int): y coordinate of the target
        click_type (str): type of click, either 'left_click' or 'right_click'
        
    Precondition: The player has a position and velocity.
    Postcondition: The player's velocity is updated based on direction and click type
    
    Returns: None
    """
    def shoot(self, player, targetx, targety, click_type):
        if click_type == "left_click":
            dx = targetx - player.rect.x
            dy = targety - player.rect.y
            
            magnitude = math.sqrt(dx*dx + dy*dy)
            
            if magnitude == 0:
                velx_change = 0
                vely_change = 0
            else:
                velx_change = (dx / magnitude) * 25
                vely_change = (dy / magnitude) * 25
            
            player.velocity[0] += velx_change
            player.velocity[1] += vely_change
        elif click_type == "right_click":
            player.velocity[0] = 0
            player.velocity[1] = 0