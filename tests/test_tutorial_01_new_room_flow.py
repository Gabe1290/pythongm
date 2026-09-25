"""Tutorial 1 must teach the flow the IDE actually has: a new project already
contains `room0`, so students RENAME it to `room_game` instead of creating a
room -- and the optional width hint on handout image lines.

Why it matters: a new project's only room is `room0` and nothing writes
`room_order`, so the game starts in the first room. A student who created a
second room and placed their object there got an empty black window on F5.
The truth tests' reference projects define only `room_game`, so they could
not catch this; this pins the new-project default against the handout text.
"""
import importlib.util
import re
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
T1 = REPO / "docs" / "handouts" / "01_getting_started"


def _load(name, rel):
    spec = importlib.util.spec_from_file_location(name, REPO / rel)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def _load_generator(monkeypatch, name, rel):
    """Load a scripts/ generator. CI has no fpdf2 (a dev-tool-only dependency),
    and the PDF generator imports it at module level, so stub just enough of it
    for the import when it is absent -- the logic under test never renders."""
    try:
        import fpdf  # noqa: F401
    except ImportError:
        import types
        stub = types.ModuleType("fpdf")
        stub.FPDF = type("FPDF", (), {})
        monkeypatch.setitem(sys.modules, "fpdf", stub)
    return _load(name, rel)


def _read(name):
    return (T1 / name).read_text(encoding="utf-8")


def test_new_project_still_starts_with_room0():
    """The premise of the handout wording. If this ever changes, the handouts
    must be revisited (rename step vs. create step)."""
    src = (REPO / "core" / "project_manager.py").read_text(encoding="utf-8")
    assert '["assets"]["rooms"]["room0"]' in src


def test_student_handouts_rename_room0_instead_of_creating_a_room():
    for lang, create_phrase in (("en", "Create New Room"), ("fr", "Créer une salle")):
        s = _read(f"student.{lang}.md")
        assert create_phrase not in s, f"student.{lang}.md tells students to create a room"
        step = next(l for l in s.splitlines() if "room0" in l)
        assert "room_game" in step, f"student.{lang}.md rename step must name room_game"


def test_student_handout_steps_are_numbered_1_to_8_in_order():
    for lang in ("en", "fr"):
        nums = [int(m.group(1)) for m in
                re.finditer(r"^- \[ \] \*\*(\d+)\.", _read(f"student.{lang}.md"), re.M)]
        assert nums == list(range(1, 9)), f"student.{lang}.md steps: {nums}"


def test_teacher_and_worksheet_match_the_rename_flow():
    for lang in ("en", "fr"):
        t = _read(f"teacher.{lang}.md")
        assert "room0" in t and "room_game" in t
        w = _read(f"worksheet.{lang}.md")
        assert "room_game" in w
        assert "8" in t  # "the 8 steps below" / "les 8 étapes ci-dessous"


def test_referenced_handout_images_exist():
    for lang in ("en", "fr"):
        for m in re.finditer(r"!\[[^\]]*\]\(([^)\s]+)", _read(f"student.{lang}.md")):
            assert (T1 / m.group(1)).exists(), f"missing image {m.group(1)}"


def test_image_width_hint_parsing_in_both_generators(monkeypatch):
    for name, rel in (("pdfgen", "scripts/generate_tutorial_handouts_pdf.py"),
                      ("odtgen", "scripts/generate_tutorial_handouts_odt.py")):
        mod = _load_generator(monkeypatch, name, rel)
        assert mod.split_image_target("a.png") == ("a.png", 100)
        assert mod.split_image_target('a.png "45%"') == ("a.png", 45)
        assert mod.split_image_target('dir/a b.png "5%"') == ("dir/a b.png", 10)   # clamped up
        assert mod.split_image_target('a.png "250%"') == ("a.png", 100)            # clamped down
