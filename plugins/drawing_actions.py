#!/usr/bin/env python3
"""
Drawing Actions Plugin
Adds drawing and visual effect actions to PyGameMaker
"""

from events.action_types import ActionType, ActionParameter

# Plugin Metadata
PLUGIN_NAME = "Drawing Actions"
PLUGIN_VERSION = "1.0.0"
PLUGIN_AUTHOR = "PyGameMaker Team"
PLUGIN_DESCRIPTION = "Adds drawing and visual effect actions"

# Define drawing actions
PLUGIN_ACTIONS = {
    "draw_text": ActionType(
        name="draw_text",
        display_name="Draw Text",
        description="Draw text at a position",
        category="Drawing",
        icon="📝",
        parameters=[
            ActionParameter(
                name="text",
                display_name="Text",
                param_type="string",
                default_value="Hello!",
                description="Text to draw"
            ),
            ActionParameter(
                name="position",
                display_name="Position",
                param_type="position",
                default_value=[0, 0],
                description="X,Y position"
            ),
            ActionParameter(
                name="color",
                display_name="Color",
                param_type="color",
                default_value="#FFFFFF",
                description="Text color"
            ),
            ActionParameter(
                name="size",
                display_name="Font Size",
                param_type="number",
                default_value=24,
                description="Font size in pixels",
                min_value=8,
                max_value=128
            )
        ]
    ),

    "draw_rectangle": ActionType(
        name="draw_rectangle",
        display_name="Draw Rectangle",
        description="Draw a filled rectangle",
        category="Drawing",
        icon="▭",
        parameters=[
            ActionParameter(
                name="position",
                display_name="Position",
                param_type="position",
                default_value=[0, 0],
                description="X,Y position"
            ),
            ActionParameter(
                name="width",
                display_name="Width",
                param_type="number",
                default_value=100,
                description="Rectangle width"
            ),
            ActionParameter(
                name="height",
                display_name="Height",
                param_type="number",
                default_value=100,
                description="Rectangle height"
            ),
            ActionParameter(
                name="color",
                display_name="Color",
                param_type="color",
                default_value="#FF0000",
                description="Fill color"
            )
        ]
    ),

    "draw_circle": ActionType(
        name="draw_circle",
        display_name="Draw Circle",
        description="Draw a filled circle",
        category="Drawing",
        icon="⭕",
        parameters=[
            ActionParameter(
                name="position",
                display_name="Center Position",
                param_type="position",
                default_value=[0, 0],
                description="Circle center X,Y"
            ),
            ActionParameter(
                name="radius",
                display_name="Radius",
                param_type="number",
                default_value=50,
                description="Circle radius",
                min_value=1,
                max_value=500
            ),
            ActionParameter(
                name="color",
                display_name="Color",
                param_type="color",
                default_value="#0000FF",
                description="Fill color"
            )
        ]
    ),

    "set_sprite": ActionType(
        name="set_sprite",
        display_name="Set Sprite",
        description="Change the sprite of this instance",
        category="Drawing",
        icon="🖼️",
        parameters=[
            ActionParameter(
                name="sprite",
                display_name="Sprite",
                param_type="sprite",
                default_value="",
                description="Sprite to use"
            )
        ]
    ),

    "set_alpha": ActionType(
        name="set_alpha",
        display_name="Set Transparency",
        description="Set sprite transparency (alpha)",
        category="Drawing",
        icon="👻",
        parameters=[
            ActionParameter(
                name="alpha",
                display_name="Alpha",
                param_type="float",
                default_value=1.0,
                description="Transparency (0.0 = invisible, 1.0 = solid)",
                min_value=0,
                max_value=1
            )
        ]
    ),
}


# Action executors
class PluginExecutor:
    """Handles execution of drawing actions"""

    def execute_draw_text_action(self, instance, parameters):
        """Draw text on screen"""
        text = parameters.get("text", "")
        position = parameters.get("position", [0, 0])
        color = parameters.get("color", "#FFFFFF")
        size = int(parameters.get("size", 24))

        print(f"📝 Drawing text: '{text}' at {position}")

        # Store drawing command for game renderer
        if not hasattr(instance, 'draw_commands'):
            instance.draw_commands = []

        instance.draw_commands.append({
            'type': 'text',
            'text': text,
            'x': position[0],
            'y': position[1],
            'color': self._parse_color(color),
            'size': size
        })

    def execute_draw_rectangle_action(self, instance, parameters):
        """Draw a rectangle"""
        position = parameters.get("position", [0, 0])
        width = int(parameters.get("width", 100))
        height = int(parameters.get("height", 100))
        color = parameters.get("color", "#FF0000")

        print(f"▭ Drawing rectangle at {position}, size {width}x{height}")

        if not hasattr(instance, 'draw_commands'):
            instance.draw_commands = []

        instance.draw_commands.append({
            'type': 'rectangle',
            'x': position[0],
            'y': position[1],
            'width': width,
            'height': height,
            'color': self._parse_color(color)
        })

    def execute_draw_circle_action(self, instance, parameters):
        """Draw a circle"""
        position = parameters.get("position", [0, 0])
        radius = int(parameters.get("radius", 50))
        color = parameters.get("color", "#0000FF")

        print(f"⭕ Drawing circle at {position}, radius {radius}")

        if not hasattr(instance, 'draw_commands'):
            instance.draw_commands = []

        instance.draw_commands.append({
            'type': 'circle',
            'x': position[0],
            'y': position[1],
            'radius': radius,
            'color': self._parse_color(color)
        })

    def execute_set_sprite_action(self, instance, parameters):
        """Change instance sprite"""
        sprite_name = parameters.get("sprite", "")

        print(f"🖼️  Setting sprite to: {sprite_name}")

        try:
            if hasattr(instance, 'game') and hasattr(instance.game, 'sprites'):
                if sprite_name in instance.game.sprites:
                    instance.sprite = instance.game.sprites[sprite_name]
                    instance.sprite_name = sprite_name
                else:
                    print(f"⚠️  Sprite not found: {sprite_name}")
        except Exception as e:
            print(f"❌ Error setting sprite: {e}")

    def execute_set_alpha_action(self, instance, parameters):
        """Set instance transparency"""
        alpha = float(parameters.get("alpha", 1.0))

        print(f"👻 Setting alpha to: {alpha}")

        # Store alpha value
        instance.alpha = alpha

        # If instance has a sprite, apply alpha
        if hasattr(instance, 'sprite') and instance.sprite:
            try:
                alpha_value = int(alpha * 255)
                instance.sprite.set_alpha(alpha_value)
            except Exception as e:
                print(f"❌ Error setting alpha: {e}")

    def _parse_color(self, color_str: str) -> tuple:
        """Parse hex color string to RGB tuple"""
        try:
            if color_str.startswith('#'):
                color_str = color_str[1:]
            r = int(color_str[0:2], 16)
            g = int(color_str[2:4], 16)
            b = int(color_str[4:6], 16)
            return (r, g, b)
        except:
            return (255, 255, 255)  # Default to white
