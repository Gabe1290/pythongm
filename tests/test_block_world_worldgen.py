"""Regression tests for Block World world authoring: loading a pre-authored
world from a data file (Unit 1) and the committed generator that produces
one (Unit 2).

docs/VOXEL_WORLD_PLAN.md: state.py has said since Phase 1 that "wiring an
actual load path is Phase 3+" -- this is that path.
"""
import json
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

from runtime.game_runner import GameRoom  # noqa: E402
from runtime.action_executor import ActionExecutor  # noqa: E402
from events.plugin_loader import load_all_plugins  # noqa: E402
from extensions.block_world.state import (  # noqa: E402
    BLOCK_TYPES, get_block, iter_blocks, set_block,
)

CELL = 32


class MockRunner:
    def __init__(self, room, project_path=None):
        self.current_room = room
        self.global_variables = {}
        self.project_path = project_path


def _room():
    return GameRoom("worldgen", {"width": 40 * CELL, "height": 40 * CELL},
                    action_executor=None)


def _run(room, action, project_path=None, **params):
    ex = ActionExecutor(game_runner=MockRunner(room, project_path))
    load_all_plugins(ex)

    class _Instance:
        object_name = "obj_person"
        action_executor = None

    instance = _Instance()
    instance.action_executor = ex
    return ex.action_handlers[action](instance, params)


# ---------------------------------------------------------------------------
# load_block_world (Unit 1)
# ---------------------------------------------------------------------------

class TestLoadBlockWorld:
    def test_loads_a_valid_file(self, tmp_path):
        (tmp_path / "blocks").mkdir()
        data = [
            {"x": 0, "y": 0, "z": 0, "type": "stone"},
            {"x": 1, "y": 0, "z": 0, "type": "dirt"},
        ]
        (tmp_path / "blocks" / "room1.json").write_text(json.dumps(data))

        room = _room()
        _run(room, "load_block_world", project_path=tmp_path,
             data_file="blocks/room1.json")
        assert get_block(room, 0, 0, 0) == "stone"
        assert get_block(room, 1, 0, 0) == "dirt"

    def test_a_second_load_replaces_the_first(self, tmp_path):
        (tmp_path / "a.json").write_text(json.dumps(
            [{"x": 0, "y": 0, "z": 0, "type": "stone"}]))
        (tmp_path / "b.json").write_text(json.dumps(
            [{"x": 5, "y": 5, "z": 5, "type": "brick"}]))

        room = _room()
        _run(room, "load_block_world", project_path=tmp_path, data_file="a.json")
        _run(room, "load_block_world", project_path=tmp_path, data_file="b.json")
        assert get_block(room, 0, 0, 0) is None, "the first load should not linger"
        assert get_block(room, 5, 5, 5) == "brick"

    def test_missing_data_file_parameter_is_a_noop(self, tmp_path):
        room = _room()
        set_block(room, 9, 9, 9, "stone")
        _run(room, "load_block_world", project_path=tmp_path, data_file="")
        assert get_block(room, 9, 9, 9) == "stone", "existing world must survive a no-op call"

    def test_nonexistent_file_is_a_noop(self, tmp_path):
        room = _room()
        _run(room, "load_block_world", project_path=tmp_path,
             data_file="does_not_exist.json")
        assert list(iter_blocks(room)) == []

    def test_malformed_json_is_a_noop(self, tmp_path):
        (tmp_path / "bad.json").write_text("{not valid json")
        room = _room()
        _run(room, "load_block_world", project_path=tmp_path, data_file="bad.json")
        assert list(iter_blocks(room)) == []

    def test_an_unknown_block_type_rejects_the_whole_file(self, tmp_path):
        """load_block_list is atomic (see its own docstring) -- a bad entry
        must not leave a half-loaded world."""
        data = [
            {"x": 0, "y": 0, "z": 0, "type": "stone"},
            {"x": 1, "y": 0, "z": 0, "type": "unobtainium"},
        ]
        (tmp_path / "room.json").write_text(json.dumps(data))
        room = _room()
        _run(room, "load_block_world", project_path=tmp_path, data_file="room.json")
        assert list(iter_blocks(room)) == [], "a bad entry must reject the whole file"

    def test_no_project_path_is_a_noop(self):
        room = _room()
        _run(room, "load_block_world", project_path=None, data_file="blocks/room1.json")
        assert list(iter_blocks(room)) == []

    def test_no_current_room_is_a_noop(self, tmp_path):
        (tmp_path / "room.json").write_text(json.dumps(
            [{"x": 0, "y": 0, "z": 0, "type": "stone"}]))
        ex = ActionExecutor(game_runner=MockRunner(None, tmp_path))

        class _Instance:
            object_name = "obj_person"
            action_executor = None

        instance = _Instance()
        instance.action_executor = ex
        load_all_plugins(ex)
        ex.action_handlers["load_block_world"](instance, {"data_file": "room.json"})
        # must not raise


