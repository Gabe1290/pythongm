#!/usr/bin/env python3
"""Render the Tutorial-1 student handouts / teacher guides into editable ODTs.

Same custom Markdown-subset source files as
scripts/generate_tutorial_handouts_pdf.py (checkbox/numbered-step list
items, TIP/INFO/DONE callout boxes, a blank-lines "notes" placeholder), but
converted to HTML and handed to a headless LibreOffice for a real ODT Writer
document -- editable/printable in LibreOffice or Word, unlike the PDF.
Pipeline mirrors scripts/generate_flyer_odt.py and
scripts/generate_release_qa_odt.py.

Extra line-level syntax beyond plain Markdown (kept in sync with
generate_tutorial_handouts_pdf.py's docstring -- see that file for the
canonical description of each):
    - [ ] text          checkbox list item (rendered as a "☐ text" line)
    1. text             numbered step item
    > TIP: text         yellow "tip" callout box (can wrap onto more
    > more text          "> "-prefixed lines)
    > INFO: text         blue "info" callout box, same wrapping rule
    > DONE: text         green "success" callout box, same wrapping rule
    ![alt](path.png)    an image, scaled to the page's content width,
                          path relative to the source .md's own folder
    [[notes:4]]         4 blank ruled lines for handwriting

Usage:
    python3 scripts/generate_tutorial_handouts_odt.py [SRC.md [OUT.odt]]

Default (no arguments): renders every docs/handouts/<NN_slug>/*.md file into its
matching .odt next to it.

Requires `soffice` / `libreoffice` on PATH.
"""

import base64
import glob
import html
import mimetypes
import os
import re
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), os.pardir))
DOCS = os.path.join(ROOT, "docs")

# NOTE on styling strategy: LibreOffice's "HTML (StarWriter)" import filter
# is unreliable for anything beyond simple single-tag-selector rules in a
# <style> block -- verified empirically: plain single-element selectors
# (h1, h2, code) reliably carry color/border/background, but a COMMA-GROUPED
# selector (`th, td { ... }`) or a CLASS selector (`.tip { background... }`,
# `p.tip { background... }`) silently drops border/background (border-left
# on a class selector even worked while background-color on the same rule
# did not -- there is no reliable subset to lean on). So headings/paragraphs/
# code below use this shared stylesheet, but tables, callout boxes and the
# notes-lines all use per-element inline `style=""` attributes instead
# (confirmed reliable), built in the emitter code further down.
_STYLE = """
  body     { font-family: "DejaVu Sans","Liberation Sans",sans-serif; font-size: 10.5pt; color: #2c3e50; }
  h1       { color: #2c3e50; font-size: 22pt; margin: 0 0 4pt 0; border-bottom: 2px solid #3498db; padding-bottom: 4pt; }
  h2       { color: #3498db; font-size: 15pt; margin: 16pt 0 6pt 0; page-break-after: avoid; }
  h3       { color: #2c3e50; font-size: 12pt; margin: 10pt 0 4pt 0; page-break-after: avoid; }
  p        { margin: 0 0 7pt 0; line-height: 1.35; }
  li       { margin: 0 0 4pt 0; line-height: 1.3; }
  code     { font-family: "DejaVu Sans Mono", monospace; font-size: 9.5pt; background-color: #e9ecef; padding: 1pt 3pt; }
"""

# Inline-style building blocks (see the NOTE above for why these are inline).
_TABLE_STYLE = "border-collapse:collapse;width:100%;margin:4pt 0 10pt 0;"
_TH_STYLE = ("border:1px solid #dee2e6;padding:4pt 6pt;font-size:9.5pt;"
             "text-align:left;background-color:#d1ecf1;")
_TD_STYLE = ("border:1px solid #dee2e6;padding:4pt 6pt;font-size:9.5pt;"
             "vertical-align:top;text-align:left;")
# LibreOffice's HTML import ignores a CSS `width` on <table>/<th>/<td>
# entirely (verified empirically -- ANY unit, ANY of those three elements)
# and instead auto-sizes each column to its widest WORD under the overall
# page-width budget, which can squeeze a narrow first column below even a
# short word's width and split it mid-word (e.g. "Object" -> "Objec"/"t").
# Two things DO work, both perverse HTML4-attribute holdovers rather than
# CSS, verified against live conversions: the legacy <col width="N%"> sets
# each column's share correctly, and a literal width="100%" HTML ATTRIBUTE
# (not a CSS width, which is silently ignored the same as above) on <table>
# itself is what makes the whole table actually span the page instead of
# shrinking to its content's natural width. Column-count -> percentages
# below are tuned for this doc's actual tables (a 2-col term/definition
# table and a 3-col segment/time/description table).
_COLGROUP_WIDTHS = {1: ["100%"], 2: ["26%", "74%"], 3: ["25%", "15%", "60%"]}
_CALLOUT_COLORS = {
    "TIP": ("#fff3cd", "#ffc107"),
    "INFO": ("#d1ecf1", "#17a2b8"),
    "DONE": ("#d4edda", "#28a745"),
}
# A run of underscores, not a bordered empty paragraph/table row: LibreOffice's
# HTML import collapses consecutive identical empty/whitespace-only
# paragraphs (and table rows) into a single line regardless of styling --
# verified empirically -- so N blank "write here" lines must carry distinct,
# non-empty visible content to survive the import as N separate lines.
_NOTES_LINE = "_" * 78

