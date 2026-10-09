#!/usr/bin/env python3
"""Single resolver for "is this action/event visible in the Blockly toolbox /
action-list editor / add-event menu right now"
(docs/BLOCKLY_TOOLBOX_GATING_PLAN.md, Units 1 and 4).

Every one of these editors decided this themselves, differently and all
wrong, by the same bug in three different places: the Blockly toolbox
(``editors/object_editor/blockly/blockly_workspace.html``
``reconfigureToolbox``) appended any auto-generated category whose name
doesn't match a hardcoded one with **no preset check at all**; the
action-list editor's ``get_actions_by_category`` kept any action with no
``ACTION_TO_BLOCKLY_MAP`` entry "for backward compatibility"; and
``get_available_events`` did the identical thing for events with no
``EVENT_TO_BLOCKLY_MAP`` entry. This module is the one place that decides,
so every caller can delete its own bypass and call this instead.

Pure Python, no Qt -- importable from a JS-generation step, a test, or a
headless script with no display.
"""
from typing import Optional, Set

from events.action_types import ACTION_TYPES, ACTION_TO_BLOCKLY_MAP
from events.event_types import EVENT_TYPES, EVENT_TO_BLOCKLY_MAP

AUDIO_CATEGORY = "Audio"


def active_extensions(project_data: Optional[dict]) -> Set[str]:
    """Folder names of every extension whose actions should be offered in
    *this* project right now.

    A candidate (named in the project's own ``settings.active_extensions``,
    or already used by one of its actions -- decision 2026-09-30: usage
    always counts, so an existing project needs no migration) only counts if
    the extension is also globally enabled; a user switching an extension
    off entirely must still hide it, even for a project that already uses
    it (the existing outer gate, unchanged).
    """
    from events.plugin_loader import is_extension_enabled, required_extensions_for_project

    project_data = project_data or {}
    settings = project_data.get("settings") or {}
    manual = settings.get("active_extensions")
    manual_set = set(manual) if isinstance(manual, (list, set, tuple)) else set()
    used_set = set(required_extensions_for_project(project_data))
    candidates = manual_set | used_set
    return {folder for folder in candidates if is_extension_enabled(folder)}


def visible_actions(config, project_data: Optional[dict] = None) -> Set[str]:
    """Action names that should appear in the toolbox / action picker for
    ``config`` (a :class:`~config.blockly_config.BlocklyConfig`, or ``None``
    for "no preset restriction" -- see below) in the context of
    ``project_data`` (``None`` for "no project open yet" -- extension
    actions are then never active, same as an empty project).

    Rule, applied once per action in ``ACTION_TYPES``:

    - owned by an extension (``plugin_loader.extension_for_action``) → shown
      iff that extension is in :func:`active_extensions` for this project.
      The preset is NOT consulted for these -- decision 2026-09-30, "active
      overrides the preset" -- so an active extension's actions show in
      beginner too, and this check runs even with ``config=None``.
    - else in the Audio category → always shown (existing deliberate
      decision, CLAUDE.md "Audio actions are plugin-owned").
    - else (a core action, hand-written block or auto-generated): with a
      real ``config``, shown iff its block type --
      ``ACTION_TO_BLOCKLY_MAP[name]`` for a hand-written block, or ``name``
      itself for an auto-generated one with no entry in that map -- is in
      ``config.enabled_blocks``. With ``config=None``, always shown --
      Unit 4's action-list editor callers (``action_editor.py``,
      ``conditional_editor.py``) never gated core actions by a preset at
      all, and this keeps that unchanged; they still gain correct
      extension-activation gating, which is independent of a preset.
    """
    from events.plugin_loader import extension_for_action

    active = active_extensions(project_data)
    enabled_blocks = config.enabled_blocks if config is not None else None
    result: Set[str] = set()
    for name, action in ACTION_TYPES.items():
        owner = extension_for_action(name)
        if owner is not None:
            if owner["folder"] in active:
                result.add(name)
            continue
        if getattr(action, "category", None) == AUDIO_CATEGORY:
            result.add(name)
            continue
        if enabled_blocks is None:
            result.add(name)
            continue
        block_type = ACTION_TO_BLOCKLY_MAP.get(name, name)
        if block_type in enabled_blocks:
            result.add(name)
    return result


def visible_events(config, project_data: Optional[dict] = None) -> Set[str]:
    """``visible_actions``'s twin for events -- the same rule, no Audio-style
    always-visible category (events have no equivalent). Added
    docs/BLOCKLY_TOOLBOX_GATING_PLAN.md Unit 4, same session, after
    regenerating the preset wiki docs surfaced that ``get_available_events``
    had the identical "no mapping -> include anyway" bug
    ``get_actions_by_category`` had, just for events: every preset's
    Add-Event menu showed all 12 multiplayer network events unconditionally.

    Extension activation reuses :func:`active_extensions` as-is (computed
    from the project's ACTIONS, via ``required_extensions_for_project`` --
    not extended to also detect event-only usage, since a project using a
    multiplayer extension's events without ever calling one of its actions
    is not a real scenario worth the extra complexity).
    """
    from events.plugin_loader import extension_for_event

    active = active_extensions(project_data)
    enabled_blocks = config.enabled_blocks if config is not None else None
    result: Set[str] = set()
    for name in EVENT_TYPES:
        owner = extension_for_event(name)
        if owner is not None:
            if owner["folder"] in active:
                result.add(name)
            continue
        if enabled_blocks is None:
            result.add(name)
            continue
        block_type = EVENT_TO_BLOCKLY_MAP.get(name, name)
        if block_type in enabled_blocks:
            result.add(name)
    return result


def toolbox_enabled_blocks(config, project_data: Optional[dict] = None) -> Set[str]:
    """The ``enabled_blocks`` list BlocklyWidget sends to the JS toolbox.

    ``config.enabled_blocks`` also carries non-action block types (events,
    value blocks, Thymio's own entries) that ``visible_actions`` has no
    opinion on; those pass through. Every real action is replaced by
    ``visible_actions``' answer -- a plain union could only ever add blocks,
    never hide one it says should be hidden.

    Each visible action is sent under BOTH its hand-written block name
    (``ACTION_TO_BLOCKLY_MAP``) and its own name. The JS toolbox matches an
    auto-generated ``custom_<action>`` block by the action's own name, so a
    mapping whose block name exists nowhere in JS hid the action's only
    block: ``change_instance`` -> ``instance_change`` left the beginner
    preset's Blockly tab without Change Instance, though the action-list
    editor showed it (docs/BLOCKLY_BLOCK_AUDIT_2026-10-08.md B8). Sending
    the action name too can't over-show: only already-visible names are
    added, and an action with a hand-written block has no custom block for
    the extra name to match.
    """
    visible = visible_actions(config, project_data)
    resolved = {ACTION_TO_BLOCKLY_MAP.get(name, name) for name in visible} | set(visible)
    action_block_types = ({ACTION_TO_BLOCKLY_MAP.get(name, name) for name in ACTION_TYPES}
                          | set(ACTION_TYPES))
    non_action_entries = set(config.enabled_blocks) - action_block_types
    return non_action_entries | resolved
