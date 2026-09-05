#!/usr/bin/env python3
"""GameRoom: instance list, spatial grid, collision-listened-types cache,
and room rendering (backgrounds, tiles, views, draw-event compositing).

Extracted verbatim from ``runtime/game_runner.py`` (``docs/POST_1_0_REFACTOR.md``
File 3, cluster 2). Substantially larger than the plan doc's original
estimate (~150 LoC) -- that estimate predates the rendering methods
(``render``/``_render_room``/``render_tiles``/the background-layer and
view-compositing methods) that have since accumulated on this class; the
plan's own "Proposed split" allocates rendering to separate
``rendering.py``/``views.py`` modules eventually, but splitting GameRoom's
*own* methods across files needs the harder, File-2-style mixin
methodology -- deferred; this commit only relocates the whole class,
unsplit, which is still a large, real win for ``game_runner.py``'s size
and is behaviour-identical (AST-diff-clean).

``GameRoom.__init__`` constructs ``GameInstance`` directly, and
``set_sprites_for_instances`` calls ``resolve_parent_inheritance`` --
both still live in ``game_runner.py`` (GameInstance hasn't been
extracted yet), which makes this a genuine two-way relationship between
the two files. Resolved with a plain module-level import here
(``from runtime.game_runner import GameInstance, resolve_parent_inheritance``)
rather than a local/lazy import, because it's safe by construction: in
``game_runner.py``, the ``from runtime.room import GameRoom`` re-export
sits at the exact position ``class GameRoom`` used to occupy -- AFTER
both ``GameInstance`` and ``resolve_parent_inheritance`` are already
fully defined in that module's namespace, so by the time this module's
own top-level import runs, there's nothing partially-initialized left to
trip over. **Do not move that import earlier in game_runner.py** (e.g.
to the top-of-file import block) -- that would reintroduce a real
circular-import failure at process start.

``GameSprite`` (already its own module), ``ThymioSimulator``, and
``runtime.extension_hooks`` have no dependency on ``game_runner.py`` and
import here directly with no such ordering constraint.

``game_runner.py`` re-exports ``GameRoom``/``_sane_room_dimension``/
``ROOM_MIN_DIMENSION``/``ROOM_MAX_DIMENSION`` (same precedent as
``runtime/sprite.py``'s ``GameSprite`` re-export) so the many existing
``from runtime.game_runner import ...`` call sites -- including
``tests/test_room_dimension_bounds.py``'s 12 tests -- keep working
unchanged.
"""

import pygame
from pathlib import Path
from typing import Any, Dict, List, Optional, Set, Tuple

from runtime.sprite import GameSprite
from runtime.thymio_simulator import ThymioSimulator
from runtime import extension_hooks
# Safe only because of WHERE game_runner.py re-imports GameRoom from this
# module -- see the module docstring above before touching either side.
from runtime.game_runner import GameInstance, resolve_parent_inheritance

from core.logger import get_logger
logger = get_logger(__name__)


# Room dimension sanity bounds. A room surface is allocated at width x height,
# so a corrupt/hostile project that requests 0, a negative, a non-numeric, or an
# absurdly large size would otherwise crash pygame or exhaust memory at room
# build time. 16384 is comfortably above any real room and below the point where
# a single Surface allocation becomes a problem; 64 is the minimum that still
# renders sensibly.
ROOM_MIN_DIMENSION = 64
ROOM_MAX_DIMENSION = 16384


def _sane_room_dimension(value, default):
    """Coerce a room width/height to a positive int within sane bounds.

    Falls back to ``default`` when ``value`` isn't a finite number (None, a
    string, NaN -> ValueError, inf -> OverflowError), then clamps to
    [ROOM_MIN_DIMENSION, ROOM_MAX_DIMENSION].
    """
    try:
        n = int(value)
    except (TypeError, ValueError, OverflowError):
        n = default
    return max(ROOM_MIN_DIMENSION, min(n, ROOM_MAX_DIMENSION))


