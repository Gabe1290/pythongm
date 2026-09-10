"""The release QA checklist must describe the software as it is.

`docs/RELEASE_QA_CHECKLIST.md` is the single hand-verification checklist for a
release sign-off. Most of it is deliberately unautomatable -- that is the whole
point of it. What IS checkable is every concrete claim it makes (a tool name, a
sample, a window size, a language count), and those are pinned here so the
document can't rot into telling a reader to chase a phantom.

(Renamed from test_platform_display_checklist.py when the split checklist set --
test_checklist.md / PLATFORM_DISPLAY_CHECKLIST.md / TESTING_CHECKLIST.md /
TESTING_PRESET_CHECKLIST.md / blockly_editor_test_checklist.md -- was
consolidated into this one document.)
"""
import json
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT))

CHECKLIST = REPO_ROOT / "docs" / "RELEASE_QA_CHECKLIST.md"


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
        "tools/smoke_room_lifecycle.py",
        "tools/smoke_run_multiplayer.py",
        "tools/verify_desktop_export.py",
        "tools/build_qa_bundle.py",
        "scripts/build_pyinstaller.py",
        "scripts/generate_release_qa_odt.py",
        "scripts/generate_checklist_pdf.py",
        "docs/EXPORT_TESTING_GUIDE.md",
        "docs/ANDROID_EXPORT.md",
        "docs/BUILDING.md",
        "docs/MULTIPLAYER_LAN_V2_PLAN.md",
        "docs/MULTIPLAYER_FILE_EXCHANGE_PLAN.md",
        "docs/FULL_AUDIT_2026-09-07.md",
    ]
    for relative in referenced:
        assert relative in text, "%s should be referenced" % relative
        assert (REPO_ROOT / relative).exists(), (
            "the checklist points at %s, which does not exist" % relative)


def test_it_does_not_point_at_the_removed_split_checklists():
    """The whole reason this file was renamed: those docs are gone. They may
    be named once in the "this replaces ..." disclaimer at the very top, but
    never in the body as a doc to go read."""
    lines = _text().splitlines()
    body = "\n".join(lines[12:])  # everything after the intro disclaimer
    for gone in ("test_checklist.md",
                 "PLATFORM_DISPLAY_CHECKLIST.md",
                 "TESTING_CHECKLIST.md",
                 "TESTING_PRESET_CHECKLIST.md",
                 "blockly_editor_test_checklist.md",
                 "generate_platform_test_pdfs.py"):
        assert gone not in body, (
            "%s is referenced in the body as if it still existed" % gone)


def test_every_named_sample_exists():
    """The samples are named by folder name or display name; both have been
    renamed before (raycast -> "2.5 D"), which is how this rots."""
    text = _text()
    for sample in ("maze_1", "maze_2", "maze_3", "maze_4",
                   "plateforme_1", "plateforme_2", "plateforme_3",
                   "match3_1", "match3_2", "match3_3",
                   "views_1", "views_2", "sky_strike_1", "treasure",
                   "raycast_1", "raycast_2", "raycast_3", "raycast_4",
                   "block_world_1", "block_world_2", "block_world_3",
                   "reseau_1", "reseau_2", "reseau_3", "reseau_4",
                   "fichier_1"):
        assert sample in text, "%s is not covered by the checklist" % sample
        assert (REPO_ROOT / "samples" / sample / "project.json").exists()


def test_views_1_window_and_room_sizes_are_as_stated():
    """The checklist says an 800x600 window over a 2400x800 room, and tells the
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
    """Mobile's four gaps were fixed on 2026-08-17. The section must still name
    all four so a regression is recognisable, and say plainly that nobody has
    played an exported mobile build -- every fix was verified by executing
    generated code, which is not the same thing."""
    text = _text()
    lower = text.lower()
    assert "Kivy" in text
    for subsystem in ("tiles", "arrow", "collision", "jump"):
        assert subsystem in lower, subsystem
    assert "falls, not rises" in lower
    assert "maze_4 starts" in text
    assert "nobody has actually played" in lower


def test_it_puts_the_automated_checks_first():
    """The reader's attention is the scarce resource: anything a script can
    check should not be done by hand. The automated pre-flight has to come
    before the manual IDE pass."""
    text = _text()
    automated = text.index("## 1. Automated pre-flight")
    manual = text.index("## 2. IDE application shell")
    assert automated < manual
    assert text.index("verify_desktop_export.py --all") < manual


def test_platform_columns_are_used_consistently():
    """Every check should be tickable per platform, since the reason this
    document exists is that the three platforms differ. A few items are
    deliberately single-platform (quarantine, SmartScreen, the executable
    bit) and a few are run-once (the automated pre-flight)."""
    checkable = [line for line in _text().splitlines()
                 if line.strip().startswith(("- L [ ]", "- [ ] L"))]
    assert len(checkable) > 80, "only %d checkable items" % len(checkable)

    per_platform = [line for line in checkable if line.strip().startswith("- L [ ]")]
    all_three = [line for line in per_platform
                 if "L [ ]" in line and "M [ ]" in line and "W [ ]" in line]
    # The single-platform gotchas are the minority by design.
    assert len(all_three) >= len(per_platform) - 12, (
        "%d of %d per-platform items are not tickable on all three"
        % (len(per_platform) - len(all_three), len(per_platform)))


def test_every_command_has_a_windows_form():
    """Bare `python3` does not work on Windows -- it hits the Microsoft Store
    stub, or an unsupported 3.14. So every tool the checklist tells you to run
    must appear in a `py -3.12` form as well as a `python3` one."""
    text = _text()
    for tool in ("-m pytest", "tools/smoke_run_samples.py",
                 "tools/verify_desktop_export.py"):
        assert "py -3.12 %s" % tool in text, (
            "%s has no `py -3.12` form; a Windows reader cannot run it" % tool)
        assert "python3 %s" % tool in text, (
            "%s has no `python3` form for Linux/macOS" % tool)


def test_it_warns_about_bare_python3_on_windows():
    """Naming the failure mode is what stops the reader assuming their install
    is broken when they see "Python was not found"."""
    text = _text()
    assert "py -3.12" in text and "python3" in text
    assert "Microsoft Store" in text, (
        "the checklist should name the stub the user actually sees")


def test_it_has_a_signoff_matrix():
    """A checklist without a place to record the result is a to-do list."""
    text = _text()
    assert "## Release sign-off" in text
    assert "Signed off for release?" in text
