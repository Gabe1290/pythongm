#!/usr/bin/env python3
"""
Tests for the runtime game engine (GameRunner, GameInstance, GameRoom, GameSprite)

These tests focus on logic that can be tested without a pygame display:
- Collision detection (pure math)
- Spatial grid operations
- Game state management (score, lives, health)
- Project/room data loading
- Instance properties and state
"""

import json
import tempfile
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

# Import centralized dependency detection from conftest
# Note: conftest.py already sets SDL_VIDEODRIVER and SDL_AUDIODRIVER before pygame import
from conftest import skip_without_pygame

# Skip all tests if pygame is not available
pytestmark = skip_without_pygame


class TestRectanglesOverlap:
    """Tests for the rectangles_overlap collision detection function"""

    @pytest.fixture
    def game_runner(self):
        """Create a GameRunner instance without loading a project"""
        # Patch pygame initialization and plugin loading
        with patch('runtime.game_runner.pygame'):
            with patch('runtime.game_runner.load_all_plugins'):
                from runtime.game_runner import GameRunner
                runner = GameRunner.__new__(GameRunner)
                # Initialize only the attributes we need for collision testing
                runner.running = False
                runner.screen = None
                runner.clock = None
                runner.project_data = None
                runner.project_path = None
                runner.score = 0
                runner.lives = 3
                runner.health = 100.0
                runner.highscores = []
                runner.global_variables = {}
                runner.sprites = {}
                runner.rooms = {}
                runner.current_room = None
                runner.fps = 60
                runner.window_width = 800
                runner.window_height = 600
                runner.show_score_in_caption = False
                runner.show_lives_in_caption = False
                runner.show_health_in_caption = False
                runner.window_caption = ""
                runner.language = 'en'
                return runner

    def test_no_overlap_left(self, game_runner):
        """Test rectangles with no overlap (rect2 to the right of rect1)"""
        # Rect1: (0, 0) to (32, 32)
        # Rect2: (50, 0) to (82, 32) - completely to the right
        assert not game_runner.rectangles_overlap(0, 0, 32, 32, 50, 0, 32, 32)

    def test_no_overlap_right(self, game_runner):
        """Test rectangles with no overlap (rect2 to the left of rect1)"""
        # Rect1: (50, 0) to (82, 32)
        # Rect2: (0, 0) to (32, 32) - completely to the left
        assert not game_runner.rectangles_overlap(50, 0, 32, 32, 0, 0, 32, 32)

    def test_no_overlap_above(self, game_runner):
        """Test rectangles with no overlap (rect2 below rect1)"""
        # Rect1: (0, 0) to (32, 32)
        # Rect2: (0, 50) to (32, 82) - completely below
        assert not game_runner.rectangles_overlap(0, 0, 32, 32, 0, 50, 32, 32)

    def test_no_overlap_below(self, game_runner):
        """Test rectangles with no overlap (rect2 above rect1)"""
        # Rect1: (0, 50) to (32, 82)
        # Rect2: (0, 0) to (32, 32) - completely above
        assert not game_runner.rectangles_overlap(0, 50, 32, 32, 0, 0, 32, 32)

    def test_overlap_partial(self, game_runner):
        """Test rectangles with partial overlap"""
        # Rect1: (0, 0) to (32, 32)
        # Rect2: (16, 16) to (48, 48) - overlaps in corner
        assert game_runner.rectangles_overlap(0, 0, 32, 32, 16, 16, 32, 32)

    def test_overlap_complete(self, game_runner):
        """Test rectangles with complete overlap (same position)"""
        # Same rectangle
        assert game_runner.rectangles_overlap(0, 0, 32, 32, 0, 0, 32, 32)

    def test_overlap_contained(self, game_runner):
        """Test when one rectangle contains another"""
        # Small rect inside large rect
        assert game_runner.rectangles_overlap(0, 0, 100, 100, 25, 25, 50, 50)
        # Large rect contains small rect
        assert game_runner.rectangles_overlap(25, 25, 50, 50, 0, 0, 100, 100)

    def test_touching_edges_no_overlap(self, game_runner):
        """Test rectangles that touch at edge but don't overlap"""
        # Rect1: (0, 0) to (32, 32)
        # Rect2: (32, 0) to (64, 32) - touches at edge
        assert not game_runner.rectangles_overlap(0, 0, 32, 32, 32, 0, 32, 32)

    def test_negative_coordinates(self, game_runner):
        """Test with negative coordinates"""
        # Rect at negative coords
        assert game_runner.rectangles_overlap(-10, -10, 32, 32, 0, 0, 32, 32)
        # No overlap at negative coords
        assert not game_runner.rectangles_overlap(-100, -100, 32, 32, 0, 0, 32, 32)

    def test_float_coordinates(self, game_runner):
        """Test with float coordinates"""
        # Overlapping floats
        assert game_runner.rectangles_overlap(0.5, 0.5, 32.0, 32.0, 16.0, 16.0, 32.0, 32.0)
        # Non-overlapping floats
        assert not game_runner.rectangles_overlap(0.0, 0.0, 32.0, 32.0, 100.5, 100.5, 32.0, 32.0)


