#!/usr/bin/env python3
"""
Test Room Lifecycle Events - room_start and room_end

Tests that room_start and room_end events are triggered correctly
when rooms are loaded, changed, and restarted.
"""

import sys
import os
sys.path.insert(0, os.path.dirname(__file__))


def test_lifecycle_helper_methods():
    """Test that the lifecycle helper methods exist and work"""
    print("\n=== Testing Lifecycle Helper Methods ===")

    from runtime.game_runner import GameRunner

    # Test 1: trigger_room_start_event method exists
    print("\n1. Testing trigger_room_start_event exists...")
    try:
        runner = GameRunner()
        assert hasattr(runner, 'trigger_room_start_event'), \
            "GameRunner should have trigger_room_start_event method"
        print("  ✅ trigger_room_start_event method exists")
    except Exception as e:
        print(f"  ❌ Test failed: {e}")
        raise

    # Test 2: trigger_room_end_event method exists
    print("\n2. Testing trigger_room_end_event exists...")
    try:
        runner = GameRunner()
        assert hasattr(runner, 'trigger_room_end_event'), \
            "GameRunner should have trigger_room_end_event method"
        print("  ✅ trigger_room_end_event method exists")
    except Exception as e:
        print(f"  ❌ Test failed: {e}")
        raise

    # Test 3: Methods can be called without errors (when no current_room)
    print("\n3. Testing methods handle missing current_room gracefully...")
    try:
        runner = GameRunner()
        runner.current_room = None

        # Should not raise errors
        runner.trigger_room_start_event()
        runner.trigger_room_end_event()

        print("  ✅ Methods handle missing room gracefully")
    except Exception as e:
        print(f"  ❌ Test failed: {e}")
        raise

    print("\n✅ All lifecycle helper method tests passed!")


def test_event_definitions():
    """Test that room_start and room_end events are defined in the event system"""
    print("\n=== Testing Event Definitions ===")

    # Test 1: room_start event definition exists
    print("\n1. Testing room_start event definition...")
    try:
        from events.event_types import EVENT_TYPES

        assert 'room_start' in EVENT_TYPES, "room_start should be defined in EVENT_TYPES"
        room_start_event = EVENT_TYPES['room_start']

        assert room_start_event.name == 'room_start', "Event name should be room_start"
        assert room_start_event.display_name == 'Room Start', "Display name should be 'Room Start'"
        assert room_start_event.category == 'Room', "Category should be 'Room'"

        print(f"  ✅ room_start event: {room_start_event.display_name} ({room_start_event.category})")
    except Exception as e:
        print(f"  ❌ Test failed: {e}")
        raise

    # Test 2: room_end event definition exists
    print("\n2. Testing room_end event definition...")
    try:
        from events.event_types import EVENT_TYPES

        assert 'room_end' in EVENT_TYPES, "room_end should be defined in EVENT_TYPES"
        room_end_event = EVENT_TYPES['room_end']

        assert room_end_event.name == 'room_end', "Event name should be room_end"
        assert room_end_event.display_name == 'Room End', "Display name should be 'Room End'"
        assert room_end_event.category == 'Room', "Category should be 'Room'"

        print(f"  ✅ room_end event: {room_end_event.display_name} ({room_end_event.category})")
    except Exception as e:
        print(f"  ❌ Test failed: {e}")
        raise

    print("\n✅ All event definition tests passed!")


def test_change_room_triggers():
    """Test that change_room calls the lifecycle methods"""
    print("\n=== Testing change_room Triggers Lifecycle Events ===")

    from runtime.game_runner import GameRunner
    from pathlib import Path
    import tempfile
    import json

    # Create a minimal test project
    with tempfile.TemporaryDirectory() as temp_dir:
        project_path = Path(temp_dir)
        project_file = project_path / "project.json"

        project_data = {
            "name": "LifecycleTest",
            "version": "1.0",
            "settings": {},
            "assets": {
                "rooms": {
                    "room_a": {
                        "name": "room_a",
                        "width": 640,
                        "height": 480,
                        "instances": []
                    },
                    "room_b": {
                        "name": "room_b",
                        "width": 640,
                        "height": 480,
                        "instances": []
                    }
                },
                "objects": {},
                "sprites": {}
            }
        }

        with open(project_file, 'w') as f:
            json.dump(project_data, f, indent=2)

        # Test: change_room calls trigger_room_end_event and trigger_room_start_event
        print("\n1. Testing that change_room triggers lifecycle events...")
        try:
            runner = GameRunner()
            runner.load_project_data_only(project_path)

            # Track method calls
            room_end_called = []
            room_start_called = []

            original_trigger_end = runner.trigger_room_end_event
            original_trigger_start = runner.trigger_room_start_event

            def mock_trigger_end():
                room_end_called.append(True)
                original_trigger_end()

            def mock_trigger_start():
                room_start_called.append(True)
                original_trigger_start()

            runner.trigger_room_end_event = mock_trigger_end
            runner.trigger_room_start_event = mock_trigger_start

            # Start with room_a
            runner.current_room = runner.rooms["room_a"]

            # Change to room_b
            runner.change_room("room_b")

            # Verify both methods were called
            assert len(room_end_called) == 1, "trigger_room_end_event should have been called once"
            assert len(room_start_called) == 1, "trigger_room_start_event should have been called once"

            print("  ✅ change_room triggers room_end and room_start")

        except Exception as e:
            print(f"  ❌ Test failed: {e}")
            raise

    print("\n✅ change_room lifecycle trigger tests passed!")


def run_all_tests():
    """Run all room lifecycle tests"""
    print("="*60)
    print("ROOM LIFECYCLE EVENTS TEST SUITE")
    print("="*60)

    tests = [
        ("Lifecycle Helper Methods", test_lifecycle_helper_methods),
        ("Event Definitions", test_event_definitions),
        ("change_room Triggers", test_change_room_triggers)
    ]

    passed = 0
    failed = 0

    for test_name, test_func in tests:
        try:
            test_func()
            passed += 1
        except Exception as e:
            print(f"\n❌ {test_name} FAILED: {e}")
            import traceback
            traceback.print_exc()
            failed += 1

    print("\n" + "="*60)
    print(f"TEST RESULTS: {passed} passed, {failed} failed out of {len(tests)} tests")
    print("="*60)

    if failed == 0:
        print("\n✅ ALL TESTS PASSED! Room lifecycle events are working correctly.")
    else:
        print(f"\n❌ {failed} test(s) failed.")

    return failed == 0


if __name__ == '__main__':
    try:
        success = run_all_tests()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n\nTests interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n\nFatal error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
