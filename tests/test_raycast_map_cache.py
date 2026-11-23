"""Per-frame costs that grew with level size (2026-11-23, while sizing a 48 x 48 test level).

* The floor-height and ceiling maps were rebuilt from every instance twice a frame (renderer +
  climbing). They are now reused while no step / ceiling marker changed -- keyed on what the map
  depends on, so a step that moves, changes height or is destroyed still shows the next frame
  (an earlier cache keyed on cell size only left destroyed walls visible, 2026-10-06).
* The micro:bit overlay hook is offered every instance every frame and imported its renderer
  each time; it now returns at once for an instance with no extension state.

64 x 64 test room: 25.1 -> 20.7 ms/frame; 48 x 48: 15.7 -> 13.5. Frames identical to before on
raycast_5, raycast_6 and both perf levels (commit message).
"""
import os
os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
sys.path.insert(0, str(Path(__file__).resolve().parent))

from conftest import skip_without_pygame  # noqa: E402

pytestmark = skip_without_pygame

import pygame  # noqa: E402
pygame.init()

from runtime.game_runner import GameInstance  # noqa: E402
from extensions.raycast_2_5d.heights import build_ceiling_heights, build_floor_heights  # noqa: E402
from test_raycast_view import _room  # noqa: E402
from test_raycast_floor_heights import _step  # noqa: E402
from test_raycast_ceiling_heights import _marker  # noqa: E402

CELL = 32
HIGH = 1000.0


def _floors(room):
    return build_floor_heights(room, CELL, HIGH)[0]


class TestFloorMap:
    def test_reused_while_nothing_changed(self):
        room = _room(320, 320)
        room.instances.append(_step(64, 32, 16))
        first = _floors(room)
        assert _floors(room) is first

    def test_a_moved_step_is_seen(self):
        room = _room(320, 320)
        step = _step(64, 32, 16)
        room.instances.append(step)
        assert _floors(room) == {(2, 1): 16.0}
        step.x = 96
        assert _floors(room) == {(3, 1): 16.0}

    def test_a_new_height_is_seen(self):
        room = _room(320, 320)
        step = _step(64, 32, 16)
        room.instances.append(step)
        _floors(room)
        step.raycast_floor_height = 24.0
        assert _floors(room) == {(2, 1): 24.0}

    def test_a_destroyed_step_is_gone(self):
        room = _room(320, 320)
        step = _step(64, 32, 16)
        room.instances.append(step)
        _floors(room)
        room.instances.remove(step)
        assert _floors(room) == {}

    def test_a_different_limit_rebuilds(self):
        room = _room(320, 320)
        room.instances.append(_step(64, 32, 64))
        assert build_floor_heights(room, CELL, HIGH)[0] == {(2, 1): 64.0}
        assert build_floor_heights(room, CELL, 40.0)[0] == {(2, 1): 40.0}


class TestCeilingMap:
    def _ceil(self, room, floors):
        return build_ceiling_heights(room, CELL, 96.0, floors, 24.0)[0]

    def test_reused_while_nothing_changed(self):
        room = _room(320, 320)
        room.instances.append(_marker(0, 0, 48))
        first = self._ceil(room, {})
        assert self._ceil(room, {}) is first

    def test_the_clamp_follows_the_floor_under_it(self):
        room = _room(320, 320)
        room.instances.append(_marker(0, 0, 40))
        assert self._ceil(room, {}) == {(0, 0): 40.0}
        assert self._ceil(room, {(0, 0): 32.0}) == {(0, 0): 32.0 + 24.0 + 4.0}

    def test_a_lowered_marker_is_seen(self):
        room = _room(320, 320)
        marker = _marker(0, 0, 64)
        room.instances.append(marker)
        self._ceil(room, {})
        marker.raycast_ceiling_height = 40.0
        assert self._ceil(room, {}) == {(0, 0): 40.0}


class TestMicrobitOverlay:
    def test_an_ordinary_instance_never_reaches_the_renderer(self, monkeypatch):
        import extensions.microbit as mb
        import extensions.microbit.renderer as mb_renderer
        called = []
        monkeypatch.setattr(mb_renderer, "draw_overlay", lambda inst, scr: called.append(inst))
        plain = GameInstance("obj_wall", 0, 0, {}, action_executor=None)
        mb._draw_board(plain, pygame.Surface((8, 8)))
        assert called == []
        board = GameInstance("microbit_1", 0, 0, {}, action_executor=None)
        board.extension_state = {"microbit": {"simulator": object()}}
        mb._draw_board(board, pygame.Surface((8, 8)))
        assert called == [board]
