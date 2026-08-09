"""Asset usage tracking — DEFERRED_ITEMS_PLAN.md item 10 (Asset Manager),
Tier 1. See docs/ASSET_MANAGER_PLAN.md for the full scoping.

Finds every place a named asset (sprite/sound/background/object/room) is
referenced across a project: typed action parameters, collision-event
targets, room instances/backgrounds/tiles, and object sprite/parent
fields. The shared detection engine both "usage tracking" and future
"unused-asset cleanup" work need — see find_unused_assets.

Known limitations, both inherent to static analysis:
- A reference written as a plain string inside execute_code/
  execute_script (e.g. ``self.game_runner.sounds['explosion'].play()``)
  cannot be found this way — only structured action parameters are
  visible. Only static-analysis recall is claimed; this is not a
  guarantee that an asset with zero reported usages is truly
  unreferenced by every code path.
- A room the player starts in but that no action ever explicitly
  navigates TO (e.g. a single-room game, or the first room of a linear
  sequence with no "return to start" action) legitimately has zero
  AssetUsage records — it's real "no explicit reference" and not a bug,
  but callers presenting find_unused_assets()'s room list to a user
  should phrase it as "not explicitly navigated to," not "unused," to
  avoid implying deletion is obviously safe.
"""
from dataclasses import dataclass
from typing import Any, Dict, List, Optional

from events.action_types import get_action_type
from events.plugin_loader import load_all_plugins

# ActionParameter.param_type value -> project.json asset category key.
# "background" has no typed selector in action_types.py (see module
# docstring / docs/ASSET_MANAGER_PLAN.md) so it's handled separately by
# explicit field name, not through this map.
_PARAM_TYPE_TO_CATEGORY = {
    "sprite": "sprites",
    "sound": "sounds",
    "object": "objects",
    "room": "rooms",
}

# Container events store their sub-actions keyed by sub-event name
# (arrow key, literal key name) rather than directly under "actions" —
# mirrors object_events_panel.py's _CONTAINER_EVENT_HINTS keys.
_CONTAINER_EVENTS = ("keyboard", "keyboard_press", "keyboard_release")

# action name -> {param name: asset category} for actions whose asset-
# referencing parameter has no typed param_type to key off of.
_UNTYPED_ASSET_PARAMS = {
    "draw_background": {"background": "backgrounds"},
}


@dataclass
class AssetUsage:
    """One place an asset is referenced.

    kind: 'action_param' | 'collision_target' | 'room_instance' |
          'room_background' | 'room_tile' | 'object_sprite' |
          'object_parent'
    location: human-readable description, e.g. "obj_pingus / step / play_sound"
    object_name / room_name: whichever container this usage lives in (the
        other is None)
    """
    kind: str
    location: str
    object_name: Optional[str] = None
    room_name: Optional[str] = None


