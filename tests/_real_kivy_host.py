"""Worker for tests/test_kivy_multiplayer_host.py -- run as a SUBPROCESS, never imported by pytest.

Builds a room scene of a generated Kivy export under REAL Kivy on a hidden window and HOSTS from it: the
export's ``mp_lan.glue`` starts the desktop host session, a real desktop client (the IDE's own
NetworkSession) joins over 127.0.0.1, and a real ``obj_person`` (real sprite, real widget) is created with
``network_spawn`` and replicated. The scene's own ``update`` -> extension hook -> glue path runs.

    python _real_kivy_host.py <game_dir> <repo_root> <result.json>
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
    import mp_lan.glue as glue
    glue.host(0, "Prof", 4, False)
    client = NetworkSession(mode="client", host="127.0.0.1", port=glue._session.bound_port, player_name="Ada")
    client.start()

    def tick(n):
        for _ in range(n):
            client.pump_before_step()
            scene.update(1.0 / 60.0)
            client.pump_after_update()
            time.sleep(0.004)

    tick(40)
    caller = scene.instances[0] if scene.instances else scene.create_instance('obj_ctrl', 0, 0)   # a real widget to act as the caller
    spawned = glue.network_spawn(caller, "obj_person", 96, 64, 1)
    result["spawned"] = None if spawned is None else {
        "object": spawned.object_name, "x": float(spawned.x),
        "gm_y": float(scene.room_height) - float(spawned.y) - float(spawned.image_height),
        "owner": spawned._net_owner, "has_sprite": bool(spawned.has_sprite)}
    creates, end = [], time.monotonic() + 3
    while time.monotonic() < end and not creates:
        tick(2)
        creates += client.take_ghost_changes()[0]
    result["client_saw"] = [list(c) for c in creates]
    result["client_owner"] = client.ghost_owner(creates[0][0]) if creates else None
    result["player_count"] = glue._session.player_count
    glue.leave(scene)
except Exception:
    import traceback
    result["error"] = traceback.format_exc()[-1800:]
json.dump(result, open(result_path, "w", encoding="utf-8"))
