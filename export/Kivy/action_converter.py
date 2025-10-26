"""
GameMaker Action Converter for Kivy Export
Converts PyGameMaker IDE actions to Kivy Python code
"""

from typing import Dict, List, Any, Optional


class ActionConverter:
    """
    Converts GameMaker-style actions to executable Kivy Python code.
    Handles grid-based movement, speed control, collisions, and conditionals.
    """
    
    def __init__(self, grid_size: int = 32):
        """
        Initialize the action converter.
        
        Args:
            grid_size: Default grid size for grid-based actions
        """
        self.grid_size = grid_size
        self.indent_level = 2  # Base indentation (8 spaces)
    
    def convert_actions(self, actions, indent_level: int = 2) -> str:
        """
        Convert a list of actions to Python code.
        
        Args:
            actions: List of action dictionaries or strings, or a single string
            indent_level: Current indentation level (number of 4-space indents)
            
        Returns:
            str: Generated Python code
        """
        if not actions:
            return self._indent("pass", indent_level)
        
        # Handle case where actions is a single string
        if isinstance(actions, str):
            actions = actions.strip()
            if not actions:
                return self._indent("pass", indent_level)
            
            # Custom code - just indent it properly
            lines = actions.split('\n')
            indented_lines = []
            for line in lines:
                stripped = line.strip()
                if stripped:
                    indented_lines.append(self._indent(line.rstrip(), indent_level))
                else:
                    indented_lines.append('')
            
            result = '\n'.join(indented_lines)
            if not result.strip():
                return self._indent("pass", indent_level)
            return result
        
        code_lines = []
        for action in actions:
            action_code = self._convert_single_action(action, indent_level)
            if action_code:
                code_lines.append(action_code)
        
        return '\n'.join(code_lines) if code_lines else self._indent("pass", indent_level)
    
    def _convert_single_action(self, action, indent_level: int) -> str:
        """Convert a single action to Python code."""
        # Handle string actions (custom code)
        if isinstance(action, str):
            action = action.strip()
            if not action:
                return ""
            
            # Check if it's just a word (incomplete action)
            if action.isidentifier():
                return self._indent(f"# TODO: Implement action: {action}", indent_level)
            
            # Properly indent the action code
            action_lines = action.split('\n')
            indented = []
            for line in action_lines:
                if line.strip():
                    indented.append(self._indent(line.rstrip(), indent_level))
            return '\n'.join(indented) if indented else ""
        
        # Handle dictionary actions
        if not isinstance(action, dict):
            return self._indent(f"# TODO: Unknown action format: {type(action).__name__}", indent_level)
        
        action_type = action.get('action', '')
        parameters = action.get('parameters', {})
        
        # Map action types to converter methods
        converter_map = {
            'if_on_grid': self._convert_if_on_grid,
            'set_hspeed': self._convert_set_hspeed,
            'set_vspeed': self._convert_set_vspeed,
            'set_speed': self._convert_set_speed,
            'set_direction': self._convert_set_direction,
            'stop_movement': self._convert_stop_movement,
            'snap_to_grid': self._convert_snap_to_grid,
            'stop_if_no_keys': self._convert_stop_if_no_keys,
            'destroy_instance': self._convert_destroy_instance,
            'create_instance': self._convert_create_instance,
            'jump_to_position': self._convert_jump_to_position,
            'set_variable': self._convert_set_variable,
            'play_sound': self._convert_play_sound,
            'stop_sound': self._convert_stop_sound,
            # NEW: Smooth movement actions (no grid restrictions)
            'set_hspeed_smooth': self._convert_set_hspeed_smooth,
            'set_vspeed_smooth': self._convert_set_vspeed_smooth,
            'move_right_smooth': self._convert_move_right_smooth,
            'move_left_smooth': self._convert_move_left_smooth,
            'move_up_smooth': self._convert_move_up_smooth,
            'move_down_smooth': self._convert_move_down_smooth,
        }
        
        converter = converter_map.get(action_type)
        if converter:
            return converter(parameters, indent_level)
        else:
            return self._indent(f"# TODO: Implement action '{action_type}'", indent_level)
    
    def _convert_if_on_grid(self, params: Dict[str, Any], indent_level: int) -> str:
        """Convert if_on_grid conditional action."""
        grid_size = params.get('grid_size', self.grid_size)
        then_actions = params.get('then_actions', [])
        else_actions = params.get('else_actions', [])
        
        code_lines = []
        
        # Check if on grid
        code_lines.append(self._indent(f"# Check if aligned to {grid_size}px grid", indent_level))
        code_lines.append(self._indent(f"if self.x % {grid_size} == 0 and self.y % {grid_size} == 0:", indent_level))
        
        # Then branch
        if then_actions:
            then_code = self.convert_actions(then_actions, indent_level + 1)
            code_lines.append(then_code)
        else:
            code_lines.append(self._indent("pass", indent_level + 1))
        
        # Else branch
        if else_actions:
            code_lines.append(self._indent("else:", indent_level))
            else_code = self.convert_actions(else_actions, indent_level + 1)
            code_lines.append(else_code)
        
        return '\n'.join(code_lines)
    
    def _convert_set_hspeed(self, params: Dict[str, Any], indent_level: int) -> str:
        """Convert set_hspeed action."""
        speed = params.get('speed', 0)
        speed = float(speed)
        return self._indent(f"self.hspeed = {speed}", indent_level)
    
    def _convert_set_vspeed(self, params: Dict[str, Any], indent_level: int) -> str:
        """Convert set_vspeed action."""
        speed = params.get('speed', 0)
        # INVERT for Kivy's Y-axis (Y increases downward in Kivy)
        speed = float(-speed)
        return self._indent(f"self.vspeed = {speed}", indent_level)
    
    def _convert_set_speed(self, params: Dict[str, Any], indent_level: int) -> str:
        """Convert set_speed action (magnitude and direction)."""
        speed = params.get('speed', 0)
        return self._indent(f"self.speed = {speed}", indent_level)
    
    def _convert_set_direction(self, params: Dict[str, Any], indent_level: int) -> str:
        """Convert set_direction action."""
        direction = params.get('direction', 0)
        return self._indent(f"self.direction = {direction}", indent_level)
    
    def _convert_stop_movement(self, params: Dict[str, Any], indent_level: int) -> str:
        """Convert stop_movement action."""
        code_lines = []
        code_lines.append(self._indent("# Stop all movement", indent_level))
        code_lines.append(self._indent("self.hspeed = 0", indent_level))
        code_lines.append(self._indent("self.vspeed = 0", indent_level))
        code_lines.append(self._indent("self.speed = 0", indent_level))
        return '\n'.join(code_lines)
    
    def _convert_snap_to_grid(self, params: Dict[str, Any], indent_level: int) -> str:
        """Convert snap_to_grid action."""
        grid_size = params.get('grid_size', self.grid_size)
        code_lines = []
        code_lines.append(self._indent(f"# Snap to {grid_size}px grid", indent_level))
        code_lines.append(self._indent(f"self.x = round(self.x / {grid_size}) * {grid_size}", indent_level))
        code_lines.append(self._indent(f"self.y = round(self.y / {grid_size}) * {grid_size}", indent_level))
        return '\n'.join(code_lines)
    
    def _convert_stop_if_no_keys(self, params: Dict[str, Any], indent_level: int) -> str:
        """Convert stop_if_no_keys action - stops movement if no arrow keys pressed."""
        code_lines = []
        code_lines.append(self._indent("# Stop if no movement keys are pressed", indent_level))
        code_lines.append(self._indent("if not (self.scene.keys_pressed.get(275, False) or  # right", indent_level))
        code_lines.append(self._indent("        self.scene.keys_pressed.get(276, False) or  # left", indent_level))
        code_lines.append(self._indent("        self.scene.keys_pressed.get(273, False) or  # up", indent_level))
        code_lines.append(self._indent("        self.scene.keys_pressed.get(274, False)):  # down", indent_level))
        code_lines.append(self._indent("self.hspeed = 0", indent_level + 1))
        code_lines.append(self._indent("self.vspeed = 0", indent_level + 1))
        return '\n'.join(code_lines)
    
    def _convert_destroy_instance(self, params: Dict[str, Any], indent_level: int) -> str:
        """Convert destroy_instance action."""
        target = params.get('target', 'self')
        
        if target == 'other':
            code = self._indent("# Destroy the other instance (collision target)", indent_level)
            code += '\n' + self._indent("if hasattr(self, '_collision_other') and self._collision_other:", indent_level)
            code += '\n' + self._indent("self._collision_other.destroy()", indent_level + 1)
        else:
            code = self._indent("# Destroy this instance", indent_level)
            code += '\n' + self._indent("self.destroy()", indent_level)
        
        return code
    
    def _convert_create_instance(self, params: Dict[str, Any], indent_level: int) -> str:
        """Convert create_instance action."""
        obj_type = params.get('object', '')
        x = params.get('x', 0)
        y = params.get('y', 0)
        relative = params.get('relative', False)
        
        if relative:
            return self._indent(f"self.scene.create_instance('{obj_type}', self.x + {x}, self.y + {y})", indent_level)
        else:
            return self._indent(f"self.scene.create_instance('{obj_type}', {x}, {y})", indent_level)
    
    def _convert_jump_to_position(self, params: Dict[str, Any], indent_level: int) -> str:
        """Convert jump_to_position action."""
        x = params.get('x', 0)
        y = params.get('y', 0)
        relative = params.get('relative', False)
        
        if relative:
            code_lines = []
            code_lines.append(self._indent(f"self.x += {x}", indent_level))
            code_lines.append(self._indent(f"self.y += {y}", indent_level))
            return '\n'.join(code_lines)
        else:
            code_lines = []
            code_lines.append(self._indent(f"self.x = {x}", indent_level))
            code_lines.append(self._indent(f"self.y = {y}", indent_level))
            return '\n'.join(code_lines)
    
    def _convert_set_variable(self, params: Dict[str, Any], indent_level: int) -> str:
        """Convert set_variable action."""
        var_name = params.get('variable', 'temp')
        value = params.get('value', 0)
        return self._indent(f"self.{var_name} = {value}", indent_level)
    
    def _convert_play_sound(self, params: Dict[str, Any], indent_level: int) -> str:
        """Convert play_sound action."""
        sound = params.get('sound', '')
        loop = params.get('loop', False)
        return self._indent(f"self.play_sound('{sound}', loop={loop})", indent_level)
    
    def _convert_stop_sound(self, params: Dict[str, Any], indent_level: int) -> str:
        """Convert stop_sound action."""
        sound = params.get('sound', '')
        return self._indent(f"self.stop_sound('{sound}')", indent_level)
    
    def _convert_set_hspeed_smooth(self, params: Dict[str, Any], indent_level: int) -> str:
        """Convert smooth horizontal speed action - no grid restrictions."""
        speed = params.get('speed', 0)
        speed = float(speed)
        code_lines = []
        code_lines.append(self._indent(f"# Smooth movement - instant direction change", indent_level))
        code_lines.append(self._indent(f"self.hspeed = {speed}", indent_level))
        code_lines.append(self._indent(f"self.vspeed = 0", indent_level))
        return '\n'.join(code_lines)
    
    def _convert_set_vspeed_smooth(self, params: Dict[str, Any], indent_level: int) -> str:
        """Convert smooth vertical speed action - no grid restrictions."""
        speed = params.get('speed', 0)
        speed = float(-speed)  # Invert for Kivy Y-axis
        code_lines = []
        code_lines.append(self._indent(f"# Smooth movement - instant direction change", indent_level))
        code_lines.append(self._indent(f"self.vspeed = {speed}", indent_level))
        code_lines.append(self._indent(f"self.hspeed = 0", indent_level))
        return '\n'.join(code_lines)
    
    def _convert_move_right_smooth(self, params: Dict[str, Any], indent_level: int) -> str:
        """Move right with smooth movement."""
        speed = params.get('speed', 4)
        speed = float(speed)
        code_lines = []
        code_lines.append(self._indent(f"self.hspeed = {speed}", indent_level))
        code_lines.append(self._indent(f"self.vspeed = 0", indent_level))
        return '\n'.join(code_lines)
    
    def _convert_move_left_smooth(self, params: Dict[str, Any], indent_level: int) -> str:
        """Move left with smooth movement."""
        speed = params.get('speed', 4)
        speed = float(speed)
        code_lines = []
        code_lines.append(self._indent(f"self.hspeed = -{speed}", indent_level))
        code_lines.append(self._indent(f"self.vspeed = 0", indent_level))
        return '\n'.join(code_lines)
    
    def _convert_move_up_smooth(self, params: Dict[str, Any], indent_level: int) -> str:
        """Move up with smooth movement."""
        speed = params.get('speed', 4)
        speed = float(speed)
        code_lines = []
        code_lines.append(self._indent(f"self.vspeed = {speed}", indent_level))  # Positive for up in Kivy
        code_lines.append(self._indent(f"self.hspeed = 0", indent_level))
        return '\n'.join(code_lines)
    
    def _convert_move_down_smooth(self, params: Dict[str, Any], indent_level: int) -> str:
        """Move down with smooth movement."""
        speed = params.get('speed', 4)
        speed = float(speed)
        code_lines = []
        code_lines.append(self._indent(f"self.vspeed = -{speed}", indent_level))  # Negative for down in Kivy
        code_lines.append(self._indent(f"self.hspeed = 0", indent_level))
        return '\n'.join(code_lines)

    def _indent(self, text: str, level: int) -> str:
        """
        Add proper indentation to a line of code.
        
        Args:
            text: The text to indent
            level: Indentation level (1 = 4 spaces)
            
        Returns:
            str: Indented text
        """
        indent = '    ' * level
        return f"{indent}{text}"


# Export the main class
__all__ = ['ActionConverter']