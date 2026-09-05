#!/usr/bin/env python3
"""GameSprite: image loading, animation-frame extraction, and collision
mask/bbox computation for the desktop runtime.

Extracted verbatim from ``runtime/game_runner.py`` (``docs/POST_1_0_REFACTOR.md``
File 3 -- the first, self-contained cluster the plan calls out as "easy").
GameSprite has no dependency on GameInstance/GameRoom/GameRunner or on
anything else in game_runner.py; it is instantiated in exactly one place
(``GameRunner``'s sprite-loading code) and otherwise only ever imported by
name.

``game_runner.py`` re-exports ``GameSprite`` (``from runtime.sprite import
GameSprite``) rather than requiring every caller to update its import path
-- unlike the ``core/ide/`` mixin extractions (which deliberately used no
compatibility shim, since those are internal inheritance-mixin pieces of
one class), this is an ordinary module-level class relocation with real
external call sites: over a dozen tests do
``from runtime.game_runner import GameSprite`` directly, and keeping that
path live via a plain re-export is the standard, lowest-churn way to move
a class to its own module in Python. No test changes were needed for this
reason -- confirmed by running the full suite unchanged.
"""

import pygame
from pathlib import Path
from PIL import Image

from core.logger import get_logger
logger = get_logger(__name__)


class GameSprite:
    """Represents a loaded sprite with animation support"""

    def __init__(self, image_path: str, sprite_data: dict = None):
        self.path = image_path
        self.sprite_data = sprite_data or {}
        self.surface = None  # Full sprite sheet surface
        self.frames = []  # List of individual frame surfaces
        self.masks = []  # Per-frame pygame.Mask, populated only when precise=True
        self.frame_count = 1
        self.frame_width = 32
        self.frame_height = 32
        self.width = 32  # Actual display width (frame width)
        self.height = 32  # Actual display height (frame height)
        self.origin_x = 0
        self.origin_y = 0
        self.speed = 10.0  # Animation FPS
        self.animation_type = "single"  # single, strip_h, strip_v, grid
        # Opt-in pixel-perfect collision. Static-only: rotation/scale fall back to AABB.
        self.precise = bool(self.sprite_data.get('precise', False))
        # Collision bbox in sprite-local pixel coords (matches GameMaker's
        # bbox_left/right/top/bottom). Defaults to the smallest rect containing
        # all opaque pixels of frame 0 — that way a 32x32 sprite of a 24-wide
        # character with transparent edges won't trigger collision while two
        # cells apart on the grid. JSON overrides win; if the auto-derive can't
        # produce a sensible answer the box stays at the full frame.
        # Populated by _compute_collision_bbox after load_image runs.
        self.bbox_left = 0
        self.bbox_top = 0
        self.bbox_right = 32   # provisional; refreshed below
        self.bbox_bottom = 32
        self.load_image()
        # Apply origin from sprite data (after load_image sets dimensions)
        self.origin_x = self.sprite_data.get('origin_x', 0)
        self.origin_y = self.sprite_data.get('origin_y', 0)
        if self.precise:
            self._build_masks()
        self._compute_collision_bbox()

    def _build_masks(self):
        """Build per-frame pygame.Mask for pixel-perfect collision."""
        self.masks = [pygame.mask.from_surface(f) for f in self.frames]

    def _compute_collision_bbox(self) -> None:
        """Populate bbox_left/top/right/bottom in sprite-local pixel coords.

        Three sources, in priority order:
        1. Explicit override in sprite_data (`bbox_left` etc). All four must be
           present — if any are missing we ignore the override and fall through.
        2. Automatic — the union of opaque pixels in frame 0 (GameMaker's
           default "Automatic" bbox mode). Uses a fresh `pygame.mask.from_surface`
           so the computation works even when `precise` is off (the runtime's
           per-frame mask cache only exists for precise=True sprites).
        3. Fallback — full frame (0, 0, width, height). Behaviour-preserving
           for old sprites that don't load cleanly through mask generation.
        """
        d = self.sprite_data
        if all(k in d for k in ('bbox_left', 'bbox_top', 'bbox_right', 'bbox_bottom')):
            self.bbox_left = int(d['bbox_left'])
            self.bbox_top = int(d['bbox_top'])
            self.bbox_right = int(d['bbox_right'])
            self.bbox_bottom = int(d['bbox_bottom'])
            return

        if self.frames:
            try:
                mask = pygame.mask.from_surface(self.frames[0])
                rects = mask.get_bounding_rects()
                if rects:
                    union = rects[0]
                    for r in rects[1:]:
                        union = union.union(r)
                    self.bbox_left = union.left
                    self.bbox_top = union.top
                    self.bbox_right = union.right  # pygame rect.right is exclusive — matches our half-open AABB convention
                    self.bbox_bottom = union.bottom
                    return
            except Exception:
                pass  # fall through to full-frame fallback

        # Fallback: full frame
        self.bbox_left = 0
        self.bbox_top = 0
        self.bbox_right = self.width
        self.bbox_bottom = self.height

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

                # Pre-compute tolerance bounds for transparent color matching
                if transparent_color:
                    tr, tg, tb = transparent_color
                    lo_r, hi_r = tr - 5, tr + 5
                    lo_g, hi_g = tg - 5, tg + 5
                    lo_b, hi_b = tb - 5, tb + 5

                # Extract all frames from the animated GIF
                self.frames = []
                for frame_idx in range(n_frames):
                    pil_image.seek(frame_idx)
                    # Convert to RGBA for transparency support
                    frame_rgba = pil_image.convert('RGBA')

                    # Make the background color transparent using bulk byte operations
                    # This is ~100x faster than iterating pixel-by-pixel in Python
                    if transparent_color:
                        raw = bytearray(frame_rgba.tobytes())
                        for i in range(0, len(raw), 4):
                            if (lo_r <= raw[i] <= hi_r and
                                lo_g <= raw[i + 1] <= hi_g and
                                lo_b <= raw[i + 2] <= hi_b):
                                raw[i + 3] = 0  # Set alpha to 0
                        frame_rgba = Image.frombytes('RGBA', frame_rgba.size, bytes(raw))

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

    def get_mask(self, image_index: float):
        """Get the per-frame pygame.Mask, or None if precise collision is disabled."""
        if not self.masks:
            return None
        frame_idx = int(image_index) % len(self.masks)
        return self.masks[frame_idx]

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
