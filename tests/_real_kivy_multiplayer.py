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
    host.push_local_instances([{"nid": nid, "o": "obj_person", "x": 128, "y": 96, "r": 0, "f": 0, "v": True}])

    import mp_lan.glue as glue
    glue.join("127.0.0.1", host.bound_port, "Ada")
    for _ in range(90):
        host.pump_before_step()
        scene.update(1.0 / 60.0)             # the real scene update -> _update_extensions -> glue.update
        host.pump_after_update()
        time.sleep(0.004)
    ghosts = [i for i in scene.instances if getattr(i, "_net_ghost", None) is not None]
    result["ghosts"] = [{"object": g.object_name, "x": float(g.x), "y": float(g.y),
                         "image_height": float(g.image_height), "room_height": float(scene.room_height)}
                        for g in ghosts]
    result["player_id"] = glue._session.player_id        # (main has no GameApp here, so no globals store)
    glue.leave(scene)
    host.close()
except Exception:
    import traceback
    result["error"] = traceback.format_exc()[-1800:]
json.dump(result, open(result_path, "w", encoding="utf-8"))
