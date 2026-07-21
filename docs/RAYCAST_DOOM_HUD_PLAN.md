# Plan: DOOM-style status-bar HUD (`draw_doom_hud`) + viewport shrink + the `raycast_4` sample concept

Status: **ALL SIX UNITS DONE (2026-07-21).** The engine capability
(`viewport_height` letterbox + `draw_doom_hud`, all three targets) and the
`raycast_4` sample that showcases it are complete, tested and shipped. Commits:
`1d207db` (Unit 1 desktop) `dc90cc1` (Unit 2 HTML5) `896a228` (Unit 3 Kivy)
`e3280e1` (Unit 4a sprite multi-frame) `25e94e9` (Units 4b+5 draw_doom_hud +
parity) `62f04bf` (Unit 6 raycast_4 + the export-config gap fix). Suite 2052 →
2090 passed, 0 failed; smoke 17/17.

**Still not watched render** — the one open item, now genuinely unblockable:
open a `raycast_4` export or Test Game and look. It's the first raycast sample
whose *view shape* changes, so it's the most worth eyeballing on each target.
Unit 6 surfaced two real bugs (the export config-builders never set
`viewport_height`; one-sided collision-event firing) — both fixed with tests,
see `62f04bf`.

## Context

`docs/RAYCAST_HUD_PLAN.md` (corner-overlay HUD compositing) and
`docs/RAYCAST_MINIMAP_PLAN.md` (`draw_minimap`) are both DONE and are reused
directly here. This plan **reopens and reverses** one explicit prior decision:
`RAYCAST_HUD_PLAN.md`'s "Questions settled before Session C" section rejected
a DOOM bottom bar for `raycast_3` in favor of corner overlays, specifically
because it required threading a viewport height through all three renderers
("an engine unit the size of Sessions A-B for a cosmetic change") — but it
explicitly left the door open: *"A DOOM-style bar remains a legitimate
standalone feature later... and would pair naturally with the Session E
minimap, which also wants screen real estate."* That follow-up is this plan.

The user reviewed the two-way trade (cheap opaque overlay vs. true letterbox)
that doc made, and chose the full letterbox this time, plus a health-reactive
face/portrait icon, plus a sketch of the `raycast_4` sample this action is
being built for. `raycast_1`–`raycast_3` are **not** retrofitted; their
corner-overlay HUDs are untouched and remain correct — this is new, additive
engine capability for a new sample.

## Problem

Today, `enable_raycast_view` always renders the first-person view into the
full render-surface height on all three targets — `w, h = screen.get_size()`
(desktop), `ctx.canvas.width/height` (HTML5), `self.display_width/height`
(Kivy) — and the horizon is hardcoded at `h/2`. The earlier HUD-compositing
work made HUD draw actions composite correctly *over* that full-height frame,
in screen space, after the raycast render — but only as an overlay: nothing
shrinks the 3D view to make room for a real status bar. `raycast_3`'s
`obj_hud` is exactly that style (score top-left, lives top-right, health
bottom-left corner, toggleable minimap) and looks right for that game.

`raycast_4` wants the other aesthetic: an actual DOOM-style bottom status bar
— a reserved band across the bottom of the screen, with the 3D view
letterboxed into a shorter band above it, showing a reactive face/portrait
icon plus health/score/lives/objective readouts. That needs two additions:

1. **A `viewport_height` parameter on `enable_raycast_view`**, threaded
   through the vertical-space math in all three hand-written renderers, so
   the 3D view actually occupies a shorter band instead of the whole window.
2. **A new macro draw action, `draw_doom_hud`**, that composes the bottom
   bar's content (face icon + health bar/number + score + lives + an
   objective/key counter) from the same generic draw-queue primitives
   `draw_minimap` proved out (`rectangle`, `line`, `text`, plus `sprite` for
   the face icon) — so, per `draw_minimap`'s precedent, no new draw-queue
   dispatch type needs to be added to any renderer's switch/dispatch table.

## A load-bearing correction found during research

Before assuming the existing `sprite` primitive "just works" for a
multi-frame, health-reactive face icon, checked directly against code:

- **Desktop is fine.** `game_runner.py`'s `_draw_sprite` (`:1191-1219`) already
  slices a specific frame via the `subimage` field.
