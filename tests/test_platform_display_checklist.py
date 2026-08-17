"""The hand-verification checklist must describe the software as it is.

docs/PLATFORM_DISPLAY_CHECKLIST.md tells a human what to look for on Linux,
Windows and macOS. A checklist that names a sample, a key or a window size that
no longer matches the code is worse than none: the reader either chases a
phantom regression or, more likely, learns to ignore the document.

Most of it is deliberately unautomatable -- that is the whole point of it. What
IS checkable is every concrete claim it makes, and those are pinned here.
"""
import json
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT))

CHECKLIST = REPO_ROOT / "docs" / "PLATFORM_DISPLAY_CHECKLIST.md"


def _text():
    return CHECKLIST.read_text(encoding="utf-8")


def test_the_checklist_exists():
    assert CHECKLIST.is_file()


def test_every_named_tool_and_document_exists():
    """A checklist that tells you to run a script that was renamed wastes the
    reader's time at exactly the wrong moment."""
    text = _text()
    referenced = [
        "tools/smoke_run_samples.py",
        "tools/verify_desktop_export.py",
        "scripts/generate_platform_test_pdfs.py",
        "docs/test_checklist.md",
        "docs/EYEBALL_FIXES_2026-08-16.md",
    ]
    for relative in referenced:
        assert relative in text, "%s should be referenced" % relative
        assert (REPO_ROOT / relative).exists(), (
            "the checklist points at %s, which does not exist" % relative)


def test_every_named_sample_exists():
    """The samples are named by their folder name or their display name; both
    have been renamed before (raycast -> "2.5 D"), which is how this rots."""
    text = _text()
    for sample in ("maze_1", "maze_2", "maze_3", "maze_4",
                   "plateforme_1", "plateforme_2", "plateforme_3",
                   "match3_1", "match3_2", "match3_3",
                   "views_1", "views_2",
                   "block_world_1", "block_world_2"):
        assert sample in text, "%s is not covered by the checklist" % sample
        assert (REPO_ROOT / "samples" / sample / "project.json").exists()


def test_the_25d_display_name_matches_the_welcome_tab():
    """Issue 3 renamed these. The checklist tells the reader what they should
    see, so it has to agree with what the IDE actually shows."""
    from widgets.welcome_tab import SAMPLE_PROJECTS

    text = _text()
    displayed = [label for path, label in SAMPLE_PROJECTS
                 if "raycast" in str(path)]
    assert displayed, "no raycast samples found in the Welcome tab"
    for label in displayed:
        assert label.startswith("2.5 D"), label
    assert "2.5 D — Level 1" in text
    assert "Lancer de rayons" not in text, (
        "the checklist still uses the name that was replaced")


def test_views_1_window_and_room_sizes_are_as_stated():
    """The checklist says 800x600 window over a 2400x800 room, and tells the
    reader that seeing the whole room means a regression. Those numbers have to
    be right or the instruction is misleading."""
    data = json.loads((REPO_ROOT / "samples" / "views_1" /
                       "project.json").read_text(encoding="utf-8"))
    settings = data.get("settings", {})
    assert settings.get("window_width") == 800
    assert settings.get("window_height") == 600
    room = data["assets"]["rooms"]["room0"]
    assert room.get("width") == 2400
    assert room.get("height") == 800

    text = _text()
    assert "800×600" in text and "2400×800" in text


def test_block_world_help_overlay_line_count_is_as_stated():
    """The checklist says H shows a 7-line overlay. If a line is added or
    removed the reader would count wrong and report a phantom bug."""
    events = json.loads((REPO_ROOT / "samples" / "block_world_1" / "objects" /
                         "obj_person.json").read_text(encoding="utf-8"))
    lines = json.dumps(events).count('"draw_text"')
    assert lines == 7, "the overlay now has %d lines, not 7" % lines
    assert "7-line" in _text()


def test_the_language_list_length_is_as_stated():
    """Adding a language without updating the count would make the reader
    report a defect that is really a feature."""
    from core.language_manager import get_language_manager

    codes = get_language_manager()._discover_languages()
    assert len(codes) == 11, (
        "the checklist says 11 language entries, discovery found %d: %s"
        % (len(codes), codes))
    assert "**11**" in _text()


def test_the_frozen_launcher_diagnostics_named_are_the_real_ones():
    """The checklist tells the reader to look for game_error.log and
    highscores.json next to the executable. Those filenames come from the
    generated launcher, so they must match it."""
    from export.desktop import pygame_desktop_exporter as exporter

    launcher = exporter.LAUNCHER_TEMPLATE
    assert "game_error.log" in launcher
    assert "highscores.json" in launcher

    text = _text()
    assert "game_error.log" in text
    assert "highscores.json" in text


def test_it_covers_the_four_repaired_mobile_subsystems():
    """Mobile's four gaps were fixed on 2026-08-17, so this section changed from
    "expect it broken" to "check each repair". It must still name all four, so a
    regression is recognisable rather than a vague feeling, and it must say
    plainly that nobody has played an exported mobile build -- every fix was
    verified by executing generated code, which is not the same thing."""
    text = _text()
    lower = text.lower()
    assert "Kivy" in text
    for subsystem in ("tiles", "arrow", "collision", "jump"):
        assert subsystem in lower, subsystem
    # The specific symptoms, so the reader knows what "fixed" looked like.
    assert "falls, not rises" in lower or "falls, not rises" in text.lower()
    assert "maze_4 starts" in text
    assert "never yet played" in lower or "nobody has actually" in lower


def test_platform_columns_are_used_consistently():
    """Every check should be tickable per platform, since the reason this
    document exists is that the three platforms differ. A few items are
    deliberately single-platform (quarantine, SmartScreen, the executable
    bit)."""
    checkable = [line for line in _text().splitlines()
                 if line.strip().startswith("- ") and "[ ]" in line]
    assert len(checkable) > 40, "only %d checkable items" % len(checkable)

    all_three = [line for line in checkable
                 if "L [ ]" in line and "M [ ]" in line and "W [ ]" in line]
    # The single-platform gotchas are the minority by design.
    assert len(all_three) >= len(checkable) - 5, (
        "%d of %d items are not tickable on all three platforms"
        % (len(checkable) - len(all_three), len(checkable)))


def test_it_puts_the_automated_checks_first():
    """The reader's attention is the scarce resource: anything a script can
    check should not be done by hand. If the automated section drifts below the
    manual ones, the document has lost its shape."""
    text = _text()
    automated = text.index("verify_desktop_export.py --all")
    manual = text.index("## 1. The IDE window itself")
    assert automated < manual
