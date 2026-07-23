"""Kivy scene-code extension mechanism — Stage C, unit C2a.

Each Kivy room is its own scene class generated from a ``.format()`` template, so
an extension contributes class-body methods that the exporter injects at a
marker AFTER ``.format()`` runs (dodging the brace-doubling landmine — injected
Python keeps its own ``{ }`` dict literals). This proves the seam is present and
wired BEFORE the raycast Kivy code is moved onto it (C2b/C2c), mirroring C1a on
the HTML5 side.
"""
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT))

from export.Kivy.kivy_exporter import KivyExporter  # noqa: E402

SRC = (REPO_ROOT / "export" / "Kivy" / "kivy_exporter.py").read_text(encoding="utf-8")


def _exporter():
    return KivyExporter({}, REPO_ROOT, REPO_ROOT / "_unused_out")


# --- The seam exists and is wired -----------------------------------------

def test_scene_template_has_the_injection_marker():
    # The marker sits inside the scene class body (a plain comment, so it
    # survives .format()); the exporter replaces it post-format.
    assert "# __PYGM_EXTENSION_SCENE_CODE__" in SRC


def test_generate_scene_injects_after_format():
    # The injection runs on the formatted scene, not the raw template.
    assert "code_formatted = self._inject_extension_scene_code(code_formatted)" in SRC


# --- Collection + injection --------------------------------------------------

def _write_fixture(tmp_path, folder, scene_code):
    d = tmp_path / folder
    d.mkdir()
    (d / "export_kivy.py").write_text(f"SCENE_CODE = {scene_code!r}\n", encoding="utf-8")
    return d


def test_collects_enabled_extension_scene_code(tmp_path, monkeypatch):
    import events.plugin_loader as pl
    _write_fixture(tmp_path, "demo_ext",
                   "    def _demo_hook(self):\n        return 42\n")
    monkeypatch.setattr(pl, "get_extension_directory", lambda: tmp_path)
    monkeypatch.setattr(pl, "list_available_extensions",
                        lambda: [{"folder": "demo_ext", "enabled": True}])
    got = _exporter()._collect_extension_scene_code()
    assert "def _demo_hook(self):" in got


def test_injection_replaces_the_marker(tmp_path, monkeypatch):
    import events.plugin_loader as pl
    _write_fixture(tmp_path, "demo_ext", "    def _demo_hook(self):\n        return 42\n")
    monkeypatch.setattr(pl, "get_extension_directory", lambda: tmp_path)
    monkeypatch.setattr(pl, "list_available_extensions",
                        lambda: [{"folder": "demo_ext", "enabled": True}])
    scene = ("class RmScene(Widget):\n"
             "    def __init__(self):\n        pass\n\n"
             "    # __PYGM_EXTENSION_SCENE_CODE__\n\n"
             "    def other(self):\n        return 1\n")
    out = _exporter()._inject_extension_scene_code(scene)
    assert "def _demo_hook(self):" in out
    assert KivyExporter.EXTENSION_SCENE_MARKER not in out
    compile(out, "scene.py", "exec")   # still valid Python


def test_disabled_extension_contributes_nothing(tmp_path, monkeypatch):
    import events.plugin_loader as pl
    _write_fixture(tmp_path, "off_ext", "    def _off(self):\n        return 0\n")
    monkeypatch.setattr(pl, "get_extension_directory", lambda: tmp_path)
    monkeypatch.setattr(pl, "list_available_extensions",
                        lambda: [{"folder": "off_ext", "enabled": False}])
    assert _exporter()._collect_extension_scene_code() == ""


def test_no_extension_code_leaves_a_valid_scene(tmp_path, monkeypatch):
    """With nothing to inject the marker is removed — the class body stays
    valid (raycast still ships from the template until C2b)."""
    import events.plugin_loader as pl
    monkeypatch.setattr(pl, "get_extension_directory", lambda: tmp_path)
    monkeypatch.setattr(pl, "list_available_extensions", lambda: [])
    scene = ("class RmScene(Widget):\n"
             "    # __PYGM_EXTENSION_SCENE_CODE__\n\n"
             "    def other(self):\n        return 1\n")
    out = _exporter()._inject_extension_scene_code(scene)
    assert KivyExporter.EXTENSION_SCENE_MARKER not in out
    compile(out, "scene.py", "exec")
