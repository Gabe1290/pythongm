"""Build Game / Build and Run (F7/F8) -- deferred-items plan Tier 2 item 7.

Restores the Build -> Build Game... (F7) / Build and Run (F8) menu
entries removed in rc.11's "stop lying to users" cleanup (commit
77e9dbf) along with their "Not Implemented" stubs, tracked in TODO.md
since. Per the plan's note, this is wiring a menu action + progress UI
around an existing capability rather than new export infrastructure:
export.registry.desktop_exporter_for_host already picks the right
PyInstaller-based exporter class for the host OS (the same one the
Export Game dialog's Windows/macOS/Linux entries use), and
_run_export_with_progress already drives an exporter behind a progress
dialog. build_game/build_and_run just call both directly instead of
requiring the multi-target Export Game dialog detour; build_and_run
additionally launches the built artifact via a new on_success hook on
_run_export_with_progress.

Same StubIDE-with-a-fake-_run_export_with_progress pattern as
test_audit_project_dialogs.py's export_windows_exe tests.
"""
import os
os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

import platform
import sys
from pathlib import Path
from unittest.mock import patch

import pytest

sys.path.insert(0, str(Path(__file__).parent.parent))
from conftest import skip_without_pyside6

pytestmark = skip_without_pyside6


@pytest.fixture(scope="module")
def _qapp():
    from PySide6.QtWidgets import QApplication
    app = QApplication.instance() or QApplication([])
    yield app


def _ide_cls():
    from core.ide_window import PyGameMakerIDE
    return PyGameMakerIDE


class _StubIDE:
    """Every attribute _build_desktop's body touches."""

    def __init__(self, output_dir="/tmp/out", options=None):
        self._output_dir = output_dir
        self._export_options = options
        self.captured = {}

    def tr(self, text):
        return text

    def _require_open_project(self):
        return True

    def _ask_export_dir(self, suffix):
        return self._output_dir

    def _current_export_options(self):
        return _ide_cls()._current_export_options(self)

    def _run_export_with_progress(self, **kwargs):
        self.captured.update(kwargs)

    def _build_desktop(self, run_after):
        return _ide_cls()._build_desktop(self, run_after)


class TestBuildDesktopRouting:
    def test_picks_the_host_appropriate_exporter_class(self, _qapp):
        from export.registry import desktop_exporter_for_host
        stub = _StubIDE()
        _ide_cls()._build_desktop(stub, run_after=False)
        expected = desktop_exporter_for_host(platform.system())
        assert stub.captured["exporter_class"] is expected

    def test_output_dir_reaches_export_settings(self, _qapp):
        stub = _StubIDE(output_dir="/tmp/mygame_build")
        _ide_cls()._build_desktop(stub, run_after=False)
        assert stub.captured["output_dir"] == "/tmp/mygame_build"
        assert stub.captured["export_settings"]["output_path"] == "/tmp/mygame_build"

    def test_checkbox_options_reach_export_settings(self, _qapp):
        stub = _StubIDE(options={"include_assets": False, "optimize": False,
                                  "include_debug": True})
        _ide_cls()._build_desktop(stub, run_after=False)
        settings = stub.captured["export_settings"]
        assert settings["include_debug"] is True
        assert settings["optimize"] is False

    def test_build_game_has_no_success_hook(self, _qapp):
        stub = _StubIDE()
        _ide_cls().build_game(stub)
        assert stub.captured["on_success"] is None

    def test_build_and_run_has_a_success_hook(self, _qapp):
        stub = _StubIDE()
        _ide_cls().build_and_run(stub)
        assert callable(stub.captured["on_success"])

    def test_build_and_run_hook_launches_the_built_game(self, _qapp):
        stub = _StubIDE(output_dir="/tmp/whatever")
        launched = []
        stub._launch_built_game = lambda output_dir: launched.append(output_dir)
        _ide_cls().build_and_run(stub)
        stub.captured["on_success"]()
        assert launched == ["/tmp/whatever"]

    def test_no_open_project_never_reaches_run_export(self, _qapp):
        stub = _StubIDE()
        stub._require_open_project = lambda: False
        _ide_cls().build_game(stub)
        assert stub.captured == {}

    def test_cancelled_dir_picker_never_reaches_run_export(self, _qapp):
        stub = _StubIDE(output_dir="")  # QFileDialog cancel returns ""
        _ide_cls().build_game(stub)
        assert stub.captured == {}


