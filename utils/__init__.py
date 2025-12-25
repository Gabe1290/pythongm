#!/usr/bin/env python3
# ==============================================================================
# UTILS PACKAGE: utils/__init__.py
# Location: /project_root/utils/__init__.py  
# ==============================================================================
"""
Utilities package for GameMaker-style IDE
Location: utils/__init__.py

Common utilities and helper functions:
- File operations
- Image processing
- JSON handling
- Path utilities
- Logging setup
"""

import json
import os
import shutil
from pathlib import Path
from typing import Dict, List, Optional, Union
from PIL import Image
import logging

# Package version
__version__ = "1.0.0"

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# =============================================================================
# PROJECT MANAGEMENT UTILITIES
# =============================================================================

class ProjectManager:
    """Handles project creation, loading, and saving operations"""
    
    @staticmethod
    def create_new_project(project_path: Union[str, Path], project_name: str) -> bool:
        """
        Create a new GameMaker-style project structure
        
        Args:
            project_path: Path where project should be created
            project_name: Name of the project
            
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            project_path = Path(project_path)
            project_dir = project_path / project_name
            
            # Create project directory structure
            directories = [
                'sprites',
                'sounds', 
                'backgrounds',
                'objects',
                'rooms',
                'scripts',
                'fonts',
                'extensions'
            ]
            
            for directory in directories:
                (project_dir / directory).mkdir(parents=True, exist_ok=True)
            
            # Create project.json
            project_data = {
                "name": project_name,
                "version": "1.0.0",
                "created": str(Path.ctime(project_dir)) if project_dir.exists() else "",
                "assets": {
                    "sprites": {},
                    "sounds": {},
                    "backgrounds": {},
                    "objects": {},
                    "rooms": {},
                    "scripts": {},
                    "fonts": {}
                },
                "settings": {
                    "window_width": 800,
                    "window_height": 600,
                    "fps": 60,
                    "fullscreen": False
                }
            }
            
            project_file = project_dir / "project.json"
            with open(project_file, 'w') as f:
                json.dump(project_data, f, indent=2)
                
            logger.info(f"Created new project: {project_dir}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to create project: {e}")
            return False
    
    @staticmethod
    def load_project(project_path: Union[str, Path]) -> Optional[Dict]:
        """
        Load project data from project.json
        
        Args:
            project_path: Path to project directory or project.json file
            
        Returns:
            Dict with project data or None if failed
        """
        try:
            project_path = Path(project_path)
            
            # If path is directory, look for project.json
            if project_path.is_dir():
                project_file = project_path / "project.json"
            else:
                project_file = project_path
                
            if not project_file.exists():
                logger.error(f"Project file not found: {project_file}")
                return None
                
            with open(project_file, 'r') as f:
                project_data = json.load(f)
                
            logger.info(f"Loaded project: {project_file}")
            return project_data
            
        except Exception as e:
            logger.error(f"Failed to load project: {e}")
            return None
    
    @staticmethod
    def save_project(project_path: Union[str, Path], project_data: Dict) -> bool:
        """
        Save project data to project.json
        
        Args:
            project_path: Path to project directory or project.json file
            project_data: Dictionary containing project data
            
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            project_path = Path(project_path)
            
            # If path is directory, save to project.json
            if project_path.is_dir():
                project_file = project_path / "project.json"
            else:
                project_file = project_path
                
            with open(project_file, 'w') as f:
                json.dump(project_data, f, indent=2)
                
            logger.info(f"Saved project: {project_file}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to save project: {e}")
            return False

# =============================================================================
# ASSET MANAGEMENT UTILITIES  
# =============================================================================

