#!/usr/bin/env python3
"""Render docs/FLYER.md into docs/FLYER.pdf -- the one-sheet promo flyer.

A pragmatic Markdown-subset renderer (title, subtitle, section headings,
horizontal rules, bold-lead paragraphs, a single pipe table and a fenced
code block) built on fpdf2 -- not a general Markdown engine. Kept close to
scripts/generate_checklist_pdf.py's cross-platform font resolution so it runs
on Linux, Windows and macOS. A Noto Sans CJK face is registered as a glyph
fallback so the "Available in N languages" line (日本語 / 中文) renders.

Usage:
    python3 scripts/generate_flyer_pdf.py [SRC.md [OUT.pdf]]

Default: docs/FLYER.md -> docs/FLYER.pdf  (also generates the *_XX.md siblings
when run with no arguments).
"""

import os
import re
import sys

from fpdf import FPDF

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), os.pardir))

# --- font resolution -------------------------------------------------------

_SANS_DIRS = [
    "/usr/share/fonts/truetype/dejavu/",                              # Debian/Ubuntu
    "/usr/share/fonts/dejavu/",                                       # Fedora/Arch
    "/usr/share/fonts/dejavu-sans-fonts/",                            # some RPM distros
    os.path.join(os.environ.get("WINDIR", r"C:\Windows"), "Fonts"),  # Windows
    "/Library/Fonts/",                                               # macOS (system)
    os.path.expanduser("~/Library/Fonts/"),                          # macOS (user)
    os.path.join(os.path.dirname(__file__), "fonts"),                # vendored fallback
]

_CJK_CANDIDATES = [
    "/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc",
    "/usr/share/fonts/opentype/noto/NotoSansCJKsc-Regular.otf",
    "/usr/share/fonts/truetype/noto/NotoSansCJK-Regular.ttc",
    "/usr/share/fonts/noto-cjk/NotoSansCJK-Regular.ttc",
    "/Library/Fonts/NotoSansCJKsc-Regular.otf",
    "/System/Library/Fonts/PingFang.ttc",                             # macOS built-in CJK
    "C:\\Windows\\Fonts\\msgothic.ttc",
    os.path.join(os.path.dirname(__file__), "fonts", "NotoSansCJK-Regular.ttc"),
]


def _resolve(name):
    for d in _SANS_DIRS:
        p = os.path.join(d, name)
        if os.path.isfile(p):
            return p
    raise FileNotFoundError(
        f"{name} not found. Install the DejaVu fonts or drop the .ttf into "
        "scripts/fonts/. Searched: " + ", ".join(_SANS_DIRS)
    )


def _resolve_cjk():
    for p in _CJK_CANDIDATES:
        if os.path.isfile(p):
            return p
    return None


# --- palette -------------------------------------------------------------

ACCENT = (36, 92, 168)     # headings / title
INK = (28, 32, 38)         # body text
MUTED = (96, 104, 114)     # subtitle, footer
RULE = (206, 212, 220)     # horizontal rules, table borders
CODE_BG = (243, 245, 248)
HEAD_BG = (233, 239, 248)   # table header fill


