"""Regression tests for the Blockly round-trip safety net (U0 of
docs/BLOCKLY_BLOCK_AUDIT_2026-10-08.md).

The audit found that ObjectEditor.on_blockly_events_modified replaces an
object's ENTIRE events dict with whatever Blockly's JS page currently holds,
on every block edit -- and Blockly's save/load layer loses real data for
many objects (conditions lose their nested actions, events with no matching
block vanish, typing 0 saves the default, ...). So opening an object that
Blockly can't represent exactly and then touching any unrelated block
silently destroys data.

U0 is the safety net: whenever events are synced into Blockly
(BlocklyWidget.load_events_data), the widget immediately asks the real page
to regenerate code and diffs it against what was loaded
(editors/object_editor/blockly_roundtrip.diff_events — the same function the
audit tool itself uses). If there's a difference, the workspace is locked
(JS change-listener stops notifying Python; an overlay explains why) instead
of being left editable.
"""
import json

import pytest

from conftest import skip_without_pyside6

pytestmark = skip_without_pyside6

# QtWebEngine may be absent in headless CI; skip the whole module if the
# widget can't even be imported.
pytest.importorskip("PySide6.QtWebEngineWidgets")


def _widget():
    from editors.object_editor.blockly_widget import BlocklyWidget
    w = BlocklyWidget.__new__(BlocklyWidget)
    w._page_ready = True
    w.round_trip_unsafe = False
    return w


class _FakePage:
    """Records every script run and replies with the next queued result,
    only for calls that actually pass a callback -- matching how
    set_locked's own runJavaScript call (no callback) behaves for real."""

    def __init__(self, *responses):
        self.calls = []
        self._responses = list(responses)

    def runJavaScript(self, script, callback=None):
        self.calls.append(script)
        if callback is not None:
            callback(self._responses.pop(0) if self._responses else None)


class _FakeView:
    def __init__(self, page):
        self._page = page

    def page(self):
        return self._page


# --------------------------------------------------------------- diff_events
from editors.object_editor.blockly_roundtrip import diff_events, summarize_issues  # noqa: E402


class TestDiffEvents:
    def test_identical_events_have_no_issues(self):
        ev = {"create": {"actions": [{"action": "set_gravity", "parameters": {"value": 0.5}}]}}
        assert diff_events(ev, ev) == []

    def test_representational_differences_are_not_issues(self):
        """"4" vs 4, "self" vs "sel" -- the same real value, just
        differently typed/spelled; not a loss."""
        before = {"create": {"actions": [{"action": "x", "parameters": {"n": "4", "target": "self"}}]}}
        after = {"create": {"actions": [{"action": "x", "parameters": {"n": 4, "target": "sel"}}]}}
        assert diff_events(before, after) == []

    def test_dropped_event_is_reported(self):
        before = {"game_start": {"actions": [{"action": "set_lives", "parameters": {"value": 3}}]}}
        after = {}
        issues = diff_events(before, after)
        assert ("game_start", "event-dropped", "game_start", "game_start") in issues

    def test_dropped_parameter_is_reported(self):
        before = {"create": {"actions": [{"action": "draw_text", "parameters": {"text": "hi", "color": "#fff"}}]}}
        after = {"create": {"actions": [{"action": "draw_text", "parameters": {"text": "hi"}}]}}
        issues = diff_events(before, after)
        assert ("create", "param-dropped", "draw_text", "color") in issues

    def test_changed_parameter_is_reported(self):
        """B1: typing 0 saves the default instead."""
        before = {"create": {"actions": [{"action": "set_gravity", "parameters": {"value": 0}}]}}
        after = {"create": {"actions": [{"action": "set_gravity", "parameters": {"value": 0.5}}]}}
        issues = diff_events(before, after)
        assert any(kind == "param-changed" and a == "set_gravity" for _, kind, a, _ in issues)

    def test_lost_action_is_reported(self):
        before = {"create": {"actions": [{"action": "set_lives", "parameters": {}},
                                          {"action": "set_score", "parameters": {}}]}}
        after = {"create": {"actions": [{"action": "set_lives", "parameters": {}}]}}
        issues = diff_events(before, after)
        assert any(kind == "action-lost" and a == "set_score" for _, kind, a, _ in issues)

    def test_nested_then_actions_are_walked(self):
        """B2: a condition that loses its nested then/else actions."""
        before = {"create": {"actions": [{
            "action": "if_condition",
            "parameters": {"then_actions": [{"action": "set_score", "parameters": {"value": 10}}],
                            "else_actions": []},
        }]}}
        after = {"create": {"actions": [{"action": "if_condition", "parameters": {}}]}}
        issues = diff_events(before, after)
        # walk() recurses into then_actions and reports the lost action
        # itself (more precise than a bare "then_actions dropped")
        assert any(kind == "action-lost" and a == "set_score" and "if_condition.then_actions" in where
                   for where, kind, a, _ in issues)

    def test_flat_and_nested_alarm_keys_are_equivalent(self):
        """The runtime accepts both shapes (game_runner's alarm lookup
        checks both), so this alone is not a real loss."""
        before = {"alarm_0": {"actions": [{"action": "set_score", "parameters": {"value": 1}}]}}
        after = {"alarm": {"alarm_0": {"actions": [{"action": "set_score", "parameters": {"value": 1}}]}}}
        assert diff_events(before, after) == []


