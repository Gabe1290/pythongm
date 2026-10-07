"""
"Open Project..." picks a FOLDER, not project.json.

Classroom report (2026-10-07): students didn't understand that they had to
find and select project.json inside the project. Open Project now takes a
folder: the folder itself if it is a project, otherwise the projects
directly inside it (one level down, e.g. a USB stick holding several
projects); several are offered in a list.
"""

from pathlib import Path
from unittest.mock import MagicMock, patch

import sys
sys.path.insert(0, str(Path(__file__).parent.parent))

from core.project_manager import find_projects_in_folder

TRANS_DIR = Path(__file__).resolve().parent.parent / "translations"


def _project(folder: Path) -> Path:
    folder.mkdir(parents=True, exist_ok=True)
    (folder / "project.json").write_text("{}")
    return folder


# --- the pure search -------------------------------------------------------

def test_project_folder_itself(tmp_path):
    p = _project(tmp_path / "Mon jeu")
    (p / "sprites").mkdir()
    assert find_projects_in_folder(p) == [p]


def test_projects_one_level_down_sorted(tmp_path):
    b = _project(tmp_path / "plateforme")
    a = _project(tmp_path / "Labyrinthe")
    (tmp_path / "devoirs").mkdir()
    (tmp_path / "notes.txt").write_text("x")
    assert find_projects_in_folder(tmp_path) == [a, b]


def test_only_one_level_down(tmp_path):
    _project(tmp_path / "classe" / "eleve" / "Mon jeu")
    assert find_projects_in_folder(tmp_path) == []


def test_hidden_folders_and_stray_files_ignored(tmp_path):
    _project(tmp_path / ".Trash-1000")
    (tmp_path / "project.json.bak").write_text("{}")
    (tmp_path / "fake").mkdir()
    (tmp_path / "fake" / "project.json").mkdir()   # a folder, not a file
    assert find_projects_in_folder(tmp_path) == []


def test_missing_folder(tmp_path):
    assert find_projects_in_folder(tmp_path / "gone") == []


# --- the IDE handler -------------------------------------------------------

def _run_open(chosen, pick=None):
    from core.ide._project_actions import ProjectActionsMixin

    ide = MagicMock()
    ide.tr = lambda s: s
    with patch("core.ide._project_actions.QFileDialog.getExistingDirectory",
               return_value=str(chosen) if chosen else ""), \
         patch("core.ide._project_actions.QMessageBox") as box, \
         patch("PySide6.QtWidgets.QInputDialog.getItem",
               return_value=(pick, pick is not None)) as get_item:
        ProjectActionsMixin.open_project(ide)
    return ide, box, get_item


def test_choosing_the_project_folder_opens_it(tmp_path):
    p = _project(tmp_path / "Mon jeu")
    ide, box, get_item = _run_open(p)
    ide.load_project.assert_called_once_with(p)
    get_item.assert_not_called()


def test_choosing_the_stick_with_one_project_opens_it(tmp_path):
    p = _project(tmp_path / "Mon jeu")
    ide, _, get_item = _run_open(tmp_path)
    ide.load_project.assert_called_once_with(p)
    get_item.assert_not_called()


def test_several_projects_offer_a_list(tmp_path):
    _project(tmp_path / "Labyrinthe")
    p = _project(tmp_path / "Plateforme")
    ide, _, get_item = _run_open(tmp_path, pick="Plateforme")
    assert get_item.call_args[0][3] == ["Labyrinthe", "Plateforme"]
    ide.load_project.assert_called_once_with(p)


def test_cancelling_the_list_opens_nothing(tmp_path):
    _project(tmp_path / "Labyrinthe")
    _project(tmp_path / "Plateforme")
    ide, _, _ = _run_open(tmp_path, pick=None)
    ide.load_project.assert_not_called()


def test_no_project_found_explains(tmp_path):
    (tmp_path / "devoirs").mkdir()
    ide, box, _ = _run_open(tmp_path)
    ide.load_project.assert_not_called()
    box.information.assert_called_once()
    assert str(tmp_path) in box.information.call_args[0][2]


def test_cancelled_folder_dialog_does_nothing():
    ide, box, _ = _run_open(None)
    ide.load_project.assert_not_called()
    box.information.assert_not_called()


# --- the new strings are translated everywhere -----------------------------

_SPLIT_LANGS = {"de", "it", "ru", "sl", "uk"}
_ALL_LANGS = ["de", "es", "fr", "it", "pt", "ru", "sl", "uk", "ja", "zh", "pl"]
_SOURCES = [
    "No Project Found",
    "No project was found in:\n{0}\n\nChoose your project's folder, "
    "or the folder that contains it.",
    "Choose a Project",
    "Several projects were found in:\n{0}\n\nWhich one do you want to open?",
]


def test_open_project_strings_resolve_in_every_language():
    from PySide6.QtCore import QCoreApplication, QTranslator
    from PySide6.QtWidgets import QApplication

    app = QApplication.instance() or QApplication([])
    for lang in _ALL_LANGS:
        name = f"pygm2_{lang}_core.qm" if lang in _SPLIT_LANGS else f"pygm2_{lang}.qm"
        translator = QTranslator()
        assert translator.load(str(TRANS_DIR / name)), f"{lang}: .qm failed to load"
        app.installTranslator(translator)
        try:
            for source in _SOURCES:
                resolved = QCoreApplication.translate("PyGameMakerIDE", source)
                assert resolved and resolved != source, f"{lang}: {source!r} untranslated"
                if "{0}" in source:
                    assert "{0}" in resolved, f"{lang}: placeholder lost"
        finally:
            app.removeTranslator(translator)
