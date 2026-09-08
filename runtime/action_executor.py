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
from runtime.action_appearance import AppearanceMixin
from runtime.action_drawing import DrawingMixin
from runtime.action_misc import MiscMixin, _ExecKeyboard
from runtime.action_dialogs import DialogSystemMixin
from runtime.action_gamestate import GameStateMixin
from runtime.action_particles import ParticleTimelineMixin
from runtime.action_spawn import SpawnMixin
from runtime.action_room import RoomMixin
from runtime.action_score_lives_health import ScoreLivesHealthMixin
from runtime.action_movement import MovementMixin
logger = get_logger(__name__)


# The raycast HUD builders (build_minimap_commands, build_doom_hud_commands,
# doom_face_frame) + MINIMAP_HEADING_LEN / MINIMAP_MARKER_HALF MOVED to
# extensions/raycast_2_5d/hud.py (Stage B3, docs/RAYCAST_EXTENSION_PLAN.md).











class ActionExecutor(DrawingMixin, MovementMixin, ScoreLivesHealthMixin, RoomMixin, SpawnMixin, ParticleTimelineMixin, FlowMixin, AppearanceMixin, GameStateMixin, DialogSystemMixin, MiscMixin):
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

        # There is no Phase 2 any more. runtime/action_handlers/ -- a second,
        # parallel handler source that predated the execute_*_action
        # convention -- was retired on 2026-09-06 (docs/POST_1_0_REFACTOR.md's
        # companion teardown). Its last live entries were folded into the
        # mixins: move_free / set_speed / set_direction into MovementMixin,
        # comment and the play_sound fallback into MiscMixin. Everything else
        # it held was legacy action names with no producer anywhere.
        #
        # Plugins still register at runtime through register_custom_action
        # below, which is a different mechanism and unaffected.

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





        # else: no keys pressed, movement already stopped by stop_if_no_keys

    # ==================== CONTROL ACTIONS ====================






    # ==================== GAME ACTIONS ====================


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



    # ==================== ALARM ACTIONS ====================


    # Maximum blocking sleep, in milliseconds. A blocking sleep freezes
    # rendering and input, so an absurd value (typo / hostile project) would
    # hang the game; the common use case (let a sound finish) is well under this.
    SLEEP_MAX_MS = 10000


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





    # ==================== GAME CONTROL ACTIONS ====================



    # ==================== INFO ACTIONS ====================









    # ==================== CODE EXECUTION ACTIONS ====================



    # ==================== INSTANCE ACTIONS ====================





    # ==================== DRAWING ACTIONS ====================










    # ==================== AUDIO ACTIONS ====================


    # ==================== RESOURCE REPLACEMENT ACTIONS ====================




    # ==================== ROOM CONFIGURATION ACTIONS ====================








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
                # Screen -> room space (L6, docs/FULL_AUDIT_2026-09-07.md) --
                # instance.x/y are room coordinates, so a scrolled view's
                # offset must be undone before comparing.
                if self.game_runner and self.game_runner.current_room:
                    mx, my = self.game_runner.current_room.screen_to_room(mx, my)
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





    # ==================== DRAW TAB ACTIONS ====================





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






