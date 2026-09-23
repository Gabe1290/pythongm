#!/usr/bin/env python3
"""Publish the tutorial handouts/guides/worksheets as wiki pages + downloads.

Source of truth: docs/handouts/<NN_slug>/{student,teacher,worksheet}.<en|fr>.md
(plus optional images and hand-edited .odt drafts alongside), and the course
overview docs/handouts/course_overview.<lang>.md. answer_key.<lang>.md is
ALSO generated (by scripts/extract_worksheet_answer_keys.py, called below) --
it is a slice of teacher.<lang>.md's own "Worksheet Answer Key" section, not
a second hand-authored source; edit the teacher guide, not this file.

Output (all under wiki/, then pushed by scripts/sync_wiki.sh):
    Student-Handout-<NN>-<slug>[_fr].md     Teacher-Guide-<NN>-<slug>[_fr].md
    Worksheet-<NN>-<slug>[_fr].md           Answer-Key-<NN>-<slug>[_fr].md
    Teacher-Resources[_fr].md (landing)     images/handouts/...
    downloads/<same stem>.pdf / .odt

The wiki pages and downloads are GENERATED -- edit the docs/handouts sources.

Usage:  python scripts/build_teacher_wiki.py [--no-pdf]
"""
import glob
import importlib.util
import os
import re
import shutil
import subprocess
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(ROOT, "docs", "handouts")
WIKI = os.path.join(ROOT, "wiki")
KINDS = {  # kind -> (wiki prefix, label en, label fr)
    "student": ("Student-Handout", "Student handout", "Fiche élève"),
    "worksheet": ("Worksheet", "Worksheet", "Feuille d'exercices"),
    "answer_key": ("Answer-Key", "Answer key", "Corrigé"),
    "teacher": ("Teacher-Guide", "Teacher guide", "Guide de l'enseignant"),
}
LANGS = {"en": "", "fr": "_fr"}
HOME = {"en": ("Home", "Home", "Teacher-Resources", "Teacher resources"),
        "fr": ("Home_fr", "Accueil", "Teacher-Resources_fr", "Ressources pour enseignants")}
DL_LABEL = {"en": "Download:", "fr": "Télécharger :"}
SOLUTIONS_LABEL = {"en": "Reference projects (ZIP)", "fr": "Projets de référence (ZIP)"}
ANSWER_KEY_POINTER = {"en": "For teachers:", "fr": "Pour les enseignant·e·s :"}
NOTES = {"en": "My notes", "fr": "Mes notes"}
CALLOUT = {"en": {"TIP": "Tip", "INFO": "Info", "DONE": "Done"},
           "fr": {"TIP": "Astuce", "INFO": "Info", "DONE": "Réussi"}}


def stem(kind, nn_slug, lang):
    return f"{KINDS[kind][0]}-{nn_slug.replace('_', '-')}{LANGS[lang]}"


def convert(md, lang, img_dir_rel):
    """Custom handout markup -> GitHub-flavoured Markdown."""
    out, lines, i = [], md.splitlines(), 0

    def gap():
        if out and out[-1].strip():
            out.append("")

    while i < len(lines):
        ln = lines[i]
        m = re.match(r"^> (TIP|INFO|DONE): ?(.*)$", ln)
        if m:
            gap()
            out.append(f"> **{CALLOUT[lang][m.group(1)]}:** {m.group(2)}")
        elif re.match(r"^\[\[notes:(\d+)\]\]$", ln):
            n = int(re.match(r"^\[\[notes:(\d+)\]\]$", ln).group(1))
            out.extend(["<br>", ""] * min(n, 6))
        elif re.match(r"^!\[.*\]\(.+\)$", ln):
            out.append(re.sub(r"\]\((?!http)([^)]+)\)", lambda mm: f"]({img_dir_rel}/{mm.group(1)})", ln))
        elif ln.startswith("|"):
            gap()
            block = []
            while i < len(lines) and lines[i].startswith("|"):
                block.append(lines[i])
                i += 1
            i -= 1
            if len(block) > 1 and not re.match(r"^\|[\s\-:|]+\|?$", block[1]):
                cols = block[0].count("|") - 1
                block.insert(1, "|" + "---|" * cols)
            out.extend(block)
            out.append("")
        else:
            out.append(ln)
        i += 1
    return "\n".join(out) + "\n"


def _refresh_answer_keys():
    """Regenerate docs/handouts/*/answer_key.<lang>.md from each teacher guide's
    own "Worksheet Answer Key" section (single source of truth stays the
    teacher guide -- see scripts/extract_worksheet_answer_keys.py)."""
    spec = importlib.util.spec_from_file_location(
        "extract_worksheet_answer_keys", os.path.join(ROOT, "scripts", "extract_worksheet_answer_keys.py"))
    mod = importlib.util.module_from_spec(spec)
    sys.modules["extract_worksheet_answer_keys"] = mod
    spec.loader.exec_module(mod)
    mod.build()


def _build_solutions():
    """Checkpoint project zips (tools/tutorial_reference_projects.py) -> wiki/downloads/solutions/."""
    spec = importlib.util.spec_from_file_location(
        "tutorial_reference_projects", os.path.join(ROOT, "tools", "tutorial_reference_projects.py"))
    mod = importlib.util.module_from_spec(spec)
    sys.modules["tutorial_reference_projects"] = mod
    spec.loader.exec_module(mod)
    mod.build_checkpoint_zips(os.path.join(WIKI, "downloads", "solutions"))


