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


class ActionCodeGenerator:
    """
    Handles proper code generation with indentation tracking for block-based actions.

    This class solves the critical problem where conditional actions like if_on_grid,
    start_block, and else_action need to properly indent subsequent actions.
    """

    def __init__(self, base_indent=2):
        """
        Initialize the code generator.

        Args:
            base_indent: Base indentation level (2 = inside a method definition)
        """
        self.base_indent = base_indent
        self.indent_level = 0  # Additional indent beyond base
        self.lines = []
        self.block_stack = []  # Track open blocks for proper nesting

    def add_line(self, code):
        """Add a line with current indentation"""
        if not code:
            return
        total_indent = self.base_indent + self.indent_level
        indent_str = "    " * total_indent

        # Handle multi-line code - indent each line properly
        if '\n' in code:
            for line in code.split('\n'):
                if line.strip():
                    # Check if line already has relative indentation (starts with spaces)
                    if line.startswith('    '):
                        # Line has relative indent - add base indent
                        self.lines.append(f"{indent_str}{line}")
                    else:
                        # No relative indent - add base indent only
                        self.lines.append(f"{indent_str}{line}")
        else:
            self.lines.append(f"{indent_str}{code}")

    def push_indent(self):
        """Increase indentation level (entering block)"""
        self.indent_level += 1

    def pop_indent(self):
        """Decrease indentation level (exiting block)"""
        self.indent_level = max(0, self.indent_level - 1)

    def get_code(self):
        """Get final generated code"""
        return '\n'.join(self.lines)

    def process_action(self, action: Dict, event_type: str = ''):
        """
        Process a single action and generate appropriate code.

        Handles both simple actions and complex block actions.
        Supports both 'action_type' and 'action' keys for compatibility.
        """
        # Support both 'action_type' and 'action' keys
        action_type = action.get('action_type', action.get('action', ''))
        params = action.get('parameters', {})

        # BLOCK CONTROL ACTIONS
        if action_type == 'start_block':
            # Start of a code block - just push indent, no code generated
            self.push_indent()
            self.block_stack.append('block')
            return

        elif action_type == 'end_block':
            # End of a code block - pop indent
            if self.block_stack and self.block_stack[-1] == 'block':
                self.block_stack.pop()
            self.pop_indent()
            return

        elif action_type == 'else_action':
            # Else clause - pop indent, add else, push indent
            self.pop_indent()
            self.add_line("else:")
            self.push_indent()
            if self.block_stack and self.block_stack[-1] in ['if', 'if_on_grid']:
                self.block_stack[-1] = 'else'
            return

        # CONDITIONAL ACTIONS (these start blocks)
        elif action_type == 'if_on_grid':
            self.add_line("if self.is_on_grid():")
            self.push_indent()
            self.block_stack.append('if_on_grid')

            # Process nested then_actions if present
            then_actions = params.get('then_actions', [])
            if then_actions:
                for nested_action in then_actions:
                    if isinstance(nested_action, dict):
                        self.process_action(nested_action, event_type)
                    elif isinstance(nested_action, str) and nested_action.strip():
                        self.add_line(nested_action)
                # Pop indent after processing nested actions
                self.pop_indent()
                if self.block_stack and self.block_stack[-1] == 'if_on_grid':
                    self.block_stack.pop()
            return

        elif action_type == 'test_expression':
            expr = params.get('expression', 'False')
            self.add_line(f"if {expr}:")
            self.push_indent()
            self.block_stack.append('if')
            return

        elif action_type == 'if_collision':
            obj_name = params.get('object', 'object')
            x = params.get('x', 'self.x')
            y = params.get('y', 'self.y')
            self.add_line(f"if self.check_collision_at({x}, {y}, '{obj_name}'):")
            self.push_indent()
            self.block_stack.append('if')
            return

        elif action_type == 'if_key_pressed':
            key = params.get('key', 'right')
            key_map = {'right': '275', 'left': '276', 'up': '273', 'down': '274'}
            key_code = key_map.get(key, '275')
            self.add_line(f"if self.scene.keys_pressed.get({key_code}, False):")
            self.push_indent()
            self.block_stack.append('if')
            return

        # LOOP ACTIONS
        elif action_type == 'repeat':
            count = params.get('count', 1)
            self.add_line(f"for _i in range({count}):")
            self.push_indent()
            self.block_stack.append('loop')
            return

        elif action_type == 'while':
            condition = params.get('condition', 'False')
            self.add_line(f"while {condition}:")
            self.push_indent()
            self.block_stack.append('loop')
            return

        # SPECIAL CONDITIONAL ACTIONS
        elif action_type == 'stop_if_no_keys':
            # Grid-based movement: stop, snap to grid, then check keys to start new movement
            # This prevents wall-phasing and ensures proper grid alignment
            self.add_line("# Snap to exact grid position")
            self.add_line("self.snap_to_grid()")
            self.add_line("")
            self.add_line("# Always stop when on grid")
            self.add_line("self.hspeed = 0")
            self.add_line("self.vspeed = 0")
            self.add_line("")
            self.add_line("# Check if arrow keys are pressed to start moving to next grid")
            self.add_line("# Use wall collision check to prevent phasing")
            self.add_line("if self.scene.keys_pressed.get(275, False):  # right")
            self.push_indent()
            self.add_line("if not self._check_wall_ahead(32, 0):")
            self.push_indent()
            self.add_line("self.hspeed = 4")
            self.pop_indent()
            self.pop_indent()
            self.add_line("elif self.scene.keys_pressed.get(276, False):  # left")
            self.push_indent()
            self.add_line("if not self._check_wall_ahead(-32, 0):")
            self.push_indent()
            self.add_line("self.hspeed = -4")
            self.pop_indent()
            self.pop_indent()
            self.add_line("elif self.scene.keys_pressed.get(273, False):  # up")
            self.push_indent()
            self.add_line("if not self._check_wall_ahead(0, 32):")
            self.push_indent()
            self.add_line("self.vspeed = 4")
            self.pop_indent()
            self.pop_indent()
            self.add_line("elif self.scene.keys_pressed.get(274, False):  # down")
            self.push_indent()
            self.add_line("if not self._check_wall_ahead(0, -32):")
            self.push_indent()
            self.add_line("self.vspeed = -4")
            self.pop_indent()
            self.pop_indent()
            return

        # SIMPLE ACTIONS - generate code directly
        else:
            code = self._convert_simple_action(action_type, params, event_type)
            if code:
                # Handle multi-line code
                if '\n' in code:
                    for line in code.split('\n'):
                        if line.strip():
                            self.add_line(line.strip())
                else:
                    self.add_line(code)

    def _convert_simple_action(self, action_type: str, params: Dict, event_type: str) -> str:
        """Convert a simple (non-block) action to Python code"""

        # MOVEMENT ACTIONS
        if action_type == 'set_hspeed':
            return f"self.hspeed = {params.get('speed', params.get('value', 0))}"

        elif action_type == 'set_vspeed':
            # KIVY COORDINATE FIX: Kivy uses bottom-left origin (Y increases upward)
            # GameMaker uses top-left origin (Y increases downward)
            # So we need to flip the vspeed sign
            speed = params.get('speed', params.get('value', 0))
            flipped_speed = -speed if isinstance(speed, (int, float)) else f"-({speed})"
            return f"self.vspeed = {flipped_speed}"

        elif action_type == 'set_speed':
            return f"self.speed = {params.get('speed', params.get('value', 0))}"

        elif action_type == 'set_direction':
            return f"self.direction = {params.get('direction', params.get('value', 0))}"

        elif action_type == 'move_fixed':
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
                dirs = [str(dir_map.get(d, 0)) for d in directions if d != 'stop']
                return f"import random; self.direction = random.choice([{', '.join(dirs)}]); self.speed = {speed}"

        elif action_type == 'stop_movement':
            return "self.hspeed = 0; self.vspeed = 0; self.speed = 0"

        elif action_type == 'snap_to_grid':
            return "self.snap_to_grid()"

        elif action_type == 'stop_if_no_keys':
            # This is handled as a block action in process_action, not here
            return None

        # INSTANCE ACTIONS
        elif action_type == 'destroy_instance':
            target = params.get('target', 'self')
            if target == 'other' and 'collision' in event_type:
                return "other.destroy()"
            else:
                return "self.destroy()"

        # ALARM ACTIONS
        elif action_type == 'set_alarm':
            alarm_num = params.get('alarm_number', 0)
            steps = params.get('steps', 30)
            return f"self.alarms[{alarm_num}] = {steps}"

        # DEFAULT
        else:
            print(f"            Warning: Unknown action type '{action_type}'")
            return f"pass  # TODO: {action_type}"


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

        # PERFORMANCE FIX: Schedule game loop at 60 FPS for optimal performance
        # Running faster than 60 FPS wastes CPU/battery with no visual benefit
        # The scene.update() method uses dt for frame-independent movement
        Clock.schedule_interval(self.scene.update, 1.0/60.0)  # 60 FPS target

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
            y_gamemaker = instance.get('y', 0)

            # KIVY COORDINATE FIX: Flip Y-axis for room layout
            # GameMaker: Y=0 at top, increases downward
            # Kivy: Y=0 at bottom, increases upward
            # Formula: y_kivy = room_height - y_gamemaker
            y = height - y_gamemaker

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

        # 3. KEYBOARD/MOUSE EVENTS - handled by Kivy event system

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
        
        with self.canvas:
            Color(1, 1, 1, 1)
            self.rect = Rectangle(pos=self.pos, size=self.size)

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
        if hasattr(self, 'rect'):
            self.rect.pos = self.pos
            # PERFORMANCE FIX: Removed canvas.ask_update() - Kivy auto-updates on property changes
            # Calling ask_update() every frame for every object was causing major slowdowns
    
    def check_collision(self, other):
        """Check AABB (Axis-Aligned Bounding Box) collision with another object

        PERFORMANCE: This is a fast rectangular collision check.
        Returns True if this object overlaps with the other object.
        """
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
        # Check if we're within movement speed of a grid position
        # This handles float precision issues
        tolerance = 3.5  # Allow up to 3.5 pixels off (tighter tolerance to prevent overshoot)

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
        """Generate a consolidated keyboard handler for all key-specific events - DISABLED FOR GRID MOVEMENT"""
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

        # If using grid movement, don't generate keyboard handler
        # The step event will handle everything
        if uses_grid_movement:
            return ""

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
            return "if self.is_on_grid():"

        elif action_type == 'test_expression':
            expr = params.get('expression', 'False')
            return f"if {expr}:"

        elif action_type == 'check_empty':
            x = params.get('x', 'self.x')
            y = params.get('y', 'self.y')
            only_solid = params.get('only_solid', True)
            # This needs collision checking logic
            return f"# TODO: check_empty at ({x}, {y}, solid={only_solid})"

        elif action_type == 'check_collision':
            x = params.get('x', 'self.x')
            y = params.get('y', 'self.y')
            only_solid = params.get('only_solid', True)
            return f"# TODO: check_collision at ({x}, {y}, solid={only_solid})"

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
