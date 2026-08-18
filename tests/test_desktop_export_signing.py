"""Desktop export code signing mechanism (docs/EXPORT_POLISH_PLAN.md item
2b): a real Authenticode certificate / Apple Developer ID is out of this
repo's reach, so this is "mechanism only" -- signing_certificate_path /
signing_identity absent (the default) must change nothing, and every
subprocess call (signtool / codesign / notarytool / stapler) is mocked
rather than actually run.
"""
import json
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


def _exe_exporter(tmp_path, settings=None):
    from export.exe.exe_exporter import ExeExporter
    ex = ExeExporter()
    ex.project_data = {"name": "Mon Jeu"}
    ex.export_settings = settings or {}
    ex.output_path = tmp_path / "out"
    ex.output_path.mkdir(parents=True, exist_ok=True)
    return ex


def _macos_exporter(tmp_path, settings=None):
    from export.macos.macos_exporter import MacOSExporter
    ex = MacOSExporter()
    ex.project_data = {"name": "Mon Jeu"}
    ex.export_settings = settings or {}
    ex.output_path = tmp_path / "out"
    ex.output_path.mkdir(parents=True, exist_ok=True)
    return ex


# ---------------------------------------------------------------------------
# Base hook: no-op by default
# ---------------------------------------------------------------------------

def test_base_sign_build_is_a_no_op(qapp, tmp_path):
    from export.desktop.pygame_desktop_exporter import BasePygameDesktopExporter
    ex = BasePygameDesktopExporter()
    assert ex._sign_build(tmp_path) is None


def test_linux_never_overrides_sign_build(qapp):
    """ELF has no signing-metadata concept -- Linux inherits the no-op."""
    from export.linux.linux_exporter import LinuxExporter
    from export.desktop.pygame_desktop_exporter import BasePygameDesktopExporter
    assert LinuxExporter._sign_build is BasePygameDesktopExporter._sign_build


# ---------------------------------------------------------------------------
# Windows (signtool)
# ---------------------------------------------------------------------------

class TestWindowsSigning:
    def test_unconfigured_is_a_no_op(self, qapp, tmp_path):
        ex = _exe_exporter(tmp_path)
        assert ex._sign_build(tmp_path) is None

    def test_missing_exe_produces_a_clear_error(self, qapp, tmp_path, monkeypatch):
        ex = _exe_exporter(tmp_path, {"signing_certificate_path": "/tmp/cert.pfx"})
        # exe was never actually built at output_path in this test
        result = ex._sign_build(tmp_path)
        assert result is not None
        assert "Could not find" in result

    def test_missing_signtool_produces_a_clear_error(self, qapp, tmp_path, monkeypatch):
        import export.exe.exe_exporter as mod
        ex = _exe_exporter(tmp_path, {"signing_certificate_path": "/tmp/cert.pfx"})
        exe_path = ex.output_path / (ex.app_name() + ex.executable_suffix)
        exe_path.write_bytes(b"fake exe")

        monkeypatch.setattr(mod.shutil, "which", lambda name: None)
        result = ex._sign_build(tmp_path)
        assert result is not None
        assert "signtool" in result.lower()

    def test_configured_runs_signtool_with_expected_args(self, qapp, tmp_path, monkeypatch):
        import export.exe.exe_exporter as mod
        ex = _exe_exporter(tmp_path, {
            "signing_certificate_path": "/tmp/cert.pfx",
            "signing_certificate_password": "s3cret",
        })
        exe_path = ex.output_path / (ex.app_name() + ex.executable_suffix)
        exe_path.write_bytes(b"fake exe")

        monkeypatch.setattr(mod.shutil, "which", lambda name: "/usr/bin/signtool")

        captured = {}

        class _Result:
            returncode = 0
            stdout = "Successfully signed"
            stderr = ""

        def _fake_run(cmd, **kwargs):
            captured["cmd"] = cmd
            return _Result()

        monkeypatch.setattr(mod.subprocess, "run", _fake_run)

        result = ex._sign_build(tmp_path)
        assert result is None
        cmd = captured["cmd"]
        assert cmd[0] == "/usr/bin/signtool"
        assert cmd[1] == "sign"
        assert "/f" in cmd and cmd[cmd.index("/f") + 1] == "/tmp/cert.pfx"
        assert "/p" in cmd and cmd[cmd.index("/p") + 1] == "s3cret"
        assert str(exe_path) in cmd
        assert "timestamp.digicert.com" in " ".join(cmd)

    def test_custom_timestamp_url_is_used(self, qapp, tmp_path, monkeypatch):
        import export.exe.exe_exporter as mod
        ex = _exe_exporter(tmp_path, {
            "signing_certificate_path": "/tmp/cert.pfx",
            "signing_timestamp_url": "http://timestamp.example.com",
        })
        exe_path = ex.output_path / (ex.app_name() + ex.executable_suffix)
        exe_path.write_bytes(b"fake exe")
        monkeypatch.setattr(mod.shutil, "which", lambda name: "/usr/bin/signtool")

        captured = {}

        class _Result:
            returncode = 0
            stdout = ""
            stderr = ""

        def _fake_run(cmd, **kw):
            captured["cmd"] = cmd
            return _Result()
        monkeypatch.setattr(mod.subprocess, "run", _fake_run)

        ex._sign_build(tmp_path)
        assert "http://timestamp.example.com" in captured["cmd"]

    def test_signtool_failure_surfaces_its_output(self, qapp, tmp_path, monkeypatch):
        import export.exe.exe_exporter as mod
        ex = _exe_exporter(tmp_path, {"signing_certificate_path": "/tmp/cert.pfx"})
        exe_path = ex.output_path / (ex.app_name() + ex.executable_suffix)
        exe_path.write_bytes(b"fake exe")
        monkeypatch.setattr(mod.shutil, "which", lambda name: "/usr/bin/signtool")

        class _Result:
            returncode = 1
            stdout = "Error: cert not found"
            stderr = ""

        monkeypatch.setattr(mod.subprocess, "run", lambda cmd, **kw: _Result())

        result = ex._sign_build(tmp_path)
        assert result is not None
        assert "cert not found" in result


