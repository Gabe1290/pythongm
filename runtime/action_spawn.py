#!/usr/bin/env python3
"""Instance creation, destruction and change actions for
:class:`~runtime.action_executor.ActionExecutor`.

Seven methods: ``create_instance`` and its moving/random variants,
``destroy_instance`` and ``destroy_at_position``, and ``change_instance`` with
the ``_change_single_instance`` worker it delegates to.

Extracted verbatim from ``runtime/action_executor.py``
(``docs/POST_1_0_REFACTOR.md`` File 4, cluster 5) as a MIXIN -- see
``runtime/action_drawing.py``'s header for why these are sibling modules rather
than the package layout the plan sketched.

**Do not hoist the ``from runtime.game_runner import GameInstance,
resolve_parent_inheritance`` statements to module level.** They sit inside the
methods on purpose: ``runtime/game_runner.py`` requires pygame, and this whole
side of the engine is deliberately importable without it (see
``runtime/__init__.py``'s own note, and the 35 test files that load the
executor by file path for exactly that reason). Moving them up would look
tidier and would quietly reintroduce a pygame dependency here. ``random`` is
likewise imported inside ``create_random_instance``.

The particle/emitter ``create_*``/``destroy_*`` actions deliberately did NOT
come along despite matching the same name shapes -- they belong with the rest
of the particle system, not with instance spawning.
"""

import math
from typing import Any, Dict

from core.logger import get_logger

logger = get_logger(__name__)


