"""Kivy export parity batch: draw family, creation cluster, animation_end,
no_more_lives — plus two pre-existing exporter breakers found while closing
the matrix:

- an ORPHANED else_action (GMK mis-imports drop the question action; see
  TODO.md maze_3 findings) generated a bare `else:` SyntaxError, so the
  plateforme_4/5 Kivy exports never compiled (those two samples were later
  removed from the bundled set pending import cleanup — see samples/README.md
  — so the create_moving_instance/jump_to_random/test_score-unknown-operation
  assertions below are now pinned directly against ActionCodeGenerator
  rather than through a sample export);
- maze_3's "obj trigger" (space in the object name) generated
  `class Obj trigger` / `from objects.obj trigger import ...`, so the
  whole maze_3 Kivy export never compiled.

The compile gate below would have caught both years earlier: every module
of every bundled sample's Kivy export must be valid Python.
"""
import json
import py_compile
import sys
import tempfile
import types
from contextlib import contextmanager
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT))

from export.Kivy.kivy_exporter import KivyExporter  # noqa: E402
from export.Kivy.code_generator import ActionCodeGenerator  # noqa: E402
from utils.project_file_merge import merge_object_file  # noqa: E402

SAMPLES = ["maze_1", "maze_2", "maze_3",
           "plateforme_1", "plateforme_2", "plateforme_3", "match3_1"]


def _load_project(sample):
    root = REPO_ROOT / "samples" / sample
    data = json.loads((root / "project.json").read_text(encoding="utf-8"))
    for name, obj in data["assets"]["objects"].items():
        f = root / "objects" / f"{name}.json"
        if f.exists() and isinstance(obj, dict):
            merge_object_file(obj, json.loads(f.read_text(encoding="utf-8")))
    for name in list(data["assets"]["rooms"]):
        f = root / "rooms" / f"{name}.json"
        if f.exists():
            data["assets"]["rooms"][name] = json.loads(f.read_text(encoding="utf-8"))
    return data


@pytest.fixture(scope="module")
def exports(tmp_path_factory):
    """Export every bundled sample once; return {sample: game_dir}."""
    result = {}
    for sample in SAMPLES:
        out = tmp_path_factory.mktemp(f"kivy_{sample}") / "export"
        assert KivyExporter(_load_project(sample),
                            REPO_ROOT / "samples" / sample, out).export(), sample
        result[sample] = out / "game"
    return result


# ---------------------------------------------------------------------------
# The compile gate: every generated module of every sample must be valid
# ---------------------------------------------------------------------------

@pytest.mark.parametrize("sample", SAMPLES)
def test_every_generated_module_compiles(exports, sample):
    errors = []
    for f in sorted(exports[sample].rglob("*.py")):
        try:
            py_compile.compile(str(f), doraise=True)
        except py_compile.PyCompileError as e:
            errors.append(f"{f.relative_to(exports[sample])}: {e}")
    assert not errors, "\n".join(errors)


# ---------------------------------------------------------------------------
# Generated-code markers for the parity batch
# ---------------------------------------------------------------------------

def test_draw_family_queues_runtime_commands(exports):
    maze2 = (exports["maze_2"] / "objects" / "controller_main.py").read_text(encoding="utf-8")
    assert "type='text'" in maze2 and "_ga().score" in maze2  # draw_score
    maze3 = (exports["maze_3"] / "objects" / "controller_main.py").read_text(encoding="utf-8")
    assert "type='lives'" in maze3                            # draw_lives
    assert "self.draw_color = (255, 255, 255)" in maze3       # set_draw_color


def test_creation_cluster_and_expressions(exports):
    maze3_monster = (exports["maze_3"] / "objects" / "monster_all.py").read_text(encoding="utf-8")
    # set_direction_speed with an expression param ("direction+90")
    assert "self.direction = (self.direction + 90)" in maze3_monster


def test_create_moving_instance_and_jump_to_random_codegen():
    """create_moving_instance / jump_to_random codegen, pinned directly
    against ActionCodeGenerator rather than through a bundled sample.

    These two action types don't naturally occur in any currently-bundled
    sample — they used to be exercised by plateforme_4/5's real GMK-import
    data (obj_personnage's create_moving_instance('obj_monstre_volant_mort',
    ...) on collision, obj_monstre's jump_to_random on a wall bump) before
    those two samples were removed from the bundled set pending import
    cleanup (see samples/README.md)."""
    gen = ActionCodeGenerator(base_indent=2)
    gen.process_action(
        {"action": "create_moving_instance",
         "parameters": {"object": "obj_monstre_volant_mort", "x": "1"}},
        "create")
    code = gen.get_code()
    compile(f"def _t(self):\n{code}\n", "<gen>", "exec")
    assert "self.scene.create_instance('obj_monstre_volant_mort'" in code

    gen2 = ActionCodeGenerator(base_indent=2)
    gen2.process_action({"action": "jump_to_random", "parameters": {}}, "create")
    code2 = gen2.get_code()
    compile(f"def _t(self):\n{code2}\n", "<gen>", "exec")
    assert "self.jump_to_random(" in code2


