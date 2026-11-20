"""Climbing stairs in the raycast view (docs/RAYCAST_STAIRS_PLAN.md, S8).

extensions/raycast_2_5d/climbing.py, driven by the extension frame hooks:
a move that would raise an instance's floor by more than max_step is undone
one axis at a time (slide along the ledge), going down is always allowed, a
move longer than a cell (a teleport) is never undone, and the camera's view
height eases instead of snapping. Unit tests call the two hooks around a
hand-made move; the end-to-end tests run authored projects through the real
GameRunner with the keyboard held down.
"""
import json
import os
import sys
from pathlib import Path

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")

import pytest

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT))
sys.path.insert(0, str(Path(__file__).resolve().parent))  # for sibling test import

from conftest import skip_without_pygame  # noqa: E402

pytestmark = skip_without_pygame

import pygame  # noqa: E402
pygame.init()

from runtime.game_runner import GameInstance  # noqa: E402
from extensions.raycast_2_5d import climbing  # noqa: E402
from extensions.raycast_2_5d.climbing import (  # noqa: E402
    before_step, after_collision, CLIMB_SPEED, FALL_GRAVITY,
)
from extensions.raycast_2_5d.state import raycast_state  # noqa: E402
from extensions.raycast_2_5d.renderer import (  # noqa: E402
    render_raycast_view, stairs_y, RAYCAST_EYE_HEIGHT,
)
from events.action_types import get_action_type  # noqa: E402
from events.plugin_loader import load_all_plugins  # noqa: E402
from test_raycast_view import _room, _solid_instance  # noqa: E402
from test_raycast_stairs_render import _step  # noqa: E402

load_all_plugins()

CELL = 32


class _Runner:
    def __init__(self, room):
        self.current_room = room


def _mover(name, x, y):
    inst = GameInstance(name, x, y, {}, action_executor=None)
    inst._cached_object_data = {"solid": False}
    inst._cached_width = inst._cached_height = 32
    return inst


def _scene(steps, **cfg):
    """A room with steps {(gx, gy): h} and the camera obj_person at cell (2, 7)."""
    room = _room(480, 480)
    for (gx, gy), h in steps.items():
        room.instances.append(_step(gx * CELL, gy * CELL, h))
    cam = _mover("obj_person", 2 * CELL, 7 * CELL)
    room.instances.append(cam)
    camera = {"enabled": True, "camera_object": "obj_person", "cell_size": CELL,
              "wall_height": 3}
    camera.update(cfg)
    raycast_state(room)["camera"] = camera
    return _Runner(room), room, cam


def _move(runner, inst, dx, dy):
    before_step(runner)
    inst.x += dx
    inst.y += dy
    after_collision(runner)


# ---------------------------------------------------------------- the rule

