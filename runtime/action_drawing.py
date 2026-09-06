#!/usr/bin/env python3
"""Drawing actions for :class:`~runtime.action_executor.ActionExecutor`.

The 13 ``execute_draw_*_action`` methods — text, scaled text, rectangle,
ellipse, circle, line, sprite, background, arrow, variable, plus the score /
lives / health-bar readouts. Every one of them ends by appending a command to
the instance's draw queue rather than touching a surface, which is what makes
them separable at all: they share no state with each other.

Extracted verbatim from ``runtime/action_executor.py``
(``docs/POST_1_0_REFACTOR.md`` File 4, cluster 1) as a MIXIN, the same
technique ``runtime/input_handler.py`` and ``runtime/collision.py`` used for
File 3 — these are ``ActionExecutor`` methods reached through ``self``, not a
separable object.

**Why a sibling module and not the package layout the plan sketched.** The
plan proposed turning ``runtime/action_executor.py`` into a
``runtime/action_executor/`` package. That would break 35 test files: they
load the engine with ``import_module_directly("runtime/action_executor.py")``,
a ``spec_from_file_location`` helper that deliberately bypasses ``__init__.py``
so the module can be imported *without pygame or PySide6* — a property
``runtime/__init__.py`` documents and this module's own import list (math, re,
typing, core.logger) exists to preserve. A sibling module keeps that path, and
keeps this file equally light.

The four helpers these methods lean on — ``_parse_value``, ``_parse_color``,
``_resolve_draw_color``, ``_is_relative``, ``localize_param`` — deliberately
stay on ``ActionExecutor``: the plan's own risk callout says helpers called
from many action methods belong on the base, not on one mixin.
"""

import math
from typing import Any, Dict

from core.logger import get_logger

logger = get_logger(__name__)


