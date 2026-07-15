"""match3_3's special-tile / move-limit / level-progression logic, run
through the real ActionExecutor against the sample's actual event code
(not a re-implemented copy) — mirrors test_match3_2_swap_animation.py's
approach. Pins the mechanics described in samples/match3_3/README.md:
4-run -> row/col special, 5+-run -> color-bomb special, single-pass
(non-recursive) activation, move-limit loss + retry, and level-advance
room switching via self.goto_room_target.

Qt-free, pygame-free (import_module_directly avoids game_runner.py's
pygame dependency).
"""
import json
import random
import sys
from pathlib import Path

from conftest import import_module_directly

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT))
SAMPLE = REPO_ROOT / "samples" / "match3_3"

_action_executor_module = import_module_directly("runtime/action_executor.py")
ActionExecutor = _action_executor_module.ActionExecutor


class MockSound:
    def __init__(self):
        self.played = 0

    def set_volume(self, v):
        pass

    def play(self):
        self.played += 1


SOUND_NAMES = ("snd_swap", "snd_match", "snd_cascade", "snd_special", "snd_level_up")


class MockRoom:
    def __init__(self, name):
        self.name = name


class MockGameRunner:
    def __init__(self, room_name="rm_level1"):
        self.sounds = {name: MockSound() for name in SOUND_NAMES}
        self.current_room = MockRoom(room_name)


class MockInstance:
    def __init__(self):
        self.object_name = "obj_GridManager"
        self._sound_queue = []
        self.mouse_x = 0
        self.mouse_y = 0
        self.goto_room_target = None
        self.restart_room_flag = False
        events = json.loads(
            (SAMPLE / "objects" / "obj_GridManager.json").read_text(encoding="utf-8"))["events"]
        self.object_data = {"events": events}


def _make(seed, room_name="rm_level1"):
    random.seed(seed)
    ae = ActionExecutor(game_runner=MockGameRunner(room_name))
    inst = MockInstance()
    ae.execute_event(inst, "create", inst.object_data["events"])
    return ae, inst


def _click(ae, inst, gx, gy):
    inst.mouse_x = inst.ox + gx * inst.tile + inst.tile / 2
    inst.mouse_y = inst.oy + gy * inst.tile + inst.tile / 2
    ae.execute_event(inst, "mouse_left_press", inst.object_data["events"])


def _step(ae, inst):
    ae.execute_event(inst, "step", inst.object_data["events"])


def _settle(ae, inst, cap=500):
    guard = 0
    while (inst.flash > 0 or inst.falling or inst.swap_off) and guard < cap:
        _step(ae, inst)
        guard += 1
    return guard


def test_create_sets_level_config_from_room_name():
    ae, inst = _make(seed=1, room_name="rm_level2")
    assert inst.level_num == 2
    assert inst.target == 500
    assert inst.moves == 18
    assert inst.room_name == "rm_level2"


def test_four_in_a_row_creates_a_row_or_col_special():
    ae, inst = _make(seed=1)
    inst.grid[0][0] = 0
    inst.grid[0][1] = 0
    inst.grid[0][2] = 0
    inst.grid[0][3] = 1
    inst.grid[1][3] = 0

    _click(ae, inst, 3, 0)
    _click(ae, inst, 3, 1)
    assert inst.pending_marks and len(inst.pending_marks) == 4

    guard = 0
    while inst.swap_off and guard < 100:
        _step(ae, inst)
        guard += 1
    _settle(ae, inst)

    assert inst.special, "expected a special tile from the 4-run"
    kinds = {v[0] for v in inst.special.values()}
    assert kinds <= {"row", "col"}
    assert inst.score == 40


def test_five_in_a_row_creates_a_color_bomb():
    ae, inst = _make(seed=2)
    for xx in range(4):
        inst.grid[0][xx] = 0
    inst.grid[0][4] = 1
    inst.grid[1][4] = 0

    _click(ae, inst, 4, 0)
    _click(ae, inst, 4, 1)
    assert inst.pending_marks and len(inst.pending_marks) == 5

    guard = 0
    while inst.swap_off and guard < 100:
        _step(ae, inst)
        guard += 1
    _settle(ae, inst)

    kinds = {v[0] for v in inst.special.values()}
    assert "color" in kinds
    assert inst.score == 50


def test_activating_a_row_special_clears_the_whole_row():
    ae, inst = _make(seed=3)
    inst.special[(2, 3)] = ("row",)
    color = 2
    inst.grid[3][2] = color
    inst.grid[2][2] = color
    inst.grid[4][2] = color
    before_score = inst.score

    marks, runs = inst.find_matches(inst.grid, inst.rows, inst.cols)
    assert (2, 3) in marks, "fixture must catch the special tile in a real match"
    inst.marked = marks
    inst.marked_runs = runs
    inst.flash = 1
    _step(ae, inst)

    assert inst.score - before_score >= 60, (
        f"expected a full 6-tile row clear, got +{inst.score - before_score}")
    assert ae.game_runner.sounds["snd_special"].played >= 1


def test_move_only_spent_on_a_matching_swap():
    ae, inst = _make(seed=4)
    start_moves = inst.moves
    # Find a non-matching adjacent pair.
    found = None
    for gy in range(inst.rows):
        for gx in range(inst.cols - 1):
            g = inst.grid
            g[gy][gx], g[gy][gx + 1] = g[gy][gx + 1], g[gy][gx]
            no_match = inst.find_matches(g, inst.rows, inst.cols)[0] == set()
            g[gy][gx], g[gy][gx + 1] = g[gy][gx + 1], g[gy][gx]
            if no_match and g[gy][gx] != g[gy][gx + 1]:
                found = (gx, gy)
                break
        if found:
            break
    gx, gy = found
    _click(ae, inst, gx, gy)
    _click(ae, inst, gx + 1, gy)
    assert inst.moves == start_moves, "an invalid swap must not cost a move"


def test_move_limit_loss_and_click_to_retry():
    ae, inst = _make(seed=5)
    inst.moves = 1
    inst.target = 10 ** 9
    inst.grid[0][0] = 0
    inst.grid[0][1] = 0
    inst.grid[0][2] = 1
    inst.grid[1][2] = 0

    _click(ae, inst, 2, 0)
    _click(ae, inst, 2, 1)
    assert inst.moves == 0
    _settle(ae, inst)

    assert inst.lost
    assert not inst.restart_room_flag
    _click(ae, inst, 0, 0)
    assert inst.restart_room_flag


def test_reaching_target_sets_goto_room_target_to_next_level():
    ae, inst = _make(seed=6, room_name="rm_level1")
    inst.target = 10
    inst.grid[0][0] = 0
    inst.grid[0][1] = 0
    inst.grid[0][2] = 1
    inst.grid[1][2] = 0

    _click(ae, inst, 2, 0)
    _click(ae, inst, 2, 1)
    _settle(ae, inst)

    assert inst.goto_room_target == "rm_level2"
    assert not inst.won
    assert ae.game_runner.sounds["snd_level_up"].played == 1


def test_reaching_target_on_final_level_sets_won():
    ae, inst = _make(seed=7, room_name="rm_level3")
    inst.target = 10
    inst.grid[0][0] = 0
    inst.grid[0][1] = 0
    inst.grid[0][2] = 1
    inst.grid[1][2] = 0

    _click(ae, inst, 2, 0)
    _click(ae, inst, 2, 1)
    _settle(ae, inst)

    assert inst.won
    assert inst.goto_room_target is None
