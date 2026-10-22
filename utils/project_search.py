"""Project-wide search — TODO.md's "project-wide search (asset names,
identifiers)" item, logged as a deliberately separate, larger follow-up
when Find/Replace (a single text editor's own search) shipped
2026-10-18.

Finds every place a search string appears across a project: asset names
in every category, object fields (sprite/parent/mask), every action's
name and parameter values (including inside nested then_actions/
else_actions/sub_actions and the keyboard/keyboard_press/
keyboard_release container events — the exact same project.json shapes
utils/asset_usage.py already has to handle), room fields (background
image, instance object names, tile background names), and script asset
code (line by line, so a match carries a line number).

Deliberately a separate, self-contained walker rather than sharing code
with utils/asset_usage.py: that module answers a narrower question (does
parameter X of type Y equal exactly this one asset name?), typed by
ActionParameter.param_type; this one is a general substring search over
every string value regardless of type. The two walk the same project
shape but for different enough purposes that forcing them through one
abstraction risked destabilizing asset_usage.py's own existing,
already-tested behaviour for a search feature that doesn't need it.

Known limitation, inherent to static analysis (the same one
asset_usage.py documents): a match written as a literal string inside
execute_code/execute_script's own Python code IS found (script/code text
is searched directly), but a reference built up at runtime
(string concatenation, an f-string, a name read from a variable) is not
and cannot be — this is a project.json text search, not an interpreter.
"""
from dataclasses import dataclass
from typing import Any, Dict, List, Optional

# Container events store their sub-actions keyed by sub-event name (an
# arrow key, a literal key name) rather than directly under "actions" --
# mirrors object_events_panel.py's _CONTAINER_EVENT_HINTS keys and
# utils/asset_usage.py's own _CONTAINER_EVENTS.
_CONTAINER_EVENTS = ("keyboard", "keyboard_press", "keyboard_release")

# Nested action-list keys a single action's own "parameters" dict (or,
# for a couple of legacy/Blockly shapes, the action dict itself) may
# carry — walked recursively so a match inside an if_condition's
# then/else branch, or a custom block's expanded body, is still found.
_NESTED_ACTION_LIST_KEYS = ("then_actions", "else_actions", "sub_actions", "actions")

# Object-level fields (not inside an event) worth searching as plain
# asset-reference text.
_OBJECT_SEARCHABLE_FIELDS = ("sprite", "parent", "mask")


@dataclass
class SearchResult:
    """One place `query` was found.

    kind: 'asset_name' | 'object_field' | 'action_name' | 'action_param'
          | 'room_field' | 'script_code'
    category: the project.json asset category this result belongs to
        (e.g. "objects", "rooms", "scripts") -- plural, matching
        project_data["assets"] and widgets/asset_tree/asset_utils.py's
        ASSET_TYPE_REGISTRY, so a caller can open the right editor
        directly from a result with no extra translation.
    name: the asset's own name within that category (the object/room/
        script/sprite/... this result belongs to).
    location: human-readable description of exactly where the match is,
        e.g. "obj_player / step / set_hspeed (value)" or
        "calc_damage (line 12)".
    matched_text: the actual string value (or source line, for script
        code) that matched -- shown as context in a results list.
    """
    kind: str
    category: str
    name: str
    location: str
    matched_text: str


def _matches(value: Any, query: str, case_sensitive: bool) -> bool:
    if not isinstance(value, str) or not value:
        return False
    if case_sensitive:
        return query in value
    return query.lower() in value.lower()


def _walk_param_values(params: Dict[str, Any], query: str, case_sensitive: bool):
    """Every (key, matching string) pair in a flat parameters dict --
    nested action-list keys are deliberately excluded here (the action
    walker below recurses into those separately, as whole actions, not
    as plain string values)."""
    matches = []
    if not isinstance(params, dict):
        return matches
    for key, value in params.items():
        if key in _NESTED_ACTION_LIST_KEYS:
            continue
        if isinstance(value, str):
            if _matches(value, query, case_sensitive):
                matches.append((key, value))
        elif isinstance(value, list):
            for item in value:
                if isinstance(item, str) and _matches(item, query, case_sensitive):
                    matches.append((key, item))
    return matches