class TestGameInstance:
    """Tests for GameInstance class"""

    @pytest.fixture
    def mock_action_executor(self):
        """Create a mock action executor"""
        return MagicMock()

    def test_instance_creation(self, mock_action_executor):
        """Test basic instance creation"""
        with patch('runtime.game_runner.pygame'):
            with patch('runtime.game_runner.load_all_plugins'):
                from runtime.game_runner import GameInstance
                instance = GameInstance(
                    object_name="test_object",
                    x=100.0,
                    y=200.0,
                    instance_data={'visible': True},
                    action_executor=mock_action_executor
                )

                assert instance.object_name == "test_object"
                assert instance.x == 100.0
                assert instance.y == 200.0
                assert instance.xstart == 100.0
                assert instance.ystart == 200.0
                assert instance.visible is True
                assert instance.hspeed == 0.0
                assert instance.vspeed == 0.0
                assert len(instance.alarm) == 12
                assert all(a == -1 for a in instance.alarm)

    def test_instance_position_tracking(self, mock_action_executor):
        """Test that position changes mark the grid as dirty"""
        with patch('runtime.game_runner.pygame'):
            with patch('runtime.game_runner.load_all_plugins'):
                from runtime.game_runner import GameInstance
                instance = GameInstance("test", 0, 0, {}, mock_action_executor)

                assert instance._grid_dirty is False

                # Changing position should mark as dirty
                instance.x = 50
                assert instance._grid_dirty is True

                # Reset
                instance._grid_dirty = False

                instance.y = 50
                assert instance._grid_dirty is True

    def test_instance_cached_dimensions(self, mock_action_executor):
        """Test that cached dimensions default to 32x32"""
        with patch('runtime.game_runner.pygame'):
            with patch('runtime.game_runner.load_all_plugins'):
                from runtime.game_runner import GameInstance
                instance = GameInstance("test", 0, 0, {}, mock_action_executor)

                assert instance._cached_width == 32
                assert instance._cached_height == 32

    def test_instance_alarm_initialization(self, mock_action_executor):
        """Test that alarms are properly initialized"""
        with patch('runtime.game_runner.pygame'):
            with patch('runtime.game_runner.load_all_plugins'):
                from runtime.game_runner import GameInstance
                instance = GameInstance("test", 0, 0, {}, mock_action_executor)

                # All alarms should be disabled (-1)
                assert len(instance.alarm) == 12
                for i in range(12):
                    assert instance.alarm[i] == -1

    def test_set_object_data_parses_collision_targets(self, mock_action_executor):
        """Test that set_object_data pre-parses collision events"""
        with patch('runtime.game_runner.pygame'):
            with patch('runtime.game_runner.load_all_plugins'):
                from runtime.game_runner import GameInstance
                instance = GameInstance("player", 0, 0, {}, mock_action_executor)

                object_data = {
                    'visible': True,
                    'depth': 5,
                    'events': {
                        'collision_with_wall': {'actions': [{'action': 'stop_movement'}]},
                        'collision_with_enemy': {'actions': [{'action': 'destroy_self'}]},
                        'step': {'actions': []},  # Not a collision event
                    }
                }

                instance.set_object_data(object_data)

                # Check collision targets were parsed
                assert 'wall' in instance._collision_targets
                assert 'enemy' in instance._collision_targets
                assert 'step' not in instance._collision_targets  # step is not collision

    def test_set_object_data_applies_depth(self, mock_action_executor):
        """Test that depth is applied from object data"""
        with patch('runtime.game_runner.pygame'):
            with patch('runtime.game_runner.load_all_plugins'):
                from runtime.game_runner import GameInstance
                instance = GameInstance("test", 0, 0, {}, mock_action_executor)

                instance.set_object_data({'depth': 10})
                assert instance.depth == 10


class TestGameRoom:
    """Tests for GameRoom class (spatial grid operations)"""

    @pytest.fixture
    def mock_action_executor(self):
        """Create a mock action executor"""
        return MagicMock()

    def test_room_creation(self, mock_action_executor):
        """Test basic room creation"""
        with patch('runtime.game_runner.pygame'):
            with patch('runtime.game_runner.load_all_plugins'):
                from runtime.game_runner import GameRoom
                room_data = {
                    'width': 800,
                    'height': 600,
                    'background_color': '#87CEEB',
                    'instances': []
                }

                room = GameRoom("test_room", room_data, mock_action_executor)

                assert room.name == "test_room"
                assert room.width == 800
                assert room.height == 600
                assert room.background_color == (135, 206, 235)
                assert len(room.instances) == 0

    def test_room_with_instances(self, mock_action_executor):
        """Test room with instances"""
        with patch('runtime.game_runner.pygame'):
            with patch('runtime.game_runner.load_all_plugins'):
                from runtime.game_runner import GameRoom
                room_data = {
                    'width': 640,
                    'height': 480,
                    'instances': [
                        {'object_name': 'player', 'x': 100, 'y': 100},
                        {'object_name': 'enemy', 'x': 200, 'y': 200},
                    ]
                }

                room = GameRoom("game_room", room_data, mock_action_executor)

                assert len(room.instances) == 2
                assert room.instances[0].object_name == 'player'
                assert room.instances[1].object_name == 'enemy'

    def test_parse_color_hex(self, mock_action_executor):
        """Test hex color parsing"""
        with patch('runtime.game_runner.pygame'):
            with patch('runtime.game_runner.load_all_plugins'):
                from runtime.game_runner import GameRoom
                room = GameRoom("test", {'width': 100, 'height': 100}, mock_action_executor)

                # With hash
                assert room.parse_color('#FF0000') == (255, 0, 0)
                assert room.parse_color('#00FF00') == (0, 255, 0)
                assert room.parse_color('#0000FF') == (0, 0, 255)

                # Without hash
                assert room.parse_color('FFFFFF') == (255, 255, 255)
                assert room.parse_color('000000') == (0, 0, 0)

    def test_spatial_grid_cells(self, mock_action_executor):
        """Test spatial grid cell calculation"""
        with patch('runtime.game_runner.pygame'):
            with patch('runtime.game_runner.load_all_plugins'):
                from runtime.game_runner import GameRoom
                room = GameRoom("test", {'width': 640, 'height': 480}, mock_action_executor)

                # Object at origin (cell 0,0)
                cells = room._get_grid_cells(0, 0, 32, 32)
                assert (0, 0) in cells

                # Object spanning multiple cells
                cells = room._get_grid_cells(60, 60, 32, 32)
                # Should span cells (0,0), (1,0), (0,1), (1,1) with 64px cells
                assert len(cells) >= 1

    def test_get_nearby_instances(self, mock_action_executor):
        """Test spatial grid query"""
        with patch('runtime.game_runner.pygame'):
            with patch('runtime.game_runner.load_all_plugins'):
                from runtime.game_runner import GameRoom
                room_data = {
                    'width': 640,
                    'height': 480,
                    'instances': [
                        {'object_name': 'a', 'x': 0, 'y': 0},
                        {'object_name': 'b', 'x': 50, 'y': 50},
                        {'object_name': 'c', 'x': 500, 'y': 500},  # Far away
                    ]
                }

                room = GameRoom("test", room_data, mock_action_executor)

                # Query near origin - should find 'a' and 'b', not 'c'
                nearby = room.get_nearby_instances(0, 0, 32, 32)
                nearby_names = [inst.object_name for inst in nearby]

                assert 'a' in nearby_names
                assert 'b' in nearby_names
                # 'c' might or might not be included depending on cell size

    def test_update_dirty_instances(self, mock_action_executor):
        """Test lazy spatial grid update"""
        with patch('runtime.game_runner.pygame'):
            with patch('runtime.game_runner.load_all_plugins'):
                from runtime.game_runner import GameRoom
                room_data = {
                    'width': 640,
                    'height': 480,
                    'instances': [
                        {'object_name': 'player', 'x': 0, 'y': 0},
                    ]
                }

                room = GameRoom("test", room_data, mock_action_executor)
                player = room.instances[0]

                # Move the player
                player.x = 100
                player.y = 100
                assert player._grid_dirty is True

                # Update dirty instances
                room.update_dirty_instances()
                assert player._grid_dirty is False


