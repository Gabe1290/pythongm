# Plan: move the 2.5D raycast feature into a PyGameMaker extension

Status: **STAGE B COMPLETE, INCLUDING B3b (2026-07-23).** Stage A (A1–A3) and
Stage B (B1–B4 + B3b) are done: the 2.5D raycast **renderer**, all four
**actions**, their **handlers**, the HUD **builders**, and now all per-room
**state** (`room.extension_state["raycast"]`) live in `extensions/raycast_2_5d/`.
Core's `GameRoom` carries **nothing** raycast-specific. Desktop raycast is fully
extension-owned. The only remaining item is **Stage C** — move the HTML5/Kivy
export renderers into the extension (the risky, low-teaching-value build-system
half). Stopping here is a defensible end state; the exports already work because
they key off action names.

## Why

A stated objective of this project is teaching Python **at all levels, up to and
including programming an IDE like PyGameMaker itself**. The 2.5D/DOOM-like
raycast feature is currently woven through the core engine (see the footprint
below), which makes it invisible as a *unit of work* — a student can't see
"here is a self-contained feature someone added to the IDE."

Moving it into an extension serves two goals:

1. **Pedagogy.** The extension becomes a worked example of extending an IDE: a
   readable, self-contained folder a student can open, understand, modify, or
   copy to build their own feature.
2. **Reuse.** Once the extension mechanism exists, other optional features
   (Thymio, exotic exporters, experimental actions) can use it, and optional
   features stop inflating the core.

The user accepted that this is "a bit more complicated" than leaving it in core.
This plan is written to be honest about *how* much more complicated, and to
stage the work so value lands early and the risky part is separable.

## What exists today — an honest assessment

There **is** a plugin system (`events/plugin_loader.py` + `plugins/`), and
`plugins/audio_actions.py` uses it. Its contract:

- a single `.py` file in `plugins/`, declaring `PLUGIN_NAME` / `PLUGIN_VERSION`
  / `PLUGIN_AUTHOR` / `PLUGIN_DESCRIPTION`;
- `PLUGIN_ACTIONS: Dict[str, ActionType]` → merged into `ACTION_TYPES`
  (skipped if the name already exists — the shadowing landmine in CLAUDE.md);
- optionally `PLUGIN_EVENTS` → merged into `EVENT_TYPES`;
- an executor class whose `execute_*_action` methods are registered via
  `ActionExecutor.register_custom_action`.

**Three gaps make it unable to hold raycast today.** All verified against code:

