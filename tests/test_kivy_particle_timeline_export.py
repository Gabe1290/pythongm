"""Kivy export codegen + real-execution coverage for particles + timelines
(Tier 5.3, docs/DEFERRED_GAPS_2026_PLAN.md / Section A of
docs/REMAINING_WORK_2026-08-15.md).

Codegen unit tests mirror tests/test_kivy_tier3_actions_export.py's own
`_gen`/`_valid` pattern. The execution tests import the REAL generated
`GameObject` class from a real Kivy export (objects/base_object.py) under
the established stub-kivy environment (mirrors
tests/test_kivy_parity_batch.py's `_stub_kivy_env` /
`test_base_object_helpers_behave`) and drive its real
create_particle_system/create_particle_type/create_emitter/burst_particles/
stream_particles/update_particle_system/update_timeline methods -- not a
reimplementation, the actual generated code.
"""
import json
import sys
import tempfile
import types
from contextlib import contextmanager
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT))

from export.Kivy.code_generator import ActionCodeGenerator  # noqa: E402
from export.Kivy.kivy_exporter import KivyExporter  # noqa: E402
from utils.project_file_merge import merge_object_file  # noqa: E402


def _gen(action_type, params, event_type="step"):
    g = ActionCodeGenerator(base_indent=2)
    g.process_action({"action_type": action_type, "parameters": params}, event_type)
    return g.get_code()


def _valid(src):
    wrapper = "class _C:\n    def m(self, other=None):\n" + src + "\n"
    compile(wrapper, "<gen>", "exec")
    return True


# ---------------------------------------------------------------------------
# Codegen unit tests
# ---------------------------------------------------------------------------

def test_create_particle_system_codegen():
    out = _gen("create_particle_system", {"depth": "5"})
    assert out.strip() == "self.create_particle_system(5)"
    assert _valid(out)


def test_destroy_particle_system_codegen():
    assert _gen("destroy_particle_system", {}).strip() == "self.destroy_particle_system()"


def test_clear_particles_codegen():
    assert _gen("clear_particles", {}).strip() == "self.clear_particles()"


def test_create_particle_type_codegen_full_params():
    out = _gen("create_particle_type", {
        "sprite": "spr_spark", "size_min": "1", "size_max": "2",
        "size_increase": "-0.1", "color": "#FF0000", "alpha": "0.8",
        "speed_min": "1", "speed_max": "3", "direction_min": "0",
        "direction_max": "360", "life_min": "20", "life_max": "40",
    })
    assert "self.create_particle_type(" in out
    assert "sprite='spr_spark'" in out
    assert "color='#FF0000'" in out
    assert _valid(out)


def test_create_emitter_codegen():
    out = _gen("create_emitter", {"x": "10", "y": "20", "width": "5",
                                   "height": "5", "shape": "ellipse"})
    assert "self.create_emitter(" in out
    assert "shape='ellipse'" in out
    assert _valid(out)


def test_destroy_emitter_codegen():
    assert _gen("destroy_emitter", {}).strip() == "self.destroy_emitter()"


def test_burst_particles_codegen():
    out = _gen("burst_particles", {"particle_type": "0", "number": "5"})
    assert out.strip() == "self.burst_particles(0, 5)"


def test_stream_particles_codegen():
    out = _gen("stream_particles", {"particle_type": "0", "number": "1"})
    assert out.strip() == "self.stream_particles(0, 1)"


def test_set_timeline_codegen():
    out = _gen("set_timeline", {"timeline": "tl_intro"})
    assert out.strip() == "self.set_timeline('tl_intro')"
    assert _valid(out)


def test_set_timeline_position_codegen():
    out = _gen("set_timeline_position", {"position": "5", "relative": True})
    assert out.strip() == "self.set_timeline_position(5, True)"


def test_set_timeline_speed_codegen():
    out = _gen("set_timeline_speed", {"speed": "0.5"})
    assert out.strip() == "self.set_timeline_speed(0.5)"


def test_start_pause_stop_timeline_codegen():
    assert _gen("start_timeline", {}).strip() == "self.start_timeline()"
    assert _gen("pause_timeline", {}).strip() == "self.pause_timeline()"
    assert _gen("stop_timeline", {}).strip() == "self.stop_timeline()"


# ---------------------------------------------------------------------------
# Real export + stub-kivy execution harness
# ---------------------------------------------------------------------------

class _Widget:
    def __init__(self, *a, **kw):
        self.canvas = types.SimpleNamespace(
            clear=lambda: None,
            add=lambda x: None,
            after=types.SimpleNamespace(add=lambda x: None, clear=lambda: None),
        )
        self.children = []

    def add_widget(self, w):
        self.children.append(w)

    def remove_widget(self, w):
        if w in self.children:
            self.children.remove(w)


