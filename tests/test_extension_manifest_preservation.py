"""ProjectManager._prepare_project_data_for_save's requires_extensions
fidelity — DEFERRED_ITEMS_PLAN.md Tier 3 item 13 / extension_compat_2_0
PLAN.md Task 2.

Confirmed bug (found by direct reproduction, not inspection alone): the
field is recomputed from scratch on every save via
required_extensions_for_project(), which can only NAME an extension whose
manifest is present on disk. Resaving a project that references an
extension this install doesn't have at all silently wiped the dependency
record, even though the actual unrecognized actions in assets.objects
were untouched. Fixed by unioning the recomputed set with any existing
entry this editor has no manifest for (so it can't verify is stale)
rather than trusting the recomputation alone.
"""
import os
os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

from unittest.mock import MagicMock, patch

import pytest

from conftest import skip_without_pyside6

pytestmark = skip_without_pyside6


@pytest.fixture
def project_manager():
    with patch('PySide6.QtCore.QTimer'):
        from core.project_manager import ProjectManager
        pm = ProjectManager(asset_manager=MagicMock())
        pm.auto_save_timer = MagicMock()
        return pm


def _project_with_action(action_name, requires_extensions=None):
    data = {
        "name": "Test",
        "version": "1.0.0",
        "assets": {
            "objects": {
                "obj_test": {
                    "events": {
                        "step": {
                            "actions": [
                                {"action": action_name, "parameters": {}},
                            ]
                        }
                    }
                }
            },
            "rooms": {},
            "playgrounds": {},
        },
    }
    if requires_extensions is not None:
        data["requires_extensions"] = requires_extensions
    return data


class TestRequiresExtensionsFidelity:
    def test_unavailable_extension_dependency_survives_resave(self, project_manager):
        # "threed" isn't a real installed extension anywhere in this repo —
        # exactly the "opened by an editor without it" case.
        project_manager.current_project_data = _project_with_action(
            "set_camera_3d", requires_extensions=["threed"])

        saved = project_manager._prepare_project_data_for_save()

        assert saved["requires_extensions"] == ["threed"]
        # The actual unrecognized action must also be untouched.
        actions = saved["assets"]["objects"]["obj_test"]["events"]["step"]["actions"]
        assert actions == [{"action": "set_camera_3d", "parameters": {}}]

    def test_installed_extension_dependency_recomputed(self, project_manager):
        # raycast_2_5d IS a real installed extension in this repo, so a
        # dependency on it CAN be positively verified either way.
        project_manager.current_project_data = _project_with_action(
            "enable_raycast_view")

        saved = project_manager._prepare_project_data_for_save()

        assert saved.get("requires_extensions") == ["raycast_2_5d"]

    def test_genuinely_stale_installed_extension_entry_is_dropped(self, project_manager):
        # requires_extensions claims raycast_2_5d, but no raycast action is
        # actually used any more — since this editor DOES have that
        # extension's manifest, it can positively confirm the record is
        # stale and should clean it up (not union blindly).
        project_manager.current_project_data = _project_with_action(
            "set_score", requires_extensions=["raycast_2_5d"])

        saved = project_manager._prepare_project_data_for_save()

        assert "requires_extensions" not in saved

    def test_no_extension_actions_no_field_added(self, project_manager):
        project_manager.current_project_data = _project_with_action("set_score")

        saved = project_manager._prepare_project_data_for_save()

        assert "requires_extensions" not in saved

    def test_mixed_verifiable_and_unverifiable_entries_both_preserved_correctly(self, project_manager):
        # requires_extensions lists BOTH a real installed extension (still
        # used, so recomputation confirms it) and an absent one (can't be
        # verified, must be preserved) at the same time.
        data = _project_with_action("enable_raycast_view",
                                     requires_extensions=["raycast_2_5d", "threed"])
        project_manager.current_project_data = data

        saved = project_manager._prepare_project_data_for_save()

        assert saved["requires_extensions"] == ["raycast_2_5d", "threed"]
