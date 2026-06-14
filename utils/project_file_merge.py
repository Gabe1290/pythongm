#!/usr/bin/env python3
"""
Shared kernel for merging split project files into in-memory asset dicts.

Projects store room/object metadata in project.json but keep the heavy
payloads (room instances, object events) in separate
`rooms/<name>.json` / `objects/<name>.json` files. Three loaders read those
back: `core.project_manager` (editor, authoritative — handles string refs,
OrderedDict ordering, marker cleanup), `runtime.game_runner` (lean read-only
runtime) and `export.base_exporter` (export). Their *orchestration* legitimately
differs (signatures, data source, logging, file-open) and is left intact.

What was byte-identical in all three — and the real drift hazard — is the
merge itself: the fixed list of room/object property keys copied from the
file. If a key were added to one copy and not the others, projects would
silently lose data on load. That kernel is single-sourced here as pure,
side-effect-free functions; each loader keeps its own logging/orchestration.
"""

# Room properties copied from rooms/<name>.json (besides 'instances').
# The GMK converter (and editor saves) write a room's heavy payload — tile
# layers, the 8 parallax background layers, views, parallax scroll/stretch and
# creation code — ONLY to rooms/<name>.json, with a metadata-only project.json
# entry. Every key the runtime/editor actually reads (see GameRoom.__init__)
# must be whitelisted here, or it never reaches memory on load AND is erased
# from the room file on the next save (the merged in-memory dict is what gets
# rewritten). Keep this in sync with the room_data.get(...) reads in GameRoom.
_ROOM_FILE_KEYS = (
    'width', 'height', 'background_color', 'background_image',
    'tile_horizontal', 'tile_vertical',
    'bg_hspeed', 'bg_vspeed', 'bg_stretch',
    'backgrounds', 'tiles',
    'views_enabled', 'enable_views', 'views',
    'persistent', 'creation_code',
)

# Object properties copied from objects/<name>.json.
_OBJECT_FILE_KEYS = (
    'events', 'sprite', 'visible', 'solid', 'persistent',
    'depth', 'parent', 'mask', 'imported', 'created', 'modified',
    # 'remember_destroyed' is a child-only opt-in flag every object file may
    # carry; omitting it dropped the flag on load and reverted it on save (L6).
    'remember_destroyed',
)

# Sprite properties copied from sprites/<name>.json. Must include every key a
# sprite file actually carries, or a hand/external edit to the file is ignored
# at load and reverted on the next save (the merged in-memory copy is rewritten)
# — 'precise', 'frame_width', 'frame_height', 'animation_type' and 'speed' were
# missing (L6).
_SPRITE_FILE_KEYS = (
    'frames', 'width', 'height', 'origin_x', 'origin_y', 'collision_mask',
    'bbox_left', 'bbox_right', 'bbox_top', 'bbox_bottom',
    'precise', 'frame_width', 'frame_height', 'animation_type', 'speed',
    'imported', 'created', 'modified', 'file_path',
)


def merge_sprite_file(sprite_data: dict, file_sprite_data: dict) -> None:
    """Merge a sprites/<name>.json payload into ``sprite_data`` in place.

    File properties take precedence, mirroring the room/object kernels.
    """
    for key in _SPRITE_FILE_KEYS:
        if key in file_sprite_data:
            sprite_data[key] = file_sprite_data[key]


def merge_room_file(room_data: dict, file_room_data: dict):
    """Merge a rooms/<name>.json payload into ``room_data`` in place.

    File ``instances`` take precedence, then the fixed room-property keys are
    copied over when present. Returns the merged instance count when the file
    carried ``instances`` (so the caller can log it), else ``None`` — exactly
    mirroring the original ``if 'instances' in file_room_data:`` guard.
    """
    instance_count = None
    if 'instances' in file_room_data:
        room_data['instances'] = file_room_data['instances']
        instance_count = len(room_data['instances'])
    for key in _ROOM_FILE_KEYS:
        if key in file_room_data:
            room_data[key] = file_room_data[key]
    return instance_count


def merge_object_file(object_data: dict, file_object_data: dict) -> int:
    """Merge an objects/<name>.json payload into ``object_data`` in place.

    File properties take precedence. Returns the event count
    (``len(file_object_data.get('events', {}))``) for the caller to log,
    matching the original unconditional ``event_count`` computation.
    """
    for key in _OBJECT_FILE_KEYS:
        if key in file_object_data:
            object_data[key] = file_object_data[key]
    return len(file_object_data.get('events', {}))
