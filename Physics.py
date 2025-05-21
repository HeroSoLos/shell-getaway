import math

class Physics:
    def __init__(self):
        self.gravity = 9.81  # m/s^2
        self.friction_coefficient = 0.6  # Arbitrary value to control friction strength
        self.velocity_threshold = 0.01  # Minimum velocity before setting it to 0
    
    def applyFriction(self, obj_list, delta_time=0.016):
        for obj in obj_list:
            if hasattr(obj, 'velocity'):
                if obj.velocity[0] > 0:
                    obj.velocity[0] -= self.friction_coefficient * delta_time
                    if obj.velocity[0] < 0:
                        obj.velocity[0] = 0
                elif obj.velocity[0] < 0:
                    obj.velocity[0] += self.friction_coefficient * delta_time
                    if obj.velocity[0] > 0:
                        obj.velocity[0] = 0

                if abs(obj.velocity[0]) < self.velocity_threshold:
                    obj.velocity[0] = 0
                if abs(obj.velocity[1]) < self.velocity_threshold:
                    obj.velocity[1] = 0

    """
    Gives gravity
    Args:
        obj_list (list): list of objects to apply gravity to
        
    Precondition: The object has a velocity.
    Postcondition: The object has updated its velocity due to gravity.
    Returns: None
    
    """
    def applyGravity(self, obj_list):
        for obj in obj_list:
            if hasattr(obj, 'velocity'):
                obj.velocity[1] += self.gravity * 0.016  # Assuming 60 FPS, so delta time is 1/60 seconds