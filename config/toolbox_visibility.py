#!/usr/bin/env python3
"""Single resolver for "is this action visible in the Blockly toolbox /
action-list editor right now" (docs/BLOCKLY_TOOLBOX_GATING_PLAN.md, Unit 1).

Both editors currently decide this themselves, differently and both wrong:
the Blockly toolbox (``editors/object_editor/blockly/blockly_workspace.html``
``reconfigureToolbox``) appends any auto-generated category whose name
doesn't match a hardcoded one with **no preset check at all**, and the
action-list editor's ``get_actions_by_category`` keeps any action with no
``ACTION_TO_BLOCKLY_MAP`` entry "for backward compatibility" -- the same bug
by a different route. This module is the one place that decides, so later
units can delete both bypasses and call this instead.

Pure Python, no Qt -- importable from a JS-generation step, a test, or a
headless script with no display.
"""
from typing import Optional, Set

from events.action_types import ACTION_TYPES, ACTION_TO_BLOCKLY_MAP

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
    ``config`` (a :class:`~config.blockly_config.BlocklyConfig`) in the
    context of ``project_data`` (``None`` for "no project open yet" --
    extension actions are then never active, same as an empty project).

    Rule, applied once per action in ``ACTION_TYPES``:

    - owned by an extension (``plugin_loader.extension_for_action``) → shown
      iff that extension is in :func:`active_extensions` for this project.
      The preset is NOT consulted for these -- decision 2026-09-30, "active
      overrides the preset" -- so an active extension's actions show in
      beginner too.
    - else in the Audio category → always shown (existing deliberate
      decision, CLAUDE.md "Audio actions are plugin-owned").
    - else (a core action, hand-written block or auto-generated) → shown iff
      its block type -- ``ACTION_TO_BLOCKLY_MAP[name]`` for a hand-written
      block, or ``name`` itself for an auto-generated one with no entry in
      that map -- is in ``config.enabled_blocks``.
    """
    from events.plugin_loader import extension_for_action

    active = active_extensions(project_data)
    enabled_blocks = config.enabled_blocks
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
        block_type = ACTION_TO_BLOCKLY_MAP.get(name, name)
        if block_type in enabled_blocks:
            result.add(name)
    return result
