"""Every language whose Blockly workspace is translated has complete tables (docs/OPEN_WORK_2026-11-22.md
U3-U8).

For each language in BLOCKLY_WORKSPACE_LANGUAGES, blockly_i18n.js must hold a full BLOCK_MESSAGES,
KEY_NAMES, CATEGORY_MESSAGES, BLOCKLY_MSG_TRANSLATIONS and THYMIO_BLOCK_MESSAGES block (same keys as
French), the file must still evaluate in a real JS engine, and a language's text must not be a copy of
the French. Generated blocks follow the same list (config/blockly_generated_block_i18n.py).
"""
import os
import re
import sys
from pathlib import Path

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

import pytest

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
JS = ROOT / "editors" / "object_editor" / "blockly" / "blockly_i18n.js"
TABLES = ("BLOCK_MESSAGES", "KEY_NAMES", "CATEGORY_MESSAGES", "BLOCKLY_MSG_TRANSLATIONS", "THYMIO_BLOCK_MESSAGES")

from config.blockly_generated_block_i18n import BLOCKLY_WORKSPACE_LANGUAGES  # noqa: E402


def _block(src, table, lang):
    start = src.index(f"const {table} = {{")
    m = re.compile(r"\n    '" + lang + r"': \{").search(src, start)
    end_table = src.index("\n};", start)
    if not m or m.start() > end_table:
        return None
    i = m.end()
    depth = 1
    while depth:
        c = src[i]
        if c in "'\"":
            q = c
            i += 1
            while src[i] != q:
                i += 2 if src[i] == "\\" else 1
        depth += {"{": 1, "}": -1}.get(c, 0)
        i += 1
    return src[m.end():i - 1]


def _entries(block):
    return dict(re.findall(r"^\s*'((?:\\.|[^'])+)'\s*:\s*'((?:\\.|[^'])*)'", block, re.M))


@pytest.mark.parametrize("lang", [x for x in BLOCKLY_WORKSPACE_LANGUAGES if x != "fr"])
def test_every_table_is_complete(lang):
    src = JS.read_text(encoding="utf-8")
    for table in TABLES:
        fr, other = _block(src, table, "fr"), _block(src, table, lang)
        assert other is not None, (table, lang)
        missing = set(_entries(fr)) - set(_entries(other))
        assert not missing, (table, lang, sorted(missing)[:10])


@pytest.mark.parametrize("lang", [x for x in BLOCKLY_WORKSPACE_LANGUAGES if x not in ("fr",)])
def test_no_french_copies(lang):
    src = JS.read_text(encoding="utf-8")
    fr, other = _entries(_block(src, "BLOCK_MESSAGES", "fr")), _entries(_block(src, "BLOCK_MESSAGES", lang))
    copies = [k for k, v in other.items() if len(v) > 4 and fr.get(k) == v and " " in v]
    assert not copies, copies[:10]


def test_the_file_evaluates_and_resolves():
    from PySide6.QtWidgets import QApplication
    from PySide6.QtQml import QJSEngine
    QApplication.instance() or QApplication([])
    src = JS.read_text(encoding="utf-8")
    for lang in BLOCKLY_WORKSPACE_LANGUAGES:
        eng = QJSEngine()
        r = eng.evaluate("var console={log:function(){},warn:function(){}};var Blockly={Msg:{}};"
                         f"var window={{location:{{search:'?lang={lang}'}}}};" + src +
                         f";getBlockMessage('event_create','{lang}')+'|'+getCategoryMessage('Events','{lang}')")
        assert not r.isError(), (lang, r.toString())
        create, events = r.toString().split("|")
        assert create and create != "null" and create != "When created", (lang, create)
        assert events and events != "Events", (lang, events)
