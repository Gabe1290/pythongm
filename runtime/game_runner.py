#!/usr/bin/env python3
"""
Enhanced GameRunner that properly renders room objects
"""

import pygame
import json
import sys
from pathlib import Path
from typing import Dict, List, Optional, Tuple

from runtime.action_executor import ActionExecutor

class GameSprite:
    """Represents a loaded sprite"""
    
    def __init__(self, image_path: str):
        self.path = image_path
        self.surface = None
        self.width = 32
        self.height = 32
        self.load_image()

        # Add movement properties
        self.speed = 0.0
        self.direction = 0.0

        # Grid movement animation
        self.target_x = None
        self.target_y = None
        self.grid_move_speed = 4  # Pixels per frame for grid movement
    
    def load_image(self):
        """Load the sprite image"""
        try:
            if Path(self.path).exists():
                self.surface = pygame.image.load(self.path).convert_alpha()
                self.width = self.surface.get_width()
                self.height = self.surface.get_height()
            else:
                print(f"Sprite not found: {self.path}")
                self.create_default_sprite()
        except Exception as e:
            print(f"Error loading sprite {self.path}: {e}")
            self.create_default_sprite()
    
    def create_default_sprite(self):
        """Create a default sprite (colored rectangle)"""
        self.surface = pygame.Surface((32, 32))
        self.surface.fill((255, 100, 100))  # Red rectangle
        pygame.draw.rect(self.surface, (0, 0, 0), (0, 0, 32, 32), 2)
        self.width = 32
        self.height = 32

class GameInstance:
    """Represents an object instance in the game world"""
    
    def __init__(self, object_name: str, x: float, y: float, instance_data: dict):
        self.object_name = object_name
        self.x = float(x)
        self.y = float(y)
        self.instance_id = instance_data.get('instance_id', id(self))
        self.visible = instance_data.get('visible', True)
        self.rotation = instance_data.get('rotation', 0)
        self.scale_x = instance_data.get('scale_x', 1.0)
        self.scale_y = instance_data.get('scale_y', 1.0)
        
        # Movement properties - dual system (polar + cartesian)
        self.speed = 0.0       # Magnitude (polar)
        self.direction = 0.0   # Angle in degrees (polar)
        self.hspeed = 0.0      # Horizontal velocity (cartesian)
        self.vspeed = 0.0      # Vertical velocity (cartesian)

        # Grid movement animation
        self.target_x = None
        self.target_y = None
        self.grid_move_speed = 8

        # Add collision and destruction properties
        self.to_destroy = False
        self.collision_width = 32
        self.collision_height = 32

        self.sprite = None
        self.object_data = None

        # Action executor
        self.action_executor = ActionExecutor()
        self.alarms = {}  # {alarm_id: {'frames': N, 'action': action_data}}
    
    def step(self):
        """Execute step event every frame"""
        # Process alarms FIRST
        if hasattr(self, 'alarms'):
            finished_alarms = []
            for alarm_id, alarm_data in self.alarms.items():
                alarm_data['frames'] -= 1
                if alarm_data['frames'] <= 0:
                    # Alarm finished - execute the action
                    if alarm_data.get('action'):
                        self.action_executor.execute_action(self, alarm_data['action'])
                    finished_alarms.append(alarm_id)
            
            # Remove finished alarms
            for alarm_id in finished_alarms:
                del self.alarms[alarm_id]

        # Initialize grid movement attributes if they don't exist
        if not hasattr(self, 'target_x'):
            self.target_x = None
            self.target_y = None
            self.grid_move_speed = 8
        
        # Grid movement animation - ATOMIC completion
        if self.target_x is not None and self.target_y is not None:
            dx = self.target_x - self.x
            dy = self.target_y - self.y
            distance = (dx**2 + dy**2) ** 0.5
            
            if distance < self.grid_move_speed:
                # Snap to EXACT position (maintain grid alignment)
                self.x = self.target_x
                self.y = self.target_y
                self.target_x = None
                self.target_y = None
            else:
                # Move toward target
                move_x = (dx / distance) * self.grid_move_speed
                move_y = (dy / distance) * self.grid_move_speed
                self.x += move_x
                self.y += move_y
        
        # Apply cartesian velocity (hspeed/vspeed)
        if self.hspeed != 0 or self.vspeed != 0:
            self.x += self.hspeed
            self.y += self.vspeed
        
        # Apply polar velocity (speed/direction) if no cartesian velocity
        elif self.speed > 0:
            import math
            direction_rad = math.radians(self.direction)
            dx = math.cos(direction_rad) * self.speed
            dy = -math.sin(direction_rad) * self.speed
            
            self.x += dx
            self.y += dy
        
        # Execute Step events
        if self.object_data and "events" in self.object_data:
            self.action_executor.execute_event(self, "step", self.object_data["events"])

    def set_sprite(self, sprite: GameSprite):
        """Set the sprite for this instance"""
        self.sprite = sprite
    
    def set_object_data(self, object_data: dict):
        """Set the object data from project"""
        self.object_data = object_data

        # NOW execute Create event - object_data is available!
        if self.object_data and "events" in self.object_data:
            self.action_executor.execute_event(self, "create", self.object_data["events"])
            print(f"Executed Create event for {self.object_name}")
    
    def render(self, screen: pygame.Surface):
        """Render this instance with rotation and scaling"""
        if not self.visible or not self.sprite:
            return
        
        # Start with original sprite
        surface = self.sprite.surface
        
        # Apply transformations
        needs_transform = (self.scale_x != 1.0 or self.scale_y != 1.0 or self.rotation != 0)
        
        if needs_transform:
            # Apply scaling first
            if self.scale_x != 1.0 or self.scale_y != 1.0:
                scaled_width = int(self.sprite.width * self.scale_x)
                scaled_height = int(self.sprite.height * self.scale_y)
                surface = pygame.transform.scale(surface, (scaled_width, scaled_height))
            
            # Apply rotation
            if self.rotation != 0:
                surface = pygame.transform.rotate(surface, self.rotation)
            
            # Calculate centered position (rotation changes surface size)
            offset_x = (surface.get_width() - self.sprite.width * self.scale_x) / 2
            offset_y = (surface.get_height() - self.sprite.height * self.scale_y) / 2
            render_x = int(self.x - offset_x)
            render_y = int(self.y - offset_y)
        else:
            # No transformation - render normally
            render_x = int(self.x)
            render_y = int(self.y)
        
        screen.blit(surface, (render_x, render_y))
    
    def get_collision_rect(self):
        """Get collision rectangle for this instance"""
        # Center the collision box and make it smaller than the sprite
        collision_size = 28  # Slightly smaller than 32px sprite
        return {
            'x': self.x + (32 - collision_size) // 2,  # Center horizontally
            'y': self.y + (32 - collision_size) // 2,  # Center vertically  
            'width': collision_size,
            'height': collision_size
        }

    def check_collision(self, other):
        """Check if this instance collides with another - more precise"""
        rect1 = self.get_collision_rect()
        rect2 = other.get_collision_rect()
        
        # Add small buffer to prevent collision detection when objects are just touching
        buffer = 1
        return (rect1['x'] < rect2['x'] + rect2['width'] - buffer and
                rect1['x'] + rect1['width'] - buffer > rect2['x'] and
                rect1['y'] < rect2['y'] + rect2['height'] - buffer and
                rect1['y'] + rect1['height'] - buffer > rect2['y'])

