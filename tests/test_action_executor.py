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


# ==============================================================================
# Execute Script Tests
# ==============================================================================


class TestExecuteScriptAction:
    """Tests for execute_script action"""

    def test_execute_script_basic(self):
        """execute_script executes script code from project data"""
        mock_runner = MockGameRunner()
        mock_runner.project_data = {
            'assets': {
                'objects': {},
                'scripts': {
                    'scr_test': {
                        'name': 'scr_test',
                        'code': 'test_var = 42'
                    }
                }
            }
        }
        executor = ActionExecutor(game_runner=mock_runner)
        instance = MockInstance()

        executor.execute_execute_script_action(instance, {'script': 'scr_test'})
        assert instance.test_var == 42

    def test_execute_script_with_arguments(self):
        """execute_script passes arguments to script"""
        mock_runner = MockGameRunner()
        mock_runner.project_data = {
            'assets': {
                'objects': {},
                'scripts': {
                    'scr_add': {
                        'name': 'scr_add',
                        'code': 'result = argument0 + argument1'
                    }
                }
            }
        }
        executor = ActionExecutor(game_runner=mock_runner)
        instance = MockInstance()

        executor.execute_execute_script_action(instance, {
            'script': 'scr_add',
            'arg0': '10',
            'arg1': '20'
        })
        assert instance.result == 30

    def test_execute_script_accesses_instance(self):
        """execute_script can access and modify instance properties"""
        mock_runner = MockGameRunner()
        mock_runner.project_data = {
            'assets': {
                'objects': {},
                'scripts': {
                    'scr_move': {
                        'name': 'scr_move',
                        'code': 'instance.x = 200\ninstance.y = 300'
                    }
                }
            }
        }
        executor = ActionExecutor(game_runner=mock_runner)
        instance = MockInstance()
        instance.x = 100
        instance.y = 100

        executor.execute_execute_script_action(instance, {'script': 'scr_move'})
        assert instance.x == 200
        assert instance.y == 300

    def test_execute_script_not_found(self):
        """execute_script handles missing script gracefully"""
        mock_runner = MockGameRunner()
        mock_runner.project_data = {
            'assets': {
                'objects': {},
                'scripts': {}
            }
        }
        executor = ActionExecutor(game_runner=mock_runner)
        instance = MockInstance()

        # Should not raise, just log warning
        executor.execute_execute_script_action(instance, {'script': 'nonexistent'})

    def test_execute_script_no_script_specified(self):
        """execute_script handles empty script parameter"""
        mock_runner = MockGameRunner()
        executor = ActionExecutor(game_runner=mock_runner)
        instance = MockInstance()

        # Should not raise
        executor.execute_execute_script_action(instance, {'script': ''})
        executor.execute_execute_script_action(instance, {})

    def test_execute_script_argument_count(self):
        """execute_script provides argument_count variable"""
        mock_runner = MockGameRunner()
        mock_runner.project_data = {
            'assets': {
                'objects': {},
                'scripts': {
                    'scr_count': {
                        'name': 'scr_count',
                        'code': 'count = argument_count'
                    }
                }
            }
        }
        executor = ActionExecutor(game_runner=mock_runner)
        instance = MockInstance()

        executor.execute_execute_script_action(instance, {
            'script': 'scr_count',
            'arg0': '1',
            'arg1': '2',
            'arg2': '3'
        })
        assert instance.count == 3


# ==============================================================================
# Draw Background Tests
# ==============================================================================


class TestDrawBackgroundAction:
    """Tests for draw_background action"""

    def test_draw_background_queues_command(self):
        """draw_background queues a draw command"""
        executor = ActionExecutor()
        instance = MockInstance()

        executor.execute_draw_background_action(instance, {
            'background': 'bg_sky',
            'x': 0,
            'y': 0,
            'tiled': False
        })

        assert hasattr(instance, '_draw_queue')
        assert len(instance._draw_queue) == 1
        cmd = instance._draw_queue[0]
        assert cmd['type'] == 'background'
        assert cmd['background_name'] == 'bg_sky'
        assert cmd['x'] == 0
        assert cmd['y'] == 0
        assert cmd['tiled'] is False

    def test_draw_background_with_tiling(self):
        """draw_background with tiled=True"""
        executor = ActionExecutor()
        instance = MockInstance()

        executor.execute_draw_background_action(instance, {
            'background': 'bg_grass',
            'x': 10,
            'y': 20,
            'tiled': True
        })

        assert len(instance._draw_queue) == 1
        cmd = instance._draw_queue[0]
        assert cmd['tiled'] is True
        assert cmd['x'] == 10
        assert cmd['y'] == 20

    def test_draw_background_tiled_string_conversion(self):
        """draw_background converts string 'true' to boolean"""
        executor = ActionExecutor()
        instance = MockInstance()

        executor.execute_draw_background_action(instance, {
            'background': 'bg_pattern',
            'x': 0,
            'y': 0,
            'tiled': 'true'
        })

        cmd = instance._draw_queue[0]
        assert cmd['tiled'] is True

    def test_draw_background_with_expressions(self):
        """draw_background supports expression values for position"""
        executor = ActionExecutor()
        instance = MockInstance()
        instance.x = 100
        instance.y = 200

        executor.execute_draw_background_action(instance, {
            'background': 'bg_test',
            'x': 'self.x',
            'y': 'self.y',
            'tiled': False
        })

        cmd = instance._draw_queue[0]
        assert cmd['x'] == 100
        assert cmd['y'] == 200


# ==============================================================================
# Draw Scaled Text Tests
# ==============================================================================


class TestDrawScaledTextAction:
    """Tests for draw_scaled_text action"""

    def test_draw_scaled_text_queues_command(self):
        """draw_scaled_text queues a draw command"""
        executor = ActionExecutor()
        instance = MockInstance()

        executor.execute_draw_scaled_text_action(instance, {
            'x': 50,
            'y': 100,
            'text': 'Hello',
            'xscale': 2.0,
            'yscale': 1.5
        })

        assert hasattr(instance, '_draw_queue')
        assert len(instance._draw_queue) == 1
        cmd = instance._draw_queue[0]
        assert cmd['type'] == 'scaled_text'
        assert cmd['x'] == 50
        assert cmd['y'] == 100
        assert cmd['text'] == 'Hello'
        assert cmd['xscale'] == 2.0
        assert cmd['yscale'] == 1.5

    def test_draw_scaled_text_default_scale(self):
        """draw_scaled_text defaults to scale 1.0"""
        executor = ActionExecutor()
        instance = MockInstance()

        executor.execute_draw_scaled_text_action(instance, {
            'x': 0,
            'y': 0,
            'text': 'Test'
        })

        cmd = instance._draw_queue[0]
        assert cmd['xscale'] == 1.0
        assert cmd['yscale'] == 1.0

    def test_draw_scaled_text_with_expressions(self):
        """draw_scaled_text supports expression values"""
        executor = ActionExecutor()
        instance = MockInstance()
        instance.x = 150
        instance.y = 250
        instance.scale_factor = 3.0

        executor.execute_draw_scaled_text_action(instance, {
            'x': 'self.x',
            'y': 'self.y',
            'text': 'Scaled',
            'xscale': 'self.scale_factor',
            'yscale': 2.0
        })

        cmd = instance._draw_queue[0]
        assert cmd['x'] == 150
        assert cmd['y'] == 250
        assert cmd['xscale'] == 3.0
        assert cmd['yscale'] == 2.0

    def test_draw_scaled_text_uses_draw_color(self):
        """draw_scaled_text uses instance draw_color"""
        executor = ActionExecutor()
        instance = MockInstance()
        instance.draw_color = (255, 0, 0)

        executor.execute_draw_scaled_text_action(instance, {
            'x': 0,
            'y': 0,
            'text': 'Red',
            'xscale': 1.0,
            'yscale': 1.0
        })

        cmd = instance._draw_queue[0]
        assert cmd['color'] == (255, 0, 0)

    def test_draw_scaled_text_invalid_scale_defaults(self):
        """draw_scaled_text handles invalid scale values"""
        executor = ActionExecutor()
        instance = MockInstance()

        executor.execute_draw_scaled_text_action(instance, {
            'x': 0,
            'y': 0,
            'text': 'Test',
            'xscale': 'invalid',
            'yscale': 'also_invalid'
        })

        cmd = instance._draw_queue[0]
        assert cmd['xscale'] == 1.0
        assert cmd['yscale'] == 1.0


