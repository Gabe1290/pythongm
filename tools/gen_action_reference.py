#!/usr/bin/env python3
"""Generate wiki/Full-Action-Reference.md from the live ACTION_TYPES registry.

The hand-written action reference drifted badly from the code (wrong action
names, ~35 of 109 actions, whole categories missing). This regenerates it from
the single source of truth so it can never silently drift again: re-run it
whenever actions change.

    py -3.12 tools/gen_action_reference.py

It loads plugins/extensions first so plugin actions (Audio) and extension
actions (3D View) are included exactly as the IDE's action picker shows them.
"""
import io
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO))

from events.plugin_loader import load_all_plugins  # noqa: E402

load_all_plugins()
from events.action_types import ACTION_TYPES  # noqa: E402

# Category display order (IDE-ish); any category not listed is appended A-Z.
CATEGORY_ORDER = [
    "Movement", "Instance", "Score", "Room", "Timing", "Audio", "Game",
    "Control", "Grid", "Views", "3D View",
]

TYPE_LABEL = {
    "number": "Number", "float": "Number", "string": "Text", "text": "Text",
    "boolean": "Yes/No", "color": "Color", "object": "Object", "sprite": "Sprite",
    "sound": "Sound", "room": "Room", "code": "Code", "script": "Script",
    "choice": "Choice", "multi_choice": "Multiple choice",
    "action_list": "Action list",
}


def anchor(cat: str) -> str:
    return cat.lower().replace(" ", "-")


def fmt_default(p):
    d = p.default_value
    if d is None or d == "":
        return "—"
    if isinstance(d, bool):
        return "Yes" if d else "No"
    if isinstance(d, list):
        return ", ".join(str(x) for x in d) or "—"
    return f"`{d}`"


def param_table(action) -> str:
    params = list(getattr(action, "parameters", []) or [])
    if not params:
        return "*Parameters:* none\n"
    rows = ["| Parameter | Type | Default | Notes |",
            "|-----------|------|---------|-------|"]
    for p in params:
        ptype = TYPE_LABEL.get(str(p.param_type), str(p.param_type))
        notes = []
        if getattr(p, "description", ""):
            notes.append(p.description)
        if getattr(p, "choices", None):
            notes.append("Choices: " + ", ".join(f"`{c}`" for c in p.choices))
        if not getattr(p, "required", True):
            notes.append("optional")
        rows.append(f"| `{p.name}` | {ptype} | {fmt_default(p)} | {'; '.join(notes) or ''} |")
    return "\n".join(rows) + "\n"


def build() -> str:
    by_cat: dict[str, list] = {}
    for name, a in ACTION_TYPES.items():
        by_cat.setdefault(a.category or "Other", []).append(a)
    ordered = [c for c in CATEGORY_ORDER if c in by_cat]
    ordered += sorted(c for c in by_cat if c not in CATEGORY_ORDER)

    total = len(ACTION_TYPES)
    out = [
        "# Full Action Reference",
        "",
        "*[Home](Home) | [Preset Guide](Preset-Guide) | [Event Reference](Event-Reference)*",
        "",
        "> **Auto-generated** from the IDE's action registry by "
        "`tools/gen_action_reference.py` — do not edit by hand; re-run the "
        "generator after changing actions.",
        "",
        f"This page lists all **{total}** actions available in PyGameMaker, exactly "
        "as they appear in the IDE's action picker (including the Audio plugin and "
        "the 3D View extension). Actions are commands that run when an event fires.",
        "",
        "## Categories",
        "",
    ]
    for cat in ordered:
        out.append(f"- [{cat}](#{anchor(cat)}) ({len(by_cat[cat])})")
    out.append("")
    out.append("---")
    out.append("")

    for cat in ordered:
        out.append(f"## {cat}")
        out.append("")
        for a in sorted(by_cat[cat], key=lambda x: x.display_name or x.name):
            out.append(f"### {a.display_name or a.name}")
            out.append("")
            meta = [f"| **Name** | `{a.name}` |"]
            if getattr(a, "icon", ""):
                meta.append(f"| **Icon** | {a.icon} |")
            meta.append(f"| **Category** | {a.category} |")
            if getattr(a, "supports_applies_to", False):
                meta.append("| **Applies to** | self / other / object |")
            out.append("| Property | Value |")
            out.append("|----------|-------|")
            out.extend(meta)
            out.append("")
            if getattr(a, "description", ""):
                out.append(a.description.rstrip("."))
                out.append("")
            out.append(param_table(a))
        out.append("---")
        out.append("")

    out += [
        "## See Also",
        "",
        "- [Event Reference](Event-Reference) — the events that trigger actions",
        "- [Preset Guide](Preset-Guide) — which actions each preset/edition exposes",
        "- [3D View](3D-View) — the raycast first-person actions",
        "- [Extensions](Extensions) — how the 3D View actions are provided",
        "",
    ]
    return "\n".join(out)


def main():
    md = build()
    target = REPO / "wiki" / "Full-Action-Reference.md"
    target.write_text(md, encoding="utf-8")
    # UTF-8 stdout so emoji icons don't crash the Windows console.
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")
    print(f"Wrote {target} ({len(md.splitlines())} lines, {len(ACTION_TYPES)} actions)")


if __name__ == "__main__":
    main()
