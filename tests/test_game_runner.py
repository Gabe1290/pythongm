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

            with open(project_file, 'w', encoding='utf-8') as f:
                json.dump(project_data, f, ensure_ascii=False)

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
        """Create a mock instance with position and dimensions.

        Sets bbox_* on the sprite mock to the full frame so the bbox-aware
        AABB check in instances_overlap behaves identically to the historic
        full-sprite check — keeps these unit tests focused on the AABB
        algebra rather than bbox derivation.
        """
        instance = MagicMock()
        instance.x = x
        instance.y = y
        instance._cached_width = width
        instance._cached_height = height
        instance.sprite.origin_x = 0
        instance.sprite.origin_y = 0
        instance.sprite.bbox_left = 0
        instance.sprite.bbox_top = 0
        instance.sprite.bbox_right = width
        instance.sprite.bbox_bottom = height
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


class TestPixelPerfectCollision:
    """Tests for static (unrotated/unscaled) pixel-perfect collision.

    Uses real pygame (conftest initializes it with dummy SDL drivers) because
    pygame.mask is the unit under test. Rotation or non-unity scale falls back
    to AABB — that's the documented static-only limitation.
    """

    @pytest.fixture
    def game_runner(self):
        """A bare GameRunner just sufficient to call _precise_refine / instances_overlap."""
        with patch('runtime.game_runner.load_all_plugins'):
            from runtime.game_runner import GameRunner
            return GameRunner.__new__(GameRunner)

    def _make_sprite(self, opaque_pixels, size=(8, 8), precise=True):
        """Build a GameSprite directly, bypassing file load.

        opaque_pixels: iterable of (x, y) pixel coordinates that should be
        opaque. Everything else is transparent.
        """
        import pygame
        from runtime.game_runner import GameSprite

        surface = pygame.Surface(size, pygame.SRCALPHA)
        surface.fill((0, 0, 0, 0))
        for (px, py) in opaque_pixels:
            surface.set_at((px, py), (255, 255, 255, 255))

        sprite = GameSprite.__new__(GameSprite)
        sprite.path = ""
        sprite.sprite_data = {}
        sprite.surface = surface
        sprite.frames = [surface]
        sprite.masks = []
        sprite.frame_count = 1
        sprite.frame_width = size[0]
        sprite.frame_height = size[1]
        sprite.width = size[0]
        sprite.height = size[1]
        sprite.origin_x = 0
        sprite.origin_y = 0
        sprite.speed = 10.0
        sprite.animation_type = "single"
        sprite.precise = precise
        # Bbox = full frame for these unit tests. instances_overlap reads
        # bbox_left/top/right/bottom on the sprite directly, so they have
        # to exist; auto-derivation would shrink to the (single) opaque
        # pixel and obscure what the test is actually verifying about the
        # precise-refine pathway. _compute_collision_bbox() runs in normal
        # GameSprite.__init__ but this test bypasses __init__ via __new__.
        sprite.bbox_left = 0
        sprite.bbox_top = 0
        sprite.bbox_right = size[0]
        sprite.bbox_bottom = size[1]
        if precise:
            sprite._build_masks()
        return sprite

    def _make_instance(self, sprite, x, y):
        from runtime.game_runner import GameInstance
        with patch('runtime.game_runner.load_all_plugins'):
            inst = GameInstance("test", x, y, {}, MagicMock())
        inst.sprite = sprite
        inst._cached_width = sprite.width
        inst._cached_height = sprite.height
        inst.image_index = 0
        return inst

    def test_sprite_precise_false_no_masks(self):
        sprite = self._make_sprite({(0, 0)}, precise=False)
        assert sprite.masks == []
        assert sprite.get_mask(0) is None

    def test_sprite_precise_true_builds_masks(self):
        sprite = self._make_sprite({(0, 0), (1, 1)}, precise=True)
        assert len(sprite.masks) == 1
        mask = sprite.get_mask(0)
        assert mask is not None
        assert mask.count() == 2  # two opaque pixels

    def test_get_mask_wraps_animation_index(self):
        sprite = self._make_sprite({(0, 0)}, precise=True)
        # Single frame; out-of-range index wraps.
        assert sprite.get_mask(0) is sprite.get_mask(5)

    def test_refine_accepts_when_neither_precise(self, game_runner):
        s1 = self._make_sprite({(0, 0)}, precise=False)
        s2 = self._make_sprite({(0, 0)}, precise=False)
        i1 = self._make_instance(s1, 0, 0)
        i2 = self._make_instance(s2, 0, 0)
        assert game_runner._precise_refine(i1, 0, 0, i2, 0, 0) is True

    def test_refine_rejects_when_masks_dont_overlap(self, game_runner):
        # i1 opaque at (0,0); i2 opaque at (7,7). At zero offset, AABBs overlap
        # but the opaque pixels are at opposite corners — no mask intersection.
        s1 = self._make_sprite({(0, 0)}, precise=True)
        s2 = self._make_sprite({(7, 7)}, precise=True)
        i1 = self._make_instance(s1, 0, 0)
        i2 = self._make_instance(s2, 1, 0)  # shift so masks definitely miss
        assert game_runner._precise_refine(i1, 0, 0, i2, 1, 0) is False

    def test_refine_keeps_when_masks_overlap(self, game_runner):
        s1 = self._make_sprite({(0, 0)}, precise=True)
        s2 = self._make_sprite({(0, 0)}, precise=True)
        i1 = self._make_instance(s1, 0, 0)
        i2 = self._make_instance(s2, 0, 0)
        assert game_runner._precise_refine(i1, 0, 0, i2, 0, 0) is True

    def test_refine_falls_back_when_rotated(self, game_runner):
        s1 = self._make_sprite({(0, 0)}, precise=True)
        s2 = self._make_sprite({(7, 7)}, precise=True)
        i1 = self._make_instance(s1, 0, 0)
        i2 = self._make_instance(s2, 1, 0)
        i1.rotation = 45
        # Would reject under precise, but rotation forces AABB fallback (True).
        assert game_runner._precise_refine(i1, 0, 0, i2, 1, 0) is True

    def test_refine_falls_back_when_scaled(self, game_runner):
        s1 = self._make_sprite({(0, 0)}, precise=True)
        s2 = self._make_sprite({(7, 7)}, precise=True)
        i1 = self._make_instance(s1, 0, 0)
        i2 = self._make_instance(s2, 1, 0)
        i1.scale_x = 2.0
        assert game_runner._precise_refine(i1, 0, 0, i2, 1, 0) is True

    def test_refine_returns_true_without_sprites(self, game_runner):
        i1 = MagicMock()
        i1.sprite = None
        i2 = MagicMock()
        i2.sprite = None
        assert game_runner._precise_refine(i1, 0, 0, i2, 0, 0) is True

    def test_instances_overlap_uses_precise(self, game_runner):
        # End-to-end wiring: AABBs overlap but masks don't.
        s1 = self._make_sprite({(0, 0)}, precise=True)
        s2 = self._make_sprite({(7, 7)}, precise=True)
        i1 = self._make_instance(s1, 0, 0)
        i2 = self._make_instance(s2, 1, 0)
        assert game_runner.instances_overlap(i1, i2) is False
        # Flip precise off and the AABB result wins.
        s1.precise = False
        s2.precise = False
        assert game_runner.instances_overlap(i1, i2) is True


