#!/usr/bin/env python3
"""
GameMaker 8.0 Complete Action System
All actions organized exactly as they appeared in GM8.0
Actions are organized into tabs/categories as in the original GM8

This module re-exports all action definitions from individual category modules
for backward compatibility with existing code.
"""

from typing import List

# Import core definitions
from actions.core import (
    ActionParameter,
    ActionDefinition,
    GM80_ACTION_TABS,
    get_actions_by_tab,
    get_action_tabs_ordered,
    get_action
)

# Import all action categories
from actions.move_actions import MOVE_ACTIONS
from actions.main1_actions import MAIN1_ACTIONS
from actions.main2_actions import MAIN2_ACTIONS
from actions.control_actions import CONTROL_ACTIONS
from actions.score_actions import SCORE_ACTIONS
from actions.extra_actions import EXTRA_ACTIONS
from actions.draw_actions import DRAW_ACTIONS
from actions.code_actions import CODE_ACTIONS
from actions.rooms_actions import ROOMS_ACTIONS
from actions.timing_actions import TIMING_ACTIONS
from actions.particles_actions import PARTICLES_ACTIONS
from actions.info_actions import INFO_ACTIONS
from actions.resources_actions import RESOURCES_ACTIONS
from actions.thymio_actions import THYMIO_ACTIONS, THYMIO_TAB


# Combined dictionary of all actions (for backward compatibility)
GM80_ALL_ACTIONS = {
    **MOVE_ACTIONS,
    **MAIN1_ACTIONS,
    **MAIN2_ACTIONS,
    **CONTROL_ACTIONS,
    **SCORE_ACTIONS,
    **EXTRA_ACTIONS,
    **DRAW_ACTIONS,
    **CODE_ACTIONS,
    **ROOMS_ACTIONS,
    **TIMING_ACTIONS,
    **PARTICLES_ACTIONS,
    **INFO_ACTIONS,
    **RESOURCES_ACTIONS,
    **THYMIO_ACTIONS,
}


# Re-export helper functions with GM80_ALL_ACTIONS pre-bound
def get_actions_by_tab_v2(tab: str) -> List[ActionDefinition]:
    """Get all actions in a specific tab"""
    return get_actions_by_tab(GM80_ALL_ACTIONS, tab)


def get_action_v2(action_name: str) -> ActionDefinition:
    """Get a specific action definition"""
    return get_action(GM80_ALL_ACTIONS, action_name)


# Export everything for backward compatibility
__all__ = [
    'ActionParameter',
    'ActionDefinition',
    'GM80_ACTION_TABS',
    'GM80_ALL_ACTIONS',
    'MOVE_ACTIONS',
    'MAIN1_ACTIONS',
    'MAIN2_ACTIONS',
    'CONTROL_ACTIONS',
    'SCORE_ACTIONS',
    'EXTRA_ACTIONS',
    'DRAW_ACTIONS',
    'CODE_ACTIONS',
    'ROOMS_ACTIONS',
    'TIMING_ACTIONS',
    'PARTICLES_ACTIONS',
    'INFO_ACTIONS',
    'RESOURCES_ACTIONS',
    'THYMIO_ACTIONS',
    'THYMIO_TAB',
    'get_actions_by_tab',
    'get_actions_by_tab_v2',
    'get_action_tabs_ordered',
    'get_action',
    'get_action_v2',
]
