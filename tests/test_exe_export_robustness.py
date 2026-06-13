"""Regression tests for the desktop EXE exporter (audits M38, M39).

M38: the project name was interpolated unescaped into single-quoted Python
literals in the generated PyInstaller spec, so an apostrophe (e.g. the French
"L'aventure") produced name='L'aventure.exe' — a SyntaxError when PyInstaller
exec'd the spec.

M39: _copy_to_output swallowed copy failures, so export reported success and
_cleanup deleted the only built copy when the output was locked.
"""

import os
os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

from pathlib import Path
import sys

import pytest

sys.path.insert(0, str(Path(__file__).parent.parent))

from conftest import skip_without_pyside6

pytestmark = skip_without_pyside6


@pytest.fixture(scope="module")
def _qapp():
    from PySide6.QtWidgets import QApplication
    app = QApplication.instance() or QApplication([])
    yield app


def _exporter(_qapp, name):
    from export.exe.exe_exporter import ExeExporter
    ex = ExeExporter()
    ex.project_data = {"name": name}
    ex.export_settings = {"include_debug": False, "optimize": False}
    return ex


class TestSpecNameSanitization:  # M38
    def test_apostrophe_name_produces_valid_spec(self, _qapp, tmp_path):
        build_dir = tmp_path / "build"
        (build_dir / "game").mkdir(parents=True)
        (build_dir / "game" / "main.py").write_text("# game\n", encoding="utf-8")
        launcher = build_dir / "game_launcher.py"
        launcher.write_text("# launcher\n", encoding="utf-8")

        ex = _exporter(_qapp, "L'aventure")
        ex.output_path = tmp_path / "out"
        spec_file = ex._create_spec_file(build_dir, launcher)
        spec_src = Path(spec_file).read_text(encoding="utf-8")

        # The headline failure: an apostrophe must not leak into a literal.
        assert "L'aventure" not in spec_src
        # The whole spec must be syntactically valid Python.
        compile(spec_src, "game.spec", "exec")


class TestCopyToOutputFailure:  # M39
    def test_copy_failure_returns_false(self, _qapp, tmp_path, monkeypatch):
        import time
        import export.exe.exe_exporter as mod

        ex = _exporter(_qapp, "Game")
        build_dir = tmp_path / "build"
        dist = build_dir / "dist"
        dist.mkdir(parents=True)
        (dist / "Game.exe").write_text("binary", encoding="utf-8")
        ex.output_path = tmp_path / "out"

        # Simulate a perpetually locked destination.
        def _locked(*a, **k):
            raise PermissionError("locked by antivirus")
        monkeypatch.setattr(mod.shutil, "copy2", _locked)
        monkeypatch.setattr(time, "sleep", lambda *_: None)

        assert ex._copy_to_output(build_dir) is False
        # The build copy must survive (caller must not clean up on False).
        assert (dist / "Game.exe").exists()

    def test_copy_success_returns_true(self, _qapp, tmp_path):
        ex = _exporter(_qapp, "Game")
        build_dir = tmp_path / "build"
        dist = build_dir / "dist"
        dist.mkdir(parents=True)
        (dist / "Game.exe").write_text("binary", encoding="utf-8")
        ex.output_path = tmp_path / "out"

        assert ex._copy_to_output(build_dir) is True
        assert (ex.output_path / "Game.exe").exists()
