"""Project-wide custom block sharing -- docs/BLOCKLY_SCRATCH_PARITY_PLAN.md's
2026-10-22 follow-up to Feature 2 ("My Blocks").

Each object's Blockly workspace lives on its own separate page with its
own isolated JS state (blockly_widget.py / object_editor_main.py: the
workspace XML is saved/loaded per object, nothing merges another
object's blocks in) -- so without the mechanism this file tests, a
custom block defined in object A would be invisible when editing object
B, contradicting this feature's own original "Scope: project-level...
shared by every object" decision. The project-wide registry
(current_project_data['custom_blocks']) is the fix: Python persists it
as a plain top-level project key (rides through save/load for free,
confirmed by a real round trip below), and each object's own workspace
pushes/pulls it via blockly_widget.py's push_shared_custom_blocks /
get_custom_blocks_export, which blockly_generators.js's
mergeSharedCustomBlockDefs then folds into codegen (and the "My Blocks"
toolbox flyout -- covered structurally in
tests/test_blockly_custom_blocks.py, not here, since it needs no Qt).

This file covers the PYTHON side of the mechanism: the registry's own
merge/persistence semantics (ProjectManager.update_custom_blocks_registry),
BlocklyWidget's push/pull plumbing, and core/ide/_editor_lifecycle.py's
on_editor_save_requested wiring between the two, using the same
bare-instance + fake-page stubbing pattern tests/test_blockly_workspace_xml.py
and tests/test_blockly_workspace_xml_load_race.py already established for
this exact widget (BlocklyWidget.__new__ bypasses the real QWebEngineView
construction __init__ would otherwise require), and the unbound-method-
on-a-stub pattern tests/test_room_editor_sprite_metadata_refresh.py already
established for on_editor_save_requested specifically.
"""
import json
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import MagicMock, patch

import pytest

from conftest import skip_without_pyside6

pytestmark = skip_without_pyside6

pytest.importorskip("PySide6.QtWebEngineWidgets")


# ---------------------------------------------------------------------------
# ProjectManager.update_custom_blocks_registry
# ---------------------------------------------------------------------------

