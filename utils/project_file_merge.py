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
_ROOM_FILE_KEYS = (
    'width', 'height', 'background_color', 'background_image',
    'tile_horizontal', 'tile_vertical',
)

# Object properties copied from objects/<name>.json.
_OBJECT_FILE_KEYS = (
    'events', 'sprite', 'visible', 'solid', 'persistent',
    'depth', 'parent', 'mask', 'imported', 'created', 'modified',
)


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
