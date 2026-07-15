# i18n follow-up: "Sample guides" viewer (commit 71f2b3e)

`71f2b3e` (2026-07-15) added the Sample guides button/dialog to
`widgets/welcome_tab.py` and explicitly deferred translation ("English
shows meanwhile"). This registry is the resume queue for that follow-up —
**one language per commit**, per the standing "no multi-agent workflows,
size to session budget" preference in `CLAUDE.md`. Work top to bottom;
flip `[ ]` → `[x]` with the commit hash as each language lands.

## New source strings (all in `widgets/welcome_tab.py`)

| # | Context (class) | Line | Source string |
|---|---|---|---|
| 1 | `WelcomeTab` | 195 | `📖  Sample guides` (button label) |
| 2 | `SampleDocsDialog` (new context) | 489 | `Sample guides` (window title) |
| 3 | `SampleDocsDialog` | 526 | `_No bundled samples were found in this build._` (markdown italic) |
| 4 | `SampleDocsDialog` | 567 | `_No documentation is bundled for **{0}**._` (markdown, `{0}` = sample display name) |

`SampleDocsDialog` is a brand-new class, so every language needs a new
`<context><name>SampleDocsDialog</name>...</context>` block added (there is
no existing one to extend) alongside the one new message appended to the
existing `WelcomeTab` context. Preserve the markdown markers (`_..._`,
`**{0}**`) literally around the translated words — `QTextBrowser.setMarkdown`
renders them at runtime.

Target file per language (per `scripts/compile_translations.py`'s
`should_compile`: split-set languages take the `_core.ts` group; French and
Spanish only ship a hand-translated monolithic `.qm`, so their split `.ts`
siblings are inert — edit the monolithic file instead):

| Lang | Target file | Split or monolithic |
|---|---|---|
| de | `translations/pygm2_de_core.ts` | split (has `_core.qm`) |
| it | `translations/pygm2_it_core.ts` | split |
| ru | `translations/pygm2_ru_core.ts` | split |
| sl | `translations/pygm2_sl_core.ts` | split |
| uk | `translations/pygm2_uk_core.ts` | split |
| fr | `translations/pygm2_fr.ts` | **monolithic** — do not touch `pygm2_fr_core.ts` |
| es | `translations/pygm2_es.ts` | **monolithic** — do not touch `pygm2_es_core.ts` (doesn't exist; confirm before creating) |

## Drafted translations (reuse the existing "no bundled samples" phrasing
already shipped in each file for string 3; verify accents/diacritics before
committing — French especially, per the CLAUDE.md standing rule)

**de**
1. `📖  Beispielanleitungen`
2. `Beispielanleitungen`
3. `_In dieser Version wurden keine mitgelieferten Beispiele gefunden._`
4. `_Für **{0}** ist keine Dokumentation enthalten._`

**it**
1. `📖  Guide agli esempi`
2. `Guide agli esempi`
3. `_In questa versione non è stato trovato alcun esempio incluso._`
4. `_Per **{0}** non è inclusa alcuna documentazione._`

**ru**
1. `📖  Руководства по примерам`
2. `Руководства по примерам`
3. `_В этой сборке не найдено встроенных примеров._`
4. `_Для **{0}** документация не включена._`

**sl**
1. `📖  Vodniki po vzorcih`
2. `Vodniki po vzorcih`
3. `_V tej različici ni bilo najdenih priloženih vzorcev._`
4. `_Za **{0}** ni priložene dokumentacije._`

**uk**
1. `📖  Посібники до прикладів`
2. `Посібники до прикладів`
3. `_У цій збірці не знайдено вбудованих прикладів._`
4. `_Для **{0}** документація не включена._`

**fr**
1. `📖  Guides des exemples`
2. `Guides des exemples`
3. `_Aucun exemple fourni n'a été trouvé dans cette version._`
4. `_Aucune documentation n'est fournie pour **{0}**._`

**es**
1. `📖  Guías de ejemplos`
2. `Guías de ejemplos`
3. `_No se encontraron ejemplos incluidos en esta versión._`
4. `_No se incluye documentación para **{0}**._`

## Per-language checklist (repeat for each row below)

1. Edit the target `.ts`: append message 1 to the `WelcomeTab` context;
   add a new `SampleDocsDialog` context with messages 2–4.
2. Recompile: `python3 scripts/compile_translations.py` (regenerates the
   affected `.qm` only — confirm via `git status` that unrelated `.qm`s
   don't churn).
3. Run the suite (`QT_QPA_PLATFORM=offscreen python3 -m pytest tests/ -q`)
   — expect the existing baseline, 0 failed.
4. Commit + push (message-only + `.qm` binary; one language = one commit),
   flip the checkbox below with the commit hash.

- [ ] de
- [ ] it
- [ ] ru
- [ ] sl
- [ ] uk
- [ ] fr
- [ ] es
