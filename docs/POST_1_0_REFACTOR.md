# Post-1.0 refactor plan: splitting the four giant files

This document survives into the 1.1 phase. It captures the **why**, the
**when**, and a concrete **how** for breaking up the four files that
currently dominate pygm2's complexity surface. Companion read:
`ARCHITECTURE.md` (current shape) and `docs/CODE_AUDIT.md` (audit-era
methodology).

## Status

**Not started.** Filed during the 1.0 stability push so the plan
survives when attention returns to it.

## Why this is post-1.0

Three reasons it didn't happen before 1.0:

1. **Stability priority.** The user explicitly chose stability over
   features for the rc.11→1.0 window. Refactoring the runtime under a
   testing pass would introduce regressions on top of bugs still being
   surfaced (see commit `bc7725d`, `5ad9191`, `8ae3a7a`, `e3c0cc5`,
   `649084d`, `45dc3fe` from the rc.12 user-testing session).
2. **Bidirectional call graph in `ActionExecutor`.** Recorded in
   `CLAUDE.md`: *"B6 ActionExecutor split deferred to post-1.0 — 130
   execute_* methods / 4604 lines, bidirectional call graph with the
   registry. Don't attempt mid-audit."* Splitting in the middle of a
   call graph that runs in both directions risks subtle dispatch bugs.
3. **Behaviour-preservation methodology.** §1–§3 of the audit
   (`docs/CODE_AUDIT.md`) established a hard requirement: every
   consolidation must be *proven behaviour-preserving against
   pre-refactor HEAD* via a throwaway offscreen-Qt harness, with the
   proof documented in the commit body. That's the right standard but
   it takes time and discipline; combining it with a release crunch is
   asking for cut corners.

## The four files

| File                                    | LoC    | Risk to split | Order |
| --------------------------------------- | ------ | ------------- | ----- |
| `editors/object_editor/object_events_panel.py` | 1,880  | **Low**       | 1st   |
| `core/ide_window.py`                    | 4,153  | Medium        | 2nd   |
| `runtime/game_runner.py`                | 4,680  | Medium-high   | 3rd   |
| `runtime/action_executor.py`            | 5,593  | **High**      | 4th (last) |

Risk ranking weights three factors: how isolated the file's surface
area is, how much state is shared across the call sites, and how
visible a bug introduced by the split would be (UI bugs are visible;
runtime collision bugs hide).

---

## Mandatory methodology (re-read before starting any split)

Cribbed from `docs/CODE_AUDIT.md` §1–§3 and `CLAUDE.md`:

1. **Snapshot pre-refactor HEAD** with `git show HEAD:path` to a temp
   file before extracting anything.
2. **Build an offscreen-Qt harness** that exercises the old vs new
   implementations across a representative-to-exhaustive input matrix.
   For the runtime side, drive it through the existing samples
   (`maze_1`, `maze_2`, `maze_3`) — they collectively touch ~78 of the
   ~207 runtime actions.
3. **Diff observable state** between old and new — not just return
   values, also side effects on `instance.x/y/hspeed/vspeed`,
   `current_room.instances`, `assets_cache`, `is_dirty_flag`.
4. **Document the proof in the commit body.** "Verified against pre-
   refactor HEAD over the maze_1/2/3 sample suite, 0 state diffs across
   30 frames of each room."
5. **One cluster per commit on `main`.** No long-lived branches; each
   step ships independently so a regression is bisectable.
6. **Translation safety**: PySide6 `self.tr()` takes context from the
   *concrete runtime class*, so moving `tr()` calls into a shared
   base/mixin is runtime-safe. Keep divergent strings lexically in
   subclass hooks if extracting common UI scaffolding.
7. **`pyflakes` is not installed** — substitute `py_compile` + import
   sanity. Always run `py -3.12 -m pytest tests/ -q` (Windows) before
   committing.

If you can't satisfy any of these for a particular extraction, leave
the code where it is.

