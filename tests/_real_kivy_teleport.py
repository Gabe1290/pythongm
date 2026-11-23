"""Worker for tests/test_kivy_raycast_teleport.py -- run as a SUBPROCESS, never imported by pytest.

Real Kivy on a hidden window, the REAL generated scenes of a two-room export: room0's camera runs
``_raycast_go_seamless`` (the generated action's target), then room1's scene is CONSTRUCTED -- exactly
what GameApp._do_room_switch does -- and the camera is read straight after construction, before any
update, i.e. at the first overlay frame the constructor draws.

    python _real_kivy_teleport.py <game_dir> <result.json> <room0_module> <room0_class> <room1_module> <room1_class>
"""
import json
import os
import sys
import types

game_dir, result_path, mod0, cls0, mod1, cls1 = sys.argv[1:7]
os.chdir(game_dir)
sys.path.insert(0, game_dir)
os.environ["KIVY_NO_ARGS"] = "1"
if os.environ.get("SDL_VIDEODRIVER") == "dummy":
    del os.environ["SDL_VIDEODRIVER"]
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")
result = {"error": None}
try:
    from kivy.config import Config
    Config.set("graphics", "window_state", "hidden")
    Config.set("graphics", "width", "480")
    Config.set("graphics", "height", "480")
    Config.set("kivy", "log_level", "error")
    from kivy.core.window import Window  # noqa: F401
    import importlib
    main = importlib.import_module("main")

    def camera_of(scene):
        return next(i for i in scene.instances if i.object_name in ("obj_person", "obj_person_b"))

    asked = []
    app = types.SimpleNamespace(_raycast_arrival=None)
    main._game_app = app
    main.goto_room = lambda name, transition="none": asked.append((name, transition))

    scene0 = getattr(importlib.import_module(mod0), cls0)()
    scene0.room_name = "room0"
    cam0 = camera_of(scene0)
    mk0 = next(i for i in scene0.instances if i.object_name == "obj_marker")
    result["room0"] = {"x": cam0.x, "y": cam0.y, "facing": cam0.facing_angle,
                       "marker": [mk0.x, mk0.y], "room_height": scene0.room_height}
    cam0.hspeed, cam0.vspeed = 2.0, -1.0
    scene0._raycast_eye_floor = 12.0
    scene0._raycast_go_seamless("room1", "obj_marker")
    result["asked"] = asked
    result["pending"] = app._raycast_arrival is not None

    scene1 = getattr(importlib.import_module(mod1), cls1)()        # the constructor draws the first frame
    scene1.room_name = "room1"
    cam1 = camera_of(scene1)
    mk1 = next(i for i in scene1.instances if i.object_name == "obj_marker")
    result["room1"] = {"x": cam1.x, "y": cam1.y, "facing": cam1.facing_angle,
                       "hspeed": cam1.hspeed, "vspeed": cam1.vspeed,
                       "marker": [mk1.x, mk1.y], "room_height": scene1.room_height,
                       "eye_floor": scene1._raycast_eye_floor,
                       "overlay_instructions": len(scene1._raycast_group.children)
                       if getattr(scene1, "_raycast_group", None) is not None else None}
    result["consumed"] = app._raycast_arrival is None
except Exception:
    import traceback
    result["error"] = traceback.format_exc()[-1800:]
json.dump(result, open(result_path, "w", encoding="utf-8"))
