#!/usr/bin/env python3
"""Per-room voxel world data model, namespaced into ``room.extension_state``.

Mirrors extensions/raycast_2_5d/state.py's pattern: nothing voxel-specific
touches core's GameRoom. A room's block layout lives under
``room.extension_state["block_world"]`` -- created on first access via
``block_world_state(room)`` (get-or-create) or read without creating via
``peek_blocks(room)`` (needed once a room renderer exists in Phase 2, so it
doesn't stamp block-world state onto every room in the game).

Storage is **chunked** (docs/BLOCK_WORLD_INFINITE_TERRAIN_PLAN.md, Tier 7e
Phase 1): ``{(chunk_x, chunk_y): {"x,y,z": block_type}}``, one sparse dict
per CHUNK_SIZE x CHUNK_SIZE column of (x, y) space, z unbounded within a
chunk. Absence of a key (chunk missing, or block key missing within a
present chunk) means air; there is no stored "air" block. Splitting by
chunk (rather than one flat world-wide dict, Phase 0-6's original shape)
is what makes a mutator's cache invalidation (see ``_chunk_columns``
below) proportional to the ONE chunk it touched instead of the whole
world -- necessary once Phase 2 adds generation and a world can have far
more chunks loaded than get edited in any given frame. This phase adds
no generation and no new gameplay: every public function below returns
byte-identical results for byte-identical inputs versus the pre-chunking
implementation, proven by the full pre-existing block_world test suite
staying green across the change.

``to_block_list`` / ``load_block_list`` round-trip the chunked storage
to/from a flat list of ``{"x", "y", "z", "type"}`` dicts -- the shape
convention room JSON already uses for tile layers (see the "tiles" key
rooms save under today), and the exact shape ``blocks/<room>.json``
sibling files (editors/block_world_editor/io.py, load_block_world) already
use on disk -- chunking is purely an in-memory concern; the file format
is untouched. Nothing in this module reads or writes room JSON directly:
extension_state is transient runtime state, same as raycast's camera
config (rebuilt by an action each run, never persisted by core -- see
extensions/raycast_2_5d/state.py's own docstring).
"""

import os

BLOCK_WORLD_KEY = "block_world"

TEXTURE_DIR = os.path.join(
    os.path.dirname(__file__), "textures", "source_hand_painted_expanded"
)

