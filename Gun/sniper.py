import pygame 
import math
from .base_gun import BaseGun

class Sniper(BaseGun):
    def __init__(self, x, y, **kwargs):
        magazine_size = kwargs.pop('magazine_size', 3)
        damage = kwargs.pop('damage', 75)
        reload_time = kwargs.pop('reload_time', 200)
        shoot_cooldown = kwargs.pop('shoot_cooldown', 50)
        self.projectile_speed = 20
        
        super().__init__(
            magazine_size=magazine_size,
            x=x,
            y=y,
            sprite=kwargs.pop('sprite', "assets/Sniper.png"),
            reload_time=reload_time,
            shoot_cooldown=shoot_cooldown,
            damage=damage,
            projectile_speed=20,
            projectile_type=kwargs.pop('projectile_type', 'standard_bullet'),
            weapon_type_id=kwargs.pop('weapon_type_id', 'sniper'),
            **kwargs
        )
        