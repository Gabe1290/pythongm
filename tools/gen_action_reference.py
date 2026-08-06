#!/usr/bin/env python3
"""Generate wiki/Full-Action-Reference[_<lang>].md from the live ACTION_TYPES registry.

The hand-written action reference drifted badly from the code (wrong action
names, ~35 of 109 actions, whole categories missing). This regenerates it from
the single source of truth so it can never silently drift again: re-run it
whenever actions change.

    py -3.12 tools/gen_action_reference.py            # English
    py -3.12 tools/gen_action_reference.py fr de      # + French + German

It loads plugins/extensions first so plugin actions (Audio) and extension
actions (3D View) are included exactly as the IDE's action picker shows them.

Localized editions are FULL translations: action display names, descriptions
and parameter notes are translated via the tables in ``tools/action_ref_i18n.py``,
keyed by the stable action *name* (not the display text). Anything missing from a
table falls back to English and is reported at the end of the run, so a newly
added action is never silently half-translated — exactly the drift the generator
exists to prevent.
"""
import io
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO))

from events.plugin_loader import load_all_plugins  # noqa: E402

load_all_plugins()
from events.action_types import ACTION_TYPES  # noqa: E402
from tools.action_ref_i18n import LANGS  # noqa: E402

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


class Tr:
    """Translation provider for one language. ``en`` is a no-op pass-through."""

    def __init__(self, lang: str):
        self.lang = lang
        self.data = LANGS.get(lang, {})
        self.missing: set[str] = set()

    def chrome(self, key: str, en: str) -> str:
        return self.data.get("chrome", {}).get(key, en)

    def category(self, cat: str) -> str:
        if self.lang == "en":
            return cat
        t = self.data.get("categories", {}).get(cat)
        if t is None:
            self.missing.add(f"category:{cat}")
            return cat
        return t

    def type_label(self, en_label: str) -> str:
        if self.lang == "en":
            return en_label
        return self.data.get("types", {}).get(en_label, en_label)

    def display(self, action) -> str:
        en = action.display_name or action.name
        if self.lang == "en":
            return en
        entry = self.data.get("actions", {}).get(action.name)
        if not entry or not entry.get("display"):
            self.missing.add(f"action.display:{action.name}")
            return en
        return entry["display"]

    def desc(self, action) -> str:
        en = getattr(action, "description", "") or ""
        if self.lang == "en" or not en:
            return en
        entry = self.data.get("actions", {}).get(action.name)
        if not entry or not entry.get("desc"):
            self.missing.add(f"action.desc:{action.name}")
            return en
        return entry["desc"]

    def note(self, en_note: str) -> str:
        if self.lang == "en" or not en_note:
            return en_note
        t = self.data.get("notes", {}).get(en_note)
        if t is None:
            self.missing.add(f"note:{en_note}")
            return en_note
        return t


def fmt_default(p, tr: Tr):
    d = p.default_value
    if d is None or d == "":
        return "—"
    if isinstance(d, bool):
        return tr.chrome("yes", "Yes") if d else tr.chrome("no", "No")
    if isinstance(d, list):
        return ", ".join(str(x) for x in d) or "—"
    return f"`{d}`"


def param_table(action, tr: Tr) -> str:
    params = list(getattr(action, "parameters", []) or [])
    if not params:
        return f"*{tr.chrome('params', 'Parameters')}:* {tr.chrome('none', 'none')}\n"
    rows = [f"| {tr.chrome('c_param', 'Parameter')} | {tr.chrome('c_type', 'Type')} | "
            f"{tr.chrome('c_default', 'Default')} | {tr.chrome('c_notes', 'Notes')} |",
            "|-----------|------|---------|-------|"]
    for p in params:
        ptype = tr.type_label(TYPE_LABEL.get(str(p.param_type), str(p.param_type)))
        notes = []
        if getattr(p, "description", ""):
            notes.append(tr.note(p.description))
        if getattr(p, "choices", None):
            notes.append(tr.chrome("choices", "Choices") + ": "
                         + ", ".join(f"`{c}`" for c in p.choices))
        if not getattr(p, "required", True):
            notes.append(tr.chrome("optional", "optional"))
        rows.append(f"| `{p.name}` | {ptype} | {fmt_default(p, tr)} | {'; '.join(notes) or ''} |")
    return "\n".join(rows) + "\n"


