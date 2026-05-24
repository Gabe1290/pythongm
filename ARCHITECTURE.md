# pygm2 Architecture

A walking tour of how PyGameMaker fits together — for contributors, future
maintainers, and AI agents joining the codebase cold. Everything below is
grounded in file paths and (where stable) line numbers so you can jump
straight in.

This document covers the **what** and the **flow**; for the **why** behind
specific decisions, follow the comments in the code (they reference incidents
and commits) and skim `CLAUDE.md`, `TODO.md`, and `docs/CODE_AUDIT.md`.

---

## 1. Top-level layout

```
main.py                  IDE entry point (CLI launcher)
core/                    Project lifecycle + main IDE window
  ide_window.py            PyGameMakerIDE — QMainWindow shell
  project_manager.py       Load / save / dirty-tracking
  asset_manager.py         In-memory assets_cache (OrderedDict per type)
  logger.py                Unified logger config
editors/                 Per-asset-type editors
  room_editor/             Canvas, palette, tile painter
  object_editor/           Events panel + Blockly + Python tabs
  sprite_editor/           Frame timeline, mask preview
  playground_editor/       Thymio robot arena
  script_editor.py         Minimal QPlainTextEdit fallback
  base_editor.py           Shared lifecycle (save_requested signal, auto-save)
widgets/                 Reusable Qt widgets
  asset_tree/              Project asset browser (left panel)
  welcome_tab.py           Welcome screen, recent projects, samples
  properties_panel.py      Right-side asset properties
events/                  Action / event type registry (UI metadata)
  action_types.py          ActionType registry + BLOCKLY_TO_ACTION_MAP
runtime/                 The pygame-based game runtime (used by Test Game / standalone)
  game_runner.py           GameSprite, GameInstance, GameRoom, GameRunner
  action_executor.py       ActionExecutor — 130+ execute_X_action methods
  action_handlers/         Modular handler package (newer style)
  collision_system.py      CollisionMixin (currently dead — see §6)
  run_game.py              Subprocess entry point for Test Game (F5)
importers/               GameMaker (.gmk) → pygm2 native format
  gmk_importer.py          Top-level orchestration
  gmk_parser.py            Binary .gmk reader (versions 7.0 / 8.x)
  gmk_mappings.py          GMK action codes → pygm2 action names
  gmk_converter.py         GMK structures → JSON shape
export/                  pygm2 → other targets
  HTML5/                   Browser export (Pygbag-backed)
  Kivy/                    Kivy/Android export
plugins/                 Optional extra event/action handlers
samples/                 Bundled sample games (read-only, copy-on-open)
tests/                   pytest suite (target: 539 passing, 0 failing)
```

Conventions:
- **Plural** asset_type names for storage (`'rooms'`, `'sprites'`) — see `assets_cache`.
- **Singular** asset_type names in JSON `asset_type` fields (`'room'`, `'sprite'`).
- Asset categories are open-set: adding a new one requires registering an
  editor in `core/ide_window.py:on_asset_double_clicked`.

---

## 2. Launch sequence (`python main.py`)

1. **`main.py`** sets `QtWebEngine` paths (Nuitka onefile compat), enforces
   Python 3.10–3.13, configures stdout encoding on Windows, imports
   `PyGameMakerIDE`, and calls `app.exec()`.
2. **`core.ide_window.PyGameMakerIDE.__init__`** (line ~50):
   - Builds `ProjectManager` and `AssetManager` (wired together).
   - Sets up auto-save timer (30s default, see `auto_save_interval`).
   - Calls `setup_ui()` → menu bar + toolbar + center widget + status bar.
   - Restores window geometry from `Config`.
   - Strips bundled-samples paths out of `recent_projects` (one-time
     cleanup, see `_strip_samples_from_recent_projects`).
3. IDE shows the Welcome tab. **No project is auto-loaded.**
4. User opens a project via:
   - File → Open Project
   - File → Recent Projects → `<name>`
   - Welcome tab → "Choose a sample ▾ → `<sample>`"
   - File → Import GameMaker .gmk File…

