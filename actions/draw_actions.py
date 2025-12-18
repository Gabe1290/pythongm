#!/usr/bin/env python3
"""
GameMaker 8.0 Actions - Draw Actions
"""

from actions.core import ActionDefinition, ActionParameter


DRAW_ACTIONS = {
    "draw_sprite": ActionDefinition(
        name="draw_sprite",
        display_name="Draw Sprite",
        category="drawing",
        tab="draw",
        description="Draw a sprite at position",
        icon="🖼️",
        parameters=[
            ActionParameter("sprite", "sprite", "Sprite", "Sprite to draw"),
            ActionParameter("x", "int", "X", "X position", default=0),
            ActionParameter("y", "int", "Y", "Y position", default=0),
            ActionParameter("subimage", "int", "Subimage", "Frame index", default=0)
        ]
    ),
    "draw_background": ActionDefinition(
        name="draw_background",
        display_name="Draw Background",
        category="drawing",
        tab="draw",
        description="Draw a background image",
        icon="🖼️",
        parameters=[
            ActionParameter("background", "background", "Background", "Background to draw"),
            ActionParameter("x", "int", "X", "X position", default=0),
            ActionParameter("y", "int", "Y", "Y position", default=0),
            ActionParameter("tiled", "boolean", "Tiled", "Tile the background", default=False)
        ]
    ),
    "draw_text": ActionDefinition(
        name="draw_text",
        display_name="Draw Text",
        category="drawing",
        tab="draw",
        description="Draw text on screen",
        icon="📝",
        parameters=[
            ActionParameter("x", "int", "X", "X position", default=0),
            ActionParameter("y", "int", "Y", "Y position", default=0),
            ActionParameter("text", "string", "Text", "Text to display", default="")
        ]
    ),
    "draw_scaled_text": ActionDefinition(
        name="draw_scaled_text",
        display_name="Draw Scaled Text",
        category="drawing",
        tab="draw",
        description="Draw scaled text",
        icon="📝",
        parameters=[
            ActionParameter("x", "int", "X", "X position", default=0),
            ActionParameter("y", "int", "Y", "Y position", default=0),
            ActionParameter("text", "string", "Text", "Text to display", default=""),
            ActionParameter("xscale", "float", "X Scale", "Horizontal scale", default=1.0),
            ActionParameter("yscale", "float", "Y Scale", "Vertical scale", default=1.0)
        ]
    ),
    "draw_rectangle": ActionDefinition(
        name="draw_rectangle",
        display_name="Draw Rectangle",
        category="drawing",
        tab="draw",
        description="Draw a rectangle",
        icon="▭",
        parameters=[
            ActionParameter("x1", "int", "X1", "Left", default=0),
            ActionParameter("y1", "int", "Y1", "Top", default=0),
            ActionParameter("x2", "int", "X2", "Right", default=100),
            ActionParameter("y2", "int", "Y2", "Bottom", default=100),
            ActionParameter("filled", "boolean", "Filled", "Fill rectangle", default=False)
        ]
    ),
    "draw_ellipse": ActionDefinition(
        name="draw_ellipse",
        display_name="Draw Ellipse",
        category="drawing",
        tab="draw",
        description="Draw an ellipse",
        icon="⭕",
        parameters=[
            ActionParameter("x1", "int", "X1", "Left", default=0),
            ActionParameter("y1", "int", "Y1", "Top", default=0),
            ActionParameter("x2", "int", "X2", "Right", default=100),
            ActionParameter("y2", "int", "Y2", "Bottom", default=100),
            ActionParameter("filled", "boolean", "Filled", "Fill ellipse", default=False)
        ]
    ),
    "draw_line": ActionDefinition(
        name="draw_line",
        display_name="Draw Line",
        category="drawing",
        tab="draw",
        description="Draw a line",
        icon="➖",
        parameters=[
            ActionParameter("x1", "int", "X1", "Start X", default=0),
            ActionParameter("y1", "int", "Y1", "Start Y", default=0),
            ActionParameter("x2", "int", "X2", "End X", default=100),
            ActionParameter("y2", "int", "Y2", "End Y", default=100)
        ]
    ),
    "draw_arrow": ActionDefinition(
        name="draw_arrow",
        display_name="Draw Arrow",
        category="drawing",
        tab="draw",
        description="Draw an arrow",
        icon="➡️",
        parameters=[
            ActionParameter("x1", "int", "X1", "Start X", default=0),
            ActionParameter("y1", "int", "Y1", "Start Y", default=0),
            ActionParameter("x2", "int", "X2", "End X", default=100),
            ActionParameter("y2", "int", "Y2", "End Y", default=100),
            ActionParameter("tip_size", "int", "Tip Size", "Arrow tip size", default=10)
        ]
    ),
    "set_draw_color": ActionDefinition(
        name="set_draw_color",
        display_name="Set Drawing Color",
        category="drawing",
        tab="draw",
        description="Set color for drawing",
        icon="🎨",
        parameters=[
            ActionParameter("color", "color", "Color", "Drawing color", default="#000000")
        ]
    ),
    "set_draw_font": ActionDefinition(
        name="set_draw_font",
        display_name="Set Font",
        category="drawing",
        tab="draw",
        description="Set text font",
        icon="🔤",
        parameters=[
            ActionParameter("font", "font", "Font", "Font to use"),
            ActionParameter("halign", "choice", "Horizontal Align", "Text alignment",
                          default="left", options=["left", "center", "right"]),
            ActionParameter("valign", "choice", "Vertical Align", "Vertical alignment",
                          default="top", options=["top", "middle", "bottom"])
        ]
    ),
    "fill_color": ActionDefinition(
        name="fill_color",
        display_name="Fill Color",
        category="drawing",
        tab="draw",
        description="Fill screen with color",
        icon="🎨",
        parameters=[
            ActionParameter("color", "color", "Color", "Fill color", default="#000000")
        ]
    ),
    "create_effect": ActionDefinition(
        name="create_effect",
        display_name="Create Effect",
        category="drawing",
        tab="draw",
        description="Create visual effect",
        icon="✨",
        parameters=[
            ActionParameter("effect", "choice", "Effect", "Effect type",
                          options=["explosion", "ring", "ellipse", "firework", "smoke", "smoke_up", "star", "spark", "flare", "cloud", "rain", "snow"]),
            ActionParameter("x", "int", "X", "X position", default=0),
            ActionParameter("y", "int", "Y", "Y position", default=0),
            ActionParameter("size", "choice", "Size", "Effect size",
                          default="medium", options=["small", "medium", "large"]),
            ActionParameter("color", "color", "Color", "Effect color", default="#FFFFFF")
        ]
    ),
    # Animation actions
    "set_image_index": ActionDefinition(
        name="set_image_index",
        display_name="Set Animation Frame",
        category="drawing",
        tab="draw",
        description="Set the current animation frame",
        icon="🎬",
        parameters=[
            ActionParameter("frame", "int", "Frame", "Frame number (0-based)", default=0)
        ]
    ),
    "set_image_speed": ActionDefinition(
        name="set_image_speed",
        display_name="Set Animation Speed",
        category="drawing",
        tab="draw",
        description="Set animation speed multiplier (0=stopped, 1=normal)",
        icon="⏩",
        parameters=[
            ActionParameter("speed", "float", "Speed", "Speed multiplier", default=1.0)
        ]
    ),
    "stop_animation": ActionDefinition(
        name="stop_animation",
        display_name="Stop Animation",
        category="drawing",
        tab="draw",
        description="Stop the sprite animation",
        icon="⏸️",
        parameters=[]
    ),
    "start_animation": ActionDefinition(
        name="start_animation",
        display_name="Start Animation",
        category="drawing",
        tab="draw",
        description="Start/resume the sprite animation",
        icon="▶️",
        parameters=[]
    ),
}

# ============================================================================
