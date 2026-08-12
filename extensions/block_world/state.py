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
    "leaves": {"all": "default_leaves.png", "solid": True},
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
    "obsidian": {"all": "default_obsidian.png", "solid": True},
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


def block_face_textures(block_type):
    """Resolve a block type id to its {"top", "bottom", "side"} texture map
    of absolute file paths.

    Raises KeyError for an unknown block_type -- callers are expected to
    validate against BLOCK_TYPES themselves when the id comes from untrusted
    data (e.g. a loaded world file)."""
    faces = BLOCK_TYPES[block_type]
    if "all" in faces:
        path = texture_path(faces["all"])
        return {"top": path, "bottom": path, "side": path}
    return {
        "top": texture_path(faces["top"]),
        "bottom": texture_path(faces["bottom"]),
        "side": texture_path(faces["side"]),
    }


def _key(x, y, z):
    return "%d,%d,%d" % (x, y, z)


def _fresh():
    return {"blocks": {}}


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


def remove_block(room, x, y, z):
    """Break/clear the block at (x, y, z). A no-op if it's already air or the
    room has no world state yet."""
    blocks = peek_blocks(room)
    if blocks is not None:
        blocks.pop(_key(x, y, z), None)


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
