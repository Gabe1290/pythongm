"""Regression tests for Blockly workspace XML caching (audit M16).

docs/FULL_AUDIT_2026-06-11.md: get_workspace_xml registered a
QWebEnginePage.runJavaScript result callback and immediately returned
result['xml'] — still the initial '' because the callback fires on a later
event-loop turn. So ObjectEditor.get_data never stored 'blockly_workspace'
and the workspace layout was discarded on every save. It now returns a
value cached from the on-change / on-load refreshes.
"""

import pytest

from conftest import skip_without_pyside6

pytestmark = skip_without_pyside6

# QtWebEngine may be absent in headless CI; skip the whole module if the
# widget can't even be imported.
pytest.importorskip("PySide6.QtWebEngineWidgets")


def _widget():
    from editors.object_editor.blockly_widget import BlocklyWidget
    w = BlocklyWidget.__new__(BlocklyWidget)
    w._last_xml = ""
    w._page_ready = True
    return w


class _FakePage:
    def __init__(self, xml_to_return):
        self.calls = []
        self._xml = xml_to_return

    def runJavaScript(self, script, callback=None):
        self.calls.append(script)
        if callback is not None:
            callback(self._xml)  # simulate the async result arriving


class _FakeView:
    def __init__(self, page):
        self._page = page

    def page(self):
        return self._page


class TestGetWorkspaceXmlReturnsCache:
    def test_returns_cached_value_not_empty(self, qapp):
        w = _widget()
        w._last_xml = "<xml>saved-layout</xml>"
        w.web_view = _FakeView(_FakePage("<xml>fresh</xml>"))
        # Returns the cached layout (pre-fix this was always '')
        assert w.get_workspace_xml() == "<xml>saved-layout</xml>"

    def test_get_kicks_a_refresh(self, qapp):
        w = _widget()
        w._last_xml = "<xml>old</xml>"
        page = _FakePage("<xml>new</xml>")
        w.web_view = _FakeView(page)
        w.get_workspace_xml()
        assert page.calls == ["window.blocklyApi.getXml()"]
        # the refresh stored the fresh value for next time
        assert w._last_xml == "<xml>new</xml>"

    def test_refresh_ignores_empty_result(self, qapp):
        w = _widget()
        w._last_xml = "<xml>keep</xml>"
        w.web_view = _FakeView(_FakePage(""))  # JS returns empty
        w._refresh_cached_xml()
        assert w._last_xml == "<xml>keep</xml>"  # not clobbered to ''

    def test_refresh_noop_when_page_not_ready(self, qapp):
        w = _widget()
        w._page_ready = False
        page = _FakePage("<xml>x</xml>")
        w.web_view = _FakeView(page)
        w._refresh_cached_xml()
        assert page.calls == []  # nothing fetched before the page is ready
