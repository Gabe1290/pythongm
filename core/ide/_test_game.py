#!/usr/bin/env python3
"""Test Game / Debug Game (subprocess) plumbing for :class:`PyGameMakerIDE`.

Extracted verbatim from ``core/ide_window.py`` (``docs/POST_1_0_REFACTOR.md``
File 2). A mixin -- ``self`` / ``self.tr()`` / siblings resolve on the
concrete window.

Patch-target moves:
  core.ide_window.logger     -> core.ide._test_game.logger
                                (test_game_subprocess_supervision)
  core.ide_window.QMessageBox -> core.ide._test_game.QMessageBox
                                (test_play_object, test_test_game_editor_sync)
"""

import json
import os
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

from PySide6.QtCore import QTimer
from PySide6.QtWidgets import QMessageBox

from utils.config import Config
from core.logger import get_logger

logger = get_logger(__name__)


class TestGameMixin:

    def test_game(self):
        """Test the current game"""
        # Check if a game subprocess is already running
        if hasattr(self, '_game_process') and self._game_process is not None:
            if self._game_process.poll() is None:  # Still running
                QMessageBox.information(
                    self,
                    self.tr("Game Running"),
                    self.tr("A game is already running. Please close it first.")
                )
                return

        # Check if project is open
        if not self.current_project_path:
            QMessageBox.warning(
                self,
                self.tr("No Project"),
                self.tr("Please open or create a project first before testing a game.")
            )
            return

        # Sync all open editors' data to the project before testing. Use
        # _iter_open_editors so editors floated out of the tab strip (the
        # toolbar 'Floating' mode / per-editor float button) are synced too —
        # the old tab-only loop ran F5 with stale data for detached editors
        # (audit M8).
        for widget in self._iter_open_editors():
            if hasattr(widget, 'get_data') and hasattr(widget, 'asset_name') and widget.asset_name:
                try:
                    data = widget.get_data()
                    self.on_editor_save_requested(widget.asset_name, data)
                except Exception as e:
                    logger.debug(f"Could not sync editor data for {getattr(widget, 'asset_name', '?')}: {e}")

        # Save project before testing
        self.save_project()

        # Validate project and show warnings
        self._show_validation_warnings()

        self._run_project_json(self.current_project_path)

    def _run_project_json(self, project_path: Path):
        """Launch project_path/project.json's game in a subprocess (or
        in-process for packaged builds), with the same stderr-capture +
        QTimer-polling supervision test_game already had.

        Factored out of test_game so test_object can reuse the exact
        same launch/monitor/cleanup path against a temporary
        single-object project instead of duplicating it (TODO.md's
        "Object test runner" item). Only test_game does the "sync open
        editors, save, validate" preflight — a Play Object run doesn't
        need to save or validate the whole project.
        """
        try:
            self.update_status(self.tr("Running game..."))

            project_json = project_path / "project.json"

            if not project_json.exists():
                QMessageBox.warning(
                    self,
                    self.tr("Project Error"),
                    self.tr("project.json not found in project directory")
                )
                # Unreachable for test_object (it always writes project.json
                # right before calling here), but drain unconditionally so a
                # future caller of _run_project_json can't leak a temp dir
                # through this branch.
                self._drain_game_stderr(None)
                return

            # Run game in subprocess to avoid OpenGL conflicts between Qt WebEngine and pygame
            # This isolates pygame's SDL/OpenGL context from Qt's Chromium OpenGL context
            # core/ide/_test_game.py -> parents[2] is the repo root (was
            # ide_window.py's parent.parent before the File-2 move).
            game_script = Path(__file__).resolve().parents[2] / "runtime" / "run_game.py"

            # Check if we're running from a packaged executable (Nuitka/PyInstaller)
            # In that case, sys.executable may point to a non-existent Python path
            # Detection methods:
            # 1. PyInstaller sets sys.frozen
            # 2. Nuitka onefile: sys.executable doesn't exist (points to fictional python)
            # 3. __file__ is in /tmp/ directory (Nuitka extraction)
            # 4. Check if executable name doesn't contain 'python'
            exe_exists = os.path.exists(sys.executable)
            file_dir = os.path.dirname(os.path.abspath(__file__))
            temp_dir = os.environ.get('TEMP', '')
            is_packaged = (
                getattr(sys, 'frozen', False) or  # PyInstaller
                not exe_exists or  # Nuitka: sys.executable doesn't exist
                file_dir.startswith('/tmp/') or  # Nuitka onefile extraction
                (temp_dir and file_dir.startswith(temp_dir))  # Windows temp (avoid empty string match)
            )
            logger.debug(f"🔍 Packaged detection: frozen={getattr(sys, 'frozen', False)}, exe_exists={exe_exists}, file_dir={file_dir}, is_packaged={is_packaged}")

            if is_packaged:
                # When packaged, run game in-process using the game runner
                # This works because pygame is bundled in the package
                if self.game_runner.test_game(str(project_path), Config.get('language', 'en')):
                    self.update_status(self.tr("Game closed"))
                else:
                    self.update_status(self.tr("Game test failed"))
                return

            # Run the game subprocess
            # Pass language code as second argument for runtime translations
            language = Config.get('language', 'en')

            # Use Popen instead of run to avoid blocking the Qt event loop
            # This allows the IDE to remain responsive while the game runs
            env = os.environ.copy()
            # Ensure clean display environment for pygame on Linux
            if sys.platform != 'win32' and sys.platform != 'darwin':
                # Force X11 driver on Linux for better compatibility when launched from Qt
                env['SDL_VIDEODRIVER'] = 'x11'

            # On Windows, suppress the brief python.exe console window that
            # would otherwise flash before pygame's SDL window appears.
            # CREATE_NO_WINDOW is Windows-only; getattr() yields 0 elsewhere,
            # which is a no-op for Popen on POSIX.
            creationflags = getattr(subprocess, 'CREATE_NO_WINDOW', 0)

            # Capture the game's stderr to a temp *file* (not subprocess.PIPE).
            # A PIPE nobody drains can deadlock the child once the OS pipe
            # buffer fills — the exact hazard the old "don't capture output"
            # comment was avoiding. A file has no such buffer limit, so we get
            # the crash traceback without risking a hang. Drained + deleted in
            # _drain_game_stderr when the process exits.
            import tempfile
            stderr_fd, stderr_path = tempfile.mkstemp(prefix='pygm2_game_', suffix='.log')
            self._game_stderr_path = stderr_path
            self._game_stderr_handle = os.fdopen(stderr_fd, 'w')

            try:
                process = subprocess.Popen(
                    [sys.executable, str(game_script), str(project_json), language],
                    cwd=str(project_path),
                    env=env,
                    stdout=None,
                    stderr=self._game_stderr_handle,
                    creationflags=creationflags,
                )
            except Exception:
                # Popen failed (e.g. missing interpreter/runtime): close the
                # stderr handle and delete the temp file so each failed F5
                # doesn't leak an fd + an orphan pygm2_game_*.log (L3).
                self._drain_game_stderr(None)
                raise

            # Store reference to allow stopping the game
            self._game_process = process

            # Use QTimer to check when game exits without blocking
            self._check_game_timer = QTimer(self)
            self._check_game_timer.timeout.connect(self._check_game_process)
            self._check_game_timer.start(100)  # Check every 100ms

            self.update_status(self.tr("Game running... (close game window to return)"))

        except Exception as e:
            QMessageBox.critical(
                self,
                self.tr("Game Test Error"),
                self.tr("Failed to run game:\n\n{0}\n\nCheck console for details.").format(str(e))
            )
            logger.error(f"❌ Game test error: {e}")
            import traceback
            traceback.print_exc()
            self.update_status(self.tr("Game test failed"))

    def test_object(self, object_name: str, object_data: dict):
        """Play Object: run a single object in an isolated, throwaway room.

        Restores the "Play Object" button TODO.md tracked as removed
        orphaned dead code. Builds a minimal temp project (just this
        object + its sprite, if any, + one small test room) and launches
        it through the exact same _run_project_json path Test Game uses —
        the real runtime, not a simulation, so events/collisions-with-self/
        drawing all behave identically to running it for real. Other
        object types the object might reference (e.g. a collision event
        against obj_enemy) simply won't exist in this throwaway project,
        so those specific events won't fire — an accepted limitation of
        testing in isolation, not a bug.

        Does not touch the real project.json or ask to save first — it
        tests the editor's current in-memory state (object_data comes
        from the open ObjectEditor's get_data(), including unsaved edits).
        """
        if hasattr(self, '_game_process') and self._game_process is not None:
            if self._game_process.poll() is None:
                QMessageBox.information(
                    self, self.tr("Game Running"),
                    self.tr("A game is already running. Please close it first."))
                return

        if not self.current_project_path:
            QMessageBox.warning(
                self, self.tr("No Project"),
                self.tr("Please open or create a project first before testing an object."))
            return

        import copy
        import json as _json
        import shutil
        import tempfile

        temp_dir = Path(tempfile.mkdtemp(prefix="pygm2_test_object_"))
        try:
            object_data = copy.deepcopy(object_data) if isinstance(object_data, dict) else {}
            object_data['name'] = object_name
            object_data.setdefault('asset_type', 'object')

            # Carry the object's sprite along (JSON + the actual image file)
            # so it actually renders, not just its collision box.
            sprites = {}
            sprite_name = object_data.get('sprite', '')
            current_sprites = (self.current_project_data or {}).get('assets', {}).get('sprites', {})
            if sprite_name and sprite_name in current_sprites:
                sprite_data = copy.deepcopy(current_sprites[sprite_name])
                file_path = sprite_data.get('file_path', '')
                if file_path:
                    src = self.asset_manager.get_absolute_path(file_path)
                    if src and src.exists():
                        dst_rel = Path('sprites') / Path(file_path).name
                        dst = temp_dir / dst_rel
                        dst.parent.mkdir(parents=True, exist_ok=True)
                        shutil.copy2(src, dst)
                        sprite_data['file_path'] = dst_rel.as_posix()
                sprites[sprite_name] = sprite_data

            settings = (self.current_project_data or {}).get('settings', {})
            width = int(settings.get('window_width', 800) or 800)
            height = int(settings.get('window_height', 600) or 600)
            room_speed = int(settings.get('room_speed', 30) or 30)

            room_name = 'room_test_object'
            project = {
                'name': 'TestObject',
                'settings': {
                    'window_title': self.tr('Play Object: {0}').format(object_name),
                    'window_width': width,
                    'window_height': height,
                    'room_speed': room_speed,
                    'fullscreen': False,
                    'startup_room': room_name,
                },
                'assets': {
                    'sprites': sprites,
                    'sounds': {},
                    'backgrounds': {},
                    'objects': {object_name: object_data},
                    'rooms': {
                        room_name: {
                            'name': room_name, 'asset_type': 'room',
                            'width': width, 'height': height,
                            'background_color': '#808080',
                            'instances': [{
                                'object_name': object_name,
                                'x': width // 2, 'y': height // 2,
                                'rotation': 0, 'scale_x': 1.0, 'scale_y': 1.0,
                                'visible': True,
                            }],
                            'tiles': [],
                        },
                    },
                    'playgrounds': {}, 'scripts': {}, 'fonts': {}, 'data': {},
                },
                'room_order': [room_name],
            }

            (temp_dir / 'project.json').write_text(
                _json.dumps(project, indent=2), encoding='utf-8')

        except Exception as e:
            shutil.rmtree(temp_dir, ignore_errors=True)
            QMessageBox.critical(
                self, self.tr("Error"),
                self.tr("Failed to prepare object test: {0}").format(e))
            return

        self._game_temp_project_dir = temp_dir
        self._run_project_json(temp_dir)

    def _check_game_process(self):
        """Check if the game subprocess has finished (called by QTimer)"""
        if not hasattr(self, '_game_process') or self._game_process is None:
            if hasattr(self, '_check_game_timer') and self._check_game_timer:
                self._check_game_timer.stop()
            return

        # Check if process has terminated
        return_code = self._game_process.poll()
        if return_code is not None:
            # Process has finished
            self._check_game_timer.stop()
            self._game_process = None

            if return_code != 0:
                logger.debug(f"Game exited with code: {return_code}")

            self._drain_game_stderr(return_code)
            self.update_status(self.tr("Game closed"))

    def _drain_game_stderr(self, return_code):
        """Read, surface, and clean up the game subprocess's captured stderr.

        On a non-zero exit the captured traceback is logged so a crashing game
        no longer fails silently. The temp file is always removed. Safe to call
        more than once / when no capture is active.
        """
        handle = getattr(self, '_game_stderr_handle', None)
        path = getattr(self, '_game_stderr_path', None)
        self._game_stderr_handle = None
        self._game_stderr_path = None

        # A Play Object run (test_object) built a throwaway temp project;
        # clean it up now that the process it backed has exited. Ahead of
        # the "no stderr capture" early-return below so it still runs even
        # when there's no stderr path to drain (both exit paths —
        # _check_game_process and stop_game — call _drain_game_stderr, so
        # a manually-stopped object test doesn't leak its temp dir either).
        temp_dir = getattr(self, '_game_temp_project_dir', None)
        self._game_temp_project_dir = None
        if temp_dir is not None:
            import shutil
            shutil.rmtree(temp_dir, ignore_errors=True)

        if handle is not None:
            try:
                handle.close()
            except OSError:
                pass
        if not path:
            return
        try:
            with open(path, 'r', encoding='utf-8', errors='replace') as f:
                output = f.read().strip()
            if output and return_code not in (0, None):
                logger.error(
                    f"Game subprocess (exit {return_code}) stderr:\n{output}"
                )
        except OSError as e:
            logger.debug(f"Could not read game stderr log: {e}")
        finally:
            try:
                os.remove(path)
            except OSError:
                pass

    def stop_game(self):
        """Stop the running game subprocess"""
        return_code = None
        if hasattr(self, '_game_process') and self._game_process is not None:
            try:
                self._game_process.terminate()
                # Give it a moment to terminate gracefully
                try:
                    return_code = self._game_process.wait(timeout=2)
                except subprocess.TimeoutExpired:
                    self._game_process.kill()
                self._game_process = None
                self.update_status(self.tr("Game stopped"))
            except Exception as e:
                logger.error(f"Error stopping game: {e}")
        if hasattr(self, '_check_game_timer') and self._check_game_timer:
            self._check_game_timer.stop()
        self._drain_game_stderr(return_code)

    def debug_game(self):
        """Run game in debug mode with additional logging"""
        if self.game_runner.is_game_running():
            QMessageBox.information(
                self,
                self.tr("Game Running"),
                self.tr("A game is already running. Please stop it first.")
            )
            return

        # Save project first
        if self.project_manager.is_dirty():
            self.save_project()

        # For now, debug mode is the same as test mode with verbose output
        # Future: Add breakpoints, variable inspection, step-through debugging
        self.update_status(self.tr("Starting game in debug mode..."))

        QMessageBox.information(
            self,
            self.tr("Debug Mode"),
            self.tr("Debug mode will start the game with verbose console output.\n\n"
                    "Future features:\n"
                    "• Breakpoints\n"
                    "• Variable inspection\n"
                    "• Step-through execution\n"
                    "• Performance profiling\n\n"
                    "For now, check the console for debug messages.")
        )

        # Run game in test mode (debug mode to be implemented)
        if self.game_runner.test_game(str(self.current_project_path), Config.get('language', 'en')):
            self.update_status(self.tr("Game started in debug mode - Check console for debug output"))
        else:
            self.update_status(self.tr("Failed to start game"))
            QMessageBox.warning(
                self,
                self.tr("Game Error"),
                self.tr("Failed to start the game. Check console for details.")
            )

    def _show_validation_warnings(self):
        """Validate project and show any warnings to the user"""
        issues = self.project_manager.validate_project()

        if not issues:
            return

        # Separate errors and warnings
        errors = [i for i in issues if i['type'] == 'error']
        warnings = [i for i in issues if i['type'] == 'warning']

        # Build message
        message_parts = []

        if errors:
            message_parts.append(self.tr("Errors:"))
            for err in errors:
                message_parts.append(f"  • {err['message']}")
            message_parts.append("")

        if warnings:
            message_parts.append(self.tr("Warnings:"))
            for warn in warnings:
                message_parts.append(f"  • {warn['message']}")

        message = "\n".join(message_parts)

        if errors:
            # Show errors as critical - they will likely cause problems
            QMessageBox.warning(
                self,
                self.tr("Project Validation Issues"),
                message
            )
        elif warnings:
            # Show warnings as information
            QMessageBox.information(
                self,
                self.tr("Project Validation Warnings"),
                message
            )
