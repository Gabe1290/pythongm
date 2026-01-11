#!/usr/bin/env python3
"""
Tests for the ActionExecutor class.

These tests verify the action execution engine which converts visual actions
into runtime behavior.

The ActionExecutor does not require pygame - it only depends on standard Python.
We import it directly from the module file to avoid the runtime package's
__init__.py which imports GameRunner (requiring pygame).
"""

import pytest

# Import helper from conftest for direct module loading
from conftest import import_module_directly

# Import ActionExecutor directly from the module file, bypassing the package __init__.py
# This avoids the pygame dependency from game_runner.py
_action_executor_module = import_module_directly("runtime/action_executor.py")
ActionExecutor = _action_executor_module.ActionExecutor


class MockInstance:
    """Mock game instance for testing action execution"""

    def __init__(self, object_name="test_object"):
        self.object_name = object_name
        self.x = 100.0
        self.y = 100.0
        self.xstart = 100.0
        self.ystart = 100.0
        self.hspeed = 0.0
        self.vspeed = 0.0
        self.alarm = [-1] * 12
        self.image_index = 0.0
        self.image_speed = 1.0
        self.to_destroy = False
        self.intended_x = None
        self.intended_y = None
        self.pending_messages = []
        self.restart_room_flag = False
        self.next_room_flag = False
        self.previous_room_flag = False
        self.keys_pressed = set()
        self.collision_checks = []
        self.object_data = {'events': {}}
        self._cached_width = 32
        self._cached_height = 32


class MockRoom:
    """Mock room for testing"""

    def __init__(self):
        self.name = "test_room"
        self.width = 640
        self.height = 480
        self.instances = []

    def _add_to_grid(self, instance):
        pass


class MockGameRunner:
    """Mock game runner for testing action execution"""

    def __init__(self):
        self.score = 0
        self.lives = 3
        self.health = 100.0
        self.global_variables = {}
        self.highscores = []
        self.show_score_in_caption = False
        self.show_lives_in_caption = False
        self.show_health_in_caption = False
        self.window_caption = ""
        self.current_room = MockRoom()
        self.project_data = {'assets': {'objects': {}}}
        self.sprites = {}
        self._room_list = ["room1", "room2", "room3"]

    def get_room_list(self):
        return self._room_list

    def check_collision_at_position(self, instance, x, y, object_type, exclude=None):
        return False

    def trigger_no_more_lives_event(self, instance):
        """Mock trigger for no more lives event"""
        pass

    def trigger_no_more_health_event(self, instance):
        """Mock trigger for no more health event"""
        pass


# ==============================================================================
# ActionExecutor Initialization Tests
# ==============================================================================

class TestActionExecutorInit:
    """Tests for ActionExecutor initialization and handler discovery"""

    def test_action_executor_creates_without_game_runner(self):
        """ActionExecutor can be created without a game runner"""
        executor = ActionExecutor(game_runner=None)
        assert executor.game_runner is None
        assert len(executor.action_handlers) > 0

    def test_action_executor_creates_with_game_runner(self):
        """ActionExecutor can be created with a game runner reference"""
        mock_runner = MockGameRunner()
        executor = ActionExecutor(game_runner=mock_runner)
        assert executor.game_runner == mock_runner

    def test_action_handlers_auto_discovered(self):
        """Action handlers are automatically discovered from method names"""
        executor = ActionExecutor()

        # Check that core action handlers were discovered
        expected_handlers = [
            'move_grid', 'set_hspeed', 'set_vspeed', 'stop_movement',
            'show_message', 'restart_room', 'next_room', 'destroy_instance',
            'set_score', 'set_lives', 'set_health', 'set_alarm',
            'set_variable', 'test_variable', 'if_collision'
        ]

        for handler_name in expected_handlers:
            assert handler_name in executor.action_handlers, f"Handler '{handler_name}' not found"

    def test_register_custom_action(self):
        """Custom action handlers can be registered dynamically"""
        executor = ActionExecutor()

        def custom_handler(instance, parameters):
            instance.custom_flag = True

        executor.register_custom_action("my_custom_action", custom_handler)
        assert "my_custom_action" in executor.action_handlers

        # Test execution
        instance = MockInstance()
        executor.action_handlers["my_custom_action"](instance, {})
        assert instance.custom_flag is True


# ==============================================================================
# Movement Action Tests
# ==============================================================================

