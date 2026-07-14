"""Android/WSL export: persistent build directory + sane timeouts.

The original WSL bridge ran buildozer in a fresh ``mktemp -d`` directory on
every export, so the python-for-android compile (40+ minutes) restarted from
zero on each retry — and the exporter's 40-minute timeout then killed every
healthy first build mid-compile, making the WSL Android export impossible to
complete on slower machines ("the export ran but there is no .apk").

These tests pin the fix: the build script uses a persistent per-project
directory (~/.pygm/android_builds/<key>) that keeps the .buildozer/.gradle
caches while refreshing game/ + bin/, and the timeouts are hang-failsafes
far above a legitimate first-build duration.
"""
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT))

from export.android import android_exporter  # noqa: E402
from export.android.wsl_bridge import WSLBridge  # noqa: E402


def _script(project_key="match3game"):
    return WSLBridge._build_script_text(
        WSLBridge.__new__(WSLBridge), "/mnt/c/tmp/build", project_key)


def test_build_dir_is_persistent_per_project():
    script = _script("match3game")
    assert 'BUILD_DIR="$HOME/pygm_builds/match3game"' in script
    assert "mktemp -d" not in script


def test_build_dir_has_no_hidden_path_component():
    """buildozer's _copy_application_sources skips any walk root whose
    ABSOLUTE path contains a dot-prefixed component — a build under e.g.
    ~/.pygm/ copies zero sources and p4a fails with 'No main.py found'.
    The persistent dir must therefore be dot-free below $HOME."""
    script = _script("match3game")
    line = next(l for l in script.splitlines() if l.startswith('BUILD_DIR='))
    rel = line.split('$HOME/', 1)[1].rstrip('"')
    assert not any(part.startswith('.') for part in rel.split('/')), line


def test_refreshes_sources_but_keeps_caches():
    script = _script()
    # game/ and bin/ are cleared each run...
    assert 'rm -rf "$BUILD_DIR/game" "$BUILD_DIR/bin"' in script
    # ...but nothing removes the whole dir or the p4a/gradle caches.
    assert 'rm -rf "$BUILD_DIR"\n' not in script
    assert 'rm -rf "$BUILD_DIR/.buildozer"' not in script
    assert 'rm -rf "$BUILD_DIR/.gradle"' not in script
    assert 'cp -r "/mnt/c/tmp/build"/* "$BUILD_DIR"/' in script


def test_stale_apk_cannot_be_copied_back():
    """bin/ is cleared before the build, so the post-build copy can only
    return an APK this build actually produced."""
    script = _script()
    clear = script.index('rm -rf "$BUILD_DIR/game" "$BUILD_DIR/bin"')
    copy_back = script.index('cp "$BUILD_DIR"/bin/*.apk')
    assert clear < copy_back


def test_run_script_self_deletes_on_any_exit():
    """KA-L3: `set -e` aborted before the old trailing `rm -f "$0"`, so a
    failed build leaked the run script in /tmp. An EXIT trap deletes it on
    every path (success, failure, set -e abort)."""
    script = _script()
    assert 'trap \'rm -f "$0"\' EXIT' in script
    # the old success-only trailing delete must be gone
    lines = [l.strip() for l in script.splitlines()]
    assert 'rm -f "$0"' not in lines  # only inside the trap now


def test_buildozer_exit_code_captured_without_set_e_abort():
    """The buildozer exit must be captured via && / || so `set -e` doesn't
    abort before the APK copy-back and the real code propagates (KA-L3)."""
    script = _script()
    assert 'buildozer android debug && EXIT_CODE=0 || EXIT_CODE=$?' in script
    # copy-back still runs after buildozer, exit code propagates
    assert script.index('EXIT_CODE=0 || EXIT_CODE=$?') < script.index('cp "$BUILD_DIR"/bin/*.apk')
    assert script.rstrip().endswith('exit $EXIT_CODE')


def test_project_key_sanitized():
    key = WSLBridge._project_build_key
    assert key("Match3Game") == "match3game"
    assert key("Mon Jeu (été)!") == "mon_jeu_t"
    assert key("../../etc") == "etc"
    assert key("") == "project"
    assert key(None) == "project"


def test_timeouts_are_hang_failsafes_not_build_estimates():
    """A first python-for-android compile takes 40-90+ min; the old
    20/40-minute values guaranteed failure on slower machines."""
    assert android_exporter.BUILDOZER_TIMEOUT_NATIVE >= 3600
    assert android_exporter.BUILDOZER_TIMEOUT_WSL >= 7200
