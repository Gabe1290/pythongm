#!/usr/bin/env python3
"""Collision detection and resolution for GameRunner: movement-blocking
checks (AABB and pixel-perfect), the two-pass collision-event dispatch
(detect then process), not_collision events, overlap separation, pushing,
outside_room events, and the small grid-size/slide helpers `update()`
(in `runtime/input_handler.py`) leans on.

Extracted verbatim from ``runtime/game_runner.py`` (``docs/POST_1_0_REFACTOR.md``
File 3, cluster 5) as a MIXIN, same technique as
``runtime/input_handler.py``'s ``InputMixin`` — these are ``GameRunner``
methods with a huge ``self``-state surface and heavy cross-calling between
each other and ``update()``; there's no circular-import question, since a
mixin's methods resolve through ``self`` via the MRO at runtime, not at
import time, regardless of which file defines a given method. `update()`
staying in `input_handler.py` and calling
`self.check_movement_collision_with_blocker(...)` (now defined here)
works exactly the same as it did when both were on the same class body.

**Not a revival of the old, deleted `CollisionMixin`.** A *different*
`runtime/collision_system.py` module existed years ago holding a dead
`CollisionMixin` that `GameRunner` never inherited from (see
``ARCHITECTURE.md`` §6) — it was deleted outright in 2026-06-09 because
the methods it purported to provide already existed, correctly, directly
on `GameRunner`, making the old module pure dead weight with nothing to
extract from it. This module is the *opposite* situation: there was
nothing stale to find or delete here — the collision methods below are
copied verbatim from their one and only live implementation, still on
`GameRunner` until this commit.

Two invariant comment blocks in the methods below are load-bearing and
have survived multiple bug-hunts (commits `8ae3a7a`, `e3c0cc5`) — moved
here character-for-character, not summarized: the "AABB-only for
movement blocking" note in `check_movement_collision_with_blocker`, and
the "parent-chain match symmetry" note in `_resolve_collision_event`.
Do not simplify either without re-reading why they're phrased the way
they are.
"""

import math

from core.logger import get_logger
logger = get_logger(__name__)


