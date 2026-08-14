"""HTML5Exporter's offline Pyodide bundling (TODO.md: "Pyodide loads from
the jsDelivr CDN — a Python-using game needs internet on first open").

Never touches the real network or a real ~13 MB download -- ensure_pyodide_files
is monkeypatched with small fake bytes, matching test_pyodide_bundle.py's
discipline. Also pins the pako.min.js CDN removal (every HTML5 export is now
a genuinely self-contained single file, not just Python-using ones).
"""
import base64
import gzip
import json
import zipfile
from pathlib import Path

import pytest

from export.HTML5.html5_exporter import HTML5Exporter, project_needs_python

REPO_ROOT = Path(__file__).resolve().parent.parent


# ---------------------------------------------------------------------------
# project_needs_python — Python port of engine.js's PythonBridge.projectNeedsPython
# ---------------------------------------------------------------------------

def test_no_objects_does_not_need_python():
    assert project_needs_python({"assets": {"objects": {}}}) is False


def test_plain_action_does_not_need_python():
    data = {"assets": {"objects": {"obj_a": {"events": {
        "create": {"actions": [{"action": "set_hspeed", "parameters": {"speed": 4}}]}
    }}}}}
    assert project_needs_python(data) is False


def test_top_level_execute_code_needs_python():
    data = {"assets": {"objects": {"obj_a": {"events": {
        "create": {"actions": [{"action": "execute_code", "parameters": {"code": "pass"}}]}
    }}}}}
    assert project_needs_python(data) is True


def test_execute_code_nested_in_then_actions_needs_python():
    data = {"assets": {"objects": {"obj_a": {"events": {"step": {"actions": [
        {"action": "if_collision", "parameters": {"then_actions": [
            {"action": "execute_code", "parameters": {"code": "pass"}}
        ]}}
    ]}}}}}}
    assert project_needs_python(data) is True


def test_execute_code_nested_in_else_actions_needs_python():
    data = {"assets": {"objects": {"obj_a": {"events": {"step": {"actions": [
        {"action": "if_collision", "parameters": {"else_actions": [
            {"action": "execute_code", "parameters": {"code": "pass"}}
        ]}}
    ]}}}}}}
    assert project_needs_python(data) is True


def test_execute_code_in_keyboard_sub_event_needs_python():
    data = {"assets": {"objects": {"obj_a": {"events": {"keyboard": {"left": {"actions": [
        {"action": "execute_code", "parameters": {"code": "pass"}}
    ]}}}}}}}
    assert project_needs_python(data) is True


def test_malformed_object_entries_do_not_crash():
    data = {"assets": {"objects": {"obj_a": "not-a-dict", "obj_b": None}}}
    assert project_needs_python(data) is False


# ---------------------------------------------------------------------------
# pako embedding — universal, no opt-in needed
# ---------------------------------------------------------------------------

def test_pako_vendored_file_exists_and_is_mit_licensed():
    pako_path = REPO_ROOT / "resources" / "vendor" / "pako.min.js"
    assert pako_path.exists()
    content = pako_path.read_text(encoding="utf-8")
    assert "@license" in content
    assert "MIT" in content


def test_html5_export_never_references_the_pako_cdn(tmp_path):
    exporter = HTML5Exporter()
    assert "cdnjs.cloudflare.com" not in exporter.template_html
    assert "{pako_code}" in exporter.template_html  # placeholder present pre-export


def test_exported_html_embeds_pako_inline():
    exporter = HTML5Exporter()
    assert exporter.pako_code.strip().startswith("/*! pako")
    assert "</script" not in exporter.pako_code  # would break out of the <script> block


# ---------------------------------------------------------------------------
# Offline Pyodide bundle embedding (opt-in export_settings)
# ---------------------------------------------------------------------------

