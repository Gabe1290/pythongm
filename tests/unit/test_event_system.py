#!/usr/bin/env python3
"""
Unit tests for EventSystem
Tests event creation, action management, and serialization
"""

import pytest
import json
from pythongm.core.event_system import (
    EventType, ActionCategory, ActionDefinition,
    EventAction, GameEvent, EventSystem, ActionRegistry
)


class TestEventType:
    """Test EventType enum"""

    def test_event_type_has_create(self):
        """Test that CREATE event type exists"""
        assert EventType.CREATE.value == "create"

    def test_event_type_has_destroy(self):
        """Test that DESTROY event type exists"""
        assert EventType.DESTROY.value == "destroy"

    def test_event_type_has_step(self):
        """Test that STEP event type exists"""
        assert EventType.STEP.value == "step"

    def test_event_type_has_collision(self):
        """Test that COLLISION event type exists"""
        assert EventType.COLLISION.value == "collision"

    def test_all_event_types_have_unique_values(self):
        """Test that all event types have unique values"""
        values = [et.value for et in EventType]
        assert len(values) == len(set(values))


class TestActionCategory:
    """Test ActionCategory enum"""

    def test_action_category_has_movement(self):
        """Test that MOVEMENT category exists"""
        assert ActionCategory.MOVEMENT.value == "movement"

    def test_action_category_has_control(self):
        """Test that CONTROL category exists"""
        assert ActionCategory.CONTROL.value == "control"

    def test_all_categories_have_unique_values(self):
        """Test that all categories have unique values"""
        values = [ac.value for ac in ActionCategory]
        assert len(values) == len(set(values))


class TestActionDefinition:
    """Test ActionDefinition dataclass"""

    def test_create_action_definition(self):
        """Test creating an ActionDefinition"""
        action_def = ActionDefinition(
            id="move_to",
            name="Move To",
            category=ActionCategory.MOVEMENT,
            description="Move to a position"
        )

        assert action_def.id == "move_to"
        assert action_def.name == "Move To"
        assert action_def.category == ActionCategory.MOVEMENT

    def test_action_definition_defaults(self):
        """Test ActionDefinition default values"""
        action_def = ActionDefinition(
            id="test",
            name="Test Action",
            category=ActionCategory.MAIN1
        )

        assert action_def.parameters == {}
        assert action_def.code_template == ""
        assert action_def.applies_to == "self"
        assert action_def.relative is False
        assert action_def.question is False

    def test_action_definition_with_parameters(self):
        """Test ActionDefinition with parameters"""
        params = {"x": {"type": "number", "default": 0}}
        action_def = ActionDefinition(
            id="set_x",
            name="Set X",
            category=ActionCategory.MAIN1,
            parameters=params
        )

        assert action_def.parameters == params

    def test_action_definition_description_defaults_to_name(self):
        """Test that description defaults to name if not provided"""
        action_def = ActionDefinition(
            id="test",
            name="Test Action",
            category=ActionCategory.MAIN1
        )

        assert action_def.description == "Test Action"


class TestEventAction:
    """Test EventAction dataclass"""

    def test_create_event_action(self):
        """Test creating an EventAction"""
        action = EventAction(
            action_id="move_to",
            parameters={"x": 100, "y": 200}
        )

        assert action.action_id == "move_to"
        assert action.parameters == {"x": 100, "y": 200}

    def test_event_action_defaults(self):
        """Test EventAction default values"""
        action = EventAction(action_id="test_action")

        assert action.parameters == {}
        assert action.applies_to == "self"
        assert action.relative is False
        assert action.enabled is True

    def test_event_action_to_dict(self):
        """Test serializing EventAction to dictionary"""
        action = EventAction(
            action_id="move_to",
            parameters={"x": 100, "y": 200},
            applies_to="self",
            relative=False
        )

        action_dict = action.to_dict()

        assert action_dict["action_id"] == "move_to"
        assert action_dict["parameters"] == {"x": 100, "y": 200}
        assert action_dict["applies_to"] == "self"
        assert action_dict["relative"] is False

    def test_event_action_from_dict(self):
        """Test deserializing EventAction from dictionary"""
        data = {
            "action_id": "move_to",
            "parameters": {"x": 100, "y": 200},
            "applies_to": "self",
            "relative": False,
            "enabled": True
        }

        action = EventAction.from_dict(data)

        assert action.action_id == "move_to"
        assert action.parameters == {"x": 100, "y": 200}

    def test_event_action_roundtrip_serialization(self):
        """Test that to_dict and from_dict are inverses"""
        original = EventAction(
            action_id="test",
            parameters={"param1": "value1"},
            applies_to="other",
            relative=True,
            enabled=False
        )

        serialized = original.to_dict()
        deserialized = EventAction.from_dict(serialized)

        assert deserialized.action_id == original.action_id
        assert deserialized.parameters == original.parameters
        assert deserialized.applies_to == original.applies_to
        assert deserialized.relative == original.relative
        assert deserialized.enabled == original.enabled


