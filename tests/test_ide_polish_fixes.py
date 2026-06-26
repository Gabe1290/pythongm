"""Regression tests for a batch of IDE-shell polish fixes (2026-06-26).

User-reported after the first ~10% of the manual test pass. All five live
in the IDE shell — none touch the runtime, save format, or event loop:

1. Bundled platformer samples displayed as "plateforme_N_refresh2" (the
   leftover working name was baked into samples/plateforme_N/project.json).
2. A "Close Project" File-menu action (return to the Welcome tab without
   quitting the IDE) was missing.
3. The toolbar "Test Game" icon should read as a green Run triangle, not
   the theme-tinted monochrome SP_MediaPlay.
4. The "Import Sound" toolbar icon (SP_MediaVolume) was near-invisible on
   the Windows dark theme — fixed by tinting it to a palette-contrasting
   colour.
5. In the Welcome tab's "More options" dropdown the "Import GameMaker
   .gmk" / "Import Open Roberta XML" items were greyed out: update_ui_state
   sweeps every descendant QAction (findChildren) and disables anything
   whose text contains "Import" while no project is loaded — which is
   exactly when the Welcome tab is shown. The dropdown actions are now
   marked exempt.

The Qt tests construct a real offscreen QApplication (not pytest-qt), so
they run on Python 3.11 too, following test_audit_ide_window_leaks.py.
"""

import os
os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

import json
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).parent.parent))

from conftest import skip_without_pyside6

REPO_ROOT = Path(__file__).parent.parent


# --------------------------------------------------------------------------
# 1. Sample display names (no Qt needed)
# --------------------------------------------------------------------------

@pytest.mark.parametrize("sample", ["plateforme_1", "plateforme_2", "plateforme_3"])
def test_sample_name_has_no_working_suffix(sample):
    data = json.loads((REPO_ROOT / "samples" / sample / "project.json").read_text(encoding="utf-8"))
    assert data["name"] == sample, (
        f"{sample}/project.json name should be the clean '{sample}', not a "
        f"leftover working name; got {data['name']!r}"
    )


# Everything below needs PySide6.
pytestmark = skip_without_pyside6


@pytest.fixture(scope="module")
def _qapp():
    from PySide6.QtWidgets import QApplication
    app = QApplication.instance() or QApplication([])
    yield app


# --------------------------------------------------------------------------
# 5. Welcome-tab dropdown actions are exempt from the update_ui_state sweep
# --------------------------------------------------------------------------

def test_welcome_dropdown_actions_marked_always_enabled(_qapp):
    from widgets.welcome_tab import WelcomeTab

    class _Stub:
        def tr(self, s):
            return s

    btn = WelcomeTab._dropdown_button(
        _Stub(),
        "More options",
        [("Open ZIP", lambda: None),
         ("Import GameMaker .gmk...", lambda: None),
         ("Import Open Roberta XML...", lambda: None)],
    )
    menu = btn.menu()
    assert menu is not None
    actions = menu.actions()
    assert len(actions) == 3
    for action in actions:
        assert action.property("pygm_always_enabled") is True


def test_update_ui_state_keeps_exempt_actions_enabled(_qapp):
    from PySide6.QtGui import QAction
    from core.ide_window import PyGameMakerIDE

    from PySide6.QtWidgets import QLabel

    exempt = QAction("Import GameMaker .gmk...")
    exempt.setProperty("pygm_always_enabled", True)
    plain = QAction("Import Sprite...")  # matches the "Import" substring rule

    class _Stub:
        current_project_path = None  # no project open -> would grey "Import"

        def __init__(self):
            self.project_label = QLabel()

        def tr(self, s):
            return s

        def findChildren(self, _cls):
            return [exempt, plain]

    PyGameMakerIDE.update_ui_state(_Stub())

    assert exempt.isEnabled(), "Welcome dropdown import action must stay enabled with no project"
    assert not plain.isEnabled(), "ordinary Import action should be disabled with no project"


# --------------------------------------------------------------------------
# 3 + 4. Toolbar icon helpers
# --------------------------------------------------------------------------

def test_green_play_icon_is_green(_qapp):
    from core.ide_window import _green_play_icon

    icon = _green_play_icon()
    assert not icon.isNull()
    img = icon.pixmap(16, 16).toImage()
    # Scan the triangle body for a clearly-green, opaque pixel.
    found_green = False
    for x in range(16):
        for y in range(16):
            c = img.pixelColor(x, y)
            if c.alpha() > 200 and c.green() > 120 and c.green() > c.red() + 40 and c.green() > c.blue() + 40:
                found_green = True
                break
        if found_green:
            break
    assert found_green, "the Test Game play icon should contain green pixels"


def test_contrasting_icon_color_picks_light_on_dark(_qapp):
    from PySide6.QtGui import QPalette, QColor
    from core.ide_window import _contrasting_icon_color

    dark = QPalette()
    dark.setColor(QPalette.ColorRole.Button, QColor(30, 30, 30))
    light = QPalette()
    light.setColor(QPalette.ColorRole.Button, QColor(240, 240, 240))

    dark_fg = _contrasting_icon_color(dark)
    light_fg = _contrasting_icon_color(light)
    # Light foreground on a dark button, dark foreground on a light button.
    assert dark_fg.red() > 180 and dark_fg.green() > 180 and dark_fg.blue() > 180
    assert light_fg.red() < 100 and light_fg.green() < 100 and light_fg.blue() < 100


