#!/usr/bin/env python3
"""Per-room voxel world data model, namespaced into ``room.extension_state``.

Mirrors extensions/raycast_2_5d/state.py's pattern: nothing voxel-specific
touches core's GameRoom. A room's block layout lives under
``room.extension_state["block_world"]`` -- created on first access via
``block_world_state(room)`` (get-or-create) or read without creating via
``peek_blocks(room)`` (needed once a room renderer exists in Phase 2, so it
doesn't stamp block-world state onto every room in the game).

Storage is a **sparse dict**, keyed by an ``"x,y,z"`` string, value the block
type id string. Absence of a key means air; there is no stored "air" block.
This keeps a mostly-empty world cheap -- the same reasoning
docs/VOXEL_WORLD_PLAN.md gives for not using a dense 3D array.

``to_block_list`` / ``load_block_list`` round-trip the sparse dict to/from a
flat list of ``{"x", "y", "z", "type"}`` dicts -- the shape convention room
JSON already uses for tile layers (see the "tiles" key rooms save under
today) -- so a future world-authoring path (a generator script, an action
that seeds a room from a bundled data file) has an established shape to
target rather than inventing its own. Nothing in this module reads or writes
room JSON directly: extension_state is transient runtime state, same as
raycast's camera config (rebuilt by an action each run, never persisted by
core -- see extensions/raycast_2_5d/state.py's own docstring). Wiring an
actual load path is Phase 3+.
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


def _fresh():
    # "_columns" is a DERIVED cache (see column_index) -- the leading
    # underscore marks it as not part of the saved world shape, the same way
    # raycast_2_5d's per-room state separates its camera config from the wall
    # -edge caches it derives.
    return {"blocks": {}, "camera": {"enabled": False}, "_columns": None}


def _invalidate_columns(room):
    """Drop the derived per-column cache. Called by every mutator here.

    Code that reaches around these helpers and edits ``state["blocks"]``
    directly MUST call this too, or the renderer keeps drawing the old world.
    """
    es = getattr(room, "extension_state", None)
    st = es.get(BLOCK_WORLD_KEY) if es else None
    if st is not None:
        st["_columns"] = None


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
    """This room's block dict if it already has block-world state, else None.

    Does NOT create state -- once a room renderer exists (Phase 2) it will
    run for every room, block-world or not, and must not stamp block-world
    state onto rooms that never used it. Mirrors
    extensions.raycast_2_5d.state.peek_camera."""
    es = getattr(room, "extension_state", None)
    st = es.get(BLOCK_WORLD_KEY) if es else None
    return st["blocks"] if st else None


def peek_camera(room):
    """This room's camera config if it already has block-world state, else
    None. Does NOT create state -- the room-renderer hook runs for EVERY
    room (block-world or not) and must not stamp state onto rooms that
    never enabled the view. Mirrors extensions.raycast_2_5d.state.peek_camera."""
    es = getattr(room, "extension_state", None)
    st = es.get(BLOCK_WORLD_KEY) if es else None
    return st["camera"] if st else None


def get_block(room, x, y, z):
    """The block type id at (x, y, z), or None for air. Does not create
    state -- a room nobody has touched yet is simply all air."""
    blocks = peek_blocks(room)
    if blocks is None:
        return None
    return blocks.get(_key(x, y, z))


def set_block(room, x, y, z, block_type):
    """Place a block, creating world state on first use. block_type must be a
    key in BLOCK_TYPES -- validate before calling if it came from untrusted
    data."""
    if block_type not in BLOCK_TYPES:
        raise KeyError(block_type)
    block_world_state(room)["blocks"][_key(x, y, z)] = block_type
    _invalidate_columns(room)


def remove_block(room, x, y, z):
    """Break/clear the block at (x, y, z). A no-op if it's already air or the
    room has no world state yet."""
    blocks = peek_blocks(room)
    if blocks is not None:
        blocks.pop(_key(x, y, z), None)
        _invalidate_columns(room)


def iter_blocks(room):
    """Yield (x, y, z, block_type) for every placed block in the room, in no
    particular order. Empty for an all-air / not-yet-touched room."""
    blocks = peek_blocks(room)
    if not blocks:
        return
    for key, block_type in blocks.items():
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
    instead."""
    blocks = {}
    for entry in block_list:
        block_type = entry["type"]
        if block_type not in BLOCK_TYPES:
            raise KeyError(block_type)
        blocks[_key(entry["x"], entry["y"], entry["z"])] = block_type
    block_world_state(room)["blocks"] = blocks
    _invalidate_columns(room)


def column_index(room):
    """``{(x, y): [(z, block_type), ...]}`` -- every non-empty column of the
    world, each sorted lowest z first. Built once and cached until a mutator
    calls _invalidate_columns.

    Phase 2b's renderer needs the whole vertical STACK at each cell it steps
    into, and the backing store is keyed by a formatted ``"x,y,z"`` string.
    Probing that per candidate layer means a string format per lookup, which
    at 320 columns x 24 cells x a handful of layers is tens of thousands of
    formats per frame -- comfortably the most expensive thing in the render
    path. One tuple-keyed dict lookup per cell instead, rebuilt only when the
    world actually changes, which for a built world is approximately never.
    """
    st = block_world_state(room)
    index = st.get("_columns")
    if index is None:
        index = {}
        for x, y, z, block_type in iter_blocks(room):
            index.setdefault((x, y), []).append((z, block_type))
        for column in index.values():
            column.sort()
        st["_columns"] = index
    return index


def stack_top(room, x, y):
    """The z of the highest block at (x, y), or None for an empty column.

    The heightmap query Phase 2b's "stand on top of things" needs, and Phase
    4's collision will want the same answer."""
    column = column_index(room).get((x, y))
    return column[-1][0] if column else None