---

## File 1 — `editors/object_editor/object_events_panel.py` (1,880 LoC)

### Current shape

One class `ObjectEventsPanel(QWidget)` holds:
- Tree widget setup
- The massive `show_context_menu` (collision/mouse/keyboard/regular event branches)
- `add_event`, `add_sub_event`, `add_keyboard_event_with_selector`, `add_alarm_event`, `add_mouse_event_with_selector`, `add_collision_event_with_selector`
- `add_action_to_event`, `add_action_to_sub_event`, `add_action_to_collision_event`, `add_action_to_mouse_event`, `add_thymio_action_with_selector`
- `edit_action`, `remove_action`, `remove_event`, `remove_sub_event`
- `refresh_events_display` (the giant render method)
- Several legacy/duplicate `ACTION_ALIASES` map (see §"Consolidation"
  below — this dup lives here).

### Proposed split

```
editors/object_editor/events/
  __init__.py           re-export ObjectEventsPanel for backwards compat
  _panel.py             ObjectEventsPanel — shell + tree widget + signals
  _context_menu.py      build_context_menu(panel, item) — pure dispatch on item shape
  _event_crud.py        add_event / add_sub_event / remove_event / remove_sub_event
  _action_crud.py       add_action_to_event / add_action_to_sub_event /
                        add_action_to_collision_event / add_action_to_mouse_event /
                        edit_action / remove_action
  _render.py            refresh_events_display + AssetTreeItem-style helpers
```

### Why first

- Isolated. Only `ObjectEditor` instantiates this; nothing else
  touches its internals.
- No multithreading, no async. Pure Qt slot/signal flow.
- The recent `649084d` (`_CONTAINER_EVENT_HINTS` guard) and `7c0192c`
  (contextual sub-event adder) already shaped the action-add code into
  clean, separable functions. Most of the extraction is already done
  conceptually.

### Risk callouts

- `show_context_menu` switches on tree-item shape (parent vs no parent,
  string vs dict UserRole). Extract the dispatch table first into
  `_context_menu.py` as a pure function `build_menu_for(item) → QMenu`,
  *before* moving the per-branch handlers out. Otherwise you fragment
  the dispatch logic.
- `_CONTAINER_EVENT_HINTS` is a class attribute that both
  `add_action_to_event` and `show_context_menu` consult — keep it on
  the panel class (or move to a constants module) so both sides see
  the same table.

---

## File 2 — `core/ide_window.py` (4,153 LoC)

### Current shape

One class `PyGameMakerIDE(QMainWindow)` holds:
- UI scaffolding: `setup_ui`, `create_menu_bar`, `create_toolbar`, `create_main_widget`, `create_status_bar` (~500 LoC, mostly QAction wiring)
- Project lifecycle: `new_project`, `open_project`, `save_project`, `save_project_as`, `close_project`, `load_project`
- Asset CRUD wrappers around `ProjectManager.update_asset` etc.
- Editor lifecycle: `open_room_editor`, `open_object_editor`, `open_sprite_editor`, `open_playground_editor`, `open_script_editor`, `close_editor_tab`, `close_editor_by_name`, `float_editor`, `reattach_editor`, `_focus_detached_editor`, `_destroy_detached_editor`
- Test Game / Build subprocess management
- Editor → IDE signal handlers: `on_editor_save_requested`, `on_editor_close_requested`, `on_editor_data_modified`, `on_editor_data_modified`
- Recent projects + Welcome tab interaction
- Samples auto-promotion: `_is_samples_path`, `_promote_samples_to_working_copy`, `_strip_samples_from_recent_projects`
- Properties panel + asset tree integration
- Misc: import/export wrappers, config integration, dirty-state UI updates

### Proposed split

