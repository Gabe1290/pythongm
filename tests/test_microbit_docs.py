"""The micro:bit extension's documentation (docs/MICROBIT_EXTENSION_PLAN.md, S12).

Docs rot silently, so the checkable claims are checked: every file in the
extension folder is in its README's file map, the wiki pages' links resolve,
the counts they state match the code, the generated action reference lists
every action, and the French keeps its accents.
"""
import os
import re
import sys
from pathlib import Path

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT))
EXT = REPO_ROOT / "extensions" / "microbit"
WIKI = REPO_ROOT / "wiki"

import pytest

from events.plugin_loader import load_all_plugins
from events.action_types import ACTION_TYPES
from events.event_types import EVENT_TYPES


def _read(path):
    return path.read_text(encoding="utf-8")


def _actions():
    load_all_plugins()
    return sorted(n for n, a in ACTION_TYPES.items() if a.category == "micro:bit")


def _events():
    load_all_plugins()
    return sorted(n for n in EVENT_TYPES if n.startswith("microbit_"))


# --- the extension README ---------------------------------------------------------------------

def test_readme_file_map_lists_every_file_in_the_folder():
    readme = _read(EXT / "README.md")
    for path in sorted(EXT.iterdir()):
        if path.suffix in (".py", ".json", ".md") and path.name != "THIRD_PARTY_LICENSES.md":
            assert f"`{path.name}`" in readme, f"{path.name} is not in the README's file map"


def test_readme_does_not_list_files_that_do_not_exist():
    readme = _read(EXT / "README.md")
    table = readme.split("## The files")[1].split("## How it hooks in")[0]
    named = set(re.findall(r"`([a-z_]+\.(?:py|json|md))`", table))
    assert named
    for name in named:
        assert (EXT / name).exists(), name


def test_readme_counts_match_the_code():
    readme = _read(EXT / "README.md")
    assert f"The {len(_actions())} action **schemas**" in readme
    assert f"The {len(_events())} `microbit_*` event types" in readme


def test_every_hook_the_readme_documents_is_really_declared():
    init = _read(EXT / "__init__.py")
    readme = _read(EXT / "README.md")
    for hook in ("PLUGIN_ACTIONS", "PLUGIN_EVENTS", "PLUGIN_INSTANCE_CREATED",
                 "PLUGIN_FRAME_UPDATES", "PLUGIN_INSTANCE_OVERLAYS",
                 "PLUGIN_INPUT_HANDLERS", "PLUGIN_GENERATED_BLOCK_TRANSLATIONS"):
        assert hook in readme, hook
        assert hook in init or hook == "PLUGIN_ACTIONS", hook


# --- the wiki -------------------------------------------------------------------------------------

PAGES = {"en": WIKI / "Microbit.md", "fr": WIKI / "Microbit_fr.md"}


@pytest.mark.parametrize("lang", sorted(PAGES))
def test_wiki_page_links_resolve(lang):
    text = _read(PAGES[lang])
    targets = set(re.findall(r"\]\(([A-Za-z0-9_\-]+)\)", text))
    assert targets
    for target in targets:
        assert (WIKI / f"{target}.md").exists(), f"{PAGES[lang].name} links to missing {target}"


@pytest.mark.parametrize("lang", sorted(PAGES))
def test_wiki_page_names_every_action_by_its_identifier(lang):
    text = _read(PAGES[lang])
    for name in _actions():
        assert f"`{name}`" in text, f"{PAGES[lang].name} does not document {name}"


@pytest.mark.parametrize("lang", sorted(PAGES))
def test_wiki_page_lists_every_event_family(lang):
    text = _read(PAGES[lang])
    for fragment in ("Button A Pressed", "Logo Touched", "Pin 0 / 1 / 2 Touched", "Shake",
                     "Loud Sound", "Display Finished", "Sound Finished",
                     "Radio Message Received"):
        assert fragment in text, fragment
    # and the event count the code really has is the one the extension page states
    assert len(_events()) == 24


def test_extension_and_home_pages_link_to_the_new_page_in_both_languages():
    for name, target in (("Home.md", "Microbit"), ("Extensions.md", "Microbit"),
                         ("Home_fr.md", "Microbit_fr"), ("Extensions_fr.md", "Microbit_fr")):
        assert f"]({target})" in _read(WIKI / name), name


def test_stated_action_count_matches_the_generated_reference():
    """Home's "N built-in actions" is the generated reference's own total."""
    index = _read(WIKI / "Full-Action-Reference.md")
    total = int(re.search(r"all \*\*(\d+)\*\* actions", index).group(1))
    assert f"**{total}** built-in actions" in _read(WIKI / "Home.md")
    assert f"**{total}** actions intégrées" in _read(WIKI / "Home_fr.md")


def test_generated_reference_lists_every_micro_bit_action_in_every_language():
    names = _actions()
    for suffix in ("", "_de", "_es", "_fr", "_it", "_pt", "_ru", "_sl", "_uk"):
        page = _read(WIKI / f"Full-Action-Reference-Microbit-Actions{suffix}.md")
        for name in names:
            assert name in page, (suffix, name)


def test_french_reference_translates_the_micro_bit_actions_with_accents():
    page = _read(WIKI / "Full-Action-Reference-Microbit-Actions_fr.md")
    for good in ("Afficher une image", "Faire défiler un texte", "Jouer une mélodie",
                 "Régler le groupe radio", "Arrêter le son", "Si luminosité de la LED"):
        assert good in page, good


_STRIPPED = ["Melodie", "melodie", "evenement", "Evenement", "Regler", "Arreter",
             "Eteindre", "ecran ", "Luminosite", "Duree", "Frequence", "defile ",
             "accentuee", "Parametres", "Reference Complete", "Referenc des", "a la vraie",
             "carte entiere", "Selectionn"]


def test_french_wiki_text_carries_its_accents():
    text = _read(WIKI / "Microbit_fr.md") + _read(EXT / "translations.py")
    text += _read(REPO_ROOT / "samples" / "microbit_1" / "README.fr.md")
    for bad in _STRIPPED:
        assert bad not in text, bad
    page = _read(WIKI / "Microbit_fr.md")
    for good in ("événements", "Paramètres du projet", "Référence Complète des Actions",
                 "mélodie", "Régler le groupe radio", "À l'écran"):
        assert good in page, good
