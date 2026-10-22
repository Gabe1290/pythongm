"""Project-wide search -- TODO.md's "project-wide search (asset names,
identifiers)" item, logged separately when Find/Replace (a single text
editor's own search) shipped 2026-10-18.

Two layers: utils/project_search.search_project (pure, no Qt) is tested
directly against hand-built project data covering every result kind
(asset names, object fields, nested action params, container events,
collision targets, room fields, script code). dialogs/
project_search_dialog.ProjectSearchDialog is tested against a real
offscreen QApplication (matching tests/test_room_canvas_cache_clear.py's
established no-pytest-qt-needed pattern). The IDE-level dispatch
(find_in_project) uses the unbound-method-on-a-stub pattern
tests/test_find_replace.py already established for this exact mixin.
"""
import os
os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

import sys
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import MagicMock, patch

import pytest

sys.path.insert(0, str(Path(__file__).parent.parent))
from conftest import skip_without_pyside6

pytestmark = skip_without_pyside6

from utils.project_search import SearchResult, search_project


def _identity_tr(text, *_args, **_kwargs):
    return text


@pytest.fixture(scope="module")
def _qapp():
    from PySide6.QtWidgets import QApplication
    app = QApplication.instance() or QApplication([])
    yield app


# ---------------------------------------------------------------------------
# utils.project_search.search_project
# ---------------------------------------------------------------------------

def _project():
    return {
        "assets": {
            "sprites": {"spr_player": {}, "spr_enemy": {}},
            "sounds": {"snd_jump": {}},
            "objects": {
                "obj_player": {
                    "sprite": "spr_player",
                    "parent": "",
                    "events": {
                        "create": {"actions": [
                            {"action": "set_hspeed",
                             "parameters": {"value": "player_speed"}},
                        ]},
                        "step": {"actions": [
                            {"action": "if_condition", "parameters": {
                                "then_actions": [
                                    {"action": "play_sound",
                                     "parameters": {"sound": "snd_jump"}},
                                ],
                            }},
                        ]},
                        "collision_with_obj_enemy": {
                            "target_object": "obj_enemy", "actions": [],
                        },
                        "keyboard_press": {
                            "space": {"actions": [
                                {"action": "play_sound",
                                 "parameters": {"sound": "snd_jump"}},
                            ]},
                        },
                    },
                },
                "obj_enemy": {"sprite": "spr_enemy", "events": {}},
            },
            "rooms": {
                "room1": {
                    "background_image": "",
                    "instances": [{"object_name": "obj_player"}],
                    "tiles": [{"background_name": "bg_sky"}],
                },
            },
            "scripts": {
                "calc_damage": {
                    "code": "def calc_damage(player_speed):\n    return player_speed * 2\n",
                },
            },
        },
    }


