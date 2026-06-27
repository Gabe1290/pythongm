#!/usr/bin/env python3
"""Render docs/test_checklist.md into a printable PDF.

Produces docs/PyGameMaker_Test_Checklist.pdf from the Markdown source so the
feature-by-feature checklist can be printed and ticked off per platform.

This is a pragmatic Markdown-subset renderer (headings, blockquotes, list
items, horizontal rules and the trailing environment table) built on fpdf2 —
not a general Markdown engine. The per-item "L [ ] M [ ] W [ ]" tri-boxes are
kept verbatim as ASCII checkboxes (that is what the source intends); inline
**bold** / *italic* / `code` markers are stripped to plain text.
"""

import os
import re

from fpdf import FPDF

ROOT = os.path.join(os.path.dirname(__file__), os.pardir)
SRC = os.path.join(ROOT, "docs", "test_checklist.md")
OUT = os.path.join(ROOT, "docs", "PyGameMaker_Test_Checklist.pdf")

FONT_FAMILY = "DejaVu"

# DejaVu ships in different locations per OS. Resolve the first directory that
# actually contains DejaVuSans.ttf so this runs on Linux, Windows and macOS.
_FONT_CANDIDATE_DIRS = [
    "/usr/share/fonts/truetype/dejavu/",                              # Debian/Ubuntu
    "/usr/share/fonts/dejavu/",                                       # Fedora/Arch
    "/usr/share/fonts/dejavu-sans-fonts/",                            # some RPM distros
    os.path.join(os.environ.get("WINDIR", r"C:\Windows"), "Fonts"),  # Windows
    "/Library/Fonts/",                                               # macOS (system)
    os.path.expanduser("~/Library/Fonts/"),                          # macOS (user)
    os.path.join(os.path.dirname(__file__), "fonts"),                # vendored fallback
]


def _resolve_font_dir():
    for d in _FONT_CANDIDATE_DIRS:
        if os.path.isfile(os.path.join(d, "DejaVuSans.ttf")):
            return d
    raise FileNotFoundError(
        "DejaVuSans.ttf not found. Install the DejaVu fonts, or copy DejaVuSans"
        "{,-Bold,-Oblique}.ttf into scripts/fonts/. Searched: "
        + ", ".join(_FONT_CANDIDATE_DIRS)
    )


FONT_DIR = _resolve_font_dir()


def inline(text):
    """Strip the inline Markdown markers we don't render with styling."""
    text = text.replace("&lt;", "<").replace("&gt;", ">").replace("&amp;", "&")
    text = re.sub(r"`([^`]*)`", r"\1", text)        # `code`
    text = re.sub(r"\*\*([^*]+)\*\*", r"\1", text)  # **bold**
    text = re.sub(r"\*([^*]+)\*", r"\1", text)        # *italic*
    return text


def merge_continuations(raw_lines):
    """Fold wrapped list-item continuation lines back onto their bullet."""
    merged = []
    for line in raw_lines:
        stripped = line.strip()
        if stripped == "":
            merged.append("")
            continue
        is_indented = line[:1] in (" ", "\t")
        prev_is_bullet = bool(merged) and merged[-1].lstrip().startswith("- ")
        if is_indented and prev_is_bullet and not stripped.startswith("|"):
            merged[-1] = merged[-1].rstrip() + " " + stripped
        else:
            merged.append(line.rstrip())
    return merged


