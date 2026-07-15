"""match3_2's swap-slide-animation state machine, run through the real
ActionExecutor against the sample's actual event code (not a re-implemented
copy) — pins the forward-slide / flash-and-cascade / revert-slide behavior
described in samples/match3_2/README.md.

Qt-free, pygame-free (uses conftest's import_module_directly to load
action_executor.py without pulling in runtime/game_runner.py's pygame
dependency), so this runs everywhere the rest of the light test suite does.
"""
import json
import random
import sys
from pathlib import Path

from conftest import import_module_directly

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT))
SAMPLE = REPO_ROOT / "samples" / "match3_2"

_action_executor_module = import_module_directly("runtime/action_executor.py")
ActionExecutor = _action_executor_module.ActionExecutor


class MockSound:
    def __init__(self):
        self.played = 0

    def set_volume(self, v):
        pass

    def play(self):
        self.played += 1


class MockGameRunner:
    def __init__(self):
        self.sounds = {"snd_swap": MockSound(), "snd_match": MockSound(),
                        "snd_cascade": MockSound()}


class MockInstance:
    def __init__(self):
        self.object_name = "obj_GridManager"
        self._sound_queue = []
        self.mouse_x = 0
        self.mouse_y = 0
        events = json.loads(
            (SAMPLE / "objects" / "obj_GridManager.json").read_text(encoding="utf-8"))["events"]
        self.object_data = {"events": events}


def _make(seed):
    random.seed(seed)
    ae = ActionExecutor(game_runner=MockGameRunner())
    inst = MockInstance()
    ae.execute_event(inst, "create", inst.object_data["events"])
    return ae, inst


def _click(ae, inst, gx, gy):
    inst.mouse_x = inst.ox + gx * inst.tile + inst.tile / 2
    inst.mouse_y = inst.oy + gy * inst.tile + inst.tile / 2
    ae.execute_event(inst, "mouse_left_press", inst.object_data["events"])


def _step(ae, inst):
    ae.execute_event(inst, "step", inst.object_data["events"])


def test_create_seeds_a_match_free_board():
    ae, inst = _make(seed=1)
    assert inst.find_matches(inst.grid, inst.rows, inst.cols) == set()
    assert inst.cols == inst.rows == 6
    assert inst.sprite_names == ["spr_gem_red", "spr_gem_blue", "spr_gem_green", "spr_gem_yellow"]


def test_matching_swap_slides_flashes_scores_and_plays_sounds():
    ae, inst = _make(seed=1)
    inst.grid[0][0] = 0
    inst.grid[0][1] = 0
    inst.grid[0][2] = 1
    inst.grid[1][2] = 0

    _click(ae, inst, 2, 0)
    _click(ae, inst, 2, 1)

    assert inst.swap_phase == "forward"
    assert inst.pending_marks

    guard = 0
    while inst.swap_off and guard < 100:
        _step(ae, inst)
        guard += 1
    assert inst.flash > 0, "forward slide must arm the flash once it settles"

    guard = 0
    while (inst.flash > 0 or inst.falling or inst.swap_off) and guard < 500:
        _step(ae, inst)
        guard += 1

    assert inst.swap_phase is None
    assert inst.score >= 30  # at least the rigged 3-tile match (3*10)
    assert inst.find_matches(inst.grid, inst.rows, inst.cols) == set(), (
        "board must be fully settled with no leftover matches")
    assert ae.game_runner.sounds["snd_swap"].played == 1
    assert ae.game_runner.sounds["snd_match"].played >= 1


def test_invalid_swap_slides_back_and_restores_the_grid():
    ae, inst = _make(seed=2)
    found = None
    for gy in range(inst.rows):
        for gx in range(inst.cols - 1):
            g = inst.grid
            g[gy][gx], g[gy][gx + 1] = g[gy][gx + 1], g[gy][gx]
            no_match = inst.find_matches(g, inst.rows, inst.cols) == set()
            g[gy][gx], g[gy][gx + 1] = g[gy][gx + 1], g[gy][gx]
            if no_match and g[gy][gx] != g[gy][gx + 1]:
                found = (gx, gy)
                break
        if found:
            break
    assert found, "fixture needs at least one no-match adjacent pair"
    gx, gy = found
    before = [row[:] for row in inst.grid]

    _click(ae, inst, gx, gy)
    _click(ae, inst, gx + 1, gy)
    assert inst.swap_phase == "forward"
    assert not inst.pending_marks

    saw_back_phase = False
    guard = 0
    while (inst.swap_off or inst.swap_phase is not None) and guard < 100:
        _step(ae, inst)
        if inst.swap_phase == "back":
            saw_back_phase = True
        guard += 1

    assert saw_back_phase, "expected a 'back' revert phase for a non-matching swap"
    assert inst.swap_phase is None
    assert inst.grid == before, "grid must be restored after an invalid swap reverts"
    assert inst.score == 0


def test_input_ignored_while_swap_animation_in_flight():
    ae, inst = _make(seed=3)
    gx, gy = 0, 0
    while True:
        g = inst.grid
        g[gy][gx], g[gy][gx + 1] = g[gy][gx + 1], g[gy][gx]
        no_match = inst.find_matches(g, inst.rows, inst.cols) == set()
        g[gy][gx], g[gy][gx + 1] = g[gy][gx + 1], g[gy][gx]
        if no_match and g[gy][gx] != g[gy][gx + 1]:
            break
        gx += 1
        if gx >= inst.cols - 1:
            gx = 0
            gy += 1

    _click(ae, inst, gx, gy)
    _click(ae, inst, gx + 1, gy)
    assert inst.swap_off, "expected the slide to still be in flight"

    _click(ae, inst, 5, 5)  # unrelated click while animating
    assert inst.sel is None, "clicks must be ignored while a swap is animating"


def test_draw_emits_sprite_commands_for_idle_tiles():
    ae, inst = _make(seed=4)
    inst._draw_queue = []
    ae.execute_event(inst, "draw", inst.object_data["events"])
    sprite_cmds = [c for c in inst._draw_queue if c["type"] == "sprite"]
    assert len(sprite_cmds) == inst.cols * inst.rows
    valid_names = set(inst.sprite_names)
    assert all(c["sprite_name"] in valid_names for c in sprite_cmds)
