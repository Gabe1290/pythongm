#!/usr/bin/env python3
"""Regenerate the data tables in extensions/microbit/export_html5.js.

The font, built-in images and melodies are data; they are generated from the
Python modules so the HTML5 export can never drift from the IDE's simulator.
The block between the ``generated:tables`` markers is replaced in place:

    py -3.12 tools/gen_microbit_js_tables.py          # rewrite
    py -3.12 tools/gen_microbit_js_tables.py --check  # exit 1 if stale
"""
import io
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

TARGET = ROOT / "extensions" / "microbit" / "export_html5.js"
BEGIN = "// <generated:tables> -- tools/gen_microbit_js_tables.py; do not edit by hand"
END = "// </generated:tables>"


def build_block() -> str:
    from extensions.microbit.font import GLYPHS
    from extensions.microbit.images import IMAGES
    from extensions.microbit.melodies import MELODIES
    from extensions.microbit.events import GESTURE_NAMES, _FIXED

    # Glyphs are keyed by character code: bracket and quote characters as keys
    # would confuse the (string-unaware) brace-balance guard on this file.
    def dump(name, value):
        return f"const {name} = {json.dumps(value, ensure_ascii=False, sort_keys=False)};"

    return "\n".join([
        BEGIN,
        dump("MB_GLYPHS", {str(ord(ch)): list(rows) for ch, rows in GLYPHS.items()}),
        dump("MB_IMAGES", {name: list(rows) for name, rows in IMAGES.items()}),
        dump("MB_MELODIES", {name: list(notes) for name, notes in MELODIES.items()}),
        # (kind, detail) -> event name; "kind:detail" keys, "" for a None detail.
        dump("MB_EVENT_FIXED", {f"{k}:{'' if d is None else d}": n for (k, d), n in _FIXED.items()}),
        # simulator gesture name -> the suffix of microbit_gesture_<suffix>
        dump("MB_GESTURE_EVENTS", {g: e[0] for g, e in GESTURE_NAMES.items()}),
        END,
    ])


def splice(text: str, block: str) -> str:
    start = text.index(BEGIN)
    end = text.index(END, start) + len(END)
    return text[:start] + block + text[end:]


def main(argv) -> int:
    text = io.open(TARGET, encoding="utf-8", newline="").read().replace("\r\n", "\n")
    new = splice(text, build_block())
    if "--check" in argv:
        return 0 if new == text else 1
    if new != text:
        io.open(TARGET, "w", encoding="utf-8", newline="\n").write(new)
        print("rewrote", TARGET)
    else:
        print("up to date")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
