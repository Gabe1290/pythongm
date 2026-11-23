"""Go to Room Seamlessly on desktop (docs/RAYCAST_CEILINGS_TELEPORT_PLAN.md, T1).

Through the real GameRunner loop, on a two-room project: the camera arrives in the second room at
the same offset from the marker object, with the facing, speed and eased view height it had -- and
no frame is ever drawn with the camera at the new room's AUTHORED start (its Create event sets
facing 90 at (64, 64); the carried values must win before the first frame is drawn). The failure
modes are all logged and none is fatal.
"""
import json
import os
import sys
from pathlib import Path

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
sys.path.insert(0, str(Path(__file__).resolve().parent))

from conftest import skip_without_pygame  # noqa: E402

pytestmark = skip_without_pygame

import pygame  # noqa: E402
pygame.init()

from events.plugin_loader import load_all_plugins  # noqa: E402
from extensions.raycast_2_5d.state import raycast_state  # noqa: E402
from test_raycast_climbing import _run  # noqa: E402

load_all_plugins()

AUTHORED_B = (64.0, 64.0)          # room1's camera start
MARKER_A = (160.0, 224.0)          # the marker in room0 (camera starts at (64, 224): offset -96, 0)
MARKER_B = (320.0, 128.0)


def _project(root, *, marker_a=True, marker_b=True, camera=True, target="room1", marker="obj_marker"):
    (root / "sprites").mkdir()
    surf = pygame.Surface((32, 32))
    surf.fill((128, 128, 128))
    pygame.image.save(surf, str(root / "sprites" / "spr_block.png"))
    sprite = {"name": "spr_block", "asset_type": "sprite", "file_path": "sprites/spr_block.png",
              "width": 32, "height": 32, "origin_x": 0, "origin_y": 0, "frames": 1,
              "frame_width": 32, "frame_height": 32, "animation_type": "single", "speed": 10.0}

    def obj(name, solid, events):
        return {"name": name, "asset_type": "object", "sprite": "spr_block", "visible": True,
                "solid": solid, "persistent": False, "depth": 0, "events": events}

    def person(angle):
        create = [{"action": "set_facing_angle", "parameters": {"angle": str(angle)}}]
        if camera:
            create.insert(0, {"action": "enable_raycast_view", "parameters": {
                "camera_object": "", "cell_size": "32", "wall_height": "3",
                "wall_textured": "false"}})
        return create

    # Two objects so each room's camera has its own authored facing angle.
    objects = {
        "obj_wall": obj("obj_wall", True, {}),
        "obj_marker": obj("obj_marker", False, {}),
        "obj_person": obj("obj_person", False, {
            "create": {"actions": person(40)},
            "keyboard_press": {"space": {"actions": [
                {"action": "go_to_room_seamlessly", "parameters": {"room": target, "marker": marker}}]}}}),
        "obj_person_b": obj("obj_person_b", False, {"create": {"actions": person(90)}}),
    }

    def room(name, camera_obj, camera_at, marker_at):
        instances = []
        for g in range(15):
            for (x, y) in ((g, 0), (g, 14), (0, g), (14, g)):
                instances.append({"object_name": "obj_wall", "x": x * 32, "y": y * 32})
        if marker_at is not None:
            instances.append({"object_name": "obj_marker", "x": marker_at[0], "y": marker_at[1]})
        instances.append({"object_name": camera_obj, "x": camera_at[0], "y": camera_at[1]})
        return {"name": name, "asset_type": "room", "width": 480, "height": 480,
                "background_color": "#000000", "instances": instances, "tiles": []}

    project = {
        "name": "seamless", "version": "1.0",
        "settings": {"window_width": 480, "window_height": 480, "room_speed": 30},
        "assets": {"sprites": {"spr_block": sprite}, "sounds": {}, "backgrounds": {},
                   "objects": objects, "scripts": {}, "fonts": {}, "data": {},
                   "rooms": {
                       "room0": room("room0", "obj_person", (64, 224), MARKER_A if marker_a else None),
                       "room1": room("room1", "obj_person_b", AUTHORED_B, MARKER_B if marker_b else None)}},
    }
    (root / "project.json").write_text(json.dumps(project), encoding="utf-8")
    return root / "project.json"


drawn = []                                   # (room, x, y, facing) at each draw call


