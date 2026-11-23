"""Worker for tests/test_kivy_multiplayer_client.py -- run as a SUBPROCESS, never imported by pytest.

Builds a room scene of a generated Kivy export under REAL Kivy on a hidden window, starts a real desktop
host (the IDE's own NetworkSession) on 127.0.0.1 with one networked instance, joins it through the
export's ``mp_lan.glue`` and ticks the scene's real ``update`` -- so the generated scene hook, the glue and
real GameObject widgets (sprite, x/y, image_height) all run together.

    python _real_kivy_multiplayer.py <game_dir> <repo_root> <result.json>
"""
import json
import os
import sys
import time

game_dir, repo_root, result_path = sys.argv[1:4]
os.chdir(game_dir)
sys.path.insert(0, game_dir)
sys.path.insert(1, repo_root)
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
    scene = importlib.import_module("scenes.room0").Room0()
    Window.add_widget(scene)

    from extensions.multiplayer_lan.session import NetworkSession
    host = NetworkSession(mode="host", port=0, player_name="Prof")
    host.start()
    nid = host.next_netid()
    host.push_local_instances([{"nid": nid, "o": "obj_person", "x": 128, "y": 96, "r": 0, "f": 0, "v": True,
                                "own": 1}])      # assigned to the phone (player 1): it becomes ITS avatar
    own_rows = []

    import mp_lan.glue as glue
    glue.join("127.0.0.1", host.bound_port, "Ada")
    for _ in range(90):
        host.pump_before_step()
        scene.update(1.0 / 60.0)             # the real scene update -> _update_extensions -> glue.update
        host.pump_after_update()
        time.sleep(0.004)
    ghosts = [i for i in scene.instances if getattr(i, "_net_ghost", None) is not None]
    avatar = ghosts[0]
    result["promoted"] = bool(glue._local) and avatar._net_owner == 1
    result["ghosts"] = [{"object": g.object_name, "x": float(g.x), "y": float(g.y),
                         "image_height": float(g.image_height), "room_height": float(scene.room_height)}
                        for g in ghosts]                  # where the host put it, before the player moves it
    x0 = float(avatar.x)
    scene.keys_pressed[275] = True                      # the right arrow, held (Kivy keycode 275)
    t_end = time.monotonic() + 1.0          # long enough for a refresh of a dropped input (see kivy_glue)
    while time.monotonic() < t_end:
        host.pump_before_step()
        scene.update(1.0 / 60.0)             # the generated avatar step: is_instance_owner + key_pressed right
        own_rows.extend(host.take_own_state().values())
        host.pump_after_update()
        time.sleep(0.004)
    result["held_right"] = host.remote_input(1, "right")
    scene.keys_pressed[275] = False
    t_end = time.monotonic() + 1.0
    while time.monotonic() < t_end:
        host.pump_before_step()
        scene.update(1.0 / 60.0)
        host.pump_after_update()
        time.sleep(0.004)
    result["released_right"] = host.remote_input(1, "right")
    result["own_rows"] = [{"x": r["x"], "y": r["y"], "from": r["_from"]} for r in own_rows]   # the right-arrow phase
    # The vertical keys: the avatar's step does `y = y - 4` for UP. Up is a SMALLER author's y on the
    # wire (down from the top) and a LARGER Kivy y (up from the bottom).
    y_before, rows_before = float(avatar.y), len(own_rows)
    scene.keys_pressed[273] = True                      # the up arrow
    t_end = time.monotonic() + 0.6
    while time.monotonic() < t_end:
        host.pump_before_step()
        scene.update(1.0 / 60.0)
        own_rows.extend(host.take_own_state().values())
        host.pump_after_update()
        time.sleep(0.004)
    scene.keys_pressed[273] = False
    result["up_kivy_y_delta"] = float(avatar.y) - y_before
    result["up_wire_y_before"] = own_rows[rows_before - 1]["y"] if rows_before else None
    result["up_wire_y_after"] = own_rows[-1]["y"]
    result["avatar_moved"] = float(avatar.x) - x0
    result["own_rows_all"] = [{"x": r["x"], "y": r["y"], "from": r["_from"]} for r in own_rows]
    result["player_id"] = glue._session.player_id        # (main has no GameApp here, so no globals store)
    glue.leave(scene)
    host.close()
except Exception:
    import traceback
    result["error"] = traceback.format_exc()[-1800:]
json.dump(result, open(result_path, "w", encoding="utf-8"))
