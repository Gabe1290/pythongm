"""Kivy export contribution of the Block World extension (Phase 6 Unit 9 of
docs/VOXEL_WORLD_PLAN.md).

SCENE_CODE is class-body Python (4-space-indented methods/attributes) that
KivyExporter._inject_extension_scene_code drops into every generated scene
class at its __PYGM_EXTENSION_SCENE_CODE__ marker, AFTER .format() -- so the
{ } dict/set literals here are single, not doubled (the raycast_2_5d Kivy
port's own established convention -- see that file's header for the exact
mechanism).

A faithful port of extensions/block_world/state.py + renderer.py +
handlers.py + hud.py. All three face orientations are real per-pixel
textures (side: Tier 4a; top/bottom: Tier 4b, docs/DEFERRED_GAPS_2026_PLAN.md),
falling back to the precomputed BLOCK_FACE_COLORS table only when a texture
hasn't loaded, `wall_textured` is off, or (top/bottom) `top_cast_res` is 0.
Only the _fully_covers early-out (a pure perf shortcut) remains scoped out.

Coordinate convention -- mirrors extensions/raycast_2_5d/export_kivy.py's
own solution to the same problem exactly: Kivy instance positions are y-UP
(self.x/self.y is the sprite's Kivy bottom-left), but the whole DDA/
projection pipeline is easiest to reason about, and trivially provable
consistent with desktop, in GameMaker's y-DOWN room space. So every camera/
mover position is converted BACK to GM y-down space at the point it's read
(_bw_gm_xy, mirroring raycast's _raycast_gm_xy), the entire render/pick/
collide pipeline runs in that space verbatim, and only the FINAL draw calls
convert back to Kivy y-up (_bw_fill_span: kivy_y = display_height - gm_y).
Unlike raycast's wall strips (vertically symmetric around the horizon, so a
single y_bot=mid-full_h/2 recentring sufficed), block faces are NOT
symmetric -- each fill computes its own GM-space [y0, y1] span exactly like
desktop's renderer.py, and _bw_fill_span does the one general-case flip.
"""

