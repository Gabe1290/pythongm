#!/usr/bin/env python3
"""macOS .app export: freezes the real pygame engine with PyInstaller.

Previously this bundled the Kivy code generator -- a second, incomplete engine
-- so the exported .app was not the game the author had tested. See
export/desktop/pygame_desktop_exporter.py for the full reasoning.

macOS carries more genuinely platform-specific baggage than the other two
targets, all of it kept from the Kivy-era exporter because each piece fixes a
real way an .app fails to open:

* a .app is a *directory*, so this target builds onedir + BUNDLE() rather than
  the single-file binary Windows and Linux get;
* Gatekeeper silently kills an unsigned .app that carries the
  com.apple.quarantine attribute, so it is stripped after the copy;
* copying a .app onto a filesystem with no symlink support (an exFAT USB
  stick, how these travel round a lab) fails outright, so there is a fallback
  that resolves symlinks into real files.
"""

import shutil
import subprocess
from pathlib import Path
from typing import Optional

from core.logger import get_logger
from export.desktop.pygame_desktop_exporter import (
    BasePygameDesktopExporter, _literal)

logger = get_logger(__name__)


class MacOSExporter(BasePygameDesktopExporter):
    """Export the project as a macOS .app bundle."""

    platform_label = "macOS exporter"
    build_tag = "macos"
    executable_suffix = ""
    required_host_platform = "Darwin"
    required_host_hint = (
        "To create a macOS .app, run this export on a Mac.\n\n")
    bundle_style = "onedir"

    # --- spec ------------------------------------------------------------
    def _spec_trailer(self, app_name: str) -> str:
        """Wrap the COLLECT in a real .app bundle."""
        settings = self.export_settings or {}

        icon = settings.get("icon_path")
        icon_literal = _literal(icon) if icon else "None"
        # repr() so an apostrophe in the display name survives into
        # CFBundleDisplayName (M38, the "L'aventure" case).
        display_name = repr(str(self.project_data.get("name", "Game")))
        # repr() for the same reason -- was hardcoded '1.0.0' regardless of
        # the project's own version, so every exported .app claimed to be
        # version 1.0.0 forever. CFBundleVersion (the internal build
        # string, can be any format) and CFBundleShortVersionString (the
        # user-visible version, e.g. shown in Finder's Get Info) both take
        # the project's version string directly -- unlike Windows'
        # VSVersionInfo, macOS does not require a numeric tuple.
        version_literal = repr(str(self.project_data.get("version") or "1.0.0"))

        return f'''
app = BUNDLE(
    coll,
    name={app_name + '.app'!r},
    icon={icon_literal},
    bundle_identifier={'com.pygamemaker.' + app_name.lower()!r},
    info_plist={{
        'CFBundleName': {app_name!r},
        'CFBundleDisplayName': {display_name},
        'CFBundleVersion': {version_literal},
        'CFBundleShortVersionString': {version_literal},
        # False on purpose: the engine renders to a fixed-size pygame surface,
        # so claiming Retina support would shrink the window to half its
        # authored size in points rather than sharpen it.
        'NSHighResolutionCapable': False,
        'NSRequiresAquaSystemAppearance': False,
    }},
)
'''

    # --- packaging -------------------------------------------------------
    def _copy_to_output(self, build_dir: Path) -> bool:
        """Copy the .app bundle out, then make it launchable.

        Overridden rather than extended because a .app needs symlinks
        preserved (they are part of the bundle layout) and the base's per-file
        retry loop does not apply to a directory copy.
        """
        dist_dir = build_dir / "dist"
        self.output_path.mkdir(parents=True, exist_ok=True)

        if not dist_dir.exists():
            logger.error("PyInstaller produced no dist/ directory")
            return False

        all_copied = True
        for item in dist_dir.iterdir():
            dest = self.output_path / item.name
            try:
                if item.is_dir():
                    if dest.exists():
                        shutil.rmtree(dest)
                    try:
                        # Symlinks first: they are part of the .app layout.
                        shutil.copytree(item, dest, symlinks=True)
                    except (shutil.Error, OSError):
                        logger.info("Destination does not support symlinks, "
                                    "resolving them to copies")
                        if dest.exists():
                            shutil.rmtree(dest)
                        self._copytree_resolve_symlinks(item, dest)
                else:
                    shutil.copy2(item, dest)
            except OSError as exc:
                logger.warning("Could not copy %s: %s", item.name, exc)
                logger.info("Build kept at: %s", item)
                all_copied = False

        if all_copied:
            self._strip_quarantine(self.output_path)
        return all_copied

    def _copytree_resolve_symlinks(self, src: Path, dst: Path) -> None:
        """Copy a tree, resolving symlinks to real files/directories.

        Unlike shutil.copytree(symlinks=False), this handles a symlink that
        points at a directory by copying the resolved contents rather than
        failing with EISDIR.
        """
        dst.mkdir(parents=True, exist_ok=True)
        for item in src.iterdir():
            target_path = dst / item.name
            try:
                if item.is_symlink():
                    resolved = item.resolve()
                    if not resolved.exists():
                        continue  # dangling symlink
                    if resolved.is_dir():
                        if not target_path.exists():
                            self._copytree_resolve_symlinks(resolved, target_path)
                    else:
                        shutil.copy2(resolved, target_path)
                elif item.is_dir():
                    self._copytree_resolve_symlinks(item, target_path)
                else:
                    shutil.copy2(item, target_path)
            except OSError as exc:
                logger.debug("Skipped %s: %s", item.name, exc)

    def _strip_quarantine(self, output_dir: Path) -> None:
        """Remove com.apple.quarantine from the built bundle.

        Gatekeeper silently kills a quarantined unsigned .app on
        double-click -- no error, nothing happens at all, which reads to a
        teacher as "the export is broken".
        """
        for item in output_dir.iterdir():
            if item.suffix != ".app" and not item.is_dir():
                continue
            try:
                subprocess.run(["xattr", "-cr", str(item)],
                               capture_output=True, timeout=30)
                logger.info("Stripped quarantine from %s", item.name)
            except (FileNotFoundError, subprocess.TimeoutExpired):
                logger.warning("Could not strip quarantine from %s", item.name)

    # --- diagnostics -----------------------------------------------------
    def _check_xcode_tools(self) -> bool:
        """Xcode Command Line Tools provide lipo/codesign.

        Not required to build, so this stays a diagnostic rather than a gate.
        """
        try:
            result = subprocess.run(["xcode-select", "-p"],
                                    capture_output=True, text=True, timeout=10)
            return result.returncode == 0
        except (FileNotFoundError, subprocess.TimeoutExpired):
            return False