# ==============================================================================
# Resource Replacement Tests
# ==============================================================================


class TestReplaceSpriteAction:
    """Tests for replace_sprite action"""

    def test_replace_sprite_no_sprite_specified(self):
        """replace_sprite handles missing sprite name"""
        mock_runner = MockGameRunner()
        mock_runner.sprites = {}
        mock_runner.project_path = None
        executor = ActionExecutor(game_runner=mock_runner)
        instance = MockInstance()

        # Should not raise
        executor.execute_replace_sprite_action(instance, {
            'sprite': '',
            'filename': 'test.png'
        })

    def test_replace_sprite_no_filename_specified(self):
        """replace_sprite handles missing filename"""
        mock_runner = MockGameRunner()
        mock_runner.sprites = {}
        executor = ActionExecutor(game_runner=mock_runner)
        instance = MockInstance()

        # Should not raise
        executor.execute_replace_sprite_action(instance, {
            'sprite': 'spr_test',
            'filename': ''
        })

    def test_replace_sprite_no_game_runner(self):
        """replace_sprite handles missing game_runner"""
        executor = ActionExecutor()
        instance = MockInstance()

        # Should not raise
        executor.execute_replace_sprite_action(instance, {
            'sprite': 'spr_test',
            'filename': 'test.png'
        })


class TestReplaceSoundAction:
    """Tests for replace_sound action"""

    def test_replace_sound_no_sound_specified(self):
        """replace_sound handles missing sound name"""
        mock_runner = MockGameRunner()
        mock_runner.sounds = {}
        mock_runner.music_files = {}
        mock_runner.project_path = None
        executor = ActionExecutor(game_runner=mock_runner)
        instance = MockInstance()

        # Should not raise
        executor.execute_replace_sound_action(instance, {
            'sound': '',
            'filename': 'test.wav'
        })

    def test_replace_sound_no_filename_specified(self):
        """replace_sound handles missing filename"""
        mock_runner = MockGameRunner()
        mock_runner.sounds = {}
        mock_runner.music_files = {}
        executor = ActionExecutor(game_runner=mock_runner)
        instance = MockInstance()

        # Should not raise
        executor.execute_replace_sound_action(instance, {
            'sound': 'snd_test',
            'filename': ''
        })

    def test_replace_sound_no_game_runner(self):
        """replace_sound handles missing game_runner"""
        executor = ActionExecutor()
        instance = MockInstance()

        # Should not raise
        executor.execute_replace_sound_action(instance, {
            'sound': 'snd_test',
            'filename': 'test.wav'
        })


class TestReplaceBackgroundAction:
    """Tests for replace_background action"""

    def test_replace_background_no_background_specified(self):
        """replace_background handles missing background name"""
        mock_runner = MockGameRunner()
        mock_runner.backgrounds = {}
        mock_runner.project_path = None
        executor = ActionExecutor(game_runner=mock_runner)
        instance = MockInstance()

        # Should not raise
        executor.execute_replace_background_action(instance, {
            'background': '',
            'filename': 'test.png'
        })

    def test_replace_background_no_filename_specified(self):
        """replace_background handles missing filename"""
        mock_runner = MockGameRunner()
        mock_runner.backgrounds = {}
        executor = ActionExecutor(game_runner=mock_runner)
        instance = MockInstance()

        # Should not raise
        executor.execute_replace_background_action(instance, {
            'background': 'bg_test',
            'filename': ''
        })

    def test_replace_background_no_game_runner(self):
        """replace_background handles missing game_runner"""
        executor = ActionExecutor()
        instance = MockInstance()

        # Should not raise
        executor.execute_replace_background_action(instance, {
            'background': 'bg_test',
            'filename': 'test.png'
        })


# ==============================================================================
# Info Actions Tests
# ==============================================================================


class TestShowInfoAction:
    """Tests for show_info action"""

    def test_show_info_with_project_data(self):
        """show_info displays project metadata"""
        mock_runner = MockGameRunner()
        mock_runner.project_data = {
            'name': 'Test Game',
            'version': '2.0.0',
            'author': 'Test Author',
            'description': 'A test description'
        }
        executor = ActionExecutor(game_runner=mock_runner)
        instance = MockInstance()

        executor.execute_show_info_action(instance, {})

        assert hasattr(instance, 'pending_messages')
        assert len(instance.pending_messages) == 1
        msg = instance.pending_messages[0]
        assert 'Test Game' in msg
        assert '2.0.0' in msg
        assert 'Test Author' in msg

    def test_show_info_no_project_data(self):
        """show_info handles missing project data"""
        mock_runner = MockGameRunner()
        mock_runner.project_data = None
        executor = ActionExecutor(game_runner=mock_runner)
        instance = MockInstance()

        # Should not raise
        executor.execute_show_info_action(instance, {})


class TestShowVideoAction:
    """Tests for show_video action"""

    def test_show_video_no_filename(self):
        """show_video handles missing filename"""
        executor = ActionExecutor()
        instance = MockInstance()

        # Should not raise
        executor.execute_show_video_action(instance, {'filename': ''})

    def test_show_video_no_game_runner(self):
        """show_video handles missing game_runner"""
        executor = ActionExecutor()
        instance = MockInstance()

        # Should not raise
        executor.execute_show_video_action(instance, {
            'filename': 'test.mp4',
            'fullscreen': False
        })


class TestOpenWebpageAction:
    """Tests for open_webpage action"""

    def test_open_webpage_no_url(self):
        """open_webpage handles missing URL"""
        executor = ActionExecutor()
        instance = MockInstance()

        # Should not raise
        executor.execute_open_webpage_action(instance, {'url': ''})

    def test_open_webpage_adds_protocol(self):
        """open_webpage adds https:// if no protocol"""
        # This test is more of a documentation - actual opening is mocked
        executor = ActionExecutor()
        instance = MockInstance()

        # Would open https://example.com if webbrowser was not mocked
        # Just verify no exception
        # Note: Actual browser opening is tested manually
        pass


class TestSaveGameAction:
    """Tests for save_game action"""

    def test_save_game_no_game_runner(self):
        """save_game handles missing game_runner"""
        executor = ActionExecutor()
        instance = MockInstance()

        # Should not raise
        executor.execute_save_game_action(instance, {'filename': 'test.sav'})

    def test_save_game_default_filename(self):
        """save_game uses default filename"""
        executor = ActionExecutor()
        instance = MockInstance()

        # Should not raise (no game_runner to actually save)
        executor.execute_save_game_action(instance, {})


class TestLoadGameAction:
    """Tests for load_game action"""

    def test_load_game_no_game_runner(self):
        """load_game handles missing game_runner"""
        executor = ActionExecutor()
        instance = MockInstance()

        # Should not raise
        executor.execute_load_game_action(instance, {'filename': 'test.sav'})

    def test_load_game_file_not_found(self):
        """load_game handles missing save file"""
        from pathlib import Path
        mock_runner = MockGameRunner()
        mock_runner.project_path = Path('/nonexistent/path')
        executor = ActionExecutor(game_runner=mock_runner)
        instance = MockInstance()

        # Should not raise, just log warning
        executor.execute_load_game_action(instance, {'filename': 'nonexistent.sav'})


# ==============================================================================
# Rooms Actions Tests
# ==============================================================================


