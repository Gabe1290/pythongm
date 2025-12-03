#!/usr/bin/env python3
"""
Enhanced GameRunner with smooth movement that snaps to grid
"""

import os
import sys
# Force pygame to use software rendering to avoid conflicts with Qt
# Use appropriate video driver based on platform
if sys.platform == 'win32':
    os.environ['SDL_VIDEODRIVER'] = 'windows'
elif sys.platform == 'darwin':
    os.environ['SDL_VIDEODRIVER'] = 'cocoa'
else:  # Linux and other Unix-like systems
    os.environ['SDL_VIDEODRIVER'] = 'x11'
os.environ['SDL_RENDER_DRIVER'] = 'software'

import pygame
import json
import sys
from pathlib import Path
from typing import Dict, List, Optional, Tuple

from runtime.action_executor import ActionExecutor
from events.plugin_loader import load_all_plugins

class GameSprite:
    """Represents a loaded sprite"""
    
    def __init__(self, image_path: str):
        self.path = image_path
        self.surface = None
        self.width = 32
        self.height = 32
        self.load_image()
    
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

    def __init__(self, object_name: str, x: float, y: float, instance_data: dict, action_executor=None):
        self.object_name = object_name
        self.x = float(x)
        self.y = float(y)
        self.instance_id = instance_data.get('instance_id', id(self))
        self.visible = instance_data.get('visible', True)
        self.rotation = instance_data.get('rotation', 0)
        self.scale_x = instance_data.get('scale_x', 1.0)
        self.scale_y = instance_data.get('scale_y', 1.0)

        self.sprite = None
        self.object_data = None
        self.to_destroy = False

        # Speed properties for smooth movement
        self.hspeed = 0.0  # Horizontal speed (pixels per frame)
        self.vspeed = 0.0  # Vertical speed (pixels per frame)

        # Track if movement keys are currently pressed
        self.keys_pressed = set()  # Set of currently pressed keys

        # Action executor - use shared instance or create new one
        self.action_executor = action_executor if action_executor else ActionExecutor()

        # Execute Create event when instance is created
        if self.object_data and "events" in self.object_data:
            self.action_executor.execute_event(self, "create", self.object_data["events"])
    
    def step(self):
        """Execute step event every frame"""
        if self.object_data and "events" in self.object_data:
            # Execute regular step event
            self.action_executor.execute_event(self, "step", self.object_data["events"])
            
            # Check for "nokey" event (GameMaker compatibility)
            # This event triggers when no keyboard keys are currently pressed
            events = self.object_data["events"]
            if "keyboard" in events and "nokey" in events["keyboard"]:
                # Check if no keys are currently pressed
                keys_pressed = getattr(self, 'keys_pressed', set())
                if len(keys_pressed) == 0:
                    # No keys pressed - execute nokey event actions
                    nokey_event = events["keyboard"]["nokey"]
                    if isinstance(nokey_event, dict) and "actions" in nokey_event:
                        for action_data in nokey_event["actions"]:
                            self.action_executor.execute_action(self, action_data)

    def set_sprite(self, sprite: GameSprite):
        """Set the sprite for this instance"""
        self.sprite = sprite
    
    def set_object_data(self, object_data: dict):
        """Set the object data from project (create event triggered when room becomes active)"""
        self.object_data = object_data

        # NOTE: Create event is NOT triggered here!
        # It's triggered when the room becomes active (in change_room or run_game_loop)
    
    def render(self, screen: pygame.Surface):
        """Render this instance"""
        if not self.visible or not self.sprite:
            return
        
        # Calculate render position
        render_x = int(self.x)
        render_y = int(self.y)
        
        # Handle scaling (basic implementation)
        if self.scale_x != 1.0 or self.scale_y != 1.0:
            scaled_width = int(self.sprite.width * self.scale_x)
            scaled_height = int(self.sprite.height * self.scale_y)
            scaled_surface = pygame.transform.scale(self.sprite.surface, (scaled_width, scaled_height))
            screen.blit(scaled_surface, (render_x, render_y))
        else:
            screen.blit(self.sprite.surface, (render_x, render_y))

