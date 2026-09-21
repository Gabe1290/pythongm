#!/usr/bin/env python3
"""Render the one-page A4 "download PyGameMaker at home" student flyer (EN + FR).

Output: docs/STUDENT_DOWNLOAD_FLYER.pdf and docs/STUDENT_DOWNLOAD_FLYER_FR.pdf
(docs/*.pdf is gitignored, like the promo flyer: regenerate on demand).

The content is the two dicts below -- edit the text or the URL constants
there, then re-run:

    python scripts/generate_student_download_flyer.py

Needs fpdf2 and segno (dev-tool-only, like the other scripts/ generators:
``pip install fpdf2 segno``). Fonts are resolved like generate_flyer_pdf.py.
The QR code points at the ``releases/latest`` page, so the flyer never goes
stale when a new version is published; the asset file names are the ones
.github/workflows/build.yml publishes. Fails loudly if the layout overflows
one page.
"""
import importlib.util
import os
import sys
import tempfile

import segno
from fpdf import FPDF

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), os.pardir))
DOCS = os.path.join(ROOT, "docs")

RELEASES_URL = "https://github.com/Gabe1290/pythongm/releases/latest"
RELEASES_SHORT = "github.com/Gabe1290/pythongm/releases/latest"
WIKI_SHORT = "github.com/Gabe1290/pythongm/wiki"

_spec = importlib.util.spec_from_file_location(
    "generate_flyer_pdf", os.path.join(ROOT, "scripts", "generate_flyer_pdf.py"))
_gf = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_gf)          # reuse its font resolution only

NAVY = (44, 62, 80)
ACCENT = (36, 92, 168)
INK = (28, 32, 38)
MUTED = (96, 104, 114)
SOFT = (240, 244, 250)
RULE = (200, 208, 220)
WARN_BG = (255, 246, 219)
WARN_LINE = (230, 190, 80)
WHITE = (255, 255, 255)