def test_tinted_standard_icon_recolors_to_target(_qapp):
    from PySide6.QtGui import QColor
    from core.ide_window import _tinted_standard_icon

    style = _qapp.style()
    target = QColor(235, 235, 235)
    icon = _tinted_standard_icon(style, "SP_MediaVolume", target)
    # The standard pixmap exists on every Qt style; if Qt ever returns a
    # null icon the helper returns None and the toolbar falls back gracefully.
    if icon is None:
        pytest.skip("SP_MediaVolume unavailable on this Qt style")
    assert not icon.isNull()
    img = icon.pixmap(16, 16).toImage()
    # Every opaque pixel should now be (close to) the tint colour.
    for x in range(16):
        for y in range(16):
            c = img.pixelColor(x, y)
            if c.alpha() > 200:
                assert abs(c.red() - 235) < 20 and abs(c.green() - 235) < 20 and abs(c.blue() - 235) < 20
                return
    pytest.skip("tinted icon had no opaque pixels to verify")


# --------------------------------------------------------------------------
# 2. Close Project
# --------------------------------------------------------------------------

def _close_project_stub(_qapp):
    from PySide6.QtWidgets import QTabWidget, QWidget

    class _PM:
        def __init__(self):
            self.dirty = False
            self.closed = False

        def is_dirty(self):
            return self.dirty

        def close_project(self):
            self.closed = True
            return True

    class _AssetTree:
        def __init__(self):
            self.cleared = False

        def clear_assets(self):
            self.cleared = True

    class _Props:
        def __init__(self):
            self.loaded = None

        def set_project_loaded(self, v):
            self.loaded = v

    class _Welcome(QWidget):
        def __init__(self):
            super().__init__()
            self.refreshed = False

        def refresh_recent_projects(self):
            self.refreshed = True

    class _Stub:
        def __init__(self):
            self.current_project_path = "/some/project"
            self.current_project_data = {"name": "X"}
            self.game_runner = object()
            self.project_manager = _PM()
            self.asset_tree = _AssetTree()
            self.properties_panel = _Props()
            self.editor_tabs = QTabWidget()
            self.welcome_tab = _Welcome()
            self.detached_editor_windows = {}
            self.open_editors = {"sprites:foo": QWidget()}
            self.stopped = False
            self.flushed = False
            self.status = None
            # Pretend an editor tab is open alongside the welcome tab.
            self.editor_tabs.addTab(QWidget(), "Editor")

        def tr(self, s):
            return s

        def stop_game(self):
            self.stopped = True

        def _flush_open_editors(self):
            self.flushed = True

        def _destroy_detached_editor(self, name):
            self.detached_editor_windows.pop(name, None)

        def save_project(self):
            return True

        def _add_welcome_tab(self):
            self.editor_tabs.addTab(self.welcome_tab, "Welcome")

        def update_window_title(self):
            pass

        def update_ui_state(self):
            pass

        def update_status(self, msg):
            self.status = msg

    return _Stub()


def test_close_project_no_project_is_noop(_qapp):
    from core.ide_window import PyGameMakerIDE

    stub = _close_project_stub(_qapp)
    stub.current_project_path = None
    result = PyGameMakerIDE.close_project(stub)
    assert result is False
    assert stub.project_manager.closed is False


def test_close_project_clean_tears_down_and_shows_welcome(_qapp):
    from core.ide_window import PyGameMakerIDE

    stub = _close_project_stub(_qapp)
    result = PyGameMakerIDE.close_project(stub)

    assert result is True
    assert stub.current_project_path is None
    assert stub.current_project_data is None
    assert stub.game_runner is None
    assert stub.stopped is True
    assert stub.project_manager.closed is True
    assert stub.asset_tree.cleared is True
    assert stub.properties_panel.loaded is False
    assert stub.open_editors == {}
    # Only the Welcome tab remains, and it was re-added.
    assert stub.editor_tabs.count() == 1
    assert stub.editor_tabs.widget(0) is stub.welcome_tab
    assert stub.welcome_tab.refreshed is True


def test_close_project_cancel_at_save_prompt_aborts(_qapp, monkeypatch):
    import core.ide_window as ide_mod
    from core.ide_window import PyGameMakerIDE
    from PySide6.QtWidgets import QMessageBox

    stub = _close_project_stub(_qapp)
    stub.project_manager.dirty = True
    monkeypatch.setattr(
        ide_mod.QMessageBox, "question",
        staticmethod(lambda *a, **k: QMessageBox.Cancel),
    )

    result = PyGameMakerIDE.close_project(stub)
    assert result is False
    # Nothing torn down on cancel.
    assert stub.current_project_path == "/some/project"
    assert stub.project_manager.closed is False
    assert stub.stopped is False
