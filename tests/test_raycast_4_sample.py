"""raycast_4 sample — the DOOM-status-bar showcase (DOOM HUD Unit 6).

raycast_4 is the first sample built AROUND a permanent bottom status bar: a
shrunk (letterboxed) 3D view via enable_raycast_view's viewport_height, with a
draw_doom_hud bar filling the reserved band — health bar + a health-reactive
face, score, lives, and a key counter. obj_person is both the camera AND the HUD
drawer, so the key count is its own instance variable (portable across targets).

Runs through the REAL GameRunner.run() loop (the 2026-07-17 startup lesson).
"""
import json
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT))
sys.path.insert(0, str(REPO_ROOT / "tools"))

import os
os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")
import pygame  # noqa: E402

SAMPLE = REPO_ROOT / "samples" / "raycast_4"
PROJECT = str(SAMPLE / "project.json")


def _runner():
    from runtime.game_runner import GameRunner
    runner = GameRunner(PROJECT)
    runner.language = "en"
    for attr in ("show_message_dialog", "show_highscore_dialog",
                 "process_pending_messages"):
        setattr(runner, attr, lambda *a, **k: None)
    runner._show_name_entry_dialog = lambda *a, **k: ""
    return runner


def _run(runner, hook=None, max_frames=8):
    from runtime.game_runner import GameInstance
    real = GameInstance._process_draw_queue
    seen = []

    def spy(self, screen):
        if self.object_name == "obj_person":
            seen.clear()
            seen.extend(self._draw_queue)
        self._draw_queue = []

    GameInstance._process_draw_queue = spy
    state = {"f": 0}

    class _Clock:
        def tick(self, fps=0):
            state["f"] += 1
            if hook:
                hook(state["f"], runner)
            if state["f"] >= max_frames:
                runner.running = False
            return 0

        def get_fps(self):
            return 60.0

    real_clock = pygame.time.Clock
    pygame.time.Clock = _Clock
    try:
        result = runner.run()
    finally:
        pygame.time.Clock = real_clock
        GameInstance._process_draw_queue = real
    return result, seen


# --- Geometry / generator --------------------------------------------------

def test_room_matches_the_generator():
    import gen_raycast_4_maze as gen
    built = gen.build_room()
    shipped = json.loads((SAMPLE / "rooms" / "room0.json").read_text(encoding="utf-8"))
    assert built["instances"] == shipped["instances"], \
        "room0.json drifted from tools/gen_raycast_4_maze.py"


def test_room_contents():
    room = json.loads((SAMPLE / "rooms" / "room0.json").read_text(encoding="utf-8"))
    kinds = {}
    for i in room["instances"]:
        kinds[i["object_name"]] = kinds.get(i["object_name"], 0) + 1
    assert kinds["obj_person"] == 1
    assert kinds["obj_goal"] == 1
    assert kinds["obj_key"] == 3
    assert kinds["obj_monster"] == 4
    # No separate camera/HUD object — obj_person is both.
    assert "obj_cam0" not in kinds and "obj_hud" not in kinds


# --- The letterbox + bar ---------------------------------------------------

def test_person_enables_a_shrunk_viewport():
    person = json.loads((SAMPLE / "objects" / "obj_person.json").read_text(encoding="utf-8"))
    create = person["events"]["create"]["actions"]
    erv = next(a for a in create if a["action"] == "enable_raycast_view")
    assert int(erv["parameters"]["viewport_height"]) == 400, "expected a letterboxed view"
    # obj_person is visible, so its draw event runs in the HUD pass.
    assert person["visible"] is True
    draw = [a["action"] for a in person["events"]["draw"]["actions"]]
    assert "draw_doom_hud" in draw


def test_doom_bar_renders_over_the_shrunk_view():
    runner = _runner()
    result, seen = _run(runner)
    assert result is not False
    cfg = runner.current_room.raycast_camera
    assert cfg["enabled"] is True
    assert cfg["viewport_height"] == 400
    kinds = {c.get("type") for c in seen}
    # The bar emits every one of these each frame.
    assert {"rectangle", "line", "text", "sprite", "lives"} <= kinds, \
        f"DOOM bar did not fully render; saw {sorted(kinds)}"
    # The face is a multi-frame sprite with a subimage.
    face = next(c for c in seen if c.get("type") == "sprite")
    assert face["sprite_name"] == "spr_face"
    assert "subimage" in face


