# Voxel World extension — plan

Status: **Phase 0, 1, 2a and 2b done (2b: 2026-08-13); Phase 2c deferred as
planned, Phase 3 is next.**
This doc is the worked
plan for a Minecraft-*inspired* block-building extension, built the same way
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
- **2c — free look (stretch, likely deferred).** Full 3D DDA with pitch
  (looking up/down), needed for tall builds or deep pits to read correctly
  from up close. This is the expensive step (real 3D ray marching, not the
  2D-plus-height approximation of 2b) — treat it the way the raycast plan
  treated floor-casting on HTML5/Kivy: land 2a/2b for real, defer 2c behind
  an explicit follow-up decision once students have actually used 2b.

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
- Free vertical camera look (Phase 2c) unless a later decision reopens it.
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

Phase 0 → 1 → 2a → 2b → 3 → 4 → 5, one commit-worthy unit at a time, each
gated on the full test suite + a smoke run, matching this repo's established
session-limit discipline (one task ≈ one commit, pushed immediately). Phase
2c and Phase 6 are the two genuinely optional/deferrable-until-asked-for
stages — everything through Phase 5 is enough for a real, playable, legally
clean sample.
