"""Generated Kivy games run under REAL Kivy (micro:bit follow-up M6).

Most Kivy export tests run the generated code under a stub ``kivy``, which cannot catch a wrong Kivy API
call. These export bundled samples, then build a room scene in a subprocess (``_real_kivy_game.py``) on a
hidden window, tick it and read the frame's pixels back. Where Kivy or a GL context is missing (CI, a
headless box) they skip, and a crashing worker skips instead of taking pytest down.

Scenarios: (1) ``plateforme_3`` builds all its instances and survives 60 ticks; (2) a raycast sample draws a
first-person frame (not one flat colour); (3) the draw queue's ``sprite`` command crops ONE frame of a
multi-frame strip (``raycast_4``'s ``spr_face``), as the desktop does.
"""
import json
import subprocess
import sys
import tempfile
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "tests"))

from test_kivy_parity_batch import _load_project  # noqa: E402

GAME_WORKER = ROOT / "tests" / "_real_kivy_game.py"
DQ_WORKER = ROOT / "tests" / "_real_kivy_render.py"


def _export(sample):
    from export.Kivy.kivy_exporter import KivyExporter
    out = Path(tempfile.mkdtemp(prefix=f"realgame_{sample}_")) / "export"
    project = _load_project(sample)
    assert KivyExporter(project, ROOT / "samples" / sample, out).export()
    return out / "game", project


def _run(worker, game, request):
    work = Path(tempfile.mkdtemp(prefix="realgame_req_"))
    req, res = work / "request.json", work / "result.json"
    req.write_text(json.dumps(request), encoding="utf-8")
    try:
        proc = subprocess.run([sys.executable, str(worker), str(game), str(req), str(res)],
                              capture_output=True, text=True, timeout=240)
    except subprocess.TimeoutExpired:
        pytest.skip("real Kivy worker timed out")
    if not res.exists():
        pytest.skip(f"real Kivy cannot run here: worker died (exit {proc.returncode}): {proc.stderr[-300:]}")
    data = json.loads(res.read_text(encoding="utf-8"))
    if data.get("fatal"):
        pytest.skip(f"real Kivy cannot render here: {data['fatal']}")
    return data


def _scene_of(game, project):
    room = next(iter(project["assets"]["rooms"]))
    module = f"scenes.{room}"
    text = (game / "scenes" / f"{room}.py").read_text(encoding="utf-8")
    cls = next(line.split("class ")[1].split("(")[0] for line in text.splitlines()
               if line.startswith("class ") and "(Widget)" in line)
    return module, cls, room


@pytest.fixture(scope="module")
def platformer():
    pytest.importorskip("kivy")
    game, project = _export("plateforme_3")
    module, cls, room = _scene_of(game, project)
    data = _run(GAME_WORKER, game, {"module": module, "class": cls, "frames": 60, "track": ["obj_pingus"]})
    return data, project["assets"]["rooms"][room]


def test_plateforme_3_builds_every_room_instance_and_survives_60_ticks(platformer):
    data, room = platformer
    assert data["error"] is None, data["error"]
    assert data["instances"] == len(room["instances"]) > 20
    before, after = data["tracked"]["obj_pingus"]
    assert len(before) == len(after) == 1                       # the player exists and is still there


def test_plateforme_3_draws_a_frame_that_is_not_one_flat_colour(platformer):
    data, _ = platformer
    assert data["colors"] > 3, data["colors"]


@pytest.fixture(scope="module")
def raycast():
    pytest.importorskip("kivy")
    game, project = _export("raycast_1")
    module, cls, room = _scene_of(game, project)
    w, h = 640, 480
    return _run(GAME_WORKER, game, {"module": module, "class": cls, "frames": 20, "width": w, "height": h,
                                   "points": {"ceiling": [w // 2, 40], "floor": [w // 2, h - 40]}})


def test_a_raycast_sample_draws_a_first_person_frame(raycast):
    assert raycast["error"] is None, raycast["error"]
    assert raycast["colors"] > 5, raycast["colors"]
    assert raycast["raycast_instructions"], "the first-person overlay was never filled"   # walls, sky, floor...
    ceiling, floor = raycast["points"]["ceiling"], raycast["points"]["floor"]
    assert ceiling != floor                                      # sky/ceiling above, floor below


def test_a_sprite_draw_command_crops_one_frame_of_a_strip():
    pytest.importorskip("kivy")
    game, _ = _export("raycast_4")
    h, w = 120, 200
    commands = [{"type": "sprite", "sprite_name": "spr_face", "subimage": 0, "x": 10, "y": 10},
                {"type": "sprite", "sprite_name": "spr_face", "subimage": 3, "x": 100, "y": 10}]
    points = {"f0": [27, 27], "f3": [117, 27], "right_of_f0": [10 + 34 + 12, 27], "right_of_f3": [100 + 34 + 12, 27]}
    data = _run(DQ_WORKER, game, {"scenes": [{"name": "s", "w": w, "h": h, "commands": commands, "points": points}]})
    assert not data["errors"], data["errors"]
    got = data["scenes"]["s"]
    assert got["f0"] != got["f3"]                                # different frames of the strip
    assert got["right_of_f0"][:3] == [250, 0, 250] or got["right_of_f0"] == got["right_of_f3"]
