#!/usr/bin/env python3
"""Add translations for the tutorial Float / Re-dock button + tooltips.

These strings were introduced when the tutorial moved into a dockable
panel with an editor-style detach. They live in the `TutorialPanel`
context. This script inserts the messages into every pygm2_*.ts file
that has a TutorialPanel context (both the split *_misc.ts and the
monolithic *.ts), skipping any source already present, then recompiles
the touched .ts files to .qm.

Idempotent — safe to re-run.
"""

import re
import subprocess
import sys
from pathlib import Path
from xml.sax.saxutils import escape

ROOT = Path(__file__).resolve().parent.parent
TRANS = ROOT / "translations"
LRELEASE = ROOT / "venv/lib/python3.12/site-packages/PySide6/lrelease"

S_FLOAT = "Float"
S_REDOCK = "Re-dock"
S_TT_FLOAT = "Detach this tutorial into its own movable window"
S_TT_DOCK = "Dock this tutorial back into the IDE"
S_TUT = "Tutorials"

# Per-language translations. Order here is the order inserted.
TR = {
    "de": {
        S_FLOAT: "Abdocken",
        S_REDOCK: "Andocken",
        S_TT_FLOAT: "Dieses Tutorial in ein eigenes verschiebbares Fenster lösen",
        S_TT_DOCK: "Dieses Tutorial wieder an die IDE andocken",
        S_TUT: "Tutorials",
    },
    "es": {
        S_FLOAT: "Desacoplar",
        S_REDOCK: "Acoplar",
        S_TT_FLOAT: "Desacoplar este tutorial en su propia ventana móvil",
        S_TT_DOCK: "Acoplar este tutorial de nuevo en el IDE",
        S_TUT: "Tutoriales",
    },
    "fr": {
        S_FLOAT: "Détacher",
        S_REDOCK: "Rattacher",
        S_TT_FLOAT: "Détacher ce tutoriel dans sa propre fenêtre déplaçable",
        S_TT_DOCK: "Rattacher ce tutoriel à l'IDE",
        S_TUT: "Tutoriels",
    },
    "it": {
        S_FLOAT: "Stacca",
        S_REDOCK: "Riaggancia",
        S_TT_FLOAT: "Stacca questo tutorial in una finestra mobile separata",
        S_TT_DOCK: "Riaggancia questo tutorial nell'IDE",
        S_TUT: "Tutorial",
    },
    "ru": {
        S_FLOAT: "Открепить",
        S_REDOCK: "Прикрепить",
        S_TT_FLOAT: "Открепить это руководство в отдельное перемещаемое окно",
        S_TT_DOCK: "Прикрепить это руководство обратно к IDE",
        S_TUT: "Руководства",
    },
    "sl": {
        S_FLOAT: "Odpni",
        S_REDOCK: "Pripni",
        S_TT_FLOAT: "Odpni to vadnico v lastno premakljivo okno",
        S_TT_DOCK: "Ponovno pripni to vadnico v IDE",
        S_TUT: "Vadnice",
    },
    "uk": {
        S_FLOAT: "Відкріпити",
        S_REDOCK: "Прикріпити",
        S_TT_FLOAT: "Відкріпити цей підручник в окреме рухоме вікно",
        S_TT_DOCK: "Прикріпити цей підручник назад до IDE",
        S_TUT: "Підручники",
    },
}

ORDER = [S_FLOAT, S_REDOCK, S_TT_FLOAT, S_TT_DOCK, S_TUT]


def lang_of(ts_path: Path) -> str:
    # pygm2_de_misc.ts -> de ; pygm2_fr.ts -> fr
    return ts_path.stem.split("_")[1]


def message_block(source: str, translation: str) -> str:
    return (
        "        <message>\n"
        f"            <source>{escape(source)}</source>\n"
        f"            <translation>{escape(translation)}</translation>\n"
        "        </message>\n"
    )


def process(ts_path: Path) -> bool:
    lang = lang_of(ts_path)
    table = TR.get(lang)
    if table is None:
        print(f"  skip {ts_path.name}: no translation table for '{lang}'")
        return False

    text = ts_path.read_text(encoding="utf-8")

    m = re.search(
        r"(<context>\s*<name>TutorialPanel</name>)(.*?)(</context>)",
        text,
        re.S,
    )
    if not m:
        print(f"  skip {ts_path.name}: no TutorialPanel context")
        return False

    head, body, tail = m.group(1), m.group(2), m.group(3)
    existing_sources = set(re.findall(r"<source>(.*?)</source>", body, re.S))

    additions = ""
    added = []
    for src in ORDER:
        if escape(src) in existing_sources or src in existing_sources:
            continue
        additions += message_block(src, table[src])
        added.append(src)

    if not additions:
        print(f"  ok   {ts_path.name}: already up to date")
        return False

    new_block = head + "\n" + additions + body + tail
    text = text[: m.start()] + new_block + text[m.end():]
    ts_path.write_text(text, encoding="utf-8")
    print(f"  +    {ts_path.name}: added {len(added)} ({', '.join(added)})")
    return True


def should_compile(ts_path: Path) -> bool:
    """Only compile a .ts whose .qm the language manager will actually use.

    The loader prefers split files (pygm2_<lang>_<group>.qm) but ONLY if
    a split set already exists; otherwise it uses the monolithic
    pygm2_<lang>.qm. Compiling a split _misc.ts for a language that has
    no split set (e.g. fr) would create a brand-new split .qm that
    hijacks the loader and drops the full monolithic translation. Guard
    against that: a split *_<group>.ts is compiled only when that
    language already uses split files (pygm2_<lang>_core.qm exists).
    """
    parts = ts_path.stem.split("_")
    if len(parts) <= 2:
        return True  # monolithic pygm2_<lang>.ts — always safe
    lang = parts[1]
    if (TRANS / f"pygm2_{lang}_core.qm").exists():
        return True
    print(f"  skip {ts_path.with_suffix('.qm').name}: "
          f"'{lang}' uses the monolithic .qm (no split set)")
    return False


def compile_qm(ts_path: Path) -> None:
    if not should_compile(ts_path):
        return
    qm_path = ts_path.with_suffix(".qm")
    subprocess.run(
        [str(LRELEASE), str(ts_path), "-qm", str(qm_path)],
        check=True,
        capture_output=True,
        text=True,
    )
    print(f"  qm   {qm_path.name}")


def main() -> int:
    ts_files = sorted(
        p for p in TRANS.glob("pygm2_*.ts")
        if "<name>TutorialPanel</name>" in p.read_text(encoding="utf-8")
    )
    print(f"Found {len(ts_files)} .ts files with a TutorialPanel context\n")
    touched = []
    for ts in ts_files:
        if process(ts):
            touched.append(ts)
    print()
    for ts in touched:
        compile_qm(ts)
    print(f"\nDone. {len(touched)} file(s) updated and recompiled.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
