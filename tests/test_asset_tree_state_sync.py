"""Regression tests for asset-tree operations vs the live project model.

Audit H13 + H14 (docs/FULL_AUDIT_2026-06-11.md):

- H13: AssetOperations.delete_asset round-tripped the on-disk project.json
  (stale relative to memory — sprite imports and drag-reorders only touch
  memory until the next save) and then force_project_refresh() reloaded
  the whole project from disk: unsaved imports vanished, the dirty flag
  reset, and every open editor was force-closed without a save prompt.
- H14: configure_sprite_animation mutated only the in-memory cache and
  then ran the same disk reload, deterministically wiping the frames the
  success dialog claimed were applied.

Now: deletion routes through the live model (project_manager.delete_asset
+ save_project), the animation dialog persists via save_project before
refreshing, and force_project_refresh redraws the tree from
current_project_data instead of calling load_project().
"""

import json
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import MagicMock, patch

import pytest

import sys
sys.path.insert(0, str(Path(__file__).parent.parent))

from conftest import skip_without_pyside6

pytestmark = skip_without_pyside6


def _make_pm():
    with patch('pygame.mixer.init'):
        from core.asset_manager import AssetManager
        from core.project_manager import ProjectManager
        pm = ProjectManager(asset_manager=AssetManager())
        pm.auto_save_timer = MagicMock()
        return pm


def _sprite(name):
    return {'name': name, 'asset_type': 'sprite', 'file_path': '',
            'width': 32, 'height': 32}


@pytest.fixture
def project(tmp_path):
    pm = _make_pm()
    assert pm.create_new_project("proj", tmp_path) is True
    return pm, tmp_path / "proj"


def _delete_via_operations(pm, project_dir, category, name):
    """Drive the real (non-UI) deletion path the asset tree uses."""
    from widgets.asset_tree.asset_operations import AssetOperations
    tree_stub = SimpleNamespace(project_manager=pm, project_path=str(project_dir))
    ops = AssetOperations(tree_stub)
    return ops.remove_asset_from_project(category, name)


class TestDeleteUsesLiveModel:

    def test_delete_preserves_unsaved_import(self, project):
        """H13's failure: delete one sprite, a different unsaved import
        survives (it used to vanish in the stale disk round-trip)."""
        pm, project_dir = project
        am = pm.asset_manager

        am.assets_cache.setdefault('sprites', {})['spr_dead'] = _sprite('spr_dead')
        assert pm.save_project() is True  # spr_dead is now on disk

        # An import that exists ONLY in memory (commit e950e4c semantics)
        am.assets_cache['sprites']['spr_keep'] = _sprite('spr_keep')

        assert _delete_via_operations(pm, project_dir, 'sprites', 'spr_dead') is True

        assert 'spr_dead' not in am.assets_cache['sprites']
        assert 'spr_keep' in am.assets_cache['sprites']
        with open(project_dir / "project.json", encoding="utf-8") as f:
            sprites_on_disk = json.load(f)['assets']['sprites']
        assert 'spr_dead' not in sprites_on_disk
        assert 'spr_keep' in sprites_on_disk  # persisted, not discarded

    def test_delete_missing_asset_fails(self, project):
        pm, project_dir = project
        assert _delete_via_operations(pm, project_dir, 'sprites', 'nope') is False


class TestForceRefreshStaysInMemory:

    def _run_refresh(self, pm):
        from widgets.asset_tree.asset_tree_widget import AssetTreeWidget

        ide = SimpleNamespace(project_manager=pm)

        class _Host:
            def __init__(self):
                self.refreshed_with = None

            def parent(self):
                return ide

            def refresh_from_project(self, data):
                self.refreshed_with = data

        host = _Host()
        AssetTreeWidget.force_project_refresh(host)
        return host

    def test_refresh_does_not_reload_from_disk(self):
        pm = MagicMock()
        pm.current_project_data = {'assets': {'sprites': {}}}
        host = self._run_refresh(pm)

        pm.load_project.assert_not_called()
        assert host.refreshed_with is pm.current_project_data

    def test_refresh_folds_cache_into_project_data(self, project):
        """The redraw sees cache-only state (e.g. a fresh import)."""
        pm, _ = project
        pm.asset_manager.assets_cache.setdefault('sprites', {})['spr_new'] = _sprite('spr_new')

        host = self._run_refresh(pm)

        assert 'spr_new' in host.refreshed_with['assets']['sprites']
        # and the in-memory model was NOT replaced by a disk read
        assert host.refreshed_with is pm.current_project_data


class TestSpriteAnimationPersists:

    def test_animation_settings_survive_save_and_reload(self, project):
        """H14: frames/speed reach disk and come back on a fresh load."""
        pm, project_dir = project
        am = pm.asset_manager
        am.assets_cache.setdefault('sprites', {})['spr_walk'] = _sprite('spr_walk')

        assert am.update_sprite_animation(
            'spr_walk', frames=4, frame_width=32, frame_height=32,
            speed=10.0, animation_type='strip_h') is not None
        # The dialog flow now persists before any refresh
        assert pm.save_project() is True

        pm2 = _make_pm()
        assert pm2.load_project(project_dir) is True
        reloaded = pm2.current_project_data['assets']['sprites']['spr_walk']
        assert reloaded['frames'] == 4
        assert reloaded['frame_width'] == 32
        assert reloaded['speed'] == 10.0
        assert reloaded['animation_type'] == 'strip_h'
