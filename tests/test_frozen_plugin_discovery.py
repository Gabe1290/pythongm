"""Plugins and folder extensions must still be found inside a frozen build.

A PyInstaller bundle unpacks its data files to `sys._MEIPASS`, not next to
the frozen module's nominal `__file__`. `plugins/` and `extensions/` are read
off disk with `spec_from_file_location` -- they are DATA, not frozen modules
-- so a root resolved from `__file__` points somewhere that does not exist
inside the bundle.

The reason this needs a test rather than a glance: the failure is SILENT.
`load_all_plugins` globs a directory, finds nothing, logs "Loaded 0
plugin(s)" and carries on. The exported game then runs with no audio actions
and no 2.5D renderer -- a raycast game draws as a flat 2D room -- and never
raises. That is exactly the class of "the export is not the engine we tested"
bug the desktop-export rework exists to kill, so it gets pinned here.

Verified against a real frozen build (2026-08-17 spike): all four bundled
plugins/extensions load, including 2.5D Raycast View and Block World.
"""
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT))

from events import plugin_loader  # noqa: E402


def test_unfrozen_root_is_the_repo(monkeypatch):
    monkeypatch.delattr(sys, "frozen", raising=False)
    monkeypatch.delattr(sys, "_MEIPASS", raising=False)
    assert plugin_loader.get_app_root() == REPO_ROOT


def test_unfrozen_directories_actually_exist(monkeypatch):
    """Guards the ordinary path against a regression in the frozen fix."""
    monkeypatch.delattr(sys, "frozen", raising=False)
    monkeypatch.delattr(sys, "_MEIPASS", raising=False)
    assert plugin_loader.get_plugin_directory().is_dir()
    assert plugin_loader.get_extension_directory().is_dir()


def test_frozen_root_is_meipass(monkeypatch, tmp_path):
    monkeypatch.setattr(sys, "frozen", True, raising=False)
    monkeypatch.setattr(sys, "_MEIPASS", str(tmp_path), raising=False)
    assert plugin_loader.get_app_root() == tmp_path


def test_frozen_plugin_and_extension_dirs_live_under_meipass(monkeypatch, tmp_path):
    """The whole point: both globbed directories must resolve INSIDE the
    bundle, not next to the source tree that built it."""
    monkeypatch.setattr(sys, "frozen", True, raising=False)
    monkeypatch.setattr(sys, "_MEIPASS", str(tmp_path), raising=False)
    assert plugin_loader.get_plugin_directory() == tmp_path / "plugins"
    assert plugin_loader.get_extension_directory() == tmp_path / "extensions"
    # ...and specifically NOT the repo, which is what `__file__` would give.
    assert REPO_ROOT not in plugin_loader.get_plugin_directory().parents


def test_frozen_without_meipass_falls_back_instead_of_raising(monkeypatch):
    """`sys.frozen` is set by freezers other than PyInstaller, which do not
    all provide `_MEIPASS`. An AttributeError here would take down startup,
    so the guard checks for the attribute rather than assuming it."""
    monkeypatch.setattr(sys, "frozen", True, raising=False)
    monkeypatch.delattr(sys, "_MEIPASS", raising=False)
    assert plugin_loader.get_app_root() == REPO_ROOT


def test_loader_uses_the_helpers_rather_than_recomputing_the_root():
    """A second hard-coded `Path(__file__).parent.parent` elsewhere in the
    module would reintroduce the bug for whichever caller used it."""
    source = (REPO_ROOT / "events" / "plugin_loader.py").read_text(
        encoding="utf-8")
    assert source.count("Path(__file__)") == 1, (
        "plugin_loader should resolve its root in exactly one place "
        "(get_app_root); a second copy will not be _MEIPASS-aware")
