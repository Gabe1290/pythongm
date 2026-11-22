"""Junior edition: dialogs a student reaches are not clipped at the 13 pt font (2026-11-22).

A screenshot pass of the junior edition (junior theme + 13 pt font, on a 1366x768
school-laptop screen) found text cut off in the dialogs a student uses most:
Create Sprite/Object/Room (fixed 400x150: title and button labels unreadable),
Rename (fixed 400x180), the If-condition editor (opened at 2/3 of the screen
height, crushing its Object/Count rows), the Show Message "Translations..." and
If Can Push "Configure..." buttons (capped at 120 px), the Preferences "Browse..."
button and the French Tutorials line. This builds them at junior settings and
checks every text widget gets at least the size its text needs.
"""
import os
import sys
from pathlib import Path

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

import pytest

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from conftest import skip_without_pyside6  # noqa: E402

pytestmark = skip_without_pyside6


@pytest.fixture
def junior(monkeypatch):
    """Junior theme + 13 pt font for the test, restored afterwards."""
    from PySide6.QtGui import QFont
    from PySide6.QtWidgets import QApplication
    app = QApplication.instance() or QApplication([])
    sheet, font = app.styleSheet(), QFont(app.font())
    from utils.theme_manager import ThemeManager
    ThemeManager.apply_theme("junior")
    f = QFont(app.font())
    f.setPointSize(13)
    app.setFont(f)
    yield app
    app.setStyleSheet(sheet)
    app.setFont(font)


def _clipped(dialog):
    from PySide6.QtWidgets import (QAbstractButton, QComboBox, QDoubleSpinBox, QLabel, QLineEdit, QSpinBox,
                                   QWidget)
    bad = []
    for w in dialog.findChildren(QWidget):
        if not w.isVisibleTo(dialog):
            continue
        if isinstance(w, QLabel):
            if w.wordWrap() or not w.text().strip():
                continue
            hint = w.sizeHint()
        elif isinstance(w, QAbstractButton):
            if not w.text().strip():
                continue
            hint = w.sizeHint()
        elif isinstance(w, (QComboBox, QSpinBox, QDoubleSpinBox)) or (
                isinstance(w, QLineEdit) and not isinstance(w.parent(), QComboBox)):
            hint = w.minimumSizeHint()
        else:
            continue
        if hint.width() - w.width() > 2 or hint.height() - w.height() > 2:
            bad.append((type(w).__name__, getattr(w, "text", lambda: "")()[:30], w.size().toTuple(), hint.toTuple()))
    return bad


def _show(app, dialog):
    dialog.show()
    app.processEvents()
    return dialog


@pytest.mark.parametrize("asset_type", ["sprite", "object", "room"])
def test_the_create_dialog_fits_its_text(junior, asset_type):
    from widgets.asset_tree.asset_dialogs import CreateAssetDialog
    d = _show(junior, CreateAssetDialog(asset_type))
    try:
        assert _clipped(d) == []
    finally:
        d.close()


def test_the_rename_dialog_fits_its_text(junior):
    from widgets.asset_tree.asset_dialogs import AssetRenameDialog
    d = _show(junior, AssetRenameDialog("spr_player", "sprites"))
    try:
        assert _clipped(d) == []
    finally:
        d.close()


def test_the_if_condition_editor_opens_tall_enough(junior):
    from events.conditional_editor import ConditionalActionEditor
    d = _show(junior, ConditionalActionEditor())
    try:
        avail = d.screen().availableGeometry().height()
        assert d.height() >= min(d.minimumSizeHint().height(), int(avail * 0.9)) - 2
        if d.minimumSizeHint().height() <= avail * 0.9:          # the screen has room: nothing may be crushed
            assert _clipped(d) == []
    finally:
        d.close()


def _action_dialog(name):
    from events.plugin_loader import load_all_plugins
    from events.action_types import ACTION_TYPES
    from events.action_editor import ActionConfigDialog
    load_all_plugins()
    return ActionConfigDialog(ACTION_TYPES[name])


@pytest.mark.parametrize("action, button", [("show_message", "Translations..."), ("if_can_push", "⚙️ Configure...")])
def test_action_dialog_buttons_are_not_capped(junior, action, button):
    from PySide6.QtWidgets import QPushButton
    d = _show(junior, _action_dialog(action))
    try:
        btn = next(b for b in d.findChildren(QPushButton) if b.text() == button)
        assert btn.width() >= btn.sizeHint().width() - 2, (btn.width(), btn.sizeHint().width())
    finally:
        d.close()


def test_the_preferences_browse_button_fits(junior):
    from dialogs.preferences_dialog import PreferencesDialog
    d = _show(junior, PreferencesDialog())
    try:
        btn = d.projects_dir_btn
        tabs = d.findChildren(__import__("PySide6.QtWidgets", fromlist=["QTabWidget"]).QTabWidget)[0]
        for i in range(tabs.count()):
            tabs.setCurrentIndex(i)
            junior.processEvents()
            if btn.isVisibleTo(d):
                break
        assert btn.width() >= btn.sizeHint().width() - 2, (btn.width(), btn.sizeHint().width())
    finally:
        d.close()


def test_the_french_tutorials_dialog_fits_its_text(junior):
    from core.language_manager import get_language_manager
    from widgets.tutorial_dialog import TutorialDialog
    get_language_manager().set_language("fr")
    try:
        d = _show(junior, TutorialDialog())
        try:
            assert _clipped(d) == []
        finally:
            d.close()
    finally:
        get_language_manager().set_language("en")
