#!/usr/bin/env python3
"""Room navigation and room-configuration actions for
:class:`~runtime.action_executor.ActionExecutor`.

Sixteen methods: next/previous/goto/restart room (each with its legacy
``room_goto*`` alias spelling), the two "does a neighbouring room exist"
conditionals and the ``_dispatch_room_test`` / ``_room_neighbor_exists``
helpers behind them, ``check_room``, and the three per-room settings actions
(caption, persistent, speed).

Extracted verbatim from ``runtime/action_executor.py``
(``docs/POST_1_0_REFACTOR.md`` File 4, cluster 4) as a MIXIN -- see
``runtime/action_drawing.py``'s header for why these are sibling modules rather
than the package layout the plan sketched.

Named ``RoomMixin`` rather than the plan's ``RoomNavMixin`` because the cluster
that actually holds together includes the room *configuration* actions, not
just navigation.

The two helpers travel WITH the cluster: the audit found every call to them
comes from inside it, and the four navigation actions call each other
(``goto_room`` is the common implementation the rest delegate to). What stays
on ``ActionExecutor`` and is reached through ``self`` -- ``_parse_value``,
``_resolve_room_sentinel``, and ``execute_action`` itself -- has callers well
beyond this file.
"""

from typing import Any, Dict

from core.logger import get_logger

logger = get_logger(__name__)


