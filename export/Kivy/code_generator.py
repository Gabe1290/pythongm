#!/usr/bin/env python3
"""
Kivy Code Generator for PyGameMaker IDE
Converts GameMaker-style events and actions to Kivy Python code
"""

import logging
from pathlib import Path
from typing import Dict, List, Any, Optional
from jinja2 import Environment, FileSystemLoader, Template

logger = logging.getLogger(__name__)


class KivyCodeGenerator:
    """
    Generates Kivy Python code from GameMaker project data.
    Uses Jinja2 templates to create main app, game objects, and scenes.
    """
    
    def __init__(self, project_data: Dict[str, Any], output_path: Path, templates_path: Path):
        """
        Initialize the code generator.
        
        Args:
            project_data: Complete project data dictionary
            output_path: Path where generated code will be saved
            templates_path: Path to Jinja2 template files
        """
        self.project_data = project_data
        self.output_path = output_path
        self.templates_path = templates_path
        
        # Initialize Jinja2 environment
        self.jinja_env = Environment(
            loader=FileSystemLoader(str(templates_path)),
            trim_blocks=True,
            lstrip_blocks=True
        )
        
        # Extract project components
        self.objects = project_data.get("objects", {})
        self.rooms = project_data.get("rooms", {})
        self.sprites = project_data.get("sprites", {})
        self.sounds = project_data.get("sounds", {})
        self.backgrounds = project_data.get("backgrounds", {})
        self.settings = project_data.get("settings", {})
        
        logger.info("Code generator initialized")
    
    def generate_main_py(self) -> str:
        """
        Generate the main.py file for the Kivy application.
        
        Returns:
            str: Generated Python code for main.py
        """
        logger.info("Generating main.py...")
        
        try:
            template = self._load_template("main.py.template")
            
            # Prepare template variables
            project_name = self.project_data.get("name", "KivyGame")
            window_width = self.settings.get("width", 800)
            window_height = self.settings.get("height", 600)
            
            # Get initial room (first room in the list)
            initial_room = None
            if self.rooms:
                initial_room = list(self.rooms.keys())[0]
                logger.info(f"Initial room set to: {initial_room}")
            else:
                logger.warning("NO ROOMS FOUND IN PROJECT - Generated app will show blank screen")

            # Get list of all rooms for imports
            room_names = list(self.rooms.keys())
            logger.info(f"Total rooms: {len(room_names)}")
            logger.info(f"Room names: {room_names}")
            
            # Get list of all objects for imports
            object_names = list(self.objects.keys())
            
            context = {
                'project_name': project_name,
                'window_width': window_width,
                'window_height': window_height,
                'initial_room': initial_room,
                'room_names': room_names,
                'object_names': object_names,
            }
            
            code = template.render(**context)
            logger.info("main.py generated successfully")
            return code
            
        except Exception as e:
            logger.error(f"Failed to generate main.py: {e}", exc_info=True)
            raise
    
    def generate_game_objects(self) -> Dict[str, str]:
        """
        Generate Python class files for all game objects.
        
        Returns:
            Dict[str, str]: Dictionary mapping object names to generated code
        """
        logger.info(f"Generating {len(self.objects)} game object classes...")
        
        object_files = {}
        
        try:
            template = self._load_template("game_object.py.template")
            
            for obj_name, obj_data in self.objects.items():
                logger.debug(f"Generating object: {obj_name}")
                
                # Get sprite information
                sprite_name = obj_data.get("sprite")
                sprite_path = None
                if sprite_name and sprite_name in self.sprites:
                    sprite_info = self.sprites[sprite_name]
                    if sprite_info.get("frames"):
                        sprite_path = f"assets/sprites/{sprite_name}/{sprite_info['frames'][0].get('image', '')}"
                
                # Convert events to Kivy code
                events = obj_data.get("events", {})
                converted_events = self._convert_events_to_kivy(events, obj_name)
                
                # Get object properties
                visible = obj_data.get("visible", True)
                solid = obj_data.get("solid", False)
                persistent = obj_data.get("persistent", False)
                depth = obj_data.get("depth", 0)
                
                context = {
                    'object_name': obj_name,
                    'sprite_path': sprite_path,
                    'sprite_name': sprite_name,
                    'events': converted_events,
                    'visible': visible,
                    'solid': solid,
                    'persistent': persistent,
                    'depth': depth,
                }
                
                code = template.render(**context)
                object_files[obj_name] = code
                
            logger.info(f"Generated {len(object_files)} object classes successfully")
            return object_files
            
        except Exception as e:
            logger.error(f"Failed to generate game objects: {e}", exc_info=True)
            raise
    
    def generate_scenes(self) -> Dict[str, str]:
        """
        Generate Python class files for all scenes/rooms.
        
        Returns:
            Dict[str, str]: Dictionary mapping scene names to generated code
        """
        logger.info(f"Generating {len(self.rooms)} scene classes...")
        
        scene_files = {}
        
        try:
            template = self._load_template("scene.py.template")
            
            for room_name, room_data in self.rooms.items():
                logger.debug(f"Generating scene: {room_name}")
                
                # Get room dimensions
                width = room_data.get("width", 800)
                height = room_data.get("height", 600)
                
                # Get background information
                bg_name = room_data.get("background")
                bg_path = None
                bg_color = room_data.get("background_color", "#000000")
                
                if bg_name and bg_name in self.backgrounds:
                    bg_info = self.backgrounds[bg_name]
                    bg_path = f"assets/backgrounds/{bg_info.get('image', '')}"
                
                # Get room instances
                instances = room_data.get("instances", [])
                converted_instances = self._convert_instances_to_kivy(instances)
                
                # Get list of unique objects used in this room
                unique_objects = list(set([inst.get("object_name") or inst.get("object") or inst.get("object_type") for inst in instances if inst.get("object_name") or inst.get("object") or inst.get("object_type")]))
                
                context = {
                    'room_name': room_name,
                    'width': width,
                    'height': height,
                    'background_path': bg_path,
                    'background_color': bg_color,
                    'instances': converted_instances,
                    'object_types': unique_objects,
                }
                
                code = template.render(**context)
                scene_files[room_name] = code
                
            logger.info(f"Generated {len(scene_files)} scene classes successfully")
            return scene_files
            
        except Exception as e:
            logger.error(f"Failed to generate scenes: {e}", exc_info=True)
            raise
    
    def _load_template(self, template_name: str) -> Template:
        """
        Load a Jinja2 template by name.
        
        Args:
            template_name: Name of the template file
            
        Returns:
            Template: Loaded Jinja2 template
        """
        try:
            template = self.jinja_env.get_template(template_name)
            logger.debug(f"Loaded template: {template_name}")
            return template
        except Exception as e:
            logger.error(f"Failed to load template {template_name}: {e}")
            raise
    
    def _convert_events_to_kivy(self, events: Dict[str, Any], object_name: str) -> Dict[str, Any]:
            """
            Convert GameMaker events to Kivy event handlers.
            Now uses ActionConverter for proper action handling.
            """
            from .action_converter import ActionConverter
            
            converted = {
                'create': None,
                'step': None,
                'keyboard': {},
                'collision': {},
                'draw': None,
            }
            
            converter = ActionConverter(grid_size=32)
            
            for event_type, event_data in events.items():
                if event_type == "create":
                    actions = event_data.get('actions', [])
                    converted['create'] = converter.convert_actions(actions, indent_level=2)
                    
                elif event_type == "step":
                    actions = event_data.get('actions', [])
                    converted['step'] = converter.convert_actions(actions, indent_level=2)
                    
                elif event_type == "keyboard":
                    # Keyboard events have sub-keys (left, right, up, down, etc.)
                    for key, key_data in event_data.items():
                        actions = key_data.get('actions', [])
                        converted['keyboard'][key] = converter.convert_actions(actions, indent_level=3)
                        
                elif event_type.startswith("collision_with_"):
                    # Extract target object name
                    collision_obj = event_type.replace("collision_with_", "")
                    actions = event_data.get('actions', [])
                    converted['collision'][collision_obj] = converter.convert_actions(actions, indent_level=2)
                    
                elif event_type == "draw":
                    actions = event_data.get('actions', [])
                    converted['draw'] = converter.convert_actions(actions, indent_level=2)
                    
                else:
                    logger.warning(f"{object_name}: Unsupported event type: {event_type}")
            
            return converted
    
    def _convert_create_event(self, event_list: List[Dict]) -> str:
        """Convert Create event actions to Kivy code."""
        code_lines = []
        
        for event in event_list:
            actions = event.get("actions", [])
            for action in actions:
                action_code = self._convert_action_to_kivy(action)
                if action_code:
                    code_lines.append(action_code)
        
        return "\n        ".join(code_lines) if code_lines else "pass"
    
    def _convert_step_event(self, event_list: List[Dict]) -> str:
        """Convert Step event actions to Kivy code."""
        code_lines = []
        
        for event in event_list:
            actions = event.get("actions", [])
            for action in actions:
                action_code = self._convert_action_to_kivy(action)
                if action_code:
                    code_lines.append(action_code)
        
        return "\n        ".join(code_lines) if code_lines else "pass"
    
    def _convert_keyboard_event(self, event_list: List[Dict], key: str) -> str:
        """Convert Keyboard event actions to Kivy code."""
        code_lines = []
        
        for event in event_list:
            actions = event.get("actions", [])
            for action in actions:
                action_code = self._convert_action_to_kivy(action)
                if action_code:
                    code_lines.append(action_code)
        
        return "\n            ".join(code_lines) if code_lines else "pass"
    
    def _convert_collision_event(self, event_list: List[Dict], collision_obj: str) -> str:
        """Convert Collision event actions to Kivy code."""
        code_lines = []
        
        for event in event_list:
            actions = event.get("actions", [])
            for action in actions:
                action_code = self._convert_action_to_kivy(action)
                if action_code:
                    code_lines.append(action_code)
        
        return "\n            ".join(code_lines) if code_lines else "pass"
    
    def _convert_draw_event(self, event_list: List[Dict]) -> str:
        """Convert Draw event actions to Kivy code."""
        code_lines = []
        
        for event in event_list:
            actions = event.get("actions", [])
            for action in actions:
                action_code = self._convert_action_to_kivy(action)
                if action_code:
                    code_lines.append(action_code)
        
        return "\n        ".join(code_lines) if code_lines else "pass"
    
    def _convert_action_to_kivy(self, action: Dict[str, Any]) -> str:
        """
        Convert a single GameMaker action to Kivy Python code.
        
        Args:
            action: Action data dictionary
            
        Returns:
            str: Generated Python code for the action
        """
        action_type = action.get("action")
        args = action.get("args", {})
        
        # Movement actions
        if action_type == "Move":
            direction = args.get("direction", "right")
            speed = args.get("speed", 5)
            return self._generate_move_code(direction, speed)
        
        elif action_type == "Set Speed":
            speed = args.get("speed", 0)
            return f"self.speed = {speed}"
        
        elif action_type == "Set Direction":
            direction = args.get("direction", 0)
            return f"self.direction = {direction}"
        
        # Position actions
        elif action_type == "Jump to Position":
            x = args.get("x", 0)
            y = args.get("y", 0)
            relative = args.get("relative", False)
            if relative:
                return f"self.pos = (self.pos[0] + {x}, self.pos[1] + {y})"
            else:
                return f"self.pos = ({x}, {y})"
        
        # Object actions
        elif action_type == "Create Instance":
            obj = args.get("object", "")
            x = args.get("x", 0)
            y = args.get("y", 0)
            return f"self.scene.create_instance('{obj}', {x}, {y})"
        
        elif action_type == "Destroy Instance":
            return "self.destroy()"
        
        # Variable actions
        elif action_type == "Set Variable":
            var_name = args.get("variable", "temp")
            value = args.get("value", 0)
            return f"self.{var_name} = {value}"
        
        # Room actions
        elif action_type == "Go to Room":
            room = args.get("room", "")
            return f"self.game.change_room('{room}')"
        
        elif action_type == "Restart Room":
            return "self.game.restart_room()"
        
        # Game actions
        elif action_type == "End Game":
            return "self.game.end_game()"
        
        # Sound actions
        elif action_type == "Play Sound":
            sound = args.get("sound", "")
            loop = args.get("loop", False)
            return f"self.play_sound('{sound}', loop={loop})"
        
        elif action_type == "Stop Sound":
            sound = args.get("sound", "")
            return f"self.stop_sound('{sound}')"
        
        # Sprite actions
        elif action_type == "Change Sprite":
            sprite = args.get("sprite", "")
            return f"self.change_sprite('{sprite}')"
        
        # Message actions
        elif action_type == "Show Message":
            message = args.get("message", "")
            return f"print('{message}')"
        
        else:
            logger.warning(f"Unsupported action type: {action_type}")
            return f"# TODO: Implement action: {action_type}"
    
    def _generate_move_code(self, direction: str, speed: int) -> str:
        """
        Generate movement code for a given direction.
        
        Args:
            direction: Direction to move (right, left, up, down)
            speed: Movement speed in pixels
            
        Returns:
            str: Generated movement code
        """
        direction_map = {
            "right": (speed, 0),
            "left": (-speed, 0),
            "up": (0, -speed),
            "down": (0, speed),
        }
        
        dx, dy = direction_map.get(direction.lower(), (0, 0))
        return f"self.pos = (self.pos[0] + {dx}, self.pos[1] + {dy})"
    
    def _convert_instances_to_kivy(self, instances: List[Dict]) -> List[Dict]:
            """
            Convert room instances to Kivy-compatible format.
            
            Args:
                instances: List of instance data dictionaries
                
            Returns:
                List[Dict]: Converted instance data
            """
            converted = []
            
            for instance in instances:
                # Get object type from multiple possible field names
                obj_type = (instance.get("object_name") or 
                        instance.get("object") or 
                        instance.get("object_type") or 
                        "")
                
                x = instance.get("x", 0)
                y = instance.get("y", 0)
                
                # Get creation code if available
                creation_code = instance.get("creation_code", "")
                
                converted.append({
                    'object_type': obj_type,
                    'x': x,
                    'y': y,
                    'creation_code': creation_code,
                })
            
            return converted


# Export the main class
__all__ = ['KivyCodeGenerator']
