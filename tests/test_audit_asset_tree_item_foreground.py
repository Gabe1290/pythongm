#!/usr/bin/env python3
"""Regression test for L33: asset tree items must not hardcode black
foreground (unreadable under dark themes). Imported assets should use the
application palette's Text color so they follow the active theme."""

import os

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

from conftest import skip_without_pyside6

pytestmark = skip_without_pyside6

from PySide6.QtWidgets import QApplication
from PySide6.QtGui import QColor, QPalette
from PySide6.QtCore import Qt

from widgets.asset_tree.asset_tree_item import AssetTreeItem


def _app():
    app = QApplication.instance()
    if app is None:
        app = QApplication([])
    return app


def test_imported_asset_follows_palette_text_color_dark_theme():
    app = _app()
    # Simulate a dark theme: light text on a dark window/base.
    pal = app.palette()
    pal.setColor(QPalette.Text, QColor("#e0e0e0"))
    pal.setColor(QPalette.WindowText, QColor("#e0e0e0"))
    pal.setColor(QPalette.Base, QColor("#1e1e1e"))
    app.setPalette(pal)
    try:
        item = AssetTreeItem(
            asset_type="sounds",
            asset_name="beep",
            asset_data={"imported": True},
        )
        fg = item.foreground(0).color()
        # Must NOT be the old hardcoded black.
        assert fg != QColor(Qt.GlobalColor.black)
        # Must track the palette's Text role (the light dark-theme color).
        assert fg == QColor("#e0e0e0")
    finally:
        app.setPalette(QApplication.style().standardPalette())


def test_not_imported_asset_stays_gray():
    app = _app()
    item = AssetTreeItem(
        asset_type="sounds",
        asset_name="missing",
        asset_data={"imported": False},
    )
    assert item.foreground(0).color() == QColor(Qt.GlobalColor.gray)
    assert "(not imported)" in item.text(0)