def _search_object_actions(obj_name: str, events: Dict[str, Any], query: str,
                            case_sensitive: bool, results: List[SearchResult]):
    def visit_action(event_name, action):
        if not isinstance(action, dict):
            return
        action_name = action.get("action", "") or ""
        params = action.get("parameters") if isinstance(action.get("parameters"), dict) else {}

        if _matches(action_name, query, case_sensitive):
            results.append(SearchResult(
                "action_name", "objects", obj_name,
                f"{obj_name} / {event_name} / {action_name}", action_name))

        for key, value in _walk_param_values(params, query, case_sensitive):
            results.append(SearchResult(
                "action_param", "objects", obj_name,
                f"{obj_name} / {event_name} / {action_name} ({key})", value))

    def walk_actions(event_name, actions):
        if not isinstance(actions, list):
            return
        for action in actions:
            if not isinstance(action, dict):
                continue
            visit_action(event_name, action)
            params = action.get("parameters") if isinstance(action.get("parameters"), dict) else {}
            for key in _NESTED_ACTION_LIST_KEYS:
                if key in params:
                    walk_actions(event_name, params[key])
                if key in action:
                    walk_actions(event_name, action[key])

    for event_name, event_data in (events or {}).items():
        if not isinstance(event_data, dict):
            continue
        if event_name in _CONTAINER_EVENTS:
            for sub_key, sub_data in event_data.items():
                if sub_key == "actions" or not isinstance(sub_data, dict):
                    continue
                walk_actions(f"{event_name}:{sub_key}", sub_data.get("actions"))
            continue
        walk_actions(event_name, event_data.get("actions"))


def search_project(project_data: Dict[str, Any], query: str,
                    case_sensitive: bool = False) -> List[SearchResult]:
    """Every SearchResult matching `query` anywhere in the project.

    Returns [] for an empty/whitespace-only query rather than every
    string in the project (an empty substring "matches" everything in
    Python, which would be useless noise, not a real search result)."""
    query = (query or "").strip()
    if not query:
        return []

    results: List[SearchResult] = []
    assets = (project_data or {}).get("assets") or {}

    # 1. Asset names, every category.
    for category, names in assets.items():
        if not isinstance(names, dict):
            continue
        for name in names:
            if _matches(name, query, case_sensitive):
                results.append(SearchResult(
                    "asset_name", category, name, f"{category} / {name}", name))

    objects = assets.get("objects") or {}
    if not isinstance(objects, dict):
        objects = {}

    # 2. Object-level fields.
    for obj_name, obj_data in objects.items():
        if not isinstance(obj_data, dict):
            continue
        for field in _OBJECT_SEARCHABLE_FIELDS:
            value = obj_data.get(field)
            if _matches(value, query, case_sensitive):
                results.append(SearchResult(
                    "object_field", "objects", obj_name,
                    f"{obj_name} ({field})", value))

        # 3. Every action in every event (including collision targets,
        # read directly here rather than via visit_action since they're
        # not actions at all).
        events = obj_data.get("events") or {}
        if isinstance(events, dict):
            for event_name, event_data in events.items():
                if isinstance(event_data, dict):
                    target = event_data.get("target_object")
                    if _matches(target, query, case_sensitive):
                        results.append(SearchResult(
                            "object_field", "objects", obj_name,
                            f"{obj_name} / {event_name} (collision target)", target))
            _search_object_actions(obj_name, events, query, case_sensitive, results)

    # 4. Room fields.
    rooms = assets.get("rooms") or {}
    if isinstance(rooms, dict):
        for room_name, room_data in rooms.items():
            if not isinstance(room_data, dict):
                continue
            bg = room_data.get("background_image")
            if _matches(bg, query, case_sensitive):
                results.append(SearchResult(
                    "room_field", "rooms", room_name,
                    f"{room_name} (background)", bg))
            for instance in room_data.get("instances") or []:
                if not isinstance(instance, dict):
                    continue
                obj_name = instance.get("object_name")
                if _matches(obj_name, query, case_sensitive):
                    results.append(SearchResult(
                        "room_field", "rooms", room_name,
                        f"{room_name} (instance of {obj_name})", obj_name))
            for tile in room_data.get("tiles") or []:
                if not isinstance(tile, dict):
                    continue
                bg_name = tile.get("background_name")
                if _matches(bg_name, query, case_sensitive):
                    results.append(SearchResult(
                        "room_field", "rooms", room_name,
                        f"{room_name} (tile)", bg_name))

    # 5. Script code, line by line (so a match carries a line number).
    scripts = assets.get("scripts") or {}
    if isinstance(scripts, dict):
        for script_name, script_data in scripts.items():
            if not isinstance(script_data, dict):
                continue
            code = script_data.get("code") or ""
            if not isinstance(code, str):
                continue
            for i, line in enumerate(code.splitlines(), start=1):
                if _matches(line, query, case_sensitive):
                    results.append(SearchResult(
                        "script_code", "scripts", script_name,
                        f"{script_name} (line {i})", line.strip()))

    return results
