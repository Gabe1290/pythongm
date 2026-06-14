"""Regression tests for L4 (playground window WA_DeleteOnClose) and
L7 (zip temp extraction cleanup)."""

import os
os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")
os.environ.setdefault("SDL_VIDEODRIVER", "dummy")

from pathlib import Path
import sys
from unittest.mock import MagicMock, patch

import pytest

sys.path.insert(0, str(Path(__file__).parent.parent))
from conftest import skip_without_pyside6

pytestmark = skip_without_pyside6


@pytest.fixture(scope="module")
def _qapp():
    from PySide6.QtWidgets import QApplication
    app = QApplication.instance() or QApplication([])
    yield app


def test_thymio_playground_window_delete_on_close(_qapp):  # L4
    from PySide6.QtCore import Qt
    from widgets.thymio_playground import ThymioPlaygroundWindow
    win = ThymioPlaygroundWindow()
    win.timer.stop()
    assert win.testAttribute(Qt.WA_DeleteOnClose) is True
    win.deleteLater()


def test_playground_runner_window_delete_on_close(_qapp):  # L4
    from PySide6.QtCore import Qt
    from runtime.playground_runner import PlaygroundRunnerWindow
    win = PlaygroundRunnerWindow({"width": 400, "height": 400, "walls": [],
                                  "robots": []}, {})
    if getattr(win, "timer", None) is not None:
        win.timer.stop()
    assert win.testAttribute(Qt.WA_DeleteOnClose) is True
    win.deleteLater()


def test_reset_zip_state_removes_temp_dir(_qapp, tmp_path):  # L7
    with patch('PySide6.QtCore.QTimer'):
        from core.project_manager import ProjectManager
        pm = ProjectManager(asset_manager=MagicMock())
        pm.auto_save_timer = MagicMock()

    temp_dir = tmp_path / "pygamemaker_extract"
    temp_dir.mkdir()
    (temp_dir / "project.json").write_text("{}", encoding="utf-8")
    pm._temp_extraction_dir = str(temp_dir)

    pm._reset_zip_state()

    assert not temp_dir.exists()
    assert pm._temp_extraction_dir is None
