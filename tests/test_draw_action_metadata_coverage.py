"""Regression test: UI-metadata coverage for GMK-imported draw actions.

maze_4's HUD uses draw_score / draw_text / draw_lives with GM's `relative`
checkbox and (for draw_lives) GM's `image` sprite-argument name. The runtime
honours both (draw_score/text/lives call `_is_relative`; draw_lives reads
`sprite` or `image`), but the events-panel metadata (events/action_types.py)
exposed neither — so opening one of these actions in the panel and clicking OK
silently DROPPED the relative flag / the life-icon sprite (same class as audit
M11/M60 "editing an action corrupts it").

This pins that `relative` (draw_score/text/lives) and the `image`→`sprite` alias
(draw_lives) now round-trip through ActionConfigDialog. set_draw_font's registry
(halign/valign) is already correct; its GM `align` int is an importer/runtime
concern tracked separately, not a metadata gap.
"""

import os
os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

from pathlib import Path
import sys

import pytest

sys.path.insert(0, str(Path(__file__).parent.parent))

from conftest import skip_without_pyside6

pytestmark = skip_without_pyside6


@pytest.fixture(scope="module")
def _qapp():
    from PySide6.QtWidgets import QApplication
    app = QApplication.instance() or QApplication([])
    yield app


def _parent_with_sprites(names):
    from PySide6.QtWidgets import QWidget
    w = QWidget()
    w.current_project_data = {"assets": {"sprites": {n: {} for n in names}}}
    return w


def _dialog(action_key, initial_params, sprites=None):
    from events.action_editor import ActionConfigDialog
    from events.action_types import ACTION_TYPES
    parent = _parent_with_sprites(sprites or [])
    dlg = ActionConfigDialog(ACTION_TYPES[action_key], initial_params, parent)
    dlg._keepalive_parent = parent
    return dlg


# --- the params are registered ------------------------------------------

@pytest.mark.parametrize("action", ["draw_score", "draw_text", "draw_lives"])
def test_relative_param_registered(action):
    from events.action_types import ACTION_TYPES
    names = {p.name for p in ACTION_TYPES[action].parameters}
    assert "relative" in names


def test_draw_lives_sprite_aliases_image():
    from events.action_types import ACTION_TYPES
    sprite_p = next(p for p in ACTION_TYPES["draw_lives"].parameters
                    if p.name == "sprite")
    assert "image" in sprite_p.aliases


# --- round-trip (editing must not drop data) -----------------------------

def test_draw_score_relative_round_trips(_qapp):
    dlg = _dialog("draw_score", {"x": 10, "y": 20, "caption": "Score: ",
                                 "relative": True})
    assert dlg.get_parameter_values()["relative"] is True


def test_draw_text_relative_round_trips(_qapp):
    dlg = _dialog("draw_text", {"text": "hi", "x": 0, "y": 0, "relative": True})
    assert dlg.get_parameter_values()["relative"] is True


def test_draw_lives_image_alias_and_relative_round_trip(_qapp):
    # maze_4-style saved params: GM's `image` name + `relative` flag.
    dlg = _dialog("draw_lives",
                  {"x": 8, "y": 8, "image": "spr_heart", "relative": True},
                  sprites=["spr_heart", "spr_coin"])
    out = dlg.get_parameter_values()
    # `image` migrates to the canonical `sprite` (runtime reads either).
    assert out["sprite"] == "spr_heart"
    assert out["relative"] is True


def test_draw_lives_without_relative_defaults_false(_qapp):
    dlg = _dialog("draw_lives", {"x": 0, "y": 0, "sprite": "spr_heart"},
                  sprites=["spr_heart"])
    assert dlg.get_parameter_values()["relative"] is False
