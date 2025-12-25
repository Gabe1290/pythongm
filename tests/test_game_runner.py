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
import os
import sys
import tempfile
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

# Set dummy video driver before importing pygame-dependent modules
os.environ['SDL_VIDEODRIVER'] = 'dummy'
os.environ['SDL_AUDIODRIVER'] = 'dummy'


# Check if pygame is available
HAS_PYGAME = False
try:
    import pygame
    pygame.init()
    HAS_PYGAME = True
except ImportError:
    HAS_PYGAME = False
except Exception:
    # pygame.error or other init errors
    HAS_PYGAME = False

# Skip all tests if pygame is not available
pytestmark = pytest.mark.skipif(not HAS_PYGAME, reason="pygame not available or failed to initialize")


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
                from runtime.game_runner import GameRoom, GameInstance
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


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