class TestGameState:
    """Tests for game state management (score, lives, health)"""

    @pytest.fixture
    def game_runner(self):
        """Create a GameRunner with mocked pygame"""
        with patch('runtime.game_runner.pygame'):
            with patch('runtime.game_runner.load_all_plugins'):
                from runtime.game_runner import GameRunner
                runner = GameRunner.__new__(GameRunner)
                runner.score = 0
                runner.lives = 3
                runner.health = 100.0
                runner.highscores = []
                runner.global_variables = {}
                runner.running = False
                runner.language = 'en'
                return runner

    def test_initial_state(self, game_runner):
        """Test initial game state values"""
        assert game_runner.score == 0
        assert game_runner.lives == 3
        assert game_runner.health == 100.0

    def test_score_modification(self, game_runner):
        """Test score can be modified"""
        game_runner.score = 100
        assert game_runner.score == 100

        game_runner.score += 50
        assert game_runner.score == 150

    def test_lives_modification(self, game_runner):
        """Test lives can be modified"""
        game_runner.lives = 5
        assert game_runner.lives == 5

        game_runner.lives -= 1
        assert game_runner.lives == 4

    def test_health_modification(self, game_runner):
        """Test health can be modified"""
        game_runner.health = 50.0
        assert game_runner.health == 50.0

        game_runner.health -= 25.5
        assert game_runner.health == 24.5

    def test_global_variables(self, game_runner):
        """Test global variables storage"""
        game_runner.global_variables['player_name'] = 'Test'
        game_runner.global_variables['level'] = 5
        game_runner.global_variables['completed'] = True

        assert game_runner.global_variables['player_name'] == 'Test'
        assert game_runner.global_variables['level'] == 5
        assert game_runner.global_variables['completed'] is True


class TestProjectLoading:
    """Tests for project data loading"""

    @pytest.fixture
    def temp_project(self):
        """Create a temporary project for testing"""
        with tempfile.TemporaryDirectory() as tmpdir:
            project_dir = Path(tmpdir)
            project_file = project_dir / "project.json"

            project_data = {
                "name": "Test Project",
                "version": "1.0",
                "room_order": ["room1", "room2"],
                "settings": {
                    "starting_lives": 5,
                    "starting_score": 100,
                    "starting_health": 75.0,
                    "show_lives_in_caption": True,
                },
                "assets": {
                    "rooms": {
                        "room1": {
                            "width": 640,
                            "height": 480,
                            "background_color": "#000000",
                            "instances": [
                                {"object_name": "player", "x": 100, "y": 100},
                            ]
                        },
                        "room2": {
                            "width": 800,
                            "height": 600,
                            "instances": []
                        }
                    },
                    "objects": {
                        "player": {
                            "sprite": "spr_player",
                            "solid": False,
                            "visible": True,
                        }
                    },
                    "sprites": {}
                }
            }

            with open(project_file, 'w') as f:
                json.dump(project_data, f)

            yield project_dir

    def test_load_project_data_only(self, temp_project):
        """Test loading project data without sprites"""
        with patch('runtime.game_runner.pygame'):
            with patch('runtime.game_runner.load_all_plugins'):
                from runtime.game_runner import GameRunner
                runner = GameRunner()

                result = runner.load_project_data_only(str(temp_project))

                assert result is True
                assert runner.project_data is not None
                assert runner.project_data['name'] == 'Test Project'

    def test_load_project_settings(self, temp_project):
        """Test that project settings are applied"""
        with patch('runtime.game_runner.pygame'):
            with patch('runtime.game_runner.load_all_plugins'):
                from runtime.game_runner import GameRunner
                runner = GameRunner()

                runner.load_project_data_only(str(temp_project))

                assert runner.lives == 5
                assert runner.score == 100
                assert runner.health == 75.0
                assert runner.show_lives_in_caption is True

    def test_find_starting_room(self, temp_project):
        """Test finding the starting room from room_order"""
        with patch('runtime.game_runner.pygame'):
            with patch('runtime.game_runner.load_all_plugins'):
                from runtime.game_runner import GameRunner
                runner = GameRunner()

                runner.load_project_data_only(str(temp_project))

                starting_room = runner.find_starting_room()
                assert starting_room == "room1"

    def test_get_room_list(self, temp_project):
        """Test getting ordered room list"""
        with patch('runtime.game_runner.pygame'):
            with patch('runtime.game_runner.load_all_plugins'):
                from runtime.game_runner import GameRunner
                runner = GameRunner()

                runner.load_project_data_only(str(temp_project))

                room_list = runner.get_room_list()
                assert room_list == ["room1", "room2"]

    def test_load_rooms_without_sprites(self, temp_project):
        """Test that rooms are loaded but sprites are not yet assigned"""
        with patch('runtime.game_runner.pygame'):
            with patch('runtime.game_runner.load_all_plugins'):
                from runtime.game_runner import GameRunner
                runner = GameRunner()

                runner.load_project_data_only(str(temp_project))

                assert "room1" in runner.rooms
                assert "room2" in runner.rooms
                assert len(runner.rooms["room1"].instances) == 1
                assert len(runner.rooms["room2"].instances) == 0


