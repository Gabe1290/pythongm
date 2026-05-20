#!/usr/bin/env python3
"""
Complete Fixed Config for PyGameMaker IDE
Fixes all JSON serialization and import errors
"""

import json
import sys
import base64
from pathlib import Path


def _safe_print(*args, **kwargs):
    """print() that never raises UnicodeEncodeError.

    This module prints decorative emojis (📄 ❌ 💾 🧹 ⚠️) and is loaded *at
    import time* — including transitively by ``runtime.game_runner`` inside
    exported games. On an end-user machine whose locale forces an ASCII
    ``sys.stdout`` (LC_ALL=C, no PEP 540 coercion, e.g. a stripped CI runner
    or a minimal locale-less desktop) any of those prints would raise
    ``UnicodeEncodeError`` and abort the whole import chain. Fall back to
    ``errors='replace'`` so decorative output degrades gracefully instead of
    killing the runtime.
    """
    try:
        print(*args, **kwargs)
    except UnicodeEncodeError:
        stream = kwargs.get('file', sys.stdout)
        sep = kwargs.get('sep', ' ')
        end = kwargs.get('end', '\n')
        enc = getattr(stream, 'encoding', None) or 'ascii'
        text = sep.join(str(a) for a in args) + end
        try:
            stream.write(text.encode(enc, errors='replace').decode(enc, errors='replace'))
        except Exception:
            pass  # decorative output; never let it break callers


