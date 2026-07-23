#!/usr/bin/env python3
"""Runtime handlers for the raycast extension's actions (Stage B3).

Moved verbatim out of ``ActionExecutor`` (``runtime/action_executor.py``). A
plugin's handlers run as methods of a ``PluginExecutor`` instance, not of the
``ActionExecutor``, so the one mechanical change is how they reach the engine:
what used to be ``self.game_runner`` / ``self._parse_value`` is now reached
through ``instance.action_executor`` — the same handle ``plugins/audio_actions``
already uses for ``game_runner``. Everything else is unchanged, and the raycast
samples are the behavioural proof.

The ``raycast_camera`` state these set still lives on ``GameRoom`` (core
initialises it); moving that state into ``room.extension_state`` is a separate,
purely-internal refactor left for later (see docs/RAYCAST_EXTENSION_PLAN.md).
``facing_angle`` stays a core ``GameInstance`` attribute by design (B4).
"""


class PluginExecutor:
    """Handles execution of the raycast setup actions."""

    @staticmethod
    def _executor(instance):
        """The ActionExecutor driving this instance — the moved handlers reach
        back to it for expression parsing and the current room, exactly as they
        did when they were ActionExecutor methods."""
        return getattr(instance, "action_executor", None)

    def execute_set_facing_angle_action(self, instance, parameters):
        """Set this instance's facing_angle — persistent look direction for a
        raycast camera (docs/RAYCAST_2_5D_PLAN.md), independent of movement
        speed. Same GM angle convention as set_direction_speed (0=right, 90=up,
        180=left, 270=down) and the same relative/absolute shape as every other
        set_* action.

        Parameters:
            angle: Angle in degrees (default 0)
            relative: Add to the current facing_angle instead of replacing it
                (default False)
        """
        ae = self._executor(instance)
        raw_angle = parameters.get("angle", 0)
        raw_relative = parameters.get("relative", False)
        angle = ae._parse_value(raw_angle, instance) if ae else raw_angle
        relative = ae._parse_value(raw_relative, instance) if ae else raw_relative
        if isinstance(relative, str):
            relative = relative.lower() in ("true", "1", "yes")

        try:
            angle = float(angle)
        except (TypeError, ValueError):
            angle = 0.0

        if relative:
            instance.facing_angle = (instance.facing_angle + angle) % 360.0
        else:
            instance.facing_angle = angle % 360.0

    def execute_enable_raycast_view_action(self, instance, parameters):
        """Switch the current room to a Doom/Wolfenstein-style raycast
        first-person view (docs/RAYCAST_2_5D_PLAN.md), or back to the normal
        top-down view. The renderer that actually draws it lives in this
        extension (renderer.py) and claims the room through the extension_hooks
        seam once this sets raycast_camera['enabled'].

        Parameters (all optional except enable):
            enable: True to switch to the raycast view (default True)
            camera_object: Object name whose x/y/facing_angle is the camera
                (default: the calling instance's own object)
            fov, render_distance, cell_size, columns: projection settings
            wall_color / floor_color / ceiling_color: flat-shade colours
            wall_texture / sky_texture / floor_texture / ceiling_texture,
            wall_textured, floor_cast_res: Phase 5 texturing
            viewport_height: DOOM-bar letterbox (0 = full window height)
        """
        ae = self._executor(instance)
        if ae is None or not ae.game_runner or not ae.game_runner.current_room:
            return

        enable = ae._parse_value(parameters.get("enable", True), instance)
        if isinstance(enable, str):
            enable = enable.lower() in ("true", "1", "yes")

        room = ae.game_runner.current_room
        if not enable:
            room.raycast_camera = {"enabled": False}
            return

        camera_object = ae._parse_value(parameters.get("camera_object", ""), instance)
        camera_object = str(camera_object) if camera_object else instance.object_name

        def _num(key, default):
            try:
                return float(ae._parse_value(parameters.get(key, default), instance))
            except (TypeError, ValueError):
                return default

        def _bool(key, default):
            raw = parameters.get(key, default)
            if isinstance(raw, str):
                return raw.strip().lower() in ("true", "1", "yes")
            return bool(raw)

        room.raycast_camera = {
            "enabled": True,
            "camera_object": camera_object,
            "fov": _num("fov", 66),
            "render_distance": int(_num("render_distance", 20)),
            "cell_size": int(_num("cell_size", 32)),
            "columns": int(_num("columns", 320)),
            "wall_color": str(parameters.get("wall_color", "#993333")),
            "floor_color": str(parameters.get("floor_color", "#464632")),
            "ceiling_color": str(parameters.get("ceiling_color", "#87CEEB")),
            # Phase 5 texturing: a sprite NAME to texture every wall (empty =
            # flat colour / per-instance sprite fallback), and an on/off toggle.
            "wall_texture": str(parameters.get("wall_texture", "")),
            "wall_textured": _bool("wall_textured", True),
            # Phase 5b: a sprite NAME for a DOOM-style panning sky over the
            # ceiling (empty = the flat ceiling_color fill).
            "sky_texture": str(parameters.get("sky_texture", "")),
            # Phase 5: floor / (indoor) ceiling texture sprite names, cast via
            # low-res floor casting; floor_cast_res is the downsample factor
            # (higher = faster + chunkier; 4 measured ~5ms/frame). Empty
            # textures -> the flat floor_color / ceiling fills.
            "floor_texture": str(parameters.get("floor_texture", "")),
            "ceiling_texture": str(parameters.get("ceiling_texture", "")),
            "floor_cast_res": int(_num("floor_cast_res", 4)),
            # DOOM-bar letterbox: shrink the 3D view to this many pixels tall
            # and reserve the band below for a status bar. 0 = full window
            # height, so every existing raycast game renders unchanged.
            "viewport_height": int(_num("viewport_height", 0)),
        }
        # Force the wall edges to rebuild against the (possibly new) cell_size
        # next render instead of reusing a stale cache.
        room._raycast_v_walls = None

    def execute_draw_minimap_action(self, instance, parameters):
        """Draw a north-up minimap of the raycast room's wall edges.

        A MACRO action: it reads the wall edges the raycast renderer already
        derived for this room and emits ordinary 'rectangle' / 'line' draw-queue
        commands, so no target needed a new renderer — see
        docs/RAYCAST_MINIMAP_PLAN.md. The geometry lives in
        extensions/raycast_2_5d/hud.build_minimap_commands so the export targets
        and the parity test share exactly this maths.

        No-ops silently when there's no current room (nothing to map).
        """
        from .hud import build_minimap_commands

        ae = self._executor(instance)
        if ae is None or not ae.game_runner:
            return
        room = getattr(ae.game_runner, "current_room", None)
        if room is None:
            return

        if not hasattr(instance, "_draw_queue"):
            instance._draw_queue = []

        # Resolve the camera exactly as the renderer does (renderer.py:
        # render_raycast_view) — via _find_first_instance on the config's
        # camera_object. NB _find_raycast_camera is a KIVY-only helper; looking
        # for it here silently yields no camera and no player marker.
        cfg = getattr(room, "raycast_camera", None) or {}
        camera = None
        finder = getattr(room, "_find_first_instance", None)
        if callable(finder):
            try:
                camera = finder(cfg.get("camera_object", ""))
            except Exception:
                camera = None

        # Camera position must be the same point the rays are cast from — the
        # origin-aware CENTRE of the camera's cell, not its raw x/y. Using the
        # raw corner would park the marker half a sprite off the view's actual
        # viewpoint (the 2026-07-17 exact-grid-line fix).
        cam_x = cam_y = None
        if camera is not None:
            top_left = getattr(room, "_sprite_top_left", None)
            if callable(top_left):
                cam_x, cam_y = top_left(camera)
            else:
                cam_x, cam_y = getattr(camera, "x", 0), getattr(camera, "y", 0)
            cam_x += (getattr(camera, "_cached_width", 0) or 0) / 2.0
            cam_y += (getattr(camera, "_cached_height", 0) or 0) / 2.0

        cmds = build_minimap_commands(
            v_walls=getattr(room, "_raycast_v_walls", None),
            h_walls=getattr(room, "_raycast_h_walls", None),
            cell_size=getattr(room, "_raycast_cell_size", 32) or 32,
            room_width=getattr(room, "width", 0),
            room_height=getattr(room, "height", 0),
            cam_x=cam_x,
            cam_y=cam_y,
            facing_angle=getattr(camera, "facing_angle", 0.0) if camera is not None else 0.0,
            x=float(parameters.get("x", 0)),
            y=float(parameters.get("y", 0)),
            size=float(parameters.get("size", 120)),
            back_color=parameters.get("back_color", "#101018"),
            wall_color=parameters.get("wall_color", "#8080a0"),
            player_color=parameters.get("player_color", "#ffd040"),
        )
        instance._draw_queue.extend(cmds)
