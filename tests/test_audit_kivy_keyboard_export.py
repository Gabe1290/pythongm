"""Regression tests for the Kivy exporter keyboard / background findings.

Covers:
- M35: keyboard_release events are emitted (as on_keyboard_up) instead of dropped.
- M36: plain set_hspeed/set_vspeed keyboard events are NOT rewritten into the
  grid-stepping handler (which discards every non-speed action).
- M37: duplicate generated method names (e.g. two on_keyboard / two on_update)
  are merged so the earlier body is not silently shadowed.
- L22: the scene background loader uses the actual copied filename/extension,
  not a hardcoded '<asset name>.png'.

Pure code-generation logic, no Qt widgets required.
"""

import ast
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT / "export" / "Kivy"))

from kivy_exporter import KivyExporter  # noqa: E402


def _make_exporter(project_data, tmp_path):
    out = tmp_path / "out"
    return KivyExporter(project_data, project_path=tmp_path, output_path=out)


def _method_names(class_body_src):
    """Return the list of def names found in generated method-body text."""
    names = []
    for line in class_body_src.split("\n"):
        s = line.strip()
        if s.startswith("def "):
            names.append(s[4:].split("(", 1)[0])
    return names


# --------------------------------------------------------------------------
# M35 — keyboard_release is exported as on_keyboard_up
# --------------------------------------------------------------------------

def test_m35_keyboard_release_emits_on_keyboard_up(tmp_path):
    # OUR implementation keys release sub-events by the (lowercase) direction
    # name, mapping it to the real pygame key code in _generate_keyboard_release_handler
    # (left->276, right->275). The finding intent — release events emit an
    # on_keyboard_up handler keyed by the real key codes — is preserved.
    events = {
        "keyboard_release": {
            "left": {
                "actions": [
                    {"action": "stop_movement", "parameters": {}},
                ],
            },
            "right": {
                "actions": [
                    {"action": "stop_movement", "parameters": {}},
                ],
            },
        }
    }
    project = {"name": "P", "assets": {"objects": {"obj_p": {"events": events}}, "sprites": {}}}
    exp = _make_exporter(project, tmp_path)
    (exp.output_path / "game" / "objects").mkdir(parents=True, exist_ok=True)
    exp._generate_object("obj_p", {"events": events})
    src = (exp.output_path / "game" / "objects" / "obj_p.py").read_text()

    assert "def on_keyboard_up(self, key, scancode):" in src, src
    # The release actions must be keyed by the real key codes.
    assert "key == 276" in src and "key == 275" in src, src
    # And it must parse.
    ast.parse(src)


# --------------------------------------------------------------------------
# M36 — plain set_hspeed/set_vspeed does NOT trigger the grid handler
# --------------------------------------------------------------------------

def test_m36_plain_speed_keyboard_is_not_grid_movement(tmp_path):
    project = {"name": "P", "assets": {}}
    exp = _make_exporter(project, tmp_path)

    # Platformer-style player: right/left flip sprite + set_hspeed; up is a
    # collision-gated jump (if_collision then set_vspeed).
    keyboard_events = [
        {
            "event_type": "keyboard",
            "key_name": "right",
            "actions": [
                {"action": "set_sprite", "parameters": {"sprite": "spr_r"}},
                {"action": "set_hspeed", "parameters": {"speed": "4"}},
            ],
        },
        {
            "event_type": "keyboard",
            "key_name": "up",
            "actions": [
                {"action": "if_collision", "parameters": {"x": "0", "y": "1", "object": "solid", "not_flag": False}},
                {"action": "set_vspeed", "parameters": {"speed": "-10"}},
            ],
        },
    ]
    handler = exp._generate_keyboard_handler(keyboard_events)

    # Must produce a real on_keyboard handler, NOT the synthesized grid on_update.
    assert "def on_keyboard(" in handler, handler
    assert "def on_update(" not in handler, handler
    # Grid-only scaffolding must be absent.
    assert "_grid_target_x" not in handler, handler


def test_m36_if_on_grid_still_uses_grid_handler(tmp_path):
    project = {"name": "P", "assets": {}}
    exp = _make_exporter(project, tmp_path)

    keyboard_events = [
        {
            "event_type": "keyboard",
            "key_name": "right",
            "actions": [
                {
                    "action": "if_on_grid",
                    "parameters": {
                        "then_actions": [
                            {"action": "set_hspeed", "parameters": {"value": 4}},
                        ]
                    },
                },
            ],
        }
    ]
    handler = exp._generate_keyboard_handler(keyboard_events)
    assert "def on_update(" in handler, handler
    assert "_grid_target_x" in handler, handler


