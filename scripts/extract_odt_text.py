#!/usr/bin/env python3
"""Extract an .odt's content as clean, diff-friendly plain text -- the
first step of the hand-edited-ODT round-trip procedure documented in
docs/TUTORIAL_HANDOUT_WORKFLOW.md: generate an .odt draft, a human edits
it in LibreOffice/Word, then this script's output is what a reviewer
(Claude, in practice) reads to find exactly what changed versus the .md
source that generated the draft, before hand-applying the equivalent
edit back into every source .md the pipeline covers.

Walks the real ODF paragraph/heading/list/table DOM via odfpy (far more
reliable than regex-stripping content.xml's tags directly -- this
script's own first draft did that and silently produced a false
"missing sentence" read on a perfectly normal paragraph.

Requires `odfpy` (`pip install odfpy`) -- a dev-only tool dependency,
same tier as generate_tutorial_handouts_pdf.py's fpdf2: neither is in
requirements.txt / requirements-dev.txt, both are scripts/ tooling only,
never imported by the shipped IDE or runtime.

Output line prefixes (matching this repo's tutorial-handout Markdown
subset closely enough to eyeball a diff against the source .md):
    # / ## / ###   heading, by outline level (odf:outline-level)
    -              list item (checkbox items print their plain text --
                    ODF has no native checkbox-list concept, so a
                    hand-edited checklist item is indistinguishable from
                    an ordinary bullet here; check the source .md's own
                    "- [ ]" marker to tell them apart)
    |...|          one table row, cells joined with " | "
    [IMAGE: name (WxH px)]   an embedded picture, at its position in the
                    text flow -- see --images-out to save the actual
                    bytes for a visual compare, not just its presence

Usage:
    python3 scripts/extract_odt_text.py SRC.odt
    python3 scripts/extract_odt_text.py SRC.odt --images-out DIR
"""
import argparse
import sys
from pathlib import Path

# Windows' console defaults stdout to cp1252, which can't encode plain
# accented French text (never mind the checkbox glyphs LibreOffice's own
# bullet/checkbox lists sometimes carry) -- reconfigure rather than
# requiring every caller to remember PYTHONUTF8=1.
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")


def _cell_text(cell):
    from odf import teletype
    return teletype.extractText(cell).strip()


def extract(src_path, images_out=None):
    """Dispatches on each element's real qname local part (odfpy's
    per-tag classes -- odf.text.H, odf.table.Table, etc. -- are element
    FACTORY functions, not the classes instances are actually made from,
    so isinstance() against them always raises; every real parsed node's
    class is dynamically built, hence the qname-string dispatch here)."""
    from odf.opendocument import load
    from odf import teletype

    doc = load(str(src_path))
    body = doc.text

    if images_out:
        images_out = Path(images_out)
        images_out.mkdir(parents=True, exist_ok=True)
        for name, (_flag, data, _mimetype) in doc.Pictures.items():
            (images_out / Path(name).name).write_bytes(data)

    lines = []

    def local(node):
        return node.qname[1] if hasattr(node, "qname") else None

    def find_all(node, tag):
        found = []
        for child in getattr(node, "childNodes", []):
            if local(child) == tag:
                found.append(child)
            found.extend(find_all(child, tag))
        return found

    def visit(node):
        tag = local(node)

        if tag == "table":
            for row in find_all(node, "table-row"):
                cells = [_cell_text(c) for c in find_all(row, "table-cell")]
                lines.append("| " + " | ".join(cells) + " |")
            return  # don't also recurse into the table's own paragraphs

        if tag == "h":
            level = int(node.getAttribute("outlinelevel") or 1)
            text = teletype.extractText(node).strip()
            if text:
                lines.append("#" * min(level, 3) + " " + text)
            return

        if tag == "p":
            text = teletype.extractText(node).strip()
            if text:
                lines.append(text)
            for frame in find_all(node, "frame"):
                if not find_all(frame, "image"):
                    continue
                name = frame.getAttribute("name") or "image"
                w = frame.getAttribute("width") or "?"
                h = frame.getAttribute("height") or "?"
                lines.append(f"[IMAGE: {name} ({w} x {h})]")
            return

        if tag == "list-item":
            text = teletype.extractText(node).strip()
            if text:
                lines.append("- " + text)
            return

        for child in getattr(node, "childNodes", []):
            visit(child)

    visit(body)
    return "\n".join(lines) + "\n"


def main(argv):
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument("src", help="path to the .odt file")
    ap.add_argument(
        "--images-out", default=None,
        help="directory to save every embedded picture's real bytes into "
             "(named by their internal ODF path's basename)",
    )
    args = ap.parse_args(argv[1:])

    try:
        text = extract(args.src, args.images_out)
    except ImportError:
        print(
            "odfpy is required: pip install odfpy", file=sys.stderr,
        )
        return 1
    sys.stdout.write(text)
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