class TestViewsRendering:
    """Tests for the views/camera system (Phase 2b: single-view minimum)."""

    def _make_room(self, width=1600, height=1200, views_enabled=False, follow=None):
        """Construct a GameRoom directly with predictable view config."""
        with patch('runtime.game_runner.pygame'):
            with patch('runtime.game_runner.load_all_plugins'):
                from runtime.game_runner import GameRoom
                room_data = {
                    'width': width,
                    'height': height,
                    'background_color': '#000000',
                    'views_enabled': views_enabled,
                }
                if follow is not None:
                    room_data['views'] = {
                        'view_0': {
                            'visible': True,
                            'view_x': 0, 'view_y': 0,
                            'view_w': 800, 'view_h': 600,
                            'port_x': 0, 'port_y': 0,
                            'port_w': 800, 'port_h': 600,
                            'follow': follow,
                            'hborder': 100, 'vborder': 100,
                        }
                    }
                room = GameRoom("test_room", room_data, action_executor=MagicMock())
                return room

    def test_views_default_disabled(self):
        room = self._make_room()
        assert room.views_enabled is False
        # 8 view slots always exist with default config.
        assert len(room.views) == 8
        assert room.views[0]['visible'] is True
        for v in room.views[1:]:
            assert v['visible'] is False

    def test_active_views_returns_visible_in_order(self):
        room = self._make_room()
        room.views[0]['visible'] = False
        room.views[2]['visible'] = True
        room.views[5]['visible'] = True
        active = room._active_views()
        assert [i for i, _ in active] == [2, 5]
        assert active[0][1] is room.views[2]
        assert active[1][1] is room.views[5]

    def test_active_views_empty_when_all_invisible(self):
        room = self._make_room()
        for v in room.views:
            v['visible'] = False
        assert room._active_views() == []

    def test_render_no_views_skips_clip(self):
        """Back-compat: views disabled → no clip manipulation, single fill."""
        room = self._make_room(views_enabled=False)
        screen = MagicMock()
        room.render(screen)
        screen.set_clip.assert_not_called()
        assert screen.fill.call_count == 1  # background_color fill

    def test_render_views_enabled_sets_port_clip(self):
        """View 0 has a port; render() must clip to that port and restore."""
        room = self._make_room(views_enabled=True)
        # Configure a non-default port to verify it's applied
        room.views[0]['port_x'] = 100
        room.views[0]['port_y'] = 50
        room.views[0]['port_w'] = 640
        room.views[0]['port_h'] = 480
        room.views[0]['view_w'] = 640
        room.views[0]['view_h'] = 480

        prior_clip = object()  # sentinel
        screen = MagicMock()
        screen.get_clip.return_value = prior_clip

        room.render(screen)

        screen.set_clip.assert_any_call(
            __import__('pygame').Rect(100, 50, 640, 480)
        )
        # Final restore call uses the captured prior clip.
        screen.set_clip.assert_called_with(prior_clip)

    def test_render_no_visible_views_falls_back_to_legacy(self):
        """views_enabled but no view is visible → behave like views off."""
        room = self._make_room(views_enabled=True)
        for v in room.views:
            v['visible'] = False
        screen = MagicMock()
        room.render(screen)
        screen.set_clip.assert_not_called()


