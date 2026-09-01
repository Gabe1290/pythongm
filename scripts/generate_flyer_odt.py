#!/usr/bin/env python3
"""Render docs/FLYER*.md into docs/FLYER*.odt via LibreOffice.

The flyer source is a small Markdown subset (title, subtitle, `##` section
headings, `---` rules, bold-lead paragraphs, one pipe table and a fenced code
block). This script turns that into a styled HTML document and asks a headless
LibreOffice (`soffice`) to convert it to a real ODT Writer text document
(filter `writer8`, not the Writer/Web variant).

Usage:
    python3 scripts/generate_flyer_odt.py [SRC.md [OUT.odt]]

With no arguments it regenerates docs/FLYER.odt and every docs/FLYER_XX.odt
sibling that has a matching .md.

Requires `soffice` / `libreoffice` on PATH. CJK glyphs (日本語 / 中文) rely on a
CJK font being installed for LibreOffice to fall back to (Noto Sans CJK on the
Linux box); the .md itself carries the characters.
"""

import html
import os
import re
import shutil
import subprocess
import sys
import tempfile

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), os.pardir))
LANG_SUFFIXES = ["", "_DE", "_ES", "_FR", "_IT", "_RU", "_SL", "_UK"]

_STYLE = """
  body   { font-family: "DejaVu Sans","Liberation Sans",sans-serif; font-size: 10pt; color: #1c2026; }
  h1     { font-family: "DejaVu Sans","Liberation Sans",sans-serif; color: #245ca8; font-size: 24pt; margin: 0 0 3pt 0; }
  h2     { font-family: "DejaVu Sans","Liberation Sans",sans-serif; color: #245ca8; font-size: 14pt; margin: 16pt 0 5pt 0; }
  h3.sub { font-family: "DejaVu Sans","Liberation Sans",sans-serif; color: #606872; font-size: 12pt; font-weight: bold; margin: 0 0 10pt 0; }
  p      { margin: 0 0 7pt 0; line-height: 1.35; }
  hr     { border: 0; border-top: 1px solid #ced4dc; margin: 10pt 0; }
  table  { border-collapse: collapse; width: 100%; }
  th, td { border: 1px solid #ced4dc; padding: 4pt 6pt; font-size: 9.5pt;
           vertical-align: top; text-align: left; }
  th     { background-color: #e9eff8; }
  pre    { background-color: #f3f5f8; border: 1px solid #ced4dc; padding: 7pt;
           font-family: "DejaVu Sans Mono", monospace; font-size: 9.5pt; }
  .credit { color: #606872; font-style: italic; font-size: 8.5pt; }
"""


def _inline(text):
    """Escape HTML then re-introduce **bold** as <strong>."""
    text = html.escape(text, quote=False)
    return re.sub(r"\*\*(.+?)\*\*", r"<strong>\1</strong>", text)


def md_to_html(md_text):
    lines = md_text.replace("\r\n", "\n").split("\n")
    out = []
    para = []
    i, n = 0, len(lines)

    def flush():
        if not para:
            return
        text = " ".join(s.strip() for s in para).strip()
        para.clear()
        if not text:
            return
        m = re.fullmatch(r"\*(.+)\*", text)
        if m:
            out.append(f'<p class="credit">{_inline(m.group(1))}</p>')
        else:
            out.append(f"<p>{_inline(text)}</p>")

    while i < n:
        s = lines[i].strip()

        if s == "---":
            flush()
            out.append("<hr/>")
            i += 1
            continue

        if s.startswith("```"):
            flush()
            block = []
            i += 1
            while i < n and not lines[i].strip().startswith("```"):
                block.append(html.escape(lines[i].rstrip(), quote=False))
                i += 1
            i += 1
            out.append("<pre>" + "\n".join(block) + "</pre>")
            continue

        if s.startswith("|") and s.endswith("|"):
            flush()
            rows = []
            while i < n and lines[i].strip().startswith("|"):
                cells = [c.strip() for c in lines[i].strip().strip("|").split("|")]
                if not re.fullmatch(r"[:\-\s]*", "".join(cells)):
                    rows.append(cells)
                i += 1
            if rows:
                buf = ["<table>"]
                head, body = rows[0], rows[1:]
                buf.append("<tr>" + "".join(f"<th>{_inline(c)}</th>" for c in head) + "</tr>")
                for r in body:
                    buf.append("<tr>" + "".join(f"<td>{_inline(c)}</td>" for c in r) + "</tr>")
                buf.append("</table>")
                out.append("".join(buf))
            continue

        if s.startswith("# "):
            flush()
            out.append(f"<h1>{_inline(s[2:].strip())}</h1>")
            i += 1
            continue
        if s.startswith("### "):
            flush()
            out.append(f'<h3 class="sub">{_inline(s[4:].strip())}</h3>')
            i += 1
            continue
        if s.startswith("## "):
            flush()
            out.append(f"<h2>{_inline(s[3:].strip())}</h2>")
            i += 1
            continue

        if s == "":
            flush()
            i += 1
            continue

        para.append(s)
        i += 1

    flush()
    return (
        "<!DOCTYPE html>\n<html><head><meta charset=\"utf-8\"/>\n"
        f"<style>{_STYLE}</style></head><body>\n" + "\n".join(out) + "\n</body></html>\n"
    )


def _soffice():
    for name in ("soffice", "libreoffice"):
        path = shutil.which(name)
        if path:
            return path
    raise FileNotFoundError("soffice / libreoffice not found on PATH")


def render(src_path, out_path):
    with open(src_path, encoding="utf-8") as fh:
        html_doc = md_to_html(fh.read())

    base = os.path.splitext(os.path.basename(out_path))[0]
    with tempfile.TemporaryDirectory() as tmp:
        html_path = os.path.join(tmp, base + ".html")
        with open(html_path, "w", encoding="utf-8") as fh:
            fh.write(html_doc)
        profile = "file://" + os.path.join(tmp, "loprofile")
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
        render(src, out)
        print(f"{os.path.relpath(src, ROOT)} -> {os.path.relpath(out, ROOT)}")
        return 0

    made = 0
    for suf in LANG_SUFFIXES:
        src = os.path.join(ROOT, "docs", f"FLYER{suf}.md")
        if not os.path.isfile(src):
            continue
        out = os.path.join(ROOT, "docs", f"FLYER{suf}.odt")
        render(src, out)
        print(f"  wrote {os.path.relpath(out, ROOT)}")
        made += 1
    print(f"done: {made} ODT(s)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
