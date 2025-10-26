#!/usr/bin/env python3
"""
Kivy Exporter for PyGameMaker IDE
Exports projects to Kivy format for mobile deployment
"""

import os
import json
import shutil
from pathlib import Path
from typing import Dict, List, Any, Optional


class KivyExporter:
    """Export PyGameMaker projects to Kivy format"""
    
    def __init__(self, project_data: Dict[str, Any], project_path: Path, output_path: Path):
        self.project_data = project_data
        self.project_path = Path(project_path)
        self.output_path = Path(output_path)
        self.grid_size = 32  # Default grid size for snapping
        
    def export(self) -> bool:
        """Export project to Kivy format"""
        try:
            
            print("=" * 60)
            print("Starting Kivy Export")
            print("=" * 60)
            
            # Diagnostic output
            print("\n📊 Project Data Diagnostic:")
            print(f"  Project name: {self.project_data.get('name', 'Unknown')}")
            print(f"  Output path: {self.output_path}")
            print(f"  Project path: {self.project_path}")
            
            assets = self.project_data.get('assets', {})
            print(f"\n📦 Assets found:")
            for asset_type, asset_dict in assets.items():
                print(f"  - {asset_type}: {len(asset_dict)} items")
                if asset_type in ['rooms', 'objects']:
                    for name in asset_dict.keys():
                        print(f"    • {name}")
                        # Show event info for objects
                        if asset_type == 'objects':
                            obj_data = asset_dict[name]
                            if isinstance(obj_data, dict):
                                events = obj_data.get('events', [])
                                if events:
                                    if isinstance(events, list):
                                        print(f"      └─ {len(events)} event(s)")
                                    elif isinstance(events, dict):
                                        print(f"      └─ {len(events)} event(s) in dict (keys: {list(events.keys())[:3]}...)")
                                    else:
                                        print(f"      └─ events is {type(events).__name__} (expected list or dict)")
            
            print()
            
            # Create directory structure
            self._create_directory_structure()
            print("✓ Directory structure created")
            
            # Export assets
            self._export_assets()
            print(f"✓ Exported {self._count_assets()} asset(s)")
            
            # Generate main application
            self._generate_main_app()
            print("✓ Main application generated")
            
            # Generate game scenes/rooms
            self._generate_scenes()
            print(f"✓ Generated {len(self.project_data.get('assets', {}).get('rooms', {}))} room(s)")
            
            # Generate object classes
            self._generate_objects()
            print(f"✓ Generated {len(self.project_data.get('assets', {}).get('objects', {}))} object type(s)")
            
            # Generate utility files
            self._generate_utils()
            print("✓ Game logic utilities generated")
            
            # Generate build configuration
            self._generate_buildozer_spec()
            print("✓ Buildozer spec generated")
            
            # Generate requirements file
            self._generate_requirements()
            print("✓ Requirements file generated")
            
            # Generate README
            self._generate_readme()
            print("✓ README created")
            
            print("=" * 60)
            print("Export completed successfully!")
            print("=" * 60)
            
            return True
            
        except Exception as e:
            print(f"✗ Export failed: {e}")
            import traceback
            traceback.print_exc()
            return False
    
    def _create_directory_structure(self):
        """Create the output directory structure"""
        dirs = [
            self.output_path / "game",
            self.output_path / "game" / "assets",
            self.output_path / "game" / "assets" / "images",
            self.output_path / "game" / "assets" / "sounds",
            self.output_path / "game" / "objects",
            self.output_path / "game" / "scenes",
        ]
        
        for dir_path in dirs:
            dir_path.mkdir(parents=True, exist_ok=True)
            print(f"  Created: {dir_path}")
        
        # Create __init__.py files to make directories Python packages
        package_dirs = [
            self.output_path / "game" / "objects",
            self.output_path / "game" / "scenes",
        ]
        
        for pkg_dir in package_dirs:
            init_file = pkg_dir / "__init__.py"
            init_file.write_text("# Auto-generated package file\n")
            print(f"  Created: {init_file}")
    
    def _count_assets(self) -> int:
        """Count total number of assets"""
        count = 0
        assets = self.project_data.get('assets', {})
        for asset_type in ['sprites', 'sounds', 'backgrounds']:
            count += len(assets.get(asset_type, {}))
        return count
    
    def _export_assets(self):
        """Export all game assets"""
        assets = self.project_data.get('assets', {})
        
        # Export sprites
        for sprite_name, sprite_data in assets.get('sprites', {}).items():
            self._export_sprite(sprite_name, sprite_data)
        
        # Export sounds
        for sound_name, sound_data in assets.get('sounds', {}).items():
            self._export_sound(sound_name, sound_data)
        
        # Export backgrounds
        for bg_name, bg_data in assets.get('backgrounds', {}).items():
            self._export_background(bg_name, bg_data)
    
    def _export_sprite(self, name: str, data: Dict):
        """Export a sprite asset"""
        file_path = data.get('file_path', '')
        if file_path:
            src = self.project_path / file_path
            if src.exists():
                dst = self.output_path / "game" / "assets" / "images" / src.name
                shutil.copy2(src, dst)
    
    def _export_sound(self, name: str, data: Dict):
        """Export a sound asset"""
        file_path = data.get('file_path', '')
        if file_path:
            src = self.project_path / file_path
            if src.exists():
                dst = self.output_path / "game" / "assets" / "sounds" / src.name
                shutil.copy2(src, dst)
    
    def _export_background(self, name: str, data: Dict):
        """Export a background asset"""
        file_path = data.get('file_path', '')
        if file_path:
            src = self.project_path / file_path
            if src.exists():
                dst = self.output_path / "game" / "assets" / "images" / src.name
                shutil.copy2(src, dst)
    
    def _generate_main_app(self):
        """Generate the main Kivy application file"""
        settings = self.project_data.get('settings', {})
        rooms = self.project_data.get('assets', {}).get('rooms', {})
        
        # Get first room as starting room
        first_room = next(iter(rooms.keys())) if rooms else "room0"
        
        # Get room dimensions
        room_data = rooms.get(first_room, {})
        room_width = room_data.get('width', 640)
        room_height = room_data.get('height', 480)
        
        code = f'''#!/usr/bin/env python3
"""
Generated Kivy Game Application
Exported from PyGameMaker IDE
"""

from kivy.app import App
from kivy.uix.widget import Widget
from kivy.core.window import Window
from kivy.clock import Clock
from kivy.graphics import Rectangle, Color
from kivy.core.image import Image as CoreImage
import os

# Import game scenes
from scenes.{first_room} import {self._get_room_class_name(first_room)}


class GameApp(App):
    """Main game application"""
    
    def build(self):
        """Build the application"""
        # Set window properties to match room size
        Window.size = ({room_width}, {room_height})
        Window.clearcolor = (0, 0, 0, 1)
        
        # Create and return the starting scene
        self.scene = {self._get_room_class_name(first_room)}()
        
        # Schedule game loop at maximum frame rate for smoothest movement
        # Using 1/60 to maintain 60 FPS game logic
        Clock.schedule_interval(self.scene.update, 1.0 / 60.0)
        
        return self.scene
    
    def on_stop(self):
        """Cleanup when app stops"""
        Clock.unschedule(self.scene.update)
        return True


if __name__ == '__main__':
    GameApp().run()
'''
        
        output_file = self.output_path / "game" / "main.py"
        output_file.write_text(code)
    
    def _generate_scenes(self):
        """Generate scene files for each room"""
        rooms = self.project_data.get('assets', {}).get('rooms', {})
        
        if not rooms:
            print("  Warning: No rooms found in project data")
            return
        
        for room_name, room_data in rooms.items():
            try:
                print(f"  Generating scene: {room_name}")
                self._generate_scene(room_name, room_data)
                print(f"  ✓ Scene {room_name} generated")
            except Exception as e:
                print(f"  ✗ Failed to generate scene {room_name}: {e}")
                import traceback
                traceback.print_exc()
    
    def _generate_scene(self, room_name: str, room_data: Dict):
        """Generate a single scene file"""
        class_name = self._get_room_class_name(room_name)
        
        # Get room properties
        width = room_data.get('width', 1024)
        height = room_data.get('height', 768)
        instances = room_data.get('instances', [])
        
        # Import statements for object types used in this room
        object_imports = set()
        
        print(f"    Room has {len(instances)} instances")
        if instances and len(instances) > 0:
            # Debug: show structure of first instance
            first_inst = instances[0]
            print(f"    First instance keys: {list(first_inst.keys()) if isinstance(first_inst, dict) else 'not a dict'}")
            print(f"    First instance sample: {first_inst}")
        
        for instance in instances:
            # Try multiple possible key names for object type
            obj_type = (instance.get('object_type') or 
                       instance.get('object_name') or
                       instance.get('type') or
                       instance.get('object') or
                       instance.get('obj_type') or
                       '')
            
            if obj_type:
                object_imports.add(obj_type)
                print(f"      Found object type: {obj_type}")
        
        print(f"    Total unique object types: {len(object_imports)}")
        
        import_lines = '\n'.join([
            f"from objects.{obj} import {self._get_object_class_name(obj)}"
            for obj in sorted(object_imports)
        ])
        
        # Generate instance creation code
        instance_code = []
        for i, instance in enumerate(instances):
            # Try multiple possible key names for object type
            obj_type = (instance.get('object_type') or 
                       instance.get('object_name') or
                       instance.get('type') or
                       instance.get('object') or
                       instance.get('obj_type') or
                       '')
            x = instance.get('x', 0)
            y = instance.get('y', 0)
            
            if obj_type:
                class_name_obj = self._get_object_class_name(obj_type)
                instance_code.append(
                    f"        inst_{i} = {class_name_obj}(self, {x}, {y})"
                )
                instance_code.append(
                    f"        self.add_instance(inst_{i})"
                )
        
        instances_init = '\n'.join(instance_code) if instance_code else "        pass"
        
        code = f'''#!/usr/bin/env python3
"""
Scene: {room_name}
Generated from PyGameMaker IDE
"""

from kivy.uix.widget import Widget
from kivy.graphics import Rectangle, Color
from kivy.core.window import Window
from utils import load_image

# Import object types
{import_lines}


class {class_name}(Widget):
    """Game scene for {room_name}"""
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        
        self.room_width = {width}
        self.room_height = {height}
        self.instances = []
        self.instances_to_destroy = []
        
        # Keyboard state tracking
        self.keys_pressed = {{}}
        
        # Bind keyboard events
        Window.bind(on_keyboard=self.on_keyboard)
        Window.bind(on_key_up=self.on_keyboard_up)
        
        # Initialize room
        self.create_instances()
    
    def create_instances(self):
        """Create all instances in the room"""
{instances_init}
    
    def add_instance(self, instance):
        """Add an instance to the room"""
        self.instances.append(instance)
        self.add_widget(instance)
        
        # Call create event
        if hasattr(instance, 'on_create'):
            instance.on_create()
    
    def remove_instance(self, instance):
        """Remove an instance from the room"""
        if instance in self.instances:
            self.instances.remove(instance)
            if instance in self.children:
                self.remove_widget(instance)
    
    def update(self, dt):
        """Main game loop update"""
        # Update all instances
        for instance in self.instances[:]:
            if hasattr(instance, 'on_update'):
                instance.on_update(dt)
        
        # Process movement
        for instance in self.instances[:]:
            if hasattr(instance, '_process_movement'):
                instance._process_movement(dt)
        
        # Check collisions
        for instance in self.instances[:]:
            if hasattr(instance, '_check_collisions'):
                instance._check_collisions(self.instances)
        
        # Remove destroyed instances
        for instance in self.instances_to_destroy:
            self.remove_instance(instance)
        self.instances_to_destroy.clear()
    
    def destroy_instance(self, instance):
        """Mark instance for destruction"""
        if instance not in self.instances_to_destroy:
            self.instances_to_destroy.append(instance)
    
    def on_keyboard(self, window, key, scancode, codepoint, modifier):
        """Handle keyboard press events"""
        self.keys_pressed[key] = True
        
        # Notify all instances
        for instance in self.instances:
            if hasattr(instance, 'on_keyboard'):
                instance.on_keyboard(key, scancode, codepoint, modifier)
        
        return False
    
    def on_keyboard_up(self, window, key, scancode):
        """Handle keyboard release events"""
        if key in self.keys_pressed:
            del self.keys_pressed[key]
        
        # Notify all instances
        for instance in self.instances:
            if hasattr(instance, 'on_keyboard_up'):
                instance.on_keyboard_up(key, scancode)
        
        return False
'''
        
        output_file = self.output_path / "game" / "scenes" / f"{room_name}.py"
        output_file.write_text(code)
    
    def _generate_objects(self):
        """Generate object class files"""
        # First generate base object class
        try:
            print("  Generating base object class...")
            self._generate_base_object()
            print("  ✓ Base object generated")
        except Exception as e:
            print(f"  ✗ Failed to generate base object: {e}")
            import traceback
            traceback.print_exc()
            return
        
        # Then generate specific object types
        objects = self.project_data.get('assets', {}).get('objects', {})
        
        if not objects:
            print("  Warning: No objects found in project data")
            return
        
        for obj_name, obj_data in objects.items():
            try:
                print(f"  Generating object: {obj_name}")
                self._generate_object(obj_name, obj_data)
                print(f"  ✓ Object {obj_name} generated")
            except Exception as e:
                print(f"  ✗ Failed to generate object {obj_name}: {e}")
                import traceback
                traceback.print_exc()
    
    def _generate_base_object(self):
        """Generate the base GameObject class"""
        code = f'''#!/usr/bin/env python3
"""
Base GameObject class
GameMaker-style base object with movement and collision
"""

from kivy.uix.widget import Widget
from kivy.graphics import Rectangle, Color
from kivy.core.image import Image as CoreImage
import math
from utils import load_image


class GameObject(Widget):
    """Base class for all game objects"""
    
    def __init__(self, scene, x=0, y=0, **kwargs):
        super().__init__(**kwargs)
        
        self.scene = scene
        # Use float for sub-pixel precision (smooth movement)
        self.x = float(x)
        self.y = float(y)
        
        # Movement properties (GameMaker style)
        self.hspeed = 0.0  # Horizontal speed (float for smooth movement)
        self.vspeed = 0.0  # Vertical speed (float for smooth movement)
        self.speed = 0.0   # Movement speed (magnitude)
        self.direction = 0  # Movement direction in degrees
        self.friction = 0
        self.gravity = 0
        self.gravity_direction = 270
        
        # Physics properties
        self.solid = False
        
        # Sprite properties
        self.sprite_name = None
        self.image = None
        self.image_width = 0
        self.image_height = 0
        
        # Collision tracking
        self._collision_other = None
        
        # Grid properties
        self.grid_size = {self.grid_size}
        
        self.size = (32, 32)  # Default size
        self.pos = (x, y)
        
        with self.canvas:
            Color(1, 1, 1, 1)
            self.rect = Rectangle(pos=self.pos, size=self.size)
    
    def set_sprite(self, sprite_path):
        """Set the object's sprite"""
        self.sprite_name = sprite_path
        img = load_image(sprite_path)
        
        if img:
            self.image = img
            self.image_width = img.width
            self.image_height = img.height
            self.size = (img.width, img.height)
            
            # Update canvas
            self.canvas.clear()
            with self.canvas:
                Color(1, 1, 1, 1)
                self.rect = Rectangle(texture=img.texture, pos=self.pos, size=self.size)
    
    def _process_movement(self, dt):
        """Process movement with delta time for smooth, frame-independent motion"""
        # Speed scaling factor - adjust this to tune overall game speed
        # 240 = 4x speed (matches GameMaker behavior)
        # 120 = 2x speed, 60 = 1x speed, 480 = 8x speed
        SPEED_SCALE = 60
        
        # Apply speed/direction if set
        if self.speed != 0:
            rad = math.radians(self.direction)
            self.hspeed = self.speed * math.cos(rad)
            self.vspeed = -self.speed * math.sin(rad)
        
        # Apply gravity
        if self.gravity != 0:
            grav_rad = math.radians(self.gravity_direction)
            self.hspeed += self.gravity * math.cos(grav_rad)
            self.vspeed += -self.gravity * math.sin(grav_rad)
        
        # Apply friction
        if self.friction != 0:
            if abs(self.hspeed) > self.friction:
                self.hspeed -= self.friction if self.hspeed > 0 else -self.friction
            else:
                self.hspeed = 0.0
                
            if abs(self.vspeed) > self.friction:
                self.vspeed -= self.friction if self.vspeed > 0 else -self.friction
            else:
                self.vspeed = 0.0
        
        # Only move if there's actual speed
        if self.hspeed == 0 and self.vspeed == 0:
            return
        
        # Update position with delta time for smooth, frame-independent movement
        new_x = self.x + float(self.hspeed * dt * SPEED_SCALE)
        new_y = self.y + float(self.vspeed * dt * SPEED_SCALE)
        
        # Check for collisions before moving
        can_move = True
        if self.solid:
            # Check collision at new position
            old_x, old_y = self.x, self.y
            self.x, self.y = new_x, new_y
            
            for other in self.scene.instances:
                if other != self and other.solid:
                    if self.check_collision(other):
                        can_move = False
                        break
            
            if not can_move:
                self.x, self.y = old_x, old_y
            else:
                self._update_position()
        else:
            self.x = new_x
            self.y = new_y
            self._update_position()
    
    def _update_position(self):
        """Update visual position with sub-pixel precision for smooth rendering"""
        # Keep float precision for smooth movement
        self.pos = (float(self.x), float(self.y))
        if hasattr(self, 'rect'):
            self.rect.pos = self.pos
            # Force canvas update for smooth rendering
            self.canvas.ask_update()
    
    def check_collision(self, other):
        """Check AABB collision with another object"""
        return (
            self.x < other.x + other.size[0] and
            self.x + self.size[0] > other.x and
            self.y < other.y + other.size[1] and
            self.y + self.size[1] > other.y
        )
    
    def _check_collisions(self, instances):
        """Check collisions with all other instances"""
        for other in instances:
            if other != self and self.check_collision(other):
                self._collision_other = other
                
                # Call collision event
                collision_event = f"on_collision_{{other.__class__.__name__.lower()}}"
                if hasattr(self, collision_event):
                    getattr(self, collision_event)(other)
    
    def destroy(self):
        """Destroy this instance"""
        if hasattr(self, 'on_destroy'):
            self.on_destroy()
        self.scene.destroy_instance(self)
    
    def is_on_grid(self):
        """Check if object is aligned to grid"""
        return (self.x % self.grid_size == 0 and 
                self.y % self.grid_size == 0)
    
    def snap_to_grid(self):
        """Snap object to nearest grid position"""
        self.x = round(self.x / self.grid_size) * self.grid_size
        self.y = round(self.y / self.grid_size) * self.grid_size
        self._update_position()
    
    def stop_movement(self):
        """Stop all movement"""
        self.hspeed = 0
        self.vspeed = 0
        self.speed = 0
    
    # Event handlers (to be overridden by subclasses)
    def on_create(self):
        """Called when instance is created"""
        pass
    
    def on_update(self, dt):
        """Called each frame"""
        pass
    
    def on_destroy(self):
        """Called when instance is destroyed"""
        pass
    
    def on_keyboard(self, key, scancode, codepoint, modifier):
        """Called when a key is pressed"""
        pass
    
    def on_keyboard_up(self, key, scancode):
        """Called when a key is released"""
        pass
'''
        
        output_file = self.output_path / "game" / "objects" / "base_object.py"
        output_file.write_text(code)
    
    def _generate_object(self, obj_name: str, obj_data: Dict):
        """Generate a specific object class"""
        class_name = self._get_object_class_name(obj_name)
        
        # Get object properties
        sprite_name = obj_data.get('sprite', '')
        solid = obj_data.get('solid', False)
        visible = obj_data.get('visible', True)
        persistent = obj_data.get('persistent', False)
        
        # Get sprite file path if sprite is set
        sprite_path = ""
        if sprite_name:
            sprites = self.project_data.get('assets', {}).get('sprites', {})
            if sprite_name in sprites:
                sprite_file = sprites[sprite_name].get('file_path', '')
                if sprite_file:
                    sprite_path = f"assets/images/{Path(sprite_file).name}"
        
        # Generate event handlers from object's events
        events = obj_data.get('events', [])
        
        print(f"    Raw events for {obj_name}: {type(events).__name__}")
        
        # Handle different event storage formats
        if isinstance(events, dict):
            # Events stored as dict/OrderedDict - convert to list
            print(f"    Converting events dict to list for {obj_name}")
            print(f"    Event keys in dict: {list(events.keys())}")
            events_list = []
            for event_key, event_data in events.items():
                print(f"      Processing event '{event_key}': {type(event_data).__name__}")
                if isinstance(event_data, dict):
                    print(f"        Event data keys: {list(event_data.keys())}")
                    
                    # Special handling for keyboard events
                    if event_key == 'keyboard':
                        # Keyboard events have sub-events for each key
                        # Each key (right, left, up, down) has its own actions
                        for key_name, key_data in event_data.items():
                            if isinstance(key_data, dict) and 'actions' in key_data:
                                # Create a keyboard event for this specific key
                                key_event = {
                                    'event_type': 'keyboard',
                                    'key_name': key_name,
                                    'actions': key_data.get('actions', []),
                                }
                                events_list.append(key_event)
                                print(f"        Added keyboard sub-event for '{key_name}' with {len(key_event['actions'])} actions")
                    else:
                        # Regular event - add the event type if not present
                        if 'event_type' not in event_data:
                            event_data['event_type'] = event_key
                        events_list.append(event_data)
                        actions_count = len(event_data.get('actions', []))
                        print(f"        Added event with type: {event_data.get('event_type')} ({actions_count} actions)")
                elif isinstance(event_data, list):
                    # Event data is already a list of event dicts
                    print(f"        Event data is a list with {len(event_data)} items")
                    for evt in event_data:
                        if isinstance(evt, dict):
                            if 'event_type' not in evt:
                                evt['event_type'] = event_key
                            events_list.append(evt)
                else:
                    print(f"        Warning: Skipping event '{event_key}' - data is {type(event_data).__name__}")
            events = events_list
            print(f"    Final events list has {len(events)} event(s)")
        elif not isinstance(events, list):
            print(f"    Warning: events for {obj_name} is {type(events).__name__}, converting to empty list")
            events = []
        
        # Show what events we're working with
        if events:
            print(f"    Processing {len(events)} event(s):")
            for i, evt in enumerate(events[:3]):  # Show first 3
                if isinstance(evt, dict):
                    print(f"      Event {i}: type={evt.get('event_type')}, actions={len(evt.get('actions', []))}")
        
        event_methods = self._generate_event_methods(obj_name, events)
        
        code = f'''#!/usr/bin/env python3
"""
Object: {obj_name}
Generated from PyGameMaker IDE
"""

from objects.base_object import GameObject
from kivy.core.window import Window


class {class_name}(GameObject):
    """Game object: {obj_name}"""
    
    def __init__(self, scene, x=0, y=0, **kwargs):
        super().__init__(scene, x, y, **kwargs)
        
        self.solid = {solid}
        self.visible = {visible}
        self.persistent = {persistent}
        
        # Set sprite
        {"self.set_sprite('" + sprite_path + "')" if sprite_path else "pass"}
    
{event_methods}
'''
        
        output_file = self.output_path / "game" / "objects" / f"{obj_name}.py"
        output_file.write_text(code)
    
    def _generate_event_methods(self, obj_name: str, events: List[Dict]) -> str:
        """Generate event handler methods from event data"""
        methods = []
        
        print(f"    _generate_event_methods called with {len(events)} events")
        
        # Filter out any non-dict events (malformed data)
        valid_events = []
        for i, event in enumerate(events):
            if isinstance(event, dict):
                print(f"      Event {i}: {event.get('event_type', 'unknown')} (key: {event.get('key_name', 'N/A')}) with {len(event.get('actions', []))} actions")
                valid_events.append(event)
            else:
                print(f"      Warning: Skipping malformed event in {obj_name}: {type(event).__name__}")
        
        events = valid_events
        
        if not events:
            print(f"      No valid events found, returning pass")
            return "    pass\n"
        
        # Group keyboard events together
        keyboard_events = [e for e in events if e.get('event_type') == 'keyboard' and e.get('key_name')]
        other_events = [e for e in events if not (e.get('event_type') == 'keyboard' and e.get('key_name'))]
        
        # Generate consolidated keyboard handler if there are keyboard events
        if keyboard_events:
            print(f"      Generating consolidated keyboard handler for {len(keyboard_events)} key(s)")
            keyboard_method = self._generate_keyboard_handler(keyboard_events)
            methods.append(keyboard_method)
        
        # Generate other event handlers
        for event in other_events:
            event_type = event.get('event_type', '')
            actions = event.get('actions', [])
            
            if not actions:
                continue
            
            # Map event types to method names
            method_name = self._get_event_method_name(event)
            if not method_name:
                continue
            
            # Generate method signature
            if event_type == 'keyboard':
                params = "self, key, scancode, codepoint, modifier"
            elif event_type == 'keyboard_up':
                params = "self, key, scancode"
            elif event_type == 'collision' or event_type.startswith('collision_with_'):
                params = "self, other"
            elif event_type in ['step', 'draw']:
                params = "self, dt"
            else:
                params = "self"
            
            # Generate action code
            action_code = self._generate_action_code(obj_name, actions, event)
            
            method = f'''    def {method_name}({params}):
        """Event handler: {event_type}"""
{action_code}
'''
            methods.append(method)
        
        return '\n'.join(methods) if methods else "    pass\n"
    
    def _generate_keyboard_handler(self, keyboard_events: List[Dict]) -> str:
        """Generate a consolidated keyboard handler for all key-specific events"""
        # Map key names to Kivy key codes
        key_map = {
            'right': '275',  # Kivy.core.window.Keyboard.keycodes['right']
            'left': '276',
            'up': '273',
            'down': '274',
        }
        
        code_lines = []
        code_lines.append("    def on_keyboard(self, key, scancode, codepoint, modifier):")
        code_lines.append('        """Handle keyboard press events"""')
        
        # Generate if/elif chain for each key
        for i, event in enumerate(keyboard_events):
            key_name = event.get('key_name', '')
            actions = event.get('actions', [])
            key_code = key_map.get(key_name, '0')
            
            if_keyword = "if" if i == 0 else "elif"
            code_lines.append(f"        {if_keyword} key == {key_code}:  # {key_name}")
            
            # Generate action code for this key
            if actions:
                from export.Kivy.action_converter import ActionConverter
                converter = ActionConverter()
                action_code = converter.convert_actions(actions, indent_level=3)
                code_lines.append(action_code)
            else:
                code_lines.append("            pass")
        
        return '\n'.join(code_lines)
    
    def _get_event_method_name(self, event: Dict) -> str:
        """Get the method name for an event"""
        event_type = event.get('event_type', '')
        
        # Handle collision events with specific format: collision_with_obj_name
        if event_type.startswith('collision_with_'):
            # Extract object name from collision_with_obj_name
            collision_obj = event_type.replace('collision_with_', '')
            return f"on_collision_{collision_obj.lower()}"
        
        # Map event types to method names
        event_map = {
            'create': 'on_create',
            'step': 'on_update',
            'destroy': 'on_destroy',
            'keyboard': 'on_keyboard',
            'keyboard_up': 'on_keyboard_up',
            'draw': 'on_draw',
        }
        
        if event_type == 'collision':
            collision_obj = event.get('collision_object', 'object')
            return f"on_collision_{collision_obj.lower()}"
        
        return event_map.get(event_type, '')
    
    def _generate_action_code(self, obj_name: str, actions: List[Dict], event: Dict) -> str:
        """Generate Python code from action list"""
        lines = []
        indent = "        "
        
        event_type = event.get('event_type', '')
        
        print(f"        _generate_action_code: {len(actions)} actions for event {event_type}")
        
        for i, action in enumerate(actions):
            print(f"          Action {i}: {type(action).__name__}")
            if isinstance(action, dict):
                print(f"            Keys: {list(action.keys())}")
                action_type = action.get('action_type', action.get('action', ''))
                print(f"            Type: '{action_type}'")
            elif isinstance(action, str):
                print(f"            String action: '{action[:80]}'")
            
            if isinstance(action, dict):
                action_type = action.get('action_type', action.get('action', ''))
                params = action.get('parameters', {})
                
                # Check if this is a complex/conditional action that needs the full ActionConverter
                complex_actions = ['if_on_grid', 'if_collision', 'if_key_pressed', 'repeat', 'while']
                
                if action_type in complex_actions:
                    # Use ActionConverter for complex actions
                    print(f"            Using ActionConverter for complex action '{action_type}'")
                    from export.Kivy.action_converter import ActionConverter
                    converter = ActionConverter()
                    # Convert the action dict format to what ActionConverter expects
                    action_code = converter._convert_single_action(action, 2)
                    if action_code and action_code.strip():
                        lines.append(action_code)
                    else:
                        print(f"            Warning: ActionConverter returned empty code for '{action_type}'")
                        lines.append(indent + "pass")
                else:
                    # Use simple conversion for basic actions
                    code_line = self._convert_action_to_code(action_type, params, event_type)
                    if code_line:
                        lines.append(indent + code_line)
                    else:
                        print(f"            Warning: No code generated for action type '{action_type}'")
                        lines.append(indent + "pass")
            elif isinstance(action, str):
                # String action - use ActionConverter
                if action.strip():  # Only process non-empty strings
                    from export.Kivy.action_converter import ActionConverter
                    converter = ActionConverter()
                    action_code = converter.convert_actions(action, indent_level=2)
                    if action_code.strip():
                        lines.append(action_code)
        
        # CRITICAL: Always return valid Python code with at least 'pass'
        if not lines:
            print(f"          Warning: No code generated for event {event_type}, using 'pass'")
            return indent + "pass"
        
        return '\n'.join(lines)
    
    def _convert_action_to_code(self, action_type: str, params: Dict, event_type: str) -> str:
        """Convert a single action to Python code"""
        
        # Movement actions
        if action_type == 'set_hspeed':
            return f"self.hspeed = {params.get('value', 0)}"
        
        elif action_type == 'set_vspeed':
            return f"self.vspeed = {params.get('value', 0)}"
        
        elif action_type == 'set_speed':
            return f"self.speed = {params.get('value', 0)}"
        
        elif action_type == 'set_direction':
            return f"self.direction = {params.get('value', 0)}"
        
        elif action_type == 'stop_movement':
            return "self.stop_movement()"
        
        elif action_type == 'snap_to_grid':
            return "self.snap_to_grid()"
        
        # Conditional actions
        elif action_type == 'if_on_grid':
            return "if self.is_on_grid():"
        
        elif action_type == 'stop_if_no_keys':
            return "if not self.scene.keys_pressed: self.stop_movement()"
        
        # Instance actions
        elif action_type == 'destroy_instance':
            target = params.get('target', 'self')
            if target == 'other' and event_type == 'collision':
                return "other.destroy()"
            else:
                return "self.destroy()"
        
        # Keyboard checks
        elif action_type == 'check_key':
            key_code = params.get('key', 0)
            return f"if {key_code} in self.scene.keys_pressed:"
        
        # Default: return comment for unsupported action
        return f"# TODO: Implement {action_type}"
    
    def _generate_utils(self):
        """Generate utility functions file"""
        code = '''#!/usr/bin/env python3
"""
Game Utility Functions
Helper functions for the game
"""

from kivy.core.image import Image as CoreImage
import os


_image_cache = {}


def load_image(path):
    """Load an image with caching"""
    if path in _image_cache:
        return _image_cache[path]
    
    try:
        if os.path.exists(path):
            img = CoreImage(path)
            _image_cache[path] = img
            return img
    except Exception as e:
        print(f"Failed to load image {path}: {e}")
    
    return None


def clear_image_cache():
    """Clear the image cache"""
    global _image_cache
    _image_cache.clear()
'''
        
        output_file = self.output_path / "game" / "utils.py"
        output_file.write_text(code)
    
    def _generate_buildozer_spec(self):
        """Generate buildozer.spec for Android builds"""
        project_name = self.project_data.get('name', 'MyGame')
        
        spec = f'''[app]
title = {project_name}
package.name = {project_name.lower().replace(' ', '')}
package.domain = org.pygamemaker

source.dir = ./game
source.include_exts = py,png,jpg,wav,mp3,ogg

version = 1.0

requirements = python3,kivy

orientation = landscape
fullscreen = 1

[buildozer]
log_level = 2
warn_on_root = 1
'''
        
        output_file = self.output_path / "buildozer.spec"
        output_file.write_text(spec)
    
    def _generate_requirements(self):
        """Generate requirements.txt"""
        requirements = '''kivy>=2.1.0
'''
        
        output_file = self.output_path / "requirements.txt"
        output_file.write_text(requirements)
    
    def _generate_readme(self):
        """Generate README with instructions"""
        project_name = self.project_data.get('name', 'MyGame')
        
        readme = f'''# {project_name}

Exported from PyGameMaker IDE

## Running the Game

### Desktop (Linux/Mac/Windows)

1. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

2. Run the game:
   ```bash
   cd game
   python3 main.py
   ```

### Android

1. Install Buildozer:
   ```bash
   pip install buildozer
   ```

2. Build APK:
   ```bash
   buildozer android debug
   ```

3. The APK will be in `bin/` directory

## Controls

Use arrow keys or WASD for movement.

## Project Structure

- `game/` - Main game code
  - `main.py` - Application entry point
  - `utils.py` - Utility functions
  - `objects/` - Game object classes
  - `scenes/` - Game scenes/rooms
  - `assets/` - Game assets (images, sounds)
- `buildozer.spec` - Android build configuration
- `requirements.txt` - Python dependencies

## Notes

This game was created with PyGameMaker IDE, a GameMaker-inspired
game development environment for Python.
'''
        
        output_file = self.output_path / "README.md"
        output_file.write_text(readme)
    
    def _get_room_class_name(self, room_name: str) -> str:
        """Convert room name to class name"""
        # Convert snake_case to PascalCase
        return ''.join(word.capitalize() for word in room_name.split('_'))
    
    def _get_object_class_name(self, obj_name: str) -> str:
        """Convert object name to class name"""
        # Convert snake_case to PascalCase
        return ''.join(word.capitalize() for word in obj_name.split('_'))


def export_to_kivy(project_data: Dict[str, Any], project_path: Path, 
                   output_path: Path) -> bool:
    """
    Export a PyGameMaker project to Kivy format
    
    Args:
        project_data: Project data dictionary
        project_path: Path to project directory
        output_path: Output directory for export
        
    Returns:
        True if export successful, False otherwise
    """
    exporter = KivyExporter(project_data, project_path, output_path)
    return exporter.export()
