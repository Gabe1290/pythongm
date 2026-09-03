#!/usr/bin/env python3
"""Object events panel package.

Home for ``ObjectEventsPanel`` and the pieces carved out of it (see
``docs/POST_1_0_REFACTOR.md`` File 1). ``_panel.py`` currently holds the
whole class; helper clusters move into sibling ``_*.py`` modules one
commit at a time.
"""

from ._panel import ObjectEventsPanel, ACTION_ALIASES, get_action_type

__all__ = ["ObjectEventsPanel", "ACTION_ALIASES", "get_action_type"]
