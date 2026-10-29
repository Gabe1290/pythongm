"""The Network (LAN multiplayer) wiki page exists in all nine languages and stays in step.

Same idea as tests/test_wiki_microbit_pages.py: same shape as the English page,
code identifiers kept verbatim, action names and the category taken from each
language's own generated action reference (so the page and the reference cannot
disagree), the real port numbers, links that resolve, no mojibake.
"""
import re
from pathlib import Path

import pytest

WIKI = Path(__file__).resolve().parent.parent / "wiki"
LANGS = ["fr", "de", "es", "it", "pt", "ru", "sl", "uk"]
ALL = [None] + LANGS
ACTION_IDS = ["host_game", "join_game", "leave_game", "start_networked_game", "set_shared_var",
              "get_shared_var", "send_network_message", "network_spawn", "sync_instance",
              "set_instance_owner", "is_instance_owner", "bind_network_input", "remote_input",
              "set_sync_rate"]
EVENTS = ["Network Ready", "Player Joined", "Player Left", "Network Message",
          "Network Game Started", "Connection Lost"]
LETTERS = re.compile("[À-ÖØ-öø-ſЀ-ӿ]")   # without × and ÷
MIN_LETTERS = {"fr": 150, "de": 40, "es": 80, "it": 20, "pt": 80, "ru": 1000, "sl": 20, "uk": 1000}


def _read(name):
    return (WIKI / name).read_text(encoding="utf-8")


def _page(lang):
    return _read("Network.md" if lang is None else f"Network_{lang}.md")


def _reference(lang):
    return _read("Full-Action-Reference-Network-Actions.md" if lang is None
                 else f"Full-Action-Reference-Network-Actions_{lang}.md")


NL = chr(10)


def _names_and_category(lang):
    text = _reference(lang)
    row = r'\| \*\*[^|]*\*\*\ \| '   # | **label** |  (prefix of every row)
    names = {m.group(2): m.group(1) for m in re.finditer(
        r'^### (.+)' + NL + NL + r'\|[^' + NL + r']*' + NL + r'\|[^' + NL + r']*' + NL + row + r'`([a-z_]+)` \|', text, re.M)}
    # each action's table is: Name row, Symbol row, Category row -- the third value is the category
    block = re.search(row + r'`host_game` \|' + NL + row + r'[^|]*\|' + NL + row + r'([^|' + NL + r']+) \|', text)
    return names, block.group(1).strip() if block else None


def _shape(text):
    return {"headings": len(re.findall(r"^#{1,3} ", text, re.M)),
            "table_rows": len(re.findall(r"^\|", text, re.M)),
            "bullets": len(re.findall(r"^- ", text, re.M)),
            "rules": text.count("\n---\n")}


def _identifiers(text):
    """Code tokens, not prose: globals, snake_case names, ports, ``"auto"``, assignments."""
    found = set(re.findall(r"`([^`]+)`", text))
    keep = set()
    for token in found:
        token = re.sub(r"<[^>]+>", "<x>", token)          # global.<name> is translated
        if (re.search(r"[_.<=]|\d", token) or token == '"auto"') and not re.search(r"[^\x00-\x7f]", token):
            keep.add(token)
    return keep


@pytest.mark.parametrize("lang", LANGS)
def test_same_shape_as_the_english_page(lang):
    assert _shape(_page(lang)) == _shape(_page(None))


@pytest.mark.parametrize("lang", LANGS)
def test_every_code_identifier_is_kept(lang):
    missing = sorted(_identifiers(_page(None)) - _identifiers(_page(lang)))
    assert not missing, missing


@pytest.mark.parametrize("lang", LANGS)
def test_action_names_and_category_are_the_references(lang):
    names, category = _names_and_category(lang)
    text = _page(lang)
    for action in ACTION_IDS:
        assert action in names, f"{action} missing from the {lang} reference"
        assert f"| **{names[action]}** |" in text, f"{lang}: no table row for {names[action]!r}"
    # the category names both the actions and the events section
    assert category and text.count(f"**{category}**") >= 2, f"{lang}: category {category!r}"


@pytest.mark.parametrize("lang", ALL)
def test_the_ports_and_the_six_events(lang):
    from extensions.multiplayer_lan.state import DEFAULT_PORT, DISCOVERY_PORT
    assert (DEFAULT_PORT, DISCOVERY_PORT) == (45782, 45783)
    text = _page(lang)
    assert "45782" in text and "45783" in text
    for event in EVENTS:
        # French translates the event names and keeps the English one in italics
        assert f"**{event}**" in text or f"*({event})*" in text, event


@pytest.mark.parametrize("lang", LANGS)
def test_links_resolve_and_point_at_the_same_language(lang):
    links = re.findall(r"\]\(([^)#\s]+)\)", _page(lang))
    assert links
    for target in links:
        assert (WIKI / f"{target}.md").exists(), target
        # FileExchange has no translation yet (queue item A3): the English page is linked, and says so.
        assert target.endswith(f"_{lang}") or target == "FileExchange", target


@pytest.mark.parametrize("lang", LANGS)
def test_no_mojibake_and_real_letters(lang):
    text = _page(lang)
    assert "�" not in text
    assert not re.search("[ÃÂÐÑ][\u0080-¿]", text)
    assert "\r" not in text
    assert len(LETTERS.findall(text)) >= MIN_LETTERS[lang]


def test_the_english_page_still_says_what_the_translations_say():
    """The two sample names and the fallback rule are the page's checkable claims."""
    text = _page(None)
    for sample in ("reseau_1", "reseau_3"):
        assert sample in text
        assert (WIKI.parent / "samples" / sample / "project.json").exists()
    assert "single-player" in text