SCENE_CODE = '''\n    # Precomputed per-block-type average face colors (see
    # tools/gen_block_world_face_colors.py / tools/generated/
    # block_world_face_colors.json -- pinned by
    # tests/test_block_world_export_face_colors.py). Deliberately duplicated
    # here rather than imported -- this extension stays independently
    # removable (see extensions/README.md), and the HTML5 port keeps its own
    # copy for the same reason.
    BLOCK_FACE_COLORS = {
        'brick': {'top': (124, 78, 72), 'bottom': (124, 78, 72), 'side': (124, 78, 72)},
        'clay': {'top': (180, 162, 136), 'bottom': (180, 162, 136), 'side': (180, 162, 136)},
        'coal_block': {'top': (55, 55, 56), 'bottom': (55, 55, 56), 'side': (55, 55, 56)},
        'cobble': {'top': (116, 127, 126), 'bottom': (116, 127, 126), 'side': (116, 127, 126)},
        'desert_sand': {'top': (223, 213, 154), 'bottom': (223, 213, 154), 'side': (223, 213, 154)},
        'diamond_block': {'top': (99, 143, 180), 'bottom': (99, 143, 180), 'side': (99, 143, 180)},
        'dirt': {'top': (172, 124, 68), 'bottom': (172, 124, 68), 'side': (172, 124, 68)},
        'glass': {'top': (137, 156, 168), 'bottom': (137, 156, 168), 'side': (137, 156, 168)},
        'gold_block': {'top': (220, 145, 61), 'bottom': (220, 145, 61), 'side': (220, 145, 61)},
        'grass': {'top': (49, 141, 0), 'bottom': (172, 124, 68), 'side': (46, 135, 0)},
        'gravel': {'top': (115, 116, 112), 'bottom': (115, 116, 112), 'side': (115, 116, 112)},
        'ice': {'top': (174, 204, 225), 'bottom': (174, 204, 225), 'side': (174, 204, 225)},
        'jungle_plank': {'top': (102, 77, 51), 'bottom': (102, 77, 51), 'side': (102, 77, 51)},
        'leaves': {'top': (58, 136, 58), 'bottom': (58, 136, 58), 'side': (58, 136, 58)},
        'mese_block': {'top': (152, 121, 69), 'bottom': (152, 121, 69), 'side': (152, 121, 69)},
        'obsidian': {'top': (31, 30, 30), 'bottom': (31, 30, 30), 'side': (31, 30, 30)},
        'pine_plank': {'top': (196, 150, 93), 'bottom': (196, 150, 93), 'side': (196, 150, 93)},
        'sand': {'top': (218, 204, 171), 'bottom': (218, 204, 171), 'side': (218, 204, 171)},
        'sandstone': {'top': (196, 173, 122), 'bottom': (196, 173, 122), 'side': (196, 173, 122)},
        'snow': {'top': (232, 231, 231), 'bottom': (232, 231, 231), 'side': (232, 231, 231)},
        'stone': {'top': (154, 154, 150), 'bottom': (154, 154, 150), 'side': (154, 154, 150)},
        'water': {'top': (92, 169, 31), 'bottom': (92, 169, 31), 'side': (92, 169, 31)},
        'wood_log': {'top': (134, 103, 78), 'bottom': (134, 103, 78), 'side': (95, 62, 40)},
        'wood_plank': {'top': (139, 98, 50), 'bottom': (139, 98, 50), 'side': (139, 98, 50)},
        'wool_black': {'top': (30, 30, 30), 'bottom': (30, 30, 30), 'side': (30, 30, 30)},
        'wool_blue': {'top': (33, 29, 154), 'bottom': (33, 29, 154), 'side': (33, 29, 154)},
        'wool_green': {'top': (50, 154, 29), 'bottom': (50, 154, 29), 'side': (50, 154, 29)},
        'wool_red': {'top': (154, 29, 29), 'bottom': (154, 29, 29), 'side': (154, 29, 29)},
        'wool_white': {'top': (227, 227, 226), 'bottom': (227, 227, 226), 'side': (227, 227, 226)},
        'wool_yellow': {'top': (236, 162, 0), 'bottom': (236, 162, 0), 'side': (236, 162, 0)},
    }

    # Face -> source PNG filename, mirroring state.BLOCK_TYPES's own top/
    # bottom/side (or 'all') shorthand. Files are materialized at export
    # time under assets/images/block_world/ by KivyExporter
    # ._materialize_extension_textures (decoded from export_data.py's
    # base64 block_textures).
    BLOCK_FACE_FILES = {
        'brick': {'top': 'default_brick.png', 'bottom': 'default_brick.png', 'side': 'default_brick.png'},
        'clay': {'top': 'default_clay.png', 'bottom': 'default_clay.png', 'side': 'default_clay.png'},
        'coal_block': {'top': 'default_coal_block.png', 'bottom': 'default_coal_block.png', 'side': 'default_coal_block.png'},
        'cobble': {'top': 'default_cobble.png', 'bottom': 'default_cobble.png', 'side': 'default_cobble.png'},
        'desert_sand': {'top': 'default_desert_sand.png', 'bottom': 'default_desert_sand.png', 'side': 'default_desert_sand.png'},
        'diamond_block': {'top': 'default_diamond_block.png', 'bottom': 'default_diamond_block.png', 'side': 'default_diamond_block.png'},
        'dirt': {'top': 'default_dirt.png', 'bottom': 'default_dirt.png', 'side': 'default_dirt.png'},
        'glass': {'top': 'default_glass.png', 'bottom': 'default_glass.png', 'side': 'default_glass.png'},
        'gold_block': {'top': 'default_gold_block.png', 'bottom': 'default_gold_block.png', 'side': 'default_gold_block.png'},
        'grass': {'top': 'default_grass.png', 'bottom': 'default_dirt.png', 'side': 'default_grass_side.png'},
        'gravel': {'top': 'default_gravel.png', 'bottom': 'default_gravel.png', 'side': 'default_gravel.png'},
        'ice': {'top': 'default_ice.png', 'bottom': 'default_ice.png', 'side': 'default_ice.png'},
        'jungle_plank': {'top': 'default_junglewood.png', 'bottom': 'default_junglewood.png', 'side': 'default_junglewood.png'},
        'leaves': {'top': 'default_leaves.png', 'bottom': 'default_leaves.png', 'side': 'default_leaves.png'},
        'mese_block': {'top': 'default_mese_block.png', 'bottom': 'default_mese_block.png', 'side': 'default_mese_block.png'},
        'obsidian': {'top': 'default_obsidian.png', 'bottom': 'default_obsidian.png', 'side': 'default_obsidian.png'},
        'pine_plank': {'top': 'default_pine_wood.png', 'bottom': 'default_pine_wood.png', 'side': 'default_pine_wood.png'},
        'sand': {'top': 'default_sand.png', 'bottom': 'default_sand.png', 'side': 'default_sand.png'},
        'sandstone': {'top': 'default_sandstone.png', 'bottom': 'default_sandstone.png', 'side': 'default_sandstone.png'},
        'snow': {'top': 'default_snow.png', 'bottom': 'default_snow.png', 'side': 'default_snow.png'},
        'stone': {'top': 'default_stone.png', 'bottom': 'default_stone.png', 'side': 'default_stone.png'},
        'water': {'top': 'default_water_source_animated.png', 'bottom': 'default_water_source_animated.png', 'side': 'default_water_source_animated.png'},
        'wood_log': {'top': 'default_tree_top.png', 'bottom': 'default_tree_top.png', 'side': 'default_tree.png'},
        'wood_plank': {'top': 'default_wood.png', 'bottom': 'default_wood.png', 'side': 'default_wood.png'},
        'wool_black': {'top': 'wool_black.png', 'bottom': 'wool_black.png', 'side': 'wool_black.png'},
        'wool_blue': {'top': 'wool_blue.png', 'bottom': 'wool_blue.png', 'side': 'wool_blue.png'},
        'wool_green': {'top': 'wool_green.png', 'bottom': 'wool_green.png', 'side': 'wool_green.png'},
        'wool_red': {'top': 'wool_red.png', 'bottom': 'wool_red.png', 'side': 'wool_red.png'},
        'wool_white': {'top': 'wool_white.png', 'bottom': 'wool_white.png', 'side': 'wool_white.png'},
        'wool_yellow': {'top': 'wool_yellow.png', 'bottom': 'wool_yellow.png', 'side': 'wool_yellow.png'},
    }

    # The one block type break_block refuses to remove (state.BLOCK_TYPES'
    # single 'breakable': False entry).
    BW_UNBREAKABLE = frozenset({'obsidian'})

    # Mirrors state.DEFAULT_HOTBAR exactly (order matters).
    BW_DEFAULT_HOTBAR = ['cobble', 'brick', 'wood_plank', 'glass',
                         'wool_red', 'sandstone', 'gold_block', 'leaves']

    # Shading/geometry constants -- mirror renderer.py exactly.
    BW_SIDE_SHADE = 0.85
    BW_FOG_STRENGTH = 0.55
    BW_MIN_SHADE = 0.35
    BW_TOP_SHADE = 1.15
    BW_BOTTOM_SHADE = 0.55
    BW_DEFAULT_EYE_HEIGHT = 1.5
    BW_MAX_PITCH_DEGREES = 70.0
    BW_DEFAULT_MAX_STEP_UP = 1

    def _init_extensions(self):
        # Per-scene block-world state (mirrors raycast_2_5d's own
        # _init_extensions -- was in the scene __init__ before Stage C2b).
        self.block_world_camera = None
        self._bw_group = None
        self._bw_blocks = {}
        self._bw_columns = None
        self._bw_tex_cache = {}

    def _bw_texture(self, filename):
        """Kivy texture for a block-face PNG filename (cached), materialized
        under assets/images/block_world/ at export time. Mirrors
        raycast_2_5d's own _raycast_texture. Returns None (falls back to
        BLOCK_FACE_COLORS) if the file is missing or hasn't loaded."""
        if not filename:
            return None
        cache = self._bw_tex_cache
        if filename in cache:
            return cache[filename]
        tex = None
        try:
            img = load_image('assets/images/block_world/' + filename)
            if img is not None:
                tex = img.texture
        except Exception:
            tex = None
        cache[filename] = tex
        return tex

    def _render_extension_overlay(self):
        if getattr(self, 'block_world_camera', None) and self.block_world_camera.get('enabled'):
            self._render_block_world()
            return True
        return False

    # ------------------------------------------------------------------
    # state.py port (world storage + heightmap queries, keyed by (x, y, z)
    # tuples directly -- no JSON round-trip boundary at runtime, unlike
    # desktop's string-keyed dict, which exists purely for that boundary).
    # ------------------------------------------------------------------
    def _bw_gm_xy(self, inst):
        """(gm_x, gm_y) top-left of inst in GameMaker y-down room space --
        the inverse of the y-up conversion done at instance creation
        (mirrors raycast_2_5d's _raycast_gm_xy)."""
        h = float(getattr(inst, 'image_height', 0) or 0)
        return float(inst.x), self.room_height - float(inst.y) - h

    def _bw_color(self, spec, default):
        """Parse a '#rrggbb' color to an (r, g, b) 0..255 int triple."""
        try:
            s = str(spec or default).lstrip('#')
            if len(s) == 3:
                s = ''.join(c * 2 for c in s)
            return (int(s[0:2], 16), int(s[2:4], 16), int(s[4:6], 16))
        except Exception:
            s = default.lstrip('#')
            return (int(s[0:2], 16), int(s[2:4], 16), int(s[4:6], 16))

    def _bw_get_block(self, x, y, z):
        return self._bw_blocks.get((x, y, z))

    def _bw_set_block(self, x, y, z, block_type):
        self._bw_blocks[(x, y, z)] = block_type
        self._bw_columns = None

    def _bw_remove_block(self, x, y, z):
        self._bw_blocks.pop((x, y, z), None)
        self._bw_columns = None

    def _bw_column_index(self):
        """{(x,y): [(z, block_type), ...]} sorted lowest z first, cached
        until a mutator clears self._bw_columns (mirrors
        state.column_index)."""
        if self._bw_columns is not None:
            return self._bw_columns
        index = {}
        for (x, y, z), block_type in self._bw_blocks.items():
            index.setdefault((x, y), []).append((z, block_type))
        for column in index.values():
            column.sort()
        self._bw_columns = index
        return index

    def _bw_stack_top(self, x, y):
        column = self._bw_column_index().get((x, y))
        return column[-1][0] if column else None

    def _bw_ground_layer(self, x, y):
        top = self._bw_stack_top(x, y)
        return 0 if top is None else top + 1

    def _bw_can_enter(self, x, y, standing_layer, max_step_up=None):
        if max_step_up is None:
            max_step_up = self.BW_DEFAULT_MAX_STEP_UP
        return self._bw_ground_layer(x, y) - standing_layer <= max_step_up

    def _bw_cell_of(self, pixel_value, cell_size):
        return int((pixel_value + cell_size / 2) // cell_size)

    # ------------------------------------------------------------------
    # renderer.py port
    # ------------------------------------------------------------------
    def _bw_march_ray(self, px, py, angle_rad, cell_size, max_cells):
        """The DDA: yields one entry per cell ENTERED, mirroring march_ray
        exactly -- (map_x, map_y, entry, exit, side, tex_u), tex_u added for
        Tier 4a (real per-pixel wall textures)."""
        import math
        px_cell, py_cell = px / cell_size, py / cell_size
        dx, dy = math.cos(angle_rad), math.sin(angle_rad)
        map_x, map_y = int(math.floor(px_cell)), int(math.floor(py_cell))
        delta_x = abs(1 / dx) if dx != 0 else 1e30
        delta_y = abs(1 / dy) if dy != 0 else 1e30
        if dx < 0:
            step_x = -1
            side_x = (px_cell - map_x) * delta_x
        else:
            step_x = 1
            side_x = (map_x + 1 - px_cell) * delta_x
        if dy < 0:
            step_y = -1
            side_y = (py_cell - map_y) * delta_y
        else:
            step_y = 1
            side_y = (map_y + 1 - py_cell) * delta_y
        for _ in range(max_cells):
            if side_x < side_y:
                side_x += delta_x
                map_x += step_x
                side = 0
                entry = side_x - delta_x
            else:
                side_y += delta_y
                map_y += step_y
                side = 1
                entry = side_y - delta_y
            exit_cells = side_x if side_x < side_y else side_y
            # Texture-U: fractional position along the hit face -- same
            # derivation as march_ray.py.
            if side == 0:
                wall_coord = py_cell + entry * dy
                if dx > 0:
                    wall_coord = -wall_coord
            else:
                wall_coord = px_cell + entry * dx
                if dy < 0:
                    wall_coord = -wall_coord
            tex_u = wall_coord - math.floor(wall_coord)
            yield (map_x, map_y, max(entry, 1e-4) * cell_size,
                  exit_cells * cell_size, side, tex_u)

    def _bw_eye_z_for(self, cfg):
        eye_height = cfg.get('eye_height', self.BW_DEFAULT_EYE_HEIGHT)
        return int(cfg.get('z_layer', 0)) + float(eye_height)

    def _bw_clamp_pitch(self, pitch_degrees):
        return max(-self.BW_MAX_PITCH_DEGREES,
                   min(self.BW_MAX_PITCH_DEGREES, float(pitch_degrees)))

    def _bw_horizon_for(self, screen_h, pitch_degrees):
        import math
        pitch = self._bw_clamp_pitch(pitch_degrees)
        return screen_h * 0.5 + screen_h * math.tan(math.radians(pitch))

    def _bw_screen_ray(self, sx, sy, facing_screen_rad, fov_rad, screen_w,
                       screen_h, cell_size, horizon):
        import math
        camera_x = 2.0 * sx / screen_w - 1.0
        offset = math.atan(math.tan(fov_rad / 2) * camera_x)
        if horizon is None:
            horizon = screen_h * 0.5
        z_per_px = -(sy - horizon) * math.cos(offset) / (screen_h * cell_size)
        return facing_screen_rad + offset, z_per_px

    def _bw_pick_voxel(self, cam_x, cam_y, eye_z, angle_rad, z_per_px,
                       cell_size, reach, z_min=-64, z_max=256):
        """Mirrors renderer.pick_voxel exactly -- see its docstring for the
        gap/placement rules."""
        import math
        first = None
        prev = None
        gap = None
        for map_x, map_y, entry, exit_d, _side, _tex_u in self._bw_march_ray(
                cam_x, cam_y, angle_rad, cell_size, reach):
            z_entry = eye_z + z_per_px * entry
            z_exit = eye_z + z_per_px * exit_d
            low, high = (z_entry, z_exit) if z_entry <= z_exit else (z_exit, z_entry)
            low = max(int(math.floor(low)), z_min)
            high = min(int(math.floor(high)), z_max)
            if high < low:
                continue
            layers = range(low, high + 1) if z_per_px >= 0 else range(high, low - 1, -1)
            for layer in layers:
                if first is None:
                    first = (map_x, map_y, layer)
                if self._bw_get_block(map_x, map_y, layer) is not None:
                    if gap is not None:
                        return (map_x, map_y, layer), gap
                    return (map_x, map_y, layer), prev
                if gap is None and self._bw_get_block(map_x, map_y, layer + 1) is not None:
                    gap = (map_x, map_y, layer)
                prev = (map_x, map_y, layer)
        if gap is not None:
            return None, gap
        return None, first

    def _bw_wall_shade(self, side, corrected, max_dist):
        side_factor = self.BW_SIDE_SHADE if side == 1 else 1.0
        t = corrected / max_dist if max_dist > 0 else 0.0
        t = max(0.0, min(1.0, t))
        dist_factor = 1.0 - self.BW_FOG_STRENGTH * t
        return max(self.BW_MIN_SHADE, side_factor * dist_factor)

    def _bw_face_shade(self, corrected, max_dist, facing):
        t = corrected / max_dist if max_dist > 0 else 0.0
        t = max(0.0, min(1.0, t))
        return max(self.BW_MIN_SHADE, min(1.0, facing * (1.0 - self.BW_FOG_STRENGTH * t)))

    def _bw_has_neighbor(self, stack, index, delta):
        j = index + (1 if delta > 0 else -1)
        return 0 <= j < len(stack) and stack[j][0] == stack[index][0] + delta

    def _find_block_world_camera(self, cfg):
        """The camera instance: the one stored on the config
        (camera_instance=self from enable_block_world_view with no named
        target) if still alive, else the first live instance of
        camera_object. Mirrors raycast_2_5d's _find_raycast_camera."""
        cam = cfg.get('camera_instance')
        if cam is not None and cam in self.instances \\
                and cam not in self.instances_to_destroy:
            return cam
        name = cfg.get('camera_object', '')
        return self._find_view_target(name) if name else None

    def _bw_fill_span(self, group, x0, strip_w, y0_gm, y1_gm, rgb, shade, H):
        """Fill a screen column span computed in GM y-DOWN space, converting
        to Kivy y-UP at the one point that matters: kivy_y = H - gm_y. Unlike
        raycast's symmetric wall strips, block faces need this general-case
        flip (see this file's header comment)."""
        y0 = max(0.0, min(y0_gm, y1_gm))
        y1 = min(H, max(y0_gm, y1_gm))
        if y1 <= y0:
            return
        group.add(Color(rgb[0] / 255.0 * shade, rgb[1] / 255.0 * shade,
                        rgb[2] / 255.0 * shade, 1))
        group.add(Rectangle(pos=(x0, H - y1), size=(strip_w, y1 - y0)))

    def _bw_fill_span_textured(self, group, x0, strip_w, y0_gm, y1_gm,
                               full_top_gm, full_h, tex, tex_x, shade, H):
        """Real per-pixel wall-strip texture (Tier 4a). Same GM-down-then-
        flip approach as _bw_fill_span, but the v (vertical texture)
        coordinate must ALSO respect the flip: a normal (non-flipped) Kivy
        Rectangle shows v=1 at its TOP edge and v=0 at its BOTTOM edge
        (Kivy's default tex_coords convention -- confirmed against
        raycast_2_5d's own proven wall-texture v0/v1 derivation), and
        texel row 0 (top of the source PNG) is the block's GM-TOP edge --
        which after the flip IS the Kivy-top (high y). So v=1 (Kivy rect
        top) <-> GM top (full_top_gm) <-> texel row 0, and v=0 (Kivy rect
        bottom) <-> GM top + full_h <-> texel row (th-1).

        frac0/frac1 are the CLIPPED edges' fraction of the way down from
        the unclipped strip's GM-top (0 at the top, 1 at the bottom);
        v_bottom = 1 - frac1, v_top = 1 - frac0 is the resulting Kivy
        tex_coords pair.
        """
        y0 = max(0.0, min(y0_gm, y1_gm))
        y1 = min(H, max(y0_gm, y1_gm))
        if y1 <= y0:
            return
        frac0 = (y0 - full_top_gm) / full_h
        frac1 = (y1 - full_top_gm) / full_h
        v_bottom = 1.0 - frac1
        v_top = 1.0 - frac0
        region = tex.get_region(tex_x, 0, 1, tex.height)
        group.add(Color(shade, shade, shade, 1))
        group.add(Rectangle(texture=region, pos=(x0, H - y1), size=(strip_w, y1 - y0),
                            tex_coords=(0.0, v_bottom, 1.0, v_bottom,
                                        1.0, v_top, 0.0, v_top)))

    def _bw_draw_horizontal_face_textured(self, group, x0, strip_w, y0_gm, y1_gm,
                                          tex, cam_x, cam_y, dir_x, dir_y, cos_off,
                                          plane_z, eye_z, horizon_gm, cell_size,
                                          shade, res, H):
        """Real per-pixel top/bottom face texture (Tier 4b). Faithful port
        of renderer.py's _draw_horizontal_face_textured's projection math
        (inverting y = horizon + (eye_z - zval) * (H*cell/dist) gives the
        world point straight from a screen row), but samples each texel as
        its OWN 1x1 get_region() draw rather than building a raw pixel
        buffer via Texture.create()/blit_buffer() -- that would need
        reasoning about blit_buffer's own row-order convention on top of
        get_region's; a single-pixel region has no orientation to get
        wrong, reusing get_region's bottom-left-origin behaviour (per
        _bw_fill_span_textured's own derivation above: get_region's y is
        GL/bottom-up, so an image-top-relative ty needs the same
        `th - 1 - ty` flip raycast_2_5d's _floor_buffer already established
        for reading Kivy texture pixels) for the read side only.

        n = ceil(span/res) equal-height segments tile the span exactly
        (matching what scaling a res-sampled column to fit span would do),
        each sampled at approximately the row the original per-row
        algorithm would have used.
        """
        import math
        y0 = max(0.0, min(y0_gm, y1_gm))
        y1 = min(H, max(y0_gm, y1_gm))
        span = y1 - y0
        if span <= 0:
            return
        tw, th = tex.width, tex.height
        if tw <= 0 or th <= 0:
            return

        k = (eye_z - plane_z) * H * cell_size
        inv_cell = 1.0 / cell_size

        def texel_region(y):
            denom = y + 0.5 - horizon_gm
            if -1e-6 < denom < 1e-6:
                denom = 1e-6 if denom >= 0 else -1e-6
            ray_dist = (k / denom) / cos_off
            gx = (cam_x + dir_x * ray_dist) * inv_cell
            gy = (cam_y + dir_y * ray_dist) * inv_cell
            tx = min(tw - 1, max(0, int(tw * (gx - math.floor(gx)))))
            ty = min(th - 1, max(0, int(th * (gy - math.floor(gy)))))
            return tex.get_region(tx, th - 1 - ty, 1, 1)

        n = max(1, int(math.ceil(span / res)))
        seg_h = span / n
        shade_rgb = (shade, shade, shade, 1) if shade < 1.0 else (1, 1, 1, 1)
        for i in range(n):
            seg_y0 = y0 + i * seg_h
            seg_y1 = y0 + (i + 1) * seg_h
            sample_y = min(y0 + i * res, y1 - 1e-6)
            region = texel_region(sample_y)
            group.add(Color(*shade_rgb))
            group.add(Rectangle(texture=region, pos=(x0, H - seg_y1),
                                size=(strip_w, seg_y1 - seg_y0)))

    def _render_block_world(self):
        """A faithful port of renderer.render_block_world_view. All three
        face orientations are real per-pixel textures (side: Tier 4a;
        top/bottom: Tier 4b). Only the _fully_covers early-out remains
        scoped out (a pure perf shortcut) -- see this file's module
        docstring and export_html5.js's header."""
        import math
        cfg = self.block_world_camera
        if not cfg or not cfg.get('enabled'):
            if getattr(self, '_bw_group', None) is not None:
                self._bw_group.clear()
            return
        if getattr(self, '_bw_group', None) is None:
            self._bw_group = InstructionGroup()
            self.canvas.after.add(self._bw_group)
        group = self._bw_group
        group.clear()

        cell_size = int(cfg.get('cell_size', 32))
        W = float(self.display_width)
        H = float(self.display_height)
        horizon_gm = self._bw_horizon_for(H, float(cfg.get('pitch', 0.0)))

        ceiling_rgb = self._bw_color(cfg.get('ceiling_color'), '87CEEB')
        floor_rgb = self._bw_color(cfg.get('floor_color'), '3a2f1c')
        ceil_h = max(0.0, min(H, horizon_gm))
        group.add(Color(ceiling_rgb[0] / 255.0, ceiling_rgb[1] / 255.0, ceiling_rgb[2] / 255.0, 1))
        group.add(Rectangle(pos=(0, max(0.0, H - horizon_gm)), size=(W, ceil_h)))
        group.add(Color(floor_rgb[0] / 255.0, floor_rgb[1] / 255.0, floor_rgb[2] / 255.0, 1))
        group.add(Rectangle(pos=(0, 0), size=(W, max(0.0, H - horizon_gm))))

        camera = self._find_block_world_camera(cfg)
        if camera is None:
            return   # flat floor/ceiling only

        gm_x, gm_y = self._bw_gm_xy(camera)
        cam_x = gm_x + float(getattr(camera, 'image_width', 0) or 0) / 2.0
        cam_y = gm_y + float(getattr(camera, 'image_height', 0) or 0) / 2.0
        eye_z = self._bw_eye_z_for(cfg)

        wall_rgb = self._bw_color(cfg.get('wall_color'), '8a8a8a')
        fov_deg = float(cfg.get('fov', 66))
        fov_rad = math.radians(fov_deg)
        render_distance_cells = int(cfg.get('render_distance', 20))
        max_dist = render_distance_cells * cell_size
        num_columns = int(cfg.get('columns', 0)) or int(min(W, 320))
        num_columns = max(1, num_columns)
        col_width = W / num_columns
        facing_screen_rad = math.radians(-float(getattr(camera, 'facing_angle', 0)))
        plane_tan = math.tan(fov_rad / 2)
        textured = bool(cfg.get('wall_textured', True))
        # Top/bottom per-pixel cast resolution (Tier 4b) -- 0 disables
        # texturing (flat average-color fallback), matching desktop exactly.
        top_res = int(cfg.get('top_cast_res', 4))
        top_textured = textured and top_res >= 1
        columns = self._bw_column_index()

        for col in range(num_columns):
            camera_x = 2.0 * (col + 0.5) / num_columns - 1.0
            ray_offset = math.atan(plane_tan * camera_x)
            ray_angle = facing_screen_rad + ray_offset
            cos_off = math.cos(ray_offset)
            dir_x, dir_y = math.cos(ray_angle), math.sin(ray_angle)
            x0 = int(col * col_width)
            x1 = int((col + 1) * col_width)
            strip_w = max(1, x1 - x0)

            hits = []
            for map_x, map_y, entry, exit_d, side, tex_u in self._bw_march_ray(
                    cam_x, cam_y, ray_angle, cell_size, render_distance_cells):
                stack = columns.get((map_x, map_y))
                if not stack:
                    continue
                near = max(entry * cos_off, 1e-4)
                far = max(exit_d * cos_off, near)
                px_per_cell = H * cell_size / near
                hits.append((near, far, side, tex_u, stack, px_per_cell))

            for near, far, side, tex_u, stack, px_per_cell in reversed(hits):
                px_per_cell_far = H * cell_size / far
                shade = self._bw_wall_shade(side, near, max_dist)
                mid = (near + far) / 2.0
                for i, (z, block_type) in enumerate(stack):
                    color_set = self.BLOCK_FACE_COLORS.get(block_type) if textured else None
                    side_rgb = color_set['side'] if color_set else wall_rgb

                    y_top = horizon_gm + (eye_z - (z + 1)) * px_per_cell
                    # Real per-pixel texture (Tier 4a) when loaded; flat
                    # average-color fallback otherwise.
                    file_set = self.BLOCK_FACE_FILES.get(block_type) if textured else None
                    tex = self._bw_texture(file_set['side']) if file_set else None
                    if tex is not None:
                        tw = tex.width
                        tex_x = min(tw - 1, max(0, int(tex_u * tw)))
                        self._bw_fill_span_textured(
                            group, x0, strip_w, y_top, y_top + px_per_cell,
                            y_top, px_per_cell, tex, tex_x, shade, H)
                    else:
                        self._bw_fill_span(group, x0, strip_w, y_top,
                                           y_top + px_per_cell, side_rgb, shade, H)

                    above = self._bw_has_neighbor(stack, i, 1)
                    below = self._bw_has_neighbor(stack, i, -1)

                    if eye_z > z + 1 and not above:
                        lit = self._bw_face_shade(mid, max_dist, self.BW_TOP_SHADE)
                        y_far = horizon_gm + (eye_z - (z + 1)) * px_per_cell_far
                        y_near = horizon_gm + (eye_z - (z + 1)) * px_per_cell
                        top_tex = (self._bw_texture(file_set['top'])
                                  if top_textured and file_set else None)
                        if top_tex is not None:
                            self._bw_draw_horizontal_face_textured(
                                group, x0, strip_w, y_far, y_near, top_tex,
                                cam_x, cam_y, dir_x, dir_y, cos_off,
                                z + 1, eye_z, horizon_gm, cell_size, lit, top_res, H)
                        else:
                            color = color_set['top'] if color_set else wall_rgb
                            self._bw_fill_span(group, x0, strip_w, y_far, y_near, color, lit, H)
                    elif eye_z < z and not below:
                        lit = self._bw_face_shade(mid, max_dist, self.BW_BOTTOM_SHADE)
                        y_near = horizon_gm + (eye_z - z) * px_per_cell
                        y_far = horizon_gm + (eye_z - z) * px_per_cell_far
                        bottom_tex = (self._bw_texture(file_set['bottom'])
                                     if top_textured and file_set else None)
                        if bottom_tex is not None:
                            self._bw_draw_horizontal_face_textured(
                                group, x0, strip_w, y_near, y_far, bottom_tex,
                                cam_x, cam_y, dir_x, dir_y, cos_off,
                                z, eye_z, horizon_gm, cell_size, lit, top_res, H)
                        else:
                            color = color_set['bottom'] if color_set else wall_rgb
                            self._bw_fill_span(group, x0, strip_w, y_near, y_far, color, lit, H)

    # ------------------------------------------------------------------
    # handlers.py port -- each takes the acting GameObject (`obj`) as an
    # explicit argument, called from a one-line ACTION_CODEGEN call site
    # below (self.scene._bw_xxx(self, ...)).
    # ------------------------------------------------------------------
    def _bw_pick(self, obj, reach):
        """Mirrors handlers.PluginExecutor._pick. Returns (target,
        placement), each an (x, y, z) cell or None."""
        cfg = self.block_world_camera
        if not cfg or not cfg.get('enabled'):
            return None, None
        camera = self._find_block_world_camera(cfg)
        if camera is None:
            return None, None
        reach = max(1, int(reach))
        cell_size = int(cfg.get('cell_size', 32))
        W = float(self.display_width)
        H = float(self.display_height)
        import math
        fov_rad = math.radians(float(cfg.get('fov', 66)))
        horizon = self._bw_horizon_for(H, float(cfg.get('pitch', 0.0)))
        facing_screen_rad = math.radians(-float(getattr(camera, 'facing_angle', 0)))
        angle_rad, z_per_px = self._bw_screen_ray(
            W / 2.0, H / 2.0, facing_screen_rad, fov_rad, W, H, cell_size, horizon)
        gm_x, gm_y = self._bw_gm_xy(camera)
        cam_x = gm_x + float(getattr(camera, 'image_width', 0) or 0) / 2.0
        cam_y = gm_y + float(getattr(camera, 'image_height', 0) or 0) / 2.0
        eye_z = self._bw_eye_z_for(cfg)
        return self._bw_pick_voxel(cam_x, cam_y, eye_z, angle_rad, z_per_px, cell_size, reach)

    def _bw_place_block(self, obj, block, reach):
        target, placement = self._bw_pick(obj, reach)
        if placement is None:
            return
        block = str(block) if block else 'stone'
        if block not in self.BLOCK_FACE_COLORS:
            return
        self._bw_set_block(placement[0], placement[1], placement[2], block)

    def _bw_break_block(self, obj, reach):
        target, placement = self._bw_pick(obj, reach)
        if target is None:
            return
        bt = self._bw_get_block(target[0], target[1], target[2])
        if bt is not None and bt in self.BW_UNBREAKABLE:
            return
        self._bw_remove_block(target[0], target[1], target[2])

    def _bw_select_hotbar_slot(self, obj, index, relative):
        index = int(index)
        if relative:
            index += int(getattr(obj, 'hotbar_index', 0))
        n = len(self.BW_DEFAULT_HOTBAR)
        index %= n
        obj.hotbar_index = index
        obj.hotbar_block = self.BW_DEFAULT_HOTBAR[index]

    def _bw_set_look_pitch(self, pitch, relative):
        cfg = self.block_world_camera
        if not cfg:
            return
        pitch = float(pitch)
        if relative:
            pitch += float(cfg.get('pitch', 0.0))
        cfg['pitch'] = self._bw_clamp_pitch(pitch)

    def _bw_move_and_collide(self, obj, dx, dy, collide):
        """Mirrors handlers.execute_move_and_collide_action. dx/dy are GM
        y-DOWN pixel deltas; applied to Kivy's y-UP obj.y with the axis
        flipped (obj.x is unaffected -- x isn't flipped by either frame)."""
        cfg = self.block_world_camera
        if not cfg or not cfg.get('enabled'):
            return
        cell_size = int(cfg.get('cell_size', 32))
        tl_x, tl_y = self._bw_gm_xy(obj)
        standing = self._bw_ground_layer(self._bw_cell_of(tl_x, cell_size),
                                         self._bw_cell_of(tl_y, cell_size))

        nx = tl_x + dx
        if not collide or self._bw_can_enter(
                self._bw_cell_of(nx, cell_size), self._bw_cell_of(tl_y, cell_size), standing):
            obj.x += dx
            tl_x = nx
        ny = tl_y + dy
        if not collide or self._bw_can_enter(
                self._bw_cell_of(tl_x, cell_size), self._bw_cell_of(ny, cell_size), standing):
            obj.y -= dy   # GM y-down delta -> Kivy y-up
            tl_y = ny

        standing = self._bw_ground_layer(self._bw_cell_of(tl_x, cell_size),
                                         self._bw_cell_of(tl_y, cell_size))
        camera = self._find_block_world_camera(cfg)
        if camera is obj:
            cfg['z_layer'] = standing

    def _bw_load_block_world(self, block_list):
        """Atomic: an unknown block type rejects the whole list, mirroring
        state.load_block_list's KeyError. block_list is embedded as a
        Python literal at export time (Kivy has no live project_data to
        read a path out of at runtime) by the load_block_world action
        codegen below, sourced from extensions/block_world/export_data.py's
        collect_export_data via KivyExporter's generic extension-data hook."""
        blocks = {}
        for entry in block_list:
            bt = entry.get('type')
            if bt not in self.BLOCK_FACE_COLORS:
                return
            blocks[(entry['x'], entry['y'], entry['z'])] = bt
        self._bw_blocks = blocks
        self._bw_columns = None

    # ------------------------------------------------------------------
    # hud.py port
    # ------------------------------------------------------------------
    def _bw_build_hud_commands(self, selected_index, slot_size, gap, margin_bottom,
                               back_color, border_color, selected_color, text_color,
                               crosshair_size, crosshair_color):
        """Mirrors hud.build_block_world_hud_commands exactly. Coordinates
        are screen-space y-down; the shared draw-queue path flips once for
        Kivy (see kivy_exporter.py's EXTENSION OVERLAY / HUD compositing
        comment)."""
        W = float(self.display_width)
        H = float(self.display_height)
        cmds = []
        ccx, ccy = W / 2.0, H / 2.0
        half = crosshair_size / 2.0
        cmds.append(dict(type='line', x1=ccx - half, y1=ccy, x2=ccx + half, y2=ccy,
                         color=crosshair_color))
        cmds.append(dict(type='line', x1=ccx, y1=ccy - half, x2=ccx, y2=ccy + half,
                         color=crosshair_color))

        hotbar = self.BW_DEFAULT_HOTBAR
        n = len(hotbar)
        if n == 0:
            return cmds
        total_w = n * slot_size + (n - 1) * gap
        x0 = (W - total_w) / 2.0
        y0 = H - margin_bottom - slot_size
        for i, block_type in enumerate(hotbar):
            sx = x0 + i * (slot_size + gap)
            fill = selected_color if i == selected_index else back_color
            cmds.append(dict(type='rectangle', x1=sx, y1=y0, x2=sx + slot_size,
                             y2=y0 + slot_size, color=fill, filled=True))
            cmds.append(dict(type='rectangle', x1=sx, y1=y0, x2=sx + slot_size,
                             y2=y0 + slot_size, color=border_color, filled=False))
            cmds.append(dict(type='text', text=block_type[:4], x=sx + 2,
                             y=y0 + slot_size - 14, color=text_color))
        return cmds
'''