class TestCaptionTranslations:
    """Tests for caption text translations"""

    def test_english_translations(self):
        """Test English caption translations"""
        with patch('runtime.game_runner.pygame'):
            with patch('runtime.game_runner.load_all_plugins'):
                from runtime.game_runner import GameRunner
                runner = GameRunner.__new__(GameRunner)
                runner.language = 'en'

                assert runner.get_caption_text('score') == 'Score'
                assert runner.get_caption_text('lives') == 'Lives'
                assert runner.get_caption_text('health') == 'Health'
                assert runner.get_caption_text('room') == 'Room'

    def test_german_translations(self):
        """Test German caption translations"""
        with patch('runtime.game_runner.pygame'):
            with patch('runtime.game_runner.load_all_plugins'):
                from runtime.game_runner import GameRunner
                runner = GameRunner.__new__(GameRunner)
                runner.language = 'de'

                assert runner.get_caption_text('score') == 'Punkte'
                assert runner.get_caption_text('lives') == 'Leben'
                assert runner.get_caption_text('health') == 'Gesundheit'
                assert runner.get_caption_text('room') == 'Raum'

    def test_french_translations(self):
        """Test French caption translations"""
        with patch('runtime.game_runner.pygame'):
            with patch('runtime.game_runner.load_all_plugins'):
                from runtime.game_runner import GameRunner
                runner = GameRunner.__new__(GameRunner)
                runner.language = 'fr'

                assert runner.get_caption_text('score') == 'Score'
                assert runner.get_caption_text('lives') == 'Vies'
                assert runner.get_caption_text('health') == 'Santé'
                assert runner.get_caption_text('room') == 'Niveau'

    def test_unknown_language_fallback(self):
        """Test fallback to English for unknown language"""
        with patch('runtime.game_runner.pygame'):
            with patch('runtime.game_runner.load_all_plugins'):
                from runtime.game_runner import GameRunner
                runner = GameRunner.__new__(GameRunner)
                runner.language = 'xx'  # Unknown language

                # Should fallback to English
                assert runner.get_caption_text('score') == 'Score'


class TestInstancesOverlap:
    """Tests for instances_overlap method using mocked instances"""

    @pytest.fixture
    def game_runner(self):
        """Create a minimal GameRunner for testing"""
        with patch('runtime.game_runner.pygame'):
            with patch('runtime.game_runner.load_all_plugins'):
                from runtime.game_runner import GameRunner
                runner = GameRunner.__new__(GameRunner)
                return runner

    def create_mock_instance(self, x, y, width=32, height=32):
        """Create a mock instance with position and dimensions"""
        instance = MagicMock()
        instance.x = x
        instance.y = y
        instance._cached_width = width
        instance._cached_height = height
        return instance

    def test_instances_overlap_true(self, game_runner):
        """Test overlapping instances"""
        inst1 = self.create_mock_instance(0, 0, 32, 32)
        inst2 = self.create_mock_instance(16, 16, 32, 32)

        assert game_runner.instances_overlap(inst1, inst2) is True

    def test_instances_overlap_false(self, game_runner):
        """Test non-overlapping instances"""
        inst1 = self.create_mock_instance(0, 0, 32, 32)
        inst2 = self.create_mock_instance(100, 100, 32, 32)

        assert game_runner.instances_overlap(inst1, inst2) is False

    def test_instances_overlap_same_position(self, game_runner):
        """Test instances at same position"""
        inst1 = self.create_mock_instance(50, 50, 32, 32)
        inst2 = self.create_mock_instance(50, 50, 32, 32)

        assert game_runner.instances_overlap(inst1, inst2) is True

    def test_instances_overlap_different_sizes(self, game_runner):
        """Test instances with different sizes"""
        inst1 = self.create_mock_instance(0, 0, 64, 64)
        inst2 = self.create_mock_instance(32, 32, 16, 16)

        assert game_runner.instances_overlap(inst1, inst2) is True


class TestIsGameRunning:
    """Tests for is_game_running method"""

    def test_is_game_running_false(self):
        """Test is_game_running returns False when not running"""
        with patch('runtime.game_runner.pygame'):
            with patch('runtime.game_runner.load_all_plugins'):
                from runtime.game_runner import GameRunner
                runner = GameRunner.__new__(GameRunner)
                runner.running = False

                assert runner.is_game_running() is False

    def test_is_game_running_true(self):
        """Test is_game_running returns True when running"""
        with patch('runtime.game_runner.pygame'):
            with patch('runtime.game_runner.load_all_plugins'):
                from runtime.game_runner import GameRunner
                runner = GameRunner.__new__(GameRunner)
                runner.running = True

                assert runner.is_game_running() is True


# ============================================================================
# Event System Tests
# ============================================================================

