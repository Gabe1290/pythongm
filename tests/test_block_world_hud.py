"""Regression tests for Block World's HUD (Phase 4 Unit 6): the
build_block_world_hud_commands geometry builder (hud.py) and the
draw_block_world_hud macro action that calls it.
"""
import os
import sys
from pathlib import Path

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT))

from conftest import skip_without_pygame

pytestmark = skip_without_pygame

import pygame
pygame.init()
pygame.display.set_mode((1, 1))

from runtime.game_runner import GameInstance  # noqa: E402
from runtime.action_executor import ActionExecutor  # noqa: E402
from events.plugin_loader import load_all_plugins  # noqa: E402
from extensions.block_world.hud import build_block_world_hud_commands  # noqa: E402
from extensions.block_world.state import DEFAULT_HOTBAR  # noqa: E402


def _hud(**overrides):
    kwargs = dict(
        screen_width=640, screen_height=480, hotbar=["stone", "dirt", "brick"],
        selected_index=1, slot_size=40, gap=6, margin_bottom=16,
        back_color="#202020", border_color="#ffffff", selected_color="#ffd040",
        text_color="#ffffff", crosshair_size=12, crosshair_color="#ffffff",
    )
    kwargs.update(overrides)
    return build_block_world_hud_commands(**kwargs)


# ---------------------------------------------------------------------------
# build_block_world_hud_commands
# ---------------------------------------------------------------------------

class TestBuildHudCommands:
    def test_crosshair_is_centred_on_screen(self):
        cmds = _hud(screen_width=640, screen_height=480, crosshair_size=12)
        lines = [c for c in cmds if c["type"] == "line"]
        assert len(lines) == 2
        horiz = next(l for l in lines if l["y1"] == l["y2"])
        vert = next(l for l in lines if l["x1"] == l["x2"])
        assert horiz["y1"] == 240 and (horiz["x1"], horiz["x2"]) == (314, 326)
        assert vert["x1"] == 320 and (vert["y1"], vert["y2"]) == (234, 246)

    def test_one_rectangle_pair_and_one_text_per_slot(self):
        cmds = _hud(hotbar=["stone", "dirt", "brick"])
        rects = [c for c in cmds if c["type"] == "rectangle"]
        texts = [c for c in cmds if c["type"] == "text"]
        assert len(rects) == 6   # fill + border, per slot
        assert len(texts) == 3

    def test_slots_are_centred_as_a_group(self):
        hotbar = list(DEFAULT_HOTBAR)  # 8 slots
        cmds = _hud(hotbar=hotbar, screen_width=640, slot_size=40, gap=6)
        rects = [c for c in cmds if c["type"] == "rectangle" and c.get("filled")]
        total_w = len(hotbar) * 40 + (len(hotbar) - 1) * 6
        expected_x0 = (640 - total_w) / 2.0
        assert rects[0]["x1"] == expected_x0
        last = rects[-1]
        assert last["x2"] == expected_x0 + total_w

    def test_slots_sit_above_the_bottom_margin(self):
        cmds = _hud(screen_height=480, slot_size=40, margin_bottom=16)
        rects = [c for c in cmds if c["type"] == "rectangle"]
        assert rects[0]["y2"] == 480 - 16
        assert rects[0]["y1"] == 480 - 16 - 40

    def test_the_selected_slot_gets_the_selected_color(self):
        cmds = _hud(hotbar=["stone", "dirt", "brick"], selected_index=1,
                    back_color="#202020", selected_color="#ffd040")
        fills = [c for c in cmds if c["type"] == "rectangle" and c.get("filled")]
        assert [f["color"] for f in fills] == ["#202020", "#ffd040", "#202020"]

    def test_out_of_range_selected_index_highlights_nothing(self):
        cmds = _hud(hotbar=["stone", "dirt"], selected_index=99,
                    back_color="#202020", selected_color="#ffd040")
        fills = [c for c in cmds if c["type"] == "rectangle" and c.get("filled")]
        assert all(f["color"] == "#202020" for f in fills)

    def test_labels_are_the_block_type_names_truncated(self):
        cmds = _hud(hotbar=["stone", "diamond_block"])
        texts = [c["text"] for c in cmds if c["type"] == "text"]
        assert texts == ["ston", "diam"]

    def test_empty_hotbar_still_draws_the_crosshair(self):
        cmds = _hud(hotbar=[])
        assert [c["type"] for c in cmds] == ["line", "line"]


# ---------------------------------------------------------------------------
# draw_block_world_hud action
# ---------------------------------------------------------------------------

class MockRunner:
    def __init__(self, window_width=None, window_height=None):
        self.current_room = None
        self.global_variables = {}
        if window_width is not None:
            self.window_width = window_width
        if window_height is not None:
            self.window_height = window_height


def _dispatch(runner, instance, **params):
    ex = ActionExecutor(game_runner=runner)
    load_all_plugins(ex)
    instance.action_executor = ex
    return ex.action_handlers["draw_block_world_hud"](instance, params)


class TestDrawBlockWorldHudAction:
    def test_appends_commands_to_the_draw_queue(self):
        instance = GameInstance("obj_person", 0, 0, {}, action_executor=None)
        _dispatch(MockRunner(window_width=640, window_height=480), instance)
        assert len(instance._draw_queue) > 0
        assert instance._draw_queue[0]["type"] == "line"

    def test_reads_hotbar_index_from_the_instance(self):
        instance = GameInstance("obj_person", 0, 0, {}, action_executor=None)
        instance.hotbar_index = 3
        _dispatch(MockRunner(window_width=640, window_height=480), instance)
        fills = [c for c in instance._draw_queue
                 if c["type"] == "rectangle" and c.get("filled")]
        assert fills[3]["color"] == "#ffd040"   # default selected_color
        assert all(f["color"] == "#202020" for i, f in enumerate(fills) if i != 3)

    def test_defaults_to_slot_zero_when_never_selected(self):
        instance = GameInstance("obj_person", 0, 0, {}, action_executor=None)
        _dispatch(MockRunner(window_width=640, window_height=480), instance)
        fills = [c for c in instance._draw_queue
                 if c["type"] == "rectangle" and c.get("filled")]
        assert fills[0]["color"] == "#ffd040"

    def test_falls_back_to_640x480_with_no_window_size_available(self):
        instance = GameInstance("obj_person", 0, 0, {}, action_executor=None)
        _dispatch(MockRunner(), instance)
        lines = [c for c in instance._draw_queue if c["type"] == "line"]
        vert = next(l for l in lines if l["x1"] == l["x2"])
        assert vert["x1"] == 320   # 640 / 2

    def test_no_game_runner_does_not_raise(self):
        instance = GameInstance("obj_person", 0, 0, {}, action_executor=None)
        from extensions.block_world.handlers import PluginExecutor
        instance.action_executor = None
        PluginExecutor().execute_draw_block_world_hud_action(instance, {})
        assert not hasattr(instance, "_draw_queue")

    def test_appending_twice_does_not_clear_the_first_call(self):
        """_draw_queue is created once, then extended -- a second HUD-ish
        action earlier in the same draw event must not be wiped out."""
        instance = GameInstance("obj_person", 0, 0, {}, action_executor=None)
        instance._draw_queue = [{"type": "text", "text": "score: 0", "x": 0, "y": 0}]
        _dispatch(MockRunner(window_width=640, window_height=480), instance)
        assert instance._draw_queue[0]["text"] == "score: 0"
        assert len(instance._draw_queue) > 1
