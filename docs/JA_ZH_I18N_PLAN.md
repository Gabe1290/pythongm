# Plan: ja + zh UI translation (Section H's remaining tiers)

Companion to `docs/I18N_CLEANUP_2026-08-06.md` Section H, which this
plan implements the ja/zh half of. **pt is done** (2026-08-08, commit
`c461528` and the checkbox trail before it) — this doc exists so ja and
zh can each be worked the same proven way without re-deriving the
methodology from scratch. Read `CLAUDE.md`'s 2026-08-08 session notes
for the narrative version of how pt was built; this doc is the
actionable checklist.

## Why this is its own plan doc

Same reasoning as `docs/TUTORIALS_I18N_PLAN.md`'s split from its parent:
each of ja and zh is a genuinely large, multi-session unit (1369
messages, matching pt's final count), and unlike pt — which could lean on
Romance-language pattern-matching plus spot verification — Japanese and
Chinese are typologically distant enough that translation quality can't
be self-checked the same way. The original Section H note flagged this:
*"extra technical-term-accuracy care"* for both. Treat that as a real
constraint, not boilerplate caution.

## Starting state (2026-08-08)

- `translations/pygamemaker_ja.ts` / `_zh.ts` exist: 289 entries each,
  **all `type="unfinished"`** — zero real translated content, a Nov 2025
  snapshot against a much older UI. Confirmed dead weight, same as
  `pygamemaker_pt.ts` was (already deleted). Do **not** seed from these.
- Neither language has a `pygm2_ja.ts`/`pygm2_zh.ts` yet — both start
  from nothing, same as pt did.
- Neither appears in `Tools > Language` (`LanguageManager.
  _discover_languages()` finds nothing to glob).

## Source-string reference: `pygm2_pt.ts`, not `pygm2_de.ts`

Building pt started from `pygm2_de.ts` (monolithic) per the reasoning in
`I18N_CLEANUP_2026-08-06.md`, but along the way that source needed two
rounds of correction:

1. The split `pygm2_de_*.ts` set turned out to be a **narrower** subset
   of the monolithic file (1007 vs. 1371 active messages) — not stale,
   just incomplete coverage. Not relevant to ja/zh directly, but a
   reminder to trust the monolithic count over the split one if you ever
   cross-check against German again.
2. Two real dead-translation bugs were found and fixed mid-build:
   - `self.ide` — a wrong translation-context name (18 real messages
     from `core/ide_exporters.py` were unreachable in every shipped
     language). Fixed by folding those 18 into the real `PyGameMakerIDE`
     context.
   - `self.tr(f"...")` f-strings in `widgets/thymio_playground.py` — 7
     messages were unreachable in every shipped language regardless of
     translation quality, because the f-string was evaluated before
     `tr()` ever saw it. Fixed in the Python source (now
     `self.tr("...{0}...").format(...)`), with every shipped language's
     real translation re-filed under the corrected source text.

`pygm2_pt.ts` reflects the **end state** of both fixes — 1369 real
distinct messages, already deduplicated (no `self.ide` context, no
dead f-string sources), across 61 real contexts. **Use `pygm2_pt.ts` as
the structural + source-string reference for ja and zh.**
`scripts/gen_translation_ts.py`'s `TranslationBuilder` already defaults
to it. This also means ja/zh skip re-discovering the two bugs above —
they were fixed once, upstream of both new languages.

Do **not** re-derive from `pygm2_de.ts` for ja/zh unless you have a
specific reason pt's shape is wrong for some context (unlikely — every
pt message was verified against `pygm2_de.ts`'s own source text at
authoring time).

## Tooling: `scripts/gen_translation_ts.py` (committed 2026-08-08)

Generalized from the session-local script that built all of `pygm2_pt.ts`.
Read its module docstring for full usage; short version:

```python
from scripts.gen_translation_ts import TranslationBuilder

builder = TranslationBuilder("ja")  # -> translations/pygm2_ja.ts, source pygm2_pt.ts

# Small/medium context — must cover every message in that context:
builder.add_contexts({
    "DetachedBlocklyWindow": {
        "Visual Block Programming (Detached)": "...",
    },
})

# Huge context (PyGameMakerIDE) — call repeatedly with whatever subset
# you have; already-added sources are skipped on re-run:
builder.add_partial_context("PyGameMakerIDE", {
    "&amp;File": "...",
    ...
})
```

**Critical detail proven across ~24 pt commits:** the dict *keys* (the
`<source>` text) must match the reference file's raw XML-entity-escaped
form EXACTLY (`&amp;` `&lt;` `&gt;` `&apos;` `&quot;`, literal leading/
trailing/embedded spaces, literal tab characters in a few Sprite Editor
shortcuts, literal `\n` line breaks) — copy them programmatically from a
`re.findall` dump of the reference context, never retype by hand. The
dict *values* (your translation) should be plain, unescaped real
characters; the tool XML-escapes them for you via `xml.sax.saxutils.
escape`.

