"""Kivy camera FBO build-time-only fix (Section B,
docs/REMAINING_WORK_2026-08-15.md).

Before this fix, the multi-view Fbo render target was only ever built at
room construction, gated on the room's baked `views_enabled` config --
enabling views purely via a runtime `enable_views` action
(scene.set_views_enabled(True)) on a room that started WITHOUT views left
`self._fbo`/`self._view_group` permanently None, so `update_views()`/
`_render_views()` silently did nothing forever. `_ensure_views_fbo()`
(extracted from the constructor's own Fbo-building block, now also called
from `set_views_enabled`) fixes that: enabling views at runtime now
actually retrofits a working camera.

Reuses tests/test_kivy_views.py's own stub-kivy harness via sibling import
(_stub_kivy_env/_load_scene/_scene_file) rather than a second copy.
"""
import sys
import tempfile
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT))
sys.path.insert(0, str(Path(__file__).resolve().parent))  # for sibling test import

from export.Kivy.kivy_exporter import KivyExporter  # noqa: E402

from test_kivy_views import _stub_kivy_env, _load_scene  # noqa: E402


def _non_views_project_data():
    """Same room shape as test_kivy_views.py's own fixture, but
    views_enabled starts False -- the room the Fbo build-time gate used to
    leave permanently dark once enable_views ran at runtime."""
    return {
        "name": "views_retrofit",
        "settings": {"window_width": 800, "window_height": 600},
        "assets": {
            "sprites": {}, "sounds": {}, "backgrounds": {},
            "objects": {
                "obj_player": {"name": "obj_player", "sprite": "", "events": {}},
            },
            "rooms": {
                "rm_big": {
                    "name": "rm_big", "width": 2400, "height": 800,
                    "background_color": "#204060",
                    "views_enabled": False,
                    "views": {
                        "view_0": {
                            "visible": True,
                            "view_w": 800, "view_h": 600,
                            "port_x": 0, "port_y": 0,
                            "follow": "obj_player",
                            "hborder": 100, "vborder": 100,
                        },
                    },
                    "instances": [
                        {"object_type": "obj_player", "x": 1200, "y": 400},
                    ],
                },
            },
        },
        "room_order": ["rm_big"],
    }


@pytest.fixture(scope="module")
def exported_non_views():
    src = Path(tempfile.mkdtemp(prefix="kivy_views_retrofit_src_"))
    out = Path(tempfile.mkdtemp(prefix="kivy_views_retrofit_export_")) / "export"
    assert KivyExporter(_non_views_project_data(), src, out).export()
    return out / "game"


def test_room_starts_with_no_fbo(exported_non_views):
    with _stub_kivy_env(exported_non_views):
        scene = _load_scene(exported_non_views)
        assert scene.views_enabled is False
        assert scene._fbo is None
        assert scene._view_group is None


def test_enabling_views_at_runtime_builds_a_real_fbo(exported_non_views):
    with _stub_kivy_env(exported_non_views):
        scene = _load_scene(exported_non_views)
        scene.set_views_enabled(True)

        assert scene.views_enabled is True
        assert scene._fbo is not None
        assert scene._view_group is not None


def test_retrofitted_camera_actually_renders_without_crashing(exported_non_views):
    with _stub_kivy_env(exported_non_views):
        scene = _load_scene(exported_non_views)
        scene.set_views_enabled(True)

        # update_views()/_render_views() must not silently no-op or crash
        # now that a real Fbo/view_group exist.
        target = scene.instances[0]
        target.x = 1600.0
        scene.update_views()
        scene._render_views()
        assert scene.views[0]['view_x'] is not None
        assert scene._view_group.children  # something was actually queued to draw


def test_disabling_then_reenabling_views_reuses_the_same_fbo(exported_non_views):
    """set_views_enabled must not rebuild (leak) a second Fbo on repeated
    toggles -- _ensure_views_fbo is a no-op once self._fbo already exists."""
    with _stub_kivy_env(exported_non_views):
        scene = _load_scene(exported_non_views)
        scene.set_views_enabled(True)
        first_fbo = scene._fbo

        scene.set_views_enabled(False)
        assert scene.views_enabled is False

        scene.set_views_enabled(True)
        assert scene._fbo is first_fbo


def test_legacy_views_enabled_at_construction_is_unchanged():
    """Full regression guard: a room that already had views_enabled=True at
    construction (test_kivy_views.py's own fixture shape) must build the
    Fbo exactly as before -- this fix only ADDS the runtime retrofit path,
    it must not change the construction-time path at all."""
    from test_kivy_views import _views_project_data
    src = Path(tempfile.mkdtemp(prefix="kivy_views_legacy_src_"))
    out = Path(tempfile.mkdtemp(prefix="kivy_views_legacy_export_")) / "export"
    assert KivyExporter(_views_project_data(), src, out).export()
    game = out / "game"
    with _stub_kivy_env(game):
        scene = _load_scene(game)
        assert scene.views_enabled is True
        assert scene._fbo is not None
        assert scene._view_group is not None