class TestUpdateCustomBlocksRegistry:
    @pytest.fixture
    def project_manager(self):
        with patch('PySide6.QtCore.QTimer'):
            from core.project_manager import ProjectManager
            mock_asset_manager = MagicMock()
            pm = ProjectManager(asset_manager=mock_asset_manager)
            pm.auto_save_timer = MagicMock()
            return pm

    def test_noop_when_current_project_data_is_none(self, project_manager):
        project_manager.current_project_data = None
        # Must not raise, and must not create a project out of thin air.
        project_manager.update_custom_blocks_registry("obj_a", {"square": {}})
        assert project_manager.current_project_data is None

    def test_adds_entries_tagged_with_source_object(self, project_manager, temp_project_dir):
        project_manager.load_project(temp_project_dir)
        project_manager.update_custom_blocks_registry("obj_math", {
            "square": {"arg_names": ["n"], "is_reporter": True,
                       "body_actions": [], "return_expr": "(({{PYGM_ARG:n}}) * ({{PYGM_ARG:n}}))"},
        })
        registry = project_manager.current_project_data["custom_blocks"]
        assert registry["square"]["source_object"] == "obj_math"
        assert registry["square"]["arg_names"] == ["n"]
        assert registry["square"]["return_expr"] == "(({{PYGM_ARG:n}}) * ({{PYGM_ARG:n}}))"

    def test_marks_project_dirty(self, project_manager, temp_project_dir):
        project_manager.load_project(temp_project_dir)
        project_manager.is_dirty_flag = False
        project_manager.update_custom_blocks_registry("obj_math", {"square": {}})
        assert project_manager.is_dirty_flag is True

    def test_resaving_the_same_object_drops_its_stale_entries(self, project_manager, temp_project_dir):
        """A definition renamed/deleted since the last save must not
        linger in the registry forever."""
        project_manager.load_project(temp_project_dir)
        project_manager.update_custom_blocks_registry("obj_math", {
            "square": {"arg_names": ["n"]}, "cube": {"arg_names": ["n"]},
        })
        project_manager.update_custom_blocks_registry("obj_math", {
            "square": {"arg_names": ["n"]},  # "cube" was deleted/renamed away
        })
        registry = project_manager.current_project_data["custom_blocks"]
        assert "square" in registry
        assert "cube" not in registry

    def test_entries_from_other_objects_are_left_untouched(self, project_manager, temp_project_dir):
        project_manager.load_project(temp_project_dir)
        project_manager.update_custom_blocks_registry("obj_math", {"square": {"arg_names": ["n"]}})
        project_manager.update_custom_blocks_registry("obj_player", {"give_point": {"arg_names": []}})
        # Re-saving obj_math (even with the SAME content) must not touch
        # obj_player's own entry.
        project_manager.update_custom_blocks_registry("obj_math", {"square": {"arg_names": ["n"]}})
        registry = project_manager.current_project_data["custom_blocks"]
        assert "square" in registry
        assert "give_point" in registry
        assert registry["give_point"]["source_object"] == "obj_player"

    def test_cross_object_name_collision_is_last_write_wins_not_a_crash(self, project_manager, temp_project_dir):
        """The save itself still proceeds either way -- local always wins
        at generation time regardless of which object's entry sits in
        the registry (mergeSharedCustomBlockDefs' own rule) -- so there
        is no ambiguity to block the save over, only something worth
        surfacing (see the collision-detection tests below)."""
        project_manager.load_project(temp_project_dir)
        project_manager.update_custom_blocks_registry("obj_a", {"helper": {"arg_names": ["x"]}})
        project_manager.update_custom_blocks_registry("obj_b", {"helper": {"arg_names": ["y", "z"]}})
        registry = project_manager.current_project_data["custom_blocks"]
        assert registry["helper"]["source_object"] == "obj_b"
        assert registry["helper"]["arg_names"] == ["y", "z"]

    def test_collision_is_detected_and_reported(self, project_manager, temp_project_dir):
        """2026-10-22 item 6 (defense-in-depth layer, Python side): a
        name collision across two objects is DETECTED and returned, not
        just silently resolved -- the live client-side prevention
        (blockly_generators.js's disambiguateCustomBlockNameAgainstShared)
        is the primary layer but can't be executed/verified without a
        real browser; this layer is."""
        project_manager.load_project(temp_project_dir)
        project_manager.update_custom_blocks_registry("obj_a", {"helper": {"arg_names": ["x"]}})
        collisions = project_manager.update_custom_blocks_registry(
            "obj_b", {"helper": {"arg_names": ["y", "z"]}})
        assert collisions == [("helper", "obj_a")]

    def test_no_collision_reports_an_empty_list(self, project_manager, temp_project_dir):
        project_manager.load_project(temp_project_dir)
        project_manager.update_custom_blocks_registry("obj_a", {"helper": {"arg_names": ["x"]}})
        collisions = project_manager.update_custom_blocks_registry(
            "obj_b", {"other_name": {"arg_names": []}})
        assert collisions == []

    def test_resaving_the_same_object_is_never_its_own_collision(self, project_manager, temp_project_dir):
        """Re-saving obj_a's own "helper" (e.g. after a harmless unrelated
        edit) must not be reported as colliding with itself."""
        project_manager.load_project(temp_project_dir)
        project_manager.update_custom_blocks_registry("obj_a", {"helper": {"arg_names": ["x"]}})
        collisions = project_manager.update_custom_blocks_registry(
            "obj_a", {"helper": {"arg_names": ["x", "y"]}})
        assert collisions == []

    def test_multiple_simultaneous_collisions_are_all_reported(self, project_manager, temp_project_dir):
        project_manager.load_project(temp_project_dir)
        project_manager.update_custom_blocks_registry("obj_a", {
            "foo": {"arg_names": []}, "bar": {"arg_names": []},
        })
        collisions = project_manager.update_custom_blocks_registry("obj_b", {
            "foo": {"arg_names": []}, "bar": {"arg_names": []}, "baz": {"arg_names": []},
        })
        assert sorted(collisions) == [("bar", "obj_a"), ("foo", "obj_a")]

    def test_ignores_non_dict_entries_defensively(self, project_manager, temp_project_dir):
        project_manager.load_project(temp_project_dir)
        project_manager.update_custom_blocks_registry("obj_math", {
            "square": {"arg_names": ["n"]}, "garbage": "not-a-dict", "also_bad": None,
        })
        registry = project_manager.current_project_data["custom_blocks"]
        assert "square" in registry
        assert "garbage" not in registry
        assert "also_bad" not in registry

    def test_empty_or_none_exported_defs_is_safe(self, project_manager, temp_project_dir):
        project_manager.load_project(temp_project_dir)
        project_manager.update_custom_blocks_registry("obj_math", None)
        project_manager.update_custom_blocks_registry("obj_math", {})
        assert project_manager.current_project_data.get("custom_blocks", {}) == {}

    def test_registry_round_trips_through_a_real_save_and_load(self, project_manager, temp_project_dir):
        """custom_blocks is a plain top-level project key, not under
        'assets' -- confirms it actually survives a real save_project +
        load_project cycle, not just an in-memory dict mutation."""
        project_manager.load_project(temp_project_dir)
        project_manager.update_custom_blocks_registry("obj_math", {
            "square": {"arg_names": ["n"], "is_reporter": True,
                       "body_actions": [], "return_expr": "(({{PYGM_ARG:n}}) * ({{PYGM_ARG:n}}))"},
        })
        assert project_manager.save_project() is True

        with open(temp_project_dir / "project.json", encoding="utf-8") as f:
            on_disk = json.load(f)
        assert on_disk["custom_blocks"]["square"]["source_object"] == "obj_math"

        from core.project_manager import ProjectManager
        reloaded = ProjectManager(asset_manager=MagicMock())
        reloaded.auto_save_timer = MagicMock()
        assert reloaded.load_project(temp_project_dir) is True
        assert reloaded.current_project_data["custom_blocks"]["square"]["arg_names"] == ["n"]


