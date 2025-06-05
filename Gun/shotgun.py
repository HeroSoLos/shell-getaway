import pygame 
import math
from .base_gun import BaseGun

class Shotgun(BaseGun):
    def __init__(self, x, y, **kwargs):
        magazine_size = kwargs.pop('magazine_size', 2)
        damage = kwargs.pop('damage', 20)
        reload_time = kwargs.pop('reload_time', 70)
        shoot_cooldown = kwargs.pop('shoot_cooldown', 40)
        
        super().__init__(
            magazine_size=magazine_size,
            x=x,
            y=y,
            sprite=kwargs.pop('sprite', "assets/Shotgun.png"),
            reload_time=reload_time,
            shoot_cooldown=shoot_cooldown,
            damage=damage,
            projectile_type=kwargs.pop('projectile_type', 'standard_bullet'),
            weapon_type_id=kwargs.pop('weapon_type_id', 'shotgun'),
            **kwargs
        )

    def shoot(self, player, target_x, target_y, click_type):
        if self.current_bullets <= 0:
            if self.reload_counter >= self.reload_time:
                self.reload()
                self.reload_counter = 0
            return None

        if self.current_shoot_cooldown < self.shoot_cooldown:
             return None

        self.current_shoot_cooldown = 0 
        self.current_bullets -= 1
        
        projectiles_fired = []
        
        gun_nozzle_x = self.x + 25
        gun_nozzle_y = self.y + 25
        
        dx = target_x - gun_nozzle_x
        dy = target_y - gun_nozzle_y
        base_angle_rad = math.atan2(dy, dx)
        
        angle_variations_deg = [-12, -6, 0, 6, 12]
        projection_distance = 1000 

        for angle_offset_deg in angle_variations_deg:
            angle_offset_rad = math.radians(angle_offset_deg)
            current_angle_rad = base_angle_rad + angle_offset_rad
            
            variant_target_x = gun_nozzle_x + math.cos(current_angle_rad) * projection_distance
            variant_target_y = gun_nozzle_y + math.sin(current_angle_rad) * projection_distance
            
            projectile_info = {
                'gun_x': gun_nozzle_x,
                'gun_y': gun_nozzle_y,
                'target_x': variant_target_x,
                'target_y': variant_target_y,
                'projectile_type': self.projectile_type,
                'damage': self.damage
            }
            projectiles_fired.append(projectile_info)
            
        return projectiles_fired