def find_asset_usages(project_data: Dict[str, Any], asset_type: str,
                       asset_name: str) -> List[AssetUsage]:
    """Every AssetUsage referencing (asset_type, asset_name).

    asset_type is the plural project.json category key (e.g. "sprites",
    "objects"), matching how project_data["assets"] is keyed.
    """
    # Plugin actions (play_sound, and anything else in plugins/ or
    # extensions/) only appear in ACTION_TYPES after this runs — landmine
    # documented in CLAUDE.md ("get_action_type('play_sound') returning
    # None in CLI/test imports is expected, not a bug"). Without it, every
    # plugin action's typed sprite/sound/object/room params are invisible
    # here, producing false "unused" positives for assets a project
    # actively uses. load_all_plugins() is documented safe/cheap to call
    # repeatedly (idempotent per process).
    load_all_plugins()

    usages: List[AssetUsage] = []
    assets = (project_data or {}).get("assets") or {}
    objects = assets.get("objects") or {}
    rooms = assets.get("rooms") or {}

    if not isinstance(objects, dict):
        objects = {}
    if not isinstance(rooms, dict):
        rooms = {}

    # --- Object-level fields (sprite, parent) ---
    if asset_type == "sprites":
        for obj_name, obj_data in objects.items():
            if not isinstance(obj_data, dict):
                continue
            if obj_data.get("sprite") == asset_name:
                usages.append(AssetUsage("object_sprite", f"{obj_name} (sprite)",
                                          object_name=obj_name))
    if asset_type == "objects":
        for obj_name, obj_data in objects.items():
            if not isinstance(obj_data, dict):
                continue
            if obj_data.get("parent") == asset_name:
                usages.append(AssetUsage("object_parent", f"{obj_name} (parent)",
                                          object_name=obj_name))

    # --- Object events: actions (typed params + untyped special-cases) and
    #     collision target_object ---
    for obj_name, obj_data in objects.items():
        if not isinstance(obj_data, dict):
            continue
        events = obj_data.get("events") or {}
        if not isinstance(events, dict):
            continue

        def visit_action(event_name, action, _obj_name=obj_name):
            action_name = action.get("action")
            params = action.get("parameters") if isinstance(action.get("parameters"), dict) else {}

            category = _UNTYPED_ASSET_PARAMS.get(action_name, {})
            for param_name, param_category in category.items():
                if param_category == asset_type and params.get(param_name) == asset_name:
                    usages.append(AssetUsage(
                        "action_param", f"{_obj_name} / {event_name} / {action_name}",
                        object_name=_obj_name))

            action_type = get_action_type(action_name) if action_name else None
            if action_type:
                for p in action_type.parameters:
                    param_category = _PARAM_TYPE_TO_CATEGORY.get(p.param_type)
                    if param_category == asset_type and params.get(p.name) == asset_name:
                        usages.append(AssetUsage(
                            "action_param", f"{_obj_name} / {event_name} / {action_name}",
                            object_name=_obj_name))

        def walk_actions(event_name, actions):
            if not isinstance(actions, list):
                return
            for action in actions:
                if not isinstance(action, dict):
                    continue
                visit_action(event_name, action)
                params = action.get("parameters") if isinstance(action.get("parameters"), dict) else {}
                for key in ("then_actions", "else_actions", "sub_actions", "actions"):
                    if key in params:
                        walk_actions(event_name, params[key])
                    if key in action:
                        walk_actions(event_name, action[key])

        for event_name, event_data in events.items():
            if not isinstance(event_data, dict):
                continue
            if event_name in _CONTAINER_EVENTS:
                for sub_key, sub_data in event_data.items():
                    if sub_key == "actions" or not isinstance(sub_data, dict):
                        continue
                    walk_actions(f"{event_name}:{sub_key}", sub_data.get("actions"))
                continue
            if asset_type == "objects":
                target_object = event_data.get("target_object")
                if target_object == asset_name:
                    usages.append(AssetUsage(
                        "collision_target", f"{obj_name} / {event_name} (collision target)",
                        object_name=obj_name))
            walk_actions(event_name, event_data.get("actions"))

    # --- Room-level fields (background_image, tiles, instances) ---
    for room_name, room_data in rooms.items():
        if not isinstance(room_data, dict):
            continue
        if asset_type == "backgrounds" and room_data.get("background_image") == asset_name:
            usages.append(AssetUsage("room_background", f"{room_name} (room background)",
                                      room_name=room_name))
        if asset_type == "backgrounds":
            for tile in room_data.get("tiles") or []:
                if isinstance(tile, dict) and tile.get("background_name") == asset_name:
                    usages.append(AssetUsage("room_tile", f"{room_name} (tile)",
                                              room_name=room_name))
                    break  # one usage record per room is enough for tiles
        if asset_type == "objects":
            for instance in room_data.get("instances") or []:
                if isinstance(instance, dict) and instance.get("object_name") == asset_name:
                    usages.append(AssetUsage(
                        "room_instance", f"{room_name} (instance)", room_name=room_name))
                    break  # one usage record per room is enough for instances

    return usages


def find_unused_assets(project_data: Dict[str, Any]) -> Dict[str, List[str]]:
    """Every asset with zero AssetUsage records, grouped by category.

    Only categories find_asset_usages actually tracks references for
    (sprites/sounds/backgrounds/objects/rooms) are checked; scripts/fonts/
    data have no reference concept here and are omitted."""
    assets = (project_data or {}).get("assets") or {}
    unused: Dict[str, List[str]] = {}
    for category in ("sprites", "sounds", "backgrounds", "objects", "rooms"):
        names = assets.get(category) or {}
        if not isinstance(names, dict):
            continue
        category_unused = [
            name for name in names
            if not find_asset_usages(project_data, category, name)
        ]
        if category_unused:
            unused[category] = sorted(category_unused)
    return unused