# ---------------------------------------------------------------------------
# BlocklyWidget: push/pull plumbing
# ---------------------------------------------------------------------------

class _FakePage:
    def __init__(self, result=None):
        self.calls = []
        self._result = result

    def runJavaScript(self, script, callback=None):
        self.calls.append(script)
        if callback is not None:
            callback(self._result)


class _FakeView:
    def __init__(self, page):
        self._page = page

    def page(self):
        return self._page

    def setVisible(self, value):
        pass


def _bare_widget(project_data=None):
    from editors.object_editor.blockly_widget import BlocklyWidget
    w = BlocklyWidget.__new__(BlocklyWidget)
    w._last_xml = ""
    w._last_custom_blocks_export = {}
    w._page_ready = False
    w._pending_events_data = None
    w._pending_workspace_xml = None
    w._loading = False
    w.round_trip_unsafe = False
    w._set_blockly_language = lambda: None
    w._register_custom_blocks = lambda: None
    w._push_extension_events = lambda: None
    w._apply_saved_configuration = lambda: None
    w.update_status = lambda *a, **k: None
    w._collect_project_assets = lambda: {"objects": [], "sprites": [], "sounds": [], "rooms": []}
    w._find_project_data = lambda: project_data
    return w


class TestPushSharedCustomBlocks:
    def test_noop_when_page_not_ready(self, qapp):
        w = _bare_widget(project_data={"custom_blocks": {"square": {}}})
        w._page_ready = False
        page = _FakePage()
        w.web_view = _FakeView(page)
        w.push_shared_custom_blocks()
        assert page.calls == []

    def test_sends_the_registry_from_project_data(self, qapp):
        w = _bare_widget(project_data={"custom_blocks": {
            "square": {"arg_names": ["n"], "is_reporter": True, "source_object": "obj_math"},
        }})
        w._page_ready = True
        page = _FakePage()
        w.web_view = _FakeView(page)

        w.push_shared_custom_blocks()

        assert len(page.calls) == 1
        assert "setSharedCustomBlocks" in page.calls[0]
        assert "square" in page.calls[0]
        assert "obj_math" in page.calls[0]

    def test_no_project_data_sends_an_empty_registry_not_a_crash(self, qapp):
        w = _bare_widget(project_data=None)
        w._page_ready = True
        page = _FakePage()
        w.web_view = _FakeView(page)
        w.push_shared_custom_blocks()  # must not raise
        assert "setSharedCustomBlocks({})" in page.calls[0]

    def test_no_custom_blocks_key_sends_an_empty_registry(self, qapp):
        w = _bare_widget(project_data={"assets": {}})
        w._page_ready = True
        page = _FakePage()
        w.web_view = _FakeView(page)
        w.push_shared_custom_blocks()
        assert "setSharedCustomBlocks({})" in page.calls[0]