class TestSearchProject:
    def test_empty_query_returns_nothing(self):
        assert search_project(_project(), "") == []
        assert search_project(_project(), "   ") == []

    def test_no_project_data_is_safe(self):
        assert search_project(None, "anything") == []
        assert search_project({}, "anything") == []

    def test_finds_asset_name_in_every_category(self):
        results = search_project(_project(), "obj_player")
        kinds = {(r.kind, r.category, r.name) for r in results}
        assert ("asset_name", "objects", "obj_player") in kinds

    def test_finds_object_field(self):
        results = search_project(_project(), "spr_player")
        field_matches = [r for r in results if r.kind == "object_field"]
        assert any(r.name == "obj_player" and r.matched_text == "spr_player"
                   for r in field_matches)

    def test_finds_top_level_action_parameter(self):
        results = search_project(_project(), "player_speed")
        action_params = [r for r in results if r.kind == "action_param"]
        assert any(r.name == "obj_player" and "set_hspeed" in r.location
                   for r in action_params)

    def test_finds_parameter_nested_inside_then_actions(self):
        """The whole reason this has its own tree walker, not a flat
        dict scan: a match inside if_condition's then_actions must still
        be found."""
        results = search_project(_project(), "snd_jump")
        nested = [r for r in results if r.kind == "action_param"
                  and "play_sound" in r.location and "step" in r.location]
        assert len(nested) == 1
        assert nested[0].matched_text == "snd_jump"

    def test_finds_parameter_inside_a_container_event(self):
        """keyboard_press's sub-event (space) actions are stored under a
        nested {sub_key: {actions: [...]}} shape, not directly under the
        event -- must still be walked."""
        results = search_project(_project(), "snd_jump")
        container_hit = [r for r in results if "keyboard_press:space" in r.location]
        assert len(container_hit) == 1

    def test_finds_action_name_itself(self):
        results = search_project(_project(), "if_condition")
        assert any(r.kind == "action_name" and r.matched_text == "if_condition"
                   for r in results)

    def test_finds_collision_target(self):
        results = search_project(_project(), "obj_enemy")
        collision_hits = [r for r in results if "collision target" in r.location]
        assert len(collision_hits) == 1
        assert collision_hits[0].name == "obj_player"

    def test_finds_room_instance_reference(self):
        results = search_project(_project(), "obj_player")
        room_hits = [r for r in results if r.kind == "room_field" and r.category == "rooms"]
        assert any("instance of obj_player" in r.location for r in room_hits)

    def test_finds_room_tile_background_reference(self):
        results = search_project(_project(), "bg_sky")
        assert any(r.kind == "room_field" and r.name == "room1" for r in results)

    def test_finds_script_code_with_line_number(self):
        results = search_project(_project(), "return player_speed")
        script_hits = [r for r in results if r.kind == "script_code"]
        assert len(script_hits) == 1
        assert script_hits[0].name == "calc_damage"
        assert "line 2" in script_hits[0].location

    def test_case_insensitive_by_default(self):
        results = search_project(_project(), "OBJ_PLAYER")
        assert any(r.name == "obj_player" for r in results)

    def test_case_sensitive_when_requested(self):
        results = search_project(_project(), "OBJ_PLAYER", case_sensitive=True)
        assert results == []

    def test_no_match_returns_empty_list(self):
        assert search_project(_project(), "nonexistent_xyz123") == []

    def test_result_is_the_documented_dataclass(self):
        results = search_project(_project(), "obj_player")
        assert isinstance(results[0], SearchResult)


# ---------------------------------------------------------------------------
# dialogs.project_search_dialog.ProjectSearchDialog
# ---------------------------------------------------------------------------

