#!/usr/bin/env python3
"""
Test script for draw_line and draw_sprite actions
"""

import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

from runtime.action_executor import ActionExecutor
from runtime.game_engine import GameInstance


class MockSprite:
    """Mock sprite for testing"""
    def __init__(self, name):
        self.name = name
        self.surface = None  # Would be a pygame.Surface in real use
        self.frames = []  # Empty for single-frame sprite
        self.width = 32
        self.height = 32


def test_draw_line():
    """Test draw_line action"""
    print("\n=== Testing draw_line ===")

    # Create a mock instance
    instance = GameInstance("TestObject", 100, 200, {})
    instance.draw_color = (255, 0, 0)  # Red

    # Create action executor
    executor = ActionExecutor()

    # Test 1: Basic line
    print("\n1. Basic line from (10, 20) to (100, 200)")
    parameters = {
        "x1": 10,
        "y1": 20,
        "x2": 100,
        "y2": 200
    }
    executor.execute_draw_line_action(instance, parameters)

    assert len(instance._draw_queue) == 1, "Draw queue should have 1 item"
    cmd = instance._draw_queue[0]
    assert cmd['type'] == 'line', "Command type should be 'line'"
    assert cmd['x1'] == 10, "x1 should be 10"
    assert cmd['y1'] == 20, "y1 should be 20"
    assert cmd['x2'] == 100, "x2 should be 100"
    assert cmd['y2'] == 200, "y2 should be 200"
    assert cmd['color'] == (255, 0, 0), "Color should be red"
    print("✅ Basic line test passed")

    # Clear queue
    instance._draw_queue = []

    # Test 2: Line with expression parameters
    print("\n2. Line with expression parameters")
    parameters = {
        "x1": "self.x",
        "y1": "self.y",
        "x2": "self.x + 50",
        "y2": "self.y + 50"
    }
    executor.execute_draw_line_action(instance, parameters)

    assert len(instance._draw_queue) == 1, "Draw queue should have 1 item"
    cmd = instance._draw_queue[0]
    assert cmd['x1'] == 100, f"x1 should be 100 (instance.x), got {cmd['x1']}"
    assert cmd['y1'] == 200, f"y1 should be 200 (instance.y), got {cmd['y1']}"
    assert cmd['x2'] == 150, f"x2 should be 150 (instance.x + 50), got {cmd['x2']}"
    assert cmd['y2'] == 250, f"y2 should be 250 (instance.y + 50), got {cmd['y2']}"
    print("✅ Expression parameters test passed")

    # Clear queue
    instance._draw_queue = []

    # Test 3: Default parameters
    print("\n3. Line with default parameters")
    parameters = {}
    executor.execute_draw_line_action(instance, parameters)

    assert len(instance._draw_queue) == 1, "Draw queue should have 1 item"
    cmd = instance._draw_queue[0]
    assert cmd['x1'] == 0, "x1 default should be 0"
    assert cmd['y1'] == 0, "y1 default should be 0"
    assert cmd['x2'] == 100, "x2 default should be 100"
    assert cmd['y2'] == 100, "y2 default should be 100"
    print("✅ Default parameters test passed")

    print("\n✅ All draw_line tests passed!")