# Block type registry: id -> face textures + physical flags. Every filename
# referenced here is one of the 32 files audited into this extension's
# ASSETS.md -- add a block type only alongside a matching ASSETS.md row.
#
# Face keys: "all" (same texture on every face) or "top"/"bottom"/"side"
# (side covers all four vertical faces -- no per-cardinal-direction texturing,
# unlike Luanti's node definitions). "solid" gates collision (Phase 4);
# "transparent" flags a block a renderer (Phase 2) should not use to occlude
# whatever is behind it.
BLOCK_TYPES = {
    "dirt": {"all": "default_dirt.png", "solid": True},
    "grass": {
        "top": "default_grass.png",
        "bottom": "default_dirt.png",
        "side": "default_grass_side.png",
        "solid": True,
        # default_grass_side.png has real alpha holes (~44% of its pixels
        # below full opacity) -- untagged, a gapless grass stack satisfied
        # the occlusion early-out and hid whatever should show through the
        # holes, the same point-blank bug found and fixed for glass/water/ice.
        "transparent": True,
    },
    "stone": {"all": "default_stone.png", "solid": True},
    "cobble": {"all": "default_cobble.png", "solid": True},
    "sand": {"all": "default_sand.png", "solid": True},
    "desert_sand": {"all": "default_desert_sand.png", "solid": True},
    "sandstone": {"all": "default_sandstone.png", "solid": True},
    "gravel": {"all": "default_gravel.png", "solid": True},
    "clay": {"all": "default_clay.png", "solid": True},
    "wood_log": {
        "top": "default_tree_top.png",
        "bottom": "default_tree_top.png",
        "side": "default_tree.png",
        "solid": True,
    },
    "wood_plank": {"all": "default_wood.png", "solid": True},
    "jungle_plank": {"all": "default_junglewood.png", "solid": True},
    "pine_plank": {"all": "default_pine_wood.png", "solid": True},
    # default_leaves.png has real alpha holes (~19% of its pixels below full
    # opacity) -- same reasoning as grass's side face, above.
    "leaves": {"all": "default_leaves.png", "solid": True, "transparent": True},
    "glass": {"all": "default_glass.png", "solid": True, "transparent": True},
    "water": {
        "all": "default_water_source_animated.png",
        "solid": False,
        "transparent": True,
    },
    "ice": {"all": "default_ice.png", "solid": True, "transparent": True},
    "snow": {"all": "default_snow.png", "solid": True},
    "coal_block": {"all": "default_coal_block.png", "solid": True},
    "gold_block": {"all": "default_gold_block.png", "solid": True},
    "diamond_block": {"all": "default_diamond_block.png", "solid": True},
    "brick": {"all": "default_brick.png", "solid": True},
    # The designated boundary material: the one block break_block refuses to
    # remove. Line a world's edges with it and a player cannot dig out. It is
    # the only near-black stone in the registry, so "the black one cannot be
    # broken" is a rule that reads at a glance and needs no HUD to explain.
    "obsidian": {"all": "default_obsidian.png", "solid": True, "breakable": False},
    "mese_block": {"all": "default_mese_block.png", "solid": True},
    "wool_red": {"all": "wool_red.png", "solid": True},
    "wool_blue": {"all": "wool_blue.png", "solid": True},
    "wool_green": {"all": "wool_green.png", "solid": True},
    "wool_yellow": {"all": "wool_yellow.png", "solid": True},
    "wool_white": {"all": "wool_white.png", "solid": True},
    "wool_black": {"all": "wool_black.png", "solid": True},
}

# The hotbar (Phase 3 Unit 3): a small FIXED list of block-type SLOTS, not a
# full inventory/crafting system -- crafting is still deliberately out of
# scope, see docs/VOXEL_WORLD_PLAN.md's Phase 3 notes and Tier 7c's own
# notes in docs/DEFERRED_GAPS_2026_PLAN.md. Real per-block-type COUNTS
# (pickup-on-break, consume-on-place) were added on top of this fixed slot
# list in Tier 7c -- opt-in via enable_block_world_view's `inventory`
# parameter, stored the same way selection already was: on the PLAYER
# instance (instance.block_inventory, a {block_type: count} dict lazily
# created by break_block/place_block), not here or in the room's camera
# config, so it stays per-player rather than per-room -- the natural shape
# for eventual multiplayer, and simply correct even for one player, since
# the room's block-world state is not whose inventory this is. Was the
# preview tool's own HOTBAR list first, proven there before being promoted
# here; the preview tool now imports this instead of keeping its own copy.
DEFAULT_HOTBAR = ["cobble", "brick", "wood_plank", "glass", "wool_red",
                  "sandstone", "gold_block", "leaves"]


def texture_path(filename):
    """Absolute path to a block-face texture file. No image loading here --
    that's a renderer (Phase 2) concern; this stays pygame-free like
    raycast's state.py, so the IDE can import this module for schemas
    without paying for a pygame import."""
    return os.path.join(TEXTURE_DIR, filename)


_FACE_PATH_CACHE = {}