```
core/ide/
  __init__.py              re-export PyGameMakerIDE
  window.py                PyGameMakerIDE main class — pure shell
  _menu_builder.py         build_menu_bar(ide), build_toolbar(ide)
  _editor_lifecycle.py     open_*_editor / close_editor_* / float / reattach /
                           on_editor_save_requested / on_editor_data_modified
  _project_actions.py      new/open/save/close as thin delegators
  _samples.py              _is_samples_path / _promote_samples_to_working_copy /
                           _strip_samples_from_recent_projects
  _test_game.py            test_game + subprocess plumbing
```

### Why second

- Visible UI surface — any regression shows up immediately when the
  user clicks a menu item.
- Lots of inter-method coupling on `self` (the QMainWindow). Real
  extraction means converting many methods into free functions taking
  `ide: PyGameMakerIDE` as their first arg, or using mixins.
- Many of these methods are already thin wrappers; the heavy logic
  lives in `ProjectManager` / `AssetManager`. Extraction gains: the
  file stops being the catch-all for "anything top-level."

### Risk callouts

- **Signal connections live in `setup_connections`** — if you move
  handlers out, the connections still need to find them. Easiest path
  is a partial-class style: `from ._editor_lifecycle import *` adds
  methods to the class via module-level injection (or use mixins).
- The `auto_save_timer` is on `ProjectManager`, but several IDE methods
  also touch dirty state. Audit dirty-state mutations during the split.

---

## File 3 — `runtime/game_runner.py` (4,680 LoC)

### Current shape

Four classes:
- **`GameSprite`** (~400 LoC) — image loading, mask building, frame
  retrieval. Mostly self-contained.
- **`GameInstance`** (~500 LoC) — per-instance state: position, speed,
  alarms, keys_pressed, sprite ref, step() method. Touches sprite,
  action_executor, and the room's spatial grid.
- **`GameRoom`** (~150 LoC) — instance list, spatial grid, collision
  listened-types cache. Self-contained.
- **`GameRunner`** (~3,500 LoC) — orchestration: load, sprites, rooms,
  game loop, collision detection methods (overriding `CollisionMixin`),
  rendering, input dispatch, Thymio integration, view/camera system,
  outside_room events, end-of-game flow, restart logic.

### Proposed split

```
runtime/
  sprite.py               GameSprite (already nearly self-contained)
  instance.py             GameInstance (mostly data, light coupling)
  room.py                 GameRoom + spatial grid helpers
  input_handler.py        handle_keyboard_press / handle_keyboard_release /
                          handle_mouse_press / handle_mouse_release /
                          handle_mouse_motion / _process_held_keys
                          (already partially exists — empty shell)
  collision.py            Replace CollisionMixin (currently dead — see §6
                          of ARCHITECTURE.md) with a working module that
                          GameRunner actually delegates to.
                          Methods: check_movement_collision_with_blocker,
                          detect_collisions_for_instance, instances_overlap,
                          check_collision_at_position, _precise_refine,
                          _resolve_collision_event, _object_matches_target,
                          separate_overlapping_instances, push_back_instance.
  rendering.py            render() + draw queue processing + view offset math
  views.py                update_views + view/camera Phase 2b-2c code
  game_runner.py          GameRunner — orchestration only (game loop,
                          load_project_data_only, find_starting_room,
                          run_game_loop, change_room, restart_room, etc.)
```

### Why third

- The runtime is **less visible** than the IDE — a bug here may hide
  for frames before manifesting. Pure-Python testability is harder
  (needs the pygame display + a project to drive). Compensate with the
  offscreen-Qt + sample-driven harness from the methodology section.
- `GameSprite` and `GameRoom` are easy. `GameInstance` is medium.
  `collision.py` is the load-bearing part — wire the long-dead
  `CollisionMixin` correctly this time.

### Risk callouts

- **`CollisionMixin` is currently dead.** Phase 2a (commit `e64ac63`)
  acknowledged this in its commit message: *"The CollisionMixin in
  runtime/collision_system.py is dead code (GameRunner doesn't inherit
  it) and was left untouched — that's a §4 audit item."* The right
  move is to delete the dead `CollisionMixin` and start fresh with a
  delegate object, **not** revive the mixin pattern.
