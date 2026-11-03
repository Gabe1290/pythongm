"""The Thymio ground sensors look at the FLOOR, not at the robot's own body.

A robot's ground sensors sit under its shell, and the shell is drawn on the very screen the simulator sampled, so
every reading was the off-white body (about 988) and a black line or a table edge was invisible: any "follow the
line" / "do not fall off the table" program silently did nothing. The overlay now keeps a copy of each frame taken
before the first robot is drawn (``state.remember_floor``) and the frame update samples that copy; the playground
window samples a copy of its arena taken before the robots are drawn.
"""
import ast
import json
import os
import sys
import tempfile
from pathlib import Path

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT))

import pytest

pygame = pytest.importorskip("pygame")


@pytest.fixture(autouse=True)
def _thymio_enabled(monkeypatch):
    from events import plugin_loader
    real = plugin_loader.is_extension_enabled
    monkeypatch.setattr(plugin_loader, "is_extension_enabled",
                        lambda folder, default=True: True if folder == "thymio" else real(folder, default))


def _surface(color, size=(40, 40)):
    s = pygame.Surface(size)
    s.fill(color)
    return s


# --- the helper -----------------------------------------------------------------------------------------

def test_the_first_robot_of_a_frame_takes_the_copy_and_later_robots_do_not():
    from types import SimpleNamespace
    from extensions.thymio import state
    screen = _surface((10, 20, 30))
    a, b = SimpleNamespace(), SimpleNamespace()
    state.remember_floor(a, screen)
    first = state.floor_frame(screen)
    screen.fill((200, 0, 0))                       # robot A's body gets drawn on the screen ...
    state.remember_floor(b, screen)                # ... then robot B asks: it must NOT re-copy the dirty screen
    assert state.floor_frame(screen) is first
    assert first.get_at((5, 5))[:3] == (10, 20, 30)


def test_a_new_frame_takes_a_new_copy():
    from types import SimpleNamespace
    from extensions.thymio import state
    screen = _surface((1, 1, 1))
    a = SimpleNamespace()
    state.remember_floor(a, screen)
    screen.fill((9, 9, 9))                         # next frame: the room is drawn again, robot A comes round again
    state.remember_floor(a, screen)
    assert state.floor_frame(screen).get_at((0, 0))[:3] == (9, 9, 9)


def test_a_copy_of_another_screen_is_never_used():
    from types import SimpleNamespace
    from extensions.thymio import state
    old, new = _surface((5, 5, 5)), _surface((7, 7, 7))
    state.remember_floor(SimpleNamespace(), old)
    assert state.floor_frame(new) is new           # a different game's stale copy is ignored
    state.remember_floor(SimpleNamespace(), new)   # and a new screen replaces it, even for the same robot
    assert state.floor_frame(new).get_at((0, 0))[:3] == (7, 7, 7)


# --- through the real engine ------------------------------------------------------------------------------

