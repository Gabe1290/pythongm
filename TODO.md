# TODO — Deferred Features

Features that are planned but not yet implemented. Anything listed here used to
either show a "Not Implemented" placeholder dialog or be a stub the user could
click and reach a dead end. To keep the IDE honest, the menu items / buttons
have been removed; the work is tracked here instead.

Add new entries at the top of each section. When you start implementing one,
move it to a feature branch and remove the entry once the feature ships.

---

## IDE features

### Find / Find and Replace
- Was: `Edit → Find...` (Ctrl+F) and `Edit → Find and Replace...` (Ctrl+H).
- Scope: text search across the code editor, room editor scripts, and event
  scripts. Probably also useful across the whole project (asset names,
  identifiers in events).
- Notes: removed the menu entries and the `find()` / `find_replace()` stubs in
  `core/ide_window.py`. When implementing, restore the menu wiring with the
  same Ctrl+F / Ctrl+H shortcuts.

### Asset Manager
- Was: `Tools → Asset Manager...`.
- Scope: bulk operations on assets (rename, move, delete in batch), search and
  filter, usage tracking ("which rooms / objects use this sprite?"), and
  unused-asset cleanup.
- Current workaround: the Asset Tree panel on the left handles single-asset
  operations.
- Notes: removed the menu entry and the `show_asset_manager()` stub in
  `core/ide_window.py`.

### Clean Project
- Was: `Tools → Clean Project`.
- Scope: remove temporary files, delete unused assets, clean build artifacts,
  shrink project size.
- Current workaround: manually delete `.cache/`, `__pycache__/`, `*.pyc`.
- Notes: removed the menu entry and the `clean_project()` stub in
  `core/ide_window.py`.

### Standalone executable build (Build Game / Build and Run)
- Was: `Build → Build Game...` (F7) and `Build → Build and Run` (F8).
- Scope: package the project as a standalone runnable artifact — Windows
  `.exe`, Linux binary, macOS `.app`. Android `.apk` is handled separately via
  the Kivy export path.
- Current workaround: `Build → Test Game` (F5) runs from source; `Build →
  Export Game...` produces an HTML5 build.
- Notes: removed the menu entries, the `build_game()` and `build_and_run()`
  stubs, and the `build_game_action` / `build_and_run_action` enable/disable
  references in `core/ide_window.py`.

### Object test runner ("Play Object" button)
- Was: a planned toolbar button in the Object Editor wired to a `test_object`
  method.
- Scope: run a single object in isolation (without putting it in a room) to
  test its events. Useful for unit-testing object behaviour.
- Notes: the orphaned `test_object` method in
  `editors/object_editor/object_editor_main.py` was removed (no UI element
  called it). Restore the method + a toolbar button when implementing.

### Generic asset-type editor fallback
- Currently when `open_asset_editor` is called with an asset type that has no
  registered editor (anything other than `rooms`, `objects`, `sprites`,
  `playgrounds`, `scripts`), it logs a warning and does nothing. The
  remaining holes are `sounds`, `backgrounds`, and `fonts` — those still
  show "No editor registered for asset type 'X'" if double-clicked.
- TODO: register editors for the remaining asset types, or formalize the
  registration so adding a new asset type fails loudly at startup rather than
  silently at click time.
- `scripts` got a minimal QPlainTextEdit-backed editor in rc.12
  (`editors/script_editor.py`); the same pattern is the cheapest fix
  for the others.
- Same applies to the create-asset fallback in
  `widgets/asset_tree/asset_tree_widget.py` — it now logs and returns silently
  when no `create_asset` handler is reachable.

### UI metadata coverage for runtime actions (partial in rc.12)
- The runtime knows ~207 actions (executor `execute_*_action` methods +
  modular handlers in `runtime/action_handlers/`); the UI-side
  `events/action_types.py` registry covers ~78 of them after the rc.12
  bulk-add. The remaining ~129 still trigger "Unknown action type: X" in
  the events panel when an imported project uses them, even though they
  execute correctly at runtime.
- rc.12 closed the subset visible in the bundled samples (maze_1..4,
  treasure) — 21 ActionType entries added in commit 8c756d7 + this one.
  The rest are mostly particle/draw/timeline/window-management actions
  that no shipped sample currently uses.
- Recipe for adding more: see the comments at the bottom of
  `events/action_types.py` and the survey script that lived briefly at
  `.scratch_find_missing_actions.py` (removed after the bulk pass).
- A future cleanup might generalise `get_action_type` to fall back
  through `ActionExecutor.ACTION_ALIASES` so legacy/alternate action
  names resolve to a single ActionType without duplicate entries.

### GMK importer hardening (post-1.0)
- During rc.12 user-testing the **`treasure.gmk`** and **`maze_4.gmk`**
  samples both exposed importer issues the IDE could only partially
  round-trip — the imported projects loaded but had bad action
  parameters, sprite issues, and half-converted events that produced
  confused state and save errors in the editor surface. Both samples
  were dropped from the bundled set (treasure in commit d3fd71a,
  maze_4 in the commit that adds this entry); they can be
  reintroduced once the importer is hardened.
