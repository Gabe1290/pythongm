"""No dead translations: a vanished entry for text the code still uses.

`lrelease` drops a message marked `type="vanished"`, so a real, human-written
translation carrying that mark never reaches the app -- the string shows in
English. Measured 2026-11-21 (TODO.md, Translations / i18n): 202 such strings
in each of de / it / ru / sl / uk (Sprite Editor, the conditional-action
editor, the Thymio windows...), plus 17 in the action configure dialog
(fixed in 3b17da9d). They are revived one screen (Qt context) at a time;
FIXED_CONTEXTS lists the screens done so far.

For each fixed context and each split-catalogue language, two checks:
* no (context, string) the code still uses (a literal ``self.tr("...")`` in
  a class of that name) is left only as a vanished entry;
* every used string with a live translation resolves to it through the real
  LanguageManager, as the running app does.
"""
import ast
import os
import sys
import xml.etree.ElementTree as ET
from pathlib import Path

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

import pytest

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from conftest import skip_without_pyside6  # noqa: E402

pytestmark = skip_without_pyside6

SPLIT_LANGS = ("de", "it", "ru", "sl", "uk")
FIXED_CONTEXTS = (
    "ResizeCanvasDialog",
    "ThymioConfigDialog",
    "ThymioEventSelector",
    "MultiActionEditor",
    "ThymioActionSelector",
    "ThymioEventsPanel",
    "ThymioPlaygroundWindow",
    "ConditionalActionEditor",
    "SpriteEditor",
    "ActionConfigDialog",
)

_PAIRS = None


def _code_pairs():
    """(class name, literal string) for every self.tr("...") in the code."""
    global _PAIRS
    if _PAIRS is None:
        pairs = set()
        for f in ROOT.rglob("*.py"):
            rel = f.relative_to(ROOT).parts
            if any(p in rel for p in ("venv", "tests", ".git", "build", "dist")):
                continue
            try:
                tree = ast.parse(f.read_text(encoding="utf-8"))
            except Exception:
                continue
            for cls in [n for n in ast.walk(tree) if isinstance(n, ast.ClassDef)]:
                for c in ast.walk(cls):
                    if (isinstance(c, ast.Call) and isinstance(c.func, ast.Attribute)
                            and c.func.attr == "tr" and c.args
                            and isinstance(c.args[0], ast.Constant)
                            and isinstance(c.args[0].value, str)):
                        pairs.add((cls.name, c.args[0].value))
        _PAIRS = pairs
    return _PAIRS


def _entries(lang, context):
    """[(source, translation text, vanished?)] for one context, all files."""
    out = []
    for ts in sorted((ROOT / "translations").glob(f"pygm2_{lang}_*.ts")):
        for ctx in ET.parse(ts).getroot().findall("context"):
            if ctx.findtext("name") != context:
                continue
            for msg in ctx.findall("message"):
                tr = msg.find("translation")
                out.append((msg.findtext("source") or "",
                            (tr.text or "") if tr is not None else "",
                            tr is not None and tr.get("type") == "vanished"))
    return out


def test_the_code_scan_finds_the_fixed_contexts():
    contexts = {c for c, _ in _code_pairs()}
    assert set(FIXED_CONTEXTS) <= contexts, set(FIXED_CONTEXTS) - contexts


@pytest.mark.parametrize("context", FIXED_CONTEXTS)
@pytest.mark.parametrize("lang", SPLIT_LANGS)
def test_no_used_string_is_left_vanished(lang, context):
    used = {s for c, s in _code_pairs() if c == context}
    entries = _entries(lang, context)
    live = {src for src, text, vanished in entries if not vanished and text.strip()}
    dead = sorted({src for src, text, vanished in entries
                   if vanished and text.strip() and src in used and src not in live})
    assert not dead, (lang, context, [d[:40] for d in dead])


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


@pytest.mark.parametrize("lang", SPLIT_LANGS)
def test_used_strings_resolve_in_the_running_app(lang):
    from PySide6.QtCore import QCoreApplication
    from PySide6.QtWidgets import QApplication
    from core.language_manager import get_language_manager

    QApplication.instance() or QApplication([])
    get_language_manager().set_language(lang)
    pairs = _code_pairs()
    wrong = []
    for context in FIXED_CONTEXTS:
        texts = {}
        for src, text, vanished in _entries(lang, context):
            if not vanished and text.strip() and (context, src) in pairs:
                texts.setdefault(src, set()).add(text)
        for src, options in texts.items():
            if QCoreApplication.translate(context, src) not in options:
                wrong.append((context, src[:40]))
    assert not wrong, (lang, wrong[:10])
