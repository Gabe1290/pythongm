"""Worker for tests/test_kivy_multiplayer_lobby.py -- run as a SUBPROCESS, never imported by pytest.

Real Kivy on a hidden window: the export's mp_lan.glue opens the waiting-room overlay for host_game(show_lobby),
a real desktop client joins, the overlay lists it, Démarrer starts the game and removes the overlay; a second room
checks Annuler. Buttons are pressed by dispatching on_release, as a tap would.

    python _real_kivy_lobby.py <game_dir> <repo_root> <result.json>
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


def texts(widget):
    out = []
    for w in widget.walk():
        t = getattr(w, "text", None)
        if isinstance(t, str):
            out.append(t)
    return out


try:
    from kivy.config import Config
    Config.set("graphics", "window_state", "hidden")
    Config.set("graphics", "width", "640")
    Config.set("graphics", "height", "480")
    Config.set("kivy", "log_level", "error")
    from kivy.clock import Clock
    from kivy.core.window import Window
    import importlib
    importlib.import_module("main")
    scene = importlib.import_module("scenes.room0").Room0()
    Window.add_widget(scene)

    from extensions.multiplayer_lan.session import NetworkSession
    import mp_lan.glue as glue

    def overlay():
        return glue._lobby["overlay"] if glue._lobby else None

    def pump(seconds, client=None):
        end = time.monotonic() + seconds
        while time.monotonic() < end:
            Clock.tick()
            if client is not None:
                client.pump_before_step()
                client.pump_after_update()
            time.sleep(0.01)

    def press(label):
        for w in overlay().walk():
            if getattr(w, "text", None) == label and hasattr(w, "dispatch"):
                w.dispatch("on_release")
                return True
        return False

    glue.host(0, "Prof", 4, True, "Lobby test")
    result["opened"] = overlay() is not None and overlay().parent is not None
    result["first_texts"] = texts(overlay())
    client = NetworkSession(mode="client", host="127.0.0.1", port=glue._session.bound_port, player_name="Ada")
    client.start()
    pump(1.5, client)
    result["joined_texts"] = texts(overlay())
    result["started_before"] = glue._session.started
    result["pressed_start"] = press("Démarrer")
    pump(0.3, client)
    result["started_after"] = glue._session.started
    result["closed_after_start"] = glue._lobby is None
    result["client_saw_start"] = any(e[0] == "network_game_started" for e in client.take_events())
    glue.leave(scene)
    client.close()

    glue.host(0, "Prof", 4, True, "Lobby test")
    pump(0.3)
    result["pressed_cancel"] = press("Annuler")
    pump(0.3)
    result["session_after_cancel"] = glue._session is None
    result["closed_after_cancel"] = glue._lobby is None
except Exception:
    import traceback
    result["error"] = traceback.format_exc()[-1800:]
json.dump(result, open(result_path, "w", encoding="utf-8"))
