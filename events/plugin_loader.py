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

from core.logger import get_logger
logger = get_logger(__name__)

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
            logger.debug(f"Plugin directory not found: {plugin_dir}")
            # Don't create the directory - just skip loading plugins
            return 0

        plugin_files = list(plugin_dir.glob("*.py"))
        if not plugin_files:
            logger.debug(f"No plugin files found in {plugin_dir}")
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
                logger.error(f"Could not load plugin spec: {plugin_file.name}")
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

            # Room renderers (extension_hooks) — a plugin may draw rooms too
            if hasattr(module, 'PLUGIN_ROOM_RENDERERS'):
                self._load_room_renderers(module.PLUGIN_ROOM_RENDERERS)

            # Store plugin info
            self.loaded_plugins.append(plugin_info)
            self.plugin_modules.append(module)

            logger.info(f"Loaded plugin: {plugin_info.name} v{plugin_info.version}")
            logger.debug(f"   Events: {events_loaded}, Actions: {actions_loaded}")

            return True

        except Exception as e:
            logger.error(f"Error loading plugin {plugin_file.name}: {e}")
            import traceback
            traceback.print_exc()
            return False

    # ---------------- Folder extensions (extensions/<name>/) ----------------
    #
    # An EXTENSION is a folder with an extension.json manifest and a package
    # __init__.py exposing the SAME contract as a single-file plugin
    # (PLUGIN_ACTIONS / PLUGIN_EVENTS / PluginExecutor). Deliberately the same
    # contract in two packagings: a one-file plugin for something small, a
    # folder when a feature needs to split across modules. One thing to learn,
    # not two.
    #
    # The folder is imported as a real PACKAGE (submodule_search_locations), so
    # an extension can `from .renderer import ...` its own siblings without
    # touching sys.path or risking name collisions with the host app.

    def load_extensions_from_directory(self, extension_dir: Path) -> int:
        """Load every extension folder under ``extension_dir``."""
        if not extension_dir.exists():
            logger.debug(f"Extension directory not found: {extension_dir}")
            return 0

        loaded = 0
        for folder in sorted(p for p in extension_dir.iterdir() if p.is_dir()):
            if folder.name.startswith(('.', '__')):
                continue
            if not (folder / "extension.json").exists():
                continue          # not an extension folder — ignore quietly
            if self.load_extension(folder):
                loaded += 1
        return loaded

    def load_extension(self, folder: Path) -> bool:
        """Load one ``extensions/<name>/`` folder. Returns True on success."""
        manifest_file = folder / "extension.json"
        try:
            import json
            manifest = json.loads(manifest_file.read_text(encoding="utf-8"))
        except Exception as exc:
            logger.error(f"Extension {folder.name}: bad extension.json ({exc})")
            return False

        # A manifest may ship disabled; a user's config override wins either
        # way (off for something they don't want, on for an opt-in feature).
        if not is_extension_enabled(folder.name, manifest.get("enabled", True)):
            logger.info(f"Extension '{manifest.get('name', folder.name)}' is disabled")
            return False

        init_file = folder / "__init__.py"
        if not init_file.exists():
            logger.error(f"Extension {folder.name}: no __init__.py")
            return False

        try:
            module_name = f"pygm_extension_{folder.name}"
            spec = importlib.util.spec_from_file_location(
                module_name, init_file,
                submodule_search_locations=[str(folder)])   # makes it a package
            if spec is None or spec.loader is None:
                logger.error(f"Extension {folder.name}: could not build import spec")
                return False
            module = importlib.util.module_from_spec(spec)
            sys.modules[module_name] = module
            spec.loader.exec_module(module)

            info = PluginInfo(
                name=manifest.get("name", folder.name),
                version=manifest.get("version", "1.0.0"),
                author=manifest.get("author", "Unknown"),
                description=manifest.get("description", ""),
                file_path=folder,
            )
            if hasattr(module, 'PLUGIN_EVENTS'):
                info.events_count = self._load_events(module.PLUGIN_EVENTS)
            if hasattr(module, 'PLUGIN_ACTIONS'):
                info.actions_count = self._load_actions(module.PLUGIN_ACTIONS)
            if hasattr(module, 'PluginExecutor'):
                self._register_action_handlers(module.PluginExecutor)
            if hasattr(module, 'PLUGIN_ROOM_RENDERERS'):
                self._load_room_renderers(module.PLUGIN_ROOM_RENDERERS)

            self.loaded_plugins.append(info)
            self.plugin_modules.append(module)
            logger.info(f"Loaded extension: {info.name} v{info.version}")
            return True
        except Exception as exc:
            logger.error(f"Error loading extension {folder.name}: {exc}")
            import traceback
            traceback.print_exc()
            return False

    def _load_room_renderers(self, renderers) -> int:
        """Register an extension's PLUGIN_ROOM_RENDERERS (see
        runtime/extension_hooks). Lets an extension draw a room itself instead
        of only adding actions — what the 2.5D raycast view needs."""
        from runtime.extension_hooks import register_room_renderer
        count = 0
        for func in (renderers or []):
            register_room_renderer(func)
            count += 1
        return count

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
                logger.debug(f"Event '{event_name}' already exists, skipping...")
                continue

            EVENT_TYPES[event_name] = event_type
            count += 1
            logger.debug(f"Registered event: {event_name}")

        return count

    def _load_actions(self, plugin_actions: Dict[str, ActionType]) -> int:
        """Load actions from plugin into global ACTION_TYPES"""
        count = 0
        for action_name, action_type in plugin_actions.items():
            if action_name in ACTION_TYPES:
                logger.debug(f"Action '{action_name}' already exists, skipping...")
                continue

            ACTION_TYPES[action_name] = action_type
            count += 1
            logger.debug(f"Registered action: {action_name}")

        return count

    def _register_action_handlers(self, executor_class):
        """Register action handlers from plugin executor"""
        if not self.action_executor:
            # Expected on the IDE path: it loads plugins for their SCHEMAS only
            # (to populate ACTION_TYPES for the action picker / Blockly) and has
            # no ActionExecutor — the game process registers the handlers. Debug,
            # not warning, so a normal IDE startup isn't noisy.
            logger.debug("No action executor (schema-only load); handlers not registered")
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