class TestMovementActions:
    """Tests for movement-related actions"""

    def test_move_grid_right(self):
        """move_grid action moves instance to the right"""
        # ActionExecutor imported at module level
        executor = ActionExecutor()
        instance = MockInstance()

        executor.execute_move_grid_action(instance, {"direction": "right", "grid_size": 32})
        assert instance.intended_x == 132.0  # 100 + 32
        assert instance.intended_y == 100.0

    def test_move_grid_left(self):
        """move_grid action moves instance to the left"""
        # ActionExecutor imported at module level
        executor = ActionExecutor()
        instance = MockInstance()

        executor.execute_move_grid_action(instance, {"direction": "left", "grid_size": 32})
        assert instance.intended_x == 68.0  # 100 - 32
        assert instance.intended_y == 100.0

    def test_move_grid_up(self):
        """move_grid action moves instance up"""
        # ActionExecutor imported at module level
        executor = ActionExecutor()
        instance = MockInstance()

        executor.execute_move_grid_action(instance, {"direction": "up", "grid_size": 32})
        assert instance.intended_x == 100.0
        assert instance.intended_y == 68.0  # 100 - 32

    def test_move_grid_down(self):
        """move_grid action moves instance down"""
        # ActionExecutor imported at module level
        executor = ActionExecutor()
        instance = MockInstance()

        executor.execute_move_grid_action(instance, {"direction": "down", "grid_size": 32})
        assert instance.intended_x == 100.0
        assert instance.intended_y == 132.0  # 100 + 32

    def test_set_hspeed(self):
        """set_hspeed action sets horizontal speed"""
        # ActionExecutor imported at module level
        executor = ActionExecutor()
        instance = MockInstance()

        executor.execute_set_hspeed_action(instance, {"hspeed": 5})
        assert instance.hspeed == 5.0

    def test_set_vspeed(self):
        """set_vspeed action sets vertical speed"""
        # ActionExecutor imported at module level
        executor = ActionExecutor()
        instance = MockInstance()

        executor.execute_set_vspeed_action(instance, {"vspeed": -3})
        assert instance.vspeed == -3.0

    def test_stop_movement(self):
        """stop_movement action sets both speeds to zero"""
        # ActionExecutor imported at module level
        executor = ActionExecutor()
        instance = MockInstance()
        instance.hspeed = 5.0
        instance.vspeed = 3.0

        executor.execute_stop_movement_action(instance, {})
        assert instance.hspeed == 0.0
        assert instance.vspeed == 0.0

    def test_snap_to_grid(self):
        """snap_to_grid action snaps position to nearest grid cell"""
        # ActionExecutor imported at module level
        executor = ActionExecutor()
        instance = MockInstance()
        instance.x = 105.0  # Off-grid
        instance.y = 118.0  # Off-grid

        executor.execute_snap_to_grid_action(instance, {"grid_size": 32})
        assert instance.x == 96.0  # Snapped to nearest grid (3 * 32)
        assert instance.y == 128.0  # Snapped to nearest grid (4 * 32)

    def test_jump_to_position_absolute(self):
        """jump_to_position with absolute coordinates"""
        # ActionExecutor imported at module level
        executor = ActionExecutor()
        instance = MockInstance()

        executor.execute_jump_to_position_action(instance, {"x": 200, "y": 300, "relative": False})
        # Position is set directly (no grid snapping outside collision events)
        assert instance.x == 200.0
        assert instance.y == 300.0

    def test_jump_to_position_relative(self):
        """jump_to_position with relative coordinates"""
        # ActionExecutor imported at module level
        executor = ActionExecutor()
        instance = MockInstance()
        instance.x = 96.0  # On grid
        instance.y = 96.0  # On grid

        executor.execute_jump_to_position_action(instance, {"x": 32, "y": 64, "relative": True, "push_other": False})
        assert instance.x == 128.0  # 96 + 32
        assert instance.y == 160.0  # 96 + 64

    def test_jump_to_start(self):
        """jump_to_start returns instance to starting position"""
        # ActionExecutor imported at module level
        executor = ActionExecutor()
        instance = MockInstance()
        instance.xstart = 50.0
        instance.ystart = 75.0
        instance.x = 200.0
        instance.y = 300.0

        executor.execute_jump_to_start_action(instance, {})
        assert instance.x == 50.0
        assert instance.y == 75.0

    def test_start_moving_direction(self):
        """start_moving_direction sets speed in a given direction"""
        executor = ActionExecutor()
        instance = MockInstance()

        # Move right at speed 4
        executor.execute_start_moving_direction_action(instance, {"directions": "right", "speed": 4})
        assert abs(instance.hspeed - 4.0) < 0.01
        assert abs(instance.vspeed) < 0.01

        # Move up at speed 4
        instance.hspeed = 0
        instance.vspeed = 0
        executor.execute_start_moving_direction_action(instance, {"directions": "up", "speed": 4})
        assert abs(instance.hspeed) < 0.01
        assert abs(instance.vspeed - (-4.0)) < 0.01  # Up is negative in screen coords


# ==============================================================================
# Grid Utility Tests
# ==============================================================================

