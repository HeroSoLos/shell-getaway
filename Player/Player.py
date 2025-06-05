import pygame
import sys


class Player:
    """
    Init the player with health, move speed, gun and sprite
    
    Args:
        health (float): health,
        move_speed (float): move speed,
        primary_gun (BaseGun): primary gun,
        secondary_gun (BaseGun): secondary gun,
        sprite (str, optional): sprite, default None, is a path to the image
    """
    def __init__(self, health, move_speed, primary_gun, secondary_gun, screen, player, sprite=None):
        self.health = health
        self.move_speed = move_speed
        self.primary_gun = primary_gun
        self.secondary_gun = secondary_gun
        self.active_gun_slot = 0  # 0 for primary, 1 for secondary
        self.screen = screen
        self.player = player
        self.sprite = sprite
        self.velocity = [0, 0]
        self.position = [0, 0]
        self.rect = pygame.Rect(0, 0, 50, 50)
        self.kill_streak = 0
        
        self.loaded_sprite_image = None
        if sprite:
            try:
                raw_image = pygame.image.load(sprite)
                self.loaded_sprite_image = pygame.transform.scale(raw_image, (100, 100))
                print(f"DEBUG Player.__init__: Successfully loaded and scaled sprite: {sprite}", file=sys.stderr)
            except pygame.error as e:
                print(f"DEBUG Player.__init__: Failed to load sprite '{sprite}'. Error: {e}", file=sys.stderr)
                self.loaded_sprite_image = None
    
    """representation ykyk"""
    def __repr__(self):
        return f"Player(health={self.health}, move_speed={self.move_speed}, primary_gun={self.primary_gun}, secondary_gun={self.secondary_gun}, sprite={self.sprite})"

    """
    Getter for which gun they using rn
    
    Precondition: The player has an active gun slot.
    Postcondition: The player has returned the active gun based on the active gun slot.
    
    Returns: BaseGun: The active gun (primary or secondary) based on the active gun slot.
    """
    @property
    def gun(self):
        if self.active_gun_slot == 0:
            return self.primary_gun
        elif self.active_gun_slot == 1:
            return self.secondary_gun
        return None

    """
    Update velocity.
    Args:
        direction (list): Direction vector.
    Precondition: The player has a move speed.
    Postcondition: The player has updated its velocity.
    Returns: None
    """
    def update_velocity(self, direction):
        self.velocity[0] += direction[0] * self.move_speed
        self.velocity[1] += direction[1] * self.move_speed
        
        
    """Debug for health"""
    def restore_health(self):
        print(f"DEBUG Player.restore_health: Sending request to server.", file=sys.stderr)
        pass

    """
    Update position.
    Precondition: The player has a velocity.
    Postcondition: The player has updated its position.
    Returns: None
    """
    def update_position(self):
        self.position = [self.position[0]+self.velocity[0], self.position[1]+self.velocity[1]]
        self.rect.x = self.position[0]
        self.rect.y = self.position[1]
        self.gun.update_pos(self.rect.x, self.rect.y)
    
    """
    Draw the player on the screen.
    Args:
        m_x (int): Mouse x-coordinate.
        m_y (int): Mouse y-coordinate.
        camera_offset_x (int, optional): Camera x offset for scrolling
        camera_offset_y (int, optional): Camera y offset for scrolling
    Precondition: The player has a sprite or a default shape.
    Postcondition: The player has been drawn on the screen.
    Returns: None
    """
    def draw(self, m_x, m_y, camera_offset_x=0, camera_offset_y=0):
        m_x_screen = m_x - camera_offset_x
        m_y_screen = m_y - camera_offset_y

        if self.loaded_sprite_image:
            self.screen.blit(self.loaded_sprite_image, (self.rect.x - 25 - camera_offset_x, self.rect.y - 25 - camera_offset_y))
        else:
            pygame.draw.rect(self.screen, (255, 0, 0), (self.rect.x - camera_offset_x, self.rect.y - camera_offset_y, self.rect.width, self.rect.height))

        if self.gun:
            self.gun.update_pos(self.rect.x, self.rect.y)
            self.gun.draw(self.screen, m_x_screen, m_y_screen, camera_offset_x, camera_offset_y)
        
        if self.health > 0:
            health_bar_width = self.rect.width * (self.health / 100)
            health_bar_width = max(0, health_bar_width) 
            health_bar_height = 5
            health_bar_rect_screen = pygame.Rect(
                self.rect.x - camera_offset_x, 
                self.rect.y - 10 - camera_offset_y, 
                health_bar_width, 
                health_bar_height
            )
            pygame.draw.rect(self.screen, (0, 255, 0), health_bar_rect_screen)
            
    """
    Args:
        player (Player): The player object that is shooting.
        target_x (int): The x-coordinate of the target.
        target_y (int): The y-coordinate of the target.
        click_type (str): The type of click, either 'left_click' or 'right_click'.
    Precondition: The player has a gun.
    Postcondition: The gun may have fired a projectile.
    Returns: A dictionary with projectile details if shot, else None.
    """
    def shoot(self, player, target_x, target_y, click_type):
        if self.gun:
            return self.gun.shoot(player, target_x, target_y, click_type)
        return None

    """
    Switch the active weapon slot.
    Args:
        slot (int): The weapon slot to activate (0 for primary, 1 for secondary).
    Postcondition: The active weapon slot is updated, and the active gun is switched.
    Returns: str: The weapon_type_id of the newly active weapon, or "unknown_weapon" if slot is invalid or gun is missing.
    """
    def switch_weapon(self, slot):
        if slot == 0:
            self.active_gun_slot = 0
            if self.primary_gun and hasattr(self.primary_gun, 'weapon_type_id'):
                return self.primary_gun.weapon_type_id
            return "unknown_primary_gun_type"
        elif slot == 1:
            self.active_gun_slot = 1
            if self.secondary_gun and hasattr(self.secondary_gun, 'weapon_type_id'):
                return self.secondary_gun.weapon_type_id
            return "unknown_secondary_gun_type"
        
        print(f"Warning: Invalid weapon slot {slot} requested.", file=sys.stderr)
        if self.gun and hasattr(self.gun, 'weapon_type_id'):
            return self.gun.weapon_type_id
        return "unknown_weapon"