class TestStepRule:
    def test_an_8px_step_is_climbed(self):
        runner, _, cam = _scene({(3, 7): 8.0})
        _move(runner, cam, 16, 0)                      # centre moves into cell 3
        assert (cam.x, cam.y) == (80, 224)
        assert cam.raycast_floor_z == 8.0 and cam.raycast_step_blocked == 0

    def test_a_16px_block_stops_you_like_a_wall(self):
        runner, _, cam = _scene({(3, 7): 16.0})
        _move(runner, cam, 16, 0)
        assert (cam.x, cam.y) == (64, 224)
        assert cam.raycast_floor_z == 0.0 and cam.raycast_step_blocked == 1

    def test_the_rule_is_relative_to_where_you_stand(self):
        """From the 8-px step, the 16-px one is only 8 higher: climbed."""
        runner, _, cam = _scene({(2, 7): 8.0, (3, 7): 16.0})
        _move(runner, cam, 16, 0)
        assert cam.raycast_floor_z == 16.0 and cam.raycast_step_blocked == 0

    def test_you_slide_along_a_ledge(self):
        """Moving diagonally into a too-high block keeps the free axis."""
        runner, _, cam = _scene({(3, 7): 16.0, (3, 8): 16.0})
        _move(runner, cam, 16, 6)
        assert (cam.x, cam.y) == (64, 230)
        assert cam.raycast_step_blocked == 1

    def test_walking_off_a_ledge_is_always_allowed(self):
        runner, _, cam = _scene({(2, 7): 32.0})
        _move(runner, cam, 16, 0)
        assert (cam.x, cam.y) == (80, 224) and cam.raycast_floor_z == 0.0

    def test_a_teleport_is_never_undone(self):
        runner, _, cam = _scene({(9, 7): 32.0})
        _move(runner, cam, 7 * CELL, 0)                # Jump to Position, say
        assert cam.x == 9 * CELL and cam.raycast_floor_z == 32.0
        assert cam.raycast_step_blocked == 0

    def test_max_step_comes_from_the_camera(self):
        runner, _, cam = _scene({(3, 7): 16.0}, max_step=20)
        _move(runner, cam, 16, 0)
        assert cam.x == 80

    def test_monsters_obey_it_too(self):
        """D4: every moving non-solid instance, not just the camera."""
        runner, room, _ = _scene({(6, 3): 16.0})
        monster = _mover("obj_monster", 4 * CELL, 3 * CELL)
        room.instances.append(monster)
        _move(runner, monster, 20, 0)
        assert monster.x == 4 * CELL + 20 and monster.raycast_step_blocked == 0  # cell 5: free
        monster.x = 5 * CELL
        _move(runner, monster, 20, 0)
        assert monster.x == 5 * CELL and monster.raycast_step_blocked == 1

    def test_solid_instances_and_steps_are_not_movers(self):
        runner, room, _ = _scene({(3, 7): 16.0})
        wall = _solid_instance("obj_wall", 0, 0)
        room.instances.append(wall)
        before_step(runner)
        tracked = {id(i) for i, _x, _y in raycast_state(room)["step_prev"]}
        assert id(wall) not in tracked
        assert not any(getattr(i, "raycast_floor_height", None) is not None
                       for i in room.instances if id(i) in tracked)

    def test_nothing_happens_without_an_enabled_camera(self):
        runner, room, cam = _scene({(3, 7): 16.0})
        raycast_state(room)["camera"] = {"enabled": False}
        _move(runner, cam, 16, 0)
        assert cam.x == 80 and not hasattr(cam, "raycast_step_blocked")


# ------------------------------------------------------------ the view height

class TestEyeEasing:
    def test_first_frame_snaps_then_rises_at_climb_speed(self):
        runner, room, cam = _scene({(2, 7): 8.0, (3, 7): 16.0})
        st = raycast_state(room)
        _move(runner, cam, 0, 0)
        assert st["eye_floor"] == 8.0                  # first frame: no easing
        _move(runner, cam, 16, 0)
        seen = [st["eye_floor"]]
        for _ in range(6):
            _move(runner, cam, 0, 0)
            seen.append(st["eye_floor"])
        assert seen[:4] == [8 + CLIMB_SPEED, 8 + 2 * CLIMB_SPEED,
                            8 + 3 * CLIMB_SPEED, 16.0]
        assert seen[-1] == 16.0

    def test_falls_with_gravity(self):
        runner, room, cam = _scene({(2, 7): 32.0})
        st = raycast_state(room)
        _move(runner, cam, 0, 0)
        _move(runner, cam, 16, 0)                      # off the ledge
        heights = [st["eye_floor"]]
        for _ in range(20):
            _move(runner, cam, 0, 0)
            heights.append(st["eye_floor"])
        drops = [a - b for a, b in zip([32.0] + heights, heights)]
        falling = [d for d in drops if d > 0]
        assert falling[0] == pytest.approx(FALL_GRAVITY)
        assert all(b > a for a, b in zip(falling, falling[1:-1]))   # accelerating
        assert heights[-1] == 0.0 and st["eye_vz"] == 0.0

    def test_the_renderer_draws_from_the_eased_height(self):
        """Mid-climb (eye_floor 4 on an 8-px step), the far wall's base is
        drawn from eye 4 + 24, not from the step's 8 + 24."""
        runner, room, cam = _scene({(2, 7): 8.0})
        for gy in range(15):
            room.instances.append(_solid_instance("w", 9 * CELL, gy * CELL))
        cam.facing_angle = 0.0
        raycast_state(room)["camera"].update({
            "fov": 66, "render_distance": 20, "columns": 480,
            "wall_color": "#ff0000", "floor_color": "#00ff00",
            "ceiling_color": "#0000ff", "wall_textured": False})
        raycast_state(room)["eye_floor"] = 4.0
        screen = pygame.Surface((480, 480))
        render_raycast_view(room, screen)
        base = max(y for y in range(480) if screen.get_at((240, y))[:3] != (0, 255, 0)
                   and screen.get_at((240, y))[0] > 0)
        expected = stairs_y(0, 4 + RAYCAST_EYE_HEIGHT * CELL, 6.5 * CELL, 240, 480)
        assert abs(base - expected) <= 1.5, (base, expected)