class TestSummarizeIssues:
    def test_empty_issues_summarize_to_empty(self):
        assert summarize_issues([]) == []

    def test_deduplicates_and_caps_at_limit(self):
        issues = [("create", "param-dropped", "draw_text", "color")] * 5 + \
                 [("create", "action-lost", "set_score", None)]
        out = summarize_issues(issues, limit=3)
        assert len(out) == 2  # deduped
        assert "draw_text's color setting" in out
        assert "the set_score action (and anything nested inside it)" in out


# -------------------------------------------------------------- set_locked
class TestSetLocked:
    def test_not_page_ready_sets_flag_without_js_call(self):
        w = _widget()
        w._page_ready = False
        page = _FakePage()
        w.web_view = _FakeView(page)
        w.set_locked(True, "msg")
        assert w.round_trip_unsafe is True
        assert page.calls == []

    def test_locks_calls_js_with_true_and_message(self):
        w = _widget()
        page = _FakePage()
        w.web_view = _FakeView(page)
        w.set_locked(True, "cannot edit here")
        assert w.round_trip_unsafe is True
        assert len(page.calls) == 1
        assert "setLocked(true" in page.calls[0]
        assert json.dumps("cannot edit here") in page.calls[0]

    def test_unlocks_calls_js_with_false(self):
        w = _widget()
        page = _FakePage()
        w.web_view = _FakeView(page)
        w.set_locked(False)
        assert w.round_trip_unsafe is False
        assert "setLocked(false" in page.calls[0]


# --------------------------------------------------- _check_round_trip_safety
class TestCheckRoundTripSafety:
    def test_exact_round_trip_unlocks(self):
        w = _widget()
        w.round_trip_unsafe = True  # start locked from a previous check
        events = {"create": {"actions": [{"action": "set_score", "parameters": {"value": 5}}]}}
        page = _FakePage(json.dumps(events))  # getCode() reply, then set_locked's own call
        w.web_view = _FakeView(page)
        w._check_round_trip_safety(events)
        assert w.round_trip_unsafe is False
        assert page.calls[0] == "window.blocklyApi.getCode()"
        assert "setLocked(false" in page.calls[1]

    def test_lossy_round_trip_locks_with_a_message_naming_the_loss(self):
        w = _widget()
        before = {"create": {"actions": [{"action": "draw_text", "parameters": {"text": "hi", "color": "#fff"}}]}}
        after = {"create": {"actions": [{"action": "draw_text", "parameters": {"text": "hi"}}]}}
        page = _FakePage(json.dumps(after))
        w.web_view = _FakeView(page)
        w._check_round_trip_safety(before)
        assert w.round_trip_unsafe is True
        assert "setLocked(true" in page.calls[1]
        assert "color" in page.calls[1]

    def test_unparseable_getcode_result_is_treated_as_total_loss_and_locks(self):
        w = _widget()
        events = {"create": {"actions": [{"action": "set_score", "parameters": {"value": 5}}]}}
        page = _FakePage(None)  # getCode() came back null/unparseable
        w.web_view = _FakeView(page)
        w._check_round_trip_safety(events)
        assert w.round_trip_unsafe is True

    def test_skips_entirely_when_page_not_ready(self):
        w = _widget()
        w._page_ready = False
        page = _FakePage()
        w.web_view = _FakeView(page)
        w._check_round_trip_safety({"create": {"actions": []}})
        assert page.calls == []


# ------------------------------------------------- load_events_data wiring
class TestLoadEventsDataWiring:
    def test_empty_events_unlocks_without_touching_the_page(self):
        w = _widget()
        w.round_trip_unsafe = True
        page = _FakePage()
        w.web_view = _FakeView(page)
        w.load_events_data({})
        assert w.round_trip_unsafe is False

    def test_on_load_complete_runs_the_safety_check(self, monkeypatch):
        """load_events_data's JS callback must call _check_round_trip_safety
        with the SAME events_data that was loaded -- the exact wiring the
        audit's root finding depends on being present."""
        w = _widget()
        w.push_asset_lists = lambda: None  # avoid the real asset-walk (needs a parent chain)
        calls = []
        w._check_round_trip_safety = lambda events: calls.append(events)
        page = _FakePage(3)  # loadEvents() reply: "loaded 3 events"
        w.web_view = _FakeView(page)

        events = {"create": {"actions": [{"action": "set_score", "parameters": {"value": 1}}]}}
        w.load_events_data(events)

        assert calls == [events]
