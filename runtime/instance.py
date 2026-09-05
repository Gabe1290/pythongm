#!/usr/bin/env python3
"""GameInstance: per-instance runtime state (position, speed, alarms,
particle/timeline state) plus the entire draw-queue rendering pipeline
(``run_draw_event``/``_draw_text``/``_draw_sprite``/etc.) each instance's
Draw event actions build up during a frame.

Extracted verbatim from ``runtime/game_runner.py`` (``docs/POST_1_0_REFACTOR.md``
File 3, cluster 3 -- flagged "medium risk" in the plan, but the actual
dependency audit (AST-scanned before touching anything, not assumed) found
GameInstance genuinely self-contained: no reference to ``GameRoom`` or any
of ``game_runner.py``'s room/mouse/inheritance helpers at all -- only
``ActionExecutor``, ``GameSprite`` (already its own module), and
stdlib/pygame. The plan's own risk callout about ``_process_held_keys``/
``update()``'s ``is_grid_moving`` invariant turned out to belong to a
DIFFERENT, later cluster: both of those are ``GameRunner`` methods (input
handling), not ``GameInstance`` methods -- verified by locating their real
definitions before assuming the callout applied here.

This extraction actually *removes* a fragility rather than adding one:
``runtime/room.py`` (the previous cluster) imported ``GameInstance`` from
``game_runner.py`` at a load-order-sensitive position, since GameInstance
hadn't moved out yet. Now that it lives here, ``room.py`` imports it
directly from this module instead -- a plain one-way dependency
(``room.py`` → ``instance.py``, no cycle back) with no ordering
constraint. ``game_runner.py``'s own "GameRoom must stay at this exact
position" comment is updated accordingly: the constraint that remains is
only about ``resolve_parent_inheritance`` (which still lives in
``game_runner.py``, used by both ``GameRoom`` and ``GameRunner``), not
about ``GameInstance`` any more.

``game_runner.py`` re-exports ``GameInstance`` (same precedent as
``GameSprite``/``GameRoom``) so the many existing
``from runtime.game_runner import GameInstance`` call sites (tests
included -- the multiplayer extension's ``_spawn_ghost`` also imports it
this way) keep working unchanged.
"""

import math
import pygame
from typing import Any, Dict, Tuple

from runtime.action_executor import ActionExecutor
from runtime.sprite import GameSprite

from core.logger import get_logger
logger = get_logger(__name__)


