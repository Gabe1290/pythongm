#!/usr/bin/env python3
"""
Enhanced GameRunner with smooth movement that snaps to grid
"""

import os
import sys
# Force pygame to use software rendering to avoid conflicts with Qt
# Use appropriate video driver based on platform
if sys.platform == 'win32':
    os.environ['SDL_VIDEODRIVER'] = 'windows'
elif sys.platform == 'darwin':
    os.environ['SDL_VIDEODRIVER'] = 'cocoa'
else:  # Linux and other Unix-like systems
    os.environ['SDL_VIDEODRIVER'] = 'x11'
os.environ['SDL_RENDER_DRIVER'] = 'software'

import pygame
import json
import sys
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Any
from PIL import Image

from runtime.action_executor import ActionExecutor
from events.plugin_loader import load_all_plugins
from config.blockly_translations import get_runtime_translation
from runtime.thymio_simulator import ThymioSimulator
from runtime.thymio_renderer import ThymioRenderer
from runtime.thymio_action_handlers import register_thymio_actions
from core.logger import get_logger
logger = get_logger(__name__)

# Translation strings for game caption (key: language code)
CAPTION_TRANSLATIONS = {
    'en': {'score': 'Score', 'lives': 'Lives', 'health': 'Health', 'room': 'Room'},
    'de': {'score': 'Punkte', 'lives': 'Leben', 'health': 'Gesundheit', 'room': 'Raum'},
    'fr': {'score': 'Score', 'lives': 'Vies', 'health': 'Santé', 'room': 'Niveau'},
    'it': {'score': 'Punteggio', 'lives': 'Vite', 'health': 'Salute', 'room': 'Stanza'},
    'sl': {'score': 'Točke', 'lives': 'Življenja', 'health': 'Zdravje', 'room': 'Soba'},
    'uk': {'score': 'Рахунок', 'lives': 'Життя', 'health': 'Здоров\'я', 'room': 'Кімната'},
}

