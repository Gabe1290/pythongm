"""No dead translations: a vanished entry for text the code still uses.

`lrelease` drops a message marked `type="vanished"`, so a real, human-written
translation carrying that mark never reaches the app -- the string shows in
English. Measured 2026-11-21 (TODO.md, Translations / i18n): 202 such strings
in each of de / it / ru / sl / uk (Sprite Editor, the conditional-action
editor, the Thymio windows...), plus 17 in the action configure dialog
(fixed in 3b17da9d). They were revived one screen (Qt context) per commit
(REVIVED_CONTEXTS records which); the guard now covers EVERY context the
code uses, in all ten shipped languages, so a new one cannot slip in.

For every context and every shipped language, two checks:
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

SHIPPED = ("de", "es", "fr", "it", "ja", "pt", "ru", "sl", "uk", "zh")
REVIVED_CONTEXTS = (
    "MessageTranslationsDialog",
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


def _files(lang):
    """The catalogues the app loads: the split set if present, else the single file."""
    split = sorted((ROOT / "translations").glob(f"pygm2_{lang}_*.ts"))
    return split or [ROOT / "translations" / f"pygm2_{lang}.ts"]


def _all_contexts():
    """Every Qt context the code uses that a shipped catalogue also has."""
    in_code = {c for c, _ in _code_pairs()}
    in_ts = set()
    for lang in SHIPPED:
        for ts in _files(lang):
            in_ts |= {c.findtext("name") for c in ET.parse(ts).getroot().findall("context")}
    return sorted(in_code & in_ts)


def _entries(lang, context):
    """[(source, translation text, vanished?)] for one context, all files."""
    out = []
    for ts in _files(lang):
        for ctx in ET.parse(ts).getroot().findall("context"):
            if ctx.findtext("name") != context:
                continue
            for msg in ctx.findall("message"):
                tr = msg.find("translation")
                out.append((msg.findtext("source") or "",
                            (tr.text or "") if tr is not None else "",
                            tr is not None and tr.get("type") == "vanished"))
    return out


def test_the_code_scan_finds_the_revived_contexts():
    contexts = set(_all_contexts())
    assert set(REVIVED_CONTEXTS) <= contexts, set(REVIVED_CONTEXTS) - contexts
    assert len(contexts) > 40


@pytest.mark.parametrize("lang", SHIPPED)
def test_no_used_string_is_left_vanished(lang):
    pairs = _code_pairs()
    dead = []
    for context in _all_contexts():
        entries = _entries(lang, context)
        live = {src for src, text, vanished in entries if not vanished and text.strip()}
        dead += sorted({(context, src[:40]) for src, text, vanished in entries
                        if vanished and text.strip() and (context, src) in pairs
                        and src not in live})
    assert not dead, (lang, dead[:10])


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


@pytest.mark.parametrize("lang", SHIPPED)
def test_used_strings_resolve_in_the_running_app(lang):
    from PySide6.QtCore import QCoreApplication
    from PySide6.QtWidgets import QApplication
    from core.language_manager import get_language_manager

    QApplication.instance() or QApplication([])
    get_language_manager().set_language(lang)
    pairs = _code_pairs()
    wrong = []
    for context in _all_contexts():
        texts = {}
        for src, text, vanished in _entries(lang, context):
            if not vanished and text.strip() and (context, src) in pairs:
                texts.setdefault(src, set()).add(text)
        for src, options in texts.items():
            if QCoreApplication.translate(context, src) not in options:
                wrong.append((context, src[:40]))
    assert not wrong, (lang, wrong[:10])
