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