class GameRoom:
    """Represents a game room with instances"""
    
    def __init__(self, name: str, room_data: dict):
        self.name = name
        self.width = room_data.get('width', 1024)
        self.height = room_data.get('height', 768)
        self.background_color = self.parse_color(room_data.get('background_color', '#87CEEB'))

        self.background_image = room_data.get('background_image', '')
        self.tile_horizontal = room_data.get('tile_horizontal', False)
        self.tile_vertical = room_data.get('tile_vertical', False)

        self.instances: List[GameInstance] = []
        
        # Load instances
        instances_data = room_data.get('instances', [])
        for instance_data in instances_data:
            instance = GameInstance(
                instance_data['object_name'],
                instance_data['x'],
                instance_data['y'],
                instance_data
            )
            self.instances.append(instance)
    
    def parse_color(self, color_str: str) -> Tuple[int, int, int]:
        """Parse color string to RGB tuple"""
        if color_str.startswith('#'):
            color_str = color_str[1:]
        
        try:
            r = int(color_str[0:2], 16)
            g = int(color_str[2:4], 16)
            b = int(color_str[4:6], 16)
            return (r, g, b)
        except:
            return (135, 206, 235)  # Default sky blue
    
    def set_sprites_for_instances(self, sprites: Dict[str, GameSprite], objects: Dict[str, dict]):
        """Set sprites for all instances based on their object types"""
        for instance in self.instances:
            # Get object data
            if instance.object_name in objects:
                object_data = objects[instance.object_name]
                instance.set_object_data(object_data)
                
                # Get sprite name from object
                sprite_name = object_data.get('sprite', '')
                if sprite_name and sprite_name in sprites:
                    instance.set_sprite(sprites[sprite_name])
                else:
                    # Create a default sprite for objects without sprites
                    default_sprite = self.create_default_sprite_for_object(instance.object_name)
                    instance.set_sprite(default_sprite)
    
    def create_default_sprite_for_object(self, object_name: str) -> GameSprite:
        """Create a default sprite for an object"""
        # Create a colored rectangle based on object name
        colors = {
            'player': (0, 255, 0),      # Green
            'enemy': (255, 0, 0),       # Red  
            'wall': (128, 128, 128),    # Gray
            'coin': (255, 255, 0),      # Yellow
            'door': (139, 69, 19),      # Brown
            'key': (255, 215, 0),       # Gold
        }
        
        # Get color or use hash-based color
        if object_name in colors:
            color = colors[object_name]
        else:
            # Generate color from name hash
            hash_val = hash(object_name)
            color = (
                (hash_val % 128) + 127,
                ((hash_val >> 8) % 128) + 127,
                ((hash_val >> 16) % 128) + 127
            )
        
        # Create sprite surface
        surface = pygame.Surface((32, 32))
        surface.fill(color)
        pygame.draw.rect(surface, (0, 0, 0), (0, 0, 32, 32), 2)  # Black border
        
        # Create sprite object
        sprite = GameSprite("")  # Empty path since we're creating manually
        sprite.surface = surface
        sprite.width = 32
        sprite.height = 32
        
        return sprite
    
    def load_background_image(self, project_path: Path, sprites: Dict[str, GameSprite]) -> Optional[pygame.Surface]:
        """Load background image from project"""
        if not self.background_image:
            return None
        
        try:
            # Check if it's in sprites or backgrounds
            if self.background_image in sprites:
                return sprites[self.background_image].surface
            
            # Try loading from backgrounds folder
            bg_path = project_path / 'backgrounds' / f'{self.background_image}.png'
            if bg_path.exists():
                return pygame.image.load(str(bg_path)).convert_alpha()
            
            # Try loading from sprites folder as fallback
            sprite_path = project_path / 'sprites' / f'{self.background_image}.png'
            if sprite_path.exists():
                return pygame.image.load(str(sprite_path)).convert_alpha()
            
            print(f"Background image not found: {self.background_image}")
            return None
            
        except Exception as e:
            print(f"Error loading background image {self.background_image}: {e}")
            return None

    def render(self, screen: pygame.Surface):
        """Render the room and all its instances"""
        # Clear screen with background color first
        screen.fill(self.background_color)
        
        # Draw background image if available
        if hasattr(self, 'background_surface') and self.background_surface:
            if self.tile_horizontal or self.tile_vertical:
                # Tiled rendering
                img_width = self.background_surface.get_width()
                img_height = self.background_surface.get_height()
                
                x_count = (self.width // img_width) + 2 if self.tile_horizontal else 1
                y_count = (self.height // img_height) + 2 if self.tile_vertical else 1
                
                for x_tile in range(x_count):
                    for y_tile in range(y_count):
                        x_pos = x_tile * img_width if self.tile_horizontal else 0
                        y_pos = y_tile * img_height if self.tile_vertical else 0
                        
                        if x_pos < self.width and y_pos < self.height:
                            screen.blit(self.background_surface, (x_pos, y_pos))
            else:
                # Stretched to fit room
                scaled_bg = pygame.transform.scale(self.background_surface, (self.width, self.height))
                screen.blit(scaled_bg, (0, 0))
        
        # Remove destroyed instances
        self.instances = [instance for instance in self.instances if not instance.to_destroy]
        
        # Render all instances
        for instance in self.instances:
            instance.render(screen)

class GameRunner:
    """Enhanced game runner that properly renders rooms with objects"""
    
    def __init__(self):
        self.running = False
        self.screen = None
        self.clock = None
        self.project_data = None
        self.project_path = None
        
        # Game assets
        self.sprites: Dict[str, GameSprite] = {}
        self.rooms: Dict[str, GameRoom] = {}
        self.current_room = None
        
        # Game settings
        self.fps = 60
        self.window_width = 800
        self.window_height = 600
    
    def is_game_running(self):
        """Check if game is currently running"""
        return self.running
    
    def load_project_data_only(self, project_path: str) -> bool:
        """Load project data without loading sprites (sprites loaded later)"""
        try:
            from collections import OrderedDict
            
            self.project_path = Path(project_path)
            project_file = self.project_path / "project.json"
            
            if not project_file.exists():
                print(f"Project file not found: {project_file}")
                return False
            
            # Load project data with order preservation
            with open(project_file, 'r') as f:
                self.project_data = json.load(f, object_pairs_hook=OrderedDict)
            
            print(f"Loaded project: {self.project_data.get('name', 'Untitled')}")
            
            # Only load rooms (without sprites for instances yet)
            self.load_rooms_without_sprites()
            
            return True
            
        except Exception as e:
            print(f"Error loading project: {e}")
            import traceback
            traceback.print_exc()
            return False
    
    def load_sprites(self):
        """Load all sprites from the project (called after pygame.display is initialized)"""
        sprites_data = self.project_data.get('assets', {}).get('sprites', {})
        
        print(f"Loading {len(sprites_data)} sprites...")
        
        for sprite_name, sprite_info in sprites_data.items():
            try:
                file_path = sprite_info.get('file_path', '')
                if file_path:
                    full_path = self.project_path / file_path
                    sprite = GameSprite(str(full_path))
                    self.sprites[sprite_name] = sprite
                    print(f"  Loaded sprite: {sprite_name} ({sprite.width}x{sprite.height})")
                else:
                    print(f"  Sprite {sprite_name} has no file path")
            except Exception as e:
                print(f"  Error loading sprite {sprite_name}: {e}")
    
    def load_rooms_without_sprites(self):
        """Load rooms but don't assign sprites to instances yet - RESPECTS ORDER"""
        from collections import OrderedDict
        
        rooms_data = self.project_data.get('assets', {}).get('rooms', {})
        
        print(f"Loading {len(rooms_data)} rooms in order...")
        print(f"Room order: {list(rooms_data.keys())}")
        
        # Use OrderedDict to preserve room order
        self.rooms = OrderedDict()
        
        # Important: Maintain the order from the dictionary
        for room_name, room_info in rooms_data.items():
            try:
                room = GameRoom(room_name, room_info)
                # Don't set sprites yet - will do this after pygame.display is ready
                self.rooms[room_name] = room
                print(f"  Loaded room: {room_name} ({len(room.instances)} instances)")
            except Exception as e:
                print(f"  Error loading room {room_name}: {e}")
                import traceback
                traceback.print_exc()
        
        print(f"Final room order in self.rooms: {list(self.rooms.keys())}")
    
    def assign_sprites_to_rooms(self):
        """Assign loaded sprites to room instances"""
        objects_data = self.project_data.get('assets', {}).get('objects', {})
        
        # DEBUG: Check what's in the project data for explorer
        print("\n🔍 PROJECT DATA DEBUG:")
        if 'obj_explorer' in objects_data:
            explorer_data = objects_data['obj_explorer']
            print(f"Explorer data keys: {list(explorer_data.keys())}")
            if 'events' in explorer_data:
                events = explorer_data['events']
                print(f"Explorer events in project data: {list(events.keys())}")
                for event_name, event_data in events.items():
                    print(f"  {event_name}: {event_data}")
        else:
            print("obj_explorer not found in project data!")
        
        print("Assigning sprites to room instances...")
        for room_name, room in self.rooms.items():
            room.set_sprites_for_instances(self.sprites, objects_data)
            
            # Load background image for the room
            if room.background_image:
                room.background_surface = room.load_background_image(self.project_path, self.sprites)
                if room.background_surface:
                    print(f"  Loaded background image '{room.background_image}' for room {room_name}")
                else:
                    print(f"  Warning: Could not load background image '{room.background_image}'")
            else:
                room.background_surface = None
            
            # IMPORTANT: Pass sprites and objects_data to each instance's action executor
            for instance in room.instances:
                instance.action_executor.sprites = self.sprites
                instance.action_executor.objects_data = objects_data
                instance.action_executor.game_runner = self
            
            # Count instances with sprites
            sprites_assigned = sum(1 for instance in room.instances if instance.sprite)
            print(f"  Room {room_name}: {sprites_assigned}/{len(room.instances)} instances have sprites")
            
            # DEBUG: Check explorer object data specifically
            for instance in room.instances:
                if instance.object_name == "obj_explorer":
                    print(f"\n🔍 EXPLORER DEBUG:")
                    print(f"  Object name: {instance.object_name}")
                    print(f"  Object data keys: {list(instance.object_data.keys()) if instance.object_data else 'No object_data'}")
                    if instance.object_data and 'events' in instance.object_data:
                        events = instance.object_data['events']
                        print(f"  Events keys: {list(events.keys())}")
                        for event_name, event_data in events.items():
                            print(f"    {event_name}: {event_data}")
                    break
    
    def find_starting_room(self) -> Optional[str]:
        """Find a room to start the game in - USES FIRST ROOM IN ORDER"""
        if not self.rooms:
            return None
        
        # Get the ordered list of room names directly from self.rooms (which is OrderedDict)
        room_names = list(self.rooms.keys())
        
        if room_names:
            print(f"Room order from loaded rooms: {room_names}")
            first_room = room_names[0]
            print(f"Selected starting room: {first_room} (first in order)")
            return first_room
        
        return None
    
    def test_game(self, project_path: str) -> bool:
        """Test run the game from project"""
        print(f"Testing game from project: {project_path}")
        
        # Load project data (but not sprites yet)
        if not self.load_project_data_only(project_path):
            print("Failed to load project")
            return False
        
        # Find starting room
        starting_room = self.find_starting_room()
        if not starting_room:
            print("No rooms found in project")
            return False
        
        print(f"Starting with room: {starting_room}")
        self.current_room = self.rooms[starting_room]
        
        # Set window size based on room
        self.window_width = self.current_room.width
        self.window_height = self.current_room.height
        
        # Run the game (sprites will be loaded after pygame.display is ready)
        return self.run_game_loop()
    
    def run_game_loop(self) -> bool:
        """Main game loop"""
        try:
            # Initialize pygame
            pygame.init()
            
            # Create display
            self.screen = pygame.display.set_mode((self.window_width, self.window_height))
            pygame.display.set_caption(f"PyGameMaker - {self.project_data.get('name', 'Game')}")
            
            # Initialize clock
            self.clock = pygame.time.Clock()
            
            print(f"Game window: {self.window_width}x{self.window_height}")
            
            # NOW load sprites (after pygame.display is initialized)
            print("\nLoading sprites after pygame.display initialization...")
            self.load_sprites()
            
            # Assign sprites to room instances
            self.assign_sprites_to_rooms()
            
            print(f"\nCurrent room: {self.current_room.name}")
            print(f"Room instances: {len(self.current_room.instances)}")
            
            # Print instance details for debugging
            for instance in self.current_room.instances:
                sprite_status = "has sprite" if instance.sprite else "no sprite"
                print(f"  Instance: {instance.object_name} at ({instance.x}, {instance.y}) - {sprite_status}")
            
            self.running = True
            
            # Main game loop
            while self.running:
                try:
                    # Handle all events (quit, keyboard press, etc.)
                    self.handle_all_events()
                    
                    # Update (placeholder for game logic)
                    self.update()
                    
                    # Execute step events for all instances
                    for instance in self.current_room.instances:
                        instance.step()
                    
                    # Process held keyboard keys (continuous movement)
                    self.process_held_keys()
                    
                    # Check collisions
                    self.check_collisions()

                    # Check NOT colliding events (for absence checks)
                    self.check_not_colliding_events()
                    
                    # Clear and render
                    self.screen.fill((135, 206, 235))  # Sky blue
                    self.render()
                    
                    # Control framerate
                    self.clock.tick(self.fps)
                
                except Exception as e:
                    print(f"Error in game loop iteration: {e}")
                    import traceback
                    traceback.print_exc()
                    # Don't break the loop for minor errors
            
            return True
            
        except KeyboardInterrupt:
            print("\nGame interrupted by user")
            return False
            
        except Exception as e:
            print(f"Error in game loop: {e}")
            import traceback
            traceback.print_exc()
            return False
        
        finally:
            # Always cleanup
            self.cleanup()
    
    def change_room(self, room_name: str):
        """Change to a different room"""
        if room_name not in self.rooms:
            print(f"Room {room_name} not found!")
            return
        
        print(f"Changing from {self.current_room.name} to {room_name}")
        self.current_room = self.rooms[room_name]

        # Resize window to match new room dimensions
        self.window_width = self.current_room.width
        self.window_height = self.current_room.height
        self.screen = pygame.display.set_mode((self.window_width, self.window_height))
        print(f"Resized window to {self.window_width}x{self.window_height}")
        
        # Update all instances' action executors with new room reference
        for instance in self.current_room.instances:
            instance.action_executor.room_instances = self.current_room.instances
            instance.action_executor.game_runner = self

    def get_room_list(self):
        """Get ordered list of rooms from project data"""
        rooms_data = self.project_data.get('assets', {}).get('rooms', {})
        return list(rooms_data.keys())

    def get_current_room_index(self):
        """Get index of current room in room list"""
        if self.current_room:
            room_list = self.get_room_list()
            if self.current_room.name in room_list:
                return room_list.index(self.current_room.name)
        return -1

    def go_to_next_room(self):
        """Go to the next room in order"""
        room_list = self.get_room_list()
        current_index = self.get_current_room_index()
        
        if current_index >= 0 and current_index < len(room_list) - 1:
            next_room = room_list[current_index + 1]
            self.change_room(next_room)
            return True
        return False

    def go_to_previous_room(self):
        """Go to the previous room in order"""
        room_list = self.get_room_list()
        current_index = self.get_current_room_index()
        
        if current_index > 0:
            prev_room = room_list[current_index - 1]
            self.change_room(prev_room)
            return True
        return False

    def go_to_first_room(self):
        """Go to the first room"""
        room_list = self.get_room_list()
        if room_list:
            self.change_room(room_list[0])
            return True
        return False

    def handle_all_events(self):
        """Handle all pygame events including keyboard presses"""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.stop_game()
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    self.stop_game()
                elif event.key == pygame.K_F1:
                    self.show_debug_info()
                else:
                    # Process keyboard PRESS events (once per key press)
                    self.process_keydown_event(event)
    
    def process_keydown_event(self, event):
        """Process a single KEYDOWN event for all instances"""
        for instance in self.current_room.instances:
            if instance.to_destroy:
                continue
                
            if instance.object_data and "events" in instance.object_data:
                keyboard_press_events = instance.object_data["events"].get("keyboard_press")
                if keyboard_press_events and isinstance(keyboard_press_events, dict):
                    # Pass room instances for collision checking
                    instance.action_executor.room_instances = self.current_room.instances
                    
                    # Check which key was pressed and execute corresponding actions
                    if event.key == pygame.K_LEFT and "left" in keyboard_press_events:
                        actions = keyboard_press_events["left"].get("actions", [])
                        instance.action_executor.execute_event_actions(instance, actions)
                    elif event.key == pygame.K_RIGHT and "right" in keyboard_press_events:
                        actions = keyboard_press_events["right"].get("actions", [])
                        instance.action_executor.execute_event_actions(instance, actions)
                    elif event.key == pygame.K_UP and "up" in keyboard_press_events:
                        actions = keyboard_press_events["up"].get("actions", [])
                        instance.action_executor.execute_event_actions(instance, actions)
                    elif event.key == pygame.K_DOWN and "down" in keyboard_press_events:
                        actions = keyboard_press_events["down"].get("actions", [])
                        instance.action_executor.execute_event_actions(instance, actions)
    
    def process_held_keys(self):
        """Process held keyboard keys (continuous, every frame)"""
        keys = pygame.key.get_pressed()
        
        # Control key repeat rate for grid movement (15 FPS = every 4 frames at 60 FPS)
        current_time = pygame.time.get_ticks()
        key_repeat_delay = 200  # 200ms between key repeats (5 moves per second)
        
        # Debug: Print when keys are pressed
        if keys[pygame.K_LEFT] or keys[pygame.K_RIGHT] or keys[pygame.K_UP] or keys[pygame.K_DOWN]:
            pressed_keys = []
            if keys[pygame.K_LEFT]: pressed_keys.append("LEFT")
            if keys[pygame.K_RIGHT]: pressed_keys.append("RIGHT") 
            if keys[pygame.K_UP]: pressed_keys.append("UP")
            if keys[pygame.K_DOWN]: pressed_keys.append("DOWN")
            print(f"🎮 Keys pressed: {', '.join(pressed_keys)}")
        
        for instance in self.current_room.instances:
            if instance.to_destroy:
                continue
            
            # Initialize key timing if not exists
            if not hasattr(instance, 'last_key_time'):
                instance.last_key_time = {
                    'left': 0, 'right': 0, 'up': 0, 'down': 0
                }
                
            if instance.object_data and "events" in instance.object_data:
                # Check for both "keyboard" and "keyboard_press" events
                keyboard_events = instance.object_data["events"].get("keyboard")
                if not keyboard_events:
                    # Fallback to keyboard_press events for continuous holding
                    keyboard_events = instance.object_data["events"].get("keyboard_press")
                
                if keyboard_events and isinstance(keyboard_events, dict):
                    # Pass room instances for collision checking
                    instance.action_executor.room_instances = self.current_room.instances
                    
                    # Check each arrow key with timing control
                    if keys[pygame.K_LEFT] and current_time - instance.last_key_time['left'] >= key_repeat_delay:
                        actions = []
                        if "left" in keyboard_events and keyboard_events["left"].get("actions"):
                            actions = keyboard_events["left"]["actions"]
                        elif "press_left" in keyboard_events and keyboard_events["press_left"].get("actions"):
                            actions = keyboard_events["press_left"]["actions"]
                        
                        if actions:
                            print(f"🔄 Executing LEFT actions for {instance.object_name}")
                            instance.action_executor.execute_event_actions(instance, actions)
                            instance.last_key_time['left'] = current_time
                    
                    if keys[pygame.K_RIGHT] and current_time - instance.last_key_time['right'] >= key_repeat_delay:
                        actions = []
                        if "right" in keyboard_events and keyboard_events["right"].get("actions"):
                            actions = keyboard_events["right"]["actions"]
                        elif "press_right" in keyboard_events and keyboard_events["press_right"].get("actions"):
                            actions = keyboard_events["press_right"]["actions"]
                        
                        if actions:
                            print(f"🔄 Executing RIGHT actions for {instance.object_name}")
                            instance.action_executor.execute_event_actions(instance, actions)
                            instance.last_key_time['right'] = current_time
                    
                    if keys[pygame.K_UP] and current_time - instance.last_key_time['up'] >= key_repeat_delay:
                        actions = []
                        if "up" in keyboard_events and keyboard_events["up"].get("actions"):
                            actions = keyboard_events["up"]["actions"]
                        elif "press_up" in keyboard_events and keyboard_events["press_up"].get("actions"):
                            actions = keyboard_events["press_up"]["actions"]
                        
                        if actions:
                            print(f"🔄 Executing UP actions for {instance.object_name}")
                            instance.action_executor.execute_event_actions(instance, actions)
                            instance.last_key_time['up'] = current_time
                    
                    if keys[pygame.K_DOWN] and current_time - instance.last_key_time['down'] >= key_repeat_delay:
                        actions = []
                        if "down" in keyboard_events and keyboard_events["down"].get("actions"):
                            actions = keyboard_events["down"]["actions"]
                        elif "press_down" in keyboard_events and keyboard_events["press_down"].get("actions"):
                            actions = keyboard_events["press_down"]["actions"]
                        
                        if actions:
                            print(f"🔄 Executing DOWN actions for {instance.object_name}")
                            instance.action_executor.execute_event_actions(instance, actions)
                            instance.last_key_time['down'] = current_time
    
    def check_collisions(self):
        """Check collisions and trigger events for ALL colliding objects"""
        instances = self.current_room.instances[:]
        
        for i, instance1 in enumerate(instances):
            if instance1.to_destroy:
                continue
            
            # Skip solid objects as collision initiators
            instance1_solid = instance1.object_data.get('solid', False) if instance1.object_data else False
            if instance1_solid:
                continue
            
            # Check if object is moving
            has_grid_movement = (hasattr(instance1, 'target_x') and 
                                instance1.target_x is not None and 
                                instance1.target_y is not None)
            
            is_moving = (instance1.speed > 0 or 
                        instance1.hspeed != 0 or 
                        instance1.vspeed != 0 or 
                        has_grid_movement)
            
            if not is_moving:
                continue
            
            # Collect ALL colliding objects
            colliding_objects = []
            
            for j, instance2 in enumerate(instances):
                if i != j and not instance2.to_destroy:
                    if instance1.check_collision(instance2):
                        colliding_objects.append(instance2)
            
            # Process collisions with ALL objects found
            for instance2 in colliding_objects:
                # Collision cooldown
                collision_key = f"{instance1.instance_id}_{instance2.instance_id}"
                if not hasattr(instance1, 'collision_times'):
                    instance1.collision_times = {}
                
                current_time = instance1.collision_times.get(collision_key, 0)
                import time
                now = time.time()
                
                if now - current_time >= 0.2:
                    instance1.collision_times[collision_key] = now
                    
                    print(f"🎯 COLLISION: {instance1.object_name} hit {instance2.object_name}")
                    
                    # Store 'other' in context temporarily
                    instance1._collision_other = instance2
                    
                    # Calculate bounce direction
                    dx = instance1.x - instance2.x  
                    dy = instance1.y - instance2.y
                    bounce_type = "horizontal" if abs(dx) > abs(dy) else "vertical"
                    
                    # Execute collision events
                    if instance1.object_data and "events" in instance1.object_data:
                        events = instance1.object_data["events"]
                        
                        # Object-specific collision event
                        collision_event_key = f"collision_with_{instance2.object_name}"
                        collision_event = events.get(collision_event_key)
                        
                        if collision_event and collision_event.get("actions"):
                            print(f"✅ Found specific collision event: {collision_event_key}")
                            instance1.action_executor.room_instances = self.current_room.instances
                            actions = collision_event.get("actions", [])
                            instance1.action_executor.execute_event_actions(instance1, actions)
                            print(f"Executed {collision_event_key} for {instance1.object_name}")
                        else:
                            # Generic collision event
                            collision_event = events.get("collision")
                            if collision_event and collision_event.get("actions"):
                                for action in collision_event["actions"]:
                                    if action.get("action") == "bounce":
                                        if "parameters" not in action:
                                            action["parameters"] = {}
                                        action["parameters"]["bounce_type"] = bounce_type
                                
                                instance1.action_executor.room_instances = self.current_room.instances
                                instance1.action_executor.execute_event(instance1, "collision", instance1.object_data["events"])
                                print(f"Executed generic collision event for {instance1.object_name}")
                            else:
                                # Auto-bounce for solid collisions
                                instance2_solid = instance2.object_data.get('solid', False) if instance2.object_data else False
                                if instance2_solid:
                                    self.handle_collision_bounce(instance1, instance2)
                    
                    # Clear 'other' context
                    instance1._collision_other = None

    def check_not_colliding_events(self):
        """Check for 'NOT colliding' events - triggers when objects are NOT touching"""
        instances = self.current_room.instances[:]
        
        for instance in instances:
            if instance.to_destroy or not instance.object_data:
                continue
            
            events = instance.object_data.get("events", {})
            
            # Look for "NOT colliding" events
            for event_name in events.keys():
                if event_name.startswith("not_collision_with_"):
                    target_object_name = event_name.replace("not_collision_with_", "")
                    
                    # Check if we're currently colliding with any instance of target type
                    is_colliding = False
                    for other in instances:
                        if (other.object_name == target_object_name and 
                            not other.to_destroy and
                            instance.check_collision(other)):
                            is_colliding = True
                            break
                    
                    # If NOT colliding, trigger the event
                    if not is_colliding:
                        event_data = events[event_name]
                        actions = event_data.get("actions", [])
                        if actions:
                            instance.action_executor.room_instances = self.current_room.instances
                            instance.action_executor.execute_event_actions(instance, actions)
                            # Only execute once per frame, then remove to avoid spam
                            # (or add cooldown logic here if needed)

    def handle_collision_bounce(self, moving_instance, wall_instance):
        """Separate objects and apply proper directional bouncing"""
        
        dx = moving_instance.x - wall_instance.x  
        dy = moving_instance.y - wall_instance.y
        
        if abs(dx) > abs(dy):
            # Horizontal collision (hit vertical wall) - reverse horizontal component
            moving_instance.x += 8 if dx > 0 else -8
            
            # Proper horizontal bounce: reverse horizontal direction component
            if 0 <= moving_instance.direction < 90:      # Moving up-right -> up-left
                moving_instance.direction = 180 - moving_instance.direction
            elif 90 <= moving_instance.direction < 180:  # Moving up-left -> up-right  
                moving_instance.direction = 180 - moving_instance.direction
            elif 180 <= moving_instance.direction < 270: # Moving down-left -> down-right
                moving_instance.direction = 180 - moving_instance.direction
            else:  # 270-360: Moving down-right -> down-left
                moving_instance.direction = 180 - moving_instance.direction
                
            print(f"Horizontal bounce: {moving_instance.object_name} -> {moving_instance.direction}")
            
        else:
            # Vertical collision (hit horizontal wall) - reverse vertical component  
            moving_instance.y += 8 if dy > 0 else -8
            
            # Proper vertical bounce: reverse vertical direction component
            moving_instance.direction = 360 - moving_instance.direction
            moving_instance.direction = moving_instance.direction % 360
            
            print(f"Vertical bounce: {moving_instance.object_name} -> {moving_instance.direction}")

    def update(self):
        """Update game logic (placeholder)"""
        pass
    
    def render(self):
        """Render the game"""
        if not self.screen or not self.current_room:
            return
        
        # Render current room
        self.current_room.render(self.screen)
        
        # Update display
        pygame.display.flip()
    
    def show_debug_info(self):
        """Print debug information"""
        print("\n=== DEBUG INFO ===")
        print(f"Project: {self.project_data.get('name', 'Unknown')}")
        print(f"Current room: {self.current_room.name if self.current_room else 'None'}")
        
        if self.current_room:
            print(f"Room size: {self.current_room.width}x{self.current_room.height}")
            print(f"Background: {self.current_room.background_color}")
            print(f"Instances: {len(self.current_room.instances)}")
            
            for i, instance in enumerate(self.current_room.instances):
                sprite_info = "no sprite" if not instance.sprite else f"sprite loaded"
                print(f"  {i+1}. {instance.object_name} at ({instance.x}, {instance.y}) - {sprite_info}")
        
        print("===================\n")
    
    def stop_game(self):
        """Stop the running game"""
        print("Stopping game...")
        self.running = False  # This stops the game loop
        
        # No need to check game_process since we run directly
        # The game loop will exit when self.running = False
    
    def cleanup(self):
        """Clean up pygame resources safely"""
        print("Game cleanup starting...")
        
        try:
            # Stop mixer first
            if pygame.mixer.get_init():
                pygame.mixer.quit()
                print("  Mixer stopped")
        except Exception as e:
            print(f"  Error stopping mixer: {e}")
        
        try:
            # Quit pygame display
            if pygame.display.get_init():
                pygame.display.quit()
                print("  Display quit")
        except Exception as e:
            print(f"  Error quitting display: {e}")
        
        try:
            # Final pygame quit
            if pygame.get_init():
                pygame.quit()
                print("  Pygame quit")
        except Exception as e:
            print(f"  Error quitting pygame: {e}")
        
        print("Game cleanup complete")

    def show_message_box(self, message: str, title: str = "Message", button_text: str = "OK", pause_game: bool = True):
        """Show a message box overlay that pauses the game"""
        if not self.screen:
            print(f"[Console Message - {title}]: {message}")
            return
        
        # Store the current game state
        was_running = self.running
        if pause_game:
            # Don't set self.running = False, just pause processing
            pass
        
        # Message box dimensions
        box_width = min(400, self.window_width - 40)
        box_height = 200
        box_x = (self.window_width - box_width) // 2
        box_y = (self.window_height - box_height) // 2
        
        # Create a semi-transparent overlay
        overlay = pygame.Surface((self.window_width, self.window_height))
        overlay.set_alpha(128)
        overlay.fill((0, 0, 0))
        
        # Message box loop
        font = pygame.font.Font(None, 24)
        title_font = pygame.font.Font(None, 32)
        
        waiting_for_input = True
        while waiting_for_input and self.running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False
                    waiting_for_input = False
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_RETURN or event.key == pygame.K_SPACE or event.key == pygame.K_ESCAPE:
                        waiting_for_input = False
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    # Check if clicked on button
                    mouse_x, mouse_y = event.pos
                    button_rect = pygame.Rect(box_x + box_width//2 - 50, box_y + 150, 100, 30)
                    if button_rect.collidepoint(mouse_x, mouse_y):
                        waiting_for_input = False
            
            # Render the current room (frozen state)
            if self.current_room:
                self.current_room.render(self.screen)
            
            # Draw overlay
            self.screen.blit(overlay, (0, 0))
            
            # Draw message box
            pygame.draw.rect(self.screen, (255, 255, 255), 
                            (box_x, box_y, box_width, box_height))
            pygame.draw.rect(self.screen, (0, 0, 0), 
                            (box_x, box_y, box_width, box_height), 3)
            
            # Draw title
            title_surface = title_font.render(title, True, (0, 0, 0))
            title_rect = title_surface.get_rect(centerx=box_x + box_width//2, y=box_y + 20)
            self.screen.blit(title_surface, title_rect)
            
            # Draw message (word wrap if needed)
            words = message.split(' ')
            lines = []
            current_line = []
            for word in words:
                test_line = ' '.join(current_line + [word])
                if font.size(test_line)[0] > box_width - 40:
                    if current_line:
                        lines.append(' '.join(current_line))
                        current_line = [word]
                    else:
                        lines.append(word)
                else:
                    current_line.append(word)
            if current_line:
                lines.append(' '.join(current_line))
            
            # Draw message lines
            y_offset = 70
            for line in lines[:3]:  # Max 3 lines
                text_surface = font.render(line, True, (0, 0, 0))
                text_rect = text_surface.get_rect(centerx=box_x + box_width//2, y=box_y + y_offset)
                self.screen.blit(text_surface, text_rect)
                y_offset += 30
            
            # Draw button
            button_rect = pygame.Rect(box_x + box_width//2 - 50, box_y + 150, 100, 30)
            pygame.draw.rect(self.screen, (200, 200, 200), button_rect)
            pygame.draw.rect(self.screen, (0, 0, 0), button_rect, 2)
            
            button_surface = font.render(button_text, True, (0, 0, 0))
            button_text_rect = button_surface.get_rect(center=button_rect.center)
            self.screen.blit(button_surface, button_text_rect)
            
            pygame.display.flip()
            self.clock.tick(30)  # Lower FPS while paused
        
        print(f"Message box dismissed")
    
    def cleanup(self):
        """Clean up pygame resources"""
        try:
            if pygame.get_init():
                pygame.quit()
            print("Game cleanup complete")
        except Exception as e:
            print(f"Error during cleanup: {e}")

# Test function
def test_runner():
    """Test the enhanced game runner"""
    runner = GameRunner()
    
    # Test with a project path - replace with actual path
    test_project = "/path/to/your/project"
    
    if Path(test_project).exists():
        runner.test_game(test_project)
    else:
        print(f"Test project not found: {test_project}")
        print("Please update the test_project path")

if __name__ == "__main__":
    test_runner()