def test_test_score_unknown_operation_mirrors_runtime():
    """GMK numeric operation codes (a raw, un-translated GML operation
    index left over from an import — e.g. samples/plateforme_4's
    obj_personnage had a keyboard.up test_score action with
    operation='1' instead of a named comparison) evaluate to False in the
    IDE runtime; the generated guard must do the same, not crash or guess.

    Pinned directly against ActionCodeGenerator — see
    test_create_moving_instance_and_jump_to_random_codegen's docstring for
    why this moved off the (now-removed) plateforme_4 sample."""
    gen = ActionCodeGenerator(base_indent=2)
    gen.process_action(
        {"action": "test_score", "parameters": {"value": "0", "operation": "1"}},
        "create")
    gen.process_action({"action": "reverse_horizontal", "parameters": {}}, "create")
    code = gen.get_code()
    compile(f"def _t(self):\n{code}\n", "<gen>", "exec")
    assert "test_score: unknown operation" in code


def test_animation_end_and_no_more_lives_wiring(exports):
    expl = (exports["maze_3"] / "objects" / "obj_explosion.py").read_text(encoding="utf-8")
    assert "def on_animation_end(self):" in expl
    assert "self.destroy_at_position(" in expl
    base = (exports["maze_3"] / "objects" / "base_object.py").read_text(encoding="utf-8")
    assert "on_animation_end" in base                 # wrap hook
    assert "def destroy_at_position(self" in base
    assert "def jump_to_random(self" in base
    assert "elif ctype == 'sprite':" in base          # draw_sprite renderer
    assert "elif ctype == 'lives':" in base           # draw_lives renderer
    main_py = (exports["maze_3"] / "main.py").read_text(encoding="utf-8")
    assert "on_no_more_lives" in main_py              # set_lives crossing


def test_orphaned_else_generates_false_guard():
    gen = ActionCodeGenerator(base_indent=2)
    gen.process_action({"action": "set_score", "parameters": {"value": "1"}}, "create")
    gen.process_action({"action": "else_action", "parameters": {}}, "create")
    gen.process_action({"action": "reverse_horizontal", "parameters": {}}, "create")
    code = gen.get_code()
    compile(f"def _t(self):\n{code}\n", "<gen>", "exec")
    assert "if False:" in code  # runtime skips the orphaned else's unit


def test_object_name_with_space_sanitized():
    exporter = KivyExporter({}, REPO_ROOT, REPO_ROOT)
    assert exporter._get_object_module_name("obj trigger") == "obj_trigger"
    assert exporter._get_object_class_name("obj trigger") == "ObjTrigger"


def test_room_name_with_space_or_leading_digit_sanitized():
    """KA-H1: room names (like object names, e.g. GMK's "obj trigger")
    must sanitize into valid module/class identifiers. A room "level 1"
    used to emit `scenes/level 1.py` + `class Level 1` — a SyntaxError
    that broke the whole Kivy export. ROOM_ORDER/ROOM_CLASSES keep the
    original name as the lookup key."""
    exporter = KivyExporter({}, REPO_ROOT, REPO_ROOT)
    assert exporter._get_room_module_name("level 1") == "level_1"
    assert exporter._get_room_class_name("level 1") == "Level1"
    # leading digit -> prefixed (not a valid identifier start otherwise)
    assert exporter._get_room_module_name("1_intro") == "room_1_intro"
    assert exporter._get_room_class_name("1_intro")[0].isalpha()


def test_punctuation_only_name_gets_nonempty_class(exports=None):
    """KA-L1: a punctuation-only name reduces to all-underscores; without a
    fallback the class name is empty -> `class (GameObject):` SyntaxError."""
    exporter = KivyExporter({}, REPO_ROOT, REPO_ROOT)
    assert exporter._get_object_class_name("!!!") == "Obj"
    assert exporter._get_room_class_name("###") == "Room"