class TestGameEvent:
    """Test GameEvent dataclass"""

    def test_create_game_event(self):
        """Test creating a GameEvent"""
        event = GameEvent(
            event_type=EventType.CREATE,
            object_name="obj_player"
        )

        assert event.event_type == EventType.CREATE
        assert event.object_name == "obj_player"

    def test_game_event_defaults(self):
        """Test GameEvent default values"""
        event = GameEvent(
            event_type=EventType.STEP,
            object_name="obj_test"
        )

        assert event.actions == []
        assert event.enabled is True
        assert event.collision_object == ""
        assert event.key_code == 0
        assert event.mouse_button == 0
        assert event.alarm_index == 0

    def test_add_action_to_event(self):
        """Test adding an action to an event"""
        event = GameEvent(
            event_type=EventType.CREATE,
            object_name="obj_player"
        )

        action = EventAction(action_id="set_speed")
        event.add_action(action)

        assert len(event.actions) == 1
        assert event.actions[0] == action

    def test_add_multiple_actions(self):
        """Test adding multiple actions to an event"""
        event = GameEvent(
            event_type=EventType.CREATE,
            object_name="obj_player"
        )

        action1 = EventAction(action_id="action1")
        action2 = EventAction(action_id="action2")
        action3 = EventAction(action_id="action3")

        event.add_action(action1)
        event.add_action(action2)
        event.add_action(action3)

        assert len(event.actions) == 3

    def test_remove_action_from_event(self):
        """Test removing an action from an event"""
        event = GameEvent(
            event_type=EventType.CREATE,
            object_name="obj_player"
        )

        action1 = EventAction(action_id="action1")
        action2 = EventAction(action_id="action2")
        event.add_action(action1)
        event.add_action(action2)

        result = event.remove_action(0)

        assert result is True
        assert len(event.actions) == 1
        assert event.actions[0].action_id == "action2"

    def test_remove_action_invalid_index(self):
        """Test removing action with invalid index fails"""
        event = GameEvent(
            event_type=EventType.CREATE,
            object_name="obj_player"
        )

        result = event.remove_action(0)
        assert result is False

        result = event.remove_action(-1)
        assert result is False

    def test_game_event_to_dict(self):
        """Test serializing GameEvent to dictionary"""
        event = GameEvent(
            event_type=EventType.CREATE,
            object_name="obj_player"
        )

        action = EventAction(action_id="move_to", parameters={"x": 100})
        event.add_action(action)

        event_dict = event.to_dict()

        assert event_dict["event_type"] == "create"
        assert event_dict["object_name"] == "obj_player"
        assert len(event_dict["actions"]) == 1

    def test_game_event_collision_fields(self):
        """Test collision event specific fields"""
        event = GameEvent(
            event_type=EventType.COLLISION,
            object_name="obj_player",
            collision_object="obj_enemy"
        )

        assert event.collision_object == "obj_enemy"

    def test_game_event_keyboard_fields(self):
        """Test keyboard event specific fields"""
        event = GameEvent(
            event_type=EventType.KEY_PRESS,
            object_name="obj_player",
            key_code=32  # Space key
        )

        assert event.key_code == 32


class TestActionRegistry:
    """Test ActionRegistry class"""

    def test_action_registry_exists(self):
        """Test that ActionRegistry class exists"""
        assert ActionRegistry is not None

    def test_action_registry_can_be_instantiated(self):
        """Test creating an ActionRegistry instance"""
        registry = ActionRegistry()
        assert registry is not None

    def test_action_registry_has_register_method(self):
        """Test that ActionRegistry has register method"""
        registry = ActionRegistry()
        assert hasattr(registry, 'register')

    def test_register_action(self):
        """Test registering an action"""
        registry = ActionRegistry()

        action_def = ActionDefinition(
            id="test_action",
            name="Test Action",
            category=ActionCategory.MAIN1
        )

        registry.register(action_def)

        assert "test_action" in registry.actions

    def test_get_registered_action(self):
        """Test getting a registered action"""
        registry = ActionRegistry()

        action_def = ActionDefinition(
            id="test_action",
            name="Test Action",
            category=ActionCategory.MAIN1
        )

        registry.register(action_def)
        retrieved = registry.get_action("test_action")

        assert retrieved is not None
        assert retrieved.id == "test_action"

    def test_get_nonexistent_action_returns_none(self):
        """Test getting a nonexistent action returns None"""
        registry = ActionRegistry()

        retrieved = registry.get_action("does_not_exist")

        assert retrieved is None

    def test_get_actions_by_category(self):
        """Test getting actions by category"""
        registry = ActionRegistry()

        action1 = ActionDefinition(
            id="move1", name="Move 1", category=ActionCategory.MOVEMENT
        )
        action2 = ActionDefinition(
            id="move2", name="Move 2", category=ActionCategory.MOVEMENT
        )
        action3 = ActionDefinition(
            id="draw1", name="Draw 1", category=ActionCategory.DRAWING
        )

        registry.register(action1)
        registry.register(action2)
        registry.register(action3)

        movement_actions = registry.get_actions_by_category(ActionCategory.MOVEMENT)

        assert len(movement_actions) == 2
        assert all(a.category == ActionCategory.MOVEMENT for a in movement_actions)