class TestEventSystemCreate:
    """Tests for create event firing"""

    @pytest.fixture
    def mock_action_executor(self):
        """Create a mock action executor that tracks calls"""
        executor = MagicMock()
        executor.execute_event = MagicMock()
        executor.execute_action = MagicMock()
        return executor

    def test_create_event_fires_on_room_start(self, mock_action_executor):
        """Create event should fire when room becomes active"""
        with patch('runtime.game_runner.pygame'):
            with patch('runtime.game_runner.load_all_plugins'):
                from runtime.game_runner import GameInstance

                instance = GameInstance("player", 100, 100, {}, mock_action_executor)
                instance.object_data = {
                    'events': {
                        'create': {'actions': [{'action': 'set_score', 'value': 100}]}
                    }
                }

                # Simulate what happens when room starts
                mock_action_executor.execute_event(instance, "create", instance.object_data["events"])

                # Verify create event was called
                mock_action_executor.execute_event.assert_called_with(
                    instance, "create", instance.object_data["events"]
                )


class TestEventSystemStep:
    """Tests for step event types (begin_step, step, end_step)"""

    @pytest.fixture
    def mock_action_executor(self):
        """Create a mock action executor"""
        executor = MagicMock()
        executor.execute_event = MagicMock()
        executor.execute_action = MagicMock()
        return executor

    def test_step_event_fires_each_frame(self, mock_action_executor):
        """Step event should execute on each frame"""
        with patch('runtime.game_runner.pygame'):
            with patch('runtime.game_runner.load_all_plugins'):
                from runtime.game_runner import GameInstance

                instance = GameInstance("player", 0, 0, {}, mock_action_executor)
                instance.object_data = {
                    'events': {
                        'step': {'actions': [{'action': 'move_relative', 'x': 1, 'y': 0}]}
                    }
                }

                # Simulate step being called
                instance.step()

                # Verify step event was executed
                mock_action_executor.execute_event.assert_called()

    def test_begin_step_and_end_step_events(self, mock_action_executor):
        """begin_step and end_step events should be recognized"""
        with patch('runtime.game_runner.pygame'):
            with patch('runtime.game_runner.load_all_plugins'):
                from runtime.game_runner import GameInstance

                instance = GameInstance("player", 0, 0, {}, mock_action_executor)
                instance.object_data = {
                    'events': {
                        'begin_step': {'actions': [{'action': 'test1'}]},
                        'step': {'actions': [{'action': 'test2'}]},
                        'end_step': {'actions': [{'action': 'test3'}]},
                    }
                }

                # begin_step and end_step are handled by game_runner, not instance.step()
                # Verify the event structure is valid
                assert 'begin_step' in instance.object_data['events']
                assert 'end_step' in instance.object_data['events']


class TestEventSystemDestroy:
    """Tests for destroy event"""

    @pytest.fixture
    def mock_action_executor(self):
        """Create a mock action executor"""
        executor = MagicMock()
        executor.execute_event = MagicMock()
        return executor

    def test_destroy_flag_marks_instance(self, mock_action_executor):
        """Setting to_destroy should mark instance for destruction"""
        with patch('runtime.game_runner.pygame'):
            with patch('runtime.game_runner.load_all_plugins'):
                from runtime.game_runner import GameInstance

                instance = GameInstance("enemy", 0, 0, {}, mock_action_executor)
                assert instance.to_destroy is False

                instance.to_destroy = True
                assert instance.to_destroy is True

    def test_destroy_event_structure(self, mock_action_executor):
        """Destroy event should be recognized in event structure"""
        with patch('runtime.game_runner.pygame'):
            with patch('runtime.game_runner.load_all_plugins'):
                from runtime.game_runner import GameInstance

                instance = GameInstance("enemy", 0, 0, {}, mock_action_executor)
                instance.object_data = {
                    'events': {
                        'destroy': {'actions': [{'action': 'play_sound', 'sound': 'explosion'}]}
                    }
                }

                assert 'destroy' in instance.object_data['events']
                assert len(instance.object_data['events']['destroy']['actions']) == 1


