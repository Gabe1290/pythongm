"""viewport_height letterbox on enable_raycast_view — desktop (DOOM HUD Unit 1).

The 3D view can be shrunk into a shorter band so a DOOM-style status bar has
room below it. viewport_height 0 (the default) means full height, so every
existing raycast game renders pixel-identical — asserted here, not assumed.

Runs through the REAL GameRunner.run() loop: the raycast path needs
set_sprites_for_instances to have run in run()'s startup (2026-07-17 lesson).
"""
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT))

import os
os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")
import pygame  # noqa: E402

PROJECT = str(REPO_ROOT / "samples" / "raycast_3" / "project.json")
WIN_W, WIN_H = 640, 480


def _loaded_renderer():
    """The renderer module the LOADED extension actually renders through.

    The plugin loader imports a folder extension under a synthetic package name
    (``pygm_extension_<folder>``), so its ``renderer`` submodule is a DIFFERENT
    object from ``extensions.raycast_2_5d.renderer`` imported the normal way.
    The run loop draws through the former, so a spy has to patch that one.
    Requires an extension-loading GameRunner to have been constructed first.
    """
    import importlib
    from runtime import extension_hooks
    for func in extension_hooks.get_room_renderers():
        if "raycast_2_5d" in func.__module__:
            return importlib.import_module(func.__module__ + ".renderer")
    from extensions.raycast_2_5d import renderer as rc   # single-copy fallback
    return rc


def _snapshot_with_viewport(viewport_height, flat=False, no_camera=False):
    """Run raycast_3 a few frames and return a copy of the last raycast frame,
    with viewport_height injected into obj_cam0's enable_raycast_view.

    flat=True clears the wall/sky/floor textures so the ceiling and floor are
    flat colour fills split at the horizon.

    no_camera=True points camera_object at a name that doesn't resolve, so the
    renderer draws ONLY the flat ceiling/floor/reserved-band fills and returns
    before any wall pass. That makes the horizon exactly measurable — the dense
    maze otherwise occludes the fills near the horizon (especially with the
    taller RAYCAST_WALL_HEIGHT walls), defeating a pixel-sampled horizon check.
    """
    from runtime.game_runner import GameRunner

    runner = GameRunner(PROJECT)   # loads the raycast extension
    _rc = _loaded_renderer()
    runner.language = "en"
    for attr in ("show_message_dialog", "show_highscore_dialog",
                 "process_pending_messages"):
        setattr(runner, attr, lambda *a, **k: None)
    runner._show_name_entry_dialog = lambda *a, **k: ""

    cam = runner._objects_data["obj_cam0"]
    act = cam["events"]["create"]["actions"][0]
    assert act["action"] == "enable_raycast_view"
    if viewport_height is not None:
        act["parameters"]["viewport_height"] = str(viewport_height)
    if flat:
        for k in ("wall_texture", "sky_texture", "floor_texture", "ceiling_texture"):
            act["parameters"][k] = ""
    if no_camera:
        act["parameters"]["camera_object"] = "__no_such_camera__"

    shot = {}
    # The renderer moved into the raycast extension (Stage B2); the room is
    # drawn through the extension_hooks seam, so spy on the module function.
    real = _rc.render_raycast_view

    def spy(room, screen):
        real(room, screen)
        shot["surface"] = screen.copy()

    _rc.render_raycast_view = spy
    state = {"f": 0}

    class _Clock:
        def tick(self, fps=0):
            state["f"] += 1
            if state["f"] >= 4:
                runner.running = False
            return 0

        def get_fps(self):
            return 60.0

    real_clock = pygame.time.Clock
    pygame.time.Clock = _Clock
    try:
        runner.run()
    finally:
        pygame.time.Clock = real_clock
        _rc.render_raycast_view = real
    return shot["surface"]


def _row_is_black(surf, y):
    w = surf.get_width()
    return all(surf.get_at((x, y))[:3] == (0, 0, 0) for x in range(0, w, 8))


def _row_has_content(surf, y):
    w = surf.get_width()
    return any(surf.get_at((x, y))[:3] != (0, 0, 0) for x in range(0, w, 8))


