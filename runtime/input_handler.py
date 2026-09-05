#!/usr/bin/env python3
"""Input handling and the main per-frame game-loop update: keyboard/mouse
event dispatch, held-key processing, physics (gravity/friction), collision-
checked movement, room-transition-flag handling, and alarm ticking.

Extracted verbatim from ``runtime/game_runner.py`` (``docs/POST_1_0_REFACTOR.md``
File 3, cluster 4) as a MIXIN, not a standalone class -- these are
``GameRunner`` methods that read/write a large surface of ``self`` state
(``self.current_room``, ``self._objects_data``, ``self.change_room()``,
``self.check_movement_collision_with_blocker()``, ...), the same File-2
style already used for ``core/ide/``'s mixins rather than the File-3
GameSprite/GameRoom/GameInstance "move the whole class" technique. Because
it's a mixin, there is no circular-import concern at all: every
cross-reference resolves at runtime through ``self`` via the MRO, not at
import time, regardless of which mixin file a given method physically
lives in. ``update()`` calls collision methods (``check_movement_collision_with_blocker``
and friends) that stay on ``GameRunner`` itself for now -- a future
``collision.py`` cluster can move them independently with zero coordination
needed here.

``update()`` and ``_process_held_keys`` are extracted TOGETHER deliberately
(per this plan's own risk callout): ``_process_held_keys``'s
``is_grid_moving`` check depends on ``instance.intended_x/y == instance.x/y``,
an invariant only ``update()``'s post-collision re-sync maintains.

**IMPORTANT -- this file previously held a *different*, unused, DEAD
``InputMixin``** (imported only by ``runtime/__init__.py``'s ``__all__``,
never actually inherited by ``GameRunner`` anywhere -- confirmed via
``grep`` before touching anything). That old content had diverged
significantly from the real, live ``GameRunner`` methods it was seemingly
meant to mirror: no ``anykey`` support, no Thymio button integration, no
M49 snapshot-safe iteration (``list(self.current_room.instances)``, so a
key-press event that spawns/destroys instances mid-loop can't corrupt the
iteration), and different mouse button-name conventions
(``"left"``/``"right"``/``"middle"`` vs. the real ``"left_button"``/
``"right_button"``/``"middle_button"``). This is the same shape of finding
as the 2026-06-09 ``CollisionMixin`` deletion (a long-dead, never-wired-in
mixin sitting in the tree) -- except here the fix is to replace the dead
content with the real one and actually wire it in, rather than delete it,
since ``GameRunner`` genuinely needs this functionality somewhere. The old
content is gone; nothing referenced its specific (wrong) behaviour.

``GameRunner`` now actually inherits from ``InputMixin`` (previously it
did not, despite the class existing) -- this is a real, if
behaviour-invisible, structural change: before this commit, an
``InputMixin`` in ``GameRunner.__mro__`` would have been a bug (the stale
methods would have shadowed nothing, since ``GameRunner`` never listed it
as a base, but the two implementations could have silently diverged
further over time). After this commit, ``InputMixin`` in the MRO is
exactly where these methods actually live.
"""

import math
from typing import Optional

from runtime._keymap import pygame_key_name

from core.logger import get_logger
logger = get_logger(__name__)


# Flat top-level mouse event keys (as actually written by the IDE events panel --
# f"mouse_{button}_{event_type}" -- and by the GMK importer's GM_MOUSE_SUBEVENT)
# mapped onto the runtime button_name the mouse dispatchers expect. The
# dispatchers historically read ONLY the nested events['mouse'][button_name]
# form, which no live writer produces, so every authored or GMK-imported mouse
# event was silently inert (audit H11). 'down'/'button' (held) variants fire on
# press since the runtime has no per-frame held-mouse loop.
_FLAT_MOUSE_KEY_ALIASES = {
    'mouse_left_button': 'left_button',
    'mouse_left_press': 'left_button',
    'mouse_left_down': 'left_button',
    'mouse_right_button': 'right_button',
    'mouse_right_press': 'right_button',
    'mouse_right_down': 'right_button',
    'mouse_middle_button': 'middle_button',
    'mouse_middle_press': 'middle_button',
    'mouse_middle_down': 'middle_button',
    'mouse_left_release': 'left_button_released',
    'mouse_right_release': 'right_button_released',
    'mouse_middle_release': 'middle_button_released',
    'mouse_move': 'mouse_move',
    'mouse_enter': 'mouse_move',
}


