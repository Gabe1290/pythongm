#!/usr/bin/env python3
"""
Event System for PyGameMaker IDE
Handles GameMaker-style events and actions for visual scripting
"""

from enum import Enum, auto
from typing import Dict, List, Optional, Any, Callable, Union
from dataclasses import dataclass, field
from PySide6.QtCore import QObject, Signal
import json

class EventType(Enum):
    """GameMaker-style event types"""
    
    # Basic Events
    CREATE = "create"
    DESTROY = "destroy"
    STEP = "step"
    STEP_BEGIN = "step_begin"
    STEP_END = "step_end"
    
    # Collision Events  
    COLLISION = "collision"
    
    # Input Events
    KEYBOARD = "keyboard"
    KEY_PRESS = "key_press"
    KEY_RELEASE = "key_release"
    MOUSE = "mouse"
    MOUSE_LEFT_BUTTON = "mouse_left_button"
    MOUSE_RIGHT_BUTTON = "mouse_right_button"
    MOUSE_MIDDLE_BUTTON = "mouse_middle_button"
    MOUSE_ENTER = "mouse_enter"
    MOUSE_LEAVE = "mouse_leave"
    
    # Drawing Events
    DRAW = "draw"
    DRAW_GUI = "draw_gui"
    DRAW_BEGIN = "draw_begin"
    DRAW_END = "draw_end"
    
    # Alarm Events
    ALARM_0 = "alarm_0"
    ALARM_1 = "alarm_1"
    ALARM_2 = "alarm_2"
    
    # Other Events
    ANIMATION_END = "animation_end"
    END_OF_PATH = "end_of_path"
    GAME_START = "game_start"
    GAME_END = "game_end"
    ROOM_START = "room_start"
    ROOM_END = "room_end"

class ActionCategory(Enum):
    """Categories for organizing actions"""
    
    MOVEMENT = "movement"
    MAIN1 = "main1"  # Set Variables, etc.
    MAIN2 = "main2"  # Testing actions
    CONTROL = "control"
    DRAWING = "drawing"
    SOUND = "sound"
    ROOMS = "rooms"
    TIMING = "timing"
    GAME = "game"
    RESOURCES = "resources"
    VARIABLES = "variables"
    CODE = "code"

@dataclass
class ActionDefinition:
    """Definition of a GameMaker-style action"""
    
    id: str
    name: str
    category: ActionCategory
    description: str = ""
    icon_path: str = ""
    parameters: Dict[str, Any] = field(default_factory=dict)
    code_template: str = ""
    applies_to: str = "self"  # self, other, all
    relative: bool = False
    question: bool = False  # If this is a conditional action
    
    def __post_init__(self):
        if not self.description:
            self.description = self.name

@dataclass 
class EventAction:
    """An action instance attached to an event"""
    
    action_id: str
    parameters: Dict[str, Any] = field(default_factory=dict)
    applies_to: str = "self"
    relative: bool = False
    enabled: bool = True
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization"""
        return {
            'action_id': self.action_id,
            'parameters': self.parameters,
            'applies_to': self.applies_to,
            'relative': self.relative,
            'enabled': self.enabled
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'EventAction':
        """Create from dictionary"""
        return cls(**data)

@dataclass
class GameEvent:
    """A GameMaker-style event with associated actions"""
    
    # Required fields first
    event_type: EventType
    object_name: str
    
    # Optional fields with defaults
    actions: List[EventAction] = field(default_factory=list)
    enabled: bool = True
    collision_object: str = ""  # For collision events
    key_code: int = 0  # For keyboard events  
    mouse_button: int = 0  # For mouse events
    alarm_index: int = 0  # For alarm events
    
    def add_action(self, action: EventAction):
        """Add an action to this event"""
        self.actions.append(action)
    
    def remove_action(self, index: int) -> bool:
        """Remove action at index"""
        if 0 <= index < len(self.actions):
            del self.actions[index]
            return True
        return False
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization"""
        return {
            'event_type': self.event_type.value,
            'object_name': self.object_name,
            'actions': [action.to_dict() for action in self.actions],
            'enabled': self.enabled,
            'collision_object': self.collision_object,
            'key_code': self.key_code,
            'mouse_button': self.mouse_button,
            'alarm_index': self.alarm_index
        }
    
    @classmethod  
    def from_dict(cls, data: Dict[str, Any]) -> 'GameEvent':
        """Create from dictionary"""
        event = cls(
            event_type=EventType(data['event_type']),
            object_name=data['object_name'],
            enabled=data.get('enabled', True),
            collision_object=data.get('collision_object', ''),
            key_code=data.get('key_code', 0),
            mouse_button=data.get('mouse_button', 0),
            alarm_index=data.get('alarm_index', 0)
        )
        
        # Load actions
        for action_data in data.get('actions', []):
            event.actions.append(EventAction.from_dict(action_data))
        
        return event

