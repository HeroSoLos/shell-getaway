import math

class Projectile:
    def __init__(self, id, x, y, vx, vy, radius, owner_id, projectile_type='standard_bullet'):
        self.id = id
        self.position = [x, y]
        self.velocity = [vx, vy]
        self.radius = radius
        self.owner_id = owner_id
        self.projectile_type = projectile_type

    def update(self):
        self.position[0] += self.velocity[0]
        self.position[1] += self.velocity[1]

    @staticmethod
    def draw(screen, pygame, x, y, vx, vy, projectile_type, radius=2): # Added radius for circle case
        if projectile_type == 'standard_bullet':
            if vx == 0 and vy == 0:
                pygame.draw.circle(screen, (0, 0, 0), (int(x), int(y)), radius) # Use passed radius
            else:
                # Draw a line from current pos (x,y) to a point slightly behind it based on velocity
                # Scale factor for "tail" length, adjust as needed. 0.1 * speed might be too small.
                # Let's use a fixed length for the tail for consistency.
                line_length = 5 # pixels
                
                magnitude = math.sqrt(vx**2 + vy**2)
                
                if magnitude == 0: # Should be caught by vx == 0 and vy == 0, but defensive
                    pygame.draw.circle(screen, (0, 0, 0), (int(x), int(y)), radius)
                    return

                # Calculate the "previous" point or tail end of the line
                # Line extends from (x,y) backwards along velocity vector
                prev_x = x - (vx / magnitude) * line_length
                prev_y = y - (vy / magnitude) * line_length
                
                pygame.draw.line(screen, (0, 0, 0), (int(prev_x), int(prev_y)), (int(x), int(y)), 2) # Black line, 2px thick
        
        # Example for another projectile type
        # elif projectile_type == 'laser_dot':
        #     pygame.draw.circle(screen, (255, 0, 0), (int(x), int(y)), 3) # Small red dot
        
        # Add other projectile types drawing logic here if needed
        # For example:
        # elif self.projectile_type == 'laser_beam':
        #     pygame.draw.line(screen, (255, 0, 0), (self.position[0] - self.velocity[0]*10, self.position[1] - self.velocity[1]*10), (self.position[0], self.position[1]), 3)
