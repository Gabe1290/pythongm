"""Kivy export: set_sprite's subimage must survive being an expression.

plateforme_3 gives every bonus a random frame in its create event:

    set_sprite(sprite='spr_bonus', subimage='random(image_number)', speed=0)

The Kivy generator ran `int(params['subimage'])`, which raises on any
non-numeric value, and the except branch dropped the assignment silently. So
all 52 bonuses kept frame 0 -- the "bonus objects all show image 0" half of
issue 8 in the 2026-08-16 pass.

The desktop runtime hit exactly the same class of bug and documented the fix:
GameInstance.image_number exists so the token can bind, and `random(...)` is
routed through the expression evaluator instead of reaching int(). This mirrors
both halves for the export: the generated base object provides `image_number`,
`random`, `irandom` and `choose`, and the parameter goes through _num_code,
which binds bare names to self.
"""
import sys
import tempfile
import types
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT))
sys.path.insert(0, str(Path(__file__).resolve().parent))

from export.Kivy.code_generator import ActionCodeGenerator  # noqa: E402
from export.Kivy.kivy_exporter import KivyExporter  # noqa: E402

# Reuse the vertical-convention module's stubs and project merge: same harness,
# same generated base object.
from test_kivy_vertical_convention import (  # noqa: E402
    _Group, _Scene, _Stub, _Widget, _instance, _merged)


@pytest.fixture(scope="module")
def game_object():
    sample = REPO_ROOT / "samples" / "plateforme_3"
    out = Path(tempfile.mkdtemp(prefix="kivy_subimg_"))
    assert KivyExporter(_merged(sample), sample, out).export()

    source = (out / "game" / "objects" / "base_object.py").read_text(
        encoding="utf-8")
    compile(source, "base_object.py", "exec")

    module = types.ModuleType("generated_base_object_subimg")
    module.__dict__.update({
        "Widget": _Widget, "Rectangle": _Stub, "Color": _Stub, "Line": _Stub,
        "Ellipse": _Stub, "InstructionGroup": _Group, "PushMatrix": _Stub,
        "PopMatrix": _Stub, "Label": object,
        "Window": types.SimpleNamespace(size=(800, 600)),
        "load_image": lambda *a, **k: None,
        "SPRITE_PATHS": {}, "SOUND_PATHS": {}, "BACKGROUND_PATHS": {},
        "get_game_app": lambda: None, "_ScriptGameProxy": object,
        "math": __import__("math"), "random": __import__("random"),
    })
    stripped = "\n".join(line for line in source.splitlines()
                         if not line.startswith(("from ", "import ")))
    exec(stripped, module.__dict__)  # noqa: S102 - our own generated code
    return next(v for v in module.__dict__.values()
                if isinstance(v, type) and v.__name__ == "GameObject")


def _generated(params):
    generator = ActionCodeGenerator()
    generator.sprite_paths = {"spr_bonus": "assets/images/spr_bonus.png"}
    return generator._convert_simple_action("set_sprite", params, "create")


# --- the expression is no longer dropped ----------------------------------

def test_a_random_subimage_expression_is_emitted():
    """The bug: this assignment vanished, so every bonus kept frame 0."""
    code = _generated({"sprite": "spr_bonus",
                       "subimage": "random(image_number)", "speed": "0"})
    assert "self.image_index" in code, code
    assert "random" in code and "image_number" in code


def test_bare_names_in_the_expression_are_bound_to_self():
    code = _generated({"sprite": "<self>", "subimage": "random(image_number)"})
    assert "self.random(self.image_number)" in code, code


def test_the_frame_is_truncated_to_an_integer():
    """GameMaker's random() returns a real; a subimage is an index."""
    code = _generated({"sprite": "<self>", "subimage": "random(image_number)"})
    assert "int(" in code, code


def test_a_literal_subimage_still_works():
    code = _generated({"sprite": "<self>", "subimage": "3"})
    assert "self.image_index = 3" in code