class TestGridUtilities:
    """Tests for grid-related utility actions"""

    def test_if_on_grid_returns_true(self):
        """if_on_grid returns True when on grid"""
        # ActionExecutor imported at module level
        executor = ActionExecutor()
        instance = MockInstance()
        instance.x = 64.0  # On 32px grid
        instance.y = 96.0  # On 32px grid

        result = executor.execute_if_on_grid_action(instance, {"grid_size": 32})
        assert result is True

    def test_if_on_grid_returns_false(self):
        """if_on_grid returns False when off grid"""
        # ActionExecutor imported at module level
        executor = ActionExecutor()
        instance = MockInstance()
        instance.x = 70.0  # Not on 32px grid
        instance.y = 96.0  # On 32px grid

        result = executor.execute_if_on_grid_action(instance, {"grid_size": 32})
        assert result is False

    def test_if_on_grid_snaps_when_close(self):
        """if_on_grid snaps to grid when very close"""
        # ActionExecutor imported at module level
        executor = ActionExecutor()
        instance = MockInstance()
        instance.x = 64.2  # Close to grid
        instance.y = 95.8  # Close to grid

        result = executor.execute_if_on_grid_action(instance, {"grid_size": 32})
        assert result is True
        assert instance.x == 64.0  # Snapped
        assert instance.y == 96.0  # Snapped

    def test_stop_if_no_keys(self):
        """stop_if_no_keys stops movement and snaps to grid"""
        # ActionExecutor imported at module level
        executor = ActionExecutor()
        instance = MockInstance()
        instance.hspeed = 4.0
        instance.vspeed = 2.0
        instance.x = 65.0  # Slightly off grid
        instance.y = 97.0  # Slightly off grid

        executor.execute_stop_if_no_keys_action(instance, {"grid_size": 32})
        assert instance.hspeed == 0.0
        assert instance.vspeed == 0.0
        assert instance.x == 64.0  # Snapped
        assert instance.y == 96.0  # Snapped


# ==============================================================================
# Game Action Tests
# ==============================================================================

class TestGameActions:
    """Tests for game-related actions (messages, rooms, etc.)"""

    def test_show_message(self):
        """show_message stores pending message"""
        # ActionExecutor imported at module level
        executor = ActionExecutor()
        instance = MockInstance()

        executor.execute_show_message_action(instance, {"message": "Hello World!"})
        assert "Hello World!" in instance.pending_messages

    def test_restart_room(self):
        """restart_room sets restart flag"""
        # ActionExecutor imported at module level
        executor = ActionExecutor()
        instance = MockInstance()

        executor.execute_restart_room_action(instance, {})
        assert instance.restart_room_flag is True

    def test_next_room(self):
        """next_room sets next room flag"""
        # ActionExecutor imported at module level
        executor = ActionExecutor()
        instance = MockInstance()

        executor.execute_next_room_action(instance, {})
        assert instance.next_room_flag is True

    def test_previous_room(self):
        """previous_room sets previous room flag"""
        # ActionExecutor imported at module level
        executor = ActionExecutor()
        instance = MockInstance()

        executor.execute_previous_room_action(instance, {})
        assert instance.previous_room_flag is True

    def test_if_next_room_exists_true(self):
        """if_next_room_exists returns True when next room exists"""
        # ActionExecutor imported at module level
        mock_runner = MockGameRunner()
        mock_runner.current_room.name = "room1"  # First room, so next exists
        executor = ActionExecutor(game_runner=mock_runner)
        instance = MockInstance()

        result = executor.execute_if_next_room_exists_action(instance, {})
        assert result is True

    def test_if_next_room_exists_false(self):
        """if_next_room_exists returns False when no next room"""
        # ActionExecutor imported at module level
        mock_runner = MockGameRunner()
        mock_runner.current_room.name = "room3"  # Last room
        executor = ActionExecutor(game_runner=mock_runner)
        instance = MockInstance()

        result = executor.execute_if_next_room_exists_action(instance, {})
        assert result is False


# ==============================================================================
# Instance Action Tests
# ==============================================================================

class TestInstanceActions:
    """Tests for instance-related actions"""

    def test_destroy_instance_self(self):
        """destroy_instance with target self marks instance for destruction"""
        # ActionExecutor imported at module level
        executor = ActionExecutor()
        instance = MockInstance()

        executor.execute_destroy_instance_action(instance, {"target": "self"})
        assert instance.to_destroy is True

    def test_destroy_instance_other(self):
        """destroy_instance with target other marks other for destruction"""
        # ActionExecutor imported at module level
        executor = ActionExecutor()
        instance = MockInstance()
        other = MockInstance("other_object")
        executor._collision_other = other

        executor.execute_destroy_instance_action(instance, {"target": "other"})
        assert other.to_destroy is True
        assert instance.to_destroy is False


