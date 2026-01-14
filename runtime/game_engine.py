#!/usr/bin/env python3
"""
Enhanced GameRunner that properly renders room objects
"""

import pygame
import json
from pathlib import Path
from typing import Dict, List, Optional, Tuple

from runtime.action_executor import ActionExecutor
from core.logger import get_logger
logger = get_logger(__name__)

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
                logger.debug(f"Sprite not found: {self.path}")
                self.create_default_sprite()
        except Exception as e:
            logger.error(f"Error loading sprite {self.path}: {e}")
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

        self.sprite = None
        self.object_data = None

        # Speed properties for smooth movement
        self.hspeed = 0.0  # Horizontal speed (pixels per frame)
        self.vspeed = 0.0  # Vertical speed (pixels per frame)

        # Action executor
        self.action_executor = ActionExecutor()

        # NOTE: Create event is triggered in set_object_data(), not here
        # because object_data is set to None initially

    def step(self):
        """Execute step event every frame"""
        if self.object_data and "events" in self.object_data:
            self.action_executor.execute_event(self, "step", self.object_data["events"])

    def set_sprite(self, sprite: GameSprite):
        """Set the sprite for this instance"""
        self.sprite = sprite

    def set_object_data(self, object_data: dict):
        """Set the object data from project (create event triggered when room becomes active)"""
        self.object_data = object_data

        # Apply object-level visibility setting
        # If the object type has visible=False, make all instances of it invisible
        if not object_data.get('visible', True):
            self.visible = False

        # NOTE: Create event is NOT triggered here!
        # It's triggered when the room becomes active (in change_room)

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

    def __init__(self, name: str, room_data: dict):
        self.name = name
        self.width = room_data.get('width', 1024)
        self.height = room_data.get('height', 768)
        self.background_color = self.parse_color(room_data.get('background_color', '#87CEEB'))
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
        except Exception:
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
                # else: No sprite assigned - instance.sprite remains None
                # The render method will skip instances with no sprite

    def create_default_sprite_for_object(self, object_name: str) -> GameSprite:
        """Create a default sprite for an object"""
        # Generate color from object name hash for consistency
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
                logger.error(f"Invalid project path: {project_path}")
                return False

            if not project_file.exists():
                logger.error(f"Project file not found: {project_file}")
                return False

            # Load project data
            with open(project_file, 'r') as f:
                self.project_data = json.load(f)

            logger.info(f"Loaded project: {self.project_data.get('name', 'Untitled')}")

            # Only load rooms (without sprites for instances yet)
            self.load_rooms_without_sprites()

            return True

        except Exception as e:
            logger.error(f"Error loading project: {e}")
            import traceback
            traceback.print_exc()
            return False

    def load_sprites(self):
        """Load all sprites from the project (called after pygame.display is initialized)"""
        sprites_data = self.project_data.get('assets', {}).get('sprites', {})

        logger.info(f"Loading {len(sprites_data)} sprites...")

        for sprite_name, sprite_info in sprites_data.items():
            try:
                file_path = sprite_info.get('file_path', '')
                if file_path:
                    full_path = self.project_path / file_path
                    # Pass sprite_info to enable animation support
                    sprite = GameSprite(str(full_path), sprite_info)
                    self.sprites[sprite_name] = sprite
                    logger.debug(f"  ✅ Loaded sprite: {sprite_name} ({sprite.width}x{sprite.height})")
                else:
                    logger.warning(f"  Sprite {sprite_name} has no file path")
            except Exception as e:
                logger.error(f"  Error loading sprite {sprite_name}: {e}")

    def load_rooms_without_sprites(self):
        """Load rooms but don't assign sprites to instances yet"""
        rooms_data = self.project_data.get('assets', {}).get('rooms', {})

        logger.info(f"Loading {len(rooms_data)} rooms...")

        for room_name, room_info in rooms_data.items():
            try:
                room = GameRoom(room_name, room_info)
                # Don't set sprites yet - will do this after pygame.display is ready
                self.rooms[room_name] = room
                logger.info(f"  Loaded room: {room_name} ({len(room.instances)} instances)")
            except Exception as e:
                logger.error(f"  Error loading room {room_name}: {e}")
                import traceback
                traceback.print_exc()

    def assign_sprites_to_rooms(self):
        """Assign loaded sprites to room instances"""
        objects_data = self.project_data.get('assets', {}).get('objects', {})

        logger.info("Assigning sprites to room instances...")
        for room_name, room in self.rooms.items():
            room.set_sprites_for_instances(self.sprites, objects_data)

            # Count instances with sprites
            sprites_assigned = sum(1 for instance in room.instances if instance.sprite)
            logger.debug(f"  Room {room_name}: {sprites_assigned}/{len(room.instances)} instances have sprites")

    def find_starting_room(self) -> Optional[str]:
        """Find a room to start the game in - uses room_order if available"""
        if not self.rooms:
            return None

        # Use room_order from project data if available (first room in order)
        if self.project_data:
            room_order = self.project_data.get('room_order', [])
            if room_order:
                # Return first room in the order that actually exists
                for room_name in room_order:
                    if room_name in self.rooms:
                        return room_name

        # Fallback: just use the first room in the dictionary
        return list(self.rooms.keys())[0]

    def test_game(self, project_path: str) -> bool:
        """Test run the game from project"""
        logger.info(f"Testing game from project: {project_path}")

        # Load project data (but not sprites yet)
        if not self.load_project_data_only(project_path):
            logger.error("Failed to load project")
            return False

        # Find starting room
        starting_room = self.find_starting_room()
        if not starting_room:
            logger.error("No rooms found in project")
            return False

        logger.info(f"Starting with room: {starting_room}")
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

            logger.info(f"Game window: {self.window_width}x{self.window_height}")

            # NOW load sprites (after pygame.display is initialized)
            logger.info("🎮 Loading sprites after pygame.display initialization...")
            self.load_sprites()

            # Assign sprites to room instances
            self.assign_sprites_to_rooms()

            logger.debug(f"Current room: {self.current_room.name}")
            logger.debug(f"Room instances: {len(self.current_room.instances)}")

            # Count instances by type for summary
            instance_counts = {}
            for instance in self.current_room.instances:
                obj_name = instance.object_name
                instance_counts[obj_name] = instance_counts.get(obj_name, 0) + 1

            logger.debug("Instance summary:")
            for obj_name, count in sorted(instance_counts.items()):
                logger.debug(f"  {obj_name}: {count}")


            self.running = True

            # Main game loop
            while self.running:
                # Handle events
                self.handle_events()

                # Update (placeholder for game logic)
                self.update()

                # Execute step events for all instances
                for instance in self.current_room.instances:
                    instance.step()

                # Clear screen
                self.screen.fill((135, 206, 235))  # Sky blue

                # Render
                self.render()

                # Control framerate
                self.clock.tick(self.fps)

            return True

        except Exception as e:
            logger.error(f"Error in game loop: {e}")
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
                # Handle keyboard press events for all instances
                self.handle_keyboard_press(event.key)
            elif event.type == pygame.KEYUP:
                # Handle keyboard release events
                self.handle_keyboard_release(event.key)

    def handle_keyboard_press(self, key):
        """Handle keyboard press event"""
        if not self.current_room:
            return

        # Map pygame keys to sub-event keys used in IDE
        sub_key = self._get_key_name(key)
        if not sub_key:
            return

        logger.debug(f"⌨️  Key pressed: {sub_key}")

        # Helper to find key in dict (case-insensitive)
        def find_key_in_event(event_dict, key):
            if key in event_dict:
                return key
            upper_key = key.upper()
            if upper_key in event_dict:
                return upper_key
            return None

        # Execute keyboard event for all instances
        for instance in self.current_room.instances:
            if not instance.object_data:
                continue

            events = instance.object_data.get('events', {})

            # Check for keyboard_press parent event with sub-events
            if "keyboard_press" in events:
                keyboard_press_event = events["keyboard_press"]

                if isinstance(keyboard_press_event, dict):
                    found_key = find_key_in_event(keyboard_press_event, sub_key)
                    if found_key:
                        logger.debug(f"  ✅ Found keyboard_press.{found_key} for {instance.object_name}")
                        sub_event_data = keyboard_press_event[found_key]
                        if isinstance(sub_event_data, dict) and "actions" in sub_event_data:
                            actions = sub_event_data["actions"]
                            logger.debug(f"  → Executing {len(actions)} actions from keyboard_press.{found_key}")
                            for action_data in actions:
                                logger.debug(f"    - Action: {action_data.get('action', 'unknown')}")
                                instance.action_executor.execute_action(instance, action_data)

            # ALSO check for keyboard (held) event - might be used instead
            if "keyboard" in events:
                keyboard_event = events["keyboard"]

                if isinstance(keyboard_event, dict):
                    found_key = find_key_in_event(keyboard_event, sub_key)
                    if found_key:
                        logger.debug(f"  ✅ Found keyboard.{found_key} for {instance.object_name}")
                        sub_event_data = keyboard_event[found_key]
                        if isinstance(sub_event_data, dict) and "actions" in sub_event_data:
                            actions = sub_event_data["actions"]
                            logger.debug(f"  → Executing {len(actions)} actions from keyboard.{found_key}")
                            for action_data in actions:
                                logger.debug(f"    - Action: {action_data.get('action', 'unknown')}")
                                instance.action_executor.execute_action(instance, action_data)

    def handle_keyboard_release(self, key):
        """Handle keyboard release event - execute user-defined keyboard_release events"""
        if not self.current_room:
            return

        # Map pygame keys to sub-event keys
        sub_key = self._get_key_name(key)
        if not sub_key:
            return

        logger.debug(f"⌨️  Key released: {sub_key}")

        # Execute keyboard_release events for all instances
        for instance in self.current_room.instances:
            if not instance.object_data:
                continue

            events = instance.object_data.get('events', {})

            # Check for keyboard_release event with sub-events
            if "keyboard_release" in events:
                keyboard_release_event = events["keyboard_release"]

                # Helper to find key in dict (case-insensitive)
                def find_key_in_event(event_dict, key):
                    if key in event_dict:
                        return key
                    upper_key = key.upper()
                    if upper_key in event_dict:
                        return upper_key
                    return None

                if isinstance(keyboard_release_event, dict):
                    found_key = find_key_in_event(keyboard_release_event, sub_key)
                    if found_key:
                        logger.debug(f"  ✅ Executing keyboard_release.{found_key} for {instance.object_name}")
                        sub_event_data = keyboard_release_event[found_key]
                        if isinstance(sub_event_data, dict) and "actions" in sub_event_data:
                            for action_data in sub_event_data["actions"]:
                                instance.action_executor.execute_action(instance, action_data)

    def _get_key_name(self, key):
        """Map pygame key code to key name string"""
        # Arrow keys
        arrow_keys = {
            pygame.K_LEFT: "left",
            pygame.K_RIGHT: "right",
            pygame.K_UP: "up",
            pygame.K_DOWN: "down",
        }
        if key in arrow_keys:
            return arrow_keys[key]

        # Letter keys (a-z)
        if pygame.K_a <= key <= pygame.K_z:
            return chr(key)

        # Number keys (0-9)
        if pygame.K_0 <= key <= pygame.K_9:
            return chr(key)

        # Special keys
        special_keys = {
            pygame.K_SPACE: "space",
            pygame.K_RETURN: "enter",
            pygame.K_ESCAPE: "escape",
            pygame.K_TAB: "tab",
            pygame.K_BACKSPACE: "backspace",
            pygame.K_DELETE: "delete",
            pygame.K_INSERT: "insert",
            pygame.K_HOME: "home",
            pygame.K_END: "end",
            pygame.K_PAGEUP: "pageup",
            pygame.K_PAGEDOWN: "pagedown",
            pygame.K_F1: "f1",
            pygame.K_F2: "f2",
            pygame.K_F3: "f3",
            pygame.K_F4: "f4",
            pygame.K_F5: "f5",
            pygame.K_F6: "f6",
            pygame.K_F7: "f7",
            pygame.K_F8: "f8",
            pygame.K_F9: "f9",
            pygame.K_F10: "f10",
            pygame.K_F11: "f11",
            pygame.K_F12: "f12",
            pygame.K_LSHIFT: "shift",
            pygame.K_RSHIFT: "shift",
            pygame.K_LCTRL: "control",
            pygame.K_RCTRL: "control",
            pygame.K_LALT: "alt",
            pygame.K_RALT: "alt",
        }
        return special_keys.get(key)

    def update(self):
        """Update game logic"""
        if not self.current_room:
            return

        # Get objects data for solid checks
        objects_data = self.project_data.get('assets', {}).get('objects', {})

        # Check for room restart/transition flags FIRST
        for instance in self.current_room.instances:
            if hasattr(instance, 'restart_room_flag') and instance.restart_room_flag:
                logger.info("🔄 Restarting room...")
                self.restart_current_room()
                return

            if hasattr(instance, 'next_room_flag') and instance.next_room_flag:
                logger.info("➡️  Going to next room...")
                self.goto_next_room()
                return


        # Apply speed-based movement (hspeed, vspeed)
        for instance in self.current_room.instances:
            if hasattr(instance, 'hspeed') and instance.hspeed != 0:
                instance.x += instance.hspeed
            if hasattr(instance, 'vspeed') and instance.vspeed != 0:
                instance.y += instance.vspeed
        # Handle intended movement with collision checking
        for instance in self.current_room.instances:
            if hasattr(instance, 'intended_x') and hasattr(instance, 'intended_y'):
                # Check if movement would collide with solid objects
                can_move = self.check_movement_collision(instance, objects_data)

                if can_move:
                    logger.debug(f"✅ Movement allowed: {instance.object_name} → ({instance.intended_x}, {instance.intended_y})")
                    instance.x = instance.intended_x
                    instance.y = instance.intended_y
                else:
                    logger.debug(f"❌ Movement blocked: {instance.object_name} (hit solid object)")

                # Clear intended movement
                delattr(instance, 'intended_x')
                delattr(instance, 'intended_y')

        # Check collision events
        for instance in self.current_room.instances:
            self.check_collision_events(instance, objects_data)

        # Execute step events for all instances
        for instance in self.current_room.instances:
            instance.step()

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
        """Check if instance is colliding and trigger collision events"""
        if not instance.object_data:
            return

        events = instance.object_data.get('events', {})

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
                            logger.debug(f"💥 Collision: {instance.object_name} with {target_object}")
                            instance.action_executor.execute_event(instance, event_name, events)
                            break

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
        if not self.current_room:
            return

        room_list = self.get_room_list()
        if not room_list:
            return

        try:
            current_index = room_list.index(self.current_room.name)
            next_index = (current_index + 1) % len(room_list)
            next_room_name = room_list[next_index]
            self.change_room(next_room_name)
        except ValueError:
            logger.error(f"Current room '{self.current_room.name}' not in room list")

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
            logger.info(f"🚪 Changing to room: {room_name}")
            self.current_room = self.rooms[room_name]

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
        logger.debug("=== DEBUG INFO ===")
        logger.debug(f"Project: {self.project_data.get('name', 'Unknown')}")
        logger.debug(f"Current room: {self.current_room.name if self.current_room else 'None'}")

        if self.current_room:
            logger.debug(f"Room size: {self.current_room.width}x{self.current_room.height}")
            logger.debug(f"Background: {self.current_room.background_color}")
            logger.debug(f"Instances: {len(self.current_room.instances)}")

            for i, instance in enumerate(self.current_room.instances):
                sprite_info = "no sprite" if not instance.sprite else "sprite loaded"
                logger.debug(f"  {i+1}. {instance.object_name} at ({instance.x}, {instance.y}) - {sprite_info}")

        logger.debug("===================")

    def stop_game(self):
        """Stop the game"""
        logger.info("Stopping game...")
        self.running = False

    def run(self):
        """Run the game - main entry point called by IDE"""
        if not self.project_data:
            logger.error("❌ No project loaded. Cannot run game.")
            return False

        # Find starting room
        starting_room = self.find_starting_room()
        if not starting_room:
            logger.error("❌ No rooms found in project")
            return False

        logger.info(f"🎮 Starting game with room: {starting_room}")
        self.current_room = self.rooms[starting_room]

        # Set window size based on room
        self.window_width = self.current_room.width
        self.window_height = self.current_room.height

        # Run the game loop
        return self.run_game_loop()

    def cleanup(self):
        """Clean up pygame resources"""
        try:
            if pygame.get_init():
                pygame.quit()
            logger.info("Game cleanup complete")
        except Exception as e:
            logger.error(f"Error during cleanup: {e}")

# Test function
def test_runner():
    """Test the enhanced game runner"""
    runner = GameRunner()

    # Test with a project path - replace with actual path
    test_project = "/path/to/your/project"

    if Path(test_project).exists():
        runner.test_game(test_project)
    else:
        logger.error(f"Test project not found: {test_project}")
        logger.info("Please update the test_project path")

if __name__ == "__main__":
    test_runner()