def _minimal_project(objects_dir_events=None):
    events = objects_dir_events or {
        "create": {"actions": [{"action": "execute_code", "parameters": {"code": "self.x = 1"}}]}
    }
    return {
        "name": "PyGame",
        "assets": {
            "sprites": {},
            "objects": {"obj_py": {"name": "obj_py", "sprite": "", "events": events}},
            "rooms": {"rm_a": {"name": "rm_a", "width": 320, "height": 240, "instances": []}},
        },
        "room_order": ["rm_a"],
    }


def _write_project(tmp_path, data):
    proj_dir = tmp_path / "proj"
    proj_dir.mkdir()
    (proj_dir / "project.json").write_text(json.dumps(data), encoding="utf-8")
    return proj_dir


_FAKE_FILES = {
    "pyodide.js": b"globalThis.loadPyodide = function(){};",
    "pyodide.asm.js": b"globalThis._createPyodideModule = function(){};",
    "pyodide.asm.wasm": b"\x00asmFAKEWASM",
    "pyodide-lock.json": json.dumps({"info": {}, "packages": {}}).encode(),
    "python_stdlib.zip": b"PKfake-zip",
}


def _fake_ensure_pyodide_files(progress_callback=None, **kw):
    if progress_callback:
        progress_callback(0.5, "fake progress")
    return dict(_FAKE_FILES)


@pytest.fixture
def monkeypatched_pyodide_bundle(monkeypatch):
    import export.HTML5.pyodide_bundle as bundle_mod
    monkeypatch.setattr(bundle_mod, "ensure_pyodide_files", _fake_ensure_pyodide_files)
    return bundle_mod


def test_offline_pyodide_off_by_default(tmp_path, monkeypatched_pyodide_bundle):
    proj_dir = _write_project(tmp_path, _minimal_project())
    out = tmp_path / "out"
    out.mkdir()
    exporter = HTML5Exporter()
    assert exporter.export(proj_dir, out) is True

    html_file = next(out.glob("*.html"))
    content = html_file.read_text(encoding="utf-8")
    assert "const EMBEDDED_PYODIDE = null;" in content
    assert "cdn.jsdelivr.net" in content  # CDN path preserved, unchanged


def test_offline_pyodide_off_when_project_has_no_python(tmp_path, monkeypatched_pyodide_bundle):
    proj_dir = _write_project(tmp_path, _minimal_project(objects_dir_events={
        "create": {"actions": [{"action": "set_hspeed", "parameters": {"speed": 4}}]}
    }))
    out = tmp_path / "out"
    out.mkdir()
    exporter = HTML5Exporter()
    # Asked for, but the project doesn't need it -- must not embed 17 MB
    # into a game that will never even load Pyodide.
    assert exporter.export(proj_dir, out, export_settings={'offline_pyodide': True}) is True

    html_file = next(out.glob("*.html"))
    content = html_file.read_text(encoding="utf-8")
    assert "const EMBEDDED_PYODIDE = null;" in content


def test_offline_pyodide_on_embeds_every_core_file(tmp_path, monkeypatched_pyodide_bundle):
    proj_dir = _write_project(tmp_path, _minimal_project())
    out = tmp_path / "out"
    out.mkdir()
    exporter = HTML5Exporter()
    assert exporter.export(proj_dir, out, export_settings={'offline_pyodide': True}) is True

    html_file = next(out.glob("*.html"))
    content = html_file.read_text(encoding="utf-8")
    assert "const EMBEDDED_PYODIDE = null;" not in content

    marker = "const EMBEDDED_PYODIDE = "
    start = content.index(marker) + len(marker)
    end = content.index(";", start)
    embedded = json.loads(content[start:end])

    assert set(embedded.keys()) == set(_FAKE_FILES.keys())

    # Text files: gzip-then-base64 (round-trips back to the exact fake bytes).
    for name in ("pyodide.js", "pyodide.asm.js"):
        raw = gzip.decompress(base64.b64decode(embedded[name]))
        assert raw == _FAKE_FILES[name]

    # Binary/already-compressed files: plain base64.
    for name in ("pyodide.asm.wasm", "pyodide-lock.json", "python_stdlib.zip"):
        assert base64.b64decode(embedded[name]) == _FAKE_FILES[name]


