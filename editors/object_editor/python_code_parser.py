#!/usr/bin/env python3
"""
Python Code Parser for PyGameMaker
Converts Python code to/from event/action JSON format for bidirectional sync
between the Code Editor, Blockly, and Events Panel.
"""

import ast
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass


# ============================================================================
# MAPPING TABLES
# ============================================================================

# Mapping from Python attribute assignments to actions
# Key: (object, attribute) -> action_name
ATTRIBUTE_TO_ACTION = {
    # Movement
    ('self', 'hspeed'): ('set_hspeed', 'value'),
    ('self', 'vspeed'): ('set_vspeed', 'value'),
    ('self', 'x'): ('jump_to_position', 'x'),  # Special handling needed
    ('self', 'y'): ('jump_to_position', 'y'),  # Special handling needed
    ('self', 'direction'): ('set_direction_speed', 'direction'),
    ('self', 'speed'): ('set_direction_speed', 'speed'),
    ('self', 'friction'): ('set_friction', 'friction'),
    ('self', 'gravity'): ('set_gravity', 'gravity'),
    ('self', 'gravity_direction'): ('set_gravity', 'direction'),
    ('self', 'image_alpha'): ('set_alpha', 'alpha'),
    ('self', 'sprite_index'): ('set_sprite', 'sprite'),
    ('self', 'image_speed'): ('set_image_speed', 'speed'),
    ('self', 'image_index'): ('set_image_index', 'frame'),

    # Game state
    ('game', 'score'): ('set_score', 'value'),
    ('game', 'lives'): ('set_lives', 'value'),
    ('game', 'health'): ('set_health', 'value'),
}

# Mapping from Python method calls to actions
# Key: (object, method) -> (action_name, parameter_mapping or None)
METHOD_TO_ACTION = {
    # Instance
    ('self', 'destroy'): ('destroy_instance', {'target': 'self'}),

    # Room navigation
    ('game', 'next_room'): ('next_room', {}),
    ('game', 'previous_room'): ('previous_room', {}),
    ('game', 'restart_room'): ('restart_room', {}),
    ('game', 'goto_room'): ('goto_room', {'room': 0}),  # First arg is room

    # Game control
    ('game', 'end_game'): ('end_game', {}),
    ('game', 'restart_game'): ('restart_game', {}),

    # Movement
    ('self', 'stop'): ('stop_movement', {}),
    ('self', 'reverse_horizontal'): ('reverse_horizontal', {}),
    ('self', 'reverse_vertical'): ('reverse_vertical', {}),
    ('self', 'snap_to_grid'): ('snap_to_grid', {'grid_x': 32, 'grid_y': 32}),

    # Alarm
    ('self', 'set_alarm'): ('set_alarm', {'alarm': 0, 'steps': 0}),
}

# Mapping from action names to Python code templates
ACTION_TO_PYTHON = {
    # Movement
    'set_hspeed': 'self.hspeed = {value}',
    'set_vspeed': 'self.vspeed = {value}',
    'stop_movement': 'self.hspeed = 0\nself.vspeed = 0',
    'reverse_horizontal': 'self.hspeed = -self.hspeed',
    'reverse_vertical': 'self.vspeed = -self.vspeed',
    'set_gravity': 'self.gravity = {gravity}',
    'set_friction': 'self.friction = {friction}',
    'jump_to_position': 'self.x = {x}\nself.y = {y}',
    'jump_to_start': 'self.x = self.xstart\nself.y = self.ystart',
    'snap_to_grid': 'self.x = round(self.x / {grid_x}) * {grid_x}\nself.y = round(self.y / {grid_y}) * {grid_y}',
    'start_moving_direction': 'self.direction = {direction}\nself.speed = {speed}',
    'set_direction_speed': 'self.direction = {direction}\nself.speed = {speed}',

    # Instance
    'destroy_instance': 'self.destroy()',
    'create_instance': 'game.create_instance("{object}", {x}, {y})',

    # Room
    'next_room': 'game.next_room()',
    'previous_room': 'game.previous_room()',
    'restart_room': 'game.restart_room()',
    'goto_room': 'game.goto_room("{room}")',

    # Game control
    'end_game': 'game.end_game()',
    'restart_game': 'game.restart_game()',

    # Score/Lives/Health
    'set_score': 'game.score {op} {value}',  # op is = or +=
    'set_lives': 'game.lives {op} {value}',
    'set_health': 'game.health {op} {value}',

    # Drawing (in draw event)
    'draw_score': 'game.draw_score({x}, {y}, "{caption}")',
    'draw_lives': 'game.draw_lives({x}, {y})',
    'draw_health_bar': 'game.draw_health_bar({x1}, {y1}, {x2}, {y2})',

    # Sprite/Animation
    'set_sprite': 'self.sprite_index = "{sprite}"',
    'set_alpha': 'self.image_alpha = {alpha}',
    'set_image_index': 'self.image_index = {frame}',
    'set_image_speed': 'self.image_speed = {speed}',

    # Alarm
    'set_alarm': 'self.alarm[{alarm}] = {steps}',

    # Sound
    'play_sound': 'game.play_sound("{sound}")',
    'play_music': 'game.play_music("{music}")',
    'stop_music': 'game.stop_music()',

    # Message
    'display_message': 'game.show_message("{message}")',

    # Code execution (passthrough)
    'execute_code': '{code}',
}