def _mouse_sub_event(events, button_name):
    """Return the sub-event dict (with 'actions') for a runtime mouse
    button_name, accepting both the nested events['mouse'][button_name] form
    and the flat top-level keys writers actually emit (see
    _FLAT_MOUSE_KEY_ALIASES). Returns None when there's no matching handler."""
    mouse_event = events.get('mouse')
    if isinstance(mouse_event, dict):
        sub = mouse_event.get(button_name)
        if isinstance(sub, dict) and 'actions' in sub:
            return sub
    for flat_key, mapped in _FLAT_MOUSE_KEY_ALIASES.items():
        if mapped == button_name and flat_key in events:
            sub = events[flat_key]
            if isinstance(sub, dict) and 'actions' in sub:
                return sub
    return None


def _find_key_in_event(event_dict: dict, key: str) -> Optional[str]:
    """Find key in event dict, checking both lowercase and uppercase.

    Args:
        event_dict: Dictionary of event handlers keyed by key name
        key: Key to search for (e.g., 'left', 'space')

    Returns:
        The matching key from event_dict, or None if not found
    """
    if key in event_dict:
        return key
    upper_key = key.upper()
    if upper_key in event_dict:
        return upper_key
    return None


class InputMixin:
    """Mixin providing GameRunner's input handling and per-frame update.

    Not usable standalone -- every method here reads/writes attributes
    GameRunner.__init__ sets up (self.current_room, self._objects_data,
    self._thymio_mouse_presses, self.thymio_renderer, ...) and calls
    sibling GameRunner methods (self.change_room, self.restart_game,
    self.check_movement_collision_with_blocker, ...).
    """

    def _get_key_name(self, key):
        """Map pygame key code to key name string"""
        return pygame_key_name(key)

    def handle_keyboard_press(self, key):
        """Handle keyboard press event"""
        if not self.current_room:
            return

        # Map pygame keys to sub-event keys
        sub_key = self._get_key_name(key)
        if not sub_key:
            return

        logger.debug(f"\n⌨️  Keyboard pressed: {sub_key}")

        events_found = False

        # Track which keys are pressed. Snapshot so a key-press spawner cycle
        # can't hang the frame (M49).
        for instance in list(self.current_room.instances):
            # Skip orphan instances (object_name not in the project's objects dict,
            # e.g. a renamed/deleted object), matching every other input handler.
            # Done before keys_pressed.add so they also stay out of _process_held_keys.
            if not instance.object_data:
                continue

            # keys_pressed is always initialized in __init__
            instance.keys_pressed.add(sub_key)

            events = instance.object_data.get('events', {})

            # Check for keyboard_press event
            if "keyboard_press" in events:
                keyboard_press_event = events["keyboard_press"]
                if isinstance(keyboard_press_event, dict):
                    # First try "press_<key>" variant (legacy format), then plain "<key>"
                    press_key = f"press_{sub_key}"
                    found_key = _find_key_in_event(keyboard_press_event, press_key)
                    if not found_key:
                        found_key = _find_key_in_event(keyboard_press_event, sub_key)
                    if found_key:
                        logger.debug(f"  ✅ Executing keyboard_press.{found_key} for {instance.object_name}")
                        events_found = True
                        sub_event_data = keyboard_press_event[found_key]
                        if isinstance(sub_event_data, dict) and "actions" in sub_event_data:
                            instance.action_executor.execute_action_list(instance, sub_event_data["actions"])
                    # `anykey` (press) — fires once per keydown regardless of which key
                    anykey_found = _find_key_in_event(keyboard_press_event, "anykey")
                    if anykey_found:
                        logger.debug(f"  ✅ Executing keyboard_press.anykey for {instance.object_name}")
                        events_found = True
                        anykey_data = keyboard_press_event[anykey_found]
                        if isinstance(anykey_data, dict) and "actions" in anykey_data:
                            instance.action_executor.execute_action_list(instance, anykey_data["actions"])

            # Note: keyboard (held) events are handled per-frame in _process_held_keys,
            # NOT here on KEYDOWN, to avoid double-firing with keyboard_press events

            # Handle Thymio button events (keyboard mapping)
            if instance.is_thymio and instance.thymio_simulator:
                thymio_button_map = {
                    'up': ('forward', 'thymio_button_forward'),
                    'down': ('backward', 'thymio_button_backward'),
                    'left': ('left', 'thymio_button_left'),
                    'right': ('right', 'thymio_button_right'),
                    'space': ('center', 'thymio_button_center')
                }

                if sub_key in thymio_button_map:
                    button_name, event_name = thymio_button_map[sub_key]
                    instance.thymio_simulator.set_button(button_name, True)

                    # Trigger Thymio button event
                    if event_name in events:
                        logger.debug(f"  🤖 Executing {event_name} for {instance.object_name}")
                        events_found = True
                        instance.action_executor.execute_event(instance, event_name, events)

        if not events_found:
            logger.debug(f"  ℹ️  No objects have keyboard events for '{sub_key}'")

    def _process_held_keys(self, instance):
        """Process keyboard (held) events for keys currently pressed — called every frame.

        For grid-based movement: only fires when instance is stationary (hspeed==0 and vspeed==0),
        preventing re-triggering while a grid move is in progress.
        For smooth movement: fires every frame since speed is continuously applied.
        """
        if not instance.keys_pressed:
            return

        if not instance.object_data:
            return

        events = instance.object_data.get('events', {})
        keyboard_event = events.get("keyboard")
        if not isinstance(keyboard_event, dict):
            return

        # Only skip if a grid move is in progress (intended position differs from current).
        # For smooth movement (set_hspeed/set_vspeed), always process held keys so the
        # player can change direction even when already moving or blocked by a wall.
        is_grid_moving = (
            getattr(instance, 'intended_x', instance.x) != instance.x or
            getattr(instance, 'intended_y', instance.y) != instance.y
        )
        if is_grid_moving:
            return

        for sub_key in instance.keys_pressed:
            press_key = f"press_{sub_key}"
            found_key = _find_key_in_event(keyboard_event, press_key)
            if not found_key:
                found_key = _find_key_in_event(keyboard_event, sub_key)
            if found_key:
                sub_event_data = keyboard_event[found_key]
                if isinstance(sub_event_data, dict) and "actions" in sub_event_data:
                    instance.action_executor.execute_action_list(instance, sub_event_data["actions"])

        # `anykey` (held) — fires every frame while any key is pressed,
        # mirroring `nokey` for the empty case. The GMK importer and the
        # Blockly toolbox both emit keyboard.anykey events, so the runtime
        # has to dispatch them or pressing keys against an anykey handler
        # silently does nothing (maze_3's controller_start advances to
        # room1 on this).
        anykey_found = _find_key_in_event(keyboard_event, "anykey")
        if anykey_found:
            anykey_data = keyboard_event[anykey_found]
            if isinstance(anykey_data, dict) and "actions" in anykey_data:
                instance.action_executor.execute_action_list(instance, anykey_data["actions"])

    def _release_held_key_silent(self, key):
        """Drop a released key from every instance's keys_pressed WITHOUT firing
        keyboard_release events. Used by modal dialogs, which run their own event
        loop while the game is paused: a KEYUP consumed there would otherwise
        leave the key stuck in keys_pressed, so _process_held_keys keeps firing
        the held-key event forever after the dialog closes (M54)."""
        if not self.current_room:
            return
        sub_key = self._get_key_name(key)
        if not sub_key:
            return
        for instance in self.current_room.instances:
            keys = getattr(instance, 'keys_pressed', None)
            if keys is not None:
                keys.discard(sub_key)

    def handle_keyboard_release(self, key):
        """Handle keyboard release event - trigger user-defined keyboard_release events"""
        if not self.current_room:
            return

        # Map pygame keys to sub-event keys
        sub_key = self._get_key_name(key)
        if not sub_key:
            return

        logger.debug(f"\n⌨️  Keyboard released: {sub_key}")

        # Execute keyboard_release events for all instances (snapshot, M49)
        for instance in list(self.current_room.instances):
            if not instance.object_data:
                continue

            # Remove key from pressed set (keys_pressed is always initialized in __init__)
            instance.keys_pressed.discard(sub_key)

            events = instance.object_data.get('events', {})

            # Execute keyboard_release events from JSON (custom actions only)
            if "keyboard_release" in events:
                keyboard_release_event = events["keyboard_release"]
                if isinstance(keyboard_release_event, dict):
                    # First try "release_<key>" variant (legacy format), then plain "<key>"
                    release_key = f"release_{sub_key}"
                    found_key = _find_key_in_event(keyboard_release_event, release_key)
                    if not found_key:
                        found_key = _find_key_in_event(keyboard_release_event, sub_key)
                    if found_key:
                        sub_event_data = keyboard_release_event[found_key]
                        if isinstance(sub_event_data, dict) and "actions" in sub_event_data:
                            instance.action_executor.execute_action_list(instance, sub_event_data["actions"])
                    # `anykey` (release) — fires once per keyup regardless of which key
                    anykey_found = _find_key_in_event(keyboard_release_event, "anykey")
                    if anykey_found:
                        anykey_data = keyboard_release_event[anykey_found]
                        if isinstance(anykey_data, dict) and "actions" in anykey_data:
                            instance.action_executor.execute_action_list(instance, anykey_data["actions"])

            # Handle Thymio button release
            if instance.is_thymio and instance.thymio_simulator:
                thymio_button_map = {
                    'up': 'forward',
                    'down': 'backward',
                    'left': 'left',
                    'right': 'right',
                    'space': 'center'
                }

                if sub_key in thymio_button_map:
                    button_name = thymio_button_map[sub_key]
                    instance.thymio_simulator.set_button(button_name, False)

    def handle_mouse_press(self, button, pos):
        """Handle mouse button press event"""
        if not self.current_room:
            return

        # Map pygame mouse buttons to event names
        button_map = {
            1: "left_button",
            2: "middle_button",
            3: "right_button",
        }

        button_name = button_map.get(button)
        if not button_name:
            return

        mouse_x, mouse_y = pos
        logger.debug(f"\n🖱️  Mouse pressed: {button_name} at ({mouse_x}, {mouse_y})")

        # Thymio button click takes precedence over generic mouse events:
        # if the click lands on a Thymio button, fire that robot's button event
        # and don't fall through to the per-instance mouse handlers.
        if button == 1 and self._handle_thymio_button_press(button, mouse_x, mouse_y):
            return

        # Execute mouse events for all instances (snapshot, M49)
        for instance in list(self.current_room.instances):
            if not instance.object_data:
                continue

            events = instance.object_data.get('events', {})

            # Check for mouse event (nested or flat key form)
            sub_event_data = _mouse_sub_event(events, button_name)
            if sub_event_data is not None:
                logger.debug(f"  ✅ Executing mouse.{button_name} for {instance.object_name}")
                # Add mouse position to instance for actions to use
                instance.mouse_x = mouse_x
                instance.mouse_y = mouse_y
                instance.action_executor.execute_action_list(instance, sub_event_data["actions"])

    def _handle_thymio_button_press(self, mouse_button, mouse_x, mouse_y):
        """Hit-test Thymio buttons under the mouse and fire the matching event.

        Returns True if a Thymio button was pressed (caller should swallow the click).
        """
        for instance in self.current_room.instances:
            if not (instance.is_thymio and instance.thymio_simulator):
                continue
            sim = instance.thymio_simulator
            hit = self.thymio_renderer.hit_test_button(sim.x, sim.y, sim.angle, mouse_x, mouse_y)
            if not hit:
                continue

            sim.set_button(hit, True)
            self._thymio_mouse_presses[mouse_button] = (instance, hit)

            event_name = f"thymio_button_{hit}"
            events = (instance.object_data or {}).get('events', {})
            if event_name in events:
                logger.debug(f"  🤖 Mouse-clicked {event_name} on {instance.object_name}")
                instance.action_executor.execute_event(instance, event_name, events)
            return True
        return False

    def handle_mouse_release(self, button, pos):
        """Handle mouse button release event"""
        if not self.current_room:
            return

        # If this mouse button had pressed a Thymio button, release it and stop here.
        press = self._thymio_mouse_presses.pop(button, None)
        if press is not None:
            instance, btn_name = press
            if instance.thymio_simulator:
                instance.thymio_simulator.set_button(btn_name, False)
            return

        button_map = {
            1: "left_button_released",
            2: "middle_button_released",
            3: "right_button_released",
        }

        button_name = button_map.get(button)
        if not button_name:
            return

        mouse_x, mouse_y = pos

        # Execute mouse release events (snapshot, M49)
        for instance in list(self.current_room.instances):
            if not instance.object_data:
                continue

            events = instance.object_data.get('events', {})

            sub_event_data = _mouse_sub_event(events, button_name)
            if sub_event_data is not None:
                instance.mouse_x = mouse_x
                instance.mouse_y = mouse_y
                instance.action_executor.execute_action_list(instance, sub_event_data["actions"])

    def handle_mouse_motion(self, pos):
        """Handle mouse movement event"""
        if not self.current_room:
            return

        mouse_x, mouse_y = pos

        # Execute mouse motion events (snapshot, M49)
        for instance in list(self.current_room.instances):
            if not instance.object_data:
                continue

            events = instance.object_data.get('events', {})

            sub_event_data = _mouse_sub_event(events, "mouse_move")
            if sub_event_data is not None:
                instance.mouse_x = mouse_x
                instance.mouse_y = mouse_y
                instance.action_executor.execute_action_list(instance, sub_event_data["actions"])

    def _room_transition_pending(self) -> bool:
        """True if any instance has queued a room change/restart/game-restart
        this frame. Used to stop mid-frame collision processing before the room
        is rebuilt, so one death can't deduct a life per overlapping instance.
        Mirrors the flags consumed at the top of update()."""
        room = self.current_room
        if not room:
            return False
        for inst in room.instances:
            if (inst.restart_room_flag or inst.next_room_flag
                    or inst.previous_room_flag or inst.restart_game_flag
                    or inst.goto_room_target):
                return True
        return False

    def update(self):
        """Update game logic"""
        if not self.current_room:
            return

        # Get objects data for solid checks
        objects_data = self._objects_data

        # Combined pass: check room transition flags AND apply physics
        # If any transition flag is set, we return immediately (physics is skipped for that frame)
        for instance in self.current_room.instances:
            if instance.restart_room_flag:
                logger.debug("🔄 Restarting room...")
                self.restart_current_room()
                return

            if instance.next_room_flag:
                instance.next_room_flag = False
                logger.debug("➡️  Going to next room...")
                self.goto_next_room()
                return

            if instance.previous_room_flag:
                instance.previous_room_flag = False
                logger.debug("⬅️  Going to previous room...")
                self.goto_previous_room()
                return

            if instance.restart_game_flag:
                instance.restart_game_flag = False
                logger.debug("🔄 Restarting game...")
                self.restart_game()
                return

            # Check for goto_room_target (set by delay_action or goto_room)
            if instance.goto_room_target:
                goto_target = instance.goto_room_target
                instance.goto_room_target = None
                # Only the goto_room action's explicit `transition` param
                # sets this — direct self.goto_room_target assignment (the
                # pattern execute_code samples like match3_3 use) and
                # delay_action leave it unset, which is fine: 'none' is the
                # existing instant-switch behaviour, unchanged.
                transition = getattr(instance, 'goto_room_transition', 'none')
                logger.debug(f"🚪 Going to room: {goto_target}")
                self.change_room(goto_target, transition=transition)
                # load_game's cross-room case rides the same deferred flag —
                # restore the saved instances onto the freshly-built room
                # now that change_room has returned (synchronous).
                pending_instances = getattr(instance, '_pending_load_instances', None)
                if pending_instances is not None:
                    instance._pending_load_instances = None
                    instance.action_executor._restore_instances(pending_instances)
                return

            # Apply gravity (instance.gravity is always defined, default 0)
            if instance.gravity != 0:
                gravity_dir = instance.gravity_direction
                rad = math.radians(gravity_dir)
                instance.hspeed += instance.gravity * math.cos(rad)
                instance.vspeed -= instance.gravity * math.sin(rad)  # Negative because Y increases downward

            # Apply friction (instance.friction is always defined, default 0)
            if instance.friction != 0:
                speed = math.sqrt(instance.hspeed ** 2 + instance.vspeed ** 2)
                if speed > 0:
                    new_speed = max(0, speed - instance.friction)
                    if new_speed == 0:
                        instance.hspeed = 0
                        instance.vspeed = 0
                    else:
                        scale = new_speed / speed
                        instance.hspeed *= scale
                        instance.vspeed *= scale

        # Apply speed-based movement (hspeed, vspeed) with collision checking
        # Track blocked collisions per instance - deduplicate to avoid infinite bounce loops
        # Key: instance_id -> collision info with h_blocked/v_blocked flags
        # We key by instance only (not by blocker) so corner collisions with different walls merge
        blocked_collisions_map = {}

        for instance in self.current_room.instances:
            # hspeed and vspeed are always defined (default 0)
            if instance.hspeed != 0:
                # Store intended position
                instance.intended_x = instance.x + instance.hspeed
                instance.intended_y = instance.y

                # Check collision - returns (can_move, blocking_instance)
                can_move, blocker = self.check_movement_collision_with_blocker(instance, objects_data)
                if can_move:
                    instance.x = instance.intended_x
                else:
                    # Movement blocked — reset intended position so it doesn't
                    # look like a grid move is in progress to _process_held_keys.
                    # (Horizontal is left all-or-nothing for now: hspeed is small
                    # in practice so the gap is sub-pixel-ish, and sliding here
                    # would also change how maze/bounce movers rest against walls.
                    # _slide_axis_to_contact already handles 'x' if we wire it.)
                    instance.intended_x = instance.x
                if not can_move and blocker:
                    # Movement blocked horizontally - track in map by instance only
                    key = id(instance)
                    if key not in blocked_collisions_map:
                        blocked_collisions_map[key] = {
                            'instance': instance,
                            'other_instance': blocker,  # Use first blocker for event
                            'self_hspeed': instance.hspeed,
                            'self_vspeed': instance.vspeed,
                            'h_blocked': False,
                            'v_blocked': False,
                        }
                    blocked_collisions_map[key]['h_blocked'] = True

            if instance.vspeed != 0:
                # Store intended position
                instance.intended_x = instance.x
                instance.intended_y = instance.y + instance.vspeed

                # Check collision - returns (can_move, blocking_instance)
                can_move, blocker = self.check_movement_collision_with_blocker(instance, objects_data)
                if can_move:
                    instance.y = instance.intended_y
                else:
                    # Slide flush against the blocker instead of cancelling the
                    # whole move. All-or-nothing vertical movement left a fast
                    # faller up to |vspeed| px above the floor; at terminal
                    # velocity (e.g. Pingus' clamp of 24) that gap exceeded the
                    # 1px ground probe and 12px move_to_contact snap the object
                    # logic used, so the character hung in mid-air with its
                    # animation still cycling. Sliding lands it flush at any
                    # speed (and resets intended_y to the resting position).
                    self._slide_axis_to_contact(instance, 'y', objects_data)
                if not can_move and blocker:
                    # Movement blocked vertically - track in map by instance only
                    key = id(instance)
                    if key not in blocked_collisions_map:
                        blocked_collisions_map[key] = {
                            'instance': instance,
                            'other_instance': blocker,  # Use first blocker for event
                            'self_hspeed': instance.hspeed,
                            'self_vspeed': instance.vspeed,
                            'h_blocked': False,
                            'v_blocked': False,
                        }
                    blocked_collisions_map[key]['v_blocked'] = True

        # Fire collision events for blocked movements (deduplicated)
        for collision in blocked_collisions_map.values():
            instance = collision['instance']
            other = collision['other_instance']
            h_blocked = collision.get('h_blocked', False)
            v_blocked = collision.get('v_blocked', False)

            # Check if the mover has a collision event for the blocking object
            # (walks parent chain so e.g. collision_with_obj_brick_parent fires
            # when the actual blocker is an obj_brick_green child).
            events = instance._cached_object_data.get('events', {}) if instance._cached_object_data else {}
            event_name = self._resolve_collision_event(events, other)

            # Also check if the blocker has a collision event with the mover
            blocker_events = other._cached_object_data.get('events', {}) if other._cached_object_data else {}
            blocker_event_name = self._resolve_collision_event(blocker_events, instance)

            blocker_old_x = other.x
            blocker_old_y = other.y
            blocker_old_hspeed = other.hspeed
            blocker_old_vspeed = other.vspeed

            if event_name:
                logger.debug(f"🎯 BLOCKED COLLISION: {instance.object_name} with {other.object_name} (h:{h_blocked}, v:{v_blocked})")
                instance.action_executor.execute_collision_event(
                    instance,
                    event_name,
                    events,
                    other,
                    collision_speeds={
                        'self_hspeed': collision['self_hspeed'],
                        'self_vspeed': collision['self_vspeed'],
                        'other_hspeed': other.hspeed,
                        'other_vspeed': other.vspeed,
                        'h_blocked': h_blocked,
                        'v_blocked': v_blocked,
                    }
                )

            if blocker_event_name:
                logger.debug(f"🎯 BLOCKED COLLISION (reverse): {other.object_name} with {instance.object_name} (h:{h_blocked}, v:{v_blocked})")
                other.action_executor.execute_collision_event(
                    other,
                    blocker_event_name,
                    blocker_events,
                    instance,
                    collision_speeds={
                        'self_hspeed': other.hspeed,
                        'self_vspeed': other.vspeed,
                        'other_hspeed': collision['self_hspeed'],
                        'other_vspeed': collision['self_vspeed'],
                        'h_blocked': h_blocked,
                        'v_blocked': v_blocked,
                    }
                )

            # If the blocker gained speed from the collision event, try to move it
            # one frame WITH collision checking. If the path is blocked (e.g. by
            # another Box or a Wall), the blocker stays put and loses its speed.
            # Also skip the blocker's next step event so if_on_grid won't kill
            # the speed before it can leave its starting grid cell.
            if other.hspeed != blocker_old_hspeed or other.vspeed != blocker_old_vspeed:
                # Check if the blocker can actually move
                other.intended_x = other.x + (other.hspeed if other.hspeed != 0 else 0)
                other.intended_y = other.y + (other.vspeed if other.vspeed != 0 else 0)
                can_move, _ = self.check_movement_collision_with_blocker(other, objects_data)
                if can_move:
                    if other.hspeed != 0:
                        other.x += other.hspeed
                    if other.vspeed != 0:
                        other.y += other.vspeed
                    # Skip next step so if_on_grid doesn't kill speed at start pos
                    other._skip_next_step = True
                    logger.debug(f"  ➡️ Applied first frame of blocker movement: {other.object_name} → ({other.x}, {other.y})")
                else:
                    # Blocker can't move — stop it
                    other.hspeed = 0
                    other.vspeed = 0
                    logger.debug(f"  🚫 Blocker {other.object_name} blocked, cannot move")

            # If the blocker was pushed (position changed), allow original movement
            # and snap the pusher to the nearest grid position so it stays aligned
            if other.x != blocker_old_x or other.y != blocker_old_y:
                instance.x += collision['self_hspeed']
                instance.y += collision['self_vspeed']
                # Snap pusher to grid on both axes to prevent off-grid drift
                grid_size = self._get_step_grid_size(other)
                if not grid_size:
                    grid_size = self._get_any_grid_size(instance)
                if grid_size:
                    from runtime.action_handlers.base import snap_to_grid
                    instance.x = snap_to_grid(instance.x, grid_size)
                    instance.y = snap_to_grid(instance.y, grid_size)
        # Handle intended movement (grid-based) with collision checking
        for instance in self.current_room.instances:
            if instance._has_intended_move:
                # Store movement direction so collision handlers (e.g. if_can_push) can use it
                instance._last_grid_move_dx = instance.intended_x - instance.x
                instance._last_grid_move_dy = instance.intended_y - instance.y

                # Check if movement would collide with solid objects
                can_move, blocker = self.check_movement_collision_with_blocker(instance, objects_data)

                if can_move:
                    logger.debug(f"✅ Movement allowed: {instance.object_name} → ({instance.intended_x}, {instance.intended_y})")
                    instance.x = instance.intended_x
                    instance.y = instance.intended_y
                else:
                    logger.debug(f"❌ Movement blocked: {instance.object_name} (hit solid object)")
                    # For Sokoban-style pushing: fire collision event with the blocker
                    # This allows if_can_push to move the blocker and enable movement
                    if blocker:
                        # Compute grid movement direction as pseudo-speeds for collision context
                        grid_dx = instance._last_grid_move_dx
                        grid_dy = instance._last_grid_move_dy
                        # Normalize to -1/0/1 so other.hspeed/other.vspeed give direction
                        norm_dx = (1 if grid_dx > 0 else -1) if grid_dx != 0 else 0
                        norm_dy = (1 if grid_dy > 0 else -1) if grid_dy != 0 else 0
                        collision_speeds_mover = {
                            'self_hspeed': norm_dx,
                            'self_vspeed': norm_dy,
                            'other_hspeed': 0,
                            'other_vspeed': 0,
                        }
                        collision_speeds_blocker = {
                            'self_hspeed': 0,
                            'self_vspeed': 0,
                            'other_hspeed': norm_dx,
                            'other_vspeed': norm_dy,
                        }

                        events = instance._cached_object_data.get('events', {}) if instance._cached_object_data else {}
                        event_name = self._resolve_collision_event(events, blocker)

                        blocker_events = blocker._cached_object_data.get('events', {}) if blocker._cached_object_data else {}
                        blocker_event_name = self._resolve_collision_event(blocker_events, instance)

                        blocker_old_x = blocker.x
                        blocker_old_y = blocker.y

                        if event_name:
                            logger.debug(f"🔄 Grid blocked collision: {instance.object_name} with {blocker.object_name}")
                            instance.action_executor.execute_collision_event(
                                instance, event_name, events, blocker, collision_speeds_mover
                            )

                        if blocker_event_name:
                            logger.debug(f"🔄 Grid blocked collision (reverse): {blocker.object_name} with {instance.object_name}")
                            blocker.action_executor.execute_collision_event(
                                blocker, blocker_event_name, blocker_events, instance, collision_speeds_blocker
                            )

                        # If the blocker was pushed (position changed), allow original movement
                        if blocker.x != blocker_old_x or blocker.y != blocker_old_y:
                            instance.x = instance.intended_x
                            instance.y = instance.intended_y
                            logger.debug(f"✅ Movement allowed after push: {instance.object_name} → ({instance.x}, {instance.y})")

                # Clear intended movement flag
                instance._has_intended_move = False

        # Check collision events - use global two-pass approach
        # Skip collision detection during room transition grace period
        # This prevents immediate triggers when player spawns on top of a portal
        if self._room_transition_grace_frames > 0:
            self._room_transition_grace_frames -= 1
            logger.debug(f"⏳ Room transition grace period: skipping collision detection ({self._room_transition_grace_frames} frames remaining)")
        else:
            # First pass: Detect ALL collisions for ALL instances and capture speeds
            all_collisions = []
            for instance in self.current_room.instances:
                collisions = self.detect_collisions_for_instance(instance, objects_data)
                all_collisions.extend(collisions)

            # Second pass: Process collision events with stored speeds. Stop as
            # soon as a handler queues a room change/restart (or ends the game):
            # the room is about to be rebuilt, so processing the rest of the
            # queue would let a single death keep mutating soon-to-be-discarded
            # instances — e.g. deducting one life per overlapping monster when
            # several cluster on the player (2–3 lives lost from one hit).
            for collision_data in all_collisions:
                self.process_collision_event(collision_data)
                if not self.running or self._room_transition_pending():
                    break

            # Third pass: Check for "not_collision" events (fire when NOT colliding)
            self.check_not_collision_events(objects_data)

            # Fourth pass: Separate overlapping instances that have collision events
            # This handles the case where soko pushes box into wall - soko should be pushed back
            self.separate_overlapping_instances(objects_data)

        # Update spatial grid only for instances that moved (lazy update)
        # This is much faster than rebuilding the entire grid every frame
        self.current_room.update_dirty_instances()

        # Check for outside_room events
        self.check_outside_room_events()

        # Re-sync intended_x/y to the post-collision position. Without this,
        # if a collision event handler moved the instance (e.g. snap_to_grid
        # after pixel-perfect collision let the mover slip into a wall),
        # intended_x/y is left at the pre-snap value. _process_held_keys then
        # sees intended != current next frame, thinks a grid move is in
        # progress, and silently drops keyboard input forever. Grid-based
        # intended moves (_has_intended_move) are already cleared above so
        # this overwrite is safe for them too.
        for instance in self.current_room.instances:
            instance.intended_x = instance.x
            instance.intended_y = instance.y

        # NOTE: Step events are executed in the main game loop, not here
        # (see run_game_loop where instance.step() is called)

