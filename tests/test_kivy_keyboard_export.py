"""Regression tests for Kivy keyboard export (audits M35, M36, M37).

M35: keyboard_release events were dropped (no expansion branch, no dispatch).
M36: the grid-movement heuristic fired on any set_hspeed/set_vspeed, hijacking
     platformer keyboard events and discarding non-speed actions.
M37: a grid keyboard handler and a step event both emit on_update (and keyboard
     + keyboard_press both emit on_keyboard); Python kept only the last def,
     silently shadowing the other.
"""

from pathlib import Path

import pytest

from export.Kivy.kivy_exporter import KivyExporter


@pytest.fixture
def exporter(tmp_path):
    return KivyExporter({"name": "T", "assets": {}}, tmp_path, tmp_path / "out")


def _kb(key, actions):
    return {"event_type": "keyboard", "key_name": key, "actions": actions}


def _hspeed(v):
    return {"action": "set_hspeed", "parameters": {"value": v}}


def _if_on_grid(then):
    return {"action": "if_on_grid", "parameters": {"then_actions": then}}


class TestGridHeuristic:  # M36
    def test_plain_speed_keyboard_uses_normal_handler(self, exporter):
        code = exporter._generate_keyboard_handler([_kb("left", [_hspeed(-4)])])
        assert "def on_keyboard(" in code
        assert "def on_update(" not in code

    def test_if_on_grid_keyboard_uses_grid_handler(self, exporter):
        code = exporter._generate_keyboard_handler(
            [_kb("left", [_if_on_grid([_hspeed(-4)])])])
        assert "def on_update(" in code


class TestKeyboardReleaseHandler:  # M35
    def test_release_generates_on_keyboard_up(self, exporter):
        events = [{"event_type": "keyboard_release", "key_name": "left",
                   "actions": [{"action": "stop_movement", "parameters": {}}]}]
        methods = exporter._generate_event_methods("obj_player", events)
        assert "def on_keyboard_up(self, key, scancode):" in methods

    def test_release_survives_dict_expansion_end_to_end(self, tmp_path):
        """Full export: a keyboard_release event reaches the generated object."""
        project = {
            "name": "RelGame",
            "assets": {
                "objects": {
                    "obj_player": {
                        "events": {
                            "keyboard_release": {
                                "left": {"actions": [
                                    {"action": "stop_movement", "parameters": {}}]}
                            }
                        }
                    }
                },
                "rooms": {},
                "sprites": {},
            },
        }
        out = tmp_path / "out"
        exporter = KivyExporter(project, tmp_path, out)
        assert exporter.export() is True
        player = (out / "game" / "objects" / "obj_player.py").read_text(encoding="utf-8")
        assert "def on_keyboard_up" in player
        compile(player, "obj_player.py", "exec")


class TestDuplicateMethodMerge:  # M37
    def test_grid_keyboard_and_step_merge_on_update(self, exporter):
        events = [
            _kb("left", [_if_on_grid([_hspeed(-4)])]),
            {"event_type": "step", "actions": [
                {"action": "set_vspeed", "parameters": {"value": 1}}]},
        ]
        methods = exporter._generate_event_methods("obj_player", events)
        assert methods.count("def on_update(") == 1

    def test_keyboard_and_keyboard_press_merge_on_keyboard(self, exporter):
        events = [
            _kb("left", [_hspeed(-4)]),
            {"event_type": "keyboard_press", "key_name": "up",
             "actions": [{"action": "set_vspeed", "parameters": {"value": -8}}]},
        ]
        methods = exporter._generate_event_methods("obj_player", events)
        assert methods.count("def on_keyboard(") == 1

    def test_merged_methods_compile(self, exporter):
        events = [
            _kb("left", [_if_on_grid([_hspeed(-4)])]),
            {"event_type": "step", "actions": [
                {"action": "set_vspeed", "parameters": {"value": 1}}]},
        ]
        methods = exporter._generate_event_methods("obj_player", events)
        # Wrap in a class to compile the method block.
        src = "class _C:\n" + methods
        compile(src, "methods.py", "exec")
