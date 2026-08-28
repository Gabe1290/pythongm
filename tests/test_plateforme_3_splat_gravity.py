"""Regression: plateforme_3's obj_splat fell through the floor forever.

Bug report: after a fast fall, obj_pingus correctly detects the impact
(collision_with_obj_brique's vspeed >= 15 branch) and transforms into
obj_splat via change_instance -- but obj_splat's create event reset
hspeed/vspeed to 0 (start_moving_direction stop/0) and never reset
gravity. change_instance intentionally preserves per-instance motion
state (GM8-faithful semantics -- see the "Preserve motion" comment in
ActionExecutor._change_single_instance), so the splat inherited
obj_pingus's live gravity (0.5, set in obj_pingus's own step event while
airborne) with nothing to zero it again: obj_splat has no step event and
no collision_with_obj_brique handler, so the generic per-frame gravity
application (GameRunner.update) re-accelerated it every frame and the
automatic solid-blocking check never engaged (it requires a registered
collision event between the two object types, which obj_splat/obj_brique
don't have). Result: the "corpse" silently fell through the ground forever
while playing its death animation.

Fix: samples/plateforme_3/objects/obj_splat.json's create event now also
zeroes gravity, in both the standalone file and project.json's embedded
copy (this repo's dual-storage convention -- GameRunner's loader prefers
the standalone file via merge_object_file, but both must stay in lockstep
to avoid a future edit silently drifting).

Verified via the real runtime (matching test_raycast_view.py's
TestRaycast1SampleSmoke harness: a real GameRunner.run() loop with a fake
pygame.time.Clock tick-hook), not a hand-built minimal room -- object data
merging, sprite-derived collision dimensions, and set_object_data all only
happen for real inside a genuine GameRunner run.
"""
from pathlib import Path

import pytest

from conftest import skip_without_pygame

pytestmark = skip_without_pygame

REPO_ROOT = Path(__file__).resolve().parent.parent


def _run_and_capture(max_frames=60, injected_vspeed=20.0):
    import pygame
    from runtime.game_runner import GameRunner

    project_json = str(REPO_ROOT / "samples" / "plateforme_3" / "project.json")
    runner = GameRunner(project_json)
    runner.language = "en"
    runner.show_message_dialog = lambda *a, **k: None
    runner.show_highscore_dialog = lambda *a, **k: None
    runner._show_name_entry_dialog = lambda *a, **k: ""
    runner.process_pending_messages = lambda *a, **k: None

    log = []

    class _FakeClock:
        def __init__(self):
            self.f = 0

        def tick(self, fps=0):
            self.f += 1
            f = self.f
            if f == 1:
                # Simulate a long fast fall: obj_pingus's own step event
                # would have ramped gravity to 0.5 and vspeed up to its
                # 24 clamp over many frames of real freefall -- set that
                # state directly rather than waiting ~50 real frames for
                # it to accumulate.
                pingus = next(i for i in runner.current_room.instances
                              if i.object_name == "obj_pingus")
                pingus.x = 32
                pingus.y = 400
                pingus.vspeed = injected_vspeed
                pingus.gravity = 0.5
                pingus.gravity_direction = 270

            if f <= max_frames:
                splat = next((i for i in runner.current_room.instances
                              if i.object_name == "obj_splat"), None)
                log.append((f, splat.y if splat else None,
                            getattr(splat, 'gravity', None) if splat else None))
            if f >= max_frames:
                runner.running = False
            return 0

        def get_fps(self):
            return 60.0

    real_clock = pygame.time.Clock
    pygame.time.Clock = _FakeClock
    try:
        runner.run()
    finally:
        pygame.time.Clock = real_clock

    return log


