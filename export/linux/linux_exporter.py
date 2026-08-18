#!/usr/bin/env python3
"""Linux binary export: freezes the real pygame engine with PyInstaller.

Previously this bundled the Kivy code generator -- a second, incomplete engine
-- so the exported binary was not the game the author had tested. See
export/desktop/pygame_desktop_exporter.py for the full reasoning.

Linux matters more than the download count suggests: most of the school
computer labs this software targets run Debian, so this is the export those
students actually get.

Almost nothing here is Linux-specific. What is: PyInstaller writes the output
without the executable bit set when the destination filesystem loses it (a
FAT/exFAT USB stick, the usual way a binary travels between lab machines), so
the copy restores it -- a binary a student cannot launch is indistinguishable
from a broken export.
"""

from pathlib import Path

from core.logger import get_logger
from export.desktop.pygame_desktop_exporter import BasePygameDesktopExporter

logger = get_logger(__name__)


class LinuxExporter(BasePygameDesktopExporter):
    """Export the project as a standalone Linux binary."""

    platform_label = "Linux exporter"
    build_tag = "linux"
    executable_suffix = ""
    required_host_platform = "Linux"
    required_host_hint = (
        "To create a Linux binary, run this export on a Linux machine.\n\n")

    def _copy_to_output(self, build_dir: Path) -> bool:
        copied = super()._copy_to_output(build_dir)
        if copied:
            self._restore_executable_bit()
        return copied

    def _restore_executable_bit(self) -> None:
        """Make sure the delivered binary can actually be run.

        shutil.copy2 preserves mode, but only if the destination filesystem
        stores one; copying onto a FAT-formatted USB stick silently drops it.
        """
        name = self.app_name() + self.executable_suffix
        target = self.output_path / name
        if not target.is_file():
            return
        try:
            mode = target.stat().st_mode
            target.chmod(mode | 0o111)
        except OSError as exc:
            logger.warning("Could not mark %s executable: %s", target, exc)
