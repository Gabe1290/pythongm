"""Android export: debug vs. release build presets
(docs/EXPORT_POLISH_PLAN.md item 3).

Covers: BuildspecGenerator emitting the right android.release_artifact,
AndroidExporter refusing an unsigned release before touching buildozer,
the native subprocess command + P4A_RELEASE_* env wiring for both build
types, .aab handling in _copy_to_output, and the WSL script text/keystore
plumbing (env vars must be textual `export` lines inside the script --
subprocess env= does not cross the wsl.exe process boundary).
"""

import os
os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT))

sys.path.insert(0, str(REPO_ROOT / "tests"))
from conftest import skip_without_pyside6  # noqa: E402

pytestmark = skip_without_pyside6


@pytest.fixture(scope="module")
def _qapp():
    from PySide6.QtWidgets import QApplication
    app = QApplication.instance() or QApplication([])
    yield app


# ---------------------------------------------------------------------------
# BuildspecGenerator.release_artifact
# ---------------------------------------------------------------------------

class TestBuildspecReleaseArtifact:
    def test_debug_defaults_to_apk(self, tmp_path):
        from export.Kivy.buildspec_generator import BuildspecGenerator
        gen = BuildspecGenerator({"name": "Test"}, tmp_path)
        content = gen._create_buildozer_spec_content()
        assert "android.release_artifact = apk" in content

    def test_explicit_debug_is_apk(self, tmp_path):
        from export.Kivy.buildspec_generator import BuildspecGenerator
        gen = BuildspecGenerator({"name": "Test"}, tmp_path, build_type="debug")
        content = gen._create_buildozer_spec_content()
        assert "android.release_artifact = apk" in content

    def test_release_is_aab(self, tmp_path):
        from export.Kivy.buildspec_generator import BuildspecGenerator
        gen = BuildspecGenerator({"name": "Test"}, tmp_path, build_type="release")
        content = gen._create_buildozer_spec_content()
        assert "android.release_artifact = aab" in content

    def test_unrecognized_build_type_falls_back_to_debug(self, tmp_path):
        from export.Kivy.buildspec_generator import BuildspecGenerator
        gen = BuildspecGenerator({"name": "Test"}, tmp_path, build_type="bogus")
        assert gen.build_type == "debug"


# ---------------------------------------------------------------------------
# AndroidExporter.export_project — release keystore gate
# ---------------------------------------------------------------------------

class TestReleaseKeystoreGate:
    def test_release_without_keystore_fails_before_platform_check(self, _qapp, tmp_path, monkeypatch):
        import export.android.android_exporter as mod
        ex = mod.AndroidExporter()
        monkeypatch.setattr(ex, "_load_project", lambda *a, **k: None)

        # If the keystore gate didn't fire first, this would blow up --
        # proves the gate runs before any platform/dependency work.
        monkeypatch.setattr(mod.platform, "system",
                            lambda: (_ for _ in ()).throw(AssertionError("should not reach platform check")))

        emits = []
        ex.export_complete.connect(lambda ok, msg: emits.append((ok, msg)))

        result = ex.export_project("proj", str(tmp_path / "out"), {"build_type": "release"})
        assert result is False
        assert len(emits) == 1
        assert emits[0][0] is False
        assert "keystore" in emits[0][1].lower()

    def test_release_with_partial_keystore_info_fails(self, _qapp, tmp_path, monkeypatch):
        import export.android.android_exporter as mod
        ex = mod.AndroidExporter()
        monkeypatch.setattr(ex, "_load_project", lambda *a, **k: None)
        monkeypatch.setattr(mod.platform, "system",
                            lambda: (_ for _ in ()).throw(AssertionError("should not reach platform check")))

        result = ex.export_project("proj", str(tmp_path / "out"), {
            "build_type": "release",
            "keystore_path": "/tmp/x.keystore",
            "keystore_password": "pw",
            # key_alias / key_password missing
        })
        assert result is False

    def test_debug_build_never_needs_a_keystore(self, _qapp, tmp_path, monkeypatch):
        import export.android.android_exporter as mod
        ex = mod.AndroidExporter()

        build_dir = tmp_path / "pygm_android_dbg"
        build_dir.mkdir()
        monkeypatch.setattr(mod.platform, "system", lambda: "Linux")
        monkeypatch.setattr(ex, "_load_project", lambda *a, **k: None)
        monkeypatch.setattr(ex, "_check_buildozer", lambda: True)
        monkeypatch.setattr(ex, "_check_kivy", lambda: True)
        monkeypatch.setattr(ex, "_check_cython", lambda: True)
        monkeypatch.setattr(ex, "_check_java", lambda: True)
        monkeypatch.setattr(ex, "_check_build_tools", lambda: [])
        monkeypatch.setattr(ex, "_create_build_directory", lambda: build_dir)
        # Fail at the first real build step -- we only care that the
        # keystore gate didn't block us from getting this far.
        monkeypatch.setattr(ex, "_generate_kivy_game", lambda b: False)

        result = ex.export_project("proj", str(tmp_path / "out"), {})
        assert result is False
        assert ex._build_type == "debug"
        assert ex._keystore_path is None


