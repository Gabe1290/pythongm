#!/usr/bin/env python3

import json
import os
import shutil
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional, Any
from PySide6.QtCore import QObject, Signal, QTimer

from utils.project_compression import ProjectCompressor
from utils.project_file_merge import merge_room_file, merge_object_file

from core.logger import get_logger
logger = get_logger(__name__)


def _atomic_write_json(path: Path, data: Any, *, sort_keys: bool = False) -> None:
    """Write ``data`` to ``path`` as JSON atomically.

    Writes to a sibling ``<path>.tmp`` first, then ``os.replace`` swaps it
    into place. A crash or power loss mid-write therefore leaves either the
    old file intact or the new file fully written — never a truncated mix.
    """
    tmp_path = path.with_name(path.name + '.tmp')
    try:
        with open(tmp_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False, sort_keys=sort_keys)
            f.flush()
            os.fsync(f.fileno())
        os.replace(tmp_path, path)
    except Exception:
        try:
            tmp_path.unlink()
        except OSError:
            pass
        raise

class ProjectManager(QObject):
    """
    Manages PyGameMaker projects - creation, loading, saving, and metadata
    Compatible with the updated AssetManager interface
    """

    # Signals
    project_loaded = Signal(Path, dict)  # project_path, project_data
    project_saved = Signal()
    project_closed = Signal()
    project_created = Signal(Path, dict)  # project_path, project_data
    status_changed = Signal(str)  # status_message
    dirty_changed = Signal(bool)  # is_dirty

    PROJECT_VERSION = "1.0.0"
    PROJECT_FILE = "project.json"

    DEFAULT_PROJECT_STRUCTURE = {
        "sprites": "Sprite assets",
        "sounds": "Audio assets",
        "backgrounds": "Background images",
        "objects": "Game objects",
        "rooms": "Game rooms/levels",
        "playgrounds": "Aseba playground environments",
        "scripts": "GML scripts",
        "fonts": "Font assets",
        "data": "Data files"
    }

    def __init__(self, asset_manager=None):
        super().__init__()

        # Core state
        self.current_project_path = None
        self.current_project_data = {}
        self.is_dirty_flag = False

        # Asset manager integration
        self.asset_manager = asset_manager
        if self.asset_manager:
            self.asset_manager.asset_imported.connect(self.on_asset_changed)
            self.asset_manager.asset_deleted.connect(self.on_asset_changed)
            self.asset_manager.asset_updated.connect(self.on_asset_changed)

        # Zip-related attributes
        self._original_zip_path = None
        self._temp_extraction_dir = None
        self._auto_save_as_zip = False  # NEW: Auto-save as zip preference

        # Auto-save timer (parented to self for deterministic cleanup)
        self.auto_save_timer = QTimer(self)
        self.auto_save_timer.timeout.connect(self.auto_save)
        self.auto_save_enabled = True
        self.auto_save_interval = 30000  # 30 seconds

    def create_project(self, project_name: str, location: str, template: str = "empty") -> bool:
        """
        Create a new project (compatibility wrapper for IDE)

        Args:
            project_name: Name of the project
            location: Parent directory where project folder will be created
            template: Project template id ("empty", "gameover", ...) or display name

        Returns:
            bool: True if successful, False otherwise
        """
        location_path = Path(location)
        return self.create_new_project(project_name, location_path, template)

    def set_asset_manager(self, asset_manager):
        """Set or update the asset manager reference"""
        if self.asset_manager:
            # Disconnect old signals safely
            try:
                self.asset_manager.asset_imported.disconnect(self.on_asset_changed)
                self.asset_manager.asset_deleted.disconnect(self.on_asset_changed)
                self.asset_manager.asset_updated.disconnect(self.on_asset_changed)
            except (RuntimeError, TypeError):
                pass  # Ignore if signals weren't connected

        self.asset_manager = asset_manager

        if self.asset_manager:
            # Connect new signals
            self.asset_manager.asset_imported.connect(self.on_asset_changed)
            self.asset_manager.asset_deleted.connect(self.on_asset_changed)
            self.asset_manager.asset_updated.connect(self.on_asset_changed)

            # Update asset manager with current project if one is loaded
            if self.current_project_path:
                self.asset_manager.set_project_directory(self.current_project_path)

    def create_new_project(self, project_name: str, location: Path, template: str = "empty") -> bool:
        """Create a new project at the specified location"""
        try:
            project_path = Path(location) / project_name

            # Check if directory already exists
            if project_path.exists():
                self.status_changed.emit(f"Directory {project_path} already exists")
                return False

            # Create project directory
            project_path.mkdir(parents=True, exist_ok=True)

            # Create asset directories
            self._create_project_structure(project_path)

            # Create default project data
            project_data = self._create_default_project_data(project_name)
            self._apply_project_template(project_data, template)

            # Save project file
            project_file = project_path / self.PROJECT_FILE
            _atomic_write_json(project_file, project_data)

            # Update asset manager with new project location
            if self.asset_manager:
                self.asset_manager.set_project_directory(project_path)
                self.asset_manager.load_assets_from_project_data(project_data)

            # Update internal state
            self.current_project_path = project_path
            self.current_project_data = project_data
            self.is_dirty_flag = False

            # Start auto-save
            if self.auto_save_enabled:
                self.auto_save_timer.start(self.auto_save_interval)

            self.project_created.emit(project_path, project_data)
            self.status_changed.emit(f"Created project: {project_name}")

            return True

        except Exception as e:
            self.status_changed.emit(f"Failed to create project: {str(e)}")
            return False

    def open_project(self, project_path: Path) -> bool:
        """Open an existing project"""
        return self.load_project(project_path)

    def load_project(self, project_path: Path) -> bool:
        """Load an existing project (compatibility method)"""
        try:
            project_path = Path(project_path)

            # Check if project file exists
            project_file = project_path / self.PROJECT_FILE
            if not project_file.exists():
                self.status_changed.emit(f"Project file not found: {project_file}")
                return False

            # Load project data with object_pairs_hook to preserve order
            with open(project_file, 'r', encoding='utf-8') as f:
                from collections import OrderedDict
                project_data = json.load(f, object_pairs_hook=OrderedDict)

            # Load asset data from separate files if they exist
            self._load_rooms_from_files(project_path, project_data)
            self._load_objects_from_files(project_path, project_data)
            self._load_sprites_from_files(project_path, project_data)
            self._load_playgrounds_from_files(project_path, project_data)

            # Validate project data
            if not self._validate_project_data(project_data):
                self.status_changed.emit("Invalid project file format")
                return False

            # Update asset manager with project location FIRST
            if self.asset_manager:
                self.asset_manager.set_project_directory(project_path)
                self.asset_manager.load_assets_from_project_data(project_data)

            # Update internal state
            self.current_project_path = project_path
            self.current_project_data = project_data
            self.is_dirty_flag = False

            # Start auto-save
            if self.auto_save_enabled:
                self.auto_save_timer.start(self.auto_save_interval)

            # Emit signal with project data
            self.project_loaded.emit(project_path, project_data)
            self.status_changed.emit(f"Opened project: {project_path.name}")

            return True

        except Exception as e:
            self.status_changed.emit(f"Failed to open project: {str(e)}")
            return False

    def _load_rooms_from_files(self, project_path: Path, project_data: dict) -> None:
        """Load room instance data from separate files in rooms/ directory"""
        rooms_dir = project_path / "rooms"

        if not rooms_dir.exists():
            logger.debug("No rooms/ directory found, using embedded room data")
            return

        rooms_data = project_data.get('assets', {}).get('rooms', {})

        for room_name, room_data in list(rooms_data.items()):
            room_file = rooms_dir / f"{room_name}.json"

            # Handle case where room_data is a string path reference
            if isinstance(room_data, str):
                # Convert string reference to dict that can be populated
                room_data = {"name": room_name, "asset_type": "room"}
                rooms_data[room_name] = room_data

            if room_file.exists():
                try:
                    with open(room_file, 'r', encoding='utf-8') as f:
                        from collections import OrderedDict
                        file_room_data = json.load(f, object_pairs_hook=OrderedDict)

                    # Merge file data into room data (file takes precedence for instances)
                    instance_count = merge_room_file(room_data, file_room_data)
                    if instance_count is not None:
                        logger.debug(f"📂 Loaded room: {room_name} ({instance_count} instances from file)")

                    # Clean up external file marker
                    if '_external_file' in room_data:
                        del room_data['_external_file']

                except Exception as e:
                    logger.warning(f"⚠️ Failed to load room file {room_file}: {e}")
            else:
                # No external file - check if instances are embedded (legacy format)
                if room_data.get('instances'):
                    logger.debug(f"📂 Room {room_name}: using embedded instances ({len(room_data['instances'])} instances)")
                else:
                    logger.warning(f"⚠️ Room {room_name}: no instances found")

    def _load_objects_from_files(self, project_path: Path, project_data: dict) -> None:
        """Load object data from separate files in objects/ directory"""
        objects_dir = project_path / "objects"

        if not objects_dir.exists():
            logger.debug("No objects/ directory found, using embedded object data")
            return

        objects_data = project_data.get('assets', {}).get('objects', {})

        for object_name, object_data in list(objects_data.items()):
            object_file = objects_dir / f"{object_name}.json"

            # Handle case where object_data is a string path reference
            if isinstance(object_data, str):
                # Convert string reference to dict that can be populated
                object_data = {"name": object_name, "asset_type": "object"}
                objects_data[object_name] = object_data

            if object_file.exists():
                try:
                    with open(object_file, 'r', encoding='utf-8') as f:
                        from collections import OrderedDict
                        file_object_data = json.load(f, object_pairs_hook=OrderedDict)

                    # Merge file data into object data (file takes precedence)
                    event_count = merge_object_file(object_data, file_object_data)
                    logger.debug(f"📂 Loaded object: {object_name} ({event_count} events from file)")

                    # Clean up external file marker
                    if '_external_file' in object_data:
                        del object_data['_external_file']

                except Exception as e:
                    logger.warning(f"⚠️ Failed to load object file {object_file}: {e}")
            else:
                # No external file - use embedded data
                if object_data.get('events'):
                    logger.debug(f"📂 Object {object_name}: using embedded events")

    def _load_sprites_from_files(self, project_path: Path, project_data: dict) -> None:
        """Load sprite data from separate files in sprites/ directory"""
        sprites_dir = project_path / "sprites"

        if not sprites_dir.exists():
            logger.debug("No sprites/ directory found, using embedded sprite data")
            return

        sprites_data = project_data.get('assets', {}).get('sprites', {})

        for sprite_name, sprite_data in sprites_data.items():
            sprite_file = sprites_dir / f"{sprite_name}.json"

            if sprite_file.exists():
                try:
                    with open(sprite_file, 'r', encoding='utf-8') as f:
                        from collections import OrderedDict
                        file_sprite_data = json.load(f, object_pairs_hook=OrderedDict)

                    # Merge file data into sprite data (file takes precedence)
                    for key in ['frames', 'width', 'height', 'origin_x', 'origin_y',
                               'collision_mask', 'bbox_left', 'bbox_right', 'bbox_top',
                               'bbox_bottom', 'imported', 'created', 'modified', 'file_path']:
                        if key in file_sprite_data:
                            sprite_data[key] = file_sprite_data[key]

                    # Handle frames as either a list or an integer count
                    frames_data = file_sprite_data.get('frames', [])
                    if isinstance(frames_data, int):
                        frame_count = frames_data
                    elif isinstance(frames_data, list):
                        frame_count = len(frames_data)
                    else:
                        frame_count = 1
                    logger.debug(f"📂 Loaded sprite: {sprite_name} ({frame_count} frames from file)")

                    # Clean up external file marker
                    if '_external_file' in sprite_data:
                        del sprite_data['_external_file']

                except Exception as e:
                    logger.warning(f"⚠️ Failed to load sprite file {sprite_file}: {e}")

    def save_project(self, project_path: Optional[Path] = None) -> bool:
        """
        Save the current project
        If auto-save-as-zip is enabled and project was loaded from zip,
        saves directly back to the zip file
        """
        if not self.current_project_path and not project_path:
            self.status_changed.emit("No project to save")
            return False

        try:
            # Check if we should save as zip
            if self._auto_save_as_zip and self._original_zip_path and not project_path:
                logger.info(f"💾 Auto-saving to zip: {self._original_zip_path}")
                return self._save_to_zip()
            else:
                # Regular folder save
                return self._save_to_folder(project_path)

        except Exception as e:
            logger.error(f"Save failed: {e}")
            import traceback
            traceback.print_exc()
            self.status_changed.emit(f"Failed to save project: {str(e)}")
            return False

    def _save_to_folder(self, project_path: Optional[Path] = None) -> bool:
        """Save project to folder"""
        try:
            save_path = Path(project_path) if project_path else self.current_project_path
            project_file = save_path / self.PROJECT_FILE

            # Defensive guard: refuse to write into the bundled samples/
            # folder. PyGameMakerIDE.load_project should have promoted
            # the project to a working copy before reaching us, but this
            # guard catches future regressions (e.g. someone wiring a
            # save through a different code path) before the IDE
            # overwrites the bundled sample files in the repo.
            try:
                save_path_resolved = save_path.resolve()
                # samples/ lives at <repo>/samples/ — two levels up from
                # this file (core/project_manager.py).
                samples_dir = (Path(__file__).resolve().parent.parent / 'samples').resolve()
                if save_path_resolved.is_relative_to(samples_dir):
                    logger.error(
                        f"Refusing to save into bundled samples/ folder: "
                        f"{save_path_resolved}. The IDE should have promoted "
                        f"this project to a working copy before saving."
                    )
                    return False
            except (ValueError, OSError):
                pass  # path comparison failed; fall through and try the save

            logger.debug(f"Saving project to {project_file}")

            # Update project metadata
            self.current_project_data["modified"] = datetime.now().isoformat()

            # Get latest asset data from asset manager (preserves order)
            if self.asset_manager:
                self.asset_manager.save_assets_to_project_data(self.current_project_data)

            # Save rooms to separate files
            self._save_rooms_to_files(save_path)

            # Save objects to separate files (if objects/ directory exists)
            self._save_objects_to_files(save_path)

            # Save sprites to separate files (if sprites/ directory exists)
            self._save_sprites_to_files(save_path)

            # Save playgrounds to separate files
            self._save_playgrounds_to_files(save_path)

            # Create a copy of project data without room instance data for main file
            # (room metadata stays in project.json, instance data goes to room files)
            project_data_for_save = self._prepare_project_data_for_save()

            # Save main project file (without room instance data)
            _atomic_write_json(project_file, project_data_for_save)

            logger.info(f"💾 Saved project: {project_file}")

            # Update state
            self.is_dirty_flag = False
            if project_path:
                self.current_project_path = save_path

            self.project_saved.emit()
            self.dirty_changed.emit(False)
            self.status_changed.emit(f"Saved project: {save_path.name}")

            return True

        except Exception as e:
            logger.error(f"Folder save failed: {e}")
            import traceback
            traceback.print_exc()
            return False

    def _save_rooms_to_files(self, project_path: Path) -> None:
        """Save each room's instance data to a separate file in rooms/ directory

        IMPORTANT: If a room file already exists with instances and current_project_data
        has empty instances, preserve the existing file's instances to avoid data loss.
        """
        rooms_dir = project_path / "rooms"
        rooms_dir.mkdir(exist_ok=True)

        rooms_data = self.current_project_data.get('assets', {}).get('rooms', {})

        for room_name, room_data in rooms_data.items():
            room_file = rooms_dir / f"{room_name}.json"

            # Check if we're about to overwrite a file with good data
            instances_to_save = room_data.get('instances', [])

            if not instances_to_save and room_file.exists():
                # Current data has no instances, but file exists - preserve file instances
                try:
                    with open(room_file, 'r', encoding='utf-8') as f:
                        existing_data = json.load(f)
                    existing_instances = existing_data.get('instances', [])
                    if existing_instances:
                        # Merge: use current metadata but preserve existing instances
                        logger.warning(f"⚠️ Preserving {len(existing_instances)} instances from existing file for {room_name}")
                        room_data_to_save = dict(room_data)
                        room_data_to_save['instances'] = existing_instances
                        _atomic_write_json(room_file, room_data_to_save)
                        logger.debug(f"💾 Saved room: {room_name} ({len(existing_instances)} instances preserved)")
                        continue
                except Exception as e:
                    logger.warning(f"⚠️ Could not read existing room file {room_file}: {e}")

            # Save full room data including instances
            _atomic_write_json(room_file, room_data)

            logger.debug(f"💾 Saved room: {room_name} ({len(instances_to_save)} instances)")

    def _save_objects_to_files(self, project_path: Path) -> None:
        """Save each object's data to a separate file in objects/ directory

        Only saves if objects/ directory already exists (to maintain compatibility
        with projects that don't use external object files).
        """
        objects_dir = project_path / "objects"

        # Only save to external files if the directory already exists
        # This maintains backward compatibility with projects that don't use this feature
        if not objects_dir.exists():
            logger.debug(f"💾 DEBUG _save_objects_to_files: objects_dir does not exist: {objects_dir}")
            return

        objects_data = self.current_project_data.get('assets', {}).get('objects', {})
        logger.debug(f"💾 DEBUG _save_objects_to_files: Found {len(objects_data)} objects to save")

        for object_name, object_data in objects_data.items():
            object_file = objects_dir / f"{object_name}.json"

            # Save full object data including events
            _atomic_write_json(object_file, object_data)

            event_count = len(object_data.get('events', {}))
            logger.debug(f"💾 Saved object: {object_name} ({event_count} events)")

    def _save_sprites_to_files(self, project_path: Path) -> None:
        """Save each sprite's metadata to a separate file in sprites/ directory

        Only saves if sprites/ directory already exists (to maintain compatibility
        with projects that don't use external sprite files).
        """
        sprites_dir = project_path / "sprites"

        if not sprites_dir.exists():
            logger.debug(f"💾 DEBUG _save_sprites_to_files: sprites_dir does not exist: {sprites_dir}")
            return

        sprites_data = self.current_project_data.get('assets', {}).get('sprites', {})
        logger.debug(f"💾 DEBUG _save_sprites_to_files: Found {len(sprites_data)} sprites to save")

        for sprite_name, sprite_data in sprites_data.items():
            sprite_file = sprites_dir / f"{sprite_name}.json"

            _atomic_write_json(sprite_file, sprite_data)

            logger.debug(f"💾 Saved sprite: {sprite_name}")

    def _load_playgrounds_from_files(self, project_path: Path, project_data: dict) -> None:
        """Load playground data from separate files in playgrounds/ directory"""
        playgrounds_dir = project_path / "playgrounds"

        if not playgrounds_dir.exists():
            return

        playgrounds_data = project_data.get('assets', {}).get('playgrounds', {})

        for pg_name, pg_data in list(playgrounds_data.items()):
            pg_file = playgrounds_dir / f"{pg_name}.json"

            if isinstance(pg_data, str):
                pg_data = {"name": pg_name, "asset_type": "playground"}
                playgrounds_data[pg_name] = pg_data

            if pg_file.exists():
                try:
                    with open(pg_file, 'r', encoding='utf-8') as f:
                        file_data = json.load(f)
                    # Merge file data into playground data
                    for key in ['arena', 'colors', 'walls', 'robots']:
                        if key in file_data:
                            pg_data[key] = file_data[key]
                    if '_external_file' in pg_data:
                        del pg_data['_external_file']
                    logger.debug(f"Loaded playground: {pg_name}")
                except Exception as e:
                    logger.warning(f"Failed to load playground file {pg_file}: {e}")

    def _save_playgrounds_to_files(self, project_path: Path) -> None:
        """Save each playground's data to a separate file in playgrounds/ directory"""
        playgrounds_dir = project_path / "playgrounds"
        playgrounds_data = self.current_project_data.get('assets', {}).get('playgrounds', {})

        if not playgrounds_data:
            return

        playgrounds_dir.mkdir(exist_ok=True)

        for pg_name, pg_data in playgrounds_data.items():
            pg_file = playgrounds_dir / f"{pg_name}.json"
            _atomic_write_json(pg_file, pg_data)
            logger.debug(f"Saved playground: {pg_name}")

    def _prepare_project_data_for_save(self) -> dict:
        """Prepare project data for saving - rooms store only metadata, not instances"""
        from copy import deepcopy

        # Deep copy to avoid modifying the live data
        data = deepcopy(self.current_project_data)

        # For rooms, only keep metadata (not instances) in main project.json
        if 'assets' in data and 'rooms' in data['assets']:
            rooms = data['assets']['rooms']
            for room_name, room_data in rooms.items():
                # Keep room metadata but remove instances (they're in separate files)
                if 'instances' in room_data:
                    # Store instance count for reference
                    room_data['instance_count'] = len(room_data['instances'])
                    room_data['instances'] = []  # Clear instances from main file
                    room_data['_external_file'] = f"rooms/{room_name}.json"

        # For playgrounds, strip detail data (walls/robots go to separate files)
        if 'assets' in data and 'playgrounds' in data['assets']:
            playgrounds = data['assets']['playgrounds']
            for pg_name, pg_data in playgrounds.items():
                pg_data.pop('walls', None)
                pg_data.pop('robots', None)
                pg_data.pop('colors', None)
                pg_data['_external_file'] = f"playgrounds/{pg_name}.json"

        return data

    def _save_to_zip(self) -> bool:
        """Save project directly to zip file"""
        try:
            if not self._original_zip_path:
                logger.warning("No original zip path")
                return False

            # First save to the temporary extraction directory
            if not self._save_to_folder():
                return False

            # Then re-compress the temp directory back to the original zip
            # Create backup of original zip
            backup_path = self._original_zip_path.with_suffix('.zip.bak')
            shutil.copy2(self._original_zip_path, backup_path)

            # Compress temp directory to original zip location
            if ProjectCompressor.compress_project(self._temp_extraction_dir, self._original_zip_path):
                # Remove backup on success
                backup_path.unlink()
                logger.info(f"✅ Project saved to zip: {self._original_zip_path}")
                return True
            else:
                # Restore backup on failure
                backup_path.replace(self._original_zip_path)
                logger.error("❌ Failed to save to zip, backup restored")
                return False

        except Exception as e:
            logger.error(f"Error saving to zip: {e}")
            import traceback
            traceback.print_exc()
            return False

    def close_project(self) -> bool:
        """Close the current project"""
        try:
            # Stop auto-save
            self.auto_save_timer.stop()

            # Cleanup temp files from zip extraction
            if self._temp_extraction_dir and self._temp_extraction_dir.exists():
                logger.info(f"🧹 Cleaning up temp extraction: {self._temp_extraction_dir}")
                shutil.rmtree(self._temp_extraction_dir, ignore_errors=True)

            self._original_zip_path = None
            self._temp_extraction_dir = None
            self._auto_save_as_zip = False

            # Clear asset manager
            if self.asset_manager:
                self.asset_manager.set_project_directory(None)

            # Clear internal state
            self.current_project_path = None
            self.current_project_data = {}
            self.is_dirty_flag = False

            self.project_closed.emit()
            self.dirty_changed.emit(False)
            self.status_changed.emit("Project closed")

            return True

        except Exception as e:
            self.status_changed.emit(f"Failed to close project: {str(e)}")
            return False

    def get_current_project_data(self) -> Dict[str, Any]:
        """Get the current project data"""
        return self.current_project_data.copy()

    def get_project_info(self) -> Dict[str, Any]:
        """Get information about the current project"""
        if not self.current_project_path:
            return {}

        info = {
            "name": self.current_project_data.get("name", "Unknown"),
            "path": str(self.current_project_path),
            "version": self.current_project_data.get("version", "Unknown"),
            "created": self.current_project_data.get("created", "Unknown"),
            "modified": self.current_project_data.get("modified", "Unknown"),
            "is_dirty": self.is_dirty_flag
        }

        # Add asset counts
        assets = self.current_project_data.get("assets", {})
        for asset_type in self.DEFAULT_PROJECT_STRUCTURE.keys():
            info[f"{asset_type}_count"] = len(assets.get(asset_type, {}))

        return info

    def mark_dirty(self):
        """Mark the project as having unsaved changes"""
        if not self.is_dirty_flag:
            self.is_dirty_flag = True
            self.dirty_changed.emit(True)

    def is_dirty(self) -> bool:
        """Check if the project has unsaved changes (compatibility method)"""
        return self.is_dirty_flag


    def save_project_as(self, new_path: Path) -> bool:
        """Save project to a new location"""
        try:
            # If path doesn't exist, create it
            new_path.mkdir(parents=True, exist_ok=True)

            # Copy all files to new location
            if self.current_project_path:
                for item in self.current_project_path.glob('**/*'):
                    if item.is_file():
                        rel_path = item.relative_to(self.current_project_path)
                        dest_path = new_path / rel_path
                        dest_path.parent.mkdir(parents=True, exist_ok=True)
                        shutil.copy2(item, dest_path)

            # Update current path
            old_path = self.current_project_path
            self.current_project_path = new_path

            # Save project data to new location
            if self._save_to_folder():
                # Update asset manager
                if self.asset_manager:
                    self.asset_manager.set_project_directory(new_path)

                self.status_changed.emit(f"Project saved as: {new_path.name}")
                return True
            else:
                # Restore old path on failure
                self.current_project_path = old_path
                return False

        except Exception as e:
            logger.error(f"Error in save_project_as: {e}")
            import traceback
            traceback.print_exc()
            return False

    def auto_save(self):
        """Perform automatic save if enabled and project is dirty"""
        if self.is_dirty_flag and self.current_project_path:
            self.save_project()

    def set_auto_save(self, enabled: bool, interval: int = 30000):
        """Enable/disable auto-save with specified interval"""
        self.auto_save_enabled = enabled
        self.auto_save_interval = interval

        if enabled and self.current_project_path:
            self.auto_save_timer.start(interval)
        else:
            self.auto_save_timer.stop()

    def migrate_to_external_files(self) -> bool:
        """Migrate project to use external files for objects and rooms.

        Creates objects/ and rooms/ directories if they don't exist,
        then saves all object and room data to separate JSON files.
        This enables the modular project structure.

        Returns:
            True if migration was successful, False otherwise.
        """
        if not self.current_project_path:
            logger.error("No project loaded to migrate")
            return False

        try:
            project_path = self.current_project_path

            # Create objects/ directory if it doesn't exist
            objects_dir = project_path / "objects"
            if not objects_dir.exists():
                objects_dir.mkdir(parents=True, exist_ok=True)
                logger.info(f"📁 Created objects directory: {objects_dir}")

            # Create rooms/ directory if it doesn't exist
            rooms_dir = project_path / "rooms"
            if not rooms_dir.exists():
                rooms_dir.mkdir(parents=True, exist_ok=True)
                logger.info(f"📁 Created rooms directory: {rooms_dir}")

            # Save objects to external files
            objects_data = self.current_project_data.get('assets', {}).get('objects', {})
            for object_name, object_data in objects_data.items():
                object_file = objects_dir / f"{object_name}.json"
                _atomic_write_json(object_file, object_data)
                event_count = len(object_data.get('events', {}))
                logger.info(f"💾 Migrated object: {object_name} ({event_count} events)")

            # Save rooms to external files
            rooms_data = self.current_project_data.get('assets', {}).get('rooms', {})
            for room_name, room_data in rooms_data.items():
                room_file = rooms_dir / f"{room_name}.json"
                _atomic_write_json(room_file, room_data)
                instance_count = len(room_data.get('instances', []))
                logger.info(f"💾 Migrated room: {room_name} ({instance_count} instances)")

            # Now save the project (which will use the external files)
            self.save_project()

            logger.info("✅ Project migrated to external files structure")
            self.status_changed.emit("Project migrated to modular structure")
            return True

        except Exception as e:
            logger.error(f"Error migrating project: {e}")
            import traceback
            traceback.print_exc()
            return False

    def on_asset_changed(self, *args):
        """Handle asset changes from asset manager"""
        self.mark_dirty()

    def update_asset(self, asset_type: str, asset_name: str, asset_data: Dict[str, Any]) -> bool:
        """Update an asset's data with proper type handling"""
        try:
            if not self.asset_manager:
                logger.error("update_asset: no asset_manager available")
                self.status_changed.emit("No asset manager available")
                return False
            if not hasattr(self.asset_manager, 'assets_cache'):
                logger.error("update_asset: asset_manager has no assets_cache")
                self.status_changed.emit("Asset manager not properly initialized")
                return False

            # Normalize asset_type to plural for storage; asset_data['asset_type']
            # stays singular. _KNOWN_SINGULAR covers the regular cases; anything
            # outside that map gets a naive '+s' suffix.
            asset_type_plural = asset_type
            if not asset_type_plural.endswith('s'):
                asset_type_plural = asset_type_plural + 's'

            asset_type_singular = asset_type_plural[:-1] if asset_type_plural.endswith('s') else asset_type_plural
            plural_to_singular_map = {
                'sprites': 'sprite', 'sounds': 'sound', 'backgrounds': 'background',
                'objects': 'object', 'rooms': 'room', 'playgrounds': 'playground',
                'scripts': 'script', 'fonts': 'font',
                'enemies': 'enemy', 'entities': 'entity',
            }
            if asset_type_plural in plural_to_singular_map:
                asset_type_singular = plural_to_singular_map[asset_type_plural]

            existing_asset = self.asset_manager.get_asset(asset_type_plural, asset_name)

            if existing_asset:
                # Preserve important fields from existing asset
                preserved_fields = ['created', 'file_path', 'imported', 'file_hash']
                for field in preserved_fields:
                    if field in existing_asset and field not in asset_data:
                        asset_data[field] = existing_asset[field]

                # Update existing asset with new data
                existing_asset.update(asset_data)

                # Ensure correct asset_type field (singular)
                existing_asset['asset_type'] = asset_type_singular
                existing_asset['name'] = asset_name
                existing_asset['modified'] = datetime.now().isoformat()

                # Update the cache directly
                if asset_type_plural not in self.asset_manager.assets_cache:
                    self.asset_manager.assets_cache[asset_type_plural] = {}

                self.asset_manager.assets_cache[asset_type_plural][asset_name] = existing_asset

                # Emit update signal
                self.asset_manager.asset_updated.emit(asset_type_plural, asset_name, existing_asset)

            else:
                # Asset doesn't exist, create new one
                logger.debug(f"update_asset: creating new '{asset_name}' in '{asset_type_plural}'")

                # Create complete asset data
                new_asset_data = {
                    "name": asset_name,
                    "asset_type": asset_type_singular,  # Use singular form
                    "created": datetime.now().isoformat(),
                    "modified": datetime.now().isoformat(),
                    "imported": asset_data.get('imported', True),
                    "file_path": asset_data.get('file_path', ''),
                }

                # Add type-specific defaults
                if asset_type_singular == "object":
                    new_asset_data.update({
                        "sprite": "",
                        "visible": True,
                        "solid": False,
                        "persistent": False,
                        "depth": 0,
                        "events": {}
                    })
                elif asset_type_singular == "room":
                    new_asset_data.update({
                        "width": 1024,
                        "height": 768,
                        "background_color": "#87CEEB",
                        "background_image": "",
                        "tile_horizontal": False,
                        "tile_vertical": False,
                        "bg_stretch": True,
                        "instances": [],
                        "tiles": [],
                        "backgrounds": [],
                        "views_enabled": False
                    })
                elif asset_type_singular == "sprite":
                    new_asset_data.update({
                        "width": 32,
                        "height": 32,
                        "origin_x": 16,
                        "origin_y": 16,
                        "frames": 1,
                        "speed": 1.0
                    })
                elif asset_type_singular == "script":
                    new_asset_data.update({
                        "code": "// Script code here\n",
                        "language": "gml"
                    })
                elif asset_type_singular == "font":
                    new_asset_data.update({
                        "font_name": "Arial",
                        "size": 12,
                        "bold": False,
                        "italic": False
                    })

                # Apply provided asset data (overrides defaults)
                new_asset_data.update(asset_data)

                # Ensure asset_type is singular
                new_asset_data['asset_type'] = asset_type_singular

                # Initialize cache structure if needed
                if not self.asset_manager.assets_cache:
                    self.asset_manager.assets_cache = {}
                if asset_type_plural not in self.asset_manager.assets_cache:
                    self.asset_manager.assets_cache[asset_type_plural] = {}

                # Add to cache
                self.asset_manager.assets_cache[asset_type_plural][asset_name] = new_asset_data

                # Emit creation signal
                self.asset_manager.asset_imported.emit(asset_type_plural, asset_name, new_asset_data)

            # Mark project as dirty
            self.mark_dirty()
            self.status_changed.emit(f"Updated {asset_name}")

            # Verify the update landed in the cache. Failure here is rare
            # but means the caller's later save will silently drop the asset,
            # so it's worth keeping the check + the loud error.
            if not self.asset_manager.get_asset(asset_type_plural, asset_name):
                logger.error(
                    f"update_asset: post-write verification failed — "
                    f"'{asset_name}' not found in '{asset_type_plural}' cache"
                )

            return True

        except Exception as e:
            logger.error(f"update_asset: exception {type(e).__name__}: {e}")
            import traceback
            traceback.print_exc()
            self.status_changed.emit(f"Failed to update asset {asset_name}: {str(e)}")
            return False

    def create_asset(self, asset_name: str, asset_type: str, **kwargs) -> bool:
        """Create a new asset"""
        try:
            if not self.asset_manager:
                return False

            result = self.asset_manager.create_asset(asset_name, asset_type, **kwargs)
            if result:
                self.mark_dirty()
                return True
            return False

        except Exception as e:
            self.status_changed.emit(f"Failed to create asset {asset_name}: {str(e)}")
            return False

    def delete_asset(self, asset_type: str, asset_name: str) -> bool:
        """Delete an asset"""
        try:
            if not self.asset_manager:
                return False

            result = self.asset_manager.delete_asset(asset_type, asset_name)
            if result:
                self.mark_dirty()
                return True
            return False

        except Exception as e:
            self.status_changed.emit(f"Failed to delete asset {asset_name}: {str(e)}")
            return False

    def rename_asset(self, asset_type: str, old_name: str, new_name: str) -> bool:
        """Rename an asset and update all references"""
        try:
            if not self.asset_manager:
                return False

            result = self.asset_manager.rename_asset(asset_type, old_name, new_name)
            if result:
                self.mark_dirty()
                # Auto-save to persist the rename and all updated references
                self.save_project()
                return True
            return False

        except Exception as e:
            self.status_changed.emit(f"Failed to rename asset {old_name}: {str(e)}")
            return False

    def get_asset(self, asset_type: str, asset_name: str) -> Optional[Dict[str, Any]]:
        """Get asset data"""
        if not self.asset_manager:
            return None
        return self.asset_manager.get_asset(asset_type, asset_name)

    def get_assets_by_type(self, asset_type: str) -> Dict[str, Dict[str, Any]]:
        """Get all assets of a specific type"""
        if not self.asset_manager:
            return {}
        return self.asset_manager.get_assets_by_type(asset_type)

    def import_asset(self, file_path: Path, asset_type: str, asset_name: Optional[str] = None) -> Optional[Dict[str, Any]]:
        """Import an asset from file"""
        try:
            if not self.asset_manager:
                return None

            # Import the asset (this adds it to asset_manager cache)
            result = self.asset_manager.import_asset(file_path, asset_type, asset_name)

            if result:
                # Mark project as modified
                self.mark_dirty()

                # CRITICAL FIX: Also add to project data immediately
                # This ensures the asset exists in both cache AND project data
                if 'assets' not in self.current_project_data:
                    self.current_project_data['assets'] = {}

                if asset_type not in self.current_project_data['assets']:
                    self.current_project_data['assets'][asset_type] = {}

                # Add the imported asset to project data
                self.current_project_data['assets'][asset_type][result['name']] = result

                # Optional: Auto-save to prevent any inconsistency
                # Comment this out if you prefer manual saving
                self.save_project()

                return result

            return None

        except Exception as e:
            self.status_changed.emit(f"Failed to import asset: {str(e)}")
            import traceback
            traceback.print_exc()
            return None

    def _create_project_structure(self, project_path: Path):
        """Create the default directory structure for a new project"""
        for asset_type in self.DEFAULT_PROJECT_STRUCTURE.keys():
            (project_path / asset_type).mkdir(exist_ok=True)

        # Create thumbnails directory
        (project_path / "thumbnails").mkdir(exist_ok=True)

    def _get_default_blockly_preset(self) -> str:
        """Get the default blockly preset based on the current IDE edition"""
        try:
            from config.editions import get_current_edition
            return get_current_edition()["default_blockly_preset"]
        except Exception:
            return "beginner"

    def _create_default_project_data(self, project_name: str) -> Dict[str, Any]:
        """Create default project data structure"""
        now = datetime.now().isoformat()

        project_data = {
            "name": project_name,
            "version": self.PROJECT_VERSION,
            "created": now,
            "modified": now,
            "settings": {
                "window_title": project_name,
                "window_width": 1024,
                "window_height": 768,
                "room_speed": 60,
                "fullscreen": False,
                "blockly_preset": self._get_default_blockly_preset()
            },
            "assets": {}
        }

        # Initialize empty asset categories
        for asset_type in self.DEFAULT_PROJECT_STRUCTURE.keys():
            project_data["assets"][asset_type] = {}

        # Create default room
        project_data["assets"]["rooms"]["room0"] = {
            "name": "room0",
            "asset_type": "room",
            "width": 1024,
            "height": 768,
            "background_color": "#000000",
            "instances": [],
            "creation_code": "",
            "created": now,
            "modified": now,
            "imported": True  # Room is created within IDE, so it's immediately available
        }

        return project_data

    # Map dialog display strings -> template directory names under resources/templates/
    TEMPLATE_ALIASES = {
        "empty": "empty",
        "empty project": "empty",
        "with game over screen": "gameover",
        "game over": "gameover",
        "gameover": "gameover",
    }

    def _resolve_template_id(self, template: str) -> str:
        if not template:
            return "empty"
        return self.TEMPLATE_ALIASES.get(template.strip().lower(), template.strip().lower())

    def _apply_project_template(self, project_data: Dict[str, Any], template: str) -> None:
        """Merge a starter-content template (objects + rooms) into a fresh project."""
        template_id = self._resolve_template_id(template)
        if template_id == "empty":
            return

        import sys
        if getattr(sys, 'frozen', False) and hasattr(sys, '_MEIPASS'):
            base = Path(sys._MEIPASS)
        else:
            base = Path(__file__).parent.parent
        snippet_path = base / 'templates' / template_id / 'snippet.json'

        if not snippet_path.exists():
            logger.warning(f"Template '{template_id}' not found at {snippet_path}; using empty project")
            return

        try:
            with open(snippet_path, 'r', encoding='utf-8') as f:
                snippet = json.load(f)
        except Exception as e:
            logger.warning(f"Failed to load template '{template_id}': {e}")
            return

        now = datetime.now().isoformat()
        assets = project_data["assets"]

        for obj_name, obj_data in snippet.get("objects", {}).items():
            obj_data.setdefault("created", now)
            obj_data.setdefault("modified", now)
            assets["objects"][obj_name] = obj_data

        for room_name, room_data in snippet.get("rooms", {}).items():
            room_data.setdefault("created", now)
            room_data.setdefault("modified", now)
            assets["rooms"][room_name] = room_data

        logger.info(f"Applied project template: {template_id}")

    def _validate_project_data(self, project_data: Dict[str, Any]) -> bool:
        """Validate project data structure"""
        required_keys = ["name", "version", "assets"]

        for key in required_keys:
            if key not in project_data:
                return False

        # Ensure assets is a dictionary
        if not isinstance(project_data["assets"], dict):
            return False

        return True

    # Properties
    @property
    def has_project(self) -> bool:
        """Check if a project is currently loaded"""
        return self.current_project_path is not None

    @property
    def project_name(self) -> str:
        """Get the current project name"""
        return self.current_project_data.get("name", "") if self.has_project else ""

    @property
    def project_path(self) -> Optional[Path]:
        """Get the current project path"""
        return self.current_project_path

    def export_project_as_zip(self, zip_path: Path) -> bool:
        """
        Export current project as a .zip file

        Args:
            zip_path: Path to output .zip file

        Returns:
            True if successful, False otherwise
        """
        if not self.current_project_path:
            logger.warning("No project loaded")
            return False

        # Save project first
        if not self.save_project():
            logger.error("Failed to save project before export")
            return False

        # Compress project
        return ProjectCompressor.compress_project(
            self.current_project_path,
            zip_path
        )

    def load_project_from_zip(self, zip_path: Path, work_in_place: bool = True) -> bool:
        """
        Load a project from a .zip file

        Args:
            zip_path: Path to .zip file
            work_in_place: If True, keeps project in zip and extracts to temp

        Returns:
            True if successful, False otherwise
        """
        try:
            # Create temporary extraction directory
            temp_dir = ProjectCompressor.create_temporary_extraction(zip_path)

            if not temp_dir:
                logger.error("Failed to extract project")
                return False

            # Store the original zip path for auto-save
            self._original_zip_path = zip_path
            self._temp_extraction_dir = temp_dir
            self._auto_save_as_zip = True  # Enable auto-save to zip

            # Load the extracted project
            success = self.load_project(temp_dir)

            if not success:
                # Cleanup on failure
                shutil.rmtree(temp_dir, ignore_errors=True)
                self._original_zip_path = None
                self._temp_extraction_dir = None
                self._auto_save_as_zip = False

            return success

        except Exception as e:
            logger.error(f"Error loading project from zip: {e}")
            import traceback
            traceback.print_exc()
            return False

    def is_project_from_zip(self) -> bool:
        """Check if current project was loaded from a .zip file"""
        return hasattr(self, '_original_zip_path') and self._original_zip_path is not None


    def set_auto_save_as_zip(self, enabled: bool):
        """Enable/disable auto-save as zip"""
        self._auto_save_as_zip = enabled
        logger.info(f"📦 Auto-save as zip: {'enabled' if enabled else 'disabled'}")


    def validate_project(self) -> List[Dict[str, Any]]:
        """
        Validate project for potential issues.

        Returns:
            List of validation issues, each containing:
            - 'type': 'error' or 'warning'
            - 'message': Human-readable description
            - 'object': Object name where issue was found (optional)
            - 'room': Room name if relevant (optional)
        """
        issues = []

        if not self.current_project_data:
            return issues

        assets = self.current_project_data.get('assets', {})
        rooms = assets.get('rooms', {})
        objects = assets.get('objects', {})

        room_list = list(rooms.keys())
        num_rooms = len(room_list)

        # Check each object for room navigation issues
        for obj_name, obj_data in objects.items():
            events = obj_data.get('events', {})

            # Check all event types
            for event_name, event_data in events.items():
                actions = []

                # Handle different event data structures
                if isinstance(event_data, dict):
                    actions = event_data.get('actions', [])
                elif isinstance(event_data, list):
                    actions = event_data

                # Check actions for room navigation
                self._check_actions_for_room_issues(
                    actions, obj_name, event_name, room_list, num_rooms, issues
                )

        return issues

    def _check_actions_for_room_issues(
        self,
        actions: List,
        obj_name: str,
        event_name: str,
        room_list: List[str],
        num_rooms: int,
        issues: List[Dict[str, Any]]
    ):
        """Recursively check actions for room navigation issues"""
        for action in actions:
            if not isinstance(action, dict):
                continue

            action_type = action.get('action', action.get('action_type', ''))
            params = action.get('parameters', {})

            # Check next_room when on last room
            if action_type == 'next_room' and num_rooms <= 1:
                issues.append({
                    'type': 'warning',
                    'message': f"'{obj_name}' uses 'next_room' but there is only {num_rooms} room(s). "
                               "The action will have no effect on the last room.",
                    'object': obj_name,
                    'event': event_name
                })

            # Check previous_room when on first room
            if action_type == 'previous_room' and num_rooms <= 1:
                issues.append({
                    'type': 'warning',
                    'message': f"'{obj_name}' uses 'previous_room' but there is only {num_rooms} room(s). "
                               "The action will have no effect on the first room.",
                    'object': obj_name,
                    'event': event_name
                })

            # Check goto_room with invalid room name
            if action_type == 'goto_room':
                target_room = params.get('room', params.get('room_name', ''))
                if target_room and target_room not in room_list:
                    issues.append({
                        'type': 'error',
                        'message': f"'{obj_name}' tries to go to room '{target_room}' which doesn't exist.",
                        'object': obj_name,
                        'event': event_name
                    })

            # Check nested actions (e.g., in if_on_grid)
            then_actions = params.get('then_actions', [])
            if then_actions:
                self._check_actions_for_room_issues(
                    then_actions, obj_name, event_name, room_list, num_rooms, issues
                )

            else_actions = params.get('else_actions', [])
            if else_actions:
                self._check_actions_for_room_issues(
                    else_actions, obj_name, event_name, room_list, num_rooms, issues
                )