# ---------------------------------------------------------------------------
# Kivy action codegen (Stage C2c pattern). code_generator._convert_simple_
# action's DEFAULT branch consults ACTION_CODEGEN for actions it does not
# enumerate. Each fn receives (gen, params, event_type); gen is the
# ActionCodeGenerator instance (used here for gen.extension_data --
# load_block_world's embedded world data, populated by KivyExporter's
# generic _collect_extension_data hook from
# extensions/block_world/export_data.py). Mirrors the desktop handlers in
# handlers.py.
# ---------------------------------------------------------------------------

def _cg_enable_block_world_view(gen, params, event_type):
    from export.Kivy.code_generator import _tofloat
    en = params.get('enable', True)
    if isinstance(en, str):
        en = en.strip().lower() not in ('false', '0', 'no')
    if not en:
        return "self.scene.block_world_camera = {'enabled': False}"
    cfg = {
        'enabled': True,
        'camera_object': str(params.get('camera_object') or ''),
        'z_layer': int(_tofloat(params.get('z_layer'), 0)),
        'fov': _tofloat(params.get('fov'), 66),
        'render_distance': int(_tofloat(params.get('render_distance'), 20)),
        'cell_size': int(_tofloat(params.get('cell_size'), 32)),
        'columns': int(_tofloat(params.get('columns'), 320)),
        'wall_color': str(params.get('wall_color') or '#8a8a8a'),
        'floor_color': str(params.get('floor_color') or '#3a2f1c'),
        'ceiling_color': str(params.get('ceiling_color') or '#87CEEB'),
        'wall_textured': not (str(params.get('wall_textured', 'true')).strip().lower()
                              in ('false', '0', 'no')),
        'pitch': max(-70.0, min(70.0, _tofloat(params.get('pitch'), 0))),
        'eye_height': _tofloat(params.get('eye_height'), 1.5),
        # Top/bottom per-pixel cast resolution (Tier 4b) -- 0 disables
        # texturing (flat average-color fallback), matching desktop.
        'top_cast_res': int(_tofloat(params.get('top_cast_res'), 4)),
    }
    if not cfg['camera_object']:
        # No named camera object -> the acting instance IS the camera.
        return (f"self.scene.block_world_camera = {cfg!r}; "
                f"self.scene.block_world_camera['camera_instance'] = self; "
                f"self.scene._bw_columns = None")
    return f"self.scene.block_world_camera = {cfg!r}; self.scene._bw_columns = None"