CONTENT = {
    "en": {
        "file": "STUDENT_DOWNLOAD_FLYER.pdf",
        "title": "PyGameMaker",
        "subtitle": "Make your own video games at home — free!",
        "intro": ("The same program we use at school: draw characters, build levels and bring "
                  "your games to life with drag-and-drop blocks. **No coding needed, no account, "
                  "no cost.** Works on Windows, Mac and Linux."),
        "s1": "Download it",
        "scan": "Scan the QR code with your phone, or type this address into a browser on your computer:",
        "pick": "On that page, scroll down to **Assets** and download **ONE** file for your computer:",
        "rows": [
            ("Windows 10 / 11", "PyGameMaker.exe", ""),
            ("Mac — Apple chip (M1, M2, M3, M4…)", "PyGameMaker-macOS-ARM.zip", ""),
            ("Mac — Intel processor", "PyGameMaker-macOS-Intel.zip", ""),
            ("Linux (64-bit)", "PyGameMaker-Linux.tar.gz", ""),
        ],
        "warn": ("**Not sure which Mac you have?** Apple menu → About This Mac. "
                 "“Chip: Apple M…” = Apple chip; “Processor: Intel” = Intel.  "
                 "**Big file** (about 270–330 MB): download it on Wi-Fi.  "
                 "Ignore the files called “Source code” and the .tar.gz with a version number: they are not the program."),
        "s2": "Open it",
        "cols": [
            ("Windows", [
                "Double-click **PyGameMaker.exe**. There is nothing to install.",
                "If a blue window says **“Windows protected your PC”**: click **More info**, then **Run anyway**.",
                "First start takes a few seconds. Keep the file in a folder you can find again (for example Documents).",
            ]),
            ("Mac", [
                "Double-click the .zip to unzip it, then drag **PyGameMaker** into **Applications**.",
                "First time: **right-click (or Ctrl+click) the app → Open → Open**.",
                "Still blocked? **System Settings → Privacy & Security**, scroll down, click **Open Anyway**.",
            ]),
            ("Linux", [
                "Open a terminal in your Downloads folder and type:",
                "`tar -xzf PyGameMaker-Linux.tar.gz`",
                "`./PyGameMaker`",
                "If it will not start: `chmod +x PyGameMaker`. On Ubuntu/Debian also try `sudo apt install libxcb-cursor0`.",
            ]),
        ],
        "s3": "Start creating",
        "s3_lines": [
            "Open **Help → Tutorials** and begin with **Getting Started**: each tutorial builds a real game step by step.",
            "Change the language of the program in **Tools → Language** (11 languages, including English and Français).",
            "Save often (**Ctrl+S**). Your project is a folder: copy it to a USB stick or cloud drive to work on it at school and at home.",
        ],
        "footer_help": "Questions? Ask your teacher, or read the guides: " + WIKI_SHORT,
        "footer_lic": "PyGameMaker is free, open-source software (MIT licence).",
    },
    "fr": {
        "file": "STUDENT_DOWNLOAD_FLYER_FR.pdf",
        "title": "PyGameMaker",
        "subtitle": "Crée tes propres jeux vidéo à la maison — gratuitement !",
        "intro": ("Le même programme qu’à l’école : dessine des personnages, construis des niveaux et "
                  "donne vie à tes jeux avec des blocs à glisser-déposer. **Pas besoin de programmer, "
                  "pas de compte, pas de frais.** Fonctionne sous Windows, Mac et Linux."),
        "s1": "Télécharge-le",
        "scan": "Scanne le code QR avec ton téléphone, ou tape cette adresse dans un navigateur sur ton ordinateur :",
        "pick": "Sur cette page, descends jusqu’à **Assets** et télécharge **UN SEUL** fichier pour ton ordinateur :",
        "rows": [
            ("Windows 10 / 11", "PyGameMaker.exe", ""),
            ("Mac — puce Apple (M1, M2, M3, M4…)", "PyGameMaker-macOS-ARM.zip", ""),
            ("Mac — processeur Intel", "PyGameMaker-macOS-Intel.zip", ""),
            ("Linux (64 bits)", "PyGameMaker-Linux.tar.gz", ""),
        ],
        "warn": ("**Tu ne sais pas quel Mac tu as ?** Menu Pomme → À propos de ce Mac. "
                 "« Puce : Apple M… » = puce Apple ; « Processeur : Intel » = Intel.  "
                 "**Gros fichier** (environ 270 à 330 Mo) : télécharge-le en Wi-Fi.  "
                 "Ignore les fichiers « Source code » et le .tar.gz avec un numéro de version : ce n’est pas le programme."),
        "s2": "Ouvre-le",
        "cols": [
            ("Windows", [
                "Double-clique sur **PyGameMaker.exe**. Il n’y a rien à installer.",
                "Si une fenêtre bleue indique **« Windows a protégé votre ordinateur »** : clique sur **Informations complémentaires**, puis **Exécuter quand même**.",
                "Le premier démarrage prend quelques secondes. Garde le fichier dans un dossier facile à retrouver (par exemple Documents).",
            ]),
            ("Mac", [
                "Double-clique sur le .zip pour le décompresser, puis glisse **PyGameMaker** dans **Applications**.",
                "La première fois : **clic droit (ou Ctrl+clic) sur l’app → Ouvrir → Ouvrir**.",
                "Toujours bloqué ? **Réglages Système → Confidentialité et sécurité**, descends, clique sur **Ouvrir quand même**.",
            ]),
            ("Linux", [
                "Ouvre un terminal dans ton dossier Téléchargements et tape :",
                "`tar -xzf PyGameMaker-Linux.tar.gz`",
                "`./PyGameMaker`",
                "S’il ne démarre pas : `chmod +x PyGameMaker`. Sous Ubuntu/Debian, essaie aussi `sudo apt install libxcb-cursor0`.",
            ]),
        ],
        "s3": "Lance-toi",
        "s3_lines": [
            "Ouvre **Aide → Tutoriels** et commence par **Premiers pas** : chaque tutoriel construit un vrai jeu pas à pas.",
            "Change la langue du programme dans **Outils → Langue** (11 langues, dont English et Français).",
            "Enregistre souvent (**Ctrl+S**). Ton projet est un dossier : copie-le sur une clé USB ou un espace en ligne pour travailler à l’école et à la maison.",
        ],
        "footer_help": "Des questions ? Demande à ton enseignant·e, ou lis les guides : " + WIKI_SHORT,
        "footer_lic": "PyGameMaker est un logiciel libre et gratuit (licence MIT).",
    },
}