# ==============================================================================
# Score/Lives/Health Tests
# ==============================================================================

class TestScoreLivesHealthActions:
    """Tests for score, lives, and health actions"""

    def test_set_score_absolute(self):
        """set_score sets score to absolute value"""
        # ActionExecutor imported at module level
        mock_runner = MockGameRunner()
        executor = ActionExecutor(game_runner=mock_runner)
        instance = MockInstance()

        executor.execute_set_score_action(instance, {"value": 100})
        assert mock_runner.score == 100
        assert mock_runner.show_score_in_caption is True

    def test_set_score_relative(self):
        """set_score with relative flag adds to score"""
        # ActionExecutor imported at module level
        mock_runner = MockGameRunner()
        mock_runner.score = 50
        executor = ActionExecutor(game_runner=mock_runner)
        instance = MockInstance()

        executor.execute_set_score_action(instance, {"value": 25, "relative": True})
        assert mock_runner.score == 75

    def test_set_lives_absolute(self):
        """set_lives sets lives to absolute value"""
        # ActionExecutor imported at module level
        mock_runner = MockGameRunner()
        executor = ActionExecutor(game_runner=mock_runner)
        instance = MockInstance()

        executor.execute_set_lives_action(instance, {"value": 5})
        assert mock_runner.lives == 5
        assert mock_runner.show_lives_in_caption is True

    def test_set_lives_relative_decrease(self):
        """set_lives with relative flag can decrease lives"""
        # ActionExecutor imported at module level
        mock_runner = MockGameRunner()
        mock_runner.lives = 3
        executor = ActionExecutor(game_runner=mock_runner)
        instance = MockInstance()

        executor.execute_set_lives_action(instance, {"value": -1, "relative": True})
        assert mock_runner.lives == 2

    def test_set_lives_clamps_to_zero(self):
        """set_lives cannot go below zero"""
        # ActionExecutor imported at module level
        mock_runner = MockGameRunner()
        mock_runner.lives = 1
        executor = ActionExecutor(game_runner=mock_runner)
        instance = MockInstance()

        executor.execute_set_lives_action(instance, {"value": -5, "relative": True})
        assert mock_runner.lives == 0

    def test_set_health_absolute(self):
        """set_health sets health to absolute value"""
        # ActionExecutor imported at module level
        mock_runner = MockGameRunner()
        executor = ActionExecutor(game_runner=mock_runner)
        instance = MockInstance()

        executor.execute_set_health_action(instance, {"value": 75})
        assert mock_runner.health == 75.0
        assert mock_runner.show_health_in_caption is True

    def test_set_health_clamps_to_range(self):
        """set_health clamps value between 0 and 100"""
        # ActionExecutor imported at module level
        mock_runner = MockGameRunner()
        executor = ActionExecutor(game_runner=mock_runner)
        instance = MockInstance()

        # Test upper clamp
        executor.execute_set_health_action(instance, {"value": 150})
        assert mock_runner.health == 100.0

        # Test lower clamp
        executor.execute_set_health_action(instance, {"value": -50})
        assert mock_runner.health == 0.0

    def test_test_score_equal(self):
        """test_score with equal operation"""
        # ActionExecutor imported at module level
        mock_runner = MockGameRunner()
        mock_runner.score = 100
        executor = ActionExecutor(game_runner=mock_runner)
        instance = MockInstance()

        assert executor.execute_test_score_action(instance, {"value": 100, "operation": "equal"}) is True
        assert executor.execute_test_score_action(instance, {"value": 50, "operation": "equal"}) is False

    def test_test_score_greater(self):
        """test_score with greater operation"""
        # ActionExecutor imported at module level
        mock_runner = MockGameRunner()
        mock_runner.score = 100
        executor = ActionExecutor(game_runner=mock_runner)
        instance = MockInstance()

        assert executor.execute_test_score_action(instance, {"value": 50, "operation": "greater"}) is True
        assert executor.execute_test_score_action(instance, {"value": 150, "operation": "greater"}) is False


# ==============================================================================
# Alarm Tests
# ==============================================================================