class TestGetCustomBlocksExport:
    def test_returns_cached_value_not_empty(self, qapp):
        w = _bare_widget()
        w._last_custom_blocks_export = {"square": {"arg_names": ["n"]}}
        w.web_view = _FakeView(_FakePage(json.dumps({"square": {"arg_names": ["n", "extra"]}})))
        # Returns the cached value synchronously (the fresh JS result only
        # lands via the async callback, seeding the NEXT read).
        assert w.get_custom_blocks_export() == {"square": {"arg_names": ["n"]}}

    def test_get_kicks_a_refresh(self, qapp):
        w = _bare_widget()
        w._page_ready = True
        w._last_custom_blocks_export = {}
        page = _FakePage(json.dumps({"square": {"arg_names": ["n"]}}))
        w.web_view = _FakeView(page)
        w.get_custom_blocks_export()
        assert page.calls == ["window.blocklyApi.getCustomBlocksExport()"]
        assert w._last_custom_blocks_export == {"square": {"arg_names": ["n"]}}

    def test_refresh_ignores_empty_result(self, qapp):
        w = _bare_widget()
        w._page_ready = True
        w._last_custom_blocks_export = {"square": {"arg_names": ["n"]}}
        w.web_view = _FakeView(_FakePage(""))
        w._refresh_cached_custom_blocks_export()
        assert w._last_custom_blocks_export == {"square": {"arg_names": ["n"]}}

    def test_refresh_ignores_malformed_json(self, qapp):
        w = _bare_widget()
        w._page_ready = True
        w._last_custom_blocks_export = {"square": {"arg_names": ["n"]}}
        w.web_view = _FakeView(_FakePage("{not valid json"))
        w._refresh_cached_custom_blocks_export()
        assert w._last_custom_blocks_export == {"square": {"arg_names": ["n"]}}

    def test_refresh_noop_when_page_not_ready(self, qapp):
        w = _bare_widget()
        w._page_ready = False
        page = _FakePage(json.dumps({"square": {}}))
        w.web_view = _FakeView(page)
        w._refresh_cached_custom_blocks_export()
        assert page.calls == []


class TestOnBlocksChangedRefreshesCustomBlocksExportToo:
    def test_on_blocks_changed_refreshes_both_caches(self, qapp):
        from editors.object_editor.blockly_widget import BlocklyWidget
        from PySide6.QtCore import QTimer

        w = BlocklyWidget.__new__(BlocklyWidget)
        w._loading = False
        w._last_xml = ""
        w._last_custom_blocks_export = {}
        w._page_ready = True
        w.round_trip_unsafe = False
        w.events_data = {}
        w.blocks_modified = MagicMock()
        w._auto_apply_timer = QTimer()
        w.update_status = lambda *a, **k: None

        page = _FakePage(None)
        w.web_view = _FakeView(page)

        w.on_blocks_changed(json.dumps({"create": {"actions": []}}))

        assert "window.blocklyApi.getXml()" in page.calls
        assert "window.blocklyApi.getCustomBlocksExport()" in page.calls


class TestLoadWorkspaceXmlPushesSharedBlocks:
    def test_push_shared_custom_blocks_called_alongside_asset_lists(self, qapp):
        w = _bare_widget(project_data={"custom_blocks": {"square": {"arg_names": ["n"]}}})
        w._page_ready = True
        page = _FakePage(None)
        w.web_view = _FakeView(page)

        w.load_workspace_xml("<xml></xml>")

        shared_calls = [i for i, c in enumerate(page.calls) if "setSharedCustomBlocks" in c]
        load_calls = [i for i, c in enumerate(page.calls) if "loadXml" in c]
        assert shared_calls, "push_shared_custom_blocks was never called"
        assert load_calls, "the workspace XML was never loaded"
        assert shared_calls[0] < load_calls[0], (
            "shared custom blocks must be pushed before the XML that may "
            "reference them loads"
        )

    def test_on_loaded_seeds_the_custom_blocks_export_cache(self, qapp):
        w = _bare_widget(project_data={})
        w._page_ready = True
        page = _FakePage(None)
        w.web_view = _FakeView(page)

        w.load_workspace_xml("<xml></xml>")

        # _on_loaded ran synchronously via the fake page's immediate callback.
        assert any("getCustomBlocksExport" in c for c in page.calls)


class TestOnLoadFinishedPushesSharedBlocks:
    def test_on_load_finished_calls_push_shared_custom_blocks(self, qapp):
        w = _bare_widget(project_data={"custom_blocks": {"square": {"arg_names": ["n"]}}})
        page = _FakePage(None)
        w.web_view = _FakeView(page)

        w.on_load_finished(True)

        assert any("setSharedCustomBlocks" in c for c in page.calls)


