"""Every tutorial an edition shows must be buildable from that edition's
Blockly toolbox (2026-11-18).

Students doing Pong in the Beginner edition could not find Draw Variable to
show each player's score: Beginner shows the same tutorials as Junior, but
only Junior's block set had ever been derived from them. This test derives
what each tutorial uses from its reference project
(tools/tutorial_reference_projects.py, the same builders the tutorial truth
tests run through the real engine) and checks it against every edition.

Extension actions (raycast, file-exchange multiplayer, ...) are skipped: the
toolbox shows them whenever their extension is active, whatever the preset
(config/toolbox_visibility.visible_actions).
"""
import inspect
import json
import sys
import tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

import pytest

from config.blockly_config import PRESETS, BlocklyConfig
from config.editions import EDITIONS

# Runtime action names the builders use that differ from the block name.
ACTION_ALIASES = {"end_game": "game_end"}

# Tutorial folder -> reference-project builder. 01 builds nothing; 17
# (micro:bit) is extension-only.
BUILDERS = {
    "02_first_game": "build_t02", "03_pong": "build_t03",
    "04_breakout": "build_t04", "05_sokoban": "build_t05",
    "06_maze": "build_t06", "07_platformer": "build_t07",
    "08_lunar_lander": "build_t08", "09_catch_the_coins": "build_t09",
    "10_file_exchange_multiplayer": "build_t10",
    "11_raycast_first_steps": "build_t11", "12_raycast_textures": "build_t12",
    "13_raycast_goals_monsters": "build_t13", "14_raycast_hud_minimap": "build_t14",
    "15_fruit_fusion": "build_t15", "16_fruit_basket": "build_t16",
}
ALL_FOLDERS = sorted(BUILDERS) + ["01_getting_started", "17_microbit_intro"]

_cache = {}


def _core_blocks_used(folder):
    """Block types of the core (non-extension) actions the tutorial uses,
    across every phase its builder supports."""
    if folder in _cache:
        return _cache[folder]
    from tools import tutorial_reference_projects as t
    from events.action_types import ACTION_TO_BLOCKLY_MAP
    from events.plugin_loader import extension_for_action, load_all_plugins

    load_all_plugins()
    actions = set()

    def walk(o):
        if isinstance(o, dict):
            if isinstance(o.get("action"), str):
                actions.add(o["action"])
            for v in o.values():
                walk(v)
        elif isinstance(o, list):
            for v in o:
                walk(v)

    blocks = set()
    name = BUILDERS.get(folder)
    if name:
        fn = getattr(t, name)
        phases = range(1, 6) if "phase" in inspect.signature(fn).parameters else [None]
        for phase in phases:
            root = Path(tempfile.mkdtemp())
            try:
                fn(root, phase=phase) if phase else fn(root)
            except Exception:
                continue  # phase not offered by this tutorial
            for f in [root / "project.json", *root.glob("objects/*.json")]:
                if f.exists():
                    walk(json.loads(f.read_text(encoding="utf-8")))
        blocks = {ACTION_ALIASES.get(a, ACTION_TO_BLOCKLY_MAP.get(a, a))
                  for a in actions if not extension_for_action(a)}
    _cache[folder] = blocks
    return blocks


def _edition_folders(edition):
    folders = edition["tutorial_folders"]
    return ALL_FOLDERS if folders is None else folders


def test_every_tutorial_folder_is_mapped():
    tutorials = Path(__file__).parent.parent / "Tutorials"
    real = {p.name for p in tutorials.iterdir() if p.is_dir() and p.name[:2].isdigit()}
    assert real == set(ALL_FOLDERS), "add the new tutorial to BUILDERS / ALL_FOLDERS"


@pytest.mark.parametrize("edition_key", sorted(EDITIONS))
def test_edition_offers_every_block_its_tutorials_use(edition_key):
    edition = EDITIONS[edition_key]
    enabled = PRESETS[edition["default_blockly_preset"]].enabled_blocks
    missing = {}
    for folder in _edition_folders(edition):
        gap = _core_blocks_used(folder) - enabled
        if gap:
            missing[folder] = sorted(gap)
    assert not missing, (
        f"{edition_key} edition shows tutorials its toolbox can't build: {missing}")


def test_beginner_offers_everything_junior_does():
    """Beginner and Junior show the same tutorials; Junior's set also covers
    blocks the lesson pages name that the builders express another way."""
    assert EDITIONS["beginner"]["tutorial_folders"] == EDITIONS["junior"]["tutorial_folders"]
    missing = set(BlocklyConfig.JUNIOR_BLOCKS) - PRESETS["beginner"].enabled_blocks
    assert not missing, f"beginner lacks junior blocks: {sorted(missing)}"


def test_pong_score_display_block_is_in_beginner():
    """The reported case: Tutorial 3 phase 3 draws each player's score."""
    assert "draw_variable" in PRESETS["beginner"].enabled_blocks


def _save_old_config(tmp_path, monkeypatch, preset_name, drop):
    import config.blockly_config as bc
    path = tmp_path / "blockly_config.json"
    monkeypatch.setattr(bc, "get_config_path", lambda: path)
    old = PRESETS["beginner"].to_dict()
    old["preset_name"] = preset_name
    old["enabled_blocks"] = [b for b in old["enabled_blocks"] if b not in drop]
    path.write_text(json.dumps(old), encoding="utf-8")
    return bc, path


def test_a_saved_beginner_config_gains_the_new_blocks(tmp_path, monkeypatch):
    """A machine that saved the beginner preset before the fix must not keep
    the old toolbox (a project with no preset of its own reads it)."""
    bc, path = _save_old_config(tmp_path, monkeypatch, "beginner",
                                {"draw_variable", "room_goto"})
    loaded = bc.load_config()
    assert {"draw_variable", "room_goto"} <= loaded.enabled_blocks
    assert "draw_variable" in json.loads(path.read_text(encoding="utf-8"))["enabled_blocks"]


def test_a_teachers_custom_config_is_left_alone(tmp_path, monkeypatch):
    bc, _ = _save_old_config(tmp_path, monkeypatch, "custom", {"draw_variable"})
    assert "draw_variable" not in bc.load_config().enabled_blocks
