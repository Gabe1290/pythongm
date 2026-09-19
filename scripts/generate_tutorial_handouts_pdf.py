#!/usr/bin/env python3
"""Render the Tutorial-1 student handouts / teacher guides into printable PDFs.

A pragmatic Markdown-subset renderer (title, headings, paragraphs with
**bold**, bullet/checkbox/numbered-step list items, TIP/INFO/DONE callout
boxes, a blank ruled "notes" block, a simple table, and a rule) built on
fpdf2 -- not a general Markdown engine. Font resolution mirrors
scripts/generate_flyer_pdf.py so this runs on Linux, Windows and macOS.

Extra line-level syntax beyond plain Markdown:
    - [ ] text          checkbox list item
    1. text             numbered step item (a filled circle badge)
    > TIP: text         yellow "tip" callout box (can wrap onto more
    > more text          "> "-prefixed lines)
    > INFO: text         blue "info" callout box, same wrapping rule
    > DONE: text         green "success" callout box (mirrors the in-app
                          tutorial's own .success box), same wrapping rule
    ![alt](path.png)    an image, scaled to the page's content width,
                          path relative to the source .md's own folder
    [[notes:4]]         4 blank ruled lines for handwriting

Usage:
    python3 scripts/generate_tutorial_handouts_pdf.py [SRC.md [OUT.pdf]]

Default (no arguments): renders every docs/handouts/<NN_slug>/*.md file into its
matching .pdf next to it.
"""

import glob
import os
import re
import sys

from fpdf import FPDF

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), os.pardir))
DOCS = os.path.join(ROOT, "docs")

# --- font resolution (same search order as generate_flyer_pdf.py) ---------