def block_face_textures(block_type):
    """Resolve a block type id to its {"top", "bottom", "side"} texture map
    of absolute file paths.

    Memoised, and worth it: the renderer asks per block, per cell, per screen
    column, which on a scene showing a lot of geometry is tens of thousands
    of calls a frame -- profiling a single frame of the preview's terrace
    view found 60,905, making this the most expensive thing in the whole
    render path purely through os.path.join. BLOCK_TYPES is a static
    registry, so the answer never changes; anything that adds a block type at
    runtime must clear this cache.

    Raises KeyError for an unknown block_type -- callers are expected to
    validate against BLOCK_TYPES themselves when the id comes from untrusted
    data (e.g. a loaded world file)."""
    cached = _FACE_PATH_CACHE.get(block_type)
    if cached is not None:
        return cached
    faces = BLOCK_TYPES[block_type]
    if "all" in faces:
        path = texture_path(faces["all"])
        resolved = {"top": path, "bottom": path, "side": path}
    else:
        resolved = {
            "top": texture_path(faces["top"]),
            "bottom": texture_path(faces["bottom"]),
            "side": texture_path(faces["side"]),
        }
    _FACE_PATH_CACHE[block_type] = resolved
    return resolved


def is_breakable(block_type):
    """False for a block `break_block` must refuse to remove.

    Defaults to True, so a block type says nothing unless it wants to be
    indestructible. Checked in the break action ONLY: an unbreakable block is
    still targeted (the crosshair lights up on it, which is the feedback that
    tells you it is there and solid), still occludes, still gets built
    against. It just does not go away.

    This is the whole of the protection model on purpose -- see the
    edit-mode/play-mode section of docs/VOXEL_WORLD_PLAN.md for why the
    engine has no modes. An unknown block id counts as breakable; the caller
    validates ids, and a typo should not silently produce indestructible
    scenery."""
    return bool(BLOCK_TYPES.get(block_type, {}).get("breakable", True))


def is_transparent(block_type):
    """True for a block you can see THROUGH -- glass, water, ice.

    A renderer must not treat one as an occluder: anything behind it is still
    visible, so it can neither stop a ray nor be used to decide that whatever
    is further away can be skipped."""
    return bool(BLOCK_TYPES.get(block_type, {}).get("transparent"))


def _key(x, y, z):
    return "%d,%d,%d" % (x, y, z)


# Columns per chunk side (x, y); z is unbounded within a chunk, matching how
# the world was already column-indexed by (x, y) before chunking. A starting
# guess per docs/BLOCK_WORLD_INFINITE_TERRAIN_PLAN.md, not a tuned constant --
# revisit once there's a real generated world to profile against.
CHUNK_SIZE = 16


