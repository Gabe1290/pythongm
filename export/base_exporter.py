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