class TestAlarmActions:
    """Tests for alarm-related actions"""

    def test_set_alarm(self):
        """set_alarm sets alarm to specified steps"""
        # ActionExecutor imported at module level
        executor = ActionExecutor()
        instance = MockInstance()

        executor.execute_set_alarm_action(instance, {"alarm_number": 0, "steps": 30})
        assert instance.alarm[0] == 30

    def test_set_alarm_relative(self):
        """set_alarm with relative adds to current value"""
        # ActionExecutor imported at module level
        executor = ActionExecutor()
        instance = MockInstance()
        instance.alarm[0] = 20

        executor.execute_set_alarm_action(instance, {"alarm_number": 0, "steps": 10, "relative": True})
        assert instance.alarm[0] == 30

    def test_set_alarm_disable(self):
        """set_alarm with -1 disables alarm"""
        # ActionExecutor imported at module level
        executor = ActionExecutor()
        instance = MockInstance()
        instance.alarm[0] = 30

        executor.execute_set_alarm_action(instance, {"alarm_number": 0, "steps": -1})
        assert instance.alarm[0] == -1

    def test_set_alarm_validates_number(self):
        """set_alarm validates alarm number is 0-11"""
        # ActionExecutor imported at module level
        executor = ActionExecutor()
        instance = MockInstance()

        # Should not raise but also not modify invalid alarm
        executor.execute_set_alarm_action(instance, {"alarm_number": 15, "steps": 30})
        # All alarms should remain at -1
        assert all(a == -1 for a in instance.alarm)


# ==============================================================================
# Variable Action Tests
# ==============================================================================

class TestVariableActions:
    """Tests for variable manipulation actions"""

    def test_set_variable_self(self):
        """set_variable on self sets instance variable"""
        # ActionExecutor imported at module level
        executor = ActionExecutor()
        instance = MockInstance()

        executor.execute_set_variable_action(instance, {
            "variable": "my_var",
            "value": 42,
            "scope": "self"
        })
        assert instance.my_var == 42

    def test_set_variable_relative(self):
        """set_variable with relative adds to current value"""
        # ActionExecutor imported at module level
        executor = ActionExecutor()
        instance = MockInstance()
        instance.my_var = 10

        executor.execute_set_variable_action(instance, {
            "variable": "my_var",
            "value": 5,
            "scope": "self",
            "relative": True
        })
        assert instance.my_var == 15

    def test_set_variable_global(self):
        """set_variable on global sets global variable"""
        # ActionExecutor imported at module level
        mock_runner = MockGameRunner()
        executor = ActionExecutor(game_runner=mock_runner)
        instance = MockInstance()

        executor.execute_set_variable_action(instance, {
            "variable": "global_var",
            "value": "hello",
            "scope": "global"
        })
        assert mock_runner.global_variables["global_var"] == "hello"

    def test_test_variable_equal(self):
        """test_variable with equal operation"""
        # ActionExecutor imported at module level
        executor = ActionExecutor()
        instance = MockInstance()
        instance.my_var = 42

        result = executor.execute_test_variable_action(instance, {
            "variable": "my_var",
            "value": 42,
            "operation": "equal"
        })
        assert result is True

    def test_test_variable_greater(self):
        """test_variable with greater operation"""
        # ActionExecutor imported at module level
        executor = ActionExecutor()
        instance = MockInstance()
        instance.my_var = 100

        result = executor.execute_test_variable_action(instance, {
            "variable": "my_var",
            "value": 50,
            "operation": "greater"
        })
        assert result is True


# ==============================================================================
# Animation Action Tests
# ==============================================================================

class TestAnimationActions:
    """Tests for animation-related actions"""

    def test_set_image_index(self):
        """set_image_index sets current frame"""
        # ActionExecutor imported at module level
        executor = ActionExecutor()
        instance = MockInstance()

        executor.execute_set_image_index_action(instance, {"frame": 3})
        assert instance.image_index == 3.0

    def test_set_image_speed(self):
        """set_image_speed sets animation speed"""
        # ActionExecutor imported at module level
        executor = ActionExecutor()
        instance = MockInstance()

        executor.execute_set_image_speed_action(instance, {"speed": 0.5})
        assert instance.image_speed == 0.5

    def test_stop_animation(self):
        """stop_animation sets image_speed to 0"""
        # ActionExecutor imported at module level
        executor = ActionExecutor()
        instance = MockInstance()
        instance.image_speed = 1.0

        executor.execute_stop_animation_action(instance, {})
        assert instance.image_speed == 0.0

    def test_start_animation(self):
        """start_animation sets image_speed to 1"""
        # ActionExecutor imported at module level
        executor = ActionExecutor()
        instance = MockInstance()
        instance.image_speed = 0.0

        executor.execute_start_animation_action(instance, {})
        assert instance.image_speed == 1.0


# ==============================================================================
# Value Parsing Tests
# ==============================================================================