def _cg_set_look_pitch(gen, params, event_type):
    from export.Kivy.code_generator import _num_code
    pitch = _num_code(params.get('pitch', 0))
    rel = params.get('relative', False)
    if isinstance(rel, str):
        rel = rel.strip().lower() in ('true', '1', 'yes')
    return f"self.scene._bw_set_look_pitch({pitch}, {bool(rel)!r})"

def _cg_select_hotbar_slot(gen, params, event_type):
    from export.Kivy.code_generator import _num_code
    index = _num_code(params.get('index', 0))
    rel = params.get('relative', False)
    if isinstance(rel, str):
        rel = rel.strip().lower() in ('true', '1', 'yes')
    return f"self.scene._bw_select_hotbar_slot(self, {index}, {bool(rel)!r})"

def _cg_move_and_collide(gen, params, event_type):
    from export.Kivy.code_generator import _num_code
    dx = _num_code(params.get('dx', 0))
    dy = _num_code(params.get('dy', 0))
    collide = params.get('collide', True)
    if isinstance(collide, str):
        collide = collide.strip().lower() not in ('false', '0', 'no')
    return f"self.scene._bw_move_and_collide(self, {dx}, {dy}, {bool(collide)!r})"

def _cg_place_block(gen, params, event_type):
    from export.Kivy.code_generator import _tofloat
    block_raw = str(params.get('block', 'stone'))
    reach = int(_tofloat(params.get('reach', 5), 5))
    # `block` is usually a literal block-type id (a dropdown choice); the
    # one documented exception is binding it to "hotbar_block"
    # (select_hotbar_slot's own instance attribute) -- mirrors
    # handlers.execute_place_block_action's ae._parse_value resolving a
    # bare instance-variable name via hasattr. getattr(self, name, name)
    # reproduces exactly that precedence in one runtime expression: if the
    # instance has the attribute, use it; otherwise fall back to the raw
    # string itself (the literal-block-type case).
    return (f"self.scene._bw_place_block(self, "
            f"getattr(self, {block_raw!r}, {block_raw!r}), {reach})")

