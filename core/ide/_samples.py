#!/usr/bin/env python3
"""Bundled-samples handling for :class:`PyGameMakerIDE`.

Extracted verbatim from ``core/ide_window.py`` (``docs/POST_1_0_REFACTOR.md``
File 2, first cluster). A mixin -- ``self`` / ``self.tr()`` / siblings
(``update_status`` …) resolve on the concrete window. No test patches
``core.ide_window.{QMessageBox,Config,logger}`` while exercising any of
these four methods, so nothing here needs a repointed patch target.
"""

from pathlib import Path

from PySide6.QtWidgets import QMessageBox

from utils.config import Config
from core.logger import get_logger

logger = get_logger(__name__)


class SamplesMixin:

    def _samples_dir(self) -> Path:
        """Return the repo-bundled samples/ directory (resolved)."""
        return (Path(__file__).resolve().parents[2] / 'samples').resolve()

    def _is_samples_path(self, path: Path) -> bool:
        """True if ``path`` is the bundled samples/ folder or a child of it."""
        try:
            return path.resolve().is_relative_to(self._samples_dir())
        except (ValueError, OSError):
            return False

    def _promote_samples_to_working_copy(self, samples_path: Path):
        """Copy a bundled-samples project to a fresh folder under the
        user's Documents and return the new path.

        Returns the destination Path on success, None on failure (the
        user sees a QMessageBox.warning in that case). Mirrors the
        destination-picking logic in WelcomeTab._on_open_sample (same
        ``<name>_2`` / ``_3`` suffix dance) so clicking a sample twice
        from any entry point produces independent copies.
        """
        import shutil
        from utils import documents_dir

        default_parent = documents_dir() / "PyGameMaker Projects"
        try:
            default_parent.mkdir(parents=True, exist_ok=True)
        except OSError:
            default_parent = Path.home()

        base_name = samples_path.name
        dest = default_parent / base_name
        suffix = 2
        while dest.exists():
            dest = default_parent / f"{base_name}_{suffix}"
            suffix += 1

        try:
            shutil.copytree(str(samples_path), str(dest))
        except Exception as exc:
            logger.error(f"Sample copy failed: {exc}", exc_info=True)
            QMessageBox.warning(
                self,
                self.tr("Could not open sample"),
                self.tr("Failed to copy the bundled sample to:\n{0}\n\nError:\n{1}").format(
                    str(dest), str(exc)
                ),
            )
            return None

        logger.info(f"Promoted bundled sample to working copy: {samples_path} -> {dest}")
        self.update_status(
            self.tr("Sample copied to: {0}").format(str(dest))
        )
        return dest

    def _strip_samples_from_recent_projects(self) -> None:
        """One-time cleanup of pre-rc.12 in-place sample opens.

        Before commit f8a0eb7, clicking a sample ran the GMK importer in
        place under samples/, so the path got persisted into the user's
        recent_projects list. Those entries are dead: clicking them now
        promotes to a working copy (via load_project), so the original
        Recent Projects row would silently point to a different folder
        on next launch — confusing. Strip them once at startup.
        """
        recent = Config.get("recent_projects", [])
        if not recent:
            return
        cleaned = [p for p in recent if not self._is_samples_path(Path(p))]
        if len(cleaned) != len(recent):
            removed = [p for p in recent if p not in cleaned]
            logger.info(
                f"Removed {len(removed)} stale samples/ path(s) from "
                f"recent_projects: {removed}"
            )
            Config.set("recent_projects", cleaned)
