"""Generate the illustrations for Tutorial 16's student handout
(docs/handouts/16_fruit_basket/images).

Two real screenshots, both reused unchanged between the English and French
handouts (neither shows language-specific IDE chrome -- the room canvas is
just coloured shapes, and the one piece of in-game text, the score caption,
is a minor, low-risk simplification rather than a language mismatch worth
doubling the image set for), same technique as
tools/gen_tutorial_15_handout_images.py:

* A Room Editor screenshot -- a real (offscreen) RoomCanvas widget loaded
  with build_t16's own project data (phase 2: basket + fruit + bombs, no
  behaviour yet).
* A real gameplay screenshot of the win room -- the actual pygame surface
  GameRunner renders, captured after scripting the basket onto the last
  fruit.

Run: python tools/gen_tutorial_16_handout_images.py
"""
import importlib.util
import json
import os
import sys
import tempfile
from pathlib import Path

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")
os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
OUT = ROOT / "docs" / "handouts" / "16_fruit_basket"

_spec = importlib.util.spec_from_file_location("trp", ROOT / "tools" / "tutorial_reference_projects.py")
trp = importlib.util.module_from_spec(_spec)
sys.modules["trp"] = trp
_spec.loader.exec_module(trp)


def _room_screenshot(phase, out_name):
    from PySide6.QtWidgets import QApplication
    from editors.room_editor.room_canvas import RoomCanvas

    app = QApplication.instance() or QApplication([])
    path = trp.build_t16(Path(tempfile.mkdtemp()), phase)
    project_data = json.loads(path.read_text(encoding="utf-8"))
    room = project_data["assets"]["rooms"]["room_main"]

    canvas = RoomCanvas()
    canvas.set_room_properties(
        room.get("width", 640), room.get("height", 480),
        room.get("background_color", "#cfe8ff"), "", False, False, 0.0, 0.0, True, [])
    canvas.set_project_info(str(path.parent), project_data)
    canvas.load_instances(room.get("instances", []))
    canvas.show()
    app.processEvents()
    canvas.grab().save(str(OUT / out_name))
    print("wrote", out_name)


def _play(path, script, frames):
    import pygame
    from runtime.game_runner import GameRunner
    runner = GameRunner(str(path))
    runner.language = "en"
    runner.show_message_dialog = lambda *a, **k: None
    seen = {"frame": 0, "runner": runner}

    class Clock:
        def tick(self, fps=0):
            seen["frame"] += 1
            script(seen["frame"], runner, seen)
            if seen["frame"] >= frames:
                runner.running = False
            return 0

        def get_fps(self):
            return 60.0

    real = pygame.time.Clock
    pygame.time.Clock = Clock
    try:
        runner.run()
    finally:
        pygame.time.Clock = real
    return seen


def _gameplay_win_screen(out_name):
    import pygame
    path = trp.build_t16(Path(tempfile.mkdtemp()), 4, fruit_xs=trp.T16_FRUIT_XS[:1])

    def script(f, r, seen):
        if f == 1:
            insts = [i for i in r.current_room.instances if i.object_name == "obj_player"]
            insts[0].x = trp.T16_FRUIT_XS[0]       # walk straight onto the one remaining fruit
        if f == 10:
            pygame.image.save(r.screen, str(OUT / out_name))
    _play(path, script, 11)
    print("wrote", out_name)


if __name__ == "__main__":
    OUT.mkdir(parents=True, exist_ok=True)
    _room_screenshot(2, "room_phase2_layout.png")
    _gameplay_win_screen("gameplay_win_screen.png")
    print("done")
