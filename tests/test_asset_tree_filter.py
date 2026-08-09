#!/usr/bin/env python3
"""Regression tests for Asset Manager Tier 2 (docs/ASSET_MANAGER_PLAN.md):
the asset-tree name-substring filter box.

Hand-rolled offscreen QApplication (no qtbot/pytest-qt fixture needed) so
this runs even without pytest-qt installed, per this repo's audit-test
convention.
"""

import os

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

from conftest import skip_without_pyside6

pytestmark = skip_without_pyside6

from PySide6.QtWidgets import QApplication

from widgets.asset_tree.asset_tree_widget import AssetTreeWidget
from widgets.asset_tree.asset_tree_item import AssetTreeItem


def _app():
    app = QApplication.instance()
    if app is None:
        app = QApplication([])
    return app


def _category(tree, asset_type):
    for i in range(tree.topLevelItemCount()):
        item = tree.topLevelItem(i)
        if isinstance(item, AssetTreeItem) and item.asset_type == asset_type:
            return item
    return None


def _make_tree():
    _app()
    tree = AssetTreeWidget()
    tree.add_asset("sprites", "spr_player", {"imported": True})
    tree.add_asset("sprites", "spr_enemy", {"imported": True})
    tree.add_asset("sounds", "snd_explosion", {"imported": True})
    return tree


def test_filter_hides_non_matching_leaves():
    tree = _make_tree()
    tree.apply_asset_filter("player")

    sprites = _category(tree, "sprites")
    assert sprites.child(0).isHidden() is False  # spr_player
    assert sprites.child(1).isHidden() is True   # spr_enemy


def test_filter_matches_case_insensitively_on_raw_name():
    """Match against asset_name, not the displayed text (which carries an
    emoji prefix like '🖼️ ' for imported sprites)."""
    tree = _make_tree()
    tree.apply_asset_filter("PLAYER")

    sprites = _category(tree, "sprites")
    assert sprites.child(0).isHidden() is False


def test_empty_filter_shows_everything():
    tree = _make_tree()
    tree.apply_asset_filter("player")
    tree.apply_asset_filter("")

    sprites = _category(tree, "sprites")
    sounds = _category(tree, "sounds")
    assert sprites.child(0).isHidden() is False
    assert sprites.child(1).isHidden() is False
    assert sprites.isHidden() is False
    assert sounds.isHidden() is False


def test_category_hides_when_no_children_match():
    tree = _make_tree()
    tree.apply_asset_filter("explosion")

    sprites = _category(tree, "sprites")
    sounds = _category(tree, "sounds")
    assert sprites.isHidden() is True
    assert sounds.isHidden() is False
    assert sounds.child(0).isHidden() is False


def test_category_with_no_assets_stays_visible_when_unfiltered():
    tree = _make_tree()
    objects_category = _category(tree, "objects")
    assert objects_category.isHidden() is False


def test_refresh_from_project_reapplies_active_filter():
    """A tree rebuild (e.g. after a project reload) must not silently
    drop whatever the user had typed into the filter box."""
    tree = _make_tree()
    tree.apply_asset_filter("player")

    tree.refresh_from_project({
        "assets": {
            "sprites": {
                "spr_player": {"imported": True},
                "spr_enemy": {"imported": True},
            },
        }
    })

    sprites = _category(tree, "sprites")
    names_visible = {
        sprites.child(i).asset_name: not sprites.child(i).isHidden()
        for i in range(sprites.childCount())
    }
    assert names_visible["spr_player"] is True
    assert names_visible["spr_enemy"] is False


def test_refresh_from_project_with_no_active_filter_shows_everything():
    tree = _make_tree()
    tree.refresh_from_project({
        "assets": {
            "sprites": {"spr_new": {"imported": True}},
        }
    })
    sprites = _category(tree, "sprites")
    assert sprites.child(0).isHidden() is False
