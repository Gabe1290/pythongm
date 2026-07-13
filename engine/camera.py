# engine/camera.py
import pygame

class Camera:
    def __init__(self, screen_width, screen_height):
        self.screen_width = screen_width
        self.screen_height = screen_height
        
        # The camera's rect represents its top-left corner's position within the game world.
        self.rect = pygame.Rect(0, 0, screen_width, screen_height)
        
        self.target = None
        self.world_width = 0
        self.world_height = 0

    def set_world_size(self, width, height):
        """
        Sets the boundaries of the entire world/room. The camera will not scroll beyond these limits.
        """
        self.world_width = width
        self.world_height = height

    def follow(self, target_rect):
        """
        Sets the target (usually a player's rect) for the camera to follow.
        """
        self.target = target_rect

    def update(self):
        """
        Updates the camera's position based on its target, clamping it to the world boundaries.
        This should be called once per frame, after the target has moved.
        """
        if self.target:
            # First, center the camera on the target's center.
            # This gives us the "ideal" top-left position for the camera.
            x = self.target.centerx - (self.screen_width // 2)
            y = self.target.centery - (self.screen_height // 2)

            # Clamp the camera's x-coordinate to the world boundaries.
            # It cannot go further left than 0.
            # It cannot go further right than the point where the camera's right edge meets the world's right edge.
            self.rect.x = max(0, min(x, self.world_width - self.screen_width))

            # Clamp the camera's y-coordinate to the world boundaries.
            # It cannot go further up than 0.
            # It cannot go further down than the point where the camera's bottom edge meets the world's bottom edge.
            self.rect.y = max(0, min(y, self.world_height - self.screen_height))
    
    def apply_offset(self, entity_rect):
        """
        Applies the camera's offset to a pygame.Rect object.
        This is used for drawing instances (which have a .rect attribute).
        It calculates the object's position on the screen.
        """
        return entity_rect.move(-self.rect.x, -self.rect.y)
    
    def apply_offset_to_pos(self, pos):
        """
        Applies the camera's offset to a simple (x, y) tuple.
        This is used for drawing tiles, which don't have their own Rect object.
        """
        return (pos[0] - self.rect.x, pos[1] - self.rect.y)