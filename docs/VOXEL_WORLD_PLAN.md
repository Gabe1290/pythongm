# Voxel World extension — plan

Status: **Phase 0 and Phase 1 done (2026-08-12); Phase 2 not started.**
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
- **2b — multi-layer heightmap.** Blocks stack (a handful of Z layers, not
  arbitrary depth), player can walk up single-block steps and see over
  short walls. Still no free vertical camera look — pitch stays level, like
  raycast_1-4. This is enough for "build a little house," "dig a pit,"
  "stack blocks to reach a ledge" — most of what students will actually want.
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
