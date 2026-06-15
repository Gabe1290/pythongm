#!/usr/bin/env python3
"""
IDE Edition definitions for PyGameMaker
Controls which tutorials are shown and the default blockly preset for new projects.
"""

EDITIONS = {
    "committee": {
        "name": "Committee Demo",
        "description": "Stripped-down demo edition for committee approval — minimal toolbox, single curated tutorial",
        "default_blockly_preset": "minimal",
        "tutorial_folders": ["09_catch_the_coins"],
    },
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


def filter_tutorials_for_edition(tutorials_list, base_tutorials_path=None):
    """Filter a list of tutorial dicts from index.json based on current edition.

    Args:
        tutorials_list: list of dicts from index.json "tutorials" key
        base_tutorials_path: optional path to the base (English) Tutorials
            folder. When the edition gates tutorials to a fixed set of folders
            and *none* of them appear in ``tutorials_list`` (e.g. a localized
            index that omits a curated tutorial such as the committee edition's
            ``09_catch_the_coins``), the filter falls back to the base English
            ``index.json`` so the curated tutorial is still reachable instead
            of the user getting an empty list.
    Returns:
        filtered list
    """
    edition = get_current_edition()
    allowed_folders = edition["tutorial_folders"]
    if allowed_folders is None:
        return tutorials_list

    filtered = [t for t in tutorials_list if t.get("folder") in allowed_folders]
    if filtered or not tutorials_list:
        # Either the curated tutorials were present, or there was nothing to
        # filter in the first place (a genuinely empty index) — nothing to
        # recover.
        return filtered

    # A non-empty index filtered down to nothing: the curated folder(s) this
    # edition requires are absent from this (likely localized) index. Recover
    # them from the base English index so the edition's showcase tutorial is
    # not silently unreachable.
    base_tutorials = _load_base_index_tutorials(base_tutorials_path)
    if base_tutorials:
        return [t for t in base_tutorials if t.get("folder") in allowed_folders]
    return filtered


def _load_base_index_tutorials(base_tutorials_path):
    """Load the 'tutorials' list from the base (English) Tutorials index.json.

    Returns an empty list on any failure (missing path/file, bad JSON) so the
    caller can fall back gracefully. ``base_tutorials_path`` may be a str or a
    Path; ``None`` short-circuits to an empty list.
    """
    if not base_tutorials_path:
        return []
    try:
        import json
        from pathlib import Path
        index_file = Path(base_tutorials_path) / "index.json"
        if not index_file.exists():
            return []
        with open(index_file, "r", encoding="utf-8") as f:
            data = json.load(f)
        return data.get("tutorials", []) or []
    except Exception:
        return []
