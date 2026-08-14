#!/usr/bin/env python3
"""Runtime handlers for the Block World extension's actions (Phase 2a).

Mirrors extensions/raycast_2_5d/handlers.py: a plugin's handlers run as
methods of a PluginExecutor instance, reaching the engine through
instance.action_executor (the plugins/audio_actions pattern), not through
ActionExecutor directly.
"""

import json
import math
from pathlib import Path

from .state import (BLOCK_TYPES, DEFAULT_HOTBAR, block_world_state, get_block,
                    is_breakable, load_block_list, peek_camera, remove_block,
                    set_block)


def _truthy(raw):
    """Coerce an action parameter to a bool. Strings matter: project JSON
    stores "false", which is truthy under a bare bool()."""
    if isinstance(raw, str):
        return raw.strip().lower() in ("true", "1", "yes")
    return bool(raw)


class PluginExecutor:
    """Handles execution of the Block World actions."""

    @staticmethod
    def _executor(instance):
        return getattr(instance, "action_executor", None)

    def _pick(self, instance, parameters):
        """Resolve the camera and ask what its centre ray is pointing at.

        Returns ``(room, target, placement)`` or None when there is nothing
        to act on -- no room, no block-world view, or no camera instance.

        Every number here is read back from the SAME camera config the
        renderer projects from, and the angle uses the renderer's own
        ``radians(-facing_angle)`` conversion. Recomputing either
        independently is how picking drifts away from the crosshair.

        The ray follows the camera's look pitch (Phase 2c), not just its
        facing angle: the crosshair is fixed at screen centre, but a tilted
        view puts the horizon somewhere else on screen, so the ray through
        screen centre has real vertical slope whenever pitch != 0.
        ``screen_ray``/``pick_voxel`` are exactly what the mouse-aim preview
        tool already uses for this -- at pitch 0 they reduce to the same
        level walk ``pick_block`` does, so this is not a behaviour change for
        an unpitched view.
        """
        ae = self._executor(instance)
        if ae is None or not ae.game_runner or not ae.game_runner.current_room:
            return None
        room = ae.game_runner.current_room
        cfg = peek_camera(room)
        if not cfg or not cfg.get("enabled"):
            return None
        camera = room._find_first_instance(cfg.get("camera_object", ""))
        if camera is None:
            return None

        try:
            reach = int(float(ae._parse_value(parameters.get("reach", 5), instance)))
        except (TypeError, ValueError):
            reach = 5
        reach = max(1, reach)

        cell_size = int(cfg.get("cell_size", 32))
        cx, cy = room._sprite_top_left(camera)
        from .renderer import pick_voxel, screen_ray, horizon_for, eye_z_for  # lazy: pygame
        # The layer the EYE is in, not the layer the feet are on. With the
        # default two-block-tall body those differ, and a level crosshair
        # addresses whatever is at eye height -- picking the feet layer would
        # break blocks the crosshair is not on. eye_z_for is the one place
        # this is computed, so the render path can never disagree with it.
        eye_z = eye_z_for(cfg)

        gr = ae.game_runner
        screen_w = getattr(gr, "window_width", 0) or 0
        screen_h = getattr(gr, "window_height", 0) or 0
        if not screen_w or not screen_h:
            screen = getattr(gr, "screen", None)
            if screen is not None:
                screen_w, screen_h = screen.get_size()
        screen_w = screen_w or 640
        screen_h = screen_h or 480

        fov_rad = math.radians(cfg.get("fov", 66))
        pitch = float(cfg.get("pitch", 0.0))
        horizon = horizon_for(screen_h, pitch)
        angle_rad, z_per_px = screen_ray(
            screen_w / 2.0, screen_h / 2.0,
            math.radians(-camera.facing_angle), fov_rad, screen_w, screen_h,
            cell_size, horizon=horizon)

        target, placement = pick_voxel(
            room,
            cx + camera._cached_width / 2,
            cy + camera._cached_height / 2,
            eye_z, angle_rad, z_per_px, cell_size, reach)
        return room, target, placement

    def execute_set_look_pitch_action(self, instance, parameters):
        """Tilt the view up or down (Phase 2c).

        Clamped by the renderer, so holding a look control against the limit
        just stops rather than folding the view inside out.

        Parameters:
            pitch: degrees, positive up
            relative: add to the current angle instead of replacing it
        """
        ae = self._executor(instance)
        if ae is None or not ae.game_runner or not ae.game_runner.current_room:
            return
        cfg = peek_camera(ae.game_runner.current_room)
        if not cfg:
            return
        try:
            pitch = float(ae._parse_value(parameters.get("pitch", 0), instance))
        except (TypeError, ValueError):
            return
        if _truthy(parameters.get("relative", False)):
            pitch += float(cfg.get("pitch", 0.0))
        # Clamp at the setter, not just in the renderer: a held look control
        # accumulating past the limit would have to be wound all the way back
        # before the view responded again.
        from .renderer import clamp_pitch  # lazy: keeps pygame out of the IDE
        cfg["pitch"] = clamp_pitch(pitch)

    def execute_select_hotbar_slot_action(self, instance, parameters):
        """Choose the hotbar's selected block, for place_block to build with.

        Sets two plain instance attributes: `hotbar_index` (wrapped into
        range) and `hotbar_block` (the resolved block type id). Bind
        place_block's `block` parameter to the literal expression
        `"hotbar_block"` to use it -- place_block itself needs no change,
        since its `block` parameter already resolves a bare instance-
        variable-name expression (see ActionExecutor._parse_value).

        Works even outside an active block-world view: this only touches
        the calling instance, not room state, so a menu/inventory screen
        can set the starting slot before the 3D view is ever enabled.

        Parameters:
            index: hotbar slot index, wrapping around at either end
            relative: add to the current slot instead of jumping to it, for
                cycling with a "[ ]"-style control
        """
        ae = self._executor(instance)
        if ae is None:
            return
        try:
            index = int(float(ae._parse_value(parameters.get("index", 0), instance)))
        except (TypeError, ValueError):
            return
        if _truthy(parameters.get("relative", False)):
            index += int(getattr(instance, "hotbar_index", 0))
        index %= len(DEFAULT_HOTBAR)
        instance.hotbar_index = index
        instance.hotbar_block = DEFAULT_HOTBAR[index]

    def execute_place_block_action(self, instance, parameters):
        """Put a block in the empty cell the camera's centre ray reaches.

        A no-op when there is nowhere to put one -- the camera is flush
        against a block, or the target cell is already occupied. Silent
        rather than an error: holding the build key against a wall is
        ordinary play, not a mistake worth reporting.

        Parameters:
            block: which block type to place (default "stone")
            reach: how many cells ahead you can build (default 5)
        """
        picked = self._pick(instance, parameters)
        if picked is None:
            return
        room, _target, placement = picked
        if placement is None:
            return

        ae = self._executor(instance)
        block = ae._parse_value(parameters.get("block", "stone"), instance)
        block = str(block) if block else "stone"
        if block not in BLOCK_TYPES:
            return

        # No "is this cell empty?" check: pick_voxel guarantees it. It only
        # ever returns a cell it has already read as air (see its docstring),
        # so a guard here would be unreachable code pretending to be a safety
        # net.
        set_block(room, *placement, block)

    def execute_break_block_action(self, instance, parameters):
        """Remove the block the camera's centre ray hits first.

        Block types marked unbreakable (see state.is_breakable) are left
        alone -- that check lives here and nowhere else, so an indestructible
        block is still aimed at, still occludes, and can still be built
        against. Swinging at one is a silent no-op, the same as swinging at
        thin air.

        Parameters:
            reach: how many cells ahead you can reach (default 5)
        """
        picked = self._pick(instance, parameters)
        if picked is None:
            return
        room, target, _placement = picked
        if target is None:
            return
        if not is_breakable(get_block(room, *target)):
            return
        remove_block(room, *target)

    def execute_enable_block_world_view_action(self, instance, parameters):
        """Switch the current room to a first-person voxel view (single
        layer, Phase 2a), or back to the normal top-down view. The renderer
        that actually draws it (renderer.py) claims the room through the
        extension_hooks seam once this sets the camera's 'enabled' flag.

        Parameters (all optional except enable):
            enable: True to switch to the block-world view (default True)
            camera_object: Object name whose x/y/facing_angle is the camera
                (default: the calling instance's own object)
            z_layer, fov, render_distance, cell_size, columns: projection settings
            wall_color / floor_color / ceiling_color: flat-shade colours
            wall_textured: off forces flat block colours
        """
        ae = self._executor(instance)
        if ae is None or not ae.game_runner or not ae.game_runner.current_room:
            return

        enable = _truthy(ae._parse_value(parameters.get("enable", True), instance))

        room = ae.game_runner.current_room
        if not enable:
            block_world_state(room)["camera"] = {"enabled": False}
            return

        camera_object = ae._parse_value(parameters.get("camera_object", ""), instance)
        camera_object = str(camera_object) if camera_object else instance.object_name

        def _num(key, default):
            try:
                return float(ae._parse_value(parameters.get(key, default), instance))
            except (TypeError, ValueError):
                return default

        def _bool(key, default):
            return _truthy(parameters.get(key, default))

        from .renderer import DEFAULT_EYE_HEIGHT, clamp_pitch  # lazy: pygame

        block_world_state(room)["camera"] = {
            "enabled": True,
            "camera_object": camera_object,
            "z_layer": int(_num("z_layer", 0)),
            "fov": _num("fov", 66),
            "render_distance": int(_num("render_distance", 20)),
            "cell_size": int(_num("cell_size", 32)),
            "columns": int(_num("columns", 320)),
            "wall_color": str(parameters.get("wall_color", "#8a8a8a")),
            "floor_color": str(parameters.get("floor_color", "#3a2f1c")),
            "ceiling_color": str(parameters.get("ceiling_color", "#87CEEB")),
            "wall_textured": _bool("wall_textured", True),
            # Look angle in degrees, positive up (Phase 2c). Clamped here too
            # -- was the one pitch-writing site that wasn't, rescued only by
            # horizon_for's own defensive clamp at render time.
            "pitch": clamp_pitch(_num("pitch", 0)),
            # Horizontal (top/bottom) faces cast every Nth screen row and
            # upscale the result; 0 falls back to a flat average colour,
            # which is cheaper on a scene showing a lot of deck.
            "top_cast_res": int(_num("top_cast_res", 4)),
            # Camera height in cells (Phase 3's two-block-tall body by
            # default). Was previously read everywhere with this same
            # fallback but never actually written here, so no authored
            # action could ever change it -- see docs/VOXEL_WORLD_PLAN.md.
            "eye_height": _num("eye_height", DEFAULT_EYE_HEIGHT),
        }

    def execute_load_block_world_action(self, instance, parameters):
        """Load a pre-authored world into the current room from a JSON data
        file, replacing whatever blocks are there.

        Bind this in `game_start`, not `create` -- `create` re-fires on
        `restart_room` (see this repo's own landmine notes), and reloading
        the file back on top of live edits would silently discard whatever
        the player broke or placed since the room was entered.

        The file holds a flat JSON list in the `state.to_block_list` shape:
        `[{"x":, "y":, "z":, "type":}, ...]` -- the same shape a generator
        script (tools/gen_block_world_*.py) or `to_block_list` itself
        produces. Silently does nothing on a missing file, unreadable JSON,
        or an unknown block type -- consistent with this extension's other
        actions (a flush wall, an unbreakable swing) treating bad input as a
        no-op rather than crashing the game.

        Parameters:
            data_file: path to the JSON file, relative to the project
                folder (e.g. "blocks/room1.json")
        """
        ae = self._executor(instance)
        if ae is None or not ae.game_runner or not ae.game_runner.current_room:
            return
        room = ae.game_runner.current_room

        # Not run through _parse_value: a real path ("blocks/room1.json")
        # contains "/", which _parse_value's expression heuristic reads as
        # division and mangles -- the same reason wall_color/floor_color
        # above are read as plain strings, not expressions.
        data_file = str(parameters.get("data_file", ""))
        if not data_file:
            return

        project_path = getattr(ae.game_runner, "project_path", None)
        if not project_path:
            return

        try:
            with open(Path(project_path) / data_file, "r", encoding="utf-8") as f:
                block_list = json.load(f)
            load_block_list(room, block_list)
        except (OSError, ValueError, KeyError, TypeError):
            # Bad path, bad JSON, or an unknown block type in the file --
            # see the docstring above for why this is a silent no-op.
            pass