# ---------------------------------------------------------------------------
# core/ide/_editor_lifecycle.py's on_editor_save_requested wiring
# ---------------------------------------------------------------------------

def _ide_cls():
    from core.ide_window import PyGameMakerIDE
    return PyGameMakerIDE


def _make_stub_ide(project_data, open_editors=None):
    from PySide6.QtWidgets import QTabWidget

    pm = MagicMock()
    pm.update_asset.return_value = True
    pm.save_project.return_value = True
    pm.get_current_project_data.return_value = project_data
    # Real ProjectManager.update_custom_blocks_registry always returns a
    # list (possibly empty) of collisions -- matching that here so the
    # collision-reporting loop in on_editor_save_requested behaves the
    # same way it would against the real method, not an unconfigured
    # MagicMock (which isn't iterable and would abort the whole try
    # block, including the broadcast call, before either ever runs).
    pm.update_custom_blocks_registry.return_value = []

    status_messages = []
    stub = SimpleNamespace(
        project_manager=pm,
        current_project_data=project_data,
        current_project_path=None,
        update_status=lambda msg, *a, **k: status_messages.append(msg),
        status_messages=status_messages,
        update_window_title=lambda *a, **k: None,
        asset_tree=MagicMock(),
        properties_panel=MagicMock(),
        editor_tabs=QTabWidget(),
        _refresh_blockly_asset_lists=lambda: None,
        refresh_object_sprites=MagicMock(),
        open_editors=open_editors if open_editors is not None else {},
        tr=lambda text: text,
    )
    # on_editor_save_requested calls self._broadcast_shared_custom_blocks()
    # -- a plain attribute lookup on this SimpleNamespace stub, which
    # (unlike the Cls.method(stub, ...) unbound-call pattern used to
    # invoke on_editor_save_requested itself) does NOT fall back to
    # PyGameMakerIDE's real method. Bind the real implementation to this
    # exact stub, mirroring how refresh_object_sprites/
    # _refresh_blockly_asset_lists above are already explicitly provided
    # rather than relied upon via class-level lookup.
    stub._broadcast_shared_custom_blocks = lambda: _ide_cls()._broadcast_shared_custom_blocks(stub)
    return stub


