# Plan: simplifying the whole interface for 8-9 year old students

Written 2026-10-16. **Nothing implemented yet — this is the research +
proposal only**, per the user's explicit request to produce a plan
before touching code. Logged as open work in `TODO.md` (thread A) before
this doc existed; supersedes that pointer now that the research is done.

## The ask, as given

"A plan to simplify the whole interface to make it easier to use by
8 or 9 year old students." No further constraints were given — this doc
makes the scoping decisions explicit so they can be confirmed or
redirected before any code changes start.

## What already exists (verified against code, not assumed)

A real, working three-tier edition system already exists
(`config/editions.py`, `DEFAULT_EDITION = "beginner"`), but it is
**narrower than "the whole interface"** — it only curates three things:

1. **Which Welcome-tab tutorials show** (`tutorial_folders`): beginner
   sees 6 of the ~16 lessons (Getting Started, First Game, Pong,
   Breakout, Fruit Fusion, Fruit Basket).
2. **Which Welcome-tab sample games show** (`sample_folders`): beginner
   sees 14 of them, hiding the raycast/3D, Block World, and multiplayer
   samples.
3. **The default Blockly toolbox preset** (`config/blockly_config.py`
   `BlocklyConfig.get_beginner()`): roughly **60 actions across 9
   toolbox categories** (Events, Movement, Timing, Drawing,
   Score/Lives/Health, Instance, Room, Game, Control) — a real,
   substantial cut from the full preset's **~159 actions**.

**Nothing else is edition-aware.** Verified directly in the IDE's own
code, not inferred:

- The **main window's menu bar** (`core/ide/_menu_builder.py`) always
  builds all 6 top-level menus (File/Edit/Assets/Build/Tools/Help) with
  **61 `addAction` calls** between them, plus a toolbar — identical for
  a first-time 8-year-old and a teacher doing a GMK import. Items like
  "Export Game" (6 target platforms), "Aseba (Thymio) export", "Open
  Roberta XML import", and the full Preferences dialog's advanced tabs
  are always present.