# ---------------------------------------------------------------------------
# macOS (codesign + notarytool + stapler)
# ---------------------------------------------------------------------------

class TestMacosSigning:
    def test_unconfigured_is_a_no_op(self, qapp, tmp_path):
        ex = _macos_exporter(tmp_path)
        assert ex._sign_build(tmp_path) is None

    def test_missing_app_produces_a_clear_error(self, qapp, tmp_path):
        ex = _macos_exporter(tmp_path, {"signing_identity": "Developer ID Application: X"})
        result = ex._sign_build(tmp_path)
        assert result is not None
        assert "Could not find" in result

    def _app(self, ex):
        app_path = ex.output_path / (ex.app_name() + ".app")
        app_path.mkdir(parents=True, exist_ok=True)
        return app_path

    def test_missing_codesign_produces_a_clear_error(self, qapp, tmp_path, monkeypatch):
        import export.macos.macos_exporter as mod
        ex = _macos_exporter(tmp_path, {"signing_identity": "Developer ID Application: X"})
        self._app(ex)
        monkeypatch.setattr(mod.shutil, "which", lambda name: None)
        result = ex._sign_build(tmp_path)
        assert result is not None
        assert "codesign" in result.lower()

    def test_codesign_only_runs_codesign_and_stops(self, qapp, tmp_path, monkeypatch):
        """No 'notarize' setting -- codesign runs, notarytool never called."""
        import export.macos.macos_exporter as mod
        ex = _macos_exporter(tmp_path, {"signing_identity": "Developer ID Application: X"})
        app_path = self._app(ex)
        monkeypatch.setattr(mod.shutil, "which", lambda name: f"/usr/bin/{name}")

        calls = []

        class _Result:
            returncode = 0
            stdout = ""
            stderr = ""

        def _fake_run(cmd, **kwargs):
            calls.append(cmd)
            return _Result()

        monkeypatch.setattr(mod.subprocess, "run", _fake_run)
        result = ex._sign_build(tmp_path)
        assert result is None
        assert len(calls) == 1
        cmd = calls[0]
        assert cmd[0] == "/usr/bin/codesign"
        assert "--sign" in cmd and cmd[cmd.index("--sign") + 1] == "Developer ID Application: X"
        assert str(app_path) in cmd

    def test_notarize_without_credentials_produces_a_clear_error(self, qapp, tmp_path, monkeypatch):
        import export.macos.macos_exporter as mod
        ex = _macos_exporter(tmp_path, {
            "signing_identity": "Developer ID Application: X",
            "notarize": True,
        })
        self._app(ex)
        monkeypatch.setattr(mod.shutil, "which", lambda name: f"/usr/bin/{name}")
        monkeypatch.setattr(mod.subprocess, "run",
                            lambda cmd, **kw: type("R", (), {"returncode": 0, "stdout": "", "stderr": ""})())

        result = ex._sign_build(tmp_path)
        assert result is not None
        assert "apple_id" in result

    def test_full_notarize_and_staple_flow(self, qapp, tmp_path, monkeypatch):
        import export.macos.macos_exporter as mod
        ex = _macos_exporter(tmp_path, {
            "signing_identity": "Developer ID Application: X",
            "notarize": True,
            "apple_id": "dev@example.com",
            "apple_id_password": "app-specific-pw",
            "apple_team_id": "TEAMID123",
        })
        self._app(ex)
        monkeypatch.setattr(mod.shutil, "which", lambda name: f"/usr/bin/{name}")

        calls = []

        class _Result:
            returncode = 0
            stdout = "success"
            stderr = ""

        def _fake_run(cmd, **kwargs):
            calls.append(cmd)
            return _Result()

        monkeypatch.setattr(mod.subprocess, "run", _fake_run)
        result = ex._sign_build(tmp_path)
        assert result is None

        # codesign, ditto, notarytool submit, stapler staple -- in order.
        assert calls[0][0] == "/usr/bin/codesign"
        assert calls[1][0] == "ditto"
        notarize_cmd = calls[2]
        assert notarize_cmd[0] == "/usr/bin/xcrun"
        assert "notarytool" in notarize_cmd
        assert "--apple-id" in notarize_cmd
        assert notarize_cmd[notarize_cmd.index("--apple-id") + 1] == "dev@example.com"
        assert "--team-id" in notarize_cmd
        staple_cmd = calls[3]
        assert staple_cmd[0] == "/usr/bin/xcrun"
        assert "stapler" in staple_cmd
        assert "staple" in staple_cmd

    def test_notarization_failure_stops_before_stapling(self, qapp, tmp_path, monkeypatch):
        import export.macos.macos_exporter as mod
        ex = _macos_exporter(tmp_path, {
            "signing_identity": "Developer ID Application: X",
            "notarize": True,
            "apple_id": "dev@example.com",
            "apple_id_password": "pw",
            "apple_team_id": "TEAMID123",
        })
        self._app(ex)
        monkeypatch.setattr(mod.shutil, "which", lambda name: f"/usr/bin/{name}")

        calls = []

        def _fake_run(cmd, **kwargs):
            calls.append(cmd)
            if len(calls) == 3:  # notarytool submit
                return type("R", (), {"returncode": 1, "stdout": "", "stderr": "rejected"})()
            return type("R", (), {"returncode": 0, "stdout": "", "stderr": ""})()

        monkeypatch.setattr(mod.subprocess, "run", _fake_run)
        result = ex._sign_build(tmp_path)
        assert result is not None
        assert "rejected" in result
        assert len(calls) == 3  # stapler never ran