_SANS_DIRS = [
    "/usr/share/fonts/truetype/dejavu/",
    "/usr/share/fonts/dejavu/",
    "/usr/share/fonts/dejavu-sans-fonts/",
    os.path.join(os.environ.get("WINDIR", r"C:\Windows"), "Fonts"),
    "/Library/Fonts/",
    os.path.expanduser("~/Library/Fonts/"),
    os.path.join(os.path.dirname(__file__), "fonts"),
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


# --- palette (mirrors the in-app tutorial panel's own CSS) ----------------

ACCENT = (52, 152, 219)    # #3498db -- headings, rule
INK = (44, 62, 80)         # #2c3e50 -- title, body
MUTED = (96, 104, 114)
RULE = (222, 226, 230)     # #dee2e6
TIP_BG = (255, 243, 205)   # #fff3cd
TIP_BORDER = (255, 193, 7)  # #ffc107
INFO_BG = (209, 236, 241)  # #d1ecf1
INFO_BORDER = (23, 162, 184)  # #17a2b8
DONE_BG = (212, 237, 218)   # #d4edda -- matches the in-app tutorial's .success box
DONE_BORDER = (40, 167, 69)  # #28a745
BADGE_BG = ACCENT


class Handout(FPDF):
    def __init__(self):
        super().__init__(format="A4")
        self.set_margins(18, 16, 18)
        self.set_auto_page_break(True, margin=16)
        self.add_font("body", "", _resolve("DejaVuSans.ttf"))
        self.add_font("body", "B", _resolve("DejaVuSans-Bold.ttf"))
        self.add_font("body", "I", _resolve("DejaVuSans-Oblique.ttf"))
        self.add_page()
        self._step_counter = 0

    def footer(self):
        self.set_y(-12)
        self.set_font("body", "I", 7.5)
        self.set_text_color(*MUTED)
        self.cell(0, 5, f"{self.page_no()}", align="C")

    # -- block renderers ---------------------------------------------------

    def render_title(self, text):
        self.set_font("body", "B", 20)
        self.set_text_color(*INK)
        self.multi_cell(0, 9, text, new_x="LMARGIN", new_y="NEXT")
        self.set_draw_color(*ACCENT)
        self.set_line_width(0.6)
        y = self.get_y() + 1
        self.line(self.l_margin, y, self.w - self.r_margin, y)
        self.ln(4)

    def render_heading(self, text):
        if self.get_y() > 255:
            self.add_page()
        else:
            self.ln(2.5)
        self.set_font("body", "B", 13)
        self.set_text_color(*ACCENT)
        self.multi_cell(0, 7, text, new_x="LMARGIN", new_y="NEXT")
        self.ln(1)

    def render_subheading(self, text):
        self.ln(1)
        self.set_font("body", "B", 10.5)
        self.set_text_color(*INK)
        self.multi_cell(0, 6, text, new_x="LMARGIN", new_y="NEXT")
        self.ln(0.5)

    def render_para(self, text):
        self.set_font("body", "", 9.5)
        self.set_text_color(*INK)
        self.multi_cell(0, 5.2, text, markdown=True, new_x="LMARGIN", new_y="NEXT")
        self.ln(1.5)

    def _fits_or_break(self, h):
        """Force a page break BEFORE drawing an item that mixes a vector
        badge/checkbox with a multi_cell of text -- letting fpdf2's own
        auto-page-break trigger mid-item (inside the cell() draw of a
        step's number, say) leaves the badge on the old page while the
        text call re-triggers ITS OWN break using a now-stale y, landing
        everything on the page after next and leaving a blank page
        between (see the render_step bug this replaced)."""
        if self.get_y() + h > self.h - self.b_margin:
            self.add_page()

    def render_bullet(self, text):
        line_h = 5.2
        lines = self.multi_cell(self.epw - 8, line_h, text, dry_run=True,
                                 output="LINES", markdown=True)
        self._fits_or_break(max(1, len(lines)) * line_h + 0.8)
        x0 = self.l_margin
        self.set_xy(x0 + 4, self.get_y())
        self.set_font("body", "B", 9.5)
        self.set_text_color(*INK)
        self.cell(3, line_h, "\u2022")
        self.set_xy(x0 + 8, self.get_y())
        self.set_font("body", "", 9.5)
        self.multi_cell(self.epw - 8, line_h, text, markdown=True,
                         new_x="LMARGIN", new_y="NEXT")
        self.ln(0.8)

    def render_checkbox(self, text):
        line_h, box = 5.2, 3.6
        lines = self.multi_cell(self.epw - box - 5, line_h, text, dry_run=True,
                                 output="LINES", markdown=True)
        self._fits_or_break(max(1, len(lines)) * line_h + 1.4)
        x0 = self.l_margin
        y0 = self.get_y()
        self.set_draw_color(*INK)
        self.set_line_width(0.35)
        self.rect(x0 + 1, y0 + 1.1, box, box)
        self.set_xy(x0 + box + 5, y0)
        self.set_font("body", "", 9.5)
        self.set_text_color(*INK)
        self.multi_cell(self.epw - box - 5, line_h, text, markdown=True,
                         new_x="LMARGIN", new_y="NEXT")
        self.ln(1.4)

    def render_step(self, number, text):
        line_h, d = 5.2, 6.2
        lines = self.multi_cell(self.epw - d - 5, line_h, text, dry_run=True,
                                 output="LINES", markdown=True)
        self._fits_or_break(max(1, len(lines)) * line_h + 1.6)
        x0 = self.l_margin
        y0 = self.get_y()
        self.set_fill_color(*BADGE_BG)
        self.ellipse(x0 + 1, y0, d, d, style="F")
        self.set_xy(x0 + 1, y0 + 0.9)
        self.set_font("body", "B", 8.5)
        self.set_text_color(255, 255, 255)
        self.cell(d, d - 1.6, str(number), align="C")
        self.set_xy(x0 + d + 5, y0)
        self.set_font("body", "", 9.5)
        self.set_text_color(*INK)
        self.multi_cell(self.epw - d - 5, line_h, text, markdown=True,
                         new_x="LMARGIN", new_y="NEXT")
        self.ln(1.6)

    def render_callout(self, kind, text):
        bg, border = {
            "TIP": (TIP_BG, TIP_BORDER),
            "INFO": (INFO_BG, INFO_BORDER),
            "DONE": (DONE_BG, DONE_BORDER),
        }.get(kind, (TIP_BG, TIP_BORDER))
        self.ln(0.5)
        pad = 3.0
        self.set_font("body", "", 9.5)
        avail_w = self.epw - pad * 2 - 3
        lines = self.multi_cell(avail_w, 5.2, text, dry_run=True, output="LINES",
                                 markdown=True)
        h = max(1, len(lines)) * 5.2 + pad * 2
        x0, y0 = self.l_margin, self.get_y()
        if y0 + h > self.h - self.b_margin:
            self.add_page()
            y0 = self.get_y()
        self.set_fill_color(*bg)
        self.rect(x0, y0, self.epw, h, style="F")
        self.set_fill_color(*border)
        self.rect(x0, y0, 1.6, h, style="F")
        self.set_xy(x0 + pad + 2, y0 + pad)
        self.set_text_color(*INK)
        self.multi_cell(avail_w, 5.2, text, markdown=True, new_x="LMARGIN", new_y="TOP")
        self.set_y(y0 + h)
        self.ln(3)

    def render_notes_lines(self, n):
        self.ln(1)
        self.set_draw_color(*RULE)
        self.set_line_width(0.25)
        for _ in range(n):
            y = self.get_y() + 6
            self.line(self.l_margin, y, self.w - self.r_margin, y)
            self.set_y(y)
        self.ln(3)

    def render_image(self, path):
        """Scale to the full content width, preserving aspect ratio; if the
        page doesn't have room left, start a fresh one (mirrors the
        page-break-before-drawing discipline _fits_or_break already
        established for badge+text items, since fpdf2's own image() call
        has no auto-page-break of its own)."""
        from PIL import Image as PILImage
        with PILImage.open(path) as im:
            iw, ih = im.size
        w = self.epw
        h = w * ih / iw
        y0 = self.get_y()
        avail = self.h - self.b_margin - y0
        if h > avail:
            self.add_page()
            y0 = self.get_y()
            avail = self.h - self.b_margin - y0
            if h > avail:
                h, w = avail, avail * iw / ih
        self.image(path, x=self.l_margin + (self.epw - w) / 2, y=y0, w=w, h=h)
        self.set_y(y0 + h)
        self.ln(3)

    def render_rule(self):
        self.ln(1.5)
        self.set_draw_color(*RULE)
        self.set_line_width(0.3)
        y = self.get_y()
        self.line(self.l_margin, y, self.w - self.r_margin, y)
        self.ln(3)

    def render_table(self, rows):
        head, body = rows[0], rows[1:]
        ncols = len(head)
        avail = self.epw
        w0 = avail * 0.32
        widths = [w0] + [(avail - w0) / (ncols - 1)] * (ncols - 1) if ncols > 1 else [avail]
        self.ln(1)
        self.set_draw_color(*RULE)
        self.set_line_width(0.25)
        self._table_row(head, widths, fill=True, bold=True)
        for r in body:
            self._table_row(r, widths, fill=False, bold=False)
        self.ln(3)

    def _table_row(self, cells, widths, fill, bold):
        line_h = 5.0
        x0 = self.l_margin
        y0 = self.get_y()
        heights = []
        for txt, w in zip(cells, widths):
            n = len(self.multi_cell(w - 3, line_h, txt, dry_run=True, output="LINES",
                                     markdown=True))
            heights.append(max(1, n) * line_h + 2.2)
        h = max(heights)
        if y0 + h > self.h - self.b_margin:
            self.add_page()
            y0 = self.get_y()
        if fill:
            self.set_fill_color(*INFO_BG)
        x = x0
        self.set_text_color(*INK)
        for txt, w in zip(cells, widths):
            self.rect(x, y0, w, h, style="DF" if fill else "D")
            self.set_xy(x + 1.5, y0 + 1.1)
            self.set_font("body", "B" if bold else "", 9)
            self.multi_cell(w - 3, line_h, txt, markdown=True,
                             new_x="RIGHT", new_y="TOP", max_line_height=line_h)
            x += w
        self.set_xy(x0, y0 + h)


# --- markdown-subset parse -------------------------------------------------

_BLOCK_START = re.compile(
    r"^(#{1,3}\s|-\s|>|\|.*\||\d+\.\s|---$|\[\[notes:\d+\]\]$|!\[)"
)
_IMAGE = re.compile(r"!\[([^\]]*)\]\(([^)]+)\)$")


def _merge_soft_wraps(lines):
    """Fold a block-start line's soft-wrapped continuation lines back onto
    it (plain Markdown paragraph-join semantics: consecutive non-blank
    lines belong together until a blank line or a new block starts) --
    otherwise a checkbox/bullet/step item wrapped across source lines for
    readability loses its second line to a stray, wrongly-indented
    paragraph instead of staying part of the item."""
    merged = []
    for line in lines:
        stripped = line.strip()
        if stripped == "" or _BLOCK_START.match(stripped) or not merged:
            merged.append(line)
        else:
            merged[-1] = merged[-1].rstrip() + " " + stripped
    return merged


def render(src_path, out_path):
    with open(src_path, encoding="utf-8") as fh:
        raw = fh.read().replace("\r\n", "\n")

    # fpdf2's markdown=True only understands **bold**/__italic__/--underline--
    # -- backtick `code` spans would render as literal backticks, so strip
    # them to plain text (there are no fenced code blocks in these docs).
    raw = re.sub(r"`([^`\n]*)`", r"\1", raw)

    pdf = Handout()
    lines = _merge_soft_wraps(raw.split("\n"))
    i, n = 0, len(lines)
    para_buf = []

    def flush_para():
        nonlocal para_buf
        if not para_buf:
            return
        text = " ".join(s.strip() for s in para_buf).strip()
        para_buf = []
        if text:
            pdf.render_para(text)

    while i < n:
        line = lines[i]
        stripped = line.strip()

        if stripped == "---":
            flush_para()
            pdf.render_rule()
            i += 1
            continue

        m = re.fullmatch(r"\[\[notes:(\d+)\]\]", stripped)
        if m:
            flush_para()
            pdf.render_notes_lines(int(m.group(1)))
            i += 1
            continue

        if stripped.startswith(">"):
            flush_para()
            block = []
            while i < n and lines[i].strip().startswith(">"):
                block.append(lines[i].strip().lstrip(">").strip())
                i += 1
            text = " ".join(block).strip()
            kind = "TIP"
            m2 = re.match(r"(TIP|INFO|DONE):\s*(.*)", text)
            if m2:
                kind, text = m2.group(1), m2.group(2)
            pdf.render_callout(kind, text)
            continue

        if stripped.startswith("|") and stripped.endswith("|"):
            flush_para()
            tbl = []
            while i < n and lines[i].strip().startswith("|"):
                cells = [c.strip() for c in lines[i].strip().strip("|").split("|")]
                if not re.fullmatch(r"[:\- ]+", "".join(cells)):
                    tbl.append(cells)
                i += 1
            if tbl:
                pdf.render_table(tbl)
            continue

        m_img = _IMAGE.match(stripped)
        if m_img:
            flush_para()
            img_path = os.path.join(os.path.dirname(src_path), m_img.group(2))
            pdf.render_image(img_path)
            i += 1
            continue

        if stripped.startswith("# "):
            flush_para()
            pdf.render_title(stripped[2:].strip())
            i += 1
            continue
        if stripped.startswith("### "):
            flush_para()
            pdf.render_subheading(stripped[4:].strip())
            i += 1
            continue
        if stripped.startswith("## "):
            flush_para()
            pdf.render_heading(stripped[3:].strip())
            i += 1
            continue

        if stripped.startswith("- [ ] "):
            flush_para()
            pdf.render_checkbox(stripped[6:].strip())
            i += 1
            continue
        if stripped.startswith("- "):
            flush_para()
            pdf.render_bullet(stripped[2:].strip())
            i += 1
            continue
        m3 = re.match(r"(\d+)\.\s+(.*)", stripped)
        if m3:
            flush_para()
            pdf.render_step(int(m3.group(1)), m3.group(2).strip())
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


def main(argv):
    if len(argv) >= 2:
        src = os.path.abspath(argv[1])
        out = os.path.abspath(argv[2]) if len(argv) >= 3 else os.path.splitext(src)[0] + ".pdf"
        print(f"{os.path.relpath(src, ROOT)} -> {os.path.relpath(out, ROOT)}")
        render(src, out)
        return 0

    made = 0
    for src in sorted(glob.glob(os.path.join(DOCS, "handouts", "*", "*.md"))):
        out = os.path.splitext(src)[0] + ".pdf"
        render(src, out)
        print(f"  wrote {os.path.relpath(out, ROOT)}")
        made += 1
    print(f"done: {made} PDF(s)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
