#!/usr/bin/env python3
"""
Action Execution Engine - EXPANDED FOR SMOOTH MOVEMENT
Converts visual actions into runtime behavior
"""

import math
from typing import Dict, Any, List, Optional

class ActionExecutor:
    """Executes visual actions during gameplay"""
    
    def __init__(self):
        # Action handlers dictionary - matches action names from IDE
        self.action_handlers = {
            # Grid-based movement
            "move_grid": self.execute_move_grid_action,
            
            # Speed-based movement
            "set_hspeed": self.execute_set_hspeed_action,
            "set_vspeed": self.execute_set_vspeed_action,
            "stop_movement": self.execute_stop_movement_action,
            
            # Grid utilities
            "snap_to_grid": self.execute_snap_to_grid_action,
            "if_on_grid": self.execute_if_on_grid_action,
            
            # Control
            "if_collision_at": self.execute_if_collision_at_action,
            
            # Game
            "show_message": self.execute_show_message_action,
            "restart_room": self.execute_restart_room_action,
            "next_room": self.execute_next_room_action,
            
            # Instance
            "destroy_instance": self.execute_destroy_instance_action,
        }
    
    def execute_event(self, instance, event_name: str, events_data: Dict[str, Any]):
        """Execute all actions in an event"""
        if event_name not in events_data:
            return
            
        event_data = events_data[event_name]
        actions = event_data.get("actions", [])
        
        for action_data in actions:
            self.execute_action(instance, action_data)
    
    def execute_action(self, instance, action_data: Dict[str, Any]):
        """Execute a single action"""
        action_name = action_data.get("action", "")
        parameters = action_data.get("parameters", {})
        
        if action_name in self.action_handlers:
            try:
                self.action_handlers[action_name](instance, parameters)
            except Exception as e:
                print(f"❌ Error executing action {action_name}: {e}")
                import traceback
                traceback.print_exc()
        else:
            print(f"❌ Unknown action: {action_name}")
    
    # ==================== GRID-BASED MOVEMENT ====================
    
    def execute_move_grid_action(self, instance, parameters: Dict[str, Any]):
        """Execute grid-based movement (instant snap)
        
        Parameters:
            direction: "left", "right", "up", "down"
            grid_size: Size of grid cell (default 32)
        """
        direction = parameters.get("direction", "right")
        grid_size = int(parameters.get("grid_size", 32))
        
        print(f"🎮 Move Grid: {instance.object_name} moving {direction} by {grid_size}px")
        
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
        """Set horizontal speed for smooth movement
        
        Parameters:
            speed: Horizontal speed (negative=left, positive=right)
        """
        speed = float(parameters.get("speed", 0))
        instance.hspeed = speed
        print(f"↔️ Set hspeed: {instance.object_name}.hspeed = {speed}")
    
    def execute_set_vspeed_action(self, instance, parameters: Dict[str, Any]):
        """Set vertical speed for smooth movement
        
        Parameters:
            speed: Vertical speed (negative=up, positive=down)
        """
        speed = float(parameters.get("speed", 0))
        instance.vspeed = speed
        print(f"↕️ Set vspeed: {instance.object_name}.vspeed = {speed}")
    
    def execute_stop_movement_action(self, instance, parameters: Dict[str, Any]):
        """Stop all movement by setting speeds to zero"""
        instance.hspeed = 0
        instance.vspeed = 0
        print(f"🛑 Stop movement: {instance.object_name}")
    
    # ==================== GRID UTILITIES ====================
    
    def execute_snap_to_grid_action(self, instance, parameters: Dict[str, Any]):
        """Snap instance to nearest grid position
        
        Parameters:
            grid_size: Grid cell size (default 32)
        """
        grid_size = int(parameters.get("grid_size", 32))
        
        # Round to nearest grid position
        instance.x = round(instance.x / grid_size) * grid_size
        instance.y = round(instance.y / grid_size) * grid_size
        
        print(f"📐 Snap to grid: {instance.object_name} → ({instance.x}, {instance.y})")
    
    def execute_if_on_grid_action(self, instance, parameters: Dict[str, Any]):
        """Check if instance is on grid and execute actions conditionally
        
        Parameters:
            grid_size: Grid cell size (default 32)
            then_actions: Actions if on grid
            else_actions: Actions if not on grid
        """
        grid_size = int(parameters.get("grid_size", 32))
        then_actions = parameters.get("then_actions", [])
        else_actions = parameters.get("else_actions", [])
        
        # Check if position is aligned to grid
        x_aligned = (instance.x % grid_size) == 0
        y_aligned = (instance.y % grid_size) == 0
        on_grid = x_aligned and y_aligned
        
        if on_grid:
            print(f"✅ On grid: {instance.object_name}")
            for action in then_actions:
                self.execute_action(instance, action)
        else:
            print(f"❌ Not on grid: {instance.object_name}")
            for action in else_actions:
                self.execute_action(instance, action)
    
    # ==================== CONTROL ACTIONS ====================
    
    def execute_if_collision_at_action(self, instance, parameters: Dict[str, Any]):
        """Execute collision check with conditional actions
        
        Parameters:
            x: X position expression (e.g., "self.x + 32")
            y: Y position expression
            object_type: "any" or "solid"
            then_actions: List of actions if collision found
            else_actions: List of actions if no collision
        """
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
        
        print(f"🎯 Collision check queued: {object_type} at ({x_expr}, {y_expr})")
    
    # ==================== GAME ACTIONS ====================
    
    def execute_show_message_action(self, instance, parameters: Dict[str, Any]):
        """Execute show message action
        
        Parameters:
            message: Text message to display
        """
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
        """Execute destroy instance action
        
        Parameters: None
        """
        print(f"💀 Destroying instance: {instance.object_name}")
        instance.to_destroy = True