def _run_project(background, with_black_patch):
    """A robot driving right at speed 40 over `background`; returns [(x, ground_delta_left)] per frame."""
    from PIL import Image
    from events.plugin_loader import load_all_plugins
    from runtime.game_runner import GameRunner
    from extensions.thymio.state import simulator_of
    root = Path(tempfile.mkdtemp(prefix="thy_floor_"))
    (root / "sprites").mkdir()
    Image.new("RGB", (100, 100), (0, 0, 0)).save(root / "sprites" / "spr_black.png")
    sprite = {"name": "spr_black", "asset_type": "sprite", "file_path": "sprites/spr_black.png", "width": 100,
              "height": 100, "origin_x": 0, "origin_y": 0, "frames": 1, "frame_width": 100, "frame_height": 100,
              "animation_type": "single", "speed": 10.0, "imported": True}
    move = {"action": "thymio_move_forward", "parameters": {"speed": "40"}}
    objects = {
        "thymio_bot": {"name": "thymio_bot", "asset_type": "object", "sprite": "", "visible": True, "solid": False,
                       "is_thymio": True, "events": {"create": {"actions": [move]}}},
        "obj_black": {"name": "obj_black", "asset_type": "object", "sprite": "spr_black", "visible": True,
                      "solid": False, "events": {}},
    }
    instances = [{"object_name": "thymio_bot", "x": 100, "y": 300, "visible": True}]
    if with_black_patch:
        instances.append({"object_name": "obj_black", "x": 260, "y": 250, "visible": True})   # covers x 260..360
    (root / "objects").mkdir()
    for name, obj in objects.items():
        (root / "objects" / f"{name}.json").write_text(json.dumps(obj), encoding="utf-8")
    room = {"name": "room0", "asset_type": "room", "width": 800, "height": 600, "background_color": background,
            "instances": instances, "tiles": []}
    (root / "rooms").mkdir()
    (root / "rooms" / "room0.json").write_text(json.dumps(room), encoding="utf-8")
    project = {"name": "floor", "version": "1.0", "settings": {"window_width": 800, "window_height": 600,
                                                              "room_speed": 60, "active_extensions": ["thymio"]},
               "assets": {"sprites": {"spr_black": sprite}, "sounds": {}, "backgrounds": {}, "objects": objects,
                          "rooms": {"room0": {**room, "instances": [], "_external_file": "rooms/room0.json"}},
                          "scripts": {}, "fonts": {}, "data": {}}}
    (root / "project.json").write_text(json.dumps(project), encoding="utf-8")

    load_all_plugins()
    pygame.init()
    runner = GameRunner(str(root / "project.json"))
    seen = []
    real = pygame.time.Clock

    class Clock:
        n = 0

        def tick(self, fps=0):
            Clock.n += 1
            bot = next(i for i in runner.current_room.instances if i.object_name == "thymio_bot")
            sim = simulator_of(bot)
            seen.append((sim.x, sim.sensors.ground_delta[0]))
            if Clock.n >= 200:
                pygame.event.post(pygame.event.Event(pygame.QUIT))
            return 16

        def get_fps(self):
            return 60.0
    pygame.time.Clock = Clock
    try:
        runner.run()
    finally:
        pygame.time.Clock = real
    return seen[10:]                              # let the first frames fill the floor copy


def test_a_mid_grey_floor_is_read_as_the_floor_not_as_the_robot_shell():
    """Before the fix this read ~988 (the shell); the floor is (100, 100, 100) -> 400."""
    readings = {value for _x, value in _run_project("#646464", with_black_patch=False)}
    assert readings == {400}


def test_a_black_patch_on_the_floor_is_seen_and_the_floor_around_it_is_not_black():
    seen = _run_project("#ffffff", with_black_patch=True)
    over = [v for x, v in seen if 300 <= x + 40 <= 340]           # the left sensor is ~40 px ahead of the centre
    clear = [v for x, v in seen if x + 40 < 240]
    assert over and max(over) < 100                               # over the black patch: dark
    assert clear and min(clear) > 900                             # white floor before it: light


# --- the playground window ----------------------------------------------------------------------------------

def _method(name):
    path = REPO_ROOT / "extensions" / "thymio" / "playground_runner.py"
    source = path.read_text(encoding="utf-8")
    for node in ast.walk(ast.parse(source)):
        if isinstance(node, ast.FunctionDef) and node.name == name:
            return ast.get_source_segment(source, node)
    raise AssertionError(name)


def test_the_playground_copies_the_arena_before_drawing_the_robots_and_samples_the_copy():
    render = _method("_render")
    assert render.index("self._floor_surface = surface.copy()") < render.index("self._draw_robot(surface, inst)")
    assert render.index("_draw_wall") < render.index("self._floor_surface = surface.copy()")      # walls are floor
    tick = _method("_tick")
    assert '"_floor_surface"' in tick and "sim.update(dt, self.obstacles, floor" in tick


def test_the_frame_update_and_the_overlay_use_the_helpers():
    runtime = (REPO_ROOT / "extensions" / "thymio" / "runtime.py").read_text(encoding="utf-8")
    assert "sim.update(dt, obstacles, floor_frame(game_runner.screen))" in runtime
    init = (REPO_ROOT / "extensions" / "thymio" / "__init__.py").read_text(encoding="utf-8")
    draw = init[init.index("def draw_robot"):init.index("PLUGIN_INSTANCE_OVERLAYS")]
    assert draw.index("remember_floor(instance, screen)") < draw.index(".render(screen")   # copy BEFORE the body
