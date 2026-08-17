"""Guard the JavaScript that extensions inject into the HTML5 export.

Why this exists: two missing commas in
`extensions/raycast_2_5d/export_html5.js` made the whole of `engine.js`
fail to PARSE, so every HTML5 export was a black window -- including
maze_1, which contains no raycast content whatsoever, because the extension
JS is injected unconditionally. Nothing caught it: the ~20 export test files
all assert on generated strings and file layout, and CI has no JavaScript
parser to notice a syntax error.

These files are object literals:

    Object.assign(GameRoom.prototype, {
        methodOne(a) { ... },
        methodTwo(b) { ... },
    });

so every member needs a trailing comma. Adding a method and forgetting the
comma is the single easiest way to break every export at once, and it is
invisible until a browser tries to parse it. This checks the structure
without needing one.
"""
import re
import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT))

EXTENSION_JS = sorted((REPO_ROOT / "extensions").glob("*/export_html5.js"))


def _object_assign_members(lines):
    """Yield (line_number, closing_line, next_meaningful_line) for each member
    of every top-level Object.assign({...}) literal in the file."""
    inside = False
    for n, line in enumerate(lines):
        if re.match(r"Object\.assign\(", line):
            inside = True
            continue
        if inside and line.startswith("});"):
            inside = False
            continue
        if inside and re.match(r"^    \}", line):
            j = n + 1
            while j < len(lines) and (not lines[j].strip()
                                      or lines[j].strip().startswith("//")):
                j += 1
            yield n + 1, line, (lines[j].strip() if j < len(lines) else "")


def test_there_is_extension_js_to_check():
    """If this fails the glob is wrong and every test below is vacuous."""
    assert EXTENSION_JS, "no extensions/*/export_html5.js found"


@pytest.mark.parametrize("js_path", EXTENSION_JS, ids=lambda p: p.parent.name)
def test_object_literal_members_are_comma_separated(js_path):
    lines = js_path.read_text(encoding="utf-8").split("\n")
    offenders = []
    for lineno, closing, nxt in _object_assign_members(lines):
        # The literal's own final member is followed by the closing "});",
        # which needs no comma. Anything else must end with one.
        if nxt.startswith("}"):
            continue
        if not closing.rstrip().endswith(","):
            offenders.append("%s:%d -- next member is %s"
                             % (js_path.name, lineno, nxt[:60]))
    assert not offenders, (
        "object-literal member(s) missing a trailing comma; this makes the "
        "whole exported engine.js fail to parse and every HTML5 export a "
        "black window:\n  " + "\n  ".join(offenders))


@pytest.mark.parametrize("js_path", EXTENSION_JS, ids=lambda p: p.parent.name)
def test_braces_and_parens_balance(js_path):
    """The brace-balance check this repo already uses for JS surgery, since
    there is no parser available. Not a substitute for parsing -- it cannot
    see a missing comma, which is exactly why the test above exists too."""
    src = js_path.read_text(encoding="utf-8")
    # Strip line comments and template/string literals cheaply enough for a
    # balance count; block comments are not used in these files.
    stripped = re.sub(r"//[^\n]*", "", src)
    stripped = re.sub(r"'(\\.|[^'\\])*'", "''", stripped)
    stripped = re.sub(r'"(\\.|[^"\\])*"', '""', stripped)
    stripped = re.sub(r"`(\\.|[^`\\])*`", "``", stripped)
    for open_c, close_c in (("{", "}"), ("(", ")"), ("[", "]")):
        assert stripped.count(open_c) == stripped.count(close_c), (
            "%s: unbalanced %s%s (%d vs %d)"
            % (js_path.name, open_c, close_c,
               stripped.count(open_c), stripped.count(close_c)))


@pytest.fixture(scope="module")
def exported_html(tmp_path_factory):
    """One real export, shared by the tests below. maze_1 is deliberate: it
    uses no extension features at all, so it proves the injected JS ships
    (and therefore has to parse) even for a project that never touches it --
    which is exactly how the black-window bug reached every sample."""
    from export.HTML5.html5_exporter import HTML5Exporter
    out = tmp_path_factory.mktemp("html5")
    assert HTML5Exporter().export(REPO_ROOT / "samples/maze_1", out, {}), \
        "maze_1 failed to export"
    html = list(out.glob("*.html"))
    assert len(html) == 1, "expected one .html, got %s" % html
    return html[0].read_text(encoding="utf-8")


@pytest.mark.parametrize("js_path", EXTENSION_JS, ids=lambda p: p.parent.name)
def test_it_reaches_a_real_export(js_path, exported_html):
    """A perfectly valid file that never gets injected is just as broken, in
    the other direction. Pick a distinctive line of real code from the file
    and require it in the output."""
    code = [l.strip() for l in js_path.read_text(encoding="utf-8").split("\n")
            if l.strip() and not l.strip().startswith("//")]
    signature = max(code, key=len)      # longest code line: distinctive enough
    assert signature in exported_html, (
        "%s was not injected into the export" % js_path.name)


def test_the_export_is_utf8_and_declares_it(exported_html):
    """Accented text has to survive to the browser -- this is French-language
    educational software, and exported game messages are next on the list."""
    assert '<meta charset="utf-8">' in exported_html
    assert "�" not in exported_html, \
        "U+FFFD replacement character in the export: something was decoded " \
        "with the wrong encoding on the way through"
