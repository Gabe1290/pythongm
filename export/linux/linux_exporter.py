#!/usr/bin/env python3
"""
Linux Binary Exporter for PyGameMaker
Uses Kivy runtime (80% GameMaker 7.0 compatible) bundled with PyInstaller
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


class LinuxExporter(QObject):
    """Handles exporting games as Linux binaries using Kivy runtime"""

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
            room_file = rooms_dir / f"{room_name}.json"

            if room_file.exists():
                try:
                    with open(room_file, 'r', encoding='utf-8') as f:
                        file_room_data = json.load(f)

                    # Merge file data into room data (file takes precedence for instances)
                    if 'instances' in file_room_data:
                        room_data['instances'] = file_room_data['instances']
                        logger.debug(f"Loaded room: {room_name} ({len(room_data['instances'])} instances from file)")

                    # Also copy other room properties from file if present
                    for key in ['width', 'height', 'background_color', 'background_image',
                               'tile_horizontal', 'tile_vertical']:
                        if key in file_room_data:
                            room_data[key] = file_room_data[key]

                except Exception as e:
                    logger.warning(f"Could not load room file {room_file}: {e}")
            else:
                # No external file - check if instances are embedded (legacy format)
                if room_data.get('instances'):
                    logger.debug(f"Room {room_name}: using embedded instances ({len(room_data['instances'])} instances)")
                else:
                    logger.warning(f"Room {room_name}: no instances found")

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
            object_file = objects_dir / f"{object_name}.json"

            # Handle case where object_data is a string path reference
            if isinstance(object_data, str):
                object_data = {"name": object_name, "asset_type": "object"}
                objects_data[object_name] = object_data

            if object_file.exists():
                try:
                    with open(object_file, 'r', encoding='utf-8') as f:
                        file_object_data = json.load(f, object_pairs_hook=OrderedDict)

                    # Merge file data into object data (file takes precedence)
                    for key in ['events', 'sprite', 'visible', 'solid', 'persistent',
                               'depth', 'parent', 'mask', 'imported', 'created', 'modified']:
                        if key in file_object_data:
                            object_data[key] = file_object_data[key]

                    event_count = len(file_object_data.get('events', {}))
                    logger.debug(f"Loaded object: {object_name} ({event_count} events from file)")

                except Exception as e:
                    logger.warning(f"Could not load object file {object_file}: {e}")
            else:
                # No external file - check if events are embedded (legacy format)
                if object_data.get('events'):
                    logger.debug(f"Object {object_name}: using embedded events")
                else:
                    logger.warning(f"Object {object_name}: no events found")

    def export_project(self, project_path: str, output_path: str, settings: Dict) -> bool:
        """
        Export the project as a Linux binary with Kivy runtime

        Args:
            project_path: Path to the .pgm project file
            output_path: Directory where the binary will be created
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

            # Step 1: Verify we're on Linux
            self.progress_update.emit(5, "Checking platform...")

            if platform.system() != 'Linux':
                self.export_complete.emit(
                    False,
                    "Linux export must be run on a Linux system.\n\n"
                    "PyInstaller creates binaries for the platform it runs on.\n"
                    "To create a Linux binary, run this export on Linux."
                )
                return False

            # Step 2: Verify dependencies are available
            self.progress_update.emit(10, "Checking dependencies...")

            if not self._check_pyinstaller():
                self.export_complete.emit(
                    False,
                    "PyInstaller not found.\n\n"
                    "Please install it in your virtual environment:\n"
                    "pip install pyinstaller"
                )
                return False

            if not self._check_kivy():
                self.export_complete.emit(
                    False,
                    "Kivy not found.\n\n"
                    "The Linux exporter requires Kivy to be installed.\n"
                    "Please install it in your virtual environment:\n\n"
                    "pip install kivy\n\n"
                    "Or install all dependencies:\n"
                    "pip install -r requirements.txt"
                )
                return False

            if not self._check_pillow():
                self.export_complete.emit(
                    False,
                    "Pillow (PIL) not found.\n\n"
                    "The Linux exporter requires Pillow for image handling.\n"
                    "Please install it in your virtual environment:\n\n"
                    "pip install pillow\n\n"
                    "Or install all dependencies:\n"
                    "pip install -r requirements.txt"
                )
                return False

            # Step 3: Create temporary build directory
            self.progress_update.emit(20, "Creating build directory...")
            build_dir = self._create_build_directory()

            # Step 4: Generate Kivy game using KivyExporter
            self.progress_update.emit(30, "Generating Kivy game...")
            if not self._generate_kivy_game(build_dir):
                self.export_complete.emit(False, "Failed to generate Kivy game")
                return False

            # Step 5: Create launcher script
            self.progress_update.emit(50, "Creating launcher script...")
            launcher_script = self._create_launcher_script(build_dir)

            # Step 6: Create PyInstaller spec file
            self.progress_update.emit(60, "Creating PyInstaller spec...")
            spec_file = self._create_spec_file(build_dir, launcher_script)

            # Step 7: Run PyInstaller
            self.progress_update.emit(70, "Building executable (this may take a while)...")
            if not self._run_pyinstaller(spec_file):
                self.export_complete.emit(False, "PyInstaller build failed")
                return False

            # Step 8: Copy output to final location
            self.progress_update.emit(90, "Copying to output directory...")
            self._copy_to_output(build_dir)

            # Step 9: Cleanup (if not in debug mode)
            if not settings.get('include_debug', False):
                self.progress_update.emit(95, "Cleaning up temporary files...")
                self._cleanup(build_dir)

            self.progress_update.emit(100, "Export complete!")
            self.export_complete.emit(True, f"Game exported successfully to:\n{self.output_path}")
            return True

        except Exception as e:
            error_msg = f"Export failed: {str(e)}"
            self.export_complete.emit(False, error_msg)
            import traceback
            traceback.print_exc()
            return False

    def _check_pyinstaller(self) -> bool:
        """Check if PyInstaller is installed"""
        try:
            import PyInstaller  # noqa: F401
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

    def _check_pillow(self) -> bool:
        """Check if Pillow (PIL) is installed"""
        try:
            import PIL  # noqa: F401
            return True
        except ImportError:
            return False

    def _create_build_directory(self) -> Path:
        """Create a temporary build directory"""
        project_dir = self.project_path.parent
        build_dir = project_dir / "build_temp_linux"

        # Clean if exists
        if build_dir.exists():
            shutil.rmtree(build_dir)

        build_dir.mkdir(parents=True, exist_ok=True)
        return build_dir

    def _generate_kivy_game(self, build_dir: Path) -> bool:
        """
        Use KivyExporter to generate the Kivy game in the build directory

        Returns:
            True if successful, False otherwise
        """
        try:
            # Import the Kivy exporter
            from export.Kivy.kivy_exporter import KivyExporter

            # Set up paths - use the project directory, not its parent
            # project_path can be either a directory or a project.json file
            if self.project_path.is_dir():
                project_dir = self.project_path
            else:
                project_dir = self.project_path.parent
            kivy_output = build_dir  # Export directly to build directory

            # Create the exporter and run it
            exporter = KivyExporter(self.project_data, project_dir, kivy_output)
            success = exporter.export()

            if not success:
                logger.error("KivyExporter.export() returned False")
                return False

            # Verify that the game directory was created
            game_dir = build_dir / "game"
            if not game_dir.exists():
                logger.error(f"Game directory not created at {game_dir}")
                return False

            # Verify main.py exists
            main_py = game_dir / "main.py"
            if not main_py.exists():
                logger.error(f"main.py not found at {main_py}")
                return False

            return True

        except Exception as e:
            logger.error(f"Error generating Kivy game: {e}")
            import traceback
            traceback.print_exc()
            return False

    def _create_launcher_script(self, build_dir: Path) -> Path:
        """
        Create the launcher script that runs the Kivy game

        This script handles PyInstaller frozen executable paths and
        launches the Kivy game.
        """
        launcher_script = build_dir / "game_launcher.py"

        game_name = self.project_data.get('name', 'Game')

        script_content = f'''#!/usr/bin/env python3
"""
Standalone Game Launcher for {game_name}
Generated by PyGameMaker IDE
Kivy-based runtime (80% GameMaker 7.0 compatible)
"""

import os
import sys
from pathlib import Path

def main():
    """Main game entry point"""
    try:
        # Set up paths for PyInstaller frozen executable
        if getattr(sys, 'frozen', False):
            # Running as compiled executable
            base_path = sys._MEIPASS
        else:
            # Running as script
            base_path = os.path.dirname(os.path.abspath(__file__))

        # Change to game directory
        game_dir = os.path.join(base_path, 'game')

        if not os.path.exists(game_dir):
            print(f"Error: Game directory not found at {{game_dir}}")
            sys.exit(1)

        os.chdir(game_dir)
        sys.path.insert(0, game_dir)

        # Import and run the Kivy game
        from main import GameApp

        # Run the game
        GameApp().run()

    except Exception as e:
        print(f"Game error: {{e}}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main()
'''

        with open(launcher_script, 'w') as f:
            f.write(script_content)

        return launcher_script

    def _create_spec_file(self, build_dir: Path, launcher_script: Path) -> Path:
        """
        Create PyInstaller spec file for bundling Kivy game on Linux

        This spec file includes:
        - The launcher script
        - The entire game/ directory (generated by KivyExporter)
        - All Kivy dependencies
        - All game assets (images, sounds)
        """
        import os
        spec_file = build_dir / "game.spec"

        game_name = self.project_data.get('name', 'Game').replace(' ', '_')

        # Collect ALL files from the game directory recursively
        # This ensures images, sounds, and all assets are included
        game_dir = build_dir / "game"
        datas = []

        for root, dirs, files in os.walk(game_dir):
            # Skip __pycache__ directories
            dirs[:] = [d for d in dirs if d != '__pycache__']

            for file in files:
                # Skip .pyc files
                if file.endswith('.pyc'):
                    continue

                # Get the full source path
                src_path = os.path.join(root, file)
                # Get the relative path from build_dir
                rel_path = os.path.relpath(src_path, build_dir)
                # Get the destination directory (relative to bundle)
                dest_dir = os.path.dirname(rel_path)

                datas.append((rel_path, dest_dir))

        # Format datas for spec file
        datas_str = ',\n        '.join([f"('{d[0]}', '{d[1]}')" for d in datas])

        # Hidden imports for Kivy
        hidden_imports = [
            'kivy',
            'kivy.app',
            'kivy.core.window',
            'kivy.core.image',
            'kivy.uix.widget',
            'kivy.graphics',
            'kivy.clock',
            'kivy.core.text',
            'kivy.core.audio',
            'PIL',  # Pillow for image loading
        ]

        hidden_imports_str = ',\n        '.join([f"'{imp}'" for imp in hidden_imports])

        # Create spec content (Linux-specific)
        spec_content = f'''# -*- mode: python ; coding: utf-8 -*-
# PyInstaller spec file for {game_name} (Linux)
# Generated by PyGameMaker IDE - Linux Exporter

block_cipher = None

a = Analysis(
    ['{launcher_script.name}'],
    pathex=[],
    binaries=[],
    datas=[
        {datas_str}
    ],
    hiddenimports=[
        {hidden_imports_str}
    ],
    hookspath=[],
    hooksconfig={{}},
    runtime_hooks=[],
    excludes=[
        'PySide6',
        'PyQt5',
        'PyQt6',
        'tkinter',
        'matplotlib',
        'numpy',
    ],
    noarchive=False,
    cipher=block_cipher,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='{game_name}',
    debug={self.export_settings.get('include_debug', False)},
    bootloader_ignore_signals=False,
    strip={not self.export_settings.get('include_debug', False)},
    upx={self.export_settings.get('optimize', False)},
    upx_exclude=[],
    runtime_tmpdir=None,
    console={self.export_settings.get('include_debug', False)},
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)
'''

        with open(spec_file, 'w') as f:
            f.write(spec_content)

        return spec_file

    def _run_pyinstaller(self, spec_file: Path) -> bool:
        """Run PyInstaller to build the executable"""
        try:
            logger.info("=" * 60)
            logger.info("Running PyInstaller (this may take 5-10 minutes)...")
            logger.info("Building with Kivy is memory-intensive.")
            logger.info("If the process is killed, try closing other applications.")
            logger.info("=" * 60)

            # Use the same Python interpreter that's running this script
            # This ensures we use the venv's pyinstaller
            import sys
            python_exe = sys.executable

            # Run PyInstaller as a module to ensure we use the venv's version
            process = subprocess.Popen(
                [python_exe, '-m', 'PyInstaller', '--clean', str(spec_file)],
                cwd=spec_file.parent,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
                bufsize=1
            )

            # Stream output in real-time
            for line in process.stdout:
                logger.debug(line.rstrip())

            # Wait for completion with longer timeout (10 minutes)
            process.wait(timeout=600)

            if process.returncode != 0:
                logger.error(f"PyInstaller failed with return code: {process.returncode}")
                return False

            logger.info("PyInstaller build completed successfully!")
            return True

        except subprocess.TimeoutExpired:
            logger.error("PyInstaller timed out after 10 minutes")
            logger.error("This usually means the build is too memory-intensive for your system.")
            logger.info("Try:")
            logger.info("1. Close other applications to free up memory")
            logger.info("2. Increase system swap space")
            logger.info("3. Build on a machine with more RAM (recommended: 8GB+)")
            if process:
                process.kill()
            return False
        except Exception as e:
            logger.error(f"Error running PyInstaller: {e}")
            import traceback
            traceback.print_exc()
            return False

    def _copy_to_output(self, build_dir: Path):
        """Copy the built executable to the output directory"""
        dist_dir = build_dir / "dist"

        # Create output directory
        self.output_path.mkdir(parents=True, exist_ok=True)

        # Copy all files from dist to output
        if dist_dir.exists():
            for item in dist_dir.iterdir():
                dest = self.output_path / item.name
                if item.is_file():
                    shutil.copy2(item, dest)
                    # Make the binary executable
                    if not item.suffix:  # No extension means it's likely the binary
                        dest.chmod(dest.stat().st_mode | 0o111)
                elif item.is_dir():
                    shutil.copytree(item, dest, dirs_exist_ok=True)

    def _cleanup(self, build_dir: Path):
        """Clean up temporary build files"""
        try:
            if build_dir.exists():
                shutil.rmtree(build_dir)
        except Exception as e:
            logger.warning(f"Could not clean up build directory: {e}")
