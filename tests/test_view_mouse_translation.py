"""L6, docs/FULL_AUDIT_2026-09-07.md: mouse coordinates aren't
view-translated in if_mouse_over/mouse-position expressions.

pygame.mouse.get_pos() (and every MOUSEBUTTONDOWN/UP/MOTION event's
.pos) is in SCREEN space, but instance.x/y and the "Over object"
mouse_check condition compare against ROOM space. With views disabled
(the common case, and every project predating the view system) those
two spaces coincide, so the bug was invisible -- but with a view
enabled and scrolled away from the room's origin, a click or hover was
off by exactly the view's scroll offset.

GameRoom.screen_to_room is the fix: a single helper that inverts
render()'s own `offset = (port_x - view_x, port_y - view_y)`, reused by
every mouse-position call site instead of each one reaching for
pygame.mouse.get_pos()/event.pos raw.
"""
import os
import sys
from pathlib import Path
from unittest.mock import MagicMock, patch

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT))

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")

import pytest
from conftest import skip_without_pygame

pytestmark = skip_without_pygame


def _room(views_enabled=False, views=None):
    from runtime.game_runner import GameRoom
    room_data = {"width": 800, "height": 600}
    if views_enabled:
        room_data["views_enabled"] = True
        room_data["views"] = views or {}
    return GameRoom("test_room", room_data, action_executor=None)


def _view(view_x=0, view_y=0, view_w=400, view_h=300,
          port_x=0, port_y=0, port_w=400, port_h=300, visible=True):
    return {
        "visible": visible,
        "view_x": view_x, "view_y": view_y, "view_w": view_w, "view_h": view_h,
        "port_x": port_x, "port_y": port_y, "port_w": port_w, "port_h": port_h,
    }


# ---------------------------------------------------------------------------
# GameRoom.screen_to_room -- pure unit tests
# ---------------------------------------------------------------------------

class TestScreenToRoom:
    def test_views_disabled_is_the_identity_transform(self):
        room = _room(views_enabled=False)
        assert room.screen_to_room(123, 456) == (123, 456)

    def test_views_enabled_but_none_visible_is_the_identity_transform(self):
        room = _room(views_enabled=True, views={
            "view_0": _view(view_x=500, view_y=300, visible=False),
        })
        assert room.screen_to_room(10, 10) == (10, 10)

    def test_scrolled_view_offsets_a_point_inside_its_port(self):
        # offset = (port_x - view_x, port_y - view_y) = (0 - 500, 0 - 300)
        # room = screen - offset = screen + (500, 300)
        room = _room(views_enabled=True, views={
            "view_0": _view(view_x=500, view_y=300, port_x=0, port_y=0,
                             port_w=400, port_h=300),
        })
        assert room.screen_to_room(110, 110) == (610, 410)

    def test_unscrolled_view_is_still_the_identity_transform(self):
        room = _room(views_enabled=True, views={
            "view_0": _view(view_x=0, view_y=0, port_x=0, port_y=0),
        })
        assert room.screen_to_room(50, 60) == (50, 60)

    def test_offset_viewport_position_is_accounted_for_too(self):
        # A second viewport, drawn starting at screen (400, 0), showing
        # room content starting at world (0, 0) -- port_x - view_x = 400.
        room = _room(views_enabled=True, views={
            "view_0": _view(view_x=0, view_y=0, port_x=400, port_y=0,
                             port_w=400, port_h=300),
        })
        assert room.screen_to_room(450, 50) == (50, 50)

    def test_point_outside_every_port_is_returned_unchanged(self):
        room = _room(views_enabled=True, views={
            "view_0": _view(view_x=500, view_y=300, port_x=0, port_y=0,
                             port_w=400, port_h=300),
        })
        # (900, 900) is outside the only visible port (0,0,400,300).
        assert room.screen_to_room(900, 900) == (900, 900)

    def test_matches_the_first_port_that_contains_the_point(self):
        room = _room(views_enabled=True, views={
            "view_0": _view(view_x=1000, view_y=0, port_x=0, port_y=0,
                             port_w=200, port_h=200),
            "view_1": _view(view_x=2000, view_y=0, port_x=200, port_y=0,
                             port_w=200, port_h=200),
        })
        assert room.screen_to_room(50, 50) == (1050, 50)
        assert room.screen_to_room(250, 50) == (2050, 50)