def test_the_minus_one_sentinel_still_means_no_change():
    code = _generated({"sprite": "<self>", "subimage": "-1", "speed": "-1"})
    assert "image_index" not in code
    assert "image_speed" not in code


def test_an_absent_subimage_changes_nothing():
    code = _generated({"sprite": "<self>"})
    assert "image_index" not in code


def test_animation_speed_takes_expressions_too():
    """Same handler, same trap: a non-numeric speed was also discarded."""
    code = _generated({"sprite": "<self>", "speed": "image_number"})
    assert "self.image_speed = float((self.image_number))" in code, code


def test_a_malformed_value_is_still_skipped_rather_than_breaking_the_export():
    """An unparseable field must not emit uncompilable Python -- that would
    take out the whole object module rather than one action."""
    code = _generated({"sprite": "<self>", "subimage": "10 pixels"})
    assert "image_index" not in code
    compile(code, "generated", "exec")


# --- the base object supplies the GameMaker names -------------------------

def test_image_number_reports_the_frame_count(game_object):
    scene = _Scene()
    instance = _instance(game_object, scene)
    instance._sprite_frames = 6
    instance.has_sprite = True
    assert instance.image_number == 6


def test_image_number_is_zero_without_a_sprite(game_object):
    """GameMaker reports 0, and a random(0) frame pick must not explode."""
    scene = _Scene()
    instance = _instance(game_object, scene)
    instance.has_sprite = False
    assert instance.image_number == 0
    assert instance.random(instance.image_number) == 0


def test_random_stays_below_its_bound(game_object):
    """GameMaker's random(n) is [0, n) -- n itself must never come out, or a
    frame pick would index one past the last subimage."""
    scene = _Scene()
    instance = _instance(game_object, scene)
    for _ in range(200):
        assert 0 <= instance.random(6) < 6


def test_irandom_includes_its_bound(game_object):
    """irandom(n) is inclusive, unlike random(n)."""
    scene = _Scene()
    instance = _instance(game_object, scene)
    seen = {instance.irandom(3) for _ in range(400)}
    assert seen == {0, 1, 2, 3}, seen


def test_choose_returns_one_of_its_options(game_object):
    scene = _Scene()
    instance = _instance(game_object, scene)
    seen = {instance.choose(5, 7, 9) for _ in range(200)}
    assert seen <= {5, 7, 9} and len(seen) > 1, seen


# --- end to end on the real sample ---------------------------------------

def test_the_bonuses_actually_get_different_frames(game_object):
    """The reported symptom, executed. Runs the same expression the generated
    create event runs, and asserts the frames VARY -- asserting that the
    assignment exists would have passed even if it always yielded 0."""
    scene = _Scene()
    frames = set()
    for _ in range(120):
        instance = _instance(game_object, scene)
        instance._sprite_frames = 6
        instance.has_sprite = True
        instance.image_index = int(instance.random(instance.image_number))
        frames.add(instance.image_index)

    assert frames != {0}, "every bonus still shows frame 0"
    assert frames == {0, 1, 2, 3, 4, 5}, (
        "expected every frame of a 6-frame sprite to appear, got %s"
        % sorted(frames))


def test_the_samples_create_event_generates_the_frame_pick():
    """Against the real project rather than a hand-built action."""
    sample = REPO_ROOT / "samples" / "plateforme_3"
    out = Path(tempfile.mkdtemp(prefix="kivy_subimg_sample_"))
    assert KivyExporter(_merged(sample), sample, out).export()

    source = (out / "game" / "objects" / "obj_bonus.py").read_text(
        encoding="utf-8")
    compile(source, "obj_bonus.py", "exec")
    assert "self.image_index" in source, (
        "obj_bonus must set a frame; it authors subimage=random(image_number)")
    assert "self.random(self.image_number)" in source, source[:600]
