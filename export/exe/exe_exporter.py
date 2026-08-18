#!/usr/bin/env python3
"""Windows .exe export: freezes the real pygame engine with PyInstaller.

This used to bundle the Kivy code generator instead, which is a second,
incomplete engine ("80% GameMaker 7.0 compatible") -- so an exported .exe was
not the game the author had just tested. That produced five separate
user-reported bugs in one pass (no tiles, jammed keyboard, no wall collision,
a floating player, sub-images stuck on frame 0). The shared pipeline in
export/desktop/pygame_desktop_exporter.py explains the change in full.

Everything platform-independent lives in the base. What is genuinely
Windows-specific: the .exe suffix, the DPI-awareness manifest, a .ico icon,
and the refusal to build anywhere but Windows.
"""

from pathlib import Path
from typing import Optional

from core.logger import get_logger
from export.desktop.pygame_desktop_exporter import (
    BasePygameDesktopExporter, _literal)

logger = get_logger(__name__)

# Without this, Windows scales the game window on a high-DPI display and the
# result is a blurry upscale of a smaller surface.
DPI_MANIFEST = '''<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<assembly xmlns="urn:schemas-microsoft-com:asm.v1" manifestVersion="1.0">
  <application xmlns="urn:schemas-microsoft-com:asm.v3">
    <windowsSettings>
      <dpiAware xmlns="http://schemas.microsoft.com/SMI/2005/WindowsSettings">true/pm</dpiAware>
      <dpiAwareness xmlns="http://schemas.microsoft.com/SMI/2016/WindowsSettings">permonitorv2,permonitor</dpiAwareness>
    </windowsSettings>
  </application>
</assembly>'''


class ExeExporter(BasePygameDesktopExporter):
    """Export the project as a standalone Windows .exe."""

    platform_label = "Windows EXE exporter"
    build_tag = "exe"
    executable_suffix = ".exe"
    required_host_platform = "Windows"
    required_host_hint = (
        "To create a Windows .exe, run this export on a Windows machine.\n\n")

    def __init__(self):
        super().__init__()
        self._manifest_path: Optional[Path] = None

    def _write_spec(self, build_dir: Path, launcher: Path) -> Path:
        # The manifest has to exist before PyInstaller reads the spec.
        self._manifest_path = build_dir / "game.manifest"
        self._manifest_path.write_text(DPI_MANIFEST, encoding="utf-8")
        return super()._write_spec(build_dir, launcher)

    def _spec_exe_options(self) -> str:
        options = ["manifest='game.manifest',"]
        icon = (self.export_settings or {}).get("icon_path")
        if icon:
            options.append(f"icon={_literal(icon)},")
        return "\n    ".join(options)
