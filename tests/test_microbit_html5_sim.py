"""Stage P / H1: the HTML5 export's micro:bit simulator (export_html5.js) is a
faithful port of extensions/microbit/simulator.py.

CI has no JS engine, so the byte-level guarantees here are structural (the
generated tables are fresh, every numeric constant equals the Python one). The
behavioural guarantee -- a seeded random script applied to both simulators with
identical state and events after every call -- runs when Playwright + Chromium
are installed (the dev box) and is skipped otherwise.
"""
import re
import subprocess
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "tools"))

JS = ROOT / "extensions" / "microbit" / "export_html5.js"
SRC = JS.read_text(encoding="utf-8")


def _js_const(name):
    m = re.search(r"^const %s = ([-0-9.]+);" % re.escape(name), SRC, re.M)
    assert m, f"const {name} not found in export_html5.js"
    return float(m.group(1))


def test_generated_tables_are_fresh():
    r = subprocess.run([sys.executable, str(ROOT / "tools" / "gen_microbit_js_tables.py"), "--check"],
                       capture_output=True, text=True, cwd=ROOT)
    assert r.returncode == 0, "run tools/gen_microbit_js_tables.py to refresh the JS tables"


def test_tables_are_not_empty():
    assert '"HEART"' in SRC and '"DADADADUM"' in SRC and '"65": [' in SRC
    assert "const MB_GLYPHS = {};" not in SRC


@pytest.mark.parametrize("js_name, module, py_name", [
    ("WIDTH", "simulator", "WIDTH"), ("HEIGHT", "simulator", "HEIGHT"),
    ("MAX_BRIGHTNESS", "simulator", "MAX_BRIGHTNESS"),
    ("SCROLL_DELAY", "simulator", "SCROLL_DELAY"),
    ("MAX_QUEUE", "simulator", "MAX_QUEUE"),
    ("MAX_SOUND_QUEUE", "simulator", "MAX_SOUND_QUEUE"),
    ("MAX_RADIO_OUTBOX", "simulator", "MAX_RADIO_OUTBOX"),
    ("SAMPLE_PERIOD", "simulator", "SAMPLE_PERIOD"),
    ("TILT_TOLERANCE", "simulator", "TILT_TOLERANCE"),
    ("FREEFALL_TOLERANCE", "simulator", "FREEFALL_TOLERANCE"),
    ("SHAKE_TOLERANCE", "simulator", "SHAKE_TOLERANCE"),
    ("SHAKE_COUNT_THRESHOLD", "simulator", "SHAKE_COUNT_THRESHOLD"),
    ("SHAKE_DAMPING", "simulator", "SHAKE_DAMPING"),
    ("SHAKE_RTX", "simulator", "SHAKE_RTX"),
    ("GESTURE_DAMPING", "simulator", "GESTURE_DAMPING"),
    ("MAX_SAMPLES_PER_UPDATE", "simulator", "MAX_SAMPLES_PER_UPDATE"),
    ("LOUD_THRESHOLD", "simulator", "LOUD_THRESHOLD"),
    ("QUIET_THRESHOLD", "simulator", "QUIET_THRESHOLD"),
    ("DEFAULT_BPM", "sound", "DEFAULT_BPM"), ("DEFAULT_TICKS", "sound", "DEFAULT_TICKS"),
    ("DEFAULT_OCTAVE", "sound", "DEFAULT_OCTAVE"),
    ("DEFAULT_DURATION", "sound", "DEFAULT_DURATION"),
    ("ARTICULATION", "sound", "ARTICULATION"), ("MAX_FREQUENCY", "sound", "MAX_FREQUENCY"),
    ("MIN_GROUP", "radio", "MIN_GROUP"), ("MAX_GROUP", "radio", "MAX_GROUP"),
    ("MAX_MESSAGE", "radio", "MAX_MESSAGE"),
])
def test_constant_matches_python(js_name, module, py_name):
    import importlib
    py = getattr(importlib.import_module(f"extensions.microbit.{module}"), py_name)
    assert _js_const(js_name) == pytest.approx(float(py)), js_name


def test_impulses_and_periods_match_python():
    from extensions.microbit import simulator, sound
    for name, force in simulator.IMPULSES:
        assert f"['{name}', {force}]" in SRC
    for letter, us in sound._PERIODS_US.items():
        assert f"{letter}: {us}" in SRC
    for letter, us in sound._SHARPS_US.items():
        assert f"{letter}: {us}" in SRC


def _browser_available():
    try:
        import microbit_js_parity
        return microbit_js_parity.available()
    except Exception:
        return False


@pytest.mark.skipif(not _browser_available(), reason="needs Playwright + Chromium (dev box only)")
def test_js_and_python_simulators_agree():
    import microbit_js_parity
    bad = microbit_js_parity.compare(seeds=25, steps=400)
    assert not bad, f"first mismatch: seed {bad[0][0]} op {bad[0][1]}"