- **HTML5 does NOT.** `engine.js`'s `case 'sprite':` (`:469-478`) draws the
  **whole spritesheet image**; its own comment says *"subimage ignored: HTML5
  sprites are single-frame for now."* Regular instance rendering (`:2728-2733`)
  proves the frame-cropping math already exists elsewhere, and per-name sprite
  metadata is available with no instance via `game.makeSpriteInfo(spriteName)`
  (`:3513-3529`).
- **Kivy does NOT either.** `kivy_exporter.py`'s `elif ctype == 'sprite':`
  (`~3801-3816`) draws the entire texture with no frame slicing — contrast
  `_redraw_frame` (`:3197-3210`), which already knows how to crop one frame via
  `get_region`.

**Consequence:** "no new draw-queue command TYPE is needed" still holds — this
is a fix to the **existing** `sprite` type's HTML5/Kivy handling, not a new
type — but it's real, necessary, generically-useful engine work that must land
before the face icon can frame-swap on two of three targets. Scoped as its own
small unit (4a), independent of `draw_doom_hud` itself, with its own test.

## Design

### 1. `viewport_height` on `enable_raycast_view`

**Backward compatibility:** `viewport_height` defaults to `0`, meaning "no
change — use the full render-surface height," exactly like `wall_texture`/
`sky_texture` default to `''` meaning "no texture." Every existing
`enable_raycast_view` call in `raycast_1`/`raycast_2`/`raycast_3` renders
pixel-identical to today. When positive, the 3D view's vertical math uses
`view_h = min(h, viewport_height)` instead of the true height `h`, everywhere
**except** width-only math (`w` is never touched — strictly a vertical
letterbox, not a resize).

**The reserved band `[view_h, h)`:** the raycast renderer itself fills it with
a flat, hardcoded, opaque black backdrop after finishing the 3D pass, on all
three targets, before the per-instance draw-event pass runs — mirroring how
ceiling/floor fills always happen regardless of whether a texture is
configured. `draw_doom_hud` then paints over that backdrop in the normal
draw-event pass. Not author-configurable — an internal engine default.

#### Per-target approach

- **Desktop (`runtime/game_runner.py`).** In `_render_raycast_view`
  (`:2021-2288`): after `w, h = screen.get_size()` (`:2030`), compute
  `view_h = int(cfg.get('viewport_height', 0)) or h; view_h = min(view_h, h)`
  and replace every subsequent vertical use of `h` with `view_h` — `half_h`
  (`:2031`), ceiling/floor `fill` rects (`:2035-2036`), sky panorama height
  (`:2081`, `:2086-2093`), the wall-strip loop's `full_h`/`y_top`
  (`:2161-2167`) and texel math (`:2187`), the billboard loop's `full_h`/
  `y_top_f` (`:2246-2259`) and texel math (`:2265-2266`). `w` untouched. After
  the passes, if `view_h < h`: `screen.fill((0,0,0), (0, view_h, w, h - view_h))`.
  `_cast_floor_plane` (`:2290-2352`) independently re-derives `w, h =
  screen.get_size()` (`:2305`) — needs a new `view_h` parameter (call sites
  `:2108`/`:2112` pass it through); `half_h`/`region_h`/`pos_z`/`sh`
  (`:2306-2321`) and the final blit position (`:2347-2352`) all use it.
- **HTML5 (`export/HTML5/templates/engine.js`).** Near-line-for-line port of
  the desktop change. `renderRaycastView(ctx)` (`:2980-3143`): `const w =
  ctx.canvas.width, h = ctx.canvas.height` (`:2985`) gains `viewH =
  cfg.viewport_height || h` (clamped to `h`), used in place of `h` at `halfH`
  (`:2986`), ceiling/floor `fillRect`s (`:2988-2989`), sky (`:3013`,`:3015`),
  wall strip `fullH`/`yTop` (`:3059-3064`) + texture-row math (`:3077-3079`),
  billboard `fullH`/`yTopF` (`:3115`,`:3123`,`:3125`) + texture math
  (`:3129-3132`). `w` untouched. `castFloorPlane` (`:3171-3222`) also
  independently re-derives `w, h` (`:3172-3174`) — needs a `viewH` parameter
  (call sites `:3029`/`:3034`). After the passes, if `viewH < h`: fill
  `(0, viewH, w, h - viewH)` black. Canvas width/height (room dimensions,
  `:3742-3743`/`:3893-3894`) is unrelated and untouched.
