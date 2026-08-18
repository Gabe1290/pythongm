"""raycast_4's exit must not look like a key.

Playtest report: "the keys and the gate have the same sprite". Both `obj_goal`
and `obj_key` pointed at `spr_key`, so in a level whose whole task is "find
three keys, then find the gate", the one object that must not look like a key
was drawn as one.

Guards the fix and, more usefully, the general shape of it: in a sample built
around telling objects apart, two objects sharing art is a content bug that no
amount of engine testing would catch.
"""
import json
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT))

SAMPLE = REPO_ROOT / "samples" / "raycast_4"


def _project():
    return json.loads((SAMPLE / "project.json").read_text(encoding="utf-8"))


def test_the_gate_and_the_key_use_different_sprites():
    objects = _project()["assets"]["objects"]
    gate = objects["obj_goal"]["sprite"]
    key = objects["obj_key"]["sprite"]
    assert gate != key, \
        "obj_goal and obj_key share sprite %r -- the exit looks like a key" % gate


def test_the_side_file_agrees_with_the_embedded_copy():
    """Samples carry object definitions twice: embedded in project.json and as
    objects/<name>.json. Updating only one is a standing trap in this repo --
    the runtime and the IDE do not always read the same copy."""
    embedded = _project()["assets"]["objects"]["obj_goal"]["sprite"]
    side = json.loads(
        (SAMPLE / "objects" / "obj_goal.json").read_text(encoding="utf-8"))["sprite"]
    assert embedded == side == "spr_gate"


def test_the_gate_sprite_is_registered_and_present():
    sprites = _project()["assets"]["sprites"]
    assert "spr_gate" in sprites, "spr_gate is not a registered asset"
    assert (SAMPLE / sprites["spr_gate"]["file_path"]).is_file()
    assert (SAMPLE / "sprites" / "spr_gate.json").is_file(), \
        "missing the sprite metadata side file"


def test_every_object_sprite_resolves():
    """Cheap completeness check while we are here: a sprite named by an object
    but absent from the asset table renders as nothing at all."""
    project = _project()
    sprites = project["assets"]["sprites"]
    for name, obj in project["assets"]["objects"].items():
        spr = obj.get("sprite")
        if spr:
            assert spr in sprites, "%s names unknown sprite %r" % (name, spr)
            assert (SAMPLE / sprites[spr]["file_path"]).is_file(), \
                "%s's sprite file is missing" % name


def test_the_gate_art_is_not_a_recoloured_key():
    """The two PNGs must genuinely differ. Catches a regenerate-the-wrong-file
    slip that would leave the JSON correct and the picture identical."""
    gate = (SAMPLE / "sprites" / "spr_gate.png").read_bytes()
    key = (SAMPLE / "sprites" / "spr_key.png").read_bytes()
    assert gate != key


def test_the_generator_reproduces_the_committed_sprite(tmp_path):
    """tools/gen_raycast_4_gate.py is committed so the art can be regenerated.
    If it drifts from the checked-in PNG, one of the two is stale."""
    import importlib.util
    spec = importlib.util.spec_from_file_location(
        "gen_gate", REPO_ROOT / "tools" / "gen_raycast_4_gate.py")
    gen = importlib.util.module_from_spec(spec)
    try:
        spec.loader.exec_module(gen)
    except SystemExit:
        import pytest
        pytest.skip("Pillow not installed")
    from PIL import Image
    import io
    regenerated = gen.draw_gate()
    committed = Image.open(SAMPLE / "sprites" / "spr_gate.png").convert("RGBA")
    assert regenerated.tobytes() == committed.tobytes(), \
        "gen_raycast_4_gate.py no longer reproduces the committed spr_gate.png"
