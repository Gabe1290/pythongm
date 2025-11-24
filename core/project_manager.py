#!/usr/bin/env python3

import json
import shutil
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional, Any, Tuple
from PySide6.QtCore import QObject, Signal, QTimer

from utils.project_compression import ProjectCompressor

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
        self._zip_handler = None  # NEW: Direct zip handler
        
        # Auto-save timer
        self.auto_save_timer = QTimer()
        self.auto_save_timer.timeout.connect(self.auto_save)
        self.auto_save_enabled = True
        self.auto_save_interval = 30000  # 30 seconds
    
    def create_project(self, project_name: str, location: str, template: str = "empty") -> bool:
        """
        Create a new project (compatibility wrapper for IDE)
        
        Args:
            project_name: Name of the project
            location: Parent directory where project folder will be created
            template: Project template (currently unused, for future expansion)
        
        Returns:
            bool: True if successful, False otherwise
        """
        # Convert string path to Path object
        location_path = Path(location)
        
        # Call the actual implementation
        return self.create_new_project(project_name, location_path)

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
    
    def create_new_project(self, project_name: str, location: Path) -> bool:
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
            
            # Save project file
            project_file = project_path / self.PROJECT_FILE
            with open(project_file, 'w', encoding='utf-8') as f:
                json.dump(project_data, f, indent=2, ensure_ascii=False)
            
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
            print(f"DEBUG PM load_project: path={project_path}")

            # Check if project file exists
            project_file = project_path / self.PROJECT_FILE
            print(f"DEBUG PM load_project: checking for {project_file}, exists={project_file.exists()}")
            if not project_file.exists():
                self.status_changed.emit(f"Project file not found: {project_file}")
                return False

            # Load project data with object_pairs_hook to preserve order
            with open(project_file, 'r', encoding='utf-8') as f:
                from collections import OrderedDict
                project_data = json.load(f, object_pairs_hook=OrderedDict)
            print(f"DEBUG PM load_project: loaded data keys={list(project_data.keys())}")

            # Validate project data
            if not self._validate_project_data(project_data):
                print(f"DEBUG PM load_project: validation FAILED")
                self.status_changed.emit("Invalid project file format")
                return False
            print(f"DEBUG PM load_project: validation passed")
            
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
       
    def save_project(self, project_path: Optional[Path] = None) -> bool:
        """
        Save the current project
        If auto-save-as-zip is enabled and project was loaded from zip,
        saves directly back to the zip file
        """
        print(f"💾 DEBUG: save_project called with path: {project_path}")
        
        if not self.current_project_path and not project_path:
            print("❌ DEBUG: No project to save")
            self.status_changed.emit("No project to save")
            return False
        
        try:
            # Check if we should save as zip
            if self._auto_save_as_zip and self._original_zip_path and not project_path:
                print(f"💾 Auto-saving to zip: {self._original_zip_path}")
                return self._save_to_zip()
            else:
                # Regular folder save
                return self._save_to_folder(project_path)
                
        except Exception as e:
            print(f"💥 DEBUG: Save failed with error: {e}")
            import traceback
            traceback.print_exc()
            self.status_changed.emit(f"Failed to save project: {str(e)}")
            return False

    def _save_to_folder(self, project_path: Optional[Path] = None) -> bool:
        """Save project to folder"""
        try:
            save_path = Path(project_path) if project_path else self.current_project_path
            project_file = save_path / self.PROJECT_FILE
            
            print(f"💾 DEBUG: Saving to {project_file}")
            
            # Update project metadata
            self.current_project_data["modified"] = datetime.now().isoformat()
            
            # Get latest asset data from asset manager
            if self.asset_manager:
                print("💾 DEBUG: Getting assets from asset manager...")
                # Use save_assets_to_project_data to preserve order
                self.asset_manager.save_assets_to_project_data(self.current_project_data)

                # DEBUG: Check room order being saved
                rooms_data = self.current_project_data.get('assets', {}).get('rooms', {})
                room_order = list(rooms_data.keys())
                print(f"💾 DEBUG: Saving room order: {room_order}")

                # DEBUG: Check what sprite values are actually being saved
                objects_data = self.current_project_data.get('assets', {}).get('objects', {})
                print(f"💾 DEBUG: Asset data updated. Objects in project: {list(objects_data.keys())}")
                for obj_name, obj_data in objects_data.items():
                    sprite = obj_data.get('sprite', 'none')
                    print(f"💾 DEBUG: Object '{obj_name}' has sprite: '{sprite}'")    
                    
            # Save to file
            with open(project_file, 'w', encoding='utf-8') as f:
                json.dump(self.current_project_data, f, indent=2, ensure_ascii=False, sort_keys=False)

            print(f"✅ DEBUG: Project saved successfully to {project_file}")
            
            # Update state
            self.is_dirty_flag = False
            if project_path:
                self.current_project_path = save_path
            
            self.project_saved.emit()
            self.dirty_changed.emit(False)
            self.status_changed.emit(f"Saved project: {save_path.name}")
            
            return True
            
        except Exception as e:
            print(f"💥 DEBUG: Folder save failed: {e}")
            import traceback
            traceback.print_exc()
            return False

    def _save_to_zip(self) -> bool:
        """Save project directly to zip file"""
        try:
            if not self._original_zip_path:
                print("No original zip path")
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
                print(f"✅ Project saved to zip: {self._original_zip_path}")
                return True
            else:
                # Restore backup on failure
                backup_path.replace(self._original_zip_path)
                print(f"❌ Failed to save to zip, backup restored")
                return False
                
        except Exception as e:
            print(f"Error saving to zip: {e}")
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
                print(f"🧹 Cleaning up temp extraction: {self._temp_extraction_dir}")
                shutil.rmtree(self._temp_extraction_dir, ignore_errors=True)
            
            self._original_zip_path = None
            self._temp_extraction_dir = None
            self._auto_save_as_zip = False
            self._zip_handler = None
            
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
        if not self.is_dirty:
            self.is_dirty = True
            self.dirty_changed.emit(True)
    
    def is_dirty(self) -> bool:
        """Check if the project has unsaved changes (compatibility method)"""
        return self.is_dirty_flag
    
    def get_is_dirty(self) -> bool:
        """Get dirty status as property"""
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
            print(f"Error in save_project_as: {e}")
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
    
    def on_asset_changed(self, *args):
        """Handle asset changes from asset manager"""
        self.mark_dirty()
    
    def update_asset(self, asset_type: str, asset_name: str, asset_data: Dict[str, Any]) -> bool:
        """Update an asset's data with proper type handling"""
        print(f"🔧 DEBUG: update_asset called with: {asset_type}, {asset_name}")
        print(f"🔧 DEBUG: Asset data keys: {list(asset_data.keys())}")
        
        try:
            # Validate asset manager exists
            if not self.asset_manager:
                print("❌ DEBUG: No asset manager available")
                self.status_changed.emit("No asset manager available")
                return False
            
            print(f"✅ DEBUG: Asset manager exists, checking for asset...")
            
            # Check if asset manager has assets cache
            if not hasattr(self.asset_manager, 'assets_cache'):
                print("❌ DEBUG: Asset manager has no assets_cache")
                self.status_changed.emit("Asset manager not properly initialized")
                return False
            
            print(f"📊 DEBUG: Assets cache contains: {list(self.asset_manager.assets_cache.keys())}")
            
            # Normalize asset type to plural form for storage
            # The asset_type parameter should already be plural (e.g., 'objects', 'rooms')
            # But the asset_data['asset_type'] field should be singular
            asset_type_plural = asset_type
            if not asset_type_plural.endswith('s'):
                # Convert singular to plural if needed
                if asset_type_plural in ['object', 'room', 'sprite', 'sound', 'background', 'script', 'font']:
                    asset_type_plural = asset_type_plural + 's'
                else:
                    # Unknown type, try adding 's'
                    asset_type_plural = asset_type_plural + 's'
            
            # Determine singular form for the asset_type field in data
            asset_type_singular = asset_type_plural[:-1] if asset_type_plural.endswith('s') else asset_type_plural
            
            # Special cases for irregular plurals
            plural_to_singular_map = {
                'sprites': 'sprite',
                'sounds': 'sound',
                'backgrounds': 'background',
                'objects': 'object',
                'rooms': 'room',
                'scripts': 'script',
                'fonts': 'font',
                'enemies': 'enemy',
                'entities': 'entity'
            }
            
            if asset_type_plural in plural_to_singular_map:
                asset_type_singular = plural_to_singular_map[asset_type_plural]
            
            print(f"🔧 DEBUG: Using plural form '{asset_type_plural}' for storage")
            print(f"🔧 DEBUG: Using singular form '{asset_type_singular}' for asset_type field")
            
            # Get existing asset from cache
            existing_asset = self.asset_manager.get_asset(asset_type_plural, asset_name)
            
            if existing_asset:
                print(f"✅ DEBUG: Found existing asset: {asset_name}")
                
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
                
                print(f"✅ DEBUG: Updated existing asset in cache")
                
                # Emit update signal
                self.asset_manager.asset_updated.emit(asset_type_plural, asset_name, existing_asset)
                
            else:
                # Asset doesn't exist, create new one
                print(f"⚠️ DEBUG: Asset '{asset_name}' not found in '{asset_type_plural}', creating new asset")
                
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
                        "instances": [],
                        "enable_views": False
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
                
                print(f"📝 DEBUG: New asset data created with keys: {list(new_asset_data.keys())}")
                
                # Initialize cache structure if needed
                if not self.asset_manager.assets_cache:
                    self.asset_manager.assets_cache = {}
                
                if asset_type_plural not in self.asset_manager.assets_cache:
                    self.asset_manager.assets_cache[asset_type_plural] = {}
                
                # Add to cache
                self.asset_manager.assets_cache[asset_type_plural][asset_name] = new_asset_data
                
                print(f"💾 DEBUG: Added to cache under '{asset_type_plural}' category")
                print(f"💾 DEBUG: Cache now has: {list(self.asset_manager.assets_cache.get(asset_type_plural, {}).keys())}")
                
                # Emit creation signal
                self.asset_manager.asset_imported.emit(asset_type_plural, asset_name, new_asset_data)
            
            # Mark project as dirty
            self.mark_dirty()
            
            print(f"✅ DEBUG: Successfully updated asset '{asset_name}' in category '{asset_type_plural}'")
            self.status_changed.emit(f"Updated {asset_name}")
            
            # Verify the update
            verification = self.asset_manager.get_asset(asset_type_plural, asset_name)
            if verification:
                print(f"✅ DEBUG: Verification successful - asset exists in cache")
                print(f"✅ DEBUG: Asset type field: {verification.get('asset_type', 'NOT SET')}")
            else:
                print(f"❌ DEBUG: Verification failed - asset not found in cache")
            
            return True
            
        except Exception as e:
            error_msg = f"Exception in update_asset: {str(e)}"
            print(f"💥 DEBUG: {error_msg}")
            print(f"💥 DEBUG: Exception type: {type(e)}")
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
        """Rename an asset"""
        try:
            if not self.asset_manager:
                return False
            
            result = self.asset_manager.rename_asset(asset_type, old_name, new_name)
            if result:
                self.mark_dirty()
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
                "fullscreen": False
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
            "imported": False
        }
        
        return project_data
    
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
            print("No project loaded")
            return False
        
        # Save project first
        if not self.save_project():
            print("Failed to save project before export")
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
                print("Failed to extract project")
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
            print(f"Error loading project from zip: {e}")
            import traceback
            traceback.print_exc()
            return False

    def is_project_from_zip(self) -> bool:
        """Check if current project was loaded from a .zip file"""
        return hasattr(self, '_original_zip_path') and self._original_zip_path is not None

    def get_original_zip_path(self) -> Path:
        """Get the original .zip path if project was loaded from zip"""
        return getattr(self, '_original_zip_path', None)
    
    def set_auto_save_as_zip(self, enabled: bool):
        """Enable/disable auto-save as zip"""
        self._auto_save_as_zip = enabled
        print(f"📦 Auto-save as zip: {'enabled' if enabled else 'disabled'}")

    def is_auto_save_as_zip(self) -> bool:
        """Check if auto-save as zip is enabled"""
        return self._auto_save_as_zip