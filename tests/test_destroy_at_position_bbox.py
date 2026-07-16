"""destroy_at_position uses GM bounding-box containment (maze_4 finding #13).

"In room16 the explosions do not destroy the walls so the level is impossible
to get out of." maze_4's explosion clears a 3x3 tile area by firing
destroy_at_position at points 16px INSIDE the surrounding walls (a classic GM
jump-away/destroy/jump-back pattern). destroy_at_position matched only
instances sitting within 1px of their ORIGIN, so those interior points hit
nothing and the bombs never opened the walls.

GM's action_kill_position (position_destroy) destroys every instance whose
bounding box CONTAINS the point. The radius==0 case now does that; radius>0
keeps the Euclidean-distance behavior.
"""
from types import SimpleNamespace

import pytest

from conftest import skip_without_pygame

pytestmark = skip_without_pygame


class _Inst:
    def __init__(self, name, x, y, w=32, h=32):
        self.object_name = name
        self.x = float(x)
        self.y = float(y)
        self._cached_width = w
        self._cached_height = h
        self.sprite = None
        self._cached_object_data = {}
        self.to_destroy = False


def _executor(instances):
    from runtime.action_executor import ActionExecutor
    ex = ActionExecutor()
    ex.game_runner = SimpleNamespace(
        current_room=SimpleNamespace(instances=list(instances)),
        global_variables={})
    return ex


def test_point_inside_bbox_but_off_origin_destroys():
    """A wall at (32, 0) sized 32x32; a destroy point at (48, 16) is inside its
    bbox but 16px off its origin — the exact case the explosion relied on."""
    wall = _Inst("wall", 32, 0)
    caller = _Inst("bomb", 0, 0)
    ex = _executor([wall])
    ex.execute_destroy_at_position_action(caller, {"x": "48", "y": "16"})
    assert wall.to_destroy is True


def test_point_outside_bbox_is_spared():
    wall = _Inst("wall", 32, 0)
    ex = _executor([wall])
    ex.execute_destroy_at_position_action(_Inst("bomb", 0, 0), {"x": "80", "y": "16"})
    assert wall.to_destroy is False


def test_exact_origin_still_destroys_backward_compat():
    """The pre-existing behavior (target sitting at the point) still works —
    the origin is inside its own bbox."""
    target = _Inst("obj_target", 100, 200)
    ex = _executor([target])
    ex.execute_destroy_at_position_action(_Inst("bomb", 0, 0),
                                          {"x": "100", "y": "200", "object": "obj_target"})
    assert target.to_destroy is True


def test_explosion_3x3_pattern_clears_surrounding_walls():
    """The maze_4 explosion create-event pattern: jump -200, nine
    destroy_at_position at +184/+216/+248 (net -16/+16/+48 from origin), jump
    back +200. Placed on a wall grid, it should clear the 3x3 block of walls
    around it (every point lands inside a wall bbox)."""
    # 3x3 block of 32px walls with top-left at (0, 0)
    walls = [_Inst("wall", gx * 32, gy * 32) for gx in range(3) for gy in range(3)]
    bomb = _Inst("explosion", 32, 32)      # centre wall
    ex = _executor(walls)

    def dap(px, py):
        ex.execute_destroy_at_position_action(
            bomb, {"x": str(px), "y": str(py), "relative": True})

    # jump -200 then the nine interior points then jump +200 — emulate by
    # firing at the net offsets the create event resolves to.
    for ox in (-16, 16, 48):
        for oy in (-16, 16, 48):
            dap(ox, oy)
    destroyed = sum(1 for w in walls if w.to_destroy)
    # the centre and its neighbours all fall inside the swept area
    assert destroyed >= 8, f"only {destroyed}/9 walls cleared"


def test_radius_mode_unchanged():
    """radius > 0 still does a Euclidean-distance sweep (not bbox)."""
    near = _Inst("wall", 40, 0)     # 40px from the point
    far = _Inst("wall", 200, 0)
    ex = _executor([near, far])
    ex.execute_destroy_at_position_action(
        _Inst("bomb", 0, 0), {"x": "0", "y": "0", "radius": "64"})
    assert near.to_destroy is True
    assert far.to_destroy is False