class GameRoom:
    """Represents a game room with instances"""

    def __init__(self, name: str, room_data: dict, action_executor=None):
        self.name = name
        self.width = room_data.get('width', 1024)
        self.height = room_data.get('height', 768)
        self.background_color = self.parse_color(room_data.get('background_color', '#87CEEB'))
        self.instances: List[GameInstance] = []
        self.action_executor = action_executor

        # Load instances
        instances_data = room_data.get('instances', [])
        for instance_data in instances_data:
            instance = GameInstance(
                instance_data['object_name'],
                instance_data['x'],
                instance_data['y'],
                instance_data,
                action_executor=self.action_executor
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
    
    def render(self, screen: pygame.Surface):
        """Render the room and all its instances"""
        # Clear screen with background color
        screen.fill(self.background_color)
        
        # Render all instances
        for instance in self.instances:
            instance.render(screen)

class GameRunner:
    """Enhanced game runner that properly renders rooms with objects"""

    def __init__(self, project_path: str = None):
        self.running = False
        self.screen = None
        self.clock = None
        self.project_data = None
        self.project_path = None

        # Global game state (Score/Lives/Health system) - must be before ActionExecutor
        self.score = 0
        self.lives = 3
        self.health = 100.0
        self.highscores = []  # List of (name, score) tuples

        # Shared action executor for all instances (pass self for global state access)
        self.action_executor = ActionExecutor(game_runner=self)

        # Load plugins
        print("🔌 Loading action/event plugins...")
        self.plugin_loader = load_all_plugins(self.action_executor)

        # Game assets
        self.sprites: Dict[str, GameSprite] = {}
        self.rooms: Dict[str, GameRoom] = {}
        self.current_room = None

        # Game settings
        self.fps = 60
        self.window_width = 800
        self.window_height = 600

        # If project path provided, load it
        if project_path:
            self.load_project_data_only(project_path)
    
    def is_game_running(self):
        """Check if game is currently running"""
        return self.running
    
    def load_project_data_only(self, project_path: str) -> bool:
        """Load project data without loading sprites (sprites loaded later)"""
        try:
            path = Path(project_path)
            
            # If it's a directory, look for project.json inside
            if path.is_dir():
                self.project_path = path
                project_file = path / "project.json"
            # If it's a file, use it directly
            elif path.is_file() and path.name == "project.json":
                self.project_path = path.parent
                project_file = path
            else:
                print(f"Invalid project path: {project_path}")
                return False
            
            if not project_file.exists():
                print(f"Project file not found: {project_file}")
                return False
            
            # Load project data
            with open(project_file, 'r') as f:
                self.project_data = json.load(f)
            
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
                    print(f"  âœ… Loaded sprite: {sprite_name} ({sprite.width}x{sprite.height})")
                else:
                    print(f"  âš ï¸  Sprite {sprite_name} has no file path")
            except Exception as e:
                print(f"  âŒ Error loading sprite {sprite_name}: {e}")
    
    def load_rooms_without_sprites(self):
        """Load rooms but don't assign sprites to instances yet"""
        rooms_data = self.project_data.get('assets', {}).get('rooms', {})
        
        print(f"Loading {len(rooms_data)} rooms...")
        
        for room_name, room_info in rooms_data.items():
            try:
                room = GameRoom(room_name, room_info, action_executor=self.action_executor)
                # Don't set sprites yet - will do this after pygame.display is ready
                self.rooms[room_name] = room
                print(f"  Loaded room: {room_name} ({len(room.instances)} instances)")
            except Exception as e:
                print(f"  Error loading room {room_name}: {e}")
                import traceback
                traceback.print_exc()
    
    def assign_sprites_to_rooms(self):
        """Assign loaded sprites to room instances"""
        objects_data = self.project_data.get('assets', {}).get('objects', {})
        
        print("Assigning sprites to room instances...")
        for room_name, room in self.rooms.items():
            room.set_sprites_for_instances(self.sprites, objects_data)
            
            # Count instances with sprites
            sprites_assigned = sum(1 for instance in room.instances if instance.sprite)
            print(f"  Room {room_name}: {sprites_assigned}/{len(room.instances)} instances have sprites")
    
    def find_starting_room(self) -> Optional[str]:
        """Find a room to start the game in"""
        if not self.rooms:
            return None
        
        # Look for common starting room names
        preferred_names = ['main', 'start', 'level1', 'room1', 'intro']
        
        for name in preferred_names:
            if name in self.rooms:
                return name
        
        # Just use the first room
        return list(self.rooms.keys())[0]
    
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
            print("\nðŸŽ® Loading sprites after pygame.display initialization...")
            self.load_sprites()
            
            # Assign sprites to room instances
            self.assign_sprites_to_rooms()

            print(f"\nCurrent room: {self.current_room.name}")
            print(f"Room instances: {len(self.current_room.instances)}")

            # Count instances by type for summary
            instance_counts = {}
            for instance in self.current_room.instances:
                obj_name = instance.object_name
                instance_counts[obj_name] = instance_counts.get(obj_name, 0) + 1

            print(f"Instance summary:")
            for obj_name, count in sorted(instance_counts.items()):
                print(f"  {obj_name}: {count}")

            # IMPORTANT: Execute create events for starting room instances
            print(f"\n🎬 Triggering create events for starting room: {self.current_room.name}")
            for instance in self.current_room.instances:
                if instance.object_data and "events" in instance.object_data:
                    self.action_executor.execute_event(instance, "create", instance.object_data["events"])

            self.running = True
            
            # Main game loop
            while self.running:
                # Execute begin_step events (before everything else)
                for instance in self.current_room.instances:
                    if instance.object_data and "events" in instance.object_data:
                        events = instance.object_data["events"]
                        if "begin_step" in events:
                            instance.action_executor.execute_event(instance, "begin_step", events)
                
                # Handle events (keyboard, mouse, etc.)
                self.handle_events()
                
                # Update (collision checking, movement, etc.)
                self.update()
                
                # Execute step events for all instances
                for instance in self.current_room.instances:
                    instance.step()
                
                # Execute end_step events (after step, before rendering)
                for instance in self.current_room.instances:
                    if instance.object_data and "events" in instance.object_data:
                        events = instance.object_data["events"]
                        if "end_step" in events:
                            instance.action_executor.execute_event(instance, "end_step", events)
                
                # Trigger destroy events for instances marked for destruction
                for instance in self.current_room.instances:
                    if instance.to_destroy:
                        if instance.object_data and "events" in instance.object_data:
                            events = instance.object_data["events"]
                            if "destroy" in events:
                                print(f"💥 Triggering destroy event for {instance.object_name}")
                                instance.action_executor.execute_event(instance, "destroy", events)
                
                # Remove destroyed instances
                self.current_room.instances = [inst for inst in self.current_room.instances if not inst.to_destroy]

                # Clear screen
                self.screen.fill((135, 206, 235))  # Sky blue

                # Render
                self.render()

                # Check for pending messages and display them
                self.process_pending_messages()

                # Control framerate
                self.clock.tick(self.fps)
            
            return True
            
        except Exception as e:
            print(f"Error in game loop: {e}")
            import traceback
            traceback.print_exc()
            return False
        
        finally:
            self.cleanup()
    
    def handle_events(self):
        """Handle pygame events"""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.stop_game()
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    self.stop_game()
                elif event.key == pygame.K_F1:
                    self.show_debug_info()
                else:
                    # Handle keyboard press events for all instances
                    self.handle_keyboard_press(event.key)
            elif event.type == pygame.KEYUP:
                # Handle keyboard release events
                self.handle_keyboard_release(event.key)
            elif event.type == pygame.MOUSEBUTTONDOWN:
                # Handle mouse button press
                self.handle_mouse_press(event.button, event.pos)
            elif event.type == pygame.MOUSEBUTTONUP:
                # Handle mouse button release
                self.handle_mouse_release(event.button, event.pos)
            elif event.type == pygame.MOUSEMOTION:
                # Handle mouse movement
                self.handle_mouse_motion(event.pos)
    
    def handle_keyboard_press(self, key):
        """Handle keyboard press event"""
        if not self.current_room:
            return
        
        # Map pygame keys to sub-event keys
        key_map = {
            pygame.K_LEFT: "left",
            pygame.K_RIGHT: "right",
            pygame.K_UP: "up",
            pygame.K_DOWN: "down",
        }
        
        sub_key = key_map.get(key)
        if not sub_key:
            return
        
        print(f"\n⌨️  Keyboard pressed: {sub_key}")
        
        # Track which keys are pressed
        for instance in self.current_room.instances:
            if hasattr(instance, "keys_pressed"):
                instance.keys_pressed.add(sub_key)
        
        # Execute keyboard events for all instances
        events_found = False
        for instance in self.current_room.instances:
            if not instance.object_data:
                continue
            
            events = instance.object_data.get('events', {})
            
            # Check if this is a direction reversal (moving left and pressing right, or vice versa)
            is_direction_reversal = False
            if sub_key == "left" and hasattr(instance, 'hspeed') and instance.hspeed > 0:
                is_direction_reversal = True
            elif sub_key == "right" and hasattr(instance, 'hspeed') and instance.hspeed < 0:
                is_direction_reversal = True
            elif sub_key == "up" and hasattr(instance, 'vspeed') and instance.vspeed > 0:
                is_direction_reversal = True
            elif sub_key == "down" and hasattr(instance, 'vspeed') and instance.vspeed < 0:
                is_direction_reversal = True
            
            # If reversing direction, snap to grid first for clean movement
            if is_direction_reversal:
                grid_size = 32  # Default grid size
                instance.x = round(instance.x / grid_size) * grid_size
                instance.y = round(instance.y / grid_size) * grid_size
                print(f"  🔄 Direction reversal: snapped {instance.object_name} to grid ({instance.x}, {instance.y})")
            
            # Check for keyboard_press event
            if "keyboard_press" in events:
                keyboard_press_event = events["keyboard_press"]
                if isinstance(keyboard_press_event, dict) and sub_key in keyboard_press_event:
                    print(f"  ✅ Executing keyboard_press.{sub_key} for {instance.object_name}")
                    events_found = True
                    sub_event_data = keyboard_press_event[sub_key]
                    if isinstance(sub_event_data, dict) and "actions" in sub_event_data:
                        for action_data in sub_event_data["actions"]:
                            instance.action_executor.execute_action(instance, action_data)
            
            # Check for keyboard (held) event
            if "keyboard" in events:
                keyboard_event = events["keyboard"]
                if isinstance(keyboard_event, dict) and sub_key in keyboard_event:
                    print(f"  ✅ Executing keyboard.{sub_key} for {instance.object_name}")
                    events_found = True
                    sub_event_data = keyboard_event[sub_key]
                    if isinstance(sub_event_data, dict) and "actions" in sub_event_data:
                        for action_data in sub_event_data["actions"]:
                            instance.action_executor.execute_action(instance, action_data)
                # Removed error messages - it's normal for an object to not handle every key
        
        if not events_found:
            print(f"  ℹ️  No objects have keyboard events for '{sub_key}'")
    
    def handle_keyboard_release(self, key):
        """Handle keyboard release event - stop movement immediately AND trigger JSON events"""
        if not self.current_room:
            return
        
        # Map pygame keys
        key_map = {
            pygame.K_LEFT: "left",
            pygame.K_RIGHT: "right",
            pygame.K_UP: "up",
            pygame.K_DOWN: "down",
        }
        
        sub_key = key_map.get(key)
        if not sub_key:
            return
        
        print(f"\n⌨️  Keyboard released: {sub_key}")
        
        # Stop movement immediately and snap to grid for responsive controls
        for instance in self.current_room.instances:
            if not instance.object_data:
                continue
            
            # Remove key from pressed set
            if hasattr(instance, "keys_pressed"):
                instance.keys_pressed.discard(sub_key)
            
            # Check if this instance has keyboard events for this key
            events = instance.object_data.get('events', {})
            has_keyboard_event = False
            
            if "keyboard" in events:
                keyboard_event = events["keyboard"]
                if isinstance(keyboard_event, dict) and sub_key in keyboard_event:
                    has_keyboard_event = True
            
            if "keyboard_press" in events:
                keyboard_press_event = events["keyboard_press"]
                if isinstance(keyboard_press_event, dict) and sub_key in keyboard_press_event:
                    has_keyboard_event = True
            
            # If this object responds to this key, stop its movement
            if has_keyboard_event:
                # Stop movement based on which key was released
                if sub_key in ["left", "right"]:
                    instance.hspeed = 0
                    print(f"  🛑 Stopped horizontal movement for {instance.object_name}")
                elif sub_key in ["up", "down"]:
                    instance.vspeed = 0
                    print(f"  🛑 Stopped vertical movement for {instance.object_name}")
                
                # Snap to grid for clean positioning
                grid_size = 32  # Default grid size
                instance.x = round(instance.x / grid_size) * grid_size
                instance.y = round(instance.y / grid_size) * grid_size
                print(f"  📍 Snapped to grid: ({instance.x}, {instance.y})")
            
            # NEW: Execute keyboard_release events from JSON (custom actions)
            if "keyboard_release" in events:
                keyboard_release_event = events["keyboard_release"]
                if isinstance(keyboard_release_event, dict) and sub_key in keyboard_release_event:
                    print(f"  ✅ Executing keyboard_release.{sub_key} for {instance.object_name}")
                    sub_event_data = keyboard_release_event[sub_key]
                    if isinstance(sub_event_data, dict) and "actions" in sub_event_data:
                        for action_data in sub_event_data["actions"]:
                            instance.action_executor.execute_action(instance, action_data)
    
    def handle_mouse_press(self, button, pos):
        """Handle mouse button press event"""
        if not self.current_room:
            return
        
        # Map pygame mouse buttons to event names
        button_map = {
            1: "left_button",
            2: "middle_button",
            3: "right_button",
        }
        
        button_name = button_map.get(button)
        if not button_name:
            return
        
        mouse_x, mouse_y = pos
        print(f"\n🖱️  Mouse pressed: {button_name} at ({mouse_x}, {mouse_y})")
        
        # Execute mouse events for all instances
        for instance in self.current_room.instances:
            if not instance.object_data:
                continue
            
            events = instance.object_data.get('events', {})
            
            # Check for mouse event
            if "mouse" in events:
                mouse_event = events["mouse"]
                if isinstance(mouse_event, dict) and button_name in mouse_event:
                    print(f"  ✅ Executing mouse.{button_name} for {instance.object_name}")
                    sub_event_data = mouse_event[button_name]
                    if isinstance(sub_event_data, dict) and "actions" in sub_event_data:
                        for action_data in sub_event_data["actions"]:
                            # Add mouse position to instance for actions to use
                            instance.mouse_x = mouse_x
                            instance.mouse_y = mouse_y
                            instance.action_executor.execute_action(instance, action_data)
    
    def handle_mouse_release(self, button, pos):
        """Handle mouse button release event"""
        if not self.current_room:
            return
        
        button_map = {
            1: "left_button_released",
            2: "middle_button_released",
            3: "right_button_released",
        }
        
        button_name = button_map.get(button)
        if not button_name:
            return
        
        mouse_x, mouse_y = pos
        
        # Execute mouse release events
        for instance in self.current_room.instances:
            if not instance.object_data:
                continue
            
            events = instance.object_data.get('events', {})
            
            if "mouse" in events:
                mouse_event = events["mouse"]
                if isinstance(mouse_event, dict) and button_name in mouse_event:
                    sub_event_data = mouse_event[button_name]
                    if isinstance(sub_event_data, dict) and "actions" in sub_event_data:
                        for action_data in sub_event_data["actions"]:
                            instance.mouse_x = mouse_x
                            instance.mouse_y = mouse_y
                            instance.action_executor.execute_action(instance, action_data)
    
    def handle_mouse_motion(self, pos):
        """Handle mouse movement event"""
        if not self.current_room:
            return
        
        mouse_x, mouse_y = pos
        
        # Execute mouse motion events
        for instance in self.current_room.instances:
            if not instance.object_data:
                continue
            
            events = instance.object_data.get('events', {})
            
            if "mouse" in events:
                mouse_event = events["mouse"]
                if isinstance(mouse_event, dict) and "mouse_move" in mouse_event:
                    sub_event_data = mouse_event["mouse_move"]
                    if isinstance(sub_event_data, dict) and "actions" in sub_event_data:
                        for action_data in sub_event_data["actions"]:
                            instance.mouse_x = mouse_x
                            instance.mouse_y = mouse_y
                            instance.action_executor.execute_action(instance, action_data)
    
    def update(self):
        """Update game logic"""
        if not self.current_room:
            return
        
        # Get objects data for solid checks
        objects_data = self.project_data.get('assets', {}).get('objects', {})
        
        # Check for room restart/transition flags FIRST
        for instance in self.current_room.instances:
            if hasattr(instance, 'restart_room_flag') and instance.restart_room_flag:
                print("🔄 Restarting room...")
                self.restart_current_room()
                return
            
            if hasattr(instance, 'next_room_flag') and instance.next_room_flag:
                print("➡️  Going to next room...")
                self.goto_next_room()
                return

            if hasattr(instance, 'previous_room_flag') and instance.previous_room_flag:
                print("⬅️  Going to previous room...")
                self.goto_previous_room()
                return


        # Apply speed-based movement (hspeed, vspeed) with collision checking
        for instance in self.current_room.instances:
            if hasattr(instance, 'hspeed') and instance.hspeed != 0:
                # Store intended position
                instance.intended_x = instance.x + instance.hspeed
                instance.intended_y = instance.y
                
                # Check collision
                if self.check_movement_collision(instance, objects_data):
                    instance.x = instance.intended_x
                
                # Clean up
                delattr(instance, 'intended_x')
                delattr(instance, 'intended_y')
                
            if hasattr(instance, 'vspeed') and instance.vspeed != 0:
                # Store intended position
                instance.intended_x = instance.x
                instance.intended_y = instance.y + instance.vspeed
                
                # Check collision
                if self.check_movement_collision(instance, objects_data):
                    instance.y = instance.intended_y
                
                # Clean up
                delattr(instance, 'intended_x')
                delattr(instance, 'intended_y')
        # Handle intended movement with collision checking
        for instance in self.current_room.instances:
            if hasattr(instance, 'intended_x') and hasattr(instance, 'intended_y'):
                # Check if movement would collide with solid objects
                can_move = self.check_movement_collision(instance, objects_data)
                
                if can_move:
                    print(f"✅ Movement allowed: {instance.object_name} → ({instance.intended_x}, {instance.intended_y})")
                    instance.x = instance.intended_x
                    instance.y = instance.intended_y
                else:
                    print(f"❌ Movement blocked: {instance.object_name} (hit solid object)")
                
                # Clear intended movement
                delattr(instance, 'intended_x')
                delattr(instance, 'intended_y')
        
        # Check collision events
        for instance in self.current_room.instances:
            self.check_collision_events(instance, objects_data)

        # NOTE: Step events are executed in the main game loop, not here
        # (see run_game_loop where instance.step() is called)
    
    def check_movement_collision(self, moving_instance, objects_data: dict) -> bool:
        """Check if intended movement would collide with solid objects"""
        intended_x = moving_instance.intended_x
        intended_y = moving_instance.intended_y
        
        # Get dimensions
        w1 = moving_instance.sprite.width if moving_instance.sprite else 32
        h1 = moving_instance.sprite.height if moving_instance.sprite else 32
        
        for other_instance in self.current_room.instances:
            if other_instance == moving_instance:
                continue
            
            # Check if other object is solid
            if other_instance.object_name in objects_data:
                other_obj_data = objects_data[other_instance.object_name]
                is_solid = other_obj_data.get('solid', False)
                
                if not is_solid:
                    continue
                
                # Get other instance dimensions
                w2 = other_instance.sprite.width if other_instance.sprite else 32
                h2 = other_instance.sprite.height if other_instance.sprite else 32
                
                # Check rectangle overlap at intended position
                if self.rectangles_overlap(intended_x, intended_y, w1, h1,
                                          other_instance.x, other_instance.y, w2, h2):
                    return False
        
        return True
    
    def check_collision_events(self, instance, objects_data: dict):
        """Check if instance is colliding and trigger collision events

        Uses collision tracking to fire events only once per collision pair
        until the objects separate.
        """
        if not instance.object_data:
            return

        # Initialize collision tracking set if not exists
        if not hasattr(instance, '_active_collisions'):
            instance._active_collisions = set()

        events = instance.object_data.get('events', {})

        # Track which collisions are currently active this frame
        current_collisions = set()

        # Check all collision events
        for event_name, event_data in events.items():
            if event_name.startswith('collision_with_'):
                target_object = event_name.replace('collision_with_', '')

                # Check collision with target object
                for other_instance in self.current_room.instances:
                    if other_instance == instance:
                        continue

                    if other_instance.object_name == target_object:
                        if self.instances_overlap(instance, other_instance):
                            # Create unique collision key
                            collision_key = (id(other_instance), event_name)
                            current_collisions.add(collision_key)

                            # Only fire event if this is a NEW collision (wasn't active last frame)
                            if collision_key not in instance._active_collisions:
                                print(f"🎯 COLLISION DETECTED: {instance.object_name} with {other_instance.object_name}")
                                # Pass other_instance as context for collision actions
                                instance.action_executor.execute_collision_event(instance, event_name, events, other_instance)
                            break

        # Update active collisions for next frame
        instance._active_collisions = current_collisions
    
    def instances_overlap(self, inst1, inst2) -> bool:
        """Check if two instances overlap"""
        w1 = inst1.sprite.width if inst1.sprite else 32
        h1 = inst1.sprite.height if inst1.sprite else 32
        w2 = inst2.sprite.width if inst2.sprite else 32
        h2 = inst2.sprite.height if inst2.sprite else 32
        
        return self.rectangles_overlap(inst1.x, inst1.y, w1, h1, inst2.x, inst2.y, w2, h2)
    
    def rectangles_overlap(self, x1, y1, w1, h1, x2, y2, w2, h2) -> bool:
        """Check if two rectangles overlap"""
        return not (x1 + w1 <= x2 or x2 + w2 <= x1 or y1 + h1 <= y2 or y2 + h2 <= y1)
    
    def restart_current_room(self):
        """Restart the current room"""
        if not self.current_room:
            return
        
        room_name = self.current_room.name
        # Trigger a room reload
        room_list = self.get_room_list()
        if room_name in room_list:
            # Find the room in our rooms dictionary and reload it
            room_data = self.project_data.get('assets', {}).get('rooms', {}).get(room_name)
            if room_data:
                # Just change to the same room (will recreate instances)
                self.change_room(room_name)
    
    def goto_next_room(self):
        """Go to the next room"""
        print(f"🚪 goto_next_room called")
        if not self.current_room:
            print(f"❌ No current room!")
            return

        room_list = self.get_room_list()
        print(f"🔍 Room list: {room_list}")
        if not room_list:
            print(f"❌ Room list is empty!")
            return

        try:
            current_index = room_list.index(self.current_room.name)
            next_index = current_index + 1
            if next_index < len(room_list):
                next_room_name = room_list[next_index]
                print(f"➡️  Changing from '{self.current_room.name}' (index {current_index}) to '{next_room_name}' (index {next_index})")
                self.change_room(next_room_name)
            else:
                print(f"⚠️  Already at last room '{self.current_room.name}'")
        except ValueError:
            print(f"❌ Current room '{self.current_room.name}' not in room list")

    def goto_previous_room(self):
        """Go to the previous room"""
        print(f"🚪 goto_previous_room called")
        if not self.current_room:
            print(f"❌ No current room!")
            return

        room_list = self.get_room_list()
        print(f"🔍 Room list: {room_list}")
        if not room_list:
            print(f"❌ Room list is empty!")
            return

        try:
            current_index = room_list.index(self.current_room.name)
            if current_index > 0:
                prev_index = current_index - 1
                prev_room_name = room_list[prev_index]
                print(f"⬅️  Changing from '{self.current_room.name}' (index {current_index}) to '{prev_room_name}' (index {prev_index})")
                self.change_room(prev_room_name)
            else:
                print(f"⚠️  Already at first room '{self.current_room.name}'")
        except ValueError:
            print(f"❌ Current room '{self.current_room.name}' not in room list")

    def get_room_list(self) -> List[str]:
        """Get ordered list of room names"""
        if not self.project_data:
            return []
        
        rooms_data = self.project_data.get('assets', {}).get('rooms', {})
        room_order = self.project_data.get('room_order', [])
        
        if room_order:
            return [r for r in room_order if r in rooms_data]
        else:
            return list(rooms_data.keys())
    
    def change_room(self, room_name: str):
        """Change to a different room"""
        if room_name in self.rooms:
            print(f"🚪 Changing to room: {room_name}")
            self.current_room = self.rooms[room_name]

            # Resize the window if room size is different
            if self.screen:
                room_width = self.current_room.width
                room_height = self.current_room.height
                current_width, current_height = self.screen.get_size()

                if room_width != current_width or room_height != current_height:
                    print(f"📐 Resizing window from {current_width}x{current_height} to {room_width}x{room_height}")
                    self.screen = pygame.display.set_mode((room_width, room_height))
                    print(f"✅ Window resized to {room_width}x{room_height}")

            # Execute create events for all instances
            for instance in self.current_room.instances:
                if instance.object_data and "events" in instance.object_data:
                    instance.action_executor.execute_event(instance, "create", instance.object_data["events"])

    
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
        """Stop the game"""
        print("Stopping game...")
        self.running = False
    
    def run(self):
        """Run the game - main entry point called by IDE"""
        if not self.project_data:
            print("❌ No project loaded. Cannot run game.")
            return False
        
        # Find starting room
        starting_room = self.find_starting_room()
        if not starting_room:
            print("❌ No rooms found in project")
            return False
        
        print(f"🎮 Starting game with room: {starting_room}")
        self.current_room = self.rooms[starting_room]
        
        # Set window size based on room
        self.window_width = self.current_room.width
        self.window_height = self.current_room.height
        
        # Run the game loop
        return self.run_game_loop()
    
    def process_pending_messages(self):
        """Check all instances for pending messages and display them"""
        for instance in self.current_room.instances:
            if hasattr(instance, 'pending_messages') and instance.pending_messages:
                # Get the first pending message
                message = instance.pending_messages.pop(0)
                # Display the message dialog (this pauses the game)
                self.show_message_dialog(message)

    def show_message_dialog(self, message: str):
        """Display a message dialog box that pauses the game

        The dialog shows the message centered on screen with an OK button.
        User can click OK or press Enter/Space/Escape to dismiss.
        """
        # Stop all instances when showing a message dialog
        # This prevents other instances from continuing to move while dialog is open
        for instance in self.current_room.instances:
            instance.hspeed = 0
            instance.vspeed = 0

        # Create a semi-transparent overlay
        overlay = pygame.Surface((self.window_width, self.window_height))
        overlay.fill((0, 0, 0))
        overlay.set_alpha(128)

        # Dialog box dimensions
        dialog_width = min(400, self.window_width - 40)
        dialog_height = 150
        dialog_x = (self.window_width - dialog_width) // 2
        dialog_y = (self.window_height - dialog_height) // 2

        # Button dimensions
        button_width = 80
        button_height = 30
        button_x = dialog_x + (dialog_width - button_width) // 2
        button_y = dialog_y + dialog_height - button_height - 15

        # Get font
        try:
            font = pygame.font.Font(None, 24)
            title_font = pygame.font.Font(None, 28)
        except Exception:
            font = pygame.font.SysFont('arial', 18)
            title_font = pygame.font.SysFont('arial', 22)

        # Dialog loop - waits for user to dismiss
        waiting = True
        while waiting:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.stop_game()
                    waiting = False
                elif event.type == pygame.KEYDOWN:
                    if event.key in (pygame.K_RETURN, pygame.K_SPACE, pygame.K_ESCAPE):
                        waiting = False
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    # Check if OK button was clicked
                    mx, my = event.pos
                    if (button_x <= mx <= button_x + button_width and
                        button_y <= my <= button_y + button_height):
                        waiting = False

            # Draw overlay
            self.screen.blit(overlay, (0, 0))

            # Draw dialog box
            pygame.draw.rect(self.screen, (240, 240, 240),
                           (dialog_x, dialog_y, dialog_width, dialog_height))
            pygame.draw.rect(self.screen, (100, 100, 100),
                           (dialog_x, dialog_y, dialog_width, dialog_height), 2)

            # Draw title bar
            pygame.draw.rect(self.screen, (70, 130, 180),
                           (dialog_x, dialog_y, dialog_width, 30))
            title_text = title_font.render("Message", True, (255, 255, 255))
            self.screen.blit(title_text, (dialog_x + 10, dialog_y + 5))

            # Draw message text (wrap if too long)
            words = message.split()
            lines = []
            current_line = ""
            max_text_width = dialog_width - 30

            for word in words:
                test_line = current_line + (" " if current_line else "") + word
                if font.size(test_line)[0] <= max_text_width:
                    current_line = test_line
                else:
                    if current_line:
                        lines.append(current_line)
                    current_line = word

            if current_line:
                lines.append(current_line)

            # Render message lines
            y_offset = dialog_y + 45
            for line in lines[:4]:  # Max 4 lines
                text_surface = font.render(line, True, (0, 0, 0))
                self.screen.blit(text_surface, (dialog_x + 15, y_offset))
                y_offset += 22

            # Draw OK button
            mouse_pos = pygame.mouse.get_pos()
            button_hover = (button_x <= mouse_pos[0] <= button_x + button_width and
                          button_y <= mouse_pos[1] <= button_y + button_height)

            button_color = (100, 149, 237) if button_hover else (70, 130, 180)
            pygame.draw.rect(self.screen, button_color,
                           (button_x, button_y, button_width, button_height))
            pygame.draw.rect(self.screen, (50, 50, 50),
                           (button_x, button_y, button_width, button_height), 1)

            ok_text = font.render("OK", True, (255, 255, 255))
            ok_text_x = button_x + (button_width - ok_text.get_width()) // 2
            ok_text_y = button_y + (button_height - ok_text.get_height()) // 2
            self.screen.blit(ok_text, (ok_text_x, ok_text_y))

            pygame.display.flip()
            self.clock.tick(60)

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
