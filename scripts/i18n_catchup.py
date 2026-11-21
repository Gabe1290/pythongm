#!/usr/bin/env python3
"""Bring every shipped language up to French: find the interface strings the
code uses that French translates and another language does not, and add
translations for them to the right catalogue.

    python3 scripts/i18n_catchup.py report             # gap per language
    python3 scripts/i18n_catchup.py worklist OUT.json  # every missing string,
                                                       # with the French as a hint
    python3 scripts/i18n_catchup.py apply BATCH.json   # add translations

A batch file is ``{context: {source: {lang: translation}}}``. The source is the
plain text the code passes to tr() (NOT entity-escaped); translations are plain
text too. A string is only written for a language that is still missing it, so
re-applying a batch is harmless. Run ``scripts/compile_translations.py`` after.

"Used by the code" = a literal ``self.tr("...")`` inside a class (context =
the class name) or ``QCoreApplication.translate("Ctx", "...")``. French
entries the code no longer uses are ignored.

Where a string goes:
* single-file languages (es, ja, pl, pt, zh): ``pygm2_<lang>.ts``;
* split languages (de, it, ru, sl, uk): the group file that already holds the
  context; for a context new to that language, the group that holds another
  context from the same source file (looked up across all split languages),
  else by folder (editors/ -> editors, dialogs/ -> dialogs, core/ -> core),
  else misc.
A vanished entry with the same source and no text is revived in place instead
of duplicated (two live copies of one source do not resolve).
"""
import ast
import json
import re
import sys
import xml.etree.ElementTree as ET
from pathlib import Path
from xml.sax.saxutils import escape

ROOT = Path(__file__).resolve().parent.parent
TRANS = ROOT / "translations"
LANGS = ("de", "es", "it", "ja", "pl", "pt", "ru", "sl", "uk", "zh")
SPLIT = ("de", "it", "ru", "sl", "uk")
GROUPS = ("actions", "blockly", "core", "dialogs", "editors", "misc")
SKIP = ("venv", "tests", ".git", "build", "dist")


def code_usage():
    """{(context, source): relative file of first use}."""
    out = {}
    for f in sorted(ROOT.rglob("*.py")):
        rel = f.relative_to(ROOT)
        if any(p in rel.parts for p in SKIP):
            continue
        try:
            tree = ast.parse(f.read_text(encoding="utf-8"))
        except Exception:
            continue
        for cls in [n for n in ast.walk(tree) if isinstance(n, ast.ClassDef)]:
            for c in ast.walk(cls):
                if (isinstance(c, ast.Call) and isinstance(c.func, ast.Attribute)
                        and c.func.attr == "tr" and c.args
                        and isinstance(c.args[0], ast.Constant)
                        and isinstance(c.args[0].value, str)):
                    out.setdefault((cls.name, c.args[0].value), str(rel))
        for c in ast.walk(tree):
            if (isinstance(c, ast.Call) and isinstance(c.func, ast.Attribute)
                    and c.func.attr == "translate" and len(c.args) >= 2
                    and all(isinstance(a, ast.Constant) and isinstance(a.value, str)
                            for a in c.args[:2])):
                out.setdefault((c.args[0].value, c.args[1].value), str(rel))
    return out


def files_of(lang):
    split = [TRANS / f"pygm2_{lang}_{g}.ts" for g in GROUPS]
    split = [p for p in split if p.exists()]
    return split or [TRANS / f"pygm2_{lang}.ts"]


def live(lang):
    """{(context, source): translation} with real, non-vanished text."""
    out = {}
    for ts in files_of(lang):
        for ctx in ET.parse(ts).getroot().findall("context"):
            name = ctx.findtext("name")
            for m in ctx.findall("message"):
                t = m.find("translation")
                if t is None or t.get("type") in ("vanished", "obsolete"):
                    continue
                if (t.text or "").strip():
                    out.setdefault((name, m.findtext("source") or ""), t.text)
    return out


def gaps():
    used = code_usage()
    fr = live("fr")
    want = {k: v for k, v in fr.items() if k in used}
    return used, want, {lang: sorted(k for k in want if k not in live(lang)) for lang in LANGS}


def report():
    used, want, missing = gaps()
    print(f"French translates {len(want)} strings the code uses.")
    for lang in LANGS:
        ctxs = {}
        for c, _ in missing[lang]:
            ctxs[c] = ctxs.get(c, 0) + 1
        top = ", ".join(f"{c} {n}" for c, n in sorted(ctxs.items(), key=lambda x: -x[1])[:6])
        print(f"{lang}: {len(missing[lang]):4d} missing in {len(ctxs):2d} contexts   {top}")
    return missing


def worklist(path):
    used, want, missing = gaps()
    out = {}
    for lang in LANGS:
        for ctx, src in missing[lang]:
            e = out.setdefault(ctx, {}).setdefault(src, {"fr": want[(ctx, src)], "file": used[(ctx, src)], "langs": []})
            e["langs"].append(lang)
    Path(path).write_text(json.dumps(out, ensure_ascii=False, indent=1, sort_keys=True), encoding="utf-8")
    print(f"{sum(len(v) for v in out.values())} distinct strings in {len(out)} contexts -> {path}")