## Per-context checklist (both ja and zh — same 61 contexts, same sizes)

Work order suggestion: same as pt's actual order — cluster small
contexts into one commit (5-10 contexts, 20-80 messages) for the first
many commits, save the four largest for dedicated batches near the end.
Sizes below are message counts (includes the 18 `PyGameMakerIDE`
messages already folded in from the `self.ide` fix, so translating
`PyGameMakerIDE` from `pygm2_pt.ts` gets you all 305 in one context, no
separate fold-in step needed this time).

| Context | Messages | Context | Messages |
|---|---|---|---|
| PyGameMakerIDE | 305 | BaseBlockConfigDialog | 10 |
| ThymioPlaygroundWindow | 75 | InstanceProperties | 10 |
| RoomEditor | 66 | OpenProjectDialog | 10 |
| SpriteEditor | 66 | ThymioActionSelector | 10 |
| EnhancedPropertiesPanel | 61 | BlocklyWidget | 9 |
| AssetTreeWidget | 60 | TutorialDialog | 9 |
| ObjectEventsPanel | 56 | MultiActionEditor | 9 |
| ConditionalActionEditor | 53 | PlaygroundColorManager | 9 |
| PlaygroundEditor | 44 | PlaygroundToolPalette | 9 |
| PreferencesDialog | 43 | ThymioEventSelector | 9 |
| ExportProjectDialog | 39 | FrameTimeline | 8 |
| ObjectEditor | 39 | ResizeCanvasDialog | 8 |
| WelcomeTab | 22 | ThymioConfigDialog | 8 |
| SpriteStripDialog | 21 | TilePaletteDialog | 8 |
| ActionConfigDialog | 18 | CreateAssetDialog | 7 |
| AssetPropertiesDialog | 18 | EditorStatusWidget | 7 |
| ProjectSettingsDialog | 18 | GM80ActionDialog | 7 |
| ViewConfigDialog | 17 | KeySelectorDialog | 7 |
| NewProjectDialog | 16 | AssetRenameDialog | 6 |
| BlocklyConfigDialog | 15 | MouseEventSelectorDialog | 6 |
| BackgroundLayersDialog | 15 | PlaygroundRunnerWindow | 6 |
| PlaygroundElementProperties | 15 | BlocklyVisualProgrammingTab | 5 |
| TutorialPanel | 14 | FloatableEditorMixin | 4 |
| AutoSaveSettingsDialog | 14 | MessageTranslationsDialog | 3 |
| BaseEditor | 14 | ForegroundBackgroundSwatch | 2 |
| ThymioEventsPanel | 14 | ObjectPalette | 2 |
| BuildProjectDialog | 13 | DetachedBlocklyWindow | 1 |
| ImportAssetsDialog | 12 | ActionListWidget | 1 |
| ObjectPropertiesPanel | 12 | ColorPaletteWidget | 1 |
| — | — | ColorSwatch | 1 |
| — | — | TileGridWidget | 1 |
| — | — | VisualScriptingArea | 1 |

**Total: 1369 messages, 61 contexts, per language.**

Checklist to duplicate per language (copy this block, fill in as you go):

```
- [ ] ja: 0/1369 messages, 0/61 contexts
- [ ] zh: 0/1369 messages, 0/61 contexts
```

(Deliberately not pre-expanded into 61×2 checkboxes here — that's ~2,700
lines of near-duplicate registry noise for work that hasn't started.
Expand into the same per-context-with-commit-hash format
`I18N_CLEANUP_2026-08-06.md`'s pt section used, in *that* file, once a
session actually starts ja or zh — mirrors how pt's own registry grew
organically rather than being pre-written.)

## Landmines carried forward from pt (apply identically to ja/zh)

- **Leading/trailing space sources are real and must be preserved
  exactly**: `" seconds"`, `" minutes"`, `"X: "`, `"Y: "`,
  `" Thickness: "`, `" Block: "`. Verify with `grep -n '<source>.*
  </source>'` or a `repr()` print, not visual inspection (invisible in a
  normal file viewer).
- **Literal tab characters**: `SpriteEditor`'s `"Copy\tCtrl+C"` and its 4
  siblings (`Cut`, `Paste`, `Delete`, `Deselect`) use a real tab, not
  spaces, between label and shortcut.