class TestEventSystem:
    """Test EventSystem class"""

    def test_event_system_can_be_created(self, event_system):
        """Test creating an EventSystem instance"""
        assert event_system is not None

    def test_event_system_is_qobject(self, event_system):
        """Test that EventSystem is a QObject (for signals)"""
        from PySide6.QtCore import QObject
        assert isinstance(event_system, QObject)

    def test_event_system_has_action_registry(self, event_system):
        """Test that EventSystem has an action registry"""
        assert hasattr(event_system, 'action_registry')

    def test_create_event(self, event_system):
        """Test creating an event through EventSystem"""
        event = event_system.create_event(
            EventType.CREATE,
            "obj_player"
        )

        assert event is not None
        assert event.event_type == EventType.CREATE
        assert event.object_name == "obj_player"

    def test_add_event_to_system(self, event_system):
        """Test adding an event to the event system"""
        event = GameEvent(
            event_type=EventType.CREATE,
            object_name="obj_player"
        )

        event_system.add_event(event)

        events = event_system.get_events("obj_player")
        assert len(events) > 0

    def test_get_events_for_object(self, event_system):
        """Test getting all events for an object"""
        event1 = GameEvent(
            event_type=EventType.CREATE,
            object_name="obj_player"
        )
        event2 = GameEvent(
            event_type=EventType.STEP,
            object_name="obj_player"
        )

        event_system.add_event(event1)
        event_system.add_event(event2)

        events = event_system.get_events("obj_player")

        assert len(events) >= 2

    def test_remove_event(self, event_system):
        """Test removing an event"""
        event = GameEvent(
            event_type=EventType.CREATE,
            object_name="obj_player"
        )

        event_system.add_event(event)
        initial_count = len(event_system.get_events("obj_player"))

        event_system.remove_event("obj_player", EventType.CREATE)

        final_count = len(event_system.get_events("obj_player"))
        assert final_count < initial_count


# ============================================================================
# Integration Tests (Event System + Actions)
# ============================================================================

class TestEventSystemIntegration:
    """Integration tests for EventSystem with actions"""

    def test_complete_workflow(self, event_system):
        """Test complete workflow: register action, create event, add action"""
        # Register an action
        action_def = ActionDefinition(
            id="set_speed",
            name="Set Speed",
            category=ActionCategory.MOVEMENT,
            parameters={"speed": {"type": "number", "default": 5}}
        )
        event_system.action_registry.register(action_def)

        # Create an event
        event = event_system.create_event(EventType.CREATE, "obj_player")

        # Create and add an action
        action = EventAction(
            action_id="set_speed",
            parameters={"speed": 10}
        )
        event.add_action(action)

        # Add event to system
        event_system.add_event(event)

        # Verify
        events = event_system.get_events("obj_player")
        assert len(events) > 0

        found_event = None
        for e in events:
            if e.event_type == EventType.CREATE:
                found_event = e
                break

        assert found_event is not None
        assert len(found_event.actions) == 1
        assert found_event.actions[0].action_id == "set_speed"


# ============================================================================
# Parametrized Tests
# ============================================================================

@pytest.mark.parametrize("event_type", [
    EventType.CREATE,
    EventType.DESTROY,
    EventType.STEP,
    EventType.COLLISION,
    EventType.DRAW
])
def test_create_different_event_types(event_type):
    """Test creating events of different types"""
    event = GameEvent(
        event_type=event_type,
        object_name="obj_test"
    )

    assert event.event_type == event_type


@pytest.mark.parametrize("category", [
    ActionCategory.MOVEMENT,
    ActionCategory.CONTROL,
    ActionCategory.DRAWING,
    ActionCategory.SOUND
])
def test_create_actions_in_different_categories(category):
    """Test creating action definitions in different categories"""
    action_def = ActionDefinition(
        id=f"test_{category.value}",
        name=f"Test {category.value}",
        category=category
    )

    assert action_def.category == category
