"""Export routing regression tests (audit M13 lineage).

Original finding: ExportProjectDialog routed on TRANSLATED combo text, so
'Desktop Executable' and 'Source Code (.zip)' silently no-op'd in
French/etc. The fix introduced locale-independent ids.

That dialog was retired 2026-07-12 when the two overlapping export UIs
were consolidated: File -> Export Project... and Build -> Export Game...
now both open the single registry-driven dialog, whose dispatch never
touches display text at all -- the checked radio's index selects an
ExportTarget and its `runner` method name (export/registry.py). These
tests pin the consolidated routing and that the M13 failure mode cannot
reappear.
"""
import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT))

from export.registry import EXPORT_TARGETS  # noqa: E402

from conftest import skip_without_pyside6  # noqa: E402


def test_registry_carries_the_retired_dialogs_targets():
    """The old dialog's distinct targets survived consolidation as
    registry entries (raw Kivy project + source zip)."""
    ids = [t.id for t in EXPORT_TARGETS]
    assert "kivy_project" in ids
    assert "source_zip" in ids


def test_dispatch_is_locale_independent():
    """M13's failure mode was text-based routing. The unified dialog
    dispatches index -> ExportTarget.runner; assert the dialog code never
    routes on display text."""
    src = (REPO_ROOT / "core" / "ide_window.py").read_text(encoding="utf-8")
    dialog_src = src.split("def export_game(self):", 1)[1].split(
        "\n    def ", 1)[0]
    assert "EXPORT_TARGETS[index].runner" in dialog_src
    for text_api in ("currentText", "findText"):
        assert text_api not in dialog_src, (
            f"export_game routes on display text ({text_api}) -- M13 regression")


def test_file_export_project_opens_the_unified_dialog():
    """File -> Export Project... (Ctrl+E) must open the same registry
    dialog as Build -> Export Game... -- not a second, diverging UI."""
    src = (REPO_ROOT / "core" / "ide_window.py").read_text(encoding="utf-8")
    shell = src.split("def export_project(self):", 1)[1].split(
        "\n    def ", 1)[0]
    assert "self.export_game()" in shell


def test_export_project_dialog_is_retired():
    src = (REPO_ROOT / "dialogs" / "project_dialogs.py").read_text(encoding="utf-8")
    assert "class ExportProjectDialog" not in src
    assert "class BuildProjectDialog" not in src


@skip_without_pyside6
def test_every_registry_runner_exists_including_new_targets():
    # Class-level check only: no QApplication (and no pytest-qt) needed.
    from core.ide_window import PyGameMakerIDE
    for target in EXPORT_TARGETS:
        assert callable(getattr(PyGameMakerIDE, target.runner, None)), target.id