# ---------------------------------------------------------------------------
# _generate_buildozer_spec passes build_type through
# ---------------------------------------------------------------------------

def test_generate_buildozer_spec_passes_build_type(_qapp, tmp_path, monkeypatch):
    import export.android.android_exporter as mod
    ex = mod.AndroidExporter()
    ex.project_data = {"name": "Test"}
    ex._build_type = "release"

    captured = {}

    class _FakeGen:
        def __init__(self, project_data, build_dir, build_type="debug"):
            captured["build_type"] = build_type

        def generate_buildozer_spec(self):
            return True

    monkeypatch.setattr(
        "export.Kivy.buildspec_generator.BuildspecGenerator", _FakeGen)

    build_dir = tmp_path
    ok = ex._generate_buildozer_spec(build_dir)
    assert ok is True
    assert captured["build_type"] == "release"


# ---------------------------------------------------------------------------
# Native _run_buildozer command + env wiring
# ---------------------------------------------------------------------------

class TestNativeBuildCommand:
    def _run_capturing(self, ex, tmp_path, monkeypatch):
        import export.android.android_exporter as mod

        captured = {}

        class _FakeProc:
            stdout = iter(())
            returncode = 0

            def wait(self, timeout=None):
                return 0

        def _popen(cmd, **kwargs):
            captured["cmd"] = cmd
            captured["env"] = kwargs.get("env")
            return _FakeProc()

        monkeypatch.setattr(mod.subprocess, "Popen", _popen)
        persist_dir = tmp_path / "persist"
        persist_dir.mkdir()
        monkeypatch.setattr(ex, "_native_persistent_build_dir", lambda: persist_dir)
        build_dir = tmp_path / "build"
        build_dir.mkdir()
        ex._run_buildozer(build_dir)
        return captured

    def test_debug_command_uses_debug(self, _qapp, tmp_path, monkeypatch):
        import export.android.android_exporter as mod
        ex = mod.AndroidExporter()
        ex._use_wsl = False
        ex._build_type = "debug"
        captured = self._run_capturing(ex, tmp_path, monkeypatch)
        assert captured["cmd"][-2:] == ["android", "debug"]
        assert "P4A_RELEASE_KEYSTORE" not in captured["env"]

    def test_release_command_uses_release_and_sets_env(self, _qapp, tmp_path, monkeypatch):
        import export.android.android_exporter as mod
        ex = mod.AndroidExporter()
        ex._use_wsl = False
        ex._build_type = "release"
        keys_dir = tmp_path / "keys"
        keys_dir.mkdir()
        ex._keystore_path = str(keys_dir / "release.keystore")
        (keys_dir / "release.keystore").write_bytes(b"fake")
        ex._keystore_password = "storepw"
        ex._key_alias = "myalias"
        ex._key_password = "keypw"

        captured = self._run_capturing(ex, tmp_path, monkeypatch)
        assert captured["cmd"][-2:] == ["android", "release"]
        env = captured["env"]
        assert env["P4A_RELEASE_KEYSTORE"] == str((keys_dir / "release.keystore").resolve())
        assert env["P4A_RELEASE_KEYSTORE_PASSWD"] == "storepw"
        assert env["P4A_RELEASE_KEYALIAS"] == "myalias"
        assert env["P4A_RELEASE_KEYALIAS_PASSWD"] == "keypw"


# ---------------------------------------------------------------------------
# _copy_to_output — .aab handling
# ---------------------------------------------------------------------------

class TestCopyToOutputArtifacts:
    def test_copies_aab_as_well_as_apk(self, _qapp, tmp_path):
        import export.android.android_exporter as mod
        ex = mod.AndroidExporter()
        build_dir = tmp_path / "build"
        bin_dir = build_dir / "bin"
        bin_dir.mkdir(parents=True)
        (bin_dir / "app-release.aab").write_bytes(b"AAB")
        ex.output_path = tmp_path / "out"

        assert ex._copy_to_output(build_dir) is True
        assert (ex.output_path / "app-release.aab").read_bytes() == b"AAB"

    def test_apk_still_works_unchanged(self, _qapp, tmp_path):
        import export.android.android_exporter as mod
        ex = mod.AndroidExporter()
        build_dir = tmp_path / "build"
        bin_dir = build_dir / "bin"
        bin_dir.mkdir(parents=True)
        (bin_dir / "app-debug.apk").write_bytes(b"APK")
        ex.output_path = tmp_path / "out"

        assert ex._copy_to_output(build_dir) is True
        assert (ex.output_path / "app-debug.apk").read_bytes() == b"APK"

    def test_neither_present_returns_false(self, _qapp, tmp_path):
        import export.android.android_exporter as mod
        ex = mod.AndroidExporter()
        build_dir = tmp_path / "build"
        (build_dir / "bin").mkdir(parents=True)
        ex.output_path = tmp_path / "out"
        assert ex._copy_to_output(build_dir) is False