def get_plugin_directory() -> Path:
    """Get the default plugin directory"""
    # Look for plugins directory next to this file
    plugin_dir = Path(__file__).parent.parent / "plugins"
    return plugin_dir


def get_extension_directory() -> Path:
    """Folder-based extensions live in extensions/ at the repo root."""
    return Path(__file__).parent.parent / "extensions"


# Config key holding per-extension on/off overrides: {folder_name: bool}.
# ABSENT means "use the manifest's own `enabled` value" — the config only
# records deliberate user choices, so an extension never silently disappears
# because a key was missing. (Same lesson as the sample-curation default: an
# opt-OUT that defaults to hidden is the bug, not the feature.)
EXTENSIONS_CONFIG_KEY = "extensions"


def is_extension_enabled(folder_name: str, manifest_default: bool = True) -> bool:
    """Should this extension load? Config override beats the manifest.

    Lets a user switch an extension off without editing files, and equally
    switch ON one that ships disabled (an experimental feature opting in).
    """
    try:
        from utils.config import Config
        overrides = Config.get(EXTENSIONS_CONFIG_KEY, {}) or {}
        if isinstance(overrides, dict) and folder_name in overrides:
            return bool(overrides[folder_name])
    except Exception:
        # Never let a config problem hide every extension.
        logger.debug("Could not read extension overrides; using manifest defaults")
    return manifest_default


def set_extension_enabled(folder_name: str, enabled: bool) -> None:
    """Persist an on/off choice for one extension (takes effect on restart —
    actions register at startup)."""
    from utils.config import Config
    overrides = Config.get(EXTENSIONS_CONFIG_KEY, {}) or {}
    if not isinstance(overrides, dict):
        overrides = {}
    overrides[folder_name] = bool(enabled)
    Config.set(EXTENSIONS_CONFIG_KEY, overrides)


def list_available_extensions() -> List[dict]:
    """Every extension folder on disk with its manifest + effective on/off
    state. For a settings UI — reads manifests without importing any code.
    """
    out = []
    ext_dir = get_extension_directory()
    if not ext_dir.exists():
        return out
    import json
    for folder in sorted(p for p in ext_dir.iterdir() if p.is_dir()):
        manifest_file = folder / "extension.json"
        if not manifest_file.exists():
            continue
        try:
            manifest = json.loads(manifest_file.read_text(encoding="utf-8"))
        except Exception:
            continue
        provides = manifest.get("provides_actions") or []
        out.append({
            "folder": folder.name,
            "name": manifest.get("name", folder.name),
            "version": manifest.get("version", "1.0.0"),
            "description": manifest.get("description", ""),
            "enabled": is_extension_enabled(folder.name,
                                            manifest.get("enabled", True)),
            # Action names this extension owns, declared in its manifest so they
            # are readable WITHOUT importing (loading) the extension — needed to
            # tell a user which DISABLED extension a project's action belongs to.
            "provides_actions": list(provides) if isinstance(provides, list) else [],
        })
    return out


def collect_project_action_names(project_data) -> set:
    """Every action name referenced anywhere in a project's object events,
    walking nested then/else/sub action lists. Tolerant of partial/odd data.
    """
    names: set = set()

    def walk(actions):
        if not isinstance(actions, list):
            return
        for a in actions:
            if not isinstance(a, dict):
                continue
            name = a.get("action")
            if name:
                names.add(name)
            params = a.get("parameters") if isinstance(a.get("parameters"), dict) else {}
            for key in ("then_actions", "else_actions", "sub_actions", "actions"):
                if key in params:
                    walk(params[key])
                if key in a:
                    walk(a[key])

    objects = ((project_data or {}).get("assets") or {}).get("objects") or {}
    if not isinstance(objects, dict):
        return names
    for obj in objects.values():
        if not isinstance(obj, dict):
            continue
        events = obj.get("events") or {}
        if isinstance(events, dict):
            for ev in events.values():
                if isinstance(ev, dict):
                    walk(ev.get("actions"))
                elif isinstance(ev, list):
                    walk(ev)
        elif isinstance(events, list):
            for ev in events:
                if isinstance(ev, dict):
                    walk(ev.get("actions"))
    return names