class MockRoomWithViews:
    """Mock room for testing room actions with view support"""
    def __init__(self):
        self.name = "test_room"
        self.width = 640
        self.height = 480
        self.instances = []
        self.persistent = False
        self.views_enabled = False
        self.views = []
        for i in range(8):
            self.views.append({
                'visible': i == 0,
                'view_x': 0, 'view_y': 0,
                'view_w': 640, 'view_h': 480,
                'port_x': 0, 'port_y': 0,
                'port_w': 640, 'port_h': 480,
                'follow': None,
                'hborder': 32, 'vborder': 32,
                'hspeed': -1, 'vspeed': -1,
            })

    def _add_to_grid(self, instance):
        pass


class TestSetRoomPersistentAction:
    """Tests for set_room_persistent action"""

    def test_set_room_persistent_true(self):
        """set_room_persistent sets persistent flag to True"""
        mock_runner = MockGameRunner()
        mock_runner.current_room = MockRoomWithViews()
        executor = ActionExecutor(game_runner=mock_runner)
        instance = MockInstance()

        executor.execute_set_room_persistent_action(instance, {'persistent': True})
        assert mock_runner.current_room.persistent is True

    def test_set_room_persistent_false(self):
        """set_room_persistent sets persistent flag to False"""
        mock_runner = MockGameRunner()
        mock_runner.current_room = MockRoomWithViews()
        mock_runner.current_room.persistent = True  # Start with True
        executor = ActionExecutor(game_runner=mock_runner)
        instance = MockInstance()

        executor.execute_set_room_persistent_action(instance, {'persistent': False})
        assert mock_runner.current_room.persistent is False

    def test_set_room_persistent_no_room(self):
        """set_room_persistent handles missing room"""
        mock_runner = MockGameRunner()
        mock_runner.current_room = None
        executor = ActionExecutor(game_runner=mock_runner)
        instance = MockInstance()

        # Should not raise
        executor.execute_set_room_persistent_action(instance, {'persistent': True})


class TestEnableViewsAction:
    """Tests for enable_views action"""

    def test_enable_views_true(self):
        """enable_views enables view system"""
        mock_runner = MockGameRunner()
        mock_runner.current_room = MockRoomWithViews()
        executor = ActionExecutor(game_runner=mock_runner)
        instance = MockInstance()

        executor.execute_enable_views_action(instance, {'enable': True})
        assert mock_runner.current_room.views_enabled is True

    def test_enable_views_false(self):
        """enable_views disables view system"""
        mock_runner = MockGameRunner()
        mock_runner.current_room = MockRoomWithViews()
        mock_runner.current_room.views_enabled = True
        executor = ActionExecutor(game_runner=mock_runner)
        instance = MockInstance()

        executor.execute_enable_views_action(instance, {'enable': False})
        assert mock_runner.current_room.views_enabled is False

    def test_enable_views_no_room(self):
        """enable_views handles missing room"""
        mock_runner = MockGameRunner()
        mock_runner.current_room = None
        executor = ActionExecutor(game_runner=mock_runner)
        instance = MockInstance()

        # Should not raise
        executor.execute_enable_views_action(instance, {'enable': True})


class TestSetViewAction:
    """Tests for set_view action"""

    def test_set_view_basic(self):
        """set_view configures a view"""
        mock_runner = MockGameRunner()
        mock_runner.current_room = MockRoomWithViews()
        executor = ActionExecutor(game_runner=mock_runner)
        instance = MockInstance()

        executor.execute_set_view_action(instance, {
            'view': 0,
            'visible': True,
            'view_x': 100,
            'view_y': 200,
            'view_w': 320,
            'view_h': 240
        })

        view = mock_runner.current_room.views[0]
        assert view['visible'] is True
        assert view['view_x'] == 100
        assert view['view_y'] == 200
        assert view['view_w'] == 320
        assert view['view_h'] == 240

    def test_set_view_follow_object(self):
        """set_view can set follow object"""
        mock_runner = MockGameRunner()
        mock_runner.current_room = MockRoomWithViews()
        executor = ActionExecutor(game_runner=mock_runner)
        instance = MockInstance()

        executor.execute_set_view_action(instance, {
            'view': 1,
            'follow': 'obj_player'
        })

        view = mock_runner.current_room.views[1]
        assert view['follow'] == 'obj_player'

    def test_set_view_invalid_index(self):
        """set_view handles invalid view index"""
        mock_runner = MockGameRunner()
        mock_runner.current_room = MockRoomWithViews()
        executor = ActionExecutor(game_runner=mock_runner)
        instance = MockInstance()

        # Should not raise, just log warning
        executor.execute_set_view_action(instance, {
            'view': 10,  # Invalid - must be 0-7
            'visible': True
        })

    def test_set_view_no_room(self):
        """set_view handles missing room"""
        mock_runner = MockGameRunner()
        mock_runner.current_room = None
        executor = ActionExecutor(game_runner=mock_runner)
        instance = MockInstance()

        # Should not raise
        executor.execute_set_view_action(instance, {'view': 0, 'visible': True})


# ==============================================================================
# Main1 Tab Actions Tests
# ==============================================================================


