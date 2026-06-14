"""Regression test for live-list iteration during spawning (audit M49).

The per-frame event loops iterated the live instance list, so an instance
created during a step/keyboard event was processed in the SAME frame; an
unconditioned spawner cycle hard-hung the frame. The loops now iterate a
snapshot, so a mid-frame spawn is processed starting next frame (GameMaker
semantics).
"""

import pytest

pygame = pytest.importorskip("pygame")

from runtime.game_runner import GameRunner


class _Room:
    def __init__(self):
        self.name = "r"
        self.instances = []


class _Inst:
    def __init__(self, exec_=None, events=None):
        self.object_data = {"events": events or {}}
        self.keys_pressed = set()
        self.is_thymio = False
        self.thymio_simulator = None
        self.object_name = "obj"
        self.action_executor = exec_


def test_keyboard_press_iterates_snapshot():
    room = _Room()
    runner = GameRunner.__new__(GameRunner)
    runner.current_room = room

    spawned = _Inst()  # created mid-iteration

    class _Exec:
        def __init__(self):
            self.fired = False

        def execute_action_list(self, inst, actions):
            # Simulate a keyboard_press action that spawns a new instance.
            if not self.fired:
                self.fired = True
                room.instances.append(spawned)

    ex = _Exec()
    original = _Inst(ex, {"keyboard_press": {"space": {"actions": [{}]}}})
    room.instances.append(original)

    runner.handle_keyboard_press(pygame.K_SPACE)

    # The original was iterated and got the key; the spawned instance was added
    # mid-iteration and must NOT be visited this frame (snapshot), so it has no
    # key recorded — proving the loop did not run away over new instances.
    assert "space" in original.keys_pressed
    assert "space" not in spawned.keys_pressed
    assert spawned in room.instances  # it was still added, just deferred