class TestOnEditorSaveRequestedWiresCustomBlocksExport:
    def test_object_save_with_export_updates_the_registry_and_strips_the_key(self, qapp):
        project_data = {"assets": {"objects": {"obj_math": {"name": "obj_math"}}}}
        stub = _make_stub_ide(project_data)

        object_data = {
            "name": "obj_math", "sprite": "", "events": {},
            "_custom_blocks_export": {
                "square": {"arg_names": ["n"], "is_reporter": True,
                           "body_actions": [], "return_expr": "(({{PYGM_ARG:n}}) * ({{PYGM_ARG:n}}))"},
            },
        }

        _ide_cls().on_editor_save_requested(stub, "obj_math", object_data)

        stub.project_manager.update_custom_blocks_registry.assert_called_once_with(
            "obj_math",
            {"square": {"arg_names": ["n"], "is_reporter": True,
                        "body_actions": [], "return_expr": "(({{PYGM_ARG:n}}) * ({{PYGM_ARG:n}}))"}},
        )
        # The transient key must never reach the object's OWN saved record.
        saved_data = stub.project_manager.update_asset.call_args[0][2]
        assert "_custom_blocks_export" not in saved_data

    def test_object_save_without_export_does_not_touch_the_registry(self, qapp):
        project_data = {"assets": {"objects": {"obj_player": {"name": "obj_player"}}}}
        stub = _make_stub_ide(project_data)

        object_data = {"name": "obj_player", "sprite": "", "events": {}}
        _ide_cls().on_editor_save_requested(stub, "obj_player", object_data)

        stub.project_manager.update_custom_blocks_registry.assert_not_called()

    def test_room_save_does_not_touch_the_registry(self, qapp):
        """_custom_blocks_export is only ever attached to OBJECT data
        (editors/object_editor/object_editor_main.py's get_data()) -- a
        room save should never even consider it."""
        project_data = {"assets": {"rooms": {"rm_test": {}}}}
        stub = _make_stub_ide(project_data)

        room_data = {"name": "rm_test", "instances": [], "width": 480, "height": 480}
        _ide_cls().on_editor_save_requested(stub, "rm_test", room_data)

        stub.project_manager.update_custom_blocks_registry.assert_not_called()

    def test_a_raising_registry_update_does_not_abort_the_save(self, qapp):
        """update_custom_blocks_registry is wrapped in its own try/except
        -- a bug in it must not block the object's own data from saving."""
        project_data = {"assets": {"objects": {"obj_math": {"name": "obj_math"}}}}
        stub = _make_stub_ide(project_data)
        stub.project_manager.update_custom_blocks_registry.side_effect = RuntimeError("boom")

        object_data = {
            "name": "obj_math", "sprite": "", "events": {},
            "_custom_blocks_export": {"square": {"arg_names": ["n"]}},
        }
        _ide_cls().on_editor_save_requested(stub, "obj_math", object_data)

        stub.project_manager.update_asset.assert_called_once()
        stub.project_manager.save_project.assert_called_once()

    def test_collisions_are_surfaced_as_a_visible_status_warning(self, qapp):
        """2026-10-22 item 6 (defense-in-depth layer): a collision
        ProjectManager reports must not stay silent -- shown via
        update_status, not just logged where only a developer would
        see it."""
        project_data = {"assets": {"objects": {"obj_math": {"name": "obj_math"}}}}
        stub = _make_stub_ide(project_data)
        stub.project_manager.update_custom_blocks_registry.return_value = [
            ("square", "obj_other"),
        ]

        object_data = {
            "name": "obj_math", "sprite": "", "events": {},
            "_custom_blocks_export": {"square": {"arg_names": ["n"]}},
        }
        _ide_cls().on_editor_save_requested(stub, "obj_math", object_data)

        assert any("square" in msg and "obj_other" in msg
                   for msg in stub.status_messages)

    def test_no_collisions_means_no_warning_message(self, qapp):
        project_data = {"assets": {"objects": {"obj_math": {"name": "obj_math"}}}}
        stub = _make_stub_ide(project_data)

        object_data = {
            "name": "obj_math", "sprite": "", "events": {},
            "_custom_blocks_export": {"square": {"arg_names": ["n"]}},
        }
        _ide_cls().on_editor_save_requested(stub, "obj_math", object_data)

        assert not any("conflicts" in msg for msg in stub.status_messages)

    def test_saving_broadcasts_to_every_other_open_object_editor(self, qapp):
        """2026-10-22 item 5: a block changed in object A must reach
        object B's ALREADY-OPEN editor immediately, not just the next
        time B's tab is reopened."""
        project_data = {"assets": {"objects": {
            "obj_a": {"name": "obj_a"}, "obj_b": {"name": "obj_b"},
        }}}
        editor_a = SimpleNamespace(blockly_tab=MagicMock())
        editor_b = SimpleNamespace(blockly_tab=MagicMock())
        non_object_editor = SimpleNamespace()  # e.g. a room editor -- no blockly_tab
        stub = _make_stub_ide(project_data, open_editors={
            "objects:obj_a": editor_a,
            "objects:obj_b": editor_b,
            "rooms:rm_test": non_object_editor,
        })

        object_data = {
            "name": "obj_a", "sprite": "", "events": {},
            "_custom_blocks_export": {"square": {"arg_names": ["n"]}},
        }
        _ide_cls().on_editor_save_requested(stub, "obj_a", object_data)

        editor_a.blockly_tab.push_shared_custom_blocks.assert_called_once()
        editor_b.blockly_tab.push_shared_custom_blocks.assert_called_once()

    def test_broadcast_is_not_attempted_when_nothing_was_exported(self, qapp):
        """No _custom_blocks_export key at all -- e.g. a sprite or room
        save -- must not even try to broadcast."""
        project_data = {"assets": {"objects": {"obj_a": {"name": "obj_a"}}}}
        editor_a = SimpleNamespace(blockly_tab=MagicMock())
        stub = _make_stub_ide(project_data, open_editors={"objects:obj_a": editor_a})

        object_data = {"name": "obj_a", "sprite": "", "events": {}}
        _ide_cls().on_editor_save_requested(stub, "obj_a", object_data)

        editor_a.blockly_tab.push_shared_custom_blocks.assert_not_called()

    def test_a_raising_broadcast_target_does_not_abort_the_others(self, qapp):
        project_data = {"assets": {"objects": {
            "obj_a": {"name": "obj_a"}, "obj_b": {"name": "obj_b"},
        }}}
        editor_a = SimpleNamespace(blockly_tab=MagicMock())
        editor_a.blockly_tab.push_shared_custom_blocks.side_effect = RuntimeError("boom")
        editor_b = SimpleNamespace(blockly_tab=MagicMock())
        stub = _make_stub_ide(project_data, open_editors={
            "objects:obj_a": editor_a, "objects:obj_b": editor_b,
        })

        object_data = {
            "name": "obj_a", "sprite": "", "events": {},
            "_custom_blocks_export": {"square": {"arg_names": ["n"]}},
        }
        _ide_cls().on_editor_save_requested(stub, "obj_a", object_data)

        editor_b.blockly_tab.push_shared_custom_blocks.assert_called_once()


