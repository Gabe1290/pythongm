# Plan: procedural / infinite Block World terrain (Tier 7e)

Status: **ALL FOUR PHASES DONE (2026-08-15).** Written 2026-08-15 per
`docs/REMAINING_WORK_2026-08-15.md` Section F, which sizes this as
"comparable to a second `docs/VOXEL_WORLD_PLAN.md`." Implemented the same
day it was written, one phase per commit, full-suite-green gate each,
resolving every open design question below with the recommendation this
doc itself already leaned toward: chunk size 16 (the plan's own starting
guess, never revisited since nothing has needed to yet), no cross-target
determinism requirement, and "touched chunks persist their full current
content" rather than a true cell-level diff (a deliberate simplification
over the plan's literal "diff" wording -- still solves the real
scalability problem, documented in state.py's to_touched_block_list
docstring). `samples/block_world_2` demonstrates it end to end: a room
with no `load_block_world` call at all, purely `enable_block_world_view`'s
`generate`/`seed` params, that generates real rolling terrain in every
direction with no boundary. See each phase heading below for exactly what
landed; docs/BLOCK_WORLD_EDITOR_PLAN.md's own status header (Tier 7d, the
prerequisite this plan's own "why this is sequenced last" section
named) records that it finished first, the same day.

## Why this is out of reach today, precisely

`extensions/block_world/state.py`'s world model (unchanged since Phase 1 of
the original plan, still accurate as of this doc's writing):

- **Storage**: one Python dict per room, `{"x,y,z": block_type_string}`,
  held entirely in memory (`room.extension_state["block_world"]["blocks"]`).
- **Persistence**: `to_block_list`/`load_block_list` serialize the **entire
  dict** to/from one flat JSON list in one shot. There is no partial
  load/save.
- **Derived cache**: `column_index(room)` rebuilds by calling
  `iter_blocks(room)` — a walk of **every block in the dict** — any time a
  mutator invalidates it (`_invalidate_columns`, called from every
  `set_block`/`remove_block`/`load_block_list`). Cost scales with total
  blocks ever placed, not with what's near the camera.
- **Rendering is already distance-bounded, which narrows the real
  problem**: `renderer.py`'s `march_ray` walks a DDA line capped at
  `render_distance` cells per ray (`renderer.py:820-853`) — it does NOT
  scan the whole world every frame today. So "infinite terrain" is not
  primarily a rendering-cost problem; it's a **storage/generation**
  problem. Worth stating precisely so implementation doesn't over-engineer
  the rendering side to solve a bottleneck that mostly isn't there.

Three separate things are missing, and all three are required together —
shipping only one doesn't produce "infinite terrain":

1. **Chunking** — the storage model needs to stop being "one dict, one
   file, whole world" so a world bigger than fits comfortably in memory/one
   JSON file is possible at all.
