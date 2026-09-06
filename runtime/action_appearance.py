#!/usr/bin/env python3
"""Appearance and asset-swapping actions for
:class:`~runtime.action_executor.ActionExecutor`.

The methods that change how something LOOKS rather than where it is or whether
it runs: hot-swapping a sprite / background / sound file at runtime
(``replace_*``), assigning an instance's sprite, the room background and its
colour, alpha and blend colour, the sub-image index and animation speed,
start/stop animation, and the two draw-style settings (colour and font).

Extracted verbatim from ``runtime/action_executor.py``
(``docs/POST_1_0_REFACTOR.md`` File 4, cluster 8) as a MIXIN -- see
``runtime/action_drawing.py``'s header for why these are sibling modules rather
than the package layout the plan sketched.

``_GM_FONT_ALIGN_FALLBACK`` came along: its only reader is
``set_draw_font`` here. It exists because GameMaker's Set Font action encodes
horizontal alignment as a 0/1/2 menu -- the importer translates that to
``halign`` now, but projects imported before that fix still carry the raw key.

``pygame`` and ``pathlib.Path`` are imported *inside* the four asset-swapping
methods, not at module level, so this module keeps the engine's
"imports without pygame" property. ``ReplacedSprite`` is a class defined
locally inside ``replace_sprite`` and travels with it.
"""

from typing import Any, Dict

from runtime.action_colors import _hex_to_rgb
from core.logger import get_logger

logger = get_logger(__name__)


# GM's Set Font action encodes horizontal align as a 0/1/2 menu; the converter
# now translates it to `halign`, but pre-fix imported projects still carry the
# raw GM key, so execute_set_draw_font_action reads this as a fallback.
_GM_FONT_ALIGN_FALLBACK = {"0": "left", "1": "center", "2": "right",
                           0: "left", 1: "center", 2: "right",
                           "left": "left", "center": "center", "right": "right"}


