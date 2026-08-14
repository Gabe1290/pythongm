"""IDEExporters._ask_offline_pyodide -- the UI prompt gating the offline
Pyodide bundle. Must not even ask when the project has no execute_code
(matches this repo's "don't show irrelevant options" convention, e.g. the
Views/Extensions tabs only appearing when relevant).
"""
import os
os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

import sys
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

sys.path.insert(0, str(Path(__file__).parent.parent))
from conftest import skip_without_pyside6

pytestmark = skip_without_pyside6


def _make_exporters(current_project_data):
    from core.ide_exporters import IDEExporters
    fake_ide = MagicMock()
    fake_ide.current_project_data = current_project_data
    fake_ide.tr = lambda s: s
    return IDEExporters(fake_ide)


_PYTHON_PROJECT = {
    "assets": {"objects": {"obj_a": {"events": {
        "create": {"actions": [{"action": "execute_code", "parameters": {"code": "pass"}}]}
    }}}}
}

_PLAIN_PROJECT = {
    "assets": {"objects": {"obj_a": {"events": {
        "create": {"actions": [{"action": "set_hspeed", "parameters": {"speed": 4}}]}
    }}}}
}


def test_no_prompt_when_project_has_no_python():
    exporters = _make_exporters(_PLAIN_PROJECT)
    with patch("core.ide_exporters.QMessageBox.question") as mock_question:
        result = exporters._ask_offline_pyodide()
    mock_question.assert_not_called()
    assert result is False


def test_no_prompt_when_no_project_loaded():
    exporters = _make_exporters(None)
    with patch("core.ide_exporters.QMessageBox.question") as mock_question:
        result = exporters._ask_offline_pyodide()
    mock_question.assert_not_called()
    assert result is False


def test_prompts_when_project_uses_python_and_returns_yes():
    from PySide6.QtWidgets import QMessageBox
    exporters = _make_exporters(_PYTHON_PROJECT)
    with patch("core.ide_exporters.QMessageBox.question", return_value=QMessageBox.Yes) as mock_question:
        result = exporters._ask_offline_pyodide()
    mock_question.assert_called_once()
    assert result is True


def test_prompts_when_project_uses_python_and_returns_no():
    from PySide6.QtWidgets import QMessageBox
    exporters = _make_exporters(_PYTHON_PROJECT)
    with patch("core.ide_exporters.QMessageBox.question", return_value=QMessageBox.No):
        result = exporters._ask_offline_pyodide()
    assert result is False


def test_default_button_is_no():
    """Defaulting to No means pressing Enter/Esc on the dialog doesn't
    silently commit a ~17 MB size increase the user didn't actively choose."""
    from PySide6.QtWidgets import QMessageBox
    exporters = _make_exporters(_PYTHON_PROJECT)
    with patch("core.ide_exporters.QMessageBox.question",
              return_value=QMessageBox.No) as mock_question:
        exporters._ask_offline_pyodide()
    # QMessageBox.question(parent, title, text, buttons, defaultButton) --
    # the last positional arg is the default button.
    assert mock_question.call_args.args[-1] == QMessageBox.No
