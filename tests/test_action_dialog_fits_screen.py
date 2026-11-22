"""Every action's configure form fits on the screen (2026-11-22).

Some forms (Block World view, 2.5D view, Doom HUD, Set View) are 850-900 px
tall at the junior 13 pt font, taller than a 768 px school laptop, and the
dialog had no scrolling, so OK/Cancel could end up off-screen. The form now
scrolls inside the dialog with OK/Cancel kept outside it, and the dialog
opens at its content's size capped at 90% of the screen height.
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


@pytest.fixture(scope="module")
def dialogs():
    from PySide6.QtGui import QFont
    from PySide6.QtWidgets import QApplication
    app = QApplication.instance() or QApplication([])
    sheet, font = app.styleSheet(), QFont(app.font())
    from utils.theme_manager import ThemeManager
    ThemeManager.apply_theme("junior")
    f = QFont(app.font())
    f.setPointSize(13)
    app.setFont(f)
    from events.plugin_loader import load_all_plugins
    from events.action_types import ACTION_TYPES
    from events.action_editor import ActionConfigDialog
    load_all_plugins()

    def build(name):
        d = ActionConfigDialog(ACTION_TYPES[name])
        d.show()
        app.processEvents()
        return d
    yield app, build, sorted(ACTION_TYPES)
    app.setStyleSheet(sheet)
    app.setFont(font)


def test_every_form_fits_and_keeps_ok_visible(dialogs):
    from PySide6.QtWidgets import QDialogButtonBox
    app, build, names = dialogs
    bad = []
    for name in names:
        d = build(name)
        try:
            cap = d.screen().availableGeometry().height() * 0.9
            box = d.findChildren(QDialogButtonBox)[0]
            if d.height() > cap + 1 or box.geometry().bottom() > d.height() or not box.isVisibleTo(d):
                bad.append((name, d.height(), int(cap)))
        finally:
            d.close()
            d.deleteLater()
    app.processEvents()
    assert not bad, bad[:10]


def test_a_too_tall_form_scrolls_instead_of_being_cut(dialogs):
    app, build, _ = dialogs
    d = build("enable_block_world_view")
    try:
        cap = d.screen().availableGeometry().height() * 0.9
        assert d._form_body.sizeHint().height() > cap          # it really is taller than the screen allows
        bar = d._form_scroll.verticalScrollBar()
        assert bar.maximum() > 0                               # ...so the rest is reachable by scrolling
    finally:
        d.close()


def test_a_short_form_does_not_scroll(dialogs):
    app, build, _ = dialogs
    d = build("set_hspeed") if "set_hspeed" in dialogs[2] else build(dialogs[2][0])
    try:
        assert d._form_scroll.verticalScrollBar().maximum() == 0
    finally:
        d.close()
