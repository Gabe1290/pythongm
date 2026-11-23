"""Worker for tests/test_kivy_mouse_check.py -- run as a SUBPROCESS, never imported by pytest.

Builds a room scene of a generated Kivy export under REAL Kivy on a hidden window, sends the scene
real ``on_touch_down`` / ``on_touch_up`` calls and asks a real instance's ``_mouse_check``.

    python _real_kivy_mouse.py <game_dir> <module> <class> <result.json>
"""
import json
import os
import sys
import types

game_dir, module, cls, result_path = sys.argv[1:5]
os.chdir(game_dir)
sys.path.insert(0, game_dir)
os.environ["KIVY_NO_ARGS"] = "1"
# pytest's conftest sets SDL_VIDEODRIVER=dummy for pygame and the child inherits it; Kivy's SDL2 window has
# no GL under that driver (Window comes back None). This process needs the real one.
if os.environ.get("SDL_VIDEODRIVER") == "dummy":
    del os.environ["SDL_VIDEODRIVER"]
result = {"error": None}
try:
    from kivy.config import Config
    Config.set("graphics", "window_state", "hidden")
    Config.set("graphics", "width", "640")
    Config.set("graphics", "height", "480")
    Config.set("kivy", "log_level", "error")
    from kivy.core.window import Window
    import importlib
    importlib.import_module("main")
    scene = getattr(importlib.import_module(module), cls)()
    Window.add_widget(scene)

    sprited = [i for i in scene.instances if i.has_sprite]
    inst = sprited[0]
    other = next(i for i in sprited if i is not inst and (abs(i.x - inst.x) > 64 or abs(i.y - inst.y) > 64))
    cx, cy = inst.x + inst.image_width / 2.0, inst.y + inst.image_height / 2.0
    ox, oy = other.x + other.image_width / 2.0, other.y + other.image_height / 2.0

    # The window need not match the room, and the scene rescales a touch into room coordinates:
    # send the WINDOW position of a room point, as a real finger would be.
    sx = Window.width / float(getattr(scene, "display_width", 0) or scene.width)
    sy = Window.height / float(getattr(scene, "display_height", 0) or scene.height)

    def touch(x, y, button=None):
        x, y = x * sx, y * sy
        t = types.SimpleNamespace(x=x, y=y, pos=(x, y))
        if button:
            t.button = button
        return t

    check = inst._mouse_check
    result["idle"] = [check("Left button pressed"), check("Over object")]
    t = touch(cx, cy)                                   # a touchscreen touch: no button attribute
    scene.on_touch_down(t)
    result["down_left"] = [check("Left button pressed"), check("Right button pressed"),
                           check("Over object"), other._mouse_check("Over object")]
    scene.on_touch_up(t)
    result["up_left"] = [check("Left button pressed"), check("Over object")]     # the pointer stays
    r = touch(ox, oy, "right")
    scene.on_touch_down(r)
    result["down_right_elsewhere"] = [check("Right button pressed"), check("Over object"),
                                      other._mouse_check("Over object"), other._mouse_check("Right button pressed")]
    scene.on_touch_up(r)
    scene.on_touch_down(touch(cx, cy, "scrollup"))      # a scroll tick is not a held button
    result["scroll"] = [check("Left button pressed"), check("Right button pressed"), check("Middle button pressed")]
    result["region"] = check("In region")
    # Hover: the window's mouse position moves with no button down (a desktop build). Nothing is
    # touched here, so the pointer can only have come from the scene's mouse_pos binding.
    Window.mouse_pos = (cx * sx, cy * sy)
    result["hover_first"] = [check("Over object"), other._mouse_check("Over object"), check("Left button pressed")]
    Window.mouse_pos = (ox * sx, oy * sy)
    result["hover_other"] = [check("Over object"), other._mouse_check("Over object")]
except Exception:
    import traceback
    result["error"] = traceback.format_exc()[-1800:]
json.dump(result, open(result_path, "w", encoding="utf-8"))
