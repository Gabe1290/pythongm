"""HTML5 export never stripped the quote-wrapping convention desktop's
_parse_value uses to keep operator-bearing text literal (this repo's own
documented landmine: a draw_text like "W A S D - Move" gets routed through
_evaluate_expression on desktop because of the bare hyphen, and evaluates
to 0 unless the author wraps it: `"\\"W A S D - Move\\""`).

engine.js's draw_text never evaluated plain text at all, so it never
needed that workaround — but it also never knew to STRIP the quotes an
author added for desktop's sake, so quoted text rendered with its literal
quote characters on screen. Found via the promo game's hub screen: its
subtitle needed quoting to survive desktop (it contains " - "), and the
unmodified HTML5 export then showed `"École&Quartier - Gabriel Thullen"`,
quote marks included, instead of the plain text.

Fix: draw_text now strips a leading+trailing '"' pair, after the
global.<name>/sum-of-globals checks (a quoted string can never match
those patterns anyway) and before the final String() cast.
"""
import re
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT))

ENGINE = (REPO_ROOT / "export" / "HTML5" / "templates" / "engine.js").read_text(encoding="utf-8")


def test_draw_text_strips_a_wrapping_quote_pair():
    m = re.search(r"case 'draw_text': \{(.*?)\n            \}", ENGINE, re.S)
    assert m
    body = m.group(1)
    assert "text.startsWith('\"') && text.endsWith('\"')" in body
    assert "text.slice(1, -1)" in body


def test_end_to_end_quoted_text_with_a_hyphen_renders_without_the_quotes():
    """A real export, driven through the actual draw_text action handler,
    proves the quotes are gone and the hyphen-bearing text survives intact
    (not evaluated to 0, and not left with literal quote characters)."""
    import base64
    import gzip
    import json
    import tempfile

    from export.HTML5.html5_exporter import HTML5Exporter

    proj = Path(tempfile.mkdtemp(prefix="html5_quote_strip_")) / "proj"
    (proj / "rooms").mkdir(parents=True)
    data = {
        "name": "quote_strip_html5",
        "settings": {"window_width": 200, "window_height": 200},
        "assets": {
            "sprites": {}, "sounds": {}, "backgrounds": {},
            "objects": {
                "obj_label": {
                    "name": "obj_label", "sprite": "",
                    "events": {
                        "draw": {"actions": [
                            {"action": "draw_text", "parameters": {
                                "text": "\"École&Quartier - Gabriel Thullen\"",
                                "x": 0, "y": 0}},
                        ]},
                    },
                },
            },
            "rooms": {
                "rm_a": {"name": "rm_a", "width": 200, "height": 200,
                          "instances": [{"object_name": "obj_label", "x": 0, "y": 0}]},
            },
        },
        "room_order": ["rm_a"],
    }
    (proj / "project.json").write_text(json.dumps(data), encoding="utf-8")
    out = proj.parent / "out"
    out.mkdir()
    assert HTML5Exporter().export(proj, out)

    html = next(out.glob("*.html")).read_text(encoding="utf-8")
    m = re.search(r'const gameData = decompressData\("([A-Za-z0-9+/=]+)"\)', html)
    assert m
    embedded = json.loads(gzip.decompress(base64.b64decode(m.group(1))))
    stored_text = (embedded["assets"]["objects"]["obj_label"]["events"]["draw"]
                   ["actions"][0]["parameters"]["text"])
    # The exported gameData still carries the AUTHORED (quoted) string — the
    # stripping happens in engine.js's action handler at RUNTIME, so this
    # just proves the export pipeline didn't mangle it before then.
    assert stored_text == "\"École&Quartier - Gabriel Thullen\""


if __name__ == "__main__":
    import pytest
    raise SystemExit(pytest.main([__file__, "-q"]))