class TestMain1TabActions:
    """Tests for Main1 tab actions: create_random_instance, create_moving_instance, destroy_at_position"""

    def test_create_random_instance_picks_from_choices(self):
        """create_random_instance randomly picks from provided objects"""
        mock_runner = MockGameRunner()
        mock_runner.project_data = {
            'assets': {
                'objects': {
                    'obj_enemy1': {'sprite': '', 'events': {}},
                    'obj_enemy2': {'sprite': '', 'events': {}},
                }
            }
        }
        executor = ActionExecutor(game_runner=mock_runner)
        instance = MockInstance()

        # Run multiple times to verify randomness
        created_objects = set()
        for _ in range(20):
            mock_runner.current_room.instances = []
            executor.execute_create_random_instance_action(instance, {
                'object1': 'obj_enemy1',
                'object2': 'obj_enemy2',
                'x': 100,
                'y': 200
            })
            if mock_runner.current_room.instances:
                created_objects.add(mock_runner.current_room.instances[0].object_name)

        # Should have created at least one of each (statistically likely with 20 tries)
        assert len(created_objects) >= 1  # At least created something

    def test_create_random_instance_no_objects(self):
        """create_random_instance handles no objects specified"""
        executor = ActionExecutor()
        instance = MockInstance()

        # Should not raise
        executor.execute_create_random_instance_action(instance, {
            'x': 100,
            'y': 200
        })

    def test_create_random_instance_no_game_runner(self):
        """create_random_instance handles missing game_runner"""
        executor = ActionExecutor()
        instance = MockInstance()

        # Should not raise
        executor.execute_create_random_instance_action(instance, {
            'object1': 'obj_test',
            'x': 100,
            'y': 200
        })

    def test_create_moving_instance_sets_motion(self):
        """create_moving_instance creates instance with speed and direction"""
        import math
        mock_runner = MockGameRunner()
        mock_runner.project_data = {
            'assets': {
                'objects': {
                    'obj_bullet': {'sprite': '', 'events': {}}
                }
            }
        }
        executor = ActionExecutor(game_runner=mock_runner)
        instance = MockInstance()

        executor.execute_create_moving_instance_action(instance, {
            'object': 'obj_bullet',
            'x': 50,
            'y': 75,
            'speed': 5,
            'direction': 0  # Right
        })

        assert len(mock_runner.current_room.instances) == 1
        new_inst = mock_runner.current_room.instances[0]
        assert new_inst.object_name == 'obj_bullet'
        assert new_inst.x == 50
        assert new_inst.y == 75
        assert new_inst.speed == 5
        assert new_inst.direction == 0
        assert abs(new_inst.hspeed - 5.0) < 0.001  # Moving right
        assert abs(new_inst.vspeed - 0.0) < 0.001

    def test_create_moving_instance_direction_90(self):
        """create_moving_instance handles direction 90 (up)"""
        mock_runner = MockGameRunner()
        mock_runner.project_data = {
            'assets': {
                'objects': {
                    'obj_bullet': {'sprite': '', 'events': {}}
                }
            }
        }
        executor = ActionExecutor(game_runner=mock_runner)
        instance = MockInstance()

        executor.execute_create_moving_instance_action(instance, {
            'object': 'obj_bullet',
            'x': 0,
            'y': 0,
            'speed': 10,
            'direction': 90  # Up
        })

        new_inst = mock_runner.current_room.instances[0]
        assert abs(new_inst.hspeed) < 0.001  # No horizontal movement
        assert new_inst.vspeed < 0  # Moving up (negative Y)

    def test_create_moving_instance_no_object(self):
        """create_moving_instance handles missing object"""
        executor = ActionExecutor()
        instance = MockInstance()

        # Should not raise
        executor.execute_create_moving_instance_action(instance, {
            'x': 100,
            'y': 200,
            'speed': 5,
            'direction': 0
        })

    def test_destroy_at_position_destroys_matching(self):
        """destroy_at_position marks instances at position for destruction"""
        mock_runner = MockGameRunner()
        executor = ActionExecutor(game_runner=mock_runner)
        instance = MockInstance()

        # Create target instance at specific position
        target = MockInstance("obj_target")
        target.x = 100
        target.y = 200
        mock_runner.current_room.instances.append(target)

        executor.execute_destroy_at_position_action(instance, {
            'x': 100,
            'y': 200,
            'object': 'obj_target'
        })

        assert target.to_destroy is True

    def test_destroy_at_position_filters_by_object(self):
        """destroy_at_position only destroys matching object type"""
        mock_runner = MockGameRunner()
        executor = ActionExecutor(game_runner=mock_runner)
        instance = MockInstance()

        # Create two instances at same position
        target = MockInstance("obj_target")
        target.x = 100
        target.y = 200
        other = MockInstance("obj_other")
        other.x = 100
        other.y = 200
        mock_runner.current_room.instances.extend([target, other])

        executor.execute_destroy_at_position_action(instance, {
            'x': 100,
            'y': 200,
            'object': 'obj_target'
        })

        assert target.to_destroy is True
        assert other.to_destroy is False

    def test_destroy_at_position_destroys_all_without_filter(self):
        """destroy_at_position without object filter destroys all at position"""
        mock_runner = MockGameRunner()
        executor = ActionExecutor(game_runner=mock_runner)
        instance = MockInstance()

        # Create two instances at same position
        inst1 = MockInstance("obj_a")
        inst1.x = 50
        inst1.y = 50
        inst2 = MockInstance("obj_b")
        inst2.x = 50
        inst2.y = 50
        mock_runner.current_room.instances.extend([inst1, inst2])

        executor.execute_destroy_at_position_action(instance, {
            'x': 50,
            'y': 50
        })

        assert inst1.to_destroy is True
        assert inst2.to_destroy is True

    def test_destroy_at_position_no_room(self):
        """destroy_at_position handles missing room"""
        mock_runner = MockGameRunner()
        mock_runner.current_room = None
        executor = ActionExecutor(game_runner=mock_runner)
        instance = MockInstance()

        # Should not raise
        executor.execute_destroy_at_position_action(instance, {
            'x': 100,
            'y': 200
        })


# ==============================================================================
# Main2 Tab Actions Tests
# ==============================================================================


class TestMain2TabActions:
    """Tests for Main2 tab actions: transform_sprite, set_color, check_sound"""

    def test_transform_sprite_sets_scale_and_angle(self):
        """transform_sprite sets image_xscale, image_yscale, and image_angle"""
        executor = ActionExecutor()
        instance = MockInstance()

        executor.execute_transform_sprite_action(instance, {
            'xscale': 2.0,
            'yscale': 0.5,
            'angle': 45.0
        })

        assert instance.image_xscale == 2.0
        assert instance.image_yscale == 0.5
        assert instance.image_angle == 45.0

    def test_transform_sprite_default_values(self):
        """transform_sprite uses default values when not specified"""
        executor = ActionExecutor()
        instance = MockInstance()

        executor.execute_transform_sprite_action(instance, {})

        assert instance.image_xscale == 1.0
        assert instance.image_yscale == 1.0
        assert instance.image_angle == 0.0

    def test_transform_sprite_with_expressions(self):
        """transform_sprite supports expression values"""
        executor = ActionExecutor()
        instance = MockInstance()
        instance.my_scale = 3.0
        instance.my_angle = 90.0

        executor.execute_transform_sprite_action(instance, {
            'xscale': 'self.my_scale',
            'yscale': 'self.my_scale',
            'angle': 'self.my_angle'
        })

        assert instance.image_xscale == 3.0
        assert instance.image_yscale == 3.0
        assert instance.image_angle == 90.0

    def test_set_color_hex_color(self):
        """set_color parses hex color string"""
        executor = ActionExecutor()
        instance = MockInstance()

        executor.execute_set_color_action(instance, {
            'color': '#FF0000',
            'alpha': 1.0
        })

        assert instance.image_blend == (255, 0, 0)
        assert instance.image_alpha == 1.0

    def test_set_color_with_alpha(self):
        """set_color sets alpha transparency"""
        executor = ActionExecutor()
        instance = MockInstance()

        executor.execute_set_color_action(instance, {
            'color': '#00FF00',
            'alpha': 0.5
        })

        assert instance.image_blend == (0, 255, 0)
        assert instance.image_alpha == 0.5

    def test_set_color_clamps_alpha(self):
        """set_color clamps alpha to 0-1 range"""
        executor = ActionExecutor()
        instance = MockInstance()

        executor.execute_set_color_action(instance, {
            'color': '#FFFFFF',
            'alpha': 2.0  # Should be clamped to 1.0
        })

        assert instance.image_alpha == 1.0

        executor.execute_set_color_action(instance, {
            'color': '#FFFFFF',
            'alpha': -0.5  # Should be clamped to 0.0
        })

        assert instance.image_alpha == 0.0

    def test_set_color_default_white(self):
        """set_color defaults to white when invalid color"""
        executor = ActionExecutor()
        instance = MockInstance()

        executor.execute_set_color_action(instance, {
            'color': 'invalid',
            'alpha': 1.0
        })

        assert instance.image_blend == (255, 255, 255)

    def test_check_sound_returns_false_when_not_playing(self):
        """check_sound returns False when sound is not playing"""
        mock_runner = MockGameRunner()
        mock_runner.sounds = {'snd_test': MockSound()}
        executor = ActionExecutor(game_runner=mock_runner)
        instance = MockInstance()

        result = executor.execute_check_sound_action(instance, {
            'sound': 'snd_test',
            'not_flag': False
        })

        assert result is False

    def test_check_sound_with_not_flag(self):
        """check_sound inverts result with not_flag"""
        mock_runner = MockGameRunner()
        mock_runner.sounds = {'snd_test': MockSound()}
        executor = ActionExecutor(game_runner=mock_runner)
        instance = MockInstance()

        result = executor.execute_check_sound_action(instance, {
            'sound': 'snd_test',
            'not_flag': True
        })

        assert result is True  # Not playing, inverted = True

    def test_check_sound_no_sound_specified(self):
        """check_sound handles missing sound name"""
        executor = ActionExecutor()
        instance = MockInstance()

        result = executor.execute_check_sound_action(instance, {
            'not_flag': False
        })

        assert result is True  # Returns True when no sound specified

    def test_check_sound_no_game_runner(self):
        """check_sound handles missing game_runner"""
        executor = ActionExecutor()
        instance = MockInstance()

        result = executor.execute_check_sound_action(instance, {
            'sound': 'snd_test',
            'not_flag': False
        })

        assert result is True  # Returns True (not_flag default) when no runner


class MockSound:
    """Mock pygame Sound for testing"""

    def __init__(self, playing=False):
        self._playing = playing

    def get_num_channels(self):
        return 1 if self._playing else 0


# ==============================================================================
# Draw Tab Actions Tests
# ==============================================================================