def build(lang: str = "en") -> tuple[str, set]:
    tr = Tr(lang)
    by_cat: dict[str, list] = {}
    for name, a in ACTION_TYPES.items():
        by_cat.setdefault(a.category or "Other", []).append(a)
    ordered = [c for c in CATEGORY_ORDER if c in by_cat]
    ordered += sorted(c for c in by_cat if c not in CATEGORY_ORDER)

    total = len(ACTION_TYPES)
    out = [
        f"# {tr.chrome('title', 'Full Action Reference')}",
        "",
        tr.chrome("nav", "*[Home](Home) | [Preset Guide](Preset-Guide) | "
                         "[Event Reference](Event-Reference)*"),
        "",
        tr.chrome("autogen",
                  "> **Auto-generated** from the IDE's action registry by "
                  "`tools/gen_action_reference.py` — do not edit by hand; re-run the "
                  "generator after changing actions."),
        "",
        tr.chrome("intro",
                  f"This page lists all **{total}** actions available in PyGameMaker, "
                  "exactly as they appear in the IDE's action picker (including the "
                  "Audio plugin and the 3D View extension). Actions are commands that "
                  "run when an event fires.").replace("{total}", str(total)),
        "",
        f"## {tr.chrome('categories', 'Categories')}",
        "",
    ]
    for cat in ordered:
        out.append(f"- [{tr.category(cat)}](#{anchor(cat)}) ({len(by_cat[cat])})")
    out.append("")
    out.append("---")
    out.append("")

    for cat in ordered:
        # Anchor stays English (matches the category link targets and #3d-view deep links).
        out.append(f'<a id="{anchor(cat)}"></a>')
        out.append(f"## {tr.category(cat)}")
        out.append("")
        for a in sorted(by_cat[cat], key=lambda x: x.display_name or x.name):
            out.append(f"### {tr.display(a)}")
            out.append("")
            meta = [f"| **{tr.chrome('p_name', 'Name')}** | `{a.name}` |"]
            if getattr(a, "icon", ""):
                meta.append(f"| **{tr.chrome('p_icon', 'Icon')}** | {a.icon} |")
            meta.append(f"| **{tr.chrome('p_category', 'Category')}** | {tr.category(a.category)} |")
            if getattr(a, "supports_applies_to", False):
                meta.append(f"| **{tr.chrome('p_applies', 'Applies to')}** | "
                            f"{tr.chrome('applies_val', 'self / other / object')} |")
            out.append(f"| {tr.chrome('c_property', 'Property')} | {tr.chrome('c_value', 'Value')} |")
            out.append("|----------|-------|")
            out.extend(meta)
            out.append("")
            desc = tr.desc(a)
            if desc:
                out.append(desc.rstrip("."))
                out.append("")
            out.append(param_table(a, tr))
        out.append("---")
        out.append("")

    out += [
        f"## {tr.chrome('see_also', 'See Also')}",
        "",
        tr.chrome("sa_events", "- [Event Reference](Event-Reference) — the events that trigger actions"),
        tr.chrome("sa_preset", "- [Preset Guide](Preset-Guide) — which of these actions your project's preset actually shows in the Blockly picker and the structured Actions panel"),
        tr.chrome("sa_3d", "- [3D View](3D-View) — the raycast first-person actions"),
        tr.chrome("sa_ext", "- [Extensions](Extensions) — how the 3D View actions are provided"),
        "",
    ]
    return "\n".join(out), tr.missing


def out_name(lang: str) -> str:
    return "Full-Action-Reference.md" if lang == "en" else f"Full-Action-Reference_{lang}.md"


def main():
    langs = sys.argv[1:] or ["en"]
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")
    for lang in langs:
        md, missing = build(lang)
        target = REPO / "wiki" / out_name(lang)
        target.write_text(md, encoding="utf-8")
        print(f"Wrote {target} ({len(md.splitlines())} lines, {len(ACTION_TYPES)} actions)")
        if missing:
            print(f"  [{lang}] {len(missing)} untranslated strings fell back to English:")
            for k in sorted(missing):
                print(f"    - {k}")


if __name__ == "__main__":
    main()
