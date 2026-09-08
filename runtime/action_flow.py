#!/usr/bin/env python3
"""Conditional-flow and test actions for
:class:`~runtime.action_executor.ActionExecutor`.

Every action that decides whether the actions after it run: the ``if_*`` family
(condition, collision, collision_at, object_exists, on_grid, can_push), the
``test_*`` family (variable, expression, instance_count, chance, alignment,
question), ``check_empty`` / ``check_sound`` / ``check_keys_and_move``,
``exit_event``, and the ``repeat`` block with the ``_handle_repeat_action`` and
``_find_matching_end_block`` helpers that make GameMaker's flat skip-next
action lists behave like nested blocks.

Extracted verbatim from ``runtime/action_executor.py``
(``docs/POST_1_0_REFACTOR.md`` File 4, cluster 7) as a MIXIN -- the cluster the
plan singled out as the riskiest, because these actions and the dispatcher
reference each other. What makes it tractable is that the direction is
one-way: the dispatcher (``execute_action``, ``execute_action_list``,
``_execute_action_list_inner``) stays on ``ActionExecutor``, and these methods
reach it through ``self`` exactly as before.

Two module-level pieces came along, and ``action_executor`` imports them BACK
from here (one direction, so no cycle):

* ``_ExitEvent`` -- the sentinel ``exit_event`` raises. The base's three
  ``except _ExitEvent`` sites still catch it because it is one class, imported,
  not a copy.
* ``detect_c_style_operators`` -- used only by ``_eval_bool_expression`` in
  this module, but re-exported because ``tests/test_action_executor.py`` reads
  it off the executor module by name.

``random``, ``pygame`` and ``PySide6.QtWidgets`` are imported *inside* three of
these methods; the move keeps them there, so this module -- like the engine
module it came from -- imports without pygame or Qt.
"""

import re
from typing import Any, Dict, List, Tuple

from core.logger import get_logger

logger = get_logger(__name__)


def detect_c_style_operators(expression: str) -> List[Tuple[str, str]]:
    """Find C/GML-style boolean operators that should be Python operators.

    This project teaches Python, so conditions use ``and`` / ``or`` / ``not``
    rather than the C/GameMaker ``&&`` / ``||`` / ``!``. Returns a list of
    ``(found, python_equivalent)`` pairs for every offending operator in
    ``expression`` so callers (the runtime evaluator and the IDE editor) can
    show a consistent, teachable warning. Empty list means the expression is
    clean. ``!=`` is deliberately ignored — it's valid Python.
    """
    if not expression:
        return []
    found: List[Tuple[str, str]] = []
    if '&&' in expression:
        found.append(('&&', 'and'))
    if '||' in expression:
        found.append(('||', 'or'))
    # A lone '!' (logical not) but never the '!=' inequality operator.
    if re.search(r'!(?!=)', expression):
        found.append(('!', 'not'))
    return found

class _ExitEvent(Exception):
    """Internal sentinel: raised by execute_exit_event_action to abort the
    rest of the current event's action list. Caught by execute_action_list
    and execute_collision_action_list at the top-level dispatch boundary —
    so a nested then_actions / else_actions / repeat block can still trip
    it and unwind through every level at once. Mirrors GameMaker's
    "exit event" action.
    """


