#!/usr/bin/env python3
"""
Test Drawing Actions Implementation

Tests the three drawing actions:
1. draw_text - Draw text at position
2. draw_rectangle - Draw filled or outlined rectangle
3. draw_ellipse - Draw filled or outlined ellipse/circle
"""

import sys
import os
sys.path.insert(0, os.path.abspath('.'))

from runtime.action_executor import ActionExecutor

class MockGameRunner:
    def __init__(self):
        self.instances = []
        self.draw_color = (0, 0, 0)
        self.global_variables = {}
        self.score = 0
        self.lives = 3
        self.health = 100

class MockInstance:
    def __init__(self):
        self.x = 100
        self.y = 200
        self.object_name = "obj_test"
        self.draw_color = (255, 0, 0)  # Red
        self.score = 42
        self.lives = 3

# Test Setup
print("=" * 60)
print("DRAWING ACTIONS TEST")
print("=" * 60)

game_runner = MockGameRunner()
executor = ActionExecutor(game_runner=game_runner)

# ==================== TEST 1: draw_text ====================
print("\n" + "=" * 60)
print("TEST 1: draw_text - Basic text drawing")
print("=" * 60)

instance = MockInstance()
instance.draw_color = (255, 255, 255)  # White

result = executor.execute_action(instance, {
    "action": "draw_text",
    "parameters": {
        "x": 50,
        "y": 100,
        "text": "Hello World"
    }
})

assert hasattr(instance, '_draw_queue'), "Expected _draw_queue to be created"
assert len(instance._draw_queue) == 1, f"Expected 1 draw command, got {len(instance._draw_queue)}"

cmd = instance._draw_queue[0]
assert cmd['type'] == 'text', f"Expected type='text', got {cmd['type']}"
assert cmd['x'] == 50, f"Expected x=50, got {cmd['x']}"
assert cmd['y'] == 100, f"Expected y=100, got {cmd['y']}"
assert cmd['text'] == "Hello World", f"Expected 'Hello World', got '{cmd['text']}'"
assert cmd['color'] == (255, 255, 255), f"Expected white color, got {cmd['color']}"

print("✅ Basic text drawing works")

# ==================== TEST 2: draw_text with expressions ====================
print("\n" + "=" * 60)
print("TEST 2: draw_text - With expression support")
print("=" * 60)

instance = MockInstance()
instance.draw_color = (0, 255, 0)  # Green
instance._draw_queue = []  # Clear

result = executor.execute_action(instance, {
    "action": "draw_text",
    "parameters": {
        "x": "self.x + 10",  # Expression
        "y": "self.y - 20",  # Expression
        "text": "Score: " + str(instance.score)  # Concatenation
    }
})

cmd = instance._draw_queue[0]
assert cmd['x'] == 110, f"Expected x=110 (100+10), got {cmd['x']}"
assert cmd['y'] == 180, f"Expected y=180 (200-20), got {cmd['y']}"
assert cmd['text'] == "Score: 42", f"Expected 'Score: 42', got '{cmd['text']}'"

print("✅ Text with expressions works")

# ==================== TEST 3: draw_text at instance position ====================
print("\n" + "=" * 60)
print("TEST 3: draw_text - Default to instance position")
print("=" * 60)

instance = MockInstance()
instance.x = 320
instance.y = 240
instance._draw_queue = []

result = executor.execute_action(instance, {
    "action": "draw_text",
    "parameters": {
        "text": "Centered"
    }
})

cmd = instance._draw_queue[0]
assert cmd['x'] == 320, f"Expected x=320 (instance.x), got {cmd['x']}"
assert cmd['y'] == 240, f"Expected y=240 (instance.y), got {cmd['y']}"

print("✅ Default position works")

# ==================== TEST 4: draw_rectangle - Filled ====================
print("\n" + "=" * 60)
print("TEST 4: draw_rectangle - Filled rectangle")
print("=" * 60)

instance = MockInstance()
instance.draw_color = (255, 0, 0)  # Red
instance._draw_queue = []

result = executor.execute_action(instance, {
    "action": "draw_rectangle",
    "parameters": {
        "x1": 10,
        "y1": 20,
        "x2": 110,
        "y2": 120,
        "filled": True
    }
})

