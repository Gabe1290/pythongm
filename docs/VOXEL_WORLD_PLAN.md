# Voxel World extension — plan

Status: **Phases 0, 1, 2a, 2b and 2c all done (2026-08-13); Phase 3 under
way — picking, place/break and unbreakable blocks landed, hotbar and world
generator still open.**

This doc is the worked plan for a Minecraft-*inspired* block-building
extension, built the same way
`extensions/raycast_2_5d/` was (see `docs/RAYCAST_EXTENSION_PLAN.md`) — except
this one starts life as a folder extension from commit 1, instead of living in
core first and being extracted later. That extraction (Stage B/C of the
raycast plan) was real, avoidable work; skip it this time.

## Naming and legal framing

**Do not use "Minecraft" anywhere** — not the extension name, not sample
names, not UI strings, not code comments, not the wiki page. Mojang/Microsoft
own that trademark. Working name for this doc: **Block World**. Pick the
final name before Phase 0 lands (student-facing, so keep it simple —
`Block World`, `Voxel Builder`, `Cube Craft`... anything that isn't a
Minecraft reference).

Game *mechanics* (place/break cubes, a hotbar, a blocky low-res aesthetic)
are not copyrightable — this is the same "inspired by, not copied from"
territory Minetest/Luanti, Terasology, and dozens of student projects already
occupy safely. The two things that actually carry legal risk are the name/logo
(avoided above) and specific copyrighted asset files (Phase 0 below).

## Phase 0 — asset sourcing and licensing audit (no code)

Pull block textures from Luanti/Minetest's ecosystem, but **only** ones
explicitly marked CC0 (public-domain-equivalent — no attribution or
share-alike obligation). Do not use the stock `minetest_game`/`mtg` textures
directly — those are a mix of CC BY-SA 3.0 and CC0 per-file, contributor by
contributor, and defaulting to "assume CC0" would be wrong.

