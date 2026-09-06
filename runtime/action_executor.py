#!/usr/bin/env python3
"""
Action Execution Engine - WITH GRID SNAPPING
Converts visual actions into runtime behavior
"""

import math
import re
from typing import Dict, Any, List, Tuple
from runtime.action_colors import _hex_to_rgb
from core.logger import get_logger
# Absolute import, matching runtime/game_runner.py's mixin precedent.
# runtime/__init__.py is deliberately pygame-free, so this keeps the
# "importable without pygame" property 35 tests rely on.
from runtime.action_flow import (FlowMixin, _ExitEvent,
                                 detect_c_style_operators)
from runtime.action_drawing import DrawingMixin
from runtime.action_particles import ParticleTimelineMixin
from runtime.action_spawn import SpawnMixin
from runtime.action_room import RoomMixin
from runtime.action_score_lives_health import ScoreLivesHealthMixin
from runtime.action_movement import MovementMixin
logger = get_logger(__name__)


# The raycast HUD builders (build_minimap_commands, build_doom_hud_commands,
# doom_face_frame) + MINIMAP_HEADING_LEN / MINIMAP_MARKER_HALF MOVED to
# extensions/raycast_2_5d/hud.py (Stage B3, docs/RAYCAST_EXTENSION_PLAN.md).


# GM's Set Font action encodes horizontal align as a 0/1/2 menu; the converter
# now translates it to `halign`, but pre-fix imported projects still carry the
# raw GM key, so execute_set_draw_font_action reads this as a fallback.
_GM_FONT_ALIGN_FALLBACK = {"0": "left", "1": "center", "2": "right",
                           0: "left", 1: "center", 2: "right",
                           "left": "left", "center": "center", "right": "right"}






class _ExecKeyboard:
    """`keyboard` binding for execute_code/execute_script namespaces.

    The code editor's if_condition(key_pressed) generator emits
    `keyboard.check("space")`, but no `keyboard` object existed in the exec
    namespace, so once a structured key condition round-tripped through Edit
    Custom Code into an execute_code blob it raised NameError every frame and
    the gated behaviour died (audit M20). check() mirrors the structured
    key_pressed handler: lowercase pygame key names held in
    instance.keys_pressed.
    """

    __slots__ = ('_instance',)

    def __init__(self, instance):
        self._instance = instance

    def check(self, key) -> bool:
        return str(key).lower() in getattr(self._instance, 'keys_pressed', set())

    # GameMaker-ish alias
    check_pressed = check