def test_max_step_parameter_registered():
    at = get_action_type("enable_raycast_view")
    p = next(p for p in at.parameters if p.name == "max_step")
    assert p.param_type == "number" and p.default_value == 12 and p.required is False


def test_the_hooks_are_registered_by_the_extension():
    from runtime import extension_hooks
    names = {(f.__name__, phase) for f, phase in extension_hooks.get_frame_updates()}
    assert ("before_step", "before_step") in names
    assert ("after_collision", "after_collision") in names


# ------------------------------------------------- end to end, real game loop

def _write_project(root, steps, extra_objects=None, extra_instances=(), person_x=64):
    (root / "sprites").mkdir()
    surf = pygame.Surface((32, 32))
    surf.fill((128, 128, 128))
    pygame.image.save(surf, str(root / "sprites" / "spr_block.png"))
    sprite = {"name": "spr_block", "asset_type": "sprite",
              "file_path": "sprites/spr_block.png", "width": 32, "height": 32,
              "origin_x": 0, "origin_y": 0, "frames": 1, "frame_width": 32,
              "frame_height": 32, "animation_type": "single", "speed": 10.0}

    def obj(name, solid, events):
        return {"name": name, "asset_type": "object", "sprite": "spr_block",
                "visible": True, "solid": solid, "persistent": False,
                "depth": 0, "events": events}

    objects = {
        "obj_wall": obj("obj_wall", True, {}),
        "obj_person": obj("obj_person", False, {
            "create": {"actions": [{"action": "enable_raycast_view", "parameters": {
                "camera_object": "", "cell_size": "32", "wall_height": "3",
                "wall_textured": "false"}}]},
            "keyboard": {"up": {"actions": [{"action": "set_direction_speed",
                                             "parameters": {"direction": "facing_angle",
                                                            "speed": "3"}}]},
                         "nokey": {"actions": [{"action": "set_direction_speed",
                                                "parameters": {"direction": "facing_angle",
                                                               "speed": "0"}}]}},
            "collision_with_obj_wall": {"actions": [], "target_object": "obj_wall"}}),
    }
    instances = []
    for g in range(15):
        for (x, y) in ((g, 0), (g, 14), (0, g), (14, g)):
            instances.append({"object_name": "obj_wall", "x": x * 32, "y": y * 32})
    for h in sorted(set(steps.values())):
        name = "obj_step_%d" % int(h)
        objects[name] = obj(name, False, {"create": {"actions": [
            {"action": "set_floor_height", "parameters": {"height": str(int(h))}}]}})
    for (gx, gy), h in steps.items():
        instances.append({"object_name": "obj_step_%d" % int(h), "x": gx * 32, "y": gy * 32})
    objects.update(extra_objects or {})
    instances.extend(extra_instances)
    instances.append({"object_name": "obj_person", "x": person_x, "y": 224})
    project = {
        "name": "climb_e2e", "version": "1.0",
        "settings": {"window_width": 480, "window_height": 480, "room_speed": 30},
        "assets": {"sprites": {"spr_block": sprite}, "sounds": {}, "backgrounds": {},
                   "objects": objects, "scripts": {}, "fonts": {}, "data": {},
                   "rooms": {"room0": {"name": "room0", "asset_type": "room",
                                       "width": 480, "height": 480,
                                       "background_color": "#000000",
                                       "instances": instances, "tiles": []}}},
    }
    (root / "project.json").write_text(json.dumps(project), encoding="utf-8")
    return root / "project.json"