class FlowMixin:
    """Conditional-flow / test ``execute_*_action`` methods."""

    def execute_exit_event_action(self, instance, parameters: Dict[str, Any]):
        """GameMaker's "exit event" — stop running the rest of this event's
        actions. Common use: a monster's collision_with_wall handler tries
        each candidate direction, and the moment one fits it commits +
        exits so the later fallbacks don't undo the choice.

        Implemented by raising the internal _ExitEvent sentinel; the
        top-level execute_action_list / execute_collision_action_list
        wrappers catch it. Using an exception here is deliberate — the
        action may sit inside arbitrarily deep then_actions / else_actions
        / repeat blocks, and a flag would need to bubble through every
        recursion level.
        """
        raise _ExitEvent()
    def _handle_repeat_action(self, instance, actions: list, current_index: int, action_data: dict) -> int:
        """Handle the repeat action - executes following action(s) N times

        Returns the index to continue from after the repeated actions
        """
        parameters = action_data.get("parameters", {})
        times_param = parameters.get("times", "1")

        # Parse the times parameter (can be a number or variable)
        times = self._parse_value(str(times_param), instance)
        if not isinstance(times, (int, float)):
            logger.warning(f"⚠️ Repeat: Invalid times value '{times_param}', defaulting to 1")
            times = 1
        times = int(times)

        if times <= 0:
            # Skip the next action(s) entirely
            next_index = current_index + 1
            if next_index < len(actions):
                next_action = actions[next_index].get("action", "")
                if next_action == "start_block":
                    # Skip the entire block
                    return self._find_matching_end_block(actions, next_index) + 1
                else:
                    # Skip just the next action
                    return next_index + 1
            return current_index + 1

        # Find the actions to repeat
        next_index = current_index + 1
        if next_index >= len(actions):
            return next_index

        next_action = actions[next_index].get("action", "")

        if next_action == "start_block":
            # Repeat a block of actions
            end_block_index = self._find_matching_end_block(actions, next_index)
            block_actions = actions[next_index + 1:end_block_index]  # Actions between { and }

            logger.debug(f"🔁 Repeat block {times} times ({len(block_actions)} actions)")
            for iteration in range(times):
                # Use the non-catching workhorse so an exit_event inside the
                # block unwinds the whole event (and stops the remaining
                # iterations) instead of being swallowed per-iteration (M43).
                self._execute_action_list_inner(instance, block_actions)

            return end_block_index + 1
        else:
            # Repeat a single action
            single_action = actions[next_index]
            logger.debug(f"🔁 Repeat '{next_action}' {times} times")
            for iteration in range(times):
                self.execute_action(instance, single_action)

            return next_index + 1
    def _find_matching_end_block(self, actions: list, start_block_index: int) -> int:
        """Find the index of the matching end_block for a start_block"""
        depth = 1
        i = start_block_index + 1

        while i < len(actions) and depth > 0:
            action_name = actions[i].get("action", "")
            if action_name == "start_block":
                depth += 1
            elif action_name in ("end_block", "end"):
                depth -= 1
            i += 1

        return i - 1  # Return the index of the end_block
    def execute_test_alignment_action(self, instance, parameters: Dict[str, Any]):
        """Check if instance position is aligned to an hsnap x vsnap grid.

        Returns True/False for conditional flow (like other test_ actions).
        Supports separate horizontal and vertical snap sizes.

        Parameters:
            hsnap: Horizontal grid size (default 32)
            vsnap: Vertical grid size (default 32)
        """
        hsnap = int(self._parse_value(str(parameters.get("hsnap", "32")), instance))
        vsnap = int(self._parse_value(str(parameters.get("vsnap", "32")), instance))

        if hsnap <= 0:
            hsnap = 1
        if vsnap <= 0:
            vsnap = 1

        tolerance = 0.5
        x_rem = abs(instance.x % hsnap)
        y_rem = abs(instance.y % vsnap)

        x_close = (x_rem < tolerance) or (x_rem > hsnap - tolerance)
        y_close = (y_rem < tolerance) or (y_rem > vsnap - tolerance)

        if x_close and y_close:
            instance.x = round(instance.x / hsnap) * hsnap
            instance.y = round(instance.y / vsnap) * vsnap

        on_grid = (instance.x % hsnap == 0) and (instance.y % vsnap == 0)
        return on_grid
    def execute_if_on_grid_action(self, instance, parameters: Dict[str, Any]):
        """Check if instance is on grid - returns True/False for conditional flow

        Works like other if_ actions - use with start_block/end_block for multiple actions.
        Also supports nested then_actions/else_actions for Blockly-style conditionals.

        Logic:
        1. Check if instance is CLOSE to grid (with tolerance for floating point errors)
        2. If close, SNAP to exact grid position first
        3. Return True if on grid, False otherwise
        """
        grid_size = int(parameters.get("grid_size", 32))

        # STEP 1: Check if position is close to grid alignment (with tolerance)
        # Use small tolerance (0.5 pixels) to account for floating point precision
        tolerance = 0.5
        x_remainder = abs(instance.x % grid_size)
        y_remainder = abs(instance.y % grid_size)

        # Check if close to grid alignment (either near 0 or near grid_size)
        x_close_to_grid = (x_remainder < tolerance) or (x_remainder > grid_size - tolerance)
        y_close_to_grid = (y_remainder < tolerance) or (y_remainder > grid_size - tolerance)
        close_to_grid = x_close_to_grid and y_close_to_grid

        # STEP 2: If close to grid, snap to EXACT grid position FIRST
        if close_to_grid:
            instance.x = round(instance.x / grid_size) * grid_size
            instance.y = round(instance.y / grid_size) * grid_size

        # STEP 3: Now check if on exact grid (should be true after snapping)
        x_on_grid = (instance.x % grid_size) == 0
        y_on_grid = (instance.y % grid_size) == 0
        on_grid = x_on_grid and y_on_grid

        # If there are nested actions (Blockly-style), execute them
        then_actions = parameters.get('then_actions', [])
        else_actions = parameters.get('else_actions', [])

        if then_actions or else_actions:
            if on_grid:
                for action in then_actions:
                    self.execute_action(instance, action)
            else:
                for action in else_actions:
                    self.execute_action(instance, action)
            return None  # Don't affect next action flow

        # Return True/False for GM80-style conditional flow
        return on_grid
    def execute_check_keys_and_move_action(self, instance, parameters: Dict[str, Any]):
        """Check if movement keys are held and restart movement

        This creates precise grid-by-grid movement:
        1. Player stops at every grid position (via stop_if_no_keys)
        2. This action checks if keys are still held
        3. If yes, restart movement in that direction
        4. Player moves to next grid, stops, repeat

        This prevents overshoot while allowing smooth continuous movement
        when keys are held.

        Parameters:
            grid_size: Grid cell size (default 32)
            speed: Movement speed in pixels/frame (default 4)
        """
        grid_size = int(parameters.get("grid_size", 32))
        speed = float(parameters.get("speed", 4.0))

        # Get which keys are currently held down
        keys_pressed = getattr(instance, 'keys_pressed', set())

        # Only restart movement if on exact grid position
        on_grid = (instance.x % grid_size == 0) and (instance.y % grid_size == 0)
        if not on_grid:
            return

        # Set speed based on held keys (priority: horizontal over vertical)
        if "right" in keys_pressed:
            instance.hspeed = speed
            instance.vspeed = 0
        elif "left" in keys_pressed:
            instance.hspeed = -speed
            instance.vspeed = 0
        elif "up" in keys_pressed:
            instance.hspeed = 0
            instance.vspeed = -speed
        elif "down" in keys_pressed:
            instance.hspeed = 0
            instance.vspeed = speed
    def execute_if_collision_action(self, instance, parameters: Dict[str, Any]):
        """Execute collision check (GameMaker-style)

        Supports:
        - 'any': Check for collision with any object
        - 'solid': Check for collision with solid objects only
        - specific object name: Check for collision with that object type

        X and Y can be expressions like "other.hspeed*8" or plain numbers.

        Returns True if condition is met (next action executes), False otherwise.
        """
        x_expr = str(parameters.get("x", "0"))
        y_expr = str(parameters.get("y", "0"))
        object_type = parameters.get("object_type", parameters.get("object", "any"))
        not_flag = parameters.get("not_flag", False)

        # Debug: Show stored collision speeds
        collision_speeds = getattr(self, '_collision_speeds', {})
        if collision_speeds:
            logger.debug(f"  🔍 if_collision: Using collision speeds: {collision_speeds}")

        # Evaluate X offset expression using _parse_value
        try:
            x_offset = self._parse_value(x_expr, instance)
            logger.debug(f"  🔍 X expression '{x_expr}' evaluated to: {x_offset}")
            if x_offset is None or isinstance(x_offset, str):
                x_offset = 0
            x_offset = float(x_offset)
        except Exception as e:
            logger.error(f"⚠️ Error evaluating X expression '{x_expr}': {e}")
            x_offset = 0.0

        # Evaluate Y offset expression using _parse_value
        try:
            y_offset = self._parse_value(y_expr, instance)
            logger.debug(f"  🔍 Y expression '{y_expr}' evaluated to: {y_offset}")
            if y_offset is None or isinstance(y_offset, str):
                y_offset = 0
            y_offset = float(y_offset)
        except Exception as e:
            logger.error(f"⚠️ Error evaluating Y expression '{y_expr}': {e}")
            y_offset = 0.0

        # Calculate check position
        check_x = instance.x + x_offset
        check_y = instance.y + y_offset

        # Perform the collision check using game_runner
        # Exclude the "other" instance from collision events (e.g., when rock checks for
        # collisions while being pushed by explorer, don't count the explorer itself)
        has_collision = False
        exclude_instance = getattr(self, '_collision_other', None)
        if self.game_runner:
            has_collision = self.game_runner.check_collision_at_position(
                instance, check_x, check_y, object_type, exclude_instance
            )
        else:
            logger.debug("  ⚠️ if_collision: game_runner is None! Cannot check collisions.")

        # Apply NOT flag
        result = not has_collision if not_flag else has_collision

        logger.debug(f"  ❓ if_collision at ({check_x}, {check_y}) for '{object_type}': collision={has_collision}, not_flag={not_flag}, result={result}")

        return result
    def execute_check_empty_action(self, instance, parameters: Dict[str, Any]):
        """True when (x, y) has no collision.

        Parameters:
            x, y: position to check (expressions OK, e.g. "self.x + 32").
                  Absolute by default; treated as offsets from the instance when
                  `relative` is True (matches GM7/8 action_if_empty semantics).
            objects: "solid" (only solid instances count as blocking, default)
                     or "all" (any instance blocks).
            only_solid: Legacy boolean alias. True → "solid", False → "all".
                        Used when older saves don't have `objects`.
            relative: If True, x/y are offsets from the instance's position.

        Returns True if the position is empty, False otherwise. Pair with
        start_block/end_block to gate subsequent actions (GM-style).
        """
        x_expr = str(parameters.get("x", "self.x"))
        y_expr = str(parameters.get("y", "self.y"))
        objects = parameters.get("objects")
        if objects is None:
            # Back-compat with the older boolean param
            objects = "solid" if parameters.get("only_solid", True) else "all"

        # Resolve expressions
        try:
            x_val = self._parse_value(x_expr, instance)
            x_val = float(x_val) if x_val is not None and not isinstance(x_val, str) else 0.0
        except Exception as e:
            logger.error(f"⚠️ check_empty: bad X expression '{x_expr}': {e}")
            x_val = 0.0
        try:
            y_val = self._parse_value(y_expr, instance)
            y_val = float(y_val) if y_val is not None and not isinstance(y_val, str) else 0.0
        except Exception as e:
            logger.error(f"⚠️ check_empty: bad Y expression '{y_expr}': {e}")
            y_val = 0.0

        if parameters.get("relative", False):
            x_val += instance.x
            y_val += instance.y

        # "solid" → only solid instances occupy the cell; "all" → ANY instance
        # does, solid or not (GM place_empty semantics). Note: do NOT map "all"
        # to "any" — check_collision_at_position's "any" is solid-only and would
        # ignore non-solid monsters, letting a pushed block teleport over one.
        object_type = "solid" if objects == "solid" else "all"

        has_collision = False
        if self.game_runner:
            exclude_instance = getattr(self, '_collision_other', None)
            has_collision = self.game_runner.check_collision_at_position(
                instance, x_val, y_val, object_type, exclude_instance)
        else:
            logger.debug("  ⚠️ check_empty: game_runner is None, treating as empty")

        result = not has_collision
        logger.debug(f"  🔍 check_empty at ({x_val}, {y_val}) objects={objects}: empty={result}")
        return result
    def execute_if_collision_at_action(self, instance, parameters: Dict[str, Any]):
        """Execute collision check with conditional actions"""
        x_expr = parameters.get("x", "self.x")
        y_expr = parameters.get("y", "self.y")
        object_type = parameters.get("object_type", parameters.get("object", "any"))
        then_actions = parameters.get("then_actions", [])
        else_actions = parameters.get("else_actions", [])

        # Store collision check for game_runner to process
        if not hasattr(instance, 'collision_checks'):
            instance.collision_checks = []

        instance.collision_checks.append({
            'x': x_expr,
            'y': y_expr,
            'object_type': object_type,
            'then_actions': then_actions,
            'else_actions': else_actions
        })
    def execute_if_object_exists_action(self, instance, parameters: Dict[str, Any]):
        """Check if any instance of an object type exists in the room

        Parameters:
            object: The object type to check for
            not_flag: If True, returns True when object does NOT exist

        Returns True if condition is met (for conditional flow), False otherwise.
        """
        object_type = parameters.get("object", "")
        not_flag = parameters.get("not_flag", False)

        if not object_type:
            logger.debug("  ⚠️ if_object_exists: No object type specified")
            return False

        # Count instances of the specified object type
        exists = False
        count = 0
        if self.game_runner and self.game_runner.current_room:
            for room_instance in self.game_runner.current_room.instances:
                # Skip instances already marked for destruction this frame, so
                # "level cleared" gating doesn't lag a frame behind the kill
                # (matches test_instance_count / the instance_count condition).
                if (room_instance.object_name == object_type
                        and not getattr(room_instance, 'to_destroy', False)):
                    count += 1
                    exists = True

        # Apply NOT flag
        result = not exists if not_flag else exists

        logger.debug(f"  ❓ if_object_exists: '{object_type}' count={count}, exists={exists}, not_flag={not_flag}, result={result}")

        return result
    def execute_if_can_push_action(self, instance, parameters: Dict[str, Any]):
        """Check if a box/object can be pushed in the current movement direction (Sokoban-style)

        Checks if the space behind the target object is free of solid objects.
        Works with both speed-based movement (hspeed/vspeed) and grid movement (intended_x/y).

        Parameters:
            direction: 'facing' (uses instance movement direction)
            object_type: type of object being pushed (informational)
            then_action: action to run if push is possible ('push_and_move')
            else_action: action to run if push is blocked ('stop_movement')

        Returns True if the box can be pushed, False otherwise.
        """
        other = getattr(self, '_collision_other', None)
        if not other:
            logger.debug("  ⚠️ if_can_push: No collision other instance")
            return False

        grid_size = 32

        # Determine push direction from either speed or grid movement
        # "mover" is the instance that has movement direction
        # "push_target" is the instance that gets pushed
        hspeed = getattr(instance, 'hspeed', 0)
        vspeed = getattr(instance, 'vspeed', 0)

        # By default, direction comes from instance, push target is other
        # (event on soko: soko moves, box gets pushed)
        mover = instance
        push_target = other
        dx, dy = 0, 0

        if hspeed != 0 or vspeed != 0:
            dx = hspeed
            dy = vspeed
        else:
            dx = getattr(instance, '_last_grid_move_dx', 0)
            dy = getattr(instance, '_last_grid_move_dy', 0)
            if dx == 0 and dy == 0:
                intended_x = getattr(instance, 'intended_x', instance.x)
                intended_y = getattr(instance, 'intended_y', instance.y)
                dx = intended_x - instance.x
                dy = intended_y - instance.y

        if dx == 0 and dy == 0:
            # Instance has no movement - check if the OTHER instance is the mover
            # (event on box: soko is the mover, box gets pushed = instance itself)
            other_hspeed = getattr(other, 'hspeed', 0)
            other_vspeed = getattr(other, 'vspeed', 0)

            if other_hspeed != 0 or other_vspeed != 0:
                dx = other_hspeed
                dy = other_vspeed
            else:
                dx = getattr(other, '_last_grid_move_dx', 0)
                dy = getattr(other, '_last_grid_move_dy', 0)
                if dx == 0 and dy == 0:
                    intended_x = getattr(other, 'intended_x', other.x)
                    intended_y = getattr(other, 'intended_y', other.y)
                    dx = intended_x - other.x
                    dy = intended_y - other.y

            if dx == 0 and dy == 0:
                # Also try collision speeds as last resort
                collision_speeds = getattr(self, '_collision_speeds', {})
                dx = collision_speeds.get('other_hspeed', 0)
                dy = collision_speeds.get('other_vspeed', 0)

            if dx == 0 and dy == 0:
                logger.debug("  ⚠️ if_can_push: Neither instance nor other has movement")
                return False

            # Swap roles: other is the mover, instance (self) is the push target
            mover = other
            push_target = instance
            logger.debug(f"  🔄 if_can_push: event on pushed object, direction from {other.object_name}")

        # Calculate push direction (one grid cell in movement direction)
        push_dx = grid_size if dx > 0 else (-grid_size if dx < 0 else 0)
        push_dy = grid_size if dy > 0 else (-grid_size if dy < 0 else 0)

        # Check if space behind the push target is free
        behind_x = push_target.x + push_dx
        behind_y = push_target.y + push_dy

        can_push = True
        if self.game_runner and self.game_runner.current_room:
            # Check for solid objects at the push destination
            if self.game_runner.check_collision_at_position(
                push_target, behind_x, behind_y, "solid", exclude_instance=mover
            ):
                can_push = False
            else:
                # Check for any object type the mover has collision events with
                # (e.g. soko has collision_with_obj_box and collision_with_obj_box_store)
                # These are "interactive" objects that should block pushes
                collision_targets = getattr(mover, '_collision_targets', {})
                for target_name in collision_targets:
                    if self.game_runner.check_collision_at_position(
                        push_target, behind_x, behind_y, target_name, exclude_instance=mover
                    ):
                        can_push = False
                        break

        logger.debug(f"  ❓ if_can_push: push_target=({push_target.x},{push_target.y}), behind=({behind_x},{behind_y}), can_push={can_push}")

        then_action = parameters.get('then_action', '')
        else_action = parameters.get('else_action', '')

        if can_push:
            if then_action == 'push_and_move':
                # Push the target in the direction of movement
                push_target.x += push_dx
                push_target.y += push_dy
                logger.debug(f"  📦 Pushed {push_target.object_name} to ({push_target.x}, {push_target.y})")
                # Update spatial grid if available
                if self.game_runner and self.game_runner.current_room:
                    if hasattr(self.game_runner.current_room, 'update_spatial_grid'):
                        self.game_runner.current_room.update_spatial_grid(push_target)
        else:
            if else_action == 'stop_movement':
                # Stop the mover (not necessarily instance - could be other if event is on box)
                mover.hspeed = 0
                mover.vspeed = 0
                # `speed` is a read-only property derived from hspeed/vspeed
                # (L5, docs/FULL_AUDIT_2026-09-07.md) -- zeroing those two is
                # enough, there is nothing separate left to write.
                # Revert mover position if it overlapped with push_target (non-solid case)
                last_dx = getattr(mover, '_last_grid_move_dx', 0)
                last_dy = getattr(mover, '_last_grid_move_dy', 0)
                if last_dx != 0 or last_dy != 0:
                    w1 = getattr(mover, '_cached_width', 32)
                    h1 = getattr(mover, '_cached_height', 32)
                    w2 = getattr(push_target, '_cached_width', 32)
                    h2 = getattr(push_target, '_cached_height', 32)
                    if self.game_runner and self.game_runner.rectangles_overlap(
                        mover.x, mover.y, w1, h1,
                        push_target.x, push_target.y, w2, h2
                    ):
                        mover.x -= last_dx
                        mover.y -= last_dy
                        logger.debug(f"  ↩️ Reverted mover position to ({mover.x}, {mover.y})")
                logger.debug("  🛑 Stopped movement (can't push)")

        return can_push
    def execute_test_variable_action(self, instance, parameters: Dict[str, Any]):
        """Test an instance or global variable

        Returns True if condition met, False otherwise

        Parameters:
            variable: Variable name. "variable_name" is also accepted as a legacy alias
                for projects saved before the schema alignment (see events/action_types.py).
            value: Value to compare against
            scope: "sel"/"self" instance var, "other" collision other, "global" global var
            operation: Comparison operator (equal, less, greater, etc.)
        """
        variable = parameters.get("variable") or parameters.get("variable_name") or ""
        value_str = parameters.get("value", "0")
        scope = parameters.get("scope", "sel")
        operation = parameters.get("operation", "equal")

        if not variable:
            logger.debug("⚠️  test_variable: No variable name specified")
            return False

        # Get current value based on scope / GM "Applies to" target
        if scope == "global":
            if not self.game_runner:
                return False
            current = self.game_runner.global_variables.get(variable, 0)
        elif "target" in parameters:
            # GM's "Applies to" on a question (emitted by the GMK importer):
            # "other" reads the collision partner (maze_4's obj_person tests
            # other.afraid on the monster it just touched); "object" reads the
            # first live instance of that object — an approximation of GM's
            # per-instance question execution, adequate for the shared-state
            # checks imported games actually use.
            targets = self._resolve_target_instances(instance, parameters)
            if not targets:
                logger.debug("⚠️  test_variable: 'Applies to' target resolved to no instances")
                return False
            current = getattr(targets[0], variable, 0)
        elif scope == "other":
            # Get the "other" instance from collision context
            other = getattr(self, '_collision_other', None)
            if not other:
                logger.debug("⚠️  test_variable: 'other' scope only available in collision events")
                return False
            current = getattr(other, variable, 0)
        else:  # scope == "sel"
            current = getattr(instance, variable, 0)

        # Parse comparison value
        compare_value = self._parse_value(value_str, instance)

        # Perform comparison
        try:
            if operation == "equal":
                result = current == compare_value
            elif operation == "less":
                result = current < compare_value
            elif operation == "greater":
                result = current > compare_value
            elif operation == "less_equal":
                result = current <= compare_value
            elif operation == "greater_equal":
                result = current >= compare_value
            elif operation == "not_equal":
                result = current != compare_value
            else:
                result = False
        except TypeError:
            # Can't compare these types
            result = False

        scope_label = "other" if scope == "other" else ("global" if scope == "global" else "sel")
        logger.debug(f"❓ Test {scope_label}.{variable} ({current}) {operation} {compare_value}: {result}")
        return result
    def execute_test_chance_action(self, instance, parameters: Dict[str, Any]):
        """Test a random probability (1 in N chance)

        Parameters:
            sides: Number of sides on the dice (default 6)

        Returns True if the random roll succeeds (1/N probability)
        """
        import random

        sides = parameters.get("sides", 6)
        try:
            sides = int(sides)
            if sides < 1:
                sides = 1
        except (ValueError, TypeError):
            sides = 6

        # Roll the dice - success if we roll a 1 (1/N chance)
        roll = random.randint(1, sides)
        result = (roll == 1)

        logger.debug(f"🎲 Test chance (1 in {sides}): rolled {roll}, result={result}")
        return result
    def execute_test_expression_action(self, instance, parameters: Dict[str, Any]):
        """Test/evaluate a GML-style expression

        Parameters:
            expression: String expression to evaluate (can access instance variables)

        Returns True if expression evaluates to truthy value, False otherwise

        Expressions are evaluated as strict Python — this project teaches
        Python, so use Python operators (`and`/`or`/`not`), not C/GML-style
        `&&`/`||`/`!`. The latter raise SyntaxError and the expression is
        treated as False.

        Supported expressions:
        - Variable comparisons: "x < 100", "score >= 1000"
        - Math expressions: "x + y > 200", "hspeed * 2 < 10"
        - Boolean expressions: "lives > 0 and health > 50"
        - Instance properties: "self.x", "self.y", "self.hspeed"
        - Collision partner (in collision events): "other.x", "other.y"
        """
        return self._eval_bool_expression(instance, parameters.get("expression", ""))
    def _eval_bool_expression(self, instance, expression) -> bool:
        """Evaluate a Python boolean expression in the instance/collision scope.

        Single source of truth shared by the Test Expression action and the
        if_condition "expression" condition type, so both evaluate identically.
        Strict Python (`and`/`or`/`not`), with `self`, `other` (the collision
        partner during collision events), the instance's own variables, and
        game state in scope. Returns False on empty input or any error.

        This is why a condition like "vspeed > 0 and y < other.y - 16" works:
        it is real Python via eval(), NOT the arithmetic-only mini-language in
        _parse_value / _evaluate_expression, which cannot handle `<` `>` or
        `and`/`or` (they make it return the raw string — always truthy — or 0).
        """
        if not expression or not str(expression).strip():
            return False
        expression = str(expression)

        # Teach Python: flag C/GML operators (&&, ||, !) and point at the
        # Python equivalent. These are SyntaxErrors in eval(), so without this
        # the student just sees the expression silently do nothing.
        for found, py in detect_c_style_operators(expression):
            logger.warning(
                f"⚠️  expression: '{found}' is not a Python operator — "
                f"use '{py}' instead (in expression: {expression!r})")

        # `global.NAME` is real Python syntax nowhere -- `global` is a
        # reserved keyword, so `global.is_host == 1` is a SyntaxError in the
        # eval() below regardless of what the namespace contains (confirmed
        # empirically; docs/MULTIPLAYER_LAN_V2_PLAN.md's "Core changes"
        # section assumed this "just works" the same way _parse_value's
        # separate dotted-global handling does, but that assumption was
        # never true for THIS evaluator). Rewritten here to a safe dict
        # lookup (default 0, matching _parse_value's own missing-global
        # default) before eval ever sees it -- _parse_value/
        # _evaluate_expression are untouched, since their existing
        # dotted-global handling already works correctly.
        expression = re.sub(
            r'\bglobal\.([A-Za-z_][A-Za-z0-9_]*)\b', r"_global.get('\1', 0)", expression)

        try:
            namespace = {
                'self': instance,
                # Collision partner — populated during collision events so
                # expressions such as "y < other.y" resolve; None otherwise.
                'other': getattr(self, '_collision_other', None),
                'x': instance.x,
                'y': instance.y,
                'hspeed': getattr(instance, 'hspeed', 0),
                'vspeed': getattr(instance, 'vspeed', 0),
                'speed': getattr(instance, 'speed', 0),
                'direction': getattr(instance, 'direction', 0),
                'image_index': getattr(instance, 'image_index', 0),
                'image_speed': getattr(instance, 'image_speed', 1.0),
                'score': getattr(self.game_runner, 'score', 0) if self.game_runner else 0,
                'lives': getattr(self.game_runner, 'lives', 0) if self.game_runner else 0,
                'health': getattr(self.game_runner, 'health', 100) if self.game_runner else 100,
                'room_width': getattr(self.game_runner.current_room, 'width', 0) if self.game_runner and self.game_runner.current_room else 0,
                'room_height': getattr(self.game_runner.current_room, 'height', 0) if self.game_runner and self.game_runner.current_room else 0,
                'abs': abs, 'min': min, 'max': max, 'round': round,
                '_global': self.game_runner.global_variables if self.game_runner else {},
                # Custom instance variables
                **{k: v for k, v in instance.__dict__.items() if not k.startswith('_')}
            }
            result = eval(expression, {"__builtins__": {}}, namespace)  # nosec B307 - builtins stripped; GML conditional path over author-authored project data, no untrusted channel
            logger.debug(f"📝 Expression '{expression}' = {result} (bool: {bool(result)})")
            return bool(result)
        except Exception as e:
            logger.error(f"⚠️  Error evaluating expression '{expression}': {e}")
            return False
    def execute_test_question_action(self, instance, parameters: Dict[str, Any]):
        """Show a yes/no question dialog to the user (M4,
        docs/FULL_AUDIT_2026-09-07.md).

        Parameters:
            question: Question text to display

        Returns True if the player answers Yes, False if No. Blocks the
        game loop until answered -- runtime/game_runner.py's
        show_question_dialog is the same pygame modal machinery
        show_message/splash_show_text already use, not the removed
        QMessageBox-based version. That Qt dialog only ever ran in the
        in-process IDE fallback (QApplication.instance() is not None);
        the real game process -- the Test Game subprocess and every
        desktop export, both driven by runtime/run_game.py, which never
        creates a QApplication -- always took the "no QApplication"
        branch and answered Yes unconditionally, so authors got a
        conditional that never actually asked.
        """
        question = parameters.get("question", "Continue?")

        runner = self.game_runner
        if (runner is not None and getattr(runner, 'screen', None) is not None
                and hasattr(runner, 'show_question_dialog')):
            return runner.show_question_dialog(str(question))

        logger.debug(f"⚠️  test_question: No live screen -- defaulting to True for '{question}'")
        return True

    def execute_test_instance_count_action(self, instance, parameters: Dict[str, Any]):
        """Test the number of instances of a specific object type

        Parameters:
            object: Object type name to count
            number: Number to compare against
            operation: Comparison operator (equal, less, greater, less_equal, greater_equal, not_equal)

        Returns True if condition is met, False otherwise

        Example:
            - Check if there are exactly 5 enemies: object="obj_enemy", number=5, operation="equal"
            - Check if there are less than 10 bullets: object="obj_bullet", number=10, operation="less"
        """
        object_type = parameters.get("object", "")
        target_count = parameters.get("number", 0)
        operation = parameters.get("operation", "equal")

        if not object_type:
            logger.debug("⚠️  test_instance_count: No object type specified")
            return False

        try:
            target_count = int(target_count)
        except (ValueError, TypeError):
            logger.warning(f"⚠️  test_instance_count: Invalid number '{target_count}'")
            return False

        # Count instances of this object type
        if not self.game_runner or not self.game_runner.current_room:
            logger.debug("⚠️  test_instance_count: No game runner or instances available")
            return False

        # Count instances matching the object type, excluding those marked for destruction
        actual_count = sum(1 for inst in self.game_runner.current_room.instances
                          if getattr(inst, 'object_name', '') == object_type
                          and not getattr(inst, 'to_destroy', False))

        # Perform comparison
        result = False
        if operation == "equal":
            result = (actual_count == target_count)
        elif operation == "less":
            result = (actual_count < target_count)
        elif operation == "greater":
            result = (actual_count > target_count)
        elif operation == "less_equal":
            result = (actual_count <= target_count)
        elif operation == "greater_equal":
            result = (actual_count >= target_count)
        elif operation == "not_equal":
            result = (actual_count != target_count)
        else:
            logger.debug(f"⚠️  test_instance_count: Unknown operation '{operation}'")
            return False

        logger.debug(f"🔢 Test instance count: {object_type} count={actual_count} {operation} {target_count} → {result}")
        return result
    def execute_if_condition_action(self, instance, parameters: Dict[str, Any]):
        """Execute a conditional action with then/else action lists

        Evaluates a condition and executes the appropriate action list.

        Parameters:
            condition_type: Type of condition (instance_count, variable_compare, etc.)
            then_actions: Actions to execute if condition is true
            else_actions: Actions to execute if condition is false
            (plus condition-specific parameters)
        """
        condition_type = parameters.get("condition_type", "instance_count")

        # Evaluate the condition and return the boolean. The generic
        # nested-conditional branch in execute_action runs the appropriate
        # then_actions / else_actions list exactly once — running them here too
        # double-executed every branch (M43 cleanup; verified count went 2→1).
        result = self._evaluate_if_condition(instance, condition_type, parameters)

        logger.debug(f"❓ if_condition ({condition_type}): result={result}")

        return result
    def execute_check_sound_action(self, instance, parameters: Dict[str, Any]):
        """Check if a sound is currently playing

        Parameters:
            sound: The sound name to check
            not_flag: If True, inverts the result (checks if NOT playing)

        Returns:
            True if sound is playing (or not playing if not_flag is True)
        """
        sound_name = parameters.get("sound", "")
        not_flag = parameters.get("not_flag", False)

        if isinstance(not_flag, str):
            not_flag = not_flag.lower() in ('true', '1', 'yes')

        if not sound_name:
            logger.debug("⚠️ check_sound: No sound specified")
            return not not_flag  # Return True if NOT checking, False otherwise

        if not self.game_runner:
            logger.debug("⚠️ check_sound: No game_runner reference")
            return not not_flag

        is_playing = False

        # Check if the sound exists and is playing
        if hasattr(self.game_runner, 'sounds') and sound_name in self.game_runner.sounds:
            sound = self.game_runner.sounds[sound_name]
            if hasattr(sound, 'get_num_channels'):
                # pygame.mixer.Sound object
                is_playing = sound.get_num_channels() > 0
            else:
                # Fallback: check pygame mixer directly (only import if needed)
                import pygame
                if pygame.mixer.get_init():
                    is_playing = pygame.mixer.get_busy()

        result = is_playing if not not_flag else not is_playing
        logger.debug(f"🎵 Check sound '{sound_name}': playing={is_playing}, not_flag={not_flag}, result={result}")
        return result
