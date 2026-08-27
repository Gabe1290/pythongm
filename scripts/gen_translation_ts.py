#!/usr/bin/env python3
"""Reusable helper for building a new language's translations/pygm2_<lang>.ts
incrementally, context by context, from a reference .ts's structure.

Proven across ~24 commits building pygm2_pt.ts from scratch (see
docs/I18N_CLEANUP_2026-08-06.md Section H and CLAUDE.md's 2026-08-08
session notes) — this is that session-local tool, generalized and
committed so the next language (ja, zh, ...) doesn't have to reinvent it.

Usage pattern (see docs/JA_ZH_I18N_PLAN.md for the full worked example):

    from scripts.gen_translation_ts import TranslationBuilder

    builder = TranslationBuilder("ja")  # writes translations/pygm2_ja.ts

    # Small/medium context: whole context in one call, dict must cover
    # every active (non-vanished, has <location>) message in that context.
    builder.add_contexts({
        "BlocklyConfigDialog": {
            "Configure Events &amp; Actions": "...japanese text...",
            ...
        },
    })

    # Huge context (e.g. PyGameMakerIDE, 287 messages): call repeatedly
    # with whatever subset you have translated so far. Only new sources
    # are appended each time; already-present ones are skipped, so the
    # same call is safe to re-run.
    builder.add_partial_context("PyGameMakerIDE", {
        "&amp;File": "...japanese text...",
        ...
    })

Reference source: defaults to translations/pygm2_pt.ts (NOT
pygm2_de.ts). pt is the better reference now — building pt required
first discovering that the split pygm2_de_*.ts set is a narrower
subset of the monolithic pygm2_de.ts, and separately finding + fixing
two real dead-translation bugs (the "self.ide" wrong-context bug and
the ThymioPlaygroundWindow self.tr(f"...") bug) whose corrected,
final-shape source strings only exist, already merged and clean, in
pygm2_pt.ts. Starting a new language from pygm2_de.ts again would
require re-deriving all of that. Override `source_ts` only if you have
a specific reason pt's shape doesn't apply.

XML source text (the dict keys) must match EXACTLY what's between
<source>...</source> in the reference file, entity-escaped form
(&amp; &lt; &gt; &apos; &quot;) and all — copy it from a `grep`/`python3
-c "import re; ..."` dump of the reference context, don't retype by
hand. Translation text (the dict values) should be REAL unescaped
characters (a literal & or < or "); this module escapes it for you.
"""
import re
from pathlib import Path
from xml.sax.saxutils import escape

TRANS_DIR = Path(__file__).resolve().parent.parent / "translations"