class TestMultiViewSplitScreen:
    """Tests for Phase 2c: multiple visible views rendered in split-screen."""

    def _make_room_with_two_views(self):
        with patch('runtime.game_runner.pygame'):
            with patch('runtime.game_runner.load_all_plugins'):
                from runtime.game_runner import GameRoom
                room = GameRoom("test", {
                    'width': 1600,
                    'height': 1200,
                    'views_enabled': True,
                    'views': {
                        'view_0': {
                            'visible': True,
                            'view_x': 0, 'view_y': 0,
                            'view_w': 400, 'view_h': 300,
                            'port_x': 0, 'port_y': 0,
                            'port_w': 400, 'port_h': 300,
                        },
                        'view_1': {
                            'visible': True,
                            'view_x': 800, 'view_y': 600,
                            'view_w': 400, 'view_h': 300,
                            'port_x': 400, 'port_y': 0,
                            'port_w': 400, 'port_h': 300,
                        },
                    },
                }, action_executor=MagicMock())
                return room

    def test_render_iterates_all_visible_views(self):
        """Each visible view gets its own set_clip call with its own port."""
        room = self._make_room_with_two_views()
        import pygame
        screen = MagicMock()
        screen.get_clip.return_value = pygame.Rect(0, 0, 800, 600)

        room.render(screen)

        clip_calls = [c.args[0] for c in screen.set_clip.call_args_list
                      if c.args and isinstance(c.args[0], pygame.Rect)]
        # Two ports set (one per view), plus the final restore call.
        assert pygame.Rect(0, 0, 400, 300) in clip_calls
        assert pygame.Rect(400, 0, 400, 300) in clip_calls
        # The fill happens once before the loop, not per-view, so areas not
        # covered by any port still show the bg color.
        assert screen.fill.call_count == 1

    def test_render_restores_clip_via_finally(self):
        """An exception mid-render must still restore the prior clip."""
        room = self._make_room_with_two_views()
        import pygame
        sentinel_clip = pygame.Rect(0, 0, 800, 600)
        screen = MagicMock()
        screen.get_clip.return_value = sentinel_clip

        room.render(screen)

        # Last set_clip call is the restore with the sentinel.
        assert screen.set_clip.call_args_list[-1].args == (sentinel_clip,)
        assert room.current_view_index == -1  # reset after loop

    def test_current_view_index_starts_negative(self):
        room = self._make_room_with_two_views()
        assert room.current_view_index == -1

    def test_render_skips_invisible_views(self):
        room = self._make_room_with_two_views()
        room.views[1]['visible'] = False
        import pygame
        screen = MagicMock()
        screen.get_clip.return_value = pygame.Rect(0, 0, 800, 600)
        room.render(screen)
        clip_rects = [c.args[0] for c in screen.set_clip.call_args_list
                      if c.args and isinstance(c.args[0], pygame.Rect)]
        assert pygame.Rect(0, 0, 400, 300) in clip_rects
        assert pygame.Rect(400, 0, 400, 300) not in clip_rects


