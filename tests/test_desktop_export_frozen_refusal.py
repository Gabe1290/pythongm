"""Regression test: exporting a game to a native executable from a
PACKAGED (PyInstaller-frozen) build of the IDE must refuse immediately
with an actionable message, not hang and then fail with a misleading
"PyInstaller not found".

User-reported (2026-10-14): "The Linux PyGameMaker executable cannot
generate an executable version of the game." Root cause: PyInstaller
IS bundled into the frozen IDE (export/base_exporter.py's
`_check_pyinstaller` does a plain `import PyInstaller`, and CI's build
environment has that package installed, so the import genuinely
succeeds inside the frozen app) -- so the dependency check passed, but
`_run_pyinstaller` then shells out via `sys.executable -m PyInstaller
...`, and inside a frozen build `sys.executable` IS the frozen
PyGameMaker binary, not a real Python. `main.py` has no `-m` handling,
so that command just launches a second IDE window and the real build
never runs; the export sits until its own 900-second timeout and then
reports "PyInstaller build failed" -- a deeply misleading diagnosis for
what is actually a structural limitation (see the module docstring's
"Exporting requires the IDE to run from source" note, and CLAUDE.md's
2026-06-26 export-dependency decision).

`_frozen_build_refusal` fixes this by checking `sys.frozen` up front,
before `_load_project`/`_require_pygame_dependencies` ever run, so the
refusal fires without touching the filesystem or PyInstaller at all --
this test exploits exactly that by calling `export_project` with
nonexistent paths and confirming it still returns a clean, immediate
refusal rather than crashing trying to read them.
"""
import os
os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT))

from conftest import skip_without_pyside6  # noqa: E402

pytestmark = skip_without_pyside6


@pytest.fixture(scope="module")
def qapp():
    from PySide6.QtWidgets import QApplication
    return QApplication.instance() or QApplication([])


def test_no_refusal_when_not_frozen(qapp, monkeypatch):
    from export.desktop.pygame_desktop_exporter import BasePygameDesktopExporter
    monkeypatch.setattr(sys, "frozen", False, raising=False)
    ex = BasePygameDesktopExporter()
    assert ex._frozen_build_refusal() is None


def test_refusal_when_frozen(qapp, monkeypatch):
    from export.desktop.pygame_desktop_exporter import BasePygameDesktopExporter
    monkeypatch.setattr(sys, "frozen", True, raising=False)
    ex = BasePygameDesktopExporter()
    refusal = ex._frozen_build_refusal()
    assert refusal is not None
    assert "packaged" in refusal.lower()
    assert "source checkout" in refusal.lower() or "run pygamemaker from" in refusal.lower()
    assert "html5" in refusal.lower() or "web" in refusal.lower()
    # Must NOT repeat the misleading "PyInstaller not found" wording --
    # that message is for a genuinely missing dependency, not this case.
    assert "not found" not in refusal.lower()


@pytest.mark.parametrize("exporter_cls_path,platform_label", [
    ("export.linux.linux_exporter.LinuxExporter", "Linux executable"),
    ("export.exe.exe_exporter.ExeExporter", "Windows .exe"),
    ("export.macos.macos_exporter.MacOSExporter", "macOS .app"),
])
def test_export_project_refuses_immediately_when_frozen_for_every_desktop_target(
        qapp, monkeypatch, tmp_path, exporter_cls_path, platform_label):
    """Every desktop target inherits this from BasePygameDesktopExporter --
    none of them override export_project or _host_platform_refusal, so one
    guard covers all three. Uses nonexistent project/output paths: the
    refusal must fire before any file I/O or dependency check."""
    module_path, cls_name = exporter_cls_path.rsplit(".", 1)
    import importlib
    cls = getattr(importlib.import_module(module_path), cls_name)

    monkeypatch.setattr(sys, "frozen", True, raising=False)
    # Also make sure this isn't accidentally passing because the host
    # platform refusal fired instead -- force the host check to pass.
    import platform as platform_module
    monkeypatch.setattr(platform_module, "system",
                         lambda: cls.required_host_platform or "Linux")

    ex = cls()
    results = []
    ex.export_complete.connect(lambda ok, msg: results.append((ok, msg)))

    ok = ex.export_project(
        str(tmp_path / "does_not_exist_project"),
        str(tmp_path / "does_not_exist_output"),
        {},
    )

    assert ok is False
    assert len(results) == 1
    success, message = results[0]
    assert success is False
    assert "packaged" in message.lower()
    assert "html5" in message.lower() or "web" in message.lower()


def test_frozen_refusal_checked_before_pyinstaller_dependency_check(qapp, monkeypatch, tmp_path):
    """The bug this guards against: _check_pyinstaller can return True
    inside a frozen build (the package is routinely bundled in), so the
    dependency check alone cannot catch this -- the frozen check must run
    first and never reach _require_pygame_dependencies at all."""
    from export.linux.linux_exporter import LinuxExporter
    monkeypatch.setattr(sys, "frozen", True, raising=False)
    import platform as platform_module
    monkeypatch.setattr(platform_module, "system", lambda: "Linux")

    ex = LinuxExporter()
    called = []
    monkeypatch.setattr(
        ex, "_require_pygame_dependencies", lambda: called.append(True) or True)

    ex.export_project(str(tmp_path / "proj"), str(tmp_path / "out"), {})
    assert not called, "_require_pygame_dependencies must not run when the IDE is frozen"
