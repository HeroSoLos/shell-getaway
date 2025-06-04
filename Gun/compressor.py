from Gun.base_gun import BaseGun
import math

class Compressor(BaseGun):
    """
    used for velocity changing movement
    """
    def __init__(self, magazine_size, x, y, sprite, reload_time, shoot_cooldown, damage=10, projectile_type='standard_bullet'):
        super().__init__(magazine_size, x, y, sprite, reload_time, shoot_cooldown, damage, projectile_type)

    def shoot(self, player, targetx, targety):
        dx = targetx - player.rect.x
        dy = targety - player.rect.y
        
        velx_change = dx/(math.sqrt(dx*dx+dy*dy)) * 25
        vely_change = dx/(math.sqrt(dx*dx+dy*dy)) * 25
        
        player.velocity[0] += velx_change
        player.velocity[1] += vely_change
        