def missing_extensions_for_project(project_data) -> List[dict]:
    """Extensions a project's actions need that are currently DISABLED.

    Returns ``[{folder, name, actions}]`` — for each disabled extension whose
    manifest ``provides_actions`` overlaps the actions the project uses, the
    extension's folder/name and the sorted list of action names it would supply.

    Empty in the common case (everything the project uses is available). A
    project.json that uses no such actions — or with no extensions installed —
    yields ``[]``, so a project file that never mentions an extension is fine.
    """
    used = collect_project_action_names(project_data)
    if not used:
        return []
    out = []
    for info in list_available_extensions():
        if info.get("enabled", True):
            continue                      # loaded — its actions are available
        needed = sorted(set(info.get("provides_actions") or []) & used)
        if needed:
            out.append({"folder": info["folder"], "name": info["name"],
                        "actions": needed})
    return out


def required_extensions_for_project(project_data) -> List[str]:
    """Folder names of every extension whose ``provides_actions`` the project
    uses — enabled or not. This is the project's extension *dependency*, for
    persisting into project.json (a durable record a sharing recipient can see
    without running the game). Sorted + deduped; ``[]`` when the project uses no
    extension action, so a project file simply omits the field in that case.
    """
    used = collect_project_action_names(project_data)
    if not used:
        return []
    folders = set()
    for info in list_available_extensions():
        if set(info.get("provides_actions") or []) & used:
            folders.add(info["folder"])
    return sorted(folders)


# The one shared loader for this process. See load_all_plugins.
_shared_loader: Optional[PluginLoader] = None


def load_all_plugins(action_executor=None) -> PluginLoader:
    """Load every plugin ONCE per process; safe to call repeatedly.

    THE single load point. Both entry points call it:

    * the **IDE** at startup (via the ``ensure_plugins_loaded`` alias) with NO
      executor — plugin action/event SCHEMAS land in ACTION_TYPES /
      EVENT_TYPES so the action-list editor and Blockly's auto-generated
      blocks can see them;
    * **GameRunner** with its executor — the same schemas plus the
      ``execute_*_action`` handlers that actually run them.

    Until 2026-07-22 this was called in exactly one place (GameRunner), so
    plugin actions were invisible in the IDE: ``'play_sound' in ACTION_TYPES``
    was False outside a running game. That silently contradicted the Blockly
    toolbox's own comment ("audio actions ... auto-generate into a single Audio
    category via registerCustomBlocks"), which reads ACTION_TYPES and so
    produced nothing.

    Re-calling with a *different* executor (a GameRunner created after the IDE,
    or one per test) re-registers the handlers on it WITHOUT re-importing the
    plugin modules — importing twice just creates duplicate module objects.
    Re-registering schemas is already harmless: _load_actions skips names that
    are present.

    NB the name is load-bearing for the test suite: ~28 test files stub plugin
    loading with ``patch('runtime.game_runner.load_all_plugins')``. Renaming it
    breaks them all, so keep this symbol and let GameRunner call it by name.
    """
    global _shared_loader
    if _shared_loader is None:
        plugin_dir = get_plugin_directory()
        logger.info(f"Loading plugins from: {plugin_dir}")
        _shared_loader = PluginLoader(action_executor)
        count = _shared_loader.load_plugins_from_directory(plugin_dir)
        # Folder extensions load after single-file plugins. Order matters:
        # _load_actions skips names already present, so a plugin wins a name
        # clash with an extension. Documented rather than "fixed" — silent
        # shadowing is the existing landmine (CLAUDE.md), not something to
        # extend to a new mechanism without a decision.
        count += _shared_loader.load_extensions_from_directory(get_extension_directory())
        if count > 0:
            logger.info(f"Loaded {count} plugin(s)/extension(s)")
        else:
            logger.debug("No plugins or extensions loaded")
        return _shared_loader

    if action_executor is not None and _shared_loader.action_executor is not action_executor:
        _shared_loader.action_executor = action_executor
        for module in _shared_loader.plugin_modules:
            if hasattr(module, 'PluginExecutor'):
                _shared_loader._register_action_handlers(module.PluginExecutor)
    # Re-register room renderers on every call. Registration is idempotent,
    # and the hook registry (runtime/extension_hooks) is process-global state
    # a test may legitimately clear — without this, the once-per-process load
    # above would never restore it, and every later GameRunner in the process
    # would silently lose extension rendering (raycast rooms falling back to
    # top-down).
    for module in _shared_loader.plugin_modules:
        if hasattr(module, 'PLUGIN_ROOM_RENDERERS'):
            _shared_loader._load_room_renderers(module.PLUGIN_ROOM_RENDERERS)
    return _shared_loader


# Clearer name for the IDE call site, where "ensure" reads better than "load
# all" (the IDE may well not be the first caller). Same function.
ensure_plugins_loaded = load_all_plugins
