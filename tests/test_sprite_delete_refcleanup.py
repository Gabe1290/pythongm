"""Regression test for sprite-delete reference cleanup persisting (audit L32).

Deleting a sprite must clear the dangling sprite name from objects that used it,
and the cleanup must survive (objects/<obj>.json must not restore the stale
name). With M60 (force_project_refresh no longer reloads from disk) and the
live AssetManager delete path clearing the cache + a real save rewriting
objects/*.json, the cleanup now sticks. This locks the AssetManager half:
deleting a sprite clears the object's reference in the live model.
"""

import os
os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

from pathlib import Path
import sys

import pytest

sys.path.insert(0, str(Path(__file__).parent.parent))
from conftest import skip_without_pyside6

pytestmark = skip_without_pyside6


@pytest.fixture(scope="module")
def _qapp():
    from PySide6.QtWidgets import QApplication
    app = QApplication.instance() or QApplication([])
    yield app


def test_delete_sprite_clears_object_reference(_qapp, tmp_path):
    from core.asset_manager import AssetManager
    am = AssetManager(project_directory=tmp_path)
    am.assets_cache = {
        "sprites": {"spr_old": {"name": "spr_old", "file_path": "sprites/spr_old.png"}},
        "objects": {"obj_player": {"name": "obj_player", "sprite": "spr_old"}},
    }
    # The referenced object must lose the dangling sprite name on delete.
    assert am.delete_asset("sprites", "spr_old") is True
    assert am.assets_cache["objects"]["obj_player"]["sprite"] == ""
