"""The in-app tutorials name actions and events as the IDE shows them (docs/CORE_NAMES_I18N_PLAN.md U8).

A lesson that uses the events panel must give the panel's names in its language, and a menu path
must be "<the action's own category> > <action>" as the Add Action menu shows it. A lesson that uses
Blockly (mock blocks on any of its pages) follows the Blockly workspace instead, which still shows
some blocks in English, so it is left to its own mock blocks. Also pins the restored German umlauts.
"""
import re
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

BLOCKLY = re.compile(r"blockly-group|block-event")
STRONG = re.compile(r"<strong>([^<]*)</strong>")
SEP = re.compile(r"\s*(?:&gt;|>)\s*")


def _panel_lessons(lang):
    lessons = []
    for folder in sorted((ROOT / "Tutorials" / lang).glob("[0-9]*")):
        pages = sorted(folder.glob("*.html"))
        if not any(BLOCKLY.search(p.read_text(encoding="utf-8")) for p in pages):
            lessons.append(folder)
    return lessons


@pytest.fixture(scope="module")
def registry():
    from events import plugin_loader
    real = plugin_loader.is_extension_enabled
    plugin_loader.is_extension_enabled = lambda folder, default=True: True
    try:
        plugin_loader.load_all_plugins()
        from events.action_types import ACTION_TYPES
        from events.event_types import EVENT_TYPES
        yield dict(ACTION_TYPES), dict(EVENT_TYPES)
    finally:
        plugin_loader.is_extension_enabled = real
        plugin_loader.load_all_plugins()


@pytest.mark.parametrize("lang", ["de", "es", "fr"])
def test_panel_lessons_use_the_ide_names(lang, registry):
    from config.ui_names import language_table
    actions, events = registry
    table = language_table(lang)
    english = {a.display_name for a in actions.values()} | {e.display_name for e in events.values()}
    by_name = {table["core.action"][k]: k for k in actions if k in table.get("core.action", {})}
    problems = []
    for folder in _panel_lessons(lang):
        for page in folder.glob("*.html"):
            for inner in STRONG.findall(page.read_text(encoding="utf-8")):
                parts = SEP.split(inner.strip())
                if parts[-1] in english and parts[-1] not in by_name:
                    problems.append((page.name, inner, "English name"))
                if len(parts) == 2 and parts[1] in by_name:
                    want = table["core.category"][actions[by_name[parts[1]]].category]
                    if parts[0] != want:
                        problems.append((page.name, inner, f"category should be {want}"))
    assert not problems, problems[:15]


def test_german_tutorials_keep_their_umlauts():
    stripped = re.compile(r"\b(hinzufuegen|Fuege|fuer|Muenzen|Waende|Schlaeger|pruefen|Waehle|Groesse|"
                          r"zerstoeren|koennen|muessen|ueber|Druecke|benoetigt)\b")
    bad = []
    for page in (ROOT / "Tutorials" / "de").glob("*/*.html"):
        text = re.sub(r"<(code|pre)[^>]*>.*?</\1>", "", page.read_text(encoding="utf-8"), flags=re.S)
        bad += [(page.name, m) for m in stripped.findall(text)]
    assert not bad, bad[:10]


def test_spanish_tutorials_keep_their_accents():
    stripped = re.compile(r"\b(Accion|accion|puntuacion|direccion|colision|codigo|pixeles|Tamano|pequeno)\b")
    bad = []
    for page in (ROOT / "Tutorials" / "es").glob("*/*.html"):
        text = re.sub(r"<(code|pre)[^>]*>.*?</\1>", "", page.read_text(encoding="utf-8"), flags=re.S)
        bad += [(page.name, m) for m in stripped.findall(text)]
    assert not bad, bad[:10]


# --- wiki pages (U8): hand-written pages only; the action reference, presets and the pages built from
# docs/handouts are generated and checked elsewhere.
GENERATED = re.compile(r"Full-Action-Reference|-Preset|Student-Handout|Worksheet-|Teacher-Guide|"
                       r"Teacher-Resources|Answer-Key")
# The visual-programming pages describe Blockly blocks, which follow the Blockly workspace (several of
# its generated blocks are still English there), not the events panel.
BLOCKLY_PAGES = re.compile(r"Visuelle_Programmierung|Programmation_Visuelle|Programacion_Visual|"
                           r"Programmazione_Visuale|Programacao_Visual|Vizualnoe_Programmirovanie|"
                           r"Vizualno_Programiranje|Vizualne_Prohramuvannya")
BOLD = re.compile(r"\*\*([^*\n]+)\*\*")
SPLIT_PATH = re.compile(r"\*\*([^*\n]+)\*\*\s*(?:→|&gt;|->)\s*\*\*([^*\n]+)\*\*")
WIKI_DONE = ["fr", "de"]


@pytest.mark.parametrize("lang", WIKI_DONE)
def test_wiki_pages_use_the_ide_names(lang, registry):
    from config.ui_names import language_table
    actions, events = registry
    table = language_table(lang)
    translated_actions = {actions[k].display_name for k in table.get("core.action", {}) if k in actions}
    translated_events = {events[k].display_name for k in table.get("core.event", {}) if k in events}
    english = (translated_actions | translated_events) - set(table["core.action"].values()) \
        - set(table["core.event"].values())
    by_name = {v: k for k, v in table["core.action"].items() if k in actions}
    problems = []
    for page in sorted((ROOT / "wiki").glob(f"*_{lang}.md")):
        if GENERATED.search(page.name) or BLOCKLY_PAGES.search(page.name):
            continue
        text = page.read_text(encoding="utf-8")
        for inner in BOLD.findall(text):
            last = SEP.split(inner.strip())[-1]
            if last in english:
                problems.append((page.name, inner))
        for cat, name in SPLIT_PATH.findall(text):
            if name in by_name and cat in table["core.category"].values():
                want = table["core.category"][actions[by_name[name]].category]
                if cat != want:
                    problems.append((page.name, f"{cat} -> {name}", f"want {want}"))
    assert not problems, problems[:15]