class AppearanceMixin:
    """Appearance / asset-swap ``execute_*_action`` methods."""

    def execute_set_draw_color_action(self, instance, parameters: Dict[str, Any]):
        """Set the drawing color for subsequent draw operations

        Parameters:
            color: Color in hex format (e.g., "#FF0000" for red)
        """
        color = parameters.get("color", "#000000")

        rgb_color = _hex_to_rgb(color)

        # Store drawing color on instance for draw events
        instance.draw_color = rgb_color

        # Also store on game runner for global access
        if self.game_runner:
            self.game_runner.draw_color = rgb_color

        logger.debug(f"🎨 Set drawing color to {color} ({rgb_color}) for {instance.object_name}")
    def execute_replace_sprite_action(self, instance, parameters: Dict[str, Any]):
        """Replace a sprite by loading a new image from file

        Parameters:
            sprite: Name of the sprite to replace
            filename: Path to the image file
            frames: Number of animation frames (default: 1)
            remove_background: Remove background color to make transparent (default: False)
            smooth_edges: Apply anti-aliasing to edges (default: False)
        """
        sprite_name = self._parse_value(parameters.get("sprite", ""), instance)
        filename = self._parse_value(parameters.get("filename", ""), instance)
        frames = self._parse_value(parameters.get("frames", 1), instance)
        remove_background = self._parse_value(parameters.get("remove_background", False), instance)
        smooth_edges = self._parse_value(parameters.get("smooth_edges", False), instance)

        if not sprite_name:
            logger.debug("⚠️ replace_sprite: No sprite specified")
            return

        if not filename:
            logger.debug("⚠️ replace_sprite: No filename specified")
            return

        if not self.game_runner:
            logger.debug("⚠️ replace_sprite: No game_runner reference")
            return

        # Import after validation to allow tests without pygame
        import pygame
        from pathlib import Path

        # Convert to boolean if string
        if isinstance(remove_background, str):
            remove_background = remove_background.lower() in ('true', '1', 'yes')
        if isinstance(smooth_edges, str):
            smooth_edges = smooth_edges.lower() in ('true', '1', 'yes')

        try:
            frames = int(frames)
        except (ValueError, TypeError):
            frames = 1

        # Resolve the file path (relative to project or absolute)
        file_path = Path(filename)
        if not file_path.is_absolute() and self.game_runner.project_path:
            file_path = self.game_runner.project_path / filename

        if not file_path.exists():
            logger.warning(f"⚠️ replace_sprite: File not found: {file_path}")
            return

        try:
            # Load the image
            surface = pygame.image.load(str(file_path)).convert_alpha()

            # Apply remove_background if requested (make top-left pixel color transparent)
            if remove_background:
                bg_color = surface.get_at((0, 0))[:3]
                surface.set_colorkey(bg_color)

            # Create a simple sprite object or update existing
            # For simplicity, we store the surface directly
            # GameSprite expects frames list for animation
            if frames > 1:
                # Split horizontal strip into frames
                frame_width = surface.get_width() // frames
                frame_height = surface.get_height()
                frame_list = []
                for i in range(frames):
                    frame_surface = surface.subsurface((i * frame_width, 0, frame_width, frame_height)).copy()
                    frame_list.append(frame_surface)

                # Create a sprite-like object
                class ReplacedSprite:
                    pass
                new_sprite = ReplacedSprite()
                new_sprite.surface = surface
                new_sprite.frames = frame_list
                new_sprite.frame_count = frames
                new_sprite.width = frame_width
                new_sprite.height = frame_height
                new_sprite.speed = 10.0
            else:
                # Single frame sprite
                class ReplacedSprite:
                    pass
                new_sprite = ReplacedSprite()
                new_sprite.surface = surface
                new_sprite.frames = [surface]
                new_sprite.frame_count = 1
                new_sprite.width = surface.get_width()
                new_sprite.height = surface.get_height()
                new_sprite.speed = 10.0

            self.game_runner.sprites[sprite_name] = new_sprite
            logger.debug(f"🖼️ Replaced sprite '{sprite_name}' from {filename} ({frames} frames)")

        except Exception as e:
            logger.error(f"❌ Error replacing sprite '{sprite_name}': {e}")
    def execute_replace_sound_action(self, instance, parameters: Dict[str, Any]):
        """Replace a sound by loading a new audio file

        Parameters:
            sound: Name of the sound to replace
            filename: Path to the audio file
            kind: Type of sound (normal, background, 3d, mmplayer)
        """
        sound_name = self._parse_value(parameters.get("sound", ""), instance)
        filename = self._parse_value(parameters.get("filename", ""), instance)
        kind = self._parse_value(parameters.get("kind", "normal"), instance)

        if not sound_name:
            logger.debug("⚠️ replace_sound: No sound specified")
            return

        if not filename:
            logger.debug("⚠️ replace_sound: No filename specified")
            return

        if not self.game_runner:
            logger.debug("⚠️ replace_sound: No game_runner reference")
            return

        # Import after validation to allow tests without pygame
        import pygame
        from pathlib import Path

        # Resolve the file path (relative to project or absolute)
        file_path = Path(filename)
        if not file_path.is_absolute() and self.game_runner.project_path:
            file_path = self.game_runner.project_path / filename

        if not file_path.exists():
            logger.warning(f"⚠️ replace_sound: File not found: {file_path}")
            return

        try:
            if kind == 'music' or kind == 'background':
                # Music is streamed, store the path
                self.game_runner.music_files[sound_name] = str(file_path)
                logger.debug(f"🎵 Replaced music '{sound_name}' from {filename}")
            else:
                # Sound effects are loaded into memory
                sound = pygame.mixer.Sound(str(file_path))
                self.game_runner.sounds[sound_name] = sound
                logger.debug(f"🔊 Replaced sound '{sound_name}' from {filename}")

        except Exception as e:
            logger.error(f"❌ Error replacing sound '{sound_name}': {e}")
    def execute_replace_background_action(self, instance, parameters: Dict[str, Any]):
        """Replace a background by loading a new image from file

        Parameters:
            background: Name of the background to replace
            filename: Path to the image file
            remove_background: Remove background color to make transparent (default: False)
            smooth_edges: Apply anti-aliasing to edges (default: False)
        """
        bg_name = self._parse_value(parameters.get("background", ""), instance)
        filename = self._parse_value(parameters.get("filename", ""), instance)
        remove_background = self._parse_value(parameters.get("remove_background", False), instance)
        smooth_edges = self._parse_value(parameters.get("smooth_edges", False), instance)

        if not bg_name:
            logger.debug("⚠️ replace_background: No background specified")
            return

        if not filename:
            logger.debug("⚠️ replace_background: No filename specified")
            return

        if not self.game_runner:
            logger.debug("⚠️ replace_background: No game_runner reference")
            return

        # Import after validation to allow tests without pygame
        import pygame
        from pathlib import Path

        # Convert to boolean if string
        if isinstance(remove_background, str):
            remove_background = remove_background.lower() in ('true', '1', 'yes')
        if isinstance(smooth_edges, str):
            smooth_edges = smooth_edges.lower() in ('true', '1', 'yes')

        # Resolve the file path (relative to project or absolute)
        file_path = Path(filename)
        if not file_path.is_absolute() and self.game_runner.project_path:
            file_path = self.game_runner.project_path / filename

        if not file_path.exists():
            logger.warning(f"⚠️ replace_background: File not found: {file_path}")
            return

        try:
            # Load the image
            surface = pygame.image.load(str(file_path)).convert_alpha()

            # Apply remove_background if requested (make top-left pixel color transparent)
            if remove_background:
                bg_color = surface.get_at((0, 0))[:3]
                surface.set_colorkey(bg_color)

            self.game_runner.backgrounds[bg_name] = surface
            logger.debug(f"🖼️ Replaced background '{bg_name}' from {filename} ({surface.get_width()}x{surface.get_height()})")

        except Exception as e:
            logger.error(f"❌ Error replacing background '{bg_name}': {e}")
    def execute_set_background_color_action(self, instance, parameters: Dict[str, Any]):
        """Set room background color

        Parameters:
            color: Background color (hex string like "#87CEEB")
            show_color: Whether to display the color (default: True)
        """
        if not self.game_runner or not self.game_runner.current_room:
            logger.debug("⚠️ set_background_color: No current room")
            return

        # Parse parameters
        color_str = parameters.get("color", "#000000")
        show_color = parameters.get("show_color", True)

        # Convert to boolean if string
        if isinstance(show_color, str):
            show_color = show_color.lower() in ('true', '1', 'yes')

        # Parse color
        color_rgb = self._parse_color(color_str)

        # Update room background color
        self.game_runner.current_room.background_color = color_rgb
        self.game_runner.current_room.show_background_color = show_color

        logger.debug(f"🎨 Set background color: {color_str} → {color_rgb}, show={show_color}")
    def execute_set_background_action(self, instance, parameters: Dict[str, Any]):
        """Set room background image with tiling and scrolling options

        Parameters:
            background: Background/sprite name to use
            visible: Show background (default: True)
            foreground: Draw in front of objects (default: False)
            tiled_h: Tile horizontally (default: False)
            tiled_v: Tile vertically (default: False)
            hspeed: Horizontal scroll speed (default: 0)
            vspeed: Vertical scroll speed (default: 0)
        """
        if not self.game_runner or not self.game_runner.current_room:
            logger.debug("⚠️ set_background: No current room")
            return

        # Parse parameters
        background_name = str(self._parse_value(parameters.get("background", ""), instance))
        visible = self._parse_value(parameters.get("visible", True), instance)
        foreground = self._parse_value(parameters.get("foreground", False), instance)
        tiled_h = self._parse_value(parameters.get("tiled_h", False), instance)
        tiled_v = self._parse_value(parameters.get("tiled_v", False), instance)
        hspeed = self._parse_value(parameters.get("hspeed", 0), instance)
        vspeed = self._parse_value(parameters.get("vspeed", 0), instance)

        # Convert booleans
        if isinstance(visible, str):
            visible = visible.lower() in ('true', '1', 'yes')
        if isinstance(foreground, str):
            foreground = foreground.lower() in ('true', '1', 'yes')
        if isinstance(tiled_h, str):
            tiled_h = tiled_h.lower() in ('true', '1', 'yes')
        if isinstance(tiled_v, str):
            tiled_v = tiled_v.lower() in ('true', '1', 'yes')
        try:
            hspeed = float(hspeed)
        except (TypeError, ValueError):
            hspeed = 0.0
        try:
            vspeed = float(vspeed)
        except (TypeError, ValueError):
            vspeed = 0.0

        # Look up the background/sprite
        import pygame

        background_surface = None

        # Try to load from sprites or backgrounds
        if hasattr(self.game_runner, 'sprites') and background_name in self.game_runner.sprites:
            sprite = self.game_runner.sprites[background_name]
            if sprite.surface:
                background_surface = sprite.surface
        elif hasattr(self.game_runner, 'project_data'):
            # Try to load from backgrounds in project data
            backgrounds = self.game_runner.project_data.get('assets', {}).get('backgrounds', {})
            if background_name in backgrounds:
                bg_data = backgrounds[background_name]
                file_path = bg_data.get('file_path', '')
                if file_path:
                    full_path = self.game_runner.project_path / file_path
                    if full_path.exists():
                        try:
                            background_surface = pygame.image.load(str(full_path)).convert()
                        except Exception as e:
                            logger.error(f"⚠️ Error loading background '{background_name}': {e}")

        if background_surface and visible:
            # Update room background
            self.game_runner.current_room.background_surface = background_surface
            self.game_runner.current_room.background_image_name = background_name
            self.game_runner.current_room.tile_horizontal = tiled_h
            self.game_runner.current_room.tile_vertical = tiled_v
            self.game_runner.current_room.bg_hspeed = hspeed
            self.game_runner.current_room.bg_vspeed = vspeed
            self.game_runner.current_room.background_foreground = foreground

            logger.debug(f"🖼️ Set background: '{background_name}', visible={visible}, "
                  f"tiled_h={tiled_h}, tiled_v={tiled_v}, foreground={foreground}, "
                  f"hspeed={hspeed}, vspeed={vspeed}")
        elif not visible:
            # Clear background
            self.game_runner.current_room.background_surface = None
            logger.debug("🖼️ Background hidden")
        else:
            logger.debug(f"⚠️ set_background: Background '{background_name}' not found")
    def execute_set_image_index_action(self, instance, parameters: Dict[str, Any]):
        """Set the current animation frame"""
        frame = parameters.get("frame", 0)
        try:
            frame = int(frame)
        except (ValueError, TypeError):
            frame = 0

        instance.image_index = float(frame)
        logger.debug(f"🎬 Set image_index to {frame} for {instance.object_name}")
    def execute_set_image_speed_action(self, instance, parameters: Dict[str, Any]):
        """Set the animation speed multiplier"""
        speed = parameters.get("speed", 1.0)
        try:
            speed = float(speed)
        except (ValueError, TypeError):
            speed = 1.0

        instance.image_speed = speed
        logger.debug(f"⏩ Set image_speed to {speed} for {instance.object_name}")
    def execute_stop_animation_action(self, instance, parameters: Dict[str, Any]):
        """Stop the sprite animation"""
        instance.image_speed = 0.0
        logger.debug(f"⏸️ Stopped animation for {instance.object_name}")
    def execute_start_animation_action(self, instance, parameters: Dict[str, Any]):
        """Start/resume the sprite animation"""
        instance.image_speed = 1.0
        logger.debug(f"▶️ Started animation for {instance.object_name}")
    def execute_set_sprite_action(self, instance, parameters: Dict[str, Any]):
        """Set the sprite for an instance or modify current sprite animation

        Parameters:
            sprite: Sprite name to use, or "<self>" to keep current sprite
            subimage: Frame index to set (-1 = don't change)
            speed: Animation speed to set (-1 = don't change)

        When sprite is "<self>", only the animation properties (subimage, speed)
        are modified without changing the sprite. This allows stopping/starting
        animation on the current sprite.
        """
        sprite_name = parameters.get("sprite", "<self>")
        subimage = parameters.get("subimage", -1)
        speed = parameters.get("speed", -1)

        # Parse values (can be expressions)
        try:
            subimage = int(self._parse_value(str(subimage), instance))
        except (ValueError, TypeError):
            subimage = -1

        try:
            speed = float(self._parse_value(str(speed), instance))
        except (ValueError, TypeError):
            speed = -1

        # GM's "Applies to" selector (target/target_object, emitted by the GMK
        # importer): maze_4's ring bonus changes EVERY monster_all's sprite to
        # the afraid look. Default remains the acting instance.
        if "target" in parameters:
            targets = self._resolve_target_instances(instance, parameters)
        else:
            targets = [instance]

        for target_instance in targets:
            # Handle sprite change (unless <self>)
            if sprite_name != "<self>" and sprite_name:
                if self.game_runner and sprite_name in self.game_runner.sprites:
                    target_instance.set_sprite(self.game_runner.sprites[sprite_name])
                    logger.debug(f"🖼️ Set sprite to '{sprite_name}' for {target_instance.object_name}")
                else:
                    logger.debug(f"⚠️ set_sprite: Sprite '{sprite_name}' not found")

            # Handle subimage (frame index)
            if subimage >= 0:
                target_instance.image_index = float(subimage)
                logger.debug(f"🎬 Set image_index to {subimage} for {target_instance.object_name}")

            # Handle animation speed (only print when value changes)
            if speed >= 0:
                old_speed = getattr(target_instance, 'image_speed', 1.0)
                if old_speed != speed:
                    target_instance.image_speed = speed
                    if speed == 0:
                        logger.debug(f"⏸️ Stopped animation for {target_instance.object_name}")
                    else:
                        logger.debug(f"⏩ Set image_speed to {speed} for {target_instance.object_name}")
                else:
                    target_instance.image_speed = speed  # Still set it, just don't print
    def execute_set_color_action(self, instance, parameters: Dict[str, Any]):
        """Set the blend color and alpha for the sprite

        Parameters:
            color: Blend color (hex string like "#RRGGBB")
            alpha: Transparency (0.0 = invisible, 1.0 = fully opaque)
        """
        color_param = parameters.get("color", "#FFFFFF")
        alpha_param = parameters.get("alpha", 1.0)

        # Parse values
        color = self._parse_value(str(color_param), instance)
        alpha = self._parse_value(str(alpha_param), instance)

        # Parse color if it's a hex string
        if isinstance(color, str) and color.startswith('#'):
            try:
                # Convert hex to RGB tuple
                hex_color = color.lstrip('#')
                r = int(hex_color[0:2], 16)
                g = int(hex_color[2:4], 16)
                b = int(hex_color[4:6], 16)
                instance.image_blend = (r, g, b)
            except (ValueError, IndexError):
                instance.image_blend = (255, 255, 255)
        else:
            instance.image_blend = (255, 255, 255)

        # Parse alpha
        try:
            alpha = float(alpha) if alpha is not None else 1.0
            alpha = max(0.0, min(1.0, alpha))  # Clamp to 0-1
        except (ValueError, TypeError):
            alpha = 1.0

        instance.image_alpha = alpha

        logger.debug(f"🎨 Set color for {instance.object_name}: blend={instance.image_blend}, alpha={alpha}")
    def execute_set_alpha_action(self, instance, parameters: Dict[str, Any]):
        """Set the transparency (alpha) for the sprite

        Parameters:
            alpha: Transparency (0.0 = invisible, 1.0 = fully opaque)
        """
        alpha_param = parameters.get("alpha", 1.0)

        # Parse value
        alpha = self._parse_value(str(alpha_param), instance)

        # Parse alpha
        try:
            alpha = float(alpha) if alpha is not None else 1.0
            alpha = max(0.0, min(1.0, alpha))  # Clamp to 0-1
        except (ValueError, TypeError):
            alpha = 1.0

        instance.image_alpha = alpha

        logger.debug(f"👻 Set alpha for {instance.object_name}: alpha={alpha}")
    def execute_set_draw_font_action(self, instance, parameters: Dict[str, Any]):
        """Set the font and alignment for text drawing

        Parameters:
            font: Font name/asset to use
            halign: Horizontal alignment (left, center, right)
            valign: Vertical alignment (top, middle, bottom)
        """
        font_name = self._parse_value(parameters.get("font", ""), instance)
        # Accept GM's `align` menu (0/1/2) as a fallback for `halign` — projects
        # imported before the converter translated it still carry the raw GM
        # key. New imports emit `halign` directly (see gmk_converter).
        halign_param = parameters.get("halign")
        if halign_param is None and "align" in parameters:
            halign_param = _GM_FONT_ALIGN_FALLBACK.get(
                parameters.get("align"), "left")
        halign = self._parse_value(
            halign_param if halign_param is not None else "left", instance)
        valign = self._parse_value(parameters.get("valign", "top"), instance)

        # Store font settings on the instance
        instance.draw_font = font_name if font_name else None
        instance.draw_halign = halign if halign in ('left', 'center', 'right') else 'left'
        instance.draw_valign = valign if valign in ('top', 'middle', 'bottom') else 'top'

        logger.debug(f"🔤 Set draw font: '{font_name}', halign={halign}, valign={valign}")

    def execute_transform_sprite_action(self, instance, parameters: Dict[str, Any]):
        """Transform the sprite with scaling and rotation

        Parameters:
            xscale: Horizontal scale factor (1.0 = normal)
            yscale: Vertical scale factor (1.0 = normal)
            angle: Rotation angle in degrees
        """
        xscale_param = parameters.get("xscale", 1.0)
        yscale_param = parameters.get("yscale", 1.0)
        angle_param = parameters.get("angle", 0.0)

        # Parse values
        xscale = self._parse_value(str(xscale_param), instance)
        yscale = self._parse_value(str(yscale_param), instance)
        angle = self._parse_value(str(angle_param), instance)

        try:
            xscale = float(xscale) if xscale is not None else 1.0
            yscale = float(yscale) if yscale is not None else 1.0
            angle = float(angle) if angle is not None else 0.0
        except (ValueError, TypeError):
            xscale, yscale, angle = 1.0, 1.0, 0.0

        # Apply to instance
        instance.image_xscale = xscale
        instance.image_yscale = yscale
        instance.image_angle = angle

        logger.debug(f"🔄 Transform sprite for {instance.object_name}: scale=({xscale}, {yscale}), angle={angle}")

    def execute_fill_color_action(self, instance, parameters: Dict[str, Any]):
        """Fill the entire screen with a color

        Parameters:
            color: Fill color (hex string like "#RRGGBB")
        """
        color_param = self._parse_value(parameters.get("color", "#000000"), instance)

        # Parse color if it's a hex string
        if isinstance(color_param, str) and color_param.startswith('#'):
            try:
                hex_color = color_param.lstrip('#')
                r = int(hex_color[0:2], 16)
                g = int(hex_color[2:4], 16)
                b = int(hex_color[4:6], 16)
                color = (r, g, b)
            except (ValueError, IndexError):
                color = (0, 0, 0)
        else:
            color = (0, 0, 0)

        # Queue drawing command for draw event
        if not hasattr(instance, '_draw_queue'):
            instance._draw_queue = []

        instance._draw_queue.append({
            'type': 'fill',
            'color': color
        })

        logger.debug(f"🎨 Queued fill_color: {color}")