# ---------------------------------------------------------------- applying

def _group_for(lang, ctx, src_file, cache={}):
    files = files_of(lang)
    if len(files) == 1 and not files[0].stem.endswith(GROUPS):
        return files[0]                     # a single-file language
    for ts in files:
        names = {c.findtext("name") for c in ET.parse(ts).getroot().findall("context")}
        if ctx in names:
            return ts
    if "by_file" not in cache:
        used = code_usage()
        ctx_file = {}
        for (c, _), f in used.items():
            ctx_file.setdefault(c, f)
        by_file = {}
        for l in SPLIT:
            for g in GROUPS:
                ts = TRANS / f"pygm2_{l}_{g}.ts"
                for c in ET.parse(ts).getroot().findall("context"):
                    f = ctx_file.get(c.findtext("name"))
                    if f:
                        by_file.setdefault(f, g)
        cache["by_file"] = by_file
    g = cache["by_file"].get(src_file)
    if g is None:
        top = Path(src_file).parts[0]
        g = {"editors": "editors", "dialogs": "dialogs", "core": "core"}.get(top, "misc")
    return TRANS / f"pygm2_{lang}_{g}.ts"


def _msg_xml(src, text, src_file, indent="    "):
    return (f"{indent}<message>\n"
            f'{indent}    <location filename="../{src_file}" line="0"/>\n'
            f"{indent}    <source>{escape(src, {chr(34): '&quot;', chr(39): '&apos;'})}</source>\n"
            f"{indent}    <translation>{escape(text)}</translation>\n"
            f"{indent}</message>\n")


def _insert(ts, ctx, src, text, src_file):
    content = ts.read_text(encoding="utf-8")
    esc_src = escape(src, {chr(34): "&quot;", chr(39): "&apos;"})
    for cm in re.finditer(r"<context>\s*<name>(.*?)</name>(.*?)</context>", content, re.S):
        if cm.group(1) != escape(ctx):
            continue
        body = cm.group(2)
        # revive an empty vanished/unfinished copy in place
        for mm in re.finditer(r"<message>(?:(?!</message>).)*</message>", body, re.S):
            m = mm.group(0)
            ms = re.search(r"<source>(.*?)</source>", m, re.S)
            if ms is None or ET.fromstring(f"<s>{ms.group(1)}</s>").text != src and ms.group(1) != esc_src:
                continue
            new = re.sub(r"<translation[^>]*?(/>|>.*?</translation>)",
                         lambda _: f"<translation>{escape(text)}</translation>", m, count=1, flags=re.S)
            start = cm.start(2) + mm.start()
            content = content[:start] + new + content[start + len(m):]
            ts.write_text(content, encoding="utf-8")
            return "revived"
        end = cm.end(2)
        content = content[:end] + _msg_xml(src, text, src_file) + content[end:]
        ts.write_text(content, encoding="utf-8")
        return "added"
    block = f"<context>\n    <name>{escape(ctx)}</name>\n{_msg_xml(src, text, src_file)}</context>\n"
    i = content.rindex("</TS>")
    content = content[:i] + block + content[i:]
    ts.write_text(content, encoding="utf-8")
    return "new context"


def apply(path):
    batch = json.loads(Path(path).read_text(encoding="utf-8"))
    used = code_usage()
    done, problems = {}, []
    have = {lang: live(lang) for lang in LANGS}
    for ctx, msgs in batch.items():
        for src, per_lang in msgs.items():
            if (ctx, src) not in used:
                problems.append(f"not used by the code: {ctx} / {src[:50]!r}")
                continue
            for lang, text in per_lang.items():
                if lang not in LANGS or (ctx, src) in have[lang]:
                    continue
                if not text.strip():
                    problems.append(f"empty: {lang} {ctx} / {src[:40]!r}")
                    continue
                for ph in set(re.findall(r"\{\d*\}|%\d|%s|%d", src)):
                    if ph not in text:
                        problems.append(f"placeholder {ph} lost: {lang} {ctx} / {src[:40]!r}")
                ts = _group_for(lang, ctx, used[(ctx, src)])
                _insert(ts, ctx, src, text, used[(ctx, src)])
                done[lang] = done.get(lang, 0) + 1
    for p in problems:
        print("PROBLEM:", p)
    print("written:", dict(sorted(done.items())))
    return not problems


if __name__ == "__main__":
    cmd = sys.argv[1] if len(sys.argv) > 1 else "report"
    if cmd == "report":
        report()
    elif cmd == "worklist":
        worklist(sys.argv[2])
    elif cmd == "apply":
        sys.exit(0 if apply(sys.argv[2]) else 1)
    else:
        sys.exit(__doc__)
