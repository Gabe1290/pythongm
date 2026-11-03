"""The French Thymio sheets (docs/thymio_fiches/) name what the IDE really shows, and keep their accents."""
import os
import re
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT))
os.environ.setdefault("SDL_VIDEODRIVER", "dummy")

import pytest

DOCS = REPO_ROOT / "docs" / "thymio_fiches"
FICHES = [DOCS / f"fiche_{n}.fr.md" for n in range(1, 10)]


def _text(paths):
    return "\n".join(p.read_text(encoding="utf-8") for p in paths)


def test_the_set_is_complete_and_the_readme_links_the_corrige():
    for p in FICHES + [DOCS / "README.fr.md", DOCS / "corrige.fr.md"]:
        assert p.exists(), p
    assert "corrige.fr.md" in (DOCS / "README.fr.md").read_text(encoding="utf-8")
    for n, p in enumerate(FICHES, 1):
        first = p.read_text(encoding="utf-8").splitlines()[0]
        assert first.startswith(f"# Fiche {n} :"), (p.name, first)


def test_every_action_and_event_of_the_solutions_is_named_as_the_ide_shows_it():
    from tools.thymio_fiches_solutions import PROGRAMS
    from extensions.thymio.actions import THYMIO_ACTIONS
    from extensions.thymio.events import THYMIO_EVENT_TYPES
    text = _text(FICHES + [DOCS / "corrige.fr.md"])
    missing = set()
    for prog in PROGRAMS.values():
        for event, actions in prog["events"].items():
            if event != "create" and THYMIO_EVENT_TYPES[event].display_name not in text:
                missing.add(THYMIO_EVENT_TYPES[event].display_name)
            for a in actions:
                if a["action"] in THYMIO_ACTIONS and THYMIO_ACTIONS[a["action"]].display_name not in text:
                    missing.add(THYMIO_ACTIONS[a["action"]].display_name)
    assert not missing, missing


def test_french_keeps_its_accents():
    text = _text(FICHES + [DOCS / "README.fr.md", DOCS / "corrige.fr.md"])
    for stripped in ("Duree", "Activites", "arene", "Decouvrir", "Evenement", "Evenement", "capteurs de proximite",
                     "Defi ", "Defis", "ecran", "etape "):
        assert stripped not in text, stripped
    assert text.count("é") > 100 and "è" in text and "ê" in text and "à" in text
    assert "�" not in text and "Ã©" not in text            # no mojibake


def test_every_sheet_names_the_sample_it_needs_and_the_sample_exists():
    for p in FICHES[:8]:
        m = re.search(r"\*\*Exemples? à ouvrir :\*\* (.+?)  ·", p.read_text(encoding="utf-8"))
        assert m, p.name
    for key in ("arène libre", "les murs", "le sol et le ruban"):
        assert key in (DOCS / "README.fr.md").read_text(encoding="utf-8")


def test_the_sheets_do_not_promise_features_the_simulator_lacks():
    text = _text(FICHES).lower()
    for banned in ("microphone", "accéléromètre", "mode préprogrammé"):
        assert banned not in text, banned
