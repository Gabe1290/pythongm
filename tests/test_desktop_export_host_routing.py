"""Regression test: the Export dialog's "Desktop Executable (.exe/.app)"
target must build for the host OS, not always attempt a Windows .exe.

User-reported (2026-06-26): on macOS the export failed with "cannot create
a Windows .exe", and on Linux a Linux executable couldn't be produced —
because ExportProjectDialog._export_executable hardcoded the Windows-only
ExeExporter for every host. PyInstaller can't cross-compile, so the single
desktop target must route to the exporter matching the running OS:

    Windows -> ExeExporter      (.exe)
    Darwin  -> MacOSExporter    (.app)
    Linux   -> LinuxExporter    (ELF binary)

(The separate Windows complaint — "Kivy needs to be installed" — is not a
bug: all three desktop exporters bundle a Kivy runtime via PyInstaller, so
Kivy is a genuine build dependency and the message already tells the user
to `pip install kivy`.)

The selection now lives in the module-level helper _desktop_exporter_for_host
so it is unit-testable without standing up the Qt dialog or running
PyInstaller.
"""

import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).parent.parent))

from conftest import skip_without_pyside6

pytestmark = skip_without_pyside6


@pytest.mark.parametrize("host_os,expected", [
    ("Windows", "ExeExporter"),
    ("Darwin", "MacOSExporter"),
    ("Linux", "LinuxExporter"),
    # Any other Unix falls back to the Linux (ELF) exporter rather than
    # the Windows one — the off-platform failure the user hit.
    ("FreeBSD", "LinuxExporter"),
])
def test_desktop_exporter_matches_host(host_os, expected):
    from dialogs.project_dialogs import _desktop_exporter_for_host
    assert _desktop_exporter_for_host(host_os).__name__ == expected


def test_non_windows_hosts_never_get_the_windows_exporter():
    from dialogs.project_dialogs import _desktop_exporter_for_host
    for host_os in ("Darwin", "Linux", "FreeBSD"):
        assert _desktop_exporter_for_host(host_os).__name__ != "ExeExporter", (
            f"{host_os} must not route to the Windows-only ExeExporter"
        )
