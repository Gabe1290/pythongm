"""draw_doom_hud — DOOM-style status bar macro action (DOOM HUD Unit 4b).

Like draw_minimap, it's a MACRO action: build_doom_hud_commands() is the single
source of geometry, emitting only rectangle/line/text/sprite/lives commands, so
no target needs a new draw-queue type. The HTML5/Kivy ports mirror it and
test_raycast_export_parity compares against it.
"""
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT))

import os
os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")
import pygame  # noqa: E402

# draw_doom_hud + its builders moved into the raycast extension (Stage B3,
# docs/RAYCAST_EXTENSION_PLAN.md). Load plugins so the schema is merged into
# ACTION_TYPES (the IDE does this at startup; a bare test import does not).
from events.plugin_loader import load_all_plugins  # noqa: E402
load_all_plugins()
from extensions.raycast_2_5d.hud import (  # noqa: E402
    build_doom_hud_commands, doom_face_frame,
)

BASE = dict(
    x=0, y=438, width=640, height=42, health=60, score=1234, lives=3,
    back_color="#101010", divider_color="#505050", text_color="#ffffff",
    health_label="Health", health_bar_width=90, health_bar_height=14,
    bar_color="#20c020", face_sprite="spr_face", face_frames=4,
    score_label="Score: ", lives_sprite="spr_life", lives_scale=1.0,
    objective_value="2", objective_label="Keys: ",
)


# --- Face-frame formula ----------------------------------------------------

def test_face_frame_is_an_even_bucket_map():
    # 4 frames: 0 = healthiest, 3 = dying.
    assert doom_face_frame(100, 4) == 0
    assert doom_face_frame(74, 4) == 1
    assert doom_face_frame(50, 4) == 2
    assert doom_face_frame(25, 4) == 3
    assert doom_face_frame(1, 4) == 3
    assert doom_face_frame(0, 4) == 3
    # clamps out-of-range health, and never returns >= face_frames
    assert doom_face_frame(200, 4) == 0
    assert doom_face_frame(-5, 4) == 3
    assert doom_face_frame(50, 1) == 0        # single-frame face


# --- Builder command set ---------------------------------------------------

def test_builder_emits_the_expected_command_set():
    cmds = build_doom_hud_commands(**BASE)
    types = [c["type"] for c in cmds]
    assert types.count("rectangle") == 3     # back panel + health back + fill
    assert types.count("line") == 1          # top divider
    assert types.count("text") == 4          # health label, number, score, objective
    assert types.count("sprite") == 1        # face
    assert types.count("lives") == 1
    # every command lands inside the bar rect (roughly — text has no width here).
    for c in cmds:
        xs = [c[k] for k in ("x1", "x2", "x") if k in c]
        for xv in xs:
            assert BASE["x"] - 1 <= xv <= BASE["x"] + BASE["width"] + 1, c


def test_health_fill_is_proportional():
    full = build_doom_hud_commands(**{**BASE, "health": 100})
    half = build_doom_hud_commands(**{**BASE, "health": 50})
    zero = build_doom_hud_commands(**{**BASE, "health": 0})

    def fill_width(cmds):
        # the fill is the 3rd rectangle (back panel, bar back, bar fill)
        rects = [c for c in cmds if c["type"] == "rectangle"]
        return rects[2]["x2"] - rects[2]["x1"]

    assert fill_width(full) == BASE["health_bar_width"]
    assert abs(fill_width(half) - BASE["health_bar_width"] / 2) < 1e-9
    assert fill_width(zero) == 0


def test_face_subimage_follows_health():
    for hp, frame in ((100, 0), (60, 1), (40, 2), (10, 3)):
        cmds = build_doom_hud_commands(**{**BASE, "health": hp})
        face = next(c for c in cmds if c["type"] == "sprite")
        assert face["subimage"] == frame, hp
        assert face["sprite_name"] == "spr_face"


def test_no_face_command_when_face_sprite_blank():
    cmds = build_doom_hud_commands(**{**BASE, "face_sprite": ""})
    assert not any(c["type"] == "sprite" for c in cmds)


def test_lives_command_reuses_the_lives_type():
    cmds = build_doom_hud_commands(**BASE)
    lives = next(c for c in cmds if c["type"] == "lives")
    assert lives["count"] == 3
    assert lives["sprite"] == "spr_life"
    assert lives["scale"] == 1.0


def test_objective_and_score_text():
    cmds = build_doom_hud_commands(**BASE)
    texts = [c["text"] for c in cmds if c["type"] == "text"]
    assert "Score: 1234" in texts
    assert "Keys: 2" in texts
    assert "60" in texts                      # health number


# --- Action registration + desktop end-to-end ------------------------------

def test_action_registered_and_handler_from_the_extension():
    """Schema merged into ACTION_TYPES from the extension; handler registered
    onto the executor by load_all_plugins (Stage B3), not an ActionExecutor
    method."""
    from events.action_types import ACTION_TYPES, get_action_type
    from runtime.action_executor import ActionExecutor
    assert "draw_doom_hud" in ACTION_TYPES
    assert get_action_type("draw_doom_hud").category == "3D View"
    ex = ActionExecutor()
    load_all_plugins(ex)
    assert "draw_doom_hud" in ex.action_handlers
    assert not hasattr(ex, "execute_draw_doom_hud_action")


def test_auto_y_aligns_to_the_window_bottom():
    """y < 0 places the bar flush against the bottom of the window."""
    from runtime.game_runner import GameRunner, GameInstance

    project = str(REPO_ROOT / "samples" / "raycast_3" / "project.json")
    runner = GameRunner(project)
    runner.language = "en"
    for attr in ("show_message_dialog", "show_highscore_dialog",
                 "process_pending_messages"):
        setattr(runner, attr, lambda *a, **k: None)
    runner._show_name_entry_dialog = lambda *a, **k: ""

    seen = []
    real = GameInstance._process_draw_queue

    def spy(self, screen):
        if self.object_name == "obj_hud":
            seen.clear()
            seen.extend(self._draw_queue)
        self._draw_queue = []

    runner._objects_data["obj_hud"]["events"]["draw"]["actions"] = [{
        "action": "draw_doom_hud",
        "parameters": {"x": "0", "y": "-1", "height": "40"},
    }]

    state = {"f": 0}

    class _Clock:
        def tick(self, fps=0):
            state["f"] += 1
            if state["f"] >= 5:
                runner.running = False
            return 0

        def get_fps(self):
            return 60.0

    real_clock = pygame.time.Clock
    GameInstance._process_draw_queue = spy
    pygame.time.Clock = _Clock
    try:
        runner.run()
    finally:
        pygame.time.Clock = real_clock
        GameInstance._process_draw_queue = real

    win_h = runner.window_height
    panel = next(c for c in seen if c["type"] == "rectangle")
    assert panel["y1"] == win_h - 40, f"bar not bottom-aligned: y1={panel['y1']}, win_h={win_h}"
    assert panel["y2"] == win_h
    # health/score/lives were pulled from live game state, not defaults.
    kinds = {c["type"] for c in seen}
    assert {"rectangle", "line", "text", "lives"} <= kinds