class TestProjectSearchDialog:
    def test_search_populates_results_tree(self, _qapp):
        """player_speed appears 3x in the fixture: the set_hspeed action
        param, and twice in calc_damage's script code (def line + return
        line) -- confirms the dialog surfaces every kind, not just one."""
        from dialogs.project_search_dialog import ProjectSearchDialog
        dialog = ProjectSearchDialog()
        try:
            dialog.set_project_data(_project())
            dialog.search_field.setText("player_speed")
            dialog._run_search()
            assert dialog.results_tree.topLevelItemCount() == 3
            categories = {dialog.results_tree.topLevelItem(i).data(0, 256)
                          for i in range(3)}
            assert ("objects", "obj_player") in categories
            assert ("scripts", "calc_damage") in categories
            assert "3" in dialog.status_label.text()
        finally:
            dialog.deleteLater()

    def test_empty_query_clears_results_and_status(self, _qapp):
        from dialogs.project_search_dialog import ProjectSearchDialog
        dialog = ProjectSearchDialog()
        try:
            dialog.set_project_data(_project())
            dialog.search_field.setText("player_speed")
            dialog._run_search()
            assert dialog.results_tree.topLevelItemCount() == 3
            dialog.search_field.setText("")
            dialog._run_search()
            assert dialog.results_tree.topLevelItemCount() == 0
            assert dialog.status_label.text() == ""
        finally:
            dialog.deleteLater()

    def test_no_project_data_shows_status_not_a_crash(self, _qapp):
        from dialogs.project_search_dialog import ProjectSearchDialog
        dialog = ProjectSearchDialog()
        try:
            dialog.search_field.setText("anything")
            dialog._run_search()
            assert dialog.results_tree.topLevelItemCount() == 0
            assert "No project" in dialog.status_label.text()
        finally:
            dialog.deleteLater()

    def test_rebinding_project_data_rereuns_a_pending_search(self, _qapp):
        """set_project_data is called every time the dialog is re-shown
        (core/ide/_edit_actions.py's find_in_project) -- a query typed
        before switching projects must re-run against the new data, not
        keep showing stale results from the old one."""
        from dialogs.project_search_dialog import ProjectSearchDialog
        dialog = ProjectSearchDialog()
        try:
            dialog.set_project_data(_project())
            dialog.search_field.setText("obj_player")
            dialog._run_search()
            assert dialog.results_tree.topLevelItemCount() > 0

            other_project = {"assets": {"objects": {}}}
            dialog.set_project_data(other_project)
            assert dialog.results_tree.topLevelItemCount() == 0
        finally:
            dialog.deleteLater()

    def test_double_click_opens_the_asset_via_the_parent_ide(self, _qapp):
        from PySide6.QtWidgets import QMainWindow
        from dialogs.project_search_dialog import ProjectSearchDialog

        calls = []

        class _FakeIDE(QMainWindow):
            def on_asset_double_clicked(self, asset_data):
                calls.append(asset_data)

        ide = _FakeIDE()
        dialog = ProjectSearchDialog(ide)
        try:
            dialog.set_project_data(_project())
            dialog.search_field.setText("obj_player")
            dialog._run_search()
            item = dialog.results_tree.topLevelItem(0)
            dialog._on_result_double_clicked(item, 0)
            assert len(calls) == 1
            assert calls[0]["asset_type"] == "objects"
            assert calls[0]["name"] == "obj_player"
            assert calls[0]["data"]["sprite"] == "spr_player"
        finally:
            dialog.deleteLater()
            ide.deleteLater()

    def test_double_click_on_a_now_deleted_asset_is_a_safe_noop(self, _qapp):
        from PySide6.QtWidgets import QMainWindow
        from dialogs.project_search_dialog import ProjectSearchDialog

        calls = []

        class _FakeIDE(QMainWindow):
            def on_asset_double_clicked(self, asset_data):
                calls.append(asset_data)

        ide = _FakeIDE()
        dialog = ProjectSearchDialog(ide)
        try:
            project_data = _project()
            dialog.set_project_data(project_data)
            dialog.search_field.setText("obj_player")
            dialog._run_search()
            item = dialog.results_tree.topLevelItem(0)

            del project_data["assets"]["objects"]["obj_player"]
            dialog._on_result_double_clicked(item, 0)

            assert calls == []
            assert "no longer exists" in dialog.status_label.text()
        finally:
            dialog.deleteLater()
            ide.deleteLater()

    def test_debounce_timer_is_configured(self, _qapp):
        from dialogs.project_search_dialog import ProjectSearchDialog
        dialog = ProjectSearchDialog()
        try:
            assert dialog._debounce_timer.isSingleShot()
        finally:
            dialog.deleteLater()


# ---------------------------------------------------------------------------
# IDE-level dispatch (core/ide/_edit_actions.py)
# ---------------------------------------------------------------------------

def _ide_cls():
    from core.ide_window import PyGameMakerIDE
    return PyGameMakerIDE


class TestFindInProjectEntryPoint:
    def test_no_project_open_shows_status_message_and_no_dialog(self):
        ide = _ide_cls()
        status_bar = MagicMock()
        stub = SimpleNamespace(
            current_project_data=None,
            status_bar=status_bar,
            tr=_identity_tr,
        )
        ide.find_in_project(stub)
        status_bar.showMessage.assert_called_once()
        assert not hasattr(stub, "_project_search_dialog")

    def test_binds_project_data_and_shows_dialog(self, _qapp):
        ide = _ide_cls()
        mock_dialog = MagicMock()
        project_data = {"assets": {}}
        stub = SimpleNamespace(
            current_project_data=project_data,
            tr=_identity_tr,
        )
        with patch('dialogs.project_search_dialog.ProjectSearchDialog',
                   return_value=mock_dialog):
            ide.find_in_project(stub)
        assert stub._project_search_dialog is mock_dialog
        mock_dialog.set_project_data.assert_called_once_with(project_data)
        mock_dialog.show.assert_called_once()

    def test_reuses_existing_dialog_instance_on_second_call(self, _qapp):
        ide = _ide_cls()
        mock_dialog = MagicMock()
        stub = SimpleNamespace(
            current_project_data={"assets": {}},
            tr=_identity_tr,
            _project_search_dialog=mock_dialog,
        )
        ide.find_in_project(stub)
        assert stub._project_search_dialog is mock_dialog
        mock_dialog.set_project_data.assert_called_once()