# ---------------------------------------------------------------------------
# WSLBridge — script text + keystore plumbing
# ---------------------------------------------------------------------------

class TestWslBridgeReleaseScript:
    def _bridge(self):
        from export.android.wsl_bridge import WSLBridge
        return WSLBridge.__new__(WSLBridge)

    def test_default_is_debug_backward_compatible(self):
        bridge = self._bridge()
        script = bridge._build_script_text("/mnt/c/tmp/build", "proj")
        assert "buildozer android debug" in script
        assert "P4A_RELEASE_KEYSTORE" not in script

    def test_release_without_keystore_still_debug_shaped_env(self):
        """No keystore info supplied -- proceeds without exporting any
        signing env vars (an unsigned/default-signed release, matching
        buildozer's own behavior for a caller that didn't ask for signing)."""
        bridge = self._bridge()
        script = bridge._build_script_text(
            "/mnt/c/tmp/build", "proj", build_type="release")
        assert "buildozer android release" in script
        assert "P4A_RELEASE_KEYSTORE" not in script

    def test_release_with_keystore_exports_env_vars(self):
        bridge = self._bridge()
        script = bridge._build_script_text(
            "/mnt/c/tmp/build", "proj", build_type="release",
            keystore_wsl_path="/mnt/c/keys/release.keystore",
            keystore_password="storepw",
            key_alias="myalias",
            key_password="keypw",
        )
        assert "export P4A_RELEASE_KEYSTORE='/mnt/c/keys/release.keystore'" in script
        assert "export P4A_RELEASE_KEYSTORE_PASSWD='storepw'" in script
        assert "export P4A_RELEASE_KEYALIAS='myalias'" in script
        assert "export P4A_RELEASE_KEYALIAS_PASSWD='keypw'" in script
        assert "buildozer android release" in script
        # env exports must appear BEFORE the buildozer invocation
        assert script.index("P4A_RELEASE_KEYSTORE=") < script.index("buildozer android release")

    def test_password_with_single_quote_is_safely_escaped(self):
        """A keystore password containing a single quote must not break out
        of the generated bash single-quoted string (shell-injection safety
        for a generated script)."""
        bridge = self._bridge()
        script = bridge._build_script_text(
            "/mnt/c/tmp/build", "proj", build_type="release",
            keystore_wsl_path="/mnt/c/keys/release.keystore",
            keystore_password="it's-a-secret",
            key_alias="myalias",
            key_password="keypw",
        )
        assert "export P4A_RELEASE_KEYSTORE_PASSWD='it'\\''s-a-secret'" in script

    def test_aab_is_copied_back_alongside_apk(self):
        bridge = self._bridge()
        script = bridge._build_script_text("/mnt/c/tmp/build", "proj")
        assert 'cp "$BUILD_DIR"/bin/*.apk "{src}/bin/"'.format(src="/mnt/c/tmp/build") in script
        assert 'cp "$BUILD_DIR"/bin/*.aab "{src}/bin/"'.format(src="/mnt/c/tmp/build") in script

    def test_bash_single_quote_helper(self):
        from export.android.wsl_bridge import WSLBridge
        assert WSLBridge._bash_single_quote("plain") == "'plain'"
        assert WSLBridge._bash_single_quote("it's") == "'it'\\''s'"

    def test_run_buildozer_translates_windows_keystore_path(self, monkeypatch):
        from export.android.wsl_bridge import WSLBridge
        bridge = self._bridge()

        calls = {"windows_to_wsl_path": []}

        def _fake_translate(self_, path):
            calls["windows_to_wsl_path"].append(path)
            if path == r"C:\keys\release.keystore":
                return "/mnt/c/keys/release.keystore"
            return "/mnt/c/tmp/build"

        monkeypatch.setattr(WSLBridge, "windows_to_wsl_path", _fake_translate)

        captured = {}

        def _fake_run(cmd, **kwargs):
            class _R:
                returncode = 0
                stdout = "/tmp/pygm_buildozer_run.abc.sh\n"
                stderr = ""
            if cmd[:2] == ["wsl", "mktemp"]:
                return _R()
            captured.setdefault("cmds", []).append(cmd)
            class _R2:
                returncode = 0
                stdout = ""
                stderr = b""
            return _R2()

        import export.android.wsl_bridge as wsl_mod
        monkeypatch.setattr(wsl_mod.subprocess, "run", _fake_run)

        class _FakePopen:
            def __init__(self, *a, **k):
                captured["popen_cmd"] = a[0] if a else k.get("args")

        monkeypatch.setattr(wsl_mod.subprocess, "Popen", _FakePopen)

        bridge.run_buildozer(
            r"C:\tmp\build", project_name="proj",
            build_type="release",
            keystore_path=r"C:\keys\release.keystore",
            keystore_password="storepw",
            key_alias="myalias",
            key_password="keypw",
        )

        assert r"C:\keys\release.keystore" in calls["windows_to_wsl_path"]