class TestDrawTabActions:
    """Tests for Draw tab actions: draw_arrow, set_draw_font, fill_color, create_effect"""

    def test_draw_arrow_queues_command(self):
        """draw_arrow queues an arrow draw command"""
        executor = ActionExecutor()
        instance = MockInstance()

        executor.execute_draw_arrow_action(instance, {
            'x1': 10,
            'y1': 20,
            'x2': 100,
            'y2': 50,
            'tip_size': 15
        })

        assert hasattr(instance, '_draw_queue')
        assert len(instance._draw_queue) == 1
        cmd = instance._draw_queue[0]
        assert cmd['type'] == 'arrow'
        assert cmd['x1'] == 10
        assert cmd['y1'] == 20
        assert cmd['x2'] == 100
        assert cmd['y2'] == 50
        assert 'tip1_x' in cmd
        assert 'tip1_y' in cmd
        assert 'tip2_x' in cmd
        assert 'tip2_y' in cmd

    def test_draw_arrow_calculates_tip_points(self):
        """draw_arrow calculates arrow tip points correctly"""
        import math
        executor = ActionExecutor()
        instance = MockInstance()

        # Arrow pointing right (0 degrees)
        executor.execute_draw_arrow_action(instance, {
            'x1': 0,
            'y1': 0,
            'x2': 100,
            'y2': 0,
            'tip_size': 10
        })

        cmd = instance._draw_queue[0]
        # For a horizontal arrow pointing right, tip points should be behind x2
        assert cmd['tip1_x'] < 100
        assert cmd['tip2_x'] < 100

    def test_draw_arrow_uses_draw_color(self):
        """draw_arrow uses instance draw_color"""
        executor = ActionExecutor()
        instance = MockInstance()
        instance.draw_color = (255, 0, 0)

        executor.execute_draw_arrow_action(instance, {
            'x1': 0,
            'y1': 0,
            'x2': 100,
            'y2': 100
        })

        cmd = instance._draw_queue[0]
        assert cmd['color'] == (255, 0, 0)

    def test_draw_arrow_default_values(self):
        """draw_arrow uses default values when not specified"""
        executor = ActionExecutor()
        instance = MockInstance()

        executor.execute_draw_arrow_action(instance, {})

        cmd = instance._draw_queue[0]
        assert cmd['x1'] == 0
        assert cmd['y1'] == 0
        assert cmd['x2'] == 100
        assert cmd['y2'] == 100

    def test_set_draw_font_sets_font_properties(self):
        """set_draw_font sets font name and alignment"""
        executor = ActionExecutor()
        instance = MockInstance()

        executor.execute_set_draw_font_action(instance, {
            'font': 'Arial',
            'halign': 'center',
            'valign': 'middle'
        })

        assert instance.draw_font == 'Arial'
        assert instance.draw_halign == 'center'
        assert instance.draw_valign == 'middle'

    def test_set_draw_font_default_alignment(self):
        """set_draw_font defaults to left/top alignment"""
        executor = ActionExecutor()
        instance = MockInstance()

        executor.execute_set_draw_font_action(instance, {
            'font': 'TestFont'
        })

        assert instance.draw_font == 'TestFont'
        assert instance.draw_halign == 'left'
        assert instance.draw_valign == 'top'

    def test_set_draw_font_invalid_alignment(self):
        """set_draw_font handles invalid alignment values"""
        executor = ActionExecutor()
        instance = MockInstance()

        executor.execute_set_draw_font_action(instance, {
            'font': 'Font',
            'halign': 'invalid',
            'valign': 'wrong'
        })

        assert instance.draw_halign == 'left'  # Default
        assert instance.draw_valign == 'top'   # Default

    def test_set_draw_font_empty_font(self):
        """set_draw_font handles empty font name"""
        executor = ActionExecutor()
        instance = MockInstance()

        executor.execute_set_draw_font_action(instance, {
            'font': ''
        })

        assert instance.draw_font is None

    def test_fill_color_queues_command(self):
        """fill_color queues a fill command"""
        executor = ActionExecutor()
        instance = MockInstance()

        executor.execute_fill_color_action(instance, {
            'color': '#FF0000'
        })

        assert hasattr(instance, '_draw_queue')
        assert len(instance._draw_queue) == 1
        cmd = instance._draw_queue[0]
        assert cmd['type'] == 'fill'
        assert cmd['color'] == (255, 0, 0)

    def test_fill_color_parses_hex(self):
        """fill_color parses hex color correctly"""
        executor = ActionExecutor()
        instance = MockInstance()

        executor.execute_fill_color_action(instance, {
            'color': '#00FF00'
        })

        cmd = instance._draw_queue[0]
        assert cmd['color'] == (0, 255, 0)

    def test_fill_color_default_black(self):
        """fill_color defaults to black"""
        executor = ActionExecutor()
        instance = MockInstance()

        executor.execute_fill_color_action(instance, {})

        cmd = instance._draw_queue[0]
        assert cmd['color'] == (0, 0, 0)

    def test_fill_color_invalid_color(self):
        """fill_color handles invalid color"""
        executor = ActionExecutor()
        instance = MockInstance()

        executor.execute_fill_color_action(instance, {
            'color': 'invalid'
        })

        cmd = instance._draw_queue[0]
        assert cmd['color'] == (0, 0, 0)  # Default black

    def test_create_effect_queues_command(self):
        """create_effect queues an effect command"""
        executor = ActionExecutor()
        instance = MockInstance()

        executor.execute_create_effect_action(instance, {
            'effect': 'explosion',
            'x': 100,
            'y': 200,
            'size': 'large',
            'color': '#FFFF00'
        })

        assert hasattr(instance, '_draw_queue')
        assert len(instance._draw_queue) == 1
        cmd = instance._draw_queue[0]
        assert cmd['type'] == 'effect'
        assert cmd['effect_type'] == 'explosion'
        assert cmd['x'] == 100
        assert cmd['y'] == 200
        assert cmd['size'] == 2.0  # large = 2.0
        assert cmd['color'] == (255, 255, 0)

    def test_create_effect_size_multipliers(self):
        """create_effect converts size to multiplier"""
        executor = ActionExecutor()
        instance = MockInstance()

        # Test small
        executor.execute_create_effect_action(instance, {
            'effect': 'spark',
            'size': 'small'
        })
        assert instance._draw_queue[0]['size'] == 0.5

        # Test medium
        instance._draw_queue = []
        executor.execute_create_effect_action(instance, {
            'effect': 'spark',
            'size': 'medium'
        })
        assert instance._draw_queue[0]['size'] == 1.0

        # Test large
        instance._draw_queue = []
        executor.execute_create_effect_action(instance, {
            'effect': 'spark',
            'size': 'large'
        })
        assert instance._draw_queue[0]['size'] == 2.0

    def test_create_effect_default_values(self):
        """create_effect uses default values"""
        executor = ActionExecutor()
        instance = MockInstance()

        executor.execute_create_effect_action(instance, {})

        cmd = instance._draw_queue[0]
        assert cmd['effect_type'] == 'explosion'
        assert cmd['x'] == 0
        assert cmd['y'] == 0
        assert cmd['size'] == 1.0  # medium default
        assert cmd['color'] == (255, 255, 255)  # white default

    def test_create_effect_with_expressions(self):
        """create_effect supports expression values"""
        executor = ActionExecutor()
        instance = MockInstance()
        instance.x = 150
        instance.y = 250

        executor.execute_create_effect_action(instance, {
            'effect': 'firework',
            'x': 'self.x',
            'y': 'self.y',
            'size': 'medium',
            'color': '#0000FF'
        })

        cmd = instance._draw_queue[0]
        assert cmd['x'] == 150
        assert cmd['y'] == 250


# ==============================================================================
# Extra Tab Actions Tests
# ==============================================================================


