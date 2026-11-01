"""Extensions colour their own generated Blockly blocks (micro:bit follow-up M1).

The page used to draw an extension's action category grey, because its category
colour table is core. ``PLUGIN_BLOCK_CATEGORY_COLORS`` is the generic seam.
"""
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from config import blockly_config as bc  # noqa: E402

ROOT = Path(__file__).resolve().parent.parent
HTML = (ROOT / "editors/object_editor/blockly/blockly_workspace.html").read_text(encoding="utf-8")
WIDGET = (ROOT / "editors/object_editor/blockly_widget.py").read_text(encoding="utf-8")


@pytest.fixture
def clean():
    before = dict(bc.BLOCK_CATEGORY_COLORS)
    yield
    bc.BLOCK_CATEGORY_COLORS.clear()
    bc.BLOCK_CATEGORY_COLORS.update(before)


def test_register_adds_valid_colours_and_keeps_the_first(clean):
    assert bc.register_block_category_colors({"Zed": "#112233"}) == 1
    assert bc.register_block_category_colors({"Zed": "#445566"}) == 0
    assert bc.BLOCK_CATEGORY_COLORS["Zed"] == "#112233"


@pytest.mark.parametrize("bad", ["red", "#12345", "#1234567", "112233", 5, None])
def test_register_ignores_anything_that_is_not_a_six_digit_hex(clean, bad):
    assert bc.register_block_category_colors({"Bad": bad}) == 0
    assert "Bad" not in bc.BLOCK_CATEGORY_COLORS


def test_unregister_and_none_input(clean):
    bc.register_block_category_colors({"Zed": "#112233"})
    bc.unregister_block_category_colors(["Zed", "Never"])
    assert "Zed" not in bc.BLOCK_CATEGORY_COLORS
    assert bc.register_block_category_colors(None) == 0


def test_every_extension_with_its_own_category_declares_a_colour():
    import importlib
    wanted = {"microbit": "micro:bit", "raycast_2_5d": "3D View", "block_world": "3D View",
              "multiplayer_lan": "Network", "multiplayer_files": "Network"}
    for folder, category in wanted.items():
        module = importlib.import_module(f"extensions.{folder}")
        colours = module.PLUGIN_BLOCK_CATEGORY_COLORS
        assert list(colours) == [category], folder
        assert bc.register_block_category_colors(dict(colours)) in (0, 1)
    for category in set(wanted.values()):
        assert category in bc.BLOCK_CATEGORY_COLORS
    bc.unregister_block_category_colors(set(wanted.values()))


def test_the_loader_registers_what_a_module_declares(clean):
    from types import SimpleNamespace
    from events.plugin_loader import PluginLoader
    loader = PluginLoader.__new__(PluginLoader)
    loader._load_block_categories(SimpleNamespace(PLUGIN_BLOCK_CATEGORY_COLORS={"Loaded": "#0A0B0C"}))
    assert bc.BLOCK_CATEGORY_COLORS["Loaded"] == "#0A0B0C"


def test_the_page_uses_the_colours_for_blocks_and_drawers_and_the_widget_sends_them_first():
    assert "(window.EXTENSION_CATEGORY_COLORS || {})[d.category]" in HTML       # the block body
    assert "(window.EXTENSION_CATEGORY_COLORS || {})[groupName]" in HTML        # the toolbox drawer
    assert "setCategoryColors: setCategoryColors" in HTML
    assert WIDGET.index("self._push_category_colors()") < WIDGET.index("self._register_custom_blocks()\n")


def test_the_widget_payload_is_the_registry(clean):
    bc.register_block_category_colors({"Zed": "#112233"})
    import json
    assert json.loads(json.dumps(bc.BLOCK_CATEGORY_COLORS))["Zed"] == "#112233"