class ActionRegistry:
    """Registry of all available actions"""
    
    def __init__(self):
        self.actions: Dict[str, ActionDefinition] = {}
        self._setup_default_actions()
    
    def _setup_default_actions(self):
        """Setup default GameMaker-style actions"""
        
        # Movement Actions
        movement_actions = [
            ActionDefinition("move_fixed", "Move Fixed", ActionCategory.MOVEMENT,
                           "Move in a fixed direction", 
                           parameters={"direction": 0, "speed": 0}),
            ActionDefinition("move_free", "Move Free", ActionCategory.MOVEMENT,
                           "Move freely in any direction",
                           parameters={"direction": 0, "speed": 0}),
            ActionDefinition("move_towards", "Move Towards Point", ActionCategory.MOVEMENT,
                           "Move towards a specific point",
                           parameters={"x": 0, "y": 0, "speed": 0}),
            ActionDefinition("set_friction", "Set Friction", ActionCategory.MOVEMENT,
                           "Set friction for the instance",
                           parameters={"friction": 0}),
            ActionDefinition("set_gravity", "Set Gravity", ActionCategory.MOVEMENT,
                           "Set gravity for the instance", 
                           parameters={"direction": 270, "gravity": 0.5}),
        ]
        
        # Main Actions 1 - Variables and basic operations
        main1_actions = [
            ActionDefinition("set_variable", "Set Variable", ActionCategory.MAIN1,
                           "Set a variable to a value",
                           parameters={"variable": "", "value": 0}),
            ActionDefinition("set_sprite", "Set Sprite", ActionCategory.MAIN1,
                           "Change the sprite of the instance",
                           parameters={"sprite": "", "subimage": 0}),
            ActionDefinition("play_sound", "Play Sound", ActionCategory.MAIN1,
                           "Play a sound effect",
                           parameters={"sound": "", "loop": False}),
            ActionDefinition("create_instance", "Create Instance", ActionCategory.MAIN1,
                           "Create an instance of an object",
                           parameters={"object": "", "x": 0, "y": 0}),
            ActionDefinition("destroy_instance", "Destroy Instance", ActionCategory.MAIN1,
                           "Destroy the current instance"),
        ]
        
        # Main Actions 2 - Testing and conditions  
        main2_actions = [
            ActionDefinition("test_variable", "Test Variable", ActionCategory.MAIN2,
                           "Test if a variable meets a condition",
                           parameters={"variable": "", "operation": "equal", "value": 0},
                           question=True),
            ActionDefinition("check_collision", "Check Collision", ActionCategory.MAIN2,
                           "Check for collision with an object",
                           parameters={"object": "", "x": 0, "y": 0},
                           question=True),
            ActionDefinition("test_instance_count", "Test Instance Count", ActionCategory.MAIN2,
                           "Test the number of instances",
                           parameters={"object": "", "operation": "equal", "number": 1},
                           question=True),
            ActionDefinition("check_grid", "Check Grid Position", ActionCategory.MAIN2,
                           "Check if position is free in a grid",
                           parameters={"x": 0, "y": 0, "object": ""},
                           question=True),
        ]
        
        # Control Actions
        control_actions = [
            ActionDefinition("if_question", "If Question", ActionCategory.CONTROL,
                           "Execute actions based on a question"),
            ActionDefinition("repeat", "Repeat", ActionCategory.CONTROL,
                           "Repeat actions a number of times",
                           parameters={"times": 1}),
            ActionDefinition("exit_event", "Exit Event", ActionCategory.CONTROL,
                           "Exit the current event"),
            ActionDefinition("comment", "Comment", ActionCategory.CONTROL,
                           "Add a comment",
                           parameters={"text": ""}),
        ]
        
        # Game Actions
        game_actions = [
            ActionDefinition("restart_game", "Restart Game", ActionCategory.GAME,
                           "Restart the current game"),
            ActionDefinition("end_game", "End Game", ActionCategory.GAME,
                           "End the game"),
            ActionDefinition("save_game", "Save Game", ActionCategory.GAME,
                           "Save the game",
                           parameters={"filename": "save.dat"}),
            ActionDefinition("load_game", "Load Game", ActionCategory.GAME,
                           "Load a saved game",
                           parameters={"filename": "save.dat"}),
        ]
        
        # Timing Actions
        timing_actions = [
            ActionDefinition("set_alarm", "Set Alarm", ActionCategory.TIMING,
                           "Set an alarm to go off",
                           parameters={"alarm": 0, "steps": 30}),
            ActionDefinition("sleep", "Sleep", ActionCategory.TIMING,
                           "Pause execution",
                           parameters={"milliseconds": 1000}),
        ]
        
        # Room Actions
        room_actions = [
            ActionDefinition("next_room", "Next Room", ActionCategory.ROOMS,
                           "Go to the next room"),
            ActionDefinition("previous_room", "Previous Room", ActionCategory.ROOMS,
                           "Go to the previous room"),
            ActionDefinition("restart_room", "Restart Room", ActionCategory.ROOMS,
                           "Restart the current room"),
            ActionDefinition("goto_room", "Go to Room", ActionCategory.ROOMS,
                           "Go to a specific room",
                           parameters={"room": ""}),
        ]
        
        # Register all actions
        all_actions = (movement_actions + main1_actions + main2_actions + 
                      control_actions + game_actions + timing_actions + room_actions)
        
        for action in all_actions:
            self.actions[action.id] = action
    
    def get_action(self, action_id: str) -> Optional[ActionDefinition]:
        """Get action definition by ID"""
        return self.actions.get(action_id)
    
    def get_actions_by_category(self, category: ActionCategory) -> List[ActionDefinition]:
        """Get all actions in a category"""
        return [action for action in self.actions.values() 
                if action.category == category]
    
    def register_action(self, action: ActionDefinition):
        """Register a new action"""
        self.actions[action.id] = action