All four paths route through `PyGameMakerIDE.load_project(path)`
(`core/ide_window.py:1351`).

### Sample auto-promotion

If `load_project` receives a path under `samples/`, it auto-promotes the
project to a working copy under `<Documents>/PyGameMaker Projects/<name>/`
before loading (`_promote_samples_to_working_copy`, line 1306). The
bundled `samples/` folder is **structurally read-only** — a defensive
guard in `core/project_manager.py:_save_to_folder` refuses to write
inside it. This is the rc.11 "samples ship as native folders" change
(commit `f8a0eb7`).

---

## 3. Project format on disk

```
my_project/
├── project.json           Main file — asset metadata + room/object refs
├── rooms/
│   ├── room1.json           Per-room instance data (the heavy stuff)
│   └── room2.json
├── objects/
│   ├── obj_player.json      Per-object events
│   └── obj_wall.json
├── sprites/
│   ├── sprite_player.json   Sprite metadata
│   └── sprite_player.png    Image data (same name, different ext)
├── playgrounds/
│   └── arena1.json          Thymio robot arena
├── sounds/                  *.wav, *.mid (no JSON sidecar)
├── backgrounds/             *.png
├── thumbnails/              Auto-generated, *_thumb.png
└── highscores.json          Runtime-written
```

`project.json` carries asset metadata + a `_external_file` pointer per
asset; the heavy data lives in the per-asset files. On save,
`_prepare_project_data_for_save` (`core/project_manager.py:614`)
deep-copies the live `current_project_data`, replaces each room's
`instances` array with an empty list, sets `instance_count` for
reference, and writes that thinned copy to `project.json`. The real
instance arrays go to `rooms/<room>.json` via `_save_rooms_to_files`.

**Order is preserved** through the round-trip:
- Load: `json.load(..., object_pairs_hook=OrderedDict)` keeps JSON key
  order; `_load_rooms_from_files` merges per-room instances back into the
  in-memory dicts.
- Save: `asset_manager.save_assets_to_project_data` converts OrderedDict
  → regular dict via `dict(items())`, which preserves order in Python
  3.7+. `_atomic_write_json` uses `sort_keys=False`.

This matters because **the first room in `project.json` is the starting
room** at runtime (see `runtime/game_runner.py:find_starting_room`,
line 1915). Users reorder rooms via right-click → "Move Up/Down/Top/
Bottom" or by dragging in the asset tree; both paths go through the
same `assets_cache['rooms']` mutation (see `widgets/asset_tree/
asset_tree_widget.py:_reorder_room` and `dropEvent`).

### `current_project_data` vs `assets_cache`

Two parallel containers hold the same live state, and they share value
references:

- **`ProjectManager.current_project_data`** — the full project dict
  (the thing that gets serialized).
- **`AssetManager.assets_cache`** — `{<asset_type>: OrderedDict(<asset_name>: <asset_dict>)}`.
  Same `<asset_dict>` references as `current_project_data['assets'][<asset_type>][<asset_name>]`.

`save_assets_to_project_data` (asset_manager.py:734) re-syncs the
`['assets']` sub-tree of `current_project_data` from `assets_cache`
just before write, so when reorder / edit code mutates *one*, the other
follows on the next save. Code that mutates one without the other (e.g.
the original `_reorder_room` that loaded from disk and replaced the
dict) is a bug — see `bc7725d`.

---

## 4. Action dispatch chain (Blockly → runtime)

Following an action from a Blockly block to the runtime touches **five
files**. Here's the full path for one concrete example: the
`room_if_next_exists` Blockly block ending up firing
`ActionExecutor.execute_if_next_room_exists_action` at runtime.

