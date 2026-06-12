#!/usr/bin/env python3

import shutil
import hashlib
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional, Any
from PySide6.QtCore import QObject, Signal
from PIL import Image, ImageOps
import pygame

from core.logger import get_logger
logger = get_logger(__name__)


class AssetManager(QObject):

    asset_imported = Signal(str, str, dict)  # asset_type, asset_name, asset_data
    asset_deleted = Signal(str, str)  # asset_type, asset_name
    asset_updated = Signal(str, str, dict)  # asset_type, asset_name, asset_data
    status_changed = Signal(str)  # status_message

    SUPPORTED_FORMATS = {
        "sprites": [".png", ".jpg", ".jpeg", ".bmp", ".gif", ".tga", ".webp"],
        "sounds": [".wav", ".mp3", ".ogg", ".m4a", ".aac", ".flac"],
        "backgrounds": [".png", ".jpg", ".jpeg", ".bmp", ".gif", ".tga", ".webp"],
        "fonts": [".ttf", ".otf", ".woff", ".woff2"],
        "data": [".json", ".xml", ".txt", ".csv"]
    }

    THUMBNAIL_SIZE = (64, 64)
    MAX_PREVIEW_SIZE = (256, 256)

    def __init__(self, project_directory: Optional[Path] = None):
        super().__init__()
        # Don't default to cwd - only set project_directory if explicitly provided
        self.project_directory = Path(project_directory) if project_directory else None
        self.assets_cache = {}
        self.thumbnails_cache = {}

        # Initialize audio mixer safely — some systems (headless) may not have audio device.
        try:
            pygame.mixer.init()
            self.audio_available = True
        except Exception as e:
            # Do not crash; mark audio as unavailable and emit status if possible
            self.audio_available = False
            try:
                self.status_changed.emit(f"Audio disabled: {e}")
            except Exception:
                    # Fallback to logging if signals are not connected yet
                    logger.warning("Audio disabled: %s", e)

        # Only create directories if a project directory was explicitly provided
        if self.project_directory:
            self.ensure_directories()

    def set_project_directory(self, project_directory: Optional[Path]) -> None:
        """Set the project directory and reset caches"""
        if project_directory:
            self.project_directory = Path(project_directory).resolve()
            self.ensure_directories()
        else:
            self.project_directory = None

        self.assets_cache.clear()
        self.thumbnails_cache.clear()

    def get_absolute_path(self, relative_path: str) -> Path:
        """Convert relative project path to absolute path.

        get_relative_path stores separators as forward slashes (as_posix),
        but projects saved on older Windows builds may carry backslash
        separators in file_path/thumbnail. Normalise on read so a Windows
        path like ``thumbnails\\foo.png`` resolves on every platform —
        otherwise os.stat() on a literal-backslash name raises
        OSError(EINVAL) and aborts the whole project load.
        """
        relative_path = str(relative_path).replace("\\", "/")
        if not self.project_directory:
            return Path(relative_path)  # Return as-is if no project directory
        return self.project_directory / relative_path

    def get_relative_path(self, absolute_path: Path) -> str:
        """Convert absolute path to relative project path.

        Always uses forward slashes — the result is written into project.json
        (asset file_path, thumbnail) and projects need to round-trip across
        Windows/macOS/Linux. as_posix() normalises the separator.
        """
        if not self.project_directory:
            return Path(absolute_path).as_posix()
        try:
            return Path(absolute_path).relative_to(self.project_directory).as_posix()
        except ValueError:
            # If path is not relative to project directory, return as-is
            return Path(absolute_path).as_posix()

    def ensure_directories(self) -> None:
        """Create necessary asset directories in the project directory"""
        if not self.project_directory:
            return

        directories = [
            "sprites", "sounds", "backgrounds", "objects",
            "rooms", "scripts", "fonts", "data", "thumbnails"
        ]

        for directory in directories:
            (self.project_directory / directory).mkdir(exist_ok=True)

    def get_supported_formats(self, asset_type: str) -> List[str]:
        """Get list of supported file formats for an asset type

        Args:
            asset_type: Type of asset (sprites, sounds, backgrounds, etc.)

        Returns:
            List[str]: List of supported file extensions
        """
        return self.SUPPORTED_FORMATS.get(asset_type, [])

    def is_supported_format(self, file_path: Path, asset_type: str) -> bool:
        """Check if a file format is supported for an asset type

        Args:
            file_path: Path to the file
            asset_type: Type of asset

        Returns:
            bool: True if format is supported, False otherwise
        """
        supported = self.get_supported_formats(asset_type)
        return file_path.suffix.lower() in supported

    def import_asset(self, file_path: Path, asset_type: str, asset_name: Optional[str] = None) -> Optional[Dict[str, Any]]:
        """Import an asset from an external file path to the project"""
        if not self.project_directory:
            self.status_changed.emit("No project directory set")
            return None

        if not self.is_supported_format(file_path, asset_type):
            self.status_changed.emit(f"Unsupported file format: {file_path.suffix}")
            return None

        try:
            if not asset_name:
                asset_name = file_path.stem

            asset_name = self.get_unique_asset_name(asset_name, asset_type)

            asset_data = self._create_asset_data(file_path, asset_type, asset_name)

            # Copy to project directory (store as relative path)
            relative_path = f"{asset_type}/{asset_name}{file_path.suffix}"
            dest_path = self.get_absolute_path(relative_path)
            shutil.copy2(file_path, dest_path)

            asset_data["file_path"] = relative_path

            if asset_type in ["sprites", "backgrounds"]:
                thumbnail_path = self.generate_thumbnail(dest_path, asset_name)
                if thumbnail_path:
                    asset_data["thumbnail"] = self.get_relative_path(thumbnail_path)

            self.assets_cache.setdefault(asset_type, {})[asset_name] = asset_data

            self.asset_imported.emit(asset_type, asset_name, asset_data)
            self.status_changed.emit(f"Imported {asset_name}")

            return asset_data

        except Exception as e:
            error_msg = f"Failed to import {file_path.name}: {str(e)}"
            logger.error(f"❌ IMPORT ERROR: {error_msg}")
            logger.error(f"❌ Exception type: {type(e).__name__}")
            logger.error(f"❌ File path: {file_path}")
            logger.error(f"❌ Asset type: {asset_type}")
            import traceback
            traceback.print_exc()
            self.status_changed.emit(error_msg)
            return None

    def replace_sprite_image(self, file_path: Path, sprite_name: str) -> Optional[Dict[str, Any]]:
        """Replace the image file for an existing sprite asset"""
        if not self.project_directory:
            self.status_changed.emit("No project directory set")
            return None

        if not self.is_supported_format(file_path, "sprites"):
            self.status_changed.emit(f"Unsupported file format: {file_path.suffix}")
            return None

        # Get existing sprite data
        existing_sprite = self.get_asset("sprites", sprite_name)
        if not existing_sprite:
            self.status_changed.emit(f"Sprite '{sprite_name}' not found")
            return None

        try:
            # Delete old image file if it exists
            old_file_path = existing_sprite.get("file_path")
            if old_file_path:
                old_abs_path = self.get_absolute_path(old_file_path)
                if old_abs_path.exists():
                    old_abs_path.unlink()
                    logger.debug(f"🗑️ Deleted old sprite file: {old_abs_path}")

            # Delete old thumbnail if it exists
            old_thumbnail = existing_sprite.get("thumbnail")
            if old_thumbnail:
                old_thumb_path = self.get_absolute_path(old_thumbnail)
                if old_thumb_path.exists():
                    old_thumb_path.unlink()
                    logger.debug(f"🗑️ Deleted old thumbnail: {old_thumb_path}")

            # Copy new image to project directory
            relative_path = f"sprites/{sprite_name}{file_path.suffix}"
            dest_path = self.get_absolute_path(relative_path)
            shutil.copy2(file_path, dest_path)
            logger.debug(f"📁 Copied new image: {dest_path}")

            # Update sprite data
            existing_sprite["file_path"] = relative_path
            existing_sprite["modified"] = datetime.now().isoformat()

            # Get image dimensions
            with Image.open(dest_path) as img:
                existing_sprite["width"] = img.width
                existing_sprite["height"] = img.height

            # Generate new thumbnail
            thumbnail_path = self.generate_thumbnail(dest_path, sprite_name)
            if thumbnail_path:
                existing_sprite["thumbnail"] = self.get_relative_path(thumbnail_path)

            # Update cache
            self.assets_cache.setdefault("sprites", {})[sprite_name] = existing_sprite

            self.asset_updated.emit("sprites", sprite_name, existing_sprite)
            self.status_changed.emit(f"Replaced image for {sprite_name}")

            return existing_sprite

        except Exception as e:
            error_msg = f"Failed to replace sprite image: {str(e)}"
            logger.error(f"❌ REPLACE ERROR: {error_msg}")
            import traceback
            traceback.print_exc()
            self.status_changed.emit(error_msg)
            return None

    def import_multiple_assets(self, file_paths: List[Path], asset_type: str) -> List[Dict[str, Any]]:
        """Import multiple assets at once"""
        imported_assets = []

        for file_path in file_paths:
            asset_data = self.import_asset(file_path, asset_type)
            if asset_data:
                imported_assets.append(asset_data)

        if imported_assets:
            self.status_changed.emit(f"Imported {len(imported_assets)} {asset_type}")

        return imported_assets

    def update_sprite_animation(self, sprite_name: str, frames: int, frame_width: int,
                                 frame_height: int, speed: float = 10.0,
                                 animation_type: str = "strip_h") -> Optional[Dict[str, Any]]:
        """Update sprite animation settings (for sprite strips/sheets)"""
        sprites = self.assets_cache.get("sprites", {})
        if sprite_name not in sprites:
            logger.warning("Sprite %s not found", sprite_name)
            return None

        sprite_data = sprites[sprite_name]
        sprite_data.update({
            "frames": frames,
            "frame_width": frame_width,
            "frame_height": frame_height,
            "speed": speed,
            "animation_type": animation_type,
            "origin_x": frame_width // 2,  # Update origin to frame center
            "origin_y": frame_height // 2,
            "modified": datetime.now().isoformat()
        })

        # Regenerate thumbnail to show only first frame for strips
        if sprite_data.get("file_path"):
            image_path = self.get_absolute_path(sprite_data["file_path"])
            if image_path.exists():
                thumbnail_path = self.generate_thumbnail(image_path, sprite_name, sprite_data)
                if thumbnail_path:
                    sprite_data["thumbnail"] = self.get_relative_path(thumbnail_path)

        self.asset_updated.emit("sprites", sprite_name, sprite_data)
        self.status_changed.emit(f"Updated animation for {sprite_name}: {frames} frames")

        return sprite_data

    def create_asset(self, asset_name: str, asset_type: str, **kwargs) -> Optional[Dict[str, Any]]:
        """Create a new asset (objects, rooms, scripts, etc.)"""
        asset_name = self.get_unique_asset_name(asset_name, asset_type)

        asset_data = {
            "name": asset_name,
            "asset_type": asset_type,
            "created": datetime.now().isoformat(),
            "modified": datetime.now().isoformat(),
            "imported": True,  # Asset is created within IDE, so it's immediately available
            "file_path": "",
        }

        if asset_type == "objects":
            asset_data.update({
                "sprite": "",
                "visible": True,
                "solid": False,
                "persistent": False,
                "depth": 0,
                "events": {}
            })
        elif asset_type == "rooms":
            asset_data.update({
                "width": 1024,
                "height": 768,
                "background": "",
                "background_color": "#000000",
                "instances": [],
                "creation_code": ""
            })
        elif asset_type == "scripts":
            asset_data.update({
                "code": "// Script code goes here\n",
                "language": "gml"
            })
        elif asset_type == "fonts":
            asset_data.update({
                "font_name": "Arial",
                "size": 12,
                "bold": False,
                "italic": False,
                "charset": "ascii"
            })

        asset_data.update(kwargs)

        self.assets_cache.setdefault(asset_type, {})[asset_name] = asset_data

        self.asset_imported.emit(asset_type, asset_name, asset_data)
        self.status_changed.emit(f"Created {asset_name}")

        return asset_data

    def delete_asset(self, asset_type: str, asset_name: str) -> bool:
        """Delete an asset and its associated files"""
        if not self.project_directory:
            return False

        try:
            asset_data = self.get_asset(asset_type, asset_name)
            if not asset_data:
                return False

            # Delete main file
            if asset_data.get("file_path"):
                file_path = self.get_absolute_path(asset_data["file_path"])
                if file_path.exists():
                    file_path.unlink()

            # Delete thumbnail
            if asset_data.get("thumbnail"):
                thumbnail_path = self.get_absolute_path(asset_data["thumbnail"])
                if thumbnail_path.exists():
                    thumbnail_path.unlink()

            # Rooms/objects keep their payload in <type>/<name>.json side
            # files that file_path doesn't reference. Remove them too: a
            # stale orphan would resurrect the dead asset's data into any
            # future asset created with the same name (audit H3).
            if asset_type in ("rooms", "objects"):
                side_file = self.project_directory / asset_type / f"{asset_name}.json"
                if side_file.exists():
                    side_file.unlink()

            # If deleting a sprite, clear references from objects that use it
            if asset_type == "sprites":
                self._clear_sprite_references(asset_name)

            # Remove from cache
            if asset_type in self.assets_cache and asset_name in self.assets_cache[asset_type]:
                del self.assets_cache[asset_type][asset_name]

            self.asset_deleted.emit(asset_type, asset_name)
            self.status_changed.emit(f"Deleted {asset_name}")

            return True

        except Exception as e:
            self.status_changed.emit(f"Failed to delete {asset_name}: {str(e)}")
            return False

    def _clear_sprite_references(self, sprite_name: str) -> None:
        """Clear references to a sprite from all objects that use it"""
        objects = self.assets_cache.get("objects", {})
        updated_objects = []

        for obj_name, obj_data in objects.items():
            if obj_data.get("sprite") == sprite_name:
                obj_data["sprite"] = ""
                updated_objects.append(obj_name)
                self.asset_updated.emit("objects", obj_name, obj_data)

        if updated_objects:
            logger.debug(f"🔄 Cleared sprite reference from objects: {', '.join(updated_objects)}")

    def rename_asset(self, asset_type: str, old_name: str, new_name: str) -> bool:
        """Rename an asset and update file paths"""
        if not self.project_directory:
            return False

        if old_name == new_name:
            return True

        logger.debug(f"rename_asset: {asset_type} {old_name!r} → {new_name!r}")

        if self.asset_exists(asset_type, new_name):
            self.status_changed.emit(f"Asset {new_name} already exists")
            return False

        try:
            asset_data = self.get_asset(asset_type, old_name)
            if not asset_data:
                logger.error(f"❌ Asset not found in cache: {old_name}")
                return False

            logger.debug(f"✅ Found asset data for {old_name}")

            # Rename main file
            if asset_data.get("file_path"):
                old_file_path = self.get_absolute_path(asset_data["file_path"])
                if old_file_path.exists():
                    new_file_path = old_file_path.parent / f"{new_name}{old_file_path.suffix}"
                    old_file_path.rename(new_file_path)
                    asset_data["file_path"] = self.get_relative_path(new_file_path)
                    logger.debug(f"✅ Renamed file: {old_file_path.name} → {new_file_path.name}")

            # Rename thumbnail
            if asset_data.get("thumbnail"):
                old_thumbnail_path = self.get_absolute_path(asset_data["thumbnail"])
                if old_thumbnail_path.exists():
                    new_thumbnail_path = old_thumbnail_path.parent / f"{new_name}_thumb.png"
                    old_thumbnail_path.rename(new_thumbnail_path)
                    asset_data["thumbnail"] = self.get_relative_path(new_thumbnail_path)

            # Carry the rooms/objects <type>/<name>.json side file along so
            # an orphan under the old name can't resurrect stale data into a
            # future asset reusing that name (audit H3).
            if asset_type in ("rooms", "objects"):
                old_side = self.project_directory / asset_type / f"{old_name}.json"
                if old_side.exists():
                    old_side.replace(self.project_directory / asset_type / f"{new_name}.json")

            # Update asset data
            asset_data["name"] = new_name
            asset_data["modified"] = datetime.now().isoformat()

            # CRITICAL: Update cache - DELETE old, ADD new
            if asset_type in self.assets_cache:
                # Save the data first
                updated_data = asset_data.copy()

                # Remove old key
                if old_name in self.assets_cache[asset_type]:
                    del self.assets_cache[asset_type][old_name]
                    logger.debug(f"✅ Removed old key from cache: {old_name}")

                # Add new key
                self.assets_cache[asset_type][new_name] = updated_data
                logger.debug(f"✅ Added new key to cache: {new_name}")

                # Verify the update
                logger.debug(f"  Cache after: {list(self.assets_cache.get(asset_type, {}).keys())}")

            # Update references in other assets (e.g., objects using this sprite)
            self._update_asset_references(asset_type, old_name, new_name)

            self.asset_updated.emit(asset_type, new_name, asset_data)
            self.status_changed.emit(f"Renamed {old_name} to {new_name}")

            return True

        except Exception as e:
            self.status_changed.emit(f"Failed to rename {old_name}: {str(e)}")
            logger.error(f"❌ Rename exception: {e}")
            import traceback
            traceback.print_exc()
            return False

    def _update_asset_references(self, asset_type: str, old_name: str, new_name: str):
        """Update all references to a renamed asset in other assets"""
        try:
            if asset_type == "sprites":
                # Update sprite references in objects (default sprite)
                objects = self.assets_cache.get("objects", {})
                for obj_name, obj_data in objects.items():
                    if obj_data.get("sprite") == old_name:
                        obj_data["sprite"] = new_name
                        obj_data["modified"] = datetime.now().isoformat()
                        logger.debug(f"  📝 Updated sprite reference in object '{obj_name}': {old_name} → {new_name}")

                # Update set_sprite action parameters across all objects
                self._update_param_in_all_actions(old_name, new_name, "sprite")

            elif asset_type == "objects":
                # Update object references in rooms
                rooms = self.assets_cache.get("rooms", {})
                for room_name, room_data in rooms.items():
                    instances = room_data.get("instances", [])
                    updated = False
                    for instance in instances:
                        if instance.get("object_name") == old_name:
                            instance["object_name"] = new_name
                            updated = True
                            logger.debug(f"  📝 Updated object reference in room '{room_name}' instance: {old_name} → {new_name}")
                    if updated:
                        room_data["modified"] = datetime.now().isoformat()

                # Update references in ALL objects: collision events, parent, action params
                objects = self.assets_cache.get("objects", {})
                for obj_name, obj_data in objects.items():
                    obj_modified = False

                    # Update parent reference
                    if obj_data.get("parent") == old_name:
                        obj_data["parent"] = new_name
                        logger.debug(f"  📝 Updated parent in object '{obj_name}': {old_name} → {new_name}")
                        obj_modified = True

                    events = obj_data.get("events", {})
                    if not events:
                        if obj_modified:
                            obj_data["modified"] = datetime.now().isoformat()
                        continue

                    updated_events = {}

                    for event_name, event_data in events.items():
                        new_event_name = event_name

                        # Rename collision_with_X and not_collision_with_X events
                        if event_name == f"collision_with_{old_name}":
                            new_event_name = f"collision_with_{new_name}"
                            logger.debug(f"  📝 Updated event name in object '{obj_name}': {event_name} → {new_event_name}")
                            obj_modified = True
                        elif event_name == f"not_collision_with_{old_name}":
                            new_event_name = f"not_collision_with_{new_name}"
                            logger.debug(f"  📝 Updated event name in object '{obj_name}': {event_name} → {new_event_name}")
                            obj_modified = True

                        # Update target_object in event data
                        if isinstance(event_data, dict) and event_data.get("target_object") == old_name:
                            event_data["target_object"] = new_name
                            obj_modified = True

                        # Update object references in action parameters
                        # (handles both top-level actions and sub-event actions)
                        obj_modified |= self._update_actions_object_refs(
                            event_data, old_name, new_name, obj_name, new_event_name
                        )

                        updated_events[new_event_name] = event_data

                    if obj_modified:
                        obj_data["events"] = updated_events
                        obj_data["modified"] = datetime.now().isoformat()

            elif asset_type == "sounds":
                # Update sound references in all object action parameters
                self._update_param_in_all_actions(old_name, new_name, "sound")
                self._update_param_in_all_actions(old_name, new_name, "music")

            elif asset_type == "rooms":
                # Update room references in all object action parameters
                self._update_param_in_all_actions(old_name, new_name, "room")

            elif asset_type == "backgrounds":
                # Update background references in rooms
                rooms = self.assets_cache.get("rooms", {})
                for room_name, room_data in rooms.items():
                    if room_data.get("background_image") == old_name:
                        room_data["background_image"] = new_name
                        room_data["modified"] = datetime.now().isoformat()
                        logger.debug(f"  📝 Updated background reference in room '{room_name}': {old_name} → {new_name}")

        except Exception as e:
            logger.warning(f"⚠️ Error updating asset references: {e}")

    def _update_param_in_all_actions(self, old_name, new_name, param_key):
        """Update a specific parameter across all actions in all objects.

        Used when renaming sprites, sounds, or rooms to update references
        like set_sprite(sprite=old_name), sound_play(sound=old_name), etc.
        """
        objects = self.assets_cache.get("objects", {})
        for obj_name, obj_data in objects.items():
            events = obj_data.get("events", {})
            if not events:
                continue
            obj_modified = False
            for event_name, event_data in events.items():
                if not isinstance(event_data, dict):
                    continue
                # Top-level actions
                for action in event_data.get("actions", []):
                    params = action.get("parameters", {})
                    if params.get(param_key) == old_name:
                        params[param_key] = new_name
                        obj_modified = True
                # Sub-event actions (keyboard sub-keys, etc.)
                for key, sub_data in event_data.items():
                    if key == "actions" or not isinstance(sub_data, dict):
                        continue
                    for action in sub_data.get("actions", []):
                        params = action.get("parameters", {})
                        if params.get(param_key) == old_name:
                            params[param_key] = new_name
                            obj_modified = True
            if obj_modified:
                obj_data["modified"] = datetime.now().isoformat()
                logger.debug(f"  📝 Updated '{param_key}' references in object '{obj_name}': {old_name} → {new_name}")

    def _update_actions_object_refs(self, event_data, old_name, new_name, obj_name, event_name) -> bool:
        """Update object references in action parameters, handling nested sub-events."""
        modified = False
        if not isinstance(event_data, dict):
            return False

        # Parameter names that hold object references:
        #   "object"        - create_instance, change_instance
        #   "target_object" - various collision/targeting actions
        #   "object_type"   - if_can_push (stores object name like "box")
        OBJ_PARAM_KEYS = ("object", "target_object", "object_type")

        def update_action_params(action):
            nonlocal modified
            params = action.get("parameters", {})
            for key in OBJ_PARAM_KEYS:
                if params.get(key) == old_name:
                    params[key] = new_name
                    logger.debug(f"  📝 Updated action param in '{obj_name}'.{event_name}: {key}={old_name} → {new_name}")
                    modified = True

        # Top-level actions list
        for action in event_data.get("actions", []):
            update_action_params(action)

        # Sub-events (keyboard sub-keys, etc.)
        for key, sub_data in event_data.items():
            if key == "actions" or not isinstance(sub_data, dict):
                continue
            for action in sub_data.get("actions", []):
                update_action_params(action)

        return modified

    def duplicate_asset(self, asset_type: str, asset_name: str) -> Optional[Dict[str, Any]]:
        """Create a copy of an existing asset"""
        if not self.project_directory:
            return None

        original_asset = self.get_asset(asset_type, asset_name)
        if not original_asset:
            return None

        try:
            new_name = self.get_unique_asset_name(f"{asset_name}_copy", asset_type)

            # Copy asset data
            new_asset_data = original_asset.copy()
            new_asset_data["name"] = new_name
            new_asset_data["created"] = datetime.now().isoformat()
            new_asset_data["modified"] = datetime.now().isoformat()

            # Copy main file
            if original_asset.get("file_path"):
                original_file_path = self.get_absolute_path(original_asset["file_path"])
                if original_file_path.exists():
                    new_file_path = original_file_path.parent / f"{new_name}{original_file_path.suffix}"
                    shutil.copy2(original_file_path, new_file_path)

                    new_asset_data["file_path"] = self.get_relative_path(new_file_path)

                    # Generate new thumbnail for image assets
                    if asset_type in ["sprites", "backgrounds"]:
                        thumbnail_path = self.generate_thumbnail(new_file_path, new_name)
                        if thumbnail_path:
                            new_asset_data["thumbnail"] = self.get_relative_path(thumbnail_path)

            self.assets_cache.setdefault(asset_type, {})[new_name] = new_asset_data

            self.asset_imported.emit(asset_type, new_name, new_asset_data)
            self.status_changed.emit(f"Duplicated {asset_name} as {new_name}")

            return new_asset_data

        except Exception as e:
            self.status_changed.emit(f"Failed to duplicate {asset_name}: {str(e)}")
            return None

    def get_asset(self, asset_type: str, asset_name: str) -> Optional[Dict[str, Any]]:
        """Get asset data by type and name"""
        return self.assets_cache.get(asset_type, {}).get(asset_name)

    def get_assets_by_type(self, asset_type: str) -> Dict[str, Dict[str, Any]]:
        """Get all assets of a specific type"""
        return self.assets_cache.get(asset_type, {})


    def asset_exists(self, asset_type: str, asset_name: str) -> bool:
        """Check if an asset exists"""
        return asset_name in self.assets_cache.get(asset_type, {})

    def get_unique_asset_name(self, base_name: str, asset_type: str) -> str:
        """Generate a unique asset name by adding number suffix if needed"""
        if not self.asset_exists(asset_type, base_name):
            return base_name

        counter = 1
        while self.asset_exists(asset_type, f"{base_name}_{counter}"):
            counter += 1

        return f"{base_name}_{counter}"

    def load_assets_from_project_data(self, project_data: Dict[str, Any]) -> None:
        """Load assets from project JSON data"""
        from collections import OrderedDict

        self.assets_cache = {}
        assets = project_data.get("assets", {})

        # Preserve order for ALL asset types using OrderedDict
        for asset_type, asset_dict in assets.items():
            # Use OrderedDict to preserve insertion order from JSON
            self.assets_cache[asset_type] = OrderedDict(asset_dict)

        # Validate asset paths and fix 'imported' flag for existing assets
        for asset_type, assets_of_type in self.assets_cache.items():
            for asset_name, asset_data in assets_of_type.items():
                self._validate_asset_paths(asset_data)
                # Migration fix: Assets that exist in the project should be marked as imported
                # This fixes older projects where assets were incorrectly saved with imported=False.
                # Skip assets _validate_asset_paths just flagged file_missing, otherwise this
                # immediately undoes that flag and a broken asset is shown as present.
                if (not asset_data.get('imported', False)
                        and not asset_data.get('file_missing', False)):
                    asset_data['imported'] = True

    def save_assets_to_project_data(self, project_data: Dict[str, Any]) -> None:
        """Save assets to project JSON data preserving order"""
        from collections import OrderedDict

        # Convert OrderedDict to regular dict for JSON serialization
        # but maintain the order by reconstructing from items()
        assets_for_json = {}
        for asset_type, assets_of_type in self.assets_cache.items():
            if isinstance(assets_of_type, OrderedDict):
                # Preserve order by converting to list of tuples, then back to dict
                assets_for_json[asset_type] = dict(assets_of_type.items())
            else:
                assets_for_json[asset_type] = assets_of_type

        project_data["assets"] = assets_for_json

    def generate_thumbnail(self, image_path: Path, asset_name: str,
                            sprite_data: Optional[Dict[str, Any]] = None) -> Optional[Path]:
        """Generate a thumbnail for an image asset.

        For sprite strips/sheets, extracts only the first frame for the thumbnail.

        Args:
            image_path: Path to the source image
            asset_name: Name of the asset (used for thumbnail filename)
            sprite_data: Optional sprite metadata with animation_type, frame_width, frame_height
        """
        if not self.project_directory:
            return None

        try:
            thumbnail_dir = self.project_directory / "thumbnails"
            thumbnail_dir.mkdir(exist_ok=True)

            thumbnail_path = thumbnail_dir / f"{asset_name}_thumb.png"

            with Image.open(image_path) as img:
                img = ImageOps.exif_transpose(img)

                # For sprite strips/sheets, extract only the first frame
                if sprite_data:
                    animation_type = sprite_data.get("animation_type", "single")
                    if animation_type in ("strip_h", "strip_v", "grid"):
                        frame_width = sprite_data.get("frame_width", img.width)
                        frame_height = sprite_data.get("frame_height", img.height)
                        # Extract first frame (top-left corner)
                        img = img.crop((0, 0, frame_width, frame_height))

                if img.mode == "RGBA":
                    thumbnail = Image.new("RGBA", self.THUMBNAIL_SIZE, (0, 0, 0, 0))
                else:
                    thumbnail = Image.new("RGB", self.THUMBNAIL_SIZE, (255, 255, 255))

                img.thumbnail(self.THUMBNAIL_SIZE, Image.Resampling.LANCZOS)

                x = (self.THUMBNAIL_SIZE[0] - img.width) // 2
                y = (self.THUMBNAIL_SIZE[1] - img.height) // 2

                thumbnail.paste(img, (x, y))
                thumbnail.save(thumbnail_path, "PNG")

                return thumbnail_path

        except Exception as e:
            self.status_changed.emit(f"Failed to generate thumbnail: {str(e)}")
            return None




    def get_file_hash(self, file_path: Path) -> str:
            """Generate SHA-256 hash of a file

            Used only as non-cryptographic asset-change-detection metadata
            (stored in ``file_hash``, never compared against an adversary), but
            SHA-256 is used rather than MD5 so the digest is sound if this
            field is ever wired into real integrity checking.

            Args:
                file_path: Path to the file to hash

            Returns:
                str: SHA-256 hash as hex string, or empty string if error
            """
            try:
                hash_sha256 = hashlib.sha256()
                with open(file_path, "rb") as f:
                    for chunk in iter(lambda: f.read(4096), b""):
                        hash_sha256.update(chunk)
                return hash_sha256.hexdigest()
            except FileNotFoundError:
                logger.warning("Cannot hash file - not found: %s", file_path)
                return ""
            except PermissionError:
                logger.warning("Cannot hash file - permission denied: %s", file_path)
                return ""
            except (IOError, OSError) as e:
                logger.warning("Cannot hash file - I/O error: %s", e)
                return ""
            except Exception:
                logger.exception("Unexpected error hashing file: %s", file_path)
                return ""

    def _create_asset_data(self, file_path: Path, asset_type: str, asset_name: str) -> Dict[str, Any]:
        """Create asset data dictionary from file"""
        asset_data = {
            "name": asset_name,
            "asset_type": asset_type,
            "created": datetime.now().isoformat(),
            "modified": datetime.now().isoformat(),
            "imported": True,
            "file_hash": self.get_file_hash(file_path)
        }

        if asset_type == "sprites":
            try:
                with Image.open(file_path) as img:
                    asset_data.update({
                        "width": img.width,
                        "height": img.height,
                        "frame_width": img.width,  # Single frame = full width
                        "frame_height": img.height,  # Single frame = full height
                        "origin_x": img.width // 2,
                        "origin_y": img.height // 2,
                        "frames": 1,
                        "speed": 10.0,  # Animation FPS (frames per second)
                        "animation_type": "single"  # single, strip_h, strip_v, files
                    })
            except (FileNotFoundError, OSError, IOError) as e:
                logger.warning("Could not read sprite image %s: %s — using default 32x32", file_path, e)
                asset_data.update({
                    "width": 32,
                    "height": 32,
                    "frame_width": 32,
                    "frame_height": 32,
                    "origin_x": 16,
                    "origin_y": 16,
                    "frames": 1,
                    "speed": 10.0,
                    "animation_type": "single"
                })
            except Exception:
                logger.exception("Unexpected error reading sprite %s — using default 32x32", file_path)
                asset_data.update({
                    "width": 32,
                    "height": 32,
                    "frame_width": 32,
                    "frame_height": 32,
                    "origin_x": 16,
                    "origin_y": 16,
                    "frames": 1,
                    "speed": 10.0,
                    "animation_type": "single"
                })

        elif asset_type == "sounds":
            # Only attempt to load sound length if the audio subsystem is available
            if getattr(self, "audio_available", False):
                try:
                    sound = pygame.mixer.Sound(file_path)
                    asset_data.update({
                        "length": sound.get_length(),
                        "volume": 1.0,
                        "loop": False
                    })
                except (FileNotFoundError, pygame.error) as e:
                    logger.warning("Could not load sound %s: %s — using default sound data", file_path, e)
                    asset_data.update({
                        "length": 0.0,
                        "volume": 1.0,
                        "loop": False
                    })
                except Exception:
                    logger.exception("Unexpected error loading sound %s — using default sound data", file_path)
                    asset_data.update({
                        "length": 0.0,
                        "volume": 1.0,
                        "loop": False
                    })
            else:
                # Audio backend disabled — set sensible defaults
                logger.debug("Audio backend disabled; setting default sound metadata for %s", file_path)
                asset_data.update({
                    "length": 0.0,
                    "volume": 1.0,
                    "loop": False,
                    "audio_available": False
                })

        elif asset_type == "backgrounds":
            try:
                with Image.open(file_path) as img:
                    asset_data.update({
                        "width": img.width,
                        "height": img.height,
                        "tile_horizontal": False,
                        "tile_vertical": False
                    })
            except (FileNotFoundError, OSError, IOError) as e:
                logger.warning("Could not read background image %s: %s — using default 1024x768", file_path, e)
                asset_data.update({
                    "width": 1024,
                    "height": 768,
                    "tile_horizontal": False,
                    "tile_vertical": False
                })
            except Exception:
                logger.exception("Unexpected error reading background %s — using default 1024x768", file_path)
                asset_data.update({
                    "width": 1024,
                    "height": 768,
                    "tile_horizontal": False,
                    "tile_vertical": False
                })

        return asset_data

    def revalidate_asset_import_state(self, asset_data: Dict[str, Any]) -> None:
        """Re-check an asset's backing file and fix its imported/file_missing
        flags BOTH ways.

        Load-time validation (_validate_asset_paths) only ever *flags* a missing
        file; it never clears the flag when the file reappears, and a guard in
        load_assets_from_project refuses to restore `imported` while
        `file_missing` is set. So a sprite that was absent at load (e.g. its art
        was still being created) stays badged "(not imported)" for the whole
        session even after you draw and save it. Call this when an asset's
        editor (re)writes its file to heal that stale badge.

        Assets with no file_path (objects/rooms/scripts) are created in-IDE and
        are always considered present.
        """
        file_path = asset_data.get("file_path")
        if not file_path:
            asset_data.pop("file_missing", None)
            asset_data["imported"] = True
            return
        if not self.project_directory:
            return
        abs_path = self.get_absolute_path(file_path)
        if self._path_exists(abs_path):
            asset_data.pop("file_missing", None)
            asset_data["imported"] = True
        else:
            asset_data["imported"] = False
            asset_data["file_missing"] = True

    def _validate_asset_paths(self, asset_data: Dict[str, Any]) -> None:
        """Validate that asset file paths exist and mark missing files"""
        if not self.project_directory:
            return

        if asset_data.get("file_path"):
            file_path = self.get_absolute_path(asset_data["file_path"])
            if not self._path_exists(file_path):
                asset_data["imported"] = False
                asset_data["file_missing"] = True

        if asset_data.get("thumbnail"):
            thumbnail_path = self.get_absolute_path(asset_data["thumbnail"])
            if not self._path_exists(thumbnail_path):
                asset_data.pop("thumbnail", None)

    @staticmethod
    def _path_exists(path: Path) -> bool:
        """Path.exists() that treats a malformed path as 'missing'.

        A stored path can be malformed (e.g. embedded NUL, or a separator
        the OS rejects). os.stat() then raises OSError instead of returning
        False, and an unhandled raise here would abort the entire project
        load over a single bad asset reference. Swallow it to 'missing'.
        """
        try:
            return path.exists()
        except OSError:
            return False
