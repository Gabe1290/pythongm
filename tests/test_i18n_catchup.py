"""Every shipped language translates what French translates.

docs/I18N_CATCHUP_2026-11-21.md: ten languages had fallen behind French
(238 strings each in de/it/ru/sl/uk, 112-119 in es/ja/pt/zh, 10 in pl), so
whole screens showed in English. ``scripts/i18n_catchup.py`` measures the gap
(strings the code passes to tr()/translate() that French translates and a
language does not) and applies translations. Done 2026-11-21: the gap is
zero in all ten languages, on every screen. This guard keeps it there, checks
through the real LanguageManager that the running app shows each translation,
and that no language shows FRENCH text instead of its own -- reviving vanished
entries in the dead-translation fix had put ~60 French strings into ru and sl
(the old vanished copies held French), plus 5 older ones in es.

CAUGHT_UP records the 32 screens the catch-up filled (docs/I18N_CATCHUP_2026-11-21.md).
"""
import importlib.util
import os
import sys
from pathlib import Path

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

import pytest

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from conftest import skip_without_pyside6  # noqa: E402

_spec = importlib.util.spec_from_file_location("i18n_catchup", ROOT / "scripts" / "i18n_catchup.py")
cu = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(cu)

CAUGHT_UP = (
    "PlaygroundEditor",
    "OrphanedFilesDialog",
    "TrashDialog",
    "UnusedAssetsDialog",
    "TilePaletteDialog",
    "TileGridWidget",
    "RoomEditor",
    "BlockWorldEditorWindow",
    "FindReplaceDialog",
    "PlaygroundElementProperties",
    "PlaygroundColorManager",
    "PlaygroundToolPalette",
    "PlaygroundRunnerWindow",
    "BaseBlockConfigDialog",
    "SpriteEditor",
    "FrameTimeline",
    "FloatableEditorMixin",
    "ForegroundBackgroundSwatch",
    "ColorPaletteWidget",
    "ColorSwatch",
    "ConditionalActionEditor",
    "ActionConfigDialog",
    "BackgroundEditor",
    "SoundEditor",
    "AssetTreeWidget",
    "FontEditor",
    "GM80ActionDialog",
    "EnhancedPropertiesPanel",
    "ObjectEditor",
    "ObjectPropertiesPanel",
    "ThymioDiagramWidget",
    "PyGameMakerIDE",
)

_CACHE = {}


def _state():
    if not _CACHE:
        used = cu.code_usage()
        fr = cu.live("fr")
        _CACHE["want"] = {k: v for k, v in fr.items() if k in used}
        _CACHE["live"] = {lang: cu.live(lang) for lang in cu.LANGS}
    return _CACHE["want"], _CACHE["live"]


def test_the_caught_up_screens_are_used_by_the_code():
    want, _ = _state()
    contexts = {c for c, _ in want}
    assert set(CAUGHT_UP) <= contexts, set(CAUGHT_UP) - contexts


@pytest.mark.parametrize("lang", cu.LANGS)
def test_no_language_lags_behind_french(lang):
    """Every string the code uses that French translates, on any screen."""
    want, live = _state()
    missing = sorted((c, s[:40]) for c, s in want if (c, s) not in live[lang])
    assert not missing, (lang, missing[:10])


# The same word in French and in that language (checked by hand, 2026-11-21).
SAME_AS_FRENCH = {
    ("de", "SpriteEditor", "Picker"),       # Pipette
    ("it", "SpriteEditor", "Origin"),       # Origine
    ("pt", "AssetTreeWidget", "Sounds"),    # Sons
}


@pytest.mark.parametrize("lang", cu.LANGS)
def test_no_language_shows_french_instead_of_its_own(lang):
    want, live = _state()
    leaked = sorted((c, s[:30], v[:30]) for (c, s), v in live[lang].items()
                    if (c, s) in want and want[(c, s)] == v and v.strip() != s.strip()
                    and (lang, c, s) not in SAME_AS_FRENCH)
    assert not leaked, (lang, leaked[:10])


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


@skip_without_pyside6
@pytest.mark.parametrize("lang", cu.LANGS)
def test_the_running_app_shows_the_translation(lang):
    from PySide6.QtCore import QCoreApplication
    from PySide6.QtWidgets import QApplication
    from core.language_manager import get_language_manager

    want, live = _state()
    QApplication.instance() or QApplication([])
    get_language_manager().set_language(lang)
    wrong = [(c, s[:40]) for (c, s) in want
             if (c, s) in live[lang]
             and QCoreApplication.translate(c, s) == s != live[lang][(c, s)]]
    assert not wrong, (lang, wrong[:10])


def test_the_tool_flags_a_lost_placeholder(tmp_path, monkeypatch, capsys):
    """apply() refuses to pass silently when {0}-style placeholders vanish."""
    import json
    target = tmp_path / "pygm2_es.ts"
    target.write_text('<?xml version="1.0" encoding="utf-8"?>\n<!DOCTYPE TS>\n'
                      '<TS version="2.1" language="es">\n</TS>\n', encoding="utf-8")
    monkeypatch.setattr(cu, "TRANS", tmp_path)
    monkeypatch.setattr(cu, "LANGS", ("es",))
    monkeypatch.setattr(cu, "code_usage", lambda: {("Ctx", "Saved {0}"): "x.py"})
    batch = tmp_path / "b.json"
    batch.write_text(json.dumps({"Ctx": {"Saved {0}": {"es": "Guardado"}}}), encoding="utf-8")
    assert cu.apply(batch) is False
    assert "placeholder {0} lost" in capsys.readouterr().out


@skip_without_pyside6
@pytest.mark.parametrize("lang, verb", [("fr", "Vider"), ("pl", "Opróżnij")])
def test_the_empty_trash_button_is_a_verb(lang, verb):
    """OrphanedFilesDialog's "Empty" button empties the trash; French and
    Polish had the adjective ("Vide", "Puste")."""
    from PySide6.QtCore import QCoreApplication
    from PySide6.QtWidgets import QApplication
    from core.language_manager import get_language_manager
    QApplication.instance() or QApplication([])
    get_language_manager().set_language(lang)
    assert QCoreApplication.translate("OrphanedFilesDialog", "Empty") == verb