# Event name mappings
EVENT_METHOD_NAMES = {
    'create': 'on_create',
    'destroy': 'on_destroy',
    'step': 'on_step',
    'begin_step': 'on_begin_step',
    'end_step': 'on_end_step',
    'draw': 'on_draw',
    'alarm_0': 'on_alarm_0',
    'alarm_1': 'on_alarm_1',
    'alarm_2': 'on_alarm_2',
    'alarm_3': 'on_alarm_3',
    'alarm_4': 'on_alarm_4',
    'alarm_5': 'on_alarm_5',
    'alarm_6': 'on_alarm_6',
    'alarm_7': 'on_alarm_7',
    'alarm_8': 'on_alarm_8',
    'alarm_9': 'on_alarm_9',
    'alarm_10': 'on_alarm_10',
    'alarm_11': 'on_alarm_11',
}

# Reverse mapping for parsing
METHOD_TO_EVENT = {v: k for k, v in EVENT_METHOD_NAMES.items()}


# ============================================================================
# PYTHON TO ACTIONS PARSER
# ============================================================================

@dataclass
class ParseResult:
    """Result of parsing Python code"""
    events: Dict[str, Any]
    errors: List[str]
    warnings: List[str]


class PythonToActionsParser:
    """Parses Python code and extracts action equivalents"""

    def __init__(self):
        self.errors = []
        self.warnings = []

    def parse_event_code(self, code: str, event_name: str) -> Dict[str, Any]:
        """Parse Python code for a single event, return event data with actions"""
        self.errors = []
        self.warnings = []

        try:
            tree = ast.parse(code)
        except SyntaxError as e:
            self.errors.append(f"Syntax error: {e}")
            # Return code as execute_code action
            return {
                "actions": [{"action": "execute_code", "parameters": {"code": code}}]
            }

        actions = self._extract_actions_from_body(tree.body)
        return {"actions": actions}

    def parse_full_class(self, code: str) -> ParseResult:
        """Parse a full class definition with multiple event methods"""
        self.errors = []
        self.warnings = []
        events = {}

        try:
            tree = ast.parse(code)
        except SyntaxError as e:
            self.errors.append(f"Syntax error: {e}")
            return ParseResult(events={}, errors=self.errors, warnings=self.warnings)

        # Find class definition
        for node in ast.walk(tree):
            if isinstance(node, ast.ClassDef):
                events = self._parse_class_methods(node)
                break
        else:
            # No class found - try parsing as module-level code
            # Look for function definitions that match event names
            for node in tree.body:
                if isinstance(node, ast.FunctionDef):
                    event_name = self._method_to_event_name(node.name)
                    if event_name:
                        actions = self._extract_actions_from_body(node.body)
                        events[event_name] = {"actions": actions}

        return ParseResult(events=events, errors=self.errors, warnings=self.warnings)

    def _parse_class_methods(self, class_node: ast.ClassDef) -> Dict[str, Any]:
        """Parse all methods in a class definition"""
        events = {}

        for node in class_node.body:
            if isinstance(node, ast.FunctionDef):
                event_name = self._method_to_event_name(node.name)
                if event_name:
                    # Skip 'self' parameter
                    actions = self._extract_actions_from_body(node.body)

                    # Handle keyboard events specially
                    if event_name.startswith('keyboard_'):
                        # e.g., on_keyboard_right -> keyboard.right
                        parts = event_name.split('_', 1)
                        if len(parts) == 2:
                            base_event = parts[0]  # 'keyboard'
                            key = parts[1]  # 'right'
                            if base_event not in events:
                                events[base_event] = {}
                            events[base_event][key] = {"actions": actions}
                    # Handle collision events - normalize to collision_with_<object> format
                    elif event_name.startswith('collision_'):
                        # e.g., collision_obj_wall -> collision_with_obj_wall
                        target = event_name[10:]  # Remove 'collision_'
                        if not target.startswith('with_'):
                            event_name = f"collision_with_{target}"
                        events[event_name] = {"actions": actions, "target_object": target}
                    else:
                        events[event_name] = {"actions": actions}

        return events

    def _method_to_event_name(self, method_name: str) -> Optional[str]:
        """Convert method name to event name"""
        # Direct mapping
        if method_name in METHOD_TO_EVENT:
            return METHOD_TO_EVENT[method_name]

        # Handle on_ prefix
        if method_name.startswith('on_'):
            event_name = method_name[3:]  # Remove 'on_'
            return event_name

        # Handle keyboard methods
        if method_name.startswith('keyboard_'):
            return method_name

        return None

    def _extract_actions_from_body(self, body: List[ast.stmt]) -> List[Dict[str, Any]]:
        """Extract actions from a list of statements"""
        actions = []
        unrecognized_statements = []

        i = 0
        while i < len(body):
            stmt = body[i]

            # Skip docstrings
            if isinstance(stmt, ast.Expr) and isinstance(stmt.value, ast.Constant) and isinstance(stmt.value.value, str):
                i += 1
                continue

            # Skip pass statements
            if isinstance(stmt, ast.Pass):
                i += 1
                continue

            # Check for stop_movement pattern: self.hspeed = 0; self.vspeed = 0
            if i + 1 < len(body):
                action = self._try_parse_stop_movement(stmt, body[i + 1])
                if action:
                    # Flush accumulated unrecognized code first
                    if unrecognized_statements:
                        code = self._statements_to_code(unrecognized_statements)
                        actions.append({
                            "action": "execute_code",
                            "parameters": {"code": code}
                        })
                        unrecognized_statements = []
                    actions.append(action)
                    i += 2  # Skip both statements
                    continue

            action = self._try_parse_statement(stmt)
            if action:
                # Flush accumulated unrecognized code first
                if unrecognized_statements:
                    code = self._statements_to_code(unrecognized_statements)
                    actions.append({
                        "action": "execute_code",
                        "parameters": {"code": code}
                    })
                    unrecognized_statements = []
                actions.append(action)
            else:
                unrecognized_statements.append(stmt)

            i += 1

        # Flush remaining unrecognized statements
        if unrecognized_statements:
            code = self._statements_to_code(unrecognized_statements)
            actions.append({
                "action": "execute_code",
                "parameters": {"code": code}
            })

        return actions

    def _try_parse_stop_movement(self, stmt1: ast.stmt, stmt2: ast.stmt) -> Optional[Dict[str, Any]]:
        """Try to parse two consecutive assignments as stop_movement action"""
        # Check if both are self.hspeed = 0 and self.vspeed = 0 (in any order)
        if not (isinstance(stmt1, ast.Assign) and isinstance(stmt2, ast.Assign)):
            return None

        assignments = {}
        for stmt in [stmt1, stmt2]:
            if len(stmt.targets) != 1:
                return None
            target = stmt.targets[0]
            if not (isinstance(target, ast.Attribute) and
                    isinstance(target.value, ast.Name) and
                    target.value.id == 'self' and
                    target.attr in ('hspeed', 'vspeed')):
                return None
            value = self._eval_value(stmt.value)
            if value != 0:
                return None
            assignments[target.attr] = value

        # Must have both hspeed and vspeed set to 0
        if 'hspeed' in assignments and 'vspeed' in assignments:
            return {"action": "stop_movement", "parameters": {}}

        return None

    def _try_parse_statement(self, stmt: ast.stmt) -> Optional[Dict[str, Any]]:
        """Try to parse a statement as an action"""
        if isinstance(stmt, ast.Assign):
            return self._try_parse_assignment(stmt)
        elif isinstance(stmt, ast.AugAssign):
            return self._try_parse_aug_assignment(stmt)
        elif isinstance(stmt, ast.Expr) and isinstance(stmt.value, ast.Call):
            return self._try_parse_call(stmt.value)
        return None

    def _try_parse_assignment(self, stmt: ast.Assign) -> Optional[Dict[str, Any]]:
        """Try to parse an assignment as an action"""
        if len(stmt.targets) != 1:
            return None

        target = stmt.targets[0]
        value = stmt.value

        # Handle self.attr = value or game.attr = value
        if isinstance(target, ast.Attribute) and isinstance(target.value, ast.Name):
            obj_name = target.value.id
            attr_name = target.attr

            key = (obj_name, attr_name)
            if key in ATTRIBUTE_TO_ACTION:
                action_name, param_name = ATTRIBUTE_TO_ACTION[key]
                param_value = self._eval_value(value)
                return {
                    "action": action_name,
                    "parameters": {param_name: param_value, "relative": False}
                }

        # Handle self.alarm[n] = value
        if isinstance(target, ast.Subscript):
            if (isinstance(target.value, ast.Attribute) and
                isinstance(target.value.value, ast.Name) and
                target.value.value.id == 'self' and
                target.value.attr == 'alarm'):
                alarm_num = self._eval_value(target.slice)
                steps = self._eval_value(value)
                return {
                    "action": "set_alarm",
                    "parameters": {"alarm": alarm_num, "steps": steps}
                }

        return None

    def _try_parse_aug_assignment(self, stmt: ast.AugAssign) -> Optional[Dict[str, Any]]:
        """Try to parse augmented assignment (+=, -=, etc.) as an action"""
        target = stmt.target
        value = stmt.value

        # Handle game.score += value, etc.
        if isinstance(target, ast.Attribute) and isinstance(target.value, ast.Name):
            obj_name = target.value.id
            attr_name = target.attr

            key = (obj_name, attr_name)
            if key in ATTRIBUTE_TO_ACTION:
                action_name, param_name = ATTRIBUTE_TO_ACTION[key]
                param_value = self._eval_value(value)

                # Handle -= as negative relative
                if isinstance(stmt.op, ast.Sub):
                    param_value = -param_value if isinstance(param_value, (int, float)) else f"-({param_value})"

                return {
                    "action": action_name,
                    "parameters": {param_name: param_value, "relative": True}
                }

        return None

    def _try_parse_call(self, call: ast.Call) -> Optional[Dict[str, Any]]:
        """Try to parse a method call as an action"""
        # Handle self.method() or game.method()
        if isinstance(call.func, ast.Attribute) and isinstance(call.func.value, ast.Name):
            obj_name = call.func.value.id
            method_name = call.func.attr

            key = (obj_name, method_name)
            if key in METHOD_TO_ACTION:
                action_name, default_params = METHOD_TO_ACTION[key]
                params = dict(default_params)

                # Extract arguments
                if call.args:
                    if action_name == 'goto_room' and call.args:
                        params['room'] = self._eval_value(call.args[0])
                    elif action_name == 'set_alarm' and len(call.args) >= 2:
                        params['alarm'] = self._eval_value(call.args[0])
                        params['steps'] = self._eval_value(call.args[1])
                    elif action_name == 'snap_to_grid' and len(call.args) >= 2:
                        params['grid_x'] = self._eval_value(call.args[0])
                        params['grid_y'] = self._eval_value(call.args[1])

                return {"action": action_name, "parameters": params}

        # Handle game.create_instance("object", x, y)
        if (isinstance(call.func, ast.Attribute) and
            isinstance(call.func.value, ast.Name) and
            call.func.value.id == 'game' and
            call.func.attr == 'create_instance'):
            if len(call.args) >= 3:
                return {
                    "action": "create_instance",
                    "parameters": {
                        "object": self._eval_value(call.args[0]),
                        "x": self._eval_value(call.args[1]),
                        "y": self._eval_value(call.args[2]),
                        "relative": False
                    }
                }

        # Handle game.show_message("text")
        if (isinstance(call.func, ast.Attribute) and
            isinstance(call.func.value, ast.Name) and
            call.func.value.id == 'game' and
            call.func.attr == 'show_message'):
            if call.args:
                return {
                    "action": "display_message",
                    "parameters": {"message": self._eval_value(call.args[0])}
                }

        # Handle game.play_sound("sound")
        if (isinstance(call.func, ast.Attribute) and
            isinstance(call.func.value, ast.Name) and
            call.func.value.id == 'game' and
            call.func.attr == 'play_sound'):
            if call.args:
                return {
                    "action": "play_sound",
                    "parameters": {"sound": self._eval_value(call.args[0])}
                }

        return None

    def _eval_value(self, node: ast.expr) -> Any:
        """Evaluate a simple value expression"""
        if isinstance(node, ast.Constant):
            return node.value
        elif isinstance(node, ast.Num):  # Python 3.7 compatibility
            return node.n
        elif isinstance(node, ast.Str):  # Python 3.7 compatibility
            return node.s
        elif isinstance(node, ast.Name):
            return node.id
        elif isinstance(node, ast.UnaryOp) and isinstance(node.op, ast.USub):
            val = self._eval_value(node.operand)
            if isinstance(val, (int, float)):
                return -val
            return f"-{val}"
        elif isinstance(node, ast.Attribute):
            # Handle self.x, game.score, etc.
            if isinstance(node.value, ast.Name):
                return f"{node.value.id}.{node.attr}"
        elif isinstance(node, ast.BinOp):
            left = self._eval_value(node.left)
            right = self._eval_value(node.right)
            op = self._get_op_str(node.op)
            return f"{left} {op} {right}"

        # Fallback: convert to source code
        try:
            return ast.unparse(node)
        except:
            return str(node)

    def _get_op_str(self, op: ast.operator) -> str:
        """Get string representation of operator"""
        ops = {
            ast.Add: '+', ast.Sub: '-', ast.Mult: '*', ast.Div: '/',
            ast.Mod: '%', ast.Pow: '**', ast.FloorDiv: '//'
        }
        return ops.get(type(op), '?')

    def _statements_to_code(self, statements: List[ast.stmt]) -> str:
        """Convert AST statements back to code"""
        try:
            # Create a module with these statements
            module = ast.Module(body=statements, type_ignores=[])
            return ast.unparse(module)
        except:
            # Fallback
            return "# Unable to convert statements"


