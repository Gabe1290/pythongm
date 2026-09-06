"""The Block World fps harness must keep measuring what it claims to.

`tools/measure_block_world_fps.py` produces the numbers every Block World
performance decision is argued from, so the ways it can quietly lie matter more
than the ways it can crash.

The one that already happened: the first version held the **Up arrow** for its
"moving" condition, which in these samples is bound to `set_look_pitch`, not to
movement. It tilted the camera at the empty sky and measured a 3x "speedup"
that was really a blank screen. Nothing errored; the number was simply wrong.

So these tests pin the two facts that make the harness meaningful -- that it
holds W, and that W is what actually walks in the samples -- rather than
asserting it runs. Running it is a several-minute wall-clock measurement and
belongs in a human's hands, not in the suite.
"""
import ast
import json
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT))

TOOL = REPO_ROOT / "tools" / "measure_block_world_fps.py"
SAMPLES = ("block_world_1", "block_world_2")


def _tool_ast():
    return ast.parse(TOOL.read_text(encoding="utf-8"))


def test_the_harness_exists_and_parses():
    assert TOOL.is_file()
    _tool_ast()


def test_it_holds_w_and_not_an_arrow_key():
    """Parsed, not grepped: a comment mentioning K_w would satisfy a string
    search even if the code posted K_UP, which is exactly the bug this file
    exists for."""
    keys = {node.attr
            for node in ast.walk(_tool_ast())
            if isinstance(node, ast.Attribute)
            and isinstance(node.value, ast.Name)
            and node.value.id == "pygame"
            and node.attr.startswith("K_")}
    assert "K_w" in keys, "the walking condition must hold W"
    assert not keys & {"K_UP", "K_DOWN"}, (
        "Up/Down are set_look_pitch in these samples -- holding one measures "
        "an empty sky, not a moving camera")


def test_w_really_walks_and_up_really_does_not():
    """The reason the harness holds W. If a sample is ever rebound, this fails
    and tells the next reader to revisit the harness instead of silently
    measuring the wrong thing."""
    for sample in SAMPLES:
        path = REPO_ROOT / "samples" / sample / "objects" / "obj_person.json"
        held = json.loads(path.read_text(encoding="utf-8"))["events"]["keyboard"]

        w_actions = [a["action"] for a in held["w"]["actions"]]
        assert "move_and_collide" in w_actions, (
            "%s: W no longer moves the camera" % sample)

        up_actions = [a["action"] for a in held["up"]["actions"]]
        assert "move_and_collide" not in up_actions, (
            "%s: Up now moves -- the harness comment explaining why it avoids "
            "the arrow keys is stale" % sample)


def test_it_discards_warmup_frames_and_measures_against_the_room_speed():
    tree = _tool_ast()
    consts = {t.id: n.value.value
              for n in tree.body if isinstance(n, ast.Assign)
              for t in n.targets
              if isinstance(t, ast.Name) and isinstance(n.value, ast.Constant)}

    assert consts.get("WARMUP", 0) > 0, "steady state needs a warmup discard"

    # The samples really are configured for 30fps -- the target the tool
    # compares against is not a guess. `room_speed` lives in project.json's
    # settings block, NOT on the room side-files: a first draft of this test
    # read `rooms` out of project.json, found it empty (rooms are side-files
    # under rooms/) and passed vacuously against an empty set.
    assert consts.get("TARGET_FPS") == 30
    for sample in SAMPLES:
        settings = json.loads(
            (REPO_ROOT / "samples" / sample / "project.json")
            .read_text(encoding="utf-8"))["settings"]
        assert settings["room_speed"] == 30, (
            "%s runs at %s, so 30 is the wrong target"
            % (sample, settings["room_speed"]))