class _Group:
    def __init__(self, *a, **kw):
        self.items = []

    def add(self, x):
        self.items.append(x)

    def clear(self):
        self.items = []


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
            width = 40
            height = 20

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
def exported():
    out = Path(tempfile.mkdtemp(prefix="kivy_particle_")) / "export"
    assert KivyExporter(_load_project("maze_1"), REPO_ROOT / "samples" / "maze_1", out).export()
    return out / "game"


def test_generated_base_object_compiles(exported):
    src = (exported / "objects" / "base_object.py").read_text(encoding="utf-8")
    for name in ("create_particle_system", "update_particle_system", "_spawn_particles",
                 "render_particles", "update_timeline", "set_timeline"):
        assert f"def {name}(" in src, name
    compile(src, "base_object.py", "exec")


class TestRealParticleExecution:
    def test_burst_spawns_ages_and_culls(self, exported):
        with _stub_kivy_env(exported):
            import importlib
            GameObject = importlib.import_module("objects.base_object").GameObject
            scene = _Scene()
            inst = GameObject(scene, 0, 0)

            inst.create_particle_system(depth=0)
            inst.create_particle_type(size_min=1.0, size_max=1.0, size_increase=0,
                                      color="#FF0000", alpha=1.0, speed_min=0, speed_max=0,
                                      direction_min=0, direction_max=0, life_min=2, life_max=2)
            inst.create_emitter(x=10, y=10, width=0, height=0)
            inst.burst_particles(particle_type=0, number=5)

            assert len(inst._particle_system["particles"]) == 5

            inst.update_particle_system()
            assert len(inst._particle_system["particles"]) == 5  # life 2 -> 1

            inst.update_particle_system()
            assert len(inst._particle_system["particles"]) == 0  # life 1 -> 0, culled

    def test_particle_moves_by_speed_and_direction(self, exported):
        with _stub_kivy_env(exported):
            import importlib
            GameObject = importlib.import_module("objects.base_object").GameObject
            scene = _Scene()
            inst = GameObject(scene, 0, 0)

            inst.create_particle_system()
            inst.create_particle_type(speed_min=4, speed_max=4, direction_min=0,
                                      direction_max=0, life_min=100, life_max=100)
            inst.create_emitter(x=0, y=0, width=0, height=0)
            inst.burst_particles(particle_type=0, number=1)

            p = inst._particle_system["particles"][0]
            x0, y0 = p["x"], p["y"]
            inst.update_particle_system()
            assert abs(p["x"] - (x0 + 4)) < 1e-9
            assert abs(p["y"] - y0) < 1e-9

    def test_streaming_emitter_spawns_every_frame(self, exported):
        with _stub_kivy_env(exported):
            import importlib
            GameObject = importlib.import_module("objects.base_object").GameObject
            scene = _Scene()
            inst = GameObject(scene, 0, 0)

            inst.create_particle_system()
            inst.create_particle_type(life_min=100, life_max=100)
            inst.create_emitter(x=0, y=0, width=0, height=0)
            inst.stream_particles(particle_type=0, number=3)

            assert len(inst._particle_system["particles"]) == 0  # armed, not spawned
            inst.update_particle_system()
            assert len(inst._particle_system["particles"]) == 3
            inst.update_particle_system()
            assert len(inst._particle_system["particles"]) == 6

    def test_no_particle_system_is_a_safe_noop(self, exported):
        with _stub_kivy_env(exported):
            import importlib
            GameObject = importlib.import_module("objects.base_object").GameObject
            scene = _Scene()
            inst = GameObject(scene, 0, 0)
            inst.update_particle_system()  # must not raise
            inst.render_particles()  # must not raise


class TestRealTimelineExecution:
    def test_position_advances_while_running(self, exported):
        with _stub_kivy_env(exported):
            import importlib
            GameObject = importlib.import_module("objects.base_object").GameObject
            scene = _Scene()
            inst = GameObject(scene, 0, 0)

            inst.set_timeline("tl_intro")
            inst.start_timeline()
            assert inst.timeline_position == 0
            inst.update_timeline()
            assert inst.timeline_position == 1
            inst.update_timeline()
            assert inst.timeline_position == 2

    def test_pause_stops_advancing(self, exported):
        with _stub_kivy_env(exported):
            import importlib
            GameObject = importlib.import_module("objects.base_object").GameObject
            scene = _Scene()
            inst = GameObject(scene, 0, 0)

            inst.set_timeline("tl_intro")
            inst.start_timeline()
            inst.update_timeline()
            inst.pause_timeline()
            inst.update_timeline()
            inst.update_timeline()
            assert inst.timeline_position == 1

    def test_stop_resets_position(self, exported):
        with _stub_kivy_env(exported):
            import importlib
            GameObject = importlib.import_module("objects.base_object").GameObject
            scene = _Scene()
            inst = GameObject(scene, 0, 0)

            inst.set_timeline("tl_intro")
            inst.start_timeline()
            inst.update_timeline()
            inst.update_timeline()
            inst.stop_timeline()
            assert inst.timeline_position == 0
            inst.update_timeline()
            assert inst.timeline_position == 0  # stopped, not running
