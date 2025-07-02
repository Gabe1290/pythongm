# engine/game_object.py
import pygame
import math

KEY_MAP = {
    "LEFT": pygame.K_LEFT, "RIGHT": pygame.K_RIGHT, "UP": pygame.K_UP,
    "DOWN": pygame.K_DOWN, "SPACE": pygame.K_SPACE,
}

class GameObject:
    def __init__(self, object_data, sprite_path):
        self.x = 0
        self.y = 0
        self.x_speed = 0  # NEW: Speed components for movement
        self.y_speed = 0

        self.object_data = object_data
        self.is_solid = object_data.get("solid", False) # NEW: Read solid property

        try:
            self.sprite_image = pygame.image.load(sprite_path).convert_alpha()
        except pygame.error as e:
            print(f"Error loading sprite at {sprite_path}: {e}")
            self.sprite_image = pygame.Surface((32, 32))
            self.sprite_image.fill((255, 0, 255))

        # NEW: Create a hitbox (pygame.Rect) for collisions
        self.rect = self.sprite_image.get_rect()

    def set_position(self, x, y):
        self.x = x
        self.y = y
        self.rect.topleft = (self.x, self.y) # Update rect position

    def update(self, keys_pressed, all_instances): # NEW: Accepts all_instances
        # Reset speeds at the beginning of the frame
        self.x_speed = 0
        self.y_speed = 0

        if "step" in self.object_data.get("events", {}):
            step_actions = self.object_data["events"]["step"]
            self._execute_actions(step_actions, keys_pressed)

        # --- NEW: COLLISION HANDLING LOGIC ---
        # Move horizontally
        self.x += self.x_speed
        self.rect.x = int(self.x)
        collided_solids = self._check_collision(all_instances)
        for other in collided_solids:
            if self.x_speed > 0: # Moving right
                self.rect.right = other.rect.left
            elif self.x_speed < 0: # Moving left
                self.rect.left = other.rect.right
            self.x = self.rect.x # Update position based on collision

        # Move vertically
        self.y += self.y_speed
        self.rect.y = int(self.y)
        collided_solids = self._check_collision(all_instances)
        for other in collided_solids:
            if self.y_speed > 0: # Moving down
                self.rect.bottom = other.rect.top
            elif self.y_speed < 0: # Moving up
                self.rect.top = other.rect.bottom
            self.y = self.rect.y # Update position based on collision

    def _check_collision(self, all_instances):
        """Checks for collisions with any solid objects."""
        collided_with = []
        for other in all_instances:
            if other is self: # Don't collide with yourself
                continue
            if other.is_solid and self.rect.colliderect(other.rect):
                collided_with.append(other)
        return collided_with

    def _execute_actions(self, action_list, keys_pressed):
        for action_data in action_list:
            action_type = action_data.get("action")

            if action_type == "move_fixed":
                speed = action_data.get("speed", 0)
                direction = action_data.get("direction", 0)

                rad = math.radians(direction)
                # Instead of changing x/y, we change x_speed/y_speed
                self.x_speed += math.cos(rad) * speed
                self.y_speed -= math.sin(rad) * speed

            elif action_type == "check_keyboard":
                key_name = action_data.get("key")
                if key_name in KEY_MAP:
                    pygame_key = KEY_MAP[key_name]
                    if keys_pressed[pygame_key]:
                        result_list_name = action_data.get("result_action_list")
                        if result_list_name:
                            next_actions = self.object_data.get("action_lists", {}).get(result_list_name, [])
                            self._execute_actions(next_actions, keys_pressed)

    def draw(self, screen):
        self.rect.topleft = (int(self.x), int(self.y))
        screen.blit(self.sprite_image, self.rect)
