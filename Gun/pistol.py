import pygame 
import math
from .base_gun import BaseGun

"""Pistol Class"""
class Pistol(BaseGun):
    """
    Init the gun with magazine size, speed, damage
    Args:
        magazine_size (int): self explanatory
        x (int): x position of the gun
        y (int): y position of the gun
        **kwargs, everything else from main/ will be included in BaseGun
    """
    def __init__(self, x, y, **kwargs):
        magazine_size = kwargs.pop('magazine_size', 10)
        damage = kwargs.pop('damage', 5)
        reload_time = kwargs.pop('reload_time', 50)
        shoot_cooldown = kwargs.pop('shoot_cooldown', 10)
        projectile_speed = 10
        
        super().__init__(
            magazine_size=magazine_size,
            x=x,
            y=y,
            sprite=kwargs.pop('sprite', "assets/Pistol.png"),
            reload_time=reload_time,
            shoot_cooldown=shoot_cooldown,
            damage=damage,
            projectile_speed=projectile_speed,
            projectile_type=kwargs.pop('projectile_type', 'standard_bullet'),
            weapon_type_id=kwargs.pop('weapon_type_id', 'pistol'),
            **kwargs
        )
        