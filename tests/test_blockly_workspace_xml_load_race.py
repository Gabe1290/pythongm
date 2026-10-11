"""Regression test: load_workspace_xml used to have no "page not ready yet"
guard, unlike load_events_data's own pending-data queue right next to it.

Real classroom report, 2026-10-11: a saved collision event's "OBJECT" field
(an asset-backed FieldDropdown, editors/object_editor/blockly/
blockly_workspace.html's createAssetField) silently reverted to empty on
load, corrupting the generated event key from
"collision_with_obj_fruit_cherry" to "collision_with_" -- the nested If/Else
score logic the user reported as broken was, underneath, perfectly correct;
the real bug was the collision event itself never matching the right object
at all once this happened.

Root cause: core/ide/object_editor_main.py calls load_workspace_xml as soon
as an object's saved data is available, with no check that the Blockly page
is ready. If that happens before BlocklyWidget.on_load_finished has run
push_asset_lists(), window.BLOCKLY_ASSET_LISTS is still empty when
Blockly.Xml.domToWorkspace restores the dropdown field, and Blockly's own
FieldDropdown XML loading validates the saved value against the CURRENT
(empty) option list and silently drops it instead of keeping it. Confirmed
via a real headless-browser run of the actual generator against the user's
own saved XML: asset lists pushed before loading -> correct event key;
pushed after -> this exact corruption.

Fix mirrors load_events_data's existing pattern exactly: queue the XML if
the page isn't ready yet, replay it (after push_asset_lists()) once
on_load_finished fires; and even when the page WAS already ready, refresh
asset lists immediately before loading too (same belt-and-braces
load_events_data already does), so a later load on an already-open tab
can't use stale asset names either.
"""
import pytest

from conftest import skip_without_pyside6

pytestmark = skip_without_pyside6

pytest.importorskip("PySide6.QtWebEngineWidgets")


def _bare_widget():
    from editors.object_editor.blockly_widget import BlocklyWidget
    w = BlocklyWidget.__new__(BlocklyWidget)
    w._last_xml = ""
    w._page_ready = False
    w._pending_events_data = None
    w._pending_workspace_xml = None
    w._loading = False
    w.round_trip_unsafe = False
    # Neutralize the other on_load_finished side effects -- unrelated to
    # this fix and not safe to run against a bare, parent-less instance.
    w._set_blockly_language = lambda: None
    w._register_custom_blocks = lambda: None
    w._push_extension_events = lambda: None
    w._apply_saved_configuration = lambda: None
    w.update_status = lambda *a, **k: None
    # _collect_project_assets walks self.parent() looking for project data;
    # a bare instance has none, so it would otherwise raise.
    w._collect_project_assets = lambda: {"objects": [], "sprites": [], "sounds": [], "rooms": []}
    return w


class _FakePage:
    def __init__(self):
        self.calls = []

    def runJavaScript(self, script, callback=None):
        self.calls.append(script)
        if callback is not None:
            callback(None)


class _FakeView:
    def __init__(self, page):
        self._page = page

    def page(self):
        return self._page

    def setVisible(self, value):
        pass


SAMPLE_XML = "<xml><block type='event_create'></block></xml>"


class TestQueueingWhenPageNotReady:
    def test_xml_is_queued_not_sent(self, qapp):
        w = _bare_widget()
        page = _FakePage()
        w.web_view = _FakeView(page)

        w.load_workspace_xml(SAMPLE_XML)

        assert w._pending_workspace_xml == SAMPLE_XML
        assert page.calls == []  # nothing sent to JS yet

    def test_on_load_finished_replays_queued_xml(self, qapp):
        w = _bare_widget()
        page = _FakePage()
        w.web_view = _FakeView(page)

        w.load_workspace_xml(SAMPLE_XML)  # queues, page not ready
        assert w._pending_workspace_xml == SAMPLE_XML

        w.on_load_finished(True)

        assert w._page_ready is True
        assert w._pending_workspace_xml is None  # consumed
        # The real fix: setAssetLists must reach the page BEFORE loadXml.
        asset_list_calls = [i for i, c in enumerate(page.calls) if "setAssetLists" in c]
        load_xml_calls = [i for i, c in enumerate(page.calls) if "loadXml" in c]
        assert asset_list_calls, "push_asset_lists was never called"
        assert load_xml_calls, "the queued XML was never loaded"
        assert asset_list_calls[0] < load_xml_calls[0], (
            "asset lists must be pushed before the XML that references them loads"
        )


class TestRefreshWhenAlreadyReady:
    def test_load_workspace_xml_refreshes_assets_first_even_without_queueing(self, qapp):
        """Even when the page was already ready (no queueing needed at all),
        load_workspace_xml must still push a fresh asset list immediately
        before loading -- matching load_events_data's own behaviour -- so a
        later load on an already-open tab can't use stale asset names."""
        w = _bare_widget()
        w._page_ready = True
        page = _FakePage()
        w.web_view = _FakeView(page)

        w.load_workspace_xml(SAMPLE_XML)

        asset_list_calls = [i for i, c in enumerate(page.calls) if "setAssetLists" in c]
        load_xml_calls = [i for i, c in enumerate(page.calls) if "loadXml" in c]
        assert asset_list_calls, "push_asset_lists was never called"
        assert load_xml_calls, "loadXml was never called"
        assert asset_list_calls[0] < load_xml_calls[0]


class TestNoRegressionOnEmptyXml:
    def test_empty_xml_is_a_pure_noop(self, qapp):
        w = _bare_widget()
        page = _FakePage()
        w.web_view = _FakeView(page)

        w.load_workspace_xml("")

        assert w._pending_workspace_xml is None
        assert page.calls == []