class AssetManager:
    """Handles asset import, export, and management operations"""
    
    SUPPORTED_IMAGE_FORMATS = {'.png', '.jpg', '.jpeg', '.bmp', '.gif', '.tiff'}
    SUPPORTED_AUDIO_FORMATS = {'.wav', '.mp3', '.ogg', '.m4a', '.flac'}
    
    @staticmethod
    def import_asset(source_path: Union[str, Path], 
                    project_path: Union[str, Path], 
                    asset_type: str, 
                    asset_name: Optional[str] = None) -> Optional[Dict]:
        """
        Import an asset into the project
        
        Args:
            source_path: Path to source asset file
            project_path: Path to project directory  
            asset_type: Type of asset (sprite, sound, background, etc.)
            asset_name: Optional custom name for asset
            
        Returns:
            Dict with asset info or None if failed
        """
        try:
            source_path = Path(source_path)
            project_path = Path(project_path)
            
            if not source_path.exists():
                logger.error(f"Source file not found: {source_path}")
                return None
                
            # Generate asset name if not provided
            if not asset_name:
                asset_name = source_path.stem
                
            # Create asset directory if it doesn't exist
            asset_dir = project_path / asset_type
            asset_dir.mkdir(exist_ok=True)
            
            # Copy file to project
            target_path = asset_dir / source_path.name
            shutil.copy2(source_path, target_path)
            
            # Create asset data
            asset_data = {
                'name': asset_name,
                'asset_type': asset_type.rstrip('s'),  # Remove plural 's'
                'file_path': f"{asset_type}/{source_path.name}",
                'project_path': str(target_path),
                'imported': True,
                'created': str(Path.ctime(target_path)),
            }
            
            # Add type-specific properties
            if asset_type in ['sprites', 'backgrounds']:
                try:
                    with Image.open(target_path) as img:
                        asset_data.update({
                            'width': img.width,
                            'height': img.height,
                            'format': img.format
                        })
                except Exception as e:
                    logger.warning(f"Could not read image properties: {e}")
                    
            logger.info(f"Imported {asset_type} asset: {asset_name}")
            return asset_data
            
        except Exception as e:
            logger.error(f"Failed to import asset: {e}")
            return None
    
    @staticmethod
    def validate_asset_file(file_path: Union[str, Path], asset_type: str) -> bool:
        """
        Validate if a file is suitable for the given asset type
        
        Args:
            file_path: Path to file
            asset_type: Expected asset type
            
        Returns:
            bool: True if valid, False otherwise
        """
        try:
            file_path = Path(file_path)
            
            if not file_path.exists():
                return False
                
            extension = file_path.suffix.lower()
            
            if asset_type in ['sprites', 'backgrounds']:
                return extension in AssetManager.SUPPORTED_IMAGE_FORMATS
            elif asset_type == 'sounds':
                return extension in AssetManager.SUPPORTED_AUDIO_FORMATS
            else:
                return True  # Other asset types are more flexible
                
        except Exception:
            return False
    
    @staticmethod
    def get_asset_preview_info(asset_data: Dict) -> Dict:
        """
        Get preview information for an asset
        
        Args:
            asset_data: Asset data dictionary
            
        Returns:
            Dict with preview info
        """
        preview_info = {
            'name': asset_data.get('name', 'Unknown'),
            'type': asset_data.get('asset_type', 'Unknown'),
            'imported': asset_data.get('imported', False),
            'preview_text': 'No preview available'
        }
        
        asset_type = asset_data.get('asset_type', '')
        
        if asset_type == 'sprite':
            width = asset_data.get('width', 'Unknown')
            height = asset_data.get('height', 'Unknown')
            preview_info['preview_text'] = f"Sprite Preview\n({width}x{height})"
            
        elif asset_type == 'sound':
            format_type = asset_data.get('format', 'Unknown')
            preview_info['preview_text'] = f"Sound Preview\n♪ {format_type} Audio ♪"
            
        elif asset_type == 'background':
            width = asset_data.get('width', 'Unknown') 
            height = asset_data.get('height', 'Unknown')
            preview_info['preview_text'] = f"Background Preview\n({width}x{height})"
            
        elif asset_type == 'object':
            preview_info['preview_text'] = "Object Preview\nEvents & Actions"
            
        return preview_info

# =============================================================================
# UI HELPER UTILITIES
# =============================================================================

class UIHelpers:
    """UI utility functions for the IDE"""
    
    @staticmethod
    def format_file_size(size_bytes: int) -> str:
        """Format file size in human readable format"""
        if size_bytes == 0:
            return "0 B"
        
        size_names = ["B", "KB", "MB", "GB"]
        i = 0
        while size_bytes >= 1024 and i < len(size_names) - 1:
            size_bytes /= 1024.0
            i += 1
            
        return f"{size_bytes:.1f} {size_names[i]}"
    
    @staticmethod
    def get_asset_icon_text(asset_type: str) -> str:
        """Get icon text for asset type"""
        icons = {
            'sprites': '🖼️',
            'sounds': '🔊', 
            'backgrounds': '🌄',
            'objects': '📦',
            'rooms': '🏠',
            'scripts': '📜',
            'fonts': '🔤'
        }
        return icons.get(asset_type, '📄')
    
    @staticmethod
    def get_event_color(event_type: str) -> str:
        """Get color for different event types"""
        colors = {
            'create': '#e8f4e8',
            'step': '#e8e8f4', 
            'collision': '#f4e8e8',
            'keyboard': '#f4f4e8',
            'mouse': '#f0e8f4',
            'destroy': '#f0f0f0'
        }
        return colors.get(event_type.lower(), '#f0f0f0')

