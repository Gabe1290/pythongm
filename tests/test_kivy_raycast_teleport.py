"""Go to Room Seamlessly in the Kivy (Android/iOS) export (docs/RAYCAST_CEILINGS_TELEPORT_PLAN.md, T2).

Kivy has no before-step hook, but it does not need one: GameApp._do_room_switch builds the new scene,
and the scene CONSTRUCTOR runs the create events and then renders the first overlay frame -- so the
arrival is applied at the head of that first overlay call (``_ext_overlay__raycast_2_5d``), after the
camera's Create event and before anything is drawn. Three layers:

* codegen (runs everywhere);
* the stub-kivy harness drives the REAL generated scene code: the action records the arrival (offset in
  the author's y-down space, so rooms of different heights agree) and asks for an instant change; the
  new scene's first overlay call applies it, carries facing / speed / eye height, and the failure modes
  are all logged and none fatal;
* real Kivy (skipped without it or without GL): the real generated scenes of a two-room export; the
  new scene is constructed as the game does, and its camera is read before any update.
"""
import json
import subprocess
import sys
import tempfile
import types
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(Path(__file__).resolve().parent))  # sibling test import

from test_kivy_raycast import (  # noqa: E402
    _stub_kivy_env, _scene_class, _FakeInst, _export_raycast_1,
)
from test_kivy_raycast_stairs import _stairs_scene, _real_export  # noqa: E402

AUTHORED = (64.0, 64.0)


# ------------------------------------------------------------- everywhere

def test_codegen_for_the_action():
    from extensions.raycast_2_5d.export_kivy import _cg_go_to_room_seamlessly, ACTION_CODEGEN
    assert ACTION_CODEGEN["go_to_room_seamlessly"] is _cg_go_to_room_seamlessly
    assert _cg_go_to_room_seamlessly(None, {"room": "room1", "marker": "obj_marker"}, "keyboard") == (
        "self.scene._raycast_go_seamless('room1', 'obj_marker')")


# ------------------------------------------------------------ stub harness

@pytest.fixture(scope="module")
def exported():
    return _export_raycast_1()


def _inst(gx_px, gy_gm, w=32, h=32, room_h=480, name=None):
    """A fake instance at a GM (y-down) position, stored in Kivy y-up coordinates."""
    inst = _FakeInst(gx_px, room_h - gy_gm - h, w, h, solid=False)
    inst.object_name = name
    return inst


def _scene(cls, room_name, camera_gm, marker_gm, room_h=480, with_camera=True, with_marker=True):
    scene, cam = _stairs_scene(cls, {}, room=room_h)
    scene.room_name = room_name
    scene.keys_pressed = {}                                   # the real scene has it from __init__
    scene.instances = [i for i in scene.instances if i is not cam]
    cam = _inst(camera_gm[0], camera_gm[1], room_h=room_h, name="obj_person")
    cam.facing_angle = 40.0
    cam.hspeed = cam.vspeed = 0.0
    if with_camera:
        scene.instances.append(cam)
        scene.raycast_camera["camera_instance"] = cam
    else:
        scene.raycast_camera["enabled"] = False
    if with_marker:
        scene.instances.append(_inst(marker_gm[0], marker_gm[1], room_h=room_h, name="obj_marker"))
    return scene, cam


class _App:
    _raycast_arrival = None


@pytest.fixture()
def wired(exported):
    """The stub `main` module with a game app, goto_room and ROOM_ORDER."""
    with _stub_kivy_env(exported):
        import main
        app = _App()
        asked = []
        main.get_game_app = lambda: app
        main.goto_room = lambda name, transition="none": asked.append((name, transition))
        main.ROOM_ORDER = ["room0", "room1"]
        yield exported, app, asked


def test_the_action_records_the_arrival_in_gm_space_and_asks_for_the_change(wired):
    exported, app, asked = wired
    cls = _scene_class(exported)
    scene, cam = _scene(cls, "room0", camera_gm=(64, 224), marker_gm=(160, 224))
    cam.hspeed, cam.vspeed = 2.0, -1.0
    scene._raycast_eye_floor = 12.0
    scene._raycast_go_seamless("room1", "obj_marker")
    arrival = app._raycast_arrival
    assert asked == [("room1", "none")]
    assert (arrival["dx"], arrival["dy"]) == (-96.0, 0.0)
    assert arrival["facing"] == 40.0 and (arrival["hspeed"], arrival["vspeed"]) == (2.0, -1.0)
    assert arrival["eye_floor"] == 12.0


def test_the_new_scene_applies_it_at_its_first_overlay_call(wired):
    exported, app, asked = wired
    cls = _scene_class(exported)
    scene0, cam0 = _scene(cls, "room0", camera_gm=(64, 224), marker_gm=(160, 224))
    cam0.hspeed = 2.0
    scene0.keys_pressed["up"] = True
    scene0._raycast_eye_floor = 12.0
    scene0._raycast_go_seamless("room1", "obj_marker")
    # room1 is taller, so a GM-space offset (not a Kivy one) is what must carry over.
    scene1, cam1 = _scene(cls, "room1", camera_gm=AUTHORED, marker_gm=(320, 128), room_h=640)
    cam1.facing_angle = 90.0                                  # the camera's own Create event
    assert scene1._ext_overlay__raycast_2_5d() is True
    gm_x, gm_y = scene1._raycast_gm_xy(cam1)
    assert (gm_x, gm_y) == (320 - 96, 128)                    # marker + the carried offset
    assert cam1.facing_angle == 40.0 and cam1.hspeed == 2.0
    assert scene1._raycast_eye_floor == 12.0
    assert scene1.keys_pressed == {"up": True}               # a held key stays held
    assert app._raycast_arrival is None                       # consumed