Steps:
1. Search ContentDB (Luanti's package registry) filtered to texture packs
   whose listing states CC0 (or a pack with a `LICENSE.txt` that names CC0
   for every texture file, not just the pack as a whole — some packs mix
   licenses per-author within one download).
2. For each candidate pack, open its actual license file and confirm
   per-texture, not just skim the pack description — descriptions have been
   wrong before elsewhere in this repo's own asset-audit history.
3. Record what was used in a checked-in `extensions/block_world/ASSETS.md`:
   source URL, pack name, author, license, date checked, and which specific
   files were imported. Even though CC0 needs no attribution legally, keeping
   this table means a future audit doesn't have to re-derive provenance from
   scratch — same discipline this repo already applies to translation/audit
   provenance elsewhere.
4. **Fallback if no CC0 pack fits the visual style wanted:** draw original
   pixel-art block faces (16x16 or 32x32, matching this repo's existing
   sample-art sizing) the same way `raycast_4` added its own face strip and
   key sprite. Original art has zero tracking burden and is the safer default
   if Phase 0's audit turns up anything ambiguous — don't force a CC0 pack
   that's a stylistic mismatch just to avoid drawing a dozen block faces.

This phase blocks everything else — no block texture ships in the repo
without a line in `ASSETS.md`.

**Done (2026-08-12):** audited five CC0-licensed candidate packs from
ContentDB. Picked **Hand Painted Pack Expanded** (shaft / Miloslav Číž
"drummyfish") — CC0-1.0 confirmed three independent ways (its
`texture_pack.conf`, a bundled full CC0-1.0 legal-code file, and its own
`sources.txt` per-file provenance list, grepped for any non-CC0 source and
finding none). A curated 32-file starter subset (terrain, wood, leaves,
glass, water, a few ore/decorative blocks, six wool colors) is checked in at
`extensions/block_world/textures/source_hand_painted_expanded/`, alongside
the license text and the upstream provenance file. Full audit table
(including the four other packs evaluated and why they weren't picked) is in
`extensions/block_world/ASSETS.md` — read that before pulling in any
additional texture from the same pack or sourcing a different one.

## Phase 1 — extension skeleton + world data model

`extensions/block_world/` from the start: `extension.json`
(`provides_actions`), `__init__.py` (the render-hook contract), `state.py`
(per-room state, mirroring `raycast_2_5d/state.py`'s `room.extension_state[...]`
pattern — nothing voxel-specific touches core `GameRoom`).

World storage: a **sparse dict keyed by `(x, y, z)` → block type id**, not a
dense 3D array — matches how this repo already treats sparse per-cell data
(room tile layers, raycast wall-edge sets) and keeps small/empty worlds cheap.
Persisted inside the room's own state the same way tile layers persist inside
room JSON today; large worlds may need their own side-file later (Phase 6
note) the way `.trash`/rollback snapshots got their own storage rather than
bloating `project.json`.

Decide up front: **bounded, author-sized worlds** (a maze-generator-built
region, like `raycast_2`/`raycast_3`'s hand-built mazes), not infinite
procedural terrain. Infinite chunk streaming is a much bigger engineering
problem (chunk loading/unloading, seed-based generation, LOD) with limited
teaching payoff for a student sample — explicitly out of scope unless a later
plan revisits it.

**Done (2026-08-12):** `extensions/block_world/extension.json` +
`__init__.py` load cleanly (no `PLUGIN_ACTIONS`/`PLUGIN_ROOM_RENDERERS`
declared yet — both are optional to the loader; declaring empty placeholders
would've been dead code). `state.py` has the sparse
`room.extension_state["block_world"]` store (`block_world_state`/
`peek_blocks`/`get_block`/`set_block`/`remove_block`/`iter_blocks`/`bounds`),
plus a `BLOCK_TYPES` registry mapping 27 block type ids to the 32 imported
textures (some block types, like `grass` and `wood_log`, use different
textures per face) and a `solid`/`transparent` flag per type for Phase 4/2 to
consume later. `to_block_list`/`load_block_list` round-trip the sparse dict
to the same flat-list-of-dicts shape room JSON already uses for tile layers
— chosen over inventing a new shape after checking how tiles actually persist
(`"tiles"` is a list of `{background_name, x, y, tile_x, tile_y, width,
height, depth, layer}` dicts, not a position-keyed map). Nothing yet reads or
writes room JSON — this stays transient `extension_state`, same as raycast's
camera config, until a Phase 3+ load path exists. One real bug caught by the
full suite gate: a second extension with no `PLUGIN_NAME` attribute made
`tests/test_plugin_loading_in_ide.py::test_is_idempotent`'s module-uniqueness
check collide (both defaulted to `"?"`) — fixed by giving `block_world` a
`PLUGIN_NAME`, the correct convention anyway (matches
`plugins/audio_actions.py`). 15 new tests in
`tests/test_block_world_state.py`, including one that resolves every
`BLOCK_TYPES` entry's textures and asserts the files exist on disk — ties
Phase 0's imported assets to Phase 1's registry so a future rename/removal
fails loudly. Suite 2539 → 2540 passed, 0 failed.

## Phase 2 — renderer (staged, cheapest-first)

Reuses the *shape* of `raycast_2_5d/renderer.py` (DDA ray marching, per-column
screen strips, fisheye correction) but the geometry is genuinely different —
2D wall-casting finds one wall per ray; a voxel renderer needs to find which
**cube face** a ray hits in 3D. Build in increasing difficulty, each a
separate commit + its own regression harness, matching the raycast arc's
per-unit discipline:

- **2a — flat single-layer MVP.** One block height, camera fixed at that
  height, no vertical look. This is close to a direct textured re-skin of the
  existing 2D raycaster (blocks instead of wall segments, textured faces
  instead of flat wall shading) — cheapest path to something on screen, and
  the best point to validate the CC0 textures actually read well at a
  distance.

  **Done (2026-08-12):** `renderer.py` (`cast_ray` + `render_block_world_view`)
  plus one new action, `enable_block_world_view` (`actions.py`/`handlers.py`),
  mirroring `enable_raycast_view`'s camera/config plumbing — needed as
  infrastructure for the render hook itself, not gameplay, so it landed
  alongside the renderer rather than waiting for Phase 3. `cast_ray` turned
  out simpler than raycast's own: raycast derives thin wall EDGES from sprite
  instances and stops at a specific edge; a voxel block fills its whole grid
  cell, so this is the more standard cell-occupancy DDA (Amanatides & Woo) —
  step cell by cell, stop at the first occupied one via `state.get_block`.
  Wall strips project as genuine cubes (no height multiplier, unlike
  raycast's deliberately-taller corridors). Textures load straight from the
  Phase 0 PNG files via a small lazy cache (`pygame.image.load(...)
  .convert_alpha()`, the same convention `GameSprite` already uses) since
  block textures aren't project sprite assets the way raycast's wall
  textures are. `state.py` gained a `camera` sub-key and `peek_camera`,
  mirroring raycast's non-creating peek. One test-authoring bug caught and
  fixed along the way, worth remembering for Phase 2b/2c: a camera test
  helper placed the instance's top-left at (16, 16), but the renderer centers
  the ray origin at `top_left + size/2` — the actual camera center landed a
  full cell away from where the test assumed, so a straight-ahead ray missed
  a block placed for exactly that geometry. Fixed the helper, not the
  renderer. 19 new tests in `tests/test_block_world_renderer.py` (action
  config, deterministic `cast_ray` geometry, `wall_shade`, real-Surface
  pixel-sampled rendering including one that exercises the actual imported
  CC0 texture end to end, extension wiring). Suite 2540 → 2559 passed, 0
  failed.

  **Eyeball tool (added after the fact):** `tools/preview_block_world.py`
  builds a showcase world (every registry block type, in lanes, at varied
  distances) and drives the real `render_block_world_view` — either as a
  walkaround window or, with `--shots DIR`, nine fixed frames as PNGs
  headless. Pixel-sampling tests prove a strip got drawn; they say nothing
  about whether the textures READ well, which is 2a's whole stated purpose.
  Two things it surfaced immediately, both **Phase 2b/2c input rather than
  bugs to fix now**:
  1. `BLOCK_TYPES`' `transparent` flag is not honoured — glass, water and ice
     draw fully opaque, and a ray stops at the first occupied cell regardless.
  2. Textures with real alpha (leaves, glass) blit their alpha, so the gaps
     show the flat floor/ceiling fill rather than whatever block is behind —
     there is only one hit per column, so nothing behind was ever drawn. Any
     see-through block type needs the ray to continue past it and the column
     to composite back-to-front, which is a renderer change, not a texture one.

  The scene layout has viewing lanes: a viewpoint must stand in open air with
  a clear line to its subject, and at FOV 66 a row N cells wide needs roughly
  N/1.3 cells of standoff to fit in frame. Four of the first-draft viewpoints
  were boxed inside the corridor staring at a wall, which is obvious in a
  picture and invisible to any assertion worth writing.
- **2b — multi-layer heightmap.** Blocks stack (a handful of Z layers, not
  arbitrary depth), player can walk up single-block steps and see over
  short walls. Still no free vertical camera look — pitch stays level, like
  raycast_1-4. This is enough for "build a little house," "dig a pit,"
  "stack blocks to reach a ledge" — most of what students will actually want.

  **Done (2026-08-13).** The whole vertical projection is one line, and
  `render_block_world_view`'s docstring is where it lives:
  `y = horizon + (eye_z - zval) * (screen_h * cell_size / distance)`. Phase
  2a turns out to be exactly the `eye_z = 0.5`, one-layer case of it, which
  is what made the compatibility proof possible.
  - **The DDA is now one function.** `march_ray` yields every cell entered,
    with its ENTRY *and* EXIT distance — the exit is what a top face needs,
    since a horizontal surface runs from the near vertical face back to the
    far one. `cast_ray` is a thin first-hit wrapper over it and stays as the
    single-layer query for Phase 3 picking. Do not grow a third copy.
  - **Painter's algorithm, far→near, with a gapless-opaque early-out.** A
    column can be seen *through* two ways — a hole in the stack, or a
    transparent block — so the early-out fires only for a contiguous stack
    of opaque blocks that covers the screen. Getting that wrong erases
    whatever is visible beyond. The hole case was handled from the start;
    **the transparent case was missed and shipped, and a playtest caught
    it**: a glass block looked right side-on and at range, then showed raw
    sky and floor through itself when walked up to face-on, because getting
    close made it big enough to satisfy the covers-the-screen test and stop
    the march. Being distance-dependent made it read as a texture glitch
    rather than an occlusion bug. `BLOCK_TYPES`' `transparent` flag — until
    then carried but unread — is what fixed it. **Generalise this before
    2c/Phase 6 re-derive the same logic: any occlusion shortcut must ask
    whether a block can be seen through, not just whether it is present.**
  - **Horizontal faces are texture-mapped** (`_draw_horizontal_face_textured`).
    They shipped flat-shaded from the texture's average colour, on the
    reasoning that a step or a pit reads correctly without the grain and
    per-pixel casting was 2c work — a playtest disagreed, and a large deck
    of flat grey does look like plastic. Inverting the projection gives the
    distance to the plane for a screen row directly, so the world point and
    hence the texel follow; sampled every `res` rows into a 1px column and
    upscaled, exactly the trick `raycast_2_5d.cast_floor_plane` uses.
    `top_cast_res` (default 4, 0 = flat fallback) is the same knob as that
    renderer's `floor_cast_res`. Shading is one hardware multiply on the
    finished column, never per texel.
  - **A derived per-column index** (`state.column_index`, invalidated by
    every mutator) replaces per-layer probing of the `"x,y,z"` string keys.
    Without it the render path spends tens of thousands of string formats a
    frame. `stack_top` is the heightmap query Phase 4's footing will reuse.
  - **Profile before optimising, and the answer will surprise you.** The
    obvious suspects on a slow frame were the ray march and the per-column
    blits. Neither: `cProfile` on the preview's terrace view found
    **60,905 calls to `block_face_textures` in a single frame**, each doing
    an `os.path.join`, making path construction the most expensive thing in
    the renderer. It is a pure function over a static registry — memoising
    it took ~20% off every frame, textured or flat.
  - **Known and not addressed: overdraw.** That same frame marched 18.6
    cells and drew 38.1 wall strips per column, for a handful of visible
    surfaces. Painting far→near means everything hidden is still rasterised.
    The sound fix is a cumulative-coverage early-out, but note the
    subtlety: the union of per-cell spans is only guaranteed contiguous for
    stacks taller than the eye (those all contain the horizon row), so a
    naive min/max accumulator is wrong for a world of low blocks. Deck-heavy
    views run ~18 fps at 800x600 with 320 columns; `columns` and
    `top_cast_res` are the knobs until someone does the work.
  - **Pre-existing seam bug found and fixed en route.** A textured strip
    scales its texture column to a ROUNDED height while the span it fills is
    CEILED, so it could fall a row short — 2a showed the flat floor colour
    along the bottom edge of walls. Fixed by repeating the strip's last row
    into the shortfall. Note the first attempt (growing the scale target to
    fit) recoloured *every* texel above the seam to patch one row — the
    proof harness caught that immediately, at 2.7M differing pixels.
  - **Compatibility proof:** a single-layer OPAQUE world renders identically
    to 2a across a 160-frame camera matrix (10 positions × 8 angles ×
    textured/flat) — every one of the 51,649 differing pixels out of 76.8M
    is a seam row 2a left unpainted, with no vertical run over 2px, checked
    per pixel rather than eyeballed. Two deliberate exceptions, each with
    its own test: the seam fill, and **alpha textures now compositing with
    the block behind them** instead of the flat sky (2a drew one hit per
    column, so glass and leaves showed sky through their gaps — the very
    thing the 2a preview review flagged; it falls out of painting far→near).
  - Landmine that nearly cost a bogus "identical" claim: 2a recovered the
    entry distance as `(side + delta) - delta` after stepping, which differs
    by an ULP from capturing `side` before it. That is enough to move a
    strip edge a pixel in the odd column. `march_ray` reproduces 2a's
    arithmetic deliberately — a comment says so, so nobody "cleans it up".
  - **Mutation-testing gotcha worth knowing, cost a false conclusion once:**
    if the anchor string you swap also appears in a docstring or comment, a
    naive first-occurrence replace mutates the prose and leaves the code
    intact — the mutant "survives" and you go hunting for a test gap that
    does not exist. Assert the anchor occurs exactly once, or anchor on the
    full statement including its indentation and `name =` prefix.
  - **Mutation-checked**, not just green: breaking each of the five 2b
    behaviours in turn (no horizontal faces, nearest-cell-only, eye height
    ignored, gapped stacks treated as opaque, seam left unpainted) each
    makes a test fail. The first seam test did NOT fail against the bug — it
    scanned for background rows *between* a wall's first and last drawn row,
    and the shortfall is at the bottom edge, so it was structurally blind.
    Rewritten to assert the exact last painted row. Same lesson as the
    minimap marker: assert WHERE an edge lands, not that something drew.
  - 29 tests in `tests/test_block_world_layers.py`; geometry tests use
    `columns: 1` so ray_offset is exactly 0 and the projection has a closed
    form to assert against. Suite 2563 → 2592, 0 failed.
  - `tools/preview_block_world.py` gained the multi-layer half of the scene
    (staircase, terrace, pit, tower) and step-up movement, so 2b is
    eyeballable: five new viewpoints, `--shots` now writes 14 frames. The
    **pit viewpoint is deliberately kept as evidence of the 2c limitation** —
    a level camera cannot look down, so a pit at your feet falls below the
    frame; from a few cells back it reads correctly as a recess.

  **Scene-design lesson from the first playtest, and it generalises to any
  world built on this engine:** the first version made every wall exactly one
  block tall, and the player could simply walk up onto all of them. That is
  not a movement bug — in a world of unit cubes a one-block wall and a
  one-block step are the *same object*, and any rule permissive enough to
  climb a staircase must also climb a kerb. So height is what separates them:
  walls are now 3-4 blocks (a step is a quarter of the perimeter), display
  rows 2, and the staircase is the only one-block rise in the world.
  `MAX_STEP_UP = 1` then does the right thing everywhere. Build a one-high
  wall and it stops being a wall.

  Second, less obvious: a staircase seen HEAD-ON correctly renders as a
  stepped wall, because each tread hides behind the riser in front of it.
  Reading the profile needs a side-on view from ~10 cells back (at
  `cell_size` 32 on a 600px screen, five stacked blocks only fit in frame at
  that range), and a scene has to be laid out deliberately to afford one.
  Worth knowing before Phase 5 designs a sample around a build the player is
  supposed to admire.
- **2c — free look.** Looking up and down, needed for tall builds and deep
  pits to read correctly from up close.

  **Done (2026-08-13) — and this plan's cost estimate for it was wrong.**
  The text below is left as written, because being wrong in a specific,
  checkable way is the useful part:

  > *Full 3D DDA with pitch (looking up/down) … This is the expensive step
  > (real 3D ray marching, not the 2D-plus-height approximation of 2b) —
  > treat it the way the raycast plan treated floor-casting on HTML5/Kivy:
  > land 2a/2b for real, defer 2c behind an explicit follow-up decision.*

  No 3D ray marching was needed in the renderer at all. Two facts, either of
  which is easy to miss:

  1. **`half_h` appeared 16 times and every one was the horizon reference in
     the projection.** Nothing horizontal depended on it. Grepping for it
     before designing anything is what turned this from a rewrite into a
     rename.
  2. **Pitch does not change AZIMUTH.** A screen column still corresponds to
     the same ray, so the horizontal DDA never has to learn about it.

  So looking up and down is a **Y-SHEAR**: `horizon_for()` slides the horizon
  and every other formula is left alone. `horizon = screen_h/2 + screen_h *
  tan(pitch)` — the vertical focal length works out to exactly `screen_h`
  pixels. Clamped at 70°, past which the stretch stops convincing and `tan`
  runs away.

  It is a shear, not a rotated camera: **vertical edges stay vertical instead
  of converging.** Doom did the same. For a world made of cubes the parallel
  edges arguably read better than true perspective would, but say so plainly
  rather than claiming a full 3D camera.

  `project_point` / `unproject_to_plane` / `screen_ray` / `draw_cell_outline`
  all take `horizon` as an optional argument defaulting to screen centre, so
  every existing call site kept working untouched and the 162 Block World
  tests passed through the change. Picking follows the pitched view for free,
  because `screen_ray` reads its slope from `sy - horizon`.

  What it buys, measured: the steepest ray goes from **0.5 cells per cell
  (~26°) at level to ~2.2 (~65°) at −60° pitch**, so digging down and
  building overhead now work. `set_look_pitch` (absolute or relative, for a
  held look control) is the action; the walkaround binds the wheel and R/F.

Each stage gets a `render.md`-style writeup of its own math the way
`RAYCAST_2_5D_PLAN.md` did, since three more codebases (HTML5/Kivy in Phase 6)
will need to reproduce it exactly later.

## Phase 3 — placing and breaking blocks

**Unit 1 done (2026-08-13): picking + `place_block` / `break_block`.**
`renderer.pick_block` marches the SAME `march_ray` at the SAME angle the
centre column is drawn from, and returns both the cell to break and the cell
to build in. Notes worth carrying:

- **`place_block` needs no "is this cell empty?" check** and deliberately
  has none. `pick_block` only advances past cells it has read as air, and an
  occupied first cell returns immediately with no placement, so a returned
  placement is air *by construction* — the invariant is stated in its
  docstring and pinned by a parametrised test. The guard shipped in the first
  draft and mutation testing exposed it as unreachable code posing as a
  safety net.
- **Phase 2b's level camera bounds what picking can mean.** The ray runs
  horizontally at eye height, so only the camera's OWN layer is reachable:
  you build outwards at your feet and climb what you built. Digging down or
  placing onto ground below you needs 2c. Flush against a wall there is
  legitimately nowhere to build, and the action is a silent no-op.
- Picking does NOT consult `transparent` — glass has to be breakable, so it
  is picked like anything else, unlike the renderer's occlusion test.
- **A gap beats a surface.** Placement prefers the first GAP the ray passes
  through — an empty cell at the camera's layer with a block resting on top
  — over the cell before the target. Found by playtesting: knock a block out
  of a wall and, with the plain "build against what you hit" rule, *you can
  never put it back*. A one-cell-thick wall has no cell "before the hit"
  that IS the hole, from either side, so the block always lands somewhere
  past it. The target still reaches past a gap, so the crosshair stays on
  what is really behind the hole and that block is still breakable; only
  where a new block lands changes. An open doorway has nothing resting on it
  and so is never bricked up by accident. The remaining hole this does not
  cover is one knocked out of the TOP of a wall, which has nothing above it
  — reachable only from a layer where 2c's free look would be the real fix.
- **Three mutants survived the first test pass**, all for the same reason:
  the test helper had its own copy of the handler's camera resolution, and
  every action test faced angle 0 on layer 0 — where a sign flip and a
  hardcoded layer are both invisible. Any test for this action pair must
  drive the handler at a non-zero facing AND a non-zero layer.

**Gap closed (2026-08-14): the actions never adopted Phase 2c's pitch.**
When 2c landed (same day, later), `pick_voxel`/`screen_ray` were built and
wired into the mouse-aim preview tool, but `handlers.py`'s `_pick` — what
actually backs `place_block`/`break_block` — was never updated off the
original level-only `pick_block`. So `set_look_pitch` changed what a game
*showed* without changing what the actions *targeted*: the bullet above
("digging down... needs 2c") stayed true for the shipped actions even after
2c shipped, which a close review of the commit range caught. Found by
tracing the code path, not by playtesting this time.

Fixed by building `_pick`'s ray the same way the mouse-aim tool does —
`screen_ray` through the fixed screen-centre crosshair, using
`horizon_for(screen_h, pitch)` so the ray's vertical slope follows the
current pitch — and marching it with `pick_voxel` instead of `pick_block`.
Screen dimensions come from `game_runner.window_width/height`, falling back
to `.screen.get_size()` then a hardcoded 640x480, the same fallback chain
`draw_doom_hud` already established for action-side code with no direct
render-surface access. At `pitch == 0` this is provably the same ray
`pick_block` used (`horizon_for(h, 0) == h/2` exactly, and the crosshair
sits at screen centre too, so `z_per_px` comes out to exactly `0.0`) — no
behaviour change for a level view, confirmed by the full existing picking
suite passing unmodified.

**The gap-preference rule had to move with it.** `pick_voxel` had no
equivalent of `pick_block`'s "prefer refilling a hole" heuristic — its own
docstring's claim that it was already "the general form of pick_block" was
only true for the *target*, not the *placement*, at `z_per_px == 0`: on a
total miss it fell back to the *last* empty voxel visited (near the reach
limit) rather than the *first* one (build directly ahead), and it had
nothing tracking a gap at all. A naive swap would have silently re-shipped
the exact "can't refill a hole" bug `ecb319c` fixed. Ported both the `gap`
tracking and the `first`-on-total-miss fallback into `pick_voxel`, keyed on
a single VOXEL now instead of a fixed layer (an empty voxel with a solid one
directly above it, same x, y, z+1) — verified, not assumed, against the real
functions before trusting the geometry: several new tests' exact parameters
(entry/exit distances, `z_per_px` values) were found by running `pick_voxel`
directly and reading its output before writing the assertion, the same way
`TestPickVoxel`'s existing tests derive their numbers.
`pick_block` itself is untouched — still the simpler, still-tested, still
documented single-layer reference case `pick_voxel`'s docstring compares
itself to.
6 new tests (`tests/test_block_world_picking.py`): the total-miss fallback,
the gap rule at `z_per_px == 0` and again on a genuinely tilted ray, and
three tests through the real `place_block`/`break_block` actions proving
pitch now changes what they target, including a tilt-up-then-back-to-level
round trip. Suite 2725 → 2731 passed, 0 failed. README.md's Phase 3 section
updated to match (it had been describing the pre-fix limitation as current).

**Placement outline (2026-08-13).** `draw_cell_outline` marks the footprint
of the cell a block would land in, so you see where you are building before
committing. It rides on `project_point`, the inverse of what the render loop
does per column — built from the same camera-plane depth and the same one-line
vertical mapping, so an overlay lands exactly on the geometry underneath it.
Anything later that needs to draw *into* the 3D view (a selection box, a
marker, a highlighted face) should use `project_point` rather than
re-deriving screen positions. It skips silently when a corner falls at or
behind the camera plane: a partly-behind quad projects to nonsense, and half
an outline is worse than none.

**Mouse aiming (2026-08-13), and what it says about the centre-ray rule.**
Playtesting again: with the crosshair fixed at screen centre, the placement
outline appeared stuck — break through a wall and the next wall behind, and
it still marked the first hole, because the gap rule pins placement to the
first gap along the ray. The ask was "an outline that follows the mouse, so
we can point at where the block should go", and that is the better primitive:
**pointing beats inferring.** The centre-ray rule can only ever express
"against the surface I am facing"; it cannot express "there".

`unproject_to_plane` is the exact inverse of `project_point` onto a
horizontal plane, so a screen position becomes the floor square it appears to
be over. The walkaround now asks two different questions: **breaking** casts
a ray through the mouse's COLUMN (still at eye height — with no pitch, mouse
y cannot tilt a ray), and **building** unprojects the mouse onto the floor of
the camera's layer. A build cell must also be empty, within reach, and
actually visible: the floor of a square behind a wall still projects to a
screen position, so without an occlusion check you can build through solid
rock by pointing at where the floor would be.

**3D picking (2026-08-13), and the thing that made it cheap.** Asked how to
stack blocks one atop another; the honest answer was "climb what you build,
and you cannot make a vertical column at all", because building only ever
reached the floor plane of your own layer. The fix turned on one realisation:
**a level camera constrains the forward AXIS to horizontal, not every ray.**
Each pixel already corresponds to a real ray sloping up or down — that is
precisely what `unproject_to_plane` exploits — so reading that slope out
(`screen_ray`) and marching it through the grid (`pick_voxel`) gives full
three-dimensional picking **with no renderer change at all**.

`pick_voxel` returns the first solid voxel and the last empty one before it,
so the FACE decides where a block goes and no case analysis is needed: aim at
a top face and you build on top, at a side face and you build beside. It is
the general form of `pick_block` — a centre-column ray at the horizon has
`z_per_px == 0` and reduces to the same walk.

What it does NOT lift is the vertical field of view, now measured rather than
guessed: at the very bottom of a 600px view the steepest ray drops about half
a cell per cell, roughly **26 degrees**. Consequences worth knowing before
designing a sample around building: you must stand a couple of cells back for
a ray to reach another layer at all, you can never see the top of a block on
your OWN layer (its top is half a cell above the eye), and you cannot dig
straight down. That 26 degrees is the concrete cost of deferring 2c.

The gap rule stays for the ACTIONS, which have a crosshair and no mouse. But
note the interaction it creates there: once a hole exists ahead of you, every
placement goes into it until it is filled. Defensible (you fix what you
broke) but worth revisiting if a real game feels boxed in by it — and it is
the reason the outline looked frozen.

**The camera is a two-block-tall body (2026-08-13), and it had to be.**
Playtest: "I can place blocks out from existing walls but I cannot put one
block on top of another block." Not a picking bug. A block beside you has its
top face at z = 1, so an eye at `layer + 0.5` sits BELOW that surface and
sees its underside — the face points away from you, at every pitch, so no
amount of 2c helps. `DEFAULT_EYE_HEIGHT` is now **1.5**, matching what every
block game does and what makes stacking possible at all.

Two consequences that have to move with it, or the view and the actions
disagree:

- **The actions address the layer the EYE is in**, not the layer the feet are
  on. A level crosshair points at eye height; picking the feet layer would
  break a block the crosshair is not on.
- Anything computing an eye position reads `eye_height` from the config
  rather than assuming 0.5 — the walkaround did, and would have aimed a whole
  layer low.

Changing a default like this is free ONLY because no sample ships on this
engine yet. After Phase 5 it would be a migration. If another such default is
in doubt, settle it before Phase 5, not after.

Note for anyone reading the geometry tests: they pin `eye_height: 0.5`
deliberately, because their closed-form assertions are 1:1 with layer numbers
that way. `TestDefaultEyeHeight` is what covers the shipped value, including
a control proving the old one genuinely could not stack.

Still open in this phase: the hotbar, and a committed world generator. Also
worth doing eventually: exposing the outline to authored games as an action,
so a building game does not have to reimplement it — it is currently drawn
only by the walkaround.

Two new actions (`place_block`, `break_block`), mouse-bound, operating on
whichever cube the camera's centre ray currently hits (reuse the DDA hit-test
from Phase 2, don't write a second raycast for picking). A **hotbar**:
a small fixed list of block-type slots, current selection an instance
variable — deliberately not a full inventory/crafting system; that's a
much larger feature with unclear teaching value at this stage and should be
its own follow-up plan if wanted later, not bundled in here.

World **authoring**: no in-IDE block-placing editor in this phase — worlds
are built the same way `raycast_2`/`raycast_3` mazes were, via a committed
generator script (`tools/gen_block_world_*.py`) or a small hand-authored
starting layout, so there's something to playtest before any editor UI work
is justified. A visual world editor (paint blocks in 3D inside the Room
Editor, mirroring the Room Editor's existing tile painter) is a legitimate
later phase, not Phase 3.

## Edit mode vs play mode — open design question (raised 2026-08-13)

Raised from playtesting Phase 3: breaking is instant and unbounded, so it is
far too easy to wreck a world by accident. The obvious framing is a global
"edit mode / play mode" switch. **Recommend not building that**, because the
concern is really two concerns living at different layers:

- **Authoring** — someone building a world. This is the deferred visual world
  editor (see Phase 3's note), and it is where undo/redo belongs. Note this
  repo has already reasoned about destructive edits twice and landed in two
  different places: `QUndoStack`/`QUndoCommand` for live in-memory canvas
  edits, and the soft-delete Trash for file-level asset deletion (the
  2026-08-09 session note explains why an undo stack was the wrong tool
  there). A block edit is squarely the first kind — one live object, no file
  I/O — so `QUndoCommand` is right here, and `editors/room_undo_commands.py`
  is the pattern to copy.
- **Playing** — whether the player can break anything at all is the AUTHOR's
  decision, expressed by binding `break_block` to an input event or not
  binding it. There is nothing for the engine to switch. The walkaround feels
  dangerous only because it is a harness with no event system and wires the
  mouse up unconditionally.

A global engine mode would add a concept without adding capability: the
author would still have to decide when to flip it, which is the same decision
as whether to bind the action.

**What the engine genuinely lacked**, independent of any mode, was a way to
say *this block cannot be broken* — so a player cannot dig out through the
world boundary, and so an author can protect scenery.

**Done (2026-08-13): the `breakable` flag.** `BLOCK_TYPES` already carried
`solid` and `transparent`; `breakable` (default True) is the natural third,
read by `state.is_breakable` and checked in `break_block` and nowhere else.
An unbreakable block is still targeted (the crosshair lights up, which is the
feedback saying it is there and solid), still occludes, still gets built
against, and can still be *placed* — an author lining a world's edge with the
stuff has to be able to put it there. Swinging at one is a silent no-op.

**`obsidian` is the designated boundary material.** A flag no type ever sets
is the same unreachable-code-posing-as-a-safety-net that mutation testing
caught in `place_block` earlier the same day, so it needed a real user from
the start. Obsidian is the only near-black stone in the registry, so "the
black one cannot be broken" reads at a glance with no HUD to explain it, and
it needs no new texture or `ASSETS.md` row. An unknown block id counts as
breakable: a typo must not silently produce indestructible scenery.

Mutation testing note: three of the four mutants were caught immediately, but
*moving the check into `place_block` as well* survived — nothing pinned the
"only in break_block" half of the requirement until a test placed an
unbreakable type and asserted it lands.

Still open here: an optional protected *region* (a bounding box the actions
refuse to modify), the follow-up if per-type turns out too coarse. The editor
and its undo stack are their own phase after Phase 5, when there is a real
world worth editing.

## Phase 4 — collision, gravity, HUD

- Player collision against voxel occupancy (extends the "check the grid cell
  ahead" approach the maze samples already use, one dimension richer).
- Simple gravity/jump against the heightmap from 2b.
- HUD: crosshair + hotbar strip, built as a macro action
  (`build_block_world_hud_commands()`) the same way `draw_minimap`/
  `draw_doom_hud` are macro actions in `raycast_2_5d/hud.py` — no new
  draw-queue primitive needed, just emitted rectangles/sprites/text.

## Phase 5 — sample game

One sample (working name `block_world_1`) proving the engine end to end:
a small hand-built or generated island/room, a handful of block types from
the Phase 0 asset audit, place/break, a simple goal (e.g. "build a bridge to
reach the flag"). Welcome-tab entry + guide, following the same
guide-translation-optional pattern the raycast samples use (English guide
first; translations are a separate, explicitly budgeted follow-up per the
existing i18n cost note in this repo's session history — roughly 40% of a
session per language for a full sample-guide set).

## Phase 6 — export parity (HTML5 + Kivy)

Do this **last**, after the desktop engine is genuinely stable — this was
consistently the most expensive part of the raycast arc (three independent
hand-written renderers, y-up/y-down mirroring, brace-doubling in Kivy's
`.format()` templates, no CI execution environment for either target). Follow
`extensions/raycast_2_5d/export_html5.js` / `export_kivy.py`'s established
injection-marker pattern from day one rather than inlining voxel code into
`engine.js`/`kivy_exporter.py` and extracting later (that extraction was its
own multi-commit stage — Stage C — in the raycast plan; starting extension-
native avoids repeating it).

Known open question to resolve *during* this phase, not before: whether
`viewport_height`-style letterboxing or a HUD-over-3D compositing approach
(`RAYCAST_HUD_PLAN.md` / `RAYCAST_DOOM_HUD_PLAN.md`) is closer to what a
hotbar needs — likely the latter, since a hotbar is a fixed bottom strip like
the DOOM HUD, not letterboxing.

## Explicitly out of scope for this plan

- Infinite/procedural terrain generation (Phase 1 note).
- Crafting/inventory beyond a fixed hotbar (Phase 3 note).
- A visual block-placing world editor in the IDE (Phase 3 note) — start with
  generator scripts.
- Multiplayer. There's a separate, already-decided plan to rebuild LAN
  multiplayer as its own folder extension (see the `multiplayer-network-stash`
  memory) — if a shared block world is ever wanted, that's a pairing between
  two independent extensions, not something this plan should try to design
  for preemptively.

## Landmines to watch for (anticipated from the raycast arc's history)

- **Exact-grid-line coincidence.** The raycast engine hit real bugs from
  camera rays originating exactly on a grid line (instance x/y at exact cell
  multiples). A voxel world is grid-aligned on all three axes, so this hazard
  is *more* likely here, not less — offset ray origins to cell centers from
  the first renderer commit, don't wait to discover it the hard way.
- **`create` re-firing on `restart_room`.** Any score/inventory/hotbar init
  belongs in `game_start`, not `create` — this cost a real bug in `raycast_2`
  (lives resetting every death) and will cost the same bug here for hotbar
  contents if placed wrong.
- **Kivy `.format()` templates need doubled braces**; **PowerShell commit
  messages with quotes need `git commit -F <file>`** on the Windows box —
  both are standing repo-wide gotchas, not new to this feature.
- **One-sided collision handlers.** The runtime only reliably fires one side
  of a collision pair — put pickup/break logic on the side proven to fire
  (see `raycast_4`'s key-pickup fix) rather than assuming both handlers run.

## Suggested sequencing

Phase 0 → 1 → 2a → 2b → 2c → 3 → 4 → 5 → 6, one commit-worthy unit at a
time, each gated on the full test suite + a smoke run, matching this repo's
established session-limit discipline (one task ≈ one commit, pushed
immediately). Phase 6 remains the one genuinely deferrable-until-asked-for
stage — everything through Phase 5 is enough for a real, playable, legally
clean sample. See "Finishing the plan" below for the concrete remaining
units, in order.

## Finishing the plan — remaining units (2026-08-14)

Phases 0–2c are done. Phase 3 has picking, `place_block`/`break_block`,
unbreakable blocks, and pitch-aware picking landed; two units remain to
close it. Phases 4–6 haven't started. In dependency order:

**Unit 1 — world data loading (closes a Phase 1 deferral, blocks everything
below it).** `state.py`'s own docstring has said since Phase 1 that "wiring
an actual load path is Phase 3+" — it still isn't wired. `to_block_list`/
`load_block_list` can round-trip a Python list in memory, but nothing reads
a world from a file at `create`/`game_start`, so there is no way to author a
world once and ship it — every world that exists right now (the preview
tool's demo scene) is hand-built Python, not data. Needed before the
generator (Unit 2) or the sample (Phase 5) can produce anything a real game
loads: a small new action (working name `load_block_world`, mirroring how
`enable_block_world_view` reads its own config) that reads a bundled JSON
asset in the `to_block_list` shape and calls `state.load_block_list` —
bound in `game_start`, not `create`, per this doc's own landmine list below.

**Unit 2 — a committed world generator (closes Phase 3).** Same pattern as
`tools/gen_raycast_3_maze.py`: a script under `tools/`, checked in (not
throwaway), that emits a `to_block_list`-shaped JSON file rather than
placing blocks by hand. Depends on Unit 1 to actually be loadable by a game.
Scope: reuse a maze/room generator's shape (walls + floor) translated into
block placements, sized for a Phase 5-sized sample rather than a full
game — this generator IS most of Phase 5's world, not a separate artifact.

**Unit 3 — the hotbar (closes Phase 3).** Re-examine the original scope
before building it: `execute_place_block_action`'s `block` parameter already
resolves through `ae._parse_value`, so an author can already bind it to
their own instance variable and cycle it with ordinary `set_variable` /
key-press actions — a hotbar may need **no new action at all**, just a
documented pattern (a `hotbar_index`/`hotbar_slot` instance-variable
convention) plus the HUD (Unit 6) actually drawing it. Decide during
implementation, not before, whether a small convenience action
(`select_hotbar_slot`, absolute or relative like `set_look_pitch`) earns its
keep over the author writing three lines of `set_variable`/conditional
themselves — if the sample in Phase 5 needs it written out longhand three
times, that is the signal to add the action. Whichever way it goes, the HUD
macro action (Unit 6) needs a stable parameter shape for "slots + selected
index" decided here first, since it consumes whatever this unit produces.

**Unit 4 — collision (Phase 4).** Extends the "check the grid cell ahead"
approach the maze samples already use, one dimension richer: a moving
instance's next position must be checked against `get_block`/`BLOCK_TYPES
[...]['solid']` at its own z-layer, not just x/y. Open design question to
settle here, not deferred: expose this as a full opinionated movement
action (a `move_and_collide`-style action, closer to how the maze samples'
built-in movement works), or as a smaller helper an author's own movement
code calls before applying a move (closer to how raycast's picking exposes
primitives rather than a full controller). Whichever is chosen, `_pick`
already established the pattern of layering picking on top of `march_ray`
without a second DDA — collision should reuse `get_block`/`stack_top`, not
grow a third occupancy query.

**Unit 5 — gravity/jump (Phase 4, depends on Unit 4).** The step-up logic
already exists, just not as an engine feature: the preview tool's own
movement script already builds falling/stepping on `stack_top(room, x, y)`
(the plan doc's Phase 2b notes call this out explicitly as "the heightmap
query Phase 4's footing will reuse"). This unit is mostly *promoting* that
already-proven demo-tool logic into a real, tested engine primitive (action
or documented pattern, same open question as Unit 4) rather than inventing
new physics.

**Unit 6 — HUD (Phase 4, depends on Unit 3 for the hotbar's parameter
shape).** `build_block_world_hud_commands()`, a macro action in the same
family as `raycast_2_5d.hud.build_minimap_commands`/
`build_doom_hud_commands` — crosshair (a fixed screen-centre mark, no
geometry needed) plus a hotbar strip (reads whatever shape Unit 3 settled
on). No new draw-queue primitive; emits ordinary rectangle/sprite/text
commands like its raycast siblings.

**Unit 7 — the `block_world_1` sample (Phase 5, depends on Units 1–6).** A
small world via Unit 2's generator, a handful of block types from the Phase
0 audit, place/break bound to real input, a goal ("build a bridge to reach
the flag" per the original Phase 5 note, or similar). Welcome-tab entry +
an English guide; translations stay a separate, explicitly budgeted
follow-up per this repo's established i18n cost note, not part of this
unit. This is also where the "camera is a two-block-tall body" default and
every other block-world default gets genuinely load-bearing — per the
Phase 3 note above, changing a default is free only *before* a sample
ships; audit defaults one more time in this unit, before Phase 6 makes
changing them a three-target migration too.

**Unit 8 — HTML5 export (Phase 6, depends on Unit 7 — port a real,
finished sample, not a moving target).** Follow
`extensions/raycast_2_5d/export_html5.js`'s injection-marker pattern from
day one: a generic room-renderer/action registry seam already exists in
`engine.js` from the raycast arc, so this should be *using* that seam, not
rebuilding it. Port `march_ray`/`pick_voxel`/`render_block_world_view`'s
JS equivalents plus all Phase 3/4 actions.

**Unit 9 — Kivy export (Phase 6, depends on Unit 7, can run in either order
relative to Unit 8).** Same seam-reuse principle via `export_kivy.py`'s
established injection markers. Watch the standing landmine: Kivy scene
classes are `.format()` templates, so injected Python needs its braces
un-doubled only after confirming zero `.format()` fields remain in the
block, the same discipline the raycast Stage C move used.

**Unit 10 — resolve the HUD compositing question (Phase 6, during Units 8–9,
not before).** Whether `viewport_height`-style letterboxing or a
HUD-over-3D compositing approach fits the hotbar strip is explicitly an
open question in the Phase 6 section above; the raycast DOOM-HUD precedent
(a fixed bottom bar, not letterboxing) is the likely answer but should be
confirmed against Unit 6's actual HUD shape, not assumed.

**Explicitly not in this plan** (already listed above, restated for
completeness since they're easy to accidentally scope back in while
building Units 4–7): infinite/procedural terrain, a full inventory/crafting
system, an in-IDE visual world editor, and the optional protected-region
follow-up to the `breakable` flag (build only if per-type protection proves
too coarse once the sample exists to test it against).

Sequencing note: Units 1–3 can be done in almost any relative order (1
before 2 is the only hard dependency), but Units 4–10 are a straight
dependency chain as written. One commit per unit, full suite + smoke test
each time, same discipline as every prior unit in this plan.