def test_room_dimensions_clamped():
    """KA-L2: a 0/negative/non-numeric room dimension must not reach the
    Android scaler's division (ZeroDivisionError at startup)."""
    exporter = KivyExporter({}, REPO_ROOT, REPO_ROOT)
    assert exporter._safe_room_dim(0, 640) == 640
    assert exporter._safe_room_dim(-5, 640) == 640
    assert exporter._safe_room_dim(None, 640) == 640
    assert exporter._safe_room_dim("bad", 640) == 640
    assert exporter._safe_room_dim(800, 640) == 800


def test_hostile_project_name_and_zero_dim_room_still_compile():
    """KA-M1 + KA-L2 end-to-end: a project name with an embedded quote and
    backslash, plus a 0x0 room, must still produce a compilable export."""
    import json
    import py_compile
    import shutil
    import tempfile

    src = REPO_ROOT / "samples" / "maze_1"
    tmp = Path(tempfile.mkdtemp(prefix="ka_qw_test_"))
    proj = tmp / "proj"
    shutil.copytree(src, proj)
    data = json.loads((proj / "project.json").read_text(encoding="utf-8"))
    data["name"] = 'My "Weird\\" Game'  # embedded quote + backslash (KA-M1)
    first = next(iter(data["assets"]["rooms"]))
    rf = proj / "rooms" / f"{first}.json"
    if rf.exists():
        data["assets"]["rooms"][first] = {
            **data["assets"]["rooms"][first],
            **json.loads(rf.read_text(encoding="utf-8"))}
    data["assets"]["rooms"][first]["width"] = 0   # KA-L2
    data["assets"]["rooms"][first]["height"] = 0
    (proj / "project.json").write_text(json.dumps(data), encoding="utf-8")

    out = tmp / "out"
    assert KivyExporter(data, proj, out).export()
    for f in sorted((out / "game").rglob("*.py")):
        py_compile.compile(str(f), doraise=True)  # raises on any SyntaxError


# ---------------------------------------------------------------------------
# Behavioral: base-object helpers under stub kivy modules
# ---------------------------------------------------------------------------

class _Group:
    def __init__(self):
        self.children = []

    def add(self, i):
        self.children.append(i)

    def clear(self):
        self.children.clear()

    def __enter__(self):
        return self

    def __exit__(self, *a):
        return False


class _Canvas(_Group):
    def __init__(self):
        super().__init__()
        self.before = _Group()
        self.after = _Group()


class _Widget:
    def __init__(self, **kw):
        self.canvas = _Canvas()
        self.children = []
        self.size = (0, 0)
        self.pos = (0, 0)

    def add_widget(self, w, index=0, canvas=None):
        # Real Kivy signature: children[0] is drawn LAST (on top). The
        # exporter passes index= to order instances by GameMaker depth.
        self.children.insert(index, w)

    def remove_widget(self, w):
        if w in self.children:
            self.children.remove(w)


class _Instr:
    def __init__(self, *a, **kw):
        self.a, self.kw = a, kw


@contextmanager
def _stub_kivy_env(game_dir: Path):
    saved_path = list(sys.path)
    saved_modules = dict(sys.modules)

    def mod(name, **attrs):
        m = types.ModuleType(name)
        for k, v in attrs.items():
            setattr(m, k, v)
        sys.modules[name] = m

    try:
        mod("kivy")
        mod("kivy.uix")
        mod("kivy.uix.widget", Widget=_Widget)
        mod("kivy.graphics", Rectangle=_Instr, Color=_Instr, Line=_Instr,
            Ellipse=_Instr, InstructionGroup=_Group)
        mod("kivy.core")
        mod("kivy.core.image", Image=object)

        class _Tex:
            size = (40, 20)

        class _CoreLabel:
            def __init__(self, **kw):
                self.texture = None

            def refresh(self):
                self.texture = _Tex()

        mod("kivy.core.text", Label=_CoreLabel)

        class _Window:
            width = 800
            height = 600

        mod("kivy.core.window", Window=_Window())
        for n in [k for k in sys.modules
                  if k == "utils" or k.startswith(("utils.", "objects"))]:
            del sys.modules[n]
        sys.path = [str(game_dir)] + [p for p in sys.path if p != str(REPO_ROOT)]
        yield
    finally:
        sys.path[:] = saved_path
        for n in [k for k in sys.modules if k not in saved_modules]:
            del sys.modules[n]
        sys.modules.update(saved_modules)


class _Scene:
    room_width = 640
    room_height = 480

    def __init__(self):
        self.instances = []
        self.destroyed = []

    def destroy_instance(self, inst):
        self.destroyed.append(inst)