- The recent collision invariants (commits `8ae3a7a`, `e3c0cc5`) need
  to be **carried into the new module verbatim** with the comment
  blocks intact. The "AABB-only for movement blocking" comment and the
  "parent-chain match symmetry" comment are load-bearing and survived
  multiple bug-hunts.
- `_process_held_keys` has a subtle `is_grid_moving` check that depends
  on `instance.intended_x/y == instance.x/y`. The post-collision
  re-sync at the end of `update()` makes this invariant hold. Both
  pieces must move together — extract `update()` and
  `_process_held_keys` in the same commit.

---

## File 4 — `runtime/action_executor.py` (5,593 LoC) — last and hardest

### Current shape

One class `ActionExecutor` with 130+ `execute_<X>_action` methods,
plus:
- `ACTION_ALIASES` map (~25 entries)
- Auto-registration of `execute_*_action` methods (init scan, ~30 LoC)
- Modular-handler integration via `runtime.action_handlers` package
- `execute_action`, `execute_action_list` (conditional-flow + skip_next),
  `execute_event`, `execute_collision_event`, `execute_collision_action_list`
- Per-action helpers: `_parse_value`, `_evaluate_expression`,
  `_handle_repeat_action`, `_find_matching_end_block`,
  `_dispatch_room_test`, `_room_neighbor_exists`
- Shared state: `self.game_runner`, `self._collision_other`,
  `self._collision_speeds`, `self._event_depth`,
  `self._deferred_create_events`

### Why hardest

- **Bidirectional call graph.** Actions call `execute_action_list`
  recursively (then/else_actions, repeat blocks). The dispatcher and
  the action methods reference each other through `self`.
- **Shared state on `self`.** Splitting into category modules means
  every extracted function needs the executor passed in, OR the
  category modules need to be subclasses/mixins. Mixins multiply the
  inheritance graph; passing the executor in changes every call site
  inside the action methods.
- **130 methods × representative input matrix** is a non-trivial test
  harness.

### Proposed split (one option — alternatives encouraged)

Mixin-based, because passing `executor` into every method would touch
~2000 call sites:

```
runtime/action_executor/
  __init__.py               re-export ActionExecutor
  _base.py                  ActionExecutor — registration, dispatch,
                            execute_action / execute_action_list /
                            execute_event / execute_collision_event,
                            shared state attrs
  _flow.py                  ConditionalFlowMixin — if_*, repeat, else,
                            start_block / end_block, _handle_repeat_action
  _movement.py              MovementMixin — start_moving_direction,
                            set_hspeed/vspeed, move_grid, jump_to_*,
                            snap_to_grid, set_speed, set_direction,
                            move_towards, bounce, reverse_*, etc.
  _drawing.py               DrawingMixin — draw_text, draw_rectangle,
                            draw_circle, draw_sprite, draw_score, etc.
  _score_lives_health.py    ScoreLivesHealthMixin
  _room_nav.py              RoomNavMixin — next_room, previous_room,
                            goto_room, restart_room, if_next_room_exists,
                            if_previous_room_exists, _room_neighbor_exists,
                            _dispatch_room_test
  _spawn.py                 SpawnMixin — create_instance, destroy,
                            change_instance, deferred create events
  _vars.py                  VarsMixin — set_variable, test_variable,
                            _parse_value, _evaluate_expression
  _alarms.py                AlarmsMixin — set_alarm, alarm event firing
  _misc.py                  Misc actions that don't fit a category
```

Each mixin inherits from `object`, defines its `execute_*_action`
methods, and gets composed in by `_base.py`:

```python
class ActionExecutor(
    ConditionalFlowMixin,
    MovementMixin,
    DrawingMixin,
    ScoreLivesHealthMixin,
    RoomNavMixin,
    SpawnMixin,
    VarsMixin,
    AlarmsMixin,
    MiscMixin,
):
    ...
```