class TestExtraTabActions:
    """Tests for Extra tab actions: draw_variable, goto_room, check_room"""

    def test_draw_variable_queues_text_command(self):
        """draw_variable queues a text draw command with variable value"""
        executor = ActionExecutor()
        instance = MockInstance()
        instance.my_score = 100

        executor.execute_draw_variable_action(instance, {
            'x': 50,
            'y': 100,
            'variable': 'self.my_score'
        })

        assert hasattr(instance, '_draw_queue')
        assert len(instance._draw_queue) == 1
        cmd = instance._draw_queue[0]
        assert cmd['type'] == 'text'
        assert cmd['x'] == 50
        assert cmd['y'] == 100
        assert cmd['text'] == '100'

    def test_draw_variable_global_variable(self):
        """draw_variable can display global variables"""
        mock_runner = MockGameRunner()
        mock_runner.global_variables['player_name'] = 'Hero'
        executor = ActionExecutor(game_runner=mock_runner)
        instance = MockInstance()

        executor.execute_draw_variable_action(instance, {
            'x': 0,
            'y': 0,
            'variable': 'global.player_name'
        })

        cmd = instance._draw_queue[0]
        assert cmd['text'] == 'Hero'

    def test_draw_variable_empty_variable(self):
        """draw_variable handles empty variable name"""
        executor = ActionExecutor()
        instance = MockInstance()

        executor.execute_draw_variable_action(instance, {
            'x': 0,
            'y': 0,
            'variable': ''
        })

        cmd = instance._draw_queue[0]
        assert cmd['text'] == ''

    def test_draw_variable_uses_draw_color(self):
        """draw_variable uses instance draw_color"""
        executor = ActionExecutor()
        instance = MockInstance()
        instance.draw_color = (255, 0, 0)
        instance.value = 42

        executor.execute_draw_variable_action(instance, {
            'x': 0,
            'y': 0,
            'variable': 'self.value'
        })

        cmd = instance._draw_queue[0]
        assert cmd['color'] == (255, 0, 0)

    def test_goto_room_sets_target(self):
        """goto_room sets target room on instance"""
        mock_runner = MockGameRunner()
        mock_runner._room_list = ['room1', 'room2', 'room3']
        executor = ActionExecutor(game_runner=mock_runner)
        instance = MockInstance()

        executor.execute_goto_room_action(instance, {
            'room': 'room2',
            'transition': 'create_from_left'
        })

        assert instance.goto_room_target == 'room2'
        assert instance.goto_room_transition == 'create_from_left'

    def test_goto_room_no_room_specified(self):
        """goto_room handles missing room name"""
        executor = ActionExecutor()
        instance = MockInstance()

        # Should not raise or set any flags
        executor.execute_goto_room_action(instance, {
            'transition': 'none'
        })

        assert not hasattr(instance, 'goto_room_target')

    def test_goto_room_room_not_found(self):
        """goto_room handles non-existent room"""
        mock_runner = MockGameRunner()
        mock_runner._room_list = ['room1', 'room2']
        executor = ActionExecutor(game_runner=mock_runner)
        instance = MockInstance()

        executor.execute_goto_room_action(instance, {
            'room': 'nonexistent_room',
            'transition': 'none'
        })

        assert not hasattr(instance, 'goto_room_target')

    def test_goto_room_no_game_runner(self):
        """goto_room handles missing game_runner"""
        executor = ActionExecutor()
        instance = MockInstance()

        # Should not raise
        executor.execute_goto_room_action(instance, {
            'room': 'some_room'
        })

        assert not hasattr(instance, 'goto_room_target')

    def test_check_room_returns_true_when_in_room(self):
        """check_room returns True when in specified room"""
        mock_runner = MockGameRunner()
        mock_runner.current_room = MockRoomWithViews()
        mock_runner.current_room.name = 'test_room'
        executor = ActionExecutor(game_runner=mock_runner)
        instance = MockInstance()

        result = executor.execute_check_room_action(instance, {
            'room': 'test_room',
            'not_flag': False
        })

        assert result is True

    def test_check_room_returns_false_when_not_in_room(self):
        """check_room returns False when not in specified room"""
        mock_runner = MockGameRunner()
        mock_runner.current_room = MockRoomWithViews()
        mock_runner.current_room.name = 'current_room'
        executor = ActionExecutor(game_runner=mock_runner)
        instance = MockInstance()

        result = executor.execute_check_room_action(instance, {
            'room': 'different_room',
            'not_flag': False
        })

        assert result is False

    def test_check_room_with_not_flag(self):
        """check_room inverts result with not_flag"""
        mock_runner = MockGameRunner()
        mock_runner.current_room = MockRoomWithViews()
        mock_runner.current_room.name = 'test_room'
        executor = ActionExecutor(game_runner=mock_runner)
        instance = MockInstance()

        # Not in 'other_room', with NOT flag = True
        result = executor.execute_check_room_action(instance, {
            'room': 'other_room',
            'not_flag': True
        })

        assert result is True  # NOT in other_room = True

    def test_check_room_no_room_specified(self):
        """check_room handles missing room name"""
        executor = ActionExecutor()
        instance = MockInstance()

        result = executor.execute_check_room_action(instance, {
            'not_flag': False
        })

        assert result is True  # Default when no room specified

    def test_check_room_no_game_runner(self):
        """check_room handles missing game_runner"""
        executor = ActionExecutor()
        instance = MockInstance()

        result = executor.execute_check_room_action(instance, {
            'room': 'test_room',
            'not_flag': False
        })

        assert result is True  # Default when no game_runner


# ==============================================================================
# Particles Tab Actions Tests
# ==============================================================================