class Flyer(FPDF):
    def __init__(self):
        super().__init__(format="A4")
        self.set_margins(14, 10, 14)
        self.set_auto_page_break(False)
        self.add_font("body", "", _gf._resolve("DejaVuSans.ttf"))
        self.add_font("body", "B", _gf._resolve("DejaVuSans-Bold.ttf"))
        self.add_font("body", "I", _gf._resolve("DejaVuSans-Oblique.ttf"))
        self.add_font("body", "BI", _gf._resolve("DejaVuSans-BoldOblique.ttf"))
        self.add_font("mono", "", _gf._resolve("DejaVuSansMono.ttf"))
        self.add_font("mono", "B", _gf._resolve("DejaVuSansMono-Bold.ttf"))
        self.add_page()

    # ---- helpers ---------------------------------------------------------

    def para(self, x, y, w, text, size=9.5, lh=4.6, color=INK, style="", font="body"):
        """Draw a markdown-bold paragraph; returns its height."""
        self.set_font(font, style, size)
        self.set_text_color(*color)
        self.set_xy(x, y)
        self.multi_cell(w, lh, text, markdown=True, align="L", new_x="LEFT", new_y="NEXT")
        return self.get_y() - y

    def height(self, w, text, size=9.5, lh=4.6, font="body", style=""):
        self.set_font(font, style, size)
        return self.multi_cell(w, lh, text, markdown=True, align="L", dry_run=True, output="HEIGHT")

    def step_heading(self, n, text, y):
        self.set_fill_color(*ACCENT)
        self.ellipse(14, y, 8, 8, style="F")
        self.set_font("body", "B", 11)
        self.set_text_color(*WHITE)
        self.set_xy(14, y + 0.6)
        self.cell(8, 6.8, str(n), align="C")
        self.set_font("body", "B", 14)
        self.set_text_color(*ACCENT)
        self.set_xy(25, y + 0.4)
        self.cell(0, 7.2, text)
        return y + 10

    def code_line(self, x, y, w, text):
        self.set_fill_color(235, 239, 245)
        self.set_font("mono", "", 7.3)
        self.set_text_color(*INK)
        self.rect(x, y, w, 5.4, style="F")
        self.set_xy(x + 1.5, y + 0.5)
        self.cell(w - 3, 4.4, text)
        return 6.4


def _plain(t):
    """Inline `code` -> bold (the markdown renderer has no code span)."""
    parts = t.split("`")
    return "".join(("**" + p + "**") if i % 2 else p for i, p in enumerate(parts))


