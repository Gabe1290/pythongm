"""A packaged/frozen build of the IDE cannot export a native executable,
Android APK (outside WSL), or iOS app — all three shell out to a separate
Python-based tool (PyInstaller, buildozer, kivy-ios) via ``sys.executable``,
which inside a frozen build IS the PyGameMaker binary itself, not a real
Python (see export/desktop/pygame_desktop_exporter.py's
``_frozen_build_refusal`` and tests/test_desktop_export_frozen_refusal.py,
the precedent this file follows).

User-reported (2026-10-15): even with that refusal in place, the Export
Game dialog still showed those targets as plain selectable radio buttons,
so a student had to click Export and read an error to discover the dead
end. Two changes, covered here:

1. export/registry.py's probes now report a packaged build as
   ``available=False`` with a distinct "run from Python source" message
   for every affected target (windows_exe, linux, macos, ios, and
   android_apk's NATIVE path only — android_apk via WSL is unaffected,
   since the WSL bridge never touches this process's own
   ``sys.executable``). html5 / kivy_project / source_zip are unaffected
   regardless — none of them shell out to a second Python.
2. The dialog (core/ide/_export.py's export_game) now disables (greys
   out) any radio whose probe reports ``available=False``, instead of
   discarding that half of the probe's return value.
3. AndroidExporter and iOSExporter gained their own frozen-build refusal
   (belt-and-suspenders, same shape as desktop's), since they are the two
   export targets that didn't already have one.
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


# ---------------------------------------------------------------------------
# export/registry.py probes
# ---------------------------------------------------------------------------

class TestRegistryProbesUnderAFrozenBuild:
    @pytest.mark.parametrize("probe_name,label_prefix", [
        ("_windows_probe", "Windows Executable (.exe)"),
        ("_linux_probe", "Linux Binary"),
        ("_macos_probe", "macOS Application (.app)"),
        ("_ios_probe", "iOS App (.ipa)"),
    ])
    def test_probe_refuses_when_frozen(self, monkeypatch, probe_name, label_prefix):
        import export.registry as reg
        monkeypatch.setattr(sys, "frozen", True, raising=False)
        probe = getattr(reg, probe_name)
        available, label = probe()
        assert available is False
        assert label.startswith(label_prefix)
        assert "python source" in label.lower()
        assert "packaged app" in label.lower()
        # Distinct from the host-platform-mismatch message -- a different
        # problem needs a different fix, and conflating them would send a
        # frozen-Linux-build student looking for a Windows machine.
        assert "requires" not in label.lower()

    def test_android_native_refuses_when_frozen(self, monkeypatch):
        import export.registry as reg
        monkeypatch.setattr(sys, "frozen", True, raising=False)
        monkeypatch.setattr(reg.platform, "system", lambda: "Linux")
        available, label = reg._android_probe()
        assert available is False
        assert label.startswith("Android Package (.apk)")
        assert "python source" in label.lower()

    def test_android_via_wsl_is_unaffected_by_frozen(self, monkeypatch):
        """The WSL bridge never touches this process's own sys.executable
        -- a frozen Windows build can still export Android through WSL."""
        import export.registry as reg
        monkeypatch.setattr(sys, "frozen", True, raising=False)
        monkeypatch.setattr(reg.platform, "system", lambda: "Windows")

        class _FakeBridge:
            def is_wsl_available(self):
                return True

        monkeypatch.setattr(
            "export.android.wsl_bridge.WSLBridge", lambda: _FakeBridge())
        available, label = reg._android_probe()
        assert available is True
        assert "WSL" in label

    @pytest.mark.parametrize("probe_name", [
        "_html5_probe", "_kivy_project_probe", "_source_zip_probe"])
    def test_targets_with_no_subprocess_reinvocation_are_unaffected(
            self, monkeypatch, probe_name):
        """None of these ever shell out to a second Python, frozen or not."""
        import export.registry as reg
        monkeypatch.setattr(sys, "frozen", True, raising=False)
        available, _label = getattr(reg, probe_name)()
        assert available is True

    def test_not_frozen_is_unaffected(self, monkeypatch):
        """Sanity check the gate itself: explicitly NOT frozen must not
        trip any of the new refusals (guards against an inverted check)."""
        import export.registry as reg
        monkeypatch.setattr(sys, "frozen", False, raising=False)
        monkeypatch.setattr(reg.platform, "system", lambda: "Linux")
        assert reg._linux_probe()[0] is True


# ---------------------------------------------------------------------------
# The dialog itself must actually consume `available`, not discard it
# ---------------------------------------------------------------------------

def test_export_dialog_disables_unavailable_radios():
    src = (REPO_ROOT / "core" / "ide" / "_export.py").read_text(encoding="utf-8")
    dialog_src = src.split("def export_game(self):", 1)[1].split("\n    def ", 1)[0]
    assert "available, label = target.probe()" in dialog_src, (
        "export_game must bind the probe's availability, not discard it "
        "(e.g. `_available, label = ...`)")
    assert "radio.setEnabled(available)" in dialog_src


# ---------------------------------------------------------------------------
# AndroidExporter / iOSExporter's own belt-and-suspenders refusal
# ---------------------------------------------------------------------------

class TestAndroidFrozenRefusal:
    def test_native_path_refuses_when_frozen(self, qapp, tmp_path, monkeypatch):
        import export.android.android_exporter as mod
        ex = mod.AndroidExporter()
        monkeypatch.setattr(ex, "_load_project", lambda *a, **k: None)
        monkeypatch.setattr(mod.platform, "system", lambda: "Linux")
        monkeypatch.setattr(mod.sys, "frozen", True, raising=False)

        called = []
        monkeypatch.setattr(
            ex, "_check_buildozer", lambda: called.append(True) or True)

        emits = []
        ex.export_complete.connect(lambda ok, msg: emits.append((ok, msg)))

        result = ex.export_project("proj", str(tmp_path / "out"), {})
        assert result is False
        assert not called, "_check_buildozer must not run when frozen"
        assert len(emits) == 1
        success, message = emits[0]
        assert success is False
        assert "packaged" in message.lower()
        assert "html5" in message.lower() or "web" in message.lower()

    def test_wsl_path_is_not_blocked_by_the_frozen_check(self, qapp, tmp_path, monkeypatch):
        """The frozen refusal lives in the native (else) branch only --
        prove the WSL branch is reachable without tripping it by making
        WSL itself fail for an unrelated, easily recognised reason."""
        import export.android.android_exporter as mod
        ex = mod.AndroidExporter()
        monkeypatch.setattr(ex, "_load_project", lambda *a, **k: None)
        monkeypatch.setattr(mod.platform, "system", lambda: "Windows")
        monkeypatch.setattr(mod.sys, "frozen", True, raising=False)

        class _FakeBridge:
            def is_wsl_available(self):
                return False

            def get_wsl_info(self):
                return {"message": "sentinel-not-detected"}

        monkeypatch.setattr(
            "export.android.wsl_bridge.WSLBridge", lambda: _FakeBridge())

        emits = []
        ex.export_complete.connect(lambda ok, msg: emits.append((ok, msg)))
        result = ex.export_project("proj", str(tmp_path / "out"), {})
        assert result is False
        assert "sentinel-not-detected" in emits[0][1]
        assert "packaged" not in emits[0][1].lower()


class TestIOSFrozenRefusal:
    def test_refuses_when_frozen(self, qapp, tmp_path, monkeypatch):
        import export.ios.ios_exporter as mod
        ex = mod.iOSExporter()
        monkeypatch.setattr(ex, "_check_macos", lambda: True)
        monkeypatch.setattr(mod.sys, "frozen", True, raising=False)

        called = []
        monkeypatch.setattr(
            ex, "_check_xcode", lambda: called.append(True) or True)

        emits = []
        ex.export_complete.connect(lambda ok, msg: emits.append((ok, msg)))

        result = ex.export_project(
            str(tmp_path / "proj"), str(tmp_path / "out"), {})
        assert result is False
        assert not called, "_check_xcode must not run when frozen"
        assert len(emits) == 1
        success, message = emits[0]
        assert success is False
        assert "packaged" in message.lower()
        assert "html5" in message.lower() or "web" in message.lower()

    def test_not_frozen_reaches_xcode_check(self, qapp, tmp_path, monkeypatch):
        """Sanity check: without the frozen flag, execution still reaches
        the (pre-existing) Xcode check -- proves the new guard doesn't
        fire unconditionally."""
        import export.ios.ios_exporter as mod
        ex = mod.iOSExporter()
        monkeypatch.setattr(ex, "_check_macos", lambda: True)
        monkeypatch.setattr(mod.sys, "frozen", False, raising=False)

        called = []
        monkeypatch.setattr(
            ex, "_check_xcode", lambda: called.append(True) or False)

        emits = []
        ex.export_complete.connect(lambda ok, msg: emits.append((ok, msg)))
        ex.export_project(str(tmp_path / "proj"), str(tmp_path / "out"), {})
        assert called, "_check_xcode should run when not frozen"
