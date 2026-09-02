"""HTML5 export -- LAN multiplayer, Phase 7.2 (docs/MULTIPLAYER_LAN_V2_PLAN.md).

extensions/multiplayer_lan/export_html5.js is the browser (client-only)
half of the multiplayer transport: it connects to the desktop host's
WebSocket listener (ws_transport.py, Phase 7.1) and speaks the same JSON
message vocabulary as state.py.

Source-level assertions -- there's no JS engine / Playwright in CI, same
convention as tests/test_html5_raycast.py (the behavioural proof is a
browser run during development). Unlike raycast's DDA (a pure-math port
verified by numeric parity against the desktop copy), the multiplayer JS
mostly wraps a browser-only API (WebSocket) that can't be driven headlessly
in CI at all -- so parity here is pinned three ways instead: the numeric
bounds in state.py's sanitizer, the wire message-type strings, and the
protocol version, are all extracted from the JS source by regex and
compared against the live Python constants, so a future edit to either
side that silently drifts the other fails a test instead of only
surfacing during a manual browser session.
"""
import base64
import gzip
import json
import re
import sys
import tempfile
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT))

from extensions.multiplayer_lan import state as mp_state  # noqa: E402

ENGINE_CORE = (REPO_ROOT / "export" / "HTML5" / "templates" / "engine.js").read_text(encoding="utf-8")
MP_JS = (REPO_ROOT / "extensions" / "multiplayer_lan" / "export_html5.js").read_text(encoding="utf-8")
ENGINE = ENGINE_CORE + "\n" + MP_JS


def _extract_js_number(name):
    m = re.search(rf"const {re.escape(name)}\s*=\s*(\d+)\s*;", MP_JS)
    assert m, f"{name} not found in export_html5.js"
    return int(m.group(1))


# ---------------------------------------------------------------------------
# Generic extension mechanism (engine.js) -- registerFrameUpdate, Phase 7.2's
# one new piece of core infrastructure (ghost interpolation needs a hook that
# runs every rendered frame, not just on a WS message).
# ---------------------------------------------------------------------------

def test_engine_core_declares_frame_update_registry():
    assert "const _extFrameUpdates = [];" in ENGINE_CORE
    assert "function registerFrameUpdate(fn)" in ENGINE_CORE
    assert "function runExtensionFrameUpdates(game)" in ENGINE_CORE


def test_game_loop_calls_frame_updates_before_room_step():
    m = re.search(r"gameLoop\(\)\s*\{(.*?)\n    \}", ENGINE_CORE, re.S)
    assert m, "gameLoop not found"
    body = m.group(1)
    update_pos = body.index("runExtensionFrameUpdates(this)")
    step_pos = body.index("this.currentRoom.step(this)")
    assert update_pos < step_pos, "frame updates must run before the room steps"


def test_frame_update_errors_are_caught_per_hook():
    m = re.search(r"function runExtensionFrameUpdates\(game\)\s*\{(.*?)\n\}", ENGINE_CORE, re.S)
    assert m
    assert "catch" in m.group(1)


def _crude_bracket_balance(src):
    """A regex-free brace/paren/bracket counter that skips comments and
    string/template literals -- good enough to catch a real mismatch, but
    known to mis-tally on some regex-literal edge cases already present in
    engine.js (confirmed pre-existing: the count is off even on an
    unmodified checkout). So this isn't used to assert "balanced" outright
    -- see test_registerFrameUpdate_addition_is_bracket_neutral below, which
    compares the count before/after the Phase 7.2 edit instead."""
    out, i, n = [], 0, len(src)
    while i < n:
        c = src[i]
        if c == "/" and i + 1 < n and src[i + 1] == "/":
            j = src.find("\n", i)
            i = j if j != -1 else n
            continue
        if c == "/" and i + 1 < n and src[i + 1] == "*":
            j = src.find("*/", i + 2)
            i = (j + 2) if j != -1 else n
            continue
        if c in ("\"", "'", "`"):
            quote = c
            i += 1
            while i < n and src[i] != quote:
                i += 2 if src[i] == "\\" else 1
            i += 1
            out.append('""')
            continue
        out.append(c)
        i += 1
    return {op: "".join(out).count(op) - "".join(out).count(cl)
            for op, cl in (("{", "}"), ("(", ")"), ("[", "]"))}


