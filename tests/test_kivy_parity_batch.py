"""Kivy export parity batch: draw family, creation cluster, animation_end,
no_more_lives — plus two pre-existing exporter breakers found while closing
the matrix:

- an ORPHANED else_action (GMK mis-imports drop the question action; see
  TODO.md maze_3 findings) generated a bare `else:` SyntaxError, so the
  plateforme_4/5 Kivy exports never compiled;
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
           "plateforme_1", "plateforme_2", "plateforme_3",
           "plateforme_4", "plateforme_5", "match3_1"]


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
    person = (exports["plateforme_4"] / "objects" / "obj_personnage.py").read_text(encoding="utf-8")
    assert "create_instance('obj_monstre_volant_mort'" in person
    monster = (exports["plateforme_4"] / "objects" / "obj_monstre.py").read_text(encoding="utf-8")
    assert "self.jump_to_random(" in monster
    maze3_monster = (exports["maze_3"] / "objects" / "monster_all.py").read_text(encoding="utf-8")
    # set_direction_speed with an expression param ("direction+90")
    assert "self.direction = (self.direction + 90)" in maze3_monster


def test_test_score_unknown_operation_mirrors_runtime(exports):
    """GMK numeric operation codes evaluate to False in the IDE runtime;
    the generated guard must do the same, not crash or guess."""
    person = (exports["plateforme_4"] / "objects" / "obj_personnage.py").read_text(encoding="utf-8")
    assert "test_score: unknown operation" in person


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

    def add_widget(self, w):
        self.children.append(w)

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
