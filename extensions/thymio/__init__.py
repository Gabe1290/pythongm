#!/usr/bin/env python3
"""Thymio educational robot, packaged as a folder extension.

Being moved out of core one stage at a time — docs/THYMIO_EXTENSION_PLAN.md
is the map. What lives here so far:

* ``actions.py`` — ``THYMIO_ACTIONS`` (the GM80-dialog ``ActionDefinition``
  schemas the Thymio panels and the Aseba exporter read) and ``THYMIO_TAB``,
  the "Thymio" tab of the GM80 action dialog, registered below (Stage A1).

The rest — handlers, events, simulator, renderer, playground editor, the
Aseba/Open Roberta interop — still lives in core and moves in Stages A–F.
"""

PLUGIN_NAME = "Thymio Robot"

from actions.core import register_action_tabs
from .actions import THYMIO_ACTIONS, THYMIO_TAB

register_action_tabs(THYMIO_TAB)