class EventSystem(QObject):
    """Main event system for managing GameMaker-style events"""
    
    # Signals for UI updates
    eventAdded = Signal(object)  # GameEvent
    eventRemoved = Signal(str, str)  # object_name, event_type
    actionAdded = Signal(str, str, object)  # object_name, event_type, EventAction
    actionRemoved = Signal(str, str, int)  # object_name, event_type, index
    
    def __init__(self):
        super().__init__()
        self.events: Dict[str, Dict[str, GameEvent]] = {}  # object_name -> event_type -> GameEvent
        self.action_registry = ActionRegistry()
        
    def create_event(self, object_name: str, event_type: EventType, **kwargs) -> GameEvent:
        """Create a new event for an object"""
        
        if object_name not in self.events:
            self.events[object_name] = {}
            
        event = GameEvent(event_type=event_type, object_name=object_name, **kwargs)
        self.events[object_name][event_type.value] = event
        
        self.eventAdded.emit(event)
        return event
    
    def remove_event(self, object_name: str, event_type: EventType) -> bool:
        """Remove an event from an object"""
        
        if (object_name in self.events and 
            event_type.value in self.events[object_name]):
            
            del self.events[object_name][event_type.value]
            self.eventRemoved.emit(object_name, event_type.value)
            return True
        return False
    
    def get_event(self, object_name: str, event_type: EventType) -> Optional[GameEvent]:
        """Get a specific event"""
        
        if (object_name in self.events and 
            event_type.value in self.events[object_name]):
            return self.events[object_name][event_type.value]
        return None
    
    def get_object_events(self, object_name: str) -> Dict[str, GameEvent]:
        """Get all events for an object"""
        return self.events.get(object_name, {})
    
    def add_action_to_event(self, object_name: str, event_type: EventType, 
                           action_id: str, **parameters) -> bool:
        """Add an action to an event"""
        
        event = self.get_event(object_name, event_type)
        if not event:
            return False
            
        action = EventAction(action_id=action_id, parameters=parameters)
        event.add_action(action)
        
        self.actionAdded.emit(object_name, event_type.value, action)
        return True
    
    def remove_action_from_event(self, object_name: str, event_type: EventType, 
                                action_index: int) -> bool:
        """Remove an action from an event"""
        
        event = self.get_event(object_name, event_type)
        if not event:
            return False
            
        if event.remove_action(action_index):
            self.actionRemoved.emit(object_name, event_type.value, action_index)
            return True
        return False
    
    def export_events(self, object_name: str) -> Dict[str, Any]:
        """Export events for an object to dictionary"""
        
        object_events = self.get_object_events(object_name)
        return {
            'object_name': object_name,
            'events': {event_type: event.to_dict() 
                      for event_type, event in object_events.items()}
        }
    
    def import_events(self, data: Dict[str, Any]) -> bool:
        """Import events from dictionary"""
        
        try:
            object_name = data['object_name']
            
            if object_name not in self.events:
                self.events[object_name] = {}
                
            for event_type_str, event_data in data['events'].items():
                event = GameEvent.from_dict(event_data)
                self.events[object_name][event_type_str] = event
                self.eventAdded.emit(event)
                
            return True
            
        except Exception as e:
            print(f"Error importing events: {e}")
            return False
    
    def generate_code(self, object_name: str) -> str:
        """Generate code representation of object's events"""
        
        object_events = self.get_object_events(object_name)
        if not object_events:
            return f"// No events defined for {object_name}\n"
            
        code = f"// Events for {object_name}\n\n"
        
        for event_type, event in object_events.items():
            code += f"// Event: {event_type}\n"
            
            if not event.actions:
                code += "// No actions\n\n"
                continue
                
            for i, action in enumerate(event.actions):
                action_def = self.action_registry.get_action(action.action_id)
                if action_def:
                    code += f"// Action {i+1}: {action_def.name}\n"
                    if action.parameters:
                        code += f"// Parameters: {action.parameters}\n"
                else:
                    code += f"// Unknown action: {action.action_id}\n"
                    
            code += "\n"
            
        return code

# Aliases for backward compatibility
ActionInstance = EventAction  # Alias for widgets that expect ActionInstance



# Compatibility aliases for widgets
EventInstance = EventAction
Action = ActionDefinition

# Global instance
event_system = EventSystem()

# Convenience functions
def get_event_system() -> EventSystem:
    """Get the global event system instance"""
    return event_system

def get_action_registry() -> ActionRegistry:
    """Get the global action registry"""
    return event_system.action_registry
