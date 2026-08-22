"""Desktop: draw_text/draw_scaled_text's halign/valign must be captured at
QUEUE time (when the action runs), not read from the instance at RENDER
time — a real bug the promo game's hub screen hit as soon as it used two
different alignments in one draw event.

A draw event's actions all run first (building up instance._draw_queue),
and _process_draw_queue renders the WHOLE queue only after every action
has finished. So an event shaped like:

    set_draw_font(halign="center")
    draw_text("Title")
    set_draw_font(halign="left")
    draw_text("Badge")

used to render BOTH lines left-aligned: _align_text_pos read
self.draw_halign at render time, which by then only reflected the LAST
set_draw_font call in the event, no matter which alignment was active
when each draw_text actually ran. On the hub this meant the centered
title rendered flush-left instead, wide enough to collide with the
top-right score total drawn right after it.

Fix: execute_draw_text_action/execute_draw_scaled_text_action now stash
getattr(instance, 'draw_halign'/'draw_valign', ...) into the queued
command itself; _align_text_pos takes halign/valign as explicit
parameters, and _draw_text/_draw_scaled_text pass them from the command,
not from self.
"""
import os
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT))

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")


class _FakeInstance:
    def __init__(self):
        self.x = 0
        self.y = 0
        self.object_name = "test"


def _executor():
    from runtime.action_executor import ActionExecutor
    return ActionExecutor(game_runner=None), _FakeInstance()


def test_draw_text_captures_halign_at_queue_time_not_render_time():
    ex, inst = _executor()

    ex.execute_set_draw_font_action(inst, {"halign": "center"})
    ex.execute_draw_text_action(inst, {"text": "Title", "x": 240, "y": 12})
    ex.execute_set_draw_font_action(inst, {"halign": "left"})
    ex.execute_draw_text_action(inst, {"text": "Badge", "x": 355, "y": 8})

    assert inst._draw_queue[0]["halign"] == "center"
    assert inst._draw_queue[1]["halign"] == "left"
    # The instance's CURRENT halign (what render-time-reading would have
    # used for BOTH commands) is 'left' — proving the queued values differ
    # from it for the first command, i.e. they were genuinely captured
    # earlier, not read live off the instance.
    assert inst.draw_halign == "left"


def test_draw_scaled_text_also_captures_halign_at_queue_time():
    ex, inst = _executor()

    ex.execute_set_draw_font_action(inst, {"halign": "right"})
    ex.execute_draw_scaled_text_action(inst, {"text": "R", "x": 100, "y": 20})
    ex.execute_set_draw_font_action(inst, {"halign": "left"})

    assert inst._draw_queue[0]["halign"] == "right"


def test_align_text_pos_uses_the_passed_alignment_not_the_instance():
    import pygame
    pygame.init()
    pygame.display.set_mode((1, 1))
    from runtime.game_runner import GameInstance

    inst = GameInstance.__new__(GameInstance)
    # Simulate the render-time state after a draw event that ended on
    # 'left' — the exact scenario that broke before this fix.
    inst.draw_halign = "left"
    inst.draw_valign = "top"

    x, y = inst._align_text_pos(240, 12, width=100, height=20, halign="center", valign="top")
    assert x == 240 - 50  # centered per the PASSED halign, ignoring self.draw_halign


def test_end_to_end_no_overlap_between_a_centered_title_and_a_left_aligned_badge():
    """Reproduces the actual promo-game hub bug end to end: a draw event
    that centers a title then switches back to left alignment for a badge
    must not collide the two."""
    import pygame
    pygame.init()
    pygame.display.set_mode((1, 1))
    from runtime.game_runner import GameInstance

    ex, inst = _executor()
    ex.execute_set_draw_font_action(inst, {"halign": "center"})
    ex.execute_draw_text_action(inst, {"text": "Création de jeux vidéo", "x": 240, "y": 12})
    ex.execute_set_draw_font_action(inst, {"halign": "left"})
    ex.execute_draw_text_action(inst, {"text": "Total :", "x": 355, "y": 8})

    real_inst = GameInstance.__new__(GameInstance)
    real_inst._font_cache = {}
    real_inst.draw_font = None
    font = real_inst._resolve_draw_font()

    title_cmd = inst._draw_queue[0]
    total_cmd = inst._draw_queue[1]

    title_surf = font.render(title_cmd["text"], True, (0, 0, 0))
    tx, _ = real_inst._align_text_pos(
        title_cmd["x"], title_cmd["y"], title_surf.get_width(), title_surf.get_height(),
        title_cmd["halign"], title_cmd["valign"])
    title_right_edge = tx + title_surf.get_width()

    total_surf = font.render(total_cmd["text"], True, (0, 0, 0))
    total_x, _ = real_inst._align_text_pos(
        total_cmd["x"], total_cmd["y"], total_surf.get_width(), total_surf.get_height(),
        total_cmd["halign"], total_cmd["valign"])

    assert title_right_edge <= total_x


if __name__ == "__main__":
    import pytest
    raise SystemExit(pytest.main([__file__, "-q"]))