def test_offline_pyodide_progress_callback_invoked(tmp_path, monkeypatched_pyodide_bundle):
    proj_dir = _write_project(tmp_path, _minimal_project())
    out = tmp_path / "out"
    out.mkdir()
    exporter = HTML5Exporter()
    seen = []
    exporter.export(proj_dir, out, export_settings={'offline_pyodide': True},
                    progress_callback=lambda frac, msg: seen.append((frac, msg)))
    assert seen == [(0.5, "fake progress")]


def test_offline_pyodide_download_failure_returns_false_with_specific_message(tmp_path, monkeypatch):
    """export()'s outer try/except is intentionally broad (catches
    anything, returns False, logs to console) -- last_error_message is
    how a SPECIFIC, actionable message (not just "check the console")
    still reaches the caller to show in the UI."""
    import export.HTML5.pyodide_bundle as bundle_mod

    def failing(*a, **kw):
        raise RuntimeError(
            "Could not download the offline Python runtime file 'pyodide.js'. "
            "Uncheck it to export with the normal CDN-loaded Python runtime instead.")
    monkeypatch.setattr(bundle_mod, "ensure_pyodide_files", failing)

    proj_dir = _write_project(tmp_path, _minimal_project())
    out = tmp_path / "out"
    out.mkdir()
    exporter = HTML5Exporter()
    assert exporter.export(proj_dir, out, export_settings={'offline_pyodide': True}) is False
    assert exporter.last_error_message is not None
    assert "pyodide.js" in exporter.last_error_message
    assert "Uncheck it" in exporter.last_error_message


def test_last_error_message_resets_on_a_later_successful_export(tmp_path, monkeypatch):
    """A stale error from a previous failed export must not leak into a
    later successful one's result."""
    import export.HTML5.pyodide_bundle as bundle_mod
    monkeypatch.setattr(bundle_mod, "ensure_pyodide_files",
                        lambda *a, **kw: (_ for _ in ()).throw(RuntimeError("boom")))

    proj_dir = _write_project(tmp_path, _minimal_project())
    out = tmp_path / "out"
    out.mkdir()
    exporter = HTML5Exporter()
    assert exporter.export(proj_dir, out, export_settings={'offline_pyodide': True}) is False
    assert exporter.last_error_message is not None

    monkeypatch.setattr(bundle_mod, "ensure_pyodide_files", _fake_ensure_pyodide_files)
    assert exporter.export(proj_dir, out, export_settings={'offline_pyodide': True}) is True
    assert exporter.last_error_message is None


def test_embedded_json_is_actually_valid_json_no_matter_the_byte_content(tmp_path, monkeypatch):
    """Base64 output is pure ASCII regardless of input bytes, so the
    embedded object literal is always syntactically safe to splice into
    engine.js as-is (matches the existing game_data/sprites_data
    precedent, which relies on the same base64-is-ASCII property)."""
    import export.HTML5.pyodide_bundle as bundle_mod
    weird_files = dict(_FAKE_FILES)
    weird_files["pyodide.asm.wasm"] = bytes(range(256))  # every byte value

    monkeypatch.setattr(bundle_mod, "ensure_pyodide_files",
                        lambda progress_callback=None, **kw: weird_files)

    proj_dir = _write_project(tmp_path, _minimal_project())
    out = tmp_path / "out"
    out.mkdir()
    exporter = HTML5Exporter()
    assert exporter.export(proj_dir, out, export_settings={'offline_pyodide': True}) is True

    html_file = next(out.glob("*.html"))
    content = html_file.read_text(encoding="utf-8")
    marker = "const EMBEDDED_PYODIDE = "
    start = content.index(marker) + len(marker)
    end = content.index(";", start)
    embedded = json.loads(content[start:end])  # must not raise
    assert base64.b64decode(embedded["pyodide.asm.wasm"]) == bytes(range(256))
