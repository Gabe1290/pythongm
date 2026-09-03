#!/usr/bin/env python3
"""Object events panel package.

``ObjectEventsPanel`` (in ``_panel.py``) is composed from the mixins in the
sibling ``_*.py`` modules — see ``docs/POST_1_0_REFACTOR.md`` File 1:
``_event_crud`` / ``_action_crud`` / ``_render`` / ``_clipboard`` /
``_context_menu`` / ``_action_lookup``.
"""

from ._panel import ObjectEventsPanel
from ._action_lookup import ACTION_ALIASES, get_action_type

__all__ = ["ObjectEventsPanel", "ACTION_ALIASES", "get_action_type"]
