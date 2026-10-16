#!/usr/bin/env python3
"""
IDE Edition definitions for PyGameMaker
Controls which tutorials are shown and the default blockly preset for new projects.
"""

EDITIONS = {
    # docs/KID_UI_SIMPLIFICATION_PLAN.md Phase 1: a tier below "beginner"
    # for 8-9 year olds, simplifying UI chrome the edition system never
    # touched before (menus, dialogs, the Object Editor's authoring
    # surfaces) rather than just curating content. Inherits beginner's
    # tutorial/sample curation for now (Phase 3 may give it its own,
    # smaller Blockly preset later; "beginner" is a safe placeholder,
    # not a final choice).
    "junior": {
        "name": "Junior",
        "description": "Extra-simplified interface for young students",
        "default_blockly_preset": "junior",
        "tutorial_folders": [
            "01_getting_started",
            "02_first_game",
            "03_pong",
            "04_breakout",
            "15_fruit_fusion",
            "16_fruit_basket",
        ],
        "sample_folders": [
            "maze_1", "maze_2", "maze_3", "maze_4",
            "plateforme_1", "plateforme_2", "plateforme_3",
            "match3_1", "match3_2", "match3_3",
            "views_1", "views_2",
            "treasure",
            "sky_strike_1",
        ],
        # Phase 1: the Object Editor's "Event List" and "Code Editor" tabs
        # are hidden entirely, leaving Blockly as the only authoring
        # surface a junior-tier student sees (editors/object_editor/
        # object_editor_main.py reads this). Not present (or False) on
        # every other tier -- get_current_edition().get(...) defaults to
        # False for all of them.
        "hide_advanced_object_editor_tabs": True,
        # Phase 4: strip Blockly's advanced right-click entries
        # (editors/object_editor/blockly_widget.py -> ?junior=1).
        "simplify_blockly_chrome": True,
        # Phase 2.5: visual defaults applied at startup (main.py) and for
        # the main toolbar (core/ide/_menu_builder.py) -- but only when
        # the user has never explicitly customized the matching setting
        # in Preferences (both call sites check the raw config for an
        # existing 'appearance'/'font' entry first), so picking "Junior"
        # never silently overrides a teacher's own choice on a shared
        # machine.
        "default_theme": "junior",
        "default_font_size": 13,
        "default_toolbar_icon_size": 32,
        # Phase 2: menu/toolbar entries hidden for this tier, keyed by the
        # action's slot name (QAction.objectName(), set in
        # core/ide/_menu_builder.py create_action). Kept: project
        # new/open/save, Test Game, Export as HTML5 (the only export a junior
        # sees; the multi-platform Export Game dialog is hidden), sprite/sound/background
        # import, object/room creation, undo/redo/clipboard, Preferences
        # (a teacher needs it to switch edition back), Restore Deleted
        # Assets, Language, Help. Hidden: file-format/target-specific
        # exports, GMK import, auto-save knobs, Find/Replace, scripts and
        # fonts, resource packages, debug/build, and the maintenance tools.
        "hidden_menu_actions": frozenset({
            "export_game", "export_project_zip", "export_kivy",
            "export_project", "open_project_zip", "import_gmk_file",
            "toggle_auto_save_zip", "toggle_auto_save",
            "show_auto_save_settings", "project_settings",
            "find", "find_replace",
            "create_script", "create_font",
            "import_object_package", "import_room_package",
            "debug_game", "build_game", "build_and_run",
            "configure_blockly", "validate_project",
            "migrate_project_structure", "show_unused_assets_dialog",
            "clean_project", "show_orphaned_files_dialog",
        }),
        "hidden_toolbar_actions": frozenset({"debug_game", "export_game"}),
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
            "15_fruit_fusion",
            "16_fruit_basket",
        ],
        # Welcome-tab sample games shown in this edition, by folder name under
        # samples/ (None = show all). Beginner hides the raycast_*,
        # block_world_*, and multiplayer_lan_* samples -- the first two
        # change the view shape and are the most advanced; multiplayer_lan_1
        # needs running two separate processes/terminals to see its point,
        # not a beginner activity. Everything else (maze / platform / match3
        # / views / treasure) stays.
        "sample_folders": [
            "maze_1", "maze_2", "maze_3", "maze_4",
            "plateforme_1", "plateforme_2", "plateforme_3",
            "match3_1", "match3_2", "match3_3",
            "views_1", "views_2",
            "treasure",
            "sky_strike_1",
        ],
    },
    "advanced": {
        "name": "Advanced",
        "description": "Full tutorial set with intermediate blocks",
        "default_blockly_preset": "intermediate",
        "tutorial_folders": None,  # None = show all
        "sample_folders": None,    # show all samples
    },
    "development": {
        "name": "Development",
        "description": "All tutorials and full block access for testing",
        "default_blockly_preset": "full",
        "tutorial_folders": None,  # show all
        "sample_folders": None,    # show all samples
    },
}