assert len(instance._draw_queue) == 1
cmd = instance._draw_queue[0]
assert cmd['type'] == 'rectangle', f"Expected type='rectangle', got {cmd['type']}"
assert cmd['x1'] == 10, f"Expected x1=10, got {cmd['x1']}"
assert cmd['y1'] == 20, f"Expected y1=20, got {cmd['y1']}"
assert cmd['x2'] == 110, f"Expected x2=110, got {cmd['x2']}"
assert cmd['y2'] == 120, f"Expected y2=120, got {cmd['y2']}"
assert cmd['filled'] == True, f"Expected filled=True, got {cmd['filled']}"
assert cmd['color'] == (255, 0, 0), f"Expected red color, got {cmd['color']}"

print("✅ Filled rectangle works")

# ==================== TEST 5: draw_rectangle - Outline ====================
print("\n" + "=" * 60)
print("TEST 5: draw_rectangle - Outlined rectangle")
print("=" * 60)

instance = MockInstance()
instance.draw_color = (0, 0, 255)  # Blue
instance._draw_queue = []

result = executor.execute_action(instance, {
    "action": "draw_rectangle",
    "parameters": {
        "x1": 50,
        "y1": 50,
        "x2": 200,
        "y2": 150,
        "filled": False
    }
})

cmd = instance._draw_queue[0]
assert cmd['filled'] == False, f"Expected filled=False, got {cmd['filled']}"
assert cmd['color'] == (0, 0, 255), f"Expected blue color, got {cmd['color']}"

print("✅ Outlined rectangle works")

# ==================== TEST 6: draw_rectangle - With expressions ====================
print("\n" + "=" * 60)
print("TEST 6: draw_rectangle - With expression parameters")
print("=" * 60)

instance = MockInstance()
instance.x = 100
instance.y = 100
instance.draw_color = (128, 128, 128)  # Gray
instance._draw_queue = []

result = executor.execute_action(instance, {
    "action": "draw_rectangle",
    "parameters": {
        "x1": "self.x - 25",
        "y1": "self.y - 25",
        "x2": "self.x + 25",
        "y2": "self.y + 25",
        "filled": True
    }
})

cmd = instance._draw_queue[0]
assert cmd['x1'] == 75, f"Expected x1=75, got {cmd['x1']}"
assert cmd['y1'] == 75, f"Expected y1=75, got {cmd['y1']}"
assert cmd['x2'] == 125, f"Expected x2=125, got {cmd['x2']}"
assert cmd['y2'] == 125, f"Expected y2=125, got {cmd['y2']}"

print("✅ Rectangle with expressions works")

# ==================== TEST 7: draw_ellipse - Filled ====================
print("\n" + "=" * 60)
print("TEST 7: draw_ellipse - Filled ellipse")
print("=" * 60)

instance = MockInstance()
instance.draw_color = (255, 255, 0)  # Yellow
instance._draw_queue = []

result = executor.execute_action(instance, {
    "action": "draw_ellipse",
    "parameters": {
        "x1": 100,
        "y1": 100,
        "x2": 200,
        "y2": 150,
        "filled": True
    }
})

assert len(instance._draw_queue) == 1
cmd = instance._draw_queue[0]
assert cmd['type'] == 'ellipse', f"Expected type='ellipse', got {cmd['type']}"
assert cmd['x1'] == 100, f"Expected x1=100, got {cmd['x1']}"
assert cmd['y1'] == 100, f"Expected y1=100, got {cmd['y1']}"
assert cmd['x2'] == 200, f"Expected x2=200, got {cmd['x2']}"
assert cmd['y2'] == 150, f"Expected y2=150, got {cmd['y2']}"
assert cmd['filled'] == True, f"Expected filled=True, got {cmd['filled']}"
assert cmd['color'] == (255, 255, 0), f"Expected yellow color, got {cmd['color']}"

print("✅ Filled ellipse works")

# ==================== TEST 8: draw_ellipse - Outline ====================
print("\n" + "=" * 60)
print("TEST 8: draw_ellipse - Outlined ellipse")
print("=" * 60)