_BLOCK_START = re.compile(
    r"^(#{1,3}\s|-\s|>|\|.*\||\d+\.\s|---$|\[\[notes:\d+\]\]$|!\[)"
)
_IMAGE = re.compile(r"!\[([^\]]*)\]\(([^)]+)\)$")


def _merge_soft_wraps(lines):
    """Fold a block-start line's soft-wrapped continuation lines back onto
    it, same rule (and same rationale) as generate_tutorial_handouts_pdf.py's
    helper of the same name -- kept as an independent copy so this script
    has no import-time dependency on fpdf."""
    merged = []
    for line in lines:
        stripped = line.strip()
        if stripped == "" or _BLOCK_START.match(stripped) or not merged:
            merged.append(line)
        else:
            merged[-1] = merged[-1].rstrip() + " " + stripped
    return merged


def _data_uri(path):
    """Read a local image file into a base64 data: URI, so LibreOffice's
    HTML import EMBEDS the picture into the ODT rather than importing it
    as a linked <draw:frame> pointing at a relative path computed from the
    throwaway conversion tempdir (verified empirically: an
    <img src="file:///..."> line -- even an absolute, correctly-formed
    file:// URI -- lands as an external link with a path like
    "../../../../../pygm/docs/x.png", broken the moment the .odt is moved
    to its real home; the generated document must carry its own picture
    data, not a pointer)."""
    mime = mimetypes.guess_type(path)[0] or "application/octet-stream"
    with open(path, "rb") as fh:
        b64 = base64.b64encode(fh.read()).decode("ascii")
    return f"data:{mime};base64,{b64}"


def _inline(text):
    text = html.escape(text, quote=False)
    text = re.sub(r"`([^`]+)`", r"<code>\1</code>", text)
    text = re.sub(r"\*\*(.+?)\*\*", r"<strong>\1</strong>", text)
    return text


def md_to_html(md_text, src_dir=None):
    """src_dir -- the source .md's own folder, so an image's relative path
    resolves against it (not the temp dir the HTML gets written to for the
    LibreOffice conversion). Required if md_text contains an image line."""
    lines = _merge_soft_wraps(md_text.replace("\r\n", "\n").split("\n"))
    out = []
    para, list_buf, list_tag = [], [], None
    i, n = 0, len(lines)

    def flush_para():
        if not para:
            return
        text = " ".join(s.strip() for s in para).strip()
        para.clear()
        if text:
            out.append(f"<p>{_inline(text)}</p>")

    def flush_list():
        nonlocal list_tag
        if not list_buf:
            return
        out.append(f"<{list_tag}>")
        for item in list_buf:
            out.append(f"<li>{_inline(item)}</li>")
        out.append(f"</{list_tag}>")
        list_buf.clear()
        list_tag = None

    while i < n:
        line = lines[i]
        stripped = line.strip()

        if stripped == "---":
            flush_para()
            flush_list()
            out.append("<hr/>")
            i += 1
            continue

        m_notes = re.fullmatch(r"\[\[notes:(\d+)\]\]", stripped)
        if m_notes:
            flush_para()
            flush_list()
            for _ in range(int(m_notes.group(1))):
                out.append(f'<p style="margin:0 0 12pt 0;color:#999999;">{_NOTES_LINE}</p>')
            i += 1
            continue

        if stripped.startswith(">"):
            flush_para()
            flush_list()
            block = []
            while i < n and lines[i].strip().startswith(">"):
                block.append(lines[i].strip().lstrip(">").strip())
                i += 1
            text = " ".join(block).strip()
            kind = "TIP"
            m2 = re.match(r"(TIP|INFO|DONE):\s*(.*)", text)
            if m2:
                kind, text = m2.group(1), m2.group(2)
            bg, border = _CALLOUT_COLORS[kind]
            style = (f"margin:6pt 0 10pt 0;padding:6pt 10pt;"
                     f"background-color:{bg};border-left:4px solid {border};")
            out.append(f'<p style="{style}">{_inline(text)}</p>')
            continue

        if stripped.startswith("|") and stripped.endswith("|"):
            flush_para()
            flush_list()
            tbl = []
            while i < n and lines[i].strip().startswith("|"):
                cells = [c.strip() for c in lines[i].strip().strip("|").split("|")]
                if not re.fullmatch(r"[:\- ]+", "".join(cells)):
                    tbl.append(cells)
                i += 1
            if tbl:
                head, body = tbl[0], tbl[1:]
                ncols = len(head)
                widths = _COLGROUP_WIDTHS.get(ncols) or [f"{100 // ncols}%"] * ncols
                colgroup = "<colgroup>" + "".join(f'<col width="{w}">' for w in widths) + "</colgroup>"
                out.append(f'<table width="100%" style="{_TABLE_STYLE}">{colgroup}')
                out.append("<tr>" + "".join(f'<th style="{_TH_STYLE}">{_inline(c)}</th>' for c in head) + "</tr>")
                for r in body:
                    out.append("<tr>" + "".join(f'<td style="{_TD_STYLE}">{_inline(c)}</td>' for c in r) + "</tr>")
                out.append("</table>")
            continue

        m_img = _IMAGE.match(stripped)
        if m_img:
            flush_para()
            flush_list()
            alt, relpath = m_img.group(1), m_img.group(2)
            abspath = os.path.abspath(os.path.join(src_dir or "", relpath))
            out.append(
                f'<p><img src="{_data_uri(abspath)}" '
                f'alt="{html.escape(alt, quote=True)}" width="100%"></p>'
            )
            i += 1
            continue

        if stripped.startswith("# "):
            flush_para()
            flush_list()
            out.append(f"<h1>{_inline(stripped[2:].strip())}</h1>")
            i += 1
            continue
        if stripped.startswith("### "):
            flush_para()
            flush_list()
            out.append(f"<h3>{_inline(stripped[4:].strip())}</h3>")
            i += 1
            continue
        if stripped.startswith("## "):
            flush_para()
            flush_list()
            out.append(f"<h2>{_inline(stripped[3:].strip())}</h2>")
            i += 1
            continue

        if stripped.startswith("- [ ] "):
            flush_para()
            flush_list()
            out.append(f'<p style="margin:0 0 6pt 0;">&#9744;&#160;&#160;{_inline(stripped[6:].strip())}</p>')
            i += 1
            continue
        if stripped.startswith("- "):
            flush_para()
            if list_tag not in (None, "ul"):
                flush_list()
            list_tag = "ul"
            list_buf.append(stripped[2:].strip())
            i += 1
            continue
        m3 = re.match(r"(\d+)\.\s+(.*)", stripped)
        if m3:
            flush_para()
            if list_tag not in (None, "ol"):
                flush_list()
            list_tag = "ol"
            list_buf.append(m3.group(2).strip())
            i += 1
            continue

        if stripped == "":
            flush_para()
            flush_list()
            i += 1
            continue

        para.append(stripped)
        i += 1

    flush_para()
    flush_list()
    return (
        "<!DOCTYPE html><html><head><meta charset='utf-8'>"
        f"<style>{_STYLE}</style></head><body>\n" + "\n".join(out) + "\n</body></html>"
    )


