"""
"Save Project As" into a non-empty folder saves into a project subfolder.

Classroom report (2026-10-07): the folder picker only lets you choose a
folder, and Save As wrote the project's files straight into it. Students
who chose the USB stick itself spread the project over the stick's root,
where a second project overwrote the first one's project.json and sprites/.
resolve_save_as_target now picks ``<chosen>/<project name>/`` for a
non-empty folder, and the IDE asks before replacing an existing project.
"""

from pathlib import Path
from unittest.mock import MagicMock, patch

import sys
sys.path.insert(0, str(Path(__file__).parent.parent))

from core.project_manager import resolve_save_as_target, _project_folder_name

REPO_ROOT = Path(__file__).resolve().parent.parent
TRANS_DIR = REPO_ROOT / "translations"


# --- the pure decision -----------------------------------------------------

def test_empty_folder_is_used_directly(tmp_path):
    assert resolve_save_as_target(tmp_path, "Mon jeu") == (tmp_path, False)


def test_missing_folder_is_used_directly(tmp_path):
    target = tmp_path / "new"
    assert resolve_save_as_target(target, "Mon jeu") == (target, False)


def test_stick_root_gets_a_project_subfolder(tmp_path):
    # A USB stick root usually holds other things (and System Volume
    # Information / .Trash-1000).
    (tmp_path / "devoirs.odt").write_text("x")
    assert resolve_save_as_target(tmp_path, "Mon jeu") == (tmp_path / "Mon jeu", False)


def test_second_project_on_same_stick_does_not_collide(tmp_path):
    (tmp_path / "Labyrinthe").mkdir()
    (tmp_path / "Labyrinthe" / "project.json").write_text("{}")
    target, replaces = resolve_save_as_target(tmp_path, "Plateforme")
    assert target == tmp_path / "Plateforme"
    assert replaces is False


def test_existing_same_named_project_needs_confirmation(tmp_path):
    (tmp_path / "Mon jeu").mkdir()
    (tmp_path / "Mon jeu" / "project.json").write_text("{}")
    assert resolve_save_as_target(tmp_path, "Mon jeu") == (tmp_path / "Mon jeu", True)


def test_choosing_a_project_folder_replaces_it_with_confirmation(tmp_path):
    (tmp_path / "project.json").write_text("{}")
    (tmp_path / "sprites").mkdir()
    assert resolve_save_as_target(tmp_path, "Autre") == (tmp_path, True)


def test_current_project_folder_never_asks(tmp_path):
    (tmp_path / "project.json").write_text("{}")
    assert resolve_save_as_target(tmp_path, "Mon jeu", tmp_path) == (tmp_path, False)


def test_resaving_to_own_subfolder_never_asks(tmp_path):
    stick = tmp_path / "STICK"
    sub = stick / "Mon jeu"
    sub.mkdir(parents=True)
    (sub / "project.json").write_text("{}")
    assert resolve_save_as_target(stick, "Mon jeu", sub) == (sub, False)


def test_folder_name_is_fat_safe():
    assert _project_folder_name('Jeu: "v2"?') == "Jeu_ _v2__"
    assert _project_folder_name("  ... ") == "project"
    assert _project_folder_name("Lancer de rayons — Niveau 2") == "Lancer de rayons — Niveau 2"


# --- the IDE handler -------------------------------------------------------

def _ide(current_path):
    from core.ide._project_actions import ProjectActionsMixin

    ide = MagicMock()
    ide.current_project_data = {"name": "Mon jeu"}
    ide.current_project_path = current_path
    ide.tr = lambda s: s
    ide.project_manager.save_project_as.return_value = True
    return ide, ProjectActionsMixin.save_project_as


def test_ide_saves_into_subfolder_of_non_empty_stick(tmp_path):
    stick = tmp_path / "STICK"
    stick.mkdir()
    (stick / "autre.txt").write_text("x")
    ide, save_as = _ide(tmp_path / "home" / "Mon jeu")
    with patch("core.ide._project_actions.QFileDialog.getExistingDirectory",
               return_value=str(stick)), \
         patch("core.ide._project_actions.QMessageBox") as box:
        assert save_as(ide) is True
    ide.project_manager.save_project_as.assert_called_once_with(stick / "Mon jeu")
    box.question.assert_not_called()


def test_ide_declined_replace_saves_nothing(tmp_path):
    stick = tmp_path / "STICK"
    (stick / "Mon jeu").mkdir(parents=True)
    (stick / "Mon jeu" / "project.json").write_text("{}")
    ide, save_as = _ide(tmp_path / "home" / "Mon jeu")
    with patch("core.ide._project_actions.QFileDialog.getExistingDirectory",
               return_value=str(stick)), \
         patch("core.ide._project_actions.QMessageBox") as box:
        box.question.return_value = box.No
        assert save_as(ide) is False
    box.question.assert_called_once()
    ide.project_manager.save_project_as.assert_not_called()


def test_ide_accepted_replace_saves_there(tmp_path):
    stick = tmp_path / "STICK"
    (stick / "Mon jeu").mkdir(parents=True)
    (stick / "Mon jeu" / "project.json").write_text("{}")
    ide, save_as = _ide(tmp_path / "home" / "Mon jeu")
    with patch("core.ide._project_actions.QFileDialog.getExistingDirectory",
               return_value=str(stick)), \
         patch("core.ide._project_actions.QMessageBox") as box:
        box.question.return_value = box.Yes
        assert save_as(ide) is True
    ide.project_manager.save_project_as.assert_called_once_with(stick / "Mon jeu")


# --- the new dialog strings are translated everywhere ----------------------

_SPLIT_LANGS = {"de", "it", "ru", "sl", "uk"}
_ALL_LANGS = ["de", "es", "fr", "it", "pt", "ru", "sl", "uk", "ja", "zh", "pl"]
_SOURCES = [
    "Replace Project?",
    "A project already exists in:\n{0}\n\nReplace it with this project?",
]


def _qm(lang):
    name = f"pygm2_{lang}_core.qm" if lang in _SPLIT_LANGS else f"pygm2_{lang}.qm"
    return TRANS_DIR / name


def test_replace_dialog_strings_resolve_in_every_language():
    from PySide6.QtCore import QCoreApplication, QTranslator
    from PySide6.QtWidgets import QApplication

    app = QApplication.instance() or QApplication([])
    for lang in _ALL_LANGS:
        translator = QTranslator()
        assert translator.load(str(_qm(lang))), f"{lang}: .qm failed to load"
        app.installTranslator(translator)
        try:
            for source in _SOURCES:
                resolved = QCoreApplication.translate("PyGameMakerIDE", source)
                assert resolved and resolved != source, f"{lang}: {source!r} untranslated"
                if "{0}" in source:
                    assert "{0}" in resolved, f"{lang}: placeholder lost"
        finally:
            app.removeTranslator(translator)
