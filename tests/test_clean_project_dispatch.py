"""core/ide_window.py's PyGameMakerIDE.clean_project — Tools -> Clean
Project, Tier 1 of docs/CLEAN_PROJECT_PLAN.md. Via the repo's established
unbound-call-on-a-stub pattern (see tests/test_trash_dialog.py's
TestShowTrashDialogDispatch).
"""
import os
os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

import sys
sys.path.insert(0, str(Path(__file__).parent.parent))
from conftest import skip_without_pyside6

pytestmark = skip_without_pyside6


def _ide_cls():
    from core.ide_window import PyGameMakerIDE
    return PyGameMakerIDE


def _age(path, seconds_old=120):
    import time
    t = time.time() - seconds_old
    os.utime(path, (t, t))


def test_no_project_shows_info_message():
    stub = MagicMock()
    stub.current_project_path = None
    stub.tr = lambda text: text

    with patch("core.ide_window.QMessageBox") as mock_box:
        _ide_cls().clean_project(stub)

    assert mock_box.information.called


def test_removes_orphan_tmp_files_and_reports_count(tmp_path):
    tmp_file = tmp_path / "project.json.tmp"
    tmp_file.write_text("{}")
    _age(tmp_file)

    stub = MagicMock()
    stub.current_project_path = str(tmp_path)
    stub.tr = lambda text: text

    with patch("core.ide_window.QMessageBox") as mock_box:
        _ide_cls().clean_project(stub)

    assert not tmp_file.exists()
    assert mock_box.information.called
    assert stub.update_status.called


def test_no_orphans_reports_nothing_to_clean(tmp_path):
    stub = MagicMock()
    stub.current_project_path = str(tmp_path)
    stub.tr = lambda text: text

    with patch("core.ide_window.QMessageBox") as mock_box:
        _ide_cls().clean_project(stub)

    assert mock_box.information.called
    assert not stub.update_status.called


def test_recent_tmp_file_is_not_swept(tmp_path):
    tmp_file = tmp_path / "project.json.tmp"
    tmp_file.write_text("{}")  # freshly written, not aged

    stub = MagicMock()
    stub.current_project_path = str(tmp_path)
    stub.tr = lambda text: text

    with patch("core.ide_window.QMessageBox"):
        _ide_cls().clean_project(stub)

    assert tmp_file.exists()