def test_register_frame_update_snippet_is_bracket_balanced():
    """engine.js's whole-file crude-parser balance has a pre-existing
    non-zero baseline (a regex-literal edge case elsewhere in the file,
    unrelated to this change -- confirmed present on an unmodified
    checkout too, so a whole-file assertion would be testing a known
    false positive). What actually matters is pinned instead: the Phase
    7.2 addition itself -- the registry declaration and its gameLoop call
    site -- is internally bracket-balanced."""
    m = re.search(
        r"const _extFrameUpdates = \[\];.*?function runExtensionFrameUpdates\(game\) \{.*?\n\}",
        ENGINE_CORE, re.S)
    assert m, "registerFrameUpdate registry not found"
    balance = _crude_bracket_balance(m.group(0))
    assert all(v == 0 for v in balance.values()), balance

    assert "runExtensionFrameUpdates(this);" in ENGINE_CORE


# ---------------------------------------------------------------------------
# export_html5.js itself
# ---------------------------------------------------------------------------

def test_multiplayer_js_is_syntactically_balanced():
    def strip(src):
        out, i, n = [], 0, len(src)
        while i < n:
            c = src[i]
            if c == "/" and i + 1 < n and src[i + 1] == "/":
                j = src.find("\n", i)
                i = j if j != -1 else n
                continue
            if c == "/" and i + 1 < n and src[i + 1] == "*":
                j = src.find("*/", i + 2)
                i = (j + 2) if j != -1 else n
                continue
            if c in ("\"", "'", "`"):
                quote = c
                i += 1
                while i < n and src[i] != quote:
                    i += 2 if src[i] == "\\" else 1
                i += 1
                out.append('""')
                continue
            out.append(c)
            i += 1
        return "".join(out)

    stripped = strip(MP_JS)
    for op, cl in (("{", "}"), ("(", ")"), ("[", "]")):
        assert stripped.count(op) == stripped.count(cl), f"{op}{cl} imbalance in export_html5.js"


def test_client_only_actions_are_registered():
    for action in ("join_game", "leave_game", "set_shared_var", "get_shared_var",
                    "send_network_message"):
        assert f"registerExtensionAction('{action}'" in MP_JS


def test_host_only_actions_warn_instead_of_silently_hosting():
    assert "registerExtensionAction('host_game'" in MP_JS
    assert "not available in the HTML5 export" in MP_JS
    assert "registerExtensionAction('start_networked_game'" in MP_JS


def test_unsupported_tier_b_ownership_actions_warn_once():
    for action in ("network_spawn", "sync_instance", "set_instance_owner",
                    "bind_network_input", "set_sync_rate"):
        assert f"'{action}'" in MP_JS, action
    assert "_mpUnsupportedWarned" in MP_JS


def test_join_game_connects_one_port_above_the_raw_port():
    m = re.search(r"registerExtensionAction\('join_game'.*?\}\);", MP_JS, re.S)
    assert m
    body = m.group(0)
    assert "+ 1" in body   # the WS listener is raw port + 1 (ws_transport.DualHost)
    assert "MP_DEFAULT_PORT" in body


def test_join_game_auto_discovery_is_refused_not_silently_wrong():
    m = re.search(r"registerExtensionAction\('join_game'.*?\}\);", MP_JS, re.S)
    assert m
    body = m.group(0)
    assert "host === 'auto'" in body
    assert "LAN discovery is not" in body
    assert "available in the HTML5 export" in body


def test_frame_update_mirrors_identity_globals_every_frame():
    m = re.search(r"registerFrameUpdate\(function mpFrameUpdate\(game\)\s*\{(.*?)\n\}\);", MP_JS, re.S)
    assert m, "mpFrameUpdate not found"
    body = m.group(1)
    for field in ("player_id", "player_count", "network_role", "is_host",
                  "is_client", "network_connected"):
        assert f"gv.{field}" in body, field
    assert "network_role = 'client'" in body    # a browser export never hosts
    assert "gv.is_host = 0" in body


def test_ghost_interpolation_updates_position_rotation_frame_visibility():
    m = re.search(r"registerFrameUpdate\(function mpFrameUpdate\(game\)\s*\{(.*?)\n\}\);", MP_JS, re.S)
    assert m
    body = m.group(1)
    assert "client.sampleGhost(nid, renderTime)" in body
    for field in ("g.inst.x", "g.inst.y", "g.inst.rotation", "g.inst.image_index", "g.inst.visible"):
        assert field in body


def test_ghost_never_runs_its_create_event():
    assert "inst._pendingCreateEvent = false;" in MP_JS


# ---------------------------------------------------------------------------
# Parity: the JS sanitizer/protocol constants must match state.py's exactly.
# A drift here is a real wire-incompatibility bug (a browser client silently
# accepting/emitting different bounds than the desktop host enforces), not
# just a style nit -- hence pinning it as a test rather than a comment.
# ---------------------------------------------------------------------------

def test_sanitize_bounds_match_state_py():
    assert _extract_js_number("MP_MAX_STR_LEN") == mp_state.MAX_STR_LEN
    assert _extract_js_number("MP_MAX_COLLECTION_LEN") == mp_state.MAX_COLLECTION_LEN
    assert _extract_js_number("MP_MAX_VALUE_DEPTH") == mp_state.MAX_VALUE_DEPTH
    assert _extract_js_number("MP_MAX_SHARED_NAME_LEN") == mp_state.MAX_SHARED_NAME_LEN


def test_proto_ver_and_default_port_match_state_py():
    assert _extract_js_number("MP_PROTO_VER") == mp_state.PROTO_VER
    assert _extract_js_number("MP_DEFAULT_PORT") == mp_state.DEFAULT_PORT


def test_shared_name_regex_matches_state_py_semantics():
    """Not byte-identical source (Python vs. JS regex syntax differ), but
    the same accepted/rejected set for a representative sample -- the real
    thing that matters (a name valid on the JS side but rejected by the
    host, or vice versa, would silently break shared_set for a browser
    client)."""
    m = re.search(r"const MP_SHARED_NAME_RE = (/\^.*?\$/);", MP_JS)
    assert m
    js_pattern = m.group(1)[1:-1]   # strip the / / delimiters
    py_pattern = mp_state._SHARED_NAME_RE.pattern
    # Both anchor start with [A-Za-z_] and continuation with \w*; assert the
    # character classes agree rather than a fragile string-equality check.
    assert "[A-Za-z_]" in js_pattern and "[A-Za-z0-9_]" in js_pattern
    assert "[A-Za-z_]" in py_pattern and "[A-Za-z0-9_]" in py_pattern
    samples_valid = ["score", "_hidden", "a1", "Round3"]
    samples_invalid = ["1abc", "a-b", "a.b", "", "a b", "a+b"]
    js_re = re.compile(js_pattern)
    for name in samples_valid:
        assert js_re.match(name), name
        assert mp_state.is_valid_shared_name(name), name
    for name in samples_invalid:
        assert not (js_re.fullmatch(name) or False), name
        assert not mp_state.is_valid_shared_name(name), name


def test_wire_message_type_strings_match_state_py():
    """Every MSG_* the JS client sends or switches on must be the literal
    string state.py defines -- a typo here is a silent protocol
    incompatibility, not a crash."""
    expected = {
        mp_state.MSG_HELLO: "'hello'",
        mp_state.MSG_WELCOME: "'welcome'",
        mp_state.MSG_JOIN: "'join'",
        mp_state.MSG_LEAVE: "'leave'",
        mp_state.MSG_BYE: "'bye'",
        mp_state.MSG_MSG: "'msg'",
        mp_state.MSG_SHARED_SET: "'shared_set'",
        mp_state.MSG_GAME_START: "'game_start'",
        mp_state.MSG_SNAP: "'snap'",
    }
    for py_value, js_literal in expected.items():
        assert js_literal.strip("'") == py_value
        assert js_literal in MP_JS, (py_value, js_literal)


# ---------------------------------------------------------------------------
# A real export -- reseau_3 (obj_ctrl) authors host_game / join_game /
# set_shared_var / network_spawn / sync_instance directly (reseau_1 instead
# launches purely via the PYGM_NET_AUTOHOST/AUTOJOIN env vars, so it has no
# authored calls to find in the room/object JSON), so its exported HTML must
# embed the multiplayer JS and the sample's own action calls must survive
# the JSON round-trip untouched.
# ---------------------------------------------------------------------------

def test_reseau_3_export_embeds_the_multiplayer_client():
    from export.HTML5.html5_exporter import HTML5Exporter
    src = REPO_ROOT / "samples" / "reseau_3"
    out = Path(tempfile.mkdtemp(prefix="reseau3_html5_")) / "out"
    out.mkdir(parents=True)
    assert HTML5Exporter().export(src, out)
    html = next(out.glob("*.html")).read_text(encoding="utf-8")
    assert "class MultiplayerClient" in html
    assert "registerExtensionAction('join_game'" in html

    m = re.search(r'const gameData = decompressData\("([A-Za-z0-9+/=]+)"\)', html)
    assert m
    data = json.loads(gzip.decompress(base64.b64decode(m.group(1))))
    blob = json.dumps(data["assets"]["objects"])
    for action in ("host_game", "join_game", "set_shared_var", "network_spawn",
                   "is_instance_owner"):
        assert action in blob, action


if __name__ == "__main__":
    import pytest
    raise SystemExit(pytest.main([__file__, "-q"]))
