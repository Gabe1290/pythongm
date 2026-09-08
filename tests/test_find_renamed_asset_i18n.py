"""L7, docs/FULL_AUDIT_2026-09-07.md: find_renamed_asset matched the
category by its translated label.

core/ide/_assets.py's find_renamed_asset located a category in the asset
tree by comparing category_item.text(0).lower() against a hardcoded
"<type>s" English suffix -- but the category label is a tr()'d string
(with an emoji prefix in some builds, see
widgets/asset_tree/asset_tree_item.py's icon_map), so on any
non-English-labeled category the lookup returned None and the
post-rename properties-panel refresh (on_asset_renamed) silently did
nothing.

Fix: compare against the category item's own stored `asset_type`
attribute (set at construction time, language-independent) instead of
its displayed text -- the same pattern several other asset-tree lookups
already use (widgets/asset_tree/asset_tree_widget.py).

Builds a real QTreeWidget + real AssetTreeItem instances (offscreen, no
pytest-qt needed) rather than a full PyGameMakerIDE window -- this repo's
established landmine: constructing and tearing down the real IDE window
in the same process as a language-switching test can crash (see
tests/test_create_asset_name_validation.py's own docstring for the full
reproduction). find_renamed_asset only ever touches self.asset_tree, so
a minimal AssetsMixin host is enough.
"""
import os
os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

import pytest

from conftest import skip_without_pyside6

pytestmark = skip_without_pyside6


@pytest.fixture(scope="module")
def _qapp():
    from PySide6.QtWidgets import QApplication
    app = QApplication.instance() or QApplication([])
    yield app


class _FakeIDE:
    """The minimal surface find_renamed_asset actually reads: .asset_tree."""

    def __init__(self, tree):
        self.asset_tree = tree


def _host(tree):
    from core.ide._assets import AssetsMixin

    class Host(AssetsMixin, _FakeIDE):
        pass

    return Host(tree)


def _tree_with_renamed_sprite(_qapp, category_label):
    """A tree with one "sprites" category (labeled however the caller
    wants -- simulating a translated/emoji-prefixed build) holding one
    asset named "player_new"."""
    from PySide6.QtWidgets import QTreeWidget
    from widgets.asset_tree.asset_tree_item import AssetTreeItem

    tree = QTreeWidget()
    category_item = AssetTreeItem(tree, asset_type="sprites", asset_name="")
    category_item.setText(0, category_label)  # override the real label

    asset_item = AssetTreeItem(
        category_item, asset_type="sprite", asset_name="player_new",
        asset_data={"name": "player_new"},
    )
    return tree, asset_item


class TestFindRenamedAsset:
    def test_finds_the_asset_under_an_english_category_label(self, _qapp):
        tree, asset_item = _tree_with_renamed_sprite(_qapp, "🖼️ Sprites")
        host = _host(tree)
        found = host.find_renamed_asset("player_new", "sprite")
        assert found is asset_item

    def test_finds_the_asset_under_a_translated_category_label(self, _qapp):
        """The exact bug: a non-English (or otherwise non-matching)
        category label must not stop the lookup, since it now matches on
        the item's stored asset_type, not its displayed text."""
        tree, asset_item = _tree_with_renamed_sprite(_qapp, "🖼️ Sprites (fr)")
        host = _host(tree)
        found = host.find_renamed_asset("player_new", "sprite")
        assert found is asset_item

    def test_wrong_name_returns_none(self, _qapp):
        tree, _asset_item = _tree_with_renamed_sprite(_qapp, "🖼️ Sprites")
        host = _host(tree)
        assert host.find_renamed_asset("someone_else", "sprite") is None

    def test_wrong_asset_type_returns_none(self, _qapp):
        tree, _asset_item = _tree_with_renamed_sprite(_qapp, "🖼️ Sprites")
        host = _host(tree)
        assert host.find_renamed_asset("player_new", "sound") is None

    def test_no_asset_tree_returns_none(self):
        class _NoTreeIDE:
            pass

        from core.ide._assets import AssetsMixin

        class Host(AssetsMixin, _NoTreeIDE):
            pass

        assert Host().find_renamed_asset("player_new", "sprite") is None
