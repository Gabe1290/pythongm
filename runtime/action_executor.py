#!/usr/bin/env python3
"""
Action Execution Engine - WITH GRID SNAPPING
Converts visual actions into runtime behavior
"""

import math
from typing import Dict, Any, List, Optional

class ActionExecutor:
    """Executes visual actions during gameplay with auto-discovery"""

    def __init__(self):
        # Action handlers dictionary - auto-populated via discovery
        self.action_handlers = {}

        # Auto-discover all action handler methods
        self._register_action_handlers()

        print(f"✅ ActionExecutor initialized with {len(self.action_handlers)} action handlers")

    def _register_action_handlers(self):
        """Automatically discover and register action handler methods

        Any method named execute_*_action will be automatically registered
        as a handler for the action name (the part between execute_ and _action)

        Example: execute_move_grid_action -> handles "move_grid" action
        """
        for attr_name in dir(self):
            # Look for methods matching the pattern execute_*_action
            if attr_name.startswith('execute_') and attr_name.endswith('_action'):
                # Extract action name: execute_move_grid_action -> move_grid
                action_name = attr_name[8:-7]  # Remove 'execute_' and '_action'

                # Get the method
                method = getattr(self, attr_name)

                # Verify it's callable
                if callable(method):
                    self.action_handlers[action_name] = method
                    print(f"  📌 Registered action handler: {action_name}")

    def register_custom_action(self, action_name: str, handler_func):
        """Register a custom action handler dynamically (for plugins)

        Args:
            action_name: The action name (e.g., 'play_sound')
            handler_func: A function with signature (instance, parameters) -> None
        """
        self.action_handlers[action_name] = handler_func
        print(f"  🔌 Registered custom action: {action_name}")
    
    def execute_event(self, instance, event_name: str, events_data: Dict[str, Any]):
        """Execute all actions in an event"""
        if event_name not in events_data:
            return
            
        event_data = events_data[event_name]
        actions = event_data.get("actions", [])
        
        for action_data in actions:
            self.execute_action(instance, action_data)
    
    def execute_action(self, instance, action_data: Dict[str, Any]):
        """Execute a single action with validation"""
        action_name = action_data.get("action", "")
        parameters = action_data.get("parameters", {})

        if not action_name:
            print(f"⚠️ Action missing 'action' field: {action_data}")
            return

        if action_name not in self.action_handlers:
            print(f"❌ Unknown action: {action_name}")
            print(f"   Available actions: {', '.join(sorted(self.action_handlers.keys()))}")
            return

        # Validate instance has required attributes for this action
        if not self._validate_action_requirements(instance, action_name):
            print(f"⚠️ Instance missing requirements for action '{action_name}'")
            return

        # Execute the action with error handling
        try:
            self.action_handlers[action_name](instance, parameters)
        except AttributeError as e:
            print(f"❌ Attribute error in action {action_name}: {e}")
            print(f"   Instance may be missing required attributes")
        except Exception as e:
            print(f"❌ Error executing action {action_name}: {e}")
            import traceback
            traceback.print_exc()

    def _validate_action_requirements(self, instance, action_name: str) -> bool:
        """Validate that instance has required attributes for an action

        Returns:
            True if instance meets requirements, False otherwise
        """
        # Define required attributes for each action category
        requirements = {
            # Movement actions need position and speed attributes
            "move_grid": ["x", "y"],
            "set_hspeed": ["hspeed"],
            "set_vspeed": ["vspeed"],
            "stop_movement": ["hspeed", "vspeed"],

            # Grid actions need position
            "snap_to_grid": ["x", "y"],
            "if_on_grid": ["x", "y"],
            "stop_if_no_keys": ["x", "y", "hspeed", "vspeed"],

            # Most actions work with any instance
            "show_message": [],
            "restart_room": [],
            "next_room": [],
            "destroy_instance": [],
            "if_collision_at": ["x", "y"],
        }

        # Get required attributes for this action
        required_attrs = requirements.get(action_name, [])

        # Check if instance has all required attributes
        for attr in required_attrs:
            if not hasattr(instance, attr):
                print(f"   Missing attribute: {attr}")
                return False

        return True
    
    # ==================== GRID-BASED MOVEMENT ====================
    
    def execute_move_grid_action(self, instance, parameters: Dict[str, Any]):
        """Execute grid-based movement (instant snap)"""
        direction = parameters.get("direction", "right")
        grid_size = int(parameters.get("grid_size", 32))
        
        # Calculate movement based on direction
        dx, dy = 0, 0
        if direction == "right":
            dx = grid_size
        elif direction == "left":
            dx = -grid_size
        elif direction == "up":
            dy = -grid_size
        elif direction == "down":
            dy = grid_size
        
        # Store intended movement for collision checking by game_runner
        instance.intended_x = instance.x + dx
        instance.intended_y = instance.y + dy
    
    # ==================== SPEED-BASED MOVEMENT ====================
    
    def execute_set_hspeed_action(self, instance, parameters: Dict[str, Any]):
        """Set horizontal speed for smooth movement"""
        speed = float(parameters.get("speed", 0))
        instance.hspeed = speed
    
    def execute_set_vspeed_action(self, instance, parameters: Dict[str, Any]):
        """Set vertical speed for smooth movement"""
        speed = float(parameters.get("speed", 0))
        instance.vspeed = speed
    
    def execute_stop_movement_action(self, instance, parameters: Dict[str, Any]):
        """Stop all movement by setting speeds to zero"""
        instance.hspeed = 0
        instance.vspeed = 0
    
    # ==================== GRID UTILITIES ====================
    
    def execute_snap_to_grid_action(self, instance, parameters: Dict[str, Any]):
        """Snap instance to nearest grid position"""
        grid_size = int(parameters.get("grid_size", 32))
        
        # Round to nearest grid position
        instance.x = round(instance.x / grid_size) * grid_size
        instance.y = round(instance.y / grid_size) * grid_size
    
    def execute_if_on_grid_action(self, instance, parameters: Dict[str, Any]):
        """Check if instance is on grid and execute actions conditionally"""
        grid_size = int(parameters.get("grid_size", 32))
        then_actions = parameters.get("then_actions", [])
        else_actions = parameters.get("else_actions", [])
        
        # Check if position is aligned to grid
        x_aligned = (instance.x % grid_size) == 0
        y_aligned = (instance.y % grid_size) == 0
        on_grid = x_aligned and y_aligned
        
        if on_grid:
            for action in then_actions:
                self.execute_action(instance, action)
        else:
            for action in else_actions:
                self.execute_action(instance, action)
    
    def execute_stop_if_no_keys_action(self, instance, parameters: Dict[str, Any]):
        """Stop movement and snap to nearest grid when no movement keys are pressed
        
        This allows smooth movement while key is held, but immediately stops 
        and snaps to nearest grid position when released.
        
        Parameters:
            grid_size: Grid cell size (default 32)
        """
        grid_size = int(parameters.get("grid_size", 32))
        
        # Check if any movement keys are pressed
        keys_pressed = getattr(instance, 'keys_pressed', set())
        
        if not keys_pressed:  # No keys pressed
            # Stop movement and snap to NEAREST grid position
            instance.hspeed = 0
            instance.vspeed = 0
            instance.x = round(instance.x / grid_size) * grid_size
            instance.y = round(instance.y / grid_size) * grid_size
    
    # ==================== CONTROL ACTIONS ====================
    
    def execute_if_collision_at_action(self, instance, parameters: Dict[str, Any]):
        """Execute collision check with conditional actions"""
        x_expr = parameters.get("x", "self.x")
        y_expr = parameters.get("y", "self.y")
        object_type = parameters.get("object_type", "any")
        then_actions = parameters.get("then_actions", [])
        else_actions = parameters.get("else_actions", [])
        
        # Store collision check for game_runner to process
        if not hasattr(instance, 'collision_checks'):
            instance.collision_checks = []
        
        instance.collision_checks.append({
            'x': x_expr,
            'y': y_expr,
            'object_type': object_type,
            'then_actions': then_actions,
            'else_actions': else_actions
        })
    
    # ==================== GAME ACTIONS ====================
    
    def execute_show_message_action(self, instance, parameters: Dict[str, Any]):
        """Execute show message action"""
        message = parameters.get("message", "")
        print(f"💬 MESSAGE: {message}")
        
        # Store message for game runner to display
        if not hasattr(instance, 'pending_messages'):
            instance.pending_messages = []
        instance.pending_messages.append(message)
    
    def execute_restart_room_action(self, instance, parameters: Dict[str, Any]):
        """Execute restart room action - resets current level"""
        print(f"🔄 Restart room requested by {instance.object_name}")
        instance.restart_room_flag = True
    
    def execute_next_room_action(self, instance, parameters: Dict[str, Any]):
        """Execute next room action - advances to next level"""
        print(f"➡️  Next room requested by {instance.object_name}")
        instance.next_room_flag = True
    
    # ==================== INSTANCE ACTIONS ====================
    
    def execute_destroy_instance_action(self, instance, parameters: Dict[str, Any]):
        """Execute destroy instance action"""
        print(f"💀 Destroying instance: {instance.object_name}")
        instance.to_destroy = True

    def execute_collision_event(self, instance, event_name: str, events_data: Dict[str, Any], other_instance):
        """Execute collision event with context about the other instance"""
        if event_name not in events_data:
            return
            
        event_data = events_data[event_name]
        actions = event_data.get("actions", [])
        
        for action_data in actions:
            self.execute_collision_action(instance, action_data, other_instance)

    def execute_collision_action(self, instance, action_data: Dict[str, Any], other_instance):
        """Execute a collision action with knowledge of both self and other"""
        action_name = action_data.get("action")
        parameters = action_data.get("parameters", {})
        
        if action_name == "destroy_instance":
            target = parameters.get("target", "self")
            
            if target == "self":
                instance.to_destroy = True
            elif target == "other":
                other_instance.to_destroy = True