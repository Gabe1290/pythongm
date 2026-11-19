"""Standard dialog buttons (Save/Discard/Cancel...) must be translated.

Regression: qtbase_fr lacked them via the wrong path, qtbase_sl does not exist,
pt/zh need pt_BR/zh_CN, and main.py never installed Qt's translator at startup.
"""
import os
import pytest

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")
from PySide6.QtWidgets import QApplication, QMessageBox

BUTTONS = (QMessageBox.Save, QMessageBox.Discard, QMessageBox.Cancel,
           QMessageBox.Yes, QMessageBox.No)


def _texts():
    box = QMessageBox()
    box.setStandardButtons(QMessageBox.Save | QMessageBox.Discard | QMessageBox.Cancel
                           | QMessageBox.Yes | QMessageBox.No)
    return [box.button(b).text().replace("&", "") for b in BUTTONS]


@pytest.mark.parametrize("lang", ["fr", "de", "es", "it", "ru", "sl", "uk", "pt", "ja", "zh"])
def test_standard_buttons_translated(lang):
    app = QApplication.instance() or QApplication([])
    from core.language_manager import get_language_manager
    mgr = get_language_manager()
    mgr.install_qt_standard_translators(app, lang)
    try:
        assert not set(_texts()) & {"Save", "Discard", "Cancel"}
    finally:
        app.removeTranslator(mgr.qt_translator)
        app.removeTranslator(mgr.qt_fallback_translator)


def test_french_has_accents():
    app = QApplication.instance() or QApplication([])
    from core.language_manager import get_language_manager
    mgr = get_language_manager()
    mgr.install_qt_standard_translators(app, "fr")
    try:
        assert _texts()[0] == "Enregistrer"
    finally:
        app.removeTranslator(mgr.qt_translator)
        app.removeTranslator(mgr.qt_fallback_translator)
