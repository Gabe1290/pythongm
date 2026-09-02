"""LAN multiplayer v2 -- pure protocol/sanitizer unit tests.

docs/MULTIPLAYER_LAN_V2_PLAN.md Phase 4.1: the wire-protocol vocabulary
and the inbound sanitizers in extensions/multiplayer_lan/state.py. No
sockets, no pygame -- state.py is import-light by design, so these import
it directly.

Phase 4.2 (network.py framing/caps/rate-limit) and Phase 5 (session
layer) get their own files; this one is only the pure data helpers.
"""
import json
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT))

from extensions.multiplayer_lan import state  # noqa: E402
from extensions.multiplayer_lan.state import (  # noqa: E402
    PROTO_VER, SNAPSHOT_MSG_TYPE, MSG_SNAP, MSG_HELLO, MSG_WELCOME, MSG_JOIN,
    MSG_LEAVE, MSG_BYE, MSG_MSG, MSG_SHARED_SET, MSG_INPUT, MSG_GAME_START,
    MSG_OWN, MAX_STR_LEN, MAX_COLLECTION_LEN, MAX_VALUE_DEPTH, MAX_NAME_LEN,
    DEFAULT_PLAYER_NAME, is_valid_shared_name, sanitize_name, sanitize_value,
)


# ---------------------------------------------------------------------------
# Protocol vocabulary
# ---------------------------------------------------------------------------

class TestProtocolConstants:
    def test_proto_ver_is_int_at_least_2(self):
        # v1 (the shipped spectator slice) had no version field; v2 starts at 2.
        assert isinstance(PROTO_VER, int)
        assert PROTO_VER >= 2

    def test_message_types_are_distinct_nonempty_strings(self):
        types = [MSG_HELLO, MSG_WELCOME, MSG_JOIN, MSG_LEAVE, MSG_BYE, MSG_MSG,
                 MSG_SHARED_SET, MSG_INPUT, MSG_GAME_START, MSG_SNAP, MSG_OWN]
        for t in types:
            assert isinstance(t, str) and t
        assert len(set(types)) == len(types)

    def test_snapshot_alias_preserved_for_v1(self):
        # v1's network.py / handlers.py / test_multiplayer_lan.py compare
        # against the literal "snap" via this name.
        assert SNAPSHOT_MSG_TYPE == MSG_SNAP == "snap"


# ---------------------------------------------------------------------------
# is_valid_shared_name -- the _parse_value operator-in-name guard
# ---------------------------------------------------------------------------

class TestIsValidSharedName:
    def test_plain_identifiers_pass(self):
        for name in ("score", "score_p1", "_x", "a1", "turn", "PlayerHP", "x_2_y"):
            assert is_valid_shared_name(name), name

    def test_operators_and_punctuation_rejected(self):
        # Exactly the strings that would be routed to eval() by _parse_value.
        for name in ("a+b", "a-b", "a*b", "a/b", "a%b", "a.b", "a b", "a(b)",
                     "a,b", "a=b", "a:b", "1abc", "", "  ", "a\nb", "é"):
            assert not is_valid_shared_name(name), name

    def test_non_str_rejected(self):
        for name in (None, 3, 3.0, True, ["x"], {"x": 1}):
            assert not is_valid_shared_name(name)

    def test_length_cap(self):
        assert is_valid_shared_name("a" * 64)
        assert not is_valid_shared_name("a" * 65)


# ---------------------------------------------------------------------------
# sanitize_name -- player display names
# ---------------------------------------------------------------------------

class TestSanitizeName:
    def test_ordinary_name_unchanged(self):
        assert sanitize_name("Amélie") == "Amélie"

    def test_control_chars_stripped(self):
        assert sanitize_name("Bob\n\t\x00Smith") == "BobSmith"

    def test_whitespace_trimmed(self):
        assert sanitize_name("   Bob   ") == "Bob"

    def test_overlong_truncated(self):
        out = sanitize_name("x" * 100)
        assert len(out) == MAX_NAME_LEN

    def test_blank_or_nonstr_falls_back(self):
        for bad in ("", "   ", "\n\n", None, 42, ["Bob"]):
            assert sanitize_name(bad) == DEFAULT_PLAYER_NAME


# ---------------------------------------------------------------------------
# sanitize_value -- everything that arrives over the wire
# ---------------------------------------------------------------------------

class TestSanitizeValueScalars:
    def test_scalars_pass_through(self):
        assert sanitize_value(3) == 3
        assert sanitize_value(-2.5) == -2.5
        assert sanitize_value("hello") == "hello"
        assert sanitize_value(True) is True
        assert sanitize_value(False) is False
        assert sanitize_value(None) is None

    def test_overlong_string_truncated(self):
        out = sanitize_value("x" * (MAX_STR_LEN + 500))
        assert out == "x" * MAX_STR_LEN

    def test_non_finite_floats_become_none(self):
        assert sanitize_value(float("nan")) is None
        assert sanitize_value(float("inf")) is None
        assert sanitize_value(float("-inf")) is None

    def test_unsupported_scalar_types_become_none(self):
        for bad in (complex(1, 2), b"bytes", {1, 2, 3}, object(), lambda: 1):
            assert sanitize_value(bad) is None


class TestSanitizeValueCollections:
    def test_list_of_scalars(self):
        assert sanitize_value([1, "a", True, None, 2.0]) == [1, "a", True, None, 2.0]

    def test_tuple_becomes_list(self):
        assert sanitize_value((1, 2, 3)) == [1, 2, 3]

    def test_dict_of_scalars(self):
        assert sanitize_value({"hp": 3, "name": "x"}) == {"hp": 3, "name": "x"}

    def test_nested_within_depth(self):
        # depth 0 dict -> depth 1 list -> depth 2 scalars: allowed at MAX_VALUE_DEPTH == 3
        assert sanitize_value({"answers": ["a", "b", "c"]}) == {"answers": ["a", "b", "c"]}

    def test_nesting_past_max_depth_becomes_none(self):
        deep = [[[["too deep"]]]]  # list@0 -> list@1 -> list@2 -> list@3 (>= MAX_VALUE_DEPTH)
        out = sanitize_value(deep)
        assert out == [[[None]]]

    def test_overlong_list_truncated(self):
        out = sanitize_value(list(range(MAX_COLLECTION_LEN + 50)))
        assert out == list(range(MAX_COLLECTION_LEN))

    def test_overlong_dict_truncated(self):
        big = {f"k{i}": i for i in range(MAX_COLLECTION_LEN + 50)}
        out = sanitize_value(big)
        assert len(out) == MAX_COLLECTION_LEN

    def test_non_str_dict_keys_dropped(self):
        out = sanitize_value({"ok": 1, 2: "x", (1, 2): "y", None: "z"})
        assert out == {"ok": 1}

    def test_unsupported_nested_value_becomes_none_in_place(self):
        out = sanitize_value({"a": 1, "b": {1, 2}, "c": [object(), 3]})
        assert out == {"a": 1, "b": None, "c": [None, 3]}

    def test_result_is_json_serializable(self):
        payload = {"event": "buzz", "data": {"choice": "B", "history": [1, 2, 3],
                   "bad": {1, 2}, "deep": [[[[1]]]]}}
        cleaned = sanitize_value(payload)
        # Round-trips through JSON without error -- the real guarantee.
        assert json.loads(json.dumps(cleaned)) == cleaned

    def test_does_not_mutate_input(self):
        src = {"a": [1, 2, {"b": 3}]}
        sanitize_value(src)
        assert src == {"a": [1, 2, {"b": 3}]}