- The **Object Editor** (`editors/object_editor/object_editor_main.py`)
  always shows **three parallel ways to author the same object's
  behavior** side by side: an "📋 Event List" tab (the traditional
  dropdown-based action editor), a "Blockly" tab (the visual-block
  editor this project's tutorials actually teach), and a
  "💻 Code Editor" tab exposing raw Python with an event-selector
  dropdown — `self.center_tabs.setTabEnabled(self.code_tab_index,
  True)` unconditionally; there is no edition check anywhere in this
  file. A beginner tutorial never asks a student to touch the Code
  Editor tab, but it's sitting right there, one click away, looking just
  as official as the one they're supposed to use.
- The **Blockly workspace chrome itself** (zoom controls, a trash can,
  a context-menu with "Duplicate"/"Add Comment"/"Collapse Block"/"Disable
  Block"/"Help", drag-to-scroll, right-click-to-delete) is the stock
  Blockly UI aimed at any age, not simplified for this audience.
- **Every dialog a beginner can reach from the curated menu items**
  (Export Game, Project Settings → Extensions, Preferences) is the same
  dialog a power user sees — multi-tab, every option visible, no
  "simple" vs "advanced" split within a single dialog.

**Conclusion:** the existing edition system solves "don't show tutorials
a beginner isn't ready for" well, but does nothing for "don't show UI
surface a beginner isn't ready for." Those are different problems, and
only the first one is built.

## Design principles (proposed — confirm or redirect before building)

1. **Don't fork the codebase into two apps.** Every past decision this
   project has made (one engine, one set of actions, plugins/extensions
   over new code paths — see `CLAUDE.md`'s own standing preferences) argues
   for *hiding* complexity per-edition, not maintaining a second simplified
   IDE. The existing `EDITIONS` dict is the right mechanism to extend, not
   replace.
2. **Age 8-9 means pre-touch-typing, early reading fluency, and a short
   patience budget for "where did that menu go."** The concrete,
   actionable version of that: fewer simultaneous choices per screen,
   bigger click targets, icons that carry meaning without reading text,
   and — most importantly — **only one way to do a given thing** visible
   at a time (the three-tabs-for-one-concept problem above is the single
   biggest offender found in this research).
3. **Reversible, not destructive.** A kid-simplified view should be a
   *view* a teacher/parent can toggle off, not a separate save format or
   a one-way migration — this project's "stability over features" stance
   and its history of regretting one-way changes (e.g. the asset-trash
   soft-delete work explicitly chose reversibility over `QUndoStack`
   for exactly this reason) both point the same way.
4. **Reuse the edition system's plumbing; extend its scope.** `EDITIONS`
   already has a config-driven shape (`tutorial_folders`,
   `sample_folders`, `default_blockly_preset`). Adding new keys to the
   same dict (see Phase 2 below) is far lower-risk than inventing a
   parallel mechanism.

## Phase 0 decisions (RESOLVED 2026-10-16, user confirmed)

1. **New `"junior"` tier**, not a redefinition of `"beginner"`. Purely
   additive — existing beginner-edition users/docs are undisturbed.
2. **Visual restyling is in scope**, not deferred. See Phase 2.5 below
   for what already exists to build on (`utils/theme_manager.py`) and
   what's genuinely new work (there is no existing global font-size or
   icon-size knob — only a real `ThemeManager` + `themes.json` for
   *color* palettes, confirmed by reading it directly).
3. **Hide the Code Editor tab entirely** for the junior tier (not a
   Preferences toggle).

## Proposed phases

### Phase 0 — DONE (2026-10-16): scoping questions resolved, see above

### Phase 1 — DONE (2026-10-16, commit `1fb96943`): Object Editor three-paradigm problem

`config/editions.py` gained the `"junior"` tier (inheriting beginner's
tutorial/sample curation for now) with a new
`"hide_advanced_object_editor_tabs"` flag.
`editors/object_editor/object_editor_main.py` reads it right after both
tabs are built and `removeTab()`s "📋 Event List" and "💻 Code Editor",
leaving Blockly as the only authoring surface. `removeTab()` only
detaches the widget from the tab bar — `self.actions_widget`/
`self.code_editor`/`self.custom_code_by_event` and every signal
connection stay real and intact, confirmed directly (`indexOf()` on the
detached widget's parent returns -1, but `hasattr` on every
data-carrying attribute is still true) — so a project with existing
custom code still loads and runs correctly; the tab to edit it just
isn't shown in this tier. 5 new tests
(`tests/test_junior_edition_object_editor_tabs.py`), full suite green
(6212 passed).

### Phase 2 — DONE (2026-10-16): `EDITIONS` menu/toolbar curation

Add a new key (e.g. `"menu_items"` or `"hidden_menu_actions"`) to the
kid tier's entry in `config/editions.py`, consumed by
`core/ide/_menu_builder.py` at menu-build time. Needs a first pass
through all 61 actions to sort into "keep" (New/Open/Save project, Test
Game, the asset-creation submenu, basic Edit undo/redo) vs. "hide for
this tier" (GMK/Roberta import, Aseba export, multi-platform Export
Game's advanced options, Find/Replace, the Code Editor's menu
entry-points if any exist outside the Object Editor tab itself) — this
sort is real work, not mechanical, and should be its own reviewed list
before implementation, not decided inline while writing menu-builder
code.

**Shipped:** `"hidden_menu_actions"` / `"hidden_toolbar_actions"` on the
junior tier, keyed by slot name (`create_action` now sets
`QAction.objectName()` from the slot). `_apply_edition_menu_curation` removes
them after extension contributions and tidies stray separators. The QActions
still exist, so `update_ui_state()` is unaffected. **The keep/hide sort was
made by Claude, not reviewed by the user** -- it is one frozenset in
`config/editions.py`, trivially editable. Kept: new/open/save/save-as/close,
recent, Test Game, Export Game, sprite/sound/background import, object/room
creation, undo/redo/clipboard, Preferences (a teacher needs it to switch
edition back), Restore Deleted Assets, Language, Help. Hidden: HTML5/Zip/
Kivy/Project exports, Open Zip, GMK import, auto-save toggles/settings,
Project Settings, Find/Replace, script/font creation, object/room package
import, Debug/Build/Build-and-Run, Configure Action Blocks, and the
maintenance tools. `tests/test_junior_edition_menu_curation.py`.

### Phase 2.5 — DONE (2026-10-16, commit `b92edb58`): visual restyling

**Correction to this phase's original research**: it claimed "there is
no global font-size knob anywhere in the app" — wrong, found while
implementing. `main.py`'s `setup_application()` already has a complete,
working global-font pipeline (`Config.get_font_config()` →
`app.setFont()`), just not edition-aware. Only the *icon*-size half of
the original claim held up (no existing knob at all for that).

What shipped: a new `"junior"` entry in `utils/themes.json` (reusing the
real `ThemeManager`/`QPalette` system `dark`/`light`/`default` already
use — a high-contrast, kid-friendly palette, verified with a real
round trip through `ThemeManager.apply_theme()`, not just JSON
validation); a bigger default font (13pt vs. generic 10pt) and bigger
main-toolbar icons (32px vs. 16px) for the tier. `config/editions.py`
gained a `resolve_startup_visual_overrides(config_data)` helper so
picking "Junior" never silently overrides a theme/font a teacher
already chose explicitly via Preferences on a shared machine — it
returns `None` for a setting the raw saved config shows was ever
touched, falling back to the edition default only when genuinely
unset. 12 new tests (`tests/test_junior_edition_visual_defaults.py`),
full suite green (6224 passed).

**Found, not fixed (logged in `TODO.md` instead, real scope creep):**
Preferences' "UI Scale" spinner (`appearance.ui_scale`) is saved but
never actually applied anywhere in the app — a genuine pre-existing
dead-config bug, unrelated to this phase (this phase's font/icon work
used its own explicit, narrower calls instead of trying to wire up
`ui_scale` properly).

**Not done, deliberately out of scope for this phase:** the planned
screenshot pass to check whether the bigger font breaks any
hardcoded-pixel dialog layout. Worth doing before this ships to real
users, but didn't block landing the mechanism itself.

### Phase 3 — DONE (2026-10-16): Blockly toolbox: a tier below `beginner`'s ~60 actions

**Shipped (revised: "tutorials only"):** `BlocklyConfig.JUNIOR_BLOCKS`, an explicit 46-block list derived from the junior tutorials (01-04, 15, 16) reference projects plus lesson text, pinned both ways by `tests/test_junior_blockly_preset.py` (every needed block present, nothing beyond). It is not a subset of beginner: it adds if_condition, set_variable, draw_variable, room_goto, set_sprite, which Pong and Fruit Fusion/Basket need and which junior cannot switch on itself (Configure Action Blocks is hidden). It drops if_collision, set_gravity, instance_change, move_direction, room_if_*, and all code-like blocks. Samples using dropped blocks still load; the block just cannot be re-picked.


`BlocklyConfig.get_beginner()` already proves the preset mechanism
works and is well-exercised (it's the live default today). The junior
tier doesn't need a new mechanism, just a new, smaller `get_junior()`
preset — likely built the same way `get_beginner()` itself was built
(grep every beginner-edition *sample's* `project.json` for actions
actually used, per that method's own code comments, rather than
guessing from category names). Open question, not yet resolved: does
the junior tier need its *own* curated tutorial/sample set too
(narrower than beginner's 6 tutorials), or does it inherit beginner's
content and only cut the toolbox further? Likely inherits — a 4th
content curation on top of three existing ones is probably
over-fragmenting the curriculum for a cut this narrow, but worth
confirming before Phase 3 starts.

### Phase 4 — DONE (2026-10-16): Blockly workspace chrome

**Shipped:** the junior edition (`simplify_blockly_chrome`) loads the page with `?junior=1`, which unregisters 11 right-click entries (collapse/expand, comment, disable, inline, help, workspace collapse/expand/comments, delete-all). Duplicate, Delete, Undo/Redo and Clean up stay. Verified in a real QtWebEngine page (12 registered entries -> 5). Not touched: zoom controls, trash can, wheel zoom -- all useful to kids. `tests/test_junior_blockly_chrome.py`.


Lowest priority, highest uncertainty (this is Blockly's own stock UI,
not this project's code) — a lighter pass once Phases 1-3 are live and
the user has seen them in practice: consider hiding or simplifying the
block right-click context menu's more advanced entries
("Collapse Block", "Disable Block", "Inline Inputs") for the kid tier.
Needs its own investigation into whether Blockly's JS API exposes a
clean way to do this per-session (likely via `blockly_workspace.html`'s
existing `BLOCKLY_LANG`-style global flag pattern) before committing to
an approach.

## What this plan deliberately does NOT propose

- **No new save format, no project migration.** The kid tier changes
  what's *visible*, never what's *stored* — a project started in the kid
  tier opens identically in beginner/advanced/development.
- **No rewrite of the Blockly engine or the action system.** Every
  action used by a sample/tutorial already in the beginner curriculum
  stays exactly as-is; this is a visibility/curation problem, not a
  capabilities problem.
## Honest sizing

Phase 1 (Object Editor tabs) is a single well-scoped session: one
file's edition check, one regression test file, done the way this
repo's other single-cluster fixes have been (see the Blockly
category-mismatch work this same week for the shape of "one finding,
one commit, one test"). Phase 2.5 (restyling) is its own session —
the `themes.json` color entry is cheap, but the font/icon-size work
needs a real screenshot pass to catch layout breakage, which is the
slow part. Phases 2 and 3 are each their own session-sized
audit-then-fix pass (the 61-menu-action sort for Phase 2 especially —
sorting real UI into "keep"/"cut" needs the user's judgment on several
of them, not just mine). Phase 4 is open-ended and should be scoped
properly only after seeing Phases 1-3 land. **Total: roughly 4-5
sessions** now that restyling is in scope.

## Session log

- **2026-10-16, Phase 0 resolved.** User decisions: new `"junior"`
  tier; visual restyling in scope; hide the Code Editor tab entirely.
- **2026-10-16, Phase 1 done** (`1fb96943`). See Phase 1 above.
- **2026-10-16, Phase 2.5 done** (`b92edb58`). See Phase 2.5 above.
  Only Phase 2 (menu/toolbar curation) and Phase 3 (a junior Blockly
  preset) remain, plus Phase 4 (Blockly workspace chrome, lowest
  priority). Phase 2 is next.
- **2026-10-16, Phase 2 revised on user direction:** HTML5 is the only export a junior sees (File > Export as HTML5 + toolbar button; Export Game dialog hidden). Sprite editing stays available (double-click a sprite; Import Sprite kept). Gap: there is no 'new blank sprite' menu entry in any tier.
- **2026-10-16, Create Sprite added** (Assets menu, all editions): blank 32x32 transparent PNG, opens the sprite editor; refuses a name that already exists.
- **2026-10-16, Phase 4 done -- all phases closed.** Still needs human eyes: nobody has run the junior edition in the real IDE (bigger font vs. hardcoded dialog layouts was never screenshot-checked).
- **2026-10-16, Phase 3 done.** Phase 4 (Blockly workspace chrome) is the only phase left.
- **2026-10-16, Phase 2 done.** See Phase 2 above. Phase 3 (junior Blockly
  preset) is next.