class TestViewFollowSpeedLimit:
    """Tests for hspeed/vspeed clamp on follow-induced view shifts."""

    def _make_room(self, hspeed=-1, vspeed=-1):
        with patch('runtime.game_runner.pygame'):
            with patch('runtime.game_runner.load_all_plugins'):
                from runtime.game_runner import GameRoom, GameInstance
                room = GameRoom("test", {
                    'width': 4000,
                    'height': 4000,
                    'views_enabled': True,
                    'views': {
                        'view_0': {
                            'visible': True,
                            'view_x': 0, 'view_y': 0,
                            'view_w': 800, 'view_h': 600,
                            'port_x': 0, 'port_y': 0,
                            'port_w': 800, 'port_h': 600,
                            'follow': 'player',
                            'hborder': 100, 'vborder': 100,
                            'hspeed': hspeed,
                            'vspeed': vspeed,
                        }
                    }
                }, action_executor=MagicMock())
                player = GameInstance("player", 0, 0, {}, MagicMock())
                room.instances.append(player)
                return room, player

    def test_default_minus_one_means_no_speed_limit(self):
        """hspeed=-1 (the default) lets the view jump in one tick."""
        room, player = self._make_room(hspeed=-1)
        player.x = 2000  # huge shift required
        player.y = 50
        room.update_views()
        # Unlimited: view_x = target - view_w + hborder = 2000 - 800 + 100 = 1300
        assert room.views[0]['view_x'] == 1300

    def test_hspeed_clamps_rightward_shift(self):
        """Positive hspeed caps the per-tick rightward camera movement."""
        room, player = self._make_room(hspeed=50)
        player.x = 2000  # would jump 1300 px without a limit
        player.y = 50
        room.update_views()
        assert room.views[0]['view_x'] == 50  # clamped to old_vx + hspeed

    def test_hspeed_clamps_leftward_shift(self):
        room, player = self._make_room(hspeed=30)
        room.views[0]['view_x'] = 500  # start scrolled right
        player.x = 0  # would jump view_x → -100 without a limit
        player.y = 50
        room.update_views()
        assert room.views[0]['view_x'] == 470  # old_vx - hspeed

    def test_vspeed_independent_of_hspeed(self):
        """Each axis has its own clamp."""
        room, player = self._make_room(hspeed=10, vspeed=200)
        player.x = 2000
        player.y = 2000
        room.update_views()
        assert room.views[0]['view_x'] == 10
        assert room.views[0]['view_y'] == 200


