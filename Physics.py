import math

class Physics:
    def __init__(self):
        self.gravity = 9.81
        self.friction_coefficient = 1
        self.velocity_threshold = 0.01
    
    """
    Apply friction to objects.
    Args:
        obj_list (list): List of objects to apply friction to.
        delta_time (float): Time step for friction calculation.
    Precondition: Objects have a velocity attribute.
    Postcondition: Objects' velocities are reduced by friction.
    Returns: None
    """
    def applyFriction(self, player, delta_time=0.016):
        if hasattr(player, 'velocity'):
            if player.velocity[0] > 0:
                player.velocity[0] -= self.friction_coefficient * delta_time
                if player.velocity[0] < 0:
                    player.velocity[0] = 0
            elif player.velocity[0] < 0:
                player.velocity[0] += self.friction_coefficient * delta_time
                if player.velocity[0] > 0:
                    player.velocity[0] = 0
                    
            if player.velocity[1] > 0:
                player.velocity[1] -= self.friction_coefficient * delta_time
                if player.velocity[1] < 0:
                    player.velocity[1] = 0
            elif player.velocity[1] < 0:
                player.velocity[1] += self.friction_coefficient * delta_time
                if player.velocity[1] > 0:
                    player.velocity[1] = 0

            if abs(player.velocity[0]) < self.velocity_threshold:
                player.velocity[0] = 0
            if abs(player.velocity[1]) < self.velocity_threshold:
                player.velocity[1] = 0

    """
    Apply gravity to objects.
    Args:
        obj_list (list): List of objects to apply gravity to.
    Precondition: Objects have a velocity attribute.
    Postcondition: Objects' velocities are updated due to gravity.
    Returns: None
    """
    def applyGravity(self, obj_list):
        for obj in obj_list:
            if hasattr(obj, 'velocity'):
                obj.velocity[1] += self.gravity * 0.016
                
    """
    Caps velocity
    Args:
        p: player to cap velocity
    precondition: there is a player with velocity
    postcondition: velocity doesn't exceed limit
    returns: none
    """
    def capVelocity(self, p):
        cap = 50
        if hasattr(p, 'velocity'):
            if p.velocity[0] < -cap:
                p.velocity[0] = -cap
            elif p.velocity[0] > cap:
                p.velocity[0] = cap
            
            if p.velocity[1] < -cap:
                p.velocity[1] = -cap
            elif p.velocity[1] > cap:
                p.velocity[1] = cap
            