def title_of(md):
    for ln in md.splitlines():
        if ln.startswith("# "):
            return ln[2:].strip()
    return "Untitled"


def build(make_pdf=True):
    os.makedirs(os.path.join(WIKI, "downloads"), exist_ok=True)
    catalogue = {}  # nn_slug -> {lang: {kind: (stem, title)}}
    _refresh_answer_keys()
    _build_solutions()
    for d in sorted(glob.glob(os.path.join(SRC, "[0-9][0-9]_*"))):
        nn_slug = os.path.basename(d)
        for src in sorted(glob.glob(os.path.join(d, "*.md"))):
            kind, lang, _ = os.path.basename(src).split(".")
            if kind not in KINDS or lang not in LANGS:
                continue
            md = open(src, encoding="utf-8").read()
            name = stem(kind, nn_slug, lang)
            home, home_l, res, res_l = HOME[lang]
            downloads = []
            if make_pdf:
                subprocess.run([sys.executable, os.path.join(ROOT, "scripts", "generate_tutorial_handouts_pdf.py"), src],
                               check=True, stdout=subprocess.DEVNULL)
            odt = src[:-2] + "odt"
            if make_pdf and not os.path.exists(odt) and shutil.which("soffice"):
                # never regenerate an existing .odt: it may hold a human's hand edits
                subprocess.run([sys.executable, os.path.join(ROOT, "scripts", "generate_tutorial_handouts_odt.py"), src],
                               check=True, stdout=subprocess.DEVNULL)
            for ext in ("pdf", "odt"):
                f = src[:-2] + ext
                if os.path.exists(f):
                    shutil.copy(f, os.path.join(WIKI, "downloads", f"{name}.{ext}"))
                    downloads.append(f"[{ext.upper()}](downloads/{name}.{ext})")
            zip_rel = f"downloads/solutions/{nn_slug}_checkpoints.zip"
            if kind == "teacher" and os.path.exists(os.path.join(WIKI, zip_rel)):
                downloads.append(f"[{SOLUTIONS_LABEL[lang]}]({zip_rel})")
            ak_link = ""
            if kind == "worksheet":
                # answer_key sorts before worksheet, so it is already catalogued
                ak = catalogue.get(nn_slug, {}).get(lang, {}).get("answer_key")
                if ak:
                    ak_label = KINDS["answer_key"][1 if lang == "en" else 2]
                    ak_link = f"\n**{ANSWER_KEY_POINTER[lang]}** [{ak_label}]({ak[0]})\n"
            imgs = glob.glob(os.path.join(d, "*.png"))
            if imgs:
                dst = os.path.join(WIKI, "images", "handouts", nn_slug)
                os.makedirs(dst, exist_ok=True)
                for im in imgs:
                    shutil.copy(im, dst)
            body = convert(md, lang, f"images/handouts/{nn_slug}")
            first, rest = body.split("\n", 1)
            banner = f"*[{home_l}]({home}) | [{res_l}]({res})*"
            dl = f"\n**{DL_LABEL[lang]}** " + " · ".join(downloads) + "\n" if downloads else ""
            open(os.path.join(WIKI, name + ".md"), "w", encoding="utf-8", newline="\n").write(
                f"{first}\n\n{banner}\n{dl}{ak_link}\n---\n{rest}")
            catalogue.setdefault(nn_slug, {}).setdefault(lang, {})[kind] = (name, title_of(md))
    for lang in LANGS:
        write_landing(lang, catalogue)
    return catalogue


def write_landing(lang, catalogue):
    ov = os.path.join(SRC, f"course_overview.{lang}.md")
    head = open(ov, encoding="utf-8").read() if os.path.exists(ov) else f"# {HOME[lang][3]}\n"
    hdr = ["Tutorial", "Student handout", "Worksheet", "Answer key", "Teacher guide"] if lang == "en" else \
          ["Tutoriel", "Fiche élève", "Feuille d'exercices", "Corrigé", "Guide de l'enseignant"]
    rows = [f"| {' | '.join(hdr)} |", "|---|---|---|---|---|"]
    for nn_slug in sorted(catalogue):
        kinds = catalogue[nn_slug].get(lang, {})
        if not kinds:
            continue
        cells = [f"[{KINDS[k][1 if lang == 'en' else 2]}]({kinds[k][0]})" if k in kinds else "—"
                 for k in ("student", "worksheet", "answer_key", "teacher")]
        rows.append(f"| {nn_slug.replace('_', ' ', 1).replace('_', ' ')} | " + " | ".join(cells) + " |")
    title, _, rest = head.partition("\n")
    home, home_l = HOME[lang][0], HOME[lang][1]
    text = f"{title}\n\n*[{home_l}]({home})*\n\n---\n{rest}\n\n## " + \
           ("All resources" if lang == "en" else "Toutes les ressources") + "\n\n" + "\n".join(rows) + "\n"
    open(os.path.join(WIKI, HOME[lang][2] + ".md"), "w", encoding="utf-8", newline="\n").write(text)


if __name__ == "__main__":
    cat = build(make_pdf="--no-pdf" not in sys.argv)
    print(f"built {sum(len(k) for v in cat.values() for k in v.values())} pages for {len(cat)} tutorial(s)")
