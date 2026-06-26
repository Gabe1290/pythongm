"""Regression tests for the desktop/mobile export 'dependency missing'
messages (2026-06-26).

User context: students on locked-down school machines have no admin rights,
and the old message ("Please install it in your virtual environment: pip
install kivy") didn't tell them a per-user install needs no admin, nor that
the HTML5 export needs nothing installed at all. The message now:

- states no administrator rights are required,
- gives both the venv and the `pip install --user` commands,
- points at the zero-install Web (HTML5) export as an escape hatch,
- and notes that only the *building* machine needs the toolchain.

Single-sourced through export.base_exporter._missing_dependency_message so
the PyInstaller / Kivy / Pillow messages stay consistent.
"""

import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).parent.parent))

from conftest import skip_without_pyside6

pytestmark = skip_without_pyside6


def _msg(dependency="Kivy", pip_name="kivy", label="macOS exporter", **kw):
    from export.base_exporter import _missing_dependency_message
    return _missing_dependency_message(dependency, pip_name, label, **kw)


def test_message_states_no_admin_required():
    text = _msg().lower()
    assert "no" in text and "admin" in text  # "no admin" / "administrator"


def test_message_offers_user_install_command():
    assert "pip install --user kivy" in _msg()


def test_message_offers_venv_install_command():
    assert "pip install kivy" in _msg()


def test_message_points_at_html5_escape_hatch():
    assert "HTML5" in _msg()


def test_message_names_the_dependency_and_platform():
    text = _msg(dependency="PyInstaller", pip_name="pyinstaller", label="Linux exporter")
    assert "PyInstaller not found." in text
    assert "Linux exporter" in text
    assert "pip install --user pyinstaller" in text


def test_optional_note_is_included_when_given():
    text = _msg(dependency="Pillow (PIL)", pip_name="pillow",
                note="Pillow handles the game's image assets.")
    assert "Pillow handles the game's image assets." in text
    assert "pip install --user pillow" in text


def test_require_dependencies_emits_improved_message(qapp_or_skip):
    """The live check routes its failure text through the new helper."""
    from export.exe.exe_exporter import ExeExporter

    exporter = ExeExporter()
    # Force the very first check (PyInstaller) to fail so the message fires.
    exporter._check_pyinstaller = lambda: False

    captured = {}
    exporter.export_complete.connect(lambda ok, msg: captured.update(ok=ok, msg=msg))

    result = exporter._require_kivy_dependencies("Windows EXE exporter")

    assert result is False
    assert captured["ok"] is False
    assert "pip install --user pyinstaller" in captured["msg"]
    assert "HTML5" in captured["msg"]
    assert "administrator rights" in captured["msg"]


@pytest.fixture
def qapp_or_skip():
    from PySide6.QtWidgets import QApplication
    app = QApplication.instance() or QApplication([])
    yield app
