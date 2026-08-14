#!/usr/bin/env python3
"""Export-time DATA collection for the Block World extension (Phase 6,
Units 8-9 of docs/VOXEL_WORLD_PLAN.md).

Desktop's ``load_block_world`` action (handlers.py) opens a project-relative
JSON file straight off disk at ``game_start``. A browser export has no
filesystem, and a Kivy export's runtime has no live copy of ``project.json``
to read a path out of (see export_kivy.py's own docstring) -- both need the
referenced world data EMBEDDED at export time instead. This module is the
generic hook ``html5_exporter.py``/``kivy_exporter.py`` call for every
enabled extension (see their own ``_collect_extension_data`` docstrings);
it does not import pygame or anything export-target-specific.

``collect_export_data`` walks every object's events for ``load_block_world``
actions, reads each referenced file relative to ``project_path``, and
returns ``{"block_world_files": {data_file: block_list}}`` -- exactly the
``to_block_list`` shape ``state.load_block_list`` already expects, so both
export ports can hand the result straight to their own load_block_list port
with no reshaping.
"""
import json
from pathlib import Path


def _iter_action_lists(events):
    """Yield every action LIST reachable from an object's ``events`` dict --
    top-level event actions, and each keyed sub-event's (keyboard/
    keyboard_press, one list per key) actions."""
    if not isinstance(events, dict):
        return
    for value in events.values():
        if not isinstance(value, dict):
            continue
        if "actions" in value:
            yield value["actions"]
        else:
            # A keyed sub-event dict (keyboard/keyboard_press: {key: {...}}).
            for sub in value.values():
                if isinstance(sub, dict) and "actions" in sub:
                    yield sub["actions"]


def _iter_actions(action_list):
    """Yield every action dict in ``action_list``, recursing into
    if_condition's then_actions/else_actions -- the only nesting shape this
    project's action model has (see events/action_types.py)."""
    if not isinstance(action_list, list):
        return
    for action in action_list:
        if not isinstance(action, dict):
            continue
        yield action
        params = action.get("parameters", {})
        if isinstance(params, dict):
            for key in ("then_actions", "else_actions"):
                yield from _iter_actions(params.get(key, []))


def _load_block_world_data_files(project_data):
    """Every distinct ``data_file`` a ``load_block_world`` action in this
    project references, across every object."""
    files = set()
    objects = project_data.get("assets", {}).get("objects", {})
    for obj_data in objects.values():
        if not isinstance(obj_data, dict):
            continue
        for action_list in _iter_action_lists(obj_data.get("events", {})):
            for action in _iter_actions(action_list):
                action_type = action.get("action_type", action.get("action", ""))
                if action_type != "load_block_world":
                    continue
                data_file = str(action.get("parameters", {}).get("data_file", ""))
                if data_file:
                    files.add(data_file)
    return files


def collect_export_data(project_path, project_data):
    """Read every referenced block-world data file and return it embeddable.

    Silently skips a missing/unreadable/malformed file (mirrors
    handlers.execute_load_block_world_action's own no-op-on-bad-input
    behaviour) rather than failing the whole export over one bad path.
    """
    result = {}
    for data_file in _load_block_world_data_files(project_data):
        try:
            path = Path(project_path) / data_file
            with open(path, "r", encoding="utf-8") as f:
                block_list = json.load(f)
            if isinstance(block_list, list):
                result[data_file] = block_list
        except (OSError, ValueError):
            continue
    return {"block_world_files": result}
