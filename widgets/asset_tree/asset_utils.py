#!/usr/bin/env python3
"""
Asset Utilities for PyGameMaker IDE
Pure utility functions for asset management - no UI dependencies
"""

import json
from pathlib import Path
from typing import Dict, Optional, Tuple, List


def validate_asset_name(name: str) -> Tuple[bool, str]:
    """
    Validate asset name for common issues
    Returns (is_valid, error_message)
    """
    if not name or not name.strip():
        return False, "Asset name cannot be empty."
    
    name = name.strip()
    
    # Check for invalid characters (common ones that cause file system issues)
    invalid_chars = ['<', '>', ':', '"', '/', '\\', '|', '?', '*']
    found_invalid = [char for char in invalid_chars if char in name]
    
    if found_invalid:
        return False, f"Asset name contains invalid characters: {', '.join(found_invalid)}"
    
    # Check for reserved names (Windows)
    reserved_names = [
        'CON', 'PRN', 'AUX', 'NUL',
        'COM1', 'COM2', 'COM3', 'COM4', 'COM5', 'COM6', 'COM7', 'COM8', 'COM9',
        'LPT1', 'LPT2', 'LPT3', 'LPT4', 'LPT5', 'LPT6', 'LPT7', 'LPT8', 'LPT9'
    ]
    
    if name.upper() in reserved_names:
        return False, f"'{name}' is a reserved system name."
    
    # Check length (reasonable limit)
    if len(name) > 100:
        return False, "Asset name is too long (maximum 100 characters)."
    
    # Check for leading/trailing dots or spaces (can cause issues)
    if name.startswith('.') or name.endswith('.'):
        return False, "Asset name cannot start or end with a dot."
    
    if name.startswith(' ') or name.endswith(' '):
        return False, "Asset name cannot start or end with a space."
    
    return True, "Valid"


def get_asset_icon_emoji(asset_type: str) -> str:
    """
    Get emoji icon for asset type
    Returns emoji string for display
    """
    icon_map = {
        "sprites": "🖼️",
        "sounds": "🔊", 
        "backgrounds": "🖼️",
        "objects": "⚙️",
        "rooms": "🏠",
        "scripts": "📜",
        "fonts": "🔤",
        "data": "📄"
    }
    return icon_map.get(asset_type.lower(), "📄")


def get_asset_type_singular(asset_type_plural: str) -> str:
    """
    Convert plural asset type to singular
    e.g., 'sprites' -> 'sprite'
    """
    type_map = {
        'sprites': 'sprite',
        'sounds': 'sound', 
        'backgrounds': 'background',
        'objects': 'object',
        'rooms': 'room',
        'scripts': 'script',
        'fonts': 'font'
    }
    return type_map.get(asset_type_plural.lower(), asset_type_plural.rstrip('s'))


def get_asset_type_plural(asset_type_singular: str) -> str:
    """
    Convert singular asset type to plural
    e.g., 'sprite' -> 'sprites'
    """
    type_map = {
        'sprite': 'sprites',
        'sound': 'sounds', 
        'background': 'backgrounds',
        'object': 'objects',
        'room': 'rooms',
        'script': 'scripts',
        'font': 'fonts'
    }
    return type_map.get(asset_type_singular.lower(), asset_type_singular + 's')


