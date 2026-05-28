#!/usr/bin/env python3
"""
Action schema package.

Historically this package aggregated every GameMaker-8.0 action category
(MOVE / MAIN1 / MAIN2 / SCORE / etc.) into a GM80_ALL_ACTIONS dict. That
aggregate was never read outside the package: the IDE form drives off
events/action_types.py:ACTION_TYPES, the runtime drives off method-name
dispatch + ACTION_ALIASES, and the GMK importer drives off
importers/gmk_mappings.py. Those category modules have been removed.

What remains in this package:

* ``actions.core`` — the ``ActionDefinition`` / ``ActionParameter``
  classes used by ``editors/object_editor/gm80_action_dialog.py``
  (which the Thymio panels still rely on).
* ``actions.thymio_actions`` — ``THYMIO_ACTIONS`` and ``THYMIO_TAB``,
  consumed directly by ``editors/object_editor/thymio_events_panel.py``
  and ``dialogs/thymio_action_selector.py``.
"""

from actions.core import ActionParameter, ActionDefinition
from actions.thymio_actions import THYMIO_ACTIONS, THYMIO_TAB

__all__ = [
    'ActionParameter',
    'ActionDefinition',
    'THYMIO_ACTIONS',
    'THYMIO_TAB',
]
