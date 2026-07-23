#!/usr/bin/env python3
"""Action SCHEMAS the raycast extension contributes to the IDE.

Moved out of the static ``ACTION_TYPES`` dict in ``events/action_types.py``
(Stage B3, docs/RAYCAST_EXTENSION_PLAN.md): an optional feature's actions live
with the feature, not in core. The loader merges these into ``ACTION_TYPES`` at
startup (``events/plugin_loader.load_all_plugins``), so the action picker and
Blockly still see them — the schemas are byte-for-byte what core used to carry.

Handlers are in ``handlers.py`` (the ``PluginExecutor`` class). The ``3D View``
category groups them in the editor exactly as before.
"""
from events.action_types import ActionType, ActionParameter

PLUGIN_ACTIONS = {
    "set_facing_angle": ActionType(
        name="set_facing_angle",
        display_name="Set Facing Angle",
        description="Set the instance's look direction for a raycast (first-person) "
                    "camera — independent of movement speed",
        category="3D View",
        icon="🧭",
        parameters=[
            ActionParameter(name="angle", display_name="Angle", param_type="number",
                default_value=0,
                description="Degrees (0=right, 90=up, 180=left, 270=down)"),
            ActionParameter(name="relative", display_name="Relative", param_type="boolean",
                default_value=False, required=False,
                description="Add to the current facing angle instead of replacing it"),
        ]
    ),
    "draw_minimap": ActionType(
        name="draw_minimap",
        display_name="Draw Minimap",
        description="Draw a north-up minimap of the raycast room's walls, with "
                    "a marker showing where the camera is and which way it faces",
        category="3D View",
        icon="🗺️",
        parameters=[
            ActionParameter(name="x", display_name="X", param_type="number",
                default_value=0,
                description="Left edge of the minimap, in screen pixels"),
            ActionParameter(name="y", display_name="Y", param_type="number",
                default_value=0,
                description="Top edge of the minimap, in screen pixels"),
            ActionParameter(name="size", display_name="Size", param_type="number",
                default_value=120, required=False,
                description="Width and height of the minimap square, in pixels"),
            ActionParameter(name="back_color", display_name="Background Color",
                param_type="color", default_value="#101018", required=False,
                description="Panel colour behind the map"),
            ActionParameter(name="wall_color", display_name="Wall Color",
                param_type="color", default_value="#8080a0", required=False,
                description="Colour of the wall lines"),
            ActionParameter(name="player_color", display_name="Player Color",
                param_type="color", default_value="#ffd040", required=False,
                description="Colour of the camera marker and its heading line"),
        ],
    ),
    "enable_raycast_view": ActionType(
        name="enable_raycast_view",
        display_name="Enable Raycast View",
        description="Render the room as a Doom/Wolfenstein-style first-person "
                    "3D view (walls, sky, floor) instead of the top-down view",
        category="3D View",
        icon="🕹️",
        parameters=[
            ActionParameter(name="enable", display_name="Enable", param_type="boolean",
                default_value=True,
                description="On = first-person raycast view; off = normal top-down"),
            ActionParameter(name="camera_object", display_name="Camera Object",
                param_type="object", default_value="", required=False,
                description="Object whose position + facing angle is the camera "
                            "(blank = the object running this action)"),
            ActionParameter(name="fov", display_name="Field of View", param_type="number",
                default_value=66, required=False, description="Horizontal FOV in degrees"),
            ActionParameter(name="render_distance", display_name="Render Distance",
                param_type="number", default_value=20, required=False,
                description="Max ray length in grid cells"),
            ActionParameter(name="cell_size", display_name="Cell Size", param_type="number",
                default_value=32, required=False,
                description="Grid cell size in pixels (match the wall placement grid)"),
            ActionParameter(name="columns", display_name="Columns", param_type="number",
                default_value=320, required=False,
                description="Screen columns to raycast (lower = faster/chunkier)"),
            ActionParameter(name="wall_color", display_name="Wall Color", param_type="color",
                default_value="#993333", required=False,
                description="Flat wall colour when no wall texture is set"),
            ActionParameter(name="floor_color", display_name="Floor Color", param_type="color",
                default_value="#464632", required=False,
                description="Flat floor colour when no floor texture is set"),
            ActionParameter(name="ceiling_color", display_name="Ceiling Color", param_type="color",
                default_value="#87CEEB", required=False,
                description="Flat ceiling colour when no sky/ceiling texture is set"),
            ActionParameter(name="wall_texture", display_name="Wall Texture", param_type="sprite",
                default_value="", required=False,
                description="Sprite to texture every wall (blank = flat colour)"),
            ActionParameter(name="sky_texture", display_name="Sky Texture", param_type="sprite",
                default_value="", required=False,
                description="Sprite for a panning sky over the ceiling (blank = flat)"),
            ActionParameter(name="floor_texture", display_name="Floor Texture", param_type="sprite",
                default_value="", required=False,
                description="Sprite cast onto the floor (blank = flat colour)"),
            ActionParameter(name="ceiling_texture", display_name="Ceiling Texture",
                param_type="sprite", default_value="", required=False,
                description="Sprite cast onto the ceiling when no sky is set"),
            ActionParameter(name="wall_textured", display_name="Textured Walls",
                param_type="boolean", default_value=True, required=False,
                description="Off forces flat wall colours even when a texture is set"),
            ActionParameter(name="floor_cast_res", display_name="Floor Detail",
                param_type="number", default_value=4, required=False,
                description="Floor-cast downsample (higher = faster + chunkier)"),
            ActionParameter(name="viewport_height", display_name="Viewport Height",
                param_type="number", default_value=0, required=False,
                description="Letterbox the 3D view into this many pixels tall, "
                            "reserving the band below for a DOOM-style status bar "
                            "(0 = full window height, unchanged)"),
        ]
    ),
    "draw_doom_hud": ActionType(
        name="draw_doom_hud",
        display_name="Draw DOOM HUD",
        description="Draw a DOOM-style bottom status bar (health bar + number, "
                    "score, lives, an objective counter, and a health-reactive "
                    "face icon) over the raycast view",
        category="3D View",
        icon="🎯",
        parameters=[
            ActionParameter(name="x", display_name="X", param_type="number",
                default_value=0, description="Bar's left edge, in screen pixels"),
            ActionParameter(name="y", display_name="Y", param_type="number",
                default_value=-1, required=False,
                description="Bar's top edge; negative auto-aligns to the bottom "
                            "of the window, under the shrunk viewport"),
            ActionParameter(name="width", display_name="Width", param_type="number",
                default_value=0, required=False,
                description="Bar width (0 = full window width)"),
            ActionParameter(name="height", display_name="Height", param_type="number",
                default_value=42, required=False,
                description="Bar height; keep it matched to the viewport_height "
                            "band you reserved on enable_raycast_view"),
            ActionParameter(name="back_color", display_name="Background Color",
                param_type="color", default_value="#101010", required=False,
                description="Bar background panel"),
            ActionParameter(name="divider_color", display_name="Divider Color",
                param_type="color", default_value="#505050", required=False,
                description="Top border and the health-bar backing"),
            ActionParameter(name="text_color", display_name="Text Color",
                param_type="color", default_value="#ffffff", required=False,
                description="Colour of all bar text"),
            ActionParameter(name="health_label", display_name="Health Label",
                param_type="string", default_value="Health", required=False),
            ActionParameter(name="health_bar_width", display_name="Health Bar Width",
                param_type="number", default_value=90, required=False),
            ActionParameter(name="health_bar_height", display_name="Health Bar Height",
                param_type="number", default_value=14, required=False),
            ActionParameter(name="bar_color", display_name="Health Bar Color",
                param_type="color", default_value="#20c020", required=False,
                description="Fill colour of the health bar"),
            ActionParameter(name="face_sprite", display_name="Face Sprite",
                param_type="sprite", default_value="", required=False,
                description="Horizontal strip of face frames, healthiest first "
                            "(blank = no face icon)"),
            ActionParameter(name="face_frames", display_name="Face Frames",
                param_type="number", default_value=4, required=False,
                description="How many frames the face strip has; health is "
                            "bucketed evenly across them"),
            ActionParameter(name="score_label", display_name="Score Label",
                param_type="string", default_value="Score: ", required=False),
            ActionParameter(name="lives_sprite", display_name="Lives Sprite",
                param_type="sprite", default_value="", required=False,
                description="Sprite drawn once per remaining life"),
            ActionParameter(name="lives_scale", display_name="Lives Scale",
                param_type="number", default_value=1.0, required=False),
            ActionParameter(name="objective_value", display_name="Objective Value",
                param_type="string", default_value="0", required=False,
                description="Expression shown after the objective label (bind "
                            "your own key/quest variable)"),
            ActionParameter(name="objective_label", display_name="Objective Label",
                param_type="string", default_value="Keys: ", required=False),
        ],
    ),
}