def test_bar_is_bottom_aligned_in_the_reserved_band():
    runner = _runner()
    _, seen = _run(runner)
    win_h = runner.window_height
    panel = next(c for c in seen if c["type"] == "rectangle")
    # y<0 auto-aligns the 80px bar to the window bottom, i.e. the reserved band.
    assert panel["y2"] == win_h
    assert panel["y1"] == win_h - 80


# --- Mechanics -------------------------------------------------------------

def test_face_subimage_tracks_health():
    """The whole point of the sample: the portrait reacts to damage."""
    runner = _runner()

    def hurt(f, r):
        room = r.current_room
        if not room:
            return
        p = next((i for i in room.instances if i.object_name == "obj_person"), None)
        mons = [i for i in room.instances if i.object_name == "obj_monster"]
        # Touch a monster on frames 5/40/80 (each past the 45-step invuln),
        # driving health 100 -> 75 -> 50 -> 25 and the face through its frames.
        if p and mons and f in (5, 60, 120):
            p.x, p.y = mons[0].x, mons[0].y
        elif p and f - 1 in (5, 60, 120):
            p.x, p.y = 8, 8

    frames_at = {}

    def cap(f, r):
        hurt(f, r)

    from runtime.game_runner import GameInstance
    real = GameInstance._process_draw_queue

    def spy(self, screen):
        if self.object_name == "obj_person":
            face = [c for c in self._draw_queue if c.get("type") == "sprite"]
            if face:
                frames_at[state["f"]] = (r_box["r"].health, face[0]["subimage"])
        self._draw_queue = []

    r_box = {"r": runner}
    state = {"f": 0}

    class _Clock:
        def tick(self, fps=0):
            state["f"] += 1
            hurt(state["f"], runner)
            if state["f"] >= 150:
                runner.running = False
            return 0

        def get_fps(self):
            return 60.0

    GameInstance._process_draw_queue = spy
    real_clock = pygame.time.Clock
    pygame.time.Clock = _Clock
    try:
        runner.run()
    finally:
        pygame.time.Clock = real_clock
        GameInstance._process_draw_queue = real

    # Collect (health -> frame) pairs actually observed.
    seen = {hp: fr for hp, fr in frames_at.values()}
    assert seen.get(100) == 0, seen
    assert seen.get(75.0) == 1, seen
    assert seen.get(50.0) == 2, seen
    # Health strictly drove the face down through its frames.
    assert seen.get(25.0, 3) == 3, seen


def test_collecting_a_key_scores_and_counts():
    runner = _runner()

    def grab(f, r):
        room = r.current_room
        if not room:
            return
        p = next((i for i in room.instances if i.object_name == "obj_person"), None)
        keys = [i for i in room.instances if i.object_name == "obj_key"]
        if p and keys and f == 3:
            p.x, p.y = keys[0].x, keys[0].y
        elif p and f == 4:
            p.x, p.y = 8, 8

    _run(runner, hook=grab, max_frames=10)
    player = next(i for i in runner.current_room.instances
                  if i.object_name == "obj_person")
    remaining = [i for i in runner.current_room.instances
                 if i.object_name == "obj_key"]
    assert getattr(player, "keys", 0) == 1, "key count did not increment"
    assert runner.score == 25, "key pickup did not score"
    assert len(remaining) == 2, "collected key was not destroyed"


# --- Indoor look: ceiling instead of sky, taller walls ---------------------

def test_uses_a_ceiling_not_a_sky():
    """raycast_4 is the "maze in a building" sample: it casts a ceiling texture
    and has no panning sky, unlike raycast_1-3."""
    person = json.loads((SAMPLE / "objects" / "obj_person.json").read_text(encoding="utf-8"))
    erv = next(a for a in person["events"]["create"]["actions"]
               if a["action"] == "enable_raycast_view")
    assert erv["parameters"]["ceiling_texture"] == "spr_ceiling"
    assert erv["parameters"]["sky_texture"] == "", "raycast_4 should not use a sky"
    # the ceiling art ships and the sky art was dropped
    assert (SAMPLE / "sprites" / "spr_ceiling.png").exists()
    assert not (SAMPLE / "sprites" / "spr_sky.png").exists()
    proj = json.loads((SAMPLE / "project.json").read_text(encoding="utf-8"))
    assert "spr_ceiling" in proj["assets"]["sprites"]
    assert "spr_sky" not in proj["assets"]["sprites"]


def test_walls_render_taller_globally():
    """The taller-wall look is a global engine default (RAYCAST_WALL_HEIGHT),
    so it applies here too — a sanity tie to the constant."""
    from runtime.game_runner import GameRoom
    assert GameRoom.RAYCAST_WALL_HEIGHT == 1.5