- **`&apos;`/`&quot;` entity-escaped quotes inside source text** (e.g.
  `"&quot;{0}&quot; has unsaved changes..."` in `PyGameMakerIDE`) —
  these decode to real `"`/`'` at Qt-parse time; querying a translation
  with the literal escaped form during ad-hoc verification returns a
  false "untranslated" result (this bit the pt build once — see
  `PyGameMakerIDE` batch 2's commit message). Always verify with the
  real character.
- **Combo-box snake_case display strings** (`ConditionalActionEditor`'s
  `instance_count`/`variable_compare`/etc.) are safe to translate — they
  are `_add_canonical_items`/`_select_canonical`-backed `userData`
  values under the hood, translating the *display* text can't break
  condition-type matching. de/it/es/ru/sl/uk/fr and now pt all translate
  these; do the same for ja/zh (pick natural short ja/zh equivalents,
  doesn't need to mirror the underscore-joined style literally).
- **Qt `%1`-style placeholders** exist alongside `.format()`-style `{0}`
  placeholders in a few strings (`ObjectEventsPanel`'s "Cannot add
  actions directly to %1...") — both are literal text to preserve
  verbatim in the translation, neither is something this tool
  auto-substitutes.
- **HTML in `<source>` is real markup**, not decoration — the
  `PyGameMakerIDE` About dialog and a few `<h2>`/`<h3>`/`<b>` snippets
  elsewhere must keep every tag, and the About dialog's GitHub link
  and `LICENSE`/`LICENSE-docs` `<code>` identifiers must stay in English
  verbatim (they're literal filenames/URLs, not prose).
- **Some strings are deliberately left as English loanwords even in a
  "complete" translation** — pt kept `"Sprites"`, `"Playgrounds"`,
  `"Scripts"`, `"View"`(Web)/`"Web"` etc. as-is in a few contexts,
  following the vocabulary established in Section K's sample-guide
  translations. Whether ja/zh have equivalent loanword conventions for
  these terms is a judgment call for whoever translates — not
  necessarily copy pt's exact choices, since loanword-vs-native varies
  a lot by target language and audience (this app is aimed at students).

## Verification per batch (same discipline as every pt commit)

1. `python3 -c "import xml.dom.minidom as m; m.parse('translations/pygm2_<lang>.ts')"`
   — XML well-formedness.
2. `python3 scripts/compile_translations.py` — must show
   `Compiling pygm2_<lang>.ts... ✓` (monolithic, so it always compiles;
   no split-set bootstrap gate to worry about, same as pt).
3. Live `QTranslator` resolution check for a handful of sampled strings
   per batch, via a small offscreen-`QApplication` snippet (see any pt
   commit message in `git log --grep=pygm2_pt` for the exact pattern) —
   confirms the `.qm` actually contains a working translation, not just
   that the `.ts` parses.
4. `QT_QPA_PLATFORM=offscreen python3 -m pytest tests/ -q` — full suite,
   must stay green. (Baseline as of pt's completion: 2207 passed.)
5. Commit the `.ts` + `.qm` pair together, one context (or a handful of
   small ones, or one slice of `PyGameMakerIDE`) per commit, matching
   this repo's session-limit discipline — push after every commit.

## What "done" looks like

- `translations/pygm2_ja.ts` / `pygm2_zh.ts` exist, monolithic, 1369
  messages / 61 contexts each, compiling cleanly.
- `LanguageManager._discover_languages()` lists `('ja', ..., ...)` and
  `('zh', ..., ...)`.
- `translations/pygamemaker_ja.ts` / `_zh.ts` deleted (mirrors the
  `pygamemaker_pt.ts` deletion) once the real replacement exists for
  each — do this per-language as that language finishes, not as a
  joint step.
- `translations/README.md`'s Available Languages list updated per
  language, same as the pt entry.
- `docs/I18N_CLEANUP_2026-08-06.md` Section H's ja/zh bullets checked
  off with the per-context registry filled in (commit hashes).
- **Still gated on a human with a GUI** even after all of the above:
  nobody has opened the running IDE with any of pt/ja/zh selected and
  looked at it. That applies equally here — programmatic verification
  (this plan's whole checklist) is necessary but not sufficient to call
  a language "shipped."

## Effort expectation

pt took roughly 24 translation-content commits plus verification
overhead across several session turns at increasing usage-percentage
checkpoints (~14% through ~80%+ across multiple resumptions). ja and zh
are the same *size* (1369 messages each) but should be budgeted as
**more** expensive per message than pt was, not the same — Romance-
language pattern matching (recognizing cognates, reusing sentence
structure intuitions) doesn't transfer to Japanese or Chinese, so
expect more deliberate per-string work and more value in a native or
fluent speaker's review pass than pt needed. Treat each as its own
multi-session arc; don't start zh in the same session as finishing ja
without a deliberate checkpoint in between.