class DrawingMixin:
    """``execute_draw_*_action`` methods, mixed into ``ActionExecutor``."""

    def execute_draw_score_action(self, instance, parameters: Dict[str, Any]):
        """Draw score on screen (queued for draw event)"""
        if not self.game_runner:
            return

        x = int(parameters.get("x", 0))
        y = int(parameters.get("y", 0))
        if self._is_relative(parameters):
            x += int(instance.x)
            y += int(instance.y)
        caption = self.localize_param(parameters, "caption", "Score: ")

        # Store draw command for rendering
        if not hasattr(instance, '_draw_queue'):
            instance._draw_queue = []

        instance._draw_queue.append({
            'type': 'text',
            'text': f"{caption}{self.game_runner.score}",
            'x': x,
            'y': y,
            # Respect the active draw colour; white preserves the prior look
            # when no Set Draw Color action has run.
            'color': self._resolve_draw_color(instance, (255, 255, 255))
        })
    def execute_draw_lives_action(self, instance, parameters: Dict[str, Any]):
        """Draw lives as sprite images"""
        if not self.game_runner:
            return

        x = int(parameters.get("x", 0))
        y = int(parameters.get("y", 0))
        if self._is_relative(parameters):
            x += int(instance.x)
            y += int(instance.y)
        # GM's action_draw_life_images calls the sprite argument "image" (and
        # the GMK importer emits it as such); accept both names.
        sprite_name = parameters.get("sprite") or parameters.get("image", "")
        try:
            scale = float(parameters.get("scale", 1.0))
        except (ValueError, TypeError):
            scale = 1.0

        # Queue lives drawing
        if not hasattr(instance, '_draw_queue'):
            instance._draw_queue = []

        instance._draw_queue.append({
            'type': 'lives',
            'count': self.game_runner.lives,
            'x': x,
            'y': y,
            'sprite': sprite_name,
            'scale': scale
        })
    def execute_draw_health_bar_action(self, instance, parameters: Dict[str, Any]):
        """Draw health as a bar"""
        if not self.game_runner:
            return

        x1 = int(parameters.get("x1", 0))
        y1 = int(parameters.get("y1", 0))
        x2 = int(parameters.get("x2", 100))
        y2 = int(parameters.get("y2", 20))
        back_color = parameters.get("back_color", "#FF0000")
        bar_color = parameters.get("bar_color", "#00FF00")

        # Queue health bar drawing
        if not hasattr(instance, '_draw_queue'):
            instance._draw_queue = []

        instance._draw_queue.append({
            'type': 'health_bar',
            'x1': x1,
            'y1': y1,
            'x2': x2,
            'y2': y2,
            'health': self.game_runner.health,
            'back_color': back_color,
            'bar_color': bar_color
        })
    def execute_draw_text_action(self, instance, parameters: Dict[str, Any]):
        """Draw text at specified position

        Parameters:
            x: X coordinate (default: instance.x)
            y: Y coordinate (default: instance.y)
            text: Text string to draw (supports expressions)
        """

        # Parse parameters with expression support
        x = self._parse_value(parameters.get("x", instance.x), instance)
        y = self._parse_value(parameters.get("y", instance.y), instance)
        if self._is_relative(parameters):
            x += instance.x
            y += instance.y
        text = str(self._parse_value(
            self.localize_param(parameters, "text", ""), instance))

        # Colour: an explicit `color`/`colour` param wins (GM's draw_text has
        # no colour arg, but authors and every bundled sample reasonably
        # expect one -- without this the text fell back to the active
        # set_draw_color, i.e. black, and vanished on a dark background),
        # then the active set_draw_color, then black.
        color_param = parameters.get("color", parameters.get("colour"))
        if color_param not in (None, ""):
            color = self._parse_color(str(self._parse_value(color_param, instance)))
        else:
            color = self._resolve_draw_color(instance, (0, 0, 0))

        # Queue drawing command for draw event
        if not hasattr(instance, '_draw_queue'):
            instance._draw_queue = []

        instance._draw_queue.append({
            'type': 'text',
            'x': x,
            'y': y,
            'text': text,
            'color': color,
            # Captured at QUEUE time, not render time — the whole draw event's
            # actions run before _process_draw_queue renders any of them, so
            # reading instance.draw_halign at render time would apply
            # whatever set_draw_font call happened to run LAST in the event
            # to every queued text command, not the alignment that was
            # active when each one was actually drawn (a real bug: a draw
            # event with "set_draw_font center, draw_text A, set_draw_font
            # left, draw_text B" rendered BOTH A and B left-aligned).
            'halign': getattr(instance, 'draw_halign', 'left'),
            'valign': getattr(instance, 'draw_valign', 'top'),
        })

        logger.debug(f"📝 Queued draw_text: '{text}' at ({x}, {y}) with color {color}")
    def execute_draw_scaled_text_action(self, instance, parameters: Dict[str, Any]):
        """Draw scaled text at specified position

        Parameters:
            x: X coordinate (default: 0)
            y: Y coordinate (default: 0)
            text: Text string to draw (supports expressions)
            xscale: Horizontal scale factor (default: 1.0)
            yscale: Vertical scale factor (default: 1.0)
        """
        # Parse parameters with expression support
        x = self._parse_value(parameters.get("x", 0), instance)
        y = self._parse_value(parameters.get("y", 0), instance)
        text = str(self._parse_value(
            self.localize_param(parameters, "text", ""), instance))
        xscale = self._parse_value(parameters.get("xscale", 1.0), instance)
        yscale = self._parse_value(parameters.get("yscale", 1.0), instance)

        # Convert scale values to float
        try:
            xscale = float(xscale)
            yscale = float(yscale)
        except (ValueError, TypeError):
            xscale = 1.0
            yscale = 1.0

        # Get drawing color (from instance or default black)
        color = getattr(instance, 'draw_color', (0, 0, 0))

        # Queue drawing command for draw event
        if not hasattr(instance, '_draw_queue'):
            instance._draw_queue = []

        instance._draw_queue.append({
            'type': 'scaled_text',
            'x': x,
            'y': y,
            'text': text,
            'xscale': xscale,
            'yscale': yscale,
            'color': color,
            # See execute_draw_text_action's comment: must be captured at
            # queue time, not read from the instance at render time.
            'halign': getattr(instance, 'draw_halign', 'left'),
            'valign': getattr(instance, 'draw_valign', 'top'),
        })

        logger.debug(f"📝 Queued draw_scaled_text: '{text}' at ({x}, {y}) scale ({xscale}, {yscale})")
    def execute_draw_rectangle_action(self, instance, parameters: Dict[str, Any]):
        """Draw a rectangle (filled or outlined)

        Parameters:
            x1: Left X coordinate
            y1: Top Y coordinate
            x2: Right X coordinate
            y2: Bottom Y coordinate
            filled: True for filled, False for outline (default: True)
        """

        # Parse parameters with expression support
        x1 = self._parse_value(parameters.get("x1", 0), instance)
        y1 = self._parse_value(parameters.get("y1", 0), instance)
        x2 = self._parse_value(parameters.get("x2", 100), instance)
        y2 = self._parse_value(parameters.get("y2", 100), instance)
        filled = self._parse_value(parameters.get("filled", True), instance)

        # Convert to boolean if string
        if isinstance(filled, str):
            filled = filled.lower() in ('true', '1', 'yes')

        # Get drawing color (from instance or default black)
        color = getattr(instance, 'draw_color', (0, 0, 0))

        # Queue drawing command for draw event
        if not hasattr(instance, '_draw_queue'):
            instance._draw_queue = []

        instance._draw_queue.append({
            'type': 'rectangle',
            'x1': x1,
            'y1': y1,
            'x2': x2,
            'y2': y2,
            'filled': filled,
            'color': color
        })

        fill_type = "filled" if filled else "outline"
        logger.debug(f"📐 Queued draw_rectangle: {fill_type} rect ({x1}, {y1}) to ({x2}, {y2}) with color {color}")
    def execute_draw_ellipse_action(self, instance, parameters: Dict[str, Any]):
        """Draw an ellipse or circle (filled or outlined)

        Parameters:
            x1: Left X coordinate
            y1: Top Y coordinate
            x2: Right X coordinate
            y2: Bottom Y coordinate
            filled: True for filled, False for outline (default: True)
        """

        # Parse parameters with expression support
        x1 = self._parse_value(parameters.get("x1", 0), instance)
        y1 = self._parse_value(parameters.get("y1", 0), instance)
        x2 = self._parse_value(parameters.get("x2", 100), instance)
        y2 = self._parse_value(parameters.get("y2", 100), instance)
        filled = self._parse_value(parameters.get("filled", True), instance)

        # Convert to boolean if string
        if isinstance(filled, str):
            filled = filled.lower() in ('true', '1', 'yes')

        # Get drawing color (from instance or default black)
        color = getattr(instance, 'draw_color', (0, 0, 0))

        # Queue drawing command for draw event
        if not hasattr(instance, '_draw_queue'):
            instance._draw_queue = []

        instance._draw_queue.append({
            'type': 'ellipse',
            'x1': x1,
            'y1': y1,
            'x2': x2,
            'y2': y2,
            'filled': filled,
            'color': color
        })

        fill_type = "filled" if filled else "outline"
        logger.debug(f"⭕ Queued draw_ellipse: {fill_type} ellipse ({x1}, {y1}) to ({x2}, {y2}) with color {color}")
    def execute_draw_circle_action(self, instance, parameters: Dict[str, Any]):
        """Draw a circle (filled or outlined)

        Parameters:
            x: Center X coordinate
            y: Center Y coordinate
            radius: Circle radius
            filled: True for filled, False for outline (default: True)
        """

        # Parse parameters with expression support
        x = self._parse_value(parameters.get("x", 0), instance)
        y = self._parse_value(parameters.get("y", 0), instance)
        radius = self._parse_value(parameters.get("radius", 50), instance)
        filled = self._parse_value(parameters.get("filled", True), instance)

        # Convert to boolean if string
        if isinstance(filled, str):
            filled = filled.lower() in ('true', '1', 'yes')

        # Get drawing color (from instance or default black)
        color = getattr(instance, 'draw_color', (0, 0, 0))

        # Queue drawing command for draw event
        if not hasattr(instance, '_draw_queue'):
            instance._draw_queue = []

        instance._draw_queue.append({
            'type': 'circle',
            'x': x,
            'y': y,
            'radius': radius,
            'filled': filled,
            'color': color
        })

        fill_type = "filled" if filled else "outline"
        logger.debug(f"⚫ Queued draw_circle: {fill_type} circle at ({x}, {y}) radius {radius} with color {color}")
    def execute_draw_line_action(self, instance, parameters: Dict[str, Any]):
        """Draw a line between two points

        Parameters:
            x1: Start X coordinate
            y1: Start Y coordinate
            x2: End X coordinate
            y2: End Y coordinate
        """

        # Parse parameters with expression support
        x1 = self._parse_value(parameters.get("x1", 0), instance)
        y1 = self._parse_value(parameters.get("y1", 0), instance)
        x2 = self._parse_value(parameters.get("x2", 100), instance)
        y2 = self._parse_value(parameters.get("y2", 100), instance)

        # Get drawing color (from instance or default black)
        color = getattr(instance, 'draw_color', (0, 0, 0))

        # Queue drawing command for draw event
        if not hasattr(instance, '_draw_queue'):
            instance._draw_queue = []

        instance._draw_queue.append({
            'type': 'line',
            'x1': x1,
            'y1': y1,
            'x2': x2,
            'y2': y2,
            'color': color
        })

        logger.debug(f"➖ Queued draw_line: from ({x1}, {y1}) to ({x2}, {y2}) with color {color}")
    def execute_draw_sprite_action(self, instance, parameters: Dict[str, Any]):
        """Draw a sprite at specified position

        Parameters:
            sprite: Name of the sprite to draw
            x: X coordinate (default: 0)
            y: Y coordinate (default: 0)
            subimage: Frame index for animated sprites (default: 0)
        """

        # Parse parameters with expression support
        sprite_name = self._parse_value(parameters.get("sprite", ""), instance)
        x = self._parse_value(parameters.get("x", 0), instance)
        y = self._parse_value(parameters.get("y", 0), instance)
        subimage = self._parse_value(parameters.get("subimage", 0), instance)
        try:
            scale = float(parameters.get("scale", 1.0))
        except (ValueError, TypeError):
            scale = 1.0

        # Queue drawing command for draw event
        if not hasattr(instance, '_draw_queue'):
            instance._draw_queue = []

        instance._draw_queue.append({
            'type': 'sprite',
            'sprite_name': sprite_name,
            'x': x,
            'y': y,
            'subimage': subimage,
            'scale': scale
        })

        logger.debug(f"🖼️ Queued draw_sprite: '{sprite_name}' at ({x}, {y}) frame {subimage}")
    def execute_draw_background_action(self, instance, parameters: Dict[str, Any]):
        """Draw a background image at specified position with optional tiling

        Parameters:
            background: Name of the background to draw
            x: X coordinate (default: 0)
            y: Y coordinate (default: 0)
            tiled: Whether to tile the background across the screen (default: False)
        """
        # Parse parameters with expression support
        bg_name = self._parse_value(parameters.get("background", ""), instance)
        x = self._parse_value(parameters.get("x", 0), instance)
        y = self._parse_value(parameters.get("y", 0), instance)
        tiled = self._parse_value(parameters.get("tiled", False), instance)

        # Convert tiled to boolean if string
        if isinstance(tiled, str):
            tiled = tiled.lower() in ('true', '1', 'yes')

        # Queue drawing command for draw event
        if not hasattr(instance, '_draw_queue'):
            instance._draw_queue = []

        instance._draw_queue.append({
            'type': 'background',
            'background_name': bg_name,
            'x': x,
            'y': y,
            'tiled': tiled
        })

        tiled_str = " (tiled)" if tiled else ""
        logger.debug(f"🖼️ Queued draw_background: '{bg_name}' at ({x}, {y}){tiled_str}")
    def execute_draw_arrow_action(self, instance, parameters: Dict[str, Any]):
        """Draw an arrow from one point to another with configurable tip

        Parameters:
            x1: Start X coordinate
            y1: Start Y coordinate
            x2: End X coordinate (arrow head)
            y2: End Y coordinate (arrow head)
            tip_size: Size of the arrow tip (default: 10)
        """

        # Parse parameters with expression support
        x1 = self._parse_value(parameters.get("x1", 0), instance)
        y1 = self._parse_value(parameters.get("y1", 0), instance)
        x2 = self._parse_value(parameters.get("x2", 100), instance)
        y2 = self._parse_value(parameters.get("y2", 100), instance)
        tip_size = self._parse_value(parameters.get("tip_size", 10), instance)

        try:
            x1 = int(x1) if x1 is not None else 0
            y1 = int(y1) if y1 is not None else 0
            x2 = int(x2) if x2 is not None else 100
            y2 = int(y2) if y2 is not None else 100
            tip_size = int(tip_size) if tip_size is not None else 10
        except (ValueError, TypeError):
            x1, y1, x2, y2, tip_size = 0, 0, 100, 100, 10

        # Get drawing color (from instance or default black)
        color = getattr(instance, 'draw_color', (0, 0, 0))

        # Calculate arrow tip points
        angle = math.atan2(y2 - y1, x2 - x1)
        tip_angle = math.pi / 6  # 30 degrees

        # Calculate the two points of the arrow tip
        tip1_x = x2 - tip_size * math.cos(angle - tip_angle)
        tip1_y = y2 - tip_size * math.sin(angle - tip_angle)
        tip2_x = x2 - tip_size * math.cos(angle + tip_angle)
        tip2_y = y2 - tip_size * math.sin(angle + tip_angle)

        # Queue drawing command for draw event
        if not hasattr(instance, '_draw_queue'):
            instance._draw_queue = []

        instance._draw_queue.append({
            'type': 'arrow',
            'x1': x1,
            'y1': y1,
            'x2': x2,
            'y2': y2,
            'tip1_x': tip1_x,
            'tip1_y': tip1_y,
            'tip2_x': tip2_x,
            'tip2_y': tip2_y,
            'color': color
        })

        logger.debug(f"➡️ Queued draw_arrow: from ({x1}, {y1}) to ({x2}, {y2}) with tip_size={tip_size}")
    def execute_draw_variable_action(self, instance, parameters: Dict[str, Any]):
        """Draw a variable value on screen

        Parameters:
            x: X coordinate
            y: Y coordinate
            variable: Variable name to display (supports self.var, global.var, or bare names)
        """
        # Parse position
        x = self._parse_value(parameters.get("x", 0), instance)
        y = self._parse_value(parameters.get("y", 0), instance)
        variable_name = parameters.get("variable", "")

        try:
            x = int(x) if x is not None else 0
            y = int(y) if y is not None else 0
        except (ValueError, TypeError):
            x, y = 0, 0

        # Get the variable value
        if not variable_name:
            value = ""
        else:
            # Use _parse_value to resolve the variable reference
            value = self._parse_value(variable_name, instance)

        # Convert to string for display
        text = str(value)

        # Get drawing color (from instance or default black)
        color = getattr(instance, 'draw_color', (0, 0, 0))

        # Queue drawing command for draw event
        if not hasattr(instance, '_draw_queue'):
            instance._draw_queue = []

        instance._draw_queue.append({
            'type': 'text',
            'x': x,
            'y': y,
            'text': text,
            'color': color
        })

        logger.debug(f"📊 Queued draw_variable: '{variable_name}' = '{text}' at ({x}, {y})")
