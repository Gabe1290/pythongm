#!/usr/bin/env python3
"""Bring every shipped language up to French: find the interface strings the
code uses that French translates and another language does not, and add
translations for them to the right catalogue.

    python3 scripts/i18n_catchup.py report             # gap per language
    python3 scripts/i18n_catchup.py worklist OUT.json  # every missing string,
                                                       # with the French as a hint
    python3 scripts/i18n_catchup.py apply BATCH.json   # add translations
    python3 scripts/i18n_catchup.py propagate [LEFT.json] [--dry-run]
                                       # copy mixin/base-class translations to the
                                       # concrete classes that really run them
    python3 scripts/i18n_catchup.py apply BATCH.json --replace
                                       # ...and overwrite existing live ones

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
import functools
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


def _module_file(module, rel_from, level=0):
    """Relative .py path for an import, or None."""
    if level:
        base = Path(rel_from).parent
        for _ in range(level - 1):
            base = base.parent
        parts = list(base.parts) + (module.split(".") if module else [])
    else:
        parts = module.split(".")
    for cand in (Path(*parts).with_suffix(".py"), Path(*parts) / "__init__.py"):
        if (ROOT / cand).exists():
            return str(cand)
    return None


@functools.lru_cache(maxsize=None)
def _scan():
    """Parse the code once: classes {(file, name): (bases, tr strings)}, the
    import table per file, and the QCoreApplication.translate() pairs."""
    classes, imports, translate = {}, {}, {}
    for f in sorted(ROOT.rglob("*.py")):
        rel = f.relative_to(ROOT)
        if any(p in rel.parts for p in SKIP):
            continue
        try:
            tree = ast.parse(f.read_text(encoding="utf-8"))
        except Exception:
            continue
        rel = str(rel)
        table = imports.setdefault(rel, {})
        for n in ast.walk(tree):
            if isinstance(n, ast.ImportFrom):
                mf = _module_file(n.module or "", rel, n.level)
                for a in n.names:
                    table[a.asname or a.name] = (mf, a.name)
        for cls in [n for n in ast.walk(tree) if isinstance(n, ast.ClassDef)]:
            bases = [b.id if isinstance(b, ast.Name) else getattr(b, "attr", None) for b in cls.bases]
            strings = []
            for c in ast.walk(cls):
                if (isinstance(c, ast.Call) and isinstance(c.func, ast.Attribute)
                        and c.func.attr == "tr" and c.args
                        and isinstance(c.args[0], ast.Constant)
                        and isinstance(c.args[0].value, str)):
                    strings.append(c.args[0].value)
            classes[(rel, cls.name)] = ([b for b in bases if b], strings)
        for c in ast.walk(tree):
            if (isinstance(c, ast.Call) and isinstance(c.func, ast.Attribute)
                    and c.func.attr == "translate" and len(c.args) >= 2
                    and all(isinstance(a, ast.Constant) and isinstance(a.value, str)
                            for a in c.args[:2])):
                translate.setdefault((c.args[0].value, c.args[1].value), rel)
    return classes, imports, translate


@functools.lru_cache(maxsize=None)
def runtime_contexts():
    """{(file, class): set of Qt contexts its tr() calls run under}.

    Qt's tr() takes its context from the CONCRETE runtime class, so a string in
    a mixin or a shared base class is looked up under every class that inherits
    it (SpriteEditor, PyGameMakerIDE...), never under the mixin's own name. A
    base name resolves to the class of that name in the same file, else through
    the subclass file's ``from ... import``, else to the only class with that
    name (two unrelated ``InputMixin`` classes exist, so names alone are not enough).
    """
    classes, imports, _ = _scan()
    by_name = {}
    for key in classes:
        by_name.setdefault(key[1], []).append(key)

    def resolve(base, in_file):
        if (in_file, base) in classes:
            return (in_file, base)
        mf, name = imports.get(in_file, {}).get(base, (None, base))
        if mf and (mf, name) in classes:
            return (mf, name)
        if mf:  # re-exported by a package __init__: follow one more hop
            mf2, name2 = imports.get(mf, {}).get(name, (None, name))
            if mf2 and (mf2, name2) in classes:
                return (mf2, name2)
        cands = by_name.get(name, [])
        return cands[0] if len(cands) == 1 else None

    children = {}
    for key, (bases, _) in classes.items():
        for b in bases:
            parent = resolve(b, key[0])
            if parent:
                children.setdefault(parent, set()).add(key)

    out = {}
    for key in classes:
        ctxs, stack, seen = {key[1]}, [key], {key}
        while stack:
            for ch in children.get(stack.pop(), ()):
                if ch not in seen:
                    seen.add(ch)
                    ctxs.add(ch[1])
                    stack.append(ch)
        out[key] = ctxs
    return out


def code_usage():
    """{(context, source): relative file of first use}, with each tr() string
    filed under every runtime context it really runs in (see runtime_contexts)."""
    classes, _, translate = _scan()
    contexts = runtime_contexts()
    out = {}
    for key in sorted(classes):
        for s in classes[key][1]:
            for ctx in sorted(contexts[key]):
                out.setdefault((ctx, s), key[0])
    for k, rel in translate.items():
        out.setdefault(k, rel)
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
    have = {lang: live(lang) for lang in LANGS}
    return used, want, {lang: sorted(k for k in want if k not in have[lang]) for lang in LANGS}


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


def _replace(lang, ctx, src, text):
    """Rewrite the live translation of (ctx, src) in whichever file holds it."""
    esc_src = escape(src, {chr(34): "&quot;", chr(39): "&apos;"})
    for ts in files_of(lang):
        content = ts.read_text(encoding="utf-8")
        for cm in re.finditer(r"<context>\s*<name>(.*?)</name>(.*?)</context>", content, re.S):
            if cm.group(1) != escape(ctx):
                continue
            for mm in re.finditer(r"<message>(?:(?!</message>).)*</message>", cm.group(2), re.S):
                m = mm.group(0)
                if f"<source>{esc_src}</source>" not in m or 'type="vanished"' in m:
                    continue
                new = re.sub(r"<translation[^>]*?(/>|>.*?</translation>)",
                             lambda _: f"<translation>{escape(text)}</translation>", m, count=1, flags=re.S)
                start = cm.start(2) + mm.start()
                ts.write_text(content[:start] + new + content[start + len(m):], encoding="utf-8")
                return True
    return False


def apply(path, replace=False):
    batch = json.loads(Path(path).read_text(encoding="utf-8"))
    used = code_usage()
    done, problems = {}, []
    have = {lang: live(lang) for lang in ("fr",) + LANGS}
    for ctx, msgs in batch.items():
        for src, per_lang in msgs.items():
            if (ctx, src) not in used:
                problems.append(f"not used by the code: {ctx} / {src[:50]!r}")
                continue
            for lang, text in per_lang.items():
                if lang not in ("fr",) + LANGS:
                    continue
                if (ctx, src) in have[lang]:
                    if replace and have[lang][(ctx, src)] != text:
                        if _replace(lang, ctx, src, text):
                            done[lang] = done.get(lang, 0) + 1
                        else:
                            problems.append(f"could not replace: {lang} {ctx} / {src[:40]!r}")
                    continue
                if not text.strip():
                    problems.append(f"empty: {lang} {ctx} / {src[:40]!r}")
                    continue
                for ph in set(re.findall(r"\{\w*(?::[^}]*)?\}|%\d|%s|%d", src)):
                    if ph not in text:
                        problems.append(f"placeholder {ph} lost: {lang} {ctx} / {src[:40]!r}")
                ts = _group_for(lang, ctx, used[(ctx, src)])
                _insert(ts, ctx, src, text, used[(ctx, src)])
                done[lang] = done.get(lang, 0) + 1
    for p in problems:
        print("PROBLEM:", p)
    print("written:", dict(sorted(done.items())))
    return not problems


def inherited_pairs():
    """{(runtime context, source): defining class} for every tr() string that
    runs under a class OTHER than the one whose code contains it."""
    classes, _, _ = _scan()
    contexts = runtime_contexts()
    out = {}
    for key, (_, strings) in classes.items():
        for s in strings:
            for ctx in contexts[key]:
                if ctx != key[1]:
                    out.setdefault((ctx, s), key)
    return out


def propagate(write=True, langs=("fr",) + LANGS):
    """Copy each inherited string's existing translation (under the defining
    mixin/base class, or under another class that runs the same code) to every
    runtime context still missing it. Returns {lang: [(ctx, src)]} of pairs with
    no translation anywhere in that language."""
    contexts = runtime_contexts()
    inh = inherited_pairs()
    used = code_usage()
    left = {}
    for lang in langs:
        have = live(lang)
        written = 0
        left[lang] = []
        for (ctx, src), key in sorted(inh.items()):
            if (ctx, src) in have:
                continue
            donors = [have[(c, src)] for c in sorted(contexts[key] | {key[1]}) if (c, src) in have]
            if not donors:
                left[lang].append((ctx, src))
                continue
            if write:
                ts = TRANS / "pygm2_fr.ts" if lang == "fr" else _group_for(lang, ctx, used[(ctx, src)])
                _insert(ts, ctx, src, donors[0], used[(ctx, src)])
                have[(ctx, src)] = donors[0]
            written += 1
        print(f"{lang}: copied {written}, no translation anywhere: {len(left[lang])}")
    return left


if __name__ == "__main__":
    cmd = sys.argv[1] if len(sys.argv) > 1 else "report"
    if cmd == "report":
        report()
    elif cmd == "worklist":
        worklist(sys.argv[2])
    elif cmd == "propagate":
        left = propagate(write="--dry-run" not in sys.argv)
        if len(sys.argv) > 2 and sys.argv[2].endswith(".json"):
            Path(sys.argv[2]).write_text(json.dumps({l: v for l, v in left.items()}, ensure_ascii=False, indent=1), encoding="utf-8")
    elif cmd == "apply":
        sys.exit(0 if apply(sys.argv[2], replace="--replace" in sys.argv) else 1)
    else:
        sys.exit(__doc__)