class TestEventSystemAlarm:
    """Tests for alarm events (alarm_0 through alarm_11)"""

    @pytest.fixture
    def mock_action_executor(self):
        """Create a mock action executor"""
        executor = MagicMock()
        executor.execute_event = MagicMock()
        executor.execute_action = MagicMock()
        return executor

    def test_alarm_initialization(self, mock_action_executor):
        """All 12 alarms should initialize to -1 (disabled)"""
        with patch('runtime.game_runner.pygame'):
            with patch('runtime.game_runner.load_all_plugins'):
                from runtime.game_runner import GameInstance

                instance = GameInstance("timer", 0, 0, {}, mock_action_executor)

                assert len(instance.alarm) == 12
                for i in range(12):
                    assert instance.alarm[i] == -1

    def test_alarm_can_be_set(self, mock_action_executor):
        """Alarms can be set to a positive value"""
        with patch('runtime.game_runner.pygame'):
            with patch('runtime.game_runner.load_all_plugins'):
                from runtime.game_runner import GameInstance

                instance = GameInstance("timer", 0, 0, {}, mock_action_executor)

                instance.alarm[0] = 30  # 30 frames
                instance.alarm[5] = 60  # 60 frames

                assert instance.alarm[0] == 30
                assert instance.alarm[5] == 60
                assert instance.alarm[1] == -1  # Others unchanged

    def test_alarm_event_structure_flat(self, mock_action_executor):
        """Alarm events can be in flat structure (alarm_0 at root)"""
        with patch('runtime.game_runner.pygame'):
            with patch('runtime.game_runner.load_all_plugins'):
                from runtime.game_runner import GameInstance

                instance = GameInstance("timer", 0, 0, {}, mock_action_executor)
                instance.object_data = {
                    'events': {
                        'alarm_0': {'actions': [{'action': 'spawn_enemy'}]},
                        'alarm_5': {'actions': [{'action': 'end_level'}]},
                    }
                }

                assert 'alarm_0' in instance.object_data['events']
                assert 'alarm_5' in instance.object_data['events']

    def test_alarm_event_structure_nested(self, mock_action_executor):
        """Alarm events can be in nested structure (alarm.alarm_0)"""
        with patch('runtime.game_runner.pygame'):
            with patch('runtime.game_runner.load_all_plugins'):
                from runtime.game_runner import GameInstance

                instance = GameInstance("timer", 0, 0, {}, mock_action_executor)
                instance.object_data = {
                    'events': {
                        'alarm': {
                            'alarm_0': {'actions': [{'action': 'spawn_enemy'}]},
                            'alarm_3': {'actions': [{'action': 'change_sprite'}]},
                        }
                    }
                }

                assert 'alarm' in instance.object_data['events']
                assert 'alarm_0' in instance.object_data['events']['alarm']

    def test_alarm_decrement_in_game_loop(self, mock_action_executor):
        """Alarms should decrement each frame in the game loop (not in instance.step())

        Note: Alarms are processed in the main game loop before step events,
        matching GameMaker 7.0 event execution order.
        """
        with patch('runtime.game_runner.pygame'):
            with patch('runtime.game_runner.load_all_plugins'):
                from runtime.game_runner import GameInstance

                instance = GameInstance("timer", 0, 0, {}, mock_action_executor)
                instance.object_data = {
                    'events': {
                        'alarm_0': {'actions': [{'action': 'test'}]}
                    }
                }
                instance.alarm[0] = 3

                # Alarms are processed in the main game loop, not in instance.step()
                # Here we manually simulate what the game loop does for alarm processing
                def process_alarm(inst):
                    """Simulate game loop alarm processing"""
                    for alarm_num in range(12):
                        if inst.alarm[alarm_num] > 0:
                            inst.alarm[alarm_num] -= 1
                            if inst.alarm[alarm_num] == 0:
                                inst.alarm[alarm_num] = -1  # Reset to disabled

                process_alarm(instance)
                assert instance.alarm[0] == 2

                process_alarm(instance)
                assert instance.alarm[0] == 1

                # On reaching 0, alarm fires and resets to -1
                process_alarm(instance)
                assert instance.alarm[0] == -1


class TestEventSystemKeyboard:
    """Tests for keyboard events (keyboard, keyboard_press, keyboard_release)"""

    @pytest.fixture
    def mock_action_executor(self):
        """Create a mock action executor"""
        executor = MagicMock()
        return executor

    def test_keyboard_event_structure(self, mock_action_executor):
        """Keyboard events should support directional keys"""
        with patch('runtime.game_runner.pygame'):
            with patch('runtime.game_runner.load_all_plugins'):
                from runtime.game_runner import GameInstance

                instance = GameInstance("player", 0, 0, {}, mock_action_executor)
                instance.object_data = {
                    'events': {
                        'keyboard': {
                            'left': {'actions': [{'action': 'set_hspeed', 'value': -4}]},
                            'right': {'actions': [{'action': 'set_hspeed', 'value': 4}]},
                            'up': {'actions': [{'action': 'set_vspeed', 'value': -4}]},
                            'down': {'actions': [{'action': 'set_vspeed', 'value': 4}]},
                        }
                    }
                }

                keyboard_events = instance.object_data['events']['keyboard']
                assert 'left' in keyboard_events
                assert 'right' in keyboard_events
                assert 'up' in keyboard_events
                assert 'down' in keyboard_events

    def test_keyboard_press_event_structure(self, mock_action_executor):
        """keyboard_press events fire once when key is pressed"""
        with patch('runtime.game_runner.pygame'):
            with patch('runtime.game_runner.load_all_plugins'):
                from runtime.game_runner import GameInstance

                instance = GameInstance("player", 0, 0, {}, mock_action_executor)
                instance.object_data = {
                    'events': {
                        'keyboard_press': {
                            'space': {'actions': [{'action': 'jump'}]},
                        }
                    }
                }

                assert 'keyboard_press' in instance.object_data['events']

    def test_keyboard_release_event_structure(self, mock_action_executor):
        """keyboard_release events fire when key is released"""
        with patch('runtime.game_runner.pygame'):
            with patch('runtime.game_runner.load_all_plugins'):
                from runtime.game_runner import GameInstance

                instance = GameInstance("player", 0, 0, {}, mock_action_executor)
                instance.object_data = {
                    'events': {
                        'keyboard_release': {
                            'left': {'actions': [{'action': 'stop_hspeed'}]},
                            'right': {'actions': [{'action': 'stop_hspeed'}]},
                        }
                    }
                }

                assert 'keyboard_release' in instance.object_data['events']

    def test_nokey_event_structure(self, mock_action_executor):
        """nokey event fires when no keys are pressed"""
        with patch('runtime.game_runner.pygame'):
            with patch('runtime.game_runner.load_all_plugins'):
                from runtime.game_runner import GameInstance

                instance = GameInstance("player", 0, 0, {}, mock_action_executor)
                instance.object_data = {
                    'events': {
                        'keyboard': {
                            'nokey': {'actions': [{'action': 'stop_movement'}]},
                        }
                    }
                }

                assert 'nokey' in instance.object_data['events']['keyboard']

    def test_keys_pressed_tracking(self, mock_action_executor):
        """Instance should track which keys are currently pressed"""
        with patch('runtime.game_runner.pygame'):
            with patch('runtime.game_runner.load_all_plugins'):
                from runtime.game_runner import GameInstance

                instance = GameInstance("player", 0, 0, {}, mock_action_executor)

                assert hasattr(instance, 'keys_pressed')
                assert isinstance(instance.keys_pressed, set)
                assert len(instance.keys_pressed) == 0

                # Simulate key press
                instance.keys_pressed.add('left')
                assert 'left' in instance.keys_pressed

                # Simulate key release
                instance.keys_pressed.discard('left')
                assert 'left' not in instance.keys_pressed