def load_project_data(project_file: Path) -> Optional[Dict]:
    """
    Load project data from JSON file
    Returns project data dict or None if failed
    """
    try:
        if project_file.exists():
            with open(project_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        else:
            print(f"Project file does not exist: {project_file}")
            return None
    except json.JSONDecodeError as e:
        print(f"JSON decode error in {project_file}: {e}")
        return None
    except Exception as e:
        print(f"Error loading project file {project_file}: {e}")
        return None


def save_project_data(project_file: Path, project_data: Dict) -> bool:
    """
    Save project data to JSON file
    Returns True if successful, False otherwise
    """
    try:
        # Ensure parent directory exists
        project_file.parent.mkdir(parents=True, exist_ok=True)
        
        with open(project_file, 'w', encoding='utf-8') as f:
            json.dump(project_data, f, indent=2, ensure_ascii=False)
        
        return True
    except Exception as e:
        print(f"Error saving project file {project_file}: {e}")
        return False


def get_supported_file_extensions(asset_type: str) -> List[str]:
    """
    Get supported file extensions for an asset type
    Returns list of extensions (with dots)
    """
    extension_map = {
        'sprites': ['.png', '.jpg', '.jpeg', '.bmp', '.gif', '.tga'],
        'sounds': ['.wav', '.mp3', '.ogg', '.m4a', '.flac'],
        'backgrounds': ['.png', '.jpg', '.jpeg', '.bmp', '.gif'],
        'scripts': ['.py', '.gml', '.txt'],
        'fonts': ['.ttf', '.otf', '.woff', '.woff2'],
        'data': ['.json', '.xml', '.csv', '.txt']
    }
    return extension_map.get(asset_type.lower(), [])


def is_supported_file_type(file_path: str, asset_type: str) -> bool:
    """
    Check if a file type is supported for an asset type
    """
    file_ext = Path(file_path).suffix.lower()
    supported_exts = get_supported_file_extensions(asset_type)
    return file_ext in supported_exts


def get_asset_file_filter(asset_type: str) -> str:
    """
    Get file dialog filter string for an asset type
    e.g., "Image Files (*.png *.jpg *.jpeg);;All Files (*)"
    """
    extensions = get_supported_file_extensions(asset_type)
    
    if not extensions:
        return "All Files (*)"
    
    # Create the filter string
    ext_pattern = ' '.join(f'*{ext}' for ext in extensions)
    
    type_names = {
        'sprites': 'Image Files',
        'sounds': 'Audio Files',
        'backgrounds': 'Image Files',
        'scripts': 'Script Files',
        'fonts': 'Font Files',
        'data': 'Data Files'
    }
    
    type_name = type_names.get(asset_type.lower(), f'{asset_type.title()} Files')
    
    return f"{type_name} ({ext_pattern});;All Files (*)"


def sanitize_asset_name(name: str) -> str:
    """
    Sanitize a filename to be a valid asset name
    Removes or replaces problematic characters
    """
    if not name:
        return "unnamed_asset"
    
    # Remove invalid characters
    invalid_chars = ['<', '>', ':', '"', '/', '\\', '|', '?', '*']
    sanitized = name
    
    for char in invalid_chars:
        sanitized = sanitized.replace(char, '_')
    
    # Remove leading/trailing whitespace and dots
    sanitized = sanitized.strip(' .')
    
    # Ensure not empty after sanitization
    if not sanitized:
        return "unnamed_asset"
    
    # Limit length
    if len(sanitized) > 100:
        sanitized = sanitized[:100]
    
    return sanitized


def get_asset_display_name(asset_name: str, asset_type: str, imported: bool = True) -> str:
    """
    Get the display name for an asset in the tree
    Includes emoji icon and import status
    """
    icon = get_asset_icon_emoji(asset_type)
    
    if imported:
        return f"{icon} {asset_name}"
    else:
        return f"❌ {asset_name} (not imported)"


def create_asset_data_template(name: str, asset_type: str, file_path: str = None) -> Dict:
    """
    Create a template asset data dictionary with standard fields
    """
    from datetime import datetime
    
    asset_data = {
        'name': name,
        'asset_type': get_asset_type_singular(asset_type),
        'imported': file_path is not None,
        'created_date': datetime.now().isoformat()
    }
    
    if file_path:
        asset_data['file_path'] = file_path
        asset_data['project_path'] = file_path  # Will be updated with full path
    
    return asset_data


def extract_asset_name_from_path(file_path: str) -> str:
    """
    Extract asset name from file path (filename without extension)
    Also sanitizes the name
    """
    file_name = Path(file_path).stem  # Filename without extension
    return sanitize_asset_name(file_name)


def find_project_file(start_path: Path) -> Optional[Path]:
    """
    Find the project.json file by searching up the directory tree
    Returns Path to project.json or None if not found
    """
    current = start_path
    
    # Search up to 5 levels up
    for _ in range(5):
        project_file = current / "project.json"
        if project_file.exists():
            return project_file
        
        parent = current.parent
        if parent == current:  # Reached root
            break
        current = parent
    
    return None


def get_asset_categories() -> List[str]:
    """
    Get the standard asset categories
    """
    return [
        "sprites",
        "sounds", 
        "backgrounds",
        "objects",
        "rooms",
        "scripts",
        "fonts"
    ]


def is_valid_asset_category(category: str) -> bool:
    """
    Check if a category is a valid asset category
    """
    return category.lower() in get_asset_categories()