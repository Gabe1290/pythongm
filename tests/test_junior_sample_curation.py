"""Junior-tier Welcome-tab samples (config/editions.py EDITIONS["junior"]
["sample_folders"]) must only include samples that are FULLY editable
within Junior's own restrictions: no Code Editor/Event List tabs, no
Scripts/Fonts/Playgrounds in the asset sidebar, and only JUNIOR_BLOCKS in
the Blockly toolbox. "treasure" (a Scripts-category script called via
execute_script, which has no Blockly block at all), "match3_1"/"match3_2"/
"match3_3" (every event is raw-Python execute_code, not block-built), and
"maze_3"/"maze_4" (a custom Fonts-category asset in their HUD) were pruned
for exactly this reason -- students ready for scripts/raw code/custom
fonts use a more advanced edition instead.
"""
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT))

from config.editions import EDITIONS  # noqa: E402


def test_junior_excludes_samples_that_are_not_fully_editable():
    folders = EDITIONS["junior"]["sample_folders"]
    excluded = {"treasure", "match3_1", "match3_2", "match3_3", "maze_3", "maze_4"}
    assert not (set(folders) & excluded), set(folders) & excluded


def test_junior_sample_list_is_exactly_the_fully_editable_set():
    assert EDITIONS["junior"]["sample_folders"] == [
        "maze_1", "maze_2",
        "plateforme_1", "plateforme_2", "plateforme_3",
        "views_1", "views_2",
        "sky_strike_1",
    ]


def test_every_junior_sample_folder_actually_exists():
    for folder in EDITIONS["junior"]["sample_folders"]:
        assert (REPO_ROOT / "samples" / folder / "project.json").exists(), folder