# =============================================================================
# FILE SYSTEM UTILITIES
# =============================================================================

def ensure_directory(path: Union[str, Path]) -> Path:
    """Ensure directory exists, create if it doesn't"""
    path = Path(path)
    path.mkdir(parents=True, exist_ok=True)
    return path

def safe_filename(filename: str) -> str:
    """Convert filename to safe format"""
    invalid_chars = '<>:"/\\|?*'
    for char in invalid_chars:
        filename = filename.replace(char, '_')
    return filename

def find_project_files(search_path: Union[str, Path]) -> List[Path]:
    """Find all project.json files in directory tree"""
    search_path = Path(search_path)
    project_files = []
    
    for root, dirs, files in os.walk(search_path):
        if 'project.json' in files:
            project_files.append(Path(root) / 'project.json')
            
    return project_files

def get_relative_path(file_path: Union[str, Path], base_path: Union[str, Path]) -> Path:
    """Get relative path from base path"""
    try:
        return Path(file_path).relative_to(Path(base_path))
    except ValueError:
        return Path(file_path)

# =============================================================================
# CONFIGURATION UTILITIES
# =============================================================================

class Config:
    """Configuration management for the IDE"""
    
    DEFAULT_CONFIG = {
        'window': {
            'width': 1200,
            'height': 800,
            'maximized': False
        },
        'panels': {
            'asset_width': 250,
            'properties_width': 350,
            'events_width': 600
        },
        'editor': {
            'font_size': 12,
            'theme': 'default',
            'auto_save': True
        },
        'project': {
            'recent_projects': [],
            'max_recent': 10
        }
    }
    
    @staticmethod
    def get_config_path() -> Path:
        """Get path to config file"""
        config_dir = Path.home() / '.gamemaker_ide'
        config_dir.mkdir(exist_ok=True)
        return config_dir / 'config.json'
    
    @staticmethod
    def load_config() -> Dict:
        """Load configuration from file"""
        config_path = Config.get_config_path()
        
        if config_path.exists():
            try:
                with open(config_path, 'r') as f:
                    loaded_config = json.load(f)
                    
                # Merge with defaults
                config = Config.DEFAULT_CONFIG.copy()
                config.update(loaded_config)
                return config
                
            except Exception as e:
                logger.error(f"Error loading config: {e}")
                
        return Config.DEFAULT_CONFIG.copy()
    
    @staticmethod
    def save_config(config: Dict) -> bool:
        """Save configuration to file"""
        try:
            config_path = Config.get_config_path()
            
            # Filter out non-serializable values (like Qt objects)
            serializable_config = {}
            for key, value in config.items():
                try:
                    # Test if the value can be serialized to JSON
                    json.dumps(value)
                    serializable_config[key] = value
                except (TypeError, ValueError):
                    # Skip non-serializable values silently
                    # This will filter out QByteArray objects from window geometry/state
                    continue
            
            with open(config_path, 'w') as f:
                json.dump(serializable_config, f, indent=2)
                
            return True
            
        except Exception as e:
            logger.error(f"Error saving config: {e}")
            return False

# =============================================================================
# EXPORT UTILITIES
# =============================================================================

def export_project_summary(project_data: Dict, output_path: Union[str, Path]) -> bool:
    """Export project summary to text file"""
    try:
        output_path = Path(output_path)
        
        with open(output_path, 'w') as f:
            f.write(f"Project: {project_data.get('name', 'Unknown')}\n")
            f.write(f"Version: {project_data.get('version', '1.0.0')}\n")
            f.write(f"Created: {project_data.get('created', 'Unknown')}\n\n")
            
            assets = project_data.get('assets', {})
            f.write("Assets:\n")
            f.write("-" * 20 + "\n")
            
            for asset_type, asset_list in assets.items():
                f.write(f"{asset_type.title()}: {len(asset_list)} items\n")
                for asset_name in asset_list.keys():
                    f.write(f"  - {asset_name}\n")
                f.write("\n")
                
            settings = project_data.get('settings', {})
            f.write("Settings:\n")
            f.write("-" * 20 + "\n")
            for key, value in settings.items():
                f.write(f"{key}: {value}\n")
                
        return True
        
    except Exception as e:
        logger.error(f"Error exporting project summary: {e}")
        return False

# =============================================================================
# PACKAGE EXPORTS
# =============================================================================

# Export main classes and functions
__all__ = [
    'ProjectManager',
    'AssetManager', 
    'UIHelpers',
    'Config',
    'ensure_directory',
    'safe_filename',
    'find_project_files',
    'get_relative_path',
    'export_project_summary',
    'logger'
]

# Initialize package
logger.info(f"GameMaker IDE Utils v{__version__} loaded")
