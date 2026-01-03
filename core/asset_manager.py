#!/usr/bin/env python3

import shutil
import hashlib
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional, Any
from PySide6.QtCore import QObject, Signal
from PIL import Image, ImageOps
import pygame
import logging

# Module logger
logger = logging.getLogger(__name__)


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
        """Convert relative project path to absolute path"""
        if not self.project_directory:
            return Path(relative_path)  # Return as-is if no project directory
        return self.project_directory / relative_path

    def get_relative_path(self, absolute_path: Path) -> str:
        """Convert absolute path to relative project path"""
        if not self.project_directory:
            return str(absolute_path)
        try:
            return str(Path(absolute_path).relative_to(self.project_directory))
        except ValueError:
            # If path is not relative to project directory, return as-is
            return str(absolute_path)

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
            print(f"❌ IMPORT ERROR: {error_msg}")
            print(f"❌ Exception type: {type(e).__name__}")
            print(f"❌ File path: {file_path}")
            print(f"❌ Asset type: {asset_type}")
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
                    print(f"🗑️ Deleted old sprite file: {old_abs_path}")

            # Delete old thumbnail if it exists
            old_thumbnail = existing_sprite.get("thumbnail")
            if old_thumbnail:
                old_thumb_path = self.get_absolute_path(old_thumbnail)
                if old_thumb_path.exists():
                    old_thumb_path.unlink()
                    print(f"🗑️ Deleted old thumbnail: {old_thumb_path}")

            # Copy new image to project directory
            relative_path = f"sprites/{sprite_name}{file_path.suffix}"
            dest_path = self.get_absolute_path(relative_path)
            shutil.copy2(file_path, dest_path)
            print(f"📁 Copied new image: {dest_path}")

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
            print(f"❌ REPLACE ERROR: {error_msg}")
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
            print(f"🔄 Cleared sprite reference from objects: {', '.join(updated_objects)}")

    def rename_asset(self, asset_type: str, old_name: str, new_name: str) -> bool:
        """Rename an asset and update file paths"""
        if not self.project_directory:
            return False

        if old_name == new_name:
            return True

        # DEBUG: Check state before rename
        print(f"🔍 RENAME DEBUG: Attempting to rename {asset_type}")
        print(f"  Old name: {old_name}")
        print(f"  New name: {new_name}")
        print(f"  Cache before: {list(self.assets_cache.get(asset_type, {}).keys())}")

        if self.asset_exists(asset_type, new_name):
            self.status_changed.emit(f"Asset {new_name} already exists")
            return False

        try:
            asset_data = self.get_asset(asset_type, old_name)
            if not asset_data:
                print(f"❌ Asset not found in cache: {old_name}")
                return False

            print(f"✅ Found asset data for {old_name}")

            # Rename main file
            if asset_data.get("file_path"):
                old_file_path = self.get_absolute_path(asset_data["file_path"])
                if old_file_path.exists():
                    new_file_path = old_file_path.parent / f"{new_name}{old_file_path.suffix}"
                    old_file_path.rename(new_file_path)
                    asset_data["file_path"] = self.get_relative_path(new_file_path)
                    print(f"✅ Renamed file: {old_file_path.name} → {new_file_path.name}")

            # Rename thumbnail
            if asset_data.get("thumbnail"):
                old_thumbnail_path = self.get_absolute_path(asset_data["thumbnail"])
                if old_thumbnail_path.exists():
                    new_thumbnail_path = old_thumbnail_path.parent / f"{new_name}_thumb.png"
                    old_thumbnail_path.rename(new_thumbnail_path)
                    asset_data["thumbnail"] = self.get_relative_path(new_thumbnail_path)

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
                    print(f"✅ Removed old key from cache: {old_name}")

                # Add new key
                self.assets_cache[asset_type][new_name] = updated_data
                print(f"✅ Added new key to cache: {new_name}")

                # Verify the update
                print(f"  Cache after: {list(self.assets_cache.get(asset_type, {}).keys())}")

            # Update references in other assets (e.g., objects using this sprite)
            self._update_asset_references(asset_type, old_name, new_name)

            self.asset_updated.emit(asset_type, new_name, asset_data)
            self.status_changed.emit(f"Renamed {old_name} to {new_name}")

            return True

        except Exception as e:
            self.status_changed.emit(f"Failed to rename {old_name}: {str(e)}")
            print(f"❌ Rename exception: {e}")
            import traceback
            traceback.print_exc()
            return False

    def _update_asset_references(self, asset_type: str, old_name: str, new_name: str):
        """Update all references to a renamed asset in other assets"""
        try:
            if asset_type == "sprites":
                # Update sprite references in objects
                objects = self.assets_cache.get("objects", {})
                for obj_name, obj_data in objects.items():
                    if obj_data.get("sprite") == old_name:
                        obj_data["sprite"] = new_name
                        obj_data["modified"] = datetime.now().isoformat()
                        print(f"  📝 Updated sprite reference in object '{obj_name}': {old_name} → {new_name}")

                # Update sprite references in room instances
                rooms = self.assets_cache.get("rooms", {})
                for room_name, room_data in rooms.items():
                    # Room instances typically use object_name, not sprite directly
                    # But some rooms might have direct sprite references
                    pass

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
                            print(f"  📝 Updated object reference in room '{room_name}' instance: {old_name} → {new_name}")
                    if updated:
                        room_data["modified"] = datetime.now().isoformat()

                # Update collision event references in ALL objects
                objects = self.assets_cache.get("objects", {})
                for obj_name, obj_data in objects.items():
                    events = obj_data.get("events", {})
                    if not events:
                        continue

                    updated_events = {}
                    obj_modified = False

                    for event_name, event_data in events.items():
                        new_event_name = event_name

                        # Rename collision_with_X events
                        if event_name == f"collision_with_{old_name}":
                            new_event_name = f"collision_with_{new_name}"
                            print(f"  📝 Updated event name in object '{obj_name}': {event_name} → {new_event_name}")
                            obj_modified = True

                        # Update target_object in event data
                        if event_data.get("target_object") == old_name:
                            event_data["target_object"] = new_name
                            print(f"  📝 Updated target_object in object '{obj_name}' event '{new_event_name}': {old_name} → {new_name}")
                            obj_modified = True

                        # Update object references in action parameters
                        actions = event_data.get("actions", [])
                        for action in actions:
                            params = action.get("parameters", {})
                            # Check 'object' parameter (used in if_collision, create_instance, etc.)
                            if params.get("object") == old_name:
                                params["object"] = new_name
                                print(f"  📝 Updated action parameter in object '{obj_name}': object={old_name} → {new_name}")
                                obj_modified = True
                            # Check 'target_object' parameter
                            if params.get("target_object") == old_name:
                                params["target_object"] = new_name
                                obj_modified = True

                        updated_events[new_event_name] = event_data

                    if obj_modified:
                        obj_data["events"] = updated_events
                        obj_data["modified"] = datetime.now().isoformat()

            elif asset_type == "sounds":
                # Sounds might be referenced in object events
                # This would require parsing action parameters
                pass

            elif asset_type == "backgrounds":
                # Update background references in rooms
                rooms = self.assets_cache.get("rooms", {})
                for room_name, room_data in rooms.items():
                    if room_data.get("background_image") == old_name:
                        room_data["background_image"] = new_name
                        room_data["modified"] = datetime.now().isoformat()
                        print(f"  📝 Updated background reference in room '{room_name}': {old_name} → {new_name}")

        except Exception as e:
            print(f"⚠️ Error updating asset references: {e}")

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

    def get_all_assets(self) -> Dict[str, Dict[str, Dict[str, Any]]]:
        """Get all assets"""
        return self.assets_cache.copy()

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
                # This fixes older projects where assets were incorrectly saved with imported=False
                if not asset_data.get('imported', False):
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

                # DEBUG: Verify room order is preserved
                if asset_type == 'rooms':
                    room_order = list(assets_of_type.keys())
                    print(f"💾 AssetManager: Saving room order: {room_order}")
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

    def get_asset_info(self, asset_type: str, asset_name: str) -> Dict[str, Any]:
        """Get detailed information about an asset"""
        asset_data = self.get_asset(asset_type, asset_name)
        if not asset_data:
            return {}

        info = asset_data.copy()

        if asset_data.get("file_path"):
            file_path = self.get_absolute_path(asset_data["file_path"])
            if file_path.exists():
                stat = file_path.stat()
                info.update({
                    "file_size": stat.st_size,
                    "file_modified": datetime.fromtimestamp(stat.st_mtime).isoformat(),
                    "absolute_path": str(file_path)
                })

                if asset_type in ["sprites", "backgrounds"]:
                    try:
                        with Image.open(file_path) as img:
                            info.update({
                                "width": img.width,
                                "height": img.height,
                                "format": img.format,
                                "mode": img.mode
                            })
                    except (FileNotFoundError, OSError, IOError) as e:
                        logger.warning("Could not read image %s: %s", file_path, e)
                    except Exception:
                        logger.exception("Unexpected error reading image info for %s", file_path)

                elif asset_type == "sounds":
                    # Only attempt to load sound metadata if audio backend initialized
                    if getattr(self, "audio_available", False):
                        try:
                            sound = pygame.mixer.Sound(file_path)
                            info.update({
                                "length": sound.get_length()
                            })
                        except (FileNotFoundError, pygame.error) as e:
                            logger.warning("Could not load sound %s: %s", file_path, e)
                        except Exception:
                            logger.exception("Unexpected error loading sound info for %s", file_path)
                    else:
                        # Audio not available; provide a safe default length
                        info.update({
                            "length": 0.0,
                            "audio_available": False
                        })

        return info

    def validate_project_assets(self) -> List[Dict[str, Any]]:
        """Validate all project assets and return list of issues"""
        issues = []

        if not self.project_directory:
            return issues

        for asset_type, assets in self.assets_cache.items():
            for asset_name, asset_data in assets.items():
                if asset_data.get("file_path"):
                    file_path = self.get_absolute_path(asset_data["file_path"])
                    if not file_path.exists():
                        issues.append({
                            "type": "missing_file",
                            "asset_type": asset_type,
                            "asset_name": asset_name,
                            "file_path": str(file_path),
                            "relative_path": asset_data["file_path"],
                            "message": f"File not found: {asset_data['file_path']}"
                        })
                    elif not self.is_supported_format(file_path, asset_type):
                        issues.append({
                            "type": "unsupported_format",
                            "asset_type": asset_type,
                            "asset_name": asset_name,
                            "file_path": str(file_path),
                            "relative_path": asset_data["file_path"],
                            "message": f"Unsupported format: {file_path.suffix}"
                        })

                if asset_data.get("thumbnail"):
                    thumbnail_path = self.get_absolute_path(asset_data["thumbnail"])
                    if not thumbnail_path.exists():
                        issues.append({
                            "type": "missing_thumbnail",
                            "asset_type": asset_type,
                            "asset_name": asset_name,
                            "thumbnail_path": str(thumbnail_path),
                            "relative_path": asset_data["thumbnail"],
                            "message": f"Thumbnail not found: {asset_data['thumbnail']}"
                        })

        return issues

    def clean_unused_files(self) -> List[str]:
        """Remove files that are not referenced by any assets"""
        if not self.project_directory:
            return []

        removed_files = []
        asset_directories = ["sprites", "sounds", "backgrounds", "thumbnails"]

        for directory in asset_directories:
            dir_path = self.project_directory / directory
            if not dir_path.exists():
                continue

            for file_path in dir_path.iterdir():
                if file_path.is_file():
                    relative_path = self.get_relative_path(file_path)

                    is_used = False
                    for asset_type, assets in self.assets_cache.items():
                        for asset_data in assets.values():
                            if (asset_data.get("file_path") == relative_path or
                                asset_data.get("thumbnail") == relative_path):
                                is_used = True
                                break
                        if is_used:
                            break

                    if not is_used:
                        try:
                            file_path.unlink()
                            removed_files.append(relative_path)
                        except Exception as e:
                            self.status_changed.emit(f"Failed to remove {file_path}: {str(e)}")

        if removed_files:
            self.status_changed.emit(f"Removed {len(removed_files)} unused files")

        return removed_files

    def get_file_hash(self, file_path: Path) -> str:
            """Generate MD5 hash of a file

            Args:
                file_path: Path to the file to hash

            Returns:
                str: MD5 hash as hex string, or empty string if error
            """
            try:
                hash_md5 = hashlib.md5()
                with open(file_path, "rb") as f:
                    for chunk in iter(lambda: f.read(4096), b""):
                        hash_md5.update(chunk)
                return hash_md5.hexdigest()
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

    def _validate_asset_paths(self, asset_data: Dict[str, Any]) -> None:
        """Validate that asset file paths exist and mark missing files"""
        if not self.project_directory:
            return

        if asset_data.get("file_path"):
            file_path = self.get_absolute_path(asset_data["file_path"])
            if not file_path.exists():
                asset_data["imported"] = False
                asset_data["file_missing"] = True

        if asset_data.get("thumbnail"):
            thumbnail_path = self.get_absolute_path(asset_data["thumbnail"])
            if not thumbnail_path.exists():
                asset_data.pop("thumbnail", None)