class ChecklistPDF(FPDF):
    def __init__(self):
        super().__init__(format="A4")
        self.set_auto_page_break(auto=True, margin=15)
        self.set_margins(15, 15, 15)
        self.add_font(FONT_FAMILY, "", os.path.join(FONT_DIR, "DejaVuSans.ttf"))
        self.add_font(FONT_FAMILY, "B", os.path.join(FONT_DIR, "DejaVuSans-Bold.ttf"))
        self.add_font(FONT_FAMILY, "I", os.path.join(FONT_DIR, "DejaVuSans-Oblique.ttf"))

    def footer(self):
        self.set_y(-12)
        self.set_font(FONT_FAMILY, "I", 8)
        self.set_text_color(150, 150, 150)
        self.cell(0, 10, f"PyGameMaker Test Checklist  ·  Page {self.page_no()}/{{nb}}", align="C")

    # -- block renderers ----------------------------------------------------

    def h1(self, text):
        self.set_font(FONT_FAMILY, "B", 20)
        self.set_text_color(20, 20, 20)
        self.multi_cell(0, 10, text, new_x="LMARGIN", new_y="NEXT")
        self.ln(2)

    def h2(self, text):
        if self.get_y() > 250:
            self.add_page()
        else:
            self.ln(3)
        self.set_font(FONT_FAMILY, "B", 14)
        self.set_text_color(0, 60, 120)
        self.multi_cell(0, 8, text, new_x="LMARGIN", new_y="NEXT")
        self.set_draw_color(120, 160, 200)
        self.line(self.l_margin, self.get_y() + 0.5, self.w - self.r_margin, self.get_y() + 0.5)
        self.ln(2.5)

    def h3(self, text):
        if self.get_y() > 262:
            self.add_page()
        self.ln(1)
        self.set_font(FONT_FAMILY, "B", 11)
        self.set_text_color(40, 40, 40)
        self.multi_cell(0, 6, text, new_x="LMARGIN", new_y="NEXT")
        self.ln(0.5)

    def paragraph(self, text):
        self.set_font(FONT_FAMILY, "", 9)
        self.set_text_color(40, 40, 40)
        self.multi_cell(0, 5, text, new_x="LMARGIN", new_y="NEXT")
        self.ln(1)

    def blockquote(self, text):
        self.set_font(FONT_FAMILY, "I", 9)
        self.set_text_color(90, 90, 90)
        x0 = self.get_x()
        y0 = self.get_y()
        self.set_x(x0 + 4)
        self.multi_cell(self.epw - 4, 5, text, new_x="LMARGIN", new_y="NEXT")
        self.set_draw_color(180, 180, 180)
        self.set_line_width(0.6)
        self.line(x0 + 1, y0 + 0.5, x0 + 1, self.get_y() - 0.5)
        self.set_line_width(0.2)
        self.ln(1)

    def list_item(self, text):
        self.set_font(FONT_FAMILY, "", 9)
        self.set_text_color(30, 30, 30)
        x0 = self.l_margin
        self.set_x(x0 + 3)
        self.multi_cell(self.epw - 3, 5, text, new_x="LMARGIN", new_y="NEXT")
        self.ln(0.6)

    def hrule(self):
        self.ln(1.5)
        self.set_draw_color(210, 210, 210)
        self.line(self.l_margin, self.get_y(), self.w - self.r_margin, self.get_y())
        self.ln(2.5)

    def table(self, rows):
        if not rows:
            return
        ncols = max(len(r) for r in rows)
        width = self.epw / ncols
        for ridx, row in enumerate(rows):
            if self.get_y() > 270:
                self.add_page()
            self.set_font(FONT_FAMILY, "B" if ridx == 0 else "", 9)
            self.set_text_color(30, 30, 30)
            cells = (row + [""] * ncols)[:ncols]
            for c in cells:
                self.cell(width, 7, inline(c), border=1)
            self.ln(7)
        self.ln(2)


def render():
    with open(SRC, encoding="utf-8") as fh:
        raw = fh.read().splitlines()
    lines = merge_continuations(raw)

    pdf = ChecklistPDF()
    pdf.alias_nb_pages()
    pdf.add_page()

    table_buffer = []

    def flush_table():
        if table_buffer:
            # Drop the Markdown separator row (|---|---|).
            rows = [r for r in table_buffer if not re.fullmatch(r"[\s|:\-]+", r)]
            parsed = [[c.strip() for c in r.strip().strip("|").split("|")] for r in rows]
            pdf.table(parsed)
            table_buffer.clear()

    for line in lines:
        if line.startswith("|"):
            table_buffer.append(line)
            continue
        flush_table()

        stripped = line.strip()
        if stripped == "":
            continue
        if re.fullmatch(r"-{3,}", stripped):
            pdf.hrule()
        elif line.startswith("# "):
            pdf.h1(inline(line[2:].strip()))
        elif line.startswith("## "):
            pdf.h2(inline(line[3:].strip()))
        elif line.startswith("### "):
            pdf.h3(inline(line[4:].strip()))
        elif line.startswith(">"):
            pdf.blockquote(inline(line.lstrip(">").strip()))
        elif stripped.startswith("- "):
            pdf.list_item(inline(stripped[2:].strip()))
        else:
            pdf.paragraph(inline(stripped))

    flush_table()
    pdf.output(OUT)
    return OUT


if __name__ == "__main__":
    path = render()
    print(f"Generated: {os.path.normpath(path)}")