def _run(project, frames, hold_up=True, on_frame=None):
    from runtime.game_runner import GameRunner
    runner = GameRunner(str(project))
    runner.language = "en"
    runner.show_message_dialog = lambda *a, **k: None
    runner.process_pending_messages = lambda *a, **k: None
    state = {"frames": 0}

    class _FakeClock:
        def tick(self, fps=0):
            state["frames"] += 1
            if state["frames"] == 2 and hold_up:
                pygame.event.post(pygame.event.Event(pygame.KEYDOWN, key=pygame.K_UP))
            if on_frame:
                on_frame(runner, state["frames"])
            if state["frames"] >= frames:
                runner.running = False
            return 0

        def get_fps(self):
            return 30.0

    real_clock = pygame.time.Clock
    pygame.time.Clock = _FakeClock
    try:
        assert runner.run() is not False
    finally:
        pygame.time.Clock = real_clock
    return runner


def _person(runner):
    return next(i for i in runner.current_room.instances if i.object_name == "obj_person")


def test_walking_up_a_staircase_onto_a_platform(tmp_path):
    steps = {(x, 7): 8.0 * (x - 2) for x in range(3, 7)}       # 8, 16, 24, 32
    steps.update({(x, 7): 32.0 for x in range(7, 10)})          # the platform
    eyes = []
    runner = _run(_write_project(tmp_path, steps), 70,
                  on_frame=lambda r, f: eyes.append(
                      raycast_state(r.current_room).get("eye_floor")))
    person = _person(runner)
    assert person.raycast_floor_z == 32.0
    assert person.x > 7 * CELL                                  # reached the platform
    seen = [e for e in eyes if e is not None]
    assert seen[-1] == 32.0
    rises = [b - a for a, b in zip(seen, seen[1:])]
    assert all(0 <= r <= CLIMB_SPEED + 1e-9 for r in rises)     # eased, never snapped


def test_a_block_too_high_stops_the_player(tmp_path):
    runner = _run(_write_project(tmp_path, {(5, 7): 16.0}), 60)
    person = _person(runner)
    assert person.x + 16 < 5 * CELL                             # centre never entered
    assert person.raycast_step_blocked == 1                     # still pushing
    assert person.raycast_floor_z == 0.0


def test_a_monster_turns_back_at_a_block(tmp_path):
    """A patrolling monster reads raycast_step_blocked in End Step and
    reverses -- it is neither stuck nor walking up the block."""
    monster = {"name": "obj_monster", "asset_type": "object", "sprite": "spr_block",
               "visible": True, "solid": False, "persistent": False, "depth": 0,
               "events": {
                   "create": {"actions": [{"action": "set_hspeed",
                                           "parameters": {"speed": "2"}}]},
                   "end_step": {"actions": [
                       {"action": "test_variable", "parameters": {
                           "variable": "raycast_step_blocked", "value": "1",
                           "scope": "instance", "operation": "equal"}},
                       {"action": "reverse_horizontal", "parameters": {}}]}}}
    xs = []
    runner = _run(_write_project(
        tmp_path, {(8, 3): 16.0}, extra_objects={"obj_monster": monster},
        extra_instances=[{"object_name": "obj_monster", "x": 4 * 32, "y": 3 * 32}]),
        90, hold_up=False,
        on_frame=lambda r, f: xs.append(next(
            i.x for i in r.current_room.instances if i.object_name == "obj_monster")))
    assert max(xs) + 16 < 8 * CELL                              # never on the block
    turn = xs.index(max(xs))
    assert xs[-1] < max(xs) - 20 and turn < len(xs) - 10        # and walked back
