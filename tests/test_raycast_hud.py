"""Raycast in-view HUD compositing — desktop target (RAYCAST_HUD_PLAN Unit 1).

Before this, GameRoom._render_room did `_render_raycast_view(screen); return`,
so the per-instance draw pass never ran under raycast and a raycast game's HUD
(draw_score / draw_lives / draw_text / draw_health_bar) was invisible — score
and lives showed only in the desktop window caption, and nowhere at all on the
HTML5 / Kivy exports.

Runs through the REAL GameRunner.run() loop: instances don't get
_cached_object_data or sprite-derived sizes until set_sprites_for_instances
runs inside run()'s startup, so a hand-built room would pass for the wrong
reason (2026-07-17 bug-hunt lesson).
"""
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT))

import os
os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")
import pygame  # noqa: E402

PROJECT = str(REPO_ROOT / "samples" / "raycast_2" / "project.json")

# Somewhere the first-person view never paints: raycast_2's sky is drawn over
# the top half and the floor over the bottom, but both stop short of the far
# left column at y=4. Kept small and checked against a pre-HUD baseline below
# rather than assumed empty.
HUD_TEXT = "SCORE 1234"


def _runner():
    from runtime.game_runner import GameRunner
    runner = GameRunner(PROJECT)
    runner.language = "en"
    runner.show_message_dialog = lambda *a, **k: None
    runner.show_highscore_dialog = lambda *a, **k: None
    runner._show_name_entry_dialog = lambda *a, **k: ""
    runner.process_pending_messages = lambda *a, **k: None
    return runner


def _add_hud_draw_event(runner, obj_name="obj_person", visible=True):
    """Give an object a HUD draw event, before run() resolves object_data."""
    obj = runner._objects_data[obj_name]
    obj.setdefault("events", {})["draw"] = {
        "actions": [
            {"action": "set_draw_color", "parameters": {"color": "#ff00ff"}},
            {"action": "draw_text",
             "parameters": {"text": HUD_TEXT, "x": "8", "y": "8"}},
        ]
    }
    obj["visible"] = visible


def _run(runner, max_frames=6):
    state = {"frames": 0}

    class _FakeClock:
        def tick(self, fps=0):
            state["frames"] += 1
            if state["frames"] >= max_frames:
                runner.running = False
            return 0

        def get_fps(self):
            return 60.0

    real = pygame.time.Clock
    pygame.time.Clock = _FakeClock
    try:
        result = runner.run()
    finally:
        pygame.time.Clock = real
    return result, state["frames"]


def _snapshot_last_frame():
    """Copy the screen after each render — the display surface is torn down
    once run() returns, so it can't be read afterwards."""
    from runtime.game_runner import GameRunner
    shot = {}
    real = GameRunner.render

    def spy(self):
        out = real(self)
        if self.screen is not None:
            shot["surface"] = self.screen.copy()
        return out

    GameRunner.render = spy
    return shot, (lambda: setattr(GameRunner, "render", real))


def _record_draw_queue(execute=True):
    """Capture every draw command flushed while the game runs.

    execute=False records without rasterising. Use it when the assertion is
    about *dispatch* — actually rendering text depends on ambient pygame font
    state that other tests in the suite can leave in a bad way ("Text has zero
    width"), which would fail for a reason unrelated to what's under test. The
    pixel test below covers real rasterisation.
    """
    from runtime.game_runner import GameInstance
    seen = []
    real = GameInstance._process_draw_queue

    def spy(self, screen):
        seen.extend(self._draw_queue)
        if execute:
            return real(self, screen)
        self._draw_queue = []

    GameInstance._process_draw_queue = spy
    return seen, (lambda: setattr(GameInstance, "_process_draw_queue", real))


def test_hud_draw_event_runs_under_raycast():
    """The draw event fires at all when the raycast camera is enabled."""
    runner = _runner()
    _add_hud_draw_event(runner)
    seen, restore = _record_draw_queue()
    try:
        result, _ = _run(runner)
    finally:
        restore()

    assert result is not False
    assert runner.current_room.raycast_camera["enabled"] is True, \
        "precondition: this test is meaningless unless raycast is active"
    texts = [c.get("text") for c in seen if c.get("type") == "text"]
    assert HUD_TEXT in texts, \
        f"HUD draw event did not run under raycast; captured: {texts!r}"


def test_hud_pixels_are_composited_over_the_first_person_frame():
    """Not just executed — actually painted on top of the finished frame.

    Compares against a baseline run with no HUD, so this can't pass on a
    pixel the raycast view happened to paint that colour anyway.
    """
    shot, restore = _snapshot_last_frame()
    try:
        _run(_runner())
        baseline = shot["surface"]

        runner = _runner()
        _add_hud_draw_event(runner)
        _run(runner)
        after = shot["surface"]
    finally:
        restore()

    region = pygame.Rect(0, 0, 200, 40)
    changed = sum(
        1
        for x in range(region.width)
        for y in range(region.height)
        if baseline.get_at((x, y)) != after.get_at((x, y))
    )
    assert changed > 0, "no pixels changed in the HUD region — HUD not composited"


def test_invisible_instances_still_skip_their_draw_event():
    """Preserve normal-mode semantics: render() returns early on `not visible`,
    so an invisible instance's draw event never fires. The raycast HUD pass
    must not quietly change that."""
    runner = _runner()
    _add_hud_draw_event(runner, visible=False)
    seen, restore = _record_draw_queue()
    try:
        _run(runner)
    finally:
        restore()

    texts = [c.get("text") for c in seen if c.get("type") == "text"]
    assert HUD_TEXT not in texts, \
        "invisible instance's draw event ran under raycast but not in normal mode"


def test_normal_mode_draw_events_are_unaffected():
    """The refactor split run_draw_event out of render(); the non-raycast path
    must behave exactly as before."""
    runner = _runner()
    _add_hud_draw_event(runner)
    seen, restore = _record_draw_queue(execute=False)
    try:
        _run(runner, max_frames=3)
        # Disable raycast and render once more: the normal top-down path.
        # Its own surface — run() has already torn the display down.
        runner.current_room.raycast_camera["enabled"] = False
        seen.clear()
        runner.current_room.render(pygame.Surface((800, 600)))
    finally:
        restore()

    texts = [c.get("text") for c in seen if c.get("type") == "text"]
    assert HUD_TEXT in texts, "draw event stopped running on the normal path"