def test_base_object_helpers_behave(exports):
    import importlib
    with _stub_kivy_env(exports["maze_3"]):
        GameObject = importlib.import_module("objects.base_object").GameObject
        scene = _Scene()
        a = GameObject(scene, 100, 100)
        near = GameObject(scene, 110, 100)
        far = GameObject(scene, 400, 400)
        scene.instances = [a, near, far]

        a.destroy_at_position(0, 0, 64, "all", relative=True)
        assert near in scene.destroyed
        assert far not in scene.destroyed
        assert a not in scene.destroyed  # caller excluded

        a.jump_to_random(32, 32)
        assert 0 <= a.x < 640 and 0 <= a.y < 480
        assert a.x % 32 == 0 and a.y % 32 == 0

        fired = []
        a._sprite_frames = 4
        a.image_index = 3.9
        a.image_speed = 6.0
        a.visible = False  # the advance must run even while invisible
        a.on_animation_end = lambda: fired.append(1)
        a._advance_animation(0.1)
        assert fired and 0 <= a.image_index < 4


# ---------------------------------------------------------------------------
# Kivy code-generator hardening (audit KA finder, 2026-07-14):
# empty/expression/malformed numeric fields, caption escaping, keymap.
# ---------------------------------------------------------------------------

def _gen(action, params, event="step"):
    from export.Kivy.code_generator import ActionCodeGenerator
    g = ActionCodeGenerator(base_indent=2)
    g.process_action({"action": action, "parameters": params}, event)
    return g.get_code()


def _compiles(code):
    compile(f"def _m(self):\n{code or '        pass'}\n", "<gen>", "exec")
    return True


@pytest.mark.parametrize("action,params", [
    ("set_hspeed", {"speed": ""}),
    ("set_vspeed", {"speed": ""}),
    ("set_speed", {"speed": ""}),
    ("set_direction", {"direction": ""}),
    ("set_alarm", {"alarm_number": "2", "steps": ""}),
    ("create_instance", {"object": "obj_x", "x": "", "y": ""}),
    ("jump_to_position", {"x": "", "y": ""}),
    ("set_score", {"value": "", "relative": True}),
    ("set_variable", {"variable": "hspeed", "value": ""}),
    ("set_variable", {"variable": "myvar", "value": ""}),
    ("draw_text", {"text": "hi", "x": "10 pixels", "y": 0}),  # malformed expr
    ("set_hspeed", {"speed": "5 apples"}),                    # malformed expr
])
def test_empty_or_malformed_numeric_fields_compile(action, params):
    """KA finder F1/F4: a cleared or malformed numeric field is a no-op on
    desktop but used to emit uncompilable Python (self.hspeed = ) that
    killed the whole exported object module. Now routed through _num_code."""
    assert _compiles(_gen(action, params))


def test_set_vspeed_folds_sign_for_numeric():
    """The sign flip folds a numeric literal (-3 stays a clean 3, not --3)."""
    assert "self.vspeed = 3" in _gen("set_vspeed", {"speed": "-3"})
    assert "self.vspeed = -24" in _gen("set_vspeed", {"speed": "24"})
    # an expression is wrapped, not folded
    assert "self.vspeed = -(" in _gen("set_vspeed", {"speed": "myjump"})


def test_numeric_field_resolves_bare_instance_var():
    """KA finder F3: a bare instance-var name resolves to self.<name>
    (parity with the desktop runtime's _parse_value)."""
    assert "self.direction" in _gen("set_hspeed", {"speed": "direction"})


def test_caption_and_names_with_quotes_are_repr_escaped():
    """KA finder F2: free text (caption) / a lookup name with an apostrophe
    used to break the emitted literal -> SyntaxError."""
    assert _compiles(_gen("set_window_caption", {"caption": "Player's Score"}))
    assert _compiles(_gen("create_instance", {"object": "obj'x", "x": 0, "y": 0}))


def test_if_key_pressed_non_arrow_keys():
    """KA finder F5: non-arrow keys used to all fall back to 275 (RIGHT).
    Now space/letters map correctly and an unknown key maps to -1 (never
    fires) instead of firing on the right arrow."""
    assert "get(32," in _gen("if_key_pressed", {"key": "space"})   # space
    assert "get(97," in _gen("if_key_pressed", {"key": "a"})       # 'a'
    assert "get(-1," in _gen("if_key_pressed", {"key": "f5"})      # unknown
    assert "get(275," not in _gen("if_key_pressed", {"key": "f5"})
