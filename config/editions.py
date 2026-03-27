#!/usr/bin/env python3
"""
IDE Edition definitions for PyGameMaker
Controls which tutorials are shown and the default blockly preset for new projects.
"""

EDITIONS = {
    "beginner": {
        "name": "Beginner",
        "description": "Simplified interface with introductory tutorials",
        "default_blockly_preset": "beginner",
        "tutorial_folders": [
            "01_getting_started",
            "02_first_game",
            "03_pong",
            "04_breakout",
        ],
    },
    "advanced": {
        "name": "Advanced",
        "description": "Full tutorial set with intermediate blocks",
        "default_blockly_preset": "intermediate",
        "tutorial_folders": None,  # None = show all
    },
    "development": {
        "name": "Development",
        "description": "All tutorials and full block access for testing",
        "default_blockly_preset": "full",
        "tutorial_folders": None,  # show all
    },
}

DEFAULT_EDITION = "beginner"

EDITION_KEYS = list(EDITIONS.keys())


def get_current_edition():
    """Get the current edition config dict"""
    from utils.config import Config
    edition_key = Config.get("edition", DEFAULT_EDITION)
    return EDITIONS.get(edition_key, EDITIONS[DEFAULT_EDITION])


def filter_tutorials_for_edition(tutorials_list):
    """Filter a list of tutorial dicts from index.json based on current edition.

    Args:
        tutorials_list: list of dicts from index.json "tutorials" key
    Returns:
        filtered list
    """
    edition = get_current_edition()
    allowed_folders = edition["tutorial_folders"]
    if allowed_folders is None:
        return tutorials_list
    return [t for t in tutorials_list if t.get("folder") in allowed_folders]