class TestBroadcastSharedCustomBlocks:
    """Direct unit coverage of _broadcast_shared_custom_blocks itself,
    separate from exercising it through the full save path above."""

    def test_covers_tabbed_and_floated_editors_alike(self, qapp):
        """float_editor only moves the editor WIDGET out of the tab
        strip into its own window; it never removes the entry from
        open_editors (core/ide/_editor_lifecycle.py's own float_editor) --
        so a single iteration over open_editors already covers both
        tabbed and floated/detached editors with no separate check."""
        editor_tabbed = SimpleNamespace(blockly_tab=MagicMock())
        editor_floated = SimpleNamespace(blockly_tab=MagicMock())
        stub = SimpleNamespace(open_editors={
            "objects:obj_tabbed": editor_tabbed,
            "objects:obj_floated": editor_floated,
        })

        _ide_cls()._broadcast_shared_custom_blocks(stub)

        editor_tabbed.blockly_tab.push_shared_custom_blocks.assert_called_once()
        editor_floated.blockly_tab.push_shared_custom_blocks.assert_called_once()

    def test_skips_editors_with_no_blockly_tab(self, qapp):
        sprite_editor = SimpleNamespace()  # no blockly_tab attribute at all
        stub = SimpleNamespace(open_editors={"sprites:spr_x": sprite_editor})
        _ide_cls()._broadcast_shared_custom_blocks(stub)  # must not raise

    def test_missing_open_editors_is_a_safe_noop(self, qapp):
        stub = SimpleNamespace()
        _ide_cls()._broadcast_shared_custom_blocks(stub)  # must not raise


# ---------------------------------------------------------------------------
# editors/object_editor/object_editor_main.py's get_data() forwarding
# ---------------------------------------------------------------------------

class TestObjectEditorAttachesCustomBlocksExport:
    def test_get_data_includes_export_when_present(self, qapp):
        from editors.object_editor.object_editor_main import ObjectEditor

        editor = ObjectEditor.__new__(ObjectEditor)
        editor.asset_name = "obj_math"
        editor.current_object_properties = {}
        editor.blockly_tab = MagicMock()
        editor.blockly_tab.get_workspace_xml.return_value = ""
        editor.blockly_tab.get_custom_blocks_export.return_value = {
            "square": {"arg_names": ["n"]},
        }

        data = editor.get_data()

        assert data["_custom_blocks_export"] == {"square": {"arg_names": ["n"]}}

    def test_get_data_omits_the_key_when_export_is_empty(self, qapp):
        from editors.object_editor.object_editor_main import ObjectEditor

        editor = ObjectEditor.__new__(ObjectEditor)
        editor.asset_name = "obj_player"
        editor.current_object_properties = {}
        editor.blockly_tab = MagicMock()
        editor.blockly_tab.get_workspace_xml.return_value = ""
        editor.blockly_tab.get_custom_blocks_export.return_value = {}

        data = editor.get_data()

        assert "_custom_blocks_export" not in data

    def test_get_data_tolerates_a_raising_export_call(self, qapp):
        from editors.object_editor.object_editor_main import ObjectEditor

        editor = ObjectEditor.__new__(ObjectEditor)
        editor.asset_name = "obj_player"
        editor.current_object_properties = {}
        editor.blockly_tab = MagicMock()
        editor.blockly_tab.get_workspace_xml.return_value = ""
        editor.blockly_tab.get_custom_blocks_export.side_effect = RuntimeError("boom")

        data = editor.get_data()  # must not raise

        assert "_custom_blocks_export" not in data
        assert data["name"] == "obj_player"