# ---------------------------------------------------------------------------
# mouse_check "Over object" -- integration through ActionExecutor
# ---------------------------------------------------------------------------

def _instance(x, y):
    import types
    inst = types.SimpleNamespace(x=x, y=y)
    inst.sprite = types.SimpleNamespace(
        origin_x=0, origin_y=0, bbox_left=0, bbox_top=0, bbox_right=32, bbox_bottom=32,
    )
    return inst


class TestOverObjectWithScrolledView:
    def test_over_object_translates_screen_mouse_into_room_space(self, monkeypatch):
        import pygame
        pygame.init()
        from runtime.action_executor import ActionExecutor

        monkeypatch.setattr(pygame.mouse, "get_pressed", lambda *a, **k: (0, 0, 0))
        monkeypatch.setattr(pygame.mouse, "get_pos", lambda: (110, 110))  # screen space

        room = _room(views_enabled=True, views={
            "view_0": _view(view_x=500, view_y=300, port_x=0, port_y=0,
                             port_w=400, port_h=300),
        })
        runner = MagicMock(current_room=room)
        ex = ActionExecutor(game_runner=runner)

        # Screen (110, 110) maps to room (610, 410) under this scrolled
        # view; the instance sits exactly there.
        inst = _instance(x=610, y=410)
        assert ex._evaluate_if_condition(inst, "mouse_check", {"check": "Over object"}) is True

    def test_the_fixture_genuinely_depends_on_translation(self, monkeypatch):
        """Same screen point and instance position as above, but without a
        game_runner (no translation happens) -- must NOT match, proving the
        positive case above isn't a coincidence."""
        import pygame
        pygame.init()
        from runtime.action_executor import ActionExecutor

        monkeypatch.setattr(pygame.mouse, "get_pressed", lambda *a, **k: (0, 0, 0))
        monkeypatch.setattr(pygame.mouse, "get_pos", lambda: (110, 110))

        ex = ActionExecutor(game_runner=None)
        inst = _instance(x=610, y=410)
        assert ex._evaluate_if_condition(inst, "mouse_check", {"check": "Over object"}) is False


# ---------------------------------------------------------------------------
# input_handler's three dispatchers -- instance.mouse_x/mouse_y end up in
# room space, not raw screen space, when a view is scrolled.
# ---------------------------------------------------------------------------

def _runner_with_room(room):
    with patch('runtime.game_runner.pygame'):
        with patch('runtime.game_runner.load_all_plugins'):
            from runtime.game_runner import GameRunner
            r = GameRunner.__new__(GameRunner)
            r.current_room = room
            r._thymio_mouse_presses = {}
            return r


def _mock_instance(events):
    inst = MagicMock()
    inst.object_data = {'events': events}
    inst.is_thymio = False
    inst.action_executor = MagicMock()
    return inst


class TestInputHandlerMouseTranslation:
    def test_handle_mouse_press_sets_room_space_coordinates(self):
        room = _room(views_enabled=True, views={
            "view_0": _view(view_x=500, view_y=300, port_x=0, port_y=0,
                             port_w=400, port_h=300),
        })
        room.instances = []
        runner = _runner_with_room(room)
        inst = _mock_instance({'mouse_left_press': {'actions': []}})
        room.instances = [inst]

        runner.handle_mouse_press(1, (110, 110))

        assert (inst.mouse_x, inst.mouse_y) == (610, 410)

    def test_handle_mouse_motion_sets_room_space_coordinates(self):
        room = _room(views_enabled=True, views={
            "view_0": _view(view_x=500, view_y=300, port_x=0, port_y=0,
                             port_w=400, port_h=300),
        })
        room.instances = []
        runner = _runner_with_room(room)
        inst = _mock_instance({'mouse_move': {'actions': []}})
        room.instances = [inst]

        runner.handle_mouse_motion((110, 110))

        assert (inst.mouse_x, inst.mouse_y) == (610, 410)

    def test_views_disabled_still_gets_raw_coordinates(self):
        """No regression for the overwhelmingly common no-views case."""
        room = _room(views_enabled=False)
        room.instances = []
        runner = _runner_with_room(room)
        inst = _mock_instance({'mouse_left_press': {'actions': []}})
        room.instances = [inst]

        runner.handle_mouse_press(1, (10, 20))

        assert (inst.mouse_x, inst.mouse_y) == (10, 20)
