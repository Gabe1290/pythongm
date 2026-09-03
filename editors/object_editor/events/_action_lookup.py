#!/usr/bin/env python3
"""Action-name lookup with legacy-alias fallback.

``get_action_type`` here wraps ``events.action_types.get_action_type`` with an
``ACTION_ALIASES`` fallback for a handful of legacy/alternate action names
that never got their own ``ACTION_TYPES`` entry. Kept as the object editor's
own concern (see ``docs/POST_1_0_REFACTOR.md`` companion-cleanup item 1: this
is NOT the same map as ``ActionExecutor.ACTION_ALIASES`` — different direction,
different purpose).

Tests that need to stub action resolution should patch
``editors.object_editor.events._action_lookup.get_action_type``.
"""

from events.action_types import get_action_type as _get_action_type

# Action name aliases (alternative names -> canonical names)
# Map legacy/alternate action names to their canonical ACTION_TYPES entries.
# Only needed for names NOT already in ACTION_TYPES.
ACTION_ALIASES = {
    'goto_room': 'room_goto',
    'if_collision': 'if_collision_at',
    'end_game': 'game_end',
    'restart_game': 'game_restart',
    'else_block': 'else_action',
    'display_message': 'show_message',
    'message': 'show_message',
    'change_sprite': 'set_sprite',
}


def get_action_type(action_name: str):
    """Get action type with alias support"""
    # Try the original name first
    result = _get_action_type(action_name)
    if result:
        return result

    # Try the alias if available
    if action_name in ACTION_ALIASES:
        return _get_action_type(ACTION_ALIASES[action_name])

    return None