def test_the_old_scene_does_not_consume_the_arrival(wired):
    exported, app, asked = wired
    cls = _scene_class(exported)
    scene0, _ = _scene(cls, "room0", camera_gm=(64, 224), marker_gm=(160, 224))
    scene0._raycast_go_seamless("room1", "obj_marker")
    scene0._ext_overlay__raycast_2_5d()
    assert app._raycast_arrival is not None


def test_the_first_frame_is_drawn_from_the_arrival_not_the_authored_start(wired):
    exported, app, asked = wired
    cls = _scene_class(exported)
    scene0, _ = _scene(cls, "room0", camera_gm=(64, 224), marker_gm=(160, 224))
    scene0._raycast_go_seamless("room1", "obj_marker")
    scene1, cam1 = _scene(cls, "room1", camera_gm=AUTHORED, marker_gm=(320, 128))
    drawn = []
    real = scene1._render_raycast
    scene1._render_raycast = lambda: (drawn.append(scene1._raycast_gm_xy(cam1) + (cam1.facing_angle,)), real())[1]
    scene1._ext_overlay__raycast_2_5d()
    assert drawn == [(224.0, 128.0, 40.0)]                    # never (64, 64, ...)


@pytest.mark.parametrize("kwargs", [{"with_marker": False}, {"with_camera": False}])
def test_a_missing_piece_in_the_new_room_arrives_at_its_start(wired, kwargs):
    exported, app, asked = wired
    cls = _scene_class(exported)
    scene0, _ = _scene(cls, "room0", camera_gm=(64, 224), marker_gm=(160, 224))
    scene0._raycast_go_seamless("room1", "obj_marker")
    scene1, cam1 = _scene(cls, "room1", camera_gm=AUTHORED, marker_gm=(320, 128), **kwargs)
    before = (cam1.x, cam1.y, cam1.facing_angle)
    scene1._ext_overlay__raycast_2_5d()
    assert (cam1.x, cam1.y, cam1.facing_angle) == before
    assert app._raycast_arrival is None


@pytest.mark.parametrize("kwargs, room", [({"with_marker": False}, "room1"), ({"with_camera": False}, "room1"),
                                          ({}, "nowhere")])
def test_failure_modes_in_the_old_room(wired, kwargs, room):
    exported, app, asked = wired
    cls = _scene_class(exported)
    scene0, _ = _scene(cls, "room0", camera_gm=(64, 224), marker_gm=(160, 224), **kwargs)
    scene0._raycast_go_seamless(room, "obj_marker")
    if room == "nowhere":
        assert asked == [] and app._raycast_arrival is None          # nothing happens
    else:
        assert asked == [("room1", "none")] and app._raycast_arrival is None   # a plain change


# --------------------------------------------------------------- real Kivy

WORKER = ROOT / "tests" / "_real_kivy_teleport.py"


def test_real_kivy_the_new_scene_is_built_with_the_arrival_applied(tmp_path):
    from test_raycast_seamless_teleport import _project
    game, cls0 = _real_export(lambda proj: _project(proj), tmp_path)
    text1 = (game / "scenes" / "room1.py").read_text(encoding="utf-8")
    cls1 = next(l.split("class ")[1].split("(")[0] for l in text1.splitlines()
                if l.startswith("class ") and "(Widget)" in l)
    work = Path(tempfile.mkdtemp(prefix="teleport_kivy_"))
    res = work / "result.json"
    try:
        proc = subprocess.run([sys.executable, str(WORKER), str(game), str(res),
                               "scenes.room0", cls0, "scenes.room1", cls1],
                              capture_output=True, text=True, timeout=240)
    except subprocess.TimeoutExpired:
        pytest.skip("real Kivy worker timed out")
    if not res.exists():
        pytest.skip(f"real Kivy cannot run here (exit {proc.returncode}): {proc.stderr[-300:]}")
    data = json.loads(res.read_text(encoding="utf-8"))
    if data["error"] and any(s in data["error"] for s in ("No module named 'kivy'", "GL", "Window")):
        pytest.skip("real Kivy cannot open a window here: " + data["error"][-200:])
    assert data["error"] is None, data["error"]
    assert data["asked"] == [["room1", "none"]] and data["consumed"] and data["pending"]
    r0, r1 = data["room0"], data["room1"]
    # The offset from the marker is kept, in the author's y-down space (rooms are the same height here).
    assert r1["x"] - r1["marker"][0] == pytest.approx(r0["x"] - r0["marker"][0])
    assert r1["y"] - r1["marker"][1] == pytest.approx(r0["y"] - r0["marker"][1])
    assert r1["facing"] == 40.0                          # carried, not room1's authored 90
    assert (r1["hspeed"], r1["vspeed"]) == (2.0, -1.0)
    assert r1["eye_floor"] == 12.0
    assert r1["overlay_instructions"]                    # the first overlay frame was drawn
