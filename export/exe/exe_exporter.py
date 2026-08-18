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


def _parse_version_tuple(version_str, parts: int = 4) -> tuple:
    """Best-effort parse of a project version string like "1.2.3" into a
    tuple of `parts` non-negative ints, padded with 0s. Never raises -- an
    unparsable or missing version degrades to all-zeros rather than
    failing the whole export (the .exe still gets a version RESOURCE,
    it's just 0.0.0.0, which is honest for a project that never set one)."""
    nums = []
    for piece in str(version_str or "").split("."):
        digits = "".join(ch for ch in piece if ch.isdigit())
        nums.append(int(digits) if digits else 0)
    nums = (nums + [0] * parts)[:parts]
    return tuple(nums)


def _version_info_text(app_name: str, version_str: str) -> str:
    """A PyInstaller version-info resource file (the text format its
    `EXE(version=...)` / `--version-file` option reads -- PyInstaller
    evals this file itself at build time with VSVersionInfo/FixedFileInfo/
    StringFileInfo/StringTable/StringStruct/VarFileInfo/VarStruct already
    in scope, so this module does not need to import
    PyInstaller.utils.win32.versioninfo just to generate the text).

    This is what Explorer's file Properties -> Details tab reads --
    currently nothing populates it at all, so every exported .exe shows
    blank File/Product version fields regardless of the project's own
    version."""
    ver_tuple = _parse_version_tuple(version_str, 4)
    ver_str = ".".join(str(n) for n in ver_tuple)

    def esc(s):
        return str(s).replace("\\", "\\\\").replace("'", "\\'")

    return f"""# UTF-8
VSVersionInfo(
  ffi=FixedFileInfo(
    filevers={ver_tuple!r},
    prodvers={ver_tuple!r},
    mask=0x3f,
    flags=0x0,
    OS=0x40004,
    fileType=0x1,
    subtype=0x0,
    date=(0, 0)
  ),
  kids=[
    StringFileInfo(
      [
      StringTable(
        u'040904B0',
        [StringStruct(u'FileDescription', u'{esc(app_name)}'),
        StringStruct(u'FileVersion', u'{esc(ver_str)}'),
        StringStruct(u'InternalName', u'{esc(app_name)}'),
        StringStruct(u'OriginalFilename', u'{esc(app_name)}.exe'),
        StringStruct(u'ProductName', u'{esc(app_name)}'),
        StringStruct(u'ProductVersion', u'{esc(ver_str)}')])
      ]),
    VarFileInfo([VarStruct(u'Translation', [1033, 1200])])
  ]
)
"""


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
        self._version_info_path: Optional[Path] = None

    def _write_spec(self, build_dir: Path, launcher: Path) -> Path:
        # The manifest has to exist before PyInstaller reads the spec.
        self._manifest_path = build_dir / "game.manifest"
        self._manifest_path.write_text(DPI_MANIFEST, encoding="utf-8")
        self._version_info_path = build_dir / "version_info.txt"
        self._version_info_path.write_text(
            _version_info_text(self.app_name(), self.project_data.get("version", "")),
            encoding="utf-8")
        return super()._write_spec(build_dir, launcher)

    def _spec_exe_options(self) -> str:
        options = ["manifest='game.manifest',", "version='version_info.txt',"]
        icon = (self.export_settings or {}).get("icon_path")
        if icon:
            options.append(f"icon={_literal(icon)},")
        return "\n    ".join(options)
