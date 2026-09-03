#!/usr/bin/env python3
"""Backwards-compat shim.

``ObjectEventsPanel`` moved to the ``editors.object_editor.events`` package
(``docs/POST_1_0_REFACTOR.md`` File 1). Import from there in new code:

    from editors.object_editor.events import ObjectEventsPanel

Tests that reach into module internals should patch
``editors.object_editor.events._panel.<name>``, not this module.
"""

from editors.object_editor.events._panel import (  # noqa: F401
    ObjectEventsPanel,
    ACTION_ALIASES,
    get_action_type,
)

__all__ = ["ObjectEventsPanel", "ACTION_ALIASES", "get_action_type"]