def test_obj_splat_json_zeroes_gravity_on_create():
    """Cheap, simulation-independent pin on the actual fix."""
    import json
    for path in [
        REPO_ROOT / "samples" / "plateforme_3" / "objects" / "obj_splat.json",
    ]:
        data = json.loads(path.read_text(encoding="utf-8"))
        actions = data["events"]["create"]["actions"]
        gravity_actions = [a for a in actions if a["action"] == "set_gravity"]
        assert gravity_actions, f"{path.name}: no set_gravity in create event"
        assert float(gravity_actions[0]["parameters"]["gravity"]) == 0.0

    # project.json's embedded copy must stay in lockstep (GameRunner's
    # loader prefers the standalone file, but the embedded one is what the
    # IDE shows/re-saves from until the object is next touched -- a drift
    # here is exactly the class of bug docs/CODE_AUDIT.md's manifest-ify
    # TODO warns about).
    project = json.loads(
        (REPO_ROOT / "samples" / "plateforme_3" / "project.json").read_text(encoding="utf-8")
    )
    embedded = project["assets"]["objects"]["obj_splat"]
    embedded_actions = embedded["events"]["create"]["actions"]
    embedded_gravity = [a for a in embedded_actions if a["action"] == "set_gravity"]
    assert embedded_gravity, "project.json's embedded obj_splat has no set_gravity in create"
    assert float(embedded_gravity[0]["parameters"]["gravity"]) == 0.0


def test_splat_gravity_zeroed_and_stays_put_after_transform():
    log = _run_and_capture(max_frames=60)

    # obj_splat must appear (confirms the fast-fall -> splat transform
    # itself still works) and, once it does, both its gravity must read
    # exactly 0 and its y position must never change again.
    seen_splat = [entry for entry in log if entry[1] is not None]
    assert seen_splat, "obj_splat was never created — fast-fall transform regressed"

    first_y = seen_splat[0][1]
    for f, y, gravity in seen_splat:
        assert gravity == 0.0, f"frame {f}: obj_splat.gravity == {gravity}, expected 0"
        assert y == first_y, (
            f"frame {f}: obj_splat.y moved from {first_y} to {y} — "
            "it is still falling after transforming"
        )


def test_splat_would_have_fallen_without_the_fix():
    """Negative control: prove the harness actually exercises the bug by
    reverting the fix in memory (not on disk) and confirming the old,
    broken behavior reproduces exactly as reported."""
    project_json = str(REPO_ROOT / "samples" / "plateforme_3" / "project.json")

    # Patch the loaded project data post-hoc: strip set_gravity back out
    # of obj_splat's create actions, mirroring the pre-fix file.
    import pygame
    from runtime.game_runner import GameRunner

    runner = GameRunner(project_json)
    runner.language = "en"
    runner.show_message_dialog = lambda *a, **k: None
    runner.show_highscore_dialog = lambda *a, **k: None
    runner._show_name_entry_dialog = lambda *a, **k: ""
    runner.process_pending_messages = lambda *a, **k: None

    splat_data = runner.project_data["assets"]["objects"]["obj_splat"]
    splat_data["events"]["create"]["actions"] = [
        a for a in splat_data["events"]["create"]["actions"]
        if a["action"] != "set_gravity"
    ]

    log = []

    class _FakeClock:
        def __init__(self):
            self.f = 0

        def tick(self, fps=0):
            self.f += 1
            f = self.f
            if f == 1:
                pingus = next(i for i in runner.current_room.instances
                              if i.object_name == "obj_pingus")
                pingus.x = 32
                pingus.y = 400
                pingus.vspeed = 20.0
                pingus.gravity = 0.5
                pingus.gravity_direction = 270
            if f <= 60:
                splat = next((i for i in runner.current_room.instances
                              if i.object_name == "obj_splat"), None)
                log.append(splat.y if splat else None)
            if f >= 60:
                runner.running = False
            return 0

        def get_fps(self):
            return 60.0

    real_clock = pygame.time.Clock
    pygame.time.Clock = _FakeClock
    try:
        runner.run()
    finally:
        pygame.time.Clock = real_clock

    seen = [y for y in log if y is not None]
    assert seen, "obj_splat never appeared in the negative control either"
    assert seen[-1] > seen[0] + 50, (
        "negative control did not reproduce the fall-through — "
        "the test harness itself may no longer exercise the bug"
    )
