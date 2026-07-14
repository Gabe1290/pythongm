"""HTML5 export — L1: the project name must be HTML-escaped in the page.

The exporter interpolated project_data['name'] straight into the <title>
and the title <div> of the generated HTML. A legitimate name containing
'&', '<' or '>' corrupted the markup (and in principle injected script).
"""
import json
import shutil
import sys
import tempfile
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT))

from export.HTML5.html5_exporter import HTML5Exporter  # noqa: E402


def _export_with_name(hostile_name: str) -> str:
    """Copy maze_1 to a temp dir, rename it, export, return the HTML text."""
    src = REPO_ROOT / "samples" / "maze_1"
    tmp = Path(tempfile.mkdtemp(prefix="l1_proj_"))
    proj = tmp / "proj"
    shutil.copytree(src, proj)
    data = json.loads((proj / "project.json").read_text(encoding="utf-8"))
    data["name"] = hostile_name
    (proj / "project.json").write_text(json.dumps(data), encoding="utf-8")

    out = tmp / "out"
    out.mkdir()
    assert HTML5Exporter().export(proj, out), "export failed"
    html_file = next(out.glob("*.html"))
    return html_file.read_text(encoding="utf-8")


def test_special_chars_in_name_are_escaped_in_markup():
    html = _export_with_name("Tom & <Jerry>")
    # The raw, markup-breaking form must not appear in the page chrome.
    assert "<title>Tom & <Jerry></title>" not in html
    assert '<div class="title">Tom & <Jerry></div>' not in html
    # The escaped form must be what's rendered.
    assert "Tom &amp; &lt;Jerry&gt;" in html


def test_quote_in_name_does_not_break_out():
    html = _export_with_name('My "Great" Game')
    # html.escape encodes double quotes as &quot;
    assert "&quot;Great&quot;" in html
    assert '<title>My "Great" Game</title>' not in html


def test_ordinary_name_unaffected():
    html = _export_with_name("Maze Level 1")
    assert "<title>Maze Level 1</title>" in html


def test_filename_illegal_chars_do_not_crash_export():
    """A name legal as a project name but illegal as a Windows filename
    (':' or '<>') used to crash the file write. Export must succeed and the
    on-disk name is sanitized while the in-page title keeps the real name."""
    from export.HTML5.html5_exporter import _sanitize_filename
    assert _sanitize_filename("Level 1: Go") == "Level 1_ Go"
    assert _sanitize_filename("Tom & <Jerry>") == "Tom & _Jerry_"
    assert _sanitize_filename("...") == ""  # falls back to "game" at the call site

    # End-to-end: a colon name exports without raising and titles correctly.
    html = _export_with_name("Level 1: Go")
    assert "<title>Level 1: Go</title>" in html


# --- exporter-io-registry finder (2026-07-14): I/O robustness ------------

def _export_mutated(mutate):
    """Copy maze_1, mutate its project dict, export; return (ok, out_dir)."""
    import shutil
    src = REPO_ROOT / "samples" / "maze_1"
    tmp = Path(tempfile.mkdtemp(prefix="io_test_"))
    proj = tmp / "proj"
    shutil.copytree(src, proj)
    data = json.loads((proj / "project.json").read_text(encoding="utf-8"))
    mutate(data)
    (proj / "project.json").write_text(json.dumps(data), encoding="utf-8")
    out = tmp / "out"
    out.mkdir()
    return HTML5Exporter().export(proj, out), out


def test_missing_sprite_file_does_not_abort_export():
    """#1: a sprite whose file is gone is dropped (logged) — export still
    succeeds rather than silently shipping invisible art with no signal."""
    def m(d):
        for info in d["assets"]["sprites"].values():
            info["file_path"] = "sprites/GONE.png"
            break
    ok, _ = _export_mutated(m)
    assert ok


def test_non_dict_sprite_entry_does_not_abort_export():
    """#2: a non-dict sprite entry (bare string) is skipped, not an
    AttributeError that fails the whole export (encode_sounds already did
    this; sprites/backgrounds now match)."""
    ok, _ = _export_mutated(lambda d: d["assets"]["sprites"].__setitem__("bogus", "s.png"))
    assert ok


def test_non_dict_room_entry_does_not_abort_export():
    """#3: a non-dict room value must not AttributeError in
    _load_room_instances before the per-room try."""
    ok, _ = _export_mutated(lambda d: d["assets"]["rooms"].__setitem__("bogus", "r.json"))
    assert ok


def test_nameless_project_exports_as_game_html():
    """#4: a project.json without a 'name' must not KeyError the export."""
    ok, out = _export_mutated(lambda d: d.pop("name", None))
    assert ok and (out / "game.html").exists()


def test_success_consumer_uses_sanitized_filename():
    """#5: the IDE success dialog / 'Open in browser' must reference the
    SANITIZED filename that was actually written, not the raw project name
    (a ':' name is sanitized on write; recomputing the raw name opened a
    file that doesn't exist)."""
    from export.HTML5.html5_exporter import _sanitize_filename
    ok, out = _export_mutated(lambda d: d.__setitem__("name", "Level 1: Go"))
    assert ok
    consumer = (_sanitize_filename("Level 1: Go") or "game") + ".html"
    assert (out / consumer).exists()
    # this is what core/ide_exporters.py now computes for the dialog/webbrowser
    src = (REPO_ROOT / "core" / "ide_exporters.py").read_text(encoding="utf-8")
    assert "_sanitize_filename" in src
