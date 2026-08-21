"""Room editor: saving a sprite's own metadata (origin_x/origin_y, frame
count, art) from the Sprite Editor now refreshes any already-open room
editor's cached sprite geometry, instead of leaving it stale.

Bug report: a sprite's origin was changed in the Sprite Editor (e.g. moving
a "flag" sprite's origin to its base, origin_x=0/origin_y=16, so it plants
correctly on the ground) but an already-open room editor kept drawing and
hit-testing the instance as if origin were still (0, 0) -- the flag floated
above where it was placed and clicking it landed on the wrong spot.

Root cause: RoomCanvas caches sprite pixmaps AND sprite origins per object
name (sprite_cache / origin_cache in editors/room_editor/room_canvas.py),
populated once on first paint and cleared only by
RoomCanvas.set_project_info (called when a room editor tab is opened/
switched). core/ide_window.py's on_editor_save_requested (the shared save
handler for every asset editor, including the Sprite Editor) never told any
already-open room editor to refresh those caches -- only
IDEWindow.refresh_object_sprites did that, and the ONLY caller was the
Object Editor's "change which sprite this object uses" path
(editors/object_editor/object_editor_main.py). A sprite's own metadata
changing underneath an object that already pointed at it (the far more
common edit -- moving an origin, editing pixels, changing frame count)
never triggered it.

Fix: on_editor_save_requested now calls refresh_object_sprites after saving
a 'sprites'-category asset. refresh_object_sprites' real effect is a full
RoomCanvas.set_project_info() re-point (which clears sprite_cache,
origin_cache, and tile_pixmap_cache and re-adopts the just-saved project
data) -- the object_name/old_sprite/new_sprite arguments only drive an
already-redundant single-key cache eviction, so reusing the method with the
sprite's own name (and None old/new sprite names) is safe and correct.
"""
from types import SimpleNamespace
from unittest.mock import MagicMock

import pytest

from conftest import skip_without_pyside6

pytestmark = skip_without_pyside6


def _ide_cls():
    from core.ide_window import PyGameMakerIDE
    return PyGameMakerIDE


def _make_stub_ide(qapp, project_data):
    from PySide6.QtWidgets import QTabWidget

    pm = MagicMock()
    pm.update_asset.return_value = True
    pm.save_project.return_value = True
    pm.get_current_project_data.return_value = project_data

    return SimpleNamespace(
        project_manager=pm,
        current_project_data=project_data,
        current_project_path=None,
        update_status=lambda *a, **k: None,
        update_window_title=lambda *a, **k: None,
        asset_tree=MagicMock(),
        properties_panel=MagicMock(),
        editor_tabs=QTabWidget(),
        _refresh_blockly_asset_lists=lambda: None,
        refresh_object_sprites=MagicMock(),
    )


def _project_with_flag_sprite(origin_y=16):
    return {
        "assets": {
            "sprites": {
                "spr_flag": {
                    "name": "spr_flag", "asset_type": "sprite",
                    "width": 16, "height": 16,
                    "origin_x": 0, "origin_y": origin_y,
                },
            },
            "objects": {
                "obj_flag": {"name": "obj_flag", "asset_type": "object", "sprite": "spr_flag"},
            },
        },
    }


class TestSaveRequestedRefreshesRoomEditorsForSprites:
    def test_saving_a_sprite_calls_refresh_object_sprites(self, qapp):
        project_data = _project_with_flag_sprite()
        stub = _make_stub_ide(qapp, project_data)

        sprite_data = {
            "name": "spr_flag", "asset_type": "sprite",
            "width": 16, "height": 16, "origin_x": 0, "origin_y": 16,
        }
        _ide_cls().on_editor_save_requested(stub, "spr_flag", sprite_data)

        stub.refresh_object_sprites.assert_called_once_with("spr_flag", None, None)

    def test_saving_a_room_does_not_call_refresh_object_sprites(self, qapp):
        """This new call is scoped to sprite saves -- a room/object save
        already has its own, unrelated refresh paths and shouldn't double
        up on this one."""
        project_data = {"assets": {"rooms": {"rm_test": {}}}}
        stub = _make_stub_ide(qapp, project_data)

        room_data = {"name": "rm_test", "instances": [], "width": 480, "height": 480}
        _ide_cls().on_editor_save_requested(stub, "rm_test", room_data)

        stub.refresh_object_sprites.assert_not_called()


class TestRefreshObjectSpritesUpdatesRoomCanvasOrigin:
    def test_stale_origin_cache_is_cleared_by_refresh(self, qapp):
        """End-to-end through the real RoomCanvas: a stale cached (0, 0)
        origin (from before the sprite was edited) is replaced with the
        newly-saved origin once refresh_object_sprites runs -- this is the
        exact mechanism behind on_editor_save_requested's new call."""
        from editors.room_editor.room_canvas import RoomCanvas

        old_data = _project_with_flag_sprite(origin_y=0)
        canvas = RoomCanvas()
        canvas.set_project_info("/tmp/fake_project", old_data)

        # Populate the cache with the stale origin, exactly as draw_instance
        # would on the first paint before the sprite was edited.
        assert canvas.get_sprite_origin("obj_flag") == (0, 0)

        # The sprite is now saved with a new origin (project_data mutated in
        # place, matching how IDEWindow.current_project_data is updated).
        new_data = _project_with_flag_sprite(origin_y=16)

        stub = SimpleNamespace(
            current_project_data=new_data,
            current_project_path="/tmp/fake_project",
            _iter_open_editors=lambda: iter([
                SimpleNamespace(room_canvas=canvas, object_palette=MagicMock()),
            ]),
        )
        _ide_cls().refresh_object_sprites(stub, "spr_flag", None, None)

        assert canvas.get_sprite_origin("obj_flag") == (0, 16)


if __name__ == "__main__":
    raise SystemExit(pytest.main([__file__, "-q"]))
