import math

class Projectile:
    """
    Init the projectile with stuff
    Args:
        id (int): self explanatory
        x, y: current location
        vx, vy: velocity vector to show future direction
        radius = size of ball for drawing
        owner_id: who shot the ball
        damage: damage of projectile
        projectile_type (str, optional): type of projectile, default 'standard_bullet'
    """
    def __init__(self, id, x, y, vx, vy, radius, owner_id, damage, projectile_type='standard_bullet'):
        self.id = id
        self.position = [x, y]
        self.velocity = [vx, vy]
        self.radius = radius
        self.owner_id = owner_id
        self.damage = damage
        self.projectile_type = projectile_type

    def update(self):
        self.position[0] += self.velocity[0]
        self.position[1] += self.velocity[1]

    def draw(screen, pygame, x, y, vx, vy, projectile_type, radius=2):
        if projectile_type == 'standard_bullet':
            if vx == 0 and vy == 0:
                pygame.draw.circle(screen, (0, 0, 0), (int(x), int(y)), radius)
            else:
                line_length = 5
                
                magnitude = math.sqrt(vx**2 + vy**2)
                
                if magnitude == 0:
                    pygame.draw.circle(screen, (0, 0, 0), (int(x), int(y)), radius)
                    return
                
                prev_x = x - (vx / magnitude) * line_length
                prev_y = y - (vy / magnitude) * line_length
                
                pygame.draw.line(screen, (0, 0, 0), (int(prev_x), int(prev_y)), (int(x), int(y)), 2)
        if projectile_type == "rocket":
            pygame.draw.circle(screen, (0, 0, 0), (int(x), int(y)), 20)