class SpawnMixin:
    """Instance create / destroy / change ``execute_*_action`` methods."""

    def execute_destroy_instance_action(self, instance, parameters: Dict[str, Any]):
        """Execute destroy instance action

        Parameters:
            target: "self"|"other"|"object" - which instance(s) to destroy
                    ("sel" is accepted as a legacy alias for "self")
            target_object: When target=="object", name of the object whose
                           instances should be destroyed (applies to every
                           instance of that object in the current room).
        """
        target = parameters.get("target", "self")
        target_object = parameters.get("target_object", "")

        if target == "other" and hasattr(self, '_collision_other') and self._collision_other:
            logger.debug(f"💀 Destroying other instance: {self._collision_other.object_name}")
            self._collision_other.to_destroy = True
            return

        if target == "other":
            # No collision partner (this action fired from a non-collision
            # event, or ran outside a collision this frame) -- GM's own
            # behaviour is a no-op here, not "destroy self" (M6,
            # docs/FULL_AUDIT_2026-09-07.md). Falling through to the
            # "Default: destroy self" branch below would silently destroy
            # the caller instead.
            logger.debug("⚠️ destroy_instance: target='other' but no collision partner -- no-op")
            return

        if target == "object":
            if not target_object:
                logger.debug("⚠️ destroy_instance: target='object' but no target_object given")
                return
            if not (self.game_runner and self.game_runner.current_room):
                logger.debug("⚠️ destroy_instance: No current room for target='object'")
                return
            count = 0
            for inst in self.game_runner.current_room.instances:
                if getattr(inst, 'object_name', None) == target_object:
                    inst.to_destroy = True
                    count += 1
            logger.debug(f"💀 Destroying {count} instance(s) of '{target_object}'")
            return

        # Default: destroy self ("self" and "sel" both land here).
        logger.debug(f"💀 Destroying instance: {instance.object_name}")
        instance.to_destroy = True
    def execute_create_instance_action(self, instance, parameters: Dict[str, Any]):
        """Create a new instance of an object at a specified position

        Parameters:
            object: The object type to create
            x: X position for the new instance
            y: Y position for the new instance
            relative: If True, position is relative to current instance
        """
        object_name = parameters.get("object", "")
        x_param = parameters.get("x", 0)
        y_param = parameters.get("y", 0)
        relative = parameters.get("relative", False)

        if not object_name:
            logger.debug("⚠️ create_instance: No object specified")
            return

        if not self.game_runner:
            logger.debug("⚠️ create_instance: No game_runner reference")
            return

        # Parse position values (can be expressions)
        x = self._parse_value(str(x_param), instance)
        y = self._parse_value(str(y_param), instance)

        try:
            x = float(x) if x is not None else 0.0
            y = float(y) if y is not None else 0.0
        except (ValueError, TypeError):
            x = 0.0
            y = 0.0

        # Apply relative positioning
        if relative:
            x = instance.x + x
            y = instance.y + y

        # Get the object's data
        objects_data = self.game_runner.project_data.get('assets', {}).get('objects', {})
        if object_name not in objects_data:
            logger.debug(f"⚠️ create_instance: Object '{object_name}' not found")
            return

        object_data = objects_data[object_name]

        # Import GameInstance locally to avoid circular imports
        from runtime.game_runner import GameInstance

        # Create new instance
        instance_data = {
            'object_name': object_name,
            'x': x,
            'y': y,
            'instance_id': id(object_data) + int(x * 1000) + int(y * 1000000)  # Generate unique ID
        }

        new_instance = GameInstance(
            object_name,
            x,
            y,
            instance_data,
            action_executor=self
        )

        # Set up the new instance with object data (with parent inheritance)
        from runtime.game_runner import resolve_parent_inheritance
        merged_data = resolve_parent_inheritance(object_data, self.game_runner._objects_data)
        new_instance.set_object_data(merged_data)

        # Get sprite for the new instance
        sprite_name = object_data.get('sprite', '')
        if sprite_name and sprite_name in self.game_runner.sprites:
            new_instance.set_sprite(self.game_runner.sprites[sprite_name])

        # Add to current room
        if self.game_runner.current_room:
            self.game_runner.current_room.instances.append(new_instance)
            self.game_runner.current_room._add_to_grid(new_instance)
            self.game_runner.current_room._depth_dirty = True  # Mark for re-sort
            self.game_runner.current_room.invalidate_collision_listened_types()

            # Defer create event to run after current event completes
            # This ensures conditions like instance_count are accurate
            # (e.g., the box is destroyed before checking if count is 0).
            # Read from merged_data so an inherited-only create event fires (L28).
            events = merged_data.get('events', {})
            if 'create' in events:
                if self._event_depth > 0:
                    # We're inside an event - defer the create event
                    self._deferred_create_events.append((new_instance, events))
                    logger.debug(f"➕ Created instance of '{object_name}' at ({x}, {y}) [create event deferred]")
                else:
                    # Not inside an event - execute immediately
                    self.execute_event(new_instance, 'create', events)
                    logger.debug(f"➕ Created instance of '{object_name}' at ({x}, {y})")
            else:
                logger.debug(f"➕ Created instance of '{object_name}' at ({x}, {y})")
        else:
            logger.debug("⚠️ create_instance: No current room to add instance to")
    def execute_change_instance_action(self, instance, parameters: Dict[str, Any]):
        """Change instance into a different object type

        This is like destroying the current instance and creating a new one
        of a different type at the same position.

        Parameters:
            object: The new object type to change into
            perform_events: Whether to execute destroy/create events (default True)
            target: "self"|"other"|"object" - which instance(s) to change
                    ("sel" is accepted as a legacy alias for "self")
            target_object: When target=="object", name of the object whose
                           instances should be changed (applies to every instance
                           of that object in the current room).
        """
        new_object_name = parameters.get("object", "")
        perform_events = parameters.get("perform_events", True)
        target = parameters.get("target", "self")
        target_object = parameters.get("target_object", "")

        if not new_object_name:
            logger.debug("⚠️ change_instance: No object specified")
            return

        # Determine which instance(s) to change
        target_instances = []
        if target == "other" and hasattr(self, '_collision_other') and self._collision_other:
            target_instances = [self._collision_other]
        elif target == "other":
            # No collision partner -- GM's behaviour is a no-op, not
            # "change self" (M6, docs/FULL_AUDIT_2026-09-07.md). The
            # trailing `else: target_instances = [instance]` below would
            # otherwise catch this case too, silently changing the caller.
            logger.debug("⚠️ change_instance: target='other' but no collision partner -- no-op")
            return
        elif target == "object":
            if not target_object:
                logger.debug("⚠️ change_instance: target='object' but no target_object given")
                return
            if not (self.game_runner and self.game_runner.current_room):
                logger.debug("⚠️ change_instance: No current room for target='object'")
                return
            # Snapshot the list — we'll mutate object_name on each, so don't filter
            # again mid-iteration.
            target_instances = [
                inst for inst in self.game_runner.current_room.instances
                if getattr(inst, 'object_name', None) == target_object
            ]
            if not target_instances:
                logger.debug(f"⚠️ change_instance: no instances of '{target_object}' in room")
                return
        else:
            target_instances = [instance]

        # Get the game runner to access objects data and room
        if not self.game_runner:
            logger.debug("⚠️ change_instance: No game_runner reference")
            return

        # Get the new object's data
        objects_data = self.game_runner.project_data.get('assets', {}).get('objects', {})
        if new_object_name not in objects_data:
            logger.debug(f"⚠️ change_instance: Object '{new_object_name}' not found")
            return

        new_object_data = objects_data[new_object_name]

        # Apply the same transformation to every target instance.
        for target_instance in target_instances:
            self._change_single_instance(
                target_instance, new_object_name, new_object_data, perform_events)
    def _change_single_instance(self, target_instance, new_object_name,
                                 new_object_data, perform_events):
        """Apply the change_instance transformation to one instance."""
        logger.debug(f"🔄 Changing {target_instance.object_name} into {new_object_name}")

        # Execute destroy event if requested
        if perform_events and target_instance.object_data:
            events = target_instance.object_data.get('events', {})
            if 'destroy' in events:
                logger.debug(f"  💥 Executing destroy event for {target_instance.object_name}")
                self.execute_event(target_instance, 'destroy', events)

        # Store current position and properties
        old_x = target_instance.x
        old_y = target_instance.y

        # Change the object type (with parent inheritance)
        target_instance.object_name = new_object_name
        from runtime.game_runner import resolve_parent_inheritance
        merged_data = resolve_parent_inheritance(new_object_data, self.game_runner._objects_data)
        target_instance.set_object_data(merged_data)
        # execute_event's M53 once-per-instance guard (_create_fired) is keyed
        # on the Python instance object, not the object type — change_instance
        # reuses the same instance, so without this reset the new type's create
        # event silently no-ops if the OLD type's create already fired (e.g.
        # plateforme_3's obj_monstre -> obj_monstre_mort stomp: the monster's
        # own create had already set _create_fired, so obj_monstre_mort's
        # create — which sets its "dead" sprite — never ran). The instance is
        # now logically a fresh instance of the new type, so its create-fired
        # state should start over.
        target_instance._create_fired = False
        # The instance now has different collision_targets and a different
        # object_name, so the room's listened-types cache is stale.
        if self.game_runner.current_room:
            self.game_runner.current_room.invalidate_collision_listened_types()

        # Update sprite if the new object has a different one
        sprite_name = new_object_data.get('sprite', '')
        if sprite_name and sprite_name in self.game_runner.sprites:
            # Use set_sprite to properly update cached dimensions (_cached_width, _cached_height)
            target_instance.set_sprite(self.game_runner.sprites[sprite_name])
            logger.debug(f"  🖼️ Updated sprite to: {sprite_name}")

        # Preserve collision tracking - the instance is at the same position,
        # so existing overlap state is still valid. Resetting would cause
        # residual overlaps to be treated as new collisions, triggering
        # spurious collision events (e.g., box pushed onto store changes to
        # box_stored, then the reset causes a "new" collision with the pusher
        # which moves box_stored an extra grid cell).

        # GM8's instance_change keeps every instance variable INCLUDING motion —
        # treasure's monster→scared relies on it: scared has no create/step
        # events, its movement is purely the velocity carried through the
        # change, so zeroing it froze every scared monster. Preserve motion.
        # The one exception (the e8f31c9 case this reset was added for): an
        # instance mid GRID-step — its velocity was generated by the OLD
        # type's cell-to-cell step logic (e.g. if_on_grid → stop) and without
        # that logic the leftover step velocity never terminates. Zero motion
        # only for those pending grid movers.
        was_grid_moving = (
            getattr(target_instance, 'intended_x', target_instance.x) != target_instance.x
            or getattr(target_instance, 'intended_y', target_instance.y) != target_instance.y
        )
        if was_grid_moving:
            target_instance.hspeed = 0
            target_instance.vspeed = 0
            # `speed` is a read-only property derived from hspeed/vspeed
            # (L5, docs/FULL_AUDIT_2026-09-07.md) -- zeroing those two is
            # enough, there is nothing separate left to write.
        # Clear any pending grid movement either way
        target_instance._has_intended_move = False

        # Execute create event for new object type if requested. Read from the
        # parent-merged data so an inherited-only create event fires (L28).
        if perform_events:
            events = merged_data.get('events', {})
            if 'create' in events:
                if self._event_depth > 0:
                    # Defer create event until current event completes
                    self._deferred_create_events.append((target_instance, events))
                    logger.debug(f"  🎬 Create event for {new_object_name} DEFERRED (depth={self._event_depth})")
                else:
                    logger.debug(f"  🎬 Executing create event for {new_object_name} IMMEDIATELY")
                    self.execute_event(target_instance, 'create', events)
            else:
                logger.debug(f"  ⚠️ No create event defined for {new_object_name}")
        else:
            logger.debug(f"  ℹ️ perform_events=False, skipping create event for {new_object_name}")

        logger.debug(f"  ✅ Changed instance to {new_object_name} at ({old_x}, {old_y})")
    def execute_create_random_instance_action(self, instance, parameters: Dict[str, Any]):
        """Create a random instance from up to four object choices

        Parameters:
            object1, object2, object3, object4: Object types to randomly choose from
            x: X position for the new instance
            y: Y position for the new instance
        """
        import random

        # Collect non-empty object choices
        objects = []
        for i in range(1, 5):
            obj_name = parameters.get(f"object{i}", "")
            if obj_name:
                objects.append(obj_name)

        if not objects:
            logger.debug("⚠️ create_random_instance: No objects specified")
            return

        # Pick a random object
        object_name = random.choice(objects)

        x_param = parameters.get("x", 0)
        y_param = parameters.get("y", 0)

        if not self.game_runner:
            logger.debug("⚠️ create_random_instance: No game_runner reference")
            return

        # Parse position values
        x = self._parse_value(str(x_param), instance)
        y = self._parse_value(str(y_param), instance)

        try:
            x = float(x) if x is not None else 0.0
            y = float(y) if y is not None else 0.0
        except (ValueError, TypeError):
            x = 0.0
            y = 0.0

        # Get the object's data
        objects_data = self.game_runner.project_data.get('assets', {}).get('objects', {})
        if object_name not in objects_data:
            logger.debug(f"⚠️ create_random_instance: Object '{object_name}' not found")
            return

        object_data = objects_data[object_name]

        # Import GameInstance locally to avoid circular imports
        from runtime.game_runner import GameInstance

        # Create new instance
        instance_data = {
            'object_name': object_name,
            'x': x,
            'y': y,
            'instance_id': id(object_data) + int(x * 1000) + int(y * 1000000)
        }

        new_instance = GameInstance(
            object_name,
            x,
            y,
            instance_data,
            action_executor=self
        )

        # Set up the new instance with object data (with parent inheritance)
        from runtime.game_runner import resolve_parent_inheritance
        merged_data = resolve_parent_inheritance(object_data, self.game_runner._objects_data)
        new_instance.set_object_data(merged_data)

        # Get sprite for the new instance
        sprite_name = object_data.get('sprite', '')
        if sprite_name and sprite_name in self.game_runner.sprites:
            new_instance.set_sprite(self.game_runner.sprites[sprite_name])

        # Add to current room
        if self.game_runner.current_room:
            self.game_runner.current_room.instances.append(new_instance)
            self.game_runner.current_room._add_to_grid(new_instance)
            # Invalidate the depth-sort cache so the new instance is rendered;
            # _add_to_grid does not set this and render() draws only the cached
            # _sorted_instances (M46).
            self.game_runner.current_room._depth_dirty = True
            self.game_runner.current_room.invalidate_collision_listened_types()

            # Defer create event to run after current event completes
            events = merged_data.get('events', {})
            if 'create' in events:
                if self._event_depth > 0:
                    self._deferred_create_events.append((new_instance, events))
                    logger.debug(f"🎲 Created random instance of '{object_name}' at ({x}, {y}) [create event deferred]")
                else:
                    self.execute_event(new_instance, 'create', events)
                    logger.debug(f"🎲 Created random instance of '{object_name}' at ({x}, {y})")
            else:
                logger.debug(f"🎲 Created random instance of '{object_name}' at ({x}, {y})")
        else:
            logger.debug("⚠️ create_random_instance: No current room to add instance to")
    def execute_create_moving_instance_action(self, instance, parameters: Dict[str, Any]):
        """Create a new instance with initial motion

        Parameters:
            object: The object type to create
            x: X position for the new instance
            y: Y position for the new instance
            speed: Initial speed
            direction: Initial direction in degrees
        """

        object_name = parameters.get("object", "")
        x_param = parameters.get("x", 0)
        y_param = parameters.get("y", 0)
        speed_param = parameters.get("speed", 0)
        direction_param = parameters.get("direction", 0)

        if not object_name:
            logger.debug("⚠️ create_moving_instance: No object specified")
            return

        if not self.game_runner:
            logger.debug("⚠️ create_moving_instance: No game_runner reference")
            return

        # Parse values
        x = self._parse_value(str(x_param), instance)
        y = self._parse_value(str(y_param), instance)
        speed = self._parse_value(str(speed_param), instance)
        direction = self._parse_value(str(direction_param), instance)

        try:
            x = float(x) if x is not None else 0.0
            y = float(y) if y is not None else 0.0
            speed = float(speed) if speed is not None else 0.0
            direction = float(direction) if direction is not None else 0.0
        except (ValueError, TypeError):
            x, y, speed, direction = 0.0, 0.0, 0.0, 0.0

        # Get the object's data
        objects_data = self.game_runner.project_data.get('assets', {}).get('objects', {})
        if object_name not in objects_data:
            logger.debug(f"⚠️ create_moving_instance: Object '{object_name}' not found")
            return

        object_data = objects_data[object_name]

        # Import GameInstance locally to avoid circular imports
        from runtime.game_runner import GameInstance

        # Create new instance
        instance_data = {
            'object_name': object_name,
            'x': x,
            'y': y,
            'instance_id': id(object_data) + int(x * 1000) + int(y * 1000000)
        }

        new_instance = GameInstance(
            object_name,
            x,
            y,
            instance_data,
            action_executor=self
        )

        # Set up the new instance with object data and sprite, resolving the
        # parent chain so a child object keeps its inherited events/properties
        # (collision, outside_room, etc.) — matching the other two creators and
        # room-built instances (M47).
        from runtime.game_runner import resolve_parent_inheritance
        merged_data = resolve_parent_inheritance(object_data, self.game_runner._objects_data)
        new_instance.set_object_data(merged_data)

        # Set initial motion (convert direction to hspeed/vspeed)
        # GameMaker uses degrees where 0 = right, 90 = up
        rad = math.radians(direction)
        new_instance.hspeed = speed * math.cos(rad)
        new_instance.vspeed = -speed * math.sin(rad)  # Negative because Y increases downward
        # `direction` and `speed` are both derived properties on GameInstance
        # (computed from hspeed/vspeed -- L5, docs/FULL_AUDIT_2026-09-07.md,
        # for `speed`), so there's nothing to write back here — setting
        # hspeed/vspeed above is enough.

        # Get sprite for the new instance
        sprite_name = object_data.get('sprite', '')
        if sprite_name and sprite_name in self.game_runner.sprites:
            new_instance.set_sprite(self.game_runner.sprites[sprite_name])

        # Add to current room
        if self.game_runner.current_room:
            self.game_runner.current_room.instances.append(new_instance)
            self.game_runner.current_room._add_to_grid(new_instance)
            # Invalidate the depth-sort cache so the new instance renders (M46).
            self.game_runner.current_room._depth_dirty = True
            self.game_runner.current_room.invalidate_collision_listened_types()

            # Defer create event to run after current event completes
            events = merged_data.get('events', {})
            if 'create' in events:
                if self._event_depth > 0:
                    self._deferred_create_events.append((new_instance, events))
                    logger.debug(f"🚀 Created moving instance of '{object_name}' at ({x}, {y}) with speed={speed}, dir={direction} [create event deferred]")
                else:
                    self.execute_event(new_instance, 'create', events)
                    logger.debug(f"🚀 Created moving instance of '{object_name}' at ({x}, {y}) with speed={speed}, dir={direction}")
            else:
                logger.debug(f"🚀 Created moving instance of '{object_name}' at ({x}, {y}) with speed={speed}, dir={direction}")
        else:
            logger.debug("⚠️ create_moving_instance: No current room to add instance to")
    def execute_destroy_at_position_action(self, instance, parameters: Dict[str, Any]):
        """Destroy all matching instances within `radius` pixels of (x, y).

        Parameters:
            x, y: Center of the area (expressions OK, e.g. "self.x").
            relative: If True, x/y are offsets from the caller's position
                    instead of absolute coordinates. Default False.
            radius: Pixel radius. 0 = exact-position match (legacy behavior),
                    >0 = Euclidean distance check. Default 32 (≈ one grid cell).
            object: Which OBJECT TYPE to destroy (current UI dropdown + GMK
                    import). "all"/"any" → no type filter (every instance in
                    range); "solid" → solid instances only; "non-solid" →
                    everything except solids; an object name → only that type.
                    Absent/empty → every instance in range.
            target / target_object: Legacy fallback for actions saved via the
                    old "applies to" group, honoured only when `object` is
                    unset. self → caller's object_name, other → collision
                    other's, object → `target_object`.
        """
        if not self.game_runner or not self.game_runner.current_room:
            logger.debug("⚠️ destroy_at_position: No game_runner or current_room")
            return

        # Parse position values (expressions allowed)
        x_param = parameters.get("x", 0)
        y_param = parameters.get("y", 0)
        x = self._parse_value(str(x_param), instance)
        y = self._parse_value(str(y_param), instance)
        try:
            x = float(x) if x is not None else 0.0
            y = float(y) if y is not None else 0.0
        except (ValueError, TypeError):
            x = 0.0
            y = 0.0

        # Relative: treat x/y as offsets from the caller's position (matches
        # create_instance / check_empty semantics). Off by default so saved
        # absolute actions are unaffected.
        relative = parameters.get("relative", False)
        if isinstance(relative, str):
            relative = relative.lower() in ('true', '1', 'yes')
        if relative:
            x += instance.x
            y += instance.y

        # Radius: 0 keeps the legacy exact-match behavior for older callers/tests.
        try:
            radius = float(parameters.get("radius", 0))
        except (ValueError, TypeError):
            radius = 0.0
        radius_sq = radius * radius  # avoid sqrt per instance

        # Resolve object-name filter (None = no filter, destroy any instance).
        #   filter_name None + solid_only False → every instance in range.
        #   solid_only True                     → only solid instances.
        #   filter_name set                     → only that object type.
        obj_param = parameters.get("object", None)
        target = parameters.get("target")
        target_object = parameters.get("target_object", "")
        filter_name = None
        # Solidity filter: None = ignore solidity, True = solid only,
        # False = non-solid only.
        solid_filter = None
        if obj_param not in (None, ""):
            # Explicit object dropdown (current UI + GMK import). The dialog
            # offers the sentinels "all"/"any" (no type filter), "solid"
            # (solid instances only) and "non-solid" (everything but solids)
            # ahead of the real object names.
            if obj_param in ("all", "any"):
                filter_name = None
            elif obj_param == "solid":
                solid_filter = True
            elif obj_param == "non-solid":
                solid_filter = False
            else:
                filter_name = obj_param
        elif target == "self":
            # Legacy: older saved actions stored the filter via the
            # "applies to" group (target/target_object) instead of "object".
            filter_name = getattr(instance, 'object_name', None)
        elif target == "other":
            other = getattr(self, '_collision_other', None)
            filter_name = getattr(other, 'object_name', None) if other else getattr(instance, 'object_name', None)
        elif target == "object":
            filter_name = target_object or None

        destroyed_count = 0
        for inst in self.game_runner.current_room.instances:
            if filter_name and getattr(inst, 'object_name', None) != filter_name:
                continue
            if solid_filter is not None:
                obj_data = getattr(inst, '_cached_object_data', None) or {}
                if bool(obj_data.get('solid', False)) != solid_filter:
                    continue
            if radius > 0:
                dx = inst.x - x
                dy = inst.y - y
                if dx * dx + dy * dy > radius_sq:
                    continue
            else:
                # GM's "Destroy Instance at Position" (action_kill_position /
                # position_destroy) destroys every instance whose BOUNDING BOX
                # contains the point, not only ones sitting exactly at it. The
                # old exact-origin(±1px) match missed maze_4's explosion, which
                # clears a 3x3 tile area by firing destroy_at_position at points
                # 16px inside the surrounding walls — inside their bboxes but
                # not at their origins — so bombs never opened the walls and the
                # level was inescapable.
                ox = inst.sprite.origin_x if getattr(inst, 'sprite', None) else 0
                oy = inst.sprite.origin_y if getattr(inst, 'sprite', None) else 0
                left = inst.x - ox
                top = inst.y - oy
                w = getattr(inst, '_cached_width', 0) or 0
                h = getattr(inst, '_cached_height', 0) or 0
                if w <= 0 or h <= 0:
                    # No usable bbox — fall back to exact-origin (±1px) match.
                    if abs(inst.x - x) >= 1 or abs(inst.y - y) >= 1:
                        continue
                elif not (left <= x < left + w and top <= y < top + h):
                    continue
            inst.to_destroy = True
            destroyed_count += 1

        if destroyed_count > 0:
            logger.debug(f"💣 Destroyed {destroyed_count} instance(s) at ({x}, {y}) r={radius}")
        else:
            logger.debug(f"💣 No instances destroyed at ({x}, {y}) r={radius}")