def _camera(runner):
    room = runner.current_room
    for inst in room.instances:
        if inst.object_name in ("obj_person", "obj_person_b"):
            return inst
    return None


def _play(tmp_path, before_space=None, frames=14, **project_args):
    """Run the loop, press space at frame 5 (after ``before_space(runner)`` at frame 4);
    return every frame's record, taken after the frame was drawn."""
    records = []
    drawn.clear()

    def on_frame(runner, frame):
        if frame == 1:                       # record the camera at every ACTUAL draw call
            real_render = runner.render

            def render(*a, **k):
                c = _camera(runner)
                drawn.append((runner.current_room.name, c.x, c.y, c.facing_angle))
                return real_render(*a, **k)
            runner.render = render
        cam = _camera(runner)
        st = raycast_state(runner.current_room)
        if frame == 4 and before_space:
            before_space(runner)
        if frame == 5:
            pygame.event.post(pygame.event.Event(pygame.KEYDOWN, key=pygame.K_SPACE))
        records.append({
            "frame": frame, "room": runner.current_room.name,
            "x": cam.x if cam else None, "y": cam.y if cam else None,
            "facing": getattr(cam, "facing_angle", None) if cam else None,
            "hspeed": getattr(cam, "hspeed", None) if cam else None,
            "vspeed": getattr(cam, "vspeed", None) if cam else None,
            "eye": st.get("eye_floor")})

    runner = _run(_project(tmp_path, **project_args), frames, hold_up=False, on_frame=on_frame)
    return runner, records


def _in_room1(records):
    return [r for r in records if r["room"] == "room1"]


def test_the_camera_arrives_at_the_same_offset_from_the_marker(tmp_path):
    _, records = _play(tmp_path)
    arrived = _in_room1(records)
    assert arrived, [r["room"] for r in records]
    first = arrived[0]
    assert (first["x"], first["y"]) == (MARKER_B[0] - 96.0, MARKER_B[1])      # offset (-96, 0) kept
    assert first["facing"] == 40                       # carried, not room1's authored 90


def test_no_frame_is_drawn_at_the_authored_start(tmp_path):
    _, records = _play(tmp_path)
    in_room1 = [d for d in drawn if d[0] == "room1"]
    assert in_room1
    for room, x, y, facing in in_room1:
        assert (x, y) != AUTHORED_B and facing != 90, (x, y, facing)
    assert (in_room1[0][1], in_room1[0][2]) == (MARKER_B[0] - 96.0, MARKER_B[1])


def test_speed_is_carried_across(tmp_path):
    def set_speed(runner):
        cam = _camera(runner)
        cam.hspeed, cam.vspeed = 2.0, -1.0

    _, records = _play(tmp_path, before_space=set_speed)
    first = _in_room1(records)[0]
    assert (first["hspeed"], first["vspeed"]) == (2.0, -1.0)


def test_the_eased_view_height_is_carried_not_reset(tmp_path):
    def raise_eye(runner):
        raycast_state(runner.current_room)["eye_floor"] = 12.0

    _, records = _play(tmp_path, before_space=raise_eye)
    first = _in_room1(records)[0]
    assert 9.0 < first["eye"] < 12.0                   # still falling from ~12 (gravity), not snapped to the floor


def test_a_missing_target_room_does_nothing(tmp_path):
    runner, records = _play(tmp_path, target="nowhere")
    assert not _in_room1(records) and runner.current_room.name == "room0"


@pytest.mark.parametrize("args", [{"marker_b": False}, {"marker_a": False}, {"marker": "obj_nothing"}])
def test_a_missing_marker_is_a_plain_room_change(tmp_path, args):
    _, records = _play(tmp_path, **args)
    first = _in_room1(records)[0]
    assert (first["x"], first["y"]) == AUTHORED_B and first["facing"] == 90


def test_without_a_camera_it_still_changes_room(tmp_path):
    runner, records = _play(tmp_path, camera=False)
    assert _in_room1(records) and runner.current_room.name == "room1"


def test_the_pending_arrival_is_consumed(tmp_path):
    runner, _ = _play(tmp_path)
    assert getattr(runner, "_raycast_arrival", None) is None


def test_the_action_is_registered_with_its_parameters():
    from events.action_types import get_action_type
    action = get_action_type("go_to_room_seamlessly")
    assert action is not None and action.category == "3D View"
    assert [p.name for p in action.parameters] == ["room", "marker"]
