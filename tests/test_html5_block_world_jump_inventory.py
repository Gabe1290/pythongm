"""HTML5 export structural coverage for Block World's jump/gravity
(Tier 7a), inventory-with-counts (Tier 7c), and per-type protection
(Tier 7b) -- the "Section A" export-parity units of
docs/REMAINING_WORK_2026-08-15.md.

No JS engine/Playwright in this environment (same standing limitation as
every other HTML5 block-world/raycast test) -- source-level structural
assertions, plus a numeric parity check that reimplements the JS gravity/
jump formula in Python (mirroring test_raycast_export_parity.py's
"structural equivalence" tier for HTML5) and asserts it produces IDENTICAL
per-step values to the real desktop handlers.py physics, since both are
transcribed from the same formula and must never drift apart.
"""
import re
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT))

from extensions.block_world.handlers import (  # noqa: E402
    DEFAULT_GRAVITY, DEFAULT_JUMP_SPEED, TERMINAL_FALL_SPEED)

BW_JS = (REPO_ROOT / "extensions" / "block_world" / "export_html5.js").read_text(encoding="utf-8")


def test_new_actions_registered():
    for action in ("apply_gravity", "jump", "set_block_protection"):
        assert f"registerExtensionAction('{action}'" in BW_JS, action


def test_gravity_jump_constants_match_desktop():
    checks = {
        "BW_DEFAULT_GRAVITY": DEFAULT_GRAVITY,
        "BW_DEFAULT_JUMP_SPEED": DEFAULT_JUMP_SPEED,
        "BW_TERMINAL_FALL_SPEED": TERMINAL_FALL_SPEED,
    }
    for name, value in checks.items():
        m = re.search(rf"const {name} = ([\-0-9.]+);", BW_JS)
        assert m, name
        assert float(m.group(1)) == value, name


def test_eye_z_for_no_longer_truncates():
    m = re.search(r"function bwEyeZFor\(cfg\)\s*\{(.*?)\n\}", BW_JS, re.S)
    assert m
    body = m.group(1)
    assert "Math.trunc" not in body
    assert "cfg.z_layer" in body


def test_enable_block_world_view_writes_gravity_vz_inventory():
    m = re.search(r"registerExtensionAction\('enable_block_world_view'(.*?)\n\}\);", BW_JS, re.S)
    assert m
    body = m.group(1)
    assert "gravity: num('gravity', 0.0)" in body
    assert "vz: 0.0" in body
    assert "inventory: boolTrue(params.inventory)" in body


def test_move_and_collide_is_gravity_aware():
    m = re.search(r"registerExtensionAction\('move_and_collide'(.*?)\n\}\);", BW_JS, re.S)
    assert m
    body = m.group(1)
    assert "gravityOn" in body
    assert "apply_gravity" in body  # comment documenting the hand-off


def test_place_block_checks_inventory():
    m = re.search(r"registerExtensionAction\('place_block'(.*?)\n\}\);", BW_JS, re.S)
    assert m
    assert "cfg.inventory" in m.group(1)


def test_break_block_checks_protection_and_inventory():
    m = re.search(r"registerExtensionAction\('break_block'(.*?)\n\}\);", BW_JS, re.S)
    assert m
    body = m.group(1)
    assert "cfg.protection" in body
    assert "requiredKey" in body
    assert "cfg.inventory" in body


def test_hud_builder_takes_counts_param():
    m = re.search(r"function bwBuildHudCommands\(([^)]*)\)", BW_JS)
    assert m
    assert "counts" in m.group(1)


# ---------------------------------------------------------------------------
# Numeric parity: the JS gravity/jump formula, reimplemented here, against
# the real desktop physics (handlers.execute_apply_gravity_action /
# execute_jump_action) across an identical step sequence.
# ---------------------------------------------------------------------------

def _js_apply_gravity(cfg, gravity):
    if gravity <= 0:
        return
    z = cfg.get('z_layer', 0)
    vz = cfg.get('vz', 0) - gravity
    vz = max(vz, TERMINAL_FALL_SPEED)
    z += vz
    ground = cfg.get('_ground', 0)
    if z <= ground:
        z = ground
        vz = 0
    cfg['z_layer'] = z
    cfg['vz'] = vz


def test_js_gravity_formula_matches_desktop_across_a_full_arc():
    from unittest.mock import MagicMock
    import sys as _sys
    sys_path_added = str(REPO_ROOT)
    if sys_path_added not in _sys.path:
        _sys.path.insert(0, sys_path_added)

    # Desktop side: drive the real handler through a real GameInstance.
    import os
    os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
    import pygame
    pygame.init()
    from runtime.game_runner import GameRoom, GameInstance
    from runtime.action_executor import ActionExecutor
    from events.plugin_loader import load_all_plugins
    from extensions.block_world.state import block_world_state

    CELL = 32
    room = GameRoom("parity", {"width": 40 * CELL, "height": 40 * CELL}, action_executor=None)
    camera = GameInstance("obj_person", 0, 0, {}, action_executor=None)
    camera._cached_object_data = {"solid": False}
    camera._cached_width = camera._cached_height = CELL
    camera.facing_angle = 0.0
    room.instances.append(camera)
    desktop_cfg = block_world_state(room)["camera"]
    desktop_cfg.update({"enabled": True, "camera_object": "obj_person", "cell_size": CELL,
                        "z_layer": 0.0, "vz": 0.0, "gravity": DEFAULT_GRAVITY,
                        "fov": 66, "render_distance": 20, "columns": 1,
                        "wall_textured": False, "eye_height": 0.5})

    class _Runner:
        def __init__(self, room):
            self.current_room = room
            self.global_variables = {}

    ex = ActionExecutor(game_runner=_Runner(room))
    load_all_plugins(ex)
    camera.action_executor = ex
    ex.action_handlers["jump"](camera, {"speed": DEFAULT_JUMP_SPEED})

    # JS side: reimplemented formula, same starting vz.
    js_cfg = {"z_layer": 0.0, "vz": DEFAULT_JUMP_SPEED, "_ground": 0.0}

    for _ in range(150):
        ex.action_handlers["apply_gravity"](camera, {})
        _js_apply_gravity(js_cfg, DEFAULT_GRAVITY)
        assert abs(desktop_cfg["z_layer"] - js_cfg["z_layer"]) < 1e-9
        assert abs(desktop_cfg["vz"] - js_cfg["vz"]) < 1e-9
        if desktop_cfg["vz"] == 0.0 and desktop_cfg["z_layer"] == 0.0:
            break

    assert desktop_cfg["z_layer"] == 0.0
    assert js_cfg["z_layer"] == 0.0
