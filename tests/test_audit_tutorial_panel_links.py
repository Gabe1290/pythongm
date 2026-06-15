"""Regression test for L35 — TutorialPanel external-link handling.

QTextBrowser defaults openLinks=True, which makes it auto-navigate
(setSource) to a clicked anchor. For an external http(s) URL that blanks the
tutorial page. TutorialPanel must disable openLinks so all navigation goes
through its own anchorClicked -> on_link_clicked slot, leaving the displayed
page intact.
"""
import pytest

from conftest import skip_without_pyside6

pytestmark = skip_without_pyside6


def _make_app():
    from PySide6.QtWidgets import QApplication
    return QApplication.instance() or QApplication([])


def test_content_browser_does_not_auto_navigate():
    _make_app()
    from widgets.tutorial_panel import TutorialPanel

    panel = TutorialPanel()
    # The browser must not auto-load clicked anchors as a new source.
    assert panel.content_browser.openLinks() is False
    # External links are still routed through our own slot, not the OS-open
    # shortcut, so QDesktopServices handles them once.
    assert panel.content_browser.openExternalLinks() is False


def test_external_click_keeps_page_content():
    _make_app()
    from PySide6.QtCore import QUrl
    from widgets.tutorial_panel import TutorialPanel

    panel = TutorialPanel()
    marker = "<h1>Tutorial Body</h1>"
    panel.content_browser.setHtml(marker)
    assert "Tutorial Body" in panel.content_browser.toPlainText()

    # Simulate the user clicking an external link. With openLinks disabled the
    # browser doesn't replace its document; on_link_clicked just opens the URL.
    panel.on_link_clicked(QUrl("https://example.com/"))

    # Page content survives the external click.
    assert "Tutorial Body" in panel.content_browser.toPlainText()