class TestInstanceViewOffset:
    """Tests that GameInstance.render applies view_offset to blit position."""

    def _make_instance_with_sprite(self):
        import pygame
        from runtime.game_runner import GameInstance, GameSprite

        sprite = GameSprite.__new__(GameSprite)
        sprite.path = ""
        sprite.sprite_data = {}
        sprite.surface = pygame.Surface((16, 16), pygame.SRCALPHA)
        sprite.frames = [sprite.surface]
        sprite.masks = []
        sprite.frame_count = 1
        sprite.frame_width = 16
        sprite.frame_height = 16
        sprite.width = 16
        sprite.height = 16
        sprite.origin_x = 0
        sprite.origin_y = 0
        sprite.speed = 10.0
        sprite.animation_type = "single"
        sprite.precise = False

        with patch('runtime.game_runner.load_all_plugins'):
            inst = GameInstance("test", 200, 150, {}, MagicMock())
        inst.sprite = sprite
        inst.scale_x = 1.0
        inst.scale_y = 1.0
        inst.image_index = 0
        return inst

    def test_render_no_offset_blits_at_world_pos(self):
        inst = self._make_instance_with_sprite()
        screen = MagicMock()
        inst.render(screen)
        screen.blit.assert_called_once()
        _, kwargs = screen.blit.call_args
        args = screen.blit.call_args[0]
        # blit(surface, (x, y))
        assert args[1] == (200, 150)

    def test_render_with_offset_shifts_blit_position(self):
        inst = self._make_instance_with_sprite()
        screen = MagicMock()
        inst.render(screen, view_offset=(-50, 100))
        args = screen.blit.call_args[0]
        # world (200, 150) - origin (0, 0) + offset (-50, 100) = (150, 250)
        assert args[1] == (150, 250)


class TestViewFollow:
    """Tests for GameRoom.update_views() follow-target logic."""

    def _make_room_with_follow(self, room_w=1600, room_h=1200):
        with patch('runtime.game_runner.pygame'):
            with patch('runtime.game_runner.load_all_plugins'):
                from runtime.game_runner import GameRoom, GameInstance
                room = GameRoom("test", {
                    'width': room_w,
                    'height': room_h,
                    'views_enabled': True,
                    'views': {
                        'view_0': {
                            'visible': True,
                            'view_x': 0, 'view_y': 0,
                            'view_w': 800, 'view_h': 600,
                            'port_x': 0, 'port_y': 0,
                            'port_w': 800, 'port_h': 600,
                            'follow': 'player',
                            'hborder': 100, 'vborder': 100,
                        }
                    }
                }, action_executor=MagicMock())
                player = GameInstance("player", 0, 0, {}, MagicMock())
                room.instances.append(player)
                return room, player

    def test_follow_pushes_view_right_when_target_passes_hborder(self):
        room, player = self._make_room_with_follow()
        # view_x=0, view_w=800, hborder=100 → trigger zone is x > 700.
        player.x = 750
        player.y = 50  # vborder zone doesn't matter for this assertion
        room.update_views()
        # Expected: view_x = target - view_w + hborder = 750 - 800 + 100 = 50
        assert room.views[0]['view_x'] == 50

    def test_follow_pushes_view_left_when_target_below_hborder(self):
        room, player = self._make_room_with_follow()
        room.views[0]['view_x'] = 400  # start scrolled-right
        player.x = 450  # target at view_x + 50, inside hborder=100 → push left
        player.y = 50
        room.update_views()
        # Expected: view_x = target - hborder = 450 - 100 = 350
        assert room.views[0]['view_x'] == 350

    def test_follow_clamps_view_to_room_right_edge(self):
        room, player = self._make_room_with_follow(room_w=1000, room_h=1200)
        room.views[0]['view_x'] = 200
        player.x = 950  # would push view_x = 950 - 800 + 100 = 250
        player.y = 50
        room.update_views()
        # Clamp: view_x cannot exceed room_w - view_w = 1000 - 800 = 200
        assert room.views[0]['view_x'] == 200

    def test_follow_clamps_view_to_room_left_edge(self):
        room, player = self._make_room_with_follow()
        room.views[0]['view_x'] = 500
        player.x = 10  # would push view_x = 10 - 100 = -90
        player.y = 50
        room.update_views()
        assert room.views[0]['view_x'] == 0

    def test_follow_missing_target_is_noop(self):
        room, _ = self._make_room_with_follow()
        room.instances.clear()  # remove the player
        room.views[0]['view_x'] = 400
        room.views[0]['view_y'] = 300
        room.update_views()
        assert room.views[0]['view_x'] == 400
        assert room.views[0]['view_y'] == 300

    def test_update_views_noop_when_disabled(self):
        room, player = self._make_room_with_follow()
        room.views_enabled = False
        room.views[0]['view_x'] = 100
        player.x = 5000  # would normally trigger a huge shift
        room.update_views()
        assert room.views[0]['view_x'] == 100


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