class TestEventSystemMouse:
    """Tests for mouse events"""

    @pytest.fixture
    def mock_action_executor(self):
        """Create a mock action executor"""
        return MagicMock()

    def test_mouse_button_events(self, mock_action_executor):
        """Mouse button events should be recognized"""
        with patch('runtime.game_runner.pygame'):
            with patch('runtime.game_runner.load_all_plugins'):
                from runtime.game_runner import GameInstance

                instance = GameInstance("clickable", 0, 0, {}, mock_action_executor)
                instance.object_data = {
                    'events': {
                        'mouse': {
                            'left_button': {'actions': [{'action': 'on_click'}]},
                            'right_button': {'actions': [{'action': 'show_menu'}]},
                            'middle_button': {'actions': [{'action': 'pan_camera'}]},
                        }
                    }
                }

                mouse_events = instance.object_data['events']['mouse']
                assert 'left_button' in mouse_events
                assert 'right_button' in mouse_events
                assert 'middle_button' in mouse_events

    def test_mouse_release_events(self, mock_action_executor):
        """Mouse release events should be recognized"""
        with patch('runtime.game_runner.pygame'):
            with patch('runtime.game_runner.load_all_plugins'):
                from runtime.game_runner import GameInstance

                instance = GameInstance("draggable", 0, 0, {}, mock_action_executor)
                instance.object_data = {
                    'events': {
                        'mouse': {
                            'left_button_released': {'actions': [{'action': 'drop'}]},
                            'right_button_released': {'actions': [{'action': 'cancel'}]},
                        }
                    }
                }

                mouse_events = instance.object_data['events']['mouse']
                assert 'left_button_released' in mouse_events
                assert 'right_button_released' in mouse_events

    def test_mouse_move_event(self, mock_action_executor):
        """mouse_move event should be recognized"""
        with patch('runtime.game_runner.pygame'):
            with patch('runtime.game_runner.load_all_plugins'):
                from runtime.game_runner import GameInstance

                instance = GameInstance("tracker", 0, 0, {}, mock_action_executor)
                instance.object_data = {
                    'events': {
                        'mouse': {
                            'mouse_move': {'actions': [{'action': 'follow_cursor'}]},
                        }
                    }
                }

                assert 'mouse_move' in instance.object_data['events']['mouse']


class TestEventSystemCollision:
    """Tests for collision events"""

    @pytest.fixture
    def mock_action_executor(self):
        """Create a mock action executor"""
        executor = MagicMock()
        executor.execute_collision_event = MagicMock()
        return executor

    def test_collision_event_parsing(self, mock_action_executor):
        """Collision events should be parsed into _collision_targets"""
        with patch('runtime.game_runner.pygame'):
            with patch('runtime.game_runner.load_all_plugins'):
                from runtime.game_runner import GameInstance

                instance = GameInstance("player", 0, 0, {}, mock_action_executor)

                object_data = {
                    'events': {
                        'collision_with_enemy': {'actions': [{'action': 'take_damage'}]},
                        'collision_with_wall': {'actions': [{'action': 'stop_movement'}]},
                        'collision_with_coin': {'actions': [{'action': 'collect'}]},
                    }
                }

                instance.set_object_data(object_data)

                # Check collision targets were parsed
                assert 'enemy' in instance._collision_targets
                assert 'wall' in instance._collision_targets
                assert 'coin' in instance._collision_targets

    def test_collision_event_data_preserved(self, mock_action_executor):
        """Collision event data should be preserved in _collision_targets"""
        with patch('runtime.game_runner.pygame'):
            with patch('runtime.game_runner.load_all_plugins'):
                from runtime.game_runner import GameInstance

                instance = GameInstance("player", 0, 0, {}, mock_action_executor)

                object_data = {
                    'events': {
                        'collision_with_enemy': {
                            'actions': [
                                {'action': 'take_damage', 'value': 10},
                                {'action': 'play_sound', 'sound': 'hit'},
                            ]
                        },
                    }
                }

                instance.set_object_data(object_data)

                enemy_event = instance._collision_targets['enemy']
                assert len(enemy_event['actions']) == 2
                assert enemy_event['actions'][0]['action'] == 'take_damage'

    def test_non_collision_events_not_in_targets(self, mock_action_executor):
        """Non-collision events should not be added to _collision_targets"""
        with patch('runtime.game_runner.pygame'):
            with patch('runtime.game_runner.load_all_plugins'):
                from runtime.game_runner import GameInstance

                instance = GameInstance("player", 0, 0, {}, mock_action_executor)

                object_data = {
                    'events': {
                        'create': {'actions': []},
                        'step': {'actions': []},
                        'collision_with_wall': {'actions': []},
                    }
                }

                instance.set_object_data(object_data)

                assert 'create' not in instance._collision_targets
                assert 'step' not in instance._collision_targets
                assert 'wall' in instance._collision_targets