instance = MockInstance()
instance.draw_color = (255, 0, 255)  # Magenta
instance._draw_queue = []

result = executor.execute_action(instance, {
    "action": "draw_ellipse",
    "parameters": {
        "x1": 50,
        "y1": 50,
        "x2": 150,
        "y2": 100,
        "filled": False
    }
})

cmd = instance._draw_queue[0]
assert cmd['filled'] == False, f"Expected filled=False, got {cmd['filled']}"
assert cmd['color'] == (255, 0, 255), f"Expected magenta color, got {cmd['color']}"

print("✅ Outlined ellipse works")

# ==================== TEST 9: draw_ellipse - Circle (equal dimensions) ====================
print("\n" + "=" * 60)
print("TEST 9: draw_ellipse - Circle (equal width/height)")
print("=" * 60)

instance = MockInstance()
instance.draw_color = (0, 255, 255)  # Cyan
instance._draw_queue = []

result = executor.execute_action(instance, {
    "action": "draw_ellipse",
    "parameters": {
        "x1": 100,
        "y1": 100,
        "x2": 200,
        "y2": 200,  # Same dimensions = circle
        "filled": True
    }
})

cmd = instance._draw_queue[0]
width = cmd['x2'] - cmd['x1']
height = cmd['y2'] - cmd['y1']
assert width == height, f"Expected equal dimensions for circle, got {width}x{height}"

print("✅ Circle (equal dimensions) works")

# ==================== TEST 10: draw_ellipse - With expressions ====================
print("\n" + "=" * 60)
print("TEST 10: draw_ellipse - With expression parameters")
print("=" * 60)

instance = MockInstance()
instance.x = 300
instance.y = 200
instance.draw_color = (128, 0, 128)  # Purple
instance._draw_queue = []

result = executor.execute_action(instance, {
    "action": "draw_ellipse",
    "parameters": {
        "x1": "self.x - 50",
        "y1": "self.y - 30",
        "x2": "self.x + 50",
        "y2": "self.y + 30",
        "filled": True
    }
})

cmd = instance._draw_queue[0]
assert cmd['x1'] == 250, f"Expected x1=250, got {cmd['x1']}"
assert cmd['y1'] == 170, f"Expected y1=170, got {cmd['y1']}"
assert cmd['x2'] == 350, f"Expected x2=350, got {cmd['x2']}"
assert cmd['y2'] == 230, f"Expected y2=230, got {cmd['y2']}"

print("✅ Ellipse with expressions works")

# ==================== TEST 11: Multiple drawing commands ====================
print("\n" + "=" * 60)
print("TEST 11: Multiple drawing commands in sequence")
print("=" * 60)

instance = MockInstance()
instance.draw_color = (255, 255, 255)
instance._draw_queue = []

# Draw multiple shapes
executor.execute_action(instance, {
    "action": "draw_rectangle",
    "parameters": {"x1": 0, "y1": 0, "x2": 100, "y2": 100, "filled": True}
})

executor.execute_action(instance, {
    "action": "draw_ellipse",
    "parameters": {"x1": 25, "y1": 25, "x2": 75, "y2": 75, "filled": True}
})

executor.execute_action(instance, {
    "action": "draw_text",
    "parameters": {"x": 40, "y": 45, "text": "Test"}
})

assert len(instance._draw_queue) == 3, f"Expected 3 draw commands, got {len(instance._draw_queue)}"
assert instance._draw_queue[0]['type'] == 'rectangle'
assert instance._draw_queue[1]['type'] == 'ellipse'
assert instance._draw_queue[2]['type'] == 'text'

print("✅ Multiple drawing commands work")

# ==================== FINAL SUMMARY ====================
print("\n" + "=" * 60)
print("ALL TESTS PASSED ✅")
print("=" * 60)
print("\nDrawing Actions Summary:")
print("  ✅ draw_text - 3 tests passed")
print("  ✅ draw_rectangle - 3 tests passed")
print("  ✅ draw_ellipse - 4 tests passed")
print("  ✅ Multiple commands - 1 test passed")
print("\n  Total: 11/11 tests passed")
print("\nAll drawing actions are production-ready! 🎨")
print("=" * 60)