class GameSprite:
    """Represents a loaded sprite with animation support"""

    def __init__(self, image_path: str, sprite_data: dict = None):
        self.path = image_path
        self.sprite_data = sprite_data or {}
        self.surface = None  # Full sprite sheet surface
        self.frames = []  # List of individual frame surfaces
        self.frame_count = 1
        self.frame_width = 32
        self.frame_height = 32
        self.width = 32  # Actual display width (frame width)
        self.height = 32  # Actual display height (frame height)
        self.speed = 10.0  # Animation FPS
        self.animation_type = "single"  # single, strip_h, strip_v, grid
        self.load_image()

    def load_image(self):
        """Load the sprite image and extract frames if animated"""
        try:
            if Path(self.path).exists():
                # Check if it's an animated GIF
                if self.path.lower().endswith('.gif'):
                    self._load_animated_gif()
                else:
                    self._load_static_or_sheet()
            else:
                logger.error(f"Sprite not found: {self.path}")
                self.create_default_sprite()
        except Exception as e:
            logger.error(f"Error loading sprite {self.path}: {e}")
            import traceback
            traceback.print_exc()
            self.create_default_sprite()

    def _load_animated_gif(self):
        """Load an animated GIF using PIL to extract all frames"""
        try:
            pil_image = Image.open(self.path)

            # Check if it's actually animated
            is_animated = getattr(pil_image, 'is_animated', False)
            n_frames = getattr(pil_image, 'n_frames', 1)

            if is_animated and n_frames > 1:
                # Determine the transparent color
                # First check if there's a transparency index in the GIF
                transparent_color = None
                if 'transparency' in pil_image.info:
                    trans_idx = pil_image.info['transparency']
                    palette = pil_image.getpalette()
                    if palette and isinstance(trans_idx, int):
                        transparent_color = tuple(palette[trans_idx*3:trans_idx*3+3])

                # If no transparency defined, use the top-left pixel as background
                if transparent_color is None:
                    pil_image.seek(0)
                    first_frame = pil_image.convert('RGB')
                    transparent_color = first_frame.getpixel((0, 0))

                # Extract all frames from the animated GIF
                self.frames = []
                for frame_idx in range(n_frames):
                    pil_image.seek(frame_idx)
                    # Convert to RGBA for transparency support
                    frame_rgba = pil_image.convert('RGBA')

                    # Make the background color transparent
                    if transparent_color:
                        datas = frame_rgba.getdata()
                        new_data = []
                        for item in datas:
                            # Check if pixel matches transparent color (with some tolerance)
                            if (abs(item[0] - transparent_color[0]) < 5 and
                                abs(item[1] - transparent_color[1]) < 5 and
                                abs(item[2] - transparent_color[2]) < 5):
                                # Make it fully transparent
                                new_data.append((item[0], item[1], item[2], 0))
                            else:
                                new_data.append(item)
                        frame_rgba.putdata(new_data)

                    # Convert PIL image to pygame surface
                    frame_data = frame_rgba.tobytes()
                    frame_surface = pygame.image.fromstring(
                        frame_data, frame_rgba.size, 'RGBA'
                    ).convert_alpha()
                    self.frames.append(frame_surface)

                self.frame_count = len(self.frames)
                self.surface = self.frames[0]
                self.width = self.surface.get_width()
                self.height = self.surface.get_height()
                self.frame_width = self.width
                self.frame_height = self.height

                # Get animation speed from sprite data
                self.speed = self.sprite_data.get('speed', 10.0)
                self.animation_type = self.sprite_data.get('animation_type', 'loop')

                logger.debug(f"  🎬 Loaded animated GIF: {Path(self.path).name} ({self.frame_count} frames, transparent={transparent_color})")
            else:
                # Not animated, load as static
                self._load_static_or_sheet()

        except Exception as e:
            logger.error(f"Error loading animated GIF {self.path}: {e}")
            import traceback
            traceback.print_exc()
            # Fall back to static loading
            self._load_static_or_sheet()

    def _load_gif_with_transparency(self) -> pygame.Surface:
        """Load a single-frame GIF with proper transparency handling using PIL"""
        try:
            pil_image = Image.open(self.path)

            # Determine the transparent color
            transparent_color = None
            if 'transparency' in pil_image.info:
                trans_idx = pil_image.info['transparency']
                palette = pil_image.getpalette()
                if palette and isinstance(trans_idx, int):
                    transparent_color = tuple(palette[trans_idx*3:trans_idx*3+3])

            # If no transparency defined, use the top-left pixel as background
            if transparent_color is None:
                rgb_image = pil_image.convert('RGB')
                transparent_color = rgb_image.getpixel((0, 0))

            # Convert to RGBA and make background transparent
            frame_rgba = pil_image.convert('RGBA')
            if transparent_color:
                datas = frame_rgba.getdata()
                new_data = []
                for item in datas:
                    # Check if pixel matches transparent color (with tolerance)
                    if (abs(item[0] - transparent_color[0]) < 5 and
                        abs(item[1] - transparent_color[1]) < 5 and
                        abs(item[2] - transparent_color[2]) < 5):
                        new_data.append((item[0], item[1], item[2], 0))
                    else:
                        new_data.append(item)
                frame_rgba.putdata(new_data)

            # Convert PIL image to pygame surface
            frame_data = frame_rgba.tobytes()
            surface = pygame.image.fromstring(
                frame_data, frame_rgba.size, 'RGBA'
            ).convert_alpha()

            logger.debug(f"  🖼️ Loaded GIF with transparency: {Path(self.path).name} (bg={transparent_color})")
            return surface

        except Exception as e:
            logger.error(f"Error loading GIF with PIL, falling back to pygame: {e}")
            return pygame.image.load(self.path).convert_alpha()

    def _load_static_or_sheet(self):
        """Load a static image or sprite sheet"""
        # For GIF files, use PIL to handle transparency properly
        if self.path.lower().endswith('.gif'):
            self.surface = self._load_gif_with_transparency()
        else:
            self.surface = pygame.image.load(self.path).convert_alpha()
        full_width = self.surface.get_width()
        full_height = self.surface.get_height()

        # Get animation data from sprite_data
        self.frame_count = self.sprite_data.get('frames', 1)
        self.frame_width = self.sprite_data.get('frame_width', full_width)
        self.frame_height = self.sprite_data.get('frame_height', full_height)
        self.speed = self.sprite_data.get('speed', 10.0)
        self.animation_type = self.sprite_data.get('animation_type', 'single')

        # Set display dimensions to frame size
        self.width = self.frame_width
        self.height = self.frame_height

        # Extract frames based on animation type
        if self.frame_count > 1:
            self._extract_frames(full_width, full_height)
        else:
            # Single frame - just use the whole surface
            self.frames = [self.surface]
            self.frame_count = 1

    def _extract_frames(self, full_width: int, full_height: int):
        """Extract individual frames from sprite sheet"""
        self.frames = []

        # Calculate grid dimensions
        if self.animation_type == "strip_h":
            # Horizontal strip - frames are side by side
            columns = max(1, full_width // self.frame_width)
            rows = 1
        elif self.animation_type == "strip_v":
            # Vertical strip - frames are stacked
            columns = 1
            rows = max(1, full_height // self.frame_height)
        else:
            # Grid or auto-detect
            columns = max(1, full_width // self.frame_width)
            rows = max(1, full_height // self.frame_height)

        # Extract each frame
        for row in range(rows):
            for col in range(columns):
                x = col * self.frame_width
                y = row * self.frame_height

                # Check bounds
                if x + self.frame_width <= full_width and y + self.frame_height <= full_height:
                    # Create a new surface for this frame
                    frame_surface = pygame.Surface(
                        (self.frame_width, self.frame_height),
                        pygame.SRCALPHA
                    )
                    # Copy the frame region
                    frame_surface.blit(
                        self.surface,
                        (0, 0),
                        (x, y, self.frame_width, self.frame_height)
                    )
                    self.frames.append(frame_surface)

                    if len(self.frames) >= self.frame_count:
                        break
            if len(self.frames) >= self.frame_count:
                break

        # Update frame count to actual extracted frames
        self.frame_count = len(self.frames) if self.frames else 1

        # Fallback if no frames extracted
        if not self.frames:
            self.frames = [self.surface]
            self.frame_count = 1

    def get_frame(self, image_index: float) -> pygame.Surface:
        """Get the frame surface for a given animation index"""
        if not self.frames:
            return self.surface

        # Wrap index to valid range
        frame_idx = int(image_index) % len(self.frames)
        return self.frames[frame_idx]

    def create_default_sprite(self):
        """Create a default sprite (colored rectangle)"""
        self.surface = pygame.Surface((32, 32), pygame.SRCALPHA)
        self.surface.fill((255, 100, 100))  # Red rectangle
        pygame.draw.rect(self.surface, (0, 0, 0), (0, 0, 32, 32), 2)
        self.frames = [self.surface]
        self.frame_count = 1
        self.width = 32
        self.height = 32
        self.frame_width = 32
        self.frame_height = 32

class GameInstance:
    """Represents an object instance in the game world"""

    def __init__(self, object_name: str, x: float, y: float, instance_data: dict, action_executor=None):
        self.object_name = object_name
        self._x = float(x)
        self._y = float(y)
        # Store starting position for jump_to_start action
        self.xstart = float(x)
        self.ystart = float(y)
        self._grid_dirty = False  # Track if position changed for spatial grid update
        self.instance_id = instance_data.get('instance_id', id(self))
        self.visible = instance_data.get('visible', True)
        self.rotation = instance_data.get('rotation', 0)
        self.scale_x = instance_data.get('scale_x', 1.0)
        self.scale_y = instance_data.get('scale_y', 1.0)

        self.sprite = None
        self.object_data = None
        self._cached_object_data = None  # Cached reference to object data
        self._collision_targets = {}  # Pre-parsed collision events: {target_object_name: event_data}
        self.to_destroy = False
        self.depth = 0  # Drawing depth (higher = drawn behind, lower = drawn in front)

        # Cached dimensions (updated when sprite is set)
        self._cached_width = 32
        self._cached_height = 32

        # Animation properties
        self.image_index = 0.0  # Current animation frame (can be fractional for smooth interpolation)
        self.image_speed = 1.0  # Animation speed multiplier (1.0 = normal, 0 = stopped)

        # Speed properties for smooth movement
        self.hspeed = 0.0  # Horizontal speed (pixels per frame)
        self.vspeed = 0.0  # Vertical speed (pixels per frame)

        # Physics properties
        self.gravity = 0.0  # Gravity strength (pixels per frame^2)
        self.gravity_direction = 270  # Direction of gravity in degrees (270 = down)
        self.friction = 0.0  # Friction coefficient (reduces speed each frame)

        # Track if movement keys are currently pressed
        self.keys_pressed = set()  # Set of currently pressed keys

        # Alarms - 12 alarms (0-11), -1 means disabled
        self.alarm = [-1] * 12

        # Action executor - use shared instance or create new one
        self.action_executor = action_executor if action_executor else ActionExecutor()

    @property
    def x(self):
        return self._x

    @x.setter
    def x(self, value):
        if self._x != value:
            self._x = value
            self._grid_dirty = True

    @property
    def y(self):
        return self._y

    @y.setter
    def y(self, value):
        if self._y != value:
            self._y = value
            self._grid_dirty = True

    def step(self):
        """Execute step event every frame"""
        # Advance animation
        if self.sprite and self.sprite.frame_count > 1 and self.image_speed != 0:
            # Calculate animation advancement based on sprite speed and instance speed multiplier
            # sprite.speed is in FPS, game runs at 30 FPS
            frame_advance = self.image_speed * (self.sprite.speed / 30.0)
            self.image_index += frame_advance

            # Wrap around when animation completes
            if self.image_index >= self.sprite.frame_count:
                self.image_index = self.image_index % self.sprite.frame_count
            elif self.image_index < 0:
                self.image_index = self.sprite.frame_count + (self.image_index % self.sprite.frame_count)

        if self.object_data and "events" in self.object_data:
            # Execute regular step event
            # NOTE: Alarms are now processed in main game loop (before step)
            # to match GameMaker 7.0 event execution order
            self.action_executor.execute_event(self, "step", self.object_data["events"])

            # Check for "nokey" event (GameMaker compatibility)
            events = self.object_data["events"]
            # This event triggers when no keyboard keys are currently pressed
            if "keyboard" in events and "nokey" in events["keyboard"]:
                # Check if no keys are currently pressed
                keys_pressed = getattr(self, 'keys_pressed', set())
                if len(keys_pressed) == 0:
                    # No keys pressed - execute nokey event actions
                    nokey_event = events["keyboard"]["nokey"]
                    if isinstance(nokey_event, dict) and "actions" in nokey_event:
                        for action_data in nokey_event["actions"]:
                            self.action_executor.execute_action(self, action_data)

    def set_sprite(self, sprite: GameSprite):
        """Set the sprite for this instance"""
        self.sprite = sprite
        # Cache dimensions for faster collision detection
        if sprite:
            self._cached_width = sprite.width
            self._cached_height = sprite.height
        else:
            self._cached_width = 32
            self._cached_height = 32

    def set_object_data(self, object_data: dict):
        """Set the object data from project (create event triggered when room becomes active)"""
        self.object_data = object_data
        self._cached_object_data = object_data  # Cache reference

        # Pre-parse collision events for faster lookup
        # Instead of iterating all events and checking startswith('collision_with_') each frame,
        # we build a dict of {target_object_name: event_data}
        self._collision_targets = {}
        if object_data:
            events = object_data.get('events', {})
            for event_name, event_data in events.items():
                if event_name.startswith('collision_with_'):
                    target_object = event_name[15:]  # len('collision_with_') == 15
                    self._collision_targets[target_object] = event_data

        # Apply object-level visibility setting
        # If the object type has visible=False, make all instances of it invisible
        if not object_data.get('visible', True):
            self.visible = False

        # Apply depth from object definition
        self.depth = object_data.get('depth', 0)

        # NOTE: Create event is NOT triggered here!
        # It's triggered when the room becomes active (in change_room or run_game_loop)

    def render(self, screen: pygame.Surface):
        """Render this instance"""
        if not self.visible:
            return

        # Render sprite if present
        if self.sprite:
            # Calculate render position
            render_x = int(self.x)
            render_y = int(self.y)

            # Get current animation frame
            current_frame = self.sprite.get_frame(self.image_index)

            # Handle scaling (basic implementation)
            if self.scale_x != 1.0 or self.scale_y != 1.0:
                scaled_width = int(self.sprite.width * self.scale_x)
                scaled_height = int(self.sprite.height * self.scale_y)
                scaled_surface = pygame.transform.scale(current_frame, (scaled_width, scaled_height))
                screen.blit(scaled_surface, (render_x, render_y))
            else:
                screen.blit(current_frame, (render_x, render_y))

        # Execute draw event for this instance
        if self.object_data and "events" in self.object_data:
            events = self.object_data["events"]
            if "draw" in events:
                # Clear draw queue before executing draw event
                self._draw_queue = []
                self.action_executor.execute_event(self, "draw", events)

                # Process draw queue
                self._process_draw_queue(screen)

    def _process_draw_queue(self, screen: pygame.Surface):
        """Process queued draw commands from draw event actions"""
        if not hasattr(self, '_draw_queue'):
            return

        for cmd in self._draw_queue:
            cmd_type = cmd.get('type')

            if cmd_type == 'text':
                # Draw text (from draw_score, draw_text, etc.)
                self._draw_text(screen, cmd)

            elif cmd_type == 'lives':
                # Draw lives as sprite or text
                self._draw_lives(screen, cmd)

            elif cmd_type == 'health_bar':
                # Draw health bar
                self._draw_health_bar(screen, cmd)

            elif cmd_type == 'rectangle':
                # Draw rectangle
                self._draw_rectangle(screen, cmd)

            elif cmd_type == 'circle':
                # Draw circle
                self._draw_circle(screen, cmd)

            elif cmd_type == 'ellipse':
                # Draw ellipse
                self._draw_ellipse(screen, cmd)

            elif cmd_type == 'line':
                # Draw line
                self._draw_line(screen, cmd)

            elif cmd_type == 'sprite':
                # Draw sprite
                self._draw_sprite(screen, cmd)

            elif cmd_type == 'background':
                # Draw background (possibly tiled)
                self._draw_background(screen, cmd)

        # Clear the queue after processing
        self._draw_queue = []

    def _draw_text(self, screen: pygame.Surface, cmd: dict):
        """Draw text on screen"""
        try:
            font = pygame.font.Font(None, 24)
        except Exception:
            font = pygame.font.SysFont('arial', 18)

        text = cmd.get('text', '')
        x = cmd.get('x', 0)
        y = cmd.get('y', 0)
        color = self._parse_color(cmd.get('color', '#FFFFFF'))

        text_surface = font.render(str(text), True, color)
        screen.blit(text_surface, (x, y))

    def _draw_lives(self, screen: pygame.Surface, cmd: dict):
        """Draw lives (as text for now)"""
        try:
            font = pygame.font.Font(None, 24)
        except Exception:
            font = pygame.font.SysFont('arial', 18)

        count = cmd.get('count', 0)
        x = cmd.get('x', 0)
        y = cmd.get('y', 0)

        text_surface = font.render(f"Lives: {count}", True, (255, 255, 255))
        screen.blit(text_surface, (x, y))

    def _draw_health_bar(self, screen: pygame.Surface, cmd: dict):
        """Draw health bar"""
        x1 = cmd.get('x1', 0)
        y1 = cmd.get('y1', 0)
        x2 = cmd.get('x2', 100)
        y2 = cmd.get('y2', 20)
        health = cmd.get('health', 100)
        back_color = self._parse_color(cmd.get('back_color', '#FF0000'))
        bar_color = self._parse_color(cmd.get('bar_color', '#00FF00'))

        # Draw background (full bar)
        bar_width = x2 - x1
        bar_height = y2 - y1
        pygame.draw.rect(screen, back_color, (x1, y1, bar_width, bar_height))

        # Draw health portion
        health_width = int(bar_width * (health / 100.0))
        if health_width > 0:
            pygame.draw.rect(screen, bar_color, (x1, y1, health_width, bar_height))

        # Draw border
        pygame.draw.rect(screen, (0, 0, 0), (x1, y1, bar_width, bar_height), 1)

    def _draw_rectangle(self, screen: pygame.Surface, cmd: dict):
        """Draw a rectangle"""
        x1 = cmd.get('x1', 0)
        y1 = cmd.get('y1', 0)
        x2 = cmd.get('x2', 100)
        y2 = cmd.get('y2', 100)
        color = self._parse_color(cmd.get('color', '#FFFFFF'))
        filled = cmd.get('filled', True)

        width = x2 - x1
        height = y2 - y1

        if filled:
            pygame.draw.rect(screen, color, (x1, y1, width, height))
        else:
            pygame.draw.rect(screen, color, (x1, y1, width, height), 1)

    def _draw_circle(self, screen: pygame.Surface, cmd: dict):
        """Draw a circle"""
        x = cmd.get('x', 0)
        y = cmd.get('y', 0)
        radius = cmd.get('radius', 10)
        color = self._parse_color(cmd.get('color', '#FFFFFF'))
        filled = cmd.get('filled', True)

        if filled:
            pygame.draw.circle(screen, color, (x, y), radius)
        else:
            pygame.draw.circle(screen, color, (x, y), radius, 1)

    def _draw_ellipse(self, screen: pygame.Surface, cmd: dict):
        """Draw an ellipse"""
        x1 = cmd.get('x1', 0)
        y1 = cmd.get('y1', 0)
        x2 = cmd.get('x2', 100)
        y2 = cmd.get('y2', 100)
        color = self._parse_color(cmd.get('color', '#FFFFFF'))
        filled = cmd.get('filled', True)

        width = x2 - x1
        height = y2 - y1

        # pygame.draw.ellipse expects a rect (x, y, width, height)
        if filled:
            pygame.draw.ellipse(screen, color, (x1, y1, width, height))
        else:
            pygame.draw.ellipse(screen, color, (x1, y1, width, height), 1)

    def _draw_line(self, screen: pygame.Surface, cmd: dict):
        """Draw a line between two points"""
        x1 = cmd.get('x1', 0)
        y1 = cmd.get('y1', 0)
        x2 = cmd.get('x2', 100)
        y2 = cmd.get('y2', 100)
        color = self._parse_color(cmd.get('color', '#FFFFFF'))

        # Draw line with width of 1 pixel
        pygame.draw.line(screen, color, (int(x1), int(y1)), (int(x2), int(y2)), 1)

    def _draw_sprite(self, screen: pygame.Surface, cmd: dict):
        """Draw a sprite at specified position"""
        sprite_name = cmd.get('sprite_name', '')
        x = cmd.get('x', 0)
        y = cmd.get('y', 0)
        subimage = cmd.get('subimage', 0)

        # Look up the sprite in the loaded sprites
        if sprite_name not in self.sprites:
            logger.error(f"⚠️ Warning: Sprite '{sprite_name}' not found for draw_sprite")
            return

        sprite = self.sprites[sprite_name]

        # Handle animated sprites (multiple frames)
        if len(sprite.frames) > 0:
            # Use the specified subimage (frame index)
            frame_index = int(subimage) % len(sprite.frames)
            frame_surface = sprite.frames[frame_index]
            screen.blit(frame_surface, (int(x), int(y)))
        elif sprite.surface:
            # Single frame sprite
            screen.blit(sprite.surface, (int(x), int(y)))
        else:
            logger.warning(f"⚠️ Warning: Sprite '{sprite_name}' has no surface to draw")

    def _draw_background(self, screen: pygame.Surface, cmd: dict):
        """Draw a background image at specified position, optionally tiled"""
        bg_name = cmd.get('background_name', '')
        x = cmd.get('x', 0)
        y = cmd.get('y', 0)
        tiled = cmd.get('tiled', False)

        # Look up the background in the game runner's backgrounds
        # The game runner reference is stored when action_executor is set
        game_runner = getattr(self, 'action_executor', None)
        if game_runner:
            game_runner = getattr(game_runner, 'game_runner', None)

        if not game_runner or bg_name not in game_runner.backgrounds:
            logger.warning(f"⚠️ Warning: Background '{bg_name}' not found for draw_background")
            return

        bg_surface = game_runner.backgrounds[bg_name]
        bg_width = bg_surface.get_width()
        bg_height = bg_surface.get_height()

        if tiled:
            # Tile the background across the entire screen
            screen_width = screen.get_width()
            screen_height = screen.get_height()

            # Calculate starting position (handle negative x, y for seamless scrolling)
            start_x = int(x) % bg_width - bg_width if x < 0 else int(x) % bg_width
            start_y = int(y) % bg_height - bg_height if y < 0 else int(y) % bg_height

            # If start position is positive, we need to start from a negative offset
            if start_x > 0:
                start_x -= bg_width
            if start_y > 0:
                start_y -= bg_height

            # Draw tiles
            current_y = start_y
            while current_y < screen_height:
                current_x = start_x
                while current_x < screen_width:
                    screen.blit(bg_surface, (current_x, current_y))
                    current_x += bg_width
                current_y += bg_height
        else:
            # Draw single background at position
            screen.blit(bg_surface, (int(x), int(y)))

    def _parse_color(self, color_str: str) -> tuple:
        """Parse color string to RGB tuple"""
        if isinstance(color_str, tuple):
            return color_str
        if isinstance(color_str, str) and color_str.startswith('#'):
            try:
                hex_color = color_str.lstrip('#')
                return tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))
            except Exception:
                pass
        return (255, 255, 255)  # Default to white

class GameRoom:
    """Represents a game room with instances"""

    def __init__(self, name: str, room_data: dict, action_executor=None, project_path=None, sprites_data=None):
        self.name = name
        self.width = room_data.get('width', 1024)
        self.height = room_data.get('height', 768)
        self.background_color = self.parse_color(room_data.get('background_color', '#87CEEB'))
        self.background_image_name = room_data.get('background_image', '')
        self.tile_horizontal = room_data.get('tile_horizontal', False)
        self.tile_vertical = room_data.get('tile_vertical', False)
        self.background_surface = None
        self.project_path = project_path
        self.sprites_data = sprites_data or {}
        self.instances: List[GameInstance] = []
        self.action_executor = action_executor

        # Spatial grid for collision optimization
        # Cell size of 64 pixels works well for 32x32 sprites
        self.grid_cell_size = 64
        self.spatial_grid: Dict[Tuple[int, int], List[GameInstance]] = {}

        # Don't load background image here - pygame display may not be ready yet
        # Background will be loaded later via load_background_image()

        # Load instances
        instances_data = room_data.get('instances', [])
        for instance_data in instances_data:
            instance = GameInstance(
                instance_data['object_name'],
                instance_data['x'],
                instance_data['y'],
                instance_data,
                action_executor=self.action_executor
            )

            # Check if this is a Thymio robot (by object name or special property)
            if instance_data.get('object_name', '').lower().startswith('thymio') or \
               instance_data.get('is_thymio', False):
                # Attach Thymio simulator to this instance
                instance.thymio_simulator = ThymioSimulator(
                    x=instance.x,
                    y=instance.y,
                    angle=0  # Initial angle
                )
                instance.is_thymio = True
                logger.debug(f"🤖 Created Thymio robot: {instance.object_name}")

            self.instances.append(instance)

        # Build initial spatial grid
        self.rebuild_spatial_grid()

    def rebuild_spatial_grid(self):
        """Rebuild the entire spatial grid from all instances"""
        self.spatial_grid.clear()
        for instance in self.instances:
            self._add_to_grid(instance)

    def _get_grid_cells(self, x: float, y: float, w: int = 32, h: int = 32) -> List[Tuple[int, int]]:
        """Get all grid cells that an object at (x, y) with size (w, h) occupies"""
        cell_size = self.grid_cell_size
        min_cell_x = int(x) // cell_size
        max_cell_x = int(x + w - 1) // cell_size
        min_cell_y = int(y) // cell_size
        max_cell_y = int(y + h - 1) // cell_size

        cells = []
        for cx in range(min_cell_x, max_cell_x + 1):
            for cy in range(min_cell_y, max_cell_y + 1):
                cells.append((cx, cy))
        return cells

    def _add_to_grid(self, instance: 'GameInstance'):
        """Add an instance to the spatial grid"""
        # Use cached dimensions for performance
        w = instance._cached_width
        h = instance._cached_height
        cells = self._get_grid_cells(instance.x, instance.y, w, h)
        for cell in cells:
            if cell not in self.spatial_grid:
                self.spatial_grid[cell] = []
            if instance not in self.spatial_grid[cell]:
                self.spatial_grid[cell].append(instance)

    def _remove_from_grid(self, instance: 'GameInstance'):
        """Remove an instance from the spatial grid"""
        # Remove from all cells (brute force but simple)
        for cell_instances in self.spatial_grid.values():
            if instance in cell_instances:
                cell_instances.remove(instance)

    def update_instance_grid_position(self, instance: 'GameInstance'):
        """Update an instance's position in the spatial grid"""
        self._remove_from_grid(instance)
        self._add_to_grid(instance)

    def update_dirty_instances(self):
        """Update spatial grid only for instances that have moved (lazy update)"""
        for instance in self.instances:
            if instance._grid_dirty:
                self._remove_from_grid(instance)
                self._add_to_grid(instance)
                instance._grid_dirty = False

    def get_nearby_instances(self, x: float, y: float, w: int = 32, h: int = 32) -> List['GameInstance']:
        """Get all instances that might collide with an object at (x, y) with size (w, h)

        We expand the search area by one cell in each direction to catch objects
        that might be on the border of adjacent cells.
        """
        cell_size = self.grid_cell_size
        # Calculate the cell range, expanded by 1 in each direction
        min_cell_x = int(x) // cell_size - 1
        max_cell_x = int(x + w - 1) // cell_size + 1
        min_cell_y = int(y) // cell_size - 1
        max_cell_y = int(y + h - 1) // cell_size + 1

        nearby = set()
        for cx in range(min_cell_x, max_cell_x + 1):
            for cy in range(min_cell_y, max_cell_y + 1):
                cell = (cx, cy)
                if cell in self.spatial_grid:
                    nearby.update(self.spatial_grid[cell])
        return list(nearby)

    def parse_color(self, color_str: str) -> Tuple[int, int, int]:
        """Parse color string to RGB tuple"""
        if color_str.startswith('#'):
            color_str = color_str[1:]

        try:
            r = int(color_str[0:2], 16)
            g = int(color_str[2:4], 16)
            b = int(color_str[4:6], 16)
            return (r, g, b)
        except Exception:
            return (135, 206, 235)  # Default sky blue

    def load_background_image(self):
        """Load background image from project assets"""
        if not self.background_image_name or not self.project_path:
            return

        try:
            # Look in both backgrounds and sprites
            for asset_type in ['backgrounds', 'sprites']:
                if self.background_image_name in self.sprites_data.get(asset_type, {}):
                    asset_data = self.sprites_data[asset_type][self.background_image_name]
                    file_path = asset_data.get('file_path', '')
                    if file_path:
                        full_path = Path(self.project_path) / file_path
                        if full_path.exists():
                            self.background_surface = pygame.image.load(str(full_path)).convert()
                            logger.debug(f"🖼️ Loaded background image: {self.background_image_name}")
                            return

            # Also check sprites_data directly (it might already be merged)
            if self.background_image_name in self.sprites_data:
                asset_data = self.sprites_data[self.background_image_name]
                file_path = asset_data.get('file_path', '')
                if file_path:
                    full_path = Path(self.project_path) / file_path
                    if full_path.exists():
                        self.background_surface = pygame.image.load(str(full_path)).convert()
                        logger.debug(f"🖼️ Loaded background image: {self.background_image_name}")
                        return

            logger.error(f"⚠️ Background image not found: {self.background_image_name}")
        except Exception as e:
            logger.error(f"❌ Error loading background image: {e}")

    def set_sprites_for_instances(self, sprites: Dict[str, GameSprite], objects: Dict[str, dict]):
        """Set sprites for all instances based on their object types"""
        for instance in self.instances:
            # Get object data
            if instance.object_name in objects:
                object_data = objects[instance.object_name]
                instance.set_object_data(object_data)

                # Get sprite name from object
                sprite_name = object_data.get('sprite', '')
                if sprite_name and sprite_name in sprites:
                    instance.set_sprite(sprites[sprite_name])
                # else: No sprite assigned - instance.sprite remains None
                # The render method will skip instances with no sprite

    def create_default_sprite_for_object(self, object_name: str) -> GameSprite:
        """Create a default sprite for an object"""
        # Generate color from object name hash for consistency
        hash_val = hash(object_name)
        color = (
            (hash_val % 128) + 127,
            ((hash_val >> 8) % 128) + 127,
            ((hash_val >> 16) % 128) + 127
        )

        # Create sprite surface
        surface = pygame.Surface((32, 32))
        surface.fill(color)
        pygame.draw.rect(surface, (0, 0, 0), (0, 0, 32, 32), 2)  # Black border

        # Create sprite object
        sprite = GameSprite("")  # Empty path since we're creating manually
        sprite.surface = surface
        sprite.width = 32
        sprite.height = 32

        return sprite

    def render(self, screen: pygame.Surface):
        """Render the room and all its instances"""
        # Clear screen with background color
        screen.fill(self.background_color)

        # Draw background image if present
        if self.background_surface:
            img_width = self.background_surface.get_width()
            img_height = self.background_surface.get_height()

            if self.tile_horizontal or self.tile_vertical:
                # Tile the background
                x_count = (self.width // img_width) + 2 if self.tile_horizontal else 1
                y_count = (self.height // img_height) + 2 if self.tile_vertical else 1

                for x_tile in range(x_count):
                    for y_tile in range(y_count):
                        x_pos = x_tile * img_width if self.tile_horizontal else 0
                        y_pos = y_tile * img_height if self.tile_vertical else 0

                        if x_pos < self.width and y_pos < self.height:
                            screen.blit(self.background_surface, (x_pos, y_pos))
            else:
                # Stretch to fill room
                scaled_bg = pygame.transform.scale(self.background_surface, (self.width, self.height))
                screen.blit(scaled_bg, (0, 0))

        # Render all instances sorted by depth (higher depth = drawn first/behind)
        # In GameMaker, lower depth values are drawn on top (in front)
        sorted_instances = sorted(self.instances, key=lambda inst: getattr(inst, 'depth', 0), reverse=True)
        for instance in sorted_instances:
            # Regular instances render their sprites
            if not getattr(instance, 'is_thymio', False):
                instance.render(screen)

        # Render Thymio robots separately (on top)
        for instance in self.instances:
            if getattr(instance, 'is_thymio', False) and hasattr(instance, 'thymio_simulator'):
                # Get render data from simulator and pass to renderer
                # Note: thymio_renderer is accessed from game_runner
                pass  # Will be handled by game_runner's render method

class GameRunner:
    """Enhanced game runner that properly renders rooms with objects"""

    def __init__(self, project_path: str = None):
        self.running = False
        self.screen = None
        self.clock = None
        self.project_data = None
        self.project_path = None

        # Global game state (Score/Lives/Health system) - must be before ActionExecutor
        self.score = 0
        self.lives = 3
        self.health = 100.0
        self.highscores = []  # List of (name, score) tuples
        self.highscore_max_entries = 10  # Maximum entries in highscore table
        self.highscore_file = None  # Path to highscore file (set when project loads)

        # Global variables storage (user-defined variables accessible from any instance)
        self.global_variables: Dict[str, Any] = {}

        # Shared action executor for all instances (pass self for global state access)
        self.action_executor = ActionExecutor(game_runner=self)

        # Register Thymio action handlers
        register_thymio_actions(self.action_executor)

        # Load plugins
        logger.info("🔌 Loading action/event plugins...")
        self.plugin_loader = load_all_plugins(self.action_executor)

        # Game assets
        self.sprites: Dict[str, GameSprite] = {}
        self.backgrounds: Dict[str, pygame.Surface] = {}  # Background surfaces
        self.sounds: Dict[str, Any] = {}  # pygame.mixer.Sound objects
        self.music_files: Dict[str, str] = {}  # music name -> file path
        self.rooms: Dict[str, GameRoom] = {}
        self.current_room = None

        # Thymio robot renderer (shared for all Thymio robots)
        self.thymio_renderer = ThymioRenderer()

        # Game settings
        self.fps = 60
        self.window_width = 800
        self.window_height = 600

        # Caption display settings (like GM's "Display score in caption")
        # By default, nothing shows until the value is used in the game
        self.show_score_in_caption = False
        self.show_lives_in_caption = False
        self.show_health_in_caption = False
        self.window_caption = ""  # Custom caption prefix

        # Language for caption translations (default to English)
        self.language = 'en'

        # If project path provided, load it
        if project_path:
            self.load_project_data_only(project_path)

    def is_game_running(self):
        """Check if game is currently running"""
        return self.running

    def load_project_data_only(self, project_path: str) -> bool:
        """Load project data without loading sprites (sprites loaded later)"""
        try:
            path = Path(project_path)

            # If it's a directory, look for project.json inside
            if path.is_dir():
                self.project_path = path
                project_file = path / "project.json"
            # If it's a file, use it directly
            elif path.is_file() and path.name == "project.json":
                self.project_path = path.parent
                project_file = path
            else:
                logger.error(f"Invalid project path: {project_path}")
                return False

            if not project_file.exists():
                logger.error(f"Project file not found: {project_file}")
                return False

            # Load project data
            with open(project_file, 'r') as f:
                self.project_data = json.load(f)

            # Load asset data from separate files if they exist
            self._load_rooms_from_files()
            self._load_objects_from_files()
            self._load_sprites_from_files()

            logger.info(f"Loaded project: {self.project_data.get('name', 'Untitled')}")

            # Load project settings
            self._load_project_settings()

            # Set up highscore file path and load existing scores
            self.highscore_file = self.project_path / "highscores.json"
            self.load_highscores()

            # Only load rooms (without sprites for instances yet)
            self.load_rooms_without_sprites()

            return True

        except Exception as e:
            logger.error(f"Error loading project: {e}")
            import traceback
            traceback.print_exc()
            return False

    def _load_rooms_from_files(self) -> None:
        """Load room instance data from separate files in rooms/ directory"""
        rooms_dir = self.project_path / "rooms"

        if not rooms_dir.exists():
            logger.debug("DEBUG: No rooms/ directory found, using embedded room data")
            return

        rooms_data = self.project_data.get('assets', {}).get('rooms', {})

        for room_name, room_data in rooms_data.items():
            room_file = rooms_dir / f"{room_name}.json"

            if room_file.exists():
                try:
                    with open(room_file, 'r') as f:
                        file_room_data = json.load(f)

                    # Merge file data into room data (file takes precedence for instances)
                    if 'instances' in file_room_data:
                        room_data['instances'] = file_room_data['instances']
                        logger.debug(f"📂 Loaded room: {room_name} ({len(room_data['instances'])} instances from file)")

                    # Also copy other room properties from file if present
                    for key in ['width', 'height', 'background_color', 'background_image',
                               'tile_horizontal', 'tile_vertical']:
                        if key in file_room_data:
                            room_data[key] = file_room_data[key]

                except Exception as e:
                    logger.error(f"⚠️ Failed to load room file {room_file}: {e}")
            else:
                # No external file - use embedded instances (legacy format)
                if room_data.get('instances'):
                    logger.debug(f"📂 Room {room_name}: using embedded instances")

    def _load_objects_from_files(self) -> None:
        """Load object data from separate files in objects/ directory"""
        objects_dir = self.project_path / "objects"

        if not objects_dir.exists():
            logger.error(f"📂 Objects directory not found: {objects_dir}")
            return

        logger.info(f"📂 Loading objects from: {objects_dir}")
        objects_data = self.project_data.get('assets', {}).get('objects', {})

        for object_name, object_data in objects_data.items():
            object_file = objects_dir / f"{object_name}.json"

            if object_file.exists():
                try:
                    with open(object_file, 'r') as f:
                        file_object_data = json.load(f)

                    # Merge file data into object data (file takes precedence)
                    # Copy all properties from file, especially events
                    for key in ['events', 'sprite', 'visible', 'solid', 'persistent',
                               'depth', 'parent', 'mask', 'imported', 'created', 'modified']:
                        if key in file_object_data:
                            object_data[key] = file_object_data[key]

                    event_count = len(file_object_data.get('events', {}))
                    logger.debug(f"📂 Loaded object: {object_name} ({event_count} events from file)")

                except Exception as e:
                    logger.error(f"⚠️ Failed to load object file {object_file}: {e}")

    def _load_sprites_from_files(self) -> None:
        """Load sprite data from separate files in sprites/ directory"""
        sprites_dir = self.project_path / "sprites"

        if not sprites_dir.exists():
            return

        sprites_data = self.project_data.get('assets', {}).get('sprites', {})

        for sprite_name, sprite_data in sprites_data.items():
            sprite_file = sprites_dir / f"{sprite_name}.json"

            if sprite_file.exists():
                try:
                    with open(sprite_file, 'r') as f:
                        file_sprite_data = json.load(f)

                    # Merge file data into sprite data (file takes precedence)
                    for key in ['frames', 'width', 'height', 'origin_x', 'origin_y',
                               'collision_mask', 'bbox_left', 'bbox_right', 'bbox_top',
                               'bbox_bottom', 'imported', 'created', 'modified', 'file_path']:
                        if key in file_sprite_data:
                            sprite_data[key] = file_sprite_data[key]

                except Exception as e:
                    logger.error(f"⚠️ Failed to load sprite file {sprite_file}: {e}")

    def _load_project_settings(self) -> None:
        """Load game settings from project data"""
        settings = self.project_data.get('settings', {})

        # Load lives/score/health initial values
        self.lives = settings.get('starting_lives', 3)
        self.score = settings.get('starting_score', 0)
        self.health = settings.get('starting_health', 100.0)

        # Load caption display settings
        self.show_lives_in_caption = settings.get('show_lives_in_caption', False)
        self.show_score_in_caption = settings.get('show_score_in_caption', False)
        self.show_health_in_caption = settings.get('show_health_in_caption', False)

        logger.debug(f"⚙️ Settings: lives={self.lives}, score={self.score}, health={self.health}")

    def load_sprites(self):
        """Load all sprites from the project (called after pygame.display is initialized)"""
        sprites_data = self.project_data.get('assets', {}).get('sprites', {})

        logger.info(f"Loading {len(sprites_data)} sprites...")

        for sprite_name, sprite_info in sprites_data.items():
            try:
                file_path = sprite_info.get('file_path', '')
                if file_path:
                    full_path = self.project_path / file_path
                    # Pass sprite_info to enable animation support
                    sprite = GameSprite(str(full_path), sprite_info)
                    self.sprites[sprite_name] = sprite
                    logger.debug(f"  âœ… Loaded sprite: {sprite_name} ({sprite.width}x{sprite.height})")
                else:
                    logger.debug(f"  âš ï¸  Sprite {sprite_name} has no file path")
            except Exception as e:
                logger.error(f"  âŒ Error loading sprite {sprite_name}: {e}")

    def load_backgrounds(self):
        """Load all background images from the project (called after pygame.display is initialized)"""
        backgrounds_data = self.project_data.get('assets', {}).get('backgrounds', {})

        if not backgrounds_data:
            return

        logger.info(f"Loading {len(backgrounds_data)} backgrounds...")

        for bg_name, bg_info in backgrounds_data.items():
            try:
                file_path = bg_info.get('file_path', '')
                if file_path:
                    full_path = self.project_path / file_path
                    if full_path.exists():
                        surface = pygame.image.load(str(full_path)).convert_alpha()
                        self.backgrounds[bg_name] = surface
                        logger.debug(f"  âœ… Loaded background: {bg_name} ({surface.get_width()}x{surface.get_height()})")
                    else:
                        logger.debug(f"  âš ï¸  Background file not found: {full_path}")
                else:
                    logger.debug(f"  âš ï¸  Background {bg_name} has no file path")
            except Exception as e:
                logger.error(f"  âŒ Error loading background {bg_name}: {e}")

    def load_sounds(self):
        """Load all sounds from the project (called after pygame.mixer is initialized)"""
        sounds_data = self.project_data.get('assets', {}).get('sounds', {})

        if not sounds_data:
            return

        logger.info(f"Loading {len(sounds_data)} sounds...")

        for sound_name, sound_info in sounds_data.items():
            try:
                file_path = sound_info.get('file_path', '')
                
                # Try to load full sound metadata from individual JSON file
                kind = sound_info.get('kind', None)
                volume = sound_info.get('volume', 1.0)
                
                if kind is None:
                    # Load from individual sound JSON file
                    sound_json_path = self.project_path / 'sounds' / f'{sound_name}.json'
                    if sound_json_path.exists():
                        with open(sound_json_path, 'r') as f:
                            sound_metadata = json.load(f)
                            kind = sound_metadata.get('kind', 'sound')
                            volume = sound_metadata.get('volume', volume)
                            if not file_path:
                                file_path = sound_metadata.get('file_path', '')
                    else:
                        kind = 'sound'  # Default to sound effect

                if file_path:
                    full_path = self.project_path / file_path

                    if not full_path.exists():
                        logger.error(f"  ⚠️  Sound file not found: {full_path}")
                        continue

                    if kind == 'music':
                        # Music is streamed, just store the path
                        self.music_files[sound_name] = str(full_path)
                        logger.debug(f"  🎵 Loaded music: {sound_name}")
                    else:
                        # Sound effects are loaded into memory
                        sound = pygame.mixer.Sound(str(full_path))
                        # Apply default volume from sound definition
                        sound.set_volume(float(volume))
                        self.sounds[sound_name] = sound
                        logger.debug(f"  🔊 Loaded sound: {sound_name}")
                else:
                    logger.debug(f"  ⚠️  Sound {sound_name} has no file path")
            except Exception as e:
                logger.error(f"  ❌ Error loading sound {sound_name}: {e}")

    def load_rooms_without_sprites(self):
        """Load rooms but don't assign sprites to instances yet"""
        rooms_data = self.project_data.get('assets', {}).get('rooms', {})
        assets = self.project_data.get('assets', {})

        logger.info(f"Loading {len(rooms_data)} rooms...")

        for room_name, room_info in rooms_data.items():
            try:
                room = GameRoom(
                    room_name,
                    room_info,
                    action_executor=self.action_executor,
                    project_path=self.project_path,
                    sprites_data=assets  # Pass all assets so room can find backgrounds/sprites
                )
                # Don't set sprites yet - will do this after pygame.display is ready
                self.rooms[room_name] = room
                logger.debug(f"  Loaded room: {room_name} ({len(room.instances)} instances)")
            except Exception as e:
                logger.error(f"  Error loading room {room_name}: {e}")
                import traceback
                traceback.print_exc()

    def assign_sprites_to_rooms(self):
        """Assign loaded sprites to room instances"""
        objects_data = self.project_data.get('assets', {}).get('objects', {})

        logger.info("Assigning sprites to room instances...")
        for room_name, room in self.rooms.items():
            room.set_sprites_for_instances(self.sprites, objects_data)

            # Count instances with sprites
            sprites_assigned = sum(1 for instance in room.instances if instance.sprite)
            logger.debug(f"  Room {room_name}: {sprites_assigned}/{len(room.instances)} instances have sprites")

    def load_room_backgrounds(self):
        """Load background images for all rooms (called after pygame.display is initialized)"""
        logger.info("Loading room background images...")
        for room_name, room in self.rooms.items():
            if room.background_image_name:
                room.load_background_image()
                if room.background_surface:
                    logger.debug(f"  Room {room_name}: background '{room.background_image_name}' loaded")
                else:
                    logger.error(f"  Room {room_name}: background '{room.background_image_name}' NOT found")

    def find_starting_room(self) -> Optional[str]:
        """Find a room to start the game in - uses room_order if available"""
        if not self.rooms:
            return None

        # Use room_order from project data if available (first room in order)
        if self.project_data:
            room_order = self.project_data.get('room_order', [])
            if room_order:
                # Return first room in the order that actually exists
                for room_name in room_order:
                    if room_name in self.rooms:
                        return room_name

        # Fallback: just use the first room in the dictionary
        return list(self.rooms.keys())[0]

    def test_game(self, project_path: str, language: str = 'en') -> bool:
        """Test run the game from project"""
        logger.info(f"Testing game from project: {project_path}")
        self.language = language

        # Load project data (but not sprites yet)
        if not self.load_project_data_only(project_path):
            logger.error("Failed to load project")
            return False

        # Find starting room
        starting_room = self.find_starting_room()
        if not starting_room:
            logger.debug("No rooms found in project")
            return False

        logger.info(f"Starting with room: {starting_room}")
        self.current_room = self.rooms[starting_room]

        # Set window size based on room
        self.window_width = self.current_room.width
        self.window_height = self.current_room.height

        # Run the game (sprites will be loaded after pygame.display is ready)
        return self.run_game_loop()

    def run_game_loop(self) -> bool:
        """Main game loop"""
        try:
            # Initialize pygame
            pygame.init()

            # Initialize mixer for audio (after pygame.init)
            try:
                pygame.mixer.init()
                logger.info("🔊 Audio mixer initialized")
            except Exception as e:
                logger.error(f"⚠️  Audio mixer failed to initialize: {e}")

            # Create display
            self.screen = pygame.display.set_mode((self.window_width, self.window_height))
            pygame.display.set_caption(f"PyGameMaker - {self.project_data.get('name', 'Game')}")

            # Initialize clock
            self.clock = pygame.time.Clock()

            logger.info(f"Game window: {self.window_width}x{self.window_height}")

            # NOW load sprites (after pygame.display is initialized)
            logger.info("\n🎮 Loading sprites after pygame.display initialization...")
            self.load_sprites()

            # Load background images (after pygame.display is initialized)
            self.load_backgrounds()

            # Load sounds (after mixer is initialized)
            self.load_sounds()

            # Load background images for all rooms
            self.load_room_backgrounds()

            # Assign sprites to room instances
            self.assign_sprites_to_rooms()

            logger.debug(f"\nCurrent room: {self.current_room.name}")
            logger.debug(f"Room instances: {len(self.current_room.instances)}")

            # Count instances by type for summary
            instance_counts = {}
            for instance in self.current_room.instances:
                obj_name = instance.object_name
                instance_counts[obj_name] = instance_counts.get(obj_name, 0) + 1

            logger.debug("Instance summary:")
            for obj_name, count in sorted(instance_counts.items()):
                logger.debug(f"  {obj_name}: {count}")

            # IMPORTANT: Execute create events for starting room instances
            logger.info(f"\n🎬 Triggering create events for starting room: {self.current_room.name}")
            for instance in self.current_room.instances:
                if instance.object_data and "events" in instance.object_data:
                    self.action_executor.execute_event(instance, "create", instance.object_data["events"])

            # Execute room_start event for all instances (after create events)
            logger.info(f"🚪 Triggering room_start events for starting room: {self.current_room.name}")
            self.trigger_room_start_event()

            self.running = True

            # Main game loop
            while self.running:
                # ========== GameMaker 7.0 Event Execution Order ==========
                # 1. BEGIN STEP (before everything else)
                for instance in self.current_room.instances:
                    if instance.object_data and "events" in instance.object_data:
                        events = instance.object_data["events"]
                        if "begin_step" in events:
                            instance.action_executor.execute_event(instance, "begin_step", events)

                # 2. ALARMS (countdown and trigger before keyboard/step)
                for instance in self.current_room.instances:
                    if instance.object_data and "events" in instance.object_data:
                        events = instance.object_data["events"]
                        # Process all 12 alarms
                        for alarm_num in range(12):
                            if instance.alarm[alarm_num] > 0:
                                instance.alarm[alarm_num] -= 1
                                if instance.alarm[alarm_num] == 0:
                                    # Alarm triggered! Execute alarm event
                                    instance.alarm[alarm_num] = -1  # Reset to disabled
                                    alarm_key = f"alarm_{alarm_num}"

                                    # Check for alarm event in different structures:
                                    # 1. Nested: events["alarm"]["alarm_0"]
                                    # 2. Flat: events["alarm_0"]
                                    alarm_event = None
                                    if "alarm" in events and alarm_key in events["alarm"]:
                                        alarm_event = events["alarm"][alarm_key]
                                    elif alarm_key in events:
                                        alarm_event = events[alarm_key]

                                    if alarm_event and isinstance(alarm_event, dict) and "actions" in alarm_event:
                                        logger.debug(f"⏰ Alarm {alarm_num} triggered for {instance.object_name}")
                                        for action_data in alarm_event["actions"]:
                                            instance.action_executor.execute_action(instance, action_data)

                # 3. KEYBOARD/MOUSE EVENTS
                self.handle_events()

                # 4. STEP EVENT (main game logic)
                for instance in self.current_room.instances:
                    instance.step()

                # 5. MOVEMENT (apply physics: gravity, friction, hspeed/vspeed)
                # 6. COLLISION (detect and execute collision events)
                self.update()

                # Update Thymio simulators and trigger events
                self.update_thymio_robots()

                # 7. END STEP (after collisions, before drawing)
                for instance in self.current_room.instances:
                    if instance.object_data and "events" in instance.object_data:
                        events = instance.object_data["events"]
                        if "end_step" in events:
                            instance.action_executor.execute_event(instance, "end_step", events)

                # Trigger destroy events for instances marked for destruction
                for instance in self.current_room.instances:
                    if instance.to_destroy:
                        if instance.object_data and "events" in instance.object_data:
                            events = instance.object_data["events"]
                            if "destroy" in events:
                                logger.debug(f"💥 Triggering destroy event for {instance.object_name}")
                                instance.action_executor.execute_event(instance, "destroy", events)

                # Remove destroyed instances
                old_count = len(self.current_room.instances)
                self.current_room.instances = [inst for inst in self.current_room.instances if not inst.to_destroy]
                if len(self.current_room.instances) != old_count:
                    # Rebuild spatial grid after removing instances
                    self.current_room.rebuild_spatial_grid()

                # Clear screen
                self.screen.fill((135, 206, 235))  # Sky blue

                # Render
                self.render()

                # Check for pending messages and display them
                self.process_pending_messages()

                # Control framerate
                self.clock.tick(self.fps)

            return True

        except Exception as e:
            logger.error(f"Error in game loop: {e}")
            import traceback
            traceback.print_exc()
            return False

        finally:
            self.cleanup()

    def handle_events(self):
        """Handle pygame events"""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.stop_game()
            elif event.type == pygame.KEYDOWN:
                # Check for ESC key to quit game
                if event.key == pygame.K_ESCAPE:
                    self.stop_game()
                # Handle keyboard press events for all instances
                self.handle_keyboard_press(event.key)
            elif event.type == pygame.KEYUP:
                # Handle keyboard release events
                self.handle_keyboard_release(event.key)
            elif event.type == pygame.MOUSEBUTTONDOWN:
                # Handle mouse button press
                self.handle_mouse_press(event.button, event.pos)
            elif event.type == pygame.MOUSEBUTTONUP:
                # Handle mouse button release
                self.handle_mouse_release(event.button, event.pos)
            elif event.type == pygame.MOUSEMOTION:
                # Handle mouse movement
                self.handle_mouse_motion(event.pos)

    def _get_key_name(self, key):
        """Map pygame key code to key name string"""
        # Arrow keys
        arrow_keys = {
            pygame.K_LEFT: "left",
            pygame.K_RIGHT: "right",
            pygame.K_UP: "up",
            pygame.K_DOWN: "down",
        }
        if key in arrow_keys:
            return arrow_keys[key]

        # Letter keys (a-z)
        if pygame.K_a <= key <= pygame.K_z:
            return chr(key)

        # Number keys (0-9)
        if pygame.K_0 <= key <= pygame.K_9:
            return chr(key)

        # Special keys
        special_keys = {
            pygame.K_SPACE: "space",
            pygame.K_RETURN: "enter",
            pygame.K_ESCAPE: "escape",
            pygame.K_TAB: "tab",
            pygame.K_BACKSPACE: "backspace",
            pygame.K_DELETE: "delete",
            pygame.K_INSERT: "insert",
            pygame.K_HOME: "home",
            pygame.K_END: "end",
            pygame.K_PAGEUP: "pageup",
            pygame.K_PAGEDOWN: "pagedown",
            pygame.K_F1: "f1",
            pygame.K_F2: "f2",
            pygame.K_F3: "f3",
            pygame.K_F4: "f4",
            pygame.K_F5: "f5",
            pygame.K_F6: "f6",
            pygame.K_F7: "f7",
            pygame.K_F8: "f8",
            pygame.K_F9: "f9",
            pygame.K_F10: "f10",
            pygame.K_F11: "f11",
            pygame.K_F12: "f12",
            pygame.K_LSHIFT: "shift",
            pygame.K_RSHIFT: "shift",
            pygame.K_LCTRL: "control",
            pygame.K_RCTRL: "control",
            pygame.K_LALT: "alt",
            pygame.K_RALT: "alt",
        }
        return special_keys.get(key)

    def handle_keyboard_press(self, key):
        """Handle keyboard press event"""
        if not self.current_room:
            return

        # Map pygame keys to sub-event keys
        sub_key = self._get_key_name(key)
        if not sub_key:
            return

        logger.debug(f"\n⌨️  Keyboard pressed: {sub_key}")

        events_found = False

        # Track which keys are pressed
        for instance in self.current_room.instances:
            if hasattr(instance, "keys_pressed"):
                instance.keys_pressed.add(sub_key)

            events = instance.object_data.get('events', {})

            # Helper to find key in dict (case-insensitive)
            def find_key_in_event(event_dict, key):
                """Find key in event dict, checking both lowercase and uppercase"""
                if key in event_dict:
                    return key
                upper_key = key.upper()
                if upper_key in event_dict:
                    return upper_key
                return None

            # Check for keyboard_press event
            if "keyboard_press" in events:
                keyboard_press_event = events["keyboard_press"]
                if isinstance(keyboard_press_event, dict):
                    found_key = find_key_in_event(keyboard_press_event, sub_key)
                    if found_key:
                        logger.debug(f"  ✅ Executing keyboard_press.{found_key} for {instance.object_name}")
                        events_found = True
                        sub_event_data = keyboard_press_event[found_key]
                        if isinstance(sub_event_data, dict) and "actions" in sub_event_data:
                            for action_data in sub_event_data["actions"]:
                                instance.action_executor.execute_action(instance, action_data)

            # Check for keyboard (held) event
            if "keyboard" in events:
                keyboard_event = events["keyboard"]
                if isinstance(keyboard_event, dict):
                    found_key = find_key_in_event(keyboard_event, sub_key)
                    if found_key:
                        logger.debug(f"  ✅ Executing keyboard.{found_key} for {instance.object_name}")
                        events_found = True
                        sub_event_data = keyboard_event[found_key]
                        if isinstance(sub_event_data, dict) and "actions" in sub_event_data:
                            for action_data in sub_event_data["actions"]:
                                instance.action_executor.execute_action(instance, action_data)
                # Removed error messages - it's normal for an object to not handle every key

            # Handle Thymio button events (keyboard mapping)
            if getattr(instance, 'is_thymio', False) and hasattr(instance, 'thymio_simulator'):
                thymio_button_map = {
                    'up': ('forward', 'thymio_button_forward'),
                    'down': ('backward', 'thymio_button_backward'),
                    'left': ('left', 'thymio_button_left'),
                    'right': ('right', 'thymio_button_right'),
                    'space': ('center', 'thymio_button_center')
                }

                if sub_key in thymio_button_map:
                    button_name, event_name = thymio_button_map[sub_key]
                    instance.thymio_simulator.set_button(button_name, True)

                    # Trigger Thymio button event
                    if event_name in events:
                        logger.debug(f"  🤖 Executing {event_name} for {instance.object_name}")
                        events_found = True
                        instance.action_executor.execute_event(instance, event_name, events)

        if not events_found:
            logger.debug(f"  ℹ️  No objects have keyboard events for '{sub_key}'")

    def handle_keyboard_release(self, key):
        """Handle keyboard release event - trigger user-defined keyboard_release events"""
        if not self.current_room:
            return

        # Map pygame keys to sub-event keys
        sub_key = self._get_key_name(key)
        if not sub_key:
            return

        logger.debug(f"\n⌨️  Keyboard released: {sub_key}")

        # Execute keyboard_release events for all instances
        for instance in self.current_room.instances:
            if not instance.object_data:
                continue

            # Remove key from pressed set
            if hasattr(instance, "keys_pressed"):
                instance.keys_pressed.discard(sub_key)

            events = instance.object_data.get('events', {})

            # Helper to find key in dict (case-insensitive)
            def find_key_in_event(event_dict, key):
                if key in event_dict:
                    return key
                upper_key = key.upper()
                if upper_key in event_dict:
                    return upper_key
                return None

            # Execute keyboard_release events from JSON (custom actions only)
            if "keyboard_release" in events:
                keyboard_release_event = events["keyboard_release"]
                if isinstance(keyboard_release_event, dict):
                    found_key = find_key_in_event(keyboard_release_event, sub_key)
                    if found_key:
                        logger.debug(f"  ✅ Executing keyboard_release.{found_key} for {instance.object_name}")
                        sub_event_data = keyboard_release_event[found_key]
                        if isinstance(sub_event_data, dict) and "actions" in sub_event_data:
                            for action_data in sub_event_data["actions"]:
                                instance.action_executor.execute_action(instance, action_data)

            # Handle Thymio button release
            if getattr(instance, 'is_thymio', False) and hasattr(instance, 'thymio_simulator'):
                thymio_button_map = {
                    'up': 'forward',
                    'down': 'backward',
                    'left': 'left',
                    'right': 'right',
                    'space': 'center'
                }

                if sub_key in thymio_button_map:
                    button_name = thymio_button_map[sub_key]
                    instance.thymio_simulator.set_button(button_name, False)

    def handle_mouse_press(self, button, pos):
        """Handle mouse button press event"""
        if not self.current_room:
            return

        # Map pygame mouse buttons to event names
        button_map = {
            1: "left_button",
            2: "middle_button",
            3: "right_button",
        }

        button_name = button_map.get(button)
        if not button_name:
            return

        mouse_x, mouse_y = pos
        logger.debug(f"\n🖱️  Mouse pressed: {button_name} at ({mouse_x}, {mouse_y})")

        # Execute mouse events for all instances
        for instance in self.current_room.instances:
            if not instance.object_data:
                continue

            events = instance.object_data.get('events', {})

            # Check for mouse event
            if "mouse" in events:
                mouse_event = events["mouse"]
                if isinstance(mouse_event, dict) and button_name in mouse_event:
                    logger.debug(f"  ✅ Executing mouse.{button_name} for {instance.object_name}")
                    sub_event_data = mouse_event[button_name]
                    if isinstance(sub_event_data, dict) and "actions" in sub_event_data:
                        for action_data in sub_event_data["actions"]:
                            # Add mouse position to instance for actions to use
                            instance.mouse_x = mouse_x
                            instance.mouse_y = mouse_y
                            instance.action_executor.execute_action(instance, action_data)

    def handle_mouse_release(self, button, pos):
        """Handle mouse button release event"""
        if not self.current_room:
            return

        button_map = {
            1: "left_button_released",
            2: "middle_button_released",
            3: "right_button_released",
        }

        button_name = button_map.get(button)
        if not button_name:
            return

        mouse_x, mouse_y = pos

        # Execute mouse release events
        for instance in self.current_room.instances:
            if not instance.object_data:
                continue

            events = instance.object_data.get('events', {})

            if "mouse" in events:
                mouse_event = events["mouse"]
                if isinstance(mouse_event, dict) and button_name in mouse_event:
                    sub_event_data = mouse_event[button_name]
                    if isinstance(sub_event_data, dict) and "actions" in sub_event_data:
                        for action_data in sub_event_data["actions"]:
                            instance.mouse_x = mouse_x
                            instance.mouse_y = mouse_y
                            instance.action_executor.execute_action(instance, action_data)

    def handle_mouse_motion(self, pos):
        """Handle mouse movement event"""
        if not self.current_room:
            return

        mouse_x, mouse_y = pos

        # Execute mouse motion events
        for instance in self.current_room.instances:
            if not instance.object_data:
                continue

            events = instance.object_data.get('events', {})

            if "mouse" in events:
                mouse_event = events["mouse"]
                if isinstance(mouse_event, dict) and "mouse_move" in mouse_event:
                    sub_event_data = mouse_event["mouse_move"]
                    if isinstance(sub_event_data, dict) and "actions" in sub_event_data:
                        for action_data in sub_event_data["actions"]:
                            instance.mouse_x = mouse_x
                            instance.mouse_y = mouse_y
                            instance.action_executor.execute_action(instance, action_data)

    def update(self):
        """Update game logic"""
        if not self.current_room:
            return

        # Get objects data for solid checks
        objects_data = self.project_data.get('assets', {}).get('objects', {})

        # Check for room restart/transition flags FIRST
        for instance in self.current_room.instances:
            if hasattr(instance, 'restart_room_flag') and instance.restart_room_flag:
                logger.info("🔄 Restarting room...")
                self.restart_current_room()
                return

            if hasattr(instance, 'next_room_flag') and instance.next_room_flag:
                instance.next_room_flag = False  # Clear the flag first
                logger.info("➡️  Going to next room...")
                self.goto_next_room()
                return

            if hasattr(instance, 'previous_room_flag') and instance.previous_room_flag:
                instance.previous_room_flag = False  # Clear the flag first
                logger.info("⬅️  Going to previous room...")
                self.goto_previous_room()
                return

            if hasattr(instance, 'restart_game_flag') and instance.restart_game_flag:
                instance.restart_game_flag = False  # Clear the flag first
                logger.info("🔄 Restarting game...")
                self.restart_game()
                return


        # Apply physics (gravity and friction) to all instances
        import math
        for instance in self.current_room.instances:
            # Apply gravity
            if hasattr(instance, 'gravity') and instance.gravity != 0:
                gravity_dir = getattr(instance, 'gravity_direction', 270)
                rad = math.radians(gravity_dir)
                instance.hspeed += instance.gravity * math.cos(rad)
                instance.vspeed -= instance.gravity * math.sin(rad)  # Negative because Y increases downward

            # Apply friction
            if hasattr(instance, 'friction') and instance.friction != 0:
                speed = math.sqrt(instance.hspeed ** 2 + instance.vspeed ** 2)
                if speed > 0:
                    # Reduce speed by friction amount
                    new_speed = max(0, speed - instance.friction)
                    if new_speed == 0:
                        instance.hspeed = 0
                        instance.vspeed = 0
                    else:
                        # Scale velocity to new speed
                        scale = new_speed / speed
                        instance.hspeed *= scale
                        instance.vspeed *= scale

        # Apply speed-based movement (hspeed, vspeed) with collision checking
        # Track blocked collisions per instance - deduplicate to avoid infinite bounce loops
        # Key: instance_id -> collision info with h_blocked/v_blocked flags
        # We key by instance only (not by blocker) so corner collisions with different walls merge
        blocked_collisions_map = {}

        for instance in self.current_room.instances:
            if hasattr(instance, 'hspeed') and instance.hspeed != 0:
                # Store intended position
                instance.intended_x = instance.x + instance.hspeed
                instance.intended_y = instance.y

                # Check collision - returns (can_move, blocking_instance)
                can_move, blocker = self.check_movement_collision_with_blocker(instance, objects_data)
                if can_move:
                    instance.x = instance.intended_x
                elif blocker:
                    # Movement blocked horizontally - track in map by instance only
                    key = id(instance)
                    if key not in blocked_collisions_map:
                        blocked_collisions_map[key] = {
                            'instance': instance,
                            'other_instance': blocker,  # Use first blocker for event
                            'self_hspeed': instance.hspeed,
                            'self_vspeed': instance.vspeed,
                            'h_blocked': False,
                            'v_blocked': False,
                        }
                    blocked_collisions_map[key]['h_blocked'] = True

                # Clean up
                delattr(instance, 'intended_x')
                delattr(instance, 'intended_y')

            if hasattr(instance, 'vspeed') and instance.vspeed != 0:
                # Store intended position
                instance.intended_x = instance.x
                instance.intended_y = instance.y + instance.vspeed

                # Check collision - returns (can_move, blocking_instance)
                can_move, blocker = self.check_movement_collision_with_blocker(instance, objects_data)
                if can_move:
                    instance.y = instance.intended_y
                elif blocker:
                    # Movement blocked vertically - track in map by instance only
                    key = id(instance)
                    if key not in blocked_collisions_map:
                        blocked_collisions_map[key] = {
                            'instance': instance,
                            'other_instance': blocker,  # Use first blocker for event
                            'self_hspeed': instance.hspeed,
                            'self_vspeed': instance.vspeed,
                            'h_blocked': False,
                            'v_blocked': False,
                        }
                    blocked_collisions_map[key]['v_blocked'] = True

                # Clean up
                delattr(instance, 'intended_x')
                delattr(instance, 'intended_y')

        # Fire collision events for blocked movements (deduplicated)
        for collision in blocked_collisions_map.values():
            instance = collision['instance']
            other = collision['other_instance']

            # Check if this instance has a collision event for the blocking object
            event_name = f"collision_with_{other.object_name}"
            events = instance._cached_object_data.get('events', {}) if instance._cached_object_data else {}

            if event_name in events:
                h_blocked = collision.get('h_blocked', False)
                v_blocked = collision.get('v_blocked', False)
                logger.debug(f"🎯 BLOCKED COLLISION: {instance.object_name} with {other.object_name} (h:{h_blocked}, v:{v_blocked})")
                instance.action_executor.execute_collision_event(
                    instance,
                    event_name,
                    events,
                    other,
                    collision_speeds={
                        'self_hspeed': collision['self_hspeed'],
                        'self_vspeed': collision['self_vspeed'],
                        'other_hspeed': other.hspeed,
                        'other_vspeed': other.vspeed,
                        'h_blocked': h_blocked,
                        'v_blocked': v_blocked,
                    }
                )
        # Handle intended movement with collision checking
        for instance in self.current_room.instances:
            if hasattr(instance, 'intended_x') and hasattr(instance, 'intended_y'):
                # Check if movement would collide with solid objects
                can_move = self.check_movement_collision(instance, objects_data)

                if can_move:
                    logger.debug(f"✅ Movement allowed: {instance.object_name} → ({instance.intended_x}, {instance.intended_y})")
                    instance.x = instance.intended_x
                    instance.y = instance.intended_y
                else:
                    logger.debug(f"❌ Movement blocked: {instance.object_name} (hit solid object)")

                # Clear intended movement
                delattr(instance, 'intended_x')
                delattr(instance, 'intended_y')

        # Check collision events - use global two-pass approach
        # First pass: Detect ALL collisions for ALL instances and capture speeds
        all_collisions = []
        for instance in self.current_room.instances:
            collisions = self.detect_collisions_for_instance(instance, objects_data)
            all_collisions.extend(collisions)

        # Second pass: Process ALL collision events with stored speeds
        for collision_data in all_collisions:
            self.process_collision_event(collision_data)

        # Third pass: Separate overlapping instances that have collision events
        # This handles the case where soko pushes box into wall - soko should be pushed back
        self.separate_overlapping_instances(objects_data)

        # Update spatial grid only for instances that moved (lazy update)
        # This is much faster than rebuilding the entire grid every frame
        self.current_room.update_dirty_instances()

        # Check for outside_room events
        self.check_outside_room_events()

        # NOTE: Step events are executed in the main game loop, not here
        # (see run_game_loop where instance.step() is called)

    def check_movement_collision(self, moving_instance, objects_data: dict) -> bool:
        """Check if intended movement would be blocked by solid objects.

        Only solid objects block movement. Non-solid objects don't block -
        they rely on collision events to handle interactions.
        """
        can_move, _ = self.check_movement_collision_with_blocker(moving_instance, objects_data)
        return can_move

    def check_movement_collision_with_blocker(self, moving_instance, objects_data: dict):
        """Check if intended movement would be blocked by solid objects.

        Returns:
            (can_move: bool, blocking_instance: GameInstance or None)
        """
        intended_x = moving_instance.intended_x
        intended_y = moving_instance.intended_y

        # Use cached dimensions
        w1 = moving_instance._cached_width
        h1 = moving_instance._cached_height

        # Use spatial grid for faster collision detection
        nearby_instances = self.current_room.get_nearby_instances(intended_x, intended_y, w1, h1)

        for other_instance in nearby_instances:
            if other_instance == moving_instance:
                continue

            # Use cached object data if available
            other_obj_data = other_instance._cached_object_data
            if not other_obj_data:
                other_obj_data = objects_data.get(other_instance.object_name, {})

            is_solid = other_obj_data.get('solid', False)

            # Only solid objects block movement
            if not is_solid:
                continue

            # Use cached dimensions
            w2 = other_instance._cached_width
            h2 = other_instance._cached_height

            # Check rectangle overlap at intended position
            if self.rectangles_overlap(intended_x, intended_y, w1, h1,
                                      other_instance.x, other_instance.y, w2, h2):
                return (False, other_instance)

        return (True, None)

    def separate_overlapping_instances(self, objects_data: dict):
        """Separate instances that are overlapping after collision events.

        When object A pushes object B but B can't move (hits solid), A should be pushed back.
        This only applies to instances that have collision events defined between them.
        """
        processed_pairs = set()

        for instance in self.current_room.instances:
            # Use pre-parsed collision targets for faster lookup
            collision_targets = instance._collision_targets
            if not collision_targets:
                continue

            # Use cached dimensions
            w1 = instance._cached_width
            h1 = instance._cached_height

            # Use spatial grid for faster collision detection
            nearby_instances = self.current_room.get_nearby_instances(instance.x, instance.y, w1, h1)

            for other_instance in nearby_instances:
                if other_instance == instance:
                    continue

                # Skip if we already processed this pair
                pair_key = (min(id(instance), id(other_instance)), max(id(instance), id(other_instance)))
                if pair_key in processed_pairs:
                    continue

                # Check if there's a collision event between these objects using pre-parsed targets
                if other_instance.object_name not in collision_targets:
                    continue

                # Use cached dimensions
                w2 = other_instance._cached_width
                h2 = other_instance._cached_height

                # Check if they're overlapping
                if self.rectangles_overlap(instance.x, instance.y, w1, h1,
                                          other_instance.x, other_instance.y, w2, h2):
                    # They're overlapping - push the moving instance back
                    # Determine which one was moving based on hspeed/vspeed
                    inst_moving = instance.hspeed != 0 or instance.vspeed != 0
                    other_moving = other_instance.hspeed != 0 or other_instance.vspeed != 0

                    if inst_moving and not other_moving:
                        # Push instance back to non-overlapping position
                        self.push_back_instance(instance, other_instance, w1, h1, w2, h2)
                    elif other_moving and not inst_moving:
                        # Push other_instance back
                        self.push_back_instance(other_instance, instance, w2, h2, w1, h1)

                    processed_pairs.add(pair_key)

    def push_back_instance(self, moving_inst, static_inst, w1, h1, w2, h2):
        """Push moving instance back so it no longer overlaps with static instance."""
        # Calculate overlap amounts
        overlap_left = (moving_inst.x + w1) - static_inst.x
        overlap_right = (static_inst.x + w2) - moving_inst.x
        overlap_top = (moving_inst.y + h1) - static_inst.y
        overlap_bottom = (static_inst.y + h2) - moving_inst.y

        # Find minimum overlap to resolve
        min_overlap = min(overlap_left, overlap_right, overlap_top, overlap_bottom)

        if min_overlap == overlap_left and overlap_left > 0:
            moving_inst.x = static_inst.x - w1
        elif min_overlap == overlap_right and overlap_right > 0:
            moving_inst.x = static_inst.x + w2
        elif min_overlap == overlap_top and overlap_top > 0:
            moving_inst.y = static_inst.y - h1
        elif min_overlap == overlap_bottom and overlap_bottom > 0:
            moving_inst.y = static_inst.y + h2

    def check_outside_room_events(self):
        """Check for instances that have moved outside the room boundaries.

        Triggers outside_room event when an instance is completely outside the room.
        GameMaker convention: triggers when the instance's sprite is fully outside.
        """
        if not self.current_room:
            return

        room_width = self.current_room.width
        room_height = self.current_room.height

        for instance in self.current_room.instances:
            # Skip if no object data or events
            if not instance.object_data or "events" not in instance.object_data:
                continue

            events = instance.object_data["events"]
            if "outside_room" not in events:
                continue

            # Get instance bounds
            w = instance._cached_width
            h = instance._cached_height

            # Check if completely outside room (not just partially)
            # Right edge is to the left of room left edge (x + w < 0)
            # Left edge is to the right of room right edge (x > room_width)
            # Bottom edge is above room top (y + h < 0)
            # Top edge is below room bottom (y > room_height)
            outside = (
                instance.x + w < 0 or          # Completely off left
                instance.x > room_width or     # Completely off right
                instance.y + h < 0 or          # Completely off top
                instance.y > room_height       # Completely off bottom
            )

            if outside:
                logger.debug(f"📤 outside_room event for {instance.object_name} at ({instance.x}, {instance.y})")
                instance.action_executor.execute_event(instance, "outside_room", events)

    def detect_collisions_for_instance(self, instance, objects_data: dict) -> list:
        """Detect collisions for an instance and capture speeds

        Returns a list of collision data dicts with speeds captured at detection time.
        Does NOT process the events - that's done separately.

        Optimized to use pre-parsed collision targets and cached dimensions.
        """
        collisions = []

        # Use pre-parsed collision targets (much faster than iterating all events)
        collision_targets = instance._collision_targets
        if not collision_targets:
            return collisions

        # Initialize collision tracking set if not exists
        if not hasattr(instance, '_active_collisions'):
            instance._active_collisions = set()

        # Initialize collision cooldown dict if not exists
        # Maps collision_key -> frames remaining in cooldown
        if not hasattr(instance, '_collision_cooldowns'):
            instance._collision_cooldowns = {}

        # Track which collisions are currently active this frame
        current_collisions = set()

        # Decrement cooldowns
        expired_keys = [key for key, frames in instance._collision_cooldowns.items() if frames <= 1]
        for key in expired_keys:
            del instance._collision_cooldowns[key]
        for key in instance._collision_cooldowns:
            instance._collision_cooldowns[key] -= 1

        # Get nearby instances using spatial grid for faster detection
        # Use cached dimensions instead of sprite lookup
        w1 = instance._cached_width
        h1 = instance._cached_height
        nearby_instances = self.current_room.get_nearby_instances(instance.x, instance.y, w1, h1)

        # Cache instance speeds (avoid repeated getattr)
        inst_hspeed = instance.hspeed
        inst_vspeed = instance.vspeed

        # Use pre-parsed collision targets instead of iterating all events
        for target_object, event_data in collision_targets.items():
            event_name = f"collision_with_{target_object}"

            # Check collision with target object (only nearby instances)
            for other_instance in nearby_instances:
                if other_instance == instance:
                    continue

                if other_instance.object_name == target_object:
                    if self.instances_overlap(instance, other_instance):
                        # Create unique collision key
                        collision_key = (id(other_instance), event_name)
                        current_collisions.add(collision_key)

                        # Cache other instance speeds for collision data
                        other_hspeed = other_instance.hspeed
                        other_vspeed = other_instance.vspeed

                        # Only fire event if this is a NEW collision AND not in cooldown
                        in_cooldown = collision_key in instance._collision_cooldowns
                        is_new_collision = collision_key not in instance._active_collisions

                        # Fire on new collision (not in cooldown)
                        should_fire = is_new_collision and not in_cooldown

                        if should_fire:
                            # Store the collision data with speeds captured NOW
                            collisions.append({
                                'instance': instance,
                                'event_name': event_name,
                                'events': instance._cached_object_data.get('events', {}),
                                'other_instance': other_instance,
                                # Capture speeds at moment of collision detection
                                'self_hspeed': inst_hspeed,
                                'self_vspeed': inst_vspeed,
                                'other_hspeed': other_hspeed,
                                'other_vspeed': other_vspeed,
                            })
                            # Short cooldown (5 frames) prevents double-trigger in same collision
                            # This is short enough to allow continuous pushing at normal speeds
                            instance._collision_cooldowns[collision_key] = 5
                        # Don't break - continue checking for other instances of this type
                        # and other collision events (e.g., obj_box_stored at same position as obj_store)

        # Update active collisions for next frame
        instance._active_collisions = current_collisions

        return collisions

    def process_collision_event(self, collision_data: dict):
        """Process a single collision event with stored speeds"""
        instance = collision_data['instance']
        event_name = collision_data['event_name']
        events = collision_data['events']
        other_instance = collision_data['other_instance']

        logger.debug(f"🎯 COLLISION DETECTED: {instance.object_name} with {other_instance.object_name}")
        logger.debug(f"   Stored speeds - self: ({collision_data['self_hspeed']}, {collision_data['self_vspeed']}), other: ({collision_data['other_hspeed']}, {collision_data['other_vspeed']})")

        # Pass other_instance and collision speeds as context for collision actions
        instance.action_executor.execute_collision_event(
            instance,
            event_name,
            events,
            other_instance,
            collision_speeds={
                'self_hspeed': collision_data['self_hspeed'],
                'self_vspeed': collision_data['self_vspeed'],
                'other_hspeed': collision_data['other_hspeed'],
                'other_vspeed': collision_data['other_vspeed'],
            }
        )

    def instances_overlap(self, inst1, inst2) -> bool:
        """Check if two instances overlap"""
        # Use cached dimensions for performance
        w1 = inst1._cached_width
        h1 = inst1._cached_height
        w2 = inst2._cached_width
        h2 = inst2._cached_height

        return self.rectangles_overlap(inst1.x, inst1.y, w1, h1, inst2.x, inst2.y, w2, h2)

    def rectangles_overlap(self, x1, y1, w1, h1, x2, y2, w2, h2) -> bool:
        """Check if two rectangles overlap"""
        return not (x1 + w1 <= x2 or x2 + w2 <= x1 or y1 + h1 <= y2 or y2 + h2 <= y1)

    def check_collision_at_position(self, instance, check_x: float, check_y: float,
                                    object_type: str = "any", exclude_instance=None) -> bool:
        """Check if there's a collision at a given position

        Args:
            instance: The instance doing the check
            check_x: X position to check
            check_y: Y position to check
            object_type: Type of object to check for:
                - 'any': Only solid objects (non-solid don't block, collision events fire after move)
                - 'solid': Only solid objects
                - specific name: Only that specific object type
            exclude_instance: Additional instance to exclude (e.g., collision other)

        Returns:
            True if collision found, False otherwise
        """
        if not self.current_room:
            logger.debug("⚠️ check_collision_at_position: No current room!")
            return False

        # Use cached dimensions
        w1 = instance._cached_width
        h1 = instance._cached_height

        # Use spatial grid for faster collision detection
        nearby_instances = self.current_room.get_nearby_instances(check_x, check_y, w1, h1)

        # Cache instance's collision targets for checking stop_movement
        instance_collision_targets = instance._collision_targets

        for other_instance in nearby_instances:
            if other_instance == instance:
                continue
            # Also exclude the collision "other" instance (e.g., explorer pushing rock)
            if exclude_instance and other_instance == exclude_instance:
                continue

            # Use cached dimensions
            w2 = other_instance._cached_width
            h2 = other_instance._cached_height

            # Check if positions overlap
            if self.rectangles_overlap(check_x, check_y, w1, h1,
                                       other_instance.x, other_instance.y, w2, h2):
                # Use cached object data for properties
                other_obj_data = other_instance._cached_object_data
                if not other_obj_data:
                    objects_data = self.project_data.get('assets', {}).get('objects', {})
                    other_obj_data = objects_data.get(other_instance.object_name, {})

                is_solid = other_obj_data.get('solid', False)

                # Collision detected - check if it matches the filter
                if object_type == "any":
                    # Solid objects always block
                    if is_solid:
                        return True

                    # For non-solid objects, check if there's a collision event
                    # that has a "stop_movement" action using pre-parsed collision targets
                    target_name = other_instance.object_name
                    if target_name in instance_collision_targets:
                        # Check if the collision event has a stop_movement action
                        event_data = instance_collision_targets[target_name]
                        actions = event_data.get('actions', [])
                        for action in actions:
                            if action.get('action') == 'stop_movement':
                                return True
                        # Collision event exists but no stop_movement - continue checking other objects
                        continue
                    else:
                        # Also check if the OTHER object has a collision event with stop_movement
                        # using its pre-parsed collision targets
                        other_collision_targets = other_instance._collision_targets
                        if instance.object_name in other_collision_targets:
                            reverse_event_data = other_collision_targets[instance.object_name]
                            reverse_actions = reverse_event_data.get('actions', [])
                            for action in reverse_actions:
                                if action.get('action') == 'stop_movement':
                                    return True

                        # No blocking event for THIS object - continue checking other objects
                        continue

                elif object_type == "solid":
                    # "solid" means only solid objects
                    if is_solid:
                        return True
                else:
                    # Check for specific object type
                    if other_instance.object_name == object_type:
                        return True

        return False

    def restart_current_room(self):
        """Restart the current room"""
        if not self.current_room:
            return

        room_name = self.current_room.name
        logger.info(f"🔄 Restarting room: {room_name}")

        # Reload room from project data to reset all instances
        room_data = self.project_data.get('assets', {}).get('rooms', {}).get(room_name)
        if room_data:
            # Recreate the room from scratch
            assets = self.project_data.get('assets', {})
            objects_data = assets.get('objects', {})

            new_room = GameRoom(
                room_name,
                room_data,
                action_executor=self.action_executor,
                project_path=self.project_path,
                sprites_data=assets
            )

            # Assign sprites to instances
            new_room.set_sprites_for_instances(self.sprites, objects_data)

            # Load background if needed
            if new_room.background_image_name:
                new_room.load_background_image()

            # Replace the room in our dictionary
            self.rooms[room_name] = new_room
            self.current_room = new_room

            # Execute create events for all instances
            for instance in self.current_room.instances:
                if instance.object_data and "events" in instance.object_data:
                    instance.action_executor.execute_event(instance, "create", instance.object_data["events"])

            # Execute room_start event for all instances (after create events)
            self.trigger_room_start_event()

            logger.debug(f"✅ Room {room_name} restarted with {len(new_room.instances)} instances")

    def restart_game(self):
        """Restart the game from the first room with reset score/lives/health"""
        logger.info("🔄 Restarting game from first room...")

        # Reset score, lives, and health to starting values
        settings = self.project_data.get('settings', {})
        self.score = settings.get('starting_score', 0)
        self.lives = settings.get('starting_lives', 3)
        self.health = settings.get('starting_health', 100)

        logger.debug(f"  📊 Reset: Score={self.score}, Lives={self.lives}, Health={self.health}")

        # Get the first room
        room_list = self.get_room_list()
        if not room_list:
            logger.debug("  ⚠️ No rooms found to restart to")
            return

        first_room_name = room_list[0]
        logger.debug(f"  ➡️ Going to first room: {first_room_name}")

        # Recreate the first room from scratch (like restart_current_room does)
        room_data = self.project_data.get('assets', {}).get('rooms', {}).get(first_room_name)
        if room_data:
            assets = self.project_data.get('assets', {})
            objects_data = assets.get('objects', {})

            new_room = GameRoom(
                first_room_name,
                room_data,
                action_executor=self.action_executor,
                project_path=self.project_path,
                sprites_data=assets
            )

            # Assign sprites to instances
            new_room.set_sprites_for_instances(self.sprites, objects_data)

            # Load background if needed
            if new_room.background_image_name:
                new_room.load_background_image()

            # Resize window if needed
            if self.screen:
                room_width = new_room.width
                room_height = new_room.height
                current_width, current_height = self.screen.get_size()
                if room_width != current_width or room_height != current_height:
                    logger.debug(f"  📐 Resizing window to {room_width}x{room_height}")
                    self.screen = pygame.display.set_mode((room_width, room_height))

            # Replace the room in our dictionary
            self.rooms[first_room_name] = new_room
            self.current_room = new_room

            # Execute create events for all instances
            for instance in self.current_room.instances:
                if instance.object_data and "events" in instance.object_data:
                    instance.action_executor.execute_event(instance, "create", instance.object_data["events"])

            # Execute room_start event for all instances (after create events)
            self.trigger_room_start_event()

            logger.debug(f"  ✅ Game restarted with room '{first_room_name}' ({len(new_room.instances)} instances)")
        else:
            logger.debug(f"  ⚠️ Could not find room data for '{first_room_name}'")

    def goto_next_room(self):
        """Go to the next room"""
        logger.debug("🚪 goto_next_room called")
        if not self.current_room:
            logger.debug("❌ No current room!")
            return

        room_list = self.get_room_list()
        logger.debug(f"🔍 Room list: {room_list}")
        if not room_list:
            logger.debug("❌ Room list is empty!")
            return

        try:
            current_index = room_list.index(self.current_room.name)
            next_index = current_index + 1
            if next_index < len(room_list):
                next_room_name = room_list[next_index]
                logger.debug(f"➡️  Changing from '{self.current_room.name}' (index {current_index}) to '{next_room_name}' (index {next_index})")
                self.change_room(next_room_name)
            else:
                logger.debug(f"⚠️  Already at last room '{self.current_room.name}'")
        except ValueError:
            logger.debug(f"❌ Current room '{self.current_room.name}' not in room list")

    def goto_previous_room(self):
        """Go to the previous room"""
        logger.debug("🚪 goto_previous_room called")
        if not self.current_room:
            logger.debug("❌ No current room!")
            return

        room_list = self.get_room_list()
        logger.debug(f"🔍 Room list: {room_list}")
        if not room_list:
            logger.debug("❌ Room list is empty!")
            return

        try:
            current_index = room_list.index(self.current_room.name)
            if current_index > 0:
                prev_index = current_index - 1
                prev_room_name = room_list[prev_index]
                logger.debug(f"⬅️  Changing from '{self.current_room.name}' (index {current_index}) to '{prev_room_name}' (index {prev_index})")
                self.change_room(prev_room_name)
            else:
                logger.debug(f"⚠️  Already at first room '{self.current_room.name}'")
        except ValueError:
            logger.debug(f"❌ Current room '{self.current_room.name}' not in room list")

    def get_room_list(self) -> List[str]:
        """Get ordered list of room names"""
        if not self.project_data:
            return []

        rooms_data = self.project_data.get('assets', {}).get('rooms', {})
        room_order = self.project_data.get('room_order', [])

        if room_order:
            return [r for r in room_order if r in rooms_data]
        else:
            return list(rooms_data.keys())

    def trigger_room_end_event(self):
        """Trigger room_end event on all instances in current room"""
        if not self.current_room:
            return

        for instance in self.current_room.instances:
            if instance.object_data and "events" in instance.object_data:
                instance.action_executor.execute_event(instance, "room_end", instance.object_data["events"])

    def trigger_room_start_event(self):
        """Trigger room_start event on all instances in current room"""
        if not self.current_room:
            return

        for instance in self.current_room.instances:
            if instance.object_data and "events" in instance.object_data:
                instance.action_executor.execute_event(instance, "room_start", instance.object_data["events"])

    def change_room(self, room_name: str):
        """Change to a different room"""
        if room_name in self.rooms:
            # Trigger room_end event in the current room before leaving
            if self.current_room:
                self.trigger_room_end_event()

            logger.info(f"🚪 Changing to room: {room_name}")
            self.current_room = self.rooms[room_name]

            # Resize the window if room size is different
            if self.screen:
                room_width = self.current_room.width
                room_height = self.current_room.height
                current_width, current_height = self.screen.get_size()

                if room_width != current_width or room_height != current_height:
                    logger.debug(f"📐 Resizing window from {current_width}x{current_height} to {room_width}x{room_height}")
                    self.screen = pygame.display.set_mode((room_width, room_height))
                    logger.debug(f"✅ Window resized to {room_width}x{room_height}")

            # Execute create events for all instances
            for instance in self.current_room.instances:
                if instance.object_data and "events" in instance.object_data:
                    instance.action_executor.execute_event(instance, "create", instance.object_data["events"])

            # Execute room_start event for all instances (after create events)
            self.trigger_room_start_event()


    def get_caption_text(self, key: str) -> str:
        """Get translated caption text for a key (score, lives, health, room)"""
        translations = CAPTION_TRANSLATIONS.get(self.language, CAPTION_TRANSLATIONS['en'])
        return translations.get(key, key.capitalize())

    def update_caption(self):
        """Update window caption with score/lives/health if enabled"""
        parts = []

        if self.window_caption:
            parts.append(self.window_caption)

        if self.show_score_in_caption:
            parts.append(f"{self.get_caption_text('score')}: {self.score}")

        if self.show_lives_in_caption:
            parts.append(f"{self.get_caption_text('lives')}: {self.lives}")

        if self.show_health_in_caption:
            parts.append(f"{self.get_caption_text('health')}: {int(self.health)}")

        caption = " | ".join(parts) if parts else "Game"
        pygame.display.set_caption(caption)

    def render(self):
        """Render the game"""
        if not self.screen or not self.current_room:
            return

        # Update window caption with score/lives/health
        self.update_caption()

        # Render current room
        self.current_room.render(self.screen)

        # Render Thymio robots (on top of regular sprites)
        for instance in self.current_room.instances:
            if getattr(instance, 'is_thymio', False) and hasattr(instance, 'thymio_simulator'):
                render_data = instance.thymio_simulator.get_render_data()
                self.thymio_renderer.render(self.screen, render_data)

        # Update display
        pygame.display.flip()

    def trigger_no_more_lives_event(self, triggering_instance=None):
        """Trigger the no_more_lives event for all instances that have it defined"""
        if not self.current_room:
            return

        logger.debug("💀 Triggering no_more_lives event for all instances...")

        for instance in self.current_room.instances:
            if not instance.object_data:
                continue

            events = instance.object_data.get('events', {})
            if 'no_more_lives' in events:
                logger.debug(f"  📢 Executing no_more_lives for {instance.object_name}")
                instance.action_executor.execute_event(instance, 'no_more_lives', events)

    def trigger_no_more_health_event(self, triggering_instance=None):
        """Trigger the no_more_health event for all instances that have it defined

        Note: This only triggers custom no_more_health events. Any behavior like
        decrementing lives or resetting health must be explicitly programmed
        by the user in their no_more_health event actions.
        """
        if not self.current_room:
            return

        logger.debug("💔 Triggering no_more_health event for all instances...")

        for instance in self.current_room.instances:
            if not instance.object_data:
                continue

            events = instance.object_data.get('events', {})
            if 'no_more_health' in events:
                logger.debug(f"  📢 Executing no_more_health for {instance.object_name}")
                instance.action_executor.execute_event(instance, 'no_more_health', events)

    def show_debug_info(self):
        """Print debug information"""
        logger.debug("\n=== DEBUG INFO ===")
        logger.debug(f"Project: {self.project_data.get('name', 'Unknown')}")
        logger.debug(f"Current room: {self.current_room.name if self.current_room else 'None'}")

        if self.current_room:
            logger.debug(f"Room size: {self.current_room.width}x{self.current_room.height}")
            logger.debug(f"Background: {self.current_room.background_color}")
            logger.debug(f"Instances: {len(self.current_room.instances)}")

            for i, instance in enumerate(self.current_room.instances):
                sprite_info = "no sprite" if not instance.sprite else "sprite loaded"
                logger.debug(f"  {i+1}. {instance.object_name} at ({instance.x}, {instance.y}) - {sprite_info}")

        logger.debug("===================\n")

    def stop_game(self):
        """Stop the game"""
        logger.debug("Stopping game...")
        self.running = False

    def run(self):
        """Run the game - main entry point called by IDE"""
        if not self.project_data:
            logger.debug("❌ No project loaded. Cannot run game.")
            return False

        # Find starting room
        starting_room = self.find_starting_room()
        if not starting_room:
            logger.debug("❌ No rooms found in project")
            return False

        logger.info(f"🎮 Starting game with room: {starting_room}")
        self.current_room = self.rooms[starting_room]

        # Set window size based on room
        self.window_width = self.current_room.width
        self.window_height = self.current_room.height

        # Run the game loop
        return self.run_game_loop()

    def process_pending_messages(self):
        """Check all instances for pending messages and display them"""
        for instance in self.current_room.instances:
            if hasattr(instance, 'pending_messages') and instance.pending_messages:
                # Get the first pending message
                message = instance.pending_messages.pop(0)
                # Display the message dialog (this pauses the game)
                self.show_message_dialog(message)

    def show_message_dialog(self, message: str):
        """Display a message dialog box that pauses the game

        The dialog shows the message centered on screen with an OK button.
        User can click OK or press Enter/Space/Escape to dismiss.
        """
        logger.debug(f"📢 Showing message dialog: {message}")

        # Make sure we have a screen
        if not self.screen:
            logger.debug("⚠️ Cannot show message dialog - no screen")
            return

        # Clear any pending events to prevent accidental dismissal
        pygame.event.clear()

        # Store and pause all instance speeds during dialog
        # This prevents instances from moving while dialog is open, but restores speeds afterward
        saved_speeds = {}
        if self.current_room:
            for instance in self.current_room.instances:
                saved_speeds[id(instance)] = (instance.hspeed, instance.vspeed)
                instance.hspeed = 0
                instance.vspeed = 0

        # Render the current game state first (so dialog appears over the game)
        if self.current_room:
            self.current_room.render(self.screen)
            pygame.display.flip()

        # Create a semi-transparent overlay
        overlay = pygame.Surface((self.window_width, self.window_height))
        overlay.fill((0, 0, 0))
        overlay.set_alpha(128)

        # Dialog box dimensions
        dialog_width = min(400, self.window_width - 40)
        dialog_height = 150
        dialog_x = (self.window_width - dialog_width) // 2
        dialog_y = (self.window_height - dialog_height) // 2

        # Button dimensions
        button_width = 80
        button_height = 30
        button_x = dialog_x + (dialog_width - button_width) // 2
        button_y = dialog_y + dialog_height - button_height - 15

        # Get font
        try:
            font = pygame.font.Font(None, 24)
            title_font = pygame.font.Font(None, 28)
        except Exception:
            font = pygame.font.SysFont('arial', 18)
            title_font = pygame.font.SysFont('arial', 22)

        # Dialog loop - waits for user to dismiss
        waiting = True
        while waiting:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.stop_game()
                    waiting = False
                elif event.type == pygame.KEYDOWN:
                    if event.key in (pygame.K_RETURN, pygame.K_SPACE, pygame.K_ESCAPE):
                        waiting = False
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    # Check if OK button was clicked
                    mx, my = event.pos
                    if (button_x <= mx <= button_x + button_width and
                        button_y <= my <= button_y + button_height):
                        waiting = False

            # Draw overlay
            self.screen.blit(overlay, (0, 0))

            # Draw dialog box
            pygame.draw.rect(self.screen, (240, 240, 240),
                           (dialog_x, dialog_y, dialog_width, dialog_height))
            pygame.draw.rect(self.screen, (100, 100, 100),
                           (dialog_x, dialog_y, dialog_width, dialog_height), 2)

            # Draw title bar
            pygame.draw.rect(self.screen, (70, 130, 180),
                           (dialog_x, dialog_y, dialog_width, 30))
            title_text = title_font.render("Message", True, (255, 255, 255))
            self.screen.blit(title_text, (dialog_x + 10, dialog_y + 5))

            # Draw message text (wrap if too long)
            words = message.split()
            lines = []
            current_line = ""
            max_text_width = dialog_width - 30

            for word in words:
                test_line = current_line + (" " if current_line else "") + word
                if font.size(test_line)[0] <= max_text_width:
                    current_line = test_line
                else:
                    if current_line:
                        lines.append(current_line)
                    current_line = word

            if current_line:
                lines.append(current_line)

            # Render message lines
            y_offset = dialog_y + 45
            for line in lines[:4]:  # Max 4 lines
                text_surface = font.render(line, True, (0, 0, 0))
                self.screen.blit(text_surface, (dialog_x + 15, y_offset))
                y_offset += 22

            # Draw OK button
            mouse_pos = pygame.mouse.get_pos()
            button_hover = (button_x <= mouse_pos[0] <= button_x + button_width and
                          button_y <= mouse_pos[1] <= button_y + button_height)

            button_color = (100, 149, 237) if button_hover else (70, 130, 180)
            pygame.draw.rect(self.screen, button_color,
                           (button_x, button_y, button_width, button_height))
            pygame.draw.rect(self.screen, (50, 50, 50),
                           (button_x, button_y, button_width, button_height), 1)

            ok_text = font.render("OK", True, (255, 255, 255))
            ok_text_x = button_x + (button_width - ok_text.get_width()) // 2
            ok_text_y = button_y + (button_height - ok_text.get_height()) // 2
            self.screen.blit(ok_text, (ok_text_x, ok_text_y))

            pygame.display.flip()
            if self.clock:
                self.clock.tick(60)

        # Restore instance speeds after dialog is dismissed
        if self.current_room:
            for instance in self.current_room.instances:
                if id(instance) in saved_speeds:
                    instance.hspeed, instance.vspeed = saved_speeds[id(instance)]

    # ==================== HIGHSCORE SYSTEM ====================

    def load_highscores(self):
        """Load highscores from file"""
        if not self.highscore_file:
            return

        try:
            if self.highscore_file.exists():
                with open(self.highscore_file, 'r') as f:
                    data = json.load(f)
                    self.highscores = [(entry['name'], entry['score']) for entry in data]
                    logger.debug(f"📊 Loaded {len(self.highscores)} highscores from {self.highscore_file}")
        except Exception as e:
            logger.debug(f"⚠️ Could not load highscores: {e}")
            self.highscores = []

    def save_highscores(self):
        """Save highscores to file"""
        if not self.highscore_file:
            return

        try:
            # Ensure directory exists
            self.highscore_file.parent.mkdir(parents=True, exist_ok=True)

            data = [{'name': name, 'score': score} for name, score in self.highscores]
            with open(self.highscore_file, 'w') as f:
                json.dump(data, f, indent=2)
            logger.debug(f"💾 Saved {len(self.highscores)} highscores to {self.highscore_file}")
        except Exception as e:
            logger.debug(f"⚠️ Could not save highscores: {e}")

    def clear_highscores(self):
        """Clear all highscores"""
        self.highscores = []
        self.save_highscores()
        logger.debug("🧹 Highscore table cleared")

    def is_highscore(self, score: int) -> bool:
        """Check if a score qualifies for the highscore table"""
        if len(self.highscores) < self.highscore_max_entries:
            return True
        # Check if score is higher than the lowest entry
        if self.highscores:
            lowest_score = min(entry[1] for entry in self.highscores)
            return score > lowest_score
        return True

    def add_highscore(self, name: str, score: int):
        """Add a new highscore entry"""
        self.highscores.append((name, score))
        # Sort by score descending
        self.highscores.sort(key=lambda x: x[1], reverse=True)
        # Keep only top entries
        self.highscores = self.highscores[:self.highscore_max_entries]
        self.save_highscores()

    def show_highscore_dialog(self, background_color=(255, 255, 220),
                               new_color=(255, 0, 0), other_color=(0, 0, 0),
                               allow_name_entry: bool = True):
        """Display the highscore table dialog

        Args:
            background_color: Background color for the dialog (R, G, B) - ignored, uses modern dark theme
            new_color: Color for the new highscore entry (R, G, B)
            other_color: Color for other entries (R, G, B) - ignored, uses theme colors
            allow_name_entry: If True and current score qualifies, prompt for name
        """
        logger.debug(f"🏆 Showing highscore dialog (score: {self.score})")

        if not self.screen:
            logger.debug("⚠️ Cannot show highscore dialog - no screen")
            return

        # Clear any pending events
        pygame.event.clear()

        # Check if current score qualifies and we should prompt for name
        player_name = None
        player_rank = -1
        if allow_name_entry and self.is_highscore(self.score) and self.score > 0:
            player_name = self._show_name_entry_dialog()
            if player_name:
                self.add_highscore(player_name, self.score)
                # Find the rank of the new entry
                for i, (name, score) in enumerate(self.highscores):
                    if name == player_name and score == self.score:
                        player_rank = i
                        break

        # Render the current game state first
        if self.current_room:
            self.current_room.render(self.screen)
            pygame.display.flip()

        # Modern dark theme colors (matching IDE)
        bg_dark = (30, 30, 30)           # #1e1e1e - main background
        bg_header = (0, 122, 204)        # #007acc - blue header (like IDE status bar)
        bg_row_odd = (37, 37, 38)        # #252526 - alternating row
        bg_row_even = (45, 45, 48)       # #2d2d30 - alternating row
        bg_highlight = (9, 71, 113)      # #094771 - selected/highlight
        text_primary = (224, 224, 224)   # #e0e0e0 - main text
        text_secondary = (150, 150, 150) # #969696 - secondary text
        text_gold = (255, 215, 0)        # Gold for rank numbers
        text_new = (100, 200, 100)       # Green for new entry
        border_color = (62, 62, 66)      # #3e3e42 - borders
        button_normal = (0, 122, 204)    # #007acc - blue button
        button_hover = (28, 151, 234)    # #1c97ea - lighter blue

        # Create semi-transparent overlay
        overlay = pygame.Surface((self.window_width, self.window_height))
        overlay.fill((0, 0, 0))
        overlay.set_alpha(180)

        # Dialog dimensions
        dialog_width = min(420, self.window_width - 40)
        dialog_height = min(420, self.window_height - 40)
        dialog_x = (self.window_width - dialog_width) // 2
        dialog_y = (self.window_height - dialog_height) // 2

        # Button dimensions
        button_width = 100
        button_height = 32
        button_x = dialog_x + (dialog_width - button_width) // 2
        button_y = dialog_y + dialog_height - button_height - 16

        # Fonts - try to use a clean sans-serif font
        try:
            title_font = pygame.font.SysFont('segoeui', 24, bold=True)
            header_font = pygame.font.SysFont('segoeui', 16, bold=True)
            entry_font = pygame.font.SysFont('segoeui', 18)
            button_font = pygame.font.SysFont('segoeui', 16, bold=True)
        except Exception:
            try:
                title_font = pygame.font.SysFont('arial', 24, bold=True)
                header_font = pygame.font.SysFont('arial', 16, bold=True)
                entry_font = pygame.font.SysFont('arial', 18)
                button_font = pygame.font.SysFont('arial', 16, bold=True)
            except Exception:
                title_font = pygame.font.Font(None, 32)
                header_font = pygame.font.Font(None, 22)
                entry_font = pygame.font.Font(None, 24)
                button_font = pygame.font.Font(None, 22)

        # Dialog loop
        waiting = True
        while waiting:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.stop_game()
                    waiting = False
                elif event.type == pygame.KEYDOWN:
                    if event.key in (pygame.K_RETURN, pygame.K_SPACE, pygame.K_ESCAPE):
                        waiting = False
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    mx, my = event.pos
                    if (button_x <= mx <= button_x + button_width and
                        button_y <= my <= button_y + button_height):
                        waiting = False

            # Draw overlay
            self.screen.blit(overlay, (0, 0))

            # Draw dialog with rounded corners effect (draw multiple rects)
            # Main background
            pygame.draw.rect(self.screen, bg_dark,
                           (dialog_x, dialog_y, dialog_width, dialog_height))
            # Border
            pygame.draw.rect(self.screen, border_color,
                           (dialog_x, dialog_y, dialog_width, dialog_height), 2)

            # Draw header bar
            header_height = 45
            pygame.draw.rect(self.screen, bg_header,
                           (dialog_x + 2, dialog_y + 2, dialog_width - 4, header_height))

            # Title text (translated)
            title_str = get_runtime_translation("HIGH SCORES", self.language)
            title_text = title_font.render(title_str, True, (255, 255, 255))
            title_x = dialog_x + (dialog_width - title_text.get_width()) // 2
            self.screen.blit(title_text, (title_x, dialog_y + 12))

            # Column headers background
            header_y = dialog_y + header_height + 10
            pygame.draw.rect(self.screen, bg_row_odd,
                           (dialog_x + 10, header_y, dialog_width - 20, 28))

            # Column headers (translated)
            rank_str = get_runtime_translation("Rank", self.language)
            name_str = get_runtime_translation("Name", self.language)
            score_str = get_runtime_translation("Score", self.language)
            rank_text = header_font.render(rank_str, True, text_secondary)
            name_text = header_font.render(name_str.upper(), True, text_secondary)
            score_text = header_font.render(score_str.upper(), True, text_secondary)

            self.screen.blit(rank_text, (dialog_x + 25, header_y + 6))
            self.screen.blit(name_text, (dialog_x + 70, header_y + 6))
            self.screen.blit(score_text, (dialog_x + dialog_width - 100, header_y + 6))

            # Draw highscore entries
            entry_start_y = header_y + 35
            entry_height = 30

            if not self.highscores:
                # No scores yet (translated)
                no_scores_str = get_runtime_translation("No scores yet!", self.language)
                no_scores_text = entry_font.render(no_scores_str, True, text_secondary)
                no_scores_x = dialog_x + (dialog_width - no_scores_text.get_width()) // 2
                self.screen.blit(no_scores_text, (no_scores_x, entry_start_y + 60))
            else:
                for i, (name, score) in enumerate(self.highscores[:10]):
                    entry_y = entry_start_y + i * entry_height

                    # Alternating row background
                    if i == player_rank:
                        row_bg = bg_highlight
                    elif i % 2 == 0:
                        row_bg = bg_row_even
                    else:
                        row_bg = bg_row_odd

                    pygame.draw.rect(self.screen, row_bg,
                                   (dialog_x + 10, entry_y, dialog_width - 20, entry_height - 2))

                    # Text color
                    if i == player_rank:
                        text_color = text_new
                        rank_color = text_new
                    else:
                        text_color = text_primary
                        # Gold/silver/bronze for top 3
                        if i == 0:
                            rank_color = (255, 215, 0)   # Gold
                        elif i == 1:
                            rank_color = (192, 192, 192) # Silver
                        elif i == 2:
                            rank_color = (205, 127, 50)  # Bronze
                        else:
                            rank_color = text_secondary

                    # Rank number
                    rank_str = str(i + 1)
                    rank_surface = entry_font.render(rank_str, True, rank_color)
                    self.screen.blit(rank_surface, (dialog_x + 25, entry_y + 5))

                    # Name (truncate if too long)
                    display_name = name[:18] + ".." if len(name) > 18 else name
                    name_surface = entry_font.render(display_name, True, text_color)
                    self.screen.blit(name_surface, (dialog_x + 70, entry_y + 5))

                    # Score (right-aligned)
                    score_str = f"{score:,}"
                    score_surface = entry_font.render(score_str, True, text_color)
                    score_x = dialog_x + dialog_width - 30 - score_surface.get_width()
                    self.screen.blit(score_surface, (score_x, entry_y + 5))

            # Draw OK button
            mouse_pos = pygame.mouse.get_pos()
            button_hover_state = (button_x <= mouse_pos[0] <= button_x + button_width and
                          button_y <= mouse_pos[1] <= button_y + button_height)

            btn_color = button_hover if button_hover_state else button_normal
            pygame.draw.rect(self.screen, btn_color,
                           (button_x, button_y, button_width, button_height))

            ok_str = get_runtime_translation("OK", self.language)
            ok_text = button_font.render(ok_str, True, (255, 255, 255))
            ok_x = button_x + (button_width - ok_text.get_width()) // 2
            ok_y = button_y + (button_height - ok_text.get_height()) // 2
            self.screen.blit(ok_text, (ok_x, ok_y))

            pygame.display.flip()
            if self.clock:
                self.clock.tick(60)

    def _show_name_entry_dialog(self) -> str:
        """Show dialog to enter player name for highscore

        Returns:
            Player name or empty string if cancelled
        """
        logger.debug("📝 Showing name entry dialog")

        if not self.screen:
            return ""

        pygame.event.clear()

        # Render game state
        if self.current_room:
            self.current_room.render(self.screen)
            pygame.display.flip()

        # Modern dark theme colors (matching IDE)
        bg_dark = (30, 30, 30)           # #1e1e1e
        bg_header = (0, 122, 204)        # #007acc
        bg_input = (45, 45, 48)          # #2d2d30
        text_primary = (224, 224, 224)   # #e0e0e0
        text_score = (100, 200, 100)     # Green for score
        border_color = (62, 62, 66)      # #3e3e42
        input_border = (0, 122, 204)     # Blue border for focused input
        button_ok = (0, 122, 204)        # #007acc
        button_ok_hover = (28, 151, 234) # #1c97ea
        button_cancel = (90, 90, 90)     # Gray
        button_cancel_hover = (110, 110, 110)

        # Overlay
        overlay = pygame.Surface((self.window_width, self.window_height))
        overlay.fill((0, 0, 0))
        overlay.set_alpha(180)

        # Dialog dimensions
        dialog_width = min(380, self.window_width - 40)
        dialog_height = 200
        dialog_x = (self.window_width - dialog_width) // 2
        dialog_y = (self.window_height - dialog_height) // 2

        # Input field dimensions
        input_width = dialog_width - 50
        input_height = 36
        input_x = dialog_x + 25
        input_y = dialog_y + 110

        # Button dimensions
        button_width = 90
        button_height = 32
        ok_button_x = dialog_x + dialog_width // 2 - button_width - 8
        cancel_button_x = dialog_x + dialog_width // 2 + 8
        button_y = dialog_y + dialog_height - button_height - 16

        # Fonts
        try:
            title_font = pygame.font.SysFont('segoeui', 22, bold=True)
            label_font = pygame.font.SysFont('segoeui', 16)
            score_font = pygame.font.SysFont('segoeui', 20, bold=True)
            input_font = pygame.font.SysFont('segoeui', 18)
            button_font = pygame.font.SysFont('segoeui', 15, bold=True)
        except Exception:
            try:
                title_font = pygame.font.SysFont('arial', 22, bold=True)
                label_font = pygame.font.SysFont('arial', 16)
                score_font = pygame.font.SysFont('arial', 20, bold=True)
                input_font = pygame.font.SysFont('arial', 18)
                button_font = pygame.font.SysFont('arial', 15, bold=True)
            except Exception:
                title_font = pygame.font.Font(None, 28)
                label_font = pygame.font.Font(None, 22)
                score_font = pygame.font.Font(None, 26)
                input_font = pygame.font.Font(None, 24)
                button_font = pygame.font.Font(None, 20)

        player_name = ""
        max_name_length = 20
        cursor_visible = True
        cursor_timer = 0

        waiting = True
        while waiting:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.stop_game()
                    return ""
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_RETURN:
                        if player_name.strip():
                            return player_name.strip()
                    elif event.key == pygame.K_ESCAPE:
                        return ""
                    elif event.key == pygame.K_BACKSPACE:
                        player_name = player_name[:-1]
                    elif event.unicode and len(player_name) < max_name_length:
                        # Only allow printable characters
                        if event.unicode.isprintable():
                            player_name += event.unicode
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    mx, my = event.pos
                    # OK button
                    if (ok_button_x <= mx <= ok_button_x + button_width and
                        button_y <= my <= button_y + button_height):
                        if player_name.strip():
                            return player_name.strip()
                    # Cancel button
                    if (cancel_button_x <= mx <= cancel_button_x + button_width and
                        button_y <= my <= button_y + button_height):
                        return ""

            # Update cursor blink
            cursor_timer += 1
            if cursor_timer >= 30:
                cursor_visible = not cursor_visible
                cursor_timer = 0

            # Draw overlay
            self.screen.blit(overlay, (0, 0))

            # Draw dialog background
            pygame.draw.rect(self.screen, bg_dark,
                           (dialog_x, dialog_y, dialog_width, dialog_height))
            pygame.draw.rect(self.screen, border_color,
                           (dialog_x, dialog_y, dialog_width, dialog_height), 2)

            # Header bar
            header_height = 45
            pygame.draw.rect(self.screen, bg_header,
                           (dialog_x + 2, dialog_y + 2, dialog_width - 4, header_height))

            # Title (translated)
            title_str = get_runtime_translation("NEW HIGH SCORE!", self.language)
            title_text = title_font.render(title_str, True, (255, 255, 255))
            title_x = dialog_x + (dialog_width - title_text.get_width()) // 2
            self.screen.blit(title_text, (title_x, dialog_y + 12))

            # Score display (translated)
            score_label = get_runtime_translation("Score", self.language)
            score_text = score_font.render(f"{score_label}: {self.score:,}", True, text_score)
            score_x = dialog_x + (dialog_width - score_text.get_width()) // 2
            self.screen.blit(score_text, (score_x, dialog_y + 55))

            # Name label (translated)
            label_str = get_runtime_translation("Enter your name:", self.language)
            label_text = label_font.render(label_str, True, text_primary)
            self.screen.blit(label_text, (input_x, input_y - 22))

            # Input field
            pygame.draw.rect(self.screen, bg_input,
                           (input_x, input_y, input_width, input_height))
            pygame.draw.rect(self.screen, input_border,
                           (input_x, input_y, input_width, input_height), 2)

            # Input text with cursor
            display_text = player_name
            if cursor_visible:
                display_text += "|"
            name_surface = input_font.render(display_text, True, text_primary)
            self.screen.blit(name_surface, (input_x + 10, input_y + 8))

            # Buttons
            mouse_pos = pygame.mouse.get_pos()

            # OK button
            ok_hover = (ok_button_x <= mouse_pos[0] <= ok_button_x + button_width and
                       button_y <= mouse_pos[1] <= button_y + button_height)
            ok_color = button_ok_hover if ok_hover else button_ok
            pygame.draw.rect(self.screen, ok_color,
                           (ok_button_x, button_y, button_width, button_height))
            pygame.draw.rect(self.screen, (50, 50, 50),
                           (ok_button_x, button_y, button_width, button_height), 1)
            ok_str = get_runtime_translation("OK", self.language)
            ok_text = button_font.render(ok_str, True, (255, 255, 255))
            self.screen.blit(ok_text, (ok_button_x + (button_width - ok_text.get_width()) // 2,
                                       button_y + (button_height - ok_text.get_height()) // 2))

            # Cancel button (translated)
            cancel_hover = (cancel_button_x <= mouse_pos[0] <= cancel_button_x + button_width and
                           button_y <= mouse_pos[1] <= button_y + button_height)
            cancel_color = (180, 100, 100) if cancel_hover else (150, 80, 80)
            pygame.draw.rect(self.screen, cancel_color,
                           (cancel_button_x, button_y, button_width, button_height))
            pygame.draw.rect(self.screen, (50, 50, 50),
                           (cancel_button_x, button_y, button_width, button_height), 1)
            cancel_str = get_runtime_translation("Cancel", self.language)
            cancel_text = button_font.render(cancel_str, True, (255, 255, 255))
            self.screen.blit(cancel_text, (cancel_button_x + (button_width - cancel_text.get_width()) // 2,
                                           button_y + (button_height - cancel_text.get_height()) // 2))

            pygame.display.flip()
            if self.clock:
                self.clock.tick(60)

        return ""

    def update_thymio_robots(self):
        """Update all Thymio robot simulators and trigger events"""
        if not self.current_room:
            return

        # Get obstacles for collision detection (all solid instances that aren't Thymio)
        obstacles = []
        for instance in self.current_room.instances:
            if getattr(instance, 'solid', False) and not getattr(instance, 'is_thymio', False):
                if instance.sprite:
                    rect = pygame.Rect(
                        int(instance.x - instance.sprite.width / 2),
                        int(instance.y - instance.sprite.height / 2),
                        instance.sprite.width,
                        instance.sprite.height
                    )
                    obstacles.append(rect)

        # Update each Thymio robot
        for instance in self.current_room.instances:
            if not getattr(instance, 'is_thymio', False) or not hasattr(instance, 'thymio_simulator'):
                continue

            # Update simulator (returns dict of events that occurred)
            dt = 1/60  # 60 FPS
            thymio_events = instance.thymio_simulator.update(dt, obstacles, self.screen)

            # Sync instance position with simulator
            instance.x = instance.thymio_simulator.x
            instance.y = instance.thymio_simulator.y

            # Trigger Thymio events if they occurred
            if not instance.object_data or "events" not in instance.object_data:
                continue

            events = instance.object_data["events"]

            if thymio_events.get('proximity_update'):
                if 'thymio_proximity_update' in events:
                    instance.action_executor.execute_event(instance, 'thymio_proximity_update', events)

            if thymio_events.get('ground_update'):
                if 'thymio_ground_update' in events:
                    instance.action_executor.execute_event(instance, 'thymio_ground_update', events)

            if thymio_events.get('timer_0'):
                if 'thymio_timer_0' in events:
                    instance.action_executor.execute_event(instance, 'thymio_timer_0', events)

            if thymio_events.get('timer_1'):
                if 'thymio_timer_1' in events:
                    instance.action_executor.execute_event(instance, 'thymio_timer_1', events)

            if thymio_events.get('sound_finished'):
                if 'thymio_sound_finished' in events:
                    instance.action_executor.execute_event(instance, 'thymio_sound_finished', events)

    def cleanup(self):
        """Clean up pygame resources"""
        try:
            if pygame.get_init():
                pygame.quit()
            logger.debug("Game cleanup complete")
        except Exception as e:
            logger.error(f"Error during cleanup: {e}")

# Test function
def test_runner():
    """Test the enhanced game runner"""
    runner = GameRunner()

    # Test with a project path - replace with actual path
    test_project = "/path/to/your/project"

    if Path(test_project).exists():
        runner.test_game(test_project)
    else:
        logger.error(f"Test project not found: {test_project}")
        logger.debug("Please update the test_project path")

if __name__ == "__main__":
    test_runner()