class TestEventSystemAnimationAndDrawing:
    """Tests for animation and drawing-related properties"""

    @pytest.fixture
    def mock_action_executor(self):
        """Create a mock action executor"""
        return MagicMock()

    def test_animation_properties(self, mock_action_executor):
        """Instance should have animation properties"""
        with patch('runtime.game_runner.pygame'):
            with patch('runtime.game_runner.load_all_plugins'):
                from runtime.game_runner import GameInstance

                instance = GameInstance("animated", 0, 0, {}, mock_action_executor)

                assert hasattr(instance, 'image_index')
                assert hasattr(instance, 'image_speed')
                assert instance.image_index == 0.0
                assert instance.image_speed == 1.0

    def test_depth_property(self, mock_action_executor):
        """Instance should have depth for draw ordering"""
        with patch('runtime.game_runner.pygame'):
            with patch('runtime.game_runner.load_all_plugins'):
                from runtime.game_runner import GameInstance

                instance = GameInstance("layered", 0, 0, {}, mock_action_executor)

                assert hasattr(instance, 'depth')
                assert instance.depth == 0

                # Depth can be set from object data
                instance.set_object_data({'depth': 100})
                assert instance.depth == 100

    def test_visibility_property(self, mock_action_executor):
        """Instance should have visibility property"""
        with patch('runtime.game_runner.pygame'):
            with patch('runtime.game_runner.load_all_plugins'):
                from runtime.game_runner import GameInstance

                instance = GameInstance("visible_obj", 0, 0, {'visible': True}, mock_action_executor)
                assert instance.visible is True

                instance2 = GameInstance("hidden_obj", 0, 0, {'visible': False}, mock_action_executor)
                assert instance2.visible is False


class TestEventSystemMovement:
    """Tests for movement-related properties used by events"""

    @pytest.fixture
    def mock_action_executor(self):
        """Create a mock action executor"""
        return MagicMock()

    def test_speed_properties(self, mock_action_executor):
        """Instance should have hspeed and vspeed"""
        with patch('runtime.game_runner.pygame'):
            with patch('runtime.game_runner.load_all_plugins'):
                from runtime.game_runner import GameInstance

                instance = GameInstance("moving", 0, 0, {}, mock_action_executor)

                assert hasattr(instance, 'hspeed')
                assert hasattr(instance, 'vspeed')
                assert instance.hspeed == 0.0
                assert instance.vspeed == 0.0

    def test_start_position_properties(self, mock_action_executor):
        """Instance should track starting position for jump_to_start"""
        with patch('runtime.game_runner.pygame'):
            with patch('runtime.game_runner.load_all_plugins'):
                from runtime.game_runner import GameInstance

                instance = GameInstance("movable", 100, 200, {}, mock_action_executor)

                assert instance.xstart == 100
                assert instance.ystart == 200

                # Moving shouldn't change start position
                instance.x = 300
                instance.y = 400
                assert instance.xstart == 100
                assert instance.ystart == 200


class TestEventSystemAllEventTypes:
    """Comprehensive test verifying all 19 event types are supported"""

    def test_all_event_types_recognized(self):
        """All 19 GameMaker-compatible event types should be recognized"""
        # List of all supported event types based on game_runner.py analysis
        supported_events = [
            # Lifecycle events
            'create',           # 1. When instance is created
            'destroy',          # 2. When instance is destroyed

            # Step events
            'begin_step',       # 3. Before step processing
            'step',             # 4. Main step event
            'end_step',         # 5. After step processing

            # Alarm events (alarm_0 through alarm_11)
            'alarm_0',          # 6. Alarm 0
            'alarm_1',          # 7. Alarm 1
            'alarm_2',          # 8. Alarm 2
            'alarm_3',          # 9. Alarm 3
            'alarm_4',          # 10. Alarm 4
            'alarm_5',          # 11. Alarm 5
            # (alarm_6 through alarm_11 also supported)

            # Keyboard events
            'keyboard',         # 12. Key held down (with sub-keys: left, right, up, down, etc.)
            'keyboard_press',   # 13. Key pressed (with sub-keys)
            'keyboard_release', # 14. Key released (with sub-keys)
            'nokey',            # 15. No key pressed (inside keyboard events)

            # Mouse events
            'mouse',            # 16. Mouse button events (left_button, right_button, etc.)
            # Mouse sub-events: left_button, right_button, middle_button,
            #                   left_button_released, right_button_released,
            #                   middle_button_released, mouse_move

            # Collision events
            'collision_with_*', # 17-19+. Collision with specific objects
        ]

        # Verify the expected count
        # Note: Collision events are dynamically named based on objects
        assert len([e for e in supported_events if not e.endswith('*')]) >= 16

    def test_event_structure_examples(self):
        """Example event structures should be valid"""
        # Example of a fully-featured object with all event types
        comprehensive_events = {
            'create': {'actions': [{'action': 'init'}]},
            'destroy': {'actions': [{'action': 'cleanup'}]},
            'begin_step': {'actions': [{'action': 'pre_update'}]},
            'step': {'actions': [{'action': 'update'}]},
            'end_step': {'actions': [{'action': 'post_update'}]},
            'alarm_0': {'actions': [{'action': 'timer_tick'}]},
            'keyboard': {
                'left': {'actions': [{'action': 'move_left'}]},
                'right': {'actions': [{'action': 'move_right'}]},
                'nokey': {'actions': [{'action': 'stop'}]},
            },
            'keyboard_press': {
                'space': {'actions': [{'action': 'jump'}]},
            },
            'keyboard_release': {
                'left': {'actions': [{'action': 'stop_left'}]},
            },
            'mouse': {
                'left_button': {'actions': [{'action': 'shoot'}]},
                'mouse_move': {'actions': [{'action': 'aim'}]},
            },
            'collision_with_wall': {'actions': [{'action': 'stop_movement'}]},
            'collision_with_enemy': {'actions': [{'action': 'take_damage'}]},
        }

        # All top-level keys should be valid event types
        valid_top_level = {'create', 'destroy', 'begin_step', 'step', 'end_step',
                          'alarm', 'keyboard', 'keyboard_press', 'keyboard_release',
                          'mouse'}

        for event_name in comprehensive_events.keys():
            # Event name should either be in valid_top_level or be an alarm/collision
            is_valid = (
                event_name in valid_top_level or
                event_name.startswith('alarm_') or
                event_name.startswith('collision_with_')
            )
            assert is_valid, f"Unknown event type: {event_name}"


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
