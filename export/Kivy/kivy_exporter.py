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


from export.Kivy.code_generator import ActionCodeGenerator

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
        project_name = self.project_data.get('name', 'Game')

        # Get first room as starting room
        room_names = list(rooms.keys())
        first_room = room_names[0] if room_names else "room0"

        # Get room dimensions
        room_data = rooms.get(first_room, {})
        room_width = room_data.get('width', 640)
        room_height = room_data.get('height', 480)

        # Generate imports for all rooms
        room_imports = []
        room_class_map = {}
        for room_name in room_names:
            class_name = self._get_room_class_name(room_name)
            room_imports.append(f"from scenes.{room_name} import {class_name}")
            room_class_map[room_name] = class_name

        room_imports_str = '\n'.join(room_imports)

        # Generate room list for navigation
        room_list_str = ', '.join([f'"{name}"' for name in room_names])

        # Generate room class mapping
        room_mapping_str = ', '.join([f'"{name}": {cls}' for name, cls in room_class_map.items()])

        code = f'''#!/usr/bin/env python3
"""
Generated Kivy Game Application
Exported from PyGameMaker IDE
"""

# Room dimensions - used for window sizing
GAME_WIDTH = {room_width}
GAME_HEIGHT = {room_height}

import os
os.environ['KIVY_WINDOW'] = 'sdl2'

# Get Windows DPI scale and adjust window size to compensate
def get_dpi_scale():
    try:
        import ctypes
        # Make process DPI aware
        try:
            ctypes.windll.shcore.SetProcessDpiAwareness(2)
        except:
            pass
        # Get DPI
        hdc = ctypes.windll.user32.GetDC(0)
        dpi = ctypes.windll.gdi32.GetDeviceCaps(hdc, 88)
        ctypes.windll.user32.ReleaseDC(0, hdc)
        return dpi / 96.0
    except:
        return 1.0

DPI_SCALE = get_dpi_scale()
ADJUSTED_WIDTH = int(GAME_WIDTH / DPI_SCALE)
ADJUSTED_HEIGHT = int(GAME_HEIGHT / DPI_SCALE)

# Configure Kivy with adjusted size
from kivy.config import Config
Config.set('graphics', 'width', str(ADJUSTED_WIDTH))
Config.set('graphics', 'height', str(ADJUSTED_HEIGHT))
Config.set('graphics', 'resizable', '0')
Config.set('graphics', 'fullscreen', '0')

from kivy.app import App
from kivy.uix.widget import Widget
from kivy.uix.popup import Popup
from kivy.uix.label import Label
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.core.window import Window
from kivy.clock import Clock
from kivy.graphics import Rectangle, Color
from kivy.core.image import Image as CoreImage

# Force adjusted window size
Window.size = (ADJUSTED_WIDTH, ADJUSTED_HEIGHT)

# Import all game scenes
{room_imports_str}

# Global game manager reference
_game_app = None

# Room configuration
ROOM_ORDER = [{room_list_str}]
ROOM_CLASSES = {{{room_mapping_str}}}


def get_game_app():
    """Get the global game app instance"""
    return _game_app


_room_transition_pending = False

def goto_next_room():
    """Go to the next room in the room order"""
    global _room_transition_pending
    if _game_app and not _room_transition_pending:
        _room_transition_pending = True
        _game_app.goto_next_room()


def goto_previous_room():
    """Go to the previous room in the room order"""
    global _room_transition_pending
    if _game_app and not _room_transition_pending:
        _room_transition_pending = True
        _game_app.goto_previous_room()


def goto_room(room_name):
    """Go to a specific room by name"""
    global _room_transition_pending
    if _game_app and not _room_transition_pending:
        _room_transition_pending = True
        _game_app.goto_room(room_name)


def next_room_exists():
    """Check if there is a next room after the current one"""
    if _game_app:
        return _game_app.current_room_index + 1 < len(ROOM_ORDER)
    return False


def previous_room_exists():
    """Check if there is a previous room before the current one"""
    if _game_app:
        return _game_app.current_room_index > 0
    return False


def get_score():
    """Get the current score"""
    if _game_app:
        return _game_app.score
    return 0


def set_score(value, relative=False):
    """Set the score value"""
    if _game_app:
        if relative:
            _game_app.score += value
        else:
            _game_app.score = value
        _game_app.show_score_in_caption = True
        _game_app.update_caption()


def get_lives():
    """Get the current lives"""
    if _game_app:
        return _game_app.lives
    return 0


def set_lives(value, relative=False):
    """Set the lives value"""
    if _game_app:
        if relative:
            _game_app.lives += value
        else:
            _game_app.lives = value
        _game_app.show_lives_in_caption = True
        _game_app.update_caption()


def get_health():
    """Get the current health"""
    if _game_app:
        return _game_app.health
    return 100


def set_health(value, relative=False):
    """Set the health value"""
    if _game_app:
        if relative:
            _game_app.health += value
        else:
            _game_app.health = value
        _game_app.health = max(0, min(100, _game_app.health))
        _game_app.show_health_in_caption = True
        _game_app.update_caption()


def set_window_caption(caption="", show_score=True, show_lives=True, show_health=False):
    """Set window caption settings"""
    if _game_app:
        _game_app.window_caption = caption
        _game_app.show_score_in_caption = show_score
        _game_app.show_lives_in_caption = show_lives
        _game_app.show_health_in_caption = show_health
        _game_app.update_caption()


_popup_open = False

def show_message(message):
    """Show a popup message dialog"""
    global _popup_open

    # Prevent duplicate popups
    if _popup_open:
        return
    _popup_open = True

    content = BoxLayout(orientation='vertical', padding=10, spacing=10)
    content.add_widget(Label(text=str(message)))
    btn = Button(text='OK', size_hint_y=None, height=40)
    content.add_widget(btn)

    popup = Popup(title='Message',
                  content=content,
                  size_hint=(None, None),
                  size=(300, 200),
                  auto_dismiss=False)

    def on_dismiss(instance):
        global _popup_open
        _popup_open = False

    popup.bind(on_dismiss=on_dismiss)
    btn.bind(on_release=popup.dismiss)
    popup.open()


class GameApp(App):
    """Main game application"""

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.current_room_index = 0
        self.scene = None
        self.update_event = None

        # Game state (score, lives, health)
        self.score = 0
        self.lives = 3
        self.health = 100

        # Caption display settings
        self.window_caption = ""
        self.show_score_in_caption = False
        self.show_lives_in_caption = False
        self.show_health_in_caption = False
        self.project_name = "{project_name}"

    def update_caption(self):
        """Update window caption with score/lives/health if enabled"""
        parts = []

        if self.window_caption:
            parts.append(self.window_caption)

        if self.show_score_in_caption:
            parts.append(f"Score: {{self.score}}")

        if self.show_lives_in_caption:
            parts.append(f"Lives: {{self.lives}}")

        if self.show_health_in_caption:
            parts.append(f"Health: {{int(self.health)}}")

        caption = " | ".join(parts) if parts else self.project_name
        Window.set_title(caption)

    def build(self):
        """Build the application"""
        global _game_app
        _game_app = self

        # Force DPI-adjusted window size
        Window.size = (ADJUSTED_WIDTH, ADJUSTED_HEIGHT)
        Window.clearcolor = (0, 0, 0, 1)

        # Create and return the starting scene
        self.scene = {self._get_room_class_name(first_room)}()
        self.current_room_index = 0

        # PERFORMANCE FIX: Schedule game loop at 60 FPS for optimal performance
        self.update_event = Clock.schedule_interval(self.scene.update, 1.0/60.0)

        # Force window size again after scene is created
        def force_size(dt):
            Window.size = (ADJUSTED_WIDTH, ADJUSTED_HEIGHT)
        Clock.schedule_once(force_size, 0.1)

        return self.scene

    def goto_next_room(self):
        """Switch to the next room"""
        next_index = self.current_room_index + 1
        if next_index < len(ROOM_ORDER):
            self._switch_to_room(next_index)
        else:
            show_message("Already at last room")

    def goto_previous_room(self):
        """Switch to the previous room"""
        if self.current_room_index > 0:
            self._switch_to_room(self.current_room_index - 1)
        else:
            show_message("Already at first room")

    def goto_room(self, room_name):
        """Switch to a specific room by name"""
        if room_name in ROOM_ORDER:
            index = ROOM_ORDER.index(room_name)
            self._switch_to_room(index)
        else:
            show_message(f"Room '{{room_name}}' not found")

    def _switch_to_room(self, room_index):
        """Internal method to switch rooms"""
        if room_index < 0 or room_index >= len(ROOM_ORDER):
            return

        # Stop current update loop
        if self.update_event:
            Clock.unschedule(self.update_event)

        # Clear current scene
        if self.scene:
            self.scene.clear_widgets()

        # Create new scene
        room_name = ROOM_ORDER[room_index]
        room_class = ROOM_CLASSES[room_name]
        self.scene = room_class()
        self.current_room_index = room_index

        # Resize window to match new room's dimensions (adjusted for DPI)
        new_width = int(self.scene.room_width / DPI_SCALE)
        new_height = int(self.scene.room_height / DPI_SCALE)
        Window.size = (new_width, new_height)

        # Update root widget
        self.root.clear_widgets()
        self.root.add_widget(self.scene)

        # Restart update loop
        self.update_event = Clock.schedule_interval(self.scene.update, 1.0/60.0)

        # Reset room transition flag after a short delay (allows current frame to complete)
        def reset_transition_flag(dt):
            global _room_transition_pending
            _room_transition_pending = False
        Clock.schedule_once(reset_transition_flag, 0.1)

        print(f"Switched to room: {{room_name}} ({{new_width}}x{{new_height}})")

    def on_stop(self):
        """Cleanup when app stops"""
        if self.update_event:
            Clock.unschedule(self.update_event)
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
            y_gamemaker = instance.get('y', 0)

            # KIVY COORDINATE FIX: Flip Y-axis for room layout
            # GameMaker: Y=0 at top, increases downward, position is sprite origin (usually top-left)
            # Kivy: Y=0 at bottom, increases upward, position is bottom-left corner
            # Formula: y_kivy = room_height - y_gamemaker - sprite_height
            # We use 32 as default sprite height (standard grid size)
            sprite_height = 32
            y = height - y_gamemaker - sprite_height

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

    def _class_name_to_snake_case(self, name):
        """Convert PascalCase class name to snake_case for collision events"""
        # ObjWall -> obj_wall, ObjPlayer -> obj_player
        import re
        # Insert underscore before uppercase letters (except first)
        s1 = re.sub('(.)([A-Z][a-z]+)', r'\\1_\\2', name)
        # Insert underscore before uppercase letters preceded by lowercase
        return re.sub('([a-z0-9])([A-Z])', r'\\1_\\2', s1).lower()
    
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
        """Main game loop update - GAMEMAKER 7.0 EVENT ORDER"""
        # GAMEMAKER 7.0 EVENT EXECUTION ORDER:
        # 1. Begin Step events
        # 2. Alarm events
        # 3. Keyboard, Key press, Key release (handled by Kivy elsewhere)
        # 4. Mouse events (handled by Kivy elsewhere)
        # 5. Normal Step events
        # 6. (Instances move to new positions)
        # 7. Collision events
        # 8. End Step events
        # 9. Draw events (handled by Kivy rendering)

        # 1. BEGIN STEP EVENTS
        for instance in self.instances:
            if hasattr(instance, 'on_begin_step'):
                instance.on_begin_step(dt)

        # 2. ALARM EVENTS (process countdown timers)
        for instance in self.instances:
            if hasattr(instance, '_process_alarms'):
                instance._process_alarms()

        # 3. KEYBOARD EVENTS
        # Check for "nokey" event - triggers when no keys are pressed
        if not self.keys_pressed:
            for instance in self.instances:
                if hasattr(instance, 'on_nokey'):
                    instance.on_nokey()

        # 4. NORMAL STEP EVENTS
        for instance in self.instances:
            if hasattr(instance, 'on_update'):
                instance.on_update(dt)

        # 5. MOVEMENT - instances move to new positions
        for instance in self.instances:
            if hasattr(instance, '_process_movement'):
                instance._process_movement(dt)

        # 6. COLLISION EVENTS
        # PERFORMANCE FIX: OPTIMIZED O(n²/2) collision detection
        # Check each pair of objects only ONCE instead of twice
        num_instances = len(self.instances)
        for i in range(num_instances):
            instance = self.instances[i]

            # Only check against instances we haven't checked yet (j > i)
            # This prevents checking A->B and then B->A (duplicate work)
            for j in range(i + 1, num_instances):
                other = self.instances[j]

                # Check collision between instance and other
                if instance.check_collision(other):
                    instance._collision_other = other
                    other._collision_other = instance

                    # Call collision event on BOTH objects (reciprocal events)
                    # Convert class name to snake_case: ObjWall -> obj_wall
                    other_class_snake = self._class_name_to_snake_case(other.__class__.__name__)
                    instance_event = f"on_collision_{{other_class_snake}}"
                    if hasattr(instance, instance_event):
                        getattr(instance, instance_event)(other)

                    # Also notify the other object
                    instance_class_snake = self._class_name_to_snake_case(instance.__class__.__name__)
                    other_event = f"on_collision_{{instance_class_snake}}"
                    if hasattr(other, other_event):
                        getattr(other, other_event)(instance)

        # 7. END STEP EVENTS
        for instance in self.instances:
            if hasattr(instance, 'on_end_step'):
                instance.on_end_step(dt)

        # 8. DRAW EVENTS - handled by Kivy's rendering system

        # 9. CLEANUP - Remove destroyed instances
        if self.instances_to_destroy:
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
            print(f"  ✗ CRITICAL ERROR: Failed to generate base object: {e}")
            import traceback
            traceback.print_exc()
            raise RuntimeError(f"Failed to generate base object class: {e}")

        # Then generate specific object types
        objects = self.project_data.get('assets', {}).get('objects', {})

        if not objects:
            print("  Warning: No objects found in project data")
            return

        failed_objects = []
        for obj_name, obj_data in objects.items():
            try:
                print(f"  Generating object: {obj_name}")
                self._generate_object(obj_name, obj_data)
                print(f"  ✓ Object {obj_name} generated")
            except Exception as e:
                print(f"  ✗ CRITICAL ERROR: Failed to generate object {obj_name}: {e}")
                import traceback
                traceback.print_exc()
                failed_objects.append(obj_name)

        if failed_objects:
            raise RuntimeError(f"Failed to generate {len(failed_objects)} object(s): {', '.join(failed_objects)}")
    
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
    """Base class for all game objects - GAMEMAKER 7.0 COMPATIBLE"""

    def __init__(self, scene, x=0, y=0, **kwargs):
        super().__init__(**kwargs)

        self.scene = scene
        # Use float for sub-pixel precision (smooth movement)
        self._x = float(x)
        self._y = float(y)

        # Movement properties (GameMaker style with bidirectional sync)
        self._hspeed = 0.0  # Horizontal speed (float for smooth movement)
        self._vspeed = 0.0  # Vertical speed (float for smooth movement)
        self._speed = 0.0   # Movement speed (magnitude)
        self._direction = 0  # Movement direction in degrees
        self._friction = 0
        self._gravity = 0
        self._gravity_direction = 270

        # GAMEMAKER 7.0: 12 alarm clocks per instance
        self.alarms = [-1] * 12  # -1 = inactive, >= 0 = active countdown
        
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

        # Visibility property - invisible objects can still collide, just don't render
        self.visible = True

        # Has sprite - objects without sprites have no collision mask
        self.has_sprite = False

        # Don't draw anything here - wait for set_sprite
        self.rect = None

    # GAMEMAKER 7.0: Bidirectional speed/direction synchronization
    @property
    def x(self):
        return self._x

    @x.setter
    def x(self, value):
        self._x = float(value)

    @property
    def y(self):
        return self._y

    @y.setter
    def y(self, value):
        self._y = float(value)

    @property
    def hspeed(self):
        return self._hspeed

    @hspeed.setter
    def hspeed(self, value):
        self._hspeed = float(value)
        self._sync_speed_direction_from_components()

    @property
    def vspeed(self):
        return self._vspeed

    @vspeed.setter
    def vspeed(self, value):
        self._vspeed = float(value)
        self._sync_speed_direction_from_components()

    @property
    def speed(self):
        return self._speed

    @speed.setter
    def speed(self, value):
        self._speed = float(value)
        self._sync_components_from_speed_direction()

    @property
    def direction(self):
        return self._direction

    @direction.setter
    def direction(self, value):
        self._direction = float(value)
        self._sync_components_from_speed_direction()

    @property
    def friction(self):
        return self._friction

    @friction.setter
    def friction(self, value):
        self._friction = float(value)

    @property
    def gravity(self):
        return self._gravity

    @gravity.setter
    def gravity(self, value):
        self._gravity = float(value)

    @property
    def gravity_direction(self):
        return self._gravity_direction

    @gravity_direction.setter
    def gravity_direction(self, value):
        self._gravity_direction = float(value)

    def _sync_speed_direction_from_components(self):
        """Update speed/direction when hspeed/vspeed change (GM 7.0 behavior)"""
        if self._hspeed != 0 or self._vspeed != 0:
            self._speed = math.sqrt(self._hspeed**2 + self._vspeed**2)
            self._direction = math.degrees(math.atan2(-self._vspeed, self._hspeed))
        else:
            self._speed = 0

    def _sync_components_from_speed_direction(self):
        """Update hspeed/vspeed when speed/direction change (GM 7.0 behavior)"""
        if self._speed != 0:
            rad = math.radians(self._direction)
            self._hspeed = self._speed * math.cos(rad)
            self._vspeed = -self._speed * math.sin(rad)
        else:
            self._hspeed = 0
            self._vspeed = 0
    
    def set_sprite(self, sprite_path):
        """Set the object's sprite - enables collision detection"""
        self.sprite_name = sprite_path
        img = load_image(sprite_path)

        if img:
            self.image = img
            self.image_width = img.width
            self.image_height = img.height
            self.size = (img.width, img.height)
            self.has_sprite = True  # Object has a sprite, can collide

            # Only draw if visible (invisible objects can still collide)
            if self.visible:
                self.canvas.clear()
                with self.canvas:
                    Color(1, 1, 1, 1)
                    self.rect = Rectangle(texture=img.texture, pos=self.pos, size=self.size)
            else:
                # Invisible but still has collision - don't draw anything
                self.canvas.clear()
                self.rect = None
    
    def _process_alarms(self):
        """Process alarm clocks (GAMEMAKER 7.0 feature)"""
        for i in range(12):
            if self.alarms[i] > 0:
                self.alarms[i] -= 1
                if self.alarms[i] == 0:
                    self.alarms[i] = -1  # Deactivate alarm
                    # Trigger alarm event
                    event_name = f"on_alarm_{{i}}"
                    if hasattr(self, event_name):
                        getattr(self, event_name)()

    def _process_movement(self, dt=1.0/60.0):
        """Process movement (called each frame) - GAMEMAKER 7.0 COMPATIBLE"""
        # FIXED: Now uses dt for frame-independent movement
        # speeds are in pixels per frame at 60 FPS, scaled by dt
        # This ensures consistent speed regardless of actual frame rate

        # NOTE: speed/direction are now auto-synced with hspeed/vspeed via properties
        # No manual sync needed!

        # Apply gravity (GM 7.0: adds to speed each step)
        if self._gravity != 0:
            grav_rad = math.radians(self._gravity_direction)
            # Directly modify internal values to avoid triggering sync multiple times
            self._hspeed += self._gravity * math.cos(grav_rad)
            self._vspeed += -self._gravity * math.sin(grav_rad)
            # Sync once after both changes
            self._sync_speed_direction_from_components()

        # Apply friction (GM 7.0: reduces speed towards zero)
        if self._friction != 0:
            if abs(self._hspeed) > self._friction:
                self._hspeed -= self._friction if self._hspeed > 0 else -self._friction
            else:
                self._hspeed = 0.0

            if abs(self._vspeed) > self._friction:
                self._vspeed -= self._friction if self._vspeed > 0 else -self._friction
            else:
                self._vspeed = 0.0
            # Sync after friction application
            self._sync_speed_direction_from_components()

        # Only move if there's actual speed
        if self._hspeed == 0 and self._vspeed == 0:
            return

        # MOVEMENT FIX: Scale movement by dt for frame-independence
        # speeds are in pixels/frame at 60 FPS, so scale by (dt * 60)
        # This makes movement consistent regardless of actual frame rate
        speed_factor = dt * 60.0 if dt > 0 else 1.0
        new_x = self._x + float(self._hspeed * speed_factor)
        new_y = self._y + float(self._vspeed * speed_factor)
        
        # PERFORMANCE FIX: Optimized solid collision checking
        # Only check solid-to-solid collisions to prevent overlap
        # Other collision events are handled by _check_collisions method
        can_move = True
        if self.solid:
            old_x, old_y = self.x, self.y
            self.x, self.y = new_x, new_y

            # Only check against other solid objects (much smaller set)
            for other in self.scene.instances:
                if other != self and other.solid and self.check_collision(other):
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
        # PERFORMANCE FIX: Keep float precision for smooth movement
        self.pos = (float(self.x), float(self.y))
        if self.rect is not None:
            self.rect.pos = self.pos
            # PERFORMANCE FIX: Removed canvas.ask_update() - Kivy auto-updates on property changes
            # Calling ask_update() every frame for every object was causing major slowdowns
    
    def check_collision(self, other):
        """Check AABB (Axis-Aligned Bounding Box) collision with another object

        PERFORMANCE: This is a fast rectangular collision check.
        Returns True if this object overlaps with the other object.

        GameMaker behavior:
        - Objects without sprites have no collision mask (no collisions)
        - Invisible objects WITH sprites can still collide
        """
        # No collision if either object has no sprite (no collision mask)
        if not self.has_sprite or not other.has_sprite:
            return False

        return (
            self.x < other.x + other.size[0] and
            self.x + self.size[0] > other.x and
            self.y < other.y + other.size[1] and
            self.y + self.size[1] > other.y
        )
    
    def destroy(self):
        """Destroy this instance"""
        if hasattr(self, 'on_destroy'):
            self.on_destroy()
        self.scene.destroy_instance(self)
    
    def is_on_grid(self):
        """Check if object is close to grid alignment"""
        # Tolerance must account for variable frame rates
        # At 30 FPS with speed 4: movement = 4 * 2.0 = 8 pixels/frame
        # Use generous tolerance to handle frame rate variations
        base_speed = max(abs(self.hspeed), abs(self.vspeed), 4)
        tolerance = base_speed * 2.5  # Handle up to ~24 FPS

        # Find nearest grid position
        nearest_x = round(self.x / self.grid_size) * self.grid_size
        nearest_y = round(self.y / self.grid_size) * self.grid_size

        # Check if we're close enough to that grid position
        x_diff = abs(self.x - nearest_x)
        y_diff = abs(self.y - nearest_y)

        return x_diff <= tolerance and y_diff <= tolerance
    
    def snap_to_grid(self):
        """Snap object to nearest grid position"""
        self.x = round(self.x / self.grid_size) * self.grid_size
        self.y = round(self.y / self.grid_size) * self.grid_size
        self._update_position()

    def _check_wall_ahead(self, dx, dy):
        """Check if there's a wall in the direction we want to move"""
        # Temporarily move to check position
        old_x, old_y = self.x, self.y
        self.x += dx
        self.y += dy

        # Check for collision with any solid object
        collision = False
        for other in self.scene.instances:
            if other != self and other.solid and self.check_collision(other):
                collision = True
                break

        # Restore position
        self.x, self.y = old_x, old_y

        return collision

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
        
        # Group keyboard events together (but NOT nokey - that's handled separately)
        keyboard_events = [e for e in events if e.get('event_type') == 'keyboard' and e.get('key_name') and e.get('key_name') != 'nokey']
        nokey_events = [e for e in events if e.get('event_type') == 'keyboard' and e.get('key_name') == 'nokey']
        other_events = [e for e in events if not (e.get('event_type') == 'keyboard' and e.get('key_name'))]

        # Generate consolidated keyboard handler if there are keyboard events
        if keyboard_events:
            print(f"      Generating consolidated keyboard handler for {len(keyboard_events)} key(s)")
            keyboard_method = self._generate_keyboard_handler(keyboard_events)
            methods.append(keyboard_method)

        # Generate on_nokey method for nokey events
        if nokey_events:
            print(f"      Generating nokey handler")
            nokey_event = nokey_events[0]  # There should only be one nokey event
            actions = nokey_event.get('actions', [])
            if actions:
                action_code = self._generate_action_code(obj_name, actions, nokey_event)
                nokey_method = f'''    def on_nokey(self):
        """Event handler: keyboard nokey (no keys pressed)"""
{action_code}
'''
                methods.append(nokey_method)
        
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
        # For grid-based movement games, keyboard input should be handled in the step event
        # NOT in keyboard handlers, to avoid conflicts and wall-phasing issues

        # Check if ANY keyboard event uses grid-based movement
        uses_grid_movement = False
        for event in keyboard_events:
            actions = event.get('actions', [])
            for action in actions:
                if isinstance(action, dict):
                    action_type = action.get('action_type', action.get('action', ''))
                    # Check for if_on_grid or movement actions
                    if action_type == 'if_on_grid' or action_type in ['set_hspeed', 'set_vspeed']:
                        uses_grid_movement = True
                        break
            if uses_grid_movement:
                break

        # If using grid movement, generate step-based keyboard checking instead
        if uses_grid_movement:
            return self._generate_grid_keyboard_handler(keyboard_events)

        # Otherwise, generate normal keyboard handler
        key_map = {
            'right': '275',
            'left': '276',
            'up': '273',
            'down': '274',
        }

        code_lines = []
        code_lines.append("    def on_keyboard(self, key, scancode, codepoint, modifier):")
        code_lines.append('        """Handle keyboard press events"""')

        for i, event in enumerate(keyboard_events):
            key_name = event.get('key_name', '')
            actions = event.get('actions', [])
            key_code = key_map.get(key_name, '0')

            if_keyword = "if" if i == 0 else "elif"
            code_lines.append(f"        {if_keyword} key == {key_code}:  # {key_name}")

            if actions:
                generator = ActionCodeGenerator(base_indent=3)
                for action in actions:
                    if isinstance(action, dict):
                        generator.process_action(action, 'keyboard')
                    elif isinstance(action, str) and action.strip():
                        generator.add_line(action)

                action_code = generator.get_code()
                if action_code.strip():
                    code_lines.append(action_code)
                else:
                    code_lines.append("            pass")
            else:
                code_lines.append("            pass")

        return '\n'.join(code_lines)

    def _generate_grid_keyboard_handler(self, keyboard_events: List[Dict]) -> str:
        """Generate an on_update method that checks keyboard state for grid-based movement

        Grid movement logic:
        - When on a grid position, check keys and set movement direction
        - When NOT on grid, continue moving until we reach a grid position
        - Track whether keys are released mid-movement with _want_to_stop flag
        """
        key_map = {
            'right': '275',
            'left': '276',
            'up': '273',
            'down': '274',
        }

        # Extract speed values from the keyboard events
        speed_values = {'right': 4, 'left': -4, 'up': 4, 'down': -4}
        for event in keyboard_events:
            key_name = event.get('key_name', '')
            actions = event.get('actions', [])
            for action in actions:
                if isinstance(action, dict):
                    action_type = action.get('action_type', action.get('action', ''))
                    if action_type == 'if_on_grid':
                        params = action.get('parameters', {})
                        then_actions = params.get('then_actions', [])
                        for inner in then_actions:
                            if isinstance(inner, dict):
                                inner_type = inner.get('action_type', inner.get('action', ''))
                                inner_params = inner.get('parameters', {})
                                if inner_type == 'set_hspeed' and key_name in ['right', 'left']:
                                    speed_values[key_name] = inner_params.get('value', 4)
                                elif inner_type == 'set_vspeed' and key_name in ['up', 'down']:
                                    # Flip for Kivy coordinates
                                    val = inner_params.get('value', 4)
                                    speed_values[key_name] = -val if isinstance(val, (int, float)) else val
                    elif action_type == 'set_hspeed' and key_name in ['right', 'left']:
                        params = action.get('parameters', {})
                        speed_values[key_name] = params.get('value', 4)
                    elif action_type == 'set_vspeed' and key_name in ['up', 'down']:
                        params = action.get('parameters', {})
                        val = params.get('value', 4)
                        speed_values[key_name] = -val if isinstance(val, (int, float)) else val

        code_lines = []
        code_lines.append("    def on_update(self, dt):")
        code_lines.append('        """Step event with keyboard checking for grid-based movement"""')
        code_lines.append("")
        code_lines.append("        # Initialize grid movement state if not present")
        code_lines.append("        if not hasattr(self, '_grid_target_x'):")
        code_lines.append("            self._grid_target_x = None  # Target grid X position")
        code_lines.append("            self._grid_target_y = None  # Target grid Y position")
        code_lines.append("            self._grid_moving = False   # Currently moving to a target")
        code_lines.append("")
        code_lines.append("        # Check if any movement key is currently pressed")
        code_lines.append("        key_right = self.scene.keys_pressed.get(275, False)")
        code_lines.append("        key_left = self.scene.keys_pressed.get(276, False)")
        code_lines.append("        key_up = self.scene.keys_pressed.get(273, False)")
        code_lines.append("        key_down = self.scene.keys_pressed.get(274, False)")
        code_lines.append("        any_key_pressed = key_right or key_left or key_up or key_down")
        code_lines.append("")
        code_lines.append("        grid = self.grid_size")
        code_lines.append("")
        code_lines.append("        # If we're currently moving to a target, check if we've reached it")
        code_lines.append("        if self._grid_moving:")
        code_lines.append("            reached_x = True")
        code_lines.append("            reached_y = True")
        code_lines.append("            ")
        code_lines.append("            # Check X target")
        code_lines.append("            if self._grid_target_x is not None:")
        code_lines.append("                if self.hspeed > 0 and self.x >= self._grid_target_x:")
        code_lines.append("                    self.x = self._grid_target_x")
        code_lines.append("                    reached_x = True")
        code_lines.append("                elif self.hspeed < 0 and self.x <= self._grid_target_x:")
        code_lines.append("                    self.x = self._grid_target_x")
        code_lines.append("                    reached_x = True")
        code_lines.append("                elif self.hspeed != 0:")
        code_lines.append("                    reached_x = False")
        code_lines.append("            ")
        code_lines.append("            # Check Y target")
        code_lines.append("            if self._grid_target_y is not None:")
        code_lines.append("                if self.vspeed > 0 and self.y >= self._grid_target_y:")
        code_lines.append("                    self.y = self._grid_target_y")
        code_lines.append("                    reached_y = True")
        code_lines.append("                elif self.vspeed < 0 and self.y <= self._grid_target_y:")
        code_lines.append("                    self.y = self._grid_target_y")
        code_lines.append("                    reached_y = True")
        code_lines.append("                elif self.vspeed != 0:")
        code_lines.append("                    reached_y = False")
        code_lines.append("            ")
        code_lines.append("            # If we've reached the target, check if we should continue or stop")
        code_lines.append("            if reached_x and reached_y:")
        code_lines.append("                self._update_position()")
        code_lines.append("                # Check if the same direction key is still held - continue moving")
        code_lines.append("                continue_moving = False")
        code_lines.append(f"                if self.hspeed > 0 and key_right:")
        code_lines.append(f"                    self._grid_target_x = self.x + grid")
        code_lines.append(f"                    continue_moving = True")
        code_lines.append(f"                elif self.hspeed < 0 and key_left:")
        code_lines.append(f"                    self._grid_target_x = self.x - grid")
        code_lines.append(f"                    continue_moving = True")
        code_lines.append(f"                elif self.vspeed > 0 and key_up:")
        code_lines.append(f"                    self._grid_target_y = self.y + grid")
        code_lines.append(f"                    continue_moving = True")
        code_lines.append(f"                elif self.vspeed < 0 and key_down:")
        code_lines.append(f"                    self._grid_target_y = self.y - grid")
        code_lines.append(f"                    continue_moving = True")
        code_lines.append("                ")
        code_lines.append("                if not continue_moving:")
        code_lines.append("                    # Stop moving")
        code_lines.append("                    self.hspeed = 0")
        code_lines.append("                    self.vspeed = 0")
        code_lines.append("                    self._grid_moving = False")
        code_lines.append("                    self._grid_target_x = None")
        code_lines.append("                    self._grid_target_y = None")
        code_lines.append("")
        code_lines.append("        # If not moving, check for new movement input")
        code_lines.append("        if not self._grid_moving and any_key_pressed:")
        code_lines.append("            # Snap to nearest grid position first (in case we're slightly off)")
        code_lines.append("            snap_x = round(self.x / grid) * grid")
        code_lines.append("            snap_y = round(self.y / grid) * grid")
        code_lines.append("            self.x = snap_x")
        code_lines.append("            self.y = snap_y")
        code_lines.append("            ")
        code_lines.append("            # Set target based on key pressed (priority: right, left, up, down)")
        code_lines.append(f"            if key_right:")
        code_lines.append(f"                self._grid_target_x = snap_x + grid")
        code_lines.append(f"                self._grid_target_y = snap_y")
        code_lines.append(f"                self.hspeed = {abs(speed_values.get('right', 4))}")
        code_lines.append(f"                self.vspeed = 0")
        code_lines.append(f"                self._grid_moving = True")
        code_lines.append(f"            elif key_left:")
        code_lines.append(f"                self._grid_target_x = snap_x - grid")
        code_lines.append(f"                self._grid_target_y = snap_y")
        code_lines.append(f"                self.hspeed = -{abs(speed_values.get('left', 4))}")
        code_lines.append(f"                self.vspeed = 0")
        code_lines.append(f"                self._grid_moving = True")
        code_lines.append(f"            elif key_up:")
        code_lines.append(f"                self._grid_target_x = snap_x")
        code_lines.append(f"                self._grid_target_y = snap_y + grid")
        code_lines.append(f"                self.hspeed = 0")
        code_lines.append(f"                self.vspeed = {abs(speed_values.get('up', 4))}")
        code_lines.append(f"                self._grid_moving = True")
        code_lines.append(f"            elif key_down:")
        code_lines.append(f"                self._grid_target_x = snap_x")
        code_lines.append(f"                self._grid_target_y = snap_y - grid")
        code_lines.append(f"                self.hspeed = 0")
        code_lines.append(f"                self.vspeed = -{abs(speed_values.get('down', 4))}")
        code_lines.append(f"                self._grid_moving = True")
        code_lines.append("")

        return '\n'.join(code_lines)

    def _get_event_method_name(self, event: Dict) -> str:
        """Get the method name for an event - GAMEMAKER 7.0 COMPLETE"""
        event_type = event.get('event_type', '')

        # Handle collision events with specific format: collision_with_obj_name
        if event_type.startswith('collision_with_'):
            # Extract object name from collision_with_obj_name
            collision_obj = event_type.replace('collision_with_', '')
            return f"on_collision_{collision_obj.lower()}"

        # Handle alarm events (alarm_0 through alarm_11)
        if event_type.startswith('alarm_'):
            return f"on_{event_type}"  # on_alarm_0, on_alarm_1, etc.

        # Map event types to method names (GAMEMAKER 7.0 COMPLETE)
        event_map = {
            'create': 'on_create',
            'step': 'on_update',
            'begin_step': 'on_begin_step',
            'end_step': 'on_end_step',
            'destroy': 'on_destroy',
            'keyboard': 'on_keyboard',
            'keyboard_press': 'on_keyboard_press',
            'keyboard_release': 'on_keyboard_release',
            'keyboard_up': 'on_keyboard_up',  # Legacy name
            'draw': 'on_draw',
            'room_start': 'on_room_start',
            'room_end': 'on_room_end',
            'game_start': 'on_game_start',
            'game_end': 'on_game_end',
            'outside_room': 'on_outside_room',
            'intersect_boundary': 'on_intersect_boundary',
        }

        if event_type == 'collision':
            collision_obj = event.get('collision_object', 'object')
            return f"on_collision_{collision_obj.lower()}"

        return event_map.get(event_type, '')
    
    def _generate_action_code(self, obj_name: str, actions: List[Dict], event: Dict) -> str:
        """Generate Python code from action list - WITH BLOCK SYSTEM"""
        event_type = event.get('event_type', '')

        if not actions:
            return "        pass"

        print(f"        _generate_action_code: {len(actions)} actions for event {event_type}")

        # Use the new ActionCodeGenerator for proper block/indentation handling
        generator = ActionCodeGenerator(base_indent=2)

        for i, action in enumerate(actions):
            print(f"          Action {i}: {type(action).__name__}")

            if isinstance(action, dict):
                action_type = action.get('action_type', action.get('action', ''))
                print(f"            Type: '{action_type}'")

                # Process action with block system
                generator.process_action(action, event_type)

            elif isinstance(action, str):
                # String action - add as raw code
                print(f"            String action: '{action[:80]}'")
                if action.strip():
                    generator.add_line(action)

        # Get the generated code
        code = generator.get_code()

        # CRITICAL: Always return valid Python code with at least 'pass'
        if not code or not code.strip():
            print(f"          Warning: No code generated for event {event_type}, using 'pass'")
            return "        pass"

        return code
    
    def _convert_action_to_code(self, action_type: str, params: Dict, event_type: str) -> str:
        """Convert a single action to Python code - GAMEMAKER 7.0 COMPLETE"""

        # GAMEMAKER 7.0 MOVEMENT ACTIONS
        if action_type == 'set_hspeed':
            return f"self.hspeed = {params.get('speed', params.get('value', 0))}"

        elif action_type == 'set_vspeed':
            return f"self.vspeed = {params.get('speed', params.get('value', 0))}"

        elif action_type == 'set_speed':
            return f"self.speed = {params.get('speed', params.get('value', 0))}"

        elif action_type == 'set_direction':
            return f"self.direction = {params.get('direction', params.get('value', 0))}"

        elif action_type == 'move_fixed':
            # GameMaker's 8-way movement
            directions = params.get('directions', ['right'])
            speed = params.get('speed', 4)
            dir_map = {
                'right': 0, 'up-right': 45, 'up': 90, 'up-left': 135,
                'left': 180, 'down-left': 225, 'down': 270, 'down-right': 315,
                'stop': -1
            }
            if 'stop' in directions:
                return "self.speed = 0"
            elif len(directions) == 1:
                deg = dir_map.get(directions[0], 0)
                return f"self.direction = {deg}; self.speed = {speed}"
            else:
                # Multiple directions - random choice
                dirs = [str(dir_map.get(d, 0)) for d in directions if d != 'stop']
                return f"import random; self.direction = random.choice([{', '.join(dirs)}]); self.speed = {speed}"

        elif action_type == 'move_free':
            direction = params.get('direction', 0)
            speed = params.get('speed', 4)
            return f"self.direction = {direction}; self.speed = {speed}"

        elif action_type == 'move_towards':
            x = params.get('x', 0)
            y = params.get('y', 0)
            speed = params.get('speed', 4)
            return f"import math; self.direction = math.degrees(math.atan2(-({y} - self.y), {x} - self.x)); self.speed = {speed}"

        elif action_type == 'set_gravity':
            direction = params.get('direction', 270)
            gravity = params.get('gravity', 0.5)
            return f"self.gravity_direction = {direction}; self.gravity = {gravity}"

        elif action_type == 'set_friction':
            friction = params.get('friction', 0.1)
            return f"self.friction = {friction}"

        elif action_type == 'reverse_horizontal':
            return "self.hspeed = -self.hspeed"

        elif action_type == 'reverse_vertical':
            return "self.vspeed = -self.vspeed"

        elif action_type == 'stop_movement':
            return "self.hspeed = 0; self.vspeed = 0; self.speed = 0"

        elif action_type == 'snap_to_grid':
            return "self.snap_to_grid()"

        # GAMEMAKER 7.0 CONTROL ACTIONS
        elif action_type == 'if_on_grid':
            # Check if on grid AND snap to exact position
            return """if self.is_on_grid():
            self.snap_to_grid()"""

        elif action_type == 'test_expression':
            expr = params.get('expression', 'False')
            return f"if {expr}:"

        elif action_type == 'check_empty':
            x = params.get('x', 'self.x')
            y = params.get('y', 'self.y')
            relative = params.get('relative', False)
            if relative:
                return f"if not self.check_collision_at(self.x + {x}, self.y + {y}):"
            else:
                return f"if not self.check_collision_at({x}, {y}):"

        elif action_type == 'check_collision':
            x = params.get('x', 'self.x')
            y = params.get('y', 'self.y')
            obj = params.get('object', params.get('target', ''))
            if obj:
                return f"if self.check_collision_at({x}, {y}, '{obj}'):"
            else:
                return f"if self.check_collision_at({x}, {y}):"

        elif action_type == 'if_collision_at':
            x = params.get('x', 'self.x')
            y = params.get('y', 'self.y')
            obj = params.get('object', params.get('target', ''))
            if obj:
                return f"if self.check_collision_at({x}, {y}, '{obj}'):"
            else:
                return f"if self.check_collision_at({x}, {y}):"

        elif action_type == 'move_grid':
            # Grid-based movement - move one grid cell in specified direction
            direction = params.get('direction', 'right')
            grid_size = params.get('grid_size', 32)
            dir_map = {
                'right': (1, 0), 'left': (-1, 0),
                'up': (0, 1), 'down': (0, -1),  # Kivy Y is inverted
                'up-right': (1, 1), 'up-left': (-1, 1),
                'down-right': (1, -1), 'down-left': (-1, -1)
            }
            dx, dy = dir_map.get(direction, (0, 0))
            return f"self.x += {dx * grid_size}; self.y += {dy * grid_size}"

        elif action_type == 'stop_if_no_keys':
            # Check if no arrow keys are pressed
            return """if not (self.scene.keys_pressed.get(275, False) or self.scene.keys_pressed.get(276, False) or self.scene.keys_pressed.get(273, False) or self.scene.keys_pressed.get(274, False)):
        self.snap_to_grid()
        self.hspeed = 0
        self.vspeed = 0"""

        elif action_type == 'exit_event':
            return "return  # Exit event"

        # GAMEMAKER 7.0 ALARM ACTIONS
        elif action_type == 'set_alarm':
            alarm_num = params.get('alarm_number', 0)
            steps = params.get('steps', 30)
            return f"self.alarms[{alarm_num}] = {steps}"

        # INSTANCE ACTIONS
        elif action_type == 'destroy_instance':
            target = params.get('target', 'self')
            if target == 'other' and 'collision' in event_type:
                return "other.destroy()"
            else:
                return "self.destroy()"

        # KEYBOARD CHECKS
        elif action_type == 'check_key':
            key_code = params.get('key', 0)
            return f"if {key_code} in self.scene.keys_pressed:"

        # MESSAGE ACTIONS
        elif action_type == 'show_message' or action_type == 'display_message':
            message = params.get('message', '')
            # Escape quotes in message
            escaped_message = message.replace("'", "\\'")
            return f"from main import show_message; show_message('{escaped_message}')"

        # SCORE/LIVES/HEALTH ACTIONS (use lazy import to avoid circular imports)
        elif action_type == 'set_score':
            value = params.get('value', 0)
            relative = params.get('relative', False)
            return f"from main import set_score; set_score({value}, relative={relative})"

        elif action_type == 'set_lives':
            value = params.get('value', 3)
            relative = params.get('relative', False)
            return f"from main import set_lives; set_lives({value}, relative={relative})"

        elif action_type == 'set_health':
            value = params.get('value', 100)
            relative = params.get('relative', False)
            return f"from main import set_health; set_health({value}, relative={relative})"

        elif action_type == 'set_window_caption':
            caption = params.get('caption', '')
            show_score = params.get('show_score', True)
            show_lives = params.get('show_lives', True)
            show_health = params.get('show_health', False)
            return f"from main import set_window_caption; set_window_caption(caption='{caption}', show_score={show_score}, show_lives={show_lives}, show_health={show_health})"

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
import sys


_image_cache = {}
_base_path = None


def get_base_path():
    """Get the base path for assets, handling PyInstaller frozen executables"""
    global _base_path
    if _base_path is not None:
        return _base_path

    if getattr(sys, 'frozen', False):
        # Running as compiled executable (PyInstaller)
        # Assets are in _MEIPASS/game/
        _base_path = os.path.join(sys._MEIPASS, 'game')
    else:
        # Running as script - use the directory containing this file
        _base_path = os.path.dirname(os.path.abspath(__file__))

    return _base_path


def get_asset_path(relative_path):
    """Get absolute path to an asset file"""
    base = get_base_path()
    return os.path.join(base, relative_path)


def load_image(path):
    """Load an image with caching"""
    if path in _image_cache:
        return _image_cache[path]

    # Convert relative path to absolute path
    abs_path = get_asset_path(path)

    try:
        if os.path.exists(abs_path):
            img = CoreImage(abs_path)
            _image_cache[path] = img
            return img
        else:
            print(f"Image not found: {abs_path}")
    except Exception as e:
        print(f"Failed to load image {abs_path}: {e}")

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
