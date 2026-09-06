#!/usr/bin/env python3
"""The remaining actions, each the sole member of its own small concern.

``execute_code`` and ``execute_script`` (the ``exec()``-backed power-user
feature, with the ``_ExecKeyboard`` shim that gives authored code a
``keyboard.check()``), ``set_variable``, ``set_alarm``, ``set_view`` /
``enable_views``, and ``stop_sound``.

Extracted verbatim from ``runtime/action_executor.py``
(``docs/POST_1_0_REFACTOR.md`` File 4, cluster 12 -- the last) as a MIXIN.

**Why one module and not five.** The plan sketched separate ``_vars.py`` and
``_alarms.py``, and views and audio would each want their own by the same
logic. After the eleven clusters before this one, what is left is a single
action apiece: five modules of one method each would be filing, not structure,
and every one of them would still reach the same two base helpers. When one of
these grows a real cluster around it -- a second alarm action, a views family
-- that is the moment to give it its own module, and moving it out then is the
same mechanical exercise this arc has now done twelve times.

``stop_sound`` is the base's shadowed fallback for the plugin-owned audio
action (``plugins/audio_actions.py`` owns the real one); it is here for the
same reason it was in the executor, not because audio belongs to this module.

``pygame`` and ``traceback`` are imported inside the methods, as before.
"""

from typing import Any, Dict

from core.logger import get_logger

logger = get_logger(__name__)


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


class MiscMixin:
    """Scripting, variable, alarm, view and audio-fallback actions."""

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
