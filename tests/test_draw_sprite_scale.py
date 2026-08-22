"""draw_sprite gained an optional uniform `scale` parameter (the promo
game's hub screen needed to shrink each level's icon to make room for a
per-level score readout). Added to both engines, mirroring the existing
`scale` parameter draw_lives already supports (same pygame.transform.scale
pattern on desktop).

Desktop: execute_draw_sprite_action (runtime/action_executor.py) queues
`scale` from parameters (default 1.0); GameInstance._draw_sprite
(runtime/game_runner.py) applies it via pygame.transform.scale before
blitting, for both single-frame and multi-frame (subimage-cropped)
sprites.

HTML5: the `draw_sprite` action case now queues `scale` (and — a
pre-existing, unrelated gap fixed in passing — `subimage`, which the
action case never forwarded into the draw-queue command even though the
render side already read it) via parseNumParam; the `'sprite'` render
case multiplies the drawImage destination width/height by it.
"""
import re
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT))

ENGINE = (REPO_ROOT / "export" / "HTML5" / "templates" / "engine.js").read_text(encoding="utf-8")


# ---------------------------------------------------------------------------
# Desktop
# ---------------------------------------------------------------------------

def test_desktop_draw_sprite_action_queues_scale():
    import os
    os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
    from runtime.action_executor import ActionExecutor

    class FakeInstance:
        def __init__(self):
            self.x = 0
            self.y = 0
            self.object_name = "test"

    ex = ActionExecutor(game_runner=None)
    inst = FakeInstance()
    ex.execute_draw_sprite_action(inst, {"sprite": "spr_x", "x": 1, "y": 2, "scale": 0.8})
    assert inst._draw_queue[-1]["scale"] == 0.8


def test_desktop_draw_sprite_action_defaults_scale_to_one():
    from runtime.action_executor import ActionExecutor

    class FakeInstance:
        def __init__(self):
            self.x = 0
            self.y = 0
            self.object_name = "test"

    ex = ActionExecutor(game_runner=None)
    inst = FakeInstance()
    ex.execute_draw_sprite_action(inst, {"sprite": "spr_x", "x": 1, "y": 2})
    assert inst._draw_queue[-1]["scale"] == 1.0


def test_desktop_draw_sprite_renderer_scales_the_blitted_surface():
    import os
    os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
    import pygame
    pygame.init()
    pygame.display.set_mode((1, 1))
    from runtime.game_runner import GameInstance

    class FakeSprite:
        def __init__(self, w, h):
            self.frames = []
            self.surface = pygame.Surface((w, h), pygame.SRCALPHA)

    class FakeRunner:
        def __init__(self):
            self.sprites = {"spr_x": FakeSprite(96, 96)}

    class FakeExecutor:
        def __init__(self, runner):
            self.game_runner = runner

    inst = GameInstance.__new__(GameInstance)
    inst.action_executor = FakeExecutor(FakeRunner())

    scaled = {}
    real_scale = pygame.transform.scale

    def spy_scale(surface, size):
        scaled["size"] = size
        return real_scale(surface, size)

    pygame.transform.scale = spy_scale
    try:
        screen = pygame.Surface((300, 300), pygame.SRCALPHA)
        inst._draw_sprite(screen, {"sprite_name": "spr_x", "x": 0, "y": 0, "scale": 0.8})
    finally:
        pygame.transform.scale = real_scale

    assert scaled["size"] == (76, 76)  # int(96 * 0.8)


def test_desktop_draw_sprite_renderer_skips_scaling_at_1_0():
    import os
    os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
    import pygame
    pygame.init()
    pygame.display.set_mode((1, 1))
    from runtime.game_runner import GameInstance

    class FakeSprite:
        def __init__(self, w, h):
            self.frames = []
            self.surface = pygame.Surface((w, h), pygame.SRCALPHA)

    class FakeRunner:
        def __init__(self):
            self.sprites = {"spr_x": FakeSprite(96, 96)}

    class FakeExecutor:
        def __init__(self, runner):
            self.game_runner = runner

    inst = GameInstance.__new__(GameInstance)
    inst.action_executor = FakeExecutor(FakeRunner())

    calls = []
    real_scale = pygame.transform.scale
    pygame.transform.scale = lambda *a: (calls.append(a), real_scale(*a))[1]
    try:
        screen = pygame.Surface((300, 300), pygame.SRCALPHA)
        inst._draw_sprite(screen, {"sprite_name": "spr_x", "x": 0, "y": 0, "scale": 1.0})
    finally:
        pygame.transform.scale = real_scale

    assert calls == []  # unscaled path never calls pygame.transform.scale


# ---------------------------------------------------------------------------
# HTML5 (engine.js source-level, per this repo's no-Node-in-CI convention)
# ---------------------------------------------------------------------------

def test_html5_draw_sprite_action_queues_scale_and_subimage():
    m = re.search(r"case 'draw_sprite':(.*?)break;", ENGINE, re.S)
    assert m
    body = m.group(1)
    assert "scale: parseNumParam(params.scale, this, 1.0)" in body
    assert "subimage: parseNumParam(params.subimage, this, 0)" in body


def test_html5_sprite_render_applies_scale_to_both_paths():
    case = ENGINE[ENGINE.index("case 'sprite': {"):]
    case = case[:case.index("case 'lives'")]
    assert "const scale = cmd.scale || 1;" in case
    # multi-frame (cropped) destination size scales
    assert "fw * scale, fh * scale" in case
    # single-frame path scales too, but only when scale !== 1 (perf/no-op guard)
    assert "img.width * scale, img.height * scale" in case
    assert "scale !== 1" in case


if __name__ == "__main__":
    import pytest
    raise SystemExit(pytest.main([__file__, "-q"]))
