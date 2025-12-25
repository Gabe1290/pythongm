#!/usr/bin/env python3
"""
Plugin Loader for PyGameMaker IDE
Allows loading custom events and actions from plugin files
"""

import importlib.util
import sys
from pathlib import Path
from typing import Dict, List, Optional
from dataclasses import dataclass

from .event_types import EVENT_TYPES, EventType
from .action_types import ACTION_TYPES, ActionType


@dataclass
class PluginInfo:
    """Information about a loaded plugin"""
    name: str
    version: str
    author: str
    description: str
    events_count: int = 0
    actions_count: int = 0
    file_path: Optional[Path] = None


class PluginLoader:
    """Loads and manages event/action plugins"""

    def __init__(self, action_executor=None):
        self.action_executor = action_executor
        self.loaded_plugins: List[PluginInfo] = []
        self.plugin_modules = []

    def load_plugins_from_directory(self, plugin_dir: Path):
        """Load all plugins from a directory

        Args:
            plugin_dir: Path to directory containing plugin files

        Returns:
            Number of plugins loaded
        """
        if not plugin_dir.exists():
            print(f"Plugin directory not found: {plugin_dir}")
            # Don't create the directory - just skip loading plugins
            return 0

        plugin_files = list(plugin_dir.glob("*.py"))
        if not plugin_files:
            print(f"No plugin files found in {plugin_dir}")
            return 0

        loaded_count = 0
        for plugin_file in plugin_files:
            # Skip __init__.py and __pycache__
            if plugin_file.name.startswith('__'):
                continue

            if self.load_plugin(plugin_file):
                loaded_count += 1

        return loaded_count

    def load_plugin(self, plugin_file: Path) -> bool:
        """Load a single plugin file

        Args:
            plugin_file: Path to plugin file

        Returns:
            True if plugin loaded successfully, False otherwise
        """
        try:
            # Import the plugin module
            module_name = f"plugin_{plugin_file.stem}"
            spec = importlib.util.spec_from_file_location(module_name, plugin_file)

            if spec is None or spec.loader is None:
                print(f"❌ Could not load plugin spec: {plugin_file.name}")
                return False

            module = importlib.util.module_from_spec(spec)
            sys.modules[module_name] = module
            spec.loader.exec_module(module)

            # Get plugin info
            plugin_info = self._extract_plugin_info(module, plugin_file)

            # Load events from plugin
            events_loaded = 0
            if hasattr(module, 'PLUGIN_EVENTS'):
                events_loaded = self._load_events(module.PLUGIN_EVENTS)
                plugin_info.events_count = events_loaded

            # Load actions from plugin
            actions_loaded = 0
            if hasattr(module, 'PLUGIN_ACTIONS'):
                actions_loaded = self._load_actions(module.PLUGIN_ACTIONS)
                plugin_info.actions_count = actions_loaded

            # Load action handlers from plugin
            if hasattr(module, 'PluginExecutor'):
                self._register_action_handlers(module.PluginExecutor)

            # Store plugin info
            self.loaded_plugins.append(plugin_info)
            self.plugin_modules.append(module)

            print(f"✅ Loaded plugin: {plugin_info.name} v{plugin_info.version}")
            print(f"   Events: {events_loaded}, Actions: {actions_loaded}")

            return True

        except Exception as e:
            print(f"❌ Error loading plugin {plugin_file.name}: {e}")
            import traceback
            traceback.print_exc()
            return False

    def _extract_plugin_info(self, module, plugin_file: Path) -> PluginInfo:
        """Extract plugin metadata from module"""
        return PluginInfo(
            name=getattr(module, 'PLUGIN_NAME', plugin_file.stem),
            version=getattr(module, 'PLUGIN_VERSION', '1.0.0'),
            author=getattr(module, 'PLUGIN_AUTHOR', 'Unknown'),
            description=getattr(module, 'PLUGIN_DESCRIPTION', ''),
            file_path=plugin_file
        )

    def _load_events(self, plugin_events: Dict[str, EventType]) -> int:
        """Load events from plugin into global EVENT_TYPES"""
        count = 0
        for event_name, event_type in plugin_events.items():
            if event_name in EVENT_TYPES:
                print(f"⚠️  Event '{event_name}' already exists, skipping...")
                continue

            EVENT_TYPES[event_name] = event_type
            count += 1
            print(f"   📌 Registered event: {event_name}")

        return count

    def _load_actions(self, plugin_actions: Dict[str, ActionType]) -> int:
        """Load actions from plugin into global ACTION_TYPES"""
        count = 0
        for action_name, action_type in plugin_actions.items():
            if action_name in ACTION_TYPES:
                print(f"⚠️  Action '{action_name}' already exists, skipping...")
                continue

            ACTION_TYPES[action_name] = action_type
            count += 1
            print(f"   📌 Registered action: {action_name}")

        return count

    def _register_action_handlers(self, executor_class):
        """Register action handlers from plugin executor"""
        if not self.action_executor:
            print("⚠️  No action executor available, handlers not registered")
            return

        # Create an instance of the plugin executor
        plugin_executor = executor_class()

        # Register each handler method
        for attr_name in dir(plugin_executor):
            if attr_name.startswith('execute_') and attr_name.endswith('_action'):
                action_name = attr_name[8:-7]  # Extract action name
                method = getattr(plugin_executor, attr_name)

                if callable(method):
                    self.action_executor.register_custom_action(action_name, method)

    def get_plugin_info(self) -> List[PluginInfo]:
        """Get information about all loaded plugins"""
        return self.loaded_plugins.copy()

    def reload_plugins(self, plugin_dir: Path):
        """Reload all plugins from directory

        Warning: This may cause issues with already-created actions.
        Use with caution during development only.
        """
        # Clear previously loaded plugins
        self.loaded_plugins.clear()
        self.plugin_modules.clear()

        # Reload
        return self.load_plugins_from_directory(plugin_dir)


def get_plugin_directory() -> Path:
    """Get the default plugin directory"""
    # Look for plugins directory next to this file
    plugin_dir = Path(__file__).parent.parent / "plugins"
    return plugin_dir


# Convenience function for loading plugins at startup
def load_all_plugins(action_executor=None) -> PluginLoader:
    """Load all plugins from the default plugin directory

    Args:
        action_executor: ActionExecutor instance to register handlers with

    Returns:
        PluginLoader instance
    """
    loader = PluginLoader(action_executor)
    plugin_dir = get_plugin_directory()

    print(f"🔌 Loading plugins from: {plugin_dir}")
    count = loader.load_plugins_from_directory(plugin_dir)

    if count > 0:
        print(f"✅ Loaded {count} plugin(s)")
    else:
        print(f"ℹ️  No plugins loaded")

    return loader
