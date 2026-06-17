#!/usr/bin/env python3
"""Add translations for the Welcome-tab sample-game names.

The bundled sample names ("Maze — Level 1", "Platform — Level 3", ...) live in
SAMPLE_PROJECTS (widgets/welcome_tab.py) as data, and are translated at the
call site via self.tr(label) under the WelcomeTab context. They had no .ts
entries, so non-English IDEs showed them in English. This script inserts the
source + per-language translation into the WelcomeTab context of every
pygm2_*.ts that has it, skipping any source already present, then recompiles
the touched .ts to the .qm the language manager will actually load.

Translations are generated from a single per-language term table (maze word /
platform word / level word) so there's one source of truth and the level
numbers can't drift.

Idempotent — safe to re-run. Mirrors scripts/add_python_operator_translations.py.
"""

import subprocess
import sys
import re
from pathlib import Path
from xml.sax.saxutils import escape

ROOT = Path(__file__).resolve().parent.parent
TRANS = ROOT / "translations"

CONTEXT = "WelcomeTab"

# (kind, level) for every sample exposed in SAMPLE_PROJECTS. The English label
# below MUST byte-match the label string in widgets/welcome_tab.py.
SAMPLES = [
    ("Maze", 1), ("Maze", 2), ("Maze", 3),
    ("Platform", 1), ("Platform", 2), ("Platform", 3),
]

# Per language: (maze word, platform word, level word). "Level" is kept as-is
# for German (idiomatic in gaming). The em-dash separator (—, U+2014) matches
# the English source exactly.
TERMS = {
    "fr": ("Labyrinthe", "Plateforme", "Niveau"),
    "de": ("Labyrinth", "Plattform", "Level"),
    "es": ("Laberinto", "Plataforma", "Nivel"),
    "it": ("Labirinto", "Piattaforma", "Livello"),
    "ru": ("Лабиринт", "Платформа", "Уровень"),
    "sl": ("Labirint", "Platforma", "Stopnja"),
    "uk": ("Лабіринт", "Платформа", "Рівень"),
}


def en_label(kind: str, level: int) -> str:
    return f"{kind} — Level {level}"


def translate(lang: str, kind: str, level: int) -> str:
    maze, platform, lvl = TERMS[lang]
    word = maze if kind == "Maze" else platform
    return f"{word} — {lvl} {level}"


SOURCES = [en_label(k, n) for k, n in SAMPLES]


def table_for(lang: str) -> dict:
    return {en_label(k, n): translate(lang, k, n) for k, n in SAMPLES}


def find_lrelease() -> str:
    home = Path.home()
    # Windows .exe candidates first — the synced venv/ is a Linux artifact
    # (ELF binaries) and raises WinError 193 if invoked on Windows.
    win_first = sys.platform.startswith("win")
    win = [
        ROOT / "venv_py312/Scripts/pyside6-lrelease.exe",
        ROOT / "venv/Scripts/pyside6-lrelease.exe",
    ]
    posix = [
        home / ".local/lib/python3.11/site-packages/PySide6/lrelease",
        home / ".local/lib/python3.12/site-packages/PySide6/lrelease",
        home / ".local/lib/python3.10/site-packages/PySide6/lrelease",
        ROOT / "venv/lib/python3.12/site-packages/PySide6/lrelease",
        ROOT / "venv/lib/python3.11/site-packages/PySide6/lrelease",
    ]
    # On Windows, never offer the POSIX venv paths: the Dropbox-synced Linux
    # venv/ ships ELF `lrelease` files that exist on disk but raise WinError
    # 193 when executed. Use only the .exe candidates, then the package fallback.
    candidates = win if win_first else (posix + win)
    for c in candidates:
        if c.exists():
            return str(c)
    # The packaged PySide6 ships the tool as lrelease.exe on Windows and
    # lrelease on POSIX — try both names in the installed package dir.
    try:
        import PySide6
        pkg = Path(PySide6.__file__).parent
        for name in ("lrelease.exe", "pyside6-lrelease.exe", "lrelease"):
            p = pkg / name
            if p.exists():
                return str(p)
    except Exception:
        pass
    raise SystemExit("Could not find a working PySide6 lrelease.")


def lang_of(ts_path: Path) -> str:
    return ts_path.stem.split("_")[1]


def message_block(source: str, translation: str) -> str:
    return (
        "        <message>\n"
        f"            <source>{escape(source)}</source>\n"
        f"            <translation>{escape(translation)}</translation>\n"
        "        </message>\n"
    )


def insert_into_context(text: str, context: str, sources, table) -> tuple:
    """Return (new_text, added_count) for the named context block."""
    m = re.search(
        rf"(<context>\s*<name>{re.escape(context)}</name>)(.*?)(</context>)",
        text, re.S)
    if not m:
        return text, 0
    head, body, tail = m.group(1), m.group(2), m.group(3)
    existing = set(re.findall(r"<source>(.*?)</source>", body, re.S))
    additions = ""
    added = 0
    for src in sources:
        if escape(src) in existing or src in existing:
            continue
        additions += message_block(src, table[src])
        added += 1
    if not added:
        return text, 0
    new_block = head + "\n" + additions + body + tail
    return text[:m.start()] + new_block + text[m.end():], added


def process(ts_path: Path) -> bool:
    lang = lang_of(ts_path)
    if lang not in TERMS:
        return False
    table = table_for(lang)
    text = ts_path.read_text(encoding="utf-8")
    text, added = insert_into_context(text, CONTEXT, SOURCES, table)
    if added:
        ts_path.write_text(text, encoding="utf-8")
        print(f"  +    {ts_path.name}: added {added} message(s)")
        return True
    print(f"  ok   {ts_path.name}: already up to date / no {CONTEXT} context")
    return False


def should_compile(ts_path: Path) -> bool:
    """Compile only the .qm the language manager will actually load.

    Split *_<group>.ts is compiled only when that language already uses a split
    set (pygm2_<lang>_core.qm exists); otherwise compiling it would create a
    split .qm that hijacks the loader away from the monolithic one. Monolithic
    pygm2_<lang>.ts is always safe.
    """
    parts = ts_path.stem.split("_")
    if len(parts) <= 2:
        return True
    lang = parts[1]
    if (TRANS / f"pygm2_{lang}_core.qm").exists():
        return True
    print(f"  skip {ts_path.with_suffix('.qm').name}: "
          f"'{lang}' uses the monolithic .qm (no split set)")
    return False


def main() -> int:
    lrelease = find_lrelease()
    print(f"Using lrelease: {lrelease}\n")
    ts_files = sorted(
        p for p in TRANS.glob("pygm2_*.ts")
        if f"<name>{CONTEXT}</name>" in p.read_text(encoding="utf-8"))
    print(f"Found {len(ts_files)} candidate .ts file(s)\n")
    touched = [ts for ts in ts_files if process(ts)]
    print()
    # Compile every candidate the loader will use (not just the ones changed
    # this run) so the .qm stay in sync even after a partial/crashed prior run.
    # lrelease is deterministic, so unchanged .ts recompile to identical .qm.
    compiled = 0
    for ts in ts_files:
        if not should_compile(ts):
            continue
        qm = ts.with_suffix(".qm")
        subprocess.run([lrelease, str(ts), "-qm", str(qm)],
                       check=True, capture_output=True, text=True)
        print(f"  qm   {qm.name}")
        compiled += 1
    print(f"\nDone. {len(touched)} .ts updated, {compiled} .qm compiled.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
