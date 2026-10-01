"""Pin tests for ProjectSettingsDialog's per-project extension-activation
section (docs/BLOCKLY_TOOLBOX_GATING_PLAN.md, Unit 5).
"""
import os
import sys
from pathlib import Path

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")
os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT))

import pytest

from conftest import skip_without_pyside6

pytestmark = skip_without_pyside6


@pytest.fixture(scope="module")
def qapp():
    from PySide6.QtWidgets import QApplication
    app = QApplication.instance() or QApplication([])
    yield app


def _project_using(action_name, object_name="obj_x"):
    return {
        "name": "test", "settings": {},
        "assets": {"objects": {object_name: {"events": {"create": {
            "actions": [{"action": action_name, "parameters": {}}]
        }}}}},
    }


def test_thymio_is_excluded_from_the_list(qapp):
    """Thymio's actions never appear in ACTION_TYPES (confirmed
    THYMIO_EXTENSION_PLAN.md Stage G3), so it isn't governed by this
    per-project activation mechanism and must not show a non-functional
    checkbox."""
    from events.plugin_loader import load_all_plugins
    load_all_plugins()
    from dialogs.project_dialogs import ProjectSettingsDialog

    dlg = ProjectSettingsDialog(None, {"name": "test", "settings": {}})
    try:
        assert "thymio" not in dlg.extension_checks
        assert set(dlg.extension_checks) == {
            "block_world", "multiplayer_files", "multiplayer_lan", "raycast_2_5d"}
    finally:
        dlg.deleteLater()


def test_used_extension_is_checked_and_disabled_with_a_count(qapp):
    from events.plugin_loader import load_all_plugins
    load_all_plugins()
    from dialogs.project_dialogs import ProjectSettingsDialog

    dlg = ProjectSettingsDialog(None, _project_using("set_facing_angle"))
    try:
        check = dlg.extension_checks["raycast_2_5d"]
        assert check.isChecked() is True
        assert check.isEnabled() is False
    finally:
        dlg.deleteLater()


def test_unused_extension_starts_unchecked_and_enabled(qapp):
    from events.plugin_loader import load_all_plugins
    load_all_plugins()
    from dialogs.project_dialogs import ProjectSettingsDialog

    dlg = ProjectSettingsDialog(None, {"name": "test", "settings": {}})
    try:
        check = dlg.extension_checks["raycast_2_5d"]
        assert check.isChecked() is False
        assert check.isEnabled() is True
    finally:
        dlg.deleteLater()


def test_globally_disabled_extension_is_not_listed(qapp):
    from events.plugin_loader import load_all_plugins, set_extension_enabled
    load_all_plugins()
    from dialogs.project_dialogs import ProjectSettingsDialog

    set_extension_enabled("raycast_2_5d", False)
    try:
        dlg = ProjectSettingsDialog(None, {"name": "test", "settings": {}})
        try:
            assert "raycast_2_5d" not in dlg.extension_checks
        finally:
            dlg.deleteLater()
    finally:
        set_extension_enabled("raycast_2_5d", True)


def test_accept_settings_persists_only_manually_checked_extensions(qapp):
    from events.plugin_loader import load_all_plugins
    load_all_plugins()
    from dialogs.project_dialogs import ProjectSettingsDialog

    project_data = _project_using("set_facing_angle")  # raycast already used
    dlg = ProjectSettingsDialog(None, project_data)
    try:
        dlg.extension_checks["multiplayer_lan"].setChecked(True)  # manual opt-in
        dlg.accept_settings()
        active = dlg.project_data["settings"]["active_extensions"]
        # raycast_2_5d is disabled/already-used -- not re-listed, no need to.
        assert active == ["multiplayer_lan"]
    finally:
        dlg.deleteLater()


def test_reopening_restores_a_previously_manual_activation(qapp):
    from events.plugin_loader import load_all_plugins
    load_all_plugins()
    from dialogs.project_dialogs import ProjectSettingsDialog

    project_data = {
        "name": "test",
        "settings": {"active_extensions": ["multiplayer_lan"]},
    }
    dlg = ProjectSettingsDialog(None, project_data)
    try:
        assert dlg.extension_checks["multiplayer_lan"].isChecked() is True
        assert dlg.extension_checks["multiplayer_lan"].isEnabled() is True
        assert dlg.extension_checks["raycast_2_5d"].isChecked() is False
    finally:
        dlg.deleteLater()


def test_active_extensions_round_trips_through_the_resolver(qapp):
    """The dialog's output feeds straight into
    config.toolbox_visibility.active_extensions -- confirm the saved
    settings dict is actually usable by it, not just shaped like one."""
    from events.plugin_loader import load_all_plugins
    load_all_plugins()
    from dialogs.project_dialogs import ProjectSettingsDialog
    from config.toolbox_visibility import active_extensions

    dlg = ProjectSettingsDialog(None, {"name": "test", "settings": {}})
    try:
        dlg.extension_checks["raycast_2_5d"].setChecked(True)
        dlg.accept_settings()
        assert "raycast_2_5d" in active_extensions(dlg.project_data)
    finally:
        dlg.deleteLater()


def test_project_settings_refreshes_open_editors_after_accepting():
    """Structural: project_settings() (core/ide/_project_actions.py) calls
    refresh_event_panels_config() after a successful dialog accept, so an
    activation change takes effect live without a restart."""
    src = (REPO_ROOT / "core" / "ide" / "_project_actions.py").read_text(encoding="utf-8")
    body_start = src.index("def project_settings")
    body_end = src.index("\n    def ", body_start + 1)
    body = src[body_start:body_end]
    assert "self.refresh_event_panels_config()" in body
