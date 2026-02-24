#!/usr/bin/env python3
"""
Android APK Exporter for PyGameMaker
Uses Kivy runtime bundled with Buildozer to create Android APK packages
"""

import subprocess
import shutil
import json
import platform
from pathlib import Path
from typing import Dict
from PySide6.QtCore import QObject, Signal

from core.logger import get_logger
logger = get_logger(__name__)


class AndroidExporter(QObject):
    """Handles exporting games as Android APK packages using Kivy + Buildozer"""

    progress_update = Signal(int, str)  # progress percentage, status message
    export_complete = Signal(bool, str)  # success, message

    def __init__(self):
        super().__init__()
        self.project_path = None
        self.output_path = None
        self.export_settings = {}
        self.project_data = None

    def _load_rooms_from_files(self, project_dir: Path) -> None:
        """Load room instance data from separate files in rooms/ directory

        The main project.json stores room metadata but NOT instances.
        Instances are stored in separate rooms/<room_name>.json files.
        """
        rooms_dir = project_dir / "rooms"

        if not rooms_dir.exists():
            logger.debug("No rooms/ directory found, using embedded room data")
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
                        logger.debug("Loaded room: {} ({} instances from file)".format(
                            room_name, len(room_data['instances'])))

                    for key in ['width', 'height', 'background_color', 'background_image',
                               'tile_horizontal', 'tile_vertical']:
                        if key in file_room_data:
                            room_data[key] = file_room_data[key]

                except Exception as e:
                    logger.warning("Could not load room file {}: {}".format(room_file, e))
            else:
                if room_data.get('instances'):
                    logger.debug("Room {}: using embedded instances ({} instances)".format(
                        room_name, len(room_data['instances'])))
                else:
                    logger.warning("Room {}: no instances found".format(room_name))

    def _load_objects_from_files(self, project_dir: Path) -> None:
        """Load object data from separate files in objects/ directory

        The main project.json stores object metadata but NOT events.
        Events are stored in separate objects/<object_name>.json files.
        """
        from collections import OrderedDict

        objects_dir = project_dir / "objects"

        if not objects_dir.exists():
            logger.debug("No objects/ directory found, using embedded object data")
            return

        objects_data = self.project_data.get('assets', {}).get('objects', {})

        for object_name, object_data in list(objects_data.items()):
            object_file = objects_dir / "{}.json".format(object_name)

            if isinstance(object_data, str):
                object_data = {"name": object_name, "asset_type": "object"}
                objects_data[object_name] = object_data

            if object_file.exists():
                try:
                    with open(object_file, 'r', encoding='utf-8') as f:
                        file_object_data = json.load(f, object_pairs_hook=OrderedDict)

                    for key in ['events', 'sprite', 'visible', 'solid', 'persistent',
                               'depth', 'parent', 'mask', 'imported', 'created', 'modified']:
                        if key in file_object_data:
                            object_data[key] = file_object_data[key]

                    event_count = len(file_object_data.get('events', {}))
                    logger.debug("Loaded object: {} ({} events from file)".format(
                        object_name, event_count))

                except Exception as e:
                    logger.warning("Could not load object file {}: {}".format(object_file, e))
            else:
                if object_data.get('events'):
                    logger.debug("Object {}: using embedded events".format(object_name))
                else:
                    logger.warning("Object {}: no events found".format(object_name))

    def export_project(self, project_path: str, output_path: str, settings: Dict) -> bool:
        """
        Export the project as an Android APK using Kivy + Buildozer

        Args:
            project_path: Path to the .pgm project file
            output_path: Directory where the APK will be created
            settings: Export settings dictionary

        Returns:
            True if export successful, False otherwise
        """
        self.project_path = Path(project_path)
        self.output_path = Path(output_path)
        self.export_settings = settings

        try:
            # Load project data - handle both directory and file paths
            if self.project_path.is_dir():
                project_file = self.project_path / "project.json"
                project_dir = self.project_path
            else:
                project_file = self.project_path
                project_dir = self.project_path.parent

            with open(project_file, 'r') as f:
                self.project_data = json.load(f)

            # Load room data from external files (instances are stored separately)
            self._load_rooms_from_files(project_dir)

            # Load object data from external files (events are stored separately)
            self._load_objects_from_files(project_dir)

            # Step 1: Verify platform (Buildozer only runs on Linux and macOS)
            self.progress_update.emit(5, "Checking platform...")

            self._use_wsl = False

            if platform.system() == 'Windows':
                # Check if WSL is available as a fallback
                from export.android.wsl_bridge import WSLBridge
                bridge = WSLBridge()
                if not bridge.is_wsl_available():
                    wsl_info = bridge.get_wsl_info()
                    self.export_complete.emit(
                        False,
                        "Android export requires Linux or macOS.\n\n"
                        "Buildozer (the Android build tool) does not run "
                        "natively on Windows.\n\n"
                        "WSL (Windows Subsystem for Linux) was not detected.\n"
                        "Status: {}\n\n"
                        "To enable Android export on Windows:\n"
                        "1. Open PowerShell as Administrator\n"
                        "2. Run: wsl --install\n"
                        "3. Restart your computer\n"
                        "4. Set up your Linux username and password\n"
                        "5. Try this export again\n\n"
                        "Or use the HTML5 export for a cross-platform "
                        "web version.".format(wsl_info['message'])
                    )
                    return False

                self._use_wsl = True
                self._wsl_bridge = bridge
                logger.info("Windows detected — will use WSL for buildozer")

            # Step 2: Verify dependencies
            self.progress_update.emit(10, "Checking dependencies...")

            if self._use_wsl:
                # Check and auto-install dependencies inside WSL
                deps_ok, missing = self._wsl_bridge.check_dependencies()
                if not deps_ok:
                    logger.info("Missing WSL deps: %s", missing)
                    self.progress_update.emit(
                        12, "Installing WSL dependencies (first-time setup)...")

                    success, message = self._wsl_bridge.install_dependencies(
                        progress_callback=lambda msg:
                            self.progress_update.emit(12, msg))

                    if not success:
                        self.export_complete.emit(
                            False,
                            "Failed to set up WSL dependencies.\n\n"
                            "{}\n\n"
                            "You can try installing manually in WSL:\n"
                            "  wsl -u root apt install python3 python3-pip "
                            "openjdk-17-jdk build-essential cmake zip "
                            "unzip git\n"
                            "  wsl pip3 install --user buildozer "
                            "'cython<3.0'".format(message)
                        )
                        return False
            else:
                # Native Linux/macOS dependency checks
                if not self._check_buildozer():
                    self.export_complete.emit(
                        False,
                        "Buildozer not found.\n\n"
                        "Please install it in your virtual environment:\n"
                        "pip install buildozer\n\n"
                        "Or install all dependencies:\n"
                        "pip install -r requirements.txt"
                    )
                    return False

                if not self._check_kivy():
                    self.export_complete.emit(
                        False,
                        "Kivy not found.\n\n"
                        "The Android exporter requires Kivy to be installed.\n"
                        "Please install it in your virtual environment:\n\n"
                        "pip install kivy\n\n"
                        "Or install all dependencies:\n"
                        "pip install -r requirements.txt"
                    )
                    return False

                if not self._check_cython():
                    self.export_complete.emit(
                        False,
                        "Cython not found or incompatible version.\n\n"
                        "Buildozer requires Cython < 3.0 to compile for "
                        "Android.\n"
                        "(Cython 3.x removed the 'long' type which breaks "
                        "pyjnius.)\n\n"
                        "Install a compatible version with:\n"
                        "pip install 'cython>=0.29.33,<3.0'\n\n"
                        "Or install all dependencies:\n"
                        "pip install -r requirements.txt"
                    )
                    return False

                if not self._check_java():
                    self.export_complete.emit(
                        False,
                        "Java JDK not found.\n\n"
                        "Buildozer requires Java JDK to compile Android "
                        "apps.\n\n"
                        "Install it with:\n"
                        "• Linux: sudo apt install openjdk-17-jdk\n"
                        "• macOS: brew install openjdk@17\n\n"
                        "Then try the export again."
                    )
                    return False

                missing_tools = self._check_build_tools()
                if missing_tools:
                    tools_str = ', '.join(missing_tools)
                    self.export_complete.emit(
                        False,
                        "Missing system build tools: {}\n\n"
                        "Buildozer needs these tools to compile native "
                        "code for Android.\n\n"
                        "Install them with:\n"
                        "sudo apt install build-essential autoconf automake "
                        "libtool pkg-config cmake zip unzip python3-dev "
                        "libffi-dev libssl-dev\n\n"
                        "Then try the export again.".format(tools_str)
                    )
                    return False

            # Step 3: Create temporary build directory
            self.progress_update.emit(15, "Creating build directory...")
            build_dir = self._create_build_directory()

            # Step 4: Generate Kivy game using KivyExporter
            self.progress_update.emit(20, "Generating Kivy game...")
            if not self._generate_kivy_game(build_dir):
                self.export_complete.emit(False, "Failed to generate Kivy game")
                return False

            # Step 5: Generate buildozer.spec
            self.progress_update.emit(35, "Generating buildozer.spec...")
            if not self._generate_buildozer_spec(build_dir):
                self.export_complete.emit(False, "Failed to generate buildozer.spec")
                return False

            # Step 6: Run Buildozer to build the APK
            self.progress_update.emit(40, "Building APK (this may take a long time on first run)...")
            result = self._run_buildozer(build_dir)
            if result is not True:
                self.export_complete.emit(False, "Buildozer build failed:\n\n{}".format(result))
                return False

            # Step 7: Copy APK to output directory
            self.progress_update.emit(90, "Copying APK to output directory...")
            if not self._copy_to_output(build_dir):
                self.export_complete.emit(
                    False,
                    "Build completed but no APK file was found.\n\n"
                    "Check the build output for errors."
                )
                return False

            # Step 8: Cleanup (if not in debug mode)
            if not settings.get('include_debug', False):
                self.progress_update.emit(95, "Cleaning up temporary files...")
                self._cleanup(build_dir)

            self.progress_update.emit(100, "Export complete!")
            self.export_complete.emit(
                True,
                "Game exported successfully to:\n{}".format(self.output_path)
            )
            return True

        except Exception as e:
            error_msg = "Export failed: {}".format(str(e))
            self.export_complete.emit(False, error_msg)
            import traceback
            traceback.print_exc()
            return False

    def _check_buildozer(self) -> bool:
        """Check if Buildozer is installed"""
        try:
            import buildozer  # noqa: F401
            return True
        except ImportError:
            return False

    def _check_kivy(self) -> bool:
        """Check if Kivy is installed"""
        try:
            import kivy  # noqa: F401
            return True
        except ImportError:
            return False

    def _check_cython(self) -> bool:
        """Check if Cython is installed and compatible with pyjnius.

        Cython 3.x removed the ``long`` builtin type which breaks the
        pyjnius recipe used by python-for-android.  We therefore require
        Cython < 3.0.
        """
        try:
            import Cython  # noqa: F401
            major = int(Cython.__version__.split('.')[0])
            if major >= 3:
                return False
            return True
        except ImportError:
            return False

    def _check_build_tools(self) -> list:
        """Check for system build tools required by Buildozer on Linux.

        Returns a list of missing tool names (empty if all present).
        """
        if platform.system() != 'Linux':
            return []

        missing = []
        for tool in ['autoconf', 'automake', 'libtoolize', 'pkg-config',
                      'cmake', 'zip', 'unzip']:
            try:
                result = subprocess.run(
                    ['which', tool],
                    capture_output=True, timeout=5
                )
                if result.returncode != 0:
                    missing.append(tool)
            except (FileNotFoundError, subprocess.TimeoutExpired):
                missing.append(tool)
        return missing

    def _check_java(self) -> bool:
        """Check if Java JDK is installed"""
        try:
            result = subprocess.run(
                ['java', '-version'],
                capture_output=True, text=True, timeout=10
            )
            return result.returncode == 0
        except (FileNotFoundError, subprocess.TimeoutExpired):
            return False

    def _create_build_directory(self) -> Path:
        """Create a temporary build directory.

        Uses the system temp folder instead of the project directory
        to avoid conflicts with Dropbox/OneDrive file-locking and to
        keep large build artifacts out of cloud-synced folders.
        """
        import tempfile
        build_dir = Path(tempfile.mkdtemp(prefix='pygm_android_'))

        logger.info("Build directory: %s", build_dir)
        return build_dir

    def _generate_kivy_game(self, build_dir: Path) -> bool:
        """
        Use KivyExporter to generate the Kivy game in the build directory

        Returns:
            True if successful, False otherwise
        """
        try:
            from export.Kivy.kivy_exporter import KivyExporter

            if self.project_path.is_dir():
                project_dir = self.project_path
            else:
                project_dir = self.project_path.parent

            exporter = KivyExporter(self.project_data, project_dir, build_dir)
            success = exporter.export()

            if not success:
                logger.error("KivyExporter.export() returned False")
                return False

            # Verify main.py exists (buildozer.spec sets source.dir = game)
            game_main = build_dir / "game" / "main.py"
            if not game_main.exists():
                logger.error("main.py not found in build directory")
                return False

            return True

        except Exception as e:
            logger.error("Error generating Kivy game: {}".format(e))
            import traceback
            traceback.print_exc()
            return False

    def _generate_buildozer_spec(self, build_dir: Path) -> bool:
        """
        Generate buildozer.spec using BuildspecGenerator

        Returns:
            True if successful, False otherwise
        """
        try:
            from export.Kivy.buildspec_generator import BuildspecGenerator

            generator = BuildspecGenerator(self.project_data, build_dir)
            success = generator.generate_buildozer_spec()

            if not success:
                logger.error("BuildspecGenerator.generate_buildozer_spec() returned False")
                return False

            # Patch the spec to auto-accept SDK license for unattended builds
            spec_path = build_dir / "buildozer.spec"
            if spec_path.exists():
                content = spec_path.read_text(encoding='utf-8')
                content = content.replace(
                    'android.accept_sdk_license = False',
                    'android.accept_sdk_license = True'
                )
                spec_path.write_text(content, encoding='utf-8')
                logger.debug("Patched buildozer.spec: accept_sdk_license = True")

            return True

        except Exception as e:
            logger.error("Error generating buildozer.spec: {}".format(e))
            import traceback
            traceback.print_exc()
            return False

    def _run_buildozer(self, build_dir: Path):
        """Run Buildozer to build the Android APK.

        When running on Windows with WSL, delegates to the WSLBridge which
        converts paths and executes buildozer inside the Linux environment.

        Returns:
            True on success, or an error message string on failure.
        """
        try:
            logger.info("=" * 60)
            logger.info("Running Buildozer (this may take 15-30 minutes on first run)...")
            logger.info("First run will download Android SDK/NDK (~2GB).")
            logger.info("Subsequent builds will be much faster.")
            logger.info("=" * 60)

            if self._use_wsl:
                # Run buildozer inside WSL
                logger.info("Using WSL to run buildozer")
                process = self._wsl_bridge.run_buildozer(str(build_dir))
                timeout = 2400  # 40 min — WSL filesystem I/O is slower
            else:
                # Native Linux/macOS execution
                import sys, os
                python_exe = sys.executable

                # Ensure the venv's bin dir is on PATH so buildozer can find
                # tools like cython that are installed in the virtual environment.
                env = os.environ.copy()
                venv_bin = str(Path(python_exe).parent)
                venv_root = str(Path(python_exe).parent.parent)
                env['PATH'] = venv_bin + os.pathsep + env.get('PATH', '')
                # Buildozer tries `pip install --user` which fails inside a
                # virtualenv.  Disable --user installs and point VIRTUAL_ENV
                # so pip installs into the venv normally.
                env['PIP_USER'] = '0'
                env['VIRTUAL_ENV'] = venv_root

                process = subprocess.Popen(
                    [python_exe, '-m', 'buildozer', 'android', 'debug'],
                    cwd=build_dir,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.STDOUT,
                    text=True,
                    bufsize=1,
                    env=env
                )
                timeout = 1200  # 20 min

            # Capture output for error reporting
            output_lines = []
            for line in process.stdout:
                stripped = line.rstrip()
                logger.debug(stripped)
                output_lines.append(stripped)

            # Wait for completion
            process.wait(timeout=timeout)

            if process.returncode != 0:
                logger.error("Buildozer failed with return code: {}".format(process.returncode))
                # Extract the most useful error information.
                # Buildozer's last ~30 lines are often just an environment
                # dump; the real errors are earlier.  Search for error
                # indicators and show those lines plus the tail.
                error_lines = []
                for i, line in enumerate(output_lines):
                    low = line.lower()
                    if ('error' in low or 'exception' in low
                            or 'traceback' in low or 'fatal' in low
                            or 'not found' in low or 'failed' in low
                            or 'no such file' in low
                            or 'command not found' in low
                            or 'permission denied' in low):
                        # Grab some context around the error
                        start = max(0, i - 2)
                        end = min(len(output_lines), i + 3)
                        for j in range(start, end):
                            if output_lines[j] not in error_lines:
                                error_lines.append(output_lines[j])

                tail = '\n'.join(output_lines[-15:])
                if error_lines:
                    errors = '\n'.join(error_lines[-30:])
                    return ("Buildozer exited with code {}.\n\n"
                            "Errors found:\n{}\n\n"
                            "End of log:\n{}").format(
                                process.returncode, errors, tail)
                else:
                    return "Buildozer exited with code {}.\n\nOutput:\n{}".format(
                        process.returncode, tail)

            logger.info("Buildozer build completed successfully!")
            return True

        except subprocess.TimeoutExpired:
            timeout_min = 40 if self._use_wsl else 20
            logger.error("Buildozer timed out after %d minutes", timeout_min)
            if process:
                process.kill()
            return (
                "Buildozer timed out after {} minutes.\n\n"
                "The first Android build downloads the SDK/NDK and can take\n"
                "a very long time on slow connections. Try running again —\n"
                "subsequent builds are much faster once the SDK is cached.".format(
                    timeout_min)
            )
        except Exception as e:
            logger.error("Error running Buildozer: {}".format(e))
            import traceback
            traceback.print_exc()
            return "Error launching Buildozer: {}".format(e)

    def _copy_to_output(self, build_dir: Path) -> bool:
        """Copy the built APK to the output directory.

        Returns:
            True if an APK was found and copied, False otherwise.
        """
        # Create output directory
        self.output_path.mkdir(parents=True, exist_ok=True)

        # Buildozer places APKs in the bin/ directory
        bin_dir = build_dir / "bin"
        found_apk = False

        if bin_dir.exists():
            for apk_file in bin_dir.glob("*.apk"):
                dest = self.output_path / apk_file.name
                shutil.copy2(apk_file, dest)
                logger.info("Copied APK: {}".format(apk_file.name))
                found_apk = True

        if not found_apk:
            logger.error("No APK files found in {}".format(bin_dir))

        return found_apk

    @staticmethod
    def _force_remove_readonly(func, path, exc_info):
        """Error handler for shutil.rmtree to remove read-only files.

        Git pack files and other WSL-created files may be read-only on
        Windows, causing shutil.rmtree to fail with Access Denied.
        """
        import os, stat
        try:
            os.chmod(path, stat.S_IWRITE)
            func(path)
        except Exception:
            pass

    def _cleanup(self, build_dir: Path):
        """Clean up temporary build files"""
        try:
            if build_dir.exists():
                shutil.rmtree(build_dir, onerror=self._force_remove_readonly)
        except Exception as e:
            logger.warning("Could not clean up build directory: {}".format(e))
