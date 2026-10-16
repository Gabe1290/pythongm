"""docs/KID_UI_SIMPLIFICATION_PLAN.md Phase 2: the "junior" edition hides
advanced menu/toolbar entries (keyed by slot name); every other edition keeps
the full menus. The QActions must still exist so update_ui_state() works.
"""
import os
os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).parent.parent))

from conftest import skip_without_pyside6

pytestmark = skip_without_pyside6


@pytest.fixture(scope="module")
def _qapp():
    from PySide6.QtWidgets import QApplication
    yield QApplication.instance() or QApplication([])


def _build_ide(edition):
    from utils.config import Config
    original = Config.get("edition", None)
    Config.set("edition", edition)
    try:
        from core.ide_window import PyGameMakerIDE
        return PyGameMakerIDE()
    finally:
        Config.set("edition", original)


def _menu_names(ide):
    names = set()
    for menu in ide._extension_menus.values():
        names.update(a.objectName() for a in menu.actions() if a.objectName())
    return names


def test_junior_hides_advanced_entries_keeps_core(_qapp):
    from config.editions import EDITIONS
    ide = _build_ide("junior")
    try:
        names = _menu_names(ide)
        hidden = EDITIONS["junior"]["hidden_menu_actions"]
        assert not (names & hidden)
        for keep in ("new_project", "open_project", "save_project", "test_game",
                     "export_game", "preferences", "create_object",
                     "create_room", "import_sprite", "show_trash_dialog"):
            assert keep in names, keep
        # hidden actions still exist as attributes
        assert ide.export_html5_action is not None
        from PySide6.QtWidgets import QToolBar
        toolbar = ide.findChild(QToolBar, "MainToolbar")
        assert ide.test_game_action in toolbar.actions()
        assert ide.debug_game_action not in toolbar.actions()
    finally:
        ide.deleteLater()


def test_junior_has_no_stray_separators(_qapp):
    ide = _build_ide("junior")
    try:
        for menu in ide._extension_menus.values():
            acts = menu.actions()
            if not acts:
                continue
            assert not acts[0].isSeparator() and not acts[-1].isSeparator()
            for a, b in zip(acts, acts[1:]):
                assert not (a.isSeparator() and b.isSeparator())
    finally:
        ide.deleteLater()


def test_beginner_keeps_full_menus(_qapp):
    from config.editions import EDITIONS
    ide = _build_ide("beginner")
    try:
        names = _menu_names(ide)
        for n in ("export_html5", "export_kivy", "debug_game", "find",
                  "create_script", "validate_project"):
            assert n in names, n
        assert "hidden_menu_actions" not in EDITIONS["beginner"]
    finally:
        ide.deleteLater()