class TestValueParsing:
    """Tests for value parsing (_parse_value method)"""

    def test_parse_integer(self):
        """Parses integer values"""
        # ActionExecutor imported at module level
        executor = ActionExecutor()

        assert executor._parse_value("42", None) == 42
        assert executor._parse_value("-5", None) == -5

    def test_parse_float(self):
        """Parses float values"""
        # ActionExecutor imported at module level
        executor = ActionExecutor()

        assert executor._parse_value("3.14", None) == 3.14
        assert executor._parse_value("-2.5", None) == -2.5

    def test_parse_boolean(self):
        """Parses boolean values"""
        # ActionExecutor imported at module level
        executor = ActionExecutor()

        assert executor._parse_value("true", None) is True
        assert executor._parse_value("false", None) is False
        assert executor._parse_value("TRUE", None) is True

    def test_parse_self_reference(self):
        """Parses self.variable references"""
        # ActionExecutor imported at module level
        executor = ActionExecutor()
        instance = MockInstance()
        instance.my_var = 123

        assert executor._parse_value("self.my_var", instance) == 123
        assert executor._parse_value("self.x", instance) == 100.0

    def test_parse_global_reference(self):
        """Parses global.variable references"""
        # ActionExecutor imported at module level
        mock_runner = MockGameRunner()
        mock_runner.global_variables["test_global"] = "hello"
        executor = ActionExecutor(game_runner=mock_runner)

        assert executor._parse_value("global.test_global", None) == "hello"

    def test_parse_bare_variable(self):
        """Parses bare variable names as instance variables"""
        # ActionExecutor imported at module level
        executor = ActionExecutor()
        instance = MockInstance()
        instance.custom_var = 99

        assert executor._parse_value("custom_var", instance) == 99

    def test_parse_quoted_string(self):
        """Parses quoted strings"""
        # ActionExecutor imported at module level
        executor = ActionExecutor()

        assert executor._parse_value('"hello world"', None) == "hello world"
        assert executor._parse_value("'test'", None) == "test"


# ==============================================================================
# Expression Evaluation Tests
# ==============================================================================

class TestExpressionEvaluation:
    """Tests for expression evaluation (_evaluate_expression method)"""

    def test_simple_arithmetic(self):
        """Evaluates simple arithmetic expressions"""
        # ActionExecutor imported at module level
        executor = ActionExecutor()

        assert executor._evaluate_expression("2 + 3", None) == 5
        assert executor._evaluate_expression("10 - 4", None) == 6
        assert executor._evaluate_expression("3 * 4", None) == 12
        assert executor._evaluate_expression("15 / 3", None) == 5.0

    def test_expression_with_self_vars(self):
        """Evaluates expressions with self.variable references"""
        # ActionExecutor imported at module level
        executor = ActionExecutor()
        instance = MockInstance()
        instance.hspeed = 4.0

        result = executor._evaluate_expression("self.hspeed * 8", instance)
        assert result == 32.0

    def test_expression_with_bare_vars(self):
        """Evaluates expressions with bare variable names"""
        # ActionExecutor imported at module level
        executor = ActionExecutor()
        instance = MockInstance()
        instance.x = 100.0

        result = executor._evaluate_expression("x + 50", instance)
        assert result == 150.0


# ==============================================================================
# Conditional Flow Tests
# ==============================================================================

class TestConditionalFlow:
    """Tests for conditional action flow (skip_next, blocks, etc.)"""

    def test_execute_action_list_simple(self):
        """Execute a simple action list"""
        # ActionExecutor imported at module level
        executor = ActionExecutor()
        instance = MockInstance()

        actions = [
            {"action": "set_hspeed", "parameters": {"hspeed": 5}},
            {"action": "set_vspeed", "parameters": {"vspeed": 3}}
        ]

        executor.execute_action_list(instance, actions)
        assert instance.hspeed == 5.0
        assert instance.vspeed == 3.0

    def test_conditional_skip_next_true(self):
        """When condition is true, next action executes"""
        # ActionExecutor imported at module level
        mock_runner = MockGameRunner()
        mock_runner.score = 100
        executor = ActionExecutor(game_runner=mock_runner)
        instance = MockInstance()

        actions = [
            {"action": "test_score", "parameters": {"value": 100, "operation": "equal"}},
            {"action": "set_hspeed", "parameters": {"hspeed": 5}}
        ]

        executor.execute_action_list(instance, actions)
        assert instance.hspeed == 5.0  # Should execute because score == 100

    def test_conditional_skip_next_false(self):
        """When condition is false, next action is skipped"""
        # ActionExecutor imported at module level
        mock_runner = MockGameRunner()
        mock_runner.score = 50
        executor = ActionExecutor(game_runner=mock_runner)
        instance = MockInstance()

        actions = [
            {"action": "test_score", "parameters": {"value": 100, "operation": "equal"}},
            {"action": "set_hspeed", "parameters": {"hspeed": 5}}
        ]

        executor.execute_action_list(instance, actions)
        assert instance.hspeed == 0.0  # Should NOT execute because score != 100

    def test_block_skip_when_false(self):
        """When condition is false, entire block is skipped"""
        # ActionExecutor imported at module level
        mock_runner = MockGameRunner()
        mock_runner.score = 50
        executor = ActionExecutor(game_runner=mock_runner)
        instance = MockInstance()

        actions = [
            {"action": "test_score", "parameters": {"value": 100, "operation": "equal"}},
            {"action": "start_block", "parameters": {}},
            {"action": "set_hspeed", "parameters": {"hspeed": 5}},
            {"action": "set_vspeed", "parameters": {"vspeed": 3}},
            {"action": "end_block", "parameters": {}},
            {"action": "set_hspeed", "parameters": {"hspeed": 10}}  # After block
        ]

        executor.execute_action_list(instance, actions)
        assert instance.hspeed == 10.0  # Only the action after block executes
        assert instance.vspeed == 0.0  # Block was skipped

    def test_else_block(self):
        """Else block executes when condition is false"""
        # ActionExecutor imported at module level
        mock_runner = MockGameRunner()
        mock_runner.score = 50
        executor = ActionExecutor(game_runner=mock_runner)
        instance = MockInstance()

        actions = [
            {"action": "test_score", "parameters": {"value": 100, "operation": "equal"}},
            {"action": "set_hspeed", "parameters": {"hspeed": 5}},
            {"action": "else", "parameters": {}},
            {"action": "set_vspeed", "parameters": {"vspeed": 3}}
        ]

        executor.execute_action_list(instance, actions)
        assert instance.hspeed == 0.0  # Then part skipped
        assert instance.vspeed == 3.0  # Else part executed


