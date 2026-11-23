#!/usr/bin/env python3
"""Seamless room-to-room teleport for the raycast view
(docs/RAYCAST_CEILINGS_TELEPORT_PLAN.md, T1).

Two rooms built to match around a junction can feel like one place: the author
puts ONE instance of a *marker* object in each room at the "same" spot of the
shared geometry, and **Go to Room Seamlessly** moves the camera to the other
room at the same offset from the marker, with the same facing, speed, held keys
and eased view height -- no fade, no frame at the new room's authored start.

How it works on desktop:

* the action (``request``) records a pending arrival on the game runner -- the
  camera's offset from the marker in this room, its facing, hspeed/vspeed and
  the eased view height -- and asks for an ordinary instant room change;
* the loop processes the change inside ``update()``; core then builds the new
  room and runs its Create / Room Start events (the camera re-arms its raycast
  view and sets its AUTHORED facing angle);
* in the SAME loop iteration the ``after_collision`` frame hook runs, BEFORE
  the frame is drawn: ``after_collision`` below applies the arrival there, so
  the carried values overwrite what Create set and the first frame drawn in
  the new room is already the right one. (The plan expected the first
  ``before_step`` of the new room; on desktop the frame is drawn before that,
  so ``after_collision`` is the hook that is early enough.)

Failure modes, all logged and none fatal: a missing target room does nothing
(as ``goto_room``); a missing camera, or a marker missing in either room, makes
it a plain room change that lands at the new room's authored start.

Pure Python, no pygame (the IDE imports the extension without one).
"""

import logging

from .state import peek_camera, raycast_state

logger = logging.getLogger(__name__)

ARRIVAL_ATTR = "_raycast_arrival"      # pending arrival, on the game runner


def _first_of(room, object_name):
    if not object_name:
        return None
    for inst in room.instances:
        if getattr(inst, "object_name", None) == object_name and not getattr(inst, "to_destroy", False):
            return inst
    return None


def _camera(room):
    cfg = peek_camera(room)
    if not cfg or not cfg.get("enabled"):
        return None
    return room._find_first_instance(cfg.get("camera_object", ""))


def request(executor, instance, parameters):
    """The Go to Room Seamlessly action: record the arrival, ask for the change."""
    runner = getattr(executor, "game_runner", None)
    if runner is None:
        return
    target = str(parameters.get("room", "") or "").strip()
    if not target or target not in runner.get_room_list():
        logger.debug("go_to_room_seamlessly: room %r not found", target)
        return
    room = runner.current_room
    marker_name = str(parameters.get("marker", "") or "").strip()
    arrival = None
    camera = _camera(room) if room is not None else None
    marker = _first_of(room, marker_name) if room is not None else None
    if getattr(room, "name", None) == target:
        logger.warning("go_to_room_seamlessly: already in room %r; changing room normally", target)
    elif camera is None:
        logger.warning("go_to_room_seamlessly: no raycast camera in this room; changing room normally")
    elif marker is None:
        logger.warning("go_to_room_seamlessly: no %r object in this room; changing room normally",
                       marker_name)
    else:
        st = raycast_state(room)
        arrival = {
            "from_room": room, "to": target, "marker": marker_name,
            "dx": camera.x - marker.x, "dy": camera.y - marker.y,
            "facing": getattr(camera, "facing_angle", 0.0),
            "hspeed": getattr(camera, "hspeed", 0.0), "vspeed": getattr(camera, "vspeed", 0.0),
            # The held keys belong to the camera INSTANCE and the new room has a fresh one: without
            # them a player holding Up would stop at the junction (the keyboard event sets the speed
            # every frame, and "no key" would set it to 0).
            "keys": set(getattr(camera, "keys_pressed", None) or ()),
            "eye_floor": st.get("eye_floor"), "eye_vz": st.get("eye_vz", 0.0),
        }
    setattr(runner, ARRIVAL_ATTR, arrival)
    instance.goto_room_target = target
    instance.goto_room_transition = "none"


def after_collision(game_runner):
    """Apply a pending arrival in the first loop iteration of the new room,
    before the frame is drawn."""
    arrival = getattr(game_runner, ARRIVAL_ATTR, None)
    if not arrival:
        return
    room = game_runner.current_room
    if room is None or room is arrival["from_room"]:
        return                                   # the room change has not happened yet
    setattr(game_runner, ARRIVAL_ATTR, None)
    if getattr(room, "name", None) != arrival["to"]:
        return                                   # some other room change won: drop it
    camera = _camera(room)
    marker = _first_of(room, arrival["marker"])
    if camera is None:
        logger.warning("go_to_room_seamlessly: the new room has no raycast camera")
        return
    if marker is None:
        logger.warning("go_to_room_seamlessly: no %r object in room %r; arriving at its start",
                       arrival["marker"], arrival["to"])
        return
    camera.x = marker.x + arrival["dx"]
    camera.y = marker.y + arrival["dy"]
    camera.facing_angle = arrival["facing"]
    camera.hspeed = arrival["hspeed"]
    camera.vspeed = arrival["vspeed"]
    camera.keys_pressed = set(arrival["keys"])
    if arrival["eye_floor"] is not None:
        st = raycast_state(room)
        st["eye_floor"] = arrival["eye_floor"]       # climbing keeps easing from here
        st["eye_vz"] = arrival["eye_vz"]