class Flyer(FPDF):
    def __init__(self):
        super().__init__(format="A4")
        self.set_margins(20, 18, 20)
        self.set_auto_page_break(True, margin=18)

        self.add_font("body", "", _resolve("DejaVuSans.ttf"))
        self.add_font("body", "B", _resolve("DejaVuSans-Bold.ttf"))
        self.add_font("body", "I", _resolve("DejaVuSans-Oblique.ttf"))
        self.add_font("body", "BI", _resolve("DejaVuSans-BoldOblique.ttf"))
        self.add_font("mono", "", _resolve("DejaVuSansMono.ttf"))

        cjk = _resolve_cjk()
        if cjk:
            self.add_font("cjk", "", cjk)
            self.set_fallback_fonts(["cjk"])

        self.set_page_background((255, 255, 255))
        self.add_page()

    # -- primitives ------------------------------------------------------

    def footer(self):
        self.set_y(-14)
        self.set_font("body", "I", 7.5)
        self.set_text_color(*MUTED)
        self.cell(0, 5, f"Page {self.page_no()}", align="C")

    def render_rule(self):
        self.ln(2.5)
        self.set_draw_color(*RULE)
        self.set_line_width(0.3)
        y = self.get_y()
        self.line(self.l_margin, y, self.w - self.r_margin, y)
        self.ln(3.5)

    def render_title(self, text):
        self.set_font("body", "B", 26)
        self.set_text_color(*ACCENT)
        self.multi_cell(0, 11, text, new_x="LMARGIN", new_y="NEXT")
        self.ln(0.5)

    def render_subtitle(self, text):
        self.set_font("body", "B", 12.5)
        self.set_text_color(*MUTED)
        self.multi_cell(0, 7, text, new_x="LMARGIN", new_y="NEXT")
        self.ln(1)

    def render_heading(self, text):
        self.ln(3)
        self.set_font("body", "B", 14)
        self.set_text_color(*ACCENT)
        self.multi_cell(0, 8, text, new_x="LMARGIN", new_y="NEXT")
        self.ln(1.5)

    def render_para(self, text):
        self.set_font("body", "", 10)
        self.set_text_color(*INK)
        self.multi_cell(0, 5.6, text, markdown=True, new_x="LMARGIN", new_y="NEXT")
        self.ln(2.2)

    def render_code(self, lines):
        self.ln(1)
        self.set_font("mono", "", 9.5)
        self.set_text_color(*INK)
        pad = 2.6
        line_h = 5.4
        total_h = line_h * len(lines) + pad * 2
        x0, y0 = self.l_margin, self.get_y()
        self.set_fill_color(*CODE_BG)
        self.set_draw_color(*RULE)
        self.set_line_width(0.2)
        self.rect(x0, y0, self.w - self.l_margin - self.r_margin, total_h, style="DF")
        self.set_xy(x0 + pad, y0 + pad)
        for ln_ in lines:
            self.set_x(x0 + pad)
            self.cell(0, line_h, ln_, new_x="LMARGIN", new_y="NEXT")
        self.set_y(y0 + total_h)
        self.ln(3)

    def render_table(self, rows):
        head, body = rows[0], rows[1:]
        self.ln(1)
        avail = self.w - self.l_margin - self.r_margin
        w0 = 40.0
        w1 = avail - w0
        self.set_font("body", "B", 9.5)
        self.set_text_color(*INK)
        self.set_fill_color(*HEAD_BG)
        self.set_draw_color(*RULE)
        self.set_line_width(0.25)
        self._row(head, [w0, w1], fill=True, bold=True)
        self.set_font("body", "", 9.5)
        for r in body:
            self._row(r, [w0, w1], fill=False, bold=False)
        self.ln(3)

    def _row(self, cells, widths, fill, bold):
        line_h = 5.2
        x0 = self.l_margin
        y0 = self.get_y()
        # measure tallest cell
        heights = []
        for txt, w in zip(cells, widths):
            n = len(self.multi_cell(w - 3, line_h, txt, dry_run=True, output="LINES",
                                    markdown=True))
            heights.append(max(1, n) * line_h + 2.2)
        h = max(heights)
        if y0 + h > self.h - self.b_margin:
            self.add_page()
            y0 = self.get_y()
        x = x0
        for txt, w in zip(cells, widths):
            self.rect(x, y0, w, h, style="DF" if fill else "D")
            self.set_xy(x + 1.5, y0 + 1.1)
            self.set_font("body", "B" if bold else "", 9.5)
            self.multi_cell(w - 3, line_h, txt, markdown=True,
                            new_x="RIGHT", new_y="TOP", max_line_height=line_h)
            x += w
        self.set_xy(x0, y0 + h)

    def render_footer_line(self, text):
        self.ln(1)
        self.set_font("body", "I", 8.5)
        self.set_text_color(*MUTED)
        self.multi_cell(0, 5, text, new_x="LMARGIN", new_y="NEXT")


# --- markdown parse ----------------------------------------------------


def render(src_path, out_path):
    with open(src_path, encoding="utf-8") as fh:
        raw = fh.read().replace("\r\n", "\n")

    pdf = Flyer()
    lines = raw.split("\n")
    i = 0
    n = len(lines)
    para_buf = []

    def flush_para():
        nonlocal para_buf
        if not para_buf:
            return
        text = " ".join(s.strip() for s in para_buf).strip()
        para_buf = []
        if not text:
            return
        # footer credit line: "*PyGameMaker IDE vX -- ...*"
        m = re.fullmatch(r"\*(.+)\*", text)
        if m:
            pdf.render_footer_line(m.group(1))
        else:
            pdf.render_para(text)

    while i < n:
        line = lines[i]
        stripped = line.strip()

        if stripped == "---":
            flush_para()
            pdf.render_rule()
            i += 1
            continue

        if stripped.startswith("```"):
            flush_para()
            block = []
            i += 1
            while i < n and not lines[i].strip().startswith("```"):
                block.append(lines[i].rstrip())
                i += 1
            i += 1  # closing fence
            pdf.render_code(block or [""])
            continue

        if stripped.startswith("|") and stripped.endswith("|"):
            flush_para()
            tbl = []
            while i < n and lines[i].strip().startswith("|"):
                cells = [c.strip() for c in lines[i].strip().strip("|").split("|")]
                if not re.fullmatch(r"[:\- ]+", "".join(cells)):  # skip |---|---|
                    tbl.append(cells)
                i += 1
            if tbl:
                pdf.render_table(tbl)
            continue

        if stripped.startswith("# "):
            flush_para()
            pdf.render_title(stripped[2:].strip())
            i += 1
            continue
        if stripped.startswith("### "):
            flush_para()
            pdf.render_subtitle(stripped[4:].strip())
            i += 1
            continue
        if stripped.startswith("## "):
            flush_para()
            pdf.render_heading(stripped[3:].strip())
            i += 1
            continue

        if stripped == "":
            flush_para()
            i += 1
            continue

        para_buf.append(stripped)
        i += 1

    flush_para()
    pdf.output(out_path)
    return out_path


LANG_SUFFIXES = ["", "_DE", "_ES", "_FR", "_IT", "_RU", "_SL", "_UK"]


def main(argv):
    if len(argv) >= 2:
        src = os.path.abspath(argv[1])
        out = os.path.abspath(argv[2]) if len(argv) >= 3 else os.path.splitext(src)[0] + ".pdf"
        print(f"{os.path.relpath(src, ROOT)} -> {os.path.relpath(out, ROOT)}")
        render(src, out)
        return 0

    made = 0
    for suf in LANG_SUFFIXES:
        src = os.path.join(ROOT, "docs", f"FLYER{suf}.md")
        if not os.path.isfile(src):
            continue
        out = os.path.join(ROOT, "docs", f"FLYER{suf}.pdf")
        render(src, out)
        print(f"  wrote {os.path.relpath(out, ROOT)}")
        made += 1
    print(f"done: {made} PDF(s)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