def _soffice():
    for name in ("soffice", "libreoffice"):
        path = shutil.which(name)
        if path:
            return path
    raise FileNotFoundError("soffice / libreoffice not found on PATH")


def render(src_path, out_path):
    with open(src_path, encoding="utf-8") as fh:
        html_doc = md_to_html(fh.read(), src_dir=os.path.dirname(src_path))

    base = os.path.splitext(os.path.basename(out_path))[0]
    with tempfile.TemporaryDirectory() as tmp:
        html_path = os.path.join(tmp, base + ".html")
        with open(html_path, "w", encoding="utf-8") as fh:
            fh.write(html_doc)
        # A real file:// URI (Path.as_uri(), not string-glued "file://" +
        # a Windows backslash path -- "file://C:\..." is missing the third
        # slash a Windows drive-letter URI needs). The malformed form
        # apparently tolerated text-only conversions on this machine but
        # hung indefinitely once an <img src="file:///..."> (added for
        # image support, see md_to_html) also needed real file:// URI
        # resolution in the same LibreOffice process.
        profile = Path(tmp, "loprofile").as_uri()
        subprocess.run(
            [
                _soffice(), "--headless", "--norestore",
                f"-env:UserInstallation={profile}",
                "--infilter=HTML (StarWriter)",
                "--convert-to", "odt:writer8",
                "--outdir", tmp, html_path,
            ],
            check=True,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.PIPE,
        )
        produced = os.path.join(tmp, base + ".odt")
        if not os.path.isfile(produced):
            raise RuntimeError(f"LibreOffice did not produce {produced}")
        os.makedirs(os.path.dirname(out_path), exist_ok=True)
        shutil.move(produced, out_path)
    return out_path


def main(argv):
    if len(argv) >= 2:
        src = os.path.abspath(argv[1])
        out = os.path.abspath(argv[2]) if len(argv) >= 3 else os.path.splitext(src)[0] + ".odt"
        print(f"{os.path.relpath(src, ROOT)} -> {os.path.relpath(out, ROOT)}")
        render(src, out)
        return 0

    made = 0
    for src in sorted(glob.glob(os.path.join(DOCS, "handouts", "*", "*.md"))):
        out = os.path.splitext(src)[0] + ".odt"
        render(src, out)
        print(f"  wrote {os.path.relpath(out, ROOT)}")
        made += 1
    print(f"done: {made} ODT(s)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