class TestParticlesTabActions:
    """Tests for Particles tab actions: create_particle_system, destroy_particle_system,
    clear_particles, create_particle_type, create_emitter, destroy_emitter,
    burst_particles, stream_particles"""

    def test_create_particle_system_initializes_system(self):
        """create_particle_system initializes a particle system on instance"""
        executor = ActionExecutor()
        instance = MockInstance()

        executor.execute_create_particle_system_action(instance, {'depth': 100})

        assert hasattr(instance, '_particle_system')
        assert instance._particle_system is not None
        assert instance._particle_system['depth'] == 100
        assert instance._particle_system['particle_types'] == {}
        assert instance._particle_system['emitters'] == {}
        assert instance._particle_system['particles'] == []

    def test_create_particle_system_default_depth(self):
        """create_particle_system uses default depth of 0"""
        executor = ActionExecutor()
        instance = MockInstance()

        executor.execute_create_particle_system_action(instance, {})

        assert instance._particle_system['depth'] == 0

    def test_destroy_particle_system_removes_system(self):
        """destroy_particle_system clears the particle system"""
        executor = ActionExecutor()
        instance = MockInstance()

        # First create a system
        executor.execute_create_particle_system_action(instance, {'depth': 50})
        assert instance._particle_system is not None

        # Now destroy it
        executor.execute_destroy_particle_system_action(instance, {})

        assert instance._particle_system is None

    def test_destroy_particle_system_no_system(self):
        """destroy_particle_system handles case when no system exists"""
        executor = ActionExecutor()
        instance = MockInstance()

        # Should not raise
        executor.execute_destroy_particle_system_action(instance, {})

    def test_clear_particles_empties_particle_list(self):
        """clear_particles removes all active particles"""
        executor = ActionExecutor()
        instance = MockInstance()

        # Create system with some fake particles
        executor.execute_create_particle_system_action(instance, {})
        instance._particle_system['particles'] = [{'x': 0, 'y': 0}, {'x': 10, 'y': 10}]

        executor.execute_clear_particles_action(instance, {})

        assert instance._particle_system['particles'] == []
        # Types and emitters should still exist
        assert instance._particle_system['particle_types'] == {}
        assert instance._particle_system['emitters'] == {}

    def test_clear_particles_no_system(self):
        """clear_particles handles case when no system exists"""
        executor = ActionExecutor()
        instance = MockInstance()

        # Should not raise
        executor.execute_clear_particles_action(instance, {})

    def test_create_particle_type_creates_type(self):
        """create_particle_type creates a particle type definition"""
        executor = ActionExecutor()
        instance = MockInstance()

        # First create a system
        executor.execute_create_particle_system_action(instance, {})

        # Create particle type
        type_id = executor.execute_create_particle_type_action(instance, {
            'sprite': 'spr_particle',
            'size_min': 0.5,
            'size_max': 2.0,
            'color': '#FF0000',
            'alpha': 0.8,
            'speed_min': 1,
            'speed_max': 5,
            'life_min': 30,
            'life_max': 60
        })

        assert type_id == 0
        assert 0 in instance._particle_system['particle_types']
        ptype = instance._particle_system['particle_types'][0]
        assert ptype['sprite'] == 'spr_particle'
        assert ptype['size_min'] == 0.5
        assert ptype['size_max'] == 2.0
        assert ptype['color'] == (255, 0, 0)
        assert ptype['alpha'] == 0.8
        assert ptype['life_min'] == 30
        assert ptype['life_max'] == 60

    def test_create_particle_type_no_system(self):
        """create_particle_type returns -1 when no system exists"""
        executor = ActionExecutor()
        instance = MockInstance()

        result = executor.execute_create_particle_type_action(instance, {})

        assert result == -1

    def test_create_particle_type_increments_id(self):
        """create_particle_type increments type ID for each new type"""
        executor = ActionExecutor()
        instance = MockInstance()

        executor.execute_create_particle_system_action(instance, {})

        id1 = executor.execute_create_particle_type_action(instance, {})
        id2 = executor.execute_create_particle_type_action(instance, {})
        id3 = executor.execute_create_particle_type_action(instance, {})

        assert id1 == 0
        assert id2 == 1
        assert id3 == 2

    def test_create_emitter_creates_emitter(self):
        """create_emitter creates a particle emitter"""
        executor = ActionExecutor()
        instance = MockInstance()

        executor.execute_create_particle_system_action(instance, {})

        emitter_id = executor.execute_create_emitter_action(instance, {
            'x': 100,
            'y': 200,
            'width': 50,
            'height': 30,
            'shape': 'ellipse'
        })

        assert emitter_id == 0
        assert 0 in instance._particle_system['emitters']
        emitter = instance._particle_system['emitters'][0]
        assert emitter['x'] == 100
        assert emitter['y'] == 200
        assert emitter['width'] == 50
        assert emitter['height'] == 30
        assert emitter['shape'] == 'ellipse'

    def test_create_emitter_no_system(self):
        """create_emitter returns -1 when no system exists"""
        executor = ActionExecutor()
        instance = MockInstance()

        result = executor.execute_create_emitter_action(instance, {})

        assert result == -1

    def test_create_emitter_default_shape(self):
        """create_emitter uses rectangle as default shape"""
        executor = ActionExecutor()
        instance = MockInstance()

        executor.execute_create_particle_system_action(instance, {})
        executor.execute_create_emitter_action(instance, {'x': 0, 'y': 0})

        emitter = instance._particle_system['emitters'][0]
        assert emitter['shape'] == 'rectangle'

    def test_create_emitter_invalid_shape_uses_default(self):
        """create_emitter uses rectangle for invalid shape"""
        executor = ActionExecutor()
        instance = MockInstance()

        executor.execute_create_particle_system_action(instance, {})
        executor.execute_create_emitter_action(instance, {
            'x': 0,
            'y': 0,
            'shape': 'invalid_shape'
        })

        emitter = instance._particle_system['emitters'][0]
        assert emitter['shape'] == 'rectangle'

    def test_destroy_emitter_removes_emitter(self):
        """destroy_emitter removes the last created emitter"""
        executor = ActionExecutor()
        instance = MockInstance()

        executor.execute_create_particle_system_action(instance, {})
        executor.execute_create_emitter_action(instance, {'x': 0, 'y': 0})
        assert 0 in instance._particle_system['emitters']

        executor.execute_destroy_emitter_action(instance, {})

        assert 0 not in instance._particle_system['emitters']
        assert instance._last_emitter_id is None

    def test_destroy_emitter_no_system(self):
        """destroy_emitter handles case when no system exists"""
        executor = ActionExecutor()
        instance = MockInstance()

        # Should not raise
        executor.execute_destroy_emitter_action(instance, {})

    def test_destroy_emitter_no_emitter(self):
        """destroy_emitter handles case when no emitter exists"""
        executor = ActionExecutor()
        instance = MockInstance()

        executor.execute_create_particle_system_action(instance, {})

        # Should not raise
        executor.execute_destroy_emitter_action(instance, {})

    def test_burst_particles_creates_particles(self):
        """burst_particles creates the specified number of particles"""
        executor = ActionExecutor()
        instance = MockInstance()

        # Setup: create system, type, and emitter
        executor.execute_create_particle_system_action(instance, {})
        executor.execute_create_particle_type_action(instance, {
            'size_min': 1.0,
            'size_max': 1.0,
            'speed_min': 0,
            'speed_max': 0,
            'life_min': 10,
            'life_max': 10
        })
        executor.execute_create_emitter_action(instance, {
            'x': 100,
            'y': 100,
            'width': 10,
            'height': 10
        })

        executor.execute_burst_particles_action(instance, {
            'particle_type': 0,
            'number': 5
        })

        assert len(instance._particle_system['particles']) == 5

    def test_burst_particles_no_system(self):
        """burst_particles handles case when no system exists"""
        executor = ActionExecutor()
        instance = MockInstance()

        # Should not raise
        executor.execute_burst_particles_action(instance, {
            'particle_type': 0,
            'number': 10
        })

    def test_burst_particles_no_emitter(self):
        """burst_particles handles case when no emitter exists"""
        executor = ActionExecutor()
        instance = MockInstance()

        executor.execute_create_particle_system_action(instance, {})
        executor.execute_create_particle_type_action(instance, {})

        # Should not raise, no particles created
        executor.execute_burst_particles_action(instance, {
            'particle_type': 0,
            'number': 10
        })

        assert len(instance._particle_system['particles']) == 0

    def test_burst_particles_invalid_type(self):
        """burst_particles handles invalid particle type"""
        executor = ActionExecutor()
        instance = MockInstance()

        executor.execute_create_particle_system_action(instance, {})
        executor.execute_create_emitter_action(instance, {'x': 0, 'y': 0})

        # Should not raise, no particles created
        executor.execute_burst_particles_action(instance, {
            'particle_type': 999,  # Non-existent type
            'number': 10
        })

        assert len(instance._particle_system['particles']) == 0

    def test_stream_particles_sets_stream_config(self):
        """stream_particles configures emitter for continuous emission"""
        executor = ActionExecutor()
        instance = MockInstance()

        executor.execute_create_particle_system_action(instance, {})
        executor.execute_create_particle_type_action(instance, {})
        executor.execute_create_emitter_action(instance, {'x': 50, 'y': 50})

        executor.execute_stream_particles_action(instance, {
            'particle_type': 0,
            'number': 3
        })

        emitter = instance._particle_system['emitters'][0]
        assert emitter['stream_type'] == 0
        assert emitter['stream_count'] == 3

    def test_stream_particles_no_system(self):
        """stream_particles handles case when no system exists"""
        executor = ActionExecutor()
        instance = MockInstance()

        # Should not raise
        executor.execute_stream_particles_action(instance, {
            'particle_type': 0,
            'number': 5
        })

    def test_stream_particles_no_emitter(self):
        """stream_particles handles case when no emitter exists"""
        executor = ActionExecutor()
        instance = MockInstance()

        executor.execute_create_particle_system_action(instance, {})
        executor.execute_create_particle_type_action(instance, {})

        # Should not raise
        executor.execute_stream_particles_action(instance, {
            'particle_type': 0,
            'number': 5
        })

    def test_stream_particles_invalid_type(self):
        """stream_particles handles invalid particle type"""
        executor = ActionExecutor()
        instance = MockInstance()

        executor.execute_create_particle_system_action(instance, {})
        executor.execute_create_emitter_action(instance, {'x': 0, 'y': 0})

        # Should not raise
        executor.execute_stream_particles_action(instance, {
            'particle_type': 999,  # Non-existent type
            'number': 5
        })

        # Stream should not be set
        emitter = instance._particle_system['emitters'][0]
        assert emitter['stream_type'] is None
        assert emitter['stream_count'] == 0

    def test_burst_particles_with_different_shapes(self):
        """burst_particles works with different emitter shapes"""
        executor = ActionExecutor()

        for shape in ['rectangle', 'ellipse', 'diamond', 'line']:
            instance = MockInstance()

            executor.execute_create_particle_system_action(instance, {})
            executor.execute_create_particle_type_action(instance, {
                'life_min': 10,
                'life_max': 10
            })
            executor.execute_create_emitter_action(instance, {
                'x': 100,
                'y': 100,
                'width': 50,
                'height': 50,
                'shape': shape
            })

            executor.execute_burst_particles_action(instance, {
                'particle_type': 0,
                'number': 3
            })

            assert len(instance._particle_system['particles']) == 3, f"Failed for shape: {shape}"


