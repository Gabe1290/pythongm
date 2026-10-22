"""Junior-tier assets sidebar: Playgrounds, Scripts and Fonts are hidden so a
young student isn't shown code-authoring categories or the Thymio extension's
category they're not using. Every other edition keeps the full category list.
"""
import os
os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).parent.parent))

from conftest import skip_without_pyside6

pytestmark = skip_without_pyside6


@pytest.fixture(scope="module")
def _qapp():
    from PySide6.QtWidgets import QApplication
    yield QApplication.instance() or QApplication([])


def _build_tree(edition):
    from utils.config import Config
    from widgets.asset_tree.asset_tree_widget import AssetTreeWidget
    original = Config.get("edition", None)
    Config.set("edition", edition)
    try:
        # __init__ already calls setup_categories() once.
        tree = AssetTreeWidget()
        return tree
    finally:
        Config.set("edition", original)


def _category_types(tree):
    types = []
    for i in range(tree.topLevelItemCount()):
        item = tree.topLevelItem(i)
        if getattr(item, "is_category", False):
            types.append(item.asset_type)
    return types


def _top_level_items(tree):
    return [tree.topLevelItem(i) for i in range(tree.topLevelItemCount())]


def test_junior_hides_scripts_fonts_and_playgrounds(_qapp):
    tree = _build_tree("junior")
    try:
        types = _category_types(tree)
        for hidden in ("scripts", "fonts", "playgrounds"):
            assert hidden not in types, hidden
        for kept in ("sprites", "sounds", "backgrounds", "objects", "rooms"):
            assert kept in types, kept
    finally:
        tree.deleteLater()


def test_junior_has_no_stray_separators(_qapp):
    tree = _build_tree("junior")
    try:
        items = _top_level_items(tree)
        is_sep = [not getattr(it, "is_category", False) for it in items]
        assert items, "expected at least one category"
        assert not is_sep[0] and not is_sep[-1]
        for a, b in zip(is_sep, is_sep[1:]):
            assert not (a and b)
    finally:
        tree.deleteLater()


def test_beginner_keeps_scripts_and_fonts(_qapp):
    # Playgrounds only shows up when the Thymio extension is loaded
    # (core/ide_extension_points registration), which this unit test does
    # not do -- unrelated to edition curation, so only scripts/fonts (the
    # two static categories) are checked here.
    from config.editions import EDITIONS
    tree = _build_tree("beginner")
    try:
        types = _category_types(tree)
        for kept in ("scripts", "fonts"):
            assert kept in types, kept
        assert "hidden_asset_categories" not in EDITIONS["beginner"]
    finally:
        tree.deleteLater()


def test_advanced_keeps_scripts_and_fonts(_qapp):
    tree = _build_tree("advanced")
    try:
        types = _category_types(tree)
        for kept in ("scripts", "fonts"):
            assert kept in types, kept
    finally:
        tree.deleteLater()


def test_junior_hides_a_registered_playgrounds_category(_qapp, monkeypatch):
    # Simulate the Thymio extension actually being registered, to exercise
    # the "playgrounds" branch of the hidden-category filter directly
    # rather than relying on it being absent for an unrelated reason.
    import widgets.asset_tree.asset_tree_widget as asset_tree_widget_module
    from core.ide_extension_points import AssetTreeCategory

    fake_category = AssetTreeCategory(
        plural="playgrounds", singular="playground", label="Playgrounds",
        icon="x", open_editor=lambda *a, **k: None,
        new_asset_template=lambda: {},
    )
    monkeypatch.setattr(
        asset_tree_widget_module, "get_asset_tree_categories",
        lambda: [fake_category],
    )

    tree = _build_tree("junior")
    try:
        assert "playgrounds" not in _category_types(tree)
    finally:
        tree.deleteLater()

    tree = _build_tree("beginner")
    try:
        assert "playgrounds" in _category_types(tree)
    finally:
        tree.deleteLater()
