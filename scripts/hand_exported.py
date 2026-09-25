"""Registry of handouts finished by hand (ODT edited + PDF exported in Writer).

The list lives in docs/handouts/hand_exported.txt. Anything listed there must
never be regenerated from its .md by a script -- that silently destroys the
drawn callouts and any other Writer-only edits (this happened to a hand-edited
.odt on 2026-09-17, and nearly to the Tutorial 1 PDFs on 2026-09-25).
"""
import os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
HANDOUTS = os.path.join(ROOT, "docs", "handouts")
MANIFEST = os.path.join(HANDOUTS, "hand_exported.txt")


def hand_exported_stems(manifest=MANIFEST):
    """Set of '<NN_slug>/<kind>.<lang>' stems (forward slashes, no extension)."""
    stems = set()
    if not os.path.exists(manifest):
        return stems
    with open(manifest, encoding="utf-8") as fh:
        for line in fh:
            line = line.strip()
            if line and not line.startswith("#"):
                stems.add(line.replace("\\", "/"))
    return stems


def stem_of(path, handouts=HANDOUTS):
    """'.../docs/handouts/01_x/student.fr.md' (or .odt/.pdf) -> '01_x/student.fr'."""
    rel = os.path.relpath(os.path.abspath(path), handouts).replace("\\", "/")
    return os.path.splitext(rel)[0]


def is_hand_exported(path, manifest=MANIFEST, handouts=HANDOUTS):
    return stem_of(path, handouts) in hand_exported_stems(manifest)
