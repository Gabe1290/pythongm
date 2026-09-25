"""Handouts finished by hand (docs/handouts/hand_exported.txt) must never be
regenerated from their .md.

Why: the user hand-edits each handout's .odt in Writer (drawn callouts,
screenshots) and exports the PDF by hand. Regenerating the PDF with fpdf2, or
copying a stray md-generated PDF over it, silently destroys that work
(a hand-edited .odt was lost that way on 2026-09-17; the Tutorial 1 PDFs were
one `build_teacher_wiki.py` run from the same fate on 2026-09-25).
"""
import importlib.util
import os
import sys
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO / "scripts"))
import hand_exported  # noqa: E402


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


build = _load("build_teacher_wiki_under_test", "scripts/build_teacher_wiki.py")
T1 = "01_getting_started"


def test_manifest_lists_the_finished_tutorial_1_student_handouts():
    stems = hand_exported.hand_exported_stems()
    assert {f"{T1}/student.fr", f"{T1}/student.en"} <= stems


def test_every_listed_handout_has_md_odt_and_a_published_pdf():
    for st in hand_exported.hand_exported_stems():
        nn, base = st.split("/")
        kind, lang = base.split(".")
        for ext in ("md", "odt"):
            assert (REPO / "docs" / "handouts" / nn / f"{base}.{ext}").exists(), f"{st}.{ext}"
        dl = REPO / "wiki" / "downloads" / f"{build.stem(kind, nn, lang)}.pdf"
        assert dl.exists() and dl.read_bytes()[:5] == b"%PDF-", f"published PDF missing: {dl.name}"


def test_manifest_parsing_ignores_comments_and_backslashes(tmp_path):
    m = tmp_path / "m.txt"
    m.write_text("# comment\n\n01_a\\student.fr\n02_b/worksheet.en  \n", encoding="utf-8")
    assert hand_exported.hand_exported_stems(str(m)) == {"01_a/student.fr", "02_b/worksheet.en"}
    assert hand_exported.hand_exported_stems(str(tmp_path / "missing.txt")) == set()


@pytest.mark.parametrize("script", ["generate_tutorial_handouts_pdf", "generate_tutorial_handouts_odt"])
def test_generators_refuse_a_listed_handout_unless_forced(script, monkeypatch):
    mod = _load_generator(monkeypatch, script, f"scripts/{script}.py")
    calls = []
    monkeypatch.setattr(mod, "render", lambda src, out: calls.append((src, out)))
    listed = str(REPO / "docs" / "handouts" / T1 / "student.fr.md")
    assert mod.main(["x", listed]) == 2
    assert calls == []
    assert mod.main(["x", listed, "--force"]) == 0
    assert len(calls) == 1
    unlisted = str(REPO / "docs" / "handouts" / T1 / "teacher.fr.md")
    assert mod.main(["x", unlisted]) == 0
    assert len(calls) == 2


@pytest.mark.parametrize("script", ["generate_tutorial_handouts_pdf", "generate_tutorial_handouts_odt"])
def test_generator_bulk_mode_skips_listed_handouts(script, monkeypatch):
    mod = _load_generator(monkeypatch, script, f"scripts/{script}.py")
    written = []
    monkeypatch.setattr(mod, "render", lambda src, out: written.append(os.path.relpath(src, mod.DOCS).replace("\\", "/")))
    assert mod.main(["x"]) == 0
    assert f"handouts/{T1}/student.fr.md" not in written
    assert f"handouts/{T1}/student.en.md" not in written
    assert f"handouts/{T1}/teacher.fr.md" in written


def test_build_never_regenerates_a_listed_pdf_but_does_for_others(monkeypatch):
    ran = []
    monkeypatch.setattr(build.subprocess, "run", lambda cmd, **kw: ran.append(os.path.basename(cmd[1])))
    monkeypatch.setattr(build.shutil, "which", lambda _n: None)  # no soffice: ODT step is a no-op
    base = REPO / "docs" / "handouts" / T1
    build._run_generators(str(base / "student.fr.md"), make_pdf=True)
    assert ran == []
    build._run_generators(str(base / "teacher.fr.md"), make_pdf=True)
    assert ran == ["generate_tutorial_handouts_pdf.py"]


def test_publish_keeps_the_committed_hand_export_and_still_copies_the_odt(tmp_path, monkeypatch):
    monkeypatch.setattr(build, "is_hand_exported", lambda p: True)
    src = tmp_path / "student.fr.md"
    src.write_text("x")
    (tmp_path / "student.fr.pdf").write_bytes(b"%PDF-1.4 STRAY md-generated")
    (tmp_path / "student.fr.odt").write_bytes(b"ODT")
    dl = tmp_path / "dl"
    dl.mkdir()
    (dl / "Name.pdf").write_bytes(b"%PDF-1.4 REAL hand export")
    links = build._publish_downloads(str(src), "Name", str(dl))
    assert (dl / "Name.pdf").read_bytes() == b"%PDF-1.4 REAL hand export"   # not overwritten
    assert (dl / "Name.odt").read_bytes() == b"ODT"
    assert links == ["[PDF](downloads/Name.pdf)", "[ODT](downloads/Name.odt)"]


def test_publish_fails_loudly_if_the_hand_export_is_missing(tmp_path, monkeypatch):
    monkeypatch.setattr(build, "is_hand_exported", lambda p: True)
    src = tmp_path / "student.fr.md"
    src.write_text("x")
    (tmp_path / "dl").mkdir()
    with pytest.raises(SystemExit):
        build._publish_downloads(str(src), "Name", str(tmp_path / "dl"))


def test_non_listed_pdf_is_still_copied(tmp_path, monkeypatch):
    monkeypatch.setattr(build, "is_hand_exported", lambda p: False)
    src = tmp_path / "teacher.en.md"
    src.write_text("x")
    (tmp_path / "teacher.en.pdf").write_bytes(b"%PDF-generated")
    (tmp_path / "dl").mkdir()
    build._publish_downloads(str(src), "T", str(tmp_path / "dl"))
    assert (tmp_path / "dl" / "T.pdf").read_bytes() == b"%PDF-generated"


def test_adopt_exports_publishes_only_listed_valid_pdfs(tmp_path):
    h = tmp_path / "handouts" / T1
    h.mkdir(parents=True)
    (h / "student.fr.pdf").write_bytes(b"%PDF-1.4 fresh export")
    dl = tmp_path / "dl"
    got = build.adopt_exports(str(tmp_path / "handouts"), str(dl),
                              stems={f"{T1}/student.fr", f"{T1}/student.en"})   # en has no export yet
    assert got == [f"{T1}/student.fr"]
    assert (dl / "Student-Handout-01-getting-started_fr.pdf").read_bytes() == b"%PDF-1.4 fresh export"
    (h / "student.en.pdf").write_bytes(b"not a pdf")
    with pytest.raises(SystemExit):
        build.adopt_exports(str(tmp_path / "handouts"), str(dl), stems={f"{T1}/student.en"})