# --------------------------------------------------------------------------
# M37 — duplicate method names are merged, not shadowed
# --------------------------------------------------------------------------

def test_m37_no_duplicate_on_keyboard(tmp_path):
    project = {"name": "P", "assets": {}}
    exp = _make_exporter(project, tmp_path)

    events = [
        {
            "event_type": "keyboard",
            "key_name": "right",
            "actions": [{"action": "set_hspeed", "parameters": {"speed": "4"}}],
        },
        {
            "event_type": "keyboard_press",
            "key_name": "up",
            "actions": [{"action": "set_vspeed", "parameters": {"speed": "-10"}}],
        },
    ]
    body = exp._generate_event_methods("obj_p", events)
    names = _method_names(body)
    assert names.count("on_keyboard") == 1, (names, body)
    # The merged class body must parse.
    ast.parse("class C:\n" + body)


def test_m37_step_does_not_shadow_grid_on_update(tmp_path):
    project = {"name": "P", "assets": {}}
    exp = _make_exporter(project, tmp_path)

    # Force grid movement (if_on_grid) so the keyboard handler emits on_update,
    # then add a step event (also on_update). They must merge into one method.
    events = [
        {
            "event_type": "keyboard",
            "key_name": "right",
            "actions": [
                {
                    "action": "if_on_grid",
                    "parameters": {
                        "then_actions": [
                            {"action": "set_hspeed", "parameters": {"value": 4}},
                        ]
                    },
                }
            ],
        },
        {
            "event_type": "step",
            "actions": [{"action": "set_gravity", "parameters": {"direction": "270", "gravity": "0.45"}}],
        },
    ]
    body = exp._generate_event_methods("obj_p", events)
    names = _method_names(body)
    assert names.count("on_update") == 1, (names, body)
    # The grid scaffolding (from the keyboard handler) AND the step gravity body
    # must both survive in the single merged method.
    assert "_grid_target_x" in body, body
    assert "gravity" in body.lower(), body
    ast.parse("class C:\n" + body)


def test_m37_merge_helper_combines_bodies(tmp_path):
    blocks = [
        '    def on_update(self, dt):\n        """Step event"""\n        self.a = 1\n',
        '    def on_update(self, dt):\n        """Step event"""\n        self.b = 2\n',
    ]
    # OUR _merge_duplicate_methods is an instance method; call it via an instance.
    exp = _make_exporter({"name": "P", "assets": {}}, tmp_path)
    merged = exp._merge_duplicate_methods(blocks)
    assert len(merged) == 1
    combined = merged[0]
    assert combined.count("def on_update") == 1
    assert "self.a = 1" in combined
    assert "self.b = 2" in combined


# --------------------------------------------------------------------------
# L22 — background loader uses the real copied filename/extension
# --------------------------------------------------------------------------

def test_l22_background_uses_real_filename(tmp_path):
    project = {
        "name": "P",
        "assets": {
            "objects": {},
            "sprites": {},
            "backgrounds": {
                "bg_sky": {"file_path": "backgrounds/sky_photo.jpg"},
            },
            "rooms": {},
        },
    }
    exp = _make_exporter(project, tmp_path)
    (exp.output_path / "game" / "scenes").mkdir(parents=True, exist_ok=True)

    room_data = {"width": 800, "height": 600, "instances": [], "background": "bg_sky"}
    exp._generate_scene("room_main", room_data)
    src = (exp.output_path / "game" / "scenes" / "room_main.py").read_text()

    # EIO-11: the exported name is now keyed on the (unique) ASSET NAME plus the
    # source EXTENSION — so a non-PNG background keeps its real extension (the
    # L22 intent) while two assets sharing a source basename can't collide.
    assert "assets/images/bg_sky.jpg" in src, src
    # The old hardcoded '<name>.png' form must still be gone (real ext kept).
    assert "assets/images/bg_sky.png" not in src, src
    ast.parse(src)


def test_l22_background_fallback_when_no_file_path(tmp_path):
    project = {
        "name": "P",
        "assets": {"objects": {}, "sprites": {}, "backgrounds": {}, "rooms": {}},
    }
    exp = _make_exporter(project, tmp_path)
    (exp.output_path / "game" / "scenes").mkdir(parents=True, exist_ok=True)

    room_data = {"width": 800, "height": 600, "instances": [], "background": "bg_unknown"}
    exp._generate_scene("room_main", room_data)
    src = (exp.output_path / "game" / "scenes" / "room_main.py").read_text()
    # No asset/file_path -> fall back to '<name>.png'.
    assert "assets/images/bg_unknown.png" in src, src
