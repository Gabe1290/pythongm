#!/usr/bin/env python3
"""Rename English action / event / parameter names in a non-English document to the names the IDE
shows in that language (docs/CORE_NAMES_I18N_PLAN.md U8).

Only whole bold spans are touched -- ``<strong>…</strong>``, ``<b>…</b>`` (HTML) and ``**…**``
(Markdown) -- because that is how the documents mark a UI name; running prose is never rewritten.

    python tools/convert_doc_names.py fr FILE...            # report what would change
    python tools/convert_doc_names.py fr FILE... --write    # apply

Rules:
- an action name -> the language's action name;
- a menu path "A > B" whose last part is an action ("Control > Execute Code", or an old GameMaker
  tab such as "Main2 > Show Message") -> "<the action's current category> > <action>", as the Add
  Action menu shows it;
- an event name, or a path ending in one ("Step > Step") -> the event name;
- a parameter label -> its translation, but a one-word label only when "=" follows the bold span
  ("**Object** = obj_gem"): lone words like "Visible", "Objects" or "Sprite" usually name the asset
  tree or a checkbox, not a parameter. "Relative" is always the action dialog's checkbox;
- a category written as its own bold span before an arrow ("**Room** → **Next Room**") -> the
  language's category name.

With ``--tables`` (Markdown), two more exact-match passes: a heading whose whole text is an action or
event name ("### Game Start"), and a table cell whose whole text is one ("| Game Start | `game_start` |",
or "Keyboard (held) → Right Arrow", where only the event part changes). Key columns in backticks and
prose cells are never touched.

With ``--prose`` (Markdown), running text too, but only MULTI-word action / event names ("Set
Horizontal Speed", "Game Start"): a single word like "Step" or "Draw" is too often ordinary English
("Step 6"). Code (backticks, fences) and image lines are skipped.
"""
ALWAYS_PARAMS = {"Relative"}
# Names that are also something else in running text: "Snap to Grid" is the room editor's setting too.
PROSE_SKIP = {"Snap to Grid"}
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

SPAN = re.compile(r"(<(strong|b)>)(.*?)(</\2>)|(\*\*)(?!\s)(.+?)(?<!\s)(\*\*)", re.S)
SEP = re.compile(r"\s*(&gt;|>|→)\s*")
# "the X block": a Blockly block, whose label comes from the Blockly tables and can differ from the
# panel's action name -- such spans are reported, never rewritten automatically.
BLOCK_WORD = re.compile(r"(bloc|block|bloque|blocco|блок|бло)\w*\W{0,3}$", re.IGNORECASE)


def load_names():
    from events import plugin_loader
    plugin_loader.is_extension_enabled = lambda folder, default=True: True
    plugin_loader.load_all_plugins()
    from events.action_types import ACTION_TYPES
    from events.event_types import EVENT_TYPES
    actions, events, params = {}, {}, {}
    for key, a in ACTION_TYPES.items():
        actions.setdefault(a.display_name, (key, a.category))
        params.setdefault("__categories__", set()).add(a.category)
        for p in a.parameters:
            params.setdefault(p.display_name, p.display_name)
    for key, e in EVENT_TYPES.items():
        events.setdefault(e.display_name, key)
    return actions, events, params


