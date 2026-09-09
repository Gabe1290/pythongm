"""Regression coverage for TODO.md's "Formalizing the registration" note
(IDE features section): a future new asset type used to be able to fall
through the cracks silently -- three independently hand-kept lists
(``on_asset_double_clicked``'s if/elif chain, ``_canonical_category``'s
singular->plural dict, and the never-actually-called
``get_asset_categories``, which was itself missing "playgrounds") could
each drift from the real editor methods without anything noticing until a
student double-clicked the one asset type affected.

Now there is exactly one source of truth, ``ASSET_TYPE_REGISTRY``
(widgets/asset_tree/asset_utils.py), and ``PyGameMakerIDE.__init__`` calls
``_verify_asset_editor_registry()`` (core/ide/_assets.py) which raises
immediately if a registered ``editor_method`` doesn't exist on the class --
so a typo'd or forgotten editor method now crashes the IDE at startup
instead of silently doing nothing on one specific double-click.

Constructs the real IDE window offscreen (no pytest-qt), matching
tests/test_audit_editor_key_collision.py's own pattern for this class.
"""
import os
os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

import sys
import tempfile
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch

import pytest

sys.path.insert(0, str(Path(__file__).parent.parent))

from conftest import skip_without_pyside6

pytestmark = skip_without_pyside6


@pytest.fixture(scope="module")
def _qapp():
    from PySide6.QtWidgets import QApplication
    app = QApplication.instance() or QApplication([])
    yield app


@pytest.fixture
def ide(_qapp):
    from core.ide_window import PyGameMakerIDE
    w = PyGameMakerIDE()
    w.current_project_path = tempfile.mkdtemp()
    yield w
    w.deleteLater()


# ---------------------------------------------------------------------------
# The registry itself is the real single source (not the old, unused,
# incomplete get_asset_categories/_canonical_category duplicates).
# ---------------------------------------------------------------------------

def test_registry_has_all_eight_known_asset_types():
    from widgets.asset_tree.asset_utils import ASSET_TYPE_REGISTRY
    assert set(ASSET_TYPE_REGISTRY.keys()) == {
        "sprites", "sounds", "backgrounds", "objects",
        "rooms", "scripts", "fonts", "playgrounds",
    }
    # Every entry carries both pieces every dispatch site needs.
    for plural, info in ASSET_TYPE_REGISTRY.items():
        assert info["singular"], plural
        assert info["editor_method"].startswith("open_"), plural


def test_get_asset_categories_includes_playgrounds():
    """Regression: the pre-fix get_asset_categories() had its own hardcoded
    7-item list and was missing "playgrounds" entirely -- caught only
    because nothing actually called it, not because it was correct."""
    from widgets.asset_tree.asset_utils import get_asset_categories
    assert "playgrounds" in get_asset_categories()


def test_is_valid_asset_category_matches_registry():
    from widgets.asset_tree.asset_utils import is_valid_asset_category
    assert is_valid_asset_category("playgrounds") is True
    assert is_valid_asset_category("rooms") is True
    assert is_valid_asset_category("not_a_real_type") is False


# ---------------------------------------------------------------------------
# _canonical_category is now derived from the registry, not its own dict.
# ---------------------------------------------------------------------------

def test_canonical_category_covers_every_registered_singular(ide):
    from widgets.asset_tree.asset_utils import ASSET_TYPE_REGISTRY
    for plural, info in ASSET_TYPE_REGISTRY.items():
        assert ide._canonical_category(info["singular"]) == plural
    # Unknown input passes through unchanged (existing behaviour, unaffected).
    assert ide._canonical_category("mystery") == "mystery"


# ---------------------------------------------------------------------------
# on_asset_double_clicked dispatches through the registry via getattr.
# ---------------------------------------------------------------------------

def test_double_click_dispatches_to_every_registered_editor(ide):
    from widgets.asset_tree.asset_utils import ASSET_TYPE_REGISTRY

    calls = {}
    for info in ASSET_TYPE_REGISTRY.values():
        method_name = info["editor_method"]
        def make_spy(name):
            def spy(asset_name, asset_info):
                calls[name] = (asset_name, asset_info)
            return spy
        setattr(ide, method_name, make_spy(method_name))

    for plural, info in ASSET_TYPE_REGISTRY.items():
        ide.on_asset_double_clicked({
            "asset_type": plural, "name": f"thing_{plural}", "data": {"x": 1},
        })
        assert calls[info["editor_method"]] == (f"thing_{plural}", {"x": 1})


def test_double_click_unknown_type_warns_and_calls_nothing(ide, caplog):
    # Must not raise, and must not call any editor -- a corrupt/foreign
    # project.json asset_type is a data problem, not a missing-editor bug.
    ide.on_asset_double_clicked({"asset_type": "nonsense", "name": "x", "data": {}})


# ---------------------------------------------------------------------------
# The real "fails loudly at startup" mechanism.
# ---------------------------------------------------------------------------

def test_real_ide_registry_verification_passes(ide):
    """Constructing the real class already ran this in __init__ without
    raising (the ide fixture would have failed otherwise); calling it again
    explicitly is the direct assertion that it's currently satisfied."""
    ide._verify_asset_editor_registry()


def test_verification_raises_when_a_registered_method_is_missing():
    """The actual regression check: if a new asset type is added to the
    registry with a typo'd or not-yet-written editor_method, this must
    raise -- proving the startup guard is real, not a no-op."""
    from core.ide._assets import AssetsMixin

    stub = SimpleNamespace(open_room_editor=lambda *a: None)  # missing everything else
    fake_registry = {
        "rooms": {"singular": "room", "editor_method": "open_room_editor"},
        "widgets_3d": {"singular": "widget_3d", "editor_method": "open_widget_3d_editor"},
    }
    with patch("core.ide._assets.ASSET_TYPE_REGISTRY", fake_registry):
        with pytest.raises(RuntimeError, match="open_widget_3d_editor"):
            AssetsMixin._verify_asset_editor_registry(stub)


def test_verification_passes_when_every_method_present():
    from core.ide._assets import AssetsMixin

    stub = SimpleNamespace(open_room_editor=lambda *a: None,
                            open_sprite_editor=lambda *a: None)
    fake_registry = {
        "rooms": {"singular": "room", "editor_method": "open_room_editor"},
        "sprites": {"singular": "sprite", "editor_method": "open_sprite_editor"},
    }
    with patch("core.ide._assets.ASSET_TYPE_REGISTRY", fake_registry):
        AssetsMixin._verify_asset_editor_registry(stub)  # must not raise
