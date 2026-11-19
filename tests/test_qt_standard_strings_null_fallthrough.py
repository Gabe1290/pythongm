"""The Qt-standard-strings fallback must not swallow every other string.

2026-11-19 regression: QtStandardStringsTranslator.translate returned "" for a
string it did not own. In PySide6 that is a non-null empty QString, which Qt
reads as "translated to nothing" -- and because this translator is installed
last it is asked first, so every menu, button and label of the IDE (any
non-English language) rendered blank. It must return a null string so Qt asks
the next translator. Hand-rolled offscreen QApplication (no qapp fixture).
"""
import os

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

from PySide6.QtCore import QCoreApplication, QTranslator
from PySide6.QtWidgets import QApplication

from core.qt_standard_strings import QtStandardStringsTranslator


def _app():
    return QApplication.instance() or QApplication([])


def test_unowned_strings_fall_through_to_the_next_translator():
    app = _app()
    fallback = QtStandardStringsTranslator("fr")
    app.installTranslator(fallback)
    try:
        # Not a Qt context, and a Qt context with an unknown source: both must
        # reach the source text (no other translator installed here).
        assert QCoreApplication.translate("PyGameMakerIDE", "&File") == "&File"
        assert QCoreApplication.translate("QMessageBox", "Not a standard string") == "Not a standard string"
        # Its own strings still resolve.
        assert QCoreApplication.translate("QMessageBox", "Cancel") == "Annuler"
    finally:
        app.removeTranslator(fallback)


def test_the_real_startup_translators_leave_the_menus_readable():
    from core.language_manager import get_language_manager
    app = _app()
    mgr = get_language_manager()
    installed = []
    for f in mgr._get_translation_files("fr"):
        t = QTranslator()
        if t.load(str(f)):
            app.installTranslator(t)
            installed.append(t)
    mgr.install_qt_standard_translators(app, "fr")
    try:
        assert QCoreApplication.translate("PyGameMakerIDE", "&File") == "&Fichier"
    finally:
        app.removeTranslator(mgr.qt_fallback_translator)
        for t in installed:
            app.removeTranslator(t)
