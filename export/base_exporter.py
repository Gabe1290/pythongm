#!/usr/bin/env python3
"""
Shared base class for the Kivy-based platform exporters.

ExeExporter, LinuxExporter, MacOSExporter and AndroidExporter all wrap the
KivyExporter and share project loading, dependency checks and Kivy game
generation. This base holds the parts that were verified byte-identical
across the exe/linux/macos exporters; platform-specific build and packaging
steps stay in the subclasses.

Notes:
- AndroidExporter inherits this base but overrides _load_rooms_from_files,
  _load_objects_from_files and _generate_kivy_game, which legitimately differ
  for the buildozer pipeline.
- iOSExporter is intentionally NOT built on this base: its loaders and build
  flow diverge substantially (Xcode/kivy-ios), so forcing it onto a shared
  template would risk behaviour changes for no real dedup gain.
"""

import json
from pathlib import Path
from PySide6.QtCore import QObject, Signal

from core.logger import get_logger
from utils.project_file_merge import merge_room_file, merge_object_file

logger = get_logger(__name__)


class BaseKivyExporter(QObject):
    """Common functionality shared by the Kivy-runtime platform exporters."""

    progress_update = Signal(int, str)  # progress percentage, status message
    export_complete = Signal(bool, str)  # success, message

    def __init__(self):
        super().__init__()
        self.project_path = None
        self.output_path = None
        self.export_settings = {}
        self.project_data = None

    def _load_project(self, project_path: str, output_path: str, settings: dict) -> Path:
        """Set up exporter state and load project + split asset files.

        Centralises the boilerplate that every platform subclass used to
        repeat verbatim: store the three input paths/settings on ``self``,
        read ``project.json`` as UTF-8, then merge in the external
        ``rooms/`` and ``objects/`` files.

        Returns the resolved ``project_dir`` for any further per-platform
        work (PyInstaller spec paths, etc.).
        """
        self.project_path = Path(project_path)
        self.output_path = Path(output_path)
        self.export_settings = settings

        if self.project_path.is_dir():
            project_file = self.project_path / "project.json"
            project_dir = self.project_path
        else:
            project_file = self.project_path
            project_dir = self.project_path.parent

        with open(project_file, 'r', encoding='utf-8') as f:
            self.project_data = json.load(f)

        # Load room data from external files (instances are stored separately).
        self._load_rooms_from_files(project_dir)
        # Load object data from external files (events are stored separately).
        self._load_objects_from_files(project_dir)

        return project_dir

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
                    instance_count = merge_room_file(room_data, file_room_data)
                    if instance_count is not None:
                        logger.debug(f"Loaded room: {room_name} ({instance_count} instances from file)")

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
                    event_count = merge_object_file(object_data, file_object_data)
                    logger.debug(f"Loaded object: {object_name} ({event_count} events from file)")

                except Exception as e:
                    logger.warning(f"Could not load object file {object_file}: {e}")
            else:
                # No external file - check if events are embedded (legacy format)
                if object_data.get('events'):
                    logger.debug(f"Object {object_name}: using embedded events")
                else:
                    logger.warning(f"Object {object_name}: no events found")

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

    def _require_kivy_dependencies(self, platform_label: str) -> bool:
        """Verify PyInstaller + Kivy + Pillow are available.

        On the first missing dependency, emits the standard failure message
        (parameterised by ``platform_label`` such as ``"Linux exporter"``)
        via ``export_complete`` and returns ``False``; returns ``True`` only
        when all three are present. Single-sourced from the previously
        verbatim-duplicated dependency-check blocks in the exe/linux/macos
        exporters' ``export_project`` — message text and the
        PyInstaller→Kivy→Pillow order are preserved exactly.
        """
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
                f"The {platform_label} requires Kivy to be installed.\n"
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
                f"The {platform_label} requires Pillow for image handling.\n"
                "Please install it in your virtual environment:\n\n"
                "pip install pillow\n\n"
                "Or install all dependencies:\n"
                "pip install -r requirements.txt"
            )
            return False

        return True

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