class GameRoom:
    """Represents a game room with instances"""

    def __init__(self, name: str, room_data: dict, action_executor=None, project_path=None, sprites_data=None):
        self.name = name
        self.width = _sane_room_dimension(room_data.get('width', 1024), 1024)
        self.height = _sane_room_dimension(room_data.get('height', 768), 768)
        self.background_color = self.parse_color(room_data.get('background_color', '#87CEEB'))
        # Legacy single-background (kept for backward compat)
        self.background_image_name = room_data.get('background_image', '')
        self.tile_horizontal = room_data.get('tile_horizontal', False)
        self.tile_vertical = room_data.get('tile_vertical', False)
        self.bg_hspeed = room_data.get('bg_hspeed', 0.0)
        self.bg_vspeed = room_data.get('bg_vspeed', 0.0)
        self.bg_stretch = room_data.get('bg_stretch', True)
        self.bg_scroll_x = 0.0
        self.bg_scroll_y = 0.0
        self.background_surface = None
        # set_background_color's `show_color` param (execute_set_background_
        # color_action): whether render() fills the screen with
        # background_color each frame, or black when hidden. Filling black
        # rather than skipping the fill entirely — skipping would let the
        # previous frame's pixels smear across frames in this continuously-
        # redrawing pygame loop.
        self.show_background_color = room_data.get('show_background_color', True)
        # set_background's `foreground` param (execute_set_background_action):
        # whether the legacy single-background image draws in front of
        # instances instead of behind them. Mirrors bg_layers' own per-layer
        # foreground pass (_render_bg_layers(foreground=True)) — see
        # _render_room.
        self.background_foreground = room_data.get('background_foreground', False)
        self._stretched_bg_cache = None  # Cached stretched background surface
        self._stretched_layer_cache: Dict[int, Any] = {}  # Cached stretched layer surfaces
        self.project_path = project_path
        self.sprites_data = sprites_data or {}

        # Multi-layer backgrounds (list of up to 8 dicts)
        self.bg_layers = room_data.get('backgrounds', [])
        self.bg_layer_surfaces = {}  # layer_index -> Surface
        self.bg_layer_scroll = {}  # layer_index -> [scroll_x, scroll_y]
        for i in range(len(self.bg_layers)):
            self.bg_layer_scroll[i] = [0.0, 0.0]

        # Tile layer
        self.tiles_data = room_data.get('tiles', [])
        # Pre-sort tiles by depth once (tiles don't change at runtime)
        self._sorted_tiles = sorted(self.tiles_data, key=lambda t: t.get('depth', 1000000), reverse=True)
        self.tile_surfaces = {}  # cache: (bg_name, tx, ty, w, h) -> Surface
        self.instances: List[GameInstance] = []
        self.action_executor = action_executor

        # Scratch space extensions can attach per-room state to, so they don't
        # have to add attributes to engine classes. Namespace your own key —
        # see runtime/extension_hooks.py. The 2.5D raycast feature keeps ALL of
        # its per-room state (camera config + derived wall-edge caches) under
        # extension_state['raycast'] (Stage B3b, docs/RAYCAST_EXTENSION_PLAN.md),
        # so GameRoom carries nothing raycast-specific.
        self.extension_state: Dict[str, Any] = {}

        # Depth-sorted instance cache (invalidated when instances change)
        self._sorted_instances: Optional[List[GameInstance]] = None
        self._depth_dirty = True  # Flag to trigger re-sort

        # Spatial grid for collision optimization
        # Cell size of 64 pixels works well for 32x32 sprites
        self.grid_cell_size = 64

        # Cache: union of every instance's _collision_targets keys.
        # Used by check_movement_collision_with_blocker to skip the nearby-
        # instance scan entirely when no instance in the room cares about
        # collisions with the moving instance's object_name and the moving
        # instance has no targets of its own. Lazily computed; invalidated
        # whenever instances are added/removed/retyped.
        self._collision_listened_types: Optional[Set[str]] = None
        self.spatial_grid: Dict[Tuple[int, int], List[GameInstance]] = {}
        # Reverse mapping: instance -> set of cells it occupies (for O(k) removal)
        self._instance_cells: Dict[int, Set[Tuple[int, int]]] = {}

        # Room persistence - if True, room state is preserved when leaving
        self.persistent = room_data.get('persistent', False)

        # Font cache to avoid repeated allocations (key: size, value: pygame.font.Font)
        self._font_cache: Dict[int, pygame.font.Font] = {}

        # View system - 8 views like GameMaker
        self.views_enabled = room_data.get('views_enabled', room_data.get('enable_views', False))
        # Index of the view currently being rendered (set during render), or -1
        # outside the render loop / when views are disabled. Draw events that
        # want to query the active camera read this.
        self.current_view_index = -1
        self.views = []
        views_raw = room_data.get('views', {})
        # Handle both list and dict formats for views
        if isinstance(views_raw, list):
            views_raw = {}  # Empty list means no views configured
        for i in range(8):
            view_data = views_raw.get(f'view_{i}', {})
            self.views.append({
                'visible': view_data.get('visible', i == 0),  # View 0 visible by default
                'view_x': view_data.get('view_x', 0),
                'view_y': view_data.get('view_y', 0),
                'view_w': view_data.get('view_w', self.width),
                'view_h': view_data.get('view_h', self.height),
                'port_x': view_data.get('port_x', 0),
                'port_y': view_data.get('port_y', 0),
                'port_w': view_data.get('port_w', self.width),
                'port_h': view_data.get('port_h', self.height),
                'follow': view_data.get('follow', None),
                'hborder': view_data.get('hborder', 32),
                'vborder': view_data.get('vborder', 32),
                'hspeed': view_data.get('hspeed', -1),
                'vspeed': view_data.get('vspeed', -1),
            })

        # Don't load background image here - pygame display may not be ready yet
        # Background will be loaded later via load_background_image()

        # Load instances
        instances_data = room_data.get('instances', [])
        for instance_data in instances_data:
            # Support both 'object' and 'object_name' keys for compatibility
            object_name = instance_data.get('object') or instance_data.get('object_name')
            instance = GameInstance(
                object_name,
                instance_data['x'],
                instance_data['y'],
                instance_data,
                action_executor=self.action_executor
            )

            # Check if this is a Thymio robot (by object name or special property)
            if (object_name or '').lower().startswith('thymio') or \
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

    def get_collision_listened_types(self) -> Set[str]:
        """Return the set of object_names that any instance in this room has
        a collision_with_<name> event for. Used as a fast-path filter so
        instances of types nobody cares about can skip movement-collision
        scans entirely. Recomputed lazily on first access after invalidation.
        """
        cached = self._collision_listened_types
        if cached is None:
            types: Set[str] = set()
            for inst in self.instances:
                types.update(inst._collision_targets.keys())
            self._collision_listened_types = types
            return types
        return cached

    def invalidate_collision_listened_types(self) -> None:
        """Drop the cached set so it's rebuilt on next access. Callers should
        invoke this whenever instances are added, removed, or retyped."""
        self._collision_listened_types = None

    def rebuild_spatial_grid(self):
        """Rebuild the entire spatial grid from all instances"""
        self.spatial_grid.clear()
        self._instance_cells.clear()
        for instance in self.instances:
            self._add_to_grid(instance)
        # Mark depth sorting as dirty since instance list changed
        self._depth_dirty = True

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
        instance_id = id(instance)

        # Track which cells this instance occupies
        if instance_id not in self._instance_cells:
            self._instance_cells[instance_id] = set()

        for cell in cells:
            if cell not in self.spatial_grid:
                self.spatial_grid[cell] = []
            if instance not in self.spatial_grid[cell]:
                self.spatial_grid[cell].append(instance)
            self._instance_cells[instance_id].add(cell)

    def _remove_from_grid(self, instance: 'GameInstance'):
        """Remove an instance from the spatial grid in O(k) time.

        Uses the reverse mapping to only check cells the instance actually occupies,
        instead of iterating all cells in the grid.
        """
        instance_id = id(instance)
        cells = self._instance_cells.get(instance_id)
        if cells:
            for cell in cells:
                if cell in self.spatial_grid:
                    cell_instances = self.spatial_grid[cell]
                    if instance in cell_instances:
                        cell_instances.remove(instance)
            self._instance_cells[instance_id].clear()


    def update_dirty_instances(self):
        """Update spatial grid only for instances that have moved (lazy update)"""
        for instance in self.instances:
            if instance._grid_dirty:
                self._remove_from_grid(instance)
                self._add_to_grid(instance)
                instance._grid_dirty = False

    def get_nearby_instances(self, x: float, y: float, w: int = 32, h: int = 32) -> Set['GameInstance']:
        """Get all instances that might collide with an object at (x, y) with size (w, h)

        We expand the search area by one cell in each direction to catch objects
        that might be on the border of adjacent cells.

        Returns a set to avoid duplicate instances and skip list conversion overhead.
        """
        cell_size = self.grid_cell_size
        # Calculate the cell range, expanded by 1 in each direction
        min_cell_x = int(x) // cell_size - 1
        max_cell_x = int(x + w - 1) // cell_size + 1
        min_cell_y = int(y) // cell_size - 1
        max_cell_y = int(y + h - 1) // cell_size + 1

        nearby = set()
        spatial_grid = self.spatial_grid
        for cx in range(min_cell_x, max_cell_x + 1):
            for cy in range(min_cell_y, max_cell_y + 1):
                cell_instances = spatial_grid.get((cx, cy))
                if cell_instances:
                    nearby.update(cell_instances)
        return nearby

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
        # Keep the whole sprite table so a room renderer (e.g. the raycast
        # extension) can resolve a wall_texture / sky_texture sprite by NAME
        # (not just per-instance).
        self._all_sprites = sprites
        for instance in self.instances:
            # Get object data
            if instance.object_name in objects:
                object_data = resolve_parent_inheritance(objects[instance.object_name], objects)
                instance.set_object_data(object_data)

                # Get sprite name from object
                sprite_name = object_data.get('sprite', '')
                if sprite_name and sprite_name in sprites:
                    instance.set_sprite(sprites[sprite_name])
                # else: No sprite assigned - instance.sprite remains None
                # The render method will skip instances with no sprite

        # __init__'s rebuild_spatial_grid() ran before any of the above --
        # every instance was indexed under its GameInstance.__init__ default
        # 32x32 placeholder (_cached_width/_cached_height), not its real
        # sprite size, and set_sprite() above updates those caches without
        # touching the grid (no _grid_dirty flag, no re-add). An object
        # whose real collision size exceeds 32px in either dimension is then
        # only ever found by a query inside its placeholder-sized cell
        # range -- e.g. a 480x32 ground strip registered as if it were
        # 32x32 stops blocking a player who has walked more than about a
        # cell-width away from its origin, who then falls straight through.
        # Rebuilding once more here, now that every instance's cached
        # dimensions are the real ones, is the general fix (not just a
        # patch for this one object): every instance in the room is
        # correctly indexed by its true collision size before the first
        # frame runs.
        self.rebuild_spatial_grid()


    def render(self, screen: pygame.Surface):
        """Render the room and all its instances.

        When views_enabled and at least one view is visible, the renderer
        loops over every visible view in index order (0 first, 7 last) and
        for each one: sets a clip to the port rect, translates room coords
        so the view's top-left maps to the port's top-left, and renders
        the room into the clipped region. The bg color fills the entire
        screen once before the loop so areas not covered by any port show
        the bg color, not stale pixels.
        """
        active_views = self._active_views() if self.views_enabled else []
        fill_color = self.background_color if self.show_background_color else (0, 0, 0)

        if not active_views:
            screen.fill(fill_color)
            self.current_view_index = -1
            self._render_room(screen, (0, 0))
            return

        screen.fill(fill_color)
        prev_clip = screen.get_clip()
        try:
            for i, view in active_views:
                port_x = int(view['port_x'])
                port_y = int(view['port_y'])
                port_w = int(view['port_w'])
                port_h = int(view['port_h'])
                view_x = int(view['view_x'])
                view_y = int(view['view_y'])
                offset = (port_x - view_x, port_y - view_y)

                screen.set_clip(pygame.Rect(port_x, port_y, port_w, port_h))
                self.current_view_index = i
                self._render_room(screen, offset)
        finally:
            screen.set_clip(prev_clip)
            self.current_view_index = -1

    def _active_views(self):
        """Return list of (index, view) tuples for visible views, in order."""
        return [(i, v) for i, v in enumerate(self.views) if v.get('visible')]

    def _render_room(self, screen: pygame.Surface, offset):
        """Internal: render room contents translated by offset.

        offset: (dx, dy) added to every blit so room coords (0, 0) lands at
        (dx, dy) on screen. (0, 0) preserves the legacy no-view behavior.
        """
        # Extensions get first refusal on drawing this room. One that claims it
        # (returns True) replaces the top-down pass entirely (background/tiles/
        # instance sprites); the per-instance draw-event pass still runs
        # afterwards, so HUD actions (draw_score, draw_lives, draw_text,
        # draw_health_bar) composite on top in screen space — see
        # runtime/extension_hooks.py and docs/RAYCAST_HUD_PLAN.md. The 2.5D
        # raycast first-person view (extensions/raycast_2_5d) renders through
        # exactly this seam: its own camera, not compatible with the
        # offset/multi-view system v1; game *logic* (movement, collision,
        # events) is untouched, only the picture changes.
        if extension_hooks.render_room(self, screen):
            self._render_draw_events(screen)
            return

        # Draw background layers (non-foreground) or legacy single background
        # — a legacy background configured with foreground=True (set_background's
        # `foreground` param) is skipped here and drawn after instances instead
        # (below), mirroring bg_layers' own foreground pass.
        if self._bg_layers_active:
            self._render_bg_layers(screen, foreground=False, view_offset=offset)
        elif self.background_surface and not self.background_foreground:
            self._render_legacy_background(screen, view_offset=offset)

        # Render tile layer (behind instances, at depth 1000000 by default)
        self.render_tiles(screen, view_offset=offset)

        # Render all instances sorted by depth (higher depth = drawn first/behind)
        # In GameMaker, lower depth values are drawn on top (in front)
        # Use cached sorted list if available, otherwise sort and cache
        if self._depth_dirty or self._sorted_instances is None:
            self._sorted_instances = sorted(self.instances, key=lambda inst: inst.depth, reverse=True)
            self._depth_dirty = False
        for instance in self._sorted_instances:
            # Regular instances render their sprites
            if not instance.is_thymio:
                instance.render(screen, view_offset=offset)

        # Draw foreground background layers
        if self._bg_layers_active:
            self._render_bg_layers(screen, foreground=True, view_offset=offset)
        elif self.background_surface and self.background_foreground:
            self._render_legacy_background(screen, view_offset=offset)

        # Render Thymio robots separately (on top)
        for instance in self.instances:
            if instance.is_thymio and instance.thymio_simulator:
                # Get render data from simulator and pass to renderer
                # Note: thymio_renderer is accessed from game_runner
                pass  # Will be handled by game_runner's render method

    def _render_draw_events(self, screen: pygame.Surface):
        """Composite per-instance draw events over a finished raycast frame.

        The raycast view is its own camera and replaces the normal top-down
        render, which is where draw events would otherwise run (from
        GameInstance.render). Without this pass a raycast game's HUD is
        invisible on every target — see docs/RAYCAST_HUD_PLAN.md.

        Deliberately mirrors the normal path's semantics so a HUD behaves the
        same in both modes:
          - depth order (higher depth first), same _sorted_instances list;
          - invisible instances are skipped — render() returns early on
            `not self.visible`, so an invisible instance's draw event does not
            fire in normal mode either;
          - Thymio instances are skipped, as in the normal loop.

        Screen space: no view offset, so a HUD draw at (8, 8) lands 8 px from
        the window's top-left. World-space draws (draw_self, draw_sprite at
        room coords) have no meaningful place over a first-person view and are
        NOT projected into it; they land at their raw screen coords.
        """
        if self._depth_dirty or self._sorted_instances is None:
            self._sorted_instances = sorted(self.instances, key=lambda inst: inst.depth, reverse=True)
            self._depth_dirty = False
        for instance in self._sorted_instances:
            if instance.is_thymio or not instance.visible:
                continue
            instance.run_draw_event(screen)

    def update_views(self):
        """Per-tick view update: follow targets, clamp to room bounds.

        Called from GameRunner.render() before current_room.render(). When a
        view has a follow target, the view's (view_x, view_y) is nudged so
        the target stays within (hborder, vborder) of the view edges. The
        view is then clamped so it never extends past the room.
        """
        if not self.views_enabled:
            return
        for view in self.views:
            if not view.get('visible'):
                continue
            target_name = view.get('follow')
            if not target_name:
                continue
            target = self._find_first_instance(target_name)
            if target is None:
                continue
            vw = int(view['view_w'])
            vh = int(view['view_h'])
            hborder = int(view['hborder'])
            vborder = int(view['vborder'])
            old_vx = int(view['view_x'])
            old_vy = int(view['view_y'])
            tx = target.x
            ty = target.y
            # Compute the desired view position (push edge when target outside border zone)
            new_vx = old_vx
            new_vy = old_vy
            if tx < old_vx + hborder:
                new_vx = int(tx - hborder)
            elif tx > old_vx + vw - hborder:
                new_vx = int(tx - vw + hborder)
            if ty < old_vy + vborder:
                new_vy = int(ty - vborder)
            elif ty > old_vy + vh - vborder:
                new_vy = int(ty - vh + vborder)
            # Per-axis speed limit on follow shift. -1 (the default) means no limit.
            hspeed_limit = int(view.get('hspeed', -1))
            vspeed_limit = int(view.get('vspeed', -1))
            if hspeed_limit >= 0:
                dx = new_vx - old_vx
                if dx > hspeed_limit:
                    new_vx = old_vx + hspeed_limit
                elif dx < -hspeed_limit:
                    new_vx = old_vx - hspeed_limit
            if vspeed_limit >= 0:
                dy = new_vy - old_vy
                if dy > vspeed_limit:
                    new_vy = old_vy + vspeed_limit
                elif dy < -vspeed_limit:
                    new_vy = old_vy - vspeed_limit
            # Clamp to room (never show outside the room)
            if vw < self.width:
                new_vx = max(0, min(new_vx, self.width - vw))
            else:
                new_vx = 0
            if vh < self.height:
                new_vy = max(0, min(new_vy, self.height - vh))
            else:
                new_vy = 0
            view['view_x'] = new_vx
            view['view_y'] = new_vy

    def _find_first_instance(self, object_name: str):
        """Return the first instance matching object_name, or None."""
        for inst in self.instances:
            if inst.object_name == object_name:
                return inst
        return None

    @staticmethod
    def _sprite_top_left(inst):
        """The instance's true sprite top-left in room coords.

        Rendering and collision both place a sprite at ``x - origin_x``
        (game_runner render_x, and the collision bbox maths), so anything doing
        geometry off an instance MUST subtract the origin. The raycast pass used
        raw ``inst.x``, so a sprite with a centred origin (e.g. 16,16 on a 32x32)
        was placed half a sprite off -- billboards for such sprites landed on the
        grid lines where walls sit and got sliced in half by the occlusion test
        (user report 2026-07-19).
        """
        spr = getattr(inst, 'sprite', None)
        ox = getattr(spr, 'origin_x', 0) or 0 if spr else 0
        oy = getattr(spr, 'origin_y', 0) or 0 if spr else 0
        return inst.x - ox, inst.y - oy

    def render_tiles(self, screen: pygame.Surface, view_offset=(0, 0)):
        """Render tile layer"""
        if not self.tiles_data:
            return

        backgrounds = getattr(self, '_game_runner_backgrounds', {})
        ox, oy = view_offset

        for tile in self._sorted_tiles:
            bg_name = tile.get('background_name', '')
            if not bg_name or bg_name not in backgrounds:
                continue

            key = (bg_name, tile['tile_x'], tile['tile_y'], tile['width'], tile['height'])
            if key not in self.tile_surfaces:
                bg_surface = backgrounds[bg_name]
                try:
                    sub = bg_surface.subsurface(
                        (tile['tile_x'], tile['tile_y'], tile['width'], tile['height'])
                    )
                    self.tile_surfaces[key] = sub
                except (ValueError, pygame.error):
                    continue

            # Apply layer scroll offset if tile belongs to a layer
            tx, ty = tile['x'], tile['y']
            tile_layer = tile.get('layer', -1)
            layer_scrolls = (tile_layer >= 0 and tile_layer in self.bg_layer_scroll)

            if layer_scrolls:
                scroll = self.bg_layer_scroll[tile_layer]
                sx, sy = int(scroll[0]), int(scroll[1])
                layer = self.bg_layers[tile_layer] if tile_layer < len(self.bg_layers) else {}
                hspeed = layer.get('hspeed', 0.0)
                vspeed = layer.get('vspeed', 0.0)

                # Wrap tile positions so scrolling layers repeat seamlessly
                base_x = tx + sx
                base_y = ty + sy
                if hspeed != 0.0 and self.width > 0:
                    base_x = base_x % self.width
                    if base_x > self.width - tile['width']:
                        # Draw wrapped copy on the other side
                        screen.blit(self.tile_surfaces[key], (base_x - self.width + ox, base_y + oy))
                if vspeed != 0.0 and self.height > 0:
                    base_y = base_y % self.height
                    if base_y > self.height - tile['height']:
                        screen.blit(self.tile_surfaces[key], (base_x + ox, base_y - self.height + oy))
                    # Corner case: wrapping in both axes
                    if hspeed != 0.0 and base_x > self.width - tile['width'] and base_y > self.height - tile['height']:
                        screen.blit(self.tile_surfaces[key], (base_x - self.width + ox, base_y - self.height + oy))
                screen.blit(self.tile_surfaces[key], (base_x + ox, base_y + oy))
            else:
                screen.blit(self.tile_surfaces[key], (tx + ox, ty + oy))

    @property
    def _bg_layers_active(self):
        """Is at least one multi-layer background actually visible?

        A GMK-imported room ships all 8 layer slots present but every one
        disabled (visible=False) -- the room editor's own natively-authored
        default is an empty list, but plenty of shipped rooms carry the
        fuller GMK shape. `bg_layers` being non-EMPTY must not by itself be
        treated as "has a background": _render_room picks the bg_layers
        path over the legacy single-background one (set_background's own
        scroll/tiling) whenever this is true, and a non-empty-but-all-
        disabled list would silently swallow set_background's rendering
        entirely -- exactly what happened to samples/sky_strike_1's
        scrolling ground before this fix (its room0.json copied the 8-slot
        shape from an unrelated sample; set_background's vspeed was set and
        ticking every frame, but nothing ever reached the code that
        actually draws with it). A property, not a value cached at
        construction, because `bg_layers` can be reassigned after the room
        is built (e.g. tests/test_extension_render_hook.py pokes it
        directly) and a stale cache would silently ignore that."""
        return any(layer.get('visible') for layer in self.bg_layers)

    def set_backgrounds_ref(self, backgrounds_dict):
        """Store reference to loaded backgrounds for tile rendering and multi-layer bg"""
        self._game_runner_backgrounds = backgrounds_dict
        # Pre-load surfaces for each layer
        for i, layer in enumerate(self.bg_layers):
            img_name = layer.get('background_image', '')
            if img_name and img_name in backgrounds_dict:
                self.bg_layer_surfaces[i] = backgrounds_dict[img_name]

    def _render_legacy_background(self, screen, view_offset=(0, 0)):
        """Render old single-background format"""
        img_width = self.background_surface.get_width()
        img_height = self.background_surface.get_height()
        ox, oy = view_offset

        if self.bg_hspeed != 0.0 or self.bg_vspeed != 0.0:
            self.bg_scroll_x = (self.bg_scroll_x + self.bg_hspeed) % img_width
            self.bg_scroll_y = (self.bg_scroll_y + self.bg_vspeed) % img_height

        do_tile_h = self.tile_horizontal or self.bg_hspeed != 0.0
        do_tile_v = self.tile_vertical or self.bg_vspeed != 0.0

        if do_tile_h or do_tile_v:
            offset_x = int(self.bg_scroll_x) if do_tile_h else 0
            offset_y = int(self.bg_scroll_y) if do_tile_v else 0
            start_x = offset_x - img_width if do_tile_h else 0
            start_y = offset_y - img_height if do_tile_v else 0
            step_x = img_width if do_tile_h else self.width
            step_y = img_height if do_tile_v else self.height
            x = start_x
            while x < self.width:
                y = start_y
                while y < self.height:
                    screen.blit(self.background_surface, (x + ox, y + oy))
                    y += step_y
                x += step_x
        else:
            if self.bg_stretch:
                if self._stretched_bg_cache is None:
                    self._stretched_bg_cache = pygame.transform.scale(self.background_surface, (self.width, self.height))
                screen.blit(self._stretched_bg_cache, (ox, oy))
            else:
                screen.blit(self.background_surface, (ox, oy))

    def _render_bg_layers(self, screen, foreground=False, view_offset=(0, 0)):
        """Render background layers (foreground=True for layers on top of instances)"""
        vox, voy = view_offset
        for i, layer in enumerate(self.bg_layers):
            if not layer.get('visible'):
                continue
            is_fg = layer.get('foreground', False)
            if is_fg != foreground:
                continue

            surface = self.bg_layer_surfaces.get(i)
            if not surface:
                continue

            img_w = surface.get_width()
            img_h = surface.get_height()
            lx = layer.get('x', 0)
            ly = layer.get('y', 0)
            hspeed = layer.get('hspeed', 0.0)
            vspeed = layer.get('vspeed', 0.0)
            do_tile_h = layer.get('tile_h', False) or hspeed != 0.0
            do_tile_v = layer.get('tile_v', False) or vspeed != 0.0

            # Advance scroll
            scroll = self.bg_layer_scroll.get(i, [0.0, 0.0])
            if hspeed != 0.0 or vspeed != 0.0:
                scroll[0] = (scroll[0] + hspeed) % img_w
                scroll[1] = (scroll[1] + vspeed) % img_h

            if do_tile_h or do_tile_v:
                ox = int(scroll[0]) + lx if do_tile_h else lx
                oy = int(scroll[1]) + ly if do_tile_v else ly
                sx = ox - img_w if do_tile_h else lx
                sy = oy - img_h if do_tile_v else ly
                step_x = img_w if do_tile_h else self.width
                step_y = img_h if do_tile_v else self.height
                x = sx
                while x < self.width:
                    y = sy
                    while y < self.height:
                        screen.blit(surface, (x + vox, y + voy))
                        y += step_y
                    x += step_x
            else:
                if layer.get('stretch', False):
                    if i not in self._stretched_layer_cache:
                        self._stretched_layer_cache[i] = pygame.transform.scale(surface, (self.width, self.height))
                    screen.blit(self._stretched_layer_cache[i], (lx + vox, ly + voy))
                else:
                    screen.blit(surface, (lx + vox, ly + voy))
