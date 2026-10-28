"""What a micro:bit project does on the exports that can't draw the board yet
(docs/MICROBIT_EXTENSION_PLAN.md, Stage S12; real parity is Stage P).

The desktop export freezes the real engine, so it is the one that works
(tools/verify_desktop_export.py). HTML5 and Kivy/Android have no micro:bit
simulator: their generators must not crash on a project that uses one, the
micro:bit actions they meet must fall through to the existing
unsupported-action handling (surfaced, not silently pretended), and the
generated Python must still compile. Pinned here so the claim in the release
checklist stays true.
"""
import base64
import gzip
import json
import logging
import py_compile
import re
import sys
import tempfile
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT))

ACTIONS = [
    "microbit_show_image", "microbit_scroll_text", "microbit_show_number",
    "microbit_set_pixel", "microbit_clear_display", "microbit_set_brightness",
    "microbit_play_tone", "microbit_play_melody", "microbit_stop_sound",
    "microbit_radio_set_group", "microbit_radio_send", "microbit_read_sensor",
    "microbit_if_button", "microbit_if_gesture", "microbit_if_tilt",
    "microbit_if_pixel",
]


def _project(events):
    return {
        "name": "mb", "version": "1.0",
        "settings": {"window_width": 320, "window_height": 240, "room_speed": 30,
                     "active_extensions": ["microbit"]},
        "assets": {
            "sprites": {}, "sounds": {}, "backgrounds": {}, "scripts": {},
            "fonts": {}, "data": {},
            "objects": {"microbit_1": {
                "name": "microbit_1", "asset_type": "object", "sprite": "",
                "visible": True, "solid": False, "events": events}},
            "rooms": {"room0": {
                "name": "room0", "asset_type": "room", "width": 320, "height": 240,
                "background_color": "#000000",
                "instances": [{"object_name": "microbit_1", "x": 160, "y": 120}]}},
        },
    }


def _action(name):
    from events.plugin_loader import load_all_plugins
    from events.action_types import ACTION_TYPES
    load_all_plugins()
    params = {p.name: p.default_value for p in ACTION_TYPES[name].parameters}
    return {"action": name, "parameters": params}


def _every_action_project():
    # Every micro:bit action, defaults filled in, in an event both exporters
    # understand (create), plus the micro:bit's own events.
    actions = [_action(name) for name in ACTIONS]
    return _project({
        "create": {"actions": actions},
        "microbit_button_a": {"actions": [_action("microbit_show_image")]},
        "microbit_gesture_shake": {"actions": [_action("microbit_play_tone")]},
        "microbit_radio_received": {"actions": [_action("microbit_show_number")]},
    })


# --- Kivy / Android ----------------------------------------------------------------------------

class _Collect(logging.Handler):
    def __init__(self):
        super().__init__(level=logging.WARNING)
        self.messages = []

    def emit(self, record):
        self.messages.append(record.getMessage())


@pytest.fixture
def caplog():
    """Collects the Kivy exporter's warnings. (The project's loggers don't
    propagate to the root logger, so pytest's own caplog sees nothing.)"""
    import export.Kivy.kivy_exporter as kivy_exporter
    handler = _Collect()
    kivy_exporter.logger.addHandler(handler)
    try:
        yield handler
    finally:
        kivy_exporter.logger.removeHandler(handler)


def _kivy_export(data, caplog):
    from export.Kivy.kivy_exporter import KivyExporter
    project_dir = Path(tempfile.mkdtemp(prefix="mb_kivy_src_"))
    out = Path(tempfile.mkdtemp(prefix="mb_kivy_")) / "export"
    assert KivyExporter(data, project_dir, out).export(), "Kivy export failed"
    py_files = list(out.rglob("*.py"))
    assert py_files
    for path in py_files:
        py_compile.compile(str(path), doraise=True)
    return out


def test_kivy_export_of_every_micro_bit_action_succeeds_and_compiles(caplog):
    out = _kivy_export(_every_action_project(), caplog)
    assert (out / "game" / "main.py").exists()


