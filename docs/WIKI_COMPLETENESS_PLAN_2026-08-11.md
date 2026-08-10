# Wiki completeness plan (2026-08-11)

Status: **OPEN — Phase 0 not started.** Written after an audit of the live
wiki (216 pages: 24 canonical English pages × 9 languages, full parity)
following the 2026-08-10 sync (see `docs/SESSION_NOTES.md` / session notes
for that day — 82 unpushed commits, incl. a fabricated-GML fix, were pushed
live).

## Audit findings

- **Images: essentially none.** Grepped every English page for
  `![...]()`/`<img`: 2 hits total, both the same external Wikipedia stock
  photo (an arcade Breakout cabinet) used in `Tutorial-Breakout.md` and
  `Getting-Started-Breakout.md`. Zero screenshots of the actual app — no
  IDE window, no editors, no dialogs, no exported/running game. This is the
  single biggest gap for a visual drag-and-drop IDE.
- **Detail level where content exists: genuinely good, not slop.** Sampled
  `Tutorial-Pong.md`: real numbered steps, exact menu paths ("right-click
  Sprites → Create Sprite"), tables. Tutorial pages run 1,100–2,250 words.
  `Full-Action-Reference.md` is machine-generated, covers all 109 actions
  (8,445 words) — see `tools/gen_action_reference.py`.
- **Coverage gaps — no wiki page at all for:**
  - Sprite Editor (only mentioned in passing inside tutorials)
  - Code Editor / `execute_code`
  - Asset Manager / Trash (soft-delete) — shipped 2026-08-09, undocumented
  - Thymio/Aseba robotics — a whole feature area, one incidental mention
    (`Tutorial-Sokoban.md`)
  - Keyboard shortcuts
  - Troubleshooting / Test Game debugging / reading a crash log
  - Per-export-target depth (`Exporting-Games.md` is one overview page for
    Windows/macOS/HTML5/Linux/Kivy/Android/iOS)
  - Raycast/2.5D as a build-along tutorial (`3D-View.md` is conceptual
    reference only)
  - `match3_*`/`raycast_*`/`treasure`/`views_*` sample projects have no wiki
    tutorial — they DO have in-app Sample Guides
    (`SampleDocsDialog`/`README.<lang>.md` per sample), so this may be
    intentional rather than a gap. **Needs a decision, not just work** (see
    Phase 4).
- **Minor nav gap:** `Home.md`'s own "Wiki Contents" list omits
  `Tutorial-Maze`/`Tutorial-Platformer`/`Tutorial-LunarLander` — they exist
  and are linked from `Tutorials.md`, just not from Home.
- **Separate system, worth noting:** the in-app `Tutorials/` curriculum (9
  HTML lessons, distinct from this wiki) has one real thumbnail PNG per
  lesson (`Tutorials/thumbnails/*.png`) but no in-lesson screenshots either
  — same gap, different content system. Out of scope for this plan unless
  the user wants it folded in.

## Goals

1. Add real screenshots to the highest-traffic pages (Home, Getting
   Started, the tutorials, editor pages).
2. Write the missing feature pages (Sprite Editor, Code Editor, Asset
   Manager/Trash, Thymio, Keyboard Shortcuts, Troubleshooting).
3. Translate new/changed pages into all 8 other languages (own tail, size
   it like the recent i18n arcs — do not treat as free).
4. Fix the Home.md nav gap (5-minute item, do first).

## Non-goals (unless the user asks)

- Rewriting existing tutorial prose that's already accurate and detailed.
- Screenshotting every dialog in the app — prioritize by what a
  new/intermediate user actually hits first.
- Localizing screenshots per-language (plan is one English screenshot set,
  reused across all language pages via the same image file — matches how
  most bilingual docs handle UI chrome that itself isn't localized in the
  wiki's screenshots).

## Method notes

- **Screenshot technique (proven, reuse it):** the 2026-08-10 i18n
  verification session established that an offscreen `QApplication`
  (`QT_QPA_PLATFORM=offscreen`) can `QWidget.grab()` a real, fully laid-out
  widget into a `QPixmap` and save it as PNG — no display needed. Same
  approach here: construct the real widget (main window, `ObjectEditor`,
  `RoomCanvas`, `SpriteEditor`, `AssetManager`'s `TrashDialog`,
  `ExportDialog`, etc.) with representative sample data loaded (e.g. open
  `samples/plateforme_3` or `maze_1` for a populated, non-empty screenshot),
  grab, save.
- **Publishing images is NOT automatic.** `scripts/sync_wiki.sh` only
  copies `wiki/*.md` — confirmed non-`.md` files are never carried to the
  live wiki repo. The script needs a small extension (copy an `images/`
  subfolder too) before screenshots taken here will actually show up on
  github.com. Do this as the first Phase 1 commit, verified with a trivial
  test image before spending time capturing real ones.
- **New pages:** write English first, verify accuracy against the actual
  running feature (don't describe UI from memory/guesswork — this repo's
  wiki audit already found and fixed one fabricated-content class of bug,
  the fabricated-GML tutorials; don't reintroduce that pattern for new
  pages). Translate afterward, same `TranslationBuilder`-adjacent workflow
  used for sample guides. Budget per the 2026-07-20 sample-guide note: ~40%
  of a session per language for a similarly-sized batch — size accordingly,
  don't try to land 8 languages of new content in one sitting.
- One page / one screenshot batch / one language per commit, pushed
  immediately (this repo's standing session-limit discipline) — then a
  separate `scripts/sync_wiki.sh push` once a batch is ready to go live.

## Registry (flip to DONE with commit hash as each unit lands)

### Phase 0 — quick wins
- [x] Fix `Home.md`'s Wiki Contents list to link Maze/Platformer/LunarLander
      tutorials. DONE 2026-08-11, `f919295` (English only — translated
      copies still have the old list; not yet propagated, see note below).
- [x] Add a short "Where do I find X?" cross-link section (wiki tutorials
      vs. in-app Tutorials curriculum vs. in-app Sample Guides) so the three
      content systems don't read as overlapping/redundant. DONE 2026-08-11,
      `f919295`. Menu path (`Help > Tutorials`) and button label
      (`📖 Sample guides`) verified against `core/ide_window.py` and
      `widgets/welcome_tab.py`, not assumed.
- [x] Propagate both fixes into `Home_de.md`/`Home_es.md`/`Home_fr.md`/
      `Home_it.md`/`Home_pt.md`/`Home_ru.md`/`Home_sl.md`/`Home_uk.md`.
      DONE 2026-08-11, `0e0d53d`. Reused each language's already-shipped
      tutorial titles and UI-menu translations rather than inventing new
      terminology; `pt`'s "Sample guides" button falls back to English
      text since that translation is genuinely missing from
      `pygm2_pt.ts` (see `TODO.md`, found this session).
- [x] Push Phase 0 changes to the live wiki via `scripts/sync_wiki.sh push`.
      DONE 2026-08-11 — `a610619..5493493`. **Phase 0 is fully closed.**

### Phase 1 — screenshots infrastructure + first batch — CLOSED 2026-08-11
- [x] Extend `scripts/sync_wiki.sh` to carry an `images/` folder to the live
      wiki. `affa2db`, verified with a throwaway test PNG (pushed, fetched
      from raw.githubusercontent.com/wiki/..., then manually removed —
      the sync script is additive-only by design, so stray files need a
      manual delete).
- [x] Screenshot: main IDE window (empty + with a sample project loaded).
      `a9218b5`. **Privacy fix required**: the Welcome tab's recent-projects
      panel leaked this dev machine's real project history on the first
      capture attempt — fixed by blanking `Config`'s recent-projects list
      + no-opping `add_recent_project` before constructing the window.
      Captured from a scratch copy of `samples/plateforme_3` (never load
      the bundled `samples/` path directly for this — it triggers a
      promotion-copy into the user's real Documents folder).
- [x] Screenshot: Object Editor, Room Editor, Sprite Editor. `a9218b5`.
- [x] Screenshot: Blockly/Playground workspace — **attempted, not
      achieved**. Live Blockly is a `QWebEngineView`; an isolated,
      hard-timeout attempt didn't segfault (the risk the source code
      itself warns about) but rendered solid black — GPU context lost
      under the offscreen platform, no software fallback available.
      Discarded rather than publish a black box. `Visual-Programming.md`
      reuses the Object Editor screenshot (shows the real tab) instead,
      with an honest caption. Getting a true Blockly-canvas screenshot
      needs a real display — out of scope for this automated pass, flag
      for a manual capture if someone's ever driving the app by hand.
- [x] Screenshot: Export dialog. `a9218b5` — also grabbed
      `code-editor.png` (View Generated Code mode) as a bonus for Phase 2.
- [x] Embed the above into `Home.md`, `Getting-Started.md`,
      `Object-Editor.md`, `Room-Editor.md`, `Visual-Programming.md`.
      `a9218b5`, pushed live `6ad6be8`.

### Phase 2 — missing pages (English first)
- [ ] `Sprite-Editor.md`
- [ ] `Code-Editor.md`
- [ ] `Asset-Manager.md` (covers usage tracking, Trash/restore, Clean
      Project)
- [ ] `Thymio-Robotics.md` (Aseba export, the 5 Thymio editor guard
      dialogs, sensor/LED actions)
- [ ] `Keyboard-Shortcuts.md`
- [ ] `Troubleshooting.md` (Test Game crash-log reading, common error
      messages, export dependency errors)

### Phase 3 — deepen existing pages
- [ ] Add step-relevant screenshots into the 6 build-along tutorials at
      their key steps (not just a banner image).
- [ ] Evaluate whether `Exporting-Games.md` needs per-target subpages once
      Phase 2's Troubleshooting page exists to absorb the error-handling
      content (avoid duplicating).

### Phase 4 — decision needed from the user
- [x] **DECIDED 2026-08-11: in-app Sample Guides are sufficient.**
      `match3_*`/`raycast_*`/`treasure`/`views_*` will NOT get wiki
      build-along tutorials — they stay covered only by their existing
      per-sample `README.md` guides. No wiki work planned for these
      samples.

### Phase 5 — translation tail
- [ ] Translate every page touched in Phases 0–4 into de/es/fr/it/pt/ru/sl/uk.
      Size as its own multi-session arc; do not bundle into Phase 2/3 commits.
