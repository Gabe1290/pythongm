"""samples/raycast_5 ("Stairs" / « Les escaliers »), docs/RAYCAST_STAIRS_PLAN.md S12.

The committed files must match tools/gen_raycast_5_stairs.py, and the level
must really play through the real GameRunner: walking straight ahead climbs
the staircase onto the gallery (the view easing up), the gallery leads to the
goal, and the monster turns back at the pillar it cannot climb.
"""
import os
import sys
from pathlib import Path

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")

import pytest

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "tools"))

from conftest import skip_without_pygame  # noqa: E402

pytestmark = skip_without_pygame

import pygame  # noqa: E402

import gen_raycast_5_stairs as gen  # noqa: E402

SAMPLE = ROOT / "samples" / "raycast_5"


def test_the_committed_files_match_the_generator():
    assert gen.check(SAMPLE) == []


def test_every_sprite_file_is_there():
    for name in gen.sprites():
        assert (SAMPLE / "sprites" / f"{name}.png").is_file(), name


def test_the_level_has_what_the_guide_promises():
    objs = gen.objects()
    heights = {name: next(a["parameters"]["height"] for a in o["events"]["create"]["actions"]
                          if a["action"] == "set_floor_height")
               for name, o in objs.items() if name.startswith("obj_step_")}
    assert heights == {"obj_step_8": "8", "obj_step_16": "16", "obj_step_24": "24",
                       "obj_step_32": "32", "obj_step_48": "48"}
    create = objs["obj_person"]["events"]["create"]["actions"][0]["parameters"]
    assert create["wall_height"] == "3" and create["max_step"] == "12"
    assert not any(o["solid"] for n, o in objs.items() if n.startswith("obj_step_"))


def _play(script, frames):
    from runtime.game_runner import GameRunner
    from extensions.raycast_2_5d.state import raycast_state
    runner = GameRunner(str(SAMPLE / "project.json"))
    runner.language = "en"
    messages = []
    runner.show_message_dialog = lambda *a, **k: messages.append(a[0] if a else "")
    runner.process_pending_messages = lambda *a, **k: None
    trace = []
    state = {"f": 0}

    class _Clock:
        def tick(self, fps=0):
            f = state["f"] = state["f"] + 1
            for at, kind, key in script:          # [(frame, KEYDOWN/KEYUP, key)]
                if f == at:
                    pygame.event.post(pygame.event.Event(kind, key=key))
            room = runner.current_room
            p = next((i for i in room.instances if i.object_name == "obj_person"), None)
            m = next((i for i in room.instances if i.object_name == "obj_monster"), None)
            if p is not None:
                trace.append({"x": p.x, "y": p.y, "z": getattr(p, "raycast_floor_z", None),
                              "eye": raycast_state(room).get("eye_floor"),
                              "mx": m.x if m is not None else None})
            if f >= frames or messages:
                runner.running = False
            return 0

        def get_fps(self):
            return 30.0

    real = pygame.time.Clock
    pygame.time.Clock = _Clock
    try:
        assert runner.run() is not False
    finally:
        pygame.time.Clock = real
    return trace, messages


def test_walking_ahead_climbs_the_stairs_onto_the_gallery():
    trace, _ = _play([(5, pygame.KEYDOWN, pygame.K_UP)], 130)
    zs = [t["z"] for t in trace if t["z"] is not None]
    assert 8.0 in zs and 16.0 in zs and 24.0 in zs and zs[-1] == 32.0
    eyes = [t["eye"] for t in trace if t["eye"] is not None]
    assert eyes[-1] == 32.0
    assert all(0 <= b - a <= 2.0 + 1e-9 for a, b in zip(eyes, eyes[1:]))


def test_the_gallery_leads_to_the_goal():
    """North up the stairs to the north wall, a quarter turn right (30
    frames of 3 degrees), then east along the gallery to the flag."""
    _, messages = _play([(5, pygame.KEYDOWN, pygame.K_UP),
                         (125, pygame.KEYUP, pygame.K_UP),
                         (125, pygame.KEYDOWN, pygame.K_RIGHT),
                         (155, pygame.KEYUP, pygame.K_RIGHT),
                         (155, pygame.KEYDOWN, pygame.K_UP)], 400)
    assert messages == ["You climbed the stairs and reached the goal!"]


def test_the_monster_turns_back_at_the_pillar():
    trace, _ = _play([], 120)
    xs = [t["mx"] for t in trace if t["mx"] is not None]
    pillar_x = gen.PILLAR[0] * gen.CELL
    assert max(xs) + 16 < pillar_x                    # its centre never on the pillar
    turn = xs.index(max(xs))
    assert xs[-1] < max(xs) - 20 and turn < len(xs) - 5


def test_registered_in_the_welcome_tab_the_smoke_run_and_french():
    welcome = (ROOT / "widgets" / "welcome_tab.py").read_text(encoding="utf-8")
    assert '("samples/raycast_5", "2.5 D — Level 5")' in welcome
    smoke = (ROOT / "tools" / "smoke_run_samples.py").read_text(encoding="utf-8")
    assert '"raycast_5"' in smoke
    fr = (ROOT / "translations" / "pygm2_fr.ts").read_text(encoding="utf-8")
    assert "<source>2.5 D — Level 5</source>" in fr and "2.5 D — Niveau 5" in fr


def test_the_french_guide_has_its_accents():
    text = (SAMPLE / "README.fr.md").read_text(encoding="utf-8")
    for word in ("première", "hauteur", "marche", "éditeur", "à", "fonctionne", "État"):
        assert word in text, word
    assert "premiere" not in text and "editeur" not in text
