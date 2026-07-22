"""Folder-based extensions: extensions/<name>/ + extension.json (Stage A2).

An extension is a FOLDER with a manifest and a package __init__.py exposing the
SAME contract as a single-file plugin (PLUGIN_ACTIONS / PLUGIN_EVENTS /
PluginExecutor). Two packagings, one contract: a one-file plugin for something
small, a folder when a feature needs several modules — which is what the
raycast move (Stage B) needs.

See docs/RAYCAST_EXTENSION_PLAN.md.
"""
import json
import sys
import textwrap
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT))

from events.action_types import ACTION_TYPES  # noqa: E402
from events.plugin_loader import (  # noqa: E402
    PluginLoader, get_extension_directory,
)


def _write_extension(root: Path, name, *, actions=("demo_hop",),
                     enabled=True, multi_module=False, manifest_ok=True):
    """Build a throwaway extension folder and return its path."""
    folder = root / name
    folder.mkdir(parents=True)
    if manifest_ok:
        (folder / "extension.json").write_text(json.dumps({
            "name": f"{name} ext", "version": "2.1.0", "author": "Tests",
            "description": "fixture", "enabled": enabled,
        }), encoding="utf-8")
    else:
        (folder / "extension.json").write_text("{ not json", encoding="utf-8")

    act_src = ", ".join(
        f'"{a}": ActionType(name="{a}", display_name="{a}", '
        f'description="d", category="Demo", parameters=[])' for a in actions)

    if multi_module:
        # A sibling module the package imports RELATIVELY — the thing a
        # single-file plugin can't do and the reason folders exist.
        (folder / "schemas.py").write_text(textwrap.dedent(f"""
            from events.action_types import ActionType
            ACTIONS = {{{act_src}}}
        """), encoding="utf-8")
        body = textwrap.dedent("""
            from .schemas import ACTIONS
            PLUGIN_ACTIONS = ACTIONS

            class PluginExecutor:
                def execute_demo_hop_action(self, instance, parameters):
                    return "hopped"
        """)
    else:
        body = textwrap.dedent(f"""
            from events.action_types import ActionType
            PLUGIN_ACTIONS = {{{act_src}}}

            class PluginExecutor:
                def execute_demo_hop_action(self, instance, parameters):
                    return "hopped"
        """)
    (folder / "__init__.py").write_text(body, encoding="utf-8")
    return folder


@pytest.fixture
def cleanup_actions():
    """Remove any demo_* actions the fixtures registered globally."""
    yield
    for key in [k for k in ACTION_TYPES if k.startswith("demo_")]:
        del ACTION_TYPES[key]


def test_loads_a_folder_extension(tmp_path, cleanup_actions):
    _write_extension(tmp_path, "demo_ext")
    loader = PluginLoader()
    assert loader.load_extensions_from_directory(tmp_path) == 1
    assert "demo_hop" in ACTION_TYPES
    info = loader.loaded_plugins[0]
    assert info.name == "demo_ext ext" and info.version == "2.1.0"
    assert info.actions_count == 1
    assert info.file_path.name == "demo_ext"      # the folder, not a file


def test_extension_can_import_its_own_siblings(tmp_path, cleanup_actions):
    """The point of folders: `from .schemas import ACTIONS` must work, which
    needs the folder imported as a real package."""
    _write_extension(tmp_path, "demo_multi", multi_module=True)
    loader = PluginLoader()
    assert loader.load_extensions_from_directory(tmp_path) == 1
    assert "demo_hop" in ACTION_TYPES


def test_handlers_register_on_the_executor(tmp_path, cleanup_actions):
    from runtime.action_executor import ActionExecutor
    _write_extension(tmp_path, "demo_exec")
    ex = ActionExecutor()
    PluginLoader(ex).load_extensions_from_directory(tmp_path)
    assert "demo_hop" in ex.action_handlers


def test_manifest_can_disable_an_extension(tmp_path, cleanup_actions):
    _write_extension(tmp_path, "demo_off", enabled=False)
    loader = PluginLoader()
    assert loader.load_extensions_from_directory(tmp_path) == 0
    assert "demo_hop" not in ACTION_TYPES


def test_folder_without_a_manifest_is_ignored(tmp_path, cleanup_actions):
    folder = tmp_path / "not_an_ext"
    folder.mkdir()
    (folder / "__init__.py").write_text("PLUGIN_ACTIONS = {}", encoding="utf-8")
    assert PluginLoader().load_extensions_from_directory(tmp_path) == 0


def test_bad_manifest_is_survivable(tmp_path, cleanup_actions):
    """One broken extension must not take down the whole load."""
    _write_extension(tmp_path, "demo_broken", manifest_ok=False)
    _write_extension(tmp_path, "demo_good")
    loader = PluginLoader()
    assert loader.load_extensions_from_directory(tmp_path) == 1
    assert "demo_hop" in ACTION_TYPES


