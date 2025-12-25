#!/usr/bin/env python3
"""
Event System for PyGameMaker IDE - MINIMAL VERSION FOR LABYRINTH GAME
Handles GameMaker-style events and actions for visual scripting
"""

from enum import Enum
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, field
from PySide6.QtCore import QObject, Signal

class EventType(Enum):
    """Minimal event types for labyrinth game"""

    # Core Events
    CREATE = "create"
    STEP = "step"

    # Collision Events
    COLLISION = "collision"

    # Input Events
    KEY_PRESS = "key_press"

class ActionCategory(Enum):
    """Minimal categories for labyrinth game"""

    MOVEMENT = "movement"
    CONTROL = "control"
    GAME = "game"

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
        """Setup minimal actions for labyrinth game"""

        # Movement Actions - Player control
        movement_actions = [
            ActionDefinition("move_step", "Move Step", ActionCategory.MOVEMENT,
                           "Move one grid step in a direction",
                           parameters={"direction": 0, "grid_size": 32}),
        ]

        # Control Actions - Game logic
        control_actions = [
            ActionDefinition("check_collision", "Check Collision", ActionCategory.CONTROL,
                           "Check if colliding with object type",
                           parameters={"object_type": "", "action_if_true": ""}),
        ]

        # Game Actions - Win/Restart
        game_actions = [
            ActionDefinition("show_message", "Show Message", ActionCategory.GAME,
                           "Display a message",
                           parameters={"message": ""}),
            ActionDefinition("restart_room", "Restart Room", ActionCategory.GAME,
                           "Restart the current room"),
            ActionDefinition("next_room", "Next Room", ActionCategory.GAME,
                           "Go to the next room"),
            ActionDefinition("destroy_instance", "Destroy Instance", ActionCategory.GAME,
                           "Destroy an instance (self or other)",
                           parameters={"target": "self"}),  # Can be "self" or "other"
        ]

        # Register all actions
        all_actions = movement_actions + control_actions + game_actions

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