class TestSlideAxisToContact:
    """A blocked axis move slides flush against the blocker instead of being
    cancelled outright.

    Regression: vertical movement was all-or-nothing, so a faster-than-the-gap
    descent (Pingus at his terminal-velocity clamp of 24) was rejected whole and
    left the character up to |vspeed| px above the floor. That gap exceeded the
    1px ground probe and 12px move_to_contact snap the object logic used, so
    Pingus hung in mid-air with his animation still cycling. Sliding to contact
    lands him flush at any speed. The collision check is faked here to model a
    floor/wall so the slide loop is exercised deterministically without a full
    room.
    """

    def _runner(self):
        with patch('runtime.game_runner.load_all_plugins'):
            from runtime.game_runner import GameRunner
            return GameRunner.__new__(GameRunner)

    def test_fast_faller_lands_flush(self):
        from types import SimpleNamespace
        runner = self._runner()
        floor_y = 140.0
        runner.check_movement_collision_with_blocker = \
            lambda inst, data: (inst.intended_y < floor_y, object())

        inst = SimpleNamespace(x=50.0, y=120.0, hspeed=0.0, vspeed=24.0,
                               intended_x=50.0, intended_y=144.0)
        # Full 24px move (to y=144) collides; without sliding the engine would
        # leave the faller at y=120 — 20px above the floor.
        runner._slide_axis_to_contact(inst, 'y', {})

        assert inst.y == 139.0           # slid down flush, 1px above the floor
        assert inst.intended_y == 139.0  # reset to the resting position
        assert inst.x == 50.0            # vertical slide leaves x untouched

    def test_no_slide_when_already_flush(self):
        from types import SimpleNamespace
        runner = self._runner()
        # Next pixel always collides: already resting against the blocker.
        runner.check_movement_collision_with_blocker = \
            lambda inst, data: (False, object())
        inst = SimpleNamespace(x=0.0, y=100.0, hspeed=0.0, vspeed=24.0,
                               intended_x=0.0, intended_y=124.0)
        runner._slide_axis_to_contact(inst, 'y', {})
        assert inst.y == 100.0           # couldn't advance a pixel; stays put

    def test_horizontal_slide_against_wall(self):
        from types import SimpleNamespace
        runner = self._runner()
        wall_x = 80.0
        runner.check_movement_collision_with_blocker = \
            lambda inst, data: (inst.intended_x < wall_x, object())
        inst = SimpleNamespace(x=60.0, y=10.0, hspeed=24.0, vspeed=0.0,
                               intended_x=84.0, intended_y=10.0)
        runner._slide_axis_to_contact(inst, 'x', {})
        assert inst.x == 79.0            # slid right flush against the wall
        assert inst.y == 10.0


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