def _cg_break_block(gen, params, event_type):
    from export.Kivy.code_generator import _tofloat
    reach = int(_tofloat(params.get('reach', 5), 5))
    return f"self.scene._bw_break_block(self, {reach})"

def _cg_load_block_world(gen, params, event_type):
    data_file = str(params.get('data_file', ''))
    if not data_file:
        return "pass  # load_block_world: no data_file"
    files = getattr(gen, 'extension_data', {}) or {}
    block_list = files.get('block_world_files', {}).get(data_file)
    if block_list is None:
        return f"pass  # load_block_world: {data_file!r} not found at export time"
    return f"self.scene._bw_load_block_world({block_list!r})"

def _cg_draw_block_world_hud(gen, params, event_type):
    from export.Kivy.code_generator import _num_code
    def _s(key, default):
        return str(params.get(key, default))
    return (
        "self._draw_queue.extend(self.scene._bw_build_hud_commands("
        "getattr(self, 'hotbar_index', 0), "
        f"{_num_code(params.get('slot_size', 40), 40)}, "
        f"{_num_code(params.get('gap', 6), 6)}, "
        f"{_num_code(params.get('margin_bottom', 16), 16)}, "
        f"{_s('back_color', '#202020')!r}, {_s('border_color', '#ffffff')!r}, "
        f"{_s('selected_color', '#ffd040')!r}, {_s('text_color', '#ffffff')!r}, "
        f"{_num_code(params.get('crosshair_size', 12), 12)}, "
        f"{_s('crosshair_color', '#ffffff')!r}))"
    )


ACTION_CODEGEN = {
    'enable_block_world_view': _cg_enable_block_world_view,
    'place_block': _cg_place_block,
    'break_block': _cg_break_block,
    'select_hotbar_slot': _cg_select_hotbar_slot,
    'move_and_collide': _cg_move_and_collide,
    'draw_block_world_hud': _cg_draw_block_world_hud,
    'load_block_world': _cg_load_block_world,
    'set_look_pitch': _cg_set_look_pitch,
}
