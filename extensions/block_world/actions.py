#!/usr/bin/env python3
"""Action SCHEMAS the Block World extension contributes to the IDE.

Phase 2a of docs/VOXEL_WORLD_PLAN.md: one action, enable_block_world_view,
mirroring extensions/raycast_2_5d/actions.py's enable_raycast_view -- the
minimal camera/config plumbing the renderer (renderer.py) needs to know
which room to claim and how to project it. Handlers are in handlers.py (the
PluginExecutor class). The loader merges this into ACTION_TYPES at startup.
"""
from events.action_types import ActionType, ActionParameter

from .state import BLOCK_TYPES

# Offered as a dropdown rather than a typed string: these are the block ids
# the CC0 texture registry actually knows, and a typo would otherwise be a
# silent no-op at runtime.
_BLOCK_CHOICES = sorted(BLOCK_TYPES)

PLUGIN_ACTIONS = {
    "enable_block_world_view": ActionType(
        name="enable_block_world_view",
        display_name="Enable Block World View",
        description="Render the room as a first-person voxel view (single "
                    "layer) instead of the top-down view",
        category="3D View",
        icon="🧱",
        parameters=[
            ActionParameter(name="enable", display_name="Enable", param_type="boolean",
                default_value=True,
                description="On = first-person block view; off = normal top-down"),
            ActionParameter(name="camera_object", display_name="Camera Object",
                param_type="object", default_value="", required=False,
                description="Object whose position + facing angle is the camera "
                            "(blank = the object running this action)"),
            ActionParameter(name="z_layer", display_name="Layer", param_type="number",
                default_value=0, required=False,
                description="Which world layer to render (Phase 2a renders exactly "
                            "one layer -- no looking up/down yet)"),
            ActionParameter(name="fov", display_name="Field of View", param_type="number",
                default_value=66, required=False, description="Horizontal FOV in degrees"),
            ActionParameter(name="render_distance", display_name="Render Distance",
                param_type="number", default_value=20, required=False,
                description="Max ray length in grid cells"),
            ActionParameter(name="cell_size", display_name="Cell Size", param_type="number",
                default_value=32, required=False,
                description="Grid cell size in pixels (match the block-placement grid)"),
            ActionParameter(name="columns", display_name="Columns", param_type="number",
                default_value=320, required=False,
                description="Screen columns to raycast (lower = faster/chunkier)"),
            ActionParameter(name="wall_color", display_name="Fallback Block Color",
                param_type="color", default_value="#8a8a8a", required=False,
                description="Flat colour used only if Textured Blocks is off"),
            ActionParameter(name="floor_color", display_name="Floor Color", param_type="color",
                default_value="#3a2f1c", required=False,
                description="Flat floor colour (Phase 2a has no floor texturing yet)"),
            ActionParameter(name="ceiling_color", display_name="Ceiling Color", param_type="color",
                default_value="#87CEEB", required=False,
                description="Flat ceiling/sky colour (Phase 2a has no sky yet)"),
            ActionParameter(name="wall_textured", display_name="Textured Blocks",
                param_type="boolean", default_value=True, required=False,
                description="Off forces flat block colours even though real "
                            "textures are available"),
        ]
    ),

    "place_block": ActionType(
        name="place_block",
        display_name="Place Block",
        description="Put a block in the empty cell the camera is looking at",
        category="3D View",
        icon="🧱",
        parameters=[
            ActionParameter(name="block", display_name="Block", param_type="choice",
                default_value="stone", choices=_BLOCK_CHOICES,
                description="Which kind of block to place"),
            ActionParameter(name="reach", display_name="Reach", param_type="number",
                default_value=5, required=False,
                description="How many cells ahead you can build, in grid cells"),
        ]
    ),

    "break_block": ActionType(
        name="break_block",
        display_name="Break Block",
        description="Remove the block the camera is looking at",
        category="3D View",
        icon="⛏️",
        parameters=[
            ActionParameter(name="reach", display_name="Reach", param_type="number",
                default_value=5, required=False,
                description="How many cells ahead you can reach, in grid cells"),
        ]
    ),
}