class TestLaunchBuiltGame:
    """_launch_built_game must find the exact artifact name each desktop
    exporter's spec file produces (game_name sanitized the same way,
    .exe/.app/no-suffix per host) -- see export/{exe,linux,macos}_exporter.py
    _create_spec_file."""

    def _ide_with_project_name(self, name):
        stub = type("S", (), {})()
        stub.current_project_data = {"name": name}
        stub.tr = lambda self, t: t
        return stub

    def test_windows_launches_sanitized_exe(self, tmp_path, _qapp):
        (tmp_path / "L_aventure.exe").write_bytes(b"")
        stub = self._ide_with_project_name("L'aventure")
        with patch("platform.system", return_value="Windows"), \
             patch("core.ide_window.os.startfile", create=True) as mock_start:
            _ide_cls()._launch_built_game(stub, str(tmp_path))
        mock_start.assert_called_once_with(str(tmp_path / "L_aventure.exe"))

    def test_macos_opens_the_app_bundle(self, tmp_path, _qapp):
        (tmp_path / "MyGame.app").mkdir()
        stub = self._ide_with_project_name("MyGame")
        with patch("platform.system", return_value="Darwin"), \
             patch("subprocess.Popen") as mock_popen:
            _ide_cls()._launch_built_game(stub, str(tmp_path))
        mock_popen.assert_called_once_with(["open", str(tmp_path / "MyGame.app")])

    def test_linux_runs_the_binary(self, tmp_path, _qapp):
        (tmp_path / "MyGame").write_bytes(b"")
        stub = self._ide_with_project_name("MyGame")
        with patch("platform.system", return_value="Linux"), \
             patch("subprocess.Popen") as mock_popen:
            _ide_cls()._launch_built_game(stub, str(tmp_path))
        mock_popen.assert_called_once_with([str(tmp_path / "MyGame")])

    def test_missing_artifact_does_not_raise(self, tmp_path, _qapp):
        stub = self._ide_with_project_name("Ghost")
        with patch("platform.system", return_value="Linux"), \
             patch("subprocess.Popen") as mock_popen:
            _ide_cls()._launch_built_game(stub, str(tmp_path))  # must not raise
        mock_popen.assert_not_called()

    def test_missing_project_data_falls_back_to_game(self, tmp_path, _qapp):
        (tmp_path / "Game").write_bytes(b"")
        stub = type("S", (), {})()
        stub.current_project_data = None
        with patch("platform.system", return_value="Linux"), \
             patch("subprocess.Popen") as mock_popen:
            _ide_cls()._launch_built_game(stub, str(tmp_path))
        mock_popen.assert_called_once_with([str(tmp_path / "Game")])


class _FakeExportThread:
    """Stands in for core.ide_window.ExportThread without spinning a real
    OS thread (real QThread + cross-thread queued signals would make this
    test's completion timing non-deterministic). Schedules the fake
    export via QTimer.singleShot(0, ...) so it runs only once
    progress_dialog.exec()'s event loop is already spinning -- matching
    the real ordering (thread starts, *then* exec() blocks until the
    background thread's signal arrives and calls accept()). Calling
    export_complete synchronously before exec() starts would hide an
    unshown dialog and then hang the subsequent exec() forever."""

    def __init__(self, exporter, project_path, output_path, settings):
        self._exporter = exporter
        self._args = (project_path, output_path, settings)

    class _NullSignal:
        def connect(self, slot):
            pass

    finished = _NullSignal()

    def start(self):
        from PySide6.QtCore import QTimer
        QTimer.singleShot(0, lambda: self._exporter.export_project(*self._args))

    def wait(self):
        pass


class TestOnSuccessHookWiring:
    """_run_export_with_progress's new on_success parameter: called after
    a successful build (even if the user declines the open-folder
    prompt), never called on failure -- exercised against the real
    method (with ExportThread faked out per _FakeExportThread's
    docstring) so the progress-dialog/signal plumbing around the new
    parameter is genuinely covered, not just the call-through."""

    def _fake_exporter_class(self, success, message="done"):
        from PySide6.QtCore import QObject, Signal

        class FakeExporter(QObject):
            progress_update = Signal(int, str)
            export_complete = Signal(bool, str)
            cancel_requested = False

            def export_project(self, project_path, output_dir, settings):
                self.export_complete.emit(success, message)
                return success

        return FakeExporter

    def _run(self, _qapp, success, on_success):
        from PySide6.QtWidgets import QWidget

        from core.ide_window import PyGameMakerIDE

        # _run_export_with_progress uses `self` as the progress dialog's
        # QWidget parent (_ExportProgressDialog(self, ...)), so the stub
        # must be a real QWidget rather than a plain object -- unlike the
        # other stubs in this file, which never reach real Qt widget
        # construction.
        stub = QWidget()
        stub.current_project_path = "/tmp/proj"

        exporter_class = self._fake_exporter_class(success)

        with patch("core.ide_window.QMessageBox") as mock_box, \
             patch("core.ide_window.ExportThread", _FakeExportThread):
            mock_box.information.return_value = mock_box.StandardButton.No
            PyGameMakerIDE._run_export_with_progress(
                stub,
                exporter_class=exporter_class,
                output_dir="/tmp/out",
                export_settings={},
                dialog_title="t", status_text="t", dialog_size=(200, 100),
                success_title="t", failure_title="t", open_folder_prompt="t",
                on_success=on_success,
            )

    def test_on_success_called_after_a_successful_build(self, _qapp):
        calls = []
        self._run(_qapp, success=True, on_success=lambda: calls.append(True))
        assert calls == [True]

    def test_on_success_not_called_on_failure(self, _qapp):
        calls = []
        self._run(_qapp, success=False, on_success=lambda: calls.append(True))
        assert calls == []

    def test_none_on_success_is_a_noop(self, _qapp):
        # Existing callers (export_windows_exe etc.) don't pass on_success
        # at all -- must not raise when it's None.
        self._run(_qapp, success=True, on_success=None)
