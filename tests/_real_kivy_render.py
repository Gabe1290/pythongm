"""Worker for tests/test_kivy_microbit_real_render.py -- run as a SUBPROCESS, never imported by pytest.

Renders draw-queue commands through the REAL generated ``objects/base_object.py`` (the code an
Android build runs) into a real Kivy ``Fbo`` on a hidden window, and writes the pixels at the
requested points. It runs in its own process because creating a Kivy window can fail or crash
(no GL, no display): the test then skips instead of taking pytest down.

    python _real_kivy_render.py <game_dir> <request.json> <result.json>

request:  {"scenes": [{"name", "w", "h", "commands": [...], "points": {name: [x, y_down]}}]}
result:   {"kivy": version, "errors": [...], "scenes": {name: {point: [r, g, b, a]}}}
"""
import json
import os
import sys

game_dir, request_path, result_path = sys.argv[1:4]
os.chdir(game_dir)
sys.path.insert(0, game_dir)
os.environ["KIVY_NO_ARGS"] = "1"

result = {"kivy": None, "errors": [], "scenes": {}}
try:
    from kivy.config import Config
    Config.set("graphics", "window_state", "hidden")
    Config.set("graphics", "width", "320")
    Config.set("graphics", "height", "240")
    Config.set("graphics", "resizable", "0")
    Config.set("kivy", "log_level", "error")
    import kivy
    from kivy.core.window import Window  # noqa: F401  (creates the GL context)
    from kivy.graphics import ClearBuffers, ClearColor, Fbo, InstructionGroup
    result["kivy"] = kivy.__version__

    import importlib
    base = importlib.import_module("objects.base_object")
    inst = base.GameObject.__new__(base.GameObject)      # _dq_render_cmd needs no widget state

    request = json.load(open(request_path, encoding="utf-8"))
    for scene in request["scenes"]:
        w, h = int(scene["w"]), int(scene["h"])
        group = InstructionGroup()
        for cmd in scene["commands"]:
            try:
                inst._dq_render_cmd(group, cmd, h)
            except Exception as exc:                      # a command that fails must show up
                result["errors"].append("%s: %s: %s" % (cmd.get("type"), type(exc).__name__, exc))
        fbo = Fbo(size=(w, h))
        with fbo:
            ClearColor(250 / 255.0, 0, 250 / 255.0, 1)
            ClearBuffers()
        fbo.add(group)
        fbo.draw()
        pixels = fbo.pixels                               # RGBA, rows bottom-up
        out = {}
        for name, (x, y) in scene["points"].items():
            x, y = int(x), int(y)
            if 0 <= x < w and 0 <= y < h:
                i = ((h - 1 - y) * w + x) * 4
                out[name] = list(pixels[i:i + 4])
        result["scenes"][scene["name"]] = out
except Exception as exc:
    import traceback
    result["fatal"] = "%s: %s" % (type(exc).__name__, exc)
    result["trace"] = traceback.format_exc()[-1500:]

json.dump(result, open(result_path, "w", encoding="utf-8"))
