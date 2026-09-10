#!/usr/bin/env python3
"""Render docs/RELEASE_QA_CHECKLIST.md into docs/RELEASE_QA_CHECKLIST.odt.

The release QA checklist is the one hand-verification document; testers need
it as an editable ODT so they can tick boxes and fill the sign-off matrix in
LibreOffice / Word without touching the repo.

Pipeline: Markdown -> HTML (the `markdown` package, with tables + fenced code
+ sane lists) -> a real ODT Writer document via a headless LibreOffice
(`soffice --convert-to "odt:writer8"`).

Usage:
    python3 scripts/generate_release_qa_odt.py [SRC.md [OUT.odt]]

Requires:
    pip install markdown       (3.x)
    soffice / libreoffice on PATH
"""
import os
import shutil
import subprocess
import sys
import tempfile

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), os.pardir))
DEFAULT_SRC = os.path.join(ROOT, "docs", "RELEASE_QA_CHECKLIST.md")
DEFAULT_OUT = os.path.join(ROOT, "docs", "RELEASE_QA_CHECKLIST.odt")

_STYLE = """
  body   { font-family: "DejaVu Sans","Liberation Sans",sans-serif; font-size: 10pt; color: #1c2026; }
  h1     { color: #245ca8; font-size: 22pt; margin: 0 0 6pt 0; }
  h2     { color: #245ca8; font-size: 14pt; margin: 18pt 0 5pt 0; page-break-after: avoid; }
  h3     { color: #3a3f47; font-size: 11.5pt; margin: 12pt 0 4pt 0; page-break-after: avoid; }
  p      { margin: 0 0 6pt 0; line-height: 1.35; }
  ul, ol { margin: 0 0 6pt 0; padding-left: 20pt; }
  li     { margin: 0 0 3pt 0; line-height: 1.3; }
  hr     { border: 0; border-top: 1px solid #ced4dc; margin: 10pt 0; }
  blockquote { margin: 6pt 0; padding: 4pt 10pt; border-left: 3px solid #b8c4d6;
               background-color: #f2f5fa; color: #3a3f47; }
  table  { border-collapse: collapse; width: 100%; margin: 4pt 0 8pt 0; }
  th, td { border: 1px solid #ced4dc; padding: 4pt 6pt; font-size: 9.5pt;
           vertical-align: top; text-align: left; }
  th     { background-color: #e9eff8; }
  code   { font-family: "DejaVu Sans Mono", monospace; font-size: 9pt;
           background-color: #f3f5f8; }
  pre    { background-color: #f3f5f8; border: 1px solid #ced4dc; padding: 7pt;
           font-family: "DejaVu Sans Mono", monospace; font-size: 9pt;
           white-space: pre-wrap; }
"""


def build_html(md_path):
    try:
        import markdown
    except ImportError:
        sys.exit("This script needs the `markdown` package: pip install markdown")

    md_text = open(md_path, encoding="utf-8").read()
    body = markdown.markdown(
        md_text,
        extensions=["tables", "fenced_code", "sane_lists", "md_in_html"],
        output_format="html5",
    )
    return (
        "<!DOCTYPE html><html><head><meta charset='utf-8'>"
        f"<style>{_STYLE}</style></head><body>\n{body}\n</body></html>"
    )


def convert(html_text, out_path):
    soffice = shutil.which("soffice") or shutil.which("libreoffice")
    if not soffice:
        sys.exit("soffice / libreoffice not found on PATH")

    with tempfile.TemporaryDirectory() as tmp:
        html_file = os.path.join(tmp, "release_qa.html")
        with open(html_file, "w", encoding="utf-8") as fh:
            fh.write(html_text)
        subprocess.run(
            [soffice, "--headless", "--norestore",
             # import the HTML as a Writer *text* document, not Writer/Web,
             # so the result is a real .odt and not an HTML-document template
             "--infilter=HTML (StarWriter)",
             "--convert-to", "odt:writer8", "--outdir", tmp, html_file],
            check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
        )
        produced = os.path.join(tmp, "release_qa.odt")
        if not os.path.isfile(produced):
            sys.exit("LibreOffice did not produce an ODT")
        shutil.move(produced, out_path)


def main(argv):
    src = argv[1] if len(argv) > 1 else DEFAULT_SRC
    out = argv[2] if len(argv) > 2 else DEFAULT_OUT
    convert(build_html(src), out)
    print(f"wrote {os.path.relpath(out, ROOT)}")


if __name__ == "__main__":
    main(sys.argv)