class Config:
    """Complete Config class with JSON-safe saving and all compatibility methods"""

    _config_file = Path.home() / ".pygamemaker" / "config.json"
    _config_data = {}

    @classmethod
    def _clean_config_for_json(cls, data):
        """Remove non-JSON-serializable objects from config data"""
        if isinstance(data, dict):
            clean_data = {}
            for key, value in data.items():
                # Skip Qt objects and other non-serializable types
                if hasattr(value, '__class__'):
                    class_name = value.__class__.__name__
                    if class_name in ['QByteArray', 'QSize', 'QPoint', 'QRect', 'QMainWindow', 'QWidget']:
                        _safe_print(f"🧹 Skipping non-serializable object: {class_name}")
                        continue  # Skip Qt objects

                if isinstance(value, (dict, list)):
                    clean_data[key] = cls._clean_config_for_json(value)
                elif isinstance(value, (str, int, float, bool, type(None))):
                    clean_data[key] = value
                else:
                    # Skip other non-serializable objects
                    _safe_print(f"🧹 Skipping non-serializable type: {type(value).__name__}")
                    continue
            return clean_data
        elif isinstance(data, list):
            clean_list = []
            for item in data:
                if isinstance(item, (str, int, float, bool, type(None))):
                    clean_list.append(item)
                elif isinstance(item, (dict, list)):
                    clean_list.append(cls._clean_config_for_json(item))
                else:
                    _safe_print(f"🧹 Skipping non-serializable list item: {type(item).__name__}")
            return clean_list
        else:
            return data

    @classmethod
    def load(cls):
        """Load configuration"""
        try:
            cls._config_file.parent.mkdir(exist_ok=True)

            if cls._config_file.exists():
                with open(cls._config_file, 'r') as f:
                    loaded_data = json.load(f)

                # Merge with defaults
                cls._config_data = {
                    "version": "0.4",
                    "recent_projects": [],
                    "window": {"width": 1200, "height": 800, "x": 100, "y": 100},
                    "ui": {"theme": "default"},
                    **loaded_data  # Override with loaded data
                }
            else:
                cls._config_data = {
                    "version": "0.4",
                    "recent_projects": [],
                    "window": {"width": 1200, "height": 800, "x": 100, "y": 100},
                    "ui": {"theme": "default"}
                }
                _safe_print("📄 Created new config with defaults")

            return cls._config_data

        except Exception as e:
            _safe_print(f"❌ Config load error: {e}")
            cls._config_data = {
                "version": "0.4",
                "recent_projects": [],
                "window": {"width": 1200, "height": 800}
            }
            return cls._config_data

    @classmethod
    def save(cls, config_data=None):
        """Save configuration with JSON-safe filtering"""
        try:
            if config_data:
                cls._config_data = config_data

            cls._config_file.parent.mkdir(exist_ok=True)

            # Clean the config data before saving
            clean_data = cls._clean_config_for_json(cls._config_data)

            with open(cls._config_file, 'w') as f:
                json.dump(clean_data, f, indent=2)

            return True

        except Exception as e:
            _safe_print(f"❌ Config save error: {e}")
            return False

    @classmethod
    def get(cls, key, default=None):
        """Get config value (handles QByteArray deserialization)"""
        # Check if there's a base64-encoded version
        b64_key = f"{key}_b64"
        if b64_key in cls._config_data:
            return cls._deserialize_qbytearray(cls._config_data[b64_key])

        return cls._config_data.get(key, default)

    @classmethod
    def _serialize_qbytearray(cls, qbytearray):
        """Convert QByteArray to base64 string for JSON serialization"""
        try:
            # Convert QByteArray to bytes, then to base64 string
            return base64.b64encode(bytes(qbytearray)).decode('utf-8')
        except Exception as e:
            _safe_print(f"❌ Error serializing QByteArray: {e}")
            return None

    @classmethod
    def _deserialize_qbytearray(cls, b64_string):
        """Convert base64 string back to QByteArray"""
        try:
            from PySide6.QtCore import QByteArray
            data = base64.b64decode(b64_string)
            return QByteArray(data)
        except Exception as e:
            _safe_print(f"❌ Error deserializing QByteArray: {e}")
            return None

    @classmethod
    def set(cls, key, value):
        """Set config value (handles QByteArray and other types)"""
        # Handle QByteArray objects
        if hasattr(value, '__class__') and value.__class__.__name__ == 'QByteArray':
            serialized = cls._serialize_qbytearray(value)
            if serialized:
                cls._config_data[f"{key}_b64"] = serialized
                _safe_print(f"💾 Saved {key} as base64 string")
            return

        # Check if value is JSON-serializable
        try:
            json.dumps(value)  # Test serialization
            cls._config_data[key] = value
        except (TypeError, ValueError):
            _safe_print(f"⚠️  Skipping non-JSON-serializable value for key '{key}': {type(value).__name__}")

    @classmethod
    def get_recent_projects(cls):
        """Get recent projects"""
        return cls._config_data.get("recent_projects", [])

    @classmethod
    def add_recent_project(cls, project_path):
        """Add recent project"""
        recent = cls.get_recent_projects()

        if project_path in recent:
            recent.remove(project_path)

        recent.insert(0, project_path)
        recent = recent[:10]  # Keep last 10

        cls.set("recent_projects", recent)

    @classmethod
    def get_window_config(cls):
        """Get window configuration"""
        return cls._config_data.get("window", {
            "width": 1200,
            "height": 800,
            "x": 100,
            "y": 100,
            "maximized": False
        })

    @classmethod
    def set_window_config(cls, width, height, x, y, maximized=False):
        """Set window configuration"""
        window_config = {
            "width": int(width),
            "height": int(height),
            "x": int(x),
            "y": int(y),
            "maximized": bool(maximized)
        }
        cls.set("window", window_config)

    @classmethod
    def get_font_config(cls):
        """Get font configuration"""
        font_config = cls._config_data.get('font', {})
        return {
            'family': font_config.get('family', ''),  # Empty means use system default
            'size': font_config.get('size', 10),
        }

    @classmethod
    def set_font_config(cls, family=None, size=10):
        """Set font configuration"""
        if 'font' not in cls._config_data:
            cls._config_data['font'] = {}

        if family:
            cls._config_data['font']['family'] = family
        cls._config_data['font']['size'] = size

        cls.save()

    @classmethod
    def get_editor_config(cls):
        """Get editor configuration"""
        editor_config = cls._config_data.get('editor', {})
        return {
            'auto_save_enabled': editor_config.get('auto_save_enabled', True),
            'auto_save_interval': editor_config.get('auto_save_interval', 5),
            'show_grid': editor_config.get('show_grid', True),
            'grid_size': editor_config.get('grid_size', 32),
            'snap_to_grid': editor_config.get('snap_to_grid', True),
            'show_collision_boxes': editor_config.get('show_collision_boxes', False),
        }

    @classmethod
    def set_editor_config(cls, **kwargs):
        """Set editor configuration"""
        if 'editor' not in cls._config_data:
            cls._config_data['editor'] = {}

        cls._config_data['editor'].update(kwargs)
        cls.save()

    @classmethod
    def get_project_config(cls):
        """Get project configuration"""
        project_config = cls._config_data.get('project', {})
        default_projects_dir = str(Path.home() / "PyGameMaker Projects")

        return {
            'default_projects_dir': project_config.get('default_projects_dir', default_projects_dir),
            'recent_projects_limit': project_config.get('recent_projects_limit', 10),
            'create_backup_on_save': project_config.get('create_backup_on_save', True),
        }

    @classmethod
    def set_project_config(cls, **kwargs):
        """Set project configuration"""
        if 'project' not in cls._config_data:
            cls._config_data['project'] = {}

        cls._config_data['project'].update(kwargs)
        cls.save()

    @classmethod
    def get_appearance_config(cls):
        """Get appearance configuration"""
        appearance_config = cls._config_data.get('appearance', {})
        return {
            'theme': appearance_config.get('theme', 'default'),
            'ui_scale': appearance_config.get('ui_scale', 1.0),
            'show_tooltips': appearance_config.get('show_tooltips', True),
        }

    @classmethod
    def set_appearance_config(cls, **kwargs):
        """Set appearance configuration"""
        if 'appearance' not in cls._config_data:
            cls._config_data['appearance'] = {}

        cls._config_data['appearance'].update(kwargs)
        cls.save()

    @classmethod
    def get_advanced_config(cls):
        """Get advanced configuration"""
        advanced_config = cls._config_data.get('advanced', {})
        return {
            'debug_mode': advanced_config.get('debug_mode', False),
            'max_undo_steps': advanced_config.get('max_undo_steps', 50),
            'console_output': advanced_config.get('console_output', True),
        }

    @classmethod
    def set_advanced_config(cls, **kwargs):
        """Set advanced configuration"""
        if 'advanced' not in cls._config_data:
            cls._config_data['advanced'] = {}

        cls._config_data['advanced'].update(kwargs)
        cls.save()

# Initialize config on import
Config.load()


# Create a config_manager instance for compatibility
class ConfigManager:
    """Wrapper for Config class to provide config_manager compatibility"""

    def __init__(self):
        self.config = Config._config_data

    def save_config(self):
        """Save configuration"""
        return Config.save()

    def load_config(self):
        """Load configuration"""
        return Config.load()




# Create global instance for compatibility
config_manager = ConfigManager()


# Utility functions for compatibility
def load_config():
    """Load configuration"""
    return Config.load()


def save_config(config_data=None):
    """Save configuration"""
    return Config.save(config_data)


def save_on_exit():
    """Save configuration on exit - COMPLETELY FIXED VERSION"""
    try:
        success = Config.save()
        if success:
            _safe_print("💾 Configuration saved on exit")
        else:
            _safe_print("⚠️  Configuration save had issues but completed")
    except Exception as e:
        _safe_print(f"❌ Error saving config on exit: {e}")


# Export all needed symbols
__all__ = [
    'Config',
    'config_manager',
    'save_on_exit',
    'load_config',
    'save_config',
    'ConfigManager'
]