# ---------------------------------------------------------------------------
# tools/gen_block_world_demo.py (Unit 2)
# ---------------------------------------------------------------------------

def _generator():
    import importlib.util
    path = REPO_ROOT / "tools" / "gen_block_world_demo.py"
    spec = importlib.util.spec_from_file_location("gen_block_world_demo", path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class TestGeneratedDemoWorld:
    def test_output_matches_the_committed_file(self):
        """Pins the generator against its own checked-in output, the same
        discipline tools/gen_raycast_3_maze.py's rooms are held to --
        regenerating must reproduce it byte-for-byte (content, not the
        trailing newline/formatting choices, which json.dumps makes
        deterministic anyway)."""
        gen = _generator()
        committed = json.loads(gen.OUT.read_text(encoding="utf-8"))
        assert gen.to_block_list(gen.build_room()) == committed

    def test_every_block_type_used_is_real(self):
        gen = _generator()
        for entry in json.loads(gen.OUT.read_text(encoding="utf-8")):
            assert entry["type"] in BLOCK_TYPES, entry["type"]

    def test_no_duplicate_positions(self):
        """A generator bug (two features writing the same cell) would
        silently drop one -- to_block_list's dict-keyed construction can't
        detect it after the fact, so check the pre-flattened working dict."""
        gen = _generator()
        blocks = gen.build_room()
        flat = gen.to_block_list(blocks)
        assert len(flat) == len(blocks)

    def test_the_wall_is_taller_than_one_block(self):
        """The whole reason WALL_HEIGHT isn't 1 -- see the module docstring:
        a one-block wall reads as a climbable step, not a wall."""
        gen = _generator()
        assert gen.WALL_HEIGHT > 1

    def test_the_staircase_rises_one_block_per_step(self):
        """Matches MAX_STEP_UP (Unit 4/5) -- each step must be reachable
        from the previous one without a taller rise than that."""
        gen = _generator()
        blocks = gen.build_room()
        stair_x = gen.GRID // 2
        tops = []
        for i in range(gen.STEP_COUNT):
            y = gen.STAIR_START_Y + i
            zs = [z for (x, yy, z) in blocks if x == stair_x and yy == y]
            assert zs, f"no step block at row {i}"
            tops.append(max(zs))
        footings = [1] + [t + 1 for t in tops]  # 1 = the floor's own footing (stack_top 0, +1)
        for prev, cur in zip(footings, footings[1:]):
            assert cur - prev == 1, f"step rises {cur - prev}, not 1: {footings}"

    def test_load_block_world_can_actually_load_it(self, tmp_path):
        """End-to-end: the generator's output is exactly what Unit 1's
        action expects, not just structurally similar to it."""
        gen = _generator()
        (tmp_path / "demo.json").write_text(gen.OUT.read_text(encoding="utf-8"))
        room = _room()
        _run(room, "load_block_world", project_path=tmp_path, data_file="demo.json")
        assert get_block(room, 0, 0, 0) == "grass"
        assert get_block(room, 0, 0, 1) == "cobble"
        stair_x = gen.GRID // 2
        assert get_block(room, stair_x, gen.STAIR_START_Y, 1) == "wood_plank"


# ---------------------------------------------------------------------------
# tools/gen_block_world_1_room.py (Unit 7 -- the block_world_1 sample world)
# ---------------------------------------------------------------------------

def _sample_generator():
    import importlib.util
    path = REPO_ROOT / "tools" / "gen_block_world_1_room.py"
    spec = importlib.util.spec_from_file_location("gen_block_world_1_room", path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class TestSampleRoomGenerator:
    def test_output_matches_the_committed_file(self):
        gen = _sample_generator()
        committed = json.loads(gen.OUT.read_text(encoding="utf-8"))
        assert gen.to_block_list(gen.build_room()) == committed

    def test_every_block_type_used_is_real(self):
        gen = _sample_generator()
        for entry in json.loads(gen.OUT.read_text(encoding="utf-8")):
            assert entry["type"] in BLOCK_TYPES, entry["type"]

    def test_no_duplicate_positions(self):
        gen = _sample_generator()
        blocks = gen.build_room()
        assert len(gen.to_block_list(blocks)) == len(blocks)

    def test_exactly_one_goal_marker(self):
        gen = _sample_generator()
        golds = [pos for pos, t in gen.build_room().items() if t == "gold_block"]
        assert len(golds) == 1
        assert golds[0] == (gen.TERRACE_CX, gen.TERRACE_CY, gen.TERRACE_Z)

    def test_the_staircase_rises_one_block_per_step(self):
        gen = _sample_generator()
        blocks = gen.build_room()
        tops = []
        for i in range(gen.STEP_COUNT):
            x = gen.STAIR_X0 + i
            zs = [z for (xx, y, z) in blocks if xx == x and y == gen.STAIR_Y]
            assert zs, f"no step block at step {i}"
            tops.append(max(zs))
        footings = [1] + [t + 1 for t in tops]   # 1 = the floor's own footing
        for prev, cur in zip(footings, footings[1:]):
            assert cur - prev == 1, f"step rises {cur - prev}, not 1: {footings}"

    def test_the_terrace_is_level_with_the_top_step(self):
        """Same TOP height as the last step -- so walking from the final
        step onto the terrace is flat (footing-continuous), not one more
        rise on top of the climb the staircase already accounted for."""
        gen = _sample_generator()
        blocks = gen.build_room()
        last_step_top = max(z for (x, y, z) in blocks
                            if x == gen.STAIR_X0 + gen.STEP_COUNT - 1 and y == gen.STAIR_Y)
        assert gen.TERRACE_Z == last_step_top, \
            "terrace top should be level with the top step, not another rise above it"

    def test_start_position_is_clear_floor_not_inside_a_wall_or_the_stairs(self):
        gen = _sample_generator()
        blocks = gen.build_room()
        assert blocks.get((gen.START_X, gen.START_Y, 0)) == "grass"
        assert not any(x == gen.START_X and y == gen.START_Y and z > 0
                       for (x, y, z) in blocks)

    def test_start_is_within_the_perimeter_and_the_goal_is_reachable_by_walking(self):
        """The whole design constraint this sample leans on: reaching the
        goal must be possible by walking a pre-built staircase, not by
        placing blocks with exact geometry -- see the generator's own
        module docstring for why. Pin the geometric facts that make it
        true: the goal sits within the walled interior, and every step
        plus the terrace all sit on the SAME x=STAIR_X0.. column path the
        player can walk in a straight line from the entrance."""
        gen = _sample_generator()
        assert 0 < gen.START_X < gen.GRID - 1
        assert 0 < gen.TERRACE_CX < gen.GRID - 1
        assert 0 < gen.TERRACE_CY < gen.GRID - 1
        assert gen.STAIR_Y == gen.START_Y == gen.TERRACE_CY, \
            "stairs, start and terrace should share one straight approach row"

    def test_load_block_world_can_actually_load_it(self, tmp_path):
        gen = _sample_generator()
        (tmp_path / "room.json").write_text(gen.OUT.read_text(encoding="utf-8"))
        room = _room()
        _run(room, "load_block_world", project_path=tmp_path, data_file="room.json")
        assert get_block(room, gen.TERRACE_CX, gen.TERRACE_CY, gen.TERRACE_Z) == "gold_block"
        assert get_block(room, gen.START_X, gen.START_Y, 0) == "grass"