```
User drags block into the canvas:
  editors/object_editor/blockly/blockly_blocks.js
      Blockly.Blocks['room_if_next_exists'].init()  → block UI shape
      (toolbox entry: blockly_workspace.html line ~435 + dynamic JS ~2672)

Blockly serializes the block when the user saves the object:
  editors/object_editor/blockly/blockly_generators.js
      case 'room_if_next_exists':                      → produces
          {action: 'if_next_room_exists', parameters: {...}}

That action name is registered for the event-tree picker:
  events/action_types.py
      ACTION_TYPES['if_next_room_exists'] = ActionType(...)
      BLOCKLY_TO_ACTION_MAP['room_if_next_exists'] = 'if_next_room_exists'

At runtime, ActionExecutor.execute_action() dispatches:
  runtime/action_executor.py
      action_handlers['if_next_room_exists'] is bound at class init by
      scanning all execute_*_action methods (line ~60).
      ACTION_ALIASES (line ~302) maps legacy names to canonical handler.

The handler runs:
  runtime/action_executor.py:execute_if_next_room_exists_action  →
      uses helpers _room_neighbor_exists and _dispatch_room_test to
      either gate the next action (GM80 flat) or run then_actions/
      else_actions (Blockly nested).
```

### Two parallel handler systems

`ActionExecutor` registers handlers from **two sources** at init
(`runtime/action_executor.py:60-100`):

1. **Inline `execute_*_action` methods on `ActionExecutor`** — auto-registered
   by pattern match on `execute_<name>_action`. Method name minus prefix +
   suffix = the action name in JSON.
2. **`runtime/action_handlers/` modular package** — newer style; functions
   with signature `(executor, instance, params)` wrapped by `make_wrapper`
   at register time. Existing-method names take precedence (logged as
   "Skipping modular handler").

Both feed the same `self.action_handlers` dict. Aliases (`ACTION_ALIASES`)
let JSON-saved action names stay stable across runtime renames.

### Why so many files for one action?

Blockly (visual) and the event tree (flat list) are two parallel UIs
over the same runtime, and Blockly has its own per-language toolbox /
i18n / generator layers. Adding a new action means touching:
- runtime/action_executor.py (the handler)
- events/action_types.py (event-tree picker entry + Blockly→canonical map)
- editors/object_editor/blockly/blockly_blocks.js (block shape)
- editors/object_editor/blockly/blockly_generators.js (block → JSON)
- editors/object_editor/blockly/blockly_workspace.html (toolbox)
- editors/object_editor/blockly/blockly_i18n.js (fr/de/it/uk labels)
- config/blockly_config.py (preset eligibility)

Recent example: `eb562eb` adding `if_no_next_room_exists` shows the full
seven-file diff. (That action was reverted in `0f7f19a` as redundant —
the lesson stuck.)

---

## 5. The runtime game loop

When the user presses F5 (Test Game), `core.ide_window.test_game`:
1. Iterates open editor tabs and syncs their unsaved data into
   `current_project_data` (so the game sees in-flight edits).
2. Calls `save_project()`.
3. Spawns a subprocess: `python runtime/run_game.py <project_path> <lang>`.

The subprocess isolation is deliberate — it avoids OpenGL conflicts
between Qt WebEngine (Chromium-based, used by the Blockly editor) and
pygame's SDL/OpenGL context.

Inside `run_game.py`, `GameRunner.test_game()` loads, then enters
`run_game_loop()`. **Per-frame order matches GameMaker 7.0** and lives in
`runtime/game_runner.py:2022-2150`:

```
For each instance:
  1. begin_step event
  2. alarms (countdown, fire on zero)
  3. delayed actions (countdown, execute on zero)
  4. step event   ← regular step + nokey check
  5. _process_held_keys(instance)   ← keyboard.<key> + keyboard.anykey

After per-instance pass:
  6. handle_events()   ← pygame keydown/keyup/mouse → press/release events
  7. update()
     a. gravity + friction
     b. speed-based movement (hspeed/vspeed) with collision blocking
     c. fire collision events for blocked movements
     d. grid-based intended movement (_has_intended_move)
     e. general overlap-based collision detection (detect_collisions_for_instance)
     f. separate_overlapping_instances
     g. update spatial grid, check outside_room events
     h. RE-SYNC intended_x/y to current x/y (post-collision invariant)
  8. update_thymio_robots()

For each instance:
  9. end_step event
  10. destroy event (if to_destroy)
  11. clear destroyed instances

  12. render()
  13. process_pending_messages()
  14. clock.tick(fps)
```

