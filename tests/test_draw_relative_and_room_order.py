"""maze_4 playtest findings #7/#8 — room play order + relative HUD draws.

#8 "Score and lives are not displayed at bottom of room": controller_main's
draw event uses GM's `relative` checkbox (coordinates offset from the instance,
which sits at (0, 480) — the bottom strip), but draw_score / draw_text /
draw_lives ignored `relative` and drew at absolute (300,4)/(8,4)/(70,4), buried
in the top wall row. draw_lives additionally read only a `sprite` parameter
while GM's action_draw_life_images (and the GMK importer) call it `image`, so
the lives images resolved to "" and drew nothing at all.

#7 "wrong level order": the importer built the rooms dict in the .gmk's play
order but never wrote an explicit `room_order`, leaving the runtime to rely on
JSON key order (fragile — any tool re-sorting keys scrambles progression).
Note maze_4's own play order genuinely IS room_start, room14, room13, ...
(three descending runs) — calibrated against maze_1/maze_3/treasure, which all
parse in their known-correct ascending order, so this is the original author's
ordering, faithfully imported.
"""
import json
import sys
import tempfile
from types import SimpleNamespace
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT))

from conftest import skip_without_pygame

pytestmark = skip_without_pygame


# ---------------------------------------------------------------------------
# relative draw actions (runtime)
# ---------------------------------------------------------------------------

def _hud_instance(x=0, y=480):
    with patch('runtime.game_runner.pygame'), patch('runtime.game_runner.load_all_plugins'):
        from runtime.game_runner import GameInstance
        return GameInstance("controller_main", x, y, {}, MagicMock())


def _executor():
    from runtime.action_executor import ActionExecutor
    ex = ActionExecutor()
    ex.game_runner = SimpleNamespace(score=0, lives=3, draw_color=None,
                                     global_variables={})
    return ex


def test_draw_score_relative_offsets_from_instance():
    ctrl = _hud_instance()
    ex = _executor()
    ex.execute_draw_score_action(
        ctrl, {"x": "300", "y": "4", "caption": "Score: ", "relative": True})
    cmd = ctrl._draw_queue[-1]
    assert (cmd["x"], cmd["y"]) == (300, 484)        # bottom strip, not (300, 4)
    assert cmd["text"] == "Score: 0"


def test_draw_score_absolute_unchanged():
    ctrl = _hud_instance()
    ex = _executor()
    ex.execute_draw_score_action(ctrl, {"x": "300", "y": "4"})
    cmd = ctrl._draw_queue[-1]
    assert (cmd["x"], cmd["y"]) == (300, 4)


def test_draw_text_relative_offsets_from_instance():
    ctrl = _hud_instance()
    ex = _executor()
    ex.execute_draw_text_action(
        ctrl, {"text": "Lives:", "x": "8", "y": "4", "relative": True})
    cmd = ctrl._draw_queue[-1]
    assert (cmd["x"], cmd["y"]) == (8.0, 484.0)


def test_draw_lives_relative_and_image_alias():
    """GM calls the lives sprite argument `image`; the handler read only
    `sprite`, so imported HUDs drew zero lives images."""
    ctrl = _hud_instance()
    ex = _executor()
    ex.execute_draw_lives_action(
        ctrl, {"x": "70", "y": "4", "image": "sprite_lives", "relative": True})
    cmd = ctrl._draw_queue[-1]
    assert (cmd["x"], cmd["y"]) == (70, 484)
    assert cmd["sprite"] == "sprite_lives"
    assert cmd["count"] == 3


def test_draw_lives_sprite_param_still_works():
    ctrl = _hud_instance()
    ex = _executor()
    ex.execute_draw_lives_action(ctrl, {"x": "0", "y": "0", "sprite": "spr_heart"})
    assert ctrl._draw_queue[-1]["sprite"] == "spr_heart"


# ---------------------------------------------------------------------------
# room_order emission (importer)
# ---------------------------------------------------------------------------

def _import(gmk_name):
    from importers.gmk_importer import import_gmk_detailed
    out = Path(tempfile.mkdtemp(prefix="room_order_")) / "import"
    import_gmk_detailed(str(REPO_ROOT / "samples" / gmk_name), str(out))
    return json.loads((out / "project.json").read_text(encoding="utf-8"))


def test_room_order_emitted_and_faithful_maze1():
    proj = _import("maze_1.gmk")
    assert proj["room_order"] == ["room0", "room1"]


def test_room_order_emitted_and_faithful_maze4():
    """maze_4's genuine authored order — room_start then three descending
    runs. Calibrated: maze_1/maze_3/treasure all parse in their known-correct
    ascending order, so this is the original game's ordering, not a parse bug."""
    proj = _import("maze_4.gmk")
    order = proj["room_order"]
    assert order[0] == "room_start"
    assert order[1:4] == ["room14", "room13", "room12"]
    assert len(order) == 21
    # and it matches the rooms dict's insertion order (belt and braces)
    assert order == list(proj["assets"]["rooms"].keys())