def render(lang, out_path):
    c = CONTENT[lang]
    pdf = Flyer()
    W = pdf.w
    L, R = 14, W - 14
    inner = R - L

    # header band
    pdf.set_fill_color(*NAVY)
    pdf.rect(0, 0, W, 30, style="F")
    pdf.set_font("body", "B", 28)
    pdf.set_text_color(*WHITE)
    pdf.set_xy(L, 5)
    pdf.cell(0, 12, c["title"])
    pdf.set_font("body", "", 13)
    pdf.set_text_color(214, 226, 240)
    pdf.set_xy(L, 17.5)
    pdf.cell(0, 8, c["subtitle"])

    y = 35
    y += pdf.para(L, y, inner, c["intro"], size=10, lh=4.9) + 3.5

    # ---- step 1 ----------------------------------------------------------
    y = pdf.step_heading(1, c["s1"], y)
    qr_size = 32
    with tempfile.TemporaryDirectory() as tmp:
        qr_png = os.path.join(tmp, "qr.png")
        segno.make(RELEASES_URL, error="m").save(qr_png, scale=12, border=1, dark="#1c2026")
        pdf.image(qr_png, x=L, y=y, w=qr_size, h=qr_size)
    tx = L + qr_size + 5
    tw = R - tx
    yy = y
    yy += pdf.para(tx, yy, tw, c["scan"], size=9.5) + 1.2
    pdf.set_font("mono", "B", 9.6)
    pdf.set_text_color(*ACCENT)
    pdf.set_xy(tx, yy)
    pdf.cell(tw, 6, RELEASES_SHORT)
    yy += 8.4
    yy += pdf.para(tx, yy, tw, c["pick"], size=9.5)
    y = max(y + qr_size, yy) + 2.5

    # download table
    row_h = 7.4
    col1, col2 = 88, inner - 88
    for i, (os_name, fname, _) in enumerate(c["rows"]):
        pdf.set_fill_color(*(SOFT if i % 2 == 0 else WHITE))
        pdf.rect(L, y, inner, row_h, style="F")
        pdf.set_draw_color(*RULE)
        pdf.rect(L, y, inner, row_h)
        pdf.set_font("body", "B", 9.6)
        pdf.set_text_color(*INK)
        pdf.set_xy(L + 2.5, y + 0.9)
        pdf.cell(col1, 5.6, os_name)
        pdf.set_font("mono", "B", 9.6)
        pdf.set_text_color(*ACCENT)
        pdf.set_xy(L + col1, y + 0.9)
        pdf.cell(col2, 5.6, fname)
        y += row_h
    y += 2.5

    # warning box
    h = pdf.height(inner - 6, c["warn"], size=8.6, lh=4.1)
    pdf.set_fill_color(*WARN_BG)
    pdf.set_draw_color(*WARN_LINE)
    pdf.rect(L, y, inner, h + 4, style="DF")
    pdf.para(L + 3, y + 2, inner - 6, c["warn"], size=8.6, lh=4.1)
    y += h + 4 + 4.5

    # ---- step 2 ----------------------------------------------------------
    y = pdf.step_heading(2, c["s2"], y)
    gap = 4
    fr = (0.31, 0.31, 0.38)
    cws = [(inner - 2 * gap) * f for f in fr]
    heights = []
    for (title, lines), cw in zip(c["cols"], cws):
        hh = 8
        for ln in lines:
            if ln.startswith("`"):
                hh += 6.4
            else:
                hh += pdf.height(cw - 6, "• " + _plain(ln), size=8.4, lh=4.0) + 1.5
        heights.append(hh + 1)
    box_h = max(heights)
    for i, (title, lines) in enumerate(c["cols"]):
        cw = cws[i]
        x = L + sum(cws[:i]) + i * gap
        pdf.set_fill_color(*SOFT)
        pdf.set_draw_color(*RULE)
        pdf.rect(x, y, cw, box_h, style="DF")
        pdf.set_fill_color(*ACCENT)
        pdf.rect(x, y, cw, 6.4, style="F")
        pdf.set_font("body", "B", 10.5)
        pdf.set_text_color(*WHITE)
        pdf.set_xy(x + 3, y + 0.8)
        pdf.cell(cw - 6, 5, title)
        yy = y + 8.2
        for ln in lines:
            if ln.startswith("`"):
                yy += pdf.code_line(x + 3, yy, cw - 6, ln.strip("`"))
            else:
                yy += pdf.para(x + 3, yy, cw - 6, "• " + _plain(ln), size=8.4, lh=4.0) + 1.5
    y += box_h + 5

    # ---- step 3 ----------------------------------------------------------
    y = pdf.step_heading(3, c["s3"], y)
    for ln in c["s3_lines"]:
        y += pdf.para(L + 2, y, inner - 2, "• " + ln, size=9.0, lh=4.3) + 1.2

    # footer
    pdf.set_draw_color(*RULE)
    pdf.line(L, 279.5, R, 279.5)
    pdf.set_font("body", "", 8)
    pdf.set_text_color(*MUTED)
    pdf.set_xy(L, 281.5)
    pdf.cell(inner, 4, c["footer_help"])
    pdf.set_xy(L, 285.5)
    pdf.cell(inner, 4, c["footer_lic"])

    if y > 277:
        raise SystemExit(f"{lang}: content overflows the page (y={y:.1f} mm)")
    if pdf.page_no() != 1:
        raise SystemExit(f"{lang}: flyer spilled onto {pdf.page_no()} pages")
    pdf.output(out_path)
    return y


def main(argv):
    os.makedirs(DOCS, exist_ok=True)
    for lang in CONTENT:
        out = os.path.join(DOCS, CONTENT[lang]["file"])
        end = render(lang, out)
        print(f"wrote {os.path.relpath(out, ROOT)} (content ends at y={end:.1f} mm of 277)")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
