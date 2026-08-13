#!/usr/bin/env python3
"""Runtime handlers for the Block World extension's actions (Phase 2a).

Mirrors extensions/raycast_2_5d/handlers.py: a plugin's handlers run as
methods of a PluginExecutor instance, reaching the engine through
instance.action_executor (the plugins/audio_actions pattern), not through
ActionExecutor directly.
"""

from .state import block_world_state


class PluginExecutor:
    """Handles execution of the Block World setup action."""

    @staticmethod
    def _executor(instance):
        return getattr(instance, "action_executor", None)

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

        enable = ae._parse_value(parameters.get("enable", True), instance)
        if isinstance(enable, str):
            enable = enable.lower() in ("true", "1", "yes")

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
            raw = parameters.get(key, default)
            if isinstance(raw, str):
                return raw.strip().lower() in ("true", "1", "yes")
            return bool(raw)

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
            # Horizontal (top/bottom) faces cast every Nth screen row and
            # upscale the result; 0 falls back to a flat average colour,
            # which is cheaper on a scene showing a lot of deck.
            "top_cast_res": int(_num("top_cast_res", 4)),
        }