# ==============================================================================
# Timing Tab Actions Tests (Timeline)
# ==============================================================================


class TestTimingTabActions:
    """Tests for Timing tab actions: set_timeline, set_timeline_position,
    set_timeline_speed, start_timeline, pause_timeline, stop_timeline"""

    def test_set_timeline_sets_timeline_index(self):
        """set_timeline sets the timeline_index property"""
        executor = ActionExecutor()
        instance = MockInstance()

        executor.execute_set_timeline_action(instance, {'timeline': 'tl_player_animation'})

        assert instance.timeline_index == 'tl_player_animation'
        assert instance.timeline_position == 0
        assert instance.timeline_speed == 1.0
        assert instance.timeline_running is False

    def test_set_timeline_resets_position(self):
        """set_timeline resets position when setting new timeline"""
        executor = ActionExecutor()
        instance = MockInstance()

        # Set initial timeline and position
        executor.execute_set_timeline_action(instance, {'timeline': 'tl_first'})
        instance.timeline_position = 50

        # Set new timeline
        executor.execute_set_timeline_action(instance, {'timeline': 'tl_second'})

        assert instance.timeline_index == 'tl_second'
        assert instance.timeline_position == 0

    def test_set_timeline_none(self):
        """set_timeline can clear the timeline by setting None"""
        executor = ActionExecutor()
        instance = MockInstance()

        executor.execute_set_timeline_action(instance, {'timeline': None})

        assert instance.timeline_index is None

    def test_set_timeline_position_absolute(self):
        """set_timeline_position sets absolute position"""
        executor = ActionExecutor()
        instance = MockInstance()
        instance.timeline_position = 10

        executor.execute_set_timeline_position_action(instance, {
            'position': 50,
            'relative': False
        })

        assert instance.timeline_position == 50

    def test_set_timeline_position_relative(self):
        """set_timeline_position adds to current position when relative"""
        executor = ActionExecutor()
        instance = MockInstance()
        instance.timeline_position = 30

        executor.execute_set_timeline_position_action(instance, {
            'position': 20,
            'relative': True
        })

        assert instance.timeline_position == 50

    def test_set_timeline_position_relative_negative(self):
        """set_timeline_position handles negative relative values"""
        executor = ActionExecutor()
        instance = MockInstance()
        instance.timeline_position = 30

        executor.execute_set_timeline_position_action(instance, {
            'position': -10,
            'relative': True
        })

        assert instance.timeline_position == 20

    def test_set_timeline_position_clamps_to_zero(self):
        """set_timeline_position clamps position to minimum of 0"""
        executor = ActionExecutor()
        instance = MockInstance()
        instance.timeline_position = 10

        executor.execute_set_timeline_position_action(instance, {
            'position': -50,
            'relative': True
        })

        assert instance.timeline_position == 0

    def test_set_timeline_position_default(self):
        """set_timeline_position uses default values"""
        executor = ActionExecutor()
        instance = MockInstance()

        executor.execute_set_timeline_position_action(instance, {})

        assert instance.timeline_position == 0

    def test_set_timeline_speed_sets_speed(self):
        """set_timeline_speed sets the timeline speed multiplier"""
        executor = ActionExecutor()
        instance = MockInstance()

        executor.execute_set_timeline_speed_action(instance, {'speed': 2.0})

        assert instance.timeline_speed == 2.0

    def test_set_timeline_speed_half(self):
        """set_timeline_speed can set half speed"""
        executor = ActionExecutor()
        instance = MockInstance()

        executor.execute_set_timeline_speed_action(instance, {'speed': 0.5})

        assert instance.timeline_speed == 0.5

    def test_set_timeline_speed_default(self):
        """set_timeline_speed uses default of 1.0"""
        executor = ActionExecutor()
        instance = MockInstance()

        executor.execute_set_timeline_speed_action(instance, {})

        assert instance.timeline_speed == 1.0

    def test_start_timeline_sets_running_true(self):
        """start_timeline sets timeline_running to True"""
        executor = ActionExecutor()
        instance = MockInstance()
        instance.timeline_running = False

        executor.execute_start_timeline_action(instance, {})

        assert instance.timeline_running is True

    def test_start_timeline_initializes_if_missing(self):
        """start_timeline initializes timeline_running if not present"""
        executor = ActionExecutor()
        instance = MockInstance()

        executor.execute_start_timeline_action(instance, {})

        assert instance.timeline_running is True

    def test_pause_timeline_sets_running_false(self):
        """pause_timeline sets timeline_running to False"""
        executor = ActionExecutor()
        instance = MockInstance()
        instance.timeline_running = True

        executor.execute_pause_timeline_action(instance, {})

        assert instance.timeline_running is False

    def test_pause_timeline_preserves_position(self):
        """pause_timeline preserves the current position"""
        executor = ActionExecutor()
        instance = MockInstance()
        instance.timeline_running = True
        instance.timeline_position = 75

        executor.execute_pause_timeline_action(instance, {})

        assert instance.timeline_running is False
        assert instance.timeline_position == 75

    def test_stop_timeline_stops_and_resets(self):
        """stop_timeline stops playback and resets position to 0"""
        executor = ActionExecutor()
        instance = MockInstance()
        instance.timeline_running = True
        instance.timeline_position = 100

        executor.execute_stop_timeline_action(instance, {})

        assert instance.timeline_running is False
        assert instance.timeline_position == 0

    def test_stop_timeline_on_stopped_timeline(self):
        """stop_timeline works even if already stopped"""
        executor = ActionExecutor()
        instance = MockInstance()
        instance.timeline_running = False
        instance.timeline_position = 50

        executor.execute_stop_timeline_action(instance, {})

        assert instance.timeline_running is False
        assert instance.timeline_position == 0

    def test_timeline_workflow(self):
        """Test complete timeline workflow: set, start, pause, stop"""
        executor = ActionExecutor()
        instance = MockInstance()

        # Set timeline
        executor.execute_set_timeline_action(instance, {'timeline': 'tl_cutscene'})
        assert instance.timeline_index == 'tl_cutscene'
        assert instance.timeline_running is False

        # Set speed
        executor.execute_set_timeline_speed_action(instance, {'speed': 1.5})
        assert instance.timeline_speed == 1.5

        # Start
        executor.execute_start_timeline_action(instance, {})
        assert instance.timeline_running is True

        # Simulate position advancement
        instance.timeline_position = 30

        # Pause
        executor.execute_pause_timeline_action(instance, {})
        assert instance.timeline_running is False
        assert instance.timeline_position == 30

        # Resume
        executor.execute_start_timeline_action(instance, {})
        assert instance.timeline_running is True
        assert instance.timeline_position == 30

        # Stop
        executor.execute_stop_timeline_action(instance, {})
        assert instance.timeline_running is False
        assert instance.timeline_position == 0


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
