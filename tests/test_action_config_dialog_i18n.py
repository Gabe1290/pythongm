"""The action configure dialog's own text reads in every shipped language.

Found by the raycast follow-up F2 (rendering the dialog in German): 17 of the
dialog's own strings -- its title "Configure {0}", "Choose Color...", the room
navigation choices... -- were marked type="vanished" in the de/it/ru/sl/uk
catalogues. lrelease drops vanished entries, so those translations, though
present in the files, never reached the app: the dialog was half English in
five languages. A few others ("Applies to", "Self", "Other", "Object:",
"Number or expression", the C-style-operators warning) had no entry at all
in several languages.

Checked through the real LanguageManager, as the running app does, for every
literal self.tr() string in the ActionConfigDialog class.
"""
import ast
import os
import sys
from pathlib import Path

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

import pytest

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from conftest import skip_without_pyside6  # noqa: E402

pytestmark = skip_without_pyside6

SHIPPED = ("de", "es", "fr", "it", "ja", "pt", "ru", "sl", "uk", "zh")
# Text that is the same in every language.
NEUTRAL = {"🎨 {0}", "X: ", "Y: "}


def _dialog_strings():
    tree = ast.parse((ROOT / "events" / "action_editor.py").read_text(encoding="utf-8"))
    cls = next(n for n in tree.body
               if isinstance(n, ast.ClassDef) and n.name == "ActionConfigDialog")
    return sorted({c.args[0].value for c in ast.walk(cls)
                   if isinstance(c, ast.Call) and isinstance(c.func, ast.Attribute)
                   and c.func.attr == "tr" and c.args
                   and isinstance(c.args[0], ast.Constant)
                   and isinstance(c.args[0].value, str)})


@pytest.fixture(autouse=True)
def _back_to_english():
    yield
    try:
        from PySide6.QtWidgets import QApplication
        from core.language_manager import get_language_manager
        if QApplication.instance() is not None:
            get_language_manager().set_language("en")
    except Exception:
        pass


def test_the_dialog_has_strings_to_check():
    assert len(_dialog_strings()) >= 20


@pytest.mark.parametrize("lang", SHIPPED)
def test_every_dialog_string_resolves(lang):
    from PySide6.QtCore import QCoreApplication
    from PySide6.QtWidgets import QApplication
    from core.language_manager import get_language_manager

    QApplication.instance() or QApplication([])
    get_language_manager().set_language(lang)
    unresolved = [s[:40] for s in _dialog_strings()
                  if s not in NEUTRAL
                  and QCoreApplication.translate("ActionConfigDialog", s) == s]
    assert not unresolved, (lang, unresolved)


def test_no_used_dialog_string_is_left_vanished():
    """The specific trap: a translation that exists but is marked vanished."""
    import re
    from xml.sax.saxutils import unescape
    used = set(_dialog_strings())
    for ts in sorted((ROOT / "translations").glob("pygm2_*.ts")):
        text = ts.read_text(encoding="utf-8")
        m = re.search(r"<context>\s*<name>ActionConfigDialog</name>(.*?)</context>", text, re.S)
        if not m:
            continue
        for msg in re.findall(r"<message>(.*?)</message>", m.group(1), re.S):
            src = unescape(re.search(r"<source>(.*?)</source>", msg, re.S).group(1))
            assert not (src in used and 'type="vanished"' in msg), (ts.name, src[:40])
