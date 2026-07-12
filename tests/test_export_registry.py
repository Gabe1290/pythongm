"""Export-target registry (export/registry.py).

The Build → Export Game dialog used to hardcode six radio buttons with
inline platform checks and dispatch on magic numbers; the registry is now
the single source of truth (id, runner method, availability probe). These
tests pin:

- the registry's shape and stable ids (locale-independent routing, M13),
- that every runner is a real method on PyGameMakerIDE,
- that probe labels stay BYTE-IDENTICAL to the historical dialog strings
  (they are .ts translation source keys — changing them silently reverts
  translated IDEs to English),
- that export_game actually builds from the registry.
"""
import platform
import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT))

from export.registry import EXPORT_TARGETS, ExportTarget  # noqa: E402

EXPECTED_IDS = ["html5", "windows_exe", "linux", "macos", "android_apk", "ios"]

# Every label a probe may return, exactly as the dialog always showed them.
LEGACY_LABELS = {
    "html5": {"HTML5 (Web Browser) - ✅ Available"},
    "windows_exe": {"Windows Executable (.exe) - ✅ Available",
                    "Windows Executable (.exe) - ⚠️ Requires Windows"},
    "linux": {"Linux Binary - ✅ Available",
              "Linux Binary - ⚠️ Requires Linux"},
    "macos": {"macOS Application (.app) - ✅ Available",
              "macOS Application (.app) - ⚠️ Requires macOS"},
    "android_apk": {"Android Package (.apk) - ✅ Available",
                    "Android Package (.apk) - ✅ Available (via WSL)",
                    "Android Package (.apk) - ⚠️ Requires WSL (not detected)",
                    "Android Package (.apk) - ⚠️ Requires Linux or macOS"},
    "ios": {"iOS App (.ipa) - ✅ Available (macOS only)",
            "iOS App (.ipa) - ⚠️ Requires macOS with Xcode"},
}


def test_registry_shape_and_stable_ids():
    assert [t.id for t in EXPORT_TARGETS] == EXPECTED_IDS
    assert len({t.id for t in EXPORT_TARGETS}) == len(EXPORT_TARGETS)
    assert all(isinstance(t, ExportTarget) for t in EXPORT_TARGETS)
    # html5 first: the dialog pre-selects index 0 as the one target
    # available on every host.
    assert EXPORT_TARGETS[0].id == "html5"


def test_probes_return_legacy_labels():
    for target in EXPORT_TARGETS:
        available, label = target.probe()
        assert isinstance(available, bool), target.id
        assert label in LEGACY_LABELS[target.id], (
            f"{target.id}: probe label {label!r} is not one of the "
            f"historical dialog strings — these are .ts translation keys; "
            f"changing them reverts translated IDEs to English")


def test_probes_match_this_platform():
    system = platform.system()
    by_id = {t.id: t.probe() for t in EXPORT_TARGETS}
    assert by_id["html5"][0] is True
    assert by_id["windows_exe"][0] is (system == "Windows")
    assert by_id["linux"][0] is (system == "Linux")
    assert by_id["macos"][0] is (system == "Darwin")
    assert by_id["ios"][0] is (system == "Darwin")
    # android depends on WSL when on Windows — just require a coherent tuple
    assert isinstance(by_id["android_apk"][0], bool)


def test_runners_are_ide_methods():
    pytest.importorskip("PySide6")
    from core.ide_window import PyGameMakerIDE
    for target in EXPORT_TARGETS:
        assert callable(getattr(PyGameMakerIDE, target.runner, None)), (
            f"{target.id}: runner {target.runner!r} is not a "
            f"PyGameMakerIDE method")


def test_export_game_builds_from_registry():
    src = (REPO_ROOT / "core" / "ide_window.py").read_text(encoding="utf-8")
    assert "from export.registry import EXPORT_TARGETS" in src
    assert "EXPORT_TARGETS[index].runner" in src
    # The hardcoded per-target radios are gone from the dialog builder —
    # their label literals now live only in the registry.
    assert "HTML5 (Web Browser)" not in src
    assert "Android Package (.apk)" not in src
