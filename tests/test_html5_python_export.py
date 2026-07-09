"""HTML5 export: Python (execute_code) bridge, mouse dispatch, object-file merge.

The HTML5 engine historically had no mouse events and no execute_code
support (a draw-queue + mouse game like samples/match3_1 exported to a
dead page), and the exporter read object events only from project.json's
embedded copies, which go stale (objects/<name>.json is the source of
truth the project loader prefers). These tests pin:

- the exporter merges object side files (file wins) before embedding
- the emitted page carries the Pyodide bridge, mouse/touch dispatch,
  draw-queue renderer, and the maze actions (test_alignment /
  start_moving_direction) the bundled samples need

The full in-browser behaviour (Pyodide boot, click-swap round, canvas
pixels) is covered by the Playwright harness run during development;
browser + network aren't assumed available here.
"""
import gzip
import base64
import json
import re
import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT))

from export.HTML5.html5_exporter import HTML5Exporter  # noqa: E402


@pytest.fixture(scope="module")
def match3_html(tmp_path_factory):
    out = tmp_path_factory.mktemp("html5_export")
    exporter = HTML5Exporter()
    assert exporter.export(REPO_ROOT / "samples" / "match3_1", out)
    return (out / "Match3Game.html").read_text(encoding="utf-8")


def _embedded_game_data(html):
    m = re.search(r'const gameData = decompressData\("([A-Za-z0-9+/=]+)"\)', html)
    assert m, "embedded game data blob not found"
    return json.loads(gzip.decompress(base64.b64decode(m.group(1))))


def test_object_side_files_win_over_embedded_copy(match3_html):
    """project.json's embedded object is the stale pre-animation version;
    the export must carry objects/obj_GridManager.json's events."""
    data = _embedded_game_data(match3_html)
    events = data["assets"]["objects"]["obj_GridManager"]["events"]
    assert "step" in events, "step event exists only in the object side file"
    step_code = events["step"]["actions"][0]["parameters"]["code"]
    assert "self.falling" in step_code  # slide animation state


def test_engine_has_python_bridge(match3_html):
    assert "class PythonBridge" in match3_html
    assert "PYODIDE_URL" in match3_html
    assert "projectNeedsPython" in match3_html
    # IDE execute_code parity bits inside the Python bootstrap
    assert "exec_locals.items()" in match3_html
    assert "_Keyboard" in match3_html


def test_engine_dispatches_mouse_and_touch(match3_html):
    assert "'mouse_left_press', 'mouse_left_button', 'mouse_left_down'" in match3_html
    assert "'mouse_left_release'" in match3_html
    assert "addEventListener('mousedown'" in match3_html
    assert "addEventListener('touchstart'" in match3_html
    assert "inst.mouse_x = mx" in match3_html


def test_engine_renders_draw_queue(match3_html):
    assert "function renderDrawCommands" in match3_html
    for cmd in ("'rectangle'", "'circle'", "'ellipse'", "'line'", "'text'", "'scaled_text'"):
        assert f"case {cmd}" in match3_html


def test_engine_executes_code_actions(match3_html):
    assert "case 'execute_code'" in match3_html
    assert "game.python.runCode" in match3_html
    assert "game.python.runDraw" in match3_html


def test_engine_fires_create_before_first_step(match3_html):
    """Pending create events must fire at the TOP of GameRoom.step; firing
    them at the end let frame-1 step events run on un-initialized instances
    (AttributeError for execute_code games whose state is built in create)."""
    step_body = match3_html.split("step(game) {", 1)[1].split("render(ctx)")[0]
    create_pos = step_body.index("triggerCreateEvent")
    begin_pos = step_body.index("onBeginStep")
    assert create_pos < begin_pos


def test_engine_supports_maze_movement_actions(match3_html):
    """maze_1's player is driven by test_alignment + start_moving_direction,
    which the engine silently dropped — the flagship sample couldn't move."""
    assert "case 'test_alignment'" in match3_html
    assert "case 'start_moving_direction'" in match3_html
    assert "actionType === 'test_alignment'" in match3_html  # conditional gating