def test_missing_init_is_survivable(tmp_path, cleanup_actions):
    folder = tmp_path / "demo_noinit"
    folder.mkdir()
    (folder / "extension.json").write_text('{"name": "x"}', encoding="utf-8")
    assert PluginLoader().load_extensions_from_directory(tmp_path) == 0


def test_missing_extensions_dir_is_not_an_error():
    assert PluginLoader().load_extensions_from_directory(
        Path("/definitely/not/here")) == 0


def test_shared_loader_also_loads_extensions():
    """load_all_plugins covers BOTH mechanisms, so the IDE and runtime get
    extensions through the same single load point as plugins."""
    src = (REPO_ROOT / "events" / "plugin_loader.py").read_text(encoding="utf-8")
    assert "load_extensions_from_directory(get_extension_directory())" in src


def test_single_file_plugins_still_work():
    """Regression guard: folder extensions must not disturb plugins/."""
    from events.plugin_loader import ensure_plugins_loaded
    ensure_plugins_loaded()
    assert "play_sound" in ACTION_TYPES, "single-file audio plugin stopped loading"


def test_extension_directory_is_repo_root_extensions():
    assert get_extension_directory() == REPO_ROOT / "extensions"


# --- Stage A3: config-driven enable/disable --------------------------------
# The manifest sets a default; a user's config override wins either way, so an
# extension can be switched off (or an opt-in one switched on) without editing
# files. An ABSENT config key means "use the manifest" — the config records
# only deliberate choices, so nothing disappears because a key was missing.

@pytest.fixture
def config_overrides(monkeypatch):
    """Drive the extensions override map without touching the real config."""
    from utils.config import Config
    from events import plugin_loader as pl
    store = {}
    real_get = Config.get

    def fake_get(cls, key, default=None):
        if key == pl.EXTENSIONS_CONFIG_KEY:
            return store
        return real_get(key, default)

    monkeypatch.setattr(Config, "get", classmethod(fake_get))
    return store


def test_config_can_disable_an_enabled_extension(tmp_path, cleanup_actions,
                                                 config_overrides):
    _write_extension(tmp_path, "demo_cfgoff")          # manifest: enabled
    config_overrides["demo_cfgoff"] = False
    assert PluginLoader().load_extensions_from_directory(tmp_path) == 0
    assert "demo_hop" not in ACTION_TYPES


def test_config_can_enable_an_extension_that_ships_disabled(tmp_path, cleanup_actions,
                                                            config_overrides):
    """Opt-in for experimental features."""
    _write_extension(tmp_path, "demo_optin", enabled=False)
    config_overrides["demo_optin"] = True
    assert PluginLoader().load_extensions_from_directory(tmp_path) == 1
    assert "demo_hop" in ACTION_TYPES


def test_absent_override_falls_back_to_the_manifest(tmp_path, cleanup_actions,
                                                    config_overrides):
    _write_extension(tmp_path, "demo_default")          # manifest: enabled
    assert config_overrides == {}                       # nothing configured
    assert PluginLoader().load_extensions_from_directory(tmp_path) == 1


def test_unreadable_config_does_not_hide_extensions(tmp_path, cleanup_actions,
                                                    monkeypatch):
    """A config problem must never silently disable every extension."""
    from utils.config import Config
    from events import plugin_loader as pl

    def boom(cls, key, default=None):
        raise RuntimeError("config unavailable")

    monkeypatch.setattr(Config, "get", classmethod(boom))
    assert pl.is_extension_enabled("anything", manifest_default=True) is True
    _write_extension(tmp_path, "demo_cfgboom")
    assert PluginLoader().load_extensions_from_directory(tmp_path) == 1


def test_list_available_extensions_reads_manifests_without_importing():
    """A settings UI needs the list + state without executing extension code."""
    from events.plugin_loader import list_available_extensions
    rows = list_available_extensions()
    assert isinstance(rows, list)
    for r in rows:
        assert {"folder", "name", "version", "description", "enabled"} <= set(r)


def test_set_extension_enabled_round_trips(monkeypatch):
    from utils.config import Config
    from events import plugin_loader as pl
    store = {"value": {}}
    monkeypatch.setattr(Config, "get", classmethod(
        lambda cls, key, default=None: store["value"] if key == pl.EXTENSIONS_CONFIG_KEY else default))
    monkeypatch.setattr(Config, "set", classmethod(
        lambda cls, key, value: store.update(value=value)))
    pl.set_extension_enabled("demo_x", False)
    assert store["value"]["demo_x"] is False
    assert pl.is_extension_enabled("demo_x") is False
    pl.set_extension_enabled("demo_x", True)
    assert pl.is_extension_enabled("demo_x") is True