- **Kivy (`export/Kivy/kivy_exporter.py`) — the hard one, its own unit.** The
  whole scene class (including every raycast render method) lives inside a
  `.format()`-templated source string (opens `~:1523`, closes `~:2700`). The
  `_render_raycast` body (`:1990-2233`) currently has no dict/set literals, so
  it's safe today, but any new literal `{`/`}` added while threading `view_h`
  through must be doubled or it breaks the template substitution.
  - Kivy is **y-up** (inverted from desktop/HTML5): ceiling is the **top**
    half, floor the **bottom** half; `y_bot` (not `y_top`) is used throughout
    for exactly this reason. **The reserved DOOM bar band is therefore
    `[0, h - view_h)` in Kivy's y-up coordinates (the bottom of the window)**
    — get this inversion right; it's the single easiest thing to get backwards.
  - `_render_raycast` (`:1990-2233`): `w = float(self.display_width); h =
    float(self.display_height); half_h = h/2.0` (`:2015-2017`) — replace with
    a `view_h` used for the ceiling/floor `Rectangle` fills (`:2025-2028`),
    sky (`:2059-2068`), the call into `_render_floor_plane` (`:2079-2086`),
    the wall strip's `full_h`/`y_bot` (`:2114-2120`) + `tex_coords`
    (`:2139-2140`), the billboard's `full_h_b`/`y_bot_b` (`:2191-2201`) +
    `tex_coords` (`:2207-2208`). `w`/`self.display_width` untouched.
  - `_render_floor_plane` (`:1967-1988`) receives `w, h` already but only uses
    `region_h = h - h/2.0` (`:1980`) — needs `view_h` threaded from its caller.
  - `_floor_buffer` (`:1918-1965`) does **not** take `w`/`h` as parameters —
    independently reads `self.display_width`/`self.display_height`
    (`:1926-1927`), `half_h`/`region_h`/`pos_z` (`:1928-1938`). Needs its
    **own** new `view_h` parameter (both call sites inside
    `_render_floor_plane`, `:1976-1977`, pass it through).
  - Reserved-band fill: if `view_h < h`, add a black `Rectangle` at
    `pos=(0, 0), size=(w, h - view_h)` (y-up: bottom of window).
  - **The HUD group already exists and needs no new work.**
    `_raycast_hud_group` (declared `:1569-1570`, built/populated
    `:2542-2572`) is a scene-level `InstructionGroup` on `self.canvas.after`,
    added **after** `_raycast_group` specifically so HUD draw-queue commands
    paint on top of the opaque raycast overlay. `draw_doom_hud`'s emitted
    commands flow through this identical path with **zero changes** — no
    third group to invent.

### 2. `draw_doom_hud` — a macro action, not a new draw-queue type

Follows `build_minimap_commands`'s proven shape (`runtime/action_executor.py`
`:21-81`): a pure, module-level function — `build_doom_hud_commands(...)` —
returning a list of ordinary `rectangle`/`line`/`text`/`sprite` command dicts;
the executor action resolves game-runner state (health/score/lives) and calls
it, extending `instance._draw_queue`. No target needs a new dispatch-table
entry — `_DRAW_HANDLERS` (desktop), the render-side switch (`engine.js`),
`_dq_render_cmd` (Kivy) already handle every type this emits.

**Why not delegate to the existing `health_bar`/`lives` types?** Deliberately
not reused for health — those are their own opinionated look that would
constrain the bar's aesthetic. Build the health readout from raw `rectangle`
pairs (a back panel + proportional fill) for full visual control. **The lives
readout is the one exception — reuse the existing `lives` type verbatim**
(`count`, `x`, `y`, `sprite`, `scale`): already exactly what's wanted and
already parity-tested on all three targets.

**No loop over an unbounded collection — easier than `draw_minimap` was for
Kivy.** `draw_minimap` needed Kivy's "two-halves" call-out-to-a-generated-
method pattern because a maze's wall count is unbounded. `draw_doom_hud` emits
a **fixed, small** set of commands (~8-10: two health rectangles, a couple of
divider lines, a health number, a face sprite, a score text, one `lives`
command, an objective text) — bounded regardless of room size. Confirmed
against `code_generator.py`'s existing `draw_health_bar`/`draw_score`/
`draw_lives` codegen (`:1032-1163`): these already emit runtime-value-driven
single `dict(...)` append statements inline. `draw_doom_hud` follows the
identical pattern — plain Python `code_generator.py` (not a template), one
`self._draw_queue.append(dict(type=..., ...))` per emitted command. Use
`dict(...)` call syntax, not a `{}` literal, in generated source text — same
trick the existing actions already use to sidestep brace-doubling.