# ==============================================================================
# Action Execution Tests
# ==============================================================================

class TestActionExecution:
    """Tests for general action execution"""

    def test_execute_action_with_alias(self):
        """Action aliases are resolved correctly"""
        # ActionExecutor imported at module level
        executor = ActionExecutor()
        instance = MockInstance()

        # "display_message" is an alias for "show_message"
        executor.execute_action(instance, {"action": "display_message", "parameters": {"message": "Test"}})
        assert "Test" in instance.pending_messages

    def test_execute_action_unknown_action(self):
        """Unknown actions are handled gracefully"""
        # ActionExecutor imported at module level
        executor = ActionExecutor()
        instance = MockInstance()

        # Should not raise
        result = executor.execute_action(instance, {"action": "nonexistent_action", "parameters": {}})
        assert result is None

    def test_execute_action_missing_action_field(self):
        """Missing action field is handled gracefully"""
        # ActionExecutor imported at module level
        executor = ActionExecutor()
        instance = MockInstance()

        result = executor.execute_action(instance, {"parameters": {}})
        assert result is None

    def test_execute_event(self):
        """execute_event runs all actions in an event"""
        # ActionExecutor imported at module level
        executor = ActionExecutor()
        instance = MockInstance()

        events_data = {
            "step": {
                "actions": [
                    {"action": "set_hspeed", "parameters": {"hspeed": 2}},
                    {"action": "set_vspeed", "parameters": {"vspeed": 1}}
                ]
            }
        }

        executor.execute_event(instance, "step", events_data)
        assert instance.hspeed == 2.0
        assert instance.vspeed == 1.0

    def test_execute_event_nonexistent(self):
        """execute_event with nonexistent event does nothing"""
        # ActionExecutor imported at module level
        executor = ActionExecutor()
        instance = MockInstance()
        instance.hspeed = 5.0

        events_data = {}

        # Should not raise, should do nothing
        executor.execute_event(instance, "nonexistent", events_data)
        assert instance.hspeed == 5.0  # Unchanged


# ==============================================================================
# Collision Action Tests
# ==============================================================================

class TestCollisionActions:
    """Tests for collision-related actions"""

    def test_execute_collision_event(self):
        """Collision event executes with proper context"""
        # ActionExecutor imported at module level
        executor = ActionExecutor()
        instance = MockInstance()
        other = MockInstance("other_object")

        events_data = {
            "collision_with_wall": {
                "actions": [
                    {"action": "stop_movement", "parameters": {}}
                ]
            }
        }

        instance.hspeed = 5.0
        instance.vspeed = 3.0

        executor.execute_collision_event(
            instance, "collision_with_wall", events_data, other,
            collision_speeds={"self_hspeed": 5.0, "self_vspeed": 3.0}
        )

        assert instance.hspeed == 0.0
        assert instance.vspeed == 0.0

    def test_collision_event_destroy_other(self):
        """Collision event can destroy the other instance"""
        # ActionExecutor imported at module level
        executor = ActionExecutor()
        instance = MockInstance()
        other = MockInstance("enemy")

        events_data = {
            "collision_with_enemy": {
                "actions": [
                    {"action": "destroy_instance", "parameters": {"target": "other"}}
                ]
            }
        }

        executor.execute_collision_event(
            instance, "collision_with_enemy", events_data, other
        )

        assert other.to_destroy is True
        assert instance.to_destroy is False

    def test_bounce_action_horizontal(self):
        """bounce action reverses horizontal velocity"""
        # ActionExecutor imported at module level
        executor = ActionExecutor()
        instance = MockInstance()
        instance.hspeed = 5.0
        instance.vspeed = 0.0

        executor._collision_speeds = {
            "self_hspeed": 5.0,
            "self_vspeed": 0.0,
            "h_blocked": True,
            "v_blocked": False
        }

        executor.execute_bounce_action(instance, {})
        assert instance.hspeed == -5.0

    def test_bounce_action_vertical(self):
        """bounce action reverses vertical velocity"""
        # ActionExecutor imported at module level
        executor = ActionExecutor()
        instance = MockInstance()
        instance.hspeed = 0.0
        instance.vspeed = 4.0

        executor._collision_speeds = {
            "self_hspeed": 0.0,
            "self_vspeed": 4.0,
            "h_blocked": False,
            "v_blocked": True
        }

        executor.execute_bounce_action(instance, {})
        assert instance.vspeed == -4.0


