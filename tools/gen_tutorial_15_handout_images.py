"""Generate the illustrations for Tutorial 15's student handout
(docs/handouts/15_fruit_fusion/images/).

Two kinds of real screenshot, both reused unchanged between the English and
French handouts (neither shows language-specific IDE chrome -- the room
canvas is just coloured shapes, and the one piece of in-game text, the score
caption, is a minor, low-risk simplification rather than a language mismatch
worth doubling the image set for):

* Room Editor screenshots -- a real (offscreen) RoomCanvas widget loaded
  with build_t15's own project data, via the same technique used by
  tests/test_room_canvas_cache_clear.py (construct RoomCanvas() directly,
  no full IDE window needed).
* Real gameplay screenshots -- the actual pygame surface GameRunner renders,
  captured mid-script the same way tests/test_tutorial_reference_projects.py's
  `play()` helper drives the engine (scripted keypresses / placed fruit,
  frame-counted callback), not the production PYGM_SCREENSHOT hook (which
  has no way to inject input, so the basket would never move).

Run: python tools/gen_tutorial_15_handout_images.py
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
# Flat, alongside the .md files -- build_teacher_wiki.py's image-copy step
# only globs *.png directly in the handout folder, not a subdirectory, and
# Tutorial 1's handout (the only other one with images) already uses this
# same flat layout.
OUT = ROOT / "docs" / "handouts" / "15_fruit_fusion"

_spec = importlib.util.spec_from_file_location("trp", ROOT / "tools" / "tutorial_reference_projects.py")
trp = importlib.util.module_from_spec(_spec)
sys.modules["trp"] = trp
_spec.loader.exec_module(trp)


def _room_screenshot(phase, out_name):
    from PySide6.QtWidgets import QApplication
    from editors.room_editor.room_canvas import RoomCanvas

    app = QApplication.instance() or QApplication([])
    path = trp.build_t15(Path(tempfile.mkdtemp()), phase)
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

    def post(kind, key):
        pygame.event.post(pygame.event.Event(kind, key=key))

    class Clock:
        def tick(self, fps=0):
            seen["frame"] += 1
            script(seen["frame"], post, runner, seen)
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


def _place(path, object_name, x, y):
    data = json.loads(path.read_text(encoding="utf-8"))
    data["assets"]["rooms"]["room_main"]["instances"].append(
        {"object_name": object_name, "x": x, "y": y, "rotation": 0,
         "scale_x": 1.0, "scale_y": 1.0, "visible": True})
    path.write_text(json.dumps(data), encoding="utf-8")
    return path


def _gameplay_moving_basket(out_name):
    import pygame
    path = trp.build_t15(Path(tempfile.mkdtemp()), 1)

    def script(f, post, r, seen):
        if f == 3:
            post(pygame.KEYDOWN, pygame.K_RIGHT)
        if f == 25:
            pygame.image.save(r.screen, str(OUT / out_name))
    _play(path, script, 26)
    print("wrote", out_name)


def _gameplay_first_fusion(out_name):
    import pygame
    path = trp.build_t15(Path(tempfile.mkdtemp()), 2)
    _place(path, "obj_fruit_cherry", 304, 400)

    def script(f, post, r, seen):
        if f == 20:
            pygame.image.save(r.screen, str(OUT / out_name))
    _play(path, script, 21)
    print("wrote", out_name)


def _gameplay_second_fusion(out_name):
    """A cherry resolves first (score 10, basket -> strawberry), then a
    strawberry falls in right after (score 30, basket -> orange) -- a
    realistic cumulative screenshot, not a forced-variable shortcut."""
    import pygame
    path = trp.build_t15(Path(tempfile.mkdtemp()), 3)
    _place(path, "obj_fruit_cherry", 304, 400)
    _place(path, "obj_fruit_strawberry", 150, 0)

    def script(f, post, r, seen):
        if f == 30:
            strawberry = [i for i in r.current_room.instances if i.object_name == "obj_fruit_strawberry"][0]
            strawberry.x, strawberry.y = 304, 400
        if f == 55:
            pygame.image.save(r.screen, str(OUT / out_name))
    _play(path, script, 56)
    print("wrote", out_name)


def _gameplay_win_screen(out_name):
    import pygame
    path = trp.build_t15(Path(tempfile.mkdtemp()), 4)
    _place(path, "obj_fruit_orange", 304, 400)

    def script(f, post, r, seen):
        if f == 1:
            insts = [i for i in r.current_room.instances if i.object_name == "obj_player"]
            insts[0].held_level = 3
        if f == 25:
            pygame.image.save(r.screen, str(OUT / out_name))
    _play(path, script, 26)
    print("wrote", out_name)


if __name__ == "__main__":
    OUT.mkdir(parents=True, exist_ok=True)
    _room_screenshot(1, "room_phase1_basket_only.png")
    _room_screenshot(4, "room_phase4_full.png")
    _gameplay_moving_basket("gameplay_moving_basket.png")
    _gameplay_first_fusion("gameplay_first_fusion.png")
    _gameplay_second_fusion("gameplay_second_fusion.png")
    _gameplay_win_screen("gameplay_win_screen.png")
    print("done")