#### Parameters (`events/action_types.py`, category `"3D View"` next to
`enable_raycast_view`/`set_facing_angle`/`draw_minimap`)

| Parameter | Type | Default | Notes |
|---|---|---|---|
| `x` | number | `0` | Bar's screen-space left edge |
| `y` | number | `0` (`<0` = auto) | Negative auto-aligns to `h - height`, under the shrunk viewport |
| `width` | number | `0` (`0` = full window width) | |
| `height` | number | `42` | Author's responsibility to keep roughly matched to `viewport_height`'s reserved band — document loudly, same as `cell_size`'s existing warning |
| `back_color` | color | `#101010` | Bar background panel |
| `divider_color` | color | `#505050` | Border/divider `line` commands |
| `text_color` | color | `#ffffff` | Single color for all bar text (v1) |
| `health_label` | string | `"Health"` | |
| `health_bar_width` / `health_bar_height` | number | `90` / `14` | |
| `bar_color` | color | `#20c020` | Flat, not tier-graded in v1 |
| `face_sprite` | sprite | `""` | Horizontal strip, `face_frames` frames, best-health-first |
| `face_frames` | number | `4` | Health bucketed evenly across frames (formula below) |
| `score_label` | string | `"Score: "` | Mirrors `draw_score`'s `caption` |
| `lives_sprite` | sprite | `""` | Passed to the reused `lives` command |
| `lives_scale` | number | `1.0` | Passed to `lives.scale` |
| `objective_value` | string | `"0"` | Expression, like `draw_text`'s `text` param — no engine-level "objective" global, author binds their own variable |
| `objective_label` | string | `"Keys: "` | |

**Face-frame mapping:**
```
frac  = clamp(health / 100.0, 0.0, 1.0)
frame = min(face_frames - 1, int((1.0 - frac) * face_frames))
```
Frame 0 = healthiest, last frame = worst/dying. One formula, portable to all
three codegen targets, instead of an authored threshold table.

