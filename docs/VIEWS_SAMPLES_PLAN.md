# Plan: sample games introducing views (large-level scrolling)

Status: **planned, not started.** Written 2026-07-15 at ~68% of that
session's budget specifically so it could be picked up cold on a
different machine. Read this whole file before starting — it's the only
record of the investigation, there's no partial branch/WIP to resume.

## Why this exists

The user asked for a set of sample games that introduce **views**
(GameMaker-style cameras) so a level can be much larger than the window.
This doc is the investigation + plan produced before any implementation
started, so the next session doesn't have to re-derive it.

## What's already there (investigated, not guessed)

- **Desktop pygame runtime: fully implemented.** `runtime/game_runner.py`
  has a real GameMaker-style 8-view system: `views_enabled`,
  `self.views` (list of 8 view dicts: `view_x/y/w/h`, `port_x/y/w/h`,
  `follow`, `hborder`/`vborder`, `hspeed`/`vspeed`), `update_views()`
  (~line 1562) does border-based camera-follow with per-axis speed
  limiting and clamps to room bounds — genuinely complete, not a stub.
  `render(screen, view_offset=...)` threads the offset through.
- Action handlers exist and work: `execute_enable_views_action` and
  `execute_set_view_action` in `runtime/action_executor.py` (~line 4146).
  Full parameter set documented in their docstrings.
- **Not exposed in the IDE UI.** `enable_views`/`set_view` have **no**
  entry in `events/action_types.py` — no action-editor dialog, no
  Blockly block. Usable today only by hand-authoring the JSON action
  dict directly, or driving it from `execute_code` (the same pattern
  match3_1/2/3 already established for other under-exposed engine
  features). This is a deliberate choice per `TODO.md`'s "Still deferred
  to post-1.0" note — exposing an incomplete feature in the UI would
  repeat the rc.11 "stop lying to users" mistake.
- **Zero export support — the real gap.** `grep -rl "views_enabled\|view_offset" export/`
  returns nothing. Neither the Kivy exporter (`export/Kivy/`) nor the
  Web/HTML5 exporter (`export/HTML5/templates/engine.js`) has any concept
  of a camera. A views-based game exported to either target would render
  every instance at absolute room coordinates — the scroll simply
  wouldn't happen (or worse, depending on how each renderer clips).

This is the same *shape* of gap as the sound-queue / sprite-by-name
fallback work done for match3_2 (see that sample's README, "The
`self._sound_queue` primitive" section, and `export/Kivy/kivy_exporter.py`'s
`asset_paths.py` generation) — but bigger. Sound was an *additive* queue
bolted onto an existing draw/sound path. Views change the **rendering
transform of every draw call**, so Kivy/Web support means threading a
view offset through each exporter's whole render path, not adding one
primitive next to existing ones.

## Proposed plan

### Phase 1 — engine work (do this first; it's the actual risk/unknown)

1. Add view-offset-aware rendering to the Kivy exporter:
   - `base_object.py`'s per-instance render + `_render_draw_queue` need a
     camera transform (translate by `-view_x, -view_y`, port placement).
   - The scene's per-frame update loop needs a `update_views()` analog
     (port `runtime/game_runner.py`'s follow/clamp logic — or better,
     factor it into something shared so desktop and Kivy don't drift).
2. Add the equivalent to `engine.js`: a canvas `ctx.translate()`/clip
   before drawing room instances and tiles, driven by the same view
   state, recomputed per frame in JS (mirroring `update_views()`).
3. Register `enable_views`/`set_view` in `events/action_types.py` so
   they're usable as structured actions, not just from raw
   `execute_code` — this unblocks samples that don't want to be
   pure-script. (UI *polish* — icons, a nice action-editor layout — can
   stay deferred; just the metadata entry is needed for the action to
   round-trip through save/load and the exporters' action dispatch.)
4. Prove it on a **minimal synthetic room** (not real sample content)
   across all 3 targets before writing any sample game — a small
   `tests/test_views_export_parity.py` in the same spirit as
   `tests/test_kivy_match3_2_sound_sprite_export.py`: export a synthetic
   project with `views_enabled` + a `follow` target, drive it headlessly,
   assert the rendered position accounts for the view offset on desktop,
   Kivy (stub-kivy harness), and the Pyodide bootstrap (or engine.js
   camera math directly, since Pyodide doesn't own rendering).

**Do not skip straight to Phase 2.** If Phase 1 turns out to be too big
for one session, ship it standalone first (with its own regression
tests) rather than half-migrating the rendering path underneath a sample
that then can't be honestly documented as "verified on 3 targets" — that
would repeat the exact mistake this repo's audits keep catching (a
feature that looks done because a sample exists, but isn't actually
wired everywhere).

### Phase 2 — sample progression

Two samples, not three (smaller scope than maze/plateforme/match3 given
the engine-work overhead above):

- **`views_1`** — single view, one large room (proposed: 2400×800 room
  behind an 800×600 window — big enough that scrolling is obviously the
  point, small enough to stay a quick demo). Camera follows the player
  with GameMaker-style border scrolling (`hborder`/`vborder`, no speed
  cap). This is the minimal proof of the mechanic — one room, likely one
  or two objects (player + walls/collectibles), similar scope to
  `maze_1`.
- **`views_2`** — adds a second, smaller fixed-position view (e.g. a
  minimap pinned to a screen corner, `port_x/port_y` in the corner,
  `view_w/view_h` much larger than `port_w/port_h` to show more of the
  room zoomed out) — demonstrates multi-view, the feature's other
  headline capability beyond simple scrolling.

Follow the same authoring discipline already established this session
for match3_2/3: validate the state machine in a standalone harness
before touching sample JSON, then a real-`ActionExecutor` test, then a
real-`GameRunner` deep-smoke test driving actual frames, then export
verification on all 3 targets, *then* write the README.

### Phase 3 — docs + registration

- Extend the progression narrative already added to `samples/README.md`
  (`## Progression: how each family is built, not just how it plays`)
  with a fourth entry for `views_*` — the room-larger-than-window /
  camera step, distinct from all three existing families.
- Each sample's own README, following the established template (Overview,
  Where this fits, Sound & music, How to play, Project structure,
  Objects, Things to tweak, Export status).
- Register in `widgets/welcome_tab.py` (`SAMPLE_PROJECTS`) +
  `scripts/add_sample_name_translations.py` (run it to add + compile
  translations for all languages) + `tools/smoke_run_samples.py`.
- Regression tests per the pattern in `tests/test_match3_3_sample.py` /
  `tests/test_match3_3_special_tiles.py`.
- Update `TODO.md`'s views/camera note once Phase 1 lands — it currently
  says the feature is incomplete and UI-deferred; that description will
  need to change to reflect whatever subset actually got exported/UI-wired.

## Explicitly not decided yet — pick these up when resuming

- Exact room dimensions for `views_1`/`views_2` (2400×800 above is a
  starting guess, not a commitment).
- Whether `views_2`'s second view is a minimap (zoomed out) or a genuine
  split-screen (two players) — minimap is cheaper to build and still
  demonstrates the multi-view capability; split-screen is flashier but
  needs a second controllable character.
- Whether Phase 1's Kivy/web camera logic should be factored into a
  shared/ported implementation of `update_views()` or reimplemented
  per-target (desktop already has its own copy in `game_runner.py`, so a
  third and fourth copy is plausible drift risk — worth 10 minutes of
  thought before writing either).