def test_default_is_full_height_and_unchanged():
    """viewport_height 0 and == render height both render the full frame, and
    identically — the backward-compat guarantee."""
    a = _snapshot_with_viewport(None)      # no parameter at all
    b = _snapshot_with_viewport(0)         # explicit 0
    h = a.get_height()
    c = _snapshot_with_viewport(h)         # == full height, clamps to same
    w = a.get_width()

    for other, label in ((b, "explicit 0"), (c, "== render height")):
        diff = sum(1 for x in range(0, w, 4) for y in range(0, h, 4)
                   if a.get_at((x, y)) != other.get_at((x, y)))
        assert diff == 0, f"{label} differs from the no-parameter render ({diff} px)"


def test_shrunk_viewport_reserves_a_black_band_below():
    surf = _snapshot_with_viewport(300)
    h = surf.get_height()
    # The reserved band [300, h) is solid black on every sampled row.
    for y in range(305, h, 20):
        assert _row_is_black(surf, y), f"row {y} in the reserved band is not black"
    # And the 3D view above it actually rendered something (walls/sky/floor).
    assert _row_has_content(surf, 150), "no 3D content in the shrunk viewport"


def test_horizon_moves_up_with_the_viewport():
    """With view_h=300 the horizon sits at 150, not h/2. Flat fills (no
    textures) make the ceiling one solid colour above the horizon and the
    floor another below it, so the horizon is where the centre column's colour
    flips."""
    # No camera => only the flat ceiling/floor/band fills draw, so the horizon
    # (view_h/2) is exact and unoccluded by walls.
    full = _snapshot_with_viewport(0, flat=True, no_camera=True)
    short = _snapshot_with_viewport(300, flat=True, no_camera=True)
    FLOOR = (0x46, 0x46, 0x32)      # floor_color #464632
    w = full.get_width()

    def floor_top(surf, view_h):
        """First row (from the top) that is the floor fill = the horizon."""
        for y in range(1, view_h):
            if surf.get_at((w // 2, y))[:3] == FLOOR:
                return y
        return view_h

    hf = floor_top(full, full.get_height())
    hs = floor_top(short, 300)
    assert abs(hf - full.get_height() / 2) <= 1, f"full horizon not centred: {hf}"
    assert abs(hs - 150) <= 1, f"shrunk horizon not at 150: {hs}"
    assert hs < hf - 40, "horizon did not move up when the viewport shrank"


def test_camera_config_carries_viewport_height():
    """Plumbing: the action parameter reaches the room's raycast_camera."""
    from runtime.game_runner import GameRunner

    runner = GameRunner(PROJECT)
    runner.language = "en"
    for attr in ("show_message_dialog", "show_highscore_dialog",
                 "process_pending_messages"):
        setattr(runner, attr, lambda *a, **k: None)
    runner._show_name_entry_dialog = lambda *a, **k: ""
    cam = runner._objects_data["obj_cam0"]
    cam["events"]["create"]["actions"][0]["parameters"]["viewport_height"] = "280"

    state = {"f": 0}

    class _Clock:
        def tick(self, fps=0):
            state["f"] += 1
            if state["f"] >= 3:
                runner.running = False
            return 0

        def get_fps(self):
            return 60.0

    real_clock = pygame.time.Clock
    pygame.time.Clock = _Clock
    try:
        runner.run()
    finally:
        pygame.time.Clock = real_clock
    assert runner.current_room.raycast_camera["viewport_height"] == 280


# --- viewport_height reaches the exported camera config (Units 2/3 gap fix) -
# Units 2/3 made the export RENDERERS read cfg.viewport_height, but the config
# BUILDERS (enable_raycast_view codegen) didn't set it — so an exported game
# ignored viewport_height entirely. Caught while building raycast_4.

def test_export_enable_raycast_view_carries_viewport_height():
    kg = (REPO_ROOT / "export" / "Kivy" / "code_generator.py").read_text(encoding="utf-8")
    eng = (REPO_ROOT / "export" / "HTML5" / "templates" / "engine.js").read_text(encoding="utf-8")
    assert "'viewport_height': int(_tofloat(params.get('viewport_height'), 0))" in kg
    assert "viewport_height: Math.floor(rNum('viewport_height', 0))" in eng


def test_kivy_export_camera_config_includes_viewport_height():
    """End-to-end: a generated object's enable_raycast_view sets the letterbox
    height in the camera dict the scene renderer reads."""
    from export.Kivy.code_generator import ActionCodeGenerator
    g = ActionCodeGenerator(base_indent=0)
    g.process_action({"action": "enable_raycast_view",
                      "parameters": {"viewport_height": "400"}}, "create")
    assert "'viewport_height': 400" in g.get_code()
