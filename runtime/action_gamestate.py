#!/usr/bin/env python3
"""Saved-game and game-lifecycle actions for
:class:`~runtime.action_executor.ActionExecutor`.

``save_game`` / ``load_game`` (a JSON snapshot of score, lives, health, global
variables and the current room's instances), plus ``restart_game`` and
``end_game``. ``_restore_instances`` is the worker ``load_game`` delegates the
instance half to.

Extracted verbatim from ``runtime/action_executor.py``
(``docs/POST_1_0_REFACTOR.md`` File 4, cluster 9) as a MIXIN -- see
``runtime/action_drawing.py``'s header for why these are sibling modules rather
than the package layout the plan sketched.

``json`` and ``pathlib.Path`` are imported *inside* the save/load methods, as
they were before the move, so this module stays as import-light as the engine.
"""

from typing import Any, Dict

from core.logger import get_logger

logger = get_logger(__name__)


class GameStateMixin:
    """Save / load / restart / end ``execute_*_action`` methods."""

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