2. **Procedural generation** — there is currently **zero** noise/seed-based
   generation anywhere in this engine. Every block today is either
   hand-placed (`place_block`/the preview tool's `build_world`) or loaded
   from a finite, fully-authored file (`load_block_world`). "Infinite"
   requires something that fills in never-visited space on demand.
3. **Bounded working set** — `column_index` needs to stop being "rebuild
   from every block ever placed" and become "rebuild from chunks near the
   camera," or the *storage* problem above is solved while the *per-mutation
   cache cost* problem isn't.

## Open design questions — decide before writing code, not while writing it

- **Chunk size.** No number is picked yet. Smaller chunks = finer-grained
  loading but more per-chunk bookkeeping overhead; larger = the opposite.
  A reasonable starting guess (16×16 columns, unbounded in z, matching how
  the existing world is column-indexed by `(x, y)` already) is *a guess*,
  not a decision — pick it empirically once there's a real chunked
  prototype to profile, not in this doc.
- **Generation algorithm.** Perlin/Simplex noise is the standard choice for
  this genre, but this repo has **zero existing noise-generation code** to
  build on — it would be a new dependency (or a hand-rolled
  value-noise implementation) on **all three targets independently**
  (desktop Python, HTML5 JS, Kivy Python) if procedural terrain needs to
  look identical across exports, the same "three hand-written copies, one
  precedent" pattern every other cross-target feature in this repo
  (raycast's DDA, block world's own DDA/shading constants) has already
  established. **Open question worth settling explicitly: does procedural
  terrain need to be identical across targets at all?** Unlike jump
  physics or particle aging (where a player could reasonably compare
  desktop vs. web behavior directly), infinite terrain is typically
  experienced on ONE target per playthrough — a strong case exists for
  "the generation algorithm only needs to be internally consistent
  per-target (same seed → same world, deterministic, on whichever target
  you're running), not byte-identical ACROSS targets." If true, this cuts
  the generation work roughly to a third — each target can have its own
  straightforward noise implementation without a shared-parity test
  burden. **Recommend deciding this is true** (no cross-target determinism
  requirement) unless there's a concrete use case (e.g. a saved seed
  shared between a desktop player and a web player expecting the same
  world) that specifically needs it — and if that use case doesn't exist
  yet, don't build for it speculatively.
- **What persists vs. what regenerates.** The standard, well-proven model
  (Minecraft and every similar game): a chunk's terrain is
  100% reproducible from `(seed, chunk_coords)` alone, so an
  UNMODIFIED chunk needs **zero storage** — only chunks the player has
  actually changed (placed/broken a block in) need their diff persisted.
  This needs `to_block_list`/`load_block_list`'s shape to grow a
  `seed` field and a per-chunk "has this been touched" flag, and
  `set_block`/`remove_block` need to mark a chunk dirty the first time
  they touch it. This is a real, non-trivial change to the save format —
  plan for a migration story (a room saved under the old flat-list format
  should still load) rather than a breaking one.
- **Loading/unloading trigger.** Chunk load radius around the camera —
  tied to `render_distance` (the config value the renderer already reads,
  `enable_block_world_view`'s own parameter) is the natural choice, so a
  chunk stays loaded slightly further out than the render distance that
  would draw it, avoiding pop-in at the exact render boundary.

## Suggested phase breakdown (once the questions above are answered)

1. **Chunked storage, generation-free.** Split `state.py`'s single dict
   into `{(chunk_x, chunk_y): {"x,y,z": type}}`. `column_index` rebuilds
   per-chunk instead of globally; a mutator invalidates only its own
   chunk's cache entry, not the whole world's. `to_block_list`/
   `load_block_list` gain a chunked-aware save/load path. **No new
   gameplay yet** — an author-built, finite, hand-placed world (everything
   that works today) must keep working byte-for-byte through this phase,
   proven the same way every other consolidation in this repo's history
   has been: snapshot behavior against pre-change HEAD, diff.
2. **Seed-based generation for one target (desktop only).** Pick the
   chunk-size and algorithm questions above for real. A chunk requested
   that has no stored diff generates deterministically from
   `(seed, chunk_x, chunk_y)`. Loading/unloading driven by camera distance.
   This phase proves the concept works at all before paying the 3x
   cross-target generation cost.
3. **HTML5 + Kivy generation**, once desktop's approach is proven — each
   port's own generation implementation (see the cross-target-determinism
   question above for whether these need to numerically match desktop or
   just be internally consistent).
4. **A sample** demonstrating genuinely large/unbounded exploration —
   `raycast_2`'s maze-generator precedent (`tools/gen_raycast_3_maze.py`,
   a **committed** generator script, not a throwaway one) is the right
   model for how a generated-world sample should ship: reproducible,
   regenerable, not just a giant static JSON blob checked into the repo.

## Explicitly out of scope

- **Level-of-detail (LOD) rendering** (distant chunks rendered at reduced
  detail) — `VOXEL_WORLD_PLAN.md`'s own Phase 1 notes named this as part of
  "the much bigger engineering problem" being deliberately deferred; still
  deferred here. The render pass is already distance-bounded by
  `render_distance`, so LOD is a *quality/performance tuning* concern for
  once generation exists and is slow, not a blocker to a first cut.
- **Multiplayer-shared infinite worlds** (two players in the same
  generated world seeing consistent chunk state) — depends on
  `docs/MULTIPLAYER_LAN_PLAN.md` existing first, and that plan's own scope
  is explicitly single-snapshot position sync, not shared world-state
  authority. Do not combine these two plans' scope.
- **Biomes / structure generation / anything beyond raw heightmap-style
  terrain.** A first cut should be "the ground undulates and has variety,"
  not "there are villages." Structure generation is a distinct, larger
  problem worth its own follow-up once basic terrain generation exists and
  is fun to walk around in.

## Why this is sequenced last among the Block World items

Both `docs/BLOCK_WORLD_EDITOR_PLAN.md` (Tier 7d) and this plan touch
`extensions/block_world/state.py`'s storage model — the editor plan's own
"per-room sibling file" save/load design and this plan's chunked storage
are not obviously compatible without a decision about which one lands
first and how the other adapts. Recommend the editor lands first (it
targets the CURRENT finite-world storage model, which is simpler and
already well-understood) and this plan's chunking work treats the editor's
save/load format as something it needs to migrate FROM, not something
designed concurrently with an unstable target.
