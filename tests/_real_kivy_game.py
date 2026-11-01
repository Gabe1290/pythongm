"""Worker for tests/test_kivy_real_game.py -- run as a SUBPROCESS, never imported by pytest.

Builds ONE room scene of a generated Kivy export (the code an Android build runs) under REAL Kivy on a
hidden window, ticks it, draws a frame and reads the window's pixels back. It runs in its own process
because creating a Kivy window can fail or crash (no GL, no display): the test then skips instead of
taking pytest down.

    python _real_kivy_game.py <game_dir> <request.json> <result.json>

request:  {"module": "scenes.niveau_01", "class": "Niveau01", "frames": 30,
           "track": ["obj_pingus"], "points": {name: [x, y_down]}}
result:   {"kivy": version, "instances": n, "tracked": {object: [[x0, y0], [x1, y1]]},
           "window": [w, h], "colors": distinct sampled colours, "points": {name: [r, g, b, a]},
           "error": traceback or null}
"""
import json
import os
import sys

game_dir, request_path, result_path = sys.argv[1:4]
os.chdir(game_dir)
sys.path.insert(0, game_dir)
os.environ["KIVY_NO_ARGS"] = "1"
request = json.load(open(request_path, encoding="utf-8"))

result = {"kivy": None, "error": None}
try:
    from kivy.config import Config
    Config.set("graphics", "window_state", "hidden")
    Config.set("graphics", "width", str(request.get("width", 640)))
    Config.set("graphics", "height", str(request.get("height", 480)))
    Config.set("graphics", "resizable", "0")
    Config.set("kivy", "log_level", "error")
    import kivy
    from kivy.base import EventLoop
    from kivy.core.window import Window
    result["kivy"] = kivy.__version__

    import importlib
    importlib.import_module("main")                      # the generated main.py: GameApp, ROOM_CLASSES...
    scene = getattr(importlib.import_module(request["module"]), request["class"])()
    Window.add_widget(scene)

    def positions(name):
        return [[float(i.x), float(i.y)] for i in scene.instances if i.object_name == name]

    tracked = {name: [positions(name)] for name in request.get("track", [])}
    for _ in range(int(request.get("frames", 30))):
        scene.update(1.0 / 60.0)
    for name in tracked:
        tracked[name].append(positions(name))
    EventLoop.idle()                                     # let pending Clock work run
    w, h = int(getattr(scene, "display_width", 0) or scene.width), int(getattr(scene, "display_height", 0) or scene.height)
    scene.size = (w, h)
    image = scene.export_as_image()                      # renders the widget's whole canvas (incl. canvas.after)
    texture = image.texture
    w, h = texture.size
    pixels = texture.pixels                              # RGBA, rows bottom-up
    result["window"] = [w, h]
    result["instances"] = len(scene.instances)
    group = getattr(scene, "_raycast_group", None)       # the first-person overlay, when a camera is enabled
    result["raycast_instructions"] = len(group.children) if group is not None else None
    result["tracked"] = tracked
    result["colors"] = len({bytes(pixels[i:i + 4]) for i in range(0, len(pixels), 4 * 53)})
    out = {}
    for name, (x, y) in request.get("points", {}).items():
        x, y = int(x), int(y)
        if 0 <= x < w and 0 <= y < h:
            i = ((h - 1 - y) * w + x) * 4
            out[name] = list(pixels[i:i + 4])
    result["points"] = out
except Exception:
    import traceback
    result["error"] = traceback.format_exc()[-1800:]

json.dump(result, open(result_path, "w", encoding="utf-8"))