def test_kivy_export_reports_the_actions_it_skipped(caplog):
    _kivy_export(_every_action_project(), caplog)
    warning = next((m for m in caplog.messages
                    if "not supported and were skipped" in m), None)
    assert warning, "unsupported micro:bit actions were skipped silently"
    for name in ACTIONS:
        assert name in warning, name


def test_kivy_generated_code_runs_no_micro_bit_behaviour(caplog):
    """Skipped, not faked: the actions become inert placeholders and the
    micro:bit events produce no handlers."""
    out = _kivy_export(_every_action_project(), caplog)
    text = "\n".join(p.read_text(encoding="utf-8") for p in out.rglob("*.py"))
    assert "# TODO: microbit_show_image" in text
    assert "def on_microbit_" not in text and "microbit_button_a" not in text


def test_kivy_export_of_the_real_sample_succeeds(caplog):
    from core.project_manager import merge_object_file
    from export.Kivy.kivy_exporter import KivyExporter
    sample = REPO_ROOT / "samples" / "microbit_1"
    data = json.loads((sample / "project.json").read_text(encoding="utf-8"))
    for name, obj in data["assets"]["objects"].items():
        merge_object_file(obj, json.loads(
            (sample / "objects" / f"{name}.json").read_text(encoding="utf-8")))
    data["assets"]["rooms"]["room0"] = json.loads(
        (sample / "rooms" / "room0.json").read_text(encoding="utf-8"))
    out = Path(tempfile.mkdtemp(prefix="mb1_kivy_")) / "export"
    assert KivyExporter(data, sample, out).export()
    assert any("microbit_show_image" in m for m in caplog.messages)
    for path in out.rglob("*.py"):
        py_compile.compile(str(path), doraise=True)


# --- HTML5 -------------------------------------------------------------------------------------

def _html5_export(data):
    from export.HTML5.html5_exporter import HTML5Exporter
    src = Path(tempfile.mkdtemp(prefix="mb_html5_src_"))
    (src / "project.json").write_text(json.dumps(data), encoding="utf-8")
    out = Path(tempfile.mkdtemp(prefix="mb_html5_")) / "out"
    out.mkdir(parents=True)
    assert HTML5Exporter().export(src, out), "HTML5 export failed"
    html = next(out.glob("*.html")).read_text(encoding="utf-8")
    m = re.search(r'const gameData = decompressData\("([A-Za-z0-9+/=]+)"\)', html)
    assert m, "no embedded game data"
    return html, json.loads(gzip.decompress(base64.b64decode(m.group(1))))


def test_html5_export_of_every_micro_bit_action_succeeds_and_keeps_the_data():
    html, game = _html5_export(_every_action_project())
    blob = json.dumps(game["assets"]["objects"])
    for name in ACTIONS:
        assert name in blob, name
    assert "microbit_radio_received" in blob


def test_html5_engine_still_warns_on_an_action_nobody_knows_and_now_knows_ours():
    html, _ = _html5_export(_every_action_project())
    # engine.js's executeAction default branch: unknown actions warn and carry on.
    assert "console.warn(`Unknown action: ${actionType}`)" in html
    # Stage P / H2: the micro:bit actions are registered by the extension
    # (12 actions + 4 conditions), not left to that warning.
    for name in ACTIONS:
        assert f"    {name}(inst, p, game, sim)" in html, name


def test_html5_export_embeds_the_micro_bit_simulator():
    """Stage P / H1: the pure simulator ships with every HTML5 export (like
    every extension's export_html5.js); the actions come in later units."""
    html, _ = _html5_export(_every_action_project())
    assert "class MicrobitSimulator" in html and "window.__pygmMicrobit" in html


@pytest.mark.parametrize("sample", ["microbit_1"])
def test_html5_export_of_the_real_sample_succeeds(sample):
    from export.HTML5.html5_exporter import HTML5Exporter
    out = Path(tempfile.mkdtemp(prefix="mb1_html5_")) / "out"
    out.mkdir(parents=True)
    assert HTML5Exporter().export(REPO_ROOT / "samples" / sample, out)
    assert next(out.glob("*.html")).stat().st_size > 10_000