Critical invariants (each is comment-tagged in the code):

- **`instance.intended_x/y == instance.x/y`** after every frame. Violations
  lock `_process_held_keys` because it interprets the mismatch as
  "grid-move in progress, skip keyboard input." Re-synced at step 7h.
  (Source incident: commit `8ae3a7a`.)
- **Movement-blocking uses AABB only**; pixel-perfect (`sprite.precise`)
  applies to collision-event firing via `instances_overlap`, NOT to
  `check_movement_collision_with_blocker`. Otherwise sprites with
  transparent edges slip into walls. (Source: commit `e3c0cc5`.)
- **Parent-chain matching** is used in both event firing and movement
  blocking (`_object_matches_target`). Inconsistency here used to let
  the player walk through walls because their `collision_with_<parent>`
  event didn't block the actual child instance. (Source: commit `8ae3a7a`.)
- **Collision events have a 5-frame cooldown** in
  `detect_collisions_for_instance` (post-overlap path) but NOT in the
  movement-blocked path. Cooldown is there to prevent double-fires on
  continuous overlap.

---

## 6. Known dead-or-deferred code paths

- `runtime/collision_system.py:CollisionMixin` is **dead code** —
  `GameRunner` doesn't inherit from it. Phase 2a (commit `e64ac63`)
  intended to wire it in but didn't. The live collision code is in
  `game_runner.py` itself (overridden methods of the same name).
- `runtime/action_executor.py` should eventually split by category
  (movement, drawing, score-lives-health, …). Deferred to post-1.0 with
  rigorous behaviour-preservation methodology — see
  `docs/POST_1_0_REFACTOR.md`.
- Several `ACTION_ALIASES` copies exist in parallel:
  `runtime/action_executor.py` (runtime),
  `editors/object_editor/object_events_panel.py` (event-tree display),
  `events/action_types.py:BLOCKLY_TO_ACTION_MAP` (Blockly serialization).
  Drift between them has caused bugs.

---

## 7. Where to look first when something breaks

| Symptom                                  | Start here                                                    |
| ---------------------------------------- | ------------------------------------------------------------- |
| Game won't launch                        | `runtime/run_game.py`, then `GameRunner.run_game_loop`        |
| Save fires "Preserving" warnings         | Whatever last touched `assets_cache['rooms']`                 |
| Action exists in JSON but does nothing   | `ActionExecutor.action_handlers`, then check `ACTION_ALIASES` |
| Keyboard event doesn't fire              | `_process_held_keys` and `handle_keyboard_press` + `_find_key_in_event` case-folding |
| Player walks through walls               | `check_movement_collision_with_blocker` parent-chain match    |
| Player gets stuck at a wall              | `intended_x/y` sync; collision-event handler clearing speeds  |
| Room order doesn't persist               | `_reorder_room` and `dropEvent` in `asset_tree_widget.py`     |
| New action doesn't appear in Blockly     | See the seven-file checklist in §4                            |
| Tests fail on Windows                    | Run `py -3.12 -m pytest tests/ -q` (not `python3`); see `CLAUDE.md` |

---

## Further reading

- **`CLAUDE.md`** — agent-session notes, current priorities, testing
  conventions.
- **`TODO.md`** — deferred features registry (not silent stubs).
- **`docs/CODE_AUDIT.md`** — §0–§4 audit methodology and findings.
- **`docs/POST_1_0_REFACTOR.md`** — post-1.0 split plan for the four
  giant files.
- **`docs/maze_*_testing_pass.md`** — per-sample testing checklists
  showing the intended user flow end-to-end.
- **`CHANGELOG.md`** — per-rc release notes.