# ==============================================================================
# Repeat Action Tests
# ==============================================================================

class TestRepeatAction:
    """Tests for repeat action functionality"""

    def test_repeat_single_action(self):
        """repeat action executes next action N times"""
        # ActionExecutor imported at module level
        mock_runner = MockGameRunner()
        executor = ActionExecutor(game_runner=mock_runner)
        instance = MockInstance()

        actions = [
            {"action": "repeat", "parameters": {"times": 3}},
            {"action": "set_score", "parameters": {"value": 10, "relative": True}}
        ]

        executor.execute_action_list(instance, actions)
        assert mock_runner.score == 30  # 10 * 3

    def test_repeat_zero_times(self):
        """repeat with 0 times skips the next action"""
        # ActionExecutor imported at module level
        mock_runner = MockGameRunner()
        executor = ActionExecutor(game_runner=mock_runner)
        instance = MockInstance()

        actions = [
            {"action": "repeat", "parameters": {"times": 0}},
            {"action": "set_score", "parameters": {"value": 100}}
        ]

        executor.execute_action_list(instance, actions)
        assert mock_runner.score == 0  # Action was skipped


# ==============================================================================
# If Collision Tests
# ==============================================================================

class TestIfCollisionAction:
    """Tests for if_collision action"""

    def test_if_collision_no_collision(self):
        """if_collision returns False when no collision"""
        # ActionExecutor imported at module level
        mock_runner = MockGameRunner()
        executor = ActionExecutor(game_runner=mock_runner)
        instance = MockInstance()

        result = executor.execute_if_collision_action(instance, {
            "x": 32,
            "y": 0,
            "object": "wall"
        })
        assert result is False

    def test_if_collision_with_not_flag(self):
        """if_collision with not_flag inverts result"""
        # ActionExecutor imported at module level
        mock_runner = MockGameRunner()
        executor = ActionExecutor(game_runner=mock_runner)
        instance = MockInstance()

        # No collision, but not_flag makes it True
        result = executor.execute_if_collision_action(instance, {
            "x": 32,
            "y": 0,
            "object": "wall",
            "not_flag": True
        })
        assert result is True


# ==============================================================================
# If Object Exists Tests
# ==============================================================================

class TestIfObjectExistsAction:
    """Tests for if_object_exists action"""

    def test_if_object_exists_found(self):
        """if_object_exists returns True when object exists"""
        # ActionExecutor imported at module level
        mock_runner = MockGameRunner()
        mock_runner.current_room.instances = [MockInstance("enemy")]
        executor = ActionExecutor(game_runner=mock_runner)
        instance = MockInstance()

        result = executor.execute_if_object_exists_action(instance, {"object": "enemy"})
        assert result is True

    def test_if_object_exists_not_found(self):
        """if_object_exists returns False when object not found"""
        # ActionExecutor imported at module level
        mock_runner = MockGameRunner()
        mock_runner.current_room.instances = [MockInstance("player")]
        executor = ActionExecutor(game_runner=mock_runner)
        instance = MockInstance()

        result = executor.execute_if_object_exists_action(instance, {"object": "enemy"})
        assert result is False

    def test_if_object_exists_with_not_flag(self):
        """if_object_exists with not_flag inverts result"""
        # ActionExecutor imported at module level
        mock_runner = MockGameRunner()
        mock_runner.current_room.instances = []
        executor = ActionExecutor(game_runner=mock_runner)
        instance = MockInstance()

        # No enemies, not_flag makes it True (good for "if no enemies left")
        result = executor.execute_if_object_exists_action(instance, {
            "object": "enemy",
            "not_flag": True
        })
        assert result is True


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
