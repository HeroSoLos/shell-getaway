from Gun.base_gun import BaseGun
import math

class Compressor(BaseGun):
    """
    used for velocity changing movement
    """
    def __init__(self, magazine_size, x, y, sprite, reload_time, shoot_cooldown, damage=10, projectile_type='standard_bullet', weapon_type_id='compressor'): # Added weapon_type_id
        super().__init__(magazine_size, x, y, sprite, reload_time, shoot_cooldown, damage, projectile_type, weapon_type_id) # Passed to super

    def shoot(self, player, targetx, targety):
        dx = targetx - player.rect.x
        dy = targety - player.rect.y
        
        magnitude = math.sqrt(dx*dx + dy*dy)
        
        if magnitude == 0:
            velx_change = 0
            vely_change = 0
        else:
            velx_change = (dx / magnitude) * 1
            vely_change = (dy / magnitude) * 1
        
        player.velocity[0] += velx_change
        player.velocity[1] += vely_change
        