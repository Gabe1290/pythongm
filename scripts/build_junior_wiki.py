#!/usr/bin/env python3
"""Build the Junior-edition wiki pages and downloads from docs/junior/.

Sources: docs/junior/{student,teacher}.{en,fr}.md (+ .pdf/.odt next to them)
and the lessons under docs/junior/lessons/<name>/ (same file names).
Outputs: wiki/Junior-Student-Handout[_fr].md, wiki/Junior-Teacher-Guide[_fr].md,
wiki/Junior-Maze-Lesson-{Student,Teacher}[_fr].md,
wiki/Junior-Treasure-Lesson-{Student,Teacher}[_fr].md and wiki/downloads/Junior-*
({pdf,odt}, plus each lesson's starter/finished project zips from
tools/junior_maze_lesson.py and tools/junior_maze2_lesson.py). Never hand-edit the outputs: edit the
.md (or hand-edit the .odt and fold it back, docs/TUTORIAL_HANDOUT_WORKFLOW.md)
and re-run. Publishing to the live wiki is a separate, explicit step
(scripts/sync_wiki.sh).

Usage: python3 scripts/build_junior_wiki.py
"""
import re
import shutil
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SRC = ROOT / "docs" / "junior"
WIKI = ROOT / "wiki"
DL = WIKI / "downloads"

PAGES = {
    "student": "Junior-Student-Handout",
    "teacher": "Junior-Teacher-Guide",
}
# docs/junior/lessons/<name>/: (page name per kind, extra download links).
LESSONS = {
    "maze": {
        "pages": {"student": "Junior-Maze-Lesson-Student",
                  "teacher": "Junior-Maze-Lesson-Teacher"},
        "extra": {"en": [("Starter project", "Junior-Maze-Starter.zip"),
                         ("Finished project", "Junior-Maze-Finished.zip")],
                  "fr": [("Projet de départ", "Junior-Maze-Starter.zip"),
                         ("Projet terminé", "Junior-Maze-Finished.zip")]},
    },
    "maze2": {
        "pages": {"student": "Junior-Treasure-Lesson-Student",
                  "teacher": "Junior-Treasure-Lesson-Teacher"},
        "extra": {"en": [("Starter project", "Junior-Treasure-Starter.zip"),
                         ("Finished project", "Junior-Treasure-Finished.zip")],
                  "fr": [("Projet de départ", "Junior-Treasure-Starter.zip"),
                         ("Projet terminé", "Junior-Treasure-Finished.zip")]},
    },
}
NAV = {
    "en": "*[Home](Home) | [Teacher resources](Teacher-Resources)*",
    "fr": "*[Accueil](Home_fr) | [Ressources pour enseignants](Teacher-Resources_fr)*",
}
DOWNLOAD = {"en": "**Download:**", "fr": "**Télécharger :**"}
NOTES_HEADING = {"en": "## My Notes", "fr": "## Mes notes"}


IMG_DST = WIKI / "images" / "junior"


def copy_images():
    """docs/junior/images/** -> wiki/images/junior/** (the French shots sit
    directly in images/, the English ones in images/en/)."""
    for im in (SRC / "images").rglob("*.png"):
        dst = IMG_DST / im.relative_to(SRC / "images")
        dst.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(im, dst)


_IMG_LINK = re.compile(r'\]\(images/([^)\s]+?)(?:\s+"[^"]*")?\)')


def wiki_images(text: str) -> str:
    """``![alt](images/x.png "55%")`` -> ``![alt](images/junior/x.png)``: the
    wiki has its own image folder, and a width hint is print-only."""
    return _IMG_LINK.sub(lambda m: f"](images/junior/{m.group(1)})", text)


def body(md: str, lang: str):
    """Source markdown -> wiki markdown: drop the print-only notes block and
    the H1 (re-emitted by the caller)."""
    md = wiki_images(md)
    lines = md.splitlines()
    title = lines[0].lstrip("# ").strip()
    text = "\n".join(lines[1:]).strip("\n")
    text = re.sub(r"^\[\[notes:\d+\]\]\s*$", "", text, flags=re.M)
    text = text.replace(NOTES_HEADING[lang], "").rstrip() + "\n"
    return title, text


def build_set(src_dir, pages, extra_links=None):
    """One student handout + one teacher guide, in every language."""
    for lang in ("en", "fr"):
        suffix = "" if lang == "en" else "_fr"
        for kind, page in pages.items():
            src = src_dir / f"{kind}.{lang}.md"
            title, text = body(src.read_text(encoding="utf-8"), lang)
            links = []
            for ext in ("pdf", "odt"):
                f = src_dir / f"{kind}.{lang}.{ext}"
                if f.exists():
                    shutil.copyfile(f, DL / f"{page}{suffix}.{ext}")
                    links.append(f"[{ext.upper()}](downloads/{page}{suffix}.{ext})")
            if kind == "teacher":
                for label, filename in (extra_links or {}).get(lang, []):
                    links.append(f"[{label}](downloads/{filename})")
            out = (f"# {title}\n\n{NAV[lang]}\n\n"
                   f"{DOWNLOAD[lang]} {' · '.join(links)}\n\n---\n\n{text}")
            (WIKI / f"{page}{suffix}.md").write_text(out, encoding="utf-8", newline="\n")
            print("wrote", f"{page}{suffix}.md")


def main():
    DL.mkdir(exist_ok=True)
    copy_images()
    build_set(SRC, PAGES)
    sys.path.insert(0, str(ROOT / "tools"))
    import junior_maze_lesson
    import junior_maze2_lesson
    junior_maze_lesson.write_zips(DL)
    junior_maze2_lesson.write_zips(DL)
    for name, lesson in LESSONS.items():
        build_set(SRC / "lessons" / name, lesson["pages"], lesson["extra"])


if __name__ == "__main__":
    main()