1. **The IDE never loads plugins.** `load_all_plugins()` is called in exactly
   one place — `GameRunner.__init__` (`runtime/game_runner.py:2576`). Nothing in
   `core/`, `main.py`, `editors/` or `widgets/` loads them. Proof:
   `'play_sound' in ACTION_TYPES` is **False** outside a running game, while
   `'enable_raycast_view'` is **True** (it's static). So plugin actions are
   second-class — they work at runtime but don't populate the IDE's action
   registry. Moving raycast to a plugin as-is would delete it from the IDE's
   action picker. **This is the foundational fix and must come first.**
2. **No render hook.** Raycast doesn't just add actions — it *replaces the room
   render*. `GameRoom._render_room` early-returns into `_render_raycast_view`.
   Plugins can contribute actions, not rendering.
3. **No export contribution mechanism.** The HTML5 and Kivy exporters contain
   hand-written raycast renderers. A plugin cannot contribute JS or Kivy codegen.

## The footprint being moved (measured, not estimated)

Raycast-related lines per core file (`raycast|facing_angle|minimap|doom_hud|
_cast_ray|billboard|floor_plane|floor_buffer|viewport_height|wall_height`):

| File | Matches | Of |
|---|---|---|
| `runtime/game_runner.py` | 80 | 6165 |
| `runtime/action_executor.py` | 58 | 6719 |
| `events/action_types.py` | 29 | 2623 |
| `export/HTML5/templates/engine.js` | 76 | 4010 |
| `export/Kivy/kivy_exporter.py` | 146 | 4922 |
| `export/Kivy/code_generator.py` | 24 | 1466 |

~410 touchpoints across six files, but they are **not evenly hard**: the two
runtime files are ordinary Python (movable), while the three export files are
hand-written renderers in a JS template and a `.format()`-string Kivy template
(much harder — see Stage C).

### What is genuinely raycast-specific vs. generic

Worth separating, because some of it **should stay in core**:

- **Move (raycast-specific):** `_render_raycast_view`, `_cast_ray`,
  `_build_raycast_walls`, `_cast_floor_plane`, `_wall_shade`, the billboard
  pass, `RAYCAST_*` constants, the four actions (`enable_raycast_view`,
  `set_facing_angle`, `draw_minimap`, `draw_doom_hud`) and their builders
  (`build_minimap_commands`, `build_doom_hud_commands`, `doom_face_frame`).
- **Keep in core (generic, already used by non-raycast paths):**
  `run_draw_event` / `_render_draw_events` (compositing draw events over *any*
  custom render — not raycast-specific), `_sprite_top_left` (origin-aware
  helper), the `rectangle`/`line`/`text`/`sprite`/`lives` draw-queue types.
- **Awkward, needs a decision:** `facing_angle`. It's a `GameInstance`
  attribute *and* it's referenced by the expression parser so authors can write
  `set_direction_speed(direction="facing_angle")`. Extracting it means either
  (a) a generic "extensions may register expression variables" hook, or
  (b) leaving `facing_angle` in core as a general-purpose instance property
  (defensible — a persistent facing direction isn't inherently 3D).
  **Recommendation: (b)**, and say so in the extension's README.

## Design: what an extension is

Extend the existing plugin system rather than inventing a parallel one — a
second mechanism would be worse for the teaching goal, not better.

```
extensions/
  raycast_2_5d/
    extension.json        # manifest: name, version, description, enabled-by-default
    actions.py            # ActionType schemas (the four actions)
    handlers.py           # execute_*_action methods (the executor class)
    renderer.py           # the raycast renderer: DDA, walls, floor, billboards
    hud.py                # build_minimap_commands / build_doom_hud_commands
    export_html5.js       # JS contributed to the HTML5 engine (Stage C)
    export_kivy.py        # Kivy scene methods + codegen (Stage C)
    README.md             # what it does + how it hooks in (the teaching artifact)
```

Single-file `plugins/*.py` keeps working unchanged (audio_actions must not
regress); folder-based extensions are the richer form.

## The hook API core must grow

Each hook is small, generic, and justified by more than raycast — that's the
test for whether it belongs in core at all.

1. **Extension loading in the IDE** (Stage A). A single load point both the IDE
   and `GameRunner` call, so `ACTION_TYPES` is identically populated in both.
   *Generic value:* fixes plugin actions being invisible in the IDE — an
   existing latent bug, not just a raycast need.
2. **Room render override** (Stage B). Before its normal render, `GameRoom`
   asks registered extensions whether one claims this room's render; if one
   returns True, core skips the top-down pass and still runs the draw-event
   compositing pass afterwards. *Generic value:* any alternate renderer
   (isometric, hex, top-down-with-shaders) uses the same hook.
3. **Per-room extension state.** A plain `room.extension_state: dict` so an
   extension can stash its camera config without core knowing about
   `raycast_camera`. *Generic value:* any stateful extension.
4. **Export contributions** (Stage C, the hard one):
   - **HTML5:** the exporter already reads `engine.js` as one string
     (`html5_exporter.py:38`), so an extension's JS can be concatenated at a
     marker. Feasible.
   - **Kivy:** the scene is a `.format()` template; contributing scene methods
     means adding an injection point and having extensions supply template
     text. Feasible but fiddly (the brace-doubling landmine applies).

## Staging — and the key decoupling that makes this safe

**Exporters key off action *names* in the project JSON; they do not import
`ACTION_TYPES`.** So moving an action's schema + desktop handler into an
extension does **not** break the HTML5/Kivy exports — they keep emitting their
own raycast code. That means Stage B can ship without touching the exporters,
and Stage C is genuinely optional/deferrable.

### Stage A — the extension mechanism (no raycast moved)

- [ ] **A1 — one load point, used by IDE and runtime.** Extract plugin/extension
  loading so the IDE populates `ACTION_TYPES` the same way `GameRunner` does.
  Test: `play_sound` is visible in `ACTION_TYPES` after the IDE's startup path,
  and audio actions still work at runtime.
- [ ] **A2 — folder extensions + manifest.** Loader supports `extensions/<name>/`
  with `extension.json`, alongside existing single-file plugins. Test: a
  fixture extension loads; `plugins/audio_actions.py` still loads unchanged.
- [ ] **A3 — enable/disable.** Config-driven on/off per extension, surfaced
  where the editions/sample curation lives. Test: a disabled extension
  contributes nothing.

*Cut line: the mechanism is usable by any optional feature even if raycast never
moves.*

### Stage B — move the raycast runtime into the extension

- [x] **B1 — render-override + extension-state hooks in core.** Done (commit
  `13e0650`). `runtime/extension_hooks.py` is a dependency-free registry both
  `events/plugin_loader` (registers) and `runtime/game_runner` (invokes) import;
  a room renderer is declared as `PLUGIN_ROOM_RENDERERS = [fn]` and returns True
  to claim a room. `GameRoom.extension_state` is the per-room namespace.
  Proven with a fixture extension before raycast depended on it.
- [x] **B2 — move the renderer.** `_render_raycast_view` and friends → the
  extension (`extensions/raycast_2_5d/renderer.py`, done 2026-07-23). Core keeps
  `run_draw_event`/`_render_draw_events`/`_sprite_top_left`. The renderer was
  extracted behaviour-identical (`self` → an explicit `room` param, class
  constants → module constants), proven pixel-for-pixel against pre-move HEAD
  across a flat/textured/sky/floor/letterbox/no-camera matrix and a 480-ray DDA
  matrix before the core copy was deleted. `GameRoom._render_room` now draws
  raycast rooms through the Stage-B1 `extension_hooks` seam — the built-in
  `if self.raycast_camera.get('enabled')` branch is gone. The four raycast
  actions + the `raycast_camera`/wall-cache state they set stay in core (B3).
  Two things worth carrying forward: (1) `load_all_plugins` now re-registers
  room renderers on every call (idempotent), because the hook registry is
  process-global state a test can clear — without it a later GameRunner in the
  same process would silently lose extension rendering. (2) The loader imports a
  folder extension under a synthetic package name (`pygm_extension_<folder>`),
  so its `renderer` submodule is a DIFFERENT object from
  `extensions.raycast_2_5d.renderer` imported the normal way. Harmless for the
  renderer (no module-level mutable state), but a test that spies on the render
  path must patch the *loaded* copy — see `_loaded_renderer()` in
  `tests/test_raycast_viewport.py`.
- [x] **B3 — move the actions + builders.** Done in three commits (2026-07-23):
  `8ca55c9` set_facing_angle + enable_raycast_view, `74e418b` draw_minimap +
  build_minimap_commands, `fa9219f` draw_doom_hud + build_doom_hud_commands +
  doom_face_frame. All four "3D View" action **schemas** are now in
  `extensions/raycast_2_5d/actions.py` (`PLUGIN_ACTIONS`), the **handlers** in
  `handlers.py` (`PluginExecutor`), and the HUD **builders** in `hud.py`. Core's
  static `ACTION_TYPES` has no 3D-View entry and `action_executor.py` no raycast
  handler/builder — only pointer comments. The loader merges the schemas back
  into `ACTION_TYPES` at startup so the picker/Blockly still see them.
  - **The one mechanical change:** a plugin handler runs as a `PluginExecutor`
    method, not an `ActionExecutor` method, so `self.game_runner` /
    `self._parse_value` became `instance.action_executor.game_runner` /
    `._parse_value` — the same handle `plugins/audio_actions` uses. Tests that
    used to call `executor.execute_*_action` directly now load the extension and
    dispatch through `action_handlers`, and registration tests call
    `load_all_plugins()` before querying `get_action_type` / `ACTION_TYPES`.
- [x] **B3b — move the state into `room.extension_state`.** Done (2026-07-23,
  commit after `fa9219f`). All raycast per-room state — the `camera` config the
  action sets and the derived wall-edge caches — now lives under
  `room.extension_state["raycast"]`, reached through
  `extensions/raycast_2_5d/state.py`'s `raycast_state(room)` (get-or-create) and
  `peek_camera(room)` (non-creating, for the render hook, which runs on every
  room and must not stamp raycast state onto non-raycast ones). `GameRoom.__init__`
  dropped all six raycast attributes and keeps only `extension_state = {}`; core
  now carries **nothing** raycast-specific. Proven behaviour-identical by running
  raycast_3 through the real loop (camera enabled, 123 wall edges built in
  `extension_state`, no raycast attrs on `GameRoom`) and the full suite. The
  Kivy/HTML5 ports are unaffected — their scene keeps its own `self._raycast_*`;
  only the desktop extension's storage changed, so the parity test feeds each
  side its own way (`raycast_state(room)[...]` vs `scene._raycast_*`).
- [x] **B4 — decide `facing_angle`: leave it in core.** Recommendation (b)
  adopted. `facing_angle` stays a plain `GameInstance` attribute (initialised in
  `game_runner.py`), because a persistent look/facing direction isn't inherently
  3D and the expression parser references it by name
  (`set_direction_speed(direction="facing_angle")`); extracting it would mean
  building a generic "extensions register expression variables" hook for a single
  case. Documented in the extension's `handlers.py` / `README.md`. `set_facing_angle`
  (the action that writes it) moved to the extension in B3; the attribute it
  writes did not.

*Cut line: desktop raycast is fully extension-owned; exports still work
unchanged because they match action names. Reached — Stage C (below) is
optional.*

### Stage C — move the export contributions (the hard half)

Decision (2026-07-23): do the **full clean mechanism**, not a partial relocation.
The HTML5 (`engine.js`) and Kivy (`kivy_exporter.py`) engines have **no**
extension system — unlike Stage B, which leaned on the existing plugin loader —
so Stage C first *builds* one on each target (a render-hook registry **and** an
action-dispatch registry, plus a code-injection point the exporter fills from
each enabled extension), then moves the raycast code onto it. End state:
`engine.js` and `kivy_exporter.py` know **nothing** about raycast. Mirrors the
desktop `extension_hooks` + plugin-action split. Worked as a queue of small
committed units (session-limit discipline); each keeps the full suite at 0
failed and smoke 17/17.

Structural map (measured):
- `engine.js` (4010 lines): raycast render is 5 methods **inside** `class
  GameRoom {}` (`buildRaycastWalls`/`castRay`/`wallShade`/`renderRaycastView`/
  `castFloorPlane`) + `RAYCAST_*` module consts; the dispatch is in
  `GameRoom.render` (`if (this.raycastCamera && ...enabled)`); the actions are
  three `case`s in `GameObject.executeAction`'s `switch` (`draw_doom_hud`,
  `draw_minimap`, `enable_raycast_view`) before its `default:`.
- `HTML5Exporter` reads `engine.js` as one string and substitutes it into the
  page — so an injection **marker** near EOF (after all classes, before the
  `load` bootstrap) is where extension JS concatenates.

- [x] **C1a — HTML5 extension mechanism (inert; prove the seam first).** Done
  (`d66fdea`). `engine.js` gained `registerRoomRenderer`/`renderExtensionRoom`
  (called first in `GameRoom.render`; a claim runs the draw-event/HUD pass and
  returns) and `registerExtensionAction`/`_extActions` (consulted in
  `executeAction`'s `default:`), plus a `// __PYGM_EXTENSION_JS__` marker.
  `HTML5Exporter._collect_extension_js` concatenates each **enabled** extension's
  `export_html5.js` at the marker (raycast had none yet, so inert). Proven with a
  fixture extension in `tests/test_html5_extension_mechanism.py`.
- [x] **C1b — move the raycast HTML5 RENDER.** Done. `RAYCAST_*` consts + the 5
  render methods → `extensions/raycast_2_5d/export_html5.js`, wrapped in
  `Object.assign(GameRoom.prototype, {…})` (method signatures preserved verbatim
  so the parity regexes still match) and registered through
  `registerRoomRenderer`. The `raycastCamera.enabled` dispatch in
  `GameRoom.render` is deleted — the generic hook replaces it. `GameRoom.
  spriteTopLeft` (the generic origin helper) stays in `engine.js`. Extraction was
  brace-count-verified (both files stay brace-balanced) since no `node` was
  available to validate JS execution. HTML5 tests now read the shipped
  `engine.js + export_html5.js` (a combined `ENGINE`, with `ENGINE_CORE` /
  `RAYCAST_JS` kept separable for structural tests).
- [ ] **C1c — move the raycast HTML5 ACTIONS.** The three `case`s →
  `registerExtensionAction(...)` in `export_html5.js`; removed from the switch.
- [ ] **C1d — HTML5 tests follow the code.** `test_html5_raycast` /
  `test_raycast_export_parity` read `export_html5.js` for the moved strings; a
  new test covers the injection mechanism.
- [ ] **C2a — Kivy extension mechanism (inert).** Same shape in the `.format()`
  scene/base templates + `code_generator`; exporter injects each enabled
  extension's `export_kivy.py` fragments. Brace-doubling landmine applies.
- [ ] **C2b — move the raycast Kivy RENDER + scene state.**
- [ ] **C2c — move the raycast Kivy codegen (actions).**
- [ ] **C3 — parity tests consolidated; full suite + smoke green.**

*Honest note (unchanged): Stage C is the risky, low-teaching-value part — it's
build-system plumbing. Stage B was already a defensible end state; this stage is
being done because the full clean move was explicitly chosen.*

## Testing / the regression bar

Non-negotiable at **every** unit: `py -3.12 -m pytest tests/ -q` stays at **0
failed** (2101 passing today) and `tools/smoke_run_samples.py` stays **17/17**.
The four raycast samples are the integration test — if raycast_1–4 still run,
render and export, the move is behaviour-preserving.

Extra care: the existing raycast tests import from `runtime.game_runner` /
`runtime.action_executor`. As code moves, tests move with it — but a test that
merely changes its import path proves nothing new, so keep the *behavioural*
assertions (the real-loop runs) and let them follow the code.

## Risks, honestly

- **Biggest risk: churn for no visible gain.** 410 touchpoints, 2101 tests, and
  the user-visible behaviour must be *identical* at the end. This is a refactor
  whose success looks like "nothing changed."
- **The IDE-loading fix (A1) may surface latent issues** — plugin actions have
  never been in the IDE's registry, so Blockly/action-picker paths may not
  expect them. Expect to find and fix things there.
- **Stage C touches the export pipeline**, which has historically been where
  silent breakage hides (this session alone found three export gaps). Parity
  tests are the guard.
- **`facing_angle` in the expression parser** is the one genuinely entangled
  piece; the recommendation is to leave it in core rather than build an
  expression-variable hook for a single case.

## Out of scope

- Rewriting the raycast feature itself — this is a *move*, behaviour-identical.
- A plugin marketplace / download mechanism.
- Moving audio actions or Thymio into the new format (they can follow later;
  the mechanism is what unlocks it).
- Any change to how the samples author raycast games — `raycast_1`–`4` must be
  untouched and keep working.