class ActionExecutor(DrawingMixin, MovementMixin, ScoreLivesHealthMixin, RoomMixin, SpawnMixin, ParticleTimelineMixin, FlowMixin):
    """Executes visual actions during gameplay with auto-discovery"""

    def __init__(self, game_runner=None):
        # Action handlers dictionary - auto-populated via discovery
        self.action_handlers = {}

        # Reference to game runner for accessing global state (score, lives, health)
        self.game_runner = game_runner

        # Deferred create events queue - processed after current event completes
        # This fixes timing issues where create events check conditions before
        # the triggering action list finishes (e.g., instance count checks)
        self._deferred_create_events = []
        self._event_depth = 0  # Track nested event execution depth

        # Auto-discover all action handler methods
        self._register_action_handlers()

        logger.debug(f"✅ ActionExecutor initialized with {len(self.action_handlers)} action handlers")

    def _register_action_handlers(self):
        """Automatically discover and register action handler methods

        Any method named execute_*_action will be automatically registered
        as a handler for the action name (the part between execute_ and _action)

        Example: execute_move_grid_action -> handles "move_grid" action

        Then, modular handlers from runtime/action_handlers/ are registered
        for any action names not already covered by executor methods.
        """
        # Phase 1: Auto-discover execute_*_action methods on this class
        for attr_name in dir(self):
            # Look for methods matching the pattern execute_*_action
            if attr_name.startswith('execute_') and attr_name.endswith('_action'):
                # Extract action name: execute_move_grid_action -> move_grid
                action_name = attr_name[8:-7]  # Remove 'execute_' and '_action'

                # Skip if no action name (e.g., "execute_action" -> "")
                if not action_name:
                    continue

                # Get the method
                method = getattr(self, attr_name)

                # Verify it's callable
                if callable(method):
                    self.action_handlers[action_name] = method
                    logger.debug(f"  📌 Registered action handler: {action_name}")

        # Phase 2: Register modular handlers from action_handlers package.
        # These have signature (ctx, instance, params) where ctx is the executor.
        # Wrap them to match the dispatch signature (instance, params).
        try:
            from runtime.action_handlers import ACTION_HANDLERS

            def make_wrapper(fn):
                """Factory to correctly capture fn in closure"""
                def wrapper(instance, parameters):
                    return fn(self, instance, parameters)
                wrapper.__name__ = fn.__name__
                return wrapper

            modular_count = 0
            for action_name, handler_func in ACTION_HANDLERS.items():
                if action_name in self.action_handlers:
                    logger.debug(f"  ⚠️ Skipping modular handler '{action_name}' (executor method takes priority)")
                    continue
                self.action_handlers[action_name] = make_wrapper(handler_func)
                modular_count += 1
                logger.debug(f"  📦 Registered modular handler: {action_name}")

            if modular_count > 0:
                logger.debug(f"  📦 Registered {modular_count} modular action handlers")
        except ImportError as e:
            logger.warning(f"  ⚠️ Could not load modular action handlers: {e}")

    def register_custom_action(self, action_name: str, handler_func):
        """Register a custom action handler dynamically (for plugins)

        Args:
            action_name: The action name (e.g., 'play_sound')
            handler_func: A function with signature (instance, parameters) -> None
        """
        self.action_handlers[action_name] = handler_func
        logger.debug(f"  🔌 Registered custom action: {action_name}")

    def execute_event(self, instance, event_name: str, events_data: Dict[str, Any]):
        """Execute all actions in an event"""
        if event_name not in events_data:
            return

        # The create event fires at most once per instance lifetime. Re-entering
        # a PERSISTENT room's instances reuses the same (state-preserved)
        # objects, so without this guard create would re-run on every visit,
        # accumulating side effects (duplicate spawns, re-armed alarms, reset
        # variables) — M53. Room rebuilds (restart, or a non-persistent room's
        # rebuild-on-revisit — see GameRunner.change_room) produce fresh
        # instances with the flag unset, so create correctly fires again there.
        if event_name == "create":
            if getattr(instance, "_create_fired", False):
                return
            instance._create_fired = True

        event_data = events_data[event_name]
        actions = event_data.get("actions", [])

        if event_name == "create":
            obj_name = getattr(instance, 'object_name', instance.__class__.__name__)
            logger.debug(f"🎬 Executing CREATE event for {obj_name}")
            logger.debug(f"   Actions: {len(actions)} action(s)")
            if actions:
                logger.debug(f"   First action: {actions[0].get('action', 'unknown')}")

        # Track event execution depth for deferred create event processing
        self._event_depth += 1
        try:
            # Execute actions with conditional flow support
            self.execute_action_list(instance, actions)
        finally:
            self._event_depth -= 1
            self._drain_sound_queue(instance)

            # Process deferred create events when we return to top level
            # This ensures instance counts are accurate (e.g., after destroy_instance)
            if self._event_depth == 0 and self._deferred_create_events:
                self._process_deferred_create_events()

    def _drain_sound_queue(self, instance):
        """Play and clear sounds queued by execute_code via
        ``self._sound_queue.append('snd_name')`` (or a
        ``{'sound': name, 'volume': v}`` dict for a non-default volume).

        This is the desktop half of the cross-platform sound primitive —
        execute_code has no live `game` object on Kivy/Web exports, so code
        that wants to play a sound queues it here instead of calling
        `game.sounds[...].play()` directly, and the Kivy/Web runtimes drain
        their own mirror of this queue the same way.
        """
        queue = getattr(instance, '_sound_queue', None)
        if not queue:
            return
        sounds = getattr(self.game_runner, 'sounds', None) or {}
        for item in queue:
            if isinstance(item, dict):
                name = item.get('sound', '')
                volume = item.get('volume', 1.0)
            else:
                name = item
                volume = 1.0
            sound = sounds.get(name)
            if sound is None:
                logger.debug(f"⚠️ Queued sound '{name}' not found")
                continue
            try:
                sound.set_volume(float(volume))
                sound.play()
            except Exception as e:
                logger.debug(f"⚠️ Could not play queued sound '{name}': {e}")
        instance._sound_queue = []

    def _process_deferred_create_events(self):
        """Process any deferred create events

        Create events are deferred when instances are created mid-event so that
        conditions like instance_count are evaluated after the triggering event
        completes (e.g., after destroy_instance runs).
        """
        # Take the current queue and clear it (in case create events add more)
        events_to_process = self._deferred_create_events[:]
        self._deferred_create_events = []

        if events_to_process:
            logger.debug(f"🎬 Processing {len(events_to_process)} deferred CREATE event(s)")

        for new_instance, events in events_to_process:
            logger.debug(f"  🎬 Running deferred CREATE event for {new_instance.object_name}")
            self.execute_event(new_instance, 'create', events)

    def execute_action_list(self, instance, actions: list):
        """Execute a list of actions with conditional flow support

        GM80-style conditionals: test actions set skip_next flag to skip following action(s).
        The `exit_event` action raises _ExitEvent to short-circuit the rest of the list;
        we catch it here so callers don't need to know.
        """
        try:
            self._execute_action_list_inner(instance, actions)
        except _ExitEvent:
            return

    # Question actions: they return True/False and guard the following unit.
    # The skip logic needs to know them WITHOUT executing them — when a false
    # question's guarded unit is being skipped and that unit is ITSELF a
    # question, GM semantics skip the nested question AND its guarded unit,
    # recursively. (maze_4's obj_person step is the canonical chain:
    # test_alignment → if_collision(move_*) → start_moving_direction ×4; the
    # old skip-one-action logic ran every movement unconditionally whenever
    # the alignment check failed, force-feeding the last direction each frame.)
    _QUESTION_ACTIONS = frozenset({
        "check_empty", "check_room", "check_sound",
        "if_can_push", "if_collision", "if_collision_at", "if_condition",
        "if_next_room_exists", "if_object_exists", "if_on_grid",
        "if_previous_room_exists",
        "test_alignment", "test_chance", "test_expression", "test_health",
        "test_instance_count", "test_lives", "test_question", "test_score",
        "test_variable",
    })

    def _execute_action_list_inner(self, instance, actions: list):
        i = 0
        skip_next = False
        condition_was_false = False  # Track if original condition was false

        while i < len(actions):
            action_data = actions[i]
            action_name = action_data.get("action", "")

            # Handle else action (supports both else_action and else_block)
            if action_name in ("else_action", "else_block", "else"):
                # If the condition was false, we skipped the "then" part, so execute the "else" part
                # If the condition was true, we executed the "then" part, so skip the "else" part
                skip_next = not condition_was_false
                i += 1
                continue

            # Handle start_block - if we're skipping, skip the entire block
            if action_name in ("start_block", "start"):
                if skip_next:
                    # Skip until matching end_block
                    block_depth = 1
                    i += 1
                    while i < len(actions) and block_depth > 0:
                        next_action = actions[i].get("action", "")
                        if next_action in ("start_block", "start"):
                            block_depth += 1
                        elif next_action in ("end_block", "end"):
                            block_depth -= 1
                        i += 1
                    skip_next = False
                    condition_was_false = True  # Block was skipped
                    continue
                i += 1
                continue

            # Handle end_block - reset conditional state
            if action_name in ("end_block", "end"):
                skip_next = False
                condition_was_false = False
                i += 1
                continue

            # Skip this action if skip_next is set (for single actions)
            if skip_next:
                skip_next = False
                # A skipped QUESTION takes its own guarded unit down with it
                # (recursively — question chains skip as one unit, GM-style).
                if action_name in self._QUESTION_ACTIONS:
                    skip_next = True
                i += 1
                continue

            # Handle repeat action specially
            if action_name == "repeat":
                i = self._handle_repeat_action(instance, actions, i, action_data)
                continue

            # Execute the action
            result = self.execute_action(instance, action_data)

            # Check if this was a conditional action that returned False
            # Conditional actions return True/False, regular actions return None
            if result is False:
                skip_next = True
                condition_was_false = True
            elif result is True:
                condition_was_false = False

            i += 1




    # Action name aliases for compatibility between different naming conventions
    ACTION_ALIASES = {
        "display_message": "show_message",
        "message": "show_message",
        "goto_next_room": "next_room",
        "goto_previous_room": "previous_room",
        # Room action aliases (GameMaker naming convention)
        "room_restart": "restart_room",
        "room_goto_next": "next_room",
        "room_goto_previous": "previous_room",
        "room_goto": "goto_room",
        # Legacy/GMK import action names
        # NOTE: "if_collision" is NOT aliased - it has its own handler (execute_if_collision_action)
        # that evaluates immediately and supports nested then_actions/else_actions.
        # "if_collision_at" is the deferred version that stores checks for later processing.
        "game_end": "end_game",
        "game_restart": "restart_game",
        "else_block": "else_action",
        "change_sprite": "set_sprite",
        # Folded into the real (now-registered) actions they duplicated --
        # docs/DEFERRED_GAPS_2026_PLAN.md Tier 2.4. splash_show_text/
        # splash_show_image are NOT aliased here: they get their own real
        # implementations (Tier 2.5), not a fold into an existing action.
        "splash_show_video": "show_video",
        "splash_show_webpage": "open_webpage",
    }

    # Legacy add_score/add_lives/add_health were consolidated into the set_*
    # actions plus a Relative flag. Pre-consolidation project JSON is rewritten
    # to set_*(relative=True) on dispatch so it keeps adding instead of
    # replacing. (Projects loaded through ProjectManager are migrated in-place;
    # this is the safety net for any data that reaches the runtime unmigrated.)
    LEGACY_RELATIVE_ADD = {
        "add_score": "set_score",
        "add_lives": "set_lives",
        "add_health": "set_health",
    }

    def execute_action(self, instance, action_data: Dict[str, Any]):
        """Execute a single action with validation

        Returns:
            - True if action is a conditional that evaluated to True
            - False if action is a conditional that evaluated to False
            - None for non-conditional actions
        """
        action_name = action_data.get("action", "")
        parameters = action_data.get("parameters", {})

        if not action_name:
            logger.debug(f"⚠️ Action missing 'action' field: {action_data}")
            return None

        # Normalise legacy add_* duplicates to set_*(relative=True)
        if action_name in self.LEGACY_RELATIVE_ADD:
            action_name = self.LEGACY_RELATIVE_ADD[action_name]
            parameters = {**parameters, "relative": True}

        # Apply action name aliases
        if action_name in self.ACTION_ALIASES:
            action_name = self.ACTION_ALIASES[action_name]

        if action_name not in self.action_handlers:
            logger.error(f"❌ Unknown action: {action_name}")
            return None

        # Validate instance has required attributes for this action
        if not self._validate_action_requirements(instance, action_name):
            logger.debug(f"⚠️ Instance missing requirements for action '{action_name}'")
            return None

        # Execute the action with error handling
        try:
            result = self.action_handlers[action_name](instance, parameters)

            # Generic support for nested then_actions/else_actions on any conditional action.
            # If a handler returns True/False (conditional) and the parameters contain
            # nested action lists, execute the appropriate branch and return None
            # so the outer flow control is not affected.
            if result is not None and isinstance(result, bool):
                # Blockly serialises Thymio condition blocks' DO-slot children
                # under "sub_actions" (on the action dict or in parameters)
                # rather than then_actions; honor it so those nested children
                # actually run and a false condition does not skip the unrelated
                # next action (M44).
                sub_actions = (action_data.get("sub_actions")
                               or parameters.get("sub_actions") or [])
                then_actions = parameters.get("then_actions", []) or sub_actions
                else_actions = parameters.get("else_actions", [])
                if then_actions or else_actions:
                    actions_to_run = then_actions if result else else_actions
                    # Non-catching workhorse: an exit_event inside the branch
                    # must abort the whole event, not just this nested list, so
                    # it propagates to the single top-level catch (M43).
                    self._execute_action_list_inner(instance, actions_to_run)
                    return None

            return result  # Return result for conditional flow
        except _ExitEvent:
            # Sentinel raised by execute_exit_event_action — must
            # propagate to the top-level action-list dispatcher so the
            # rest of the event aborts. The catch-all below would
            # otherwise swallow it and log it as a generic error.
            raise
        except AttributeError as e:
            logger.debug(f"❌ Attribute error in action {action_name}: {e}")
            logger.debug("   Instance may be missing required attributes")
            return None
        except Exception as e:
            logger.error(f"❌ Error executing action {action_name}: {e}")
            import traceback
            traceback.print_exc()
            return None

    def _validate_action_requirements(self, instance, action_name: str) -> bool:
        """Validate that instance has required attributes for an action

        Returns:
            True if instance meets requirements, False otherwise
        """
        # Define required attributes for each action category
        requirements = {
            # Movement actions need position and speed attributes
            "move_grid": ["x", "y"],
            "set_hspeed": ["hspeed"],
            "set_vspeed": ["vspeed"],
            "stop_movement": ["hspeed", "vspeed"],
            "start_moving_direction": ["hspeed", "vspeed"],

            # Grid actions need position
            "snap_to_grid": ["x", "y"],
            "if_on_grid": ["x", "y"],
            "stop_if_no_keys": ["x", "y", "hspeed", "vspeed"],
            "check_keys_and_move": ["x", "y", "hspeed", "vspeed"],

            # Most actions work with any instance
            "show_message": [],
            "restart_room": [],
            "next_room": [],
            "destroy_instance": [],
            "if_collision_at": ["x", "y"],
        }

        # Get required attributes for this action
        required_attrs = requirements.get(action_name, [])

        # Check if instance has all required attributes
        for attr in required_attrs:
            if not hasattr(instance, attr):
                logger.debug(f"   Missing attribute: {attr}")
                return False

        return True

    # ==================== GRID-BASED MOVEMENT ====================


    # ==================== SPEED-BASED MOVEMENT ====================




    def execute_stop_movement_action(self, instance, parameters: Dict[str, Any]):
        """Stop all movement by setting speeds to zero"""
        instance.hspeed = 0
        instance.vspeed = 0











    def _resolve_target_instances(self, instance, parameters: Dict[str, Any]):
        """Resolve GM-style target/target_object parameters to instances.

        target: "self" (default) | "other" (collision partner) | "object"
        (every live instance of parameters["target_object"]). Mirrors the
        semantics execute_destroy_instance_action / execute_change_instance_action
        already implement inline — GM's "Applies to" selector, which the GMK
        importer now emits (treasure's power-pill / death-reset events).
        """
        target = parameters.get("target", "self")
        if target in ("self", "sel", "", None):
            return [instance]
        if target == "other":
            # The desktop collision pipeline installs the collision context on
            # the EXECUTOR (self._collision_other, set/cleared around each
            # collision event) — reading it off the instance silently resolved
            # to nothing, so treasure's eaten scared monster never teleported
            # home and the explorer died to it next frame. Keep the instance
            # attribute as a fallback for harnesses that set it there.
            other = (getattr(self, '_collision_other', None)
                     or getattr(instance, '_collision_other', None))
            return [other] if other else []
        if target == "object":
            target_object = parameters.get("target_object", "")
            if not target_object or not (self.game_runner and self.game_runner.current_room):
                return []
            return [inst for inst in self.game_runner.current_room.instances
                    if getattr(inst, 'object_name', None) == target_object]
        return [instance]





    # ==================== GRID UTILITIES ====================




    def execute_stop_if_no_keys_action(self, instance, parameters: Dict[str, Any]):
        """Stop movement when on grid (for precise grid-based movement)

        NEW LOGIC (Nov 19, 2025 - Fix overshoot issue):
        - ALWAYS stop movement when this action executes
        - This action is called from step event when player reaches grid
        - Prevents overshoot by forcing stop at every grid position
        - Keyboard events will restart movement on next frame if key still held
        - This creates precise one-grid-cell-at-a-time movement

        Old logic checked if keys were pressed, but this caused overshoot
        because keyboard events fire continuously while key is held.

        Parameters:
            grid_size: Grid cell size (default 32)
        """
        grid_size = int(parameters.get("grid_size", 32))

        # ALWAYS stop movement - don't check keys_pressed
        # This ensures player stops at EVERY grid position
        instance.hspeed = 0
        instance.vspeed = 0

        # Ensure exact grid alignment
        instance.x = round(instance.x / grid_size) * grid_size
        instance.y = round(instance.y / grid_size) * grid_size

        # else: no keys pressed, movement already stopped by stop_if_no_keys

    # ==================== CONTROL ACTIONS ====================






    # ==================== GAME ACTIONS ====================

    def _show_or_queue_message(self, instance, message):
        """Display a message dialog in authored action order.

        Shown **synchronously** (blocking) when a live screen is available, so
        message-style actions (show_message, show_info) appear in the order the
        user placed them — matching show_highscore, which already shows
        immediately. Queuing them into ``pending_messages`` (drained by the
        game loop after the event) made them appear *after* any same-event
        immediate dialog, inverting the order. Falls back to the queue when
        there is no live screen yet (headless runs / tests).
        """
        runner = self.game_runner
        if (runner is not None and getattr(runner, 'screen', None) is not None
                and hasattr(runner, 'show_message_dialog')):
            runner.show_message_dialog(message)
            return

        if not hasattr(instance, 'pending_messages'):
            instance.pending_messages = []
        instance.pending_messages.append(message)

    def localize_param(self, parameters: Dict[str, Any], name: str, default=""):
        """A display parameter's value, in the runner's language.

        Honours the `<param>_translations` convention: a dict of
        {language_code: text} stored alongside the parameter. The IDE has
        offered this for ANY string parameter since action_editor.py's
        translation dialog was added -- but the runtime only ever read
        `message_translations`, so an author could enter translations for a
        draw_text and the engine would silently ignore them. This closes that.

        Falls back to the base (English) value whenever there is no dict, no
        entry for the language, or no runner -- so an untranslated string
        keeps working exactly as before.

        NOTE the export targets do NOT read these dicts (engine.js's
        show_message reads params.message only; Kivy has no support at all).
        Exported games are meant to get their strings resolved at EXPORT time
        instead, so a translated project cannot behave differently once
        exported. Until that lands, translations are a desktop-only feature.
        """
        value = parameters.get(name, default)
        translations = parameters.get("%s_translations" % name)
        if not isinstance(translations, dict) or not self.game_runner:
            return value
        lang = getattr(self.game_runner, "language", "en") or "en"
        if lang != "en" and lang in translations and translations[lang]:
            return translations[lang]
        return value

    def execute_show_message_action(self, instance, parameters: Dict[str, Any]):
        """Execute show message action with optional translation support."""
        message = self.localize_param(parameters, "message", "")

        logger.debug(f"💬 MESSAGE: {message}")
        self._show_or_queue_message(instance, message)

    def execute_delay_action_action(self, instance, parameters: Dict[str, Any]):
        """Execute an action after a delay (in frames)

        Parameters:
            frames: Number of frames to wait before executing the action
            then_action: The action to execute after the delay (e.g., "change_room", "next_room")
            room_name: Room name for change_room action (optional)
            (other parameters are passed to the delayed action)
        """
        frames = parameters.get("frames", 60)
        then_action = parameters.get("then_action", "")

        try:
            frames = int(frames)
        except (ValueError, TypeError):
            frames = 60

        if not then_action:
            logger.warning("⚠️ delay_action: No then_action specified")
            return

        # _delayed_actions is now eagerly initialised in GameInstance.__init__,
        # so no lazy-init guard is needed here.

        # Store the delayed action with remaining frames and parameters
        delayed = {
            'frames_remaining': frames,
            'action': then_action,
            'parameters': parameters.copy()
        }
        instance._delayed_actions.append(delayed)

        logger.debug(f"⏱️ Scheduled {then_action} action in {frames} frames for {instance.object_name}")











    # ==================== VARIABLE ACTIONS ====================

    def _parse_value(self, value_str: str, instance=None):
        """Parse a value string into appropriate type (number, string, or expression result)

        Supports:
        - Numbers: 42, 3.14, -5
        - Booleans: true, false
        - Strings: "hello", 'world'
        - Variable references: hspeed, my_var
        - Scoped references: self.hspeed, other.hspeed, global.my_var
        """
        if not isinstance(value_str, str):
            return value_str

        value_str = value_str.strip()

        # Try to parse as integer
        try:
            return int(value_str)
        except ValueError:
            pass

        # Try to parse as float
        try:
            return float(value_str)
        except ValueError:
            pass

        # Check for boolean
        if value_str.lower() == "true":
            return True
        if value_str.lower() == "false":
            return False

        # Check for scoped variable references (self.var, other.var, global.var)
        if '.' in value_str and not value_str.startswith('"') and not value_str.startswith("'"):
            parts = value_str.split('.', 1)
            if len(parts) == 2:
                scope, var_name = parts
                scope = scope.lower()

                # Get stored collision speeds (if in a collision event)
                collision_speeds = getattr(self, '_collision_speeds', {})

                if scope == 'self' and instance:
                    # For collision events, use stored collision speed if available
                    if var_name == 'hspeed' and 'self_hspeed' in collision_speeds:
                        return collision_speeds['self_hspeed']
                    elif var_name == 'vspeed' and 'self_vspeed' in collision_speeds:
                        return collision_speeds['self_vspeed']
                    elif hasattr(instance, var_name):
                        return getattr(instance, var_name)
                    # Special handling for 'direction' - compute from hspeed/vspeed
                    elif var_name == 'direction':
                        hspeed = collision_speeds.get('self_hspeed', getattr(instance, 'hspeed', 0))
                        vspeed = collision_speeds.get('self_vspeed', getattr(instance, 'vspeed', 0))
                        if hspeed == 0 and vspeed == 0:
                            return 0  # No movement, default to right
                        # GameMaker convention: 0° = right, 90° = up
                        # vspeed is negated because screen y increases downward
                        return math.degrees(math.atan2(-vspeed, hspeed)) % 360
                elif scope == 'other':
                    # For collision events, use stored collision speed if available
                    if var_name == 'hspeed' and 'other_hspeed' in collision_speeds:
                        return collision_speeds['other_hspeed']
                    elif var_name == 'vspeed' and 'other_vspeed' in collision_speeds:
                        return collision_speeds['other_vspeed']
                    else:
                        other = getattr(self, '_collision_other', None)
                        if other:
                            if hasattr(other, var_name):
                                return getattr(other, var_name)
                            # Special handling for 'direction' - compute from hspeed/vspeed
                            elif var_name == 'direction':
                                hspeed = collision_speeds.get('other_hspeed', getattr(other, 'hspeed', 0))
                                vspeed = collision_speeds.get('other_vspeed', getattr(other, 'vspeed', 0))
                                if hspeed == 0 and vspeed == 0:
                                    return 0  # No movement, default to right
                                # GameMaker convention: 0° = right, 90° = up
                                # vspeed is negated because screen y increases downward
                                return math.degrees(math.atan2(-vspeed, hspeed)) % 360
                elif scope == 'global' and self.game_runner and not any(
                    op in value_str for op in ('*', '+', '-', '/', '%')
                ):
                    # Defaults to 0 for a global that was never set, matching
                    # _get_variable_value's own default (used by the
                    # arithmetic-expression path for the exact same dotted
                    # reference when it appears inside an operator
                    # expression) — a bare "global.foo" with no operator
                    # used to fall through to the raw-string return at the
                    # bottom of this function instead, e.g. a draw_text
                    # showing a never-yet-set score global rendered the
                    # literal text "global.score_maze" rather than "0".
                    # Guarded to a truly bare reference (no operator
                    # anywhere in the string): a compound expression like
                    # "global.a + global.b" must fall through to the
                    # has_operator routing below instead, since the naive
                    # split('.', 1) above would otherwise capture
                    # "a + global.b" as var_name and look that up as a
                    # single (nonexistent) key, silently returning 0.
                    return self.game_runner.global_variables.get(var_name, 0)

        # Check for simple variable reference (no dot)
        if instance and not value_str.startswith('"') and not value_str.startswith("'"):
            # Try to get instance variable
            if hasattr(instance, value_str):
                return getattr(instance, value_str)
            # Built-in game-state readouts (score/lives/health) — mirrors the
            # namespace _eval_bool_expression already exposes for conditions;
            # this lets an action's value (e.g. set_variable copying the
            # current score into a global) reference them by bare name too.
            if self.game_runner and value_str in ('score', 'lives', 'health'):
                return getattr(self.game_runner, value_str, 0)
            # Try global variable
            if self.game_runner and value_str in self.game_runner.global_variables:
                return self.game_runner.global_variables[value_str]

        # Route to the expression evaluator for arithmetic (contains an
        # operator) OR a GML function call like random(...)/irandom(...)/
        # choose(...). Function calls carry no arithmetic operator, so without
        # this second trigger they'd fall through to the raw-string return
        # below — e.g. `random(image_number)` would reach int()/float() in the
        # calling action as a literal string and silently fail to parse.
        import re as _re
        has_operator = any(op in value_str for op in ['*', '+', '-', '/', '%'])
        has_function = _re.search(r'\b(?:random|irandom|choose|max|min|abs|round)\s*\(', value_str) is not None
        if (has_operator or has_function) and not value_str.startswith('"'):
            # Evaluate arithmetic / function expression
            return self._evaluate_expression(value_str, instance)

        # Return as string (strip quotes if present)
        if (value_str.startswith('"') and value_str.endswith('"')) or \
           (value_str.startswith("'") and value_str.endswith("'")):
            return value_str[1:-1]

        return value_str

    def _evaluate_expression(self, expr_str: str, instance=None):
        """Evaluate an arithmetic expression with variable substitution

        Supports expressions like:
        - other.hspeed*8
        - self.x + 32
        - other.vspeed * -1
        - hspeed*16 (bare variable names treated as self.)
        """
        import re

        # Replace scoped variable references with their values (self.x, other.hspeed, etc.)
        def replace_scoped_var(match):
            var_ref = match.group(0)
            value = self._get_variable_value(var_ref, instance)
            if value is not None:
                return str(value)
            return var_ref

        # Pattern to match scoped variable references like self.x, other.hspeed, etc.
        scoped_var_pattern = r'(self|other|global)\.\w+'
        expr_substituted = re.sub(scoped_var_pattern, replace_scoped_var, expr_str)

        # Bare tokens that are function names (substituted further below), not
        # instance variables — these legitimately don't resolve to an attribute,
        # so they must be excluded from the "unresolved token" warning.
        _known_functions = {'random', 'irandom', 'choose', 'max', 'min', 'abs', 'round'}

        # Replace bare variable names (hspeed, vspeed, x, y, etc.) with their instance values
        def replace_bare_var(match):
            var_name = match.group(0)
            # Skip if it's a number or already processed
            if var_name.isdigit():
                return var_name
            # Check if instance has this attribute
            if instance and hasattr(instance, var_name):
                # For collision speeds, check stored values first
                collision_speeds = getattr(self, '_collision_speeds', {})
                if var_name == 'hspeed' and 'self_hspeed' in collision_speeds:
                    return str(collision_speeds['self_hspeed'])
                elif var_name == 'vspeed' and 'self_vspeed' in collision_speeds:
                    return str(collision_speeds['self_vspeed'])
                return str(getattr(instance, var_name))
            # Built-in game-state readouts (score/lives/health) — mirrors
            # _parse_value's own bare-token support for these (and
            # _eval_bool_expression's namespace), so an arithmetic
            # expression like a difficulty ramp ("40 - score/50") can
            # reference score directly without first copying it into an
            # instance variable.
            if self.game_runner and var_name in ('score', 'lives', 'health'):
                return str(getattr(self.game_runner, var_name, 0))
            # Token didn't resolve to a number, a function name, or an instance
            # attribute. It will reach eval() unbound and raise NameError, so the
            # whole expression silently defaults to 0 (see the except below).
            # Warn so unsupported/typo'd variables surface instead of vanishing.
            if var_name not in _known_functions:
                logger.warning(
                    f"⚠️ Unresolved variable '{var_name}' in expression '{expr_str}'"
                    " — not a known instance attribute; expression will default to 0"
                )
            return var_name

        # Pattern to match bare variable names (word characters not preceded by a dot)
        # Only match words that aren't already part of a scoped reference
        bare_var_pattern = r'(?<![.\w])\b([a-zA-Z_]\w*)\b(?!\s*\.)'
        expr_substituted = re.sub(bare_var_pattern, replace_bare_var, expr_substituted)

        # Handle GameMaker-style functions before evaluation
        import random as random_module

        # random(n) - returns random float from 0 to n (exclusive)
        def gm_random(n):
            return random_module.random() * n

        # irandom(n) - returns random integer from 0 to n (inclusive)
        def gm_irandom(n):
            return random_module.randint(0, int(n))

        # choose(a, b, c, ...) - returns one of the arguments randomly
        def gm_choose(*args):
            return random_module.choice(args)

        # Replace function calls with Python equivalents
        expr_substituted = re.sub(r'\brandom\s*\(', 'gm_random(', expr_substituted)
        expr_substituted = re.sub(r'\birandom\s*\(', 'gm_irandom(', expr_substituted)
        expr_substituted = re.sub(r'\bchoose\s*\(', 'gm_choose(', expr_substituted)

        # Try to evaluate the expression safely
        try:
            # Allow safe characters plus function calls
            if re.match(r'^[\d\s\+\-\*\/\%\(\)\.\,a-zA-Z_]+$', expr_substituted):
                # Create safe namespace with only allowed functions
                safe_namespace = {
                    'gm_random': gm_random,
                    'gm_irandom': gm_irandom,
                    'gm_choose': gm_choose,
                    'random': random_module,  # Allow Python random module access
                    # Matches _eval_bool_expression's own namespace (and
                    # HTML5's gmExpressionValue) — needed for e.g. a
                    # difficulty ramp clamped with max(15, 40 - score/50).
                    'max': max, 'min': min, 'abs': abs, 'round': round,
                }
                result = eval(expr_substituted, {"__builtins__": {}}, safe_namespace)  # nosec B307 - builtins stripped + regex whitelist (:2006) gates input; literal_eval would break random()/choose()
                return result
            else:
                logger.debug(f"⚠️ Unsafe expression: {expr_substituted}")
                return 0
        except Exception as e:
            logger.error(f"⚠️ Error evaluating expression '{expr_str}': {e}")
            return 0

    def _get_variable_value(self, var_ref: str, instance=None):
        """Get the value of a variable reference like self.x, other.hspeed

        For collision events, uses stored collision speeds (captured at collision time)
        instead of current speeds which may have been modified by other collision handlers.
        """
        if '.' not in var_ref:
            return None

        parts = var_ref.split('.', 1)
        if len(parts) != 2:
            return None

        scope, var_name = parts
        scope = scope.lower()

        if scope == 'self' and instance:
            # For collision events, use stored collision speed if available
            collision_speeds = getattr(self, '_collision_speeds', {})
            if var_name == 'hspeed' and 'self_hspeed' in collision_speeds:
                return collision_speeds['self_hspeed']
            elif var_name == 'vspeed' and 'self_vspeed' in collision_speeds:
                return collision_speeds['self_vspeed']
            elif hasattr(instance, var_name):
                return getattr(instance, var_name)
        elif scope == 'other':
            # For collision events, use stored collision speed if available
            collision_speeds = getattr(self, '_collision_speeds', {})
            if var_name == 'hspeed' and 'other_hspeed' in collision_speeds:
                return collision_speeds['other_hspeed']
            elif var_name == 'vspeed' and 'other_vspeed' in collision_speeds:
                return collision_speeds['other_vspeed']
            else:
                other = getattr(self, '_collision_other', None)
                if other and hasattr(other, var_name):
                    return getattr(other, var_name)
        elif scope == 'global' and self.game_runner:
            if var_name in self.game_runner.global_variables:
                return self.game_runner.global_variables[var_name]

        return 0  # Default to 0 for unknown variables

    def execute_set_variable_action(self, instance, parameters: Dict[str, Any]):
        """Set an instance or global variable

        Parameters:
            variable: Variable name. "variable_name" is also accepted as a legacy alias
                for projects saved before the schema alignment (see events/action_types.py).
            value: Value to set (number, string, or expression)
            scope: "sel"/"self" instance var, "other" collision other, "global" global var
            relative: If True, add to current value instead of replacing
        """
        variable = parameters.get("variable") or parameters.get("variable_name") or ""
        value_str = parameters.get("value", "0")
        scope = parameters.get("scope", "sel")
        relative = parameters.get("relative", False)

        if not variable:
            logger.debug("⚠️  set_variable: No variable name specified")
            return

        # Parse the value
        value = self._parse_value(value_str, instance)

        if scope == "global":
            if not self.game_runner:
                logger.debug("⚠️  set_variable: Cannot access global variables without game_runner")
                return

            if relative:
                current = self.game_runner.global_variables.get(variable, 0)
                try:
                    value = current + value
                except TypeError:
                    logger.debug(f"⚠️  set_variable: Cannot add {type(value)} to {type(current)}")
                    return

            self.game_runner.global_variables[variable] = value
            logger.debug(f"🌐 Global variable '{variable}' = {value}")

        else:
            # Who gets the variable: GM's "Applies to" selector
            # (target/target_object, emitted by the GMK importer — e.g.
            # maze_4's ring bonus sets afraid=true on EVERY monster_all)
            # takes precedence; otherwise the legacy scope param.
            if "target" in parameters:
                targets = self._resolve_target_instances(instance, parameters)
            elif scope == "other":
                other = getattr(self, '_collision_other', None)
                if not other:
                    logger.debug("⚠️  set_variable: 'other' scope only available in collision events")
                    return
                targets = [other]
            else:  # scope == "sel"
                targets = [instance]

            for target_instance in targets:
                new_value = value
                if relative:
                    current = getattr(target_instance, variable, 0)
                    try:
                        new_value = current + value
                    except TypeError:
                        logger.debug(f"⚠️  set_variable: Cannot add {type(value)} to {type(current)}")
                        continue
                setattr(target_instance, variable, new_value)
                logger.debug(f"📝 {target_instance.object_name}.{variable} = {new_value}")


    # ==================== ALARM ACTIONS ====================

    def execute_set_alarm_action(self, instance, parameters: Dict[str, Any]):
        """Set an alarm to trigger after N steps

        Parameters:
            alarm_number (or alarm): Which alarm (0-11)
            steps: Number of steps until alarm triggers (-1 to disable)
            relative: If True, add to current alarm value
        """
        # Accept "alarm_number", "alarm_num", and "alarm" parameter names for flexibility
        alarm_number = parameters.get("alarm_number", parameters.get("alarm_num", parameters.get("alarm", 0)))
        alarm_number = int(alarm_number)
        steps_param = parameters.get("steps", "30")
        relative = parameters.get("relative", False)

        # Validate alarm number
        if alarm_number < 0 or alarm_number > 11:
            logger.warning(f"⚠️ set_alarm: Invalid alarm number {alarm_number} (must be 0-11)")
            return

        # Parse steps (can be a number or variable)
        steps = self._parse_value(str(steps_param), instance)
        if not isinstance(steps, (int, float)):
            logger.warning(f"⚠️ set_alarm: Invalid steps value '{steps_param}', defaulting to 30")
            steps = 30
        steps = int(steps)

        # Honors GM's "Applies to" selector (target/target_object) — e.g.
        # treasure arms alarm 0 on every scared monster so they revert to
        # normal when it fires. Default remains the acting instance.
        for target_instance in self._resolve_target_instances(instance, parameters):
            # Ensure the instance has an alarm array
            if not hasattr(target_instance, 'alarm'):
                target_instance.alarm = [-1] * 12

            value = steps
            if relative:
                current = target_instance.alarm[alarm_number]
                if current < 0:
                    current = 0  # If disabled, treat as 0
                value = current + steps

            target_instance.alarm[alarm_number] = value

            if value < 0:
                logger.debug(f"⏰ Alarm {alarm_number} disabled for {target_instance.object_name}")
            else:
                logger.debug(f"⏰ Alarm {alarm_number} set to {value} steps "
                             f"for {target_instance.object_name}")

    # Maximum blocking sleep, in milliseconds. A blocking sleep freezes
    # rendering and input, so an absurd value (typo / hostile project) would
    # hang the game; the common use case (let a sound finish) is well under this.
    SLEEP_MAX_MS = 10000

    def execute_sleep_action(self, instance, parameters: Dict[str, Any]):
        """Pause the game for a number of milliseconds, then continue.

        This is a *blocking* pause (pygame.time.delay): rendering and input are
        frozen for the duration. Sounds play on independent mixer channels, so
        they keep playing through the sleep — the intended use is letting a sound
        finish before the next action (e.g. a room change) cuts it off.

        Parameters:
            milliseconds (or ms / duration): how long to pause; clamped to
                [0, SLEEP_MAX_MS]. Accepts a number, variable, or expression.
        """
        ms_param = parameters.get(
            "milliseconds", parameters.get("ms", parameters.get("duration", 1000))
        )

        ms = self._parse_value(str(ms_param), instance)
        if not isinstance(ms, (int, float)):
            logger.warning(f"⚠️ sleep: Invalid milliseconds value '{ms_param}', defaulting to 1000")
            ms = 1000
        ms = int(ms)

        if ms <= 0:
            return

        if ms > self.SLEEP_MAX_MS:
            logger.warning(
                f"⚠️ sleep: {ms}ms exceeds the {self.SLEEP_MAX_MS}ms cap; clamping"
            )
            ms = self.SLEEP_MAX_MS

        try:
            import pygame
            pygame.time.delay(ms)
        except Exception as e:
            logger.warning(f"⚠️ sleep: could not delay ({e})")

    # ==================== SCORE/LIVES/HEALTH ACTIONS ====================



    def _resolve_draw_color(self, instance, default):
        """Return the active draw colour for a draw_* action.

        The colour is global state in GameMaker: ``set_draw_color`` stores it
        both on the calling instance and on the game runner. Drawing actions
        therefore prefer the instance's own colour (set earlier in the same
        event) but fall back to the global runner colour (set by any object),
        and finally to ``default`` when nothing has set a colour yet.
        """
        color = getattr(instance, 'draw_color', None)
        if color is None and self.game_runner is not None:
            color = getattr(self.game_runner, 'draw_color', None)
        return color if color is not None else default

    @staticmethod
    def _is_relative(parameters: Dict[str, Any]) -> bool:
        """GM's 'relative' checkbox on draw actions: coordinates are offsets
        from the instance's position (imported GMK controllers draw HUDs this
        way — e.g. maze_4's controller at (0, 480) drawing the score strip at
        y+4 = the bottom of the room)."""
        relative = parameters.get("relative", False)
        if isinstance(relative, str):
            return relative.strip().lower() in ("true", "1", "yes")
        return bool(relative)







    # execute_draw_minimap_action MOVED to extensions/raycast_2_5d/handlers.py
    # (PluginExecutor) in Stage B3. It reads the room's derived wall edges via
    # instance.action_executor and emits ordinary draw-queue commands.

    # execute_draw_doom_hud_action MOVED to extensions/raycast_2_5d/handlers.py
    # (PluginExecutor) in Stage B3. It resolves game state via
    # instance.action_executor and emits ordinary draw-queue commands.


    def execute_set_window_caption_action(self, instance, parameters: Dict[str, Any]):
        """Set game window caption settings (score/lives/health display)"""
        if not self.game_runner:
            return

        # Update caption display settings on game_runner
        self.game_runner.show_score_in_caption = parameters.get("show_score", True)
        self.game_runner.show_lives_in_caption = parameters.get("show_lives", True)
        self.game_runner.show_health_in_caption = parameters.get("show_health", False)
        self.game_runner.window_caption = parameters.get("caption", "")

        logger.debug(f"🪟 Caption settings updated: score={self.game_runner.show_score_in_caption}, "
              f"lives={self.game_runner.show_lives_in_caption}, health={self.game_runner.show_health_in_caption}")



    # ==================== GAME CONTROL ACTIONS ====================

    def execute_end_game_action(self, instance, parameters: Dict[str, Any]):
        """End the game and close the window"""
        if not self.game_runner:
            return

        logger.debug("🚪 Ending game...")
        self.game_runner.running = False

    def execute_restart_game_action(self, instance, parameters: Dict[str, Any]):
        """Restart the game from the first room"""
        if not self.game_runner:
            return

        logger.debug("🔄 Restart game requested...")
        # Set flag for game loop to handle the restart
        # This ensures the room is properly recreated with fresh instances
        instance.restart_game_flag = True

    # ==================== INFO ACTIONS ====================

    def execute_show_info_action(self, instance, parameters: Dict[str, Any]):
        """Display game information screen

        Shows the game info defined in project settings.
        In GameMaker, this displays an RTF document with game information.
        We'll show a simple info dialog with project metadata.
        """
        if not self.game_runner or not self.game_runner.project_data:
            logger.debug("⚠️ show_info: No project data available")
            return

        # Get game info from project data
        project = self.game_runner.project_data
        name = project.get('name', 'Unknown Game')
        version = project.get('version', '1.0.0')
        author = project.get('author', 'Unknown')
        description = project.get('description', '')

        # Build info message
        info_text = f"{name}\nVersion: {version}\nBy: {author}"
        if description:
            info_text += f"\n\n{description}"

        logger.debug(f"ℹ️ GAME INFO:\n{info_text}")
        self._show_or_queue_message(instance, info_text)

    def execute_splash_show_text_action(self, instance, parameters: Dict[str, Any]):
        """Show a blocking text message -- reuses the same modal machinery
        show_message/show_info already use, rather than the old placeholder
        that only logged the text and did nothing (see
        docs/DEFERRED_GAPS_2026_PLAN.md Tier 2.5).

        Parameters:
            text: the message to show
        """
        text = self._parse_value(parameters.get("text", ""), instance)
        if not text:
            logger.debug("⚠️ splash_show_text: No text specified")
            return
        logger.debug(f"💬 SPLASH TEXT: {text}")
        self._show_or_queue_message(instance, str(text))

    def execute_splash_show_image_action(self, instance, parameters: Dict[str, Any]):
        """Show a sprite full-screen, blocking until dismissed -- reuses the
        same sprite registry draw_sprite reads from and
        GameRunner.show_splash_image's blocking-loop shape (mirrors
        show_message_dialog). Replaces the old placeholder that only
        logged the image name (Tier 2.5).

        Parameters:
            image: name of the sprite to show full-screen
        """
        image_name = self._parse_value(parameters.get("image", ""), instance)
        if not image_name:
            logger.debug("⚠️ splash_show_image: No image specified")
            return

        runner = self.game_runner
        if runner is None or not getattr(runner, 'screen', None):
            logger.debug("⚠️ splash_show_image: No live screen (headless) -- no-op")
            return

        sprite = runner.sprites.get(str(image_name))
        if sprite is None:
            logger.warning(f"⚠️ splash_show_image: Sprite '{image_name}' not found")
            return

        surface = sprite.frames[0] if sprite.frames else sprite.surface
        if surface is None:
            logger.warning(f"⚠️ splash_show_image: Sprite '{image_name}' has no surface")
            return

        logger.debug(f"🖼️ SPLASH IMAGE: {image_name}")
        runner.show_splash_image(surface)

    def execute_show_video_action(self, instance, parameters: Dict[str, Any]):
        """Play a video file

        Parameters:
            filename: Path to the video file
            fullscreen: Whether to play in fullscreen mode

        Note: Video playback requires additional libraries (moviepy/opencv).
        This implementation logs the request but actual playback may be limited.
        """
        from pathlib import Path

        filename = self._parse_value(parameters.get("filename", ""), instance)
        fullscreen = self._parse_value(parameters.get("fullscreen", False), instance)

        if not filename:
            logger.debug("⚠️ show_video: No filename specified")
            return

        # Convert to boolean if string
        if isinstance(fullscreen, str):
            fullscreen = fullscreen.lower() in ('true', '1', 'yes')

        # Resolve the file path
        file_path = Path(filename)
        if not file_path.is_absolute() and self.game_runner and self.game_runner.project_path:
            file_path = self.game_runner.project_path / filename

        if not file_path.exists():
            logger.warning(f"⚠️ show_video: Video file not found: {file_path}")
            return

        logger.debug(f"🎬 Video playback requested: {file_path} (fullscreen={fullscreen})")

        # Try to play video using available methods
        try:
            # Attempt to use system default video player
            import sys
            import subprocess

            if sys.platform == 'win32':
                import os
                os.startfile(str(file_path))
            elif sys.platform == 'darwin':
                subprocess.call(['open', str(file_path)])
            else:
                subprocess.call(['xdg-open', str(file_path)])

            logger.debug(f"🎬 Opened video with system player: {file_path}")
        except Exception as e:
            logger.warning(f"⚠️ Could not play video: {e}")

    def execute_open_webpage_action(self, instance, parameters: Dict[str, Any]):
        """Open a URL in the default web browser

        Parameters:
            url: The web address to open
        """
        import webbrowser

        url = self._parse_value(parameters.get("url", ""), instance)

        if not url:
            logger.debug("⚠️ open_webpage: No URL specified")
            return

        # Ensure URL has a protocol
        if not url.startswith(('http://', 'https://', 'file://')):
            url = 'https://' + url

        logger.debug(f"🌐 Opening web page: {url}")

        try:
            webbrowser.open(url)
        except Exception as e:
            logger.warning(f"⚠️ Could not open web page: {e}")

    def execute_save_game_action(self, instance, parameters: Dict[str, Any]):
        """Save the current game state to a file

        Parameters:
            filename: Name of the save file (default: savegame.sav)

        Saves:
        - Current room name
        - Score, lives, health
        - Global variables
        - Instance positions and states
        """
        import json
        from pathlib import Path

        filename = self._parse_value(parameters.get("filename", "savegame.sav"), instance)

        if not self.game_runner:
            logger.debug("⚠️ save_game: No game_runner reference")
            return

        # Determine save path (in project directory or user's save folder)
        if self.game_runner.project_path:
            save_dir = self.game_runner.project_path / "saves"
            save_dir.mkdir(exist_ok=True)
            save_path = save_dir / filename
        else:
            save_path = Path(filename)

        # Build save data
        save_data = {
            'version': '1.0',
            'current_room': self.game_runner.current_room.name if self.game_runner.current_room else None,
            'score': self.game_runner.score,
            'lives': self.game_runner.lives,
            'health': self.game_runner.health,
            'global_variables': dict(self.game_runner.global_variables),
            'instances': []
        }

        # Save instance data
        if self.game_runner.current_room:
            for inst in self.game_runner.current_room.instances:
                inst_data = {
                    'object_name': inst.object_name,
                    'x': inst.x,
                    'y': inst.y,
                    'hspeed': getattr(inst, 'hspeed', 0),
                    'vspeed': getattr(inst, 'vspeed', 0),
                    'alarm': list(getattr(inst, 'alarm', [-1] * 12)),
                    'visible': getattr(inst, 'visible', True),
                    'image_index': getattr(inst, 'image_index', 0),
                }
                # Save custom instance variables
                custom_vars = {}
                for key, value in vars(inst).items():
                    if not key.startswith('_') and key not in ['object_name', 'x', 'y', 'hspeed', 'vspeed',
                                                                'alarm', 'visible', 'image_index', 'sprite',
                                                                'object_data', 'action_executor', 'to_destroy',
                                                                'keys_pressed', 'pending_messages']:
                        if isinstance(value, (int, float, str, bool, list, dict)):
                            custom_vars[key] = value
                if custom_vars:
                    inst_data['custom_vars'] = custom_vars
                save_data['instances'].append(inst_data)

        try:
            with open(save_path, 'w', encoding='utf-8') as f:
                json.dump(save_data, f, indent=2, ensure_ascii=False)
            logger.debug(f"💾 Game saved to: {save_path}")
        except Exception as e:
            logger.error(f"❌ Error saving game: {e}")

    def execute_load_game_action(self, instance, parameters: Dict[str, Any]):
        """Load game state from a file

        Parameters:
            filename: Name of the save file (default: savegame.sav)

        Restores:
        - Current room
        - Score, lives, health
        - Global variables
        - Instance positions and states
        """
        import json
        from pathlib import Path

        filename = self._parse_value(parameters.get("filename", "savegame.sav"), instance)

        if not self.game_runner:
            logger.debug("⚠️ load_game: No game_runner reference")
            return

        # Determine save path
        if self.game_runner.project_path:
            save_path = self.game_runner.project_path / "saves" / filename
        else:
            save_path = Path(filename)

        try:
            save_exists = save_path.exists()
        except OSError as e:
            logger.warning(f"⚠️ load_game: Cannot access save file {save_path}: {e}")
            return

        if not save_exists:
            logger.warning(f"⚠️ load_game: Save file not found: {save_path}")
            return

        try:
            with open(save_path, 'r', encoding='utf-8') as f:
                save_data = json.load(f)

            # Restore game state
            self.game_runner.score = save_data.get('score', 0)
            self.game_runner.lives = save_data.get('lives', 3)
            self.game_runner.health = save_data.get('health', 100)
            self.game_runner.global_variables = save_data.get('global_variables', {})

            # Change to saved room
            saved_room = save_data.get('current_room')
            if saved_room and saved_room != (self.game_runner.current_room.name if self.game_runner.current_room else None):
                if saved_room in self.game_runner.rooms:
                    # Defer via the same goto_room_target flag every other
                    # room-changing action uses (GameRunner.update() consumes
                    # it, calling change_room synchronously, then restores
                    # _pending_load_instances right after — see there).
                    instance.goto_room_target = saved_room
                    instance._pending_load_instances = save_data.get('instances', [])
                    logger.debug(f"📂 Will load room: {saved_room}")
                else:
                    logger.warning(f"⚠️ load_game: Saved room '{saved_room}' not found")
            else:
                # Restore instances in current room
                self._restore_instances(save_data.get('instances', []))

            logger.debug(f"📂 Game loaded from: {save_path}")

        except json.JSONDecodeError as e:
            logger.error(f"❌ Invalid save file format: {e}")
        except Exception as e:
            logger.error(f"❌ Error loading game: {e}")

    def _restore_instances(self, instances_data: list):
        """Restore instance states from save data"""
        if not self.game_runner or not self.game_runner.current_room:
            return

        # Match each saved instance to a DISTINCT current instance of the same
        # object. Without consuming matched instances, every saved instance of a
        # given object restored onto the first one in the room, so rooms with N
        # same-object instances collapsed to a single restored state.
        consumed = set()
        for inst_data in instances_data:
            for inst in self.game_runner.current_room.instances:
                if id(inst) in consumed:
                    continue
                if inst.object_name == inst_data.get('object_name'):
                    consumed.add(id(inst))
                    # Restore position and state
                    inst.x = inst_data.get('x', inst.x)
                    inst.y = inst_data.get('y', inst.y)
                    inst.hspeed = inst_data.get('hspeed', 0)
                    inst.vspeed = inst_data.get('vspeed', 0)
                    inst.visible = inst_data.get('visible', True)
                    inst.image_index = inst_data.get('image_index', 0)

                    # Restore alarms
                    alarms = inst_data.get('alarm', [-1] * 12)
                    for i, alarm_val in enumerate(alarms[:12]):
                        inst.alarm[i] = alarm_val

                    # Restore custom variables
                    custom_vars = inst_data.get('custom_vars', {})
                    for key, value in custom_vars.items():
                        setattr(inst, key, value)

                    break  # Found and restored this instance

    # ==================== CODE EXECUTION ACTIONS ====================

    def execute_execute_code_action(self, instance, parameters: Dict[str, Any]):
        """Execute custom Python code

        Provides access to:
        - self: the current instance
        - game: the game runner object
        - All Python built-ins
        """
        code = parameters.get('code', '')

        if not code or not code.strip():
            return

        # If the code is a bare identifier that matches a project script,
        # delegate to execute_script (imported GMK files use execute_code
        # for script calls since GML allows calling scripts without parens)
        stripped = code.strip()
        if stripped.isidentifier() and self.game_runner and self.game_runner.project_data:
            scripts = self.game_runner.project_data.get('assets', {}).get('scripts', {})
            if stripped in scripts:
                return self.execute_execute_script_action(instance, {'script': stripped})

        # Create execution environment
        exec_globals = {
            '__builtins__': __builtins__,
            'sel': instance,
            'self': instance,  # the code editor generates self.<attr> references
            'game': self.game_runner,
            'instance': instance,  # Alternative name
            # In a collision event, custom code may reference `other` (the eval
            # expression path already binds it); None outside collisions (M45).
            'other': getattr(self, '_collision_other', None),
            # `keyboard.check("space")` is emitted by the if_condition
            # key_pressed code generator (audit M20).
            'keyboard': _ExecKeyboard(instance),
            # Add common modules for convenience
            'math': __import__('math'),
            'random': __import__('random'),
        }

        exec_locals = {}

        try:
            # Execute the code
            exec(code, exec_globals, exec_locals)  # nosec B102 - execute_code power-user feature; runs author-authored project code, no untrusted channel

            # Apply any changes to instance variables from locals
            for key, value in exec_locals.items():
                if not key.startswith('__'):
                    setattr(instance, key, value)

        except Exception as e:
            logger.error(f"⚠️  Error executing custom code: {e}")
            import traceback
            traceback.print_exc()

    def execute_execute_script_action(self, instance, parameters: Dict[str, Any]):
        """Execute a script from the project's scripts assets

        Parameters:
            script: Name of the script to execute
            arg0-arg4: Optional arguments to pass to the script

        The script code has access to:
        - self/sel/instance: the current instance
        - game: the game runner object
        - argument0-argument4: the passed arguments
        - All Python built-ins
        """
        script_name = parameters.get('script', '')

        if not script_name:
            logger.debug("⚠️ execute_script: No script specified")
            return

        if not self.game_runner or not self.game_runner.project_data:
            logger.debug("⚠️ execute_script: No game_runner or project data")
            return

        # Get the script from project data
        scripts_data = self.game_runner.project_data.get('assets', {}).get('scripts', {})
        script_data = scripts_data.get(script_name)

        if not script_data:
            logger.warning(f"⚠️ execute_script: Script '{script_name}' not found")
            return

        code = script_data.get('code', '')

        if not code or not code.strip():
            logger.debug(f"⚠️ execute_script: Script '{script_name}' has no code")
            return

        # Parse arguments (up to 5: arg0-arg4)
        arguments = []
        for i in range(5):
            arg_key = f'arg{i}'
            arg_value = parameters.get(arg_key, '')
            if arg_value != '':
                # Parse the argument value (could be a number, string, or variable reference)
                parsed_value = self._parse_value(str(arg_value), instance)
                arguments.append(parsed_value)
            else:
                arguments.append(None)

        # Create execution environment
        exec_globals = {
            '__builtins__': __builtins__,
            'sel': instance,
            'self': instance,  # the code editor generates self.<attr> references
            'game': self.game_runner,
            'instance': instance,
            'other': getattr(self, '_collision_other', None),  # M45
            'keyboard': _ExecKeyboard(instance),  # audit M20
            # Add common modules for convenience
            'math': __import__('math'),
            'random': __import__('random'),
            # GameMaker-style argument variables
            'argument0': arguments[0],
            'argument1': arguments[1],
            'argument2': arguments[2],
            'argument3': arguments[3],
            'argument4': arguments[4],
            'argument_count': sum(1 for a in arguments if a is not None),
        }

        exec_locals = {}

        try:
            logger.debug(f"📜 Executing script: {script_name}")
            # Execute the script code
            exec(code, exec_globals, exec_locals)  # nosec B102 - execute_script power-user feature; runs author-authored project scripts, no untrusted channel

            # Apply any changes to instance variables from locals
            for key, value in exec_locals.items():
                if not key.startswith('__'):
                    setattr(instance, key, value)

        except Exception as e:
            logger.error(f"⚠️ Error executing script '{script_name}': {e}")
            import traceback
            traceback.print_exc()

    # ==================== INSTANCE ACTIONS ====================





    # ==================== DRAWING ACTIONS ====================

    def execute_set_draw_color_action(self, instance, parameters: Dict[str, Any]):
        """Set the drawing color for subsequent draw operations

        Parameters:
            color: Color in hex format (e.g., "#FF0000" for red)
        """
        color = parameters.get("color", "#000000")

        rgb_color = _hex_to_rgb(color)

        # Store drawing color on instance for draw events
        instance.draw_color = rgb_color

        # Also store on game runner for global access
        if self.game_runner:
            self.game_runner.draw_color = rgb_color

        logger.debug(f"🎨 Set drawing color to {color} ({rgb_color}) for {instance.object_name}")









    # ==================== AUDIO ACTIONS ====================

    def execute_stop_sound_action(self, instance, parameters: Dict[str, Any]):
        """Stop playing a specific sound

        Parameters:
            sound: The sound name to stop
        """
        sound_name = parameters.get("sound", "")

        if not sound_name:
            logger.debug("⚠️ stop_sound: No sound specified")
            return

        if not self.game_runner:
            logger.debug("⚠️ stop_sound: No game_runner reference")
            return

        # Get the sound from the asset manager
        if hasattr(self.game_runner, 'sounds') and sound_name in self.game_runner.sounds:
            sound = self.game_runner.sounds[sound_name]
            if hasattr(sound, 'stop'):
                sound.stop()
                logger.debug(f"🔇 Stopped sound: {sound_name}")
            else:
                # Try pygame.mixer.stop for all sounds
                import pygame
                pygame.mixer.stop()
                logger.debug(f"🔇 Stopped all sounds (trying to stop: {sound_name})")
        else:
            logger.debug(f"⚠️ stop_sound: Sound '{sound_name}' not found")

    # ==================== RESOURCE REPLACEMENT ACTIONS ====================

    def execute_replace_sprite_action(self, instance, parameters: Dict[str, Any]):
        """Replace a sprite by loading a new image from file

        Parameters:
            sprite: Name of the sprite to replace
            filename: Path to the image file
            frames: Number of animation frames (default: 1)
            remove_background: Remove background color to make transparent (default: False)
            smooth_edges: Apply anti-aliasing to edges (default: False)
        """
        sprite_name = self._parse_value(parameters.get("sprite", ""), instance)
        filename = self._parse_value(parameters.get("filename", ""), instance)
        frames = self._parse_value(parameters.get("frames", 1), instance)
        remove_background = self._parse_value(parameters.get("remove_background", False), instance)
        smooth_edges = self._parse_value(parameters.get("smooth_edges", False), instance)

        if not sprite_name:
            logger.debug("⚠️ replace_sprite: No sprite specified")
            return

        if not filename:
            logger.debug("⚠️ replace_sprite: No filename specified")
            return

        if not self.game_runner:
            logger.debug("⚠️ replace_sprite: No game_runner reference")
            return

        # Import after validation to allow tests without pygame
        import pygame
        from pathlib import Path

        # Convert to boolean if string
        if isinstance(remove_background, str):
            remove_background = remove_background.lower() in ('true', '1', 'yes')
        if isinstance(smooth_edges, str):
            smooth_edges = smooth_edges.lower() in ('true', '1', 'yes')

        try:
            frames = int(frames)
        except (ValueError, TypeError):
            frames = 1

        # Resolve the file path (relative to project or absolute)
        file_path = Path(filename)
        if not file_path.is_absolute() and self.game_runner.project_path:
            file_path = self.game_runner.project_path / filename

        if not file_path.exists():
            logger.warning(f"⚠️ replace_sprite: File not found: {file_path}")
            return

        try:
            # Load the image
            surface = pygame.image.load(str(file_path)).convert_alpha()

            # Apply remove_background if requested (make top-left pixel color transparent)
            if remove_background:
                bg_color = surface.get_at((0, 0))[:3]
                surface.set_colorkey(bg_color)

            # Create a simple sprite object or update existing
            # For simplicity, we store the surface directly
            # GameSprite expects frames list for animation
            if frames > 1:
                # Split horizontal strip into frames
                frame_width = surface.get_width() // frames
                frame_height = surface.get_height()
                frame_list = []
                for i in range(frames):
                    frame_surface = surface.subsurface((i * frame_width, 0, frame_width, frame_height)).copy()
                    frame_list.append(frame_surface)

                # Create a sprite-like object
                class ReplacedSprite:
                    pass
                new_sprite = ReplacedSprite()
                new_sprite.surface = surface
                new_sprite.frames = frame_list
                new_sprite.frame_count = frames
                new_sprite.width = frame_width
                new_sprite.height = frame_height
                new_sprite.speed = 10.0
            else:
                # Single frame sprite
                class ReplacedSprite:
                    pass
                new_sprite = ReplacedSprite()
                new_sprite.surface = surface
                new_sprite.frames = [surface]
                new_sprite.frame_count = 1
                new_sprite.width = surface.get_width()
                new_sprite.height = surface.get_height()
                new_sprite.speed = 10.0

            self.game_runner.sprites[sprite_name] = new_sprite
            logger.debug(f"🖼️ Replaced sprite '{sprite_name}' from {filename} ({frames} frames)")

        except Exception as e:
            logger.error(f"❌ Error replacing sprite '{sprite_name}': {e}")

    def execute_replace_sound_action(self, instance, parameters: Dict[str, Any]):
        """Replace a sound by loading a new audio file

        Parameters:
            sound: Name of the sound to replace
            filename: Path to the audio file
            kind: Type of sound (normal, background, 3d, mmplayer)
        """
        sound_name = self._parse_value(parameters.get("sound", ""), instance)
        filename = self._parse_value(parameters.get("filename", ""), instance)
        kind = self._parse_value(parameters.get("kind", "normal"), instance)

        if not sound_name:
            logger.debug("⚠️ replace_sound: No sound specified")
            return

        if not filename:
            logger.debug("⚠️ replace_sound: No filename specified")
            return

        if not self.game_runner:
            logger.debug("⚠️ replace_sound: No game_runner reference")
            return

        # Import after validation to allow tests without pygame
        import pygame
        from pathlib import Path

        # Resolve the file path (relative to project or absolute)
        file_path = Path(filename)
        if not file_path.is_absolute() and self.game_runner.project_path:
            file_path = self.game_runner.project_path / filename

        if not file_path.exists():
            logger.warning(f"⚠️ replace_sound: File not found: {file_path}")
            return

        try:
            if kind == 'music' or kind == 'background':
                # Music is streamed, store the path
                self.game_runner.music_files[sound_name] = str(file_path)
                logger.debug(f"🎵 Replaced music '{sound_name}' from {filename}")
            else:
                # Sound effects are loaded into memory
                sound = pygame.mixer.Sound(str(file_path))
                self.game_runner.sounds[sound_name] = sound
                logger.debug(f"🔊 Replaced sound '{sound_name}' from {filename}")

        except Exception as e:
            logger.error(f"❌ Error replacing sound '{sound_name}': {e}")

    def execute_replace_background_action(self, instance, parameters: Dict[str, Any]):
        """Replace a background by loading a new image from file

        Parameters:
            background: Name of the background to replace
            filename: Path to the image file
            remove_background: Remove background color to make transparent (default: False)
            smooth_edges: Apply anti-aliasing to edges (default: False)
        """
        bg_name = self._parse_value(parameters.get("background", ""), instance)
        filename = self._parse_value(parameters.get("filename", ""), instance)
        remove_background = self._parse_value(parameters.get("remove_background", False), instance)
        smooth_edges = self._parse_value(parameters.get("smooth_edges", False), instance)

        if not bg_name:
            logger.debug("⚠️ replace_background: No background specified")
            return

        if not filename:
            logger.debug("⚠️ replace_background: No filename specified")
            return

        if not self.game_runner:
            logger.debug("⚠️ replace_background: No game_runner reference")
            return

        # Import after validation to allow tests without pygame
        import pygame
        from pathlib import Path

        # Convert to boolean if string
        if isinstance(remove_background, str):
            remove_background = remove_background.lower() in ('true', '1', 'yes')
        if isinstance(smooth_edges, str):
            smooth_edges = smooth_edges.lower() in ('true', '1', 'yes')

        # Resolve the file path (relative to project or absolute)
        file_path = Path(filename)
        if not file_path.is_absolute() and self.game_runner.project_path:
            file_path = self.game_runner.project_path / filename

        if not file_path.exists():
            logger.warning(f"⚠️ replace_background: File not found: {file_path}")
            return

        try:
            # Load the image
            surface = pygame.image.load(str(file_path)).convert_alpha()

            # Apply remove_background if requested (make top-left pixel color transparent)
            if remove_background:
                bg_color = surface.get_at((0, 0))[:3]
                surface.set_colorkey(bg_color)

            self.game_runner.backgrounds[bg_name] = surface
            logger.debug(f"🖼️ Replaced background '{bg_name}' from {filename} ({surface.get_width()}x{surface.get_height()})")

        except Exception as e:
            logger.error(f"❌ Error replacing background '{bg_name}': {e}")

    # ==================== ROOM CONFIGURATION ACTIONS ====================



    def execute_set_background_color_action(self, instance, parameters: Dict[str, Any]):
        """Set room background color

        Parameters:
            color: Background color (hex string like "#87CEEB")
            show_color: Whether to display the color (default: True)
        """
        if not self.game_runner or not self.game_runner.current_room:
            logger.debug("⚠️ set_background_color: No current room")
            return

        # Parse parameters
        color_str = parameters.get("color", "#000000")
        show_color = parameters.get("show_color", True)

        # Convert to boolean if string
        if isinstance(show_color, str):
            show_color = show_color.lower() in ('true', '1', 'yes')

        # Parse color
        color_rgb = self._parse_color(color_str)

        # Update room background color
        self.game_runner.current_room.background_color = color_rgb
        self.game_runner.current_room.show_background_color = show_color

        logger.debug(f"🎨 Set background color: {color_str} → {color_rgb}, show={show_color}")

    def execute_set_background_action(self, instance, parameters: Dict[str, Any]):
        """Set room background image with tiling and scrolling options

        Parameters:
            background: Background/sprite name to use
            visible: Show background (default: True)
            foreground: Draw in front of objects (default: False)
            tiled_h: Tile horizontally (default: False)
            tiled_v: Tile vertically (default: False)
            hspeed: Horizontal scroll speed (default: 0)
            vspeed: Vertical scroll speed (default: 0)
        """
        if not self.game_runner or not self.game_runner.current_room:
            logger.debug("⚠️ set_background: No current room")
            return

        # Parse parameters
        background_name = str(self._parse_value(parameters.get("background", ""), instance))
        visible = self._parse_value(parameters.get("visible", True), instance)
        foreground = self._parse_value(parameters.get("foreground", False), instance)
        tiled_h = self._parse_value(parameters.get("tiled_h", False), instance)
        tiled_v = self._parse_value(parameters.get("tiled_v", False), instance)
        hspeed = self._parse_value(parameters.get("hspeed", 0), instance)
        vspeed = self._parse_value(parameters.get("vspeed", 0), instance)

        # Convert booleans
        if isinstance(visible, str):
            visible = visible.lower() in ('true', '1', 'yes')
        if isinstance(foreground, str):
            foreground = foreground.lower() in ('true', '1', 'yes')
        if isinstance(tiled_h, str):
            tiled_h = tiled_h.lower() in ('true', '1', 'yes')
        if isinstance(tiled_v, str):
            tiled_v = tiled_v.lower() in ('true', '1', 'yes')
        try:
            hspeed = float(hspeed)
        except (TypeError, ValueError):
            hspeed = 0.0
        try:
            vspeed = float(vspeed)
        except (TypeError, ValueError):
            vspeed = 0.0

        # Look up the background/sprite
        import pygame

        background_surface = None

        # Try to load from sprites or backgrounds
        if hasattr(self.game_runner, 'sprites') and background_name in self.game_runner.sprites:
            sprite = self.game_runner.sprites[background_name]
            if sprite.surface:
                background_surface = sprite.surface
        elif hasattr(self.game_runner, 'project_data'):
            # Try to load from backgrounds in project data
            backgrounds = self.game_runner.project_data.get('assets', {}).get('backgrounds', {})
            if background_name in backgrounds:
                bg_data = backgrounds[background_name]
                file_path = bg_data.get('file_path', '')
                if file_path:
                    full_path = self.game_runner.project_path / file_path
                    if full_path.exists():
                        try:
                            background_surface = pygame.image.load(str(full_path)).convert()
                        except Exception as e:
                            logger.error(f"⚠️ Error loading background '{background_name}': {e}")

        if background_surface and visible:
            # Update room background
            self.game_runner.current_room.background_surface = background_surface
            self.game_runner.current_room.background_image_name = background_name
            self.game_runner.current_room.tile_horizontal = tiled_h
            self.game_runner.current_room.tile_vertical = tiled_v
            self.game_runner.current_room.bg_hspeed = hspeed
            self.game_runner.current_room.bg_vspeed = vspeed
            self.game_runner.current_room.background_foreground = foreground

            logger.debug(f"🖼️ Set background: '{background_name}', visible={visible}, "
                  f"tiled_h={tiled_h}, tiled_v={tiled_v}, foreground={foreground}, "
                  f"hspeed={hspeed}, vspeed={vspeed}")
        elif not visible:
            # Clear background
            self.game_runner.current_room.background_surface = None
            logger.debug("🖼️ Background hidden")
        else:
            logger.debug(f"⚠️ set_background: Background '{background_name}' not found")


    def execute_enable_views_action(self, instance, parameters: Dict[str, Any]):
        """Enable or disable the view system for the current room

        Parameters:
            enable: True to enable views, False to disable (default: True)

        When views are enabled:
        - The game can display portions of the room
        - Multiple viewports can be shown simultaneously
        - Views can follow objects (like the player)
        """
        if not self.game_runner or not self.game_runner.current_room:
            logger.debug("⚠️ enable_views: No current room")
            return

        # Parse parameter
        enable = self._parse_value(parameters.get("enable", True), instance)

        # Convert to boolean if string
        if isinstance(enable, str):
            enable = enable.lower() in ('true', '1', 'yes')

        # Set views enabled state
        self.game_runner.current_room.views_enabled = bool(enable)

        logger.debug(f"👁️ Views enabled: {enable}")

    def execute_set_view_action(self, instance, parameters: Dict[str, Any]):
        """Configure a view in the current room

        Parameters:
            view: View index 0-7 (default: 0)
            visible: Enable this view (default: True)
            view_x, view_y: Position in room to view
            view_w, view_h: Size of the view area in the room
            port_x, port_y: Position on screen to draw the view
            port_w, port_h: Size of the viewport on screen
            follow: Object name to follow (camera tracking)
            hborder, vborder: Border before view starts scrolling
            hspeed, vspeed: Maximum scroll speed (-1 = instant)
        """
        if not self.game_runner or not self.game_runner.current_room:
            logger.debug("⚠️ set_view: No current room")
            return

        # Parse view index
        view_index = self._parse_value(parameters.get("view", 0), instance)
        try:
            view_index = int(view_index)
        except (ValueError, TypeError):
            view_index = 0

        # Validate view index (0-7)
        if view_index < 0 or view_index > 7:
            logger.warning(f"⚠️ set_view: Invalid view index {view_index}, must be 0-7")
            return

        # Get the view to modify
        view = self.game_runner.current_room.views[view_index]

        # Parse and apply each parameter
        if "visible" in parameters:
            visible = self._parse_value(parameters["visible"], instance)
            if isinstance(visible, str):
                visible = visible.lower() in ('true', '1', 'yes')
            view['visible'] = bool(visible)

        if "view_x" in parameters:
            view['view_x'] = int(self._parse_value(parameters["view_x"], instance))
        if "view_y" in parameters:
            view['view_y'] = int(self._parse_value(parameters["view_y"], instance))
        if "view_w" in parameters:
            view['view_w'] = int(self._parse_value(parameters["view_w"], instance))
        if "view_h" in parameters:
            view['view_h'] = int(self._parse_value(parameters["view_h"], instance))

        if "port_x" in parameters:
            view['port_x'] = int(self._parse_value(parameters["port_x"], instance))
        if "port_y" in parameters:
            view['port_y'] = int(self._parse_value(parameters["port_y"], instance))
        if "port_w" in parameters:
            view['port_w'] = int(self._parse_value(parameters["port_w"], instance))
        if "port_h" in parameters:
            view['port_h'] = int(self._parse_value(parameters["port_h"], instance))

        if "follow" in parameters:
            follow = self._parse_value(parameters["follow"], instance)
            view['follow'] = str(follow) if follow else None

        if "hborder" in parameters:
            view['hborder'] = int(self._parse_value(parameters["hborder"], instance))
        if "vborder" in parameters:
            view['vborder'] = int(self._parse_value(parameters["vborder"], instance))
        if "hspeed" in parameters:
            view['hspeed'] = int(self._parse_value(parameters["hspeed"], instance))
        if "vspeed" in parameters:
            view['vspeed'] = int(self._parse_value(parameters["vspeed"], instance))

        logger.debug(f"🔭 Set view {view_index}: visible={view['visible']}, "
                    f"view=({view['view_x']},{view['view_y']},{view['view_w']}x{view['view_h']}), "
                    f"port=({view['port_x']},{view['port_y']},{view['port_w']}x{view['port_h']}), "
                    f"follow={view['follow']}")

    # execute_set_facing_angle_action / execute_enable_raycast_view_action
    # MOVED to extensions/raycast_2_5d/handlers.py (PluginExecutor) in
    # Stage B3 (docs/RAYCAST_EXTENSION_PLAN.md). They reach game_runner /
    # _parse_value via instance.action_executor, the plugin-handler way.

    def _parse_color(self, color_str: str) -> tuple:
        """Parse color string to RGB tuple (helper method)"""
        if isinstance(color_str, tuple):
            return color_str

        if isinstance(color_str, str) and color_str.startswith('#'):
            try:
                hex_color = color_str.lstrip('#')
                if len(hex_color) == 6:
                    r = int(hex_color[0:2], 16)
                    g = int(hex_color[2:4], 16)
                    b = int(hex_color[4:6], 16)
                    return (r, g, b)
            except (ValueError, IndexError):
                pass

        # Default to black
        return (0, 0, 0)

    # ==================== CONTROL ACTIONS (Additional) ====================







    def _evaluate_if_condition(self, instance, condition_type: str, parameters: Dict[str, Any]) -> bool:
        """Evaluate a condition for if_condition action"""

        if condition_type == "instance_count":
            object_name = parameters.get("object_name", "")
            operator = parameters.get("operator", "==")
            value = parameters.get("value", 0)

            if not object_name or not self.game_runner:
                return False

            # Count instances in current room, excluding those marked for destruction
            instances = self.game_runner.current_room.instances if self.game_runner.current_room else []
            count = sum(1 for inst in instances
                        if getattr(inst, 'object_name', '') == object_name
                        and not getattr(inst, 'to_destroy', False))

            try:
                value = int(value)
            except (ValueError, TypeError):
                value = 0

            logger.debug(f"  🔢 instance_count: {object_name} = {count} (comparing {operator} {value})")
            return self._compare(count, operator, value)

        elif condition_type == "variable_compare":
            variable = parameters.get("variable", "")
            operator = parameters.get("operator", "==")
            value_str = parameters.get("value", "0")

            if not variable:
                return False

            current = getattr(instance, variable, 0)
            compare_value = self._parse_value(str(value_str), instance)

            return self._compare(current, operator, compare_value)

        elif condition_type == "expression":
            # Real Python via the shared evaluator — _parse_value cannot handle
            # comparison/boolean operators (it would return the raw string,
            # which is always truthy, or 0). This is the path the if_condition
            # action uses for a custom "expression" condition.
            return self._eval_bool_expression(
                instance, parameters.get("expression", ""))

        elif condition_type == "random_chance":
            import random
            chance = parameters.get("chance", 50)
            try:
                chance = int(chance)
            except (ValueError, TypeError):
                chance = 50
            return random.randint(1, 100) <= chance

        elif condition_type == "key_pressed":
            key = parameters.get("key", "")
            if not key:
                return False
            # Held keys are tracked per-instance (instance.keys_pressed), not on
            # game_runner — which has no `pressed_keys` attribute at all, so the
            # old getattr default made this condition always false. Stored names
            # are lowercase pygame key names (e.g. "space", "right"). Heal the
            # legacy editor spelling ("Left Arrow" -> "left arrow") so projects
            # saved before M30 still match.
            key = key.lower()
            if key.endswith(" arrow"):
                key = key[: -len(" arrow")]
            return key in getattr(instance, 'keys_pressed', set())

        elif condition_type == "collision_check":
            obj = parameters.get("object", "")
            offset_x = parameters.get("offset_x", 0)
            offset_y = parameters.get("offset_y", 0)

            if not obj or not self.game_runner:
                return False

            check_x = instance.x + offset_x
            check_y = instance.y + offset_y
            return self.game_runner.check_collision_at_position(
                instance, check_x, check_y, obj
            )

        elif condition_type == "position_check":
            check_type = parameters.get("check_type", "x position")
            operator = parameters.get("operator", "==")
            value = parameters.get("value", 0)

            try:
                value = int(value)
            except (ValueError, TypeError):
                value = 0

            if "x" in check_type.lower():
                current = instance.x
            else:
                current = instance.y

            return self._compare(current, operator, value)

        elif condition_type == "mouse_check":
            check = parameters.get("check", "")
            try:
                import pygame
            except ImportError:
                return False
            if not pygame.get_init():
                return False

            buttons = pygame.mouse.get_pressed(num_buttons=3)
            if check == "Left button pressed":
                return bool(buttons[0])
            if check == "Middle button pressed":
                return bool(buttons[1])
            if check == "Right button pressed":
                return bool(buttons[2])
            if check == "Over object":
                # A spriteless instance has no visual footprint, so the mouse
                # can never be "over" it. (Only treat an *explicit* sprite=None
                # as footprint-less; an instance with no sprite attribute at all
                # falls back to the cached-size box.)
                _missing = object()
                if getattr(instance, 'sprite', _missing) is None:
                    return False
                mx, my = pygame.mouse.get_pos()
                width = getattr(instance, '_cached_width', 32)
                height = getattr(instance, '_cached_height', 32)
                return (instance.x <= mx < instance.x + width and
                        instance.y <= my < instance.y + height)
            # "In region" has no region parameters in the editor, so it is not
            # evaluable; fall through to False.
            return False

        return False

    def _compare(self, left, operator: str, right) -> bool:
        """Perform a comparison with the given operator"""
        try:
            left = float(left)
            right = float(right)
        except (ValueError, TypeError):
            pass

        try:
            if operator == "==" or operator == "equal":
                return left == right
            elif operator == "!=" or operator == "not_equal":
                return left != right
            elif operator == "<" or operator == "less":
                return left < right
            elif operator == ">" or operator == "greater":
                return left > right
            elif operator == "<=" or operator == "less_equal":
                return left <= right
            elif operator == ">=" or operator == "greater_equal":
                return left >= right
        except TypeError:
            return False
        return False

    # ==================== ANIMATION ACTIONS ====================

    def execute_set_image_index_action(self, instance, parameters: Dict[str, Any]):
        """Set the current animation frame"""
        frame = parameters.get("frame", 0)
        try:
            frame = int(frame)
        except (ValueError, TypeError):
            frame = 0

        instance.image_index = float(frame)
        logger.debug(f"🎬 Set image_index to {frame} for {instance.object_name}")

    def execute_set_image_speed_action(self, instance, parameters: Dict[str, Any]):
        """Set the animation speed multiplier"""
        speed = parameters.get("speed", 1.0)
        try:
            speed = float(speed)
        except (ValueError, TypeError):
            speed = 1.0

        instance.image_speed = speed
        logger.debug(f"⏩ Set image_speed to {speed} for {instance.object_name}")

    def execute_stop_animation_action(self, instance, parameters: Dict[str, Any]):
        """Stop the sprite animation"""
        instance.image_speed = 0.0
        logger.debug(f"⏸️ Stopped animation for {instance.object_name}")

    def execute_start_animation_action(self, instance, parameters: Dict[str, Any]):
        """Start/resume the sprite animation"""
        instance.image_speed = 1.0
        logger.debug(f"▶️ Started animation for {instance.object_name}")

    def execute_set_sprite_action(self, instance, parameters: Dict[str, Any]):
        """Set the sprite for an instance or modify current sprite animation

        Parameters:
            sprite: Sprite name to use, or "<self>" to keep current sprite
            subimage: Frame index to set (-1 = don't change)
            speed: Animation speed to set (-1 = don't change)

        When sprite is "<self>", only the animation properties (subimage, speed)
        are modified without changing the sprite. This allows stopping/starting
        animation on the current sprite.
        """
        sprite_name = parameters.get("sprite", "<self>")
        subimage = parameters.get("subimage", -1)
        speed = parameters.get("speed", -1)

        # Parse values (can be expressions)
        try:
            subimage = int(self._parse_value(str(subimage), instance))
        except (ValueError, TypeError):
            subimage = -1

        try:
            speed = float(self._parse_value(str(speed), instance))
        except (ValueError, TypeError):
            speed = -1

        # GM's "Applies to" selector (target/target_object, emitted by the GMK
        # importer): maze_4's ring bonus changes EVERY monster_all's sprite to
        # the afraid look. Default remains the acting instance.
        if "target" in parameters:
            targets = self._resolve_target_instances(instance, parameters)
        else:
            targets = [instance]

        for target_instance in targets:
            # Handle sprite change (unless <self>)
            if sprite_name != "<self>" and sprite_name:
                if self.game_runner and sprite_name in self.game_runner.sprites:
                    target_instance.set_sprite(self.game_runner.sprites[sprite_name])
                    logger.debug(f"🖼️ Set sprite to '{sprite_name}' for {target_instance.object_name}")
                else:
                    logger.debug(f"⚠️ set_sprite: Sprite '{sprite_name}' not found")

            # Handle subimage (frame index)
            if subimage >= 0:
                target_instance.image_index = float(subimage)
                logger.debug(f"🎬 Set image_index to {subimage} for {target_instance.object_name}")

            # Handle animation speed (only print when value changes)
            if speed >= 0:
                old_speed = getattr(target_instance, 'image_speed', 1.0)
                if old_speed != speed:
                    target_instance.image_speed = speed
                    if speed == 0:
                        logger.debug(f"⏸️ Stopped animation for {target_instance.object_name}")
                    else:
                        logger.debug(f"⏩ Set image_speed to {speed} for {target_instance.object_name}")
                else:
                    target_instance.image_speed = speed  # Still set it, just don't print

    def execute_collision_event(self, instance, event_name: str, events_data: Dict[str, Any], other_instance, collision_speeds=None):
        """Execute collision event with context about the other instance

        Args:
            instance: The instance whose collision event is being executed
            event_name: Name of the collision event (e.g., "collision_with_wall")
            events_data: Dict of all events for the instance
            other_instance: The other instance involved in the collision
            collision_speeds: Dict with speeds captured at collision time:
                - self_hspeed, self_vspeed: This instance's speeds at collision
                - other_hspeed, other_vspeed: Other instance's speeds at collision
        """
        if event_name not in events_data:
            logger.debug(f"  ⚠️ Event '{event_name}' not found in events_data. Available: {list(events_data.keys())}")
            return

        event_data = events_data[event_name]
        actions = event_data.get("actions", [])

        if not actions:
            logger.debug(f"  ⚠️ No actions defined for event '{event_name}'")
            return

        logger.debug(f"  🎬 Executing {len(actions)} action(s) for {event_name}")

        # Store reference to other instance for collision-specific actions
        self._collision_other = other_instance

        # Store collision speeds so they can be accessed via other.hspeed etc.
        # These are the speeds at the moment of collision, before any events modified them
        self._collision_speeds = collision_speeds or {}

        # Track event execution depth for deferred create event processing
        # This ensures change_instance defers create events until collision event completes
        self._event_depth += 1
        try:
            # Use execute_action_list for proper conditional flow support
            self.execute_collision_action_list(instance, actions, other_instance)
        finally:
            self._event_depth -= 1

            # Clear the collision context BEFORE processing deferred create
            # events. Otherwise a deferred create event runs with the stale
            # collision context still installed, so _parse_value resolves the
            # new instance's self.hspeed/vspeed/direction to the colliding
            # pair's captured speeds (L29). In the finally so an escaping
            # exception can't leave stale context shadowing every later event.
            self._collision_other = None
            self._collision_speeds = {}

            # Process deferred create events when we return to top level
            # This ensures instance counts are accurate after all collision actions complete
            if self._event_depth == 0 and self._deferred_create_events:
                self._process_deferred_create_events()

    def execute_collision_action_list(self, instance, actions: list, other_instance):
        """Execute collision actions with conditional flow support.

        Catches `_ExitEvent` here (raised by execute_exit_event_action) so a
        nested exit_event inside a collision handler unwinds out of the
        whole list — matching the regular execute_action_list path.
        """
        try:
            self._execute_collision_action_list_inner(instance, actions, other_instance)
        except _ExitEvent:
            return

    def _execute_collision_action_list_inner(self, instance, actions: list, other_instance):
        i = 0
        skip_next = False
        condition_was_false = False

        while i < len(actions):
            action_data = actions[i]
            action_name = action_data.get("action", "")

            # Handle else action (supports both else_action and else_block)
            if action_name in ("else_action", "else_block", "else"):
                skip_next = not condition_was_false
                i += 1
                continue

            # Handle start_block - if we're skipping, skip the entire block
            if action_name in ("start_block", "start"):
                if skip_next:
                    # Skip until matching end_block
                    block_depth = 1
                    i += 1
                    while i < len(actions) and block_depth > 0:
                        next_action = actions[i].get("action", "")
                        if next_action in ("start_block", "start"):
                            block_depth += 1
                        elif next_action in ("end_block", "end"):
                            block_depth -= 1
                        i += 1
                    skip_next = False
                    condition_was_false = True  # Block was skipped
                    continue
                i += 1
                continue

            # Handle end_block
            if action_name in ("end_block", "end"):
                skip_next = False
                condition_was_false = False
                i += 1
                continue

            # Skip this action if skip_next is set (for single actions)
            if skip_next:
                skip_next = False
                # A skipped QUESTION takes its own guarded unit down with it
                # (recursively — question chains skip as one unit, GM-style).
                if action_name in self._QUESTION_ACTIONS:
                    skip_next = True
                i += 1
                continue

            # Handle repeat action specially (mirror the normal action loop).
            # Without this, "repeat" was an unknown action in collision events and
            # the following action(s) ran once. The repeated actions run through
            # the standard executor (no `other` context), which matches the
            # normal-loop semantics.
            if action_name == "repeat":
                i = self._handle_repeat_action(instance, actions, i, action_data)
                continue

            # Execute the action
            result = self.handle_collision_action(instance, action_data, other_instance)

            # Check if this was a conditional action that returned False
            if result is False:
                skip_next = True
                condition_was_false = True
            elif result is True:
                condition_was_false = False

            i += 1

    def handle_collision_action(self, instance, action_data: Dict[str, Any], other_instance):
        """Execute a collision action with knowledge of both self and other

        This method has a different signature (3 params) than standard action handlers,
        so it's named differently to avoid auto-registration.

        Returns:
            - True/False for conditional actions
            - None for regular actions
        """
        action_name = action_data.get("action")
        parameters = action_data.get("parameters", {})

        if action_name == "destroy_instance":
            target = parameters.get("target", "self")

            if target in ("self", "sel"):
                instance.to_destroy = True
                return None
            elif target == "other":
                other_instance.to_destroy = True
                return None
            # target == "object" (or an explicit object name) is not a
            # collision-local reference — delegate to the standard handler,
            # which destroys all instances of that object type. Falling through
            # the old self/other-only branch made it a silent no-op.
            return self.execute_action(instance, action_data)
        else:
            # For all other actions, use the regular action executor
            return self.execute_action(instance, action_data)

    # ==================== MAIN1 TAB ACTIONS ====================




    # ==================== MAIN2 TAB ACTIONS ====================

    def execute_transform_sprite_action(self, instance, parameters: Dict[str, Any]):
        """Transform the sprite with scaling and rotation

        Parameters:
            xscale: Horizontal scale factor (1.0 = normal)
            yscale: Vertical scale factor (1.0 = normal)
            angle: Rotation angle in degrees
        """
        xscale_param = parameters.get("xscale", 1.0)
        yscale_param = parameters.get("yscale", 1.0)
        angle_param = parameters.get("angle", 0.0)

        # Parse values
        xscale = self._parse_value(str(xscale_param), instance)
        yscale = self._parse_value(str(yscale_param), instance)
        angle = self._parse_value(str(angle_param), instance)

        try:
            xscale = float(xscale) if xscale is not None else 1.0
            yscale = float(yscale) if yscale is not None else 1.0
            angle = float(angle) if angle is not None else 0.0
        except (ValueError, TypeError):
            xscale, yscale, angle = 1.0, 1.0, 0.0

        # Apply to instance
        instance.image_xscale = xscale
        instance.image_yscale = yscale
        instance.image_angle = angle

        logger.debug(f"🔄 Transform sprite for {instance.object_name}: scale=({xscale}, {yscale}), angle={angle}")

    def execute_set_color_action(self, instance, parameters: Dict[str, Any]):
        """Set the blend color and alpha for the sprite

        Parameters:
            color: Blend color (hex string like "#RRGGBB")
            alpha: Transparency (0.0 = invisible, 1.0 = fully opaque)
        """
        color_param = parameters.get("color", "#FFFFFF")
        alpha_param = parameters.get("alpha", 1.0)

        # Parse values
        color = self._parse_value(str(color_param), instance)
        alpha = self._parse_value(str(alpha_param), instance)

        # Parse color if it's a hex string
        if isinstance(color, str) and color.startswith('#'):
            try:
                # Convert hex to RGB tuple
                hex_color = color.lstrip('#')
                r = int(hex_color[0:2], 16)
                g = int(hex_color[2:4], 16)
                b = int(hex_color[4:6], 16)
                instance.image_blend = (r, g, b)
            except (ValueError, IndexError):
                instance.image_blend = (255, 255, 255)
        else:
            instance.image_blend = (255, 255, 255)

        # Parse alpha
        try:
            alpha = float(alpha) if alpha is not None else 1.0
            alpha = max(0.0, min(1.0, alpha))  # Clamp to 0-1
        except (ValueError, TypeError):
            alpha = 1.0

        instance.image_alpha = alpha

        logger.debug(f"🎨 Set color for {instance.object_name}: blend={instance.image_blend}, alpha={alpha}")

    def execute_set_alpha_action(self, instance, parameters: Dict[str, Any]):
        """Set the transparency (alpha) for the sprite

        Parameters:
            alpha: Transparency (0.0 = invisible, 1.0 = fully opaque)
        """
        alpha_param = parameters.get("alpha", 1.0)

        # Parse value
        alpha = self._parse_value(str(alpha_param), instance)

        # Parse alpha
        try:
            alpha = float(alpha) if alpha is not None else 1.0
            alpha = max(0.0, min(1.0, alpha))  # Clamp to 0-1
        except (ValueError, TypeError):
            alpha = 1.0

        instance.image_alpha = alpha

        logger.debug(f"👻 Set alpha for {instance.object_name}: alpha={alpha}")


    # ==================== DRAW TAB ACTIONS ====================


    def execute_set_draw_font_action(self, instance, parameters: Dict[str, Any]):
        """Set the font and alignment for text drawing

        Parameters:
            font: Font name/asset to use
            halign: Horizontal alignment (left, center, right)
            valign: Vertical alignment (top, middle, bottom)
        """
        font_name = self._parse_value(parameters.get("font", ""), instance)
        # Accept GM's `align` menu (0/1/2) as a fallback for `halign` — projects
        # imported before the converter translated it still carry the raw GM
        # key. New imports emit `halign` directly (see gmk_converter).
        halign_param = parameters.get("halign")
        if halign_param is None and "align" in parameters:
            halign_param = _GM_FONT_ALIGN_FALLBACK.get(
                parameters.get("align"), "left")
        halign = self._parse_value(
            halign_param if halign_param is not None else "left", instance)
        valign = self._parse_value(parameters.get("valign", "top"), instance)

        # Store font settings on the instance
        instance.draw_font = font_name if font_name else None
        instance.draw_halign = halign if halign in ('left', 'center', 'right') else 'left'
        instance.draw_valign = valign if valign in ('top', 'middle', 'bottom') else 'top'

        logger.debug(f"🔤 Set draw font: '{font_name}', halign={halign}, valign={valign}")

    def execute_fill_color_action(self, instance, parameters: Dict[str, Any]):
        """Fill the entire screen with a color

        Parameters:
            color: Fill color (hex string like "#RRGGBB")
        """
        color_param = self._parse_value(parameters.get("color", "#000000"), instance)

        # Parse color if it's a hex string
        if isinstance(color_param, str) and color_param.startswith('#'):
            try:
                hex_color = color_param.lstrip('#')
                r = int(hex_color[0:2], 16)
                g = int(hex_color[2:4], 16)
                b = int(hex_color[4:6], 16)
                color = (r, g, b)
            except (ValueError, IndexError):
                color = (0, 0, 0)
        else:
            color = (0, 0, 0)

        # Queue drawing command for draw event
        if not hasattr(instance, '_draw_queue'):
            instance._draw_queue = []

        instance._draw_queue.append({
            'type': 'fill',
            'color': color
        })

        logger.debug(f"🎨 Queued fill_color: {color}")


    # ==================== EXTRA TAB ACTIONS ====================




    def _resolve_room_sentinel(self, sentinel: str) -> str:
        """Map a navigation sentinel to a concrete room name for check_room.

        Returns the current room for '__current__', the adjacent room for
        '__next__'/'__prev__' (or a value that cannot match at the list ends),
        and the sentinel unchanged if the room list is unavailable.
        """
        if not self.game_runner or not self.game_runner.current_room:
            return sentinel
        if sentinel == "__current__":
            return self.game_runner.current_room.name
        room_list = self.game_runner.get_room_list()
        try:
            idx = room_list.index(self.game_runner.current_room.name)
        except (ValueError, AttributeError):
            return sentinel
        if sentinel == "__next__":
            return room_list[idx + 1] if idx + 1 < len(room_list) else sentinel
        if sentinel == "__prev__":
            return room_list[idx - 1] if idx > 0 else sentinel
        return sentinel


    # ==================== PARTICLES TAB ACTIONS ====================










    # ==================== TIMING TAB ACTIONS (TIMELINE) ====================






