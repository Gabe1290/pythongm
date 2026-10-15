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
at the call site with ``self.tr(label)``.

``available`` used to be purely advisory -- the dialog let the student
select an unavailable target anyway, relying on the exporter's own error
message to explain what's missing (e.g. the Android WSL setup
instructions). Changed 2026-10-15 (user-reported, after the
``_frozen_build_refusal`` fix landed): a target that's unavailable
because the running IDE is itself a PACKAGED build (``sys.frozen``) has
no in-dialog follow-up action at all -- unlike "install WSL" or "run on
Windows", "restart as a different build of the app" isn't something a
click in this dialog can lead to, so leaving it selectable just let the
student discover the same dead end one extra, slower step later. The
dialog now disables (greys out) any radio whose probe returns
``available=False``; the still-visible label is the explanation (e.g.
"⚠️ Requires WSL (not detected)"), unchanged from before.

Adding/removing an export target is now a one-entry change here (plus
the runner method). If a real extension/plugin system lands post-1.0
(see docs/POST_1_0_REFACTOR.md), this registry is the seam it fills.
"""
import platform
import sys
from dataclasses import dataclass
from typing import Callable, Tuple


def _is_frozen() -> bool:
    """True inside a packaged/frozen build of the IDE (PyInstaller sets
    this). Windows exe / Linux / macOS / native-Android / iOS exports all
    shell out to a separate Python-based tool (PyInstaller, buildozer,
    kivy-ios) via ``sys.executable`` -- which, when frozen, IS the
    PyGameMaker binary itself, not a real Python. None of them can work
    from a packaged build; see export/desktop/pygame_desktop_exporter.py's
    ``_frozen_build_refusal`` for the fix this mirrors. Android-via-WSL is
    the one exception (the WSL bridge never touches the host's own
    ``sys.executable``).

    A function, not a module-level constant computed once at import time:
    the regression tests monkeypatch ``sys.frozen`` per-test the same way
    ``test_desktop_export_frozen_refusal.py`` already does, which a
    precomputed constant evaluated before the patch would never see."""
    return getattr(sys, 'frozen', False)


#: Shared wording for every target this blocks -- deliberately distinct from
#: the host-platform-mismatch messages ("Requires Windows"), since running
#: on the wrong OS and running a packaged build need different fixes.
_FROZEN_SUFFIX = " - ⚠️ Run PyGameMaker from its Python source code (not this packaged app)"


@dataclass(frozen=True)
class ExportTarget:
    id: str                                   # stable, locale-independent
    runner: str                               # PyGameMakerIDE method name
    probe: Callable[[], Tuple[bool, str]]     # (available, display label)


def _html5_probe() -> Tuple[bool, str]:
    return True, "HTML5 (Web Browser) - ✅ Available"


def _windows_probe() -> Tuple[bool, str]:
    if _is_frozen():
        return False, "Windows Executable (.exe)" + _FROZEN_SUFFIX
    if platform.system() == 'Windows':
        return True, "Windows Executable (.exe) - ✅ Available"
    return False, "Windows Executable (.exe) - ⚠️ Requires Windows"


def _linux_probe() -> Tuple[bool, str]:
    if _is_frozen():
        return False, "Linux Binary" + _FROZEN_SUFFIX
    if platform.system() == 'Linux':
        return True, "Linux Binary - ✅ Available"
    return False, "Linux Binary - ⚠️ Requires Linux"


def _macos_probe() -> Tuple[bool, str]:
    if _is_frozen():
        return False, "macOS Application (.app)" + _FROZEN_SUFFIX
    if platform.system() == 'Darwin':
        return True, "macOS Application (.app) - ✅ Available"
    return False, "macOS Application (.app) - ⚠️ Requires macOS"


def _android_probe() -> Tuple[bool, str]:
    system = platform.system()
    if system == 'Windows':
        # Buildozer can't run natively on Windows; WSL is the bridge, and
        # the WSL bridge never touches the host's own sys.executable, so
        # it works the same whether this IDE build is frozen or not.
        try:
            from export.android.wsl_bridge import WSLBridge
            if WSLBridge().is_wsl_available():
                return True, "Android Package (.apk) - ✅ Available (via WSL)"
        except Exception:
            pass
        return False, "Android Package (.apk) - ⚠️ Requires WSL (not detected)"
    if _is_frozen():
        return False, "Android Package (.apk)" + _FROZEN_SUFFIX
    if system in ('Linux', 'Darwin'):
        return True, "Android Package (.apk) - ✅ Available"
    return False, "Android Package (.apk) - ⚠️ Requires Linux or macOS"


def _ios_probe() -> Tuple[bool, str]:
    if _is_frozen():
        return False, "iOS App (.ipa)" + _FROZEN_SUFFIX
    if platform.system() == 'Darwin':
        return True, "iOS App (.ipa) - ✅ Available (macOS only)"
    return False, "iOS App (.ipa) - ⚠️ Requires macOS with Xcode"


def _kivy_project_probe() -> Tuple[bool, str]:
    return True, "Kivy Source Project - ✅ Available"


def _source_zip_probe() -> Tuple[bool, str]:
    return True, "Project Source (.zip) - ✅ Available"


def desktop_exporter_for_host(host_os):
    """Return the PyInstaller-based exporter class that builds a native
    desktop artifact for ``host_os`` (a ``platform.system()`` value): a
    Windows ``.exe``, a macOS ``.app``, or a Linux ELF binary.

    PyInstaller cannot cross-compile — it always builds for the platform
    it runs on — so the host OS determines the artifact. Anything that
    isn't macOS or Windows (Linux and other Unixes) gets the Linux
    exporter rather than failing on the Windows one (the off-platform
    failure users hit pre-fix; regression-pinned since the 2026-06-26
    report). Moved here from dialogs/project_dialogs.py when the two
    export dialogs were consolidated.
    """
    if host_os == 'Darwin':
        from export.macos import MacOSExporter
        return MacOSExporter
    if host_os == 'Windows':
        from export.exe import ExeExporter
        return ExeExporter
    from export.linux import LinuxExporter
    return LinuxExporter


# Dialog order. html5 stays first (and pre-selected): it is the one
# target available on every host. kivy_project and source_zip came from
# the retired File → Export Project dialog (ExportProjectDialog): the
# raw Kivy/buildozer project (its "Mobile (Kivy)"/"Mobile (APK)" entries
# — neither built an APK; export_android_apk does) and the project
# source zip.
EXPORT_TARGETS = (
    ExportTarget("html5", "export_html5", _html5_probe),
    ExportTarget("windows_exe", "export_windows_exe", _windows_probe),
    ExportTarget("linux", "export_linux_binary", _linux_probe),
    ExportTarget("macos", "export_macos_app", _macos_probe),
    ExportTarget("android_apk", "export_android_apk", _android_probe),
    ExportTarget("ios", "export_ios_app", _ios_probe),
    ExportTarget("kivy_project", "export_kivy", _kivy_project_probe),
    ExportTarget("source_zip", "export_project_zip", _source_zip_probe),
)
