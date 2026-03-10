#!/usr/bin/env python3
"""
iOS IPA Exporter for PyGameMaker IDE

Builds a signed iOS app using kivy-ios + xcodebuild on macOS.
Requires:
  - macOS with Xcode installed
  - Xcode Command Line Tools
  - Python package kivy-ios (auto-installed if missing)
  - Apple ID signed into Xcode (free account is sufficient)

Apps signed with a free Apple ID expire after 7 days and must be
re-installed to renew.  A paid Apple Developer account ($99/year)
removes this restriction and allows App Store distribution.
"""

import subprocess
import shutil
import json
import platform
import sys
import os
import tempfile
import time
import collections
from pathlib import Path
from typing import Dict

from PySide6.QtCore import QObject, Signal

from core.logger import get_logger
logger = get_logger(__name__)


class iOSExporter(QObject):
    """Exports games as iOS IPA packages using kivy-ios + xcodebuild."""

    progress_update = Signal(int, str)   # (percent, message)
    export_complete = Signal(bool, str)  # (success, message)

    def __init__(self):
        super().__init__()
        self.project_path = None
        self.output_path = None
        self.export_settings = {}
        self.project_data = None
        self.cancel_requested = False

    # ------------------------------------------------------------------
    # Public entry point
    # ------------------------------------------------------------------

    def export_project(self, project_path: str, output_path: str,
                       settings: Dict) -> bool:
        """
        Export the project as an iOS IPA using kivy-ios + xcodebuild.

        Args:
            project_path: Path to the project directory (or project.json)
            output_path:  Directory where the IPA will be written
            settings:     Export settings dictionary

        Returns:
            True on success, False otherwise (result also via signal).
        """
        self.project_path = Path(project_path)
        self.output_path = Path(output_path)
        self.export_settings = settings

        try:
            # ---- Step 1: platform check ----------------------------------
            self.progress_update.emit(5, "Checking platform requirements...")

            if not self._check_macos():
                self.export_complete.emit(
                    False,
                    "iOS export requires macOS with Xcode installed.\n\n"
                    "This feature is not available on Windows or Linux."
                )
                return False

            if not self._check_xcode():
                self.export_complete.emit(
                    False,
                    "Xcode not found.\n\n"
                    "Please install Xcode from the Mac App Store, then run:\n"
                    "  xcode-select --install\n\n"
                    "After installing, open Xcode once to accept the licence."
                )
                return False

            if not self._check_xcode_cmdline():
                self.export_complete.emit(
                    False,
                    "Xcode Command Line Tools not found.\n\n"
                    "Install them with:\n"
                    "  xcode-select --install"
                )
                return False

            # ---- Step 2: kivy-ios ----------------------------------------
            self.progress_update.emit(10, "Checking kivy-ios...")

            if not self._check_kivy_ios():
                self.progress_update.emit(
                    11, "Installing kivy-ios (one-time setup)...")
                ok, msg = self._auto_install_kivy_ios()
                if not ok:
                    self.export_complete.emit(
                        False,
                        "Failed to install kivy-ios.\n\n"
                        "{}\n\n"
                        "Install manually with:\n"
                        "  pip install kivy-ios".format(msg)
                    )
                    return False

            # ---- Step 3: load project data --------------------------------
            self.progress_update.emit(15, "Loading project...")

            if self.project_path.is_dir():
                project_file = self.project_path / "project.json"
                project_dir = self.project_path
            else:
                project_file = self.project_path
                project_dir = self.project_path.parent

            with open(project_file, 'r') as f:
                self.project_data = json.load(f)

            self._load_rooms_from_files(project_dir)
            self._load_objects_from_files(project_dir)

            # ---- Step 4: create temp build directory ----------------------
            self.progress_update.emit(16, "Creating build directory...")
            build_dir = self._create_build_directory()

            # ---- Step 5: generate Kivy game code --------------------------
            self.progress_update.emit(20, "Generating Kivy game code...")
            if not self._generate_kivy_game(build_dir):
                self.export_complete.emit(False, "Failed to generate Kivy game code.")
                return False

            # ---- Step 6: build kivy-ios distribution ----------------------
            self.progress_update.emit(
                28,
                "Building iOS libraries (first run only — ~30-60 min). "
                "Subsequent builds are fast."
            )
            result = self._build_ios_dist(build_dir)
            if result is not True:
                self.export_complete.emit(
                    False, "kivy-ios build failed:\n\n{}".format(result))
                return False

            # ---- Step 7: create Xcode project -----------------------------
            self.progress_update.emit(68, "Creating Xcode project...")
            result = self._create_xcode_project(build_dir)
            if result is not True:
                self.export_complete.emit(
                    False, "Failed to create Xcode project:\n\n{}".format(result))
                return False

            # ---- Step 8: build + archive ----------------------------------
            self.progress_update.emit(72, "Building with Xcode (this may take a few minutes)...")
            result = self._build_and_archive(build_dir)
            if result is not True:
                self.export_complete.emit(
                    False,
                    "xcodebuild failed:\n\n{}\n\n"
                    "Make sure you are signed into Xcode with your Apple ID:\n"
                    "  Xcode → Settings → Accounts → Add Apple ID".format(result)
                )
                return False

            # ---- Step 9: export IPA ---------------------------------------
            self.progress_update.emit(85, "Exporting IPA...")
            result = self._export_ipa(build_dir)
            if result is not True:
                self.export_complete.emit(
                    False, "IPA export failed:\n\n{}".format(result))
                return False

            # ---- Step 10: copy to output ----------------------------------
            self.progress_update.emit(90, "Copying IPA to output directory...")
            if not self._copy_to_output(build_dir):
                self.export_complete.emit(
                    False,
                    "Build completed but no IPA file was found.\n\n"
                    "Check the build output for errors."
                )
                return False

            # ---- Step 11: cleanup -----------------------------------------
            if not settings.get('include_debug', False):
                self.progress_update.emit(95, "Cleaning up temporary files...")
                self._cleanup(build_dir)

            self.progress_update.emit(100, "Export complete!")
            self.export_complete.emit(
                True,
                "iOS app exported successfully to:\n{}\n\n"
                "Install on your iPhone via Apple Configurator 2 (free, "
                "Mac App Store) or AltStore.\n\n"
                "Note: Apps signed with a free Apple ID expire after 7 days.\n"
                "Re-install to renew.".format(self.output_path)
            )
            return True

        except Exception as e:
            self.export_complete.emit(
                False, "Export failed: {}".format(e))
            import traceback
            traceback.print_exc()
            return False

    # ------------------------------------------------------------------
    # Dependency checks
    # ------------------------------------------------------------------

    def _check_macos(self) -> bool:
        return platform.system() == 'Darwin'

    def _check_xcode(self) -> bool:
        """Check that Xcode is installed via xcode-select."""
        try:
            result = subprocess.run(
                ['xcode-select', '-p'],
                capture_output=True, text=True, timeout=10
            )
            return result.returncode == 0 and result.stdout.strip()
        except (FileNotFoundError, subprocess.TimeoutExpired):
            return False

    def _check_xcode_cmdline(self) -> bool:
        """Check that Xcode command line tools are available."""
        try:
            result = subprocess.run(
                ['xcrun', '--version'],
                capture_output=True, text=True, timeout=10
            )
            return result.returncode == 0
        except (FileNotFoundError, subprocess.TimeoutExpired):
            return False

    def _check_kivy_ios(self) -> bool:
        try:
            import kivy_ios  # noqa: F401
            return True
        except ImportError:
            return False

    def _auto_install_kivy_ios(self):
        """Install kivy-ios via pip. Returns (success, message)."""
        try:
            process = subprocess.run(
                [sys.executable, '-m', 'pip', 'install', 'kivy-ios'],
                capture_output=True, text=True, timeout=300
            )
            if process.returncode == 0:
                return True, ""
            return False, process.stdout + process.stderr
        except subprocess.TimeoutExpired:
            return False, "pip install timed out"
        except Exception as e:
            return False, str(e)

    # ------------------------------------------------------------------
    # Project data helpers (identical to AndroidExporter)
    # ------------------------------------------------------------------

    def _load_rooms_from_files(self, project_dir: Path) -> None:
        rooms_dir = project_dir / "rooms"
        if not rooms_dir.exists():
            return
        rooms_data = self.project_data.get('assets', {}).get('rooms', {})
        for room_name, room_data in rooms_data.items():
            room_file = rooms_dir / "{}.json".format(room_name)
            if room_file.exists():
                try:
                    with open(room_file, 'r', encoding='utf-8') as f:
                        file_room_data = json.load(f)
                    if 'instances' in file_room_data:
                        room_data['instances'] = file_room_data['instances']
                    for key in ['width', 'height', 'background_color',
                                'background_image', 'tile_horizontal',
                                'tile_vertical']:
                        if key in file_room_data:
                            room_data[key] = file_room_data[key]
                except Exception as e:
                    logger.warning("Could not load room {}: {}".format(room_name, e))

    def _load_objects_from_files(self, project_dir: Path) -> None:
        objects_dir = project_dir / "objects"
        if not objects_dir.exists():
            return
        objects_data = self.project_data.get('assets', {}).get('objects', {})
        for obj_name, obj_data in objects_data.items():
            obj_file = objects_dir / "{}.json".format(obj_name)
            if obj_file.exists():
                try:
                    with open(obj_file, 'r', encoding='utf-8') as f:
                        file_obj_data = json.load(f)
                    if 'events' in file_obj_data:
                        obj_data['events'] = file_obj_data['events']
                except Exception as e:
                    logger.warning("Could not load object {}: {}".format(obj_name, e))

    # ------------------------------------------------------------------
    # Build steps
    # ------------------------------------------------------------------

    def _create_build_directory(self) -> Path:
        build_dir = Path(tempfile.mkdtemp(prefix='pygm_ios_'))
        logger.info("iOS build directory: %s", build_dir)
        return build_dir

    def _generate_kivy_game(self, build_dir: Path) -> bool:
        """Generate Kivy game code using KivyExporter (same as Android)."""
        try:
            from export.Kivy.kivy_exporter import KivyExporter

            project_dir = (self.project_path if self.project_path.is_dir()
                           else self.project_path.parent)

            exporter = KivyExporter(self.project_data, project_dir, build_dir)
            if not exporter.export():
                logger.error("KivyExporter.export() returned False")
                return False

            game_main = build_dir / "game" / "main.py"
            if not game_main.exists():
                logger.error("main.py not found at %s", game_main)
                return False

            return True

        except Exception as e:
            logger.error("Error generating Kivy game: %s", e)
            import traceback; traceback.print_exc()
            return False

    def _build_ios_dist(self, build_dir: Path):
        """Run kivy-ios toolchain to build Python/Kivy for iOS ARM.

        Returns True on success, error string on failure.
        First run compiles from source (~30-60 min).
        Results are cached in ~/.<kivy-ios-dist> for subsequent builds.
        """
        # kivy-ios caches compiled recipes in a dist directory next to
        # the working dir, so run from build_dir.
        recipes = ['python3', 'kivy', 'pillow']

        _PHASE_MARKERS = [
            ('building python3',  32),
            ('building kivy',     48),
            ('building pillow',   62),
            ('already built',     None),  # cached — jump straight to 65
        ]

        for i, recipe in enumerate(recipes):
            if self.cancel_requested:
                return "Cancelled by user."

            cmd = [sys.executable, '-m', 'kivy_ios.toolchain', 'build', recipe]
            result = self._run_subprocess(
                cmd=cmd,
                cwd=build_dir,
                timeout=3600,  # 60 min per recipe (first run)
                start_pct=28 + i * 13,
                end_pct=28 + (i + 1) * 13,
                phase_label="Building {} for iOS...".format(recipe),
            )
            if result is not True:
                return result

        return True

    def _create_xcode_project(self, build_dir: Path):
        """Create the Xcode project using toolchain create.

        Returns True on success, error string on failure.
        """
        app_name = self.project_data.get('name', 'KivyGame')
        # Sanitise: Xcode scheme names can't have spaces or special chars
        safe_name = ''.join(c if c.isalnum() else '_' for c in app_name)
        game_dir = build_dir / "game"

        cmd = [
            sys.executable, '-m', 'kivy_ios.toolchain',
            'create', safe_name, str(game_dir)
        ]
        result = self._run_subprocess(
            cmd=cmd,
            cwd=build_dir,
            timeout=300,
            start_pct=68,
            end_pct=71,
            phase_label="Creating Xcode project...",
        )
        if result is not True:
            return result

        # Remember names for later steps
        self._app_name = safe_name
        self._xcode_proj_dir = build_dir / "{}-ios".format(safe_name)
        self._xcode_proj = self._xcode_proj_dir / "{}.xcodeproj".format(safe_name)

        if not self._xcode_proj.exists():
            return ("Xcode project not found at expected path:\n"
                    "{}".format(self._xcode_proj))
        return True

    def _build_and_archive(self, build_dir: Path):
        """Compile and archive the app with xcodebuild.

        Uses automatic code signing so a free Apple ID works.
        Returns True on success, error string on failure.
        """
        archive_path = build_dir / "{}.xcarchive".format(self._app_name)
        self._archive_path = archive_path

        cmd = [
            'xcodebuild',
            '-project', str(self._xcode_proj),
            '-scheme', self._app_name,
            '-sdk', 'iphoneos',
            '-configuration', 'Debug',
            '-archivePath', str(archive_path),
            'CODE_SIGN_STYLE=Automatic',
            '-allowProvisioningUpdates',
            'archive',
        ]
        return self._run_subprocess(
            cmd=cmd,
            cwd=build_dir,
            timeout=1800,  # 30 min
            start_pct=72,
            end_pct=84,
            phase_label="Compiling iOS app...",
        )

    def _export_ipa(self, build_dir: Path):
        """Export the .xcarchive to a distributable .ipa.

        Returns True on success, error string on failure.
        """
        export_options_path = build_dir / "ExportOptions.plist"
        export_options_path.write_text(
            '<?xml version="1.0" encoding="UTF-8"?>\n'
            '<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN"'
            ' "http://www.apple.com/DTDs/PropertyList-1.0.dtd">\n'
            '<plist version="1.0">\n'
            '<dict>\n'
            '    <key>method</key><string>development</string>\n'
            '    <key>signingStyle</key><string>automatic</string>\n'
            '    <key>compileBitcode</key><false/>\n'
            '    <key>thinning</key><string>&lt;none&gt;</string>\n'
            '</dict>\n'
            '</plist>\n',
            encoding='utf-8'
        )

        ipa_out = build_dir / "ipa"
        self._ipa_dir = ipa_out

        cmd = [
            'xcodebuild',
            '-exportArchive',
            '-archivePath', str(self._archive_path),
            '-exportOptionsPlist', str(export_options_path),
            '-exportPath', str(ipa_out),
            '-allowProvisioningUpdates',
        ]
        return self._run_subprocess(
            cmd=cmd,
            cwd=build_dir,
            timeout=300,
            start_pct=85,
            end_pct=89,
            phase_label="Exporting IPA...",
        )

    def _copy_to_output(self, build_dir: Path) -> bool:
        """Copy the built IPA to the user-chosen output directory."""
        self.output_path.mkdir(parents=True, exist_ok=True)

        found = False
        for ipa_file in self._ipa_dir.rglob("*.ipa"):
            dest = self.output_path / ipa_file.name
            shutil.copy2(ipa_file, dest)
            logger.info("Copied IPA: %s", ipa_file.name)
            found = True

        if not found:
            logger.error("No IPA file found in %s", self._ipa_dir)
        return found

    def _cleanup(self, build_dir: Path):
        try:
            if build_dir.exists():
                shutil.rmtree(build_dir)
        except Exception as e:
            logger.warning("Could not clean up build directory: %s", e)

    # ------------------------------------------------------------------
    # Shared subprocess helper
    # ------------------------------------------------------------------

    def _run_subprocess(self, cmd, cwd, timeout,
                        start_pct, end_pct, phase_label):
        """Run a subprocess, streaming output to the progress dialog.

        Emits progress_update signals throttled to 0.25 s intervals.
        Progress advances linearly from start_pct to end_pct as output
        lines matching known phase keywords are seen.

        Returns True on success, error string on failure.
        """
        _SIGNAL_INTERVAL = 0.25
        _ERROR_KEYWORDS = (
            'error:', 'fatal error', 'exception', 'traceback',
            'not found', 'failed', 'no such file',
            'command not found', 'permission denied',
        )

        env = os.environ.copy()
        venv_bin = str(Path(sys.executable).parent)
        env['PATH'] = venv_bin + os.pathsep + env.get('PATH', '')

        process = None
        try:
            process = subprocess.Popen(
                cmd,
                cwd=cwd,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
                bufsize=1,
                env=env,
            )

            output_lines = collections.deque(maxlen=2000)
            last_signal = 0.0
            current_pct = start_pct
            pct_range = max(1, end_pct - start_pct)

            for line in process.stdout:
                if self.cancel_requested:
                    process.kill()
                    self.export_complete.emit(False, "Export cancelled by user.")
                    return False

                stripped = line.rstrip()
                if not stripped:
                    continue
                logger.debug(stripped)
                output_lines.append(stripped)

                now = time.monotonic()
                if now - last_signal < _SIGNAL_INTERVAL:
                    continue

                # Nudge progress forward (up to end_pct - 1 to leave room
                # for the caller's milestone emit)
                if current_pct < end_pct - 1:
                    current_pct = min(current_pct + 1, end_pct - 1)

                low = stripped.lower()
                display = stripped[:120]
                self.progress_update.emit(current_pct, display)
                last_signal = now

            process.wait(timeout=timeout)

            if process.returncode != 0:
                all_lines = list(output_lines)
                error_lines = []
                for i, ln in enumerate(all_lines):
                    low = ln.lower()
                    if any(kw in low for kw in _ERROR_KEYWORDS):
                        start = max(0, i - 2)
                        end_ctx = min(len(all_lines), i + 3)
                        for j in range(start, end_ctx):
                            if all_lines[j] not in error_lines:
                                error_lines.append(all_lines[j])

                tail = '\n'.join(all_lines[-15:])
                if error_lines:
                    errors = '\n'.join(error_lines[-30:])
                    return ("{} exited with code {}.\n\n"
                            "Errors:\n{}\n\n"
                            "End of log:\n{}").format(
                                Path(cmd[0]).name, process.returncode,
                                errors, tail)
                return ("{} exited with code {}.\n\n"
                        "Output:\n{}").format(
                            Path(cmd[0]).name, process.returncode, tail)

            return True

        except subprocess.TimeoutExpired:
            if process:
                process.kill()
            return ("{} timed out after {} minutes.\n\n"
                    "The first iOS build compiles Python and Kivy from "
                    "source which can take a long time on slow Macs.\n"
                    "Try running again — subsequent builds are much "
                    "faster once the libraries are cached.").format(
                        Path(cmd[0]).name, timeout // 60)
        except Exception as e:
            import traceback; traceback.print_exc()
            return "Error running {}: {}".format(Path(cmd[0]).name, e)