DEFAULT_EDITION = "beginner"

EDITION_KEYS = list(EDITIONS.keys())


def get_current_edition():
    """Get the current edition config dict"""
    from utils.config import Config
    edition_key = Config.get("edition", DEFAULT_EDITION)
    return EDITIONS.get(edition_key, EDITIONS[DEFAULT_EDITION])


def resolve_startup_visual_overrides(config_data):
    """docs/KID_UI_SIMPLIFICATION_PLAN.md Phase 2.5: what the current
    edition's "default_theme"/"default_font_size" should override at
    startup, given the raw saved config dict (``Config._config_data``,
    passed in rather than read globally so this is testable without a
    live ``Config`` singleton).

    Returns ``{"theme": name_or_None, "font_size": size_or_None}`` --
    ``None`` means "no override, use the normal saved/default value"
    because the user has already explicitly set that value via
    Preferences at some point (checked against the raw dict, not
    ``Config.get_appearance_config()``/``get_font_config()``'s own
    built-in fallbacks, which can't tell "never set" apart from
    "explicitly set to the generic default").
    """
    edition_key = config_data.get("edition", DEFAULT_EDITION)
    edition = EDITIONS.get(edition_key, EDITIONS[DEFAULT_EDITION])
    appearance_explicitly_set = "theme" in config_data.get("appearance", {})
    font_size_explicitly_set = "size" in config_data.get("font", {})
    return {
        "theme": None if appearance_explicitly_set else edition.get("default_theme"),
        "font_size": None if font_size_explicitly_set else edition.get("default_font_size"),
    }


def filter_tutorials_for_edition(tutorials_list, base_tutorials_path=None):
    """Filter a list of tutorial dicts from index.json based on current edition.

    Args:
        tutorials_list: list of dicts from index.json "tutorials" key
        base_tutorials_path: optional path to the base (English) Tutorials
            folder. When the edition gates tutorials to a fixed set of folders
            and *none* of them appear in ``tutorials_list`` (e.g. a localized
            index that omits a curated tutorial the edition whitelists), the
            filter falls back to the base English ``index.json`` so the curated
            tutorial is still reachable instead of the user getting an empty
            list.
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


def filter_samples_for_edition(sample_projects):
    """Filter the Welcome-tab sample list by the current edition.

    ``sample_projects`` is the list of (relative_path, label) tuples from
    widgets/welcome_tab.py's SAMPLE_PROJECTS; the folder name is the basename
    of relative_path (e.g. "samples/maze_1" -> "maze_1").

    DELIBERATE ASYMMETRY vs filter_tutorials_for_edition: samples show ALL by
    default and are curated ONLY when the user has EXPLICITLY selected an
    edition whose sample_folders whitelist excludes some. An UNSET edition
    (a fresh machine) shows every sample, even though tutorials default to
    Beginner (DEFAULT_EDITION) — a developer's raycast samples must not vanish
    just because they never opened Preferences. So this reads the raw config
    key rather than get_current_edition(), which would apply the Beginner
    default. Do NOT "simplify" it to get_current_edition() — that reintroduces
    the disappear-by-default bug.
    """
    from utils.config import Config
    edition_key = Config.get("edition", None)       # None = never chosen
    edition = EDITIONS.get(edition_key) if edition_key else None
    allowed = edition.get("sample_folders") if edition else None
    if allowed is None:                             # unset / advanced / development
        return list(sample_projects)
    allowed_set = set(allowed)
    return [(path, label) for (path, label) in sample_projects
            if path.rstrip("/").rsplit("/", 1)[-1] in allowed_set]


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
