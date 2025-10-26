#!/usr/bin/env python3
"""
Complete Fixed Config for PyGameMaker IDE
Fixes all JSON serialization and import errors
"""

import json
from pathlib import Path
from typing import Dict, Any


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
                        print(f"🧹 Skipping non-serializable object: {class_name}")
                        continue  # Skip Qt objects
                
                if isinstance(value, (dict, list)):
                    clean_data[key] = cls._clean_config_for_json(value)
                elif isinstance(value, (str, int, float, bool, type(None))):
                    clean_data[key] = value
                else:
                    # Skip other non-serializable objects
                    print(f"🧹 Skipping non-serializable type: {type(value).__name__}")
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
                    print(f"🧹 Skipping non-serializable list item: {type(item).__name__}")
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
                print("📄 Created new config with defaults")
            
            return cls._config_data
            
        except Exception as e:
            print(f"❌ Config load error: {e}")
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
            print(f"❌ Config save error: {e}")
            return False
    
    @classmethod
    def get(cls, key, default=None):
        """Get config value"""
        return cls._config_data.get(key, default)
    
    @classmethod
    def set(cls, key, value):
        """Set config value (only JSON-safe values)"""
        # Check if value is JSON-serializable
        try:
            json.dumps(value)  # Test serialization
            cls._config_data[key] = value
        except (TypeError, ValueError):
            print(f"⚠️  Skipping non-JSON-serializable value for key '{key}': {type(value).__name__}")
    
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
    
    def save_window_geometry(self, window):
        """Save window geometry (JSON-safe version)"""
        try:
            # Only save basic geometry info, skip Qt objects
            Config.set_window_config(
                width=window.width(),
                height=window.height(),
                x=window.x(),
                y=window.y(),
                maximized=window.isMaximized()
            )
            print("💾 Window geometry saved")
        except Exception as e:
            print(f"❌ Error saving window geometry: {e}")
    
    def restore_window_geometry(self, window):
        """Restore window geometry"""
        try:
            window_config = Config.get_window_config()
            
            window.resize(window_config["width"], window_config["height"])
            window.move(window_config["x"], window_config["y"])
            
            if window_config.get("maximized", False):
                window.showMaximized()
            
            print("🔄 Window geometry restored")
        except Exception as e:
            print(f"❌ Error restoring window geometry: {e}")


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
            print("💾 Configuration saved on exit")
        else:
            print("⚠️  Configuration save had issues but completed")
    except Exception as e:
        print(f"❌ Error saving config on exit: {e}")


# Export all needed symbols
__all__ = [
    'Config', 
    'config_manager', 
    'save_on_exit', 
    'load_config', 
    'save_config',
    'ConfigManager'
]
