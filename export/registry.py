#!/usr/bin/env python3
"""Export-target registry — the single source of truth for the Build →
Export Game dialog.

Each target carries:

- a stable, locale-independent ``id`` (dispatching on translated display
  text silently broke non-English exports once — audit M13);
- ``runner``: the name of the PyGameMakerIDE method that runs the export
  (the thin shells around _run_export_with_progress);
- ``probe()``: an availability check returning ``(available, label)``.

The labels are preserved BYTE-FOR-BYTE from the strings the dialog has
always shown, so the existing .ts translations keep matching; translate
at the call site with ``self.tr(label)``. ``available`` is advisory —
the dialog historically allows selecting unavailable targets so their
exporters can explain what's missing (e.g. the Android WSL setup
instructions), and that behaviour is kept.

Adding/removing an export target is now a one-entry change here (plus
the runner method). If a real extension/plugin system lands post-1.0
(see docs/POST_1_0_REFACTOR.md), this registry is the seam it fills.
"""
import platform
from dataclasses import dataclass
from typing import Callable, Tuple


@dataclass(frozen=True)
class ExportTarget:
    id: str                                   # stable, locale-independent
    runner: str                               # PyGameMakerIDE method name
    probe: Callable[[], Tuple[bool, str]]     # (available, display label)


def _html5_probe() -> Tuple[bool, str]:
    return True, "HTML5 (Web Browser) - ✅ Available"


def _windows_probe() -> Tuple[bool, str]:
    if platform.system() == 'Windows':
        return True, "Windows Executable (.exe) - ✅ Available"
    return False, "Windows Executable (.exe) - ⚠️ Requires Windows"


def _linux_probe() -> Tuple[bool, str]:
    if platform.system() == 'Linux':
        return True, "Linux Binary - ✅ Available"
    return False, "Linux Binary - ⚠️ Requires Linux"


def _macos_probe() -> Tuple[bool, str]:
    if platform.system() == 'Darwin':
        return True, "macOS Application (.app) - ✅ Available"
    return False, "macOS Application (.app) - ⚠️ Requires macOS"


def _android_probe() -> Tuple[bool, str]:
    system = platform.system()
    if system in ('Linux', 'Darwin'):
        return True, "Android Package (.apk) - ✅ Available"
    if system == 'Windows':
        # Buildozer can't run natively on Windows; WSL is the bridge.
        try:
            from export.android.wsl_bridge import WSLBridge
            if WSLBridge().is_wsl_available():
                return True, "Android Package (.apk) - ✅ Available (via WSL)"
        except Exception:
            pass
        return False, "Android Package (.apk) - ⚠️ Requires WSL (not detected)"
    return False, "Android Package (.apk) - ⚠️ Requires Linux or macOS"


def _ios_probe() -> Tuple[bool, str]:
    if platform.system() == 'Darwin':
        return True, "iOS App (.ipa) - ✅ Available (macOS only)"
    return False, "iOS App (.ipa) - ⚠️ Requires macOS with Xcode"


# Dialog order. html5 stays first (and pre-selected): it is the one
# target available on every host.
EXPORT_TARGETS = (
    ExportTarget("html5", "export_html5", _html5_probe),
    ExportTarget("windows_exe", "export_windows_exe", _windows_probe),
    ExportTarget("linux", "export_linux_binary", _linux_probe),
    ExportTarget("macos", "export_macos_app", _macos_probe),
    ExportTarget("android_apk", "export_android_apk", _android_probe),
    ExportTarget("ios", "export_ios_app", _ios_probe),
)
