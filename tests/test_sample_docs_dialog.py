"""Welcome tab — the "Sample guides" documentation viewer.

Bundled samples collapse into one "Choose a sample" dropdown, so there's no
per-card surface for a docs button; SampleDocsDialog is the per-sample docs
entry point instead (sample list + rendered README). The README files ship
inside the frozen build (PyGameMaker.spec bundles the samples/ tree) and resolve
via the same repo_root the dropdown uses, so the viewer works from source and
from a compiled executable alike.

Constructs a real offscreen QApplication rather than using pytest-qt, so it runs
anywhere PySide6 is installed (mirrors tests/test_room_canvas_cache_clear.py).
"""

import os
os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).parent.parent))

from conftest import skip_without_pyside6

pytestmark = skip_without_pyside6

REPO_ROOT = Path(__file__).resolve().parent.parent


@pytest.fixture(scope="module")
def _qapp():
    from PySide6.QtWidgets import QApplication
    app = QApplication.instance() or QApplication([])
    yield app


def _dialog(_qapp, samples=None):
    from widgets.welcome_tab import SampleDocsDialog, SAMPLE_PROJECTS
    return SampleDocsDialog(samples if samples is not None else SAMPLE_PROJECTS,
                            REPO_ROOT)


def test_lists_only_existing_samples(_qapp):
    dlg = _dialog(_qapp)
    labels = dlg.sample_labels()
    # views_1 was added this cycle; it and the maze family must be present.
    assert "Views — Level 1" in labels
    assert "Maze — Level 1" in labels
    # raycast_1 (the Doom-style first-person sample) was surfaced in the
    # Welcome tab once its export parity was complete; raycast_2 is its Level 2.
    assert "Raycast — Level 1" in labels
    assert "Raycast — Level 2" in labels
    # A bogus entry that does not exist on disk is filtered out.
    dlg2 = _dialog(_qapp, samples=[("samples/does_not_exist", "Ghost")])
    assert dlg2.sample_labels() == []


def test_guide_follows_the_ide_language_with_english_fallback(_qapp, tmp_path, monkeypatch):
    """Guides are translated per language as README.<lang>.md next to the
    English README.md. The dialog must pick the IDE language's guide when it
    exists and fall back to English when it doesn't, so a partial rollout of
    translations is safe."""
    from widgets.welcome_tab import SampleDocsDialog
    sample = tmp_path / "samples" / "demo"
    sample.mkdir(parents=True)
    (sample / "README.md").write_text("# English guide", encoding="utf-8")
    (sample / "README.fr.md").write_text("# Guide en français", encoding="utf-8")

    dlg = SampleDocsDialog([("samples/demo", "Demo")], tmp_path)

    monkeypatch.setattr(SampleDocsDialog, "_guide_language", staticmethod(lambda: "fr"))
    assert dlg.guide_path("samples/demo").name == "README.fr.md"

    # a language with no translation yet -> English
    monkeypatch.setattr(SampleDocsDialog, "_guide_language", staticmethod(lambda: "de"))
    assert dlg.guide_path("samples/demo").name == "README.md"

    # English itself -> the base file
    monkeypatch.setattr(SampleDocsDialog, "_guide_language", staticmethod(lambda: "en"))
    assert dlg.guide_path("samples/demo").name == "README.md"


def test_guide_language_reads_the_language_manager_singleton(_qapp):
    """_guide_language must go through get_language_manager() — calling the
    instance method on the class would silently always yield 'en'."""
    from widgets.welcome_tab import SampleDocsDialog
    lang = SampleDocsDialog._guide_language()
    assert isinstance(lang, str) and lang and lang == lang.lower()
    assert "_" not in lang          # normalised, e.g. 'fr' not 'fr_FR'


def test_renders_selected_readme(_qapp, monkeypatch):
    from widgets.welcome_tab import SampleDocsDialog
    # Pin English: every sample now ships a README.fr.md too, so on a
    # French-configured box guide_path() would (correctly) resolve that one
    # and the English assertions below would fail for the wrong reason.
    monkeypatch.setattr(SampleDocsDialog, "_guide_language", staticmethod(lambda: "en"))
    dlg = _dialog(_qapp)
    assert dlg.select_sample("samples/views_1")
    text = dlg.rendered_text()
    # The README's H1 and a distinctive phrase survive markdown rendering.
    assert "Views — Level 1" in text
    assert "camera" in text.lower()


def test_every_sample_ships_a_french_guide(_qapp, monkeypatch):
    """Every bundled sample has a README.fr.md, and guide_path picks it when
    the IDE language is French.

    Deliberately NOT an exact count — the per-sample loop below is what has to
    hold, and pinning a number just means bumping it each time a sample lands
    (raycast_3 took this from 15 to 16). The floor guards against the glob
    silently matching nothing.
    """
    from widgets.welcome_tab import SampleDocsDialog
    monkeypatch.setattr(SampleDocsDialog, "_guide_language", staticmethod(lambda: "fr"))
    dlg = _dialog(_qapp)
    roots = sorted(p for p in (dlg._repo_root / "samples").iterdir()
                   if (p / "README.md").is_file())
    assert len(roots) >= 15
    missing = [r.name for r in roots
               if dlg.guide_path(f"samples/{r.name}").name != "README.fr.md"]
    assert not missing, f"samples without a French guide: {missing}"


def test_first_sample_selected_by_default(_qapp):
    dlg = _dialog(_qapp)
    # Something is rendered without any interaction (row 0 auto-selected).
    assert dlg.rendered_text().strip() != ""


def test_missing_readme_shows_placeholder(_qapp, tmp_path):
    # A sample folder with a project.json but no README.md.
    sample = tmp_path / "samples" / "no_docs"
    sample.mkdir(parents=True)
    (sample / "project.json").write_text("{}", encoding="utf-8")
    from widgets.welcome_tab import SampleDocsDialog
    dlg = SampleDocsDialog([("samples/no_docs", "No Docs")], tmp_path)
    assert dlg.select_sample("samples/no_docs")
    assert "No documentation" in dlg.rendered_text()


def test_empty_build_shows_message(_qapp):
    dlg = _dialog(_qapp, samples=[])
    assert dlg.sample_labels() == []
    assert dlg.rendered_text().strip() != ""     # the "no samples" notice