class RoomMixin:
    """Room navigation / configuration ``execute_*_action`` methods."""

    def execute_restart_room_action(self, instance, parameters: Dict[str, Any]):
        """Execute restart room action - resets current level"""
        logger.debug(f"🔄 Restart room requested by {instance.object_name}")
        instance.restart_room_flag = True
    # Alias for room_restart (GameMaker naming convention)
    def execute_room_restart_action(self, instance, parameters: Dict[str, Any]):
        """Alias for restart_room (GameMaker naming convention)"""
        return self.execute_restart_room_action(instance, parameters)
    def execute_next_room_action(self, instance, parameters: Dict[str, Any]):
        """Execute next room action - advances to next level"""
        logger.debug(f"➡️  NEXT ROOM requested by {instance.object_name}")
        instance.next_room_flag = True
    # Alias for room_goto_next (GameMaker naming convention)
    def execute_room_goto_next_action(self, instance, parameters: Dict[str, Any]):
        """Alias for next_room (GameMaker naming convention)"""
        return self.execute_next_room_action(instance, parameters)
    def execute_previous_room_action(self, instance, parameters: Dict[str, Any]):
        """Execute previous room action - goes to previous level"""
        logger.debug(f"⬅️  Previous room requested by {instance.object_name}")
        instance.previous_room_flag = True
    # Alias for room_goto_previous (GameMaker naming convention)
    def execute_room_goto_previous_action(self, instance, parameters: Dict[str, Any]):
        """Alias for previous_room (GameMaker naming convention)"""
        return self.execute_previous_room_action(instance, parameters)
    def _room_neighbor_exists(self, direction: int) -> bool:
        """Return True if the current room has a neighbour in `direction` (+1 = next, -1 = previous)."""
        if not self.game_runner:
            return False
        room_list = self.game_runner.get_room_list()
        current_room = self.game_runner.current_room
        if not (current_room and room_list):
            return False
        try:
            current_index = room_list.index(current_room.name)
        except ValueError:
            return False
        target_index = current_index + direction
        return 0 <= target_index < len(room_list)
    def _dispatch_room_test(self, instance, parameters: Dict[str, Any], result: bool, label: str):
        """Shared kernel for if_next_room_exists / if_previous_room_exists.

        Supports both Blockly-style nested then_actions/else_actions and the
        GM80 flat skip_next pattern (returns True/False to gate the next
        action in the list). The "if no next room" case is expressed via the
        nested form's else_actions slot — no separate inverted action needed.
        """
        logger.debug(f"❓ {label}: {result}")
        then_actions = parameters.get('then_actions', [])
        else_actions = parameters.get('else_actions', [])
        if then_actions or else_actions:
            for action in (then_actions if result else else_actions):
                self.execute_action(instance, action)
            return None
        return result
    def execute_if_next_room_exists_action(self, instance, parameters: Dict[str, Any]):
        """Conditional: True iff a next room exists.

        Flat (GM80) form: gates the immediately-following action via skip_next.
        Nested form: runs then_actions / else_actions — use else_actions to
        do something (e.g. game_end) when this is the last room.
        """
        return self._dispatch_room_test(instance, parameters, self._room_neighbor_exists(+1), "Next room exists")
    def execute_if_previous_room_exists_action(self, instance, parameters: Dict[str, Any]):
        """Conditional: True iff a previous room exists. See if_next_room_exists for forms."""
        return self._dispatch_room_test(instance, parameters, self._room_neighbor_exists(-1), "Previous room exists")
    def execute_set_room_caption_action(self, instance, parameters: Dict[str, Any]):
        """Set room/window caption text

        Parameters:
            caption: Caption text to display
        """
        if not self.game_runner:
            logger.debug("⚠️ set_room_caption: No game_runner reference")
            return

        # Get caption directly (no expression parsing for text)
        caption = str(parameters.get("caption", ""))

        # Update the window caption
        self.game_runner.window_caption = caption

        # Update the display caption immediately
        self.game_runner.update_caption()

        logger.debug(f"🏷️ Set room caption: '{caption}'")
    def execute_set_room_speed_action(self, instance, parameters: Dict[str, Any]):
        """Set game speed (frames per second)

        Parameters:
            speed: Target FPS (default: 30)
        """
        if not self.game_runner:
            logger.debug("⚠️ set_room_speed: No game_runner reference")
            return

        # Parse speed with expression support
        speed = self._parse_value(parameters.get("speed", 30), instance)

        try:
            speed = int(speed)
            if speed < 1:
                speed = 1
            if speed > 240:
                speed = 240  # Cap at reasonable maximum
        except (ValueError, TypeError):
            speed = 30

        # Update the game FPS
        self.game_runner.fps = speed

        logger.debug(f"⏱️ Set room speed: {speed} FPS")
    def execute_set_room_persistent_action(self, instance, parameters: Dict[str, Any]):
        """Set whether the current room is persistent

        Parameters:
            persistent: If True, room state is preserved when leaving (default: True)

        When a room is persistent:
        - Instance positions and states are preserved when leaving
        - The room is not recreated when re-entering
        - Useful for keeping progress in a level
        """
        if not self.game_runner or not self.game_runner.current_room:
            logger.debug("⚠️ set_room_persistent: No current room")
            return

        # Parse parameter
        persistent = self._parse_value(parameters.get("persistent", True), instance)

        # Convert to boolean if string
        if isinstance(persistent, str):
            persistent = persistent.lower() in ('true', '1', 'yes')

        # Set room persistence
        self.game_runner.current_room.persistent = bool(persistent)

        logger.debug(f"💾 Set room persistent: {persistent}")
    def execute_goto_room_action(self, instance, parameters: Dict[str, Any]):
        """Go to a specific room

        Parameters:
            room: Target room name
            transition: 'fade' fades to black, switches, fades back in
                (GameRunner.change_room / _fade_overlay). Any other value
                (including the default 'none') is an instant switch —
                only 'fade' is implemented; desktop pygame runtime only,
                Kivy/HTML5 exports still switch instantly (see TODO.md).
        """
        room_name = parameters.get("room", "")
        transition = parameters.get("transition", "none")

        if not room_name:
            logger.debug("⚠️ goto_room: No room specified")
            return

        if not self.game_runner:
            logger.debug("⚠️ goto_room: No game_runner reference")
            return

        # The action editor offers "→ Next Room" / "← Previous Room" /
        # "↺ Restart Current Room" as the most prominent dropdown entries and
        # saves them as these sentinels. Map them onto the existing navigation
        # flags the game loop already processes, instead of treating them as
        # unknown room names (which silently did nothing).
        if room_name == "__next__":
            instance.next_room_flag = True
            logger.debug("🚪 goto_room: next room requested")
            return
        if room_name == "__prev__":
            instance.previous_room_flag = True
            logger.debug("🚪 goto_room: previous room requested")
            return
        if room_name == "__current__":
            instance.restart_room_flag = True
            logger.debug("🚪 goto_room: restart current room requested")
            return

        # Check if room exists
        room_list = self.game_runner.get_room_list()
        if room_name not in room_list:
            logger.debug(f"⚠️ goto_room: Room '{room_name}' not found")
            return

        # Set the target room for navigation
        instance.goto_room_target = room_name
        instance.goto_room_transition = transition

        logger.debug(f"🚪 Go to room '{room_name}' requested (transition: {transition})")
    # Alias for room_goto (GameMaker naming convention)
    def execute_room_goto_action(self, instance, parameters: Dict[str, Any]):
        """Alias for goto_room (GameMaker naming convention)"""
        return self.execute_goto_room_action(instance, parameters)
    def execute_check_room_action(self, instance, parameters: Dict[str, Any]):
        """Check if currently in a specific room

        Parameters:
            room: Room name to check
            not_flag: If True, inverts the result (checks if NOT in room)

        Returns:
            True if in the specified room (or not in it if not_flag is True)
        """
        room_name = parameters.get("room", "")
        not_flag = parameters.get("not_flag", False)

        if isinstance(not_flag, str):
            not_flag = not_flag.lower() in ('true', '1', 'yes')

        if not room_name:
            logger.debug("⚠️ check_room: No room specified")
            return not not_flag

        if not self.game_runner or not self.game_runner.current_room:
            logger.debug("⚠️ check_room: No game_runner or current_room")
            return not not_flag

        # Resolve the navigation sentinels the action editor may save against
        # the room list so the comparison is meaningful instead of always
        # false. "__current__" always matches the current room; "__next__" /
        # "__prev__" resolve to the adjacent room name (or no match at an end).
        if room_name in ("__next__", "__prev__", "__current__"):
            room_name = self._resolve_room_sentinel(room_name)

        is_in_room = (self.game_runner.current_room.name == room_name)
        result = is_in_room if not not_flag else not is_in_room

        logger.debug(f"❓ Check room '{room_name}': in_room={is_in_room}, not_flag={not_flag}, result={result}")
        return result
