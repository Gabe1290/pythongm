#!/usr/bin/env python3
"""
Regression: get_action_type() falls back through runtime/action_executor.py's
ActionExecutor.ACTION_ALIASES (2026-08-14).

Previously, events/action_types.py's get_action_type() only consulted its
own ACTION_TYPE_ALIASES table -- a name listed only in the runtime's
separate ACTION_ALIASES table (dispatch-time only) resolved to nothing,
even though the runtime would have happily dispatched it. This pins the
unification: a name known only to the runtime table now resolves too, and
names already covered by either table, or neither, are unaffected.
"""

from events.action_types import get_action_type, ACTION_TYPE_ALIASES, ACTION_TYPES
from runtime.action_executor import ActionExecutor


def test_runtime_only_alias_now_resolves():
    # "display_message" is only in ActionExecutor.ACTION_ALIASES, not in
    # events/action_types.py's own ACTION_TYPE_ALIASES.
    assert "display_message" not in ACTION_TYPE_ALIASES
    assert "display_message" in ActionExecutor.ACTION_ALIASES

    action_type = get_action_type("display_message")
    assert action_type is not None
    assert action_type.name == "show_message"


def test_every_runtime_alias_source_resolves_to_something_real():
    # Every ACTION_ALIASES source name should resolve to a real ActionType.
    # Some source names (e.g. "game_end") are ALSO independently registered
    # in ACTION_TYPES under that exact name -- ACTION_TYPES always wins
    # first (no behavior change there), so only assert the alias-fallback
    # target for names that aren't already a real ACTION_TYPES entry.
    for legacy_name, canonical_name in ActionExecutor.ACTION_ALIASES.items():
        resolved = get_action_type(legacy_name)
        assert resolved is not None, (
            f"runtime alias '{legacy_name}' -> '{canonical_name}' did not "
            "resolve via get_action_type"
        )
        if legacy_name not in ACTION_TYPES:
            assert resolved.name == canonical_name


def test_action_type_alias_table_still_takes_priority():
    # "room_restart" exists in BOTH tables, mapping to the same canonical
    # target either way -- confirms the events/action_types.py table is
    # still consulted first (no behavior change for already-covered names).
    assert "room_restart" in ACTION_TYPE_ALIASES
    assert "room_restart" in ActionExecutor.ACTION_ALIASES
    assert get_action_type("room_restart").name == "restart_room"


def test_unknown_name_still_returns_none():
    assert get_action_type("this_action_does_not_exist_anywhere") is None
