# Plan: move the 2.5D raycast feature into a PyGameMaker extension

Status: **PLAN (2026-07-22), not started.**

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

- [ ] **B1 — render-override + extension-state hooks in core.** With a fixture
  extension proving the hook, before raycast depends on it.
- [ ] **B2 — move the renderer.** `_render_raycast_view` and friends → the
  extension. Core keeps `run_draw_event`/`_render_draw_events`/`_sprite_top_left`.
- [ ] **B3 — move the actions + builders.** The four actions out of static
  `ACTION_TYPES` into the extension.
- [ ] **B4 — decide `facing_angle`.** Recommend leaving it core; document why.

*Cut line: desktop raycast is fully extension-owned; exports still work
unchanged because they match action names.*

### Stage C — move the export contributions (the hard half)

- [ ] **C1 — HTML5 JS injection point** + move the raycast JS out of `engine.js`.
- [ ] **C2 — Kivy scene/codegen contribution** + move the raycast Kivy code out.
- [ ] **C3 — parity tests follow the code** into the extension's own test file.

*Honest note: Stage C is the risky, low-teaching-value part — it's build-system
plumbing, not a readable example. Stopping after Stage B is a legitimate,
defensible end state, with the export renderers documented as "core supports
raycast export; the runtime feature is an extension."*

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
