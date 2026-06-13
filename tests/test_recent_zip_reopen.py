"""Regression test for reopening zip projects from Recent (audit M7).

docs/FULL_AUDIT_2026-06-11.md: open_project's zip branch recorded the .zip
path in Recent Projects, but reopening via Recent -> open_recent_project
-> load_project routed straight to project_manager.load_project, which
only handles folders (it computes <zip>/project.json, finds nothing, and
returns False). Every zip-based project was therefore a permanently dead
Recent entry. load_project now detects .zip paths and routes them through
load_project_from_zip.
"""

from pathlib import Path
from types import SimpleNamespace
from unittest.mock import MagicMock, patch

import pytest

from conftest import skip_without_pyside6

pytestmark = skip_without_pyside6


def _ide_cls():
    from core.ide_window import PyGameMakerIDE
    return PyGameMakerIDE


def _stub():
    recents = []
    return SimpleNamespace(
        _is_samples_path=lambda p: False,
        project_manager=MagicMock(),
        asset_tree=SimpleNamespace(project_manager=None),
        add_to_recent_projects=lambda p: recents.append(p),
        current_project_path=None,  # fresh IDE: no pre-switch editor flush
        _flush_open_editors=lambda: None,
        tr=lambda s: s,
        _recents=recents,
    )


class TestRecentZipReopen:
    def test_zip_path_routes_to_zip_loader(self, tmp_path):
        zip_path = tmp_path / "student.zip"
        zip_path.write_bytes(b"PK\x03\x04stub")
        stub = _stub()
        stub.project_manager.load_project_from_zip.return_value = True

        with patch('core.ide_window.Config'), \
             patch('core.ide_window.QMessageBox'), \
             patch('utils.project_compression.ProjectCompressor') as PC:
            PC.is_project_zip.return_value = True
            _ide_cls().load_project(stub, zip_path)

        stub.project_manager.load_project_from_zip.assert_called_once_with(zip_path)
        stub.project_manager.load_project.assert_not_called()  # NOT the folder loader
        assert str(zip_path) in stub._recents

    def test_invalid_zip_warns_and_does_not_load(self, tmp_path):
        zip_path = tmp_path / "notaproject.zip"
        zip_path.write_bytes(b"PK\x03\x04stub")
        stub = _stub()

        with patch('core.ide_window.Config'), \
             patch('core.ide_window.QMessageBox') as MB, \
             patch('utils.project_compression.ProjectCompressor') as PC:
            PC.is_project_zip.return_value = False
            _ide_cls().load_project(stub, zip_path)

        stub.project_manager.load_project_from_zip.assert_not_called()
        stub.project_manager.load_project.assert_not_called()
        MB.warning.assert_called_once()

    def test_folder_path_still_uses_folder_loader(self, tmp_path):
        folder = tmp_path / "myproject"
        folder.mkdir()
        stub = _stub()
        stub.project_manager.load_project.return_value = True

        with patch('core.ide_window.Config'), \
             patch('core.ide_window.QMessageBox'):
            _ide_cls().load_project(stub, folder)

        stub.project_manager.load_project.assert_called_once_with(folder)
        stub.project_manager.load_project_from_zip.assert_not_called()