# ---------------------------------------------------------------------------
# Export-level integration: a signing failure fails the whole export
# ---------------------------------------------------------------------------

def test_export_project_fails_when_signing_fails(qapp, tmp_path, monkeypatch):
    from export.exe.exe_exporter import ExeExporter
    ex = ExeExporter()

    project = tmp_path / "MyProject"
    project.mkdir()
    (project / "project.json").write_text(json.dumps({
        "name": "Mon Jeu", "assets": {"objects": {}, "rooms": {}},
    }), encoding="utf-8")

    monkeypatch.setattr(ex, "_host_platform_refusal", lambda: None)
    monkeypatch.setattr(ex, "_require_pygame_dependencies", lambda: True)
    monkeypatch.setattr(ex, "_run_pyinstaller", lambda spec: True)
    monkeypatch.setattr(ex, "_copy_to_output", lambda build_dir: True)
    monkeypatch.setattr(ex, "_sign_build", lambda build_dir: "signtool exploded")

    emits = []
    ex.export_complete.connect(lambda ok, msg: emits.append((ok, msg)))

    result = ex.export_project(str(project), str(tmp_path / "out"), {})
    assert result is False
    assert len(emits) == 1
    assert emits[0][0] is False
    assert "signtool exploded" in emits[0][1]


def test_export_project_succeeds_when_signing_is_a_no_op(qapp, tmp_path, monkeypatch):
    from export.exe.exe_exporter import ExeExporter
    ex = ExeExporter()

    project = tmp_path / "MyProject"
    project.mkdir()
    (project / "project.json").write_text(json.dumps({
        "name": "Mon Jeu", "assets": {"objects": {}, "rooms": {}},
    }), encoding="utf-8")

    monkeypatch.setattr(ex, "_host_platform_refusal", lambda: None)
    monkeypatch.setattr(ex, "_require_pygame_dependencies", lambda: True)
    monkeypatch.setattr(ex, "_run_pyinstaller", lambda spec: True)
    monkeypatch.setattr(ex, "_copy_to_output", lambda build_dir: True)
    # No signing_certificate_path in settings -- _sign_build's own no-op.

    result = ex.export_project(str(project), str(tmp_path / "out"), {"include_debug": True})
    assert result is True