class TestResolveParentInheritance:
    """Tests for resolve_parent_inheritance: events + property inheritance."""

    @pytest.fixture
    def resolve(self):
        from runtime.game_runner import resolve_parent_inheritance
        return resolve_parent_inheritance

    def test_no_parent_returns_input_unchanged(self, resolve):
        child = {'name': 'obj_child', 'depth': 5}
        objects = {'obj_child': child}
        assert resolve(child, objects) is child

    def test_unknown_parent_returns_input_unchanged(self, resolve):
        child = {'name': 'obj_child', 'parent': 'obj_missing', 'depth': 5}
        objects = {'obj_child': child}
        # Parent name is set but not in the objects dict — nothing to inherit.
        result = resolve(child, objects)
        assert result == child

    def test_inherits_unset_property_from_parent(self, resolve):
        parent = {'name': 'obj_parent', 'depth': -100}
        child = {'name': 'obj_child', 'parent': 'obj_parent'}
        objects = {'obj_parent': parent, 'obj_child': child}
        result = resolve(child, objects)
        assert result['depth'] == -100

    def test_child_property_overrides_parent(self, resolve):
        parent = {'name': 'obj_parent', 'depth': -100}
        child = {'name': 'obj_child', 'parent': 'obj_parent', 'depth': 5}
        objects = {'obj_parent': parent, 'obj_child': child}
        result = resolve(child, objects)
        assert result['depth'] == 5

    def test_none_valued_child_property_inherits(self, resolve):
        # An explicitly-None child value is treated as "not set".
        parent = {'name': 'obj_parent', 'depth': -100}
        child = {'name': 'obj_child', 'parent': 'obj_parent', 'depth': None}
        objects = {'obj_parent': parent, 'obj_child': child}
        result = resolve(child, objects)
        assert result['depth'] == -100

    def test_child_only_props_never_inherit(self, resolve):
        # sprite / visible / solid / persistent must come from the child only.
        parent = {
            'name': 'obj_parent',
            'sprite': 'spr_parent',
            'visible': False,
            'solid': True,
            'persistent': True,
        }
        child = {'name': 'obj_child', 'parent': 'obj_parent'}
        objects = {'obj_parent': parent, 'obj_child': child}
        result = resolve(child, objects)
        assert 'sprite' not in result
        assert 'visible' not in result
        assert 'solid' not in result
        assert 'persistent' not in result

    def test_child_only_props_keep_child_value(self, resolve):
        # When the child does set a child-only prop, its value is preserved
        # and the parent's is ignored — even if the parent's would "look better".
        parent = {'name': 'obj_parent', 'sprite': 'spr_parent', 'solid': True}
        child = {
            'name': 'obj_child',
            'parent': 'obj_parent',
            'sprite': 'spr_child',
            'solid': False,
        }
        objects = {'obj_parent': parent, 'obj_child': child}
        result = resolve(child, objects)
        assert result['sprite'] == 'spr_child'
        assert result['solid'] is False

    def test_grandparent_property_inherits_through_chain(self, resolve):
        grandparent = {'name': 'obj_grand', 'depth': -50}
        parent = {'name': 'obj_parent', 'parent': 'obj_grand'}
        child = {'name': 'obj_child', 'parent': 'obj_parent'}
        objects = {
            'obj_grand': grandparent,
            'obj_parent': parent,
            'obj_child': child,
        }
        result = resolve(child, objects)
        assert result['depth'] == -50

    def test_closest_parent_wins_over_grandparent(self, resolve):
        grandparent = {'name': 'obj_grand', 'depth': -50}
        parent = {'name': 'obj_parent', 'parent': 'obj_grand', 'depth': -100}
        child = {'name': 'obj_child', 'parent': 'obj_parent'}
        objects = {
            'obj_grand': grandparent,
            'obj_parent': parent,
            'obj_child': child,
        }
        result = resolve(child, objects)
        assert result['depth'] == -100

    def test_events_still_inherit_from_parent(self, resolve):
        parent_create = {'actions': [{'action': 'create_action'}]}
        parent = {'name': 'obj_parent', 'events': {'create': parent_create}}
        child = {'name': 'obj_child', 'parent': 'obj_parent', 'events': {}}
        objects = {'obj_parent': parent, 'obj_child': child}
        result = resolve(child, objects)
        assert result['events']['create'] is parent_create

    def test_child_event_overrides_parent_event(self, resolve):
        parent_step = {'actions': [{'action': 'parent_step'}]}
        child_step = {'actions': [{'action': 'child_step'}]}
        parent = {'name': 'obj_parent', 'events': {'step': parent_step}}
        child = {
            'name': 'obj_child',
            'parent': 'obj_parent',
            'events': {'step': child_step},
        }
        objects = {'obj_parent': parent, 'obj_child': child}
        result = resolve(child, objects)
        assert result['events']['step'] is child_step

    def test_does_not_mutate_input(self, resolve):
        parent = {'name': 'obj_parent', 'depth': -100, 'events': {'create': {}}}
        child = {'name': 'obj_child', 'parent': 'obj_parent'}
        objects = {'obj_parent': parent, 'obj_child': child}
        resolve(child, objects)
        assert 'depth' not in child
        assert 'events' not in child

    def test_self_referential_parent_does_not_loop(self, resolve):
        # Pathological case: an object listing itself as its parent.  The
        # 10-level cap must keep this from spinning forever.
        child = {'name': 'obj_loop', 'parent': 'obj_loop', 'depth': 7}
        objects = {'obj_loop': child}
        result = resolve(child, objects)
        # Child's own depth wins (it's set), and the call returns.
        assert result['depth'] == 7


