class Physics:
    def __init__(self):
        self.gravity = 9.81  # m/s^2
        self.air_density = 1.225  # kg/m^3
        self.drag_coefficient = 0.47  # dimensionless
        self.cross_sectional_area = 0.01  # m^2
    
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