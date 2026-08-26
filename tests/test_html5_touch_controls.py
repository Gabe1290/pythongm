"""Reported after the responsive-layout fix landed: HTML5-exported games
render correctly on a phone now, but there's no way to actually PLAY them
-- no physical keyboard on a phone, and no on-screen controls, so a
keyboard-only game (maze, platformer, raycast, Sky Strike, side-scroller)
was simply unplayable on mobile even though it displayed fine.

Fix: html5_exporter.py scans every object's keyboard/keyboard_press/
keyboard_release events for the key names actually bound anywhere in the
project (_detect_keyboard_controls) and, when any are found, emits an
on-screen d-pad (for arrow/WASD movement) plus one action button per
OTHER bound key (e.g. Sky Strike's space=shoot, z=bomb) into a new
{touch_controls_html} template slot. engine.js's setupTouchControls()
wires each button's data-key to the SAME this.keys/keysPressed/
keysReleased state a real keydown/keyup produces, so every existing
keyboard handler works unmodified -- and only reveals the panel on an
actual touchscreen (ontouchstart/maxTouchPoints), so a desktop visitor
with a real keyboard never sees it. A project with no keyboard events at
all (pure mouse/touch, e.g. Match 3) gets no panel -- nothing to add.

This mirrors export/Kivy/kivy_exporter.py's existing VirtualDPad /
NEEDS_DPAD convention for Android (arrows-only d-pad, gated on whether
the project uses ANY keyboard event) -- generalized here to also cover
non-movement action keys, since without them a game like Sky Strike would
display and move correctly on mobile but have no way to fire.
"""
import re
import shutil
import sys
import tempfile
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT))

from export.HTML5.html5_exporter import HTML5Exporter  # noqa: E402

ENGINE = (REPO_ROOT / "export" / "HTML5" / "templates" / "engine.js").read_text(encoding="utf-8")
TEMPLATE = (REPO_ROOT / "export" / "HTML5" / "templates" / "game_template.html").read_text(encoding="utf-8")


def _copy_sample(name):
    src = REPO_ROOT / "samples" / name
    tmp = Path(tempfile.mkdtemp(prefix="touch_controls_export_"))
    proj = tmp / "proj"
    shutil.copytree(src, proj)
    out = tmp / "out"
    out.mkdir()
    return proj, out


def _make_exporter():
    return HTML5Exporter()


def _project_data(objects_events):
    """objects_events: {object_name: {event_name: {key: {...}}}}"""
    return {
        "assets": {
            "objects": {
                name: {"name": name, "events": events}
                for name, events in objects_events.items()
            }
        }
    }


# ---------------------------------------------------------------------------
# _detect_keyboard_controls
# ---------------------------------------------------------------------------

def test_no_keyboard_events_means_no_controls_needed():
    ex = _make_exporter()
    pdata = _project_data({"obj_grid": {"draw": {}}})
    needs_dpad, action_keys = ex._detect_keyboard_controls(pdata)
    assert needs_dpad is False
    assert action_keys == []


def test_arrow_keys_trigger_dpad_with_no_action_buttons():
    ex = _make_exporter()
    pdata = _project_data({
        "obj_person": {"keyboard": {"left": {}, "right": {}, "up": {}, "down": {}}}
    })
    needs_dpad, action_keys = ex._detect_keyboard_controls(pdata)
    assert needs_dpad is True
    assert action_keys == []


def test_wasd_alone_also_triggers_dpad_no_duplicate_buttons():
    """WASD is movement, same as arrows -- it must not ALSO produce
    action buttons for w/a/s/d (that would be 4 redundant buttons next
    to a d-pad already covering the same directions)."""
    ex = _make_exporter()
    pdata = _project_data({
        "obj_player": {"keyboard": {"w": {}, "a": {}, "s": {}, "d": {}}}
    })
    needs_dpad, action_keys = ex._detect_keyboard_controls(pdata)
    assert needs_dpad is True
    assert action_keys == []


def test_non_movement_keys_become_action_buttons():
    ex = _make_exporter()
    pdata = _project_data({
        "obj_player": {
            "keyboard": {"left": {}, "right": {}, "up": {}, "down": {},
                         "a": {}, "d": {}, "w": {}, "s": {}, "space": {}, "z": {}},
        }
    })
    needs_dpad, action_keys = ex._detect_keyboard_controls(pdata)
    assert needs_dpad is True
    assert action_keys == ["space", "z"]


def test_key_names_are_case_insensitive_and_deduplicated():
    ex = _make_exporter()
    pdata = _project_data({
        "obj_a": {"keyboard": {"LEFT": {}}},
        "obj_b": {"keyboard_release": {"left": {}}},
    })
    needs_dpad, action_keys = ex._detect_keyboard_controls(pdata)
    assert needs_dpad is True
    assert action_keys == []


def test_pseudo_keys_nokey_and_anykey_never_produce_a_button():
    ex = _make_exporter()
    pdata = _project_data({
        "obj_person": {"keyboard": {"left": {}, "nokey": {}}},
        "obj_ctrl": {"keyboard_press": {"anykey": {}}},
    })
    needs_dpad, action_keys = ex._detect_keyboard_controls(pdata)
    assert needs_dpad is True
    assert action_keys == []


def test_keyboard_press_and_release_events_are_both_scanned():
    ex = _make_exporter()
    pdata = _project_data({
        "obj_player": {
            "keyboard_press": {"space": {}},
            "keyboard_release": {"LEFT": {}, "RIGHT": {}},
        }
    })
    needs_dpad, action_keys = ex._detect_keyboard_controls(pdata)
    assert needs_dpad is True
    assert action_keys == ["space"]


def test_malformed_object_entries_are_skipped_not_crashed_on():
    ex = _make_exporter()
    pdata = {"assets": {"objects": {
        "obj_ok": {"name": "obj_ok", "events": {"keyboard": {"left": {}}}},
        "obj_bad": "not a dict",
        "obj_bad2": {"name": "obj_bad2", "events": "not a dict either"},
    }}}
    needs_dpad, action_keys = ex._detect_keyboard_controls(pdata)
    assert needs_dpad is True
    assert action_keys == []


# ---------------------------------------------------------------------------
# _build_touch_controls_html
# ---------------------------------------------------------------------------

def test_build_html_empty_when_nothing_needed():
    ex = _make_exporter()
    assert ex._build_touch_controls_html(False, []) == ""


def test_build_html_dpad_only():
    ex = _make_exporter()
    out = ex._build_touch_controls_html(True, [])
    assert '<div id="touchControls">' in out
    assert '<div id="dpad">' in out
    assert 'data-key="up"' in out
    assert 'data-key="left"' in out
    assert 'data-key="right"' in out
    assert 'data-key="down"' in out
    assert 'id="actionButtons"' not in out


def test_build_html_action_buttons_only():
    ex = _make_exporter()
    out = ex._build_touch_controls_html(False, ["space"])
    assert 'id="dpad"' not in out
    assert '<div id="actionButtons">' in out
    assert 'data-key="space"' in out


def test_build_html_known_key_gets_a_glyph_label():
    ex = _make_exporter()
    out = ex._build_touch_controls_html(False, ["space", "enter"])
    assert '>⎵<' in out
    assert '>⏎<' in out


def test_build_html_unknown_single_letter_uppercases():
    ex = _make_exporter()
    out = ex._build_touch_controls_html(False, ["z"])
    assert 'data-key="z"' in out
    assert '>Z<' in out


def test_build_html_key_names_are_escaped():
    ex = _make_exporter()
    # Not a realistic key name, but _build_touch_controls_html must not
    # trust its input blindly -- html5_exporter.py escapes {game_name}
    # for the same reason (L1: HTML text-context injection).
    out = ex._build_touch_controls_html(False, ['"><script>'])
    assert "<script>" not in out
    assert "&lt;script&gt;" in out or "&quot;" in out


# ---------------------------------------------------------------------------
# Template source-level assertions
# ---------------------------------------------------------------------------

def test_template_has_touch_controls_placeholder():
    assert "{touch_controls_html}" in TEMPLATE


def test_template_touch_controls_css_hidden_by_default():
    m = re.search(r"#touchControls\s*\{(.*?)\n        \}", TEMPLATE, re.S)
    assert m
    assert "display: none;" in m.group(1)


def test_engine_setup_touch_controls_wires_data_key_buttons():
    m = re.search(r"setupTouchControls\(\) \{(.*?)\n    \}", ENGINE, re.S)
    assert m, "setupTouchControls not found"
    body = m.group(1)
    assert "'[data-key]'" in body
    assert "touchstart" in body
    assert "touchend" in body
    assert "mousedown" in body
    assert "mouseup" in body


def test_engine_touch_controls_only_reveal_on_a_real_touchscreen():
    m = re.search(r"setupTouchControls\(\) \{(.*?)\n    \}", ENGINE, re.S)
    assert m
    body = m.group(1)
    assert "ontouchstart" in body
    assert "maxTouchPoints" in body


def test_engine_calls_setup_touch_controls_from_constructor():
    assert "this.setupTouchControls();" in ENGINE


# ---------------------------------------------------------------------------
# End-to-end: real exports
# ---------------------------------------------------------------------------

def test_real_export_maze_1_gets_a_dpad():
    proj, out = _copy_sample("maze_1")
    assert HTML5Exporter().export(proj, out)
    html_out = next(out.glob("*.html")).read_text(encoding="utf-8")
    assert '<div id="touchControls">' in html_out
    assert 'id="dpad"' in html_out


def test_real_export_match3_1_has_no_touch_controls():
    """Match 3 is tap/click-driven -- no keyboard events at all, so no
    on-screen d-pad should appear (nothing to bind it to)."""
    proj, out = _copy_sample("match3_1")
    assert HTML5Exporter().export(proj, out)
    html_out = next(out.glob("*.html")).read_text(encoding="utf-8")
    assert '<div id="touchControls">' not in html_out


def test_real_export_placeholder_always_resolved():
    proj, out = _copy_sample("maze_1")
    assert HTML5Exporter().export(proj, out)
    html_out = next(out.glob("*.html")).read_text(encoding="utf-8")
    assert "{touch_controls_html}" not in html_out


if __name__ == "__main__":
    import pytest
    raise SystemExit(pytest.main([__file__, "-q"]))
