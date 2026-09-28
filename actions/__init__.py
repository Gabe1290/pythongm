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
  classes used by ``editors/object_editor/gm80_action_dialog.py``, plus
  the GM80 tab registry an extension can add a tab to.

The Thymio action schemas that used to live here as
``actions.thymio_actions`` are the Thymio extension's now
(``extensions/thymio/actions.py``, docs/THYMIO_EXTENSION_PLAN.md Stage A1).
"""

from actions.core import ActionParameter, ActionDefinition

__all__ = [
    'ActionParameter',
    'ActionDefinition',
]
