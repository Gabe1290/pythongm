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
            ActionParameter(name="pitch", display_name="Look Angle",
                param_type="number", default_value=0, required=False,
                description="Degrees to look up (+) or down (-); 0 is level"),
            ActionParameter(name="wall_textured", display_name="Textured Blocks",
                param_type="boolean", default_value=True, required=False,
                description="Off forces flat block colours even though real "
                            "textures are available"),
            ActionParameter(name="top_cast_res", display_name="Top/Bottom Detail",
                param_type="number", default_value=4, required=False,
                description="Top/bottom face texture detail: rows sampled per N "
                            "screen rows (higher = faster + chunkier, 0 = flat "
                            "average colour instead of texture)"),
            ActionParameter(name="eye_height", display_name="Eye Height",
                param_type="number", default_value=1.5, required=False,
                description="Camera height above the layer it stands on, in "
                            "cells (1.5 = a two-block-tall body, needed to see "
                            "the top of a block on your own layer and stack "
                            "onto it)"),
            ActionParameter(name="gravity", display_name="Gravity",
                param_type="number", default_value=0, required=False,
                description="Downward acceleration in cells/step^2 for the "
                            "Jump action + gravity/falling (Tier 7a). 0 "
                            "(default) keeps Move And Collide's original "
                            "instant-footing behaviour with no jumping; a "
                            "typical value is around 0.04"),
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

    "set_look_pitch": ActionType(
        name="set_look_pitch",
        display_name="Look Up / Down",
        description="Tilt the block-world view up or down",
        category="3D View",
        icon="🔭",
        parameters=[
            ActionParameter(name="pitch", display_name="Angle", param_type="number",
                default_value=0,
                description="Degrees to look up (+) or down (-); 0 is level"),
            ActionParameter(name="relative", display_name="Relative",
                param_type="boolean", default_value=False, required=False,
                description="On = add to the current angle, for a look control "
                            "you can hold down; off = set it outright"),
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

    "select_hotbar_slot": ActionType(
        name="select_hotbar_slot",
        display_name="Select Hotbar Slot",
        description="Choose which block the hotbar has selected, for "
                    "place_block to build with -- bind Place Block's Block "
                    "parameter to the expression \"hotbar_block\" to use it",
        category="3D View",
        icon="🔢",
        parameters=[
            ActionParameter(name="index", display_name="Slot", param_type="number",
                default_value=0,
                description="Hotbar slot index, wrapping around at either end"),
            ActionParameter(name="relative", display_name="Relative",
                param_type="boolean", default_value=False, required=False,
                description="On = add to the current slot, for cycling with "
                            "[ ] / scroll-wheel style controls; off = jump to it"),
        ]
    ),

    "move_and_collide": ActionType(
        name="move_and_collide",
        display_name="Move And Collide",
        description="Move this step, checked against the block grid, with "
                    "automatic footing (step up one block, drop any "
                    "distance) -- the camera's z_layer follows if this is "
                    "the block-world camera",
        category="3D View",
        icon="🚶",
        parameters=[
            ActionParameter(name="dx", display_name="Dx", param_type="number",
                default_value=0,
                description="How far to move on x this step, in pixels"),
            ActionParameter(name="dy", display_name="Dy", param_type="number",
                default_value=0,
                description="How far to move on y this step, in pixels"),
            ActionParameter(name="collide", display_name="Collide",
                param_type="boolean", default_value=True, required=False,
                description="Off ignores the block grid entirely (flying/debug)"),
        ]
    ),

    "apply_gravity": ActionType(
        name="apply_gravity",
        display_name="Apply Gravity",
        description="Continuous falling/landing physics for the block-world "
                    "camera -- bind in the Step event (not a keyboard-held "
                    "event) so it runs every frame regardless of movement "
                    "input. No-op unless Enable Block World View's Gravity "
                    "parameter is set above 0",
        category="3D View",
        icon="⬇️",
        parameters=[],
    ),

    "jump": ActionType(
        name="jump",
        display_name="Jump",
        description="Give the block-world camera upward velocity -- only "
                    "while standing on solid ground (no double/air jumps). "
                    "Needs Gravity configured (Enable Block World View) and "
                    "Apply Gravity bound in the Step event, or nothing "
                    "brings it back down",
        category="3D View",
        icon="⬆️",
        parameters=[
            ActionParameter(name="speed", display_name="Jump Speed",
                param_type="number", default_value=0.35, required=False,
                description="Initial upward velocity, in cells/step"),
        ]
    ),

    "draw_block_world_hud": ActionType(
        name="draw_block_world_hud",
        display_name="Draw Block World HUD",
        description="Draw a crosshair plus a hotbar strip (the selected "
                    "slot highlighted) -- call from the player/camera "
                    "object's own Draw event",
        category="3D View",
        icon="🧰",
        parameters=[
            ActionParameter(name="slot_size", display_name="Slot Size",
                param_type="number", default_value=40, required=False,
                description="Width and height of each hotbar slot, in pixels"),
            ActionParameter(name="gap", display_name="Slot Gap", param_type="number",
                default_value=6, required=False,
                description="Space between hotbar slots, in pixels"),
            ActionParameter(name="margin_bottom", display_name="Bottom Margin",
                param_type="number", default_value=16, required=False,
                description="Space between the hotbar and the bottom of the screen"),
            ActionParameter(name="back_color", display_name="Slot Color",
                param_type="color", default_value="#202020", required=False,
                description="Fill colour of an unselected slot"),
            ActionParameter(name="selected_color", display_name="Selected Slot Color",
                param_type="color", default_value="#ffd040", required=False,
                description="Fill colour of the currently selected slot"),
            ActionParameter(name="border_color", display_name="Border Color",
                param_type="color", default_value="#ffffff", required=False,
                description="Outline colour of every slot"),
            ActionParameter(name="text_color", display_name="Text Color",
                param_type="color", default_value="#ffffff", required=False,
                description="Colour of each slot's block-type label"),
            ActionParameter(name="crosshair_size", display_name="Crosshair Size",
                param_type="number", default_value=12, required=False,
                description="Width and height of the centre crosshair, in pixels"),
            ActionParameter(name="crosshair_color", display_name="Crosshair Color",
                param_type="color", default_value="#ffffff", required=False,
                description="Colour of the centre crosshair"),
        ]
    ),

    "load_block_world": ActionType(
        name="load_block_world",
        display_name="Load Block World",
        description="Load a pre-authored world (blocks placed by a generator "
                    "or hand-authored file) into the current room, replacing "
                    "whatever blocks are there",
        category="3D View",
        icon="📂",
        parameters=[
            ActionParameter(name="data_file", display_name="Data File",
                param_type="string", default_value="",
                description="Path to a block-world JSON file, relative to the "
                            "project folder (e.g. blocks/room1.json)"),
        ]
    ),
}