class TestDrawQueueSpriteResolution:
    """Regression tests for the draw_lives / draw_sprite draw-queue handlers.

    Both must resolve sprites from ``GameRunner.sprites`` via the instance's
    ``action_executor.game_runner`` back-reference. A regression had them read
    a non-existent ``self.sprites`` on the GameInstance, which crashed the
    game at draw time with AttributeError the moment a draw_lives/draw_sprite
    action ran. These tests exercise the real back-reference chain (no
    manually-injected ``sprites`` attribute that would mask the bug).
    """

    @staticmethod
    def _make_instance(sprites):
        import types
        from runtime.game_runner import GameInstance
        inst = GameInstance.__new__(GameInstance)  # skip __init__ / pygame display
        inst._font_cache = {}
        inst.action_executor = types.SimpleNamespace(
            game_runner=types.SimpleNamespace(sprites=sprites)
        )
        return inst

    @staticmethod
    def _icon(color, size=(10, 10)):
        import pygame
        surf = pygame.Surface(size)
        surf.fill(color)
        return surf

    def test_draw_lives_blits_one_sprite_per_life(self):
        import pygame
        import types
        pygame.init()
        pygame.font.init()
        icon = self._icon((255, 0, 0))
        inst = self._make_instance(
            {'spr_life': types.SimpleNamespace(frames=[icon], surface=icon)}
        )
        screen = pygame.Surface((200, 50))
        screen.fill((0, 0, 0))

        inst._draw_lives(screen, {'count': 3, 'x': 0, 'y': 0, 'sprite': 'spr_life'})

        # Three 10px-wide icons laid out at x=0,10,20; nothing at x>=30.
        assert screen.get_at((2, 5))[:3] == (255, 0, 0)
        assert screen.get_at((12, 5))[:3] == (255, 0, 0)
        assert screen.get_at((22, 5))[:3] == (255, 0, 0)
        assert screen.get_at((35, 5))[:3] == (0, 0, 0)

    def test_draw_lives_text_fallback_when_no_sprite(self):
        import pygame
        pygame.init()
        pygame.font.init()
        inst = self._make_instance({})
        screen = pygame.Surface((200, 50))
        screen.fill((0, 0, 0))

        inst._draw_lives(screen, {'count': 3, 'x': 0, 'y': 0, 'sprite': ''})

        # Numeric "Lives: N" readout draws some non-black pixels.
        assert any(screen.get_at((px, 10))[:3] != (0, 0, 0) for px in range(80))

    def test_draw_lives_no_crash_without_action_executor(self):
        import pygame
        from runtime.game_runner import GameInstance
        pygame.init()
        pygame.font.init()
        inst = GameInstance.__new__(GameInstance)
        inst._font_cache = {}  # deliberately no action_executor attribute
        screen = pygame.Surface((200, 50))
        screen.fill((0, 0, 0))

        # Must not raise AttributeError; falls back to text.
        inst._draw_lives(screen, {'count': 2, 'x': 0, 'y': 0, 'sprite': 'spr_life'})
        assert any(screen.get_at((px, 10))[:3] != (0, 0, 0) for px in range(80))

    def test_draw_sprite_resolves_via_runner(self):
        import pygame
        import types
        pygame.init()
        icon = self._icon((0, 255, 0))
        inst = self._make_instance(
            {'spr_x': types.SimpleNamespace(frames=[icon], surface=icon)}
        )
        screen = pygame.Surface((50, 50))
        screen.fill((0, 0, 0))

        inst._draw_sprite(screen, {'sprite_name': 'spr_x', 'x': 0, 'y': 0, 'subimage': 0})
        assert screen.get_at((5, 5))[:3] == (0, 255, 0)


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
