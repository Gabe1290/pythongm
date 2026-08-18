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

    # --- signing (docs/EXPORT_POLISH_PLAN.md item 2b) ---------------------
    def _sign_build(self, build_dir: Path) -> Optional[str]:
        """codesign the .app, and optionally notarize + staple it.

        Distribution outside the Mac App Store needs a real Apple
        Developer Program membership and Developer ID certificate this
        repo cannot supply or test with -- see EXPORT_POLISH_PLAN.md's own
        reasoning. This wires the mechanism only: when 'signing_identity'
        is absent (the default), nothing changes and the .app ships
        unsigned exactly as before (still launchable locally thanks to
        the existing quarantine-stripping in _copy_to_output).
        """
        settings = self.export_settings or {}
        identity = settings.get("signing_identity")
        if not identity:
            return None

        app_path = self.output_path / (self.app_name() + ".app")
        if not app_path.exists():
            return f"Could not find the built .app to sign: {app_path}"

        codesign = shutil.which("codesign")
        if not codesign:
            return (
                "codesign was not found. It ships with Xcode Command Line "
                "Tools -- install them with `xcode-select --install` and "
                "export again.")

        cmd = [codesign, "--deep", "--force", "--options", "runtime",
               "--sign", str(identity), str(app_path)]
        try:
            result = subprocess.run(
                cmd, capture_output=True, text=True, timeout=180)
        except subprocess.TimeoutExpired:
            return "codesign timed out after 180 seconds."
        except Exception as exc:  # noqa: BLE001
            return f"Could not run codesign: {exc}"

        if result.returncode != 0:
            return (f"codesign exited with code {result.returncode}:\n"
                    f"{result.stdout}\n{result.stderr}")

        logger.info("Signed %s with identity %r", app_path.name, identity)

        if settings.get("notarize"):
            return self._notarize_and_staple(app_path, settings)
        return None

    def _notarize_and_staple(self, app_path: Path, settings: dict) -> Optional[str]:
        """Submit the signed .app to Apple's notary service and staple the
        resulting ticket. Needs an app-specific password, not the real
        Apple ID password -- see support.apple.com/en-us/102654."""
        apple_id = settings.get("apple_id")
        apple_password = settings.get("apple_id_password")
        team_id = settings.get("apple_team_id")
        if not all([apple_id, apple_password, team_id]):
            return (
                "Notarization was requested but 'apple_id', "
                "'apple_id_password' (an app-specific password -- not "
                "your real Apple ID password) and 'apple_team_id' must "
                "all be provided.")

        xcrun = shutil.which("xcrun")
        if not xcrun:
            return "xcrun was not found (requires Xcode Command Line Tools)."

        import tempfile
        zip_path = Path(tempfile.mkdtemp()) / f"{app_path.stem}.zip"
        try:
            subprocess.run(
                ["ditto", "-c", "-k", "--keepParent", str(app_path), str(zip_path)],
                capture_output=True, text=True, timeout=120, check=True)
        except Exception as exc:  # noqa: BLE001
            return f"Could not prepare the .app for notarization: {exc}"

        submit_cmd = [
            xcrun, "notarytool", "submit", str(zip_path), "--wait",
            "--apple-id", str(apple_id),
            "--password", str(apple_password),
            "--team-id", str(team_id),
        ]
        try:
            result = subprocess.run(
                submit_cmd, capture_output=True, text=True, timeout=1800)
        except subprocess.TimeoutExpired:
            return "Notarization timed out after 30 minutes."
        except Exception as exc:  # noqa: BLE001
            return f"Could not run notarytool: {exc}"

        if result.returncode != 0:
            return (f"Notarization failed (exit {result.returncode}):\n"
                    f"{result.stdout}\n{result.stderr}")

        staple_cmd = [xcrun, "stapler", "staple", str(app_path)]
        try:
            staple_result = subprocess.run(
                staple_cmd, capture_output=True, text=True, timeout=120)
        except Exception as exc:  # noqa: BLE001
            return f"Notarization succeeded but stapling failed: {exc}"

        if staple_result.returncode != 0:
            return (f"Notarization succeeded but stapling failed "
                    f"(exit {staple_result.returncode}):\n"
                    f"{staple_result.stdout}\n{staple_result.stderr}")

        logger.info("Notarized and stapled %s", app_path.name)
        return None

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
