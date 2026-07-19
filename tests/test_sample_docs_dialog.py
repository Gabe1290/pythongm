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
    # Welcome tab once its export parity was complete.
    assert "Raycast — Level 1" in labels
    # A bogus entry that does not exist on disk is filtered out.
    dlg2 = _dialog(_qapp, samples=[("samples/does_not_exist", "Ghost")])
    assert dlg2.sample_labels() == []


def test_renders_selected_readme(_qapp):
    dlg = _dialog(_qapp)
    assert dlg.select_sample("samples/views_1")
    text = dlg.rendered_text()
    # The README's H1 and a distinctive phrase survive markdown rendering.
    assert "Views — Level 1" in text
    assert "camera" in text.lower()


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
