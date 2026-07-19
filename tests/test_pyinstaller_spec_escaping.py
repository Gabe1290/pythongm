"""The generated PyInstaller .spec files must be valid Python.

A .spec is a Python file PyInstaller exec()s. The exe/linux/macos exporters
interpolate every bundled asset's path into a string literal in the spec's
`datas` list, and the exe exporter interpolates the user's `icon_path` too.
Two hazards were unescaped (export-I/O finder, 2026-07-19):

- an asset filename with an apostrophe — plausible for French educational
  content, e.g. "épée d'or.png" — closed the single-quoted literal early
  (SyntaxError, whole export fails);
- a Windows icon path like C:\\Users\\...\\icon.ico injected an invalid "\\U"
  escape into the exec()'d spec.

The fix forward-slashes separators and uses repr() for every interpolated path.
This test builds a spec from a game dir containing an apostrophe-named asset (and,
for exe, a backslash icon path) and asserts the result compiles.
"""
import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT))

from export.exe.exe_exporter import ExeExporter        # noqa: E402
from export.linux.linux_exporter import LinuxExporter  # noqa: E402
from export.macos.macos_exporter import MacOSExporter  # noqa: E402

HOSTILE_ASSET = "épée d'or.png"   # apostrophe + non-ASCII (French content)


def _build_dir_with_hostile_asset(tmp_path):
    game = tmp_path / "game" / "assets" / "images"
    game.mkdir(parents=True)
    (game / HOSTILE_ASSET).write_bytes(b"\x89PNG\r\n")  # any bytes; name is the point
    (tmp_path / "game" / "main.py").write_text("# launcher\n", encoding="utf-8")
    return tmp_path


@pytest.mark.parametrize("cls", [ExeExporter, LinuxExporter, MacOSExporter])
def test_spec_with_apostrophe_asset_compiles(cls, tmp_path):
    exporter = cls()
    exporter.project_data = {"name": "L'aventure"}   # apostrophe in name too
    exporter.export_settings = {"icon_path": r"C:\Users\gthul\pics\icon.ico"}

    build_dir = _build_dir_with_hostile_asset(tmp_path)
    spec_file = exporter._create_spec_file(build_dir, Path("launcher.py"))

    spec_src = spec_file.read_text(encoding="utf-8")
    # The load-bearing assertion: PyInstaller exec()s this, so it must parse.
    compile(spec_src, str(spec_file), "exec")
    # The hostile asset must still be present in the datas (not dropped).
    assert "épée d" in spec_src


def test_exe_spec_icon_path_backslashes_are_safe(tmp_path):
    exporter = ExeExporter()
    exporter.project_data = {"name": "Game"}
    # A raw Windows path whose \U would be an invalid escape if unescaped.
    exporter.export_settings = {"icon_path": r"C:\Users\gthul\pics\icon.ico"}

    build_dir = _build_dir_with_hostile_asset(tmp_path)
    spec_file = exporter._create_spec_file(build_dir, Path("launcher.py"))
    spec_src = spec_file.read_text(encoding="utf-8")

    compile(spec_src, str(spec_file), "exec")
    assert "icon=" in spec_src
    # Forward-slashed, so no invalid escape reaches the exec()'d spec.
    assert "C:/Users/gthul/pics/icon.ico" in spec_src


def test_exe_spec_without_icon_still_compiles(tmp_path):
    exporter = ExeExporter()
    exporter.project_data = {"name": "Game"}
    exporter.export_settings = {}   # no icon_path

    build_dir = _build_dir_with_hostile_asset(tmp_path)
    spec_file = exporter._create_spec_file(build_dir, Path("launcher.py"))
    compile(spec_file.read_text(encoding="utf-8"), str(spec_file), "exec")
