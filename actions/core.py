#!/usr/bin/env python3
"""
GameMaker 8.0 Action System - Core Definitions
Base classes and tab definitions for the GM8.0 action system
"""

from typing import Dict, List, Any
from dataclasses import dataclass, field


@dataclass
class ActionParameter:
    """Definition of an action parameter"""
    name: str
    type: str  # int, float, string, boolean, object, sprite, sound, room, etc.
    display_name: str
    description: str
    default: Any = None
    options: List[Any] = field(default_factory=list)  # For dropdown/radio options


@dataclass
class ActionDefinition:
    """Definition of a GameMaker action"""
    name: str
    display_name: str
    category: str
    tab: str
    description: str
    icon: str = ""
    parameters: List[ActionParameter] = field(default_factory=list)
    gm_version: str = "8.0"
    applies_to: str = "self"  # self, other, object


# ============================================================================
# GAMEMAKER 8.0 ACTION CATEGORIES (TABS)
# ============================================================================

GM80_ACTION_TABS = {
    "move": {
        "name": "Move",
        "icon": "➡️",
        "order": 0,
        "description": "Movement and positioning actions"
    },
    "main1": {
        "name": "Main1",
        "icon": "⭐",
        "order": 1,
        "description": "Primary object manipulation actions"
    },
    "main2": {
        "name": "Main2",
        "icon": "⭐",
        "order": 2,
        "description": "Instance creation and destruction"
    },
    "control": {
        "name": "Control",
        "icon": "🎮",
        "order": 3,
        "description": "Flow control and conditional actions"
    },
    "score": {
        "name": "Score",
        "icon": "🏆",
        "order": 4,
        "description": "Score, lives, and health management"
    },
    "extra": {
        "name": "Extra",
        "icon": "✨",
        "order": 5,
        "description": "Variables, sprites, sounds, and rooms"
    },
    "draw": {
        "name": "Draw",
        "icon": "🎨",
        "order": 6,
        "description": "Drawing actions"
    },
    "code": {
        "name": "Code",
        "icon": "💻",
        "order": 7,
        "description": "Code execution and scripts"
    },
    "rooms": {
        "name": "Rooms",
        "icon": "🚪",
        "order": 8,
        "description": "Room properties and views"
    },
    "timing": {
        "name": "Timing",
        "icon": "⏱️",
        "order": 9,
        "description": "Paths and timelines"
    },
    "particles": {
        "name": "Particles",
        "icon": "✨",
        "order": 10,
        "description": "Particle systems and effects"
    },
    "info": {
        "name": "Info",
        "icon": "ℹ️",
        "order": 11,
        "description": "Information and game control"
    },
    "resources": {
        "name": "Resources",
        "icon": "📦",
        "order": 12,
        "description": "Resource replacement"
    }
}


def get_actions_by_tab(all_actions: Dict, tab: str) -> List[ActionDefinition]:
    """Get all actions in a specific tab"""
    return [action for action in all_actions.values() if action.tab == tab]


def get_action_tabs_ordered() -> List[tuple]:
    """Get action tabs in display order"""
    return sorted(GM80_ACTION_TABS.items(), key=lambda x: x[1]["order"])


def get_action(all_actions: Dict, action_name: str) -> ActionDefinition:
    """Get a specific action definition"""
    return all_actions.get(action_name)