The auto-registration scan in `__init__` walks `dir(self)` and picks up
all `execute_*_action` methods regardless of which mixin contributed
them — so it continues to work unchanged.

### Risk callouts

- The mixin inheritance order matters for any method-resolution-order
  collisions. None today, but the split should not introduce any.
- The `ACTION_ALIASES` class attribute on the base must stay on the
  base — mixins shouldn't define their own ALIASES dicts because that
  would split the aliasing surface.
- `_parse_value` and `_evaluate_expression` are called from *many*
  action methods — they're appropriate on the base (`_base.py`) or
  on a shared `_expression_eval.py` that all mixins import as a free
  function. Don't put them on `VarsMixin` only.
- The modular `runtime.action_handlers/` package already exists as a
  parallel handler source. Decide before starting: do new actions go
  into the mixin file or the modular package? Pick one direction and
  document it; the current parallel-systems situation is technical debt.

---

## Companion cleanup (not file splits, but adjacent)

These are smaller items worth tackling alongside the split work:

1. **Consolidate `ACTION_ALIASES` to a single source of truth.** Currently
   in three places (`runtime/action_executor.py`,
   `editors/object_editor/object_events_panel.py`,
   `events/action_types.py:BLOCKLY_TO_ACTION_MAP`). Define once in
   `events/action_types.py` and import from there.
2. **Delete the dead `CollisionMixin`** in `runtime/collision_system.py`
   *after* the runtime/game_runner.py split has produced a working
   replacement. Don't delete before — the file is the natural home for
   the new `collision.py`.
3. **Audit-era `# DEBUG:` comments.** A handful remain in code (not
   logger calls — code comments labeled DEBUG that were notes-to-self
   from the audit). Grep and prune.
4. **`logger.info` emoji noise.** Many "💾 ✅ 🔄" emoji-prefixed info
   logs from the audit era still fire in normal operation. Demote the
   informational ones to debug, keep the ones that are genuinely
   user-facing (Test Game start/stop, project save success).
5. **`docs/CODE_AUDIT.md` §4 follow-ups.** Some of the items listed
   there overlap with this plan; cross-check before starting any split
   so we don't redo audit work.

---

## Suggested sequencing

1. Ship 1.0 on the current structure.
2. Logger noise purge + dead-code deletion (1–2 days). Sets baseline.
3. File 1 (`object_events_panel.py`) — practice the methodology on the
   low-risk file (3–5 days).
4. **Stabilization pause** — actually use the IDE for a week. If the
   split introduced regressions you missed in tests, this is when
   you'll find them.
5. File 2 (`ide_window.py`) — apply lessons from #3 (5–7 days).
6. Stabilization pause (1 week).
7. File 3 (`game_runner.py`) — the runtime needs the offscreen-Qt +
   samples harness from the methodology section. The hardest part is
   building the harness; once built, the splits are mechanical
   (7–10 days for split + harness).
8. Stabilization pause (2 weeks — runtime bugs hide).
9. File 4 (`action_executor.py`) — only after the harness from #7 is
   battle-tested. Plan 2–3 weeks; the bidirectional call graph means
   per-mixin testing is required, not just end-to-end.

Total: ~3 months of focused work, plus stabilization windows. Compress
at your risk.

---

## When to STOP a split mid-flight

Abort criteria:
- Test suite goes from green to red and you can't identify the cause
  within 30 minutes.
- A user-facing bug (or one of the samples) starts behaving differently
  than HEAD.
- The "diff observable state" check from the methodology shows
  divergence you didn't expect.
- You find yourself wanting to "just fix this small thing" inside a
  refactor commit. That's how regressions slip in.

Abort means: `git reset --hard HEAD~N`, take a break, write up what
you learned in this doc, try again later. Sunk-cost into a bad split
ships bugs.