class TranslationBuilder:
    def __init__(self, lang, source_ts=None, dest_ts=None, ts_language_attr=None):
        self.lang = lang
        self.source_path = Path(source_ts) if source_ts else (TRANS_DIR / "pygm2_pt.ts")
        self.dest_path = Path(dest_ts) if dest_ts else (TRANS_DIR / f"pygm2_{lang}.ts")
        self.ts_language_attr = ts_language_attr or lang

    def _parse_source_context(self, name):
        content = self.source_path.read_text(encoding="utf-8")
        contexts = re.findall(r"<context>(.*?)</context>", content, re.S)
        for c in contexts:
            cname = re.search(r"<name>(.*?)</name>", c).group(1)
            if cname != name:
                continue
            messages = re.findall(r"<message>(.*?)</message>", c, re.S)
            out = []
            for m in messages:
                if "<location" not in m:
                    continue
                locs = re.findall(r'<location filename="([^"]*)" line="(\d+)"/>', m)
                src = re.search(r"<source>(.*?)</source>", m, re.S).group(1)
                out.append((src, locs))
            return out
        raise KeyError(name)

    def _existing(self):
        if not self.dest_path.exists():
            return set(), ""
        content = self.dest_path.read_text(encoding="utf-8")
        contexts = re.findall(r"<context>\s*<name>(.*?)</name>", content)
        return set(contexts), content

    def _write_new_file(self, block_xml):
        header = (
            '<?xml version="1.0" encoding="utf-8"?>\n<!DOCTYPE TS>\n'
            f'<TS version="2.1" language="{self.ts_language_attr}">\n'
        )
        footer = "\n</TS>\n"
        self.dest_path.write_text(header + block_xml + footer, encoding="utf-8")

    def add_contexts(self, context_translations):
        """context_translations: {context_name: {source: translation}}.
        Each dict must cover EVERY active message in that context (raises
        KeyError naming the missing source otherwise). Contexts already
        present in the dest file are skipped entirely (not re-checked)."""
        existing, content = self._existing()
        new_blocks = []
        for name, translations in context_translations.items():
            if name in existing:
                print(f"skip (exists): {name}")
                continue
            entries = self._parse_source_context(name)
            lines = ["<context>", f"    <name>{name}</name>"]
            for src, locs in entries:
                if src not in translations:
                    raise KeyError(f"Missing translation for {name!r}: {src!r}")
                lines.append("    <message>")
                for fn, line in locs:
                    lines.append(f'        <location filename="{fn}" line="{line}"/>')
                lines.append(f"        <source>{src}</source>")
                lines.append(f"        <translation>{escape(translations[src])}</translation>")
                lines.append("    </message>")
            lines.append("</context>")
            new_blocks.append("\n".join(lines))
            print(f"added: {name} ({len(entries)} messages)")

        if not new_blocks:
            print("Nothing new to add.")
            return

        if not self.dest_path.exists():
            self._write_new_file("\n".join(new_blocks))
            return

        insertion = "\n".join(new_blocks) + "\n"
        assert content.rstrip().endswith("</TS>")
        idx = content.rstrip().rfind("</TS>")
        self.dest_path.write_text(content[:idx] + insertion + content[idx:], encoding="utf-8")

    def add_partial_context(self, name, translations):
        """Incrementally add messages to a large context across multiple
        calls/sessions. Only entries present in `translations` AND not
        already in the dest file (matched by <source>) are appended —
        safe to call repeatedly as more of a huge context gets translated.

        A `type="vanished"` message does NOT count as "already present":
        lrelease drops vanished entries from the compiled .qm, so a live
        source string shadowed only by a stale vanished duplicate would be
        silently skipped forever, leaving it untranslated at runtime. Bug
        found and fixed 2026-08-27 (French UI-string gap fill) — it had
        already caused 5 real, live strings to be silently dropped."""
        entries = self._parse_source_context(name)
        _, content = self._existing()

        existing_sources = set()
        if content:
            block = re.search(
                r"<context>\s*<name>" + re.escape(name) + r"</name>.*?</context>",
                content, re.S,
            )
            if block:
                for msg in re.findall(r"<message>(.*?)</message>", block.group(0), re.S):
                    srcm = re.search(r"<source>(.*?)</source>", msg, re.S)
                    if not srcm:
                        continue
                    transm = re.search(r'<translation([^>]*)>', msg)
                    is_vanished = bool(transm and 'type="vanished"' in transm.group(1))
                    if not is_vanished:
                        existing_sources.add(srcm.group(1))

        to_add = [(src, locs) for src, locs in entries
                  if src in translations and src not in existing_sources]
        if not to_add:
            print(f"{name}: nothing new to add ({len(existing_sources)} already present)")
            return

        msg_lines = []
        for src, locs in to_add:
            msg_lines.append("    <message>")
            for fn, line in locs:
                msg_lines.append(f'        <location filename="{fn}" line="{line}"/>')
            msg_lines.append(f"        <source>{src}</source>")
            msg_lines.append(f"        <translation>{escape(translations[src])}</translation>")
            msg_lines.append("    </message>")
        insertion = "\n".join(msg_lines)

        if not content:
            block_xml = f"<context>\n    <name>{name}</name>\n{insertion}\n</context>"
            self._write_new_file(block_xml)
            print(f"{name}: created context with {len(to_add)} messages")
            return

        existing_block = re.search(
            r"<context>\s*<name>" + re.escape(name) + r"</name>.*?</context>",
            content, re.S,
        )
        if existing_block:
            old = existing_block.group(0)
            new = old[: -len("</context>")] + insertion + "\n</context>"
            new_content = content.replace(old, new, 1)
        else:
            idx = content.rstrip().rfind("</TS>")
            new_block = f"<context>\n    <name>{name}</name>\n{insertion}\n</context>\n"
            new_content = content[:idx] + new_block + content[idx:]
        self.dest_path.write_text(new_content, encoding="utf-8")
        total_now = len(existing_sources) + len(to_add)
        print(f"{name}: added {len(to_add)} messages (total now {total_now}/{len(entries)})")


if __name__ == "__main__":
    print(__doc__)