def _chunk_key(x, y):
    return (x // CHUNK_SIZE, y // CHUNK_SIZE)


def _fresh():
    # "_chunk_columns" and "_merged_columns" are DERIVED caches (see
    # column_index) -- the leading underscore marks them as not part of the
    # saved world shape, the same way raycast_2_5d's per-room state
    # separates its camera config from the wall-edge caches it derives.
    #
    # "seed": None means no procedural generation -- every room from Phase
    # 0-1 (hand-placed or load_block_world-loaded, no seed ever set) behaves
    # completely unchanged (Tier 7e Phase 2,
    # docs/BLOCK_WORLD_INFINITE_TERRAIN_PLAN.md). "_touched_chunks" is the
    # set of chunk keys with at least one PLAYER edit (via set_block/
    # remove_block) since the room was created or loaded -- distinct from
    # "chunks", which also holds purely-generated, never-edited chunks that
    # must never be persisted (they're 100% reproducible from
    # (seed, chunk_coords), so saving them would be redundant and would
    # defeat the whole point of not storing an unbounded generated world).
    return {"chunks": {}, "camera": {"enabled": False},
            "_chunk_columns": {}, "_merged_columns": None,
            "seed": None, "_touched_chunks": set()}


def _peek_state(room):
    """This room's block-world state dict if it already exists, else None.

    Does NOT create it -- the one shared lookup ``_invalidate_chunk_columns``,
    ``peek_blocks`` and ``peek_camera`` all build on, so a future change to
    how state is namespaced (the key name, the getattr guard for bare test
    objects) has exactly one place to update instead of three copies that
    could drift out of sync."""
    es = getattr(room, "extension_state", None)
    return es.get(BLOCK_WORLD_KEY) if es else None


def _invalidate_chunk_columns(room, chunk_key):
    """Drop the derived per-column cache for ONE chunk, and the merged
    cache column_index() returns (cheap to rebuild -- see column_index --
    but must not go stale). Called by every mutator here, scoped to
    whichever chunk it touched -- a chunk nobody edited keeps its own
    cached column data, which is the whole point of chunking the cache
    (see this module's docstring).

    Code that reaches around these helpers and edits ``state["chunks"]``
    directly MUST call this too, or the renderer keeps drawing the old
    world for that chunk."""
    st = _peek_state(room)
    if st is not None:
        st.get("_chunk_columns", {}).pop(chunk_key, None)
        st["_merged_columns"] = None


def block_world_state(room):
    """This room's voxel world state, creating it (and extension_state) if
    absent. Use from code that legitimately owns/mutates the world (world-
    loading actions, place/break handlers once Phase 3 adds them). The
    getattr guard covers bare test objects the way raycast_state does."""
    es = getattr(room, "extension_state", None)
    if es is None:
        es = {}
        setattr(room, "extension_state", es)
    st = es.get(BLOCK_WORLD_KEY)
    if st is None:
        st = _fresh()
        es[BLOCK_WORLD_KEY] = st
    return st


def peek_blocks(room):
    """This room's ``{(chunk_x, chunk_y): {"x,y,z": type}}`` chunk dict if
    it already has block-world state, else None.

    Does NOT create state -- once a room renderer exists (Phase 2) it will
    run for every room, block-world or not, and must not stamp block-world
    state onto rooms that never used it. Mirrors
    extensions.raycast_2_5d.state.peek_camera. Callers that just want "does
    this room have any blocks at all" should prefer ``next(iter_blocks(room),
    None) is not None`` over inspecting this dict's shape directly -- it
    stays correct regardless of how chunking is implemented internally."""
    st = _peek_state(room)
    return st["chunks"] if st else None


def peek_camera(room):
    """This room's camera config if it already has block-world state, else
    None. Does NOT create state -- the room-renderer hook runs for EVERY
    room (block-world or not) and must not stamp state onto rooms that
    never enabled the view. Mirrors extensions.raycast_2_5d.state.peek_camera."""
    st = _peek_state(room)
    return st["camera"] if st else None


def get_block(room, x, y, z):
    """The block type id at (x, y, z), or None for air. Does not create
    state -- a room nobody has touched yet is simply all air."""
    chunks = peek_blocks(room)
    if chunks is None:
        return None
    chunk = chunks.get(_chunk_key(x, y))
    if chunk is None:
        return None
    return chunk.get(_key(x, y, z))


def set_block(room, x, y, z, block_type):
    """Place a block, creating world state on first use. block_type must be a
    key in BLOCK_TYPES -- validate before calling if it came from untrusted
    data. Marks the chunk TOUCHED (see _fresh's docstring) -- this can turn
    a purely-generated chunk into one with real edits, which must persist."""
    if block_type not in BLOCK_TYPES:
        raise KeyError(block_type)
    ck = _chunk_key(x, y)
    st = block_world_state(room)
    st["chunks"].setdefault(ck, {})[_key(x, y, z)] = block_type
    st.setdefault("_touched_chunks", set()).add(ck)
    _invalidate_chunk_columns(room, ck)


def remove_block(room, x, y, z):
    """Break/clear the block at (x, y, z). A no-op if it's already air or the
    room has no world state yet. Marks the chunk TOUCHED (see _fresh's
    docstring) if this actually removed something -- breaking a
    procedurally-generated block is exactly the kind of edit that must
    persist (and must stop that chunk from being regenerated over it, see
    generate_chunk's own guard)."""
    chunks = peek_blocks(room)
    if chunks is None:
        return
    ck = _chunk_key(x, y)
    chunk = chunks.get(ck)
    if chunk is not None and chunk.pop(_key(x, y, z), None) is not None:
        block_world_state(room).setdefault("_touched_chunks", set()).add(ck)
        _invalidate_chunk_columns(room, ck)


def iter_blocks(room):
    """Yield (x, y, z, block_type) for every placed block in the room, in no
    particular order. Empty for an all-air / not-yet-touched room."""
    chunks = peek_blocks(room)
    if not chunks:
        return
    for chunk in chunks.values():
        for key, block_type in chunk.items():
            x, y, z = (int(part) for part in key.split(","))
            yield x, y, z, block_type


def bounds(room):
    """(min_x, min_y, min_z, max_x, max_y, max_z) across every placed block,
    or None for an all-air room. A cheap sanity/debug helper -- the Phase 2
    renderer doesn't need world bounds to cast a ray."""
    xs, ys, zs = [], [], []
    for x, y, z, _block_type in iter_blocks(room):
        xs.append(x)
        ys.append(y)
        zs.append(z)
    if not xs:
        return None
    return min(xs), min(ys), min(zs), max(xs), max(ys), max(zs)


def to_block_list(room):
    """This room's blocks as a flat list of {"x","y","z","type"} dicts -- the
    JSON-serializable shape a world-authoring file should use. See this
    module's docstring for why this shape, not the internal string-keyed
    dict, is what should ever reach a file on disk."""
    return [
        {"x": x, "y": y, "z": z, "type": block_type}
        for x, y, z, block_type in iter_blocks(room)
    ]


def load_block_list(room, block_list):
    """Replace this room's world state with the blocks in block_list (the
    to_block_list shape). Overwrites whatever was there -- callers that want
    to layer blocks onto an existing world should call set_block per entry
    instead.

    Every chunk this touches is marked TOUCHED (see _fresh's docstring):
    explicitly-listed content, however it got here (a hand-authored
    load_block_world file, or the touched-chunk half of a generated
    world's save -- see load_world_state), must never be silently
    overwritten by generate_chunk on a later visit. Does NOT reset seed --
    callers that need to change it do so separately (load_world_state)."""
    chunks = {}
    for entry in block_list:
        block_type = entry["type"]
        if block_type not in BLOCK_TYPES:
            raise KeyError(block_type)
        x, y, z = entry["x"], entry["y"], entry["z"]
        chunks.setdefault(_chunk_key(x, y), {})[_key(x, y, z)] = block_type
    st = block_world_state(room)
    st["chunks"] = chunks
    st["_touched_chunks"] = set(chunks.keys())
    st["_chunk_columns"] = {}   # a full reload invalidates every chunk
    st["_merged_columns"] = None


def _chunk_column_index(room, chunk_key):
    """The column index for ONE chunk, cached until that chunk's own cache
    entry is invalidated (see _invalidate_chunk_columns)."""
    st = block_world_state(room)
    cache = st.setdefault("_chunk_columns", {})
    index = cache.get(chunk_key)
    if index is None:
        index = {}
        chunk = st["chunks"].get(chunk_key, {})
        for key, block_type in chunk.items():
            x, y, z = (int(part) for part in key.split(","))
            index.setdefault((x, y), []).append((z, block_type))
        for column in index.values():
            column.sort()
        cache[chunk_key] = index
    return index


def column_index(room):
    """``{(x, y): [(z, block_type), ...]}`` -- every non-empty column across
    every loaded chunk of the world, each sorted lowest z first. The SAME
    dict object is returned across repeat calls until something actually
    invalidates it (a real cache, not just memoized content).

    Rebuilt by merging each chunk's own cached column index (see
    _chunk_column_index) -- a chunk nobody touched keeps its cached columns
    rather than the whole world rebuilding on any single edit -- and the
    merge itself is cached too, so a mutation forces exactly one merge on
    the NEXT call rather than one per call until something changes again.

    Phase 2b's renderer needs the whole vertical STACK at each cell it steps
    into, and the backing store is keyed by a formatted ``"x,y,z"`` string.
    Probing that per candidate layer means a string format per lookup, which
    at 320 columns x 24 cells x a handful of layers is tens of thousands of
    formats per frame -- comfortably the most expensive thing in the render
    path. One tuple-keyed dict lookup per cell instead.
    """
    st = block_world_state(room)
    merged = st.get("_merged_columns")
    if merged is None:
        merged = {}
        for chunk_key in list(st["chunks"].keys()):
            merged.update(_chunk_column_index(room, chunk_key))
        st["_merged_columns"] = merged
    return merged


def stack_top(room, x, y):
    """The z of the highest block at (x, y), or None for an empty column.

    The heightmap query Phase 2b's "stand on top of things" needs, and Phase
    4's collision will want the same answer."""
    column = column_index(room).get((x, y))
    return column[-1][0] if column else None


def ground_layer(room, x, y):
    """The layer a body standing at this cell occupies: one above whatever
    it is standing on, or 0 over open ground (stack_top None).

    Promoted from tools/preview_block_world.py's own function of the same
    name (Phase 4 Unit 4) -- proven there first, across every viewpoint the
    preview tool's own walkaround exercises, before landing here."""
    top = stack_top(room, x, y)
    return 0 if top is None else top + 1


# How many layers a body can step up onto in one move without it reading as
# a wall rather than a step. 1, not any other value: a wall in this engine
# is any obstruction taller than this, by construction -- see
# docs/VOXEL_WORLD_PLAN.md's Phase 2b notes on why a one-block wall reads as
# a climbable step rather than an obstacle, and world design (both the
# tools/gen_block_world_demo.py generator and the preview tool's own demo
# scene) relies on that meaning consistently.
DEFAULT_MAX_STEP_UP = 1


def can_enter(room, x, y, standing_layer, max_step_up=DEFAULT_MAX_STEP_UP):
    """Can a body currently standing at ``standing_layer`` walk onto cell
    (x, y)? True if that cell's own footing is at most ``max_step_up``
    layers higher -- dropping any distance is always allowed, since this
    engine has no falling animation yet: a drop is just a step down.

    Promoted from tools/preview_block_world.py's own ``_can_enter`` (Phase 4
    Unit 4), proven there first."""
    return ground_layer(room, x, y) - standing_layer <= max_step_up


def cell_of(pixel_value, cell_size):
    """World pixel coordinate -> the grid cell index whose CENTRE it is
    nearest to (not floor-based). Matches how every body in this engine is
    positioned -- a camera/instance's centre sits at a cell centre when at
    rest (see renderer.py's exact-grid-line-coincidence note) -- so movement
    code that rounds a raw x/y this way agrees with where the renderer and
    picking already think the body is standing.

    Promoted from tools/preview_block_world.py's own ``cell_of`` lambda
    (Phase 4 Unit 4), proven there first."""
    return int((pixel_value + cell_size / 2) // cell_size)


# ---------------------------------------------------------------------------
# Procedural generation (Tier 7e Phase 2, desktop only --
# docs/BLOCK_WORLD_INFINITE_TERRAIN_PLAN.md). Deliberately not required to
# match the HTML5/Kivy ports byte-for-byte (Phase 3, if/when it lands) --
# the plan's own recommendation is that generation only needs to be
# internally consistent per-target (same seed -> same world, on whichever
# target you're running), not identical across targets, since a world is
# normally experienced on one target per playthrough. A hand-rolled value
# noise, not a library dependency: this repo has zero existing noise code
# to build on, and "the ground undulates and has variety" (this plan's own
# explicit scope -- no biomes, no structures) doesn't need anything fancier.
# ---------------------------------------------------------------------------

def _hash01(seed, x, y):
    """A cheap deterministic hash of (seed, x, y) -> float in [0, 1).
    Integer-only bit-mixing (no trig/floats), so it's exactly reproducible
    across any Python build -- unlike e.g. sin-based hashes, which can
    differ in their last bits across platforms/libm versions."""
    h = (seed * 374761393 + x * 668265263 + y * 2147483647) & 0xFFFFFFFF
    h = ((h ^ (h >> 13)) * 1274126177) & 0xFFFFFFFF
    h = (h ^ (h >> 16)) & 0xFFFFFFFF
    return (h % 100000) / 100000.0


def _smoothstep(t):
    return t * t * (3.0 - 2.0 * t)


def _value_noise(seed, x, y, scale):
    """Smoothly-interpolated value noise at world cell (x, y), in [0, 1).
    Bilinear interpolation of _hash01 at the surrounding integer lattice
    points spaced `scale` cells apart -- standard value noise, chosen over
    Perlin/Simplex for how little code it needs."""
    fx, fy = x / scale, y / scale
    x0, y0 = int(fx // 1), int(fy // 1)
    x1, y1 = x0 + 1, y0 + 1
    tx, ty = _smoothstep(fx - x0), _smoothstep(fy - y0)
    v00, v10 = _hash01(seed, x0, y0), _hash01(seed, x1, y0)
    v01, v11 = _hash01(seed, x0, y1), _hash01(seed, x1, y1)
    top = v00 + tx * (v10 - v00)
    bottom = v01 + tx * (v11 - v01)
    return top + ty * (bottom - top)


# Terrain shape constants -- a first cut's worth of "rolling hills", not
# tuned against anything. BASE_HEIGHT keeps the shortest columns at least a
# few blocks deep (so there's always solid ground to stand on, never a
# height-0 column with nothing to walk on); AMPLITUDE is how many extra
# layers the tallest hills add on top of that.
TERRAIN_BASE_HEIGHT = 3
TERRAIN_AMPLITUDE = 6
TERRAIN_NOISE_SCALE = 24.0   # cells per noise lattice point -- larger = broader hills


def terrain_height(seed, x, y):
    """How many layers tall the generated column at (x, y) is, for `seed`.
    Pure function of its inputs -- the same (seed, x, y) always yields the
    same height, on this target, forever (the property the whole "don't
    need to store unmodified chunks" design depends on)."""
    n = _value_noise(seed, x, y, TERRAIN_NOISE_SCALE)
    return TERRAIN_BASE_HEIGHT + int(n * TERRAIN_AMPLITUDE)


def generate_chunk(room, chunk_x, chunk_y):
    """Deterministically fill chunk (chunk_x, chunk_y) from the room's
    seed, if it has one and this chunk has no content yet (generated
    already, or touched/loaded) -- a no-op otherwise, so this is always
    safe to call speculatively (see ensure_chunks_loaded) without risking
    overwriting a player's edits or redoing work.

    Each column gets a simple two-block-type stack (grass on top, dirt
    below) up to terrain_height -- "the ground undulates and has variety,"
    this plan's own explicit bar for a first cut, not villages."""
    st = block_world_state(room)
    seed = st.get("seed")
    if seed is None:
        return
    key = (chunk_x, chunk_y)
    if key in st["chunks"]:
        return
    chunk = {}
    for lx in range(CHUNK_SIZE):
        for ly in range(CHUNK_SIZE):
            x, y = chunk_x * CHUNK_SIZE + lx, chunk_y * CHUNK_SIZE + ly
            height = terrain_height(seed, x, y)
            for z in range(height):
                block_type = "grass" if z == height - 1 else "dirt"
                chunk[_key(x, y, z)] = block_type
    st["chunks"][key] = chunk
    # A freshly-generated chunk is NOT touched -- it must stay reproducible
    # (and therefore unsaved) until a player actually edits it.
    st["_chunk_columns"].pop(key, None)
    st["_merged_columns"] = None


def ensure_chunks_loaded(room, center_x, center_y, radius_cells):
    """Generate every chunk within radius_cells of world position
    (center_x, center_y) that isn't already loaded. A no-op (cheaply --
    generate_chunk's own guard makes an already-loaded chunk free to
    re-request) if the room has no seed. Call once per frame from the
    render path with the camera's own position and render distance, so
    a chunk is generated before the camera reaches the edge of what's
    already there."""
    if block_world_state(room).get("seed") is None:
        return
    cx0, cy0 = _chunk_key(int(center_x - radius_cells), int(center_y - radius_cells))
    cx1, cy1 = _chunk_key(int(center_x + radius_cells), int(center_y + radius_cells))
    for cx in range(cx0, cx1 + 1):
        for cy in range(cy0, cy1 + 1):
            generate_chunk(room, cx, cy)


def unload_distant_chunks(room, center_x, center_y, keep_radius_cells):
    """Evict any GENERATED-BUT-UNTOUCHED chunk more than keep_radius_cells
    (in world cells, not chunks) from (center_x, center_y) -- bounds the
    resident memory of an otherwise-unbounded generated world. Touched
    chunks are NEVER evicted: an evicted touched chunk would look
    "ungenerated" to generate_chunk's presence check and get silently
    overwritten by fresh generation on the next visit, discarding whatever
    was edited there. Call this less often than ensure_chunks_loaded (it's
    a cleanup pass, not per-frame-critical) with a radius comfortably
    larger than ensure_chunks_loaded's, or the two would fight -- generate
    just after evicting the same chunk next frame."""
    st = _peek_state(room)
    if st is None or st.get("seed") is None:
        return
    keep_radius_chunks = keep_radius_cells / CHUNK_SIZE + 1
    center_cx, center_cy = _chunk_key(int(center_x), int(center_y))
    touched = st.get("_touched_chunks", set())
    to_remove = [
        ck for ck in st["chunks"]
        if ck not in touched
        and (abs(ck[0] - center_cx) > keep_radius_chunks
             or abs(ck[1] - center_cy) > keep_radius_chunks)
    ]
    for ck in to_remove:
        del st["chunks"][ck]
        st["_chunk_columns"].pop(ck, None)
    if to_remove:
        st["_merged_columns"] = None


def to_touched_block_list(room):
    """Like to_block_list, but only chunks with at least one real edit
    (see _fresh's docstring) -- what a generation-aware world save should
    persist. For a room with no seed, every loaded chunk is touched (see
    load_block_list), so this is equivalent to to_block_list.

    Saves a touched chunk's FULL current content, not a true cell-level
    diff against what generate_chunk would produce fresh -- a deliberate
    simplification (a true diff would also need a way to represent "this
    generated cell was removed," which to_block_list's {"x","y","z","type"}
    shape has no sentinel for). This still solves the actual scalability
    problem infinite terrain needs solved: file size is bounded by (touched
    chunk count x chunk volume), not by how much of the world has been
    explored -- a chunk is at most CHUNK_SIZE^2 columns, so even a handful
    of fully-saved touched chunks stays small. Revisit only if a real
    profiled world shows this mattering in practice."""
    st = _peek_state(room)
    if st is None:
        return []
    out = []
    for ck in st.get("_touched_chunks", set()):
        chunk = st["chunks"].get(ck, {})
        for key, block_type in chunk.items():
            x, y, z = (int(part) for part in key.split(","))
            out.append({"x": x, "y": y, "z": z, "type": block_type})
    return out


def load_world_state(room, seed, touched_block_list):
    """Restore a room's seed plus its touched (player-edited) chunks.
    Generated-but-never-touched chunks are deliberately NOT restored --
    they'll regenerate identically on demand (ensure_chunks_loaded /
    generate_chunk) from (seed, chunk_coords), since by definition nothing
    about them was ever edited."""
    load_block_list(room, touched_block_list)   # populates chunks + touched set
    block_world_state(room)["seed"] = seed
