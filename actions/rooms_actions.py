#!/usr/bin/env python3
"""
GameMaker 8.0 Actions - Rooms Actions
"""

from actions.core import ActionDefinition, ActionParameter


ROOMS_ACTIONS = {
    "set_room_speed": ActionDefinition(
        name="set_room_speed",
        display_name="Set Room Speed",
        category="room_settings",
        tab="rooms",
        description="Set game speed (FPS)",
        icon="⏱️",
        parameters=[
            ActionParameter("speed", "int", "Speed", "Frames per second", default=30)
        ]
    ),
    "set_room_caption": ActionDefinition(
        name="set_room_caption",
        display_name="Set Room Caption",
        category="room_settings",
        tab="rooms",
        description="Set room caption text",
        icon="🏷️",
        parameters=[
            ActionParameter("caption", "string", "Caption", "Caption text", default="")
        ]
    ),
    "set_room_persistent": ActionDefinition(
        name="set_room_persistent",
        display_name="Set Room Persistent",
        category="room_settings",
        tab="rooms",
        description="Make room persistent",
        icon="💾",
        parameters=[
            ActionParameter("persistent", "boolean", "Persistent", "Keep room state", default=True)
        ]
    ),
    "set_background_color": ActionDefinition(
        name="set_background_color",
        display_name="Set Background Color",
        category="room_settings",
        tab="rooms",
        description="Set room background color",
        icon="🎨",
        parameters=[
            ActionParameter("color", "color", "Color", "Background color", default="#000000"),
            ActionParameter("show_color", "boolean", "Show Color", "Display background color", default=True)
        ]
    ),
    "set_background": ActionDefinition(
        name="set_background",
        display_name="Set Background Image",
        category="room_settings",
        tab="rooms",
        description="Set room background image",
        icon="🖼️",
        parameters=[
            ActionParameter("background", "background", "Background", "Background image"),
            ActionParameter("visible", "boolean", "Visible", "Show background", default=True),
            ActionParameter("foreground", "boolean", "Foreground", "Draw in front", default=False),
            ActionParameter("tiled_h", "boolean", "Tile Horizontal", "Tile horizontally", default=False),
            ActionParameter("tiled_v", "boolean", "Tile Vertical", "Tile vertically", default=False),
            ActionParameter("hspeed", "float", "H Speed", "Horizontal scroll speed", default=0),
            ActionParameter("vspeed", "float", "V Speed", "Vertical scroll speed", default=0)
        ]
    ),
    "enable_views": ActionDefinition(
        name="enable_views",
        display_name="Enable Views",
        category="room_settings",
        tab="rooms",
        description="Enable/disable view system",
        icon="👁️",
        parameters=[
            ActionParameter("enable", "boolean", "Enable", "Enable views", default=True)
        ]
    ),
    "set_view": ActionDefinition(
        name="set_view",
        display_name="Set View",
        category="room_settings",
        tab="rooms",
        description="Configure a view",
        icon="🔭",
        parameters=[
            ActionParameter("view", "int", "View", "View index (0-7)", default=0),
            ActionParameter("visible", "boolean", "Visible", "Enable this view", default=True),
            ActionParameter("view_x", "int", "View X", "View X in room", default=0),
            ActionParameter("view_y", "int", "View Y", "View Y in room", default=0),
            ActionParameter("view_w", "int", "View Width", "View width", default=640),
            ActionParameter("view_h", "int", "View Height", "View height", default=480),
            ActionParameter("port_x", "int", "Port X", "Screen X position", default=0),
            ActionParameter("port_y", "int", "Port Y", "Screen Y position", default=0),
            ActionParameter("port_w", "int", "Port Width", "Screen width", default=640),
            ActionParameter("port_h", "int", "Port Height", "Screen height", default=480),
            ActionParameter("follow", "object", "Follow Object", "Object to follow", default=None),
            ActionParameter("hborder", "int", "H Border", "Horizontal border", default=32),
            ActionParameter("vborder", "int", "V Border", "Vertical border", default=32),
            ActionParameter("hspeed", "int", "H Speed", "Max horizontal speed", default=-1),
            ActionParameter("vspeed", "int", "V Speed", "Max vertical speed", default=-1)
        ]
    ),
}

# ============================================================================