class CollisionMixin:
    """Mixin providing GameRunner's collision detection/resolution.

    Not usable standalone -- every method here reads/writes attributes
    GameRunner.__init__ sets up (self.current_room, self._objects_data,
    instance._active_collisions/instance._collision_cooldowns, ...) and is
    called by (or calls back into) runtime/input_handler.py's
    InputMixin.update(), which stays a sibling mixin on the same
    GameRunner class.
    """

    @staticmethod
    def _get_step_grid_size(instance) -> int:
        """Detect grid size from an instance's step event (if_on_grid parameter).

        Returns the grid_size if the instance has an if_on_grid action in its
        step event, or 0 if not found.
        """
        obj_data = instance._cached_object_data if instance._cached_object_data else {}
        step_event = obj_data.get('events', {}).get('step', {})
        for action in step_event.get('actions', []):
            if action.get('action') == 'if_on_grid':
                grid = action.get('parameters', {}).get('grid_size')
                if grid:
                    try:
                        return int(grid)
                    except (ValueError, TypeError):
                        pass
        return 0

    @staticmethod
    def _get_any_grid_size(instance) -> int:
        """Detect grid size from any event on an instance (if_on_grid parameter).

        Searches all events (step, keyboard nokey, etc.) for if_on_grid.
        Returns the grid_size or 0 if not found.
        """
        obj_data = instance._cached_object_data if instance._cached_object_data else {}
        events = obj_data.get('events', {})
        for event_name, event_data in events.items():
            # Handle nested keyboard events (keyboard -> nokey -> actions)
            if isinstance(event_data, dict):
                actions = event_data.get('actions', [])
                if not actions and isinstance(event_data, dict):
                    # Check nested events (e.g., keyboard -> nokey)
                    for sub_name, sub_data in event_data.items():
                        if isinstance(sub_data, dict):
                            for action in sub_data.get('actions', []):
                                if action.get('action') == 'if_on_grid':
                                    grid = action.get('parameters', {}).get('grid_size')
                                    if grid:
                                        try:
                                            return int(grid)
                                        except (ValueError, TypeError):
                                            pass
                for action in actions:
                    if action.get('action') == 'if_on_grid':
                        grid = action.get('parameters', {}).get('grid_size')
                        if grid:
                            try:
                                return int(grid)
                            except (ValueError, TypeError):
                                pass
        return 0


    def _slide_axis_to_contact(self, instance, axis: str, objects_data: dict):
        """Advance a blocked instance pixel-by-pixel along one axis until it
        rests flush against the blocker, instead of cancelling the whole move.

        Called from the blocked branch of the hspeed/vspeed movement step, so
        the full move has already been found to collide. ``axis`` is 'x' or
        'y'. Steps at most ``floor(|speed|)`` whole pixels toward the intended
        position, stopping one pixel before the first colliding cell; this
        leaves at most a sub-pixel residual gap, well within the 1px ground
        probe platformer logic relies on. Leaves intended_x/intended_y equal to
        the resting position so the post-move bookkeeping (and
        _process_held_keys) sees no pending move.

        O(|speed|) collision checks per blocked instance per frame — negligible
        for the handful of fast movers in a typical scene; revisit with a
        binary search if a stress scene ever makes it hot.
        """
        speed = instance.hspeed if axis == 'x' else instance.vspeed
        step = 1.0 if speed > 0 else -1.0
        remaining = abs(speed)
        moved = 0.0
        while moved + 1.0 <= remaining:
            if axis == 'x':
                instance.intended_x = instance.x + step
                instance.intended_y = instance.y
            else:
                instance.intended_x = instance.x
                instance.intended_y = instance.y + step
            sub_can, _ = self.check_movement_collision_with_blocker(instance, objects_data)
            if not sub_can:
                break
            if axis == 'x':
                instance.x = instance.intended_x
            else:
                instance.y = instance.intended_y
            moved += 1.0
        instance.intended_x = instance.x
        instance.intended_y = instance.y

    def check_movement_collision_with_blocker(self, moving_instance, objects_data: dict):
        """Check if intended movement would be blocked by another instance.

        Blocking rule (matches GameMaker 7.0):
        1. There must be a collision event defined between the two object
           types (in either direction — walks parent chains).
        2. At least ONE of the two objects must be marked `solid`. Pairs
           of two non-solid objects fire their collision events through
           the post-movement overlap detection path
           (`detect_collisions_for_instance`) but never physically block
           each other. This is why e.g. a maze monster can run THROUGH the
           player and trigger the death animation without getting stuck
           on top of the player's sprite — both are non-solid.

        Solid + collision-event is the Sokoban shape: the player blocks
        on the box, the box's `collision_with_player` handler runs
        if_can_push to move the box one cell, and the blocked-then-pushed
        loop in `update()` re-tries the player's move.

        Returns:
            (can_move: bool, blocking_instance: GameInstance or None)
        """
        intended_x = moving_instance.intended_x
        intended_y = moving_instance.intended_y

        # Use cached dimensions
        w1 = moving_instance._cached_width
        h1 = moving_instance._cached_height

        # Pre-parsed collision targets for the moving instance
        collision_targets = moving_instance._collision_targets

        # Fast-path: if neither this instance nor any other in the room would
        # ever block this movement (no collision targets either way), the
        # nearby-instance scan below would always return should_block=False.
        # Skip it entirely. This is the dominant cost in scenes with many
        # moving instances that don't collide (profiled at ~75% of CPU on a
        # 1000-instance bouncing-drifters scene).
        if (not collision_targets
                and moving_instance.object_name not in self.current_room.get_collision_listened_types()):
            return (True, None)

        # Use spatial grid for faster collision detection
        nearby_instances = self.current_room.get_nearby_instances(intended_x, intended_y, w1, h1)

        for other_instance in nearby_instances:
            if other_instance == moving_instance:
                continue

            # Use cached object data if available
            other_obj_data = other_instance._cached_object_data
            if not other_obj_data:
                other_obj_data = objects_data.get(other_instance.object_name, {})

            # Step 1: is there a collision event in either direction?
            # Parent-chain match (via _object_matches_target) is load-bearing:
            # the event-firing path resolves collision_with_<parent> to child
            # instances, so the blocking path must too — otherwise movement
            # passes through, the post-movement event snaps the mover back,
            # and intended_x is left stale (it never gets reset on the "no
            # collision detected" branch). _process_held_keys then sees
            # intended_x != x and skips keyboard events forever.
            has_collision_event = False

            if collision_targets:
                # Check both current name and original name (before change_instance)
                names_to_check = {other_instance.object_name}
                original = getattr(other_instance, '_original_object_name', None)
                if original and original != other_instance.object_name:
                    names_to_check.add(original)

                for target_name in collision_targets:
                    for name in names_to_check:
                        if self._object_matches_target(name, target_name):
                            has_collision_event = True
                            break
                    if has_collision_event:
                        break

            if not has_collision_event:
                # Check if the other instance has a collision event with the mover
                other_collision_targets = other_instance._collision_targets
                if other_collision_targets:
                    for target_name in other_collision_targets:
                        if self._object_matches_target(moving_instance.object_name, target_name):
                            has_collision_event = True
                            break

            if not has_collision_event:
                continue

            # Step 2: also require at least one side to be `solid`. Two
            # non-solid objects with a collision event fire the event via
            # the post-movement overlap path (detect_collisions_for_instance)
            # but never physically block each other — that's why maze_3's
            # monster_all can run THROUGH obj_person and trigger the death
            # animation without getting wedged on top of the player sprite.
            # Sokoban-style pushable boxes work because the box itself is
            # marked solid; the player blocks on it, the box's collision
            # event runs if_can_push, and update()'s blocked-then-pushed
            # loop re-tries the move.
            moving_solid = bool(
                (moving_instance._cached_object_data or {}).get('solid', False)
            )
            other_solid = bool(other_obj_data.get('solid', False))
            if not (moving_solid or other_solid):
                continue

            # Use collision bboxes (smaller than full sprite for sprites
            # with transparent borders or explicit bbox_* metadata).
            # AABB-only here (no pixel-perfect refine): movement-blocking is
            # what the player feels as "the wall stops me here", and grid-maze
            # sprites with a few transparent edge pixels would otherwise let
            # the mover slip 1–N pixels into the wall's cell every frame
            # before being snapped back by the post-movement collision event,
            # producing a visible jitter. Pixel-perfect (sprite.precise) still
            # refines collision-event firing via instances_overlap, so damage
            # zones and pickup triggers keep their pixel accuracy. Phase 2a
            # originally wired precise into all three AABB call sites — this
            # narrows it to the two firing paths where it actually helps.
            s1 = moving_instance.sprite
            s2 = other_instance.sprite
            if s1 is None or s2 is None:
                continue
            bw1 = s1.bbox_right - s1.bbox_left
            bh1 = s1.bbox_bottom - s1.bbox_top
            bw2 = s2.bbox_right - s2.bbox_left
            bh2 = s2.bbox_bottom - s2.bbox_top
            # Move-target world position uses intended_*; offsets shift by the
            # sprite origin and bbox_left/top so we compare collision-bbox
            # corners, not whole-sprite corners.
            mx = intended_x - s1.origin_x + s1.bbox_left
            my = intended_y - s1.origin_y + s1.bbox_top
            ox = other_instance.x - s2.origin_x + s2.bbox_left
            oy = other_instance.y - s2.origin_y + s2.bbox_top

            if self.rectangles_overlap(mx, my, bw1, bh1, ox, oy, bw2, bh2):
                # If the mover already overlaps the blocker at its current
                # position, let it escape: blocking every direction would
                # trap it in an oscillation freeze on the next bounce.
                cur_mx = moving_instance.x - s1.origin_x + s1.bbox_left
                cur_my = moving_instance.y - s1.origin_y + s1.bbox_top
                if self.rectangles_overlap(cur_mx, cur_my, bw1, bh1, ox, oy, bw2, bh2):
                    continue
                return (False, other_instance)

        return (True, None)

    def separate_overlapping_instances(self, objects_data: dict):
        """Separate instances that are overlapping after collision events.

        When object A pushes object B but B can't move (hits solid), A should be pushed back.
        This only applies to instances that have collision events defined between them,
        and only when at least one of the objects is solid.
        """
        processed_pairs = set()

        for instance in self.current_room.instances:
            # Use pre-parsed collision targets for faster lookup
            collision_targets = instance._collision_targets
            if not collision_targets:
                continue

            # Use cached dimensions
            w1 = instance._cached_width
            h1 = instance._cached_height

            # Use spatial grid for faster collision detection
            nearby_instances = self.current_room.get_nearby_instances(instance.x, instance.y, w1, h1)

            for other_instance in nearby_instances:
                if other_instance == instance:
                    continue

                # Skip if we already processed this pair
                pair_key = (min(id(instance), id(other_instance)), max(id(instance), id(other_instance)))
                if pair_key in processed_pairs:
                    continue

                # Check if there's a collision event between these objects using pre-parsed targets
                if other_instance.object_name not in collision_targets:
                    continue

                # Only separate when at least one object is solid.
                # Non-solid collisions (e.g. ball/paddle bounce, death zone triggers)
                # should not cause physical separation.
                inst_obj_data = objects_data.get(instance.object_name, {})
                other_obj_data = objects_data.get(other_instance.object_name, {})
                if not inst_obj_data.get('solid', False) and not other_obj_data.get('solid', False):
                    continue

                # Check if collision bboxes overlap (smaller than full sprite
                # when sprite has transparent borders / explicit bbox_* meta).
                s1 = instance.sprite
                s2 = other_instance.sprite
                if s1 is None or s2 is None:
                    continue
                bw1 = s1.bbox_right - s1.bbox_left
                bh1 = s1.bbox_bottom - s1.bbox_top
                bw2 = s2.bbox_right - s2.bbox_left
                bh2 = s2.bbox_bottom - s2.bbox_top
                ix = instance.x - s1.origin_x + s1.bbox_left
                iy = instance.y - s1.origin_y + s1.bbox_top
                ox = other_instance.x - s2.origin_x + s2.bbox_left
                oy = other_instance.y - s2.origin_y + s2.bbox_top

                if self.rectangles_overlap(ix, iy, bw1, bh1, ox, oy, bw2, bh2):
                    # They're overlapping - push the moving instance back
                    # Determine which one was moving based on hspeed/vspeed
                    inst_moving = instance.hspeed != 0 or instance.vspeed != 0
                    other_moving = other_instance.hspeed != 0 or other_instance.vspeed != 0

                    # Pass bbox-world rects so separation is computed in the same
                    # coordinate space the overlap was detected in (M50). Mixing
                    # raw instance coords with bbox dims shifted the landing
                    # position by the sprite origin / bbox offsets.
                    if inst_moving and not other_moving:
                        self.push_back_instance(instance, ix, iy, bw1, bh1,
                                                ox, oy, bw2, bh2)
                    elif other_moving and not inst_moving:
                        self.push_back_instance(other_instance, ox, oy, bw2, bh2,
                                                ix, iy, bw1, bh1)

                    processed_pairs.add(pair_key)

    def push_back_instance(self, moving_inst, mbx, mby, mbw, mbh,
                           sbx, sby, sbw, sbh):
        """Push moving instance out of overlap with a static one.

        All rects are bbox-world coordinates (top-left + size). The instance's
        raw position is recovered by adding back its bbox-to-origin offset, so
        sprites with nonzero origin or auto-bbox margins land flush instead of
        a few pixels off (which broke grid alignment / re-triggered every frame).
        """
        # Offset from the moving instance's bbox-world top-left to its raw x/y.
        off_x = moving_inst.x - mbx
        off_y = moving_inst.y - mby

        overlap_left = (mbx + mbw) - sbx
        overlap_right = (sbx + sbw) - mbx
        overlap_top = (mby + mbh) - sby
        overlap_bottom = (sby + sbh) - mby

        min_overlap = min(overlap_left, overlap_right, overlap_top, overlap_bottom)

        if min_overlap == overlap_left and overlap_left > 0:
            moving_inst.x = (sbx - mbw) + off_x
        elif min_overlap == overlap_right and overlap_right > 0:
            moving_inst.x = (sbx + sbw) + off_x
        elif min_overlap == overlap_top and overlap_top > 0:
            moving_inst.y = (sby - mbh) + off_y
        elif min_overlap == overlap_bottom and overlap_bottom > 0:
            moving_inst.y = (sby + sbh) + off_y

    def check_outside_room_events(self):
        """Check for instances that have moved outside the room boundaries.

        Triggers outside_room event when an instance is completely outside the room.
        GameMaker convention: triggers when the instance's sprite is fully outside.
        """
        if not self.current_room:
            return

        room_width = self.current_room.width
        room_height = self.current_room.height

        for instance in self.current_room.instances:
            # Skip if no object data or events
            if not instance.object_data or "events" not in instance.object_data:
                continue

            events = instance.object_data["events"]
            if "outside_room" not in events:
                continue

            # Get instance bounds
            w = instance._cached_width
            h = instance._cached_height

            # The sprite's actual screen extent is x-origin_x .. x-origin_x+w
            # (rendering uses x - origin_x). Account for the origin so the event
            # fires exactly when the sprite is fully off-screen, not origin_x px
            # late/early for nonzero-origin sprites (L30).
            sprite = getattr(instance, 'sprite', None)
            origin_x = getattr(sprite, 'origin_x', 0) if sprite else 0
            origin_y = getattr(sprite, 'origin_y', 0) if sprite else 0
            left = instance.x - origin_x
            top = instance.y - origin_y

            # Check if completely outside room (not just partially)
            outside = (
                left + w < 0 or          # Completely off left
                left > room_width or     # Completely off right
                top + h < 0 or           # Completely off top
                top > room_height        # Completely off bottom
            )

            if outside:
                logger.debug(f"📤 outside_room event for {instance.object_name} at ({instance.x}, {instance.y})")
                instance.action_executor.execute_event(instance, "outside_room", events)

    def detect_collisions_for_instance(self, instance, objects_data: dict) -> list:
        """Detect collisions for an instance and capture speeds

        Returns a list of collision data dicts with speeds captured at detection time.
        Does NOT process the events - that's done separately.

        Optimized to use pre-parsed collision targets and cached dimensions.
        """
        collisions = []

        # Use pre-parsed collision targets (much faster than iterating all events)
        collision_targets = instance._collision_targets
        if not collision_targets:
            return collisions

        # _active_collisions and _collision_cooldowns are now initialized in __init__

        # Track which collisions are currently active this frame
        current_collisions = set()

        # Decrement cooldowns in single pass (avoid multiple iterations)
        cooldowns = instance._collision_cooldowns
        if cooldowns:
            keys_to_delete = []
            for key, frames in cooldowns.items():
                if frames <= 1:
                    keys_to_delete.append(key)
                else:
                    cooldowns[key] = frames - 1
            for key in keys_to_delete:
                del cooldowns[key]

        # Get nearby instances using spatial grid for faster detection
        # Use cached dimensions instead of sprite lookup
        w1 = instance._cached_width
        h1 = instance._cached_height
        nearby_instances = self.current_room.get_nearby_instances(instance.x, instance.y, w1, h1)

        # Cache instance speeds (avoid repeated getattr)
        inst_hspeed = instance.hspeed
        inst_vspeed = instance.vspeed

        # For each nearby instance, find the MOST-SPECIFIC collision target it
        # matches and fire only that event. Inverting the iteration (other-first
        # instead of target-first) prevents double-firing: when an object like
        # obj_marqueur (parent=obj_brique) is matched by BOTH
        # collision_with_obj_marqueur (direct) and collision_with_obj_brique
        # (parent), the previous target-first loop appended both, so the parent
        # brique-snap-and-stop behavior also fired on a no-op marker pickup.
        # Concretely: Pingus would freeze in mid-air when his sprite brushed a
        # marqueur during a jump, because the brique collision zeroed his
        # vspeed even though the marqueur-specific event was just `comment`.
        objects_data = self._objects_data
        for other_instance in nearby_instances:
            if other_instance == instance:
                continue

            # Walk other's name + parent chain; first match in collision_targets wins.
            matched_target = None
            current = other_instance.object_name
            for _ in range(10):  # depth cap matches _resolve_collision_event
                if current in collision_targets:
                    matched_target = current
                    break
                parent = objects_data.get(current, {}).get('parent', '')
                if not parent:
                    break
                current = parent

            if matched_target is None:
                continue

            if not self.instances_overlap(instance, other_instance):
                continue

            event_name = f"collision_with_{matched_target}"
            collision_key = (id(other_instance), event_name)
            current_collisions.add(collision_key)

            # Cache other instance speeds for collision data
            other_hspeed = other_instance.hspeed
            other_vspeed = other_instance.vspeed

            # Only fire event if this is a NEW collision AND not in cooldown
            in_cooldown = collision_key in instance._collision_cooldowns
            is_new_collision = collision_key not in instance._active_collisions
            should_fire = is_new_collision and not in_cooldown

            if should_fire:
                collisions.append({
                    'instance': instance,
                    'event_name': event_name,
                    'events': instance._cached_object_data.get('events', {}),
                    'other_instance': other_instance,
                    # Capture object names so we can detect change_instance
                    'object_name': instance.object_name,
                    'other_object_name': other_instance.object_name,
                    # Capture speeds at moment of collision detection
                    'self_hspeed': inst_hspeed,
                    'self_vspeed': inst_vspeed,
                    'other_hspeed': other_hspeed,
                    'other_vspeed': other_vspeed,
                })
                # Short cooldown (5 frames) prevents double-trigger in same collision
                # This is short enough to allow continuous pushing at normal speeds
                instance._collision_cooldowns[collision_key] = 5

        # Update active collisions for next frame
        instance._active_collisions = current_collisions

        return collisions

    def process_collision_event(self, collision_data: dict):
        """Process a single collision event with stored speeds"""
        instance = collision_data['instance']
        event_name = collision_data['event_name']
        events = collision_data['events']
        other_instance = collision_data['other_instance']

        # Skip if either instance changed type since detection (e.g., change_instance
        # transformed box into box_stored — remaining box events are stale)
        detected_name = collision_data.get('object_name')
        if detected_name and instance.object_name != detected_name:
            logger.debug(f"  ⏭️ Skipping stale collision {event_name}: {detected_name} changed to {instance.object_name}")
            return
        detected_other_name = collision_data.get('other_object_name')
        if detected_other_name and other_instance.object_name != detected_other_name:
            logger.debug(f"  ⏭️ Skipping stale collision {event_name}: other {detected_other_name} changed to {other_instance.object_name}")
            return

        # If the colliding instance is moving and has a grid-based step event,
        # snap it to the next grid position in its movement direction before
        # processing the event. Overlap collisions fire as soon as sprite edges
        # touch, but the instance should be on-grid when actions like
        # change_instance execute (e.g. Box landing on Store).
        # This is safe because the collision-checked push in the blocked
        # collision handler prevents moving instances from overlapping blockers.
        self_hspeed = collision_data.get('self_hspeed', 0)
        self_vspeed = collision_data.get('self_vspeed', 0)
        if self_hspeed != 0 or self_vspeed != 0:
            grid_size = self._get_step_grid_size(instance)
            if grid_size:
                if self_hspeed > 0:
                    instance.x = math.ceil(instance.x / grid_size) * grid_size
                elif self_hspeed < 0:
                    instance.x = math.floor(instance.x / grid_size) * grid_size
                if self_vspeed > 0:
                    instance.y = math.ceil(instance.y / grid_size) * grid_size
                elif self_vspeed < 0:
                    instance.y = math.floor(instance.y / grid_size) * grid_size
                # Stop since we snapped to destination
                instance.hspeed = 0
                instance.vspeed = 0
                logger.debug(f"  📐 Snapped moving instance to grid: {instance.object_name} → ({instance.x}, {instance.y})")

        # Use INFO level for important collisions (box with store)
        if 'obj_box' in instance.object_name and 'obj_store' in other_instance.object_name:
            logger.debug(f"🎯 BOX-STORE COLLISION: {instance.object_name} with {other_instance.object_name} at ({instance.x}, {instance.y})")
        else:
            logger.debug(f"🎯 COLLISION DETECTED: {instance.object_name} with {other_instance.object_name}")
        logger.debug(f"   Stored speeds - self: ({collision_data['self_hspeed']}, {collision_data['self_vspeed']}), other: ({collision_data['other_hspeed']}, {collision_data['other_vspeed']})")

        # Pass other_instance and collision speeds as context for collision actions
        instance.action_executor.execute_collision_event(
            instance,
            event_name,
            events,
            other_instance,
            collision_speeds={
                'self_hspeed': collision_data['self_hspeed'],
                'self_vspeed': collision_data['self_vspeed'],
                'other_hspeed': collision_data['other_hspeed'],
                'other_vspeed': collision_data['other_vspeed'],
            }
        )

    def check_not_collision_events(self, objects_data: dict):
        """Check for 'not_collision' events - these fire when instance is NOT colliding with target.

        Used for Sokoban-style mechanics where obj_box_store transforms back to obj_box
        when pushed off an obj_store.
        """
        # Iterate over a copy since we may destroy instances
        for instance in list(self.current_room.instances):
            if not instance._cached_object_data:
                continue

            events = instance._cached_object_data.get('events', {})

            # Look for not_collision_with_* events
            for event_name, event_data in events.items():
                if not event_name.startswith('not_collision_with_'):
                    continue

                target_object = event_name[19:]  # Remove 'not_collision_with_' prefix

                # Check if instance is colliding (bbox-level) with ANY instance
                # of target object. Bbox here matches the other firing paths
                # (instances_overlap, check_collision_at_position) so a
                # not_collision_with_X event has the same "what counts as
                # touching" semantics as collision_with_X.
                is_colliding = False
                s1 = instance.sprite
                if s1 is None:
                    continue
                bw1 = s1.bbox_right - s1.bbox_left
                bh1 = s1.bbox_bottom - s1.bbox_top
                ix = instance.x - s1.origin_x + s1.bbox_left
                iy = instance.y - s1.origin_y + s1.bbox_top

                for other_instance in self.current_room.instances:
                    if other_instance == instance:
                        continue
                    if other_instance.object_name != target_object:
                        continue

                    s2 = other_instance.sprite
                    if s2 is None:
                        continue
                    bw2 = s2.bbox_right - s2.bbox_left
                    bh2 = s2.bbox_bottom - s2.bbox_top
                    ox = other_instance.x - s2.origin_x + s2.bbox_left
                    oy = other_instance.y - s2.origin_y + s2.bbox_top

                    if self.rectangles_overlap(ix, iy, bw1, bh1, ox, oy, bw2, bh2):
                        is_colliding = True
                        break

                # If NOT colliding, fire the event
                if not is_colliding:
                    actions = event_data.get('actions', [])
                    if actions:
                        logger.debug(f"🚫 NOT_COLLISION: {instance.object_name} not colliding with {target_object}")
                        instance.action_executor.execute_action_list(instance, actions)

    def _object_matches_target(self, object_name: str, target: str) -> bool:
        """Check if object_name matches target, considering parent inheritance."""
        if object_name == target:
            return True
        # Walk up the parent chain (max 10 levels to prevent cycles)
        objects_data = self._objects_data
        current = object_name
        for _ in range(10):
            obj_data = objects_data.get(current, {})
            parent = obj_data.get('parent', '')
            if not parent:
                return False
            if parent == target:
                return True
            current = parent
        return False

    def _resolve_collision_event(self, events: dict, other_instance) -> str:
        """Find the collision event in `events` that matches `other_instance`.

        Tries the other's current name, then walks its parent chain, then
        falls back to _original_object_name (set by change_instance). Returns
        the matching event name, or None if no event applies.
        """
        if not events:
            return None
        direct = f"collision_with_{other_instance.object_name}"
        if direct in events:
            return direct
        objects_data = self._objects_data
        current = other_instance.object_name
        for _ in range(10):
            parent = objects_data.get(current, {}).get('parent', '')
            if not parent:
                break
            candidate = f"collision_with_{parent}"
            if candidate in events:
                return candidate
            current = parent
        original = getattr(other_instance, '_original_object_name', None)
        if original and original != other_instance.object_name:
            alt = f"collision_with_{original}"
            if alt in events:
                return alt
        return None

    def instances_overlap(self, inst1, inst2) -> bool:
        """Check if two instances overlap using their sprite collision bboxes.

        The AABB step uses each sprite's collision bbox (sprite.bbox_left etc),
        not the full sprite size — so a 32x32 sprite of a character with
        transparent borders won't trigger collision while two grid cells apart.
        Precise refinement still uses the full sprite mask aligned at the
        AABB top-left, matching the previous semantics.
        """
        # Bbox dimensions and world top-left (origin- and bbox-adjusted)
        b1 = self._bbox_in_world(inst1)
        b2 = self._bbox_in_world(inst2)
        if b1 is None or b2 is None:
            return False
        bx1, by1, bw1, bh1 = b1
        bx2, by2, bw2, bh2 = b2

        if not self.rectangles_overlap(bx1, by1, bw1, bh1, bx2, by2, bw2, bh2):
            return False
        return self._precise_refine(inst1, bx1, by1, inst2, bx2, by2)

    @staticmethod
    def _bbox_in_world(instance):
        """Return (x, y, w, h) of the instance's collision bbox in world coords,
        or None if it has no sprite. World x/y is the bbox top-left after
        applying sprite origin and the sprite's bbox_left/top offsets."""
        s = instance.sprite
        if s is None:
            return None
        x = instance.x - s.origin_x + s.bbox_left
        y = instance.y - s.origin_y + s.bbox_top
        w = s.bbox_right - s.bbox_left
        h = s.bbox_bottom - s.bbox_top
        return (x, y, w, h)

    def rectangles_overlap(self, x1, y1, w1, h1, x2, y2, w2, h2) -> bool:
        """Check if two rectangles overlap"""
        return not (x1 + w1 <= x2 or x2 + w2 <= x1 or y1 + h1 <= y2 or y2 + h2 <= y1)

    def _precise_refine(self, inst1, ax1, ay1, inst2, ax2, ay2) -> bool:
        """Post-AABB refinement for pixel-perfect collision.

        Returns True to keep an AABB-positive hit, False to reject it.
        Pixel-perfect is opt-in per sprite (sprite.precise). Static-only:
        rotated or scaled instances bypass the mask check, so the AABB
        result stands.

        ax1, ay1, ax2, ay2 are the AABB top-left positions actually used
        at the call site (already origin-adjusted). Identical coordinates
        to the rectangles_overlap that just returned True.
        """
        s1 = inst1.sprite if inst1 else None
        s2 = inst2.sprite if inst2 else None
        if not (s1 and s2):
            return True
        if not (getattr(s1, 'precise', False) or getattr(s2, 'precise', False)):
            return True
        if (getattr(inst1, 'rotation', 0) or getattr(inst2, 'rotation', 0)
                or getattr(inst1, 'image_angle', 0) or getattr(inst2, 'image_angle', 0)
                or getattr(inst1, 'scale_x', 1) != 1 or getattr(inst1, 'scale_y', 1) != 1
                or getattr(inst2, 'scale_x', 1) != 1 or getattr(inst2, 'scale_y', 1) != 1):
            return True
        m1 = s1.get_mask(inst1.image_index) if hasattr(s1, 'get_mask') else None
        m2 = s2.get_mask(inst2.image_index) if hasattr(s2, 'get_mask') else None
        if m1 is None or m2 is None:
            return True
        # The masks are FULL-FRAME (mask (0,0) == sprite frame top-left), but
        # ax/ay are the bbox top-left in world coords (origin + bbox offset).
        # Back out each sprite's bbox offset to align the masks at their frame
        # origins; using the bbox positions directly left the overlap offset
        # wrong by (bbox_left2 - bbox_left1, bbox_top2 - bbox_top1), producing
        # false hits/misses whenever two precise sprites had different bbox
        # offsets (it self-cancelled only when they happened to match).
        fx1 = ax1 - getattr(s1, 'bbox_left', 0)
        fy1 = ay1 - getattr(s1, 'bbox_top', 0)
        fx2 = ax2 - getattr(s2, 'bbox_left', 0)
        fy2 = ay2 - getattr(s2, 'bbox_top', 0)
        return m1.overlap(m2, (int(fx2 - fx1), int(fy2 - fy1))) is not None

    def check_collision_at_position(self, instance, check_x: float, check_y: float,
                                    object_type: str = "any", exclude_instance=None) -> bool:
        """Check if there's a collision at a given position

        Args:
            instance: The instance doing the check
            check_x: X position to check
            check_y: Y position to check
            object_type: Type of object to check for:
                - 'any': Only solid objects (non-solid don't block, collision events fire after move)
                - 'all': ANY overlapping instance, solid or not (GM place_empty /
                         "all objects"); used by check_empty's "all" option
                - 'solid': Only solid objects
                - specific name: Only that specific object type
            exclude_instance: Additional instance to exclude (e.g., collision other)

        Returns:
            True if collision found, False otherwise
        """
        if not self.current_room:
            logger.debug("⚠️ check_collision_at_position: No current room!")
            return False

        # Use cached dimensions
        w1 = instance._cached_width
        h1 = instance._cached_height

        # Use spatial grid for faster collision detection
        nearby_instances = self.current_room.get_nearby_instances(check_x, check_y, w1, h1)

        # Cache instance's collision targets for checking stop_movement
        instance_collision_targets = instance._collision_targets

        for other_instance in nearby_instances:
            if other_instance == instance:
                continue
            # Also exclude the collision "other" instance (e.g., explorer pushing rock)
            if exclude_instance and other_instance == exclude_instance:
                continue

            # Use sprite collision bboxes (smaller than full sprite when the
            # sprite has transparent borders or explicit bbox_* metadata)
            s1 = instance.sprite
            s2 = other_instance.sprite
            if s1 is None or s2 is None:
                continue
            bw1 = s1.bbox_right - s1.bbox_left
            bh1 = s1.bbox_bottom - s1.bbox_top
            bw2 = s2.bbox_right - s2.bbox_left
            bh2 = s2.bbox_bottom - s2.bbox_top
            # check_x/y is the candidate top-left of `instance`; the bbox
            # is offset within the sprite by origin + bbox_left/top.
            ix = check_x - s1.origin_x + s1.bbox_left
            iy = check_y - s1.origin_y + s1.bbox_top
            ox = other_instance.x - s2.origin_x + s2.bbox_left
            oy = other_instance.y - s2.origin_y + s2.bbox_top

            # Check if collision bboxes overlap
            if self.rectangles_overlap(ix, iy, bw1, bh1, ox, oy, bw2, bh2):
                # Pixel-perfect refinement (no-op unless either sprite opts in).
                if not self._precise_refine(
                        instance, ix, iy,
                        other_instance, ox, oy):
                    continue
                # "all": every overlapping instance occupies the position,
                # solid or not (GM "all objects" / place_empty). Solid-only
                # "any" ignores non-solid monsters, which let a pushed block
                # teleport over a monster in maze_3.
                if object_type == "all":
                    return True
                # Use cached object data for properties
                other_obj_data = other_instance._cached_object_data
                if not other_obj_data:
                    objects_data = self._objects_data
                    other_obj_data = objects_data.get(other_instance.object_name, {})

                is_solid = other_obj_data.get('solid', False)

                # Collision detected - check if it matches the filter
                if object_type == "any":
                    # Solid objects always block
                    if is_solid:
                        return True

                    # For non-solid objects, check if there's a collision event
                    # that has a "stop_movement" action using pre-parsed collision targets
                    target_name = other_instance.object_name
                    if target_name in instance_collision_targets:
                        # Check if the collision event has a stop_movement action
                        event_data = instance_collision_targets[target_name]
                        actions = event_data.get('actions', [])
                        for action in actions:
                            if action.get('action') == 'stop_movement':
                                return True
                        # Collision event exists but no stop_movement - continue checking other objects
                        continue
                    else:
                        # Also check if the OTHER object has a collision event with stop_movement
                        # using its pre-parsed collision targets
                        other_collision_targets = other_instance._collision_targets
                        if instance.object_name in other_collision_targets:
                            reverse_event_data = other_collision_targets[instance.object_name]
                            reverse_actions = reverse_event_data.get('actions', [])
                            for action in reverse_actions:
                                if action.get('action') == 'stop_movement':
                                    return True

                        # No blocking event for THIS object - continue checking other objects
                        continue

                elif object_type == "solid":
                    # "solid" means only solid objects
                    if is_solid:
                        return True
                else:
                    # Check for specific object type
                    if other_instance.object_name == object_type:
                        return True

        return False