- The earlier hypothesis that only treasure was affected (because
  it's the only one using project-level scripts) was wrong: maze_4
  has no scripts but still imports with significant gaps. The
  importer issue is broader than first scoped — likely action-
  parameter parsing across a wider feature set than the smaller
  maze_1..3 samples happen to exercise.
- TODO once we have time for it:
  - Regenerate `samples/treasure/` and `samples/maze_4/` from the
    `.gmk` originals (regen path documented in `samples/README.md`).
  - For each, compare against the in-game behaviour of the original
    `.gmk` — e.g. via GameMaker 8.x if available, or by inspecting
    the `.gmk` binary structure with `importers/gmk_parser.py`.
  - Catalog every action whose parameters didn't survive the
    conversion. Likely categories:
      * Action parameter keys renamed (GameMaker had positional
        args; pygm2 expects named) — most-likely root cause
      * Sprite / object references renamed silently when assets had
        case-conflicting or whitespace-bearing names
      * Project-level scripts (`treasure` only) — code that
        references GameMaker built-ins not implemented in the pygm2
        runtime
      * Draw events using `draw_self`, `draw_sprite_ext`, etc.
        without matching UI metadata (the metadata gap is tracked
        separately above)
  - Each finding gets a separate fix in `importers/gmk_*.py` and a
    regression test under `tests/test_importers/`.
  - Consider building a side-by-side diff tool: import a `.gmk`
    twice (once raw, once after each fix) and diff the resulting
    `project.json` trees so regressions in the importer surface as
    review-blocking diffs in CI.
- The maze_1..3 samples shipped clean enough for rc.12 user
  testing — the issue compounds with project complexity
  (room/object count, action variety), so the smaller samples may
  hide the same bugs rather than truly being unaffected. Worth
  re-validating the maze_1..3 imports as part of the eventual
  hardening pass.
- **Concrete findings from rc.12 maze_1 testing pass:**
  - The importer mistranslated `test_previous_room` into
    `test_next_room` on at least one event in maze_1 (obj_goal's
    `p` event). The two are opposite-direction conditional checks
    (`is there a next room?` vs `is there a previous room?`) —
    swapping them silently inverts a navigation guard. Worth
    grepping the importer for places that disambiguate the two
    GMK action codes; the bug is probably a constant lookup with
    a wrong value rather than a logic error.
  - The importer set `visible: false` on `obj_goal` even though
    the source GameMaker project marks the object as visible.
    Symptom: the goal sprite never renders during gameplay, so
    the player has no visual feedback for where to go — only
    walking into the (invisible) goal trigger advances the room.
    Possibly the same root cause as the above (wrong constant
    lookup in the importer's object-attributes table) or a
    separate import-default-value bug.
  - Bundled maze_1 was patched manually in the IDE after these
    findings; the corrected `samples/maze_1/` is back in git.

---

## Runtime action handlers (stubs that just log and return)

In `runtime/action_handlers/extra_handlers.py`:

- **Splash text / image / video / webpage** (lines 51, 57, 63, 69) — these are
  placeholders. Need real implementations using Pygame surfaces / video
  decoder / `webbrowser` module respectively.
- **Execute file** / **Execute shell command** (lines 84, 90) — intentionally
  restricted for security. If we ever expose them, they need to be sandboxed
  and require explicit user opt-in per project.

Other:

- **Script execution action** — `runtime/action_handlers/control_handlers.py:239` —
  stub only. Decide on the script language (Python? a sandboxed mini-DSL?)
  before implementing.
- **Thymio "play sound"** — `runtime/thymio_action_handlers.py` — placeholder
  that emits a single tone instead of playing the requested sound resource.

## Runtime features called out in code

- **Background auto-scroll on `set_background`** —
  `runtime/action_executor.py:3781`. The `hspeed`/`vspeed` accepted by
  the `set_background` action are still ignored; only the room's own
  `bg_hspeed`/`bg_vspeed` (from room config or `set_view`) drive layer
  scrolling today. The view/camera system (Phase 2b–2c) handles full
  room-larger-than-window scrolling, but this specific per-call setter
  needs wiring.
- **Room transition effects** — `runtime/action_executor.py:5111`. Parameter
  accepted but ignored; transitions are instant.

## Export

- **Kivy export — long-tail action coverage** —
  `export/Kivy/code_generator.py:681`. Most actions translate fine; unhandled
  ones fall through to a no-op `pass`. Each one needs to be ported as we hit
  it.

---

## Done since the last review (don't re-add)

- **About dialog license info** — surfaced MIT (code) + CC BY 4.0 (docs) in
  the About PyGameMaker dialog with French translation.
- **macOS App-menu Preferences hijack** — explicit `setMenuRole` calls now
  pin Preferences to `PreferencesRole` and prevent `Configure Thymio Blocks...`
  from being auto-promoted to the App menu.
- **Blockly visual ↔ events sync** — automatic, no manual button needed. See
  `SyncCoordinator` in `editors/object_editor/object_editor_main.py`.