def test_draw_sprite():
    """Test draw_sprite action"""
    print("\n=== Testing draw_sprite ===")

    # Create a mock instance
    instance = GameInstance("TestObject", 100, 200, {})

    # Create action executor
    executor = ActionExecutor()

    # Test 1: Basic sprite drawing
    print("\n1. Basic sprite drawing")
    parameters = {
        "sprite": "spr_player",
        "x": 50,
        "y": 100,
        "subimage": 0
    }
    executor.execute_draw_sprite_action(instance, parameters)

    assert len(instance._draw_queue) == 1, "Draw queue should have 1 item"
    cmd = instance._draw_queue[0]
    assert cmd['type'] == 'sprite', "Command type should be 'sprite'"
    assert cmd['sprite_name'] == "spr_player", "Sprite name should be 'spr_player'"
    assert cmd['x'] == 50, "x should be 50"
    assert cmd['y'] == 100, "y should be 100"
    assert cmd['subimage'] == 0, "subimage should be 0"
    print("✅ Basic sprite drawing test passed")

    # Clear queue
    instance._draw_queue = []

    # Test 2: Sprite with expression parameters
    print("\n2. Sprite with expression parameters")
    parameters = {
        "sprite": "spr_enemy",
        "x": "self.x + 10",
        "y": "self.y - 20",
        "subimage": 2
    }
    executor.execute_draw_sprite_action(instance, parameters)

    assert len(instance._draw_queue) == 1, "Draw queue should have 1 item"
    cmd = instance._draw_queue[0]
    assert cmd['sprite_name'] == "spr_enemy", "Sprite name should be 'spr_enemy'"
    assert cmd['x'] == 110, f"x should be 110 (instance.x + 10), got {cmd['x']}"
    assert cmd['y'] == 180, f"y should be 180 (instance.y - 20), got {cmd['y']}"
    assert cmd['subimage'] == 2, "subimage should be 2"
    print("✅ Expression parameters test passed")

    # Clear queue
    instance._draw_queue = []

    # Test 3: Default parameters
    print("\n3. Sprite with default parameters")
    parameters = {
        "sprite": "spr_test"
    }
    executor.execute_draw_sprite_action(instance, parameters)

    assert len(instance._draw_queue) == 1, "Draw queue should have 1 item"
    cmd = instance._draw_queue[0]
    assert cmd['x'] == 0, "x default should be 0"
    assert cmd['y'] == 0, "y default should be 0"
    assert cmd['subimage'] == 0, "subimage default should be 0"
    print("✅ Default parameters test passed")

    # Clear queue
    instance._draw_queue = []

    # Test 4: Animated sprite (different frame)
    print("\n4. Animated sprite with frame index")
    parameters = {
        "sprite": "spr_animated",
        "x": 200,
        "y": 300,
        "subimage": 5
    }
    executor.execute_draw_sprite_action(instance, parameters)

    assert len(instance._draw_queue) == 1, "Draw queue should have 1 item"
    cmd = instance._draw_queue[0]
    assert cmd['subimage'] == 5, "subimage should be 5"
    print("✅ Animated sprite test passed")

    print("\n✅ All draw_sprite tests passed!")


def test_integration():
    """Test multiple drawing commands in sequence"""
    print("\n=== Testing Integration (Multiple Commands) ===")

    # Create a mock instance
    instance = GameInstance("TestObject", 100, 200, {})
    instance.draw_color = (0, 255, 0)  # Green

    # Create action executor
    executor = ActionExecutor()

    # Execute multiple drawing actions
    print("\n1. Drawing a line")
    executor.execute_draw_line_action(instance, {
        "x1": 10, "y1": 10, "x2": 100, "y2": 100
    })

    print("2. Drawing a sprite")
    executor.execute_draw_sprite_action(instance, {
        "sprite": "spr_test", "x": 50, "y": 50, "subimage": 0
    })

    print("3. Drawing another line")
    executor.execute_draw_line_action(instance, {
        "x1": 200, "y1": 200, "x2": 300, "y2": 300
    })

    # Verify queue has all commands
    assert len(instance._draw_queue) == 3, f"Draw queue should have 3 items, got {len(instance._draw_queue)}"
    assert instance._draw_queue[0]['type'] == 'line', "First command should be line"
    assert instance._draw_queue[1]['type'] == 'sprite', "Second command should be sprite"
    assert instance._draw_queue[2]['type'] == 'line', "Third command should be line"

    print("✅ Integration test passed - all commands queued correctly!")

    print("\n✅ All integration tests passed!")


if __name__ == '__main__':
    try:
        test_draw_line()
        test_draw_sprite()
        test_integration()

        print("\n" + "="*60)
        print("✅ ALL TESTS PASSED!")
        print("="*60)
        print("\nImplementation Summary:")
        print("- draw_line: ✅ IMPLEMENTED")
        print("  - Queues line drawing commands")
        print("  - Expression support for all parameters")
        print("  - Uses instance draw_color")
        print()
        print("- draw_sprite: ✅ IMPLEMENTED")
        print("  - Queues sprite drawing commands")
        print("  - Expression support for all parameters")
        print("  - Supports animated sprites via subimage parameter")
        print("  - Sprite lookup from GameRunner.sprites dictionary")
        print()
        print("Next steps:")
        print("1. Test with actual pygame rendering")
        print("2. Verify sprite lookup in game_runner.py works correctly")
        print("3. Test with animated sprites")

    except AssertionError as e:
        print(f"\n❌ TEST FAILED: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