class GameInstance:
    """Represents an object instance in the game world"""

    def __init__(self, object_name: str, x: float, y: float, instance_data: dict, action_executor=None):
        self.object_name = object_name
        self._original_object_name = object_name  # Tracks type before change_instance
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
        self.is_thymio = False  # Default false, set true for Thymio robot instances
        self.thymio_simulator = None  # Thymio simulator (set for Thymio instances)

        # Cached dimensions (updated when sprite is set)
        self._cached_width = 32
        self._cached_height = 32

        # Scaled surface cache: (frame_idx, scale_x, scale_y) -> pygame.Surface
        self._scaled_cache: Dict[Tuple[int, float, float], Any] = {}
        self._last_scale = (1.0, 1.0)  # Track scale changes to invalidate cache

        # Font cache for draw_text rendering, keyed by
        # (family, size, bold, italic) — see _get_cached_font.
        self._font_cache: Dict[Tuple[Any, int, bool, bool], Any] = {}

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

        # Facing angle (GM convention: 0=right, 90=up, 180=left, 270=down),
        # set by set_facing_angle. Unlike the read-only `direction` property
        # below (derived from hspeed/vspeed, so it's 0 when stationary),
        # this is real persistent state — needed for a raycast camera, which
        # must remember which way an instance is looking even while standing
        # still (e.g. turning on the spot).
        self.facing_angle = 0.0

        # Track if movement keys are currently pressed
        self.keys_pressed = set()  # Set of currently pressed keys

        # Delayed actions queued by `delay_action`. Eagerly initialised so the
        # per-frame loop in run_game_loop can do a direct truthiness check
        # instead of hasattr() for every instance every frame.
        self._delayed_actions = []

        # Sounds queued from execute_code via self._sound_queue.append('snd_x').
        # Drained (played + cleared) by ActionExecutor.execute_event after
        # every event, not just draw — this is the cross-platform sound
        # primitive mirrored by the Kivy/Web exporters, since execute_code has
        # no live `game` object to call game.sounds[...].play() on there.
        self._sound_queue = []

        # Alarms - 12 alarms (0-11), -1 means disabled
        self.alarm = [-1] * 12

        # Room/game control flags (set by actions, checked in update loop)
        self.restart_room_flag = False
        self.next_room_flag = False
        self.previous_room_flag = False
        self.restart_game_flag = False
        self.goto_room_target = None  # Target room name for goto_room action
        self._pending_load_instances = None  # Instances to restore after a load_game room switch

        # Movement intent (set before collision check)
        self.intended_x = float(x)
        self.intended_y = float(y)
        self._has_intended_move = False  # Flag for pending grid-based movement

        # Collision tracking
        self._active_collisions = set()
        self._collision_cooldowns = {}

        # Message queue for show_message actions
        self.pending_messages = []

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

    @property
    def direction(self):
        """GameMaker-style direction (degrees, 0°=right, 90°=up) derived
        from current hspeed/vspeed. Read-only because it's a view over
        the speed components — to change it, write hspeed/vspeed (or
        use set_direction_speed).

        Returns 0 when the instance is stationary, matching GameMaker's
        default. This makes bare `direction` references in action
        expressions like `set_direction_speed("direction+90", …)`
        evaluate correctly — without this property, the bare token
        couldn't resolve and the action silently defaulted to angle 0,
        so e.g. maze_3's monster_all always headed right on every wall
        collision instead of probing perpendicular directions.

        Note: `self.direction` in event expressions has its own special
        path in ActionExecutor._parse_value that prefers the captured
        pre-collision speed during collision events. This property is
        the post-collision (current) view that bare-name references
        use.
        """
        if self.hspeed == 0 and self.vspeed == 0:
            return 0.0
        # vspeed negated because screen y grows downward
        return math.degrees(math.atan2(-self.vspeed, self.hspeed)) % 360.0

    @property
    def image_number(self):
        """GameMaker-style read-only count of subimages (frames) in this
        instance's sprite, or 0 when no sprite is assigned. Mirrors GM's
        built-in `image_number` so bare references resolve in action
        expressions — e.g. `random(image_number)` (pick a random frame).
        Without this property the token couldn't bind, the surrounding
        expression raised NameError, and _evaluate_expression silently
        defaulted to 0.
        """
        return self.sprite.frame_count if self.sprite else 0

    def step(self):
        """Execute step event every frame"""
        # Advance animation
        animation_wrapped = False
        if self.sprite and self.sprite.frame_count > 1 and self.image_speed != 0:
            # GameMaker semantics: image_speed is subimages advanced per
            # game step (room_speed handles framerate). The earlier formula
            # multiplied by sprite.speed/30, but sprite.speed is hard-coded
            # to 10 by the GMK importer, so every animation effectively ran
            # at 1/3 the requested rate — pressing right/left set
            # image_speed=0.5 yielded 0.167 frames/step, which the user
            # perceived as a freeze (one subimage swap every 6 game frames).
            frame_advance = self.image_speed
            self.image_index += frame_advance

            # Wrap around when animation completes
            if self.image_index >= self.sprite.frame_count:
                self.image_index = self.image_index % self.sprite.frame_count
                animation_wrapped = True
            elif self.image_index < 0:
                self.image_index = self.sprite.frame_count + (self.image_index % self.sprite.frame_count)
                animation_wrapped = True

        # Fire animation_end after we know we wrapped. Done outside the wrap
        # branch so destroy_instance/change_instance inside the handler can't
        # leave image_index in a half-updated state.
        if animation_wrapped and self.object_data:
            events = self.object_data.get("events", {})
            if "animation_end" in events:
                self.action_executor.execute_event(self, "animation_end", events)

        if self.object_data and "events" in self.object_data:
            # Skip step event if flagged (blocker just gained speed from a push,
            # needs one frame to move off its grid position before if_on_grid stops it)
            if getattr(self, '_skip_next_step', False):
                self._skip_next_step = False
                return

            # "nokey" keyboard event — BEFORE the step event, matching GM's
            # event order (keyboard events run before step). maze_4's conveyor
            # markers set motion from the STEP event while the person's <no
            # key> event stops motion: with nokey after step, the stop stomped
            # the conveyor every frame and the person froze on the marker; in
            # GM the step runs last and the conveyor wins.
            events = self.object_data["events"]
            if "keyboard" in events and "nokey" in events["keyboard"]:
                # Check if no keys are currently pressed
                keys_pressed = getattr(self, 'keys_pressed', set())
                if len(keys_pressed) == 0:
                    # No keys pressed - execute nokey event actions
                    # Use execute_action_list for proper conditional flow (if_on_grid, etc.)
                    nokey_event = events["keyboard"]["nokey"]
                    if isinstance(nokey_event, dict) and "actions" in nokey_event:
                        self.action_executor.execute_action_list(self, nokey_event["actions"])

            # Execute regular step event
            # NOTE: Alarms are now processed in main game loop (before step)
            # to match GameMaker 7.0 event execution order
            self.action_executor.execute_event(self, "step", self.object_data["events"])

    def update_particle_system(self):
        """Per-frame particle system update: spawn from streaming emitters,
        then age/move/cull every live particle.

        Write side lives in action_executor.py's create_particle_system/
        create_particle_type/create_emitter/burst_particles/stream_particles
        actions (Tier 5.1, docs/DEFERRED_GAPS_2026_PLAN.md) — those only
        ever populated `_particle_system`; nothing previously read it.
        """
        ps = getattr(self, '_particle_system', None)
        if not ps:
            return

        # Spawn from any emitter with active streaming (stream_particles
        # action sets stream_type/stream_count on the emitter itself).
        for emitter in ps['emitters'].values():
            stream_type = emitter.get('stream_type')
            stream_count = emitter.get('stream_count', 0)
            if stream_type is None or stream_count <= 0:
                continue
            ptype = ps['particle_types'].get(stream_type)
            if ptype is None:
                continue
            self.action_executor._spawn_particles(self, emitter, ptype, stream_count)

        # Age, move and cull particles. Movement mirrors set_direction_speed's
        # convention (0 deg = right, 90 deg = up, y grows downward).
        surviving = []
        for particle in ps['particles']:
            particle['life'] -= 1
            if particle['life'] <= 0:
                continue
            angle_rad = math.radians(particle['direction'])
            particle['x'] += math.cos(angle_rad) * particle['speed']
            particle['y'] -= math.sin(angle_rad) * particle['speed']
            particle['size'] = max(0.0, particle['size'] + particle['size_increase'])
            surviving.append(particle)
        ps['particles'] = surviving

    def update_timeline(self):
        """Advance timeline_position by timeline_speed while timeline_running
        is set (set_timeline/start_timeline/pause_timeline/set_timeline_speed/
        set_timeline_position in action_executor.py). There is no separate
        Timeline resource/moments table in this engine (unlike GameMaker) --
        an author reacts to specific positions the same way they'd react to
        any other counter: a test_variable/conditional check on
        timeline_position in the object's own step event. This mirrors how
        alarms are authored as ordinary object events, just without a
        dedicated per-position event bucket.
        """
        if getattr(self, 'timeline_running', False):
            speed = getattr(self, 'timeline_speed', 1.0)
            self.timeline_position = getattr(self, 'timeline_position', 0) + speed

    def render_particles(self, screen: pygame.Surface, view_offset=(0, 0)):
        """Draw this instance's live particles (world-space, same view_offset
        as the instance's own sprite). Sprite-typed particles blit a scaled
        copy of the named sprite's first frame; colorless/no-sprite particles
        draw as a filled, alpha-blended circle. Called from render() BEFORE
        the visibility check and the instance's own sprite, so an invisible
        "particle controller" instance (a common pattern -- one instance that
        only holds emitters) still draws its particles. Known simplification:
        this instance's particles are not independently depth-sorted against
        every OTHER instance using the particle system's own `depth` field --
        there is no room-global particle layer in this engine, only
        per-instance ones.
        """
        ps = getattr(self, '_particle_system', None)
        if not ps or not ps['particles']:
            return

        runner = getattr(getattr(self, 'action_executor', None), 'game_runner', None)
        sprites = getattr(runner, 'sprites', None) or {}

        for particle in ps['particles']:
            x = int(particle['x'] + view_offset[0])
            y = int(particle['y'] + view_offset[1])
            alpha = max(0, min(255, int(particle.get('alpha', 1.0) * 255)))
            sprite_name = particle.get('sprite')
            sprite = sprites.get(sprite_name) if sprite_name else None
            frame = None
            if sprite is not None:
                frame = sprite.frames[0] if sprite.frames else sprite.surface
            if frame is not None:
                scale = max(0.01, particle.get('size', 1.0))
                w = max(1, int(frame.get_width() * scale))
                h = max(1, int(frame.get_height() * scale))
                scaled = pygame.transform.scale(frame, (w, h))
                if alpha < 255:
                    scaled = scaled.copy()
                    scaled.set_alpha(alpha)
                screen.blit(scaled, (x - w // 2, y - h // 2))
            else:
                radius = max(1, int(particle.get('size', 1.0)))
                color = particle.get('color', (255, 255, 255))
                if alpha < 255:
                    temp = pygame.Surface((radius * 2, radius * 2), pygame.SRCALPHA)
                    pygame.draw.circle(temp, (*color, alpha), (radius, radius), radius)
                    screen.blit(temp, (x - radius, y - radius))
                else:
                    pygame.draw.circle(screen, color, (x, y), radius)

    def set_sprite(self, sprite: GameSprite):
        """Set the sprite for this instance"""
        self.sprite = sprite
        # Clear scaled surface cache when sprite changes
        self._scaled_cache.clear()
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

    def render(self, screen: pygame.Surface, view_offset=(0, 0)):
        """Render this instance.

        view_offset: (dx, dy) added to the final blit position so the instance
        appears at the correct screen pixel under the active view. Defaults to
        (0, 0), which preserves identical behavior when views are disabled.
        """
        # Particles draw even when the owning instance is invisible -- an
        # invisible "particle controller" instance holding only emitters is
        # a common pattern, and GM particle systems are independent of the
        # instance's own visibility.
        self.render_particles(screen, view_offset)

        if not self.visible:
            return

        # Render sprite if present
        if self.sprite:
            # Calculate render position (offset by sprite origin + view offset)
            render_x = int(self.x - self.sprite.origin_x + view_offset[0])
            render_y = int(self.y - self.sprite.origin_y + view_offset[1])

            # Get current animation frame
            frame_idx = int(self.image_index)
            current_frame = self.sprite.get_frame(self.image_index)

            # Handle scaling with caching
            if self.scale_x != 1.0 or self.scale_y != 1.0:
                # Invalidate cache if scale changed
                current_scale = (self.scale_x, self.scale_y)
                if current_scale != self._last_scale:
                    self._scaled_cache.clear()
                    self._last_scale = current_scale

                # Check cache first
                cache_key = (frame_idx, self.scale_x, self.scale_y)
                scaled_surface = self._scaled_cache.get(cache_key)
                if scaled_surface is None:
                    scaled_width = int(self.sprite.width * self.scale_x)
                    scaled_height = int(self.sprite.height * self.scale_y)
                    scaled_surface = pygame.transform.scale(current_frame, (scaled_width, scaled_height))
                    self._scaled_cache[cache_key] = scaled_surface
                screen.blit(scaled_surface, (render_x, render_y))
            else:
                screen.blit(current_frame, (render_x, render_y))

        # Execute draw event for this instance
        self.run_draw_event(screen)

    def run_draw_event(self, screen: pygame.Surface):
        """Run this instance's draw event and flush its draw queue.

        Split out of render() so the raycast HUD pass can composite draw
        actions (draw_score / draw_lives / draw_text / draw_health_bar) over
        the finished first-person frame without also blitting sprites — see
        GameRoom._render_draw_events and docs/RAYCAST_HUD_PLAN.md.

        Draw commands are emitted in screen space; callers that need a view
        offset apply it inside _process_draw_queue as before.
        """
        if self.object_data and "events" in self.object_data:
            events = self.object_data["events"]
            if "draw" in events:
                # Clear draw queue before executing draw event
                self._draw_queue = []
                self.action_executor.execute_event(self, "draw", events)

                # Process draw queue
                self._process_draw_queue(screen)

    # Draw command dispatch table - maps command types to handler methods
    _DRAW_HANDLERS = {
        'text': '_draw_text',
        'lives': '_draw_lives',
        'health_bar': '_draw_health_bar',
        'rectangle': '_draw_rectangle',
        'circle': '_draw_circle',
        'ellipse': '_draw_ellipse',
        'line': '_draw_line',
        'sprite': '_draw_sprite',
        'background': '_draw_background',
        'scaled_text': '_draw_scaled_text',
        'arrow': '_draw_arrow',
    }

    def _process_draw_queue(self, screen: pygame.Surface):
        """Process queued draw commands from draw event actions.

        Uses a dispatch table to map command types to handler methods,
        reducing nesting depth and improving maintainability.
        """
        if not hasattr(self, '_draw_queue'):
            return

        for cmd in self._draw_queue:
            cmd_type = cmd.get('type')
            handler_name = self._DRAW_HANDLERS.get(cmd_type)
            if handler_name:
                handler = getattr(self, handler_name)
                handler(screen, cmd)

        # Clear the queue after processing
        self._draw_queue = []

    def _get_cached_font(self, size: int, family: str = None,
                          bold: bool = False, italic: bool = False) -> pygame.font.Font:
        """Get a cached font, creating it if needed.

        Args:
            size: Font size in points
            family: System font family name (None -> pygame's built-in
                default font, the pre-existing behavior for every draw_text
                call that never went through set_draw_font)
            bold, italic: Style flags, honored for both the family and
                default-font paths

        Returns:
            Cached pygame Font object
        """
        key = (family, size, bold, italic)
        if key not in self._font_cache:
            try:
                if family:
                    self._font_cache[key] = pygame.font.SysFont(family, size, bold=bold, italic=italic)
                else:
                    font = pygame.font.Font(None, size)
                    if bold:
                        font.set_bold(True)
                    if italic:
                        font.set_italic(True)
                    self._font_cache[key] = font
            except Exception:
                self._font_cache[key] = pygame.font.SysFont('arial', max(1, size - 6))
        return self._font_cache[key]

    def _resolve_draw_font(self) -> pygame.font.Font:
        """Resolve self.draw_font (a font *asset name*, set by
        set_draw_font — runtime/action_executor.py execute_set_draw_font_action)
        into a real Font honoring that asset's font_name/size/bold/italic.

        set_draw_font stored the asset name on the instance but nothing
        ever read it back; draw_text/draw_scaled_text always rendered at
        a hardcoded 24pt default font regardless. Falls back to that same
        default when no draw_font is set, or the named asset can't be
        found — every game that never calls set_draw_font (the vast
        majority, today) sees zero behavior change.
        """
        font_name = getattr(self, 'draw_font', None)
        if not font_name:
            return self._get_cached_font(24)
        runner = getattr(getattr(self, 'action_executor', None), 'game_runner', None)
        fonts = {}
        if runner and runner.project_data:
            fonts = runner.project_data.get('assets', {}).get('fonts', {}) or {}
        font_asset = fonts.get(font_name)
        if not isinstance(font_asset, dict):
            logger.warning(f"⚠️ set_draw_font: font asset '{font_name}' not found; using default")
            return self._get_cached_font(24)
        family = font_asset.get('font_name') or None
        try:
            size = int(font_asset.get('size', 12) or 12)
        except (TypeError, ValueError):
            size = 12
        bold = bool(font_asset.get('bold', False))
        italic = bool(font_asset.get('italic', False))
        return self._get_cached_font(size, family, bold, italic)

    def _align_text_pos(self, x, y, width, height, halign='left', valign='top'):
        """Shift (x, y) per halign/valign (captured on the draw-queue command
        at queue time by execute_draw_text_action/execute_draw_scaled_text_action
        — NOT read from self here, since by render time the whole draw
        event has already run and self.draw_halign only reflects whatever
        set_draw_font call happened to run LAST in that event) so x/y
        become the alignment anchor GameMaker's draw_set_halign/valign
        promise, not always the top-left corner."""
        if halign == 'center':
            x = x - width / 2
        elif halign == 'right':
            x = x - width
        if valign == 'middle':
            y = y - height / 2
        elif valign == 'bottom':
            y = y - height
        return x, y

    def _draw_text(self, screen: pygame.Surface, cmd: dict):
        """Draw text on screen"""
        font = self._resolve_draw_font()

        text = cmd.get('text', '')
        x = cmd.get('x', 0)
        y = cmd.get('y', 0)
        color = self._parse_color(cmd.get('color', '#FFFFFF'))

        text_surface = font.render(str(text), True, color)
        x, y = self._align_text_pos(x, y, text_surface.get_width(), text_surface.get_height(),
                                     cmd.get('halign', 'left'), cmd.get('valign', 'top'))
        screen.blit(text_surface, (x, y))

    def _draw_scaled_text(self, screen: pygame.Surface, cmd: dict):
        """Draw scaled text on screen"""
        font = self._resolve_draw_font()

        text = cmd.get('text', '')
        x = cmd.get('x', 0)
        y = cmd.get('y', 0)
        xscale = cmd.get('xscale', 1.0)
        yscale = cmd.get('yscale', 1.0)
        color = self._parse_color(cmd.get('color', '#FFFFFF'))

        # Render text at normal size first
        text_surface = font.render(str(text), True, color)

        # Apply scaling if not 1.0
        if xscale != 1.0 or yscale != 1.0:
            original_width = text_surface.get_width()
            original_height = text_surface.get_height()
            new_width = int(original_width * xscale)
            new_height = int(original_height * yscale)

            # Ensure minimum size of 1 pixel
            new_width = max(1, new_width)
            new_height = max(1, new_height)

            text_surface = pygame.transform.scale(text_surface, (new_width, new_height))

        # Align against the FINAL (post-scale) size — alignment is a
        # visual anchor, so it should track what's actually on screen.
        x, y = self._align_text_pos(x, y, text_surface.get_width(), text_surface.get_height(),
                                     cmd.get('halign', 'left'), cmd.get('valign', 'top'))
        screen.blit(text_surface, (int(x), int(y)))

    def _draw_lives(self, screen: pygame.Surface, cmd: dict):
        """Draw the life count as repeated sprite images.

        Matches the classic GameMaker "draw lives as image" action: one copy
        of the chosen sprite is blitted per remaining life, laid out
        left-to-right. When no sprite is given (or it can't be resolved) we
        fall back to a ``Lives: N`` text readout.
        """
        count = int(cmd.get('count', 0) or 0)
        x = int(cmd.get('x', 0))
        y = int(cmd.get('y', 0))
        sprite_name = cmd.get('sprite', '')

        # Resolve the life-icon surface (first frame for animated sprites).
        # The sprite registry lives on the GameRunner, reached via this
        # instance's action_executor back-reference (same pattern as
        # _draw_background) — GameInstance itself has no `sprites` dict.
        surface = None
        runner = getattr(getattr(self, 'action_executor', None), 'game_runner', None)
        sprites = getattr(runner, 'sprites', None) or {}
        if sprite_name and sprite_name in sprites:
            sprite = sprites[sprite_name]
            if getattr(sprite, 'frames', None):
                surface = sprite.frames[0]
            elif getattr(sprite, 'surface', None):
                surface = sprite.surface

        if surface is not None:
            # Optional uniform scale for the life icon.
            scale = cmd.get('scale', 1.0) or 1.0
            if scale != 1.0:
                w = max(1, int(surface.get_width() * scale))
                h = max(1, int(surface.get_height() * scale))
                surface = pygame.transform.scale(surface, (w, h))
            step = surface.get_width()
            for i in range(max(0, count)):
                screen.blit(surface, (x + i * step, y))
            return

        # No usable sprite — fall back to a numeric readout (also covers the
        # case where draw_lives is used without picking a sprite).
        if sprite_name:
            logger.warning(
                f"⚠️ draw_lives: sprite '{sprite_name}' not found; drawing count as text"
            )
        font = self._get_cached_font(24)
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

    def _draw_arrow(self, screen: pygame.Surface, cmd: dict):
        """Draw an arrow: the shaft plus two tip segments.

        execute_draw_arrow_action (runtime/action_executor.py) already
        computes tip1_x/tip1_y/tip2_x/tip2_y at queue time (the geometry
        depends on x1/y1/x2/y2/tip_size, which can be expressions — easier
        to resolve once there than to redo trig per draw call), so this is
        just three pygame.draw.line calls. 'arrow' was queued by
        execute_draw_arrow_action since the 2026-06-05 UI-metadata sweep
        but had no entry in _DRAW_HANDLERS until now — draw_arrow silently
        drew nothing.
        """
        x1 = cmd.get('x1', 0)
        y1 = cmd.get('y1', 0)
        x2 = cmd.get('x2', 100)
        y2 = cmd.get('y2', 100)
        tip1_x = cmd.get('tip1_x', x2)
        tip1_y = cmd.get('tip1_y', y2)
        tip2_x = cmd.get('tip2_x', x2)
        tip2_y = cmd.get('tip2_y', y2)
        color = self._parse_color(cmd.get('color', '#FFFFFF'))

        pygame.draw.line(screen, color, (int(x1), int(y1)), (int(x2), int(y2)), 1)
        pygame.draw.line(screen, color, (int(x2), int(y2)), (int(tip1_x), int(tip1_y)), 1)
        pygame.draw.line(screen, color, (int(x2), int(y2)), (int(tip2_x), int(tip2_y)), 1)

    def _draw_sprite(self, screen: pygame.Surface, cmd: dict):
        """Draw a sprite at specified position"""
        sprite_name = cmd.get('sprite_name', '')
        x = cmd.get('x', 0)
        y = cmd.get('y', 0)
        subimage = cmd.get('subimage', 0)

        # Look up the sprite in the loaded sprites. The registry lives on the
        # GameRunner, reached via the action_executor back-reference — a
        # GameInstance has no `sprites` dict of its own.
        runner = getattr(getattr(self, 'action_executor', None), 'game_runner', None)
        sprites = getattr(runner, 'sprites', None) or {}
        if sprite_name not in sprites:
            logger.error(f"⚠️ Warning: Sprite '{sprite_name}' not found for draw_sprite")
            return

        sprite = sprites[sprite_name]

        # Optional uniform scale (e.g. the promo hub's shrunk level icons),
        # matching _draw_lives's existing pygame.transform.scale pattern.
        scale = cmd.get('scale', 1.0) or 1.0

        def _scaled(surface):
            if scale == 1.0:
                return surface
            w = max(1, int(surface.get_width() * scale))
            h = max(1, int(surface.get_height() * scale))
            return pygame.transform.scale(surface, (w, h))

        # Handle animated sprites (multiple frames)
        if len(sprite.frames) > 0:
            # Use the specified subimage (frame index)
            frame_index = int(subimage) % len(sprite.frames)
            frame_surface = _scaled(sprite.frames[frame_index])
            screen.blit(frame_surface, (int(x), int(y)))
        elif sprite.surface:
            # Single frame sprite
            screen.blit(_scaled(sprite.surface), (int(x), int(y)))
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
            except (ValueError, IndexError):
                # ValueError: non-hex chars; IndexError: shorter than #RRGGBB.
                pass
        return (255, 255, 255)  # Default to white