**Layout (left to right, DOOM's face-centered arrangement):** health readout
(number + two-rectangle bar) left third; face icon centered middle third;
score + `lives` stacked in the right third's upper/lower half; objective
counter in a narrow strip at the far right edge.

**Deferred, not forgotten:** tier-graded health-bar color (green/yellow/red) —
the face icon already carries the tier-reactive signal; a two-color
`low_health_color` swap is the cheap version if wanted later.

### Unit 4a — fix the `sprite` draw-queue command's multi-frame support (HTML5 + Kivy)

Standalone bug fix, its own regression test, precedes 4b (face icon depends
on it).

- **HTML5** (`engine.js` `case 'sprite':`, `:469-478`): resolve
  `game.makeSpriteInfo(cmd.sprite_name)` and, when `frames > 1`, use the
  9-arg `ctx.drawImage(img, srcX, 0, w, h, cmd.x, cmd.y, w, h)` form with
  `srcX = (cmd.subimage % frames) * width`, mirroring `:2728-2733`.
  Single-frame sprites keep the existing whole-image blit.
- **Kivy** (`kivy_exporter.py` `elif ctype == 'sprite':`, `~3801-3816`): look
  up frame metadata via `SPRITE_META` (already populated `:2963-2970`/`:2785`,
  already read the same way at `:3173-3175`), crop with
  `tex.get_region(frame * frame_w, 0, frame_w, frame_h)` like `_redraw_frame`
  (`:3197-3210`), selecting `frame` from a new `cmd.get('subimage', 0)`.
  Desktop needs **no change** — `_draw_sprite` already does this correctly.
- Test: a >1-frame fixture sprite; assert HTML5's `drawImage` args / Kivy's
  `get_region` args select the requested frame for `subimage` 0 and 1.

## Design decisions (recap)

1. `viewport_height` default `0` = full height, unconditionally backward
   compatible.
2. Reserved band filled black by the renderer itself, unconditionally, before
   the draw-event pass — never author-configurable.
3. `draw_doom_hud`'s `y` defaults to auto-align under the shrunk viewport.
4. Health bar from raw `rectangle` pairs; lives reuses the existing `lives`
   command verbatim.
5. Face-tier mapping is an even-bucket formula over `face_frames`, not an
   authored threshold list.
6. Objective/key counter is author-supplied via an expression string.
7. No color-graded health bar in v1.
8. Category = `"3D View"`, not `"Score"` — raycast-specific companion action.

## Testing per target

- **Desktop:** render at a shrunk `viewport_height`; assert the horizon
  moved, wall-strip pixels never paint below `view_h`, the reserved band is
  solid black before any draw event runs, `_cast_floor_plane` respects the
  new parameter. Must go through the real `run()` startup (the standing
  `_cached_object_data`/sprite-size lesson — a hand-built room passes for the
  wrong reason otherwise). Separately: render `draw_doom_hud`'s output,
  assert each emitted command + the face-frame formula at several health
  values (100, 50, 1, 0).
- **HTML5:** structural assertions (no JS engine in CI) that `viewH` replaces
  `h` at each vertical-math site, the reserved-band fill exists, and
  `case 'draw_doom_hud':` emits the same command shapes as
  `build_doom_hud_commands`. Plus a dev browser run.
- **Kivy:** the existing stub-kivy harness (`tests/test_kivy_raycast.py`
  pattern). Assert the y-up inversion is right (reserved band at the
  **bottom**), `_floor_buffer` receives its own `view_h` (not window height),
  and the HUD group receives `draw_doom_hud`'s commands with no new
  group/case needed.
- **Parity:** extend `tests/test_raycast_export_parity.py` with a
  `viewport_height` geometry case (desktop vs. Kivy exact; HTML5 structural)
  and a `draw_doom_hud` three-way command comparison, following the existing
  `draw_minimap` precedent, sharing the face-frame formula as a module-level
  constant the way `MINIMAP_HEADING_LEN`/`MINIMAP_MARKER_HALF` are.
- **Unit 4a:** a focused regression test with a >1-frame fixture sprite.

## Session-size units (one commit each)

- [x] **Unit 1 — `viewport_height` schema + plumbing + desktop renderer.**
  `1d207db`. Backward-compat asserted (no-param / explicit-0 / == height all
  diff to zero).
- [x] **Unit 2 — HTML5 renderer.** `dc90cc1`. Near line-for-line port; reserved
  band filled black; `castFloorPlane` takes `viewH`.
- [x] **Unit 3 — Kivy renderer (the hard one).** `896a228`. The y-UP inversion
  was the crux: reserved band at the BOTTOM (`[0, view_bottom)`), horizon at
  `h - view_h/2`, walls clamp to `view_bottom` not 0. `_render_floor_plane` and
  `_floor_buffer` each take their own `view_h`. No literal braces added; the
  generated scene compiles. Stub-kivy test pins the band at `(0,0)`.
- [x] **Unit 4a — fix HTML5 + Kivy `sprite` multi-frame support.** `e3280e1`.
  Both drew the whole spritesheet; now crop by `subimage`. A test compiles the
  generated Kivy `base_object.py` to catch the brace-doubling.
- [x] **Unit 4b — `draw_doom_hud` action.** `25e94e9`. `build_doom_hud_commands`
  + executor action + registration + `engine.js` case + Kivy codegen (a bounded
  inline append block, not a call-out). No new dispatch type anywhere.
- [x] **Unit 5 — parity extension.** `25e94e9` (folded with 4b). Face-frame
  formula pinned identical across targets; emitted-type set asserted to stay
  within the existing draw-queue types; Kivy codegen asserted to compile.
- [x] **Unit 6 — `raycast_4` sample.** `62f04bf`. Built and shipped (not just sketched): letterboxed view + draw_doom_hud bar, health-reactive face, key-gated exit, Welcome-tab entry + FR translation, EN + FR guides, smoke 17/17. Two bugs found + fixed (export config-builders never set viewport_height; one-sided collision firing). ORIGINAL SKETCH:** Concept below; actual maze/
  asset/session-breakdown build is a **separate, later** planning + build
  pass, gated behind Units 1-5 shipping — same as how the minimap got its own
  gated Session E plan doc.

## The `raycast_4` sample sketch

**Concept — "the bar you can't look away from."** Where `raycast_3` proved a
corner-overlay HUD and health-as-a-resource, `raycast_4` is the first sample
built **around** a permanent, always-visible bottom status bar — the DOOM
aesthetic rather than the corner-HUD aesthetic. The 3D view is visibly
shorter (letterboxed) — part of the pitch, not a bug.

Mechanics, chosen so each bar element has a reason to exist:

1. **A face that reacts before the player checks the number** — health damage
   drives the face through its frames, so a player notices the portrait wince
   before reading the numeric health, like DOOM's own bar.
2. **A key-gated multi-stage exit**, mirroring `raycast_3`'s gem-gated goal
   but swapped to keys specifically so the new `objective_value` counter has
   an obvious reason to sit in the bar (DOOM's key-card readout).
3. **Score + lives**, carried over unchanged from `raycast_2`/`raycast_3` —
   now in the bar's right third instead of opposite corners.
4. **A deliberately shorter viewport** as a genuine gameplay variable — worth
   calling out in the sample's guide text, like `raycast_3`'s guide called
   out its health-bar addition.

**Assets needed (confirmed absent today):** a face/portrait spritesheet (new;
3-5 frames matching `face_frames`, e.g. calm/hurt/critical/dying), a key
pickup sprite (new, distinct from `raycast_3`'s gem), reuse of
`raycast_2`/`raycast_3`'s wall/sky/floor textures, `obj_person`,
`obj_wall_h`/`_v`, and monster sprites.

**In scope for Units 1-5 vs. deferred:** Units 1-5 ship `viewport_height` and
`draw_doom_hud` as generically usable, verified against synthetic fixtures
and parity tests — **not** against an actual `raycast_4` room. Building the
maze, key-gated exit logic, face sprite asset, and session breakdown is
deferred to a follow-up plan/build pass once Units 1-5 ship.

## Out of scope

- No retrofit of `raycast_1`/`raycast_2`/`raycast_3` — their corner overlays
  stay as-is.
- No tier-graded health-bar color gradient in v1.
- No authored per-threshold face-frame table — even-bucket formula only.
- No new draw-queue dispatch **type** on any target (Unit 4a is a capability
  fix to the existing `sprite` type, not a new type).
- No changes to the DDA / billboard / floor-cast math itself —
  `viewport_height` only changes how much vertical space that math projects
  into, not the projection formulas.
- Full `raycast_4` maze/asset/session build — sketched here, built later.

## Critical files

- `runtime/game_runner.py` — `_render_raycast_view` (`:2021-2288`),
  `_cast_floor_plane` (`:2290-2352`), `_DRAW_HANDLERS` (`:876-888`)
- `runtime/action_executor.py` — `build_minimap_commands` (`:21-81`, model
  for `build_doom_hud_commands`), `execute_enable_raycast_view_action`
  (`:4532-4611`)
- `export/HTML5/templates/engine.js` — `renderRaycastView`/`castFloorPlane`
  (`:2980-3222`), `case 'draw_minimap':` (`:2345-2412`, model), `case
  'sprite':` (`:469-478`), `makeSpriteInfo` (`:3513-3529`)
- `export/Kivy/kivy_exporter.py` — `_render_raycast` (`:1990-2233`),
  `_render_floor_plane`/`_floor_buffer` (`:1918-1988`), `_raycast_hud_group`
  wiring (`:2542-2572`), `_dq_render_cmd` sprite case (`~3801-3816`),
  `_redraw_frame` (`:3197-3210`)
- `export/Kivy/code_generator.py` — `enable_raycast_view` codegen
  (`:744-779`), `draw_health_bar`/`draw_score`/`draw_lives` codegen
  (`:1032-1163`, model for `draw_doom_hud` codegen)
- `events/action_types.py` — `enable_raycast_view` registration
  (`~:528-582`), minimap registration for the "3D View" category convention
- `tests/test_raycast_export_parity.py` — extend for both `viewport_height`
  and `draw_doom_hud`

## Verification

Once implemented: `QT_QPA_PLATFORM=offscreen python3 -m pytest tests/ -q`
must stay 0 failed at every unit. Each unit gets its own regression test per
the per-target testing section above. Before Unit 6 (sample build) starts,
manually eyeball a shrunk-viewport render on desktop (no automated pixel-diff
substitute for "does it look like DOOM") — same caveat every prior raycast
plan has carried: nobody has watched this render in a browser or on Android
until someone does.