class Converter:
    def __init__(self, lang, tables=False, prose=False):
        self.tables = tables
        self.prose = prose
        from config.ui_names import language_table
        self.t = language_table(lang)
        self.actions, self.events, self.params = load_names()

    def _action(self, english):
        key, category = self.actions[english]
        name = self.t.get("core.action", {}).get(key)
        cat = self.t.get("core.category", {}).get(category)
        return name, cat

    def _event(self, english):
        return self.t.get("core.event", {}).get(self.events[english])

    def convert_inner(self, inner, followed_by_equals, followed_by_arrow=False):
        """The translated text for one bold span, or None to leave it alone."""
        html = "&gt;" in inner
        parts = [p for p in SEP.split(inner.strip()) if p and not SEP.fullmatch(p)]
        last = parts[-1].strip()
        if len(parts) > 1:
            if last in self.actions:
                name, cat = self._action(last)
                if name and cat:
                    return f"{cat} {'&gt;' if html else '>'} {name}"
            if last in self.events:
                return self._event(last)
            return None
        if last in self.actions:
            return self._action(last)[0]
        if last in self.events:
            return self._event(last)
        if last in self.params and (" " in last or followed_by_equals or last in ALWAYS_PARAMS):
            return self.t.get("core.param", {}).get(last)
        if followed_by_arrow and last in self.params.get("__categories__", ()):
            return self.t.get("core.category", {}).get(last)
        return None

    def convert(self, text):
        changes = []
        self.skipped = []

        def repl(m):
            if m.group(1):
                open_, inner, close = m.group(1), m.group(3), m.group(4)
            else:
                open_, inner, close = m.group(5), m.group(6), m.group(7)
            after = text[m.end():m.end() + 8]
            arrow = bool(re.match(r"\s*(→|&gt;|->)\s*(\*\*|<strong>|<b>)", after))
            new = self.convert_inner(inner, after.lstrip().startswith("="), arrow)
            if not new or new == inner:
                return m.group(0)
            before = re.sub(r"<[^>]+>", "", text[max(0, m.start() - 40):m.start()])
            if BLOCK_WORD.search(before):
                self.skipped.append(inner)
                return m.group(0)
            changes.append((inner, new))
            return f"{open_}{new}{close}"

        text = SPAN.sub(repl, text)
        if self.tables:
            text = self._tables_and_headings(text, changes)
        if self.prose:
            text = self._prose(text, changes)
        return text, changes

    def _prose(self, text, changes):
        names = {n for n in list(self.actions) + list(self.events) if " " in n and n not in PROSE_SKIP}
        names = {n for n in names if self._exact(n) and self._exact(n) != n}
        if not names:
            return text
        rx = re.compile(r"(?<![\w-])(" + "|".join(re.escape(n) for n in sorted(names, key=len, reverse=True))
                        + r")(?![\w-])")
        out, fence = [], False
        for line in text.split("\n"):
            if line.lstrip().startswith("```"):
                fence = not fence
            if fence or line.lstrip().startswith("![") or line.lstrip().startswith("#"):
                out.append(line)
                continue
            parts = re.split(r"(`[^`]*`|\]\([^)]*\))", line)
            for i in range(0, len(parts), 2):
                def sub(m):
                    new = self._exact(m.group(1))
                    changes.append((m.group(1), new))
                    return new
                parts[i] = rx.sub(sub, parts[i])
            out.append("".join(parts))
        return "\n".join(out)

    def _exact(self, cell):
        """An exact action/event name (or "Event → key") translated, else None."""
        head, arrow, rest = cell.partition(" → ")
        if arrow and head in self.events:
            name = self._event(head)
            return f"{name} → {rest}" if name else None
        if cell in self.events:
            return self._event(cell)
        if cell in self.actions:
            return self._action(cell)[0]
        return None

    def _tables_and_headings(self, text, changes):
        out = []
        for line in text.split("\n"):
            m = re.match(r"^(#{1,6}\s+)(.+?)\s*$", line)
            if m:
                new = self._exact(m.group(2))
                if new and new != m.group(2):
                    changes.append((m.group(2), new))
                    line = m.group(1) + new
            elif line.lstrip().startswith("|") and "---" not in line:
                cells = line.split("|")
                for i, cell in enumerate(cells):
                    core = cell.strip()
                    new = self._exact(core) if core and "`" not in core else None
                    if new and new != core:
                        changes.append((core, new))
                        cells[i] = cell.replace(core, new)
                line = "|".join(cells)
            out.append(line)
        return "\n".join(out)


def main():
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    lang, files = args[0], args[1:]
    conv = Converter(lang, tables="--tables" in sys.argv, prose="--prose" in sys.argv)
    total = 0
    for f in files:
        text = Path(f).read_text(encoding="utf-8")
        new, changes = conv.convert(text)
        for inner in conv.skipped:
            print(f"   BLOCK? {f}: {inner!r} (a Blockly block: check by hand)")
        if changes:
            total += len(changes)
            print(f"== {f}: {len(changes)}")
            for a, b in changes:
                print(f"   {a!r} -> {b!r}")
            if "--write" in sys.argv:
                Path(f).write_text(new, encoding="utf-8")
    print("total", total)


if __name__ == "__main__":
    main()
