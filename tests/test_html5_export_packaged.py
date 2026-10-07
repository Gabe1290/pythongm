"""
HTML5 export in the packaged (PyInstaller) IDE.

Classroom report (2026-10-07): with the compiled Linux executable, "Export as
HTML5..." did nothing at all -- no file, no dialog. HTML5Exporter() reads
export/HTML5/templates/{engine.js,game_template.html} and
resources/vendor/pako.min.js when it is constructed, and PyGameMaker.spec
bundled none of them, so construction raised FileNotFoundError. That
happened outside the export's own error handling, and a Qt slot that raises
only prints to a console the packaged app doesn't have.

1. test_every_file_the_export_reads_is_bundled runs a real export from
   source, records every non-Python file it opens inside the repo, and checks
   PyGameMaker.spec ships each one at the same relative path. Any future
   data file the exporter starts reading fails here instead of in class.
2. test_export_crash_shows_a_dialog pins that an exception escaping the
   export is shown to the user.
"""

import builtins
import sys
import types
from pathlib import Path
from unittest.mock import MagicMock, patch

REPO = Path(__file__).resolve().parent.parent
SPEC = REPO / "PyGameMaker.spec"


def _bundled_files():
    """Evaluate PyGameMaker.spec with PyInstaller stand-ins and return the
    set of repo-relative paths it ships (as they land under sys._MEIPASS)."""
    hooks = types.ModuleType("PyInstaller.utils.hooks")
    hooks.collect_data_files = lambda *a, **k: []
    hooks.collect_submodules = lambda *a, **k: []
    fake = {"PyInstaller": types.ModuleType("PyInstaller"),
            "PyInstaller.utils": types.ModuleType("PyInstaller.utils"),
            "PyInstaller.utils.hooks": hooks}

    class _Analysis:
        def __init__(self, *args, datas=(), **kwargs):
            self.datas = list(datas)
            self.pure = self.zipped_data = self.scripts = []
            self.binaries = self.zipfiles = []

    def _tree(path, prefix, excludes=()):
        return [("__TREE__", path, prefix)]

    ns = {"SPECPATH": str(REPO), "Analysis": _Analysis, "Tree": _tree,
          "PYZ": lambda *a, **k: None, "EXE": lambda *a, **k: None,
          "BUNDLE": lambda *a, **k: None, "COLLECT": lambda *a, **k: None,
          "__name__": "__spec__"}
    with patch.dict(sys.modules, fake):
        exec(compile(SPEC.read_text(encoding="utf-8"), str(SPEC), "exec"), ns)

    shipped = set()
    for entry in ns["a"].datas:
        if entry[0] == "__TREE__":
            _, root, prefix = entry
            for f in Path(root).rglob("*"):
                if f.is_file() and "__pycache__" not in f.parts:
                    shipped.add((Path(prefix) / f.relative_to(root)).as_posix())
        else:
            src, dest = entry[0], entry[1]
            for f in Path(src).parent.glob(Path(src).name):
                if f.is_file():
                    shipped.add((Path(dest) / f.name).as_posix())
    return shipped


def test_every_file_the_export_reads_is_bundled(tmp_path):
    project = REPO / "samples" / "maze_1"
    opened = set()
    real_open = builtins.open

    def recording_open(file, *args, **kwargs):
        try:
            p = Path(file).resolve()
            if p.is_relative_to(REPO) and not p.is_relative_to(project) \
                    and p.suffix not in (".py", ".pyc"):
                opened.add(p.relative_to(REPO).as_posix())
        except (TypeError, ValueError, OSError):
            pass
        return real_open(file, *args, **kwargs)

    from export.HTML5 import html5_exporter
    with patch("builtins.open", recording_open), patch("io.open", recording_open):
        exporter = html5_exporter.HTML5Exporter()
        assert exporter.export(project, tmp_path / "out") is True, \
            exporter.last_error_message

    # Sanity: the recorder really saw the files that were missing in class.
    assert "export/HTML5/templates/engine.js" in opened
    assert "resources/vendor/pako.min.js" in opened

    missing = sorted(opened - _bundled_files())
    assert not missing, f"read by the HTML5 export but not bundled by PyGameMaker.spec: {missing}"


def test_export_crash_shows_a_dialog(tmp_path):
    from core.ide_exporters import IDEExporters

    ide = MagicMock()
    ide.current_project_path = tmp_path
    ide.current_project_data = {"name": "Mon jeu"}
    ide.tr = lambda s: s

    with patch("export.HTML5.html5_exporter.HTML5Exporter",
               side_effect=FileNotFoundError("engine.js")), \
         patch("core.ide_exporters.QFileDialog.getExistingDirectory",
               return_value=str(tmp_path)), \
         patch("core.ide_exporters.QMessageBox") as box:
        IDEExporters(ide).export_html5()   # must not raise

    box.critical.assert_called_once()
    assert "engine.js" in box.critical.call_args[0][2]