# ============================================================================
# ACTIONS TO PYTHON GENERATOR
# ============================================================================

class ActionsToPythonGenerator:
    """Generates Python code from action JSON"""

    def __init__(self):
        self.indent = "    "

    def generate_event_code(self, event_name: str, event_data: Dict[str, Any]) -> str:
        """Generate Python code for a single event"""
        actions = event_data.get("actions", [])
        lines = []

        for action in actions:
            action_code = self._generate_action_code(action)
            if action_code:
                lines.append(action_code)

        return "\n".join(lines) if lines else "pass"

    def generate_full_class(self, object_name: str, events_data: Dict[str, Any]) -> str:
        """Generate a complete Python class with all event methods"""
        lines = [
            f"class {self._sanitize_name(object_name)}:",
            f'{self.indent}"""Object: {object_name}"""',
            ""
        ]

        if not events_data:
            lines.append(f"{self.indent}pass")
            return "\n".join(lines)

        for event_name, event_data in events_data.items():
            # Handle nested keyboard events
            if event_name in ('keyboard', 'keyboard_press', 'keyboard_release'):
                if isinstance(event_data, dict) and 'actions' not in event_data:
                    # Nested key events
                    for key_name, key_data in event_data.items():
                        if isinstance(key_data, dict) and 'actions' in key_data:
                            method_name = f"on_{event_name}_{key_name}"
                            method_code = self._generate_method(method_name, key_data)
                            lines.append(method_code)
                            lines.append("")
                    continue

            # Handle collision events
            if event_name.startswith('collision_with_'):
                target = event_name.replace('collision_with_', '')
                method_name = f"on_collision_{target}"
            else:
                method_name = EVENT_METHOD_NAMES.get(event_name, f"on_{event_name}")

            method_code = self._generate_method(method_name, event_data)
            lines.append(method_code)
            lines.append("")

        # Remove trailing empty line
        while lines and lines[-1] == "":
            lines.pop()

        return "\n".join(lines)

    def _generate_method(self, method_name: str, event_data: Dict[str, Any]) -> str:
        """Generate a method definition"""
        lines = [f"{self.indent}def {method_name}(self):"]

        actions = event_data.get("actions", [])
        if not actions:
            lines.append(f"{self.indent}{self.indent}pass")
        else:
            for action in actions:
                action_code = self._generate_action_code(action)
                if action_code:
                    # Handle multi-line code
                    for line in action_code.split('\n'):
                        lines.append(f"{self.indent}{self.indent}{line}")

        return "\n".join(lines)

    def _generate_action_code(self, action: Dict[str, Any]) -> str:
        """Generate Python code for a single action"""
        action_name = action.get("action", "")
        params = action.get("parameters", {})

        # Handle execute_code specially
        if action_name == "execute_code":
            return params.get("code", "pass")

        template = ACTION_TO_PYTHON.get(action_name)
        if not template:
            # Unknown action - generate comment
            return f"# Unknown action: {action_name}"

        # Normalize parameters - handle different parameter naming conventions
        # The action system uses different names than the templates expect
        params = dict(params)  # Copy to avoid modifying original

        # Handle hspeed/vspeed actions - normalize 'hspeed', 'vspeed', 'speed' to 'value'
        if action_name == 'set_hspeed':
            if 'value' not in params:
                params['value'] = params.get('hspeed', params.get('speed', 0))
        elif action_name == 'set_vspeed':
            if 'value' not in params:
                params['value'] = params.get('vspeed', params.get('speed', 0))

        # Handle relative operations for score/lives/health
        if action_name in ('set_score', 'set_lives', 'set_health'):
            relative = params.get('relative', False)
            params['op'] = '+=' if relative else '='

        # Format template with parameters
        try:
            return template.format(**params)
        except KeyError as e:
            return f"# Missing parameter {e} for {action_name}"

    def _sanitize_name(self, name: str) -> str:
        """Sanitize name to be a valid Python identifier"""
        # Replace invalid characters
        result = ""
        for c in name:
            if c.isalnum() or c == '_':
                result += c
            else:
                result += '_'

        # Ensure it doesn't start with a number
        if result and result[0].isdigit():
            result = '_' + result

        return result or "UnnamedObject"


# ============================================================================
# CONVENIENCE FUNCTIONS
# ============================================================================

def python_to_events(code: str) -> Tuple[Dict[str, Any], List[str]]:
    """
    Convert Python code to events dictionary.
    Returns (events_dict, errors_list)
    """
    parser = PythonToActionsParser()
    result = parser.parse_full_class(code)
    return result.events, result.errors


def events_to_python(object_name: str, events: Dict[str, Any]) -> str:
    """
    Convert events dictionary to Python code.
    Returns Python code string.
    """
    generator = ActionsToPythonGenerator()
    return generator.generate_full_class(object_name, events)


def event_to_python(event_name: str, event_data: Dict[str, Any]) -> str:
    """
    Convert a single event to Python code.
    Returns Python code string.
    """
    generator = ActionsToPythonGenerator()
    return generator.generate_event_code(event_name, event_data)
