#!/usr/bin/env python3
"""
Kivy Exporter for PyGameMaker IDE
Exports projects to Kivy format for mobile deployment
"""

from typing import Dict

from core.logger import get_logger
logger = get_logger(__name__)


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
        # Auto-close any remaining open blocks
        while self.block_stack:
            self.block_stack.pop()
            self.pop_indent()
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

        elif action_type == 'else_action' or action_type == 'else_block':
            # Else clause - pop indent, add else, push indent
            self.pop_indent()
            self.add_line("else:")
            self.push_indent()
            if self.block_stack and self.block_stack[-1] in ['if', 'if_on_grid', 'if_next_room_exists', 'if_previous_room_exists']:
                self.block_stack[-1] = 'else'
            return

        # CONDITIONAL ACTIONS (these start blocks)
        elif action_type == 'if_on_grid':
            self.add_line("if self.is_on_grid():")
            self.push_indent()
            self.block_stack.append('if_on_grid')
            # Snap to exact grid position when on grid
            self.add_line("self.snap_to_grid()")

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

        elif action_type == 'if_collision_at':
            # Check for collision at specified position (alias for if_collision)
            obj_name = params.get('object', params.get('target', 'object'))
            x = params.get('x', 'self.x')
            y = params.get('y', 'self.y')
            self.add_line(f"if self.check_collision_at({x}, {y}, '{obj_name}'):")
            self.push_indent()
            self.block_stack.append('if')
            return

        elif action_type == 'check_collision':
            # Check for collision - if collision exists, execute then block
            obj_name = params.get('object', params.get('target', 'object'))
            x = params.get('x', 'self.x')
            y = params.get('y', 'self.y')
            self.add_line(f"if self.check_collision_at({x}, {y}, '{obj_name}'):")
            self.push_indent()
            self.block_stack.append('if')
            return

        elif action_type == 'check_empty':
            # Check if position is collision-free
            x = params.get('x', 'self.x')
            y = params.get('y', 'self.y')
            # relative parameter means offset from current position
            relative = params.get('relative', False)
            if relative:
                self.add_line(f"if not self.check_collision_at(self.x + {x}, self.y + {y}):")
            else:
                self.add_line(f"if not self.check_collision_at({x}, {y}):")
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

        elif action_type == 'if_next_room_exists':
            self.add_line("from main import next_room_exists, _room_transition_pending")
            self.add_line("if _room_transition_pending:")
            self.push_indent()
            self.add_line("pass  # Room transition already in progress")
            self.pop_indent()
            self.add_line("elif next_room_exists():")
            self.push_indent()
            self.block_stack.append('if_next_room_exists')

            # Process nested then_actions if present (for nested action structure)
            then_actions = params.get('then_actions', [])
            if then_actions:
                for nested_action in then_actions:
                    if isinstance(nested_action, dict):
                        self.process_action(nested_action, event_type)
                # Pop indent after processing then actions
                self.pop_indent()

                # Process else_actions if present
                else_actions = params.get('else_actions', [])
                if else_actions:
                    self.add_line("else:")
                    self.push_indent()
                    for nested_action in else_actions:
                        if isinstance(nested_action, dict):
                            self.process_action(nested_action, event_type)
                    self.pop_indent()

                if self.block_stack and self.block_stack[-1] == 'if_next_room_exists':
                    self.block_stack.pop()
            # If no then_actions, leave block open for sequential action handling
            return

        elif action_type == 'if_previous_room_exists':
            self.add_line("from main import previous_room_exists, _room_transition_pending")
            self.add_line("if _room_transition_pending:")
            self.push_indent()
            self.add_line("pass  # Room transition already in progress")
            self.pop_indent()
            self.add_line("elif previous_room_exists():")
            self.push_indent()
            self.block_stack.append('if_previous_room_exists')

            # Process nested then_actions if present (for nested action structure)
            then_actions = params.get('then_actions', [])
            if then_actions:
                for nested_action in then_actions:
                    if isinstance(nested_action, dict):
                        self.process_action(nested_action, event_type)
                # Pop indent after processing then actions
                self.pop_indent()

                # Process else_actions if present
                else_actions = params.get('else_actions', [])
                if else_actions:
                    self.add_line("else:")
                    self.push_indent()
                    for nested_action in else_actions:
                        if isinstance(nested_action, dict):
                            self.process_action(nested_action, event_type)
                    self.pop_indent()

                if self.block_stack and self.block_stack[-1] == 'if_previous_room_exists':
                    self.block_stack.pop()
            # If no then_actions, leave block open for sequential action handling
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
            # KIVY COORDINATE FIX: Flip vspeed sign
            # GameMaker: Y=0 at top, increases downward. UP = negative vspeed
            # Kivy: Y=0 at bottom, increases upward. UP = positive vspeed
            # So: kivy_vspeed = -gamemaker_vspeed
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

        elif action_type == 'move_towards':
            # Move towards a specific point at given speed
            x = params.get('x', 0)
            y = params.get('y', 0)
            speed = params.get('speed', 4)
            return f"""import math
dx = {x} - self.x
dy = {y} - self.y
dist = math.sqrt(dx*dx + dy*dy)
if dist > 0:
    self.hspeed = (dx / dist) * {speed}
    self.vspeed = (dy / dist) * {speed}"""

        elif action_type == 'set_gravity':
            # Set gravity direction and strength
            direction = params.get('direction', 270)  # Default: down
            gravity = params.get('gravity', params.get('value', 0.5))
            return f"self.gravity = {gravity}; self.gravity_direction = {direction}"

        elif action_type == 'set_friction':
            # Set friction/deceleration
            friction = params.get('friction', params.get('value', 0.1))
            return f"self.friction = {friction}"

        elif action_type == 'reverse_horizontal':
            # Reverse horizontal direction
            return "self.hspeed = -self.hspeed"

        elif action_type == 'reverse_vertical':
            # Reverse vertical direction
            return "self.vspeed = -self.vspeed"

        elif action_type == 'exit_event':
            # Stop executing remaining actions in this event
            return "return"

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

        # ROOM ACTIONS
        elif action_type == 'next_room':
            return "from main import goto_next_room; goto_next_room()"

        elif action_type == 'previous_room':
            return "from main import goto_previous_room; goto_previous_room()"

        elif action_type == 'goto_room':
            room_name = params.get('room', params.get('room_name', ''))
            return f"from main import goto_room; goto_room('{room_name}')"

        elif action_type == 'restart_room':
            return "from main import get_game_app; app = get_game_app(); app._switch_to_room(app.current_room_index) if app else None"

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

        # DEFAULT
        else:
            logger.warning(f"Unknown action type '{action_type}'")
            return f"pass  # TODO: {action_type}"


