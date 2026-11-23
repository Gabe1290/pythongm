"""Kivy export contribution of the raycast 2.5D extension (Stage C2b).

SCENE_CODE is class-body Python (4-space-indented methods) that
KivyExporter._inject_extension_scene_code drops into every generated scene
class at its __PYGM_EXTENSION_SCENE_CODE__ marker, AFTER .format() -- so the
{ } dict/set literals here are single, not doubled. It overrides the scene's
no-op _init_extensions / _render_extension_overlay dispatchers (by adding _ext_init__ / _ext_overlay__ methods) and carries the DDA
renderer, a faithful port of extensions/raycast_2_5d/renderer.py. Numeric
parity with desktop + HTML5 is pinned by tests/test_raycast_export_parity.py.
"""

SCENE_CODE = '''\n    def _ext_init__raycast_2_5d(self):
        # Per-scene raycast state (was in the scene __init__ before Stage C2b).
        self.raycast_camera = None
        self._raycast_group = None
        self._raycast_v_walls = None
        self._raycast_cell_size = None
        self._raycast_tex_cache = {}
        self._raycast_px_cache = {}
        # Visited grid cells, for draw_minimap's opt-in breadcrumb trail.
        self._raycast_trail = set()
        # Stairs (docs/RAYCAST_STAIRS_PLAN.md, S11): the floor-height map,
        # the climbing snapshot and the eased view height.
        self._raycast_floor_heights = {}
        self._raycast_ceiling_heights = {}      # lowered ceilings (ceilings plan, C8)
        self._raycast_step_prev = None
        self._raycast_eye_floor = None
        self._raycast_eye_vz = 0.0

    def _raycast_go_seamless(self, room_name, marker_name):
        # Go to Room Seamlessly (teleport.request, ceilings plan T1/T2): record the
        # arrival on the game app, then an ordinary instant room change. The offset
        # is measured in GM y-down space so rooms of different heights agree.
        from main import get_game_app, goto_room, ROOM_ORDER
        app = get_game_app()
        if app is None or room_name not in ROOM_ORDER:
            return
        cfg = getattr(self, 'raycast_camera', None)
        camera = self._find_raycast_camera(cfg) if cfg and cfg.get('enabled') else None
        marker = None
        for inst in self.instances:
            if marker_name and getattr(inst, 'object_name', None) == marker_name:
                marker = inst
                break
        arrival = None
        if getattr(self, 'room_name', None) == room_name:
            print('go_to_room_seamlessly: already in room ' + room_name + '; changing room normally')
        elif camera is None:
            print('go_to_room_seamlessly: no raycast camera in this room; changing room normally')
        elif marker is None:
            print('go_to_room_seamlessly: no ' + str(marker_name) + ' object in this room; changing room normally')
        else:
            cx, cy = self._raycast_gm_xy(camera)
            mx, my = self._raycast_gm_xy(marker)
            arrival = {'from_scene': self, 'to': room_name, 'marker': marker_name,
                       'dx': cx - mx, 'dy': cy - my,
                       'facing': float(getattr(camera, 'facing_angle', 0.0)),
                       'hspeed': getattr(camera, 'hspeed', 0.0),
                       'vspeed': getattr(camera, 'vspeed', 0.0),
                       'eye_floor': self._raycast_eye_floor, 'eye_vz': self._raycast_eye_vz}
        app._raycast_arrival = arrival
        goto_room(room_name, 'none')

    def _raycast_apply_arrival(self):
        # Apply a pending arrival to THIS scene (the new room), before its frame is
        # drawn: the scene constructor already renders the first overlay frame after
        # the create events, and calls this hook first, so the carried values replace
        # what the camera's Create event set and no frame shows the authored start.
        try:
            from main import get_game_app
            app = get_game_app()
        except Exception:
            return
        arrival = getattr(app, '_raycast_arrival', None)
        if not arrival or arrival['from_scene'] is self:
            return
        app._raycast_arrival = None
        if getattr(self, 'room_name', None) != arrival['to']:
            return
        cfg = getattr(self, 'raycast_camera', None)
        camera = self._find_raycast_camera(cfg) if cfg and cfg.get('enabled') else None
        marker = None
        for inst in self.instances:
            if getattr(inst, 'object_name', None) == arrival['marker']:
                marker = inst
                break
        if camera is None:
            print('go_to_room_seamlessly: the new room has no raycast camera')
            return
        if marker is None:
            print('go_to_room_seamlessly: no ' + str(arrival['marker']) + ' object in room '
                  + str(arrival['to']) + '; arriving at its start')
            return
        mx, my = self._raycast_gm_xy(marker)
        ih = float(getattr(camera, 'image_height', 0) or 0)
        camera.x = mx + arrival['dx']
        camera.y = self.room_height - (my + arrival['dy']) - ih
        camera.facing_angle = arrival['facing']
        camera.hspeed = arrival['hspeed']
        camera.vspeed = arrival['vspeed']
        if arrival['eye_floor'] is not None:
            self._raycast_eye_floor = arrival['eye_floor']
            self._raycast_eye_vz = arrival['eye_vz']

    def _ext_overlay__raycast_2_5d(self):
        # Claim the frame when the raycast camera is enabled; the scene then
        # composites the HUD over this opaque overlay. Returns True if drawn.
        self._raycast_apply_arrival()
        if getattr(self, 'raycast_camera', None) and self.raycast_camera.get('enabled'):
            self._render_raycast()
            return True
        return False

    # ------------------------------------------------------------------
    # Raycast (Doom-style first-person) rendering — a faithful port of
    # runtime/game_runner.py's _build_raycast_walls / _cast_ray /
    # _render_raycast_view (see docs/RAYCAST_2_5D_PLAN.md). The desktop
    # renderer works in GameMaker y-DOWN room coordinates; Kivy instance
    # positions are y-UP (self.x/self.y are the sprite's Kivy bottom-left).
    # To reuse the desktop math verbatim (wall-key derivation, camera
    # centering, tex_u, facing_angle) we convert each instance BACK to GM
    # y-down space here, run the identical DDA, and only flip at the final
    # screen draw — which is vertically SYMMETRIC for wall strips (centered
    # on the horizon), so the sole visible difference is that the ceiling
    # fill sits in the TOP (high-y) half in Kivy and the floor in the
    # bottom half. This is unit 4b: walls only; sky/floor/billboards land
    # in unit 5.
    # ------------------------------------------------------------------
    def _raycast_gm_xy(self, inst):
        """(gm_x, gm_y) top-left of inst in GameMaker y-down room space —
        the inverse of the y-up conversion done at instance creation."""
        h = float(getattr(inst, 'image_height', 0) or 0)
        return float(inst.x), self.room_height - float(inst.y) - h

    def _build_raycast_walls(self, cell_size):
        """Derive thin wall EDGES from every solid instance (port of the
        desktop method of the same name). v_walls holds (line_x, row);
        h_walls holds (col, line_y). Parallel *_sprites dicts remember which
        instance's sprite made each edge (last writer wins)."""
        v_walls = set()
        h_walls = set()
        v_sprites = {}
        h_sprites = {}
        for inst in self.instances:
            if not getattr(inst, 'solid', False):
                continue
            width = float(getattr(inst, 'image_width', 0) or 0)
            height = float(getattr(inst, 'image_height', 0) or 0)
            if width <= 0 or height <= 0:
                continue
            gm_x, gm_y = self._raycast_gm_xy(inst)
            spr = getattr(inst, 'sprite_name', None)
            if width >= height * 1.5:
                line_y = round((gm_y + height / 2) / cell_size)
                col = int(gm_x // cell_size)
                h_walls.add((col, line_y))
                h_sprites[(col, line_y)] = spr
            elif height >= width * 1.5:
                line_x = round((gm_x + width / 2) / cell_size)
                row = int(gm_y // cell_size)
                v_walls.add((line_x, row))
                v_sprites[(line_x, row)] = spr
            else:
                gx = int(gm_x // cell_size)
                gy = int(gm_y // cell_size)
                v_walls.add((gx, gy))
                v_walls.add((gx + 1, gy))
                h_walls.add((gx, gy))
                h_walls.add((gx, gy + 1))
                for key in ((gx, gy), (gx + 1, gy)):
                    v_sprites[key] = spr
                for key in ((gx, gy), (gx, gy + 1)):
                    h_sprites[key] = spr
        self._raycast_v_walls = v_walls
        self._raycast_h_walls = h_walls
        self._raycast_v_wall_sprites = v_sprites
        self._raycast_h_wall_sprites = h_sprites
        self._raycast_cell_size = cell_size

    def _cast_ray(self, px, py, angle_rad, cell_size, max_cells):
        """DDA raycast in GM y-down pixel space (port of the desktop
        _cast_ray). Returns (distance_px, side, hit, tex_u, sprite_name)."""
        import math
        px_cell, py_cell = px / cell_size, py / cell_size
        dx, dy = math.cos(angle_rad), math.sin(angle_rad)
        map_x, map_y = int(px_cell), int(py_cell)
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
        side = 0
        dist_cells = float(max_cells)
        for _ in range(max_cells):
            if side_x < side_y:
                side_x += delta_x
                map_x += step_x
                side = 0
                line_x = map_x if step_x > 0 else map_x + 1
                wall_key = (line_x, map_y)
                hit = wall_key in self._raycast_v_walls
            else:
                side_y += delta_y
                map_y += step_y
                side = 1
                line_y = map_y if step_y > 0 else map_y + 1
                wall_key = (map_x, line_y)
                hit = wall_key in self._raycast_h_walls
            if hit:
                dist_cells = (side_x - delta_x) if side == 0 else (side_y - delta_y)
                if side == 0:
                    wall_coord = py_cell + dist_cells * dy
                    if dx > 0:
                        wall_coord = -wall_coord
                    sprite = self._raycast_v_wall_sprites.get(wall_key)
                else:
                    wall_coord = px_cell + dist_cells * dx
                    if dy < 0:
                        wall_coord = -wall_coord
                    sprite = self._raycast_h_wall_sprites.get(wall_key)
                tex_u = wall_coord - math.floor(wall_coord)
                return max(dist_cells, 1e-4) * cell_size, side, True, tex_u, sprite
        return max(dist_cells, 1e-4) * cell_size, side, False, 0.0, None

    # Wall shading model — MUST match game_runner.GameRoom._wall_shade and
    # engine.js wallShade (pinned by tests/test_raycast_export_parity.py).
    # A subtle side hint + distance falloff; the old binary half-brightness
    # y-face made h/v junctions at equal distance read as false corners.
    RAYCAST_SIDE_SHADE = 0.85
    RAYCAST_FOG_STRENGTH = 0.55
    RAYCAST_MIN_SHADE = 0.35
    RAYCAST_WALL_HEIGHT = 1.5    # walls project 1.5x taller than a cube (walls
                                 # only, not billboards); see game_runner
    # The vertical model (renderer.py, stairs plan S4), in grid cells: eye
    # RAYCAST_EYE_HEIGHT above the floor; walls + ceiling rise to the camera's
    # wall_height (default RAYCAST_WALL_HEIGHT); a wall texture covers
    # RAYCAST_TEXTURE_HEIGHT and repeats above that, anchored at the floor.
    RAYCAST_EYE_HEIGHT = 0.75
    RAYCAST_TEXTURE_HEIGHT = 1.5
    RAYCAST_EYE_FROM_TILE_TOP = (RAYCAST_TEXTURE_HEIGHT - RAYCAST_EYE_HEIGHT) / RAYCAST_TEXTURE_HEIGHT
    RAYCAST_MIN_WALL_HEIGHT = 1.0
    RAYCAST_MAX_WALL_HEIGHT = 10.0
    # Stairs (heights.py / climbing.py): ceiling margin, default max step,
    # view climb speed and fall gravity -- pinned against the desktop values.
    RAYCAST_CEILING_MARGIN = 4.0
    RAYCAST_DEFAULT_MAX_STEP = 12.0
    RAYCAST_CLIMB_SPEED = 2.0
    RAYCAST_FALL_GRAVITY = 0.6

    @classmethod
    def _clamp_wall_height(cls, value):
        """wall_height in cells, defaulted and clamped (renderer.clamp_wall_height)."""
        try:
            v = float(value)
        except (TypeError, ValueError):
            return cls.RAYCAST_WALL_HEIGHT
        if v != v:
            return cls.RAYCAST_WALL_HEIGHT
        return min(cls.RAYCAST_MAX_WALL_HEIGHT, max(cls.RAYCAST_MIN_WALL_HEIGHT, v))

    @classmethod
    def _wall_shade(cls, side, corrected, max_dist):
        """Brightness multiplier in [MIN_SHADE, 1] for a wall strip."""
        side_factor = cls.RAYCAST_SIDE_SHADE if side == 1 else 1.0
        t = corrected / max_dist if max_dist > 0 else 0.0
        if t < 0.0:
            t = 0.0
        elif t > 1.0:
            t = 1.0
        dist_factor = 1.0 - cls.RAYCAST_FOG_STRENGTH * t
        return max(cls.RAYCAST_MIN_SHADE, side_factor * dist_factor)

    def _raycast_color(self, spec, default):
        """Parse a '#rrggbb' color to an (r, g, b) float triple in 0..1."""
        try:
            s = str(spec or default).lstrip('#')
            if len(s) == 3:
                s = ''.join(c * 2 for c in s)
            r = int(s[0:2], 16) / 255.0
            g = int(s[2:4], 16) / 255.0
            b = int(s[4:6], 16) / 255.0
            return (r, g, b)
        except Exception:
            s = default.lstrip('#')
            return (int(s[0:2], 16) / 255.0, int(s[2:4], 16) / 255.0,
                    int(s[4:6], 16) / 255.0)

    def _raycast_texture(self, sprite_name):
        """Kivy texture for a sprite NAME (cached), via SPRITE_PATHS."""
        if not sprite_name:
            return None
        cache = getattr(self, '_raycast_tex_cache', None)
        if cache is None:
            cache = {}
            self._raycast_tex_cache = cache
        if sprite_name in cache:
            return cache[sprite_name]
        tex = None
        path = SPRITE_PATHS.get(sprite_name, '')
        if path:
            img = load_image(path)
            if img is not None:
                tex = img.texture
        cache[sprite_name] = tex
        return tex

    def _find_raycast_camera(self, cfg):
        """The camera instance: the one stored on the config
        (camera_instance=self from enable_raycast_view with no named target)
        if still alive, else the first live instance of camera_object."""
        cam = cfg.get('camera_instance')
        if cam is not None and cam in self.instances \\
                and cam not in self.instances_to_destroy:
            return cam
        name = cfg.get('camera_object', '')
        return self._find_view_target(name) if name else None

    def _billboard_texture(self, inst, frame_idx=None):
        """Current-frame texture for a billboard instance (or None).

        frame_idx overrides the normal animated image_index frame — passed
        by the billboard loop below when the instance has
        billboard_rotation_frames set (rotation-by-viewing-angle, picked by
        _billboard_rotation_frame)."""
        tex = getattr(inst, '_sprite_texture', None)
        if tex is None:
            return self._raycast_texture(getattr(inst, 'sprite_name', None))
        frames = int(getattr(inst, '_sprite_frames', 1) or 1)
        if frames > 1:
            fw = int(getattr(inst, '_frame_w', 0) or tex.width)
            fh = int(getattr(inst, '_frame_h', 0) or tex.height)
            idx = int(getattr(inst, 'image_index', 0)) if frame_idx is None else frame_idx
            idx = idx % frames
            return tex.get_region(idx * fw, 0, fw, fh)
        return tex

    @staticmethod
    def _billboard_rotation_frame(bx, by, facing_angle_deg, cam_x, cam_y, frames):
        """Port of renderer.billboard_rotation_frame — see its docstring.
        Numerically pinned against the desktop function by
        tests/test_raycast_export_parity.py."""
        import math
        if frames <= 1:
            return 0
        facing_rad = math.radians(-facing_angle_deg)
        view_rad = math.atan2(cam_y - by, cam_x - bx)
        rel = (view_rad - facing_rad) % (2 * math.pi)
        step = (2 * math.pi) / frames
        return int(round(rel / step)) % frames

    def _raycast_texture_pixels(self, name):
        """(rgba_bytes, tw, th) for a floor/ceiling sprite NAME (cached), for
        per-pixel floor casting. Kivy texture.pixels are bottom-up (GL order);
        the caster flips the row to match the desktop's top-down sampling."""
        if not name:
            return None
        cache = self._raycast_px_cache
        if name in cache:
            return cache[name]
        result = None
        tex = self._raycast_texture(name)
        if tex is not None:
            try:
                result = (tex.pixels, int(tex.width), int(tex.height))
            except Exception:
                result = None
        cache[name] = result
        return result

    def _floor_buffer(self, pixels, tw, th, res, facing_screen_rad, fov_rad,
                      cam_cx, cam_cy, view_h=None, plane_height=None):
        """Faithful port of _cast_floor_plane's cast into an RGBA byte buffer
        (returns buf, sw, sh). Camera-plane FOV-edge rays interpolated across
        columns; row distance plane_height*view_h/(y-horizon), plane_height =
        the plane's distance from the eye in cells (default the eye height,
        i.e. the floor); texture tiled per grid cell. `pixels` is bottom-up (Kivy), so the source row is flipped to
        sample the tile the same way the desktop's top-down get_at does.

        view_h is the DOOM-bar letterbox height (the floor band is view_h/2
        tall and the projection reference is plane_height*view_h); None = full height."""
        import math
        w = float(self.display_width)
        h = float(self.display_height)
        if view_h is None:
            view_h = h
        view_h = max(1.0, min(float(view_h), h))
        half_h = int(view_h // 2)
        region_h = int(view_h) - half_h
        sw = max(1, int(w) // res)
        sh = max(1, region_h // res)
        out = bytearray(sw * sh * 4)
        dir_x, dir_y = math.cos(facing_screen_rad), math.sin(facing_screen_rad)
        plane = math.tan(fov_rad / 2)
        plane_x, plane_y = -dir_y * plane, dir_x * plane
        rdx0, rdy0 = dir_x - plane_x, dir_y - plane_y
        rdx1, rdy1 = dir_x + plane_x, dir_y + plane_y
        # Matches the wall pass (desktop cast_floor_plane; stairs plan F1/S4).
        if plane_height is None:
            plane_height = self.RAYCAST_EYE_HEIGHT
        pos_z = plane_height * view_h
        step_scale = res / w
        floor = math.floor
        for j in range(sh):
            y = half_h + j * res
            p = y - half_h
            if p <= 0:
                p = 1
            rowd = pos_z / p
            stepx = rowd * (rdx1 - rdx0) * step_scale
            stepy = rowd * (rdy1 - rdy0) * step_scale
            fx = cam_cx + rowd * rdx0
            fy = cam_cy + rowd * rdy0
            di = j * sw * 4
            for _ in range(sw):
                tx = int(tw * (fx - floor(fx)))
                ty = int(th * (fy - floor(fy)))
                if tx >= tw:
                    tx = tw - 1
                if ty >= th:
                    ty = th - 1
                si = ((th - 1 - ty) * tw + tx) * 4   # flip row: Kivy px are bottom-up
                out[di] = pixels[si]; out[di + 1] = pixels[si + 1]
                out[di + 2] = pixels[si + 2]; out[di + 3] = 255
                di += 4
                fx += stepx
                fy += stepy
        return bytes(out), sw, sh

    def _render_floor_plane(self, group, px, res, facing_screen_rad, fov_rad,
                            cam_cx, cam_cy, w, h, ceiling, view_h=None,
                            plane_height=None):
        """Cast the floor (or, if `ceiling`, the top half) into a low-res
        Texture and add it to the overlay, GPU-upscaled to the region. Kivy is
        y-up: the floor is the BOTTOM half of the view and the cast buffer's
        horizon row (row 0) must sit at the TOP of that region (adjacent to the
        centre), so the tex_coords flip v; the ceiling mirrors it.

        view_h is the DOOM-bar letterbox height: the region is view_h/2 tall,
        the floor sits just above the reserved band at y = h - view_h, and the
        ceiling's top edge is the window top. None = full height."""
        from kivy.graphics.texture import Texture   # local import: keeps the
        # scene module importable under stubs that don't provide this submodule
        if view_h is None:
            view_h = h
        view_h = max(1.0, min(float(view_h), h))
        buf, sw, sh = self._floor_buffer(px[0], px[1], px[2], res,
                                         facing_screen_rad, fov_rad, cam_cx,
                                         cam_cy, view_h, plane_height)
        tex = Texture.create(size=(sw, sh), colorfmt='rgba')
        tex.blit_buffer(buf, colorfmt='rgba', bufferfmt='ubyte')
        region_h = view_h / 2.0
        group.add(Color(1, 1, 1, 1))
        if ceiling:
            group.add(Rectangle(texture=tex, pos=(0, h - region_h),
                                size=(w, region_h),
                                tex_coords=(0, 0, 1, 0, 1, 1, 0, 1)))
        else:
            group.add(Rectangle(texture=tex, pos=(0, h - view_h),
                                size=(w, region_h),
                                tex_coords=(0, 1, 1, 1, 1, 0, 0, 0)))

    def _render_raycast(self):
        """Draw the first-person view as an opaque overlay: flat ceiling/floor
        fills, a panning sky panorama over the ceiling, low-res textured floor
        (and indoor ceiling) casting, textured/flat wall strips, then
        camera-facing billboard sprites with per-column occlusion (units 4b +
        5). A faithful port of game_runner._render_raycast_view. Runs each frame
        from _update_impl when raycast_camera is enabled."""
        import math
        cfg = self.raycast_camera
        if not cfg or not cfg.get('enabled'):
            if getattr(self, '_raycast_group', None) is not None:
                self._raycast_group.clear()
            return
        # Lazy-build the overlay instruction group once, on canvas.after so it
        # sits ON TOP of the normal top-down widgets (which we simply paint
        # over — the raycast view is opaque edge to edge).
        if getattr(self, '_raycast_group', None) is None:
            self._raycast_group = InstructionGroup()
            self.canvas.after.add(self._raycast_group)

        cell_size = int(cfg.get('cell_size', 32))
        wall_h = self._clamp_wall_height(cfg.get('wall_height', self.RAYCAST_WALL_HEIGHT))
        wall_tiles = wall_h / self.RAYCAST_TEXTURE_HEIGHT   # 1.0 for default walls
        n_tiles = max(1, int(math.ceil(wall_tiles - 1e-9)))
        # Rebuilt every frame (parity with the desktop renderer.py fix,
        # 2026-10-06) so a solid instance created/destroyed at runtime shows
        # up immediately instead of only on room re-entry/cell_size change.
        self._build_raycast_walls(cell_size)
        # Stairs (S11): the floor-height map, rebuilt every frame like the
        # walls. Empty -> the single-hit path below, unchanged.
        heights, step_textures = self._raycast_build_floor_heights(
            cell_size, self._raycast_max_floor_height(cell_size, wall_h))
        # Lowered ceilings (ceilings plan, C3/C8): also rebuilt every frame; a
        # non-empty map takes the two-clip column walk even without steps.
        ceilings, ceiling_textures = self._raycast_build_ceiling_heights(
            cell_size, wall_h * cell_size, heights,
            self.RAYCAST_EYE_HEIGHT * cell_size)
        stairs = bool(heights) or bool(ceilings)

        w = float(self.display_width)
        h = float(self.display_height)
        # DOOM-bar letterbox. Kivy is y-UP, so the 3D view occupies the TOP
        # view_h px (y in [view_bottom, h]) and the reserved status-bar band is
        # at the BOTTOM (y in [0, view_bottom)) — the inverse of desktop/HTML5.
        # mid is the horizon; view_h 0 => full height, existing games unchanged.
        # (game_runner.py _render_raycast_view is the reference.)
        view_h = float(int(cfg.get('viewport_height', 0)) or h)
        view_h = max(1.0, min(view_h, h))
        view_bottom = h - view_h
        mid = h - view_h / 2.0          # horizon (was h/2 at full height)
        group = self._raycast_group
        group.clear()

        ceiling_color = self._raycast_color(cfg.get('ceiling_color'), '87CEEB')
        floor_color = self._raycast_color(cfg.get('floor_color'), '464632')
        # Flat fills: ceiling is the TOP half of the view (y in [mid, h]), floor
        # the bottom half of the view (y in [view_bottom, mid]).
        group.add(Color(*ceiling_color, 1))
        group.add(Rectangle(pos=(0, mid), size=(w, h - mid)))
        group.add(Color(*floor_color, 1))
        group.add(Rectangle(pos=(0, view_bottom), size=(w, mid - view_bottom)))
        # Reserved DOOM-bar band at the bottom, opaque black, before the
        # per-instance draw pass composites the bar over it. No-op at full height.
        if view_bottom > 0:
            group.add(Color(0, 0, 0, 1))
            group.add(Rectangle(pos=(0, 0), size=(w, view_bottom)))

        camera = self._find_raycast_camera(cfg)
        if camera is None:
            return  # flat floor/ceiling only

        gm_x, gm_y = self._raycast_gm_xy(camera)
        cam_x = gm_x + float(getattr(camera, 'image_width', 0) or 0) / 2.0
        cam_y = gm_y + float(getattr(camera, 'image_height', 0) or 0) / 2.0
        # Eye height (room px): the floor under the camera (eased by the
        # climbing hook) plus the eye height.
        floor_z = 0.0
        if stairs:
            floor_z = self._raycast_eye_floor
            if floor_z is None:
                floor_z = heights.get((int(cam_x // cell_size), int(cam_y // cell_size)), 0.0)
        eye_z = floor_z + self.RAYCAST_EYE_HEIGHT * cell_size
        eye_cells = eye_z / cell_size

        wall_color = self._raycast_color(cfg.get('wall_color'), '993333')
        fov_deg = float(cfg.get('fov', 66))
        fov_rad = math.radians(fov_deg)
        render_distance_cells = int(cfg.get('render_distance', 20))
        num_columns = int(cfg.get('columns', 0)) or int(min(w, 320))
        num_columns = max(1, num_columns)
        col_width = w / num_columns

        facing_screen_rad = math.radians(-float(getattr(camera, 'facing_angle', 0)))

        textured = bool(cfg.get('wall_textured', True))
        wall_texture = self._raycast_texture(cfg.get('wall_texture', ''))

        # Sky panorama over the ceiling (drawn UNDER the walls, which occlude
        # it for free). Treated as infinitely far: it pans with facing_angle
        # rather than receding with distance (a 360deg turn pans the full
        # panorama exactly once). Kivy y-up -> the ceiling band is the TOP half
        # (y in [half_h, h]). Absent sky_texture -> the flat ceiling fill above
        # stands. (Port of _render_raycast_view's Phase 5b sky.)
        facing_angle = float(getattr(camera, 'facing_angle', 0))
        sky_tex = self._raycast_texture(cfg.get('sky_texture', ''))
        if sky_tex is not None and h > 0:
            pano_w = max(1, int(w * 360.0 / max(1.0, fov_deg)))
            ceil_h = h - mid
            pan = int((facing_angle % 360) / 360.0 * pano_w)
            group.add(Color(1, 1, 1, 1))
            group.add(Rectangle(texture=sky_tex, pos=(-pan, mid),
                                size=(pano_w, ceil_h)))
            if pano_w - pan < w:
                group.add(Rectangle(texture=sky_tex, pos=(pano_w - pan, mid),
                                    size=(pano_w, ceil_h)))

        # Floor (and, when no sky claimed it, ceiling) texture casting — a
        # low-res per-pixel cast + GPU upscale (port of _cast_floor_plane).
        # res from cfg.floor_cast_res (default 4, desktop parity; the timing
        # spike measured res=4 naive at ~5ms on an AMD 840M). Drawn UNDER the
        # walls so they occlude it; absent floor_texture leaves the flat fill.
        cast_res = max(1, int(cfg.get('floor_cast_res', 4)))
        cam_cx, cam_cy = cam_x / cell_size, cam_y / cell_size
        floor_px = self._raycast_texture_pixels(cfg.get('floor_texture', ''))
        if floor_px is not None and not stairs:    # stairs: _stairs_floor below
            self._render_floor_plane(group, floor_px, cast_res, facing_screen_rad,
                                     fov_rad, cam_cx, cam_cy, w, h, False, view_h)
        ceil_name = cfg.get('ceiling_texture', '')
        if ceil_name and sky_tex is None:
            ceil_px = self._raycast_texture_pixels(ceil_name)
            if ceil_px is not None:
                # The ceiling plane is the top of the walls: (wall_h - eye)
                # above the eye.
                self._render_floor_plane(group, ceil_px, cast_res, facing_screen_rad,
                                         fov_rad, cam_cx, cam_cy, w, h, True, view_h,
                                         (wall_h - eye_cells) if stairs
                                         else wall_h - self.RAYCAST_EYE_HEIGHT)

        # CAMERA-PLANE projection (not uniform-angle) — screen columns are
        # evenly spaced, so rays must be evenly spaced on the camera plane:
        # ray_dir = dir + plane * camera_x, i.e. the off-centre angle is
        # atan(tan(fov/2) * camera_x), NOT a linear ramp. Uniform-angle sampling
        # drawn at uniform screen x isn't a perspective projection and BENDS
        # straight walls. Matches game_runner and the floor cast.
        plane_tan = math.tan(fov_rad / 2)
        # Fisheye-corrected wall distance per screen column, for billboard
        # occlusion below (Infinity where a column saw no wall).
        col_wall_dist = [float('inf')] * num_columns
        stairs_layouts = []
        half_h = view_h / 2.0               # y-DOWN rows inside the view

        for col in range(num_columns):
            camera_x = 2.0 * (col + 0.5) / num_columns - 1.0
            ray_offset = math.atan(plane_tan * camera_x)
            ray_angle = facing_screen_rad + ray_offset
            if stairs:
                if ceilings:                 # lowered ceilings: the two-clip walk
                    crossings, hit_s = self._cast_ray_steps(
                        cam_x, cam_y, ray_angle, cell_size, render_distance_cells,
                        heights, ceilings)
                    cam_cell = (int(cam_x // cell_size), int(cam_y // cell_size))
                    lay = self._layout_column_ceilings(
                        crossings, hit_s, floor_z, ceilings.get(cam_cell), eye_z,
                        wall_h * cell_size, cell_size, math.cos(ray_offset), half_h,
                        view_h, render_distance_cells)
                else:
                    crossings, hit_s = self._cast_ray_steps(
                        cam_x, cam_y, ray_angle, cell_size, render_distance_cells, heights)
                    lay = self._layout_column(crossings, hit_s, floor_z, eye_z,
                                              wall_h * cell_size, cell_size,
                                              math.cos(ray_offset), half_h, view_h,
                                              render_distance_cells)
                stairs_layouts.append(lay)
                col_wall_dist[col] = lay['wall_dist']
                continue
            dist, side, hit, tex_u, wall_sprite = self._cast_ray(
                cam_x, cam_y, ray_angle, cell_size, render_distance_cells)
            if not hit:
                continue
            corrected = dist * math.cos(ray_offset)
            col_wall_dist[col] = corrected
            # TRUE (unclamped) height; the TEXTURE is CROPPED to the visible
            # span rather than the whole texture being squeezed into a
            # screen-clamped strip — the real "bent wall" bug (close columns
            # clamped and compressed the whole brick texture while farther ones
            # didn't, breaking the courses across a flat wall).
            # tile_h: one texture tile's projected height (the whole wall for
            # the default wall_height). y-up: y_bot is the wall's bottom; tiles
            # stack UPWARD from it, the wall's real top is wall_tiles tiles up.
            tile_h = view_h * cell_size * self.RAYCAST_TEXTURE_HEIGHT / max(corrected, 1e-4)
            y_bot = mid - tile_h * self.RAYCAST_EYE_FROM_TILE_TOP
            y_wall_top = y_bot + wall_tiles * tile_h
            x0 = int(col * col_width)
            x1 = int((col + 1) * col_width)
            strip_w = max(1, x1 - x0)
            # Clamp to the VIEW bottom, not the window bottom, so a close wall
            # never paints down into the reserved status-bar band.
            y0 = max(view_bottom, y_bot)
            y1 = min(h, y_wall_top)
            vis_h = y1 - y0
            if vis_h <= 0:
                continue

            # Subtle side hint + distance falloff (see _wall_shade).
            shade = self._wall_shade(side, corrected,
                                     render_distance_cells * cell_size)
            tex = wall_texture if wall_texture is not None \\
                else self._raycast_texture(wall_sprite)
            if textured and tex is not None:
                tw = tex.width; th = tex.height
                tex_x = min(tw - 1, max(0, int(tex_u * tw)))
                # Take the FULL-height 1-px column and select the visible slice
                # with FLOAT tex_coords instead of an integer get_region crop.
                # get_region snaps to whole texels, and on a close wall one
                # texel spans tens of screen px, so per-column snapping produced
                # jagged edges. tex_coords are sub-texel exact. Kivy textures
                # are bottom-origin and y0/y_bot are too, so v maps directly.
                region = tex.get_region(tex_x, 0, 1, th)
                group.add(Color(shade, shade, shade, 1))
                # One Rectangle per texture tile, bottom tile first; the top
                # tile is cut at the wall's real top.
                for k in range(n_tiles):
                    seg_bot = y_bot + k * tile_h
                    sy0 = max(view_bottom, seg_bot)
                    sy1 = min(h, seg_bot + tile_h, y_wall_top)
                    if sy1 - sy0 <= 0:
                        continue
                    v0 = (sy0 - seg_bot) / tile_h
                    v1 = (sy1 - seg_bot) / tile_h
                    group.add(Rectangle(texture=region, pos=(x0, sy0),
                                        size=(strip_w, sy1 - sy0),
                                        tex_coords=(0.0, v0, 1.0, v0,
                                                    1.0, v1, 0.0, v1)))
            else:
                color = tuple(c * shade for c in wall_color)
                group.add(Color(*color, 1))
                group.add(Rectangle(pos=(x0, y0), size=(strip_w, vis_h)))

        # Billboard sprites (port of the desktop Phase 6 pass): every visible,
        # non-solid, sprited instance draws as a camera-facing sprite, scaled by
        # distance and centered on the horizon like a wall strip, farthest-first
        # (painter's algorithm). Real per-column occlusion against col_wall_dist
        # hides a billboard behind a wall and clips one behind a corner.
        if stairs:
            # Floor cast (textured floor or a step top texture), then risers
            # and walls at full resolution on top (renderer.py, S5/S6).
            top_px = {}
            for cell, (top_name, _side) in step_textures.items():
                px_ = self._raycast_texture_pixels(top_name) if top_name else None
                if px_ is not None:
                    top_px[cell] = px_
            floor_cast = floor_px is not None or bool(top_px)
            sf = {'eye_z': eye_z, 'cell_size': cell_size, 'half_h': half_h,
                  'view_h': view_h, 'h': h, 'w': w, 'col_width': col_width,
                  'cam_x': cam_x, 'cam_y': cam_y, 'textured': textured,
                  'wall_texture': wall_texture, 'wall_color': wall_color,
                  'floor_color': floor_color, 'step_textures': step_textures,
                  'max_dist': render_distance_cells * cell_size,
                  'wall_top_z': wall_h * cell_size, 'ceiling_color': ceiling_color}
            if floor_cast:
                self._stairs_floor(group, stairs_layouts, sf, floor_px, top_px,
                                   facing_screen_rad, fov_rad, cast_res)
            # Lowered ceilings (C4/C8): cast textured when the camera or any
            # marker has a ceiling texture; otherwise their spans stay crisp flat
            # fills.
            cell_ceil_px = {}
            for cell, tex_name in ceiling_textures.items():
                px_ = self._raycast_texture_pixels(tex_name) if tex_name else None
                if px_ is not None:
                    cell_ceil_px[cell] = px_
            ceil_default_px = self._raycast_texture_pixels(ceil_name) if ceil_name else None
            ceiling_cast = bool(ceilings) and (bool(cell_ceil_px) or ceil_default_px is not None)
            if ceiling_cast:
                self._stairs_ceiling(group, stairs_layouts, sf, cell_ceil_px, ceil_default_px,
                                     facing_screen_rad, fov_rad, cast_res)
            for col, lay in enumerate(stairs_layouts):
                self._draw_stairs_column(group, sf, col, lay, floor_cast, ceiling_cast)

        billboards = []
        for inst in self.instances:
            if inst is camera or not getattr(inst, 'visible', True):
                continue
            if getattr(inst, 'solid', False):
                continue
            if getattr(inst, 'raycast_floor_height', None) is not None:
                continue        # a step is floor, not a cutout
            if getattr(inst, 'raycast_ceiling_height', None) is not None:
                continue        # so is a ceiling marker
            iw = float(getattr(inst, 'image_width', 0) or 0)
            ih = float(getattr(inst, 'image_height', 0) or 0)
            if iw <= 0 or ih <= 0:
                continue
            b_gm_x, b_gm_y = self._raycast_gm_xy(inst)
            bx = b_gm_x + iw / 2.0
            by = b_gm_y + ih / 2.0
            dxb, dyb = bx - cam_x, by - cam_y
            dist_b = math.hypot(dxb, dyb)
            if dist_b < 1e-4:
                continue
            rel_angle = math.atan2(dyb, dxb) - facing_screen_rad
            rel_angle = (rel_angle + math.pi) % (2 * math.pi) - math.pi
            if abs(rel_angle) > fov_rad / 2 + 0.5:   # margin for sprite width
                continue
            corrected_b = dist_b * math.cos(rel_angle)
            if corrected_b <= 1e-4:
                continue
            billboards.append((corrected_b, rel_angle, inst, iw, ih, bx, by))

        billboards.sort(key=lambda b: -b[0])
        for corrected_b, rel_angle, inst, iw, ih, bx, by in billboards:
            rot_frames = int(getattr(inst, 'billboard_rotation_frames', 0) or 0)
            frame_idx = None
            if rot_frames > 1:
                facing = float(getattr(inst, 'facing_angle', 0.0) or 0.0)
                frame_idx = self._billboard_rotation_frame(
                    bx, by, facing, cam_x, cam_y, rot_frames)
            tex = self._billboard_texture(inst, frame_idx)
            if tex is None:
                continue
            # Unclamped height + a float (sub-texel) vertical slice — same as
            # the wall pass. Squeezing a walked-into sprite into a
            # screen-clamped height distorted it.
            full_h_b = view_h * ih / max(corrected_b, 1e-4)
            sprite_w = view_h * iw / max(corrected_b, 1e-4)
            if sprite_w < 1 or full_h_b < 1:
                continue
            # Same camera-plane mapping as the wall pass, so billboards line up
            # with the walls instead of drifting toward the screen edges.
            b_camera_x = math.tan(rel_angle) / plane_tan if plane_tan else 0.0
            col_center = (b_camera_x + 1.0) * 0.5 * num_columns
            x_center = col_center * col_width
            x_left = x_center - sprite_w / 2.0
            y_bot_b = mid - full_h_b / 2.0        # y-up: bottom of the sprite
            if stairs:
                # Stands on the floor of its own cell (renderer.py, S7):
                # positive = lower on screen, i.e. DOWN in Kivy's y-up.
                b_floor = heights.get((int(bx // cell_size), int(by // cell_size)), 0.0)
                y_bot_b -= (eye_z - (b_floor + self.RAYCAST_EYE_HEIGHT * cell_size)) \\
                    * view_h / max(corrected_b, 1e-4)
            by0 = max(view_bottom, y_bot_b)       # clamp to the view, not window
            by1 = min(h, y_bot_b + full_h_b)
            b_vis_h = by1 - by0
            if b_vis_h <= 0:
                continue
            bv0 = (by0 - y_bot_b) / full_h_b
            bv1 = (by1 - y_bot_b) / full_h_b
            tw, th = tex.width, tex.height
            # Draw one textured slice per overlapped screen column, skipping
            # columns where a nearer wall occludes this billboard.
            col_start = max(0, int(x_left // col_width))
            col_end = min(num_columns - 1, int((x_left + sprite_w) // col_width))
            for col in range(col_start, col_end + 1):
                if corrected_b >= col_wall_dist[col]:
                    continue
                c_by0, c_bv0 = by0, bv0
                c_by1, c_bv1 = by1, bv1
                if stairs:
                    # Steps nearer than it hide its lower rows (S7): rows at
                    # or below the y-down limit -> Kivy y below h - limit.
                    limit = self._clip_before(stairs_layouts[col]['occluders'],
                                              corrected_b, view_h)
                    c_by0 = max(by0, h - limit)
                    if c_by0 >= by1:
                        continue
                    c_bv0 = (c_by0 - y_bot_b) / full_h_b
                    # A lintel nearer than it hides its UPPER rows (ceilings
                    # plan, C5/C8): y-down rows above top_lim -> Kivy y above
                    # h - top_lim.
                    occ_top = stairs_layouts[col].get('occluders_top')
                    if occ_top:
                        top_lim = self._clip_top_before(occ_top, corrected_b)
                        c_by1 = min(by1, h - top_lim)
                        if c_by1 <= c_by0:
                            continue
                        c_bv1 = (c_by1 - y_bot_b) / full_h_b
                seg_x0 = max(x_left, col * col_width)
                seg_x1 = min(x_left + sprite_w, (col + 1) * col_width)
                if seg_x1 <= seg_x0:
                    continue
                u0 = (seg_x0 - x_left) / sprite_w
                u1 = (seg_x1 - x_left) / sprite_w
                rx = min(tw - 1, max(0, int(u0 * tw)))
                rw = max(1, int((u1 - u0) * tw))
                region = tex.get_region(rx, 0, rw, th)
                group.add(Color(1, 1, 1, 1))
                # Float tex_coords select the visible vertical slice sub-texel
                # exactly (get_region would snap to whole texels).
                group.add(Rectangle(texture=region, pos=(seg_x0, c_by0),
                                    size=(seg_x1 - seg_x0, c_by1 - c_by0),
                                    tex_coords=(0.0, c_bv0, 1.0, c_bv0,
                                                1.0, c_bv1, 0.0, c_bv1)))

    # ------------------------------------------------------------------
    # Stairs (docs/RAYCAST_STAIRS_PLAN.md, S11): ports of heights.py,
    # renderer.py's stairs path and climbing.py. _cast_ray_steps and
    # _layout_column are VERBATIM copies of the desktop functions (pinned by
    # tests/test_raycast_export_parity.py); everything runs in GM y-down
    # space and only the drawing flips (Kivy y = h - row).
    # ------------------------------------------------------------------
    @classmethod
    def _raycast_max_floor_height(cls, cell_size, wall_h):
        return max(0.0, (wall_h - cls.RAYCAST_EYE_HEIGHT) * cell_size - cls.RAYCAST_CEILING_MARGIN)

    def _raycast_build_floor_heights(self, cell_size, max_height):
        import math
        heights = {}
        textures = {}
        for inst in self.instances:
            hgt = getattr(inst, 'raycast_floor_height', None)
            if hgt is None or getattr(inst, 'solid', False):
                continue
            try:
                hgt = float(hgt)
            except (TypeError, ValueError):
                hgt = 0.0
            if hgt != hgt:
                hgt = 0.0
            hgt = min(max(hgt, 0.0), max_height)
            if hgt <= 0.0:
                continue
            gm_x, gm_y = self._raycast_gm_xy(inst)
            bw = float(getattr(inst, 'image_width', 0) or 0)
            bh = float(getattr(inst, 'image_height', 0) or 0)
            gx0 = int(math.floor(gm_x / cell_size))
            gy0 = int(math.floor(gm_y / cell_size))
            gx1 = int(math.floor((gm_x + bw) / cell_size - 1e-9)) if bw > 0 else gx0
            gy1 = int(math.floor((gm_y + bh) / cell_size - 1e-9)) if bh > 0 else gy0
            tex = (getattr(inst, 'raycast_step_top_texture', '') or '',
                   getattr(inst, 'raycast_step_side_texture', '') or '')
            for gx in range(gx0, max(gx0, gx1) + 1):
                for gy in range(gy0, max(gy0, gy1) + 1):
                    if hgt > heights.get((gx, gy), 0.0):
                        heights[(gx, gy)] = hgt
                        textures[(gx, gy)] = tex
        self._raycast_floor_heights = heights
        return heights, textures

    def _raycast_build_ceiling_heights(self, cell_size, room_ceiling, floor_heights,
                                       eye_height):
        # heights.build_ceiling_heights (ceilings plan, C1/C8): lowered cells
        # from Set Ceiling Height markers, each clamped to [floor + eye + margin,
        # room ceiling]; the lowest marker wins; a marker at the room ceiling
        # changes nothing.
        import math
        ceilings = {}
        textures = {}
        for inst in self.instances:
            raw = getattr(inst, 'raycast_ceiling_height', None)
            if raw is None or getattr(inst, 'solid', False):
                continue
            try:
                raw = float(raw)
            except (TypeError, ValueError):
                raw = 0.0
            if raw != raw:
                raw = 0.0
            tex = getattr(inst, 'raycast_ceiling_texture', '') or ''
            gm_x, gm_y = self._raycast_gm_xy(inst)
            bw = float(getattr(inst, 'image_width', 0) or 0)
            bh = float(getattr(inst, 'image_height', 0) or 0)
            gx0 = int(math.floor(gm_x / cell_size))
            gy0 = int(math.floor(gm_y / cell_size))
            gx1 = int(math.floor((gm_x + bw) / cell_size - 1e-9)) if bw > 0 else gx0
            gy1 = int(math.floor((gm_y + bh) / cell_size - 1e-9)) if bh > 0 else gy0
            for gx in range(gx0, max(gx0, gx1) + 1):
                for gy in range(gy0, max(gy0, gy1) + 1):
                    lowest = floor_heights.get((gx, gy), 0.0) + eye_height + self.RAYCAST_CEILING_MARGIN
                    height = min(max(raw, lowest), room_ceiling)
                    if height >= room_ceiling:
                        continue
                    if height < ceilings.get((gx, gy), room_ceiling):
                        ceilings[(gx, gy)] = height
                        textures[(gx, gy)] = tex
        self._raycast_ceiling_heights = ceilings
        return ceilings, textures

    def _cast_ray_steps(self, px, py, angle_rad, cell_size, max_cells, heights, ceilings=None):
        import math
        v_walls, h_walls = self._raycast_v_walls, self._raycast_h_walls
        v_sprites = getattr(self, '_raycast_v_wall_sprites', {}) or {}
        h_sprites = getattr(self, '_raycast_h_wall_sprites', {}) or {}
        px_cell, py_cell = px / cell_size, py / cell_size
        dx, dy = math.cos(angle_rad), math.sin(angle_rad)
        map_x, map_y = int(px_cell), int(py_cell)

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

        crossings = []
        h_prev = heights.get((map_x, map_y), 0.0)
        c_prev = ceilings.get((map_x, map_y)) if ceilings is not None else None
        side = 0
        dist_cells = float(max_cells)
        for _ in range(max_cells):
            if side_x < side_y:
                side_x += delta_x
                map_x += step_x
                side = 0
                line_x = map_x if step_x > 0 else map_x + 1
                wall_key = (line_x, map_y)
                hit = wall_key in v_walls
            else:
                side_y += delta_y
                map_y += step_y
                side = 1
                line_y = map_y if step_y > 0 else map_y + 1
                wall_key = (map_x, line_y)
                hit = wall_key in h_walls
            d_cells = (side_x - delta_x) if side == 0 else (side_y - delta_y)
            if side == 0:
                wall_coord = py_cell + d_cells * dy
                if dx > 0:
                    wall_coord = -wall_coord
            else:
                wall_coord = px_cell + d_cells * dx
                if dy < 0:
                    wall_coord = -wall_coord
            tex_u = wall_coord - math.floor(wall_coord)
            if hit:
                sprite = v_sprites.get(wall_key) if side == 0 else h_sprites.get(wall_key)
                return crossings, (max(d_cells, 1e-4) * cell_size, side, True, tex_u, sprite)
            h_next = heights.get((map_x, map_y), 0.0)
            if ceilings is None:
                if h_next != h_prev:
                    crossings.append((d_cells, h_next, side, tex_u, (map_x, map_y)))
                    h_prev = h_next
            else:
                c_next = ceilings.get((map_x, map_y))
                if h_next != h_prev or c_next != c_prev:
                    crossings.append((d_cells, h_next, side, tex_u, (map_x, map_y), c_next))
                    h_prev = h_next
                    c_prev = c_next
        return crossings, (max(dist_cells, 1e-4) * cell_size, side, False, 0.0, None)

    @staticmethod
    def _layout_column(crossings, hit, h0, eye_z, wall_top_z, cell_size, cos_off,
                       half_h, view_h, max_cells):
        def stairs_y(z, eye_z, d, half_h, view_h):
            return half_h + (eye_z - z) * view_h / d

        clip = float(view_h)
        treads, risers, occluders = [], [], []
        h_cur = h0
        d_prev = 0.0
        for dist_cells, h_next, side, tex_u, cell in crossings:
            d = max(dist_cells * cell_size * cos_off, 1e-4)
            y_cur = stairs_y(h_cur, eye_z, d, half_h, view_h)
            if y_cur < clip:
                treads.append((y_cur, clip, h_cur, d_prev))
                clip = y_cur
            if h_next > h_cur:
                y_top = stairs_y(h_next, eye_z, d, half_h, view_h)
                if y_top < clip:
                    risers.append((y_top, clip, d, side, tex_u, cell, h_cur, h_next))
                    clip = y_top
            occluders.append((d, clip))
            h_cur = h_next
            d_prev = d
            if clip <= 0:
                return {"treads": treads, "risers": risers, "wall": None,
                        "occluders": occluders, "wall_dist": float("inf")}
        dist_px, side, is_hit, tex_u, sprite = hit
        d = max(dist_px * cos_off, 1e-4)
        if not is_hit:
            d = max(max_cells * cell_size * cos_off, 1e-4)
        y_cur = stairs_y(h_cur, eye_z, d, half_h, view_h)
        if y_cur < clip:
            treads.append((y_cur, clip, h_cur, d_prev))
            clip = y_cur
        wall = None
        if is_hit:
            y_top = stairs_y(wall_top_z, eye_z, d, half_h, view_h)
            if y_top < clip:
                wall = (y_top, clip, d, side, tex_u, sprite)
            occluders.append((d, min(clip, y_top)))
        return {"treads": treads, "risers": risers, "wall": wall,
                "occluders": occluders, "wall_dist": d if is_hit else float("inf")}

    @staticmethod
    def _layout_column_ceilings(crossings, hit, h0, c0, eye_z, room_top_z, cell_size,
                                cos_off, half_h, view_h, max_cells):
        # renderer.layout_column_ceilings, verbatim (ceilings plan, C3): the
        # two-clip walk.
        def stairs_y(z, eye_z, d, half_h, view_h):
            return half_h + (eye_z - z) * view_h / d

        bot = float(view_h)
        top = 0.0
        treads, risers, ceils, lintels = [], [], [], []
        occluders, occluders_top = [], []
        h_cur = h0
        c_cur = c0 if c0 is not None else room_top_z
        d_prev = 0.0
        for dist_cells, h_next, side, tex_u, cell, c_raw in crossings:
            c_next = c_raw if c_raw is not None else room_top_z
            d = max(dist_cells * cell_size * cos_off, 1e-4)
            y_cur = stairs_y(h_cur, eye_z, d, half_h, view_h)
            if y_cur < bot:
                y_cur = max(y_cur, top)
                treads.append((y_cur, bot, h_cur, d_prev))
                bot = y_cur
            yc_cur = stairs_y(c_cur, eye_z, d, half_h, view_h)
            if yc_cur > top:
                yc_cur = min(yc_cur, bot)
                ceils.append((top, yc_cur, c_cur, d_prev))
                top = yc_cur
            if h_next > h_cur:
                y_up = stairs_y(h_next, eye_z, d, half_h, view_h)
                if y_up < bot:
                    y_up = max(y_up, top)
                    risers.append((y_up, bot, d, side, tex_u, cell, h_cur, h_next))
                    bot = y_up
            if c_next < c_cur:
                y_dn = stairs_y(c_next, eye_z, d, half_h, view_h)
                if y_dn > top:
                    y_dn = min(y_dn, bot)
                    lintels.append((top, y_dn, d, side, tex_u, cell, c_next, c_cur))
                    top = y_dn
            occluders.append((d, bot))
            occluders_top.append((d, top))
            h_cur, c_cur, d_prev = h_next, c_next, d
            if top >= bot:
                return {"treads": treads, "risers": risers, "wall": None,
                        "ceilings": ceils, "lintels": lintels, "occluders": occluders,
                        "occluders_top": occluders_top, "wall_dist": float("inf")}
        dist_px, side, is_hit, tex_u, sprite = hit
        d = max(dist_px * cos_off, 1e-4)
        if not is_hit:
            d = max(max_cells * cell_size * cos_off, 1e-4)
        y_cur = stairs_y(h_cur, eye_z, d, half_h, view_h)
        if y_cur < bot:
            y_cur = max(y_cur, top)
            treads.append((y_cur, bot, h_cur, d_prev))
            bot = y_cur
        yc_cur = stairs_y(c_cur, eye_z, d, half_h, view_h)
        if yc_cur > top:
            yc_cur = min(yc_cur, bot)
            ceils.append((top, yc_cur, c_cur, d_prev))
            top = yc_cur
        wall = None
        if is_hit:
            if top < bot:
                wall = (top, bot, d, side, tex_u, sprite)
            occluders.append((d, top))
            occluders_top.append((d, top))
        return {"treads": treads, "risers": risers, "wall": wall,
                "ceilings": ceils, "lintels": lintels, "occluders": occluders,
                "occluders_top": occluders_top, "wall_dist": d if is_hit else float("inf")}

    @classmethod
    def _clip_top_before(cls, occluders_top, dist):
        # renderer._clip_top_before (C5): the first y-down row NOT hidden from
        # above for something at corrected distance dist.
        limit = 0.0
        for d, top in occluders_top:
            if d >= dist:
                break
            limit = top
        return cls._stairs_row(limit)

    @staticmethod
    def _stairs_row(y):
        import math
        return int(math.floor(y + 0.5))

    @classmethod
    def _clip_before(cls, occluders, dist, view_h):
        limit = float(view_h)
        for d, clip in occluders:
            if d >= dist:
                break
            limit = clip
        return cls._stairs_row(limit)

    def _stairs_wall_rows(self, group, tex, color, tex_u, x0, strip_w, d, eye_z,
                          cell_size, half_h, view_h, h, r0, r1, shade):
        # Rows [r0, r1) (y-down, inside the view) of a wall or a riser at
        # corrected distance d; texture tiles anchored at height 0. Kivy
        # y = h - row; textures are bottom-origin (v = 0 at the tile bottom).
        import math
        r0 = max(0, r0)
        r1 = min(int(view_h), r1)
        if r1 <= r0:
            return
        if tex is None:
            group.add(Color(*[c * shade for c in color], 1))
            group.add(Rectangle(pos=(x0, h - r1), size=(strip_w, r1 - r0)))
            return
        tw, th = tex.width, tex.height
        tile_z = self.RAYCAST_TEXTURE_HEIGHT * cell_size
        tile_h = view_h * tile_z / d
        tex_x = min(tw - 1, max(0, int(tex_u * tw)))
        region = tex.get_region(tex_x, 0, 1, th)
        z_bot = eye_z - (r1 - half_h) * d / view_h
        z_top = eye_z - (r0 - half_h) * d / view_h
        k0 = max(0, int(math.floor(z_bot / tile_z)))
        k1 = max(k0, int(math.floor(z_top / tile_z)))
        group.add(Color(shade, shade, shade, 1))
        for k in range(k0, k1 + 1):
            seg_top = half_h + (eye_z - (k + 1) * tile_z) * view_h / d
            sy0 = max(r0, int(math.floor(seg_top)))
            sy1 = min(r1, int(math.ceil(seg_top + tile_h)))
            if sy1 <= sy0:
                continue
            v_low = 1.0 - (sy1 - seg_top) / tile_h
            v_high = 1.0 - (sy0 - seg_top) / tile_h
            group.add(Rectangle(texture=region, pos=(x0, h - sy1),
                                size=(strip_w, sy1 - sy0),
                                tex_coords=(0.0, v_low, 1.0, v_low,
                                            1.0, v_high, 0.0, v_high)))

    def _draw_stairs_column(self, group, sf, col, lay, floor_cast, ceiling_cast=False):
        x0 = int(col * sf['col_width'])
        strip_w = max(1, int((col + 1) * sf['col_width']) - x0)
        view_h, h = sf['view_h'], sf['h']
        row = self._stairs_row
        if not floor_cast:
            group.add(Color(*sf['floor_color'], 1))
            for y_top, y_bot, height, _d in lay['treads']:
                if height > 0:
                    r0, r1 = max(0, row(y_top)), min(int(view_h), row(y_bot))
                    if r1 > r0:
                        group.add(Rectangle(pos=(x0, h - r1), size=(strip_w, r1 - r0)))
        for y_top, y_bot, d, side, tex_u, cell, _lo, _hi in lay['risers']:
            tex = None
            if sf['textured']:
                name = sf['step_textures'].get(cell, ('', ''))[1]
                tex = self._raycast_texture(name) if name else None
                if tex is None:
                    tex = sf['wall_texture']
            self._stairs_wall_rows(group, tex, sf['wall_color'], tex_u, x0, strip_w, d,
                                   sf['eye_z'], sf['cell_size'], sf['half_h'], view_h, h,
                                   row(y_top), row(y_bot),
                                   self._wall_shade(side, d, sf['max_dist']))
        # Lowered ceilings (C3/C4): their spans flat, unless the cast already
        # painted them textured; then their lintels, textured like walls.
        low_spans = [sp for sp in lay.get('ceilings', ()) if sp[2] < sf['wall_top_z']]
        if low_spans and not ceiling_cast:
            group.add(Color(*sf['ceiling_color'], 1))
            for y_top, y_bot, height, _d in low_spans:
                r0, r1 = max(0, row(y_top)), min(int(view_h), row(y_bot))
                if r1 > r0:
                    group.add(Rectangle(pos=(x0, h - r1), size=(strip_w, r1 - r0)))
        for y_top, y_bot, d, side, tex_u, cell, _lo, _hi in lay.get('lintels', ()):
            tex = sf['wall_texture'] if sf['textured'] else None
            self._stairs_wall_rows(group, tex, sf['wall_color'], tex_u, x0, strip_w, d,
                                   sf['eye_z'], sf['cell_size'], sf['half_h'], view_h, h,
                                   row(y_top), row(y_bot),
                                   self._wall_shade(side, d, sf['max_dist']))
        wall = lay['wall']
        if wall is not None:
            y_top, y_bot, d, side, tex_u, wall_sprite = wall
            tex = None
            if sf['textured']:
                tex = sf['wall_texture']
                if tex is None:
                    tex = self._raycast_texture(wall_sprite)
            self._stairs_wall_rows(group, tex, sf['wall_color'], tex_u, x0, strip_w, d,
                                   sf['eye_z'], sf['cell_size'], sf['half_h'], view_h, h,
                                   row(y_top), row(y_bot),
                                   self._wall_shade(side, d, sf['max_dist']))

    def _stairs_floor_buffer(self, layouts, sf, floor_px, top_px,
                             facing_screen_rad, fov_rad, res):
        # Port of renderer.cast_stairs_floor into an RGBA buffer laid out
        # like _floor_buffer's (row 0 = the horizon row). The *_px are
        # (bytes, tw, th) with Kivy's bottom-up rows, flipped when sampled.
        import math
        w = float(sf['w'])
        view_h = sf['view_h']
        half_h = int(view_h // 2)
        region_h = int(view_h) - half_h
        sw = max(1, int(w) // res)
        sh = max(1, region_h // res)
        cell_size = sf['cell_size']
        eye_cells = sf['eye_z'] / cell_size
        cam_cx, cam_cy = sf['cam_x'] / cell_size, sf['cam_y'] / cell_size
        dir_x, dir_y = math.cos(facing_screen_rad), math.sin(facing_screen_rad)
        plane = math.tan(fov_rad / 2)
        plane_x, plane_y = -dir_y * plane, dir_x * plane
        rdx0, rdy0 = dir_x - plane_x, dir_y - plane_y
        rdx1, rdy1 = dir_x + plane_x, dir_y + plane_y
        fc = sf['floor_color']
        flat = bytes([int(fc[0] * 255), int(fc[1] * 255), int(fc[2] * 255), 255])
        out = bytearray(flat * (sw * sh))
        floor = math.floor
        ncol = len(layouts)
        for i in range(sw):
            sx = i * res
            c = int(sx / sf['col_width'])
            if c >= ncol:
                c = ncol - 1
            spans = layouts[c]['treads']
            if not spans:
                continue
            t = sx / w
            rdx = rdx0 + (rdx1 - rdx0) * t
            rdy = rdy0 + (rdy1 - rdy0) * t
            k = 0
            n = len(spans)
            for j in range(sh - 1, -1, -1):
                y = half_h + j * res
                while k < n - 1 and y < spans[k][0]:
                    k += 1
                height = spans[k][2]
                dz = eye_cells - height / cell_size
                if dz <= 0:
                    continue
                p = j * res
                if p <= 0:
                    p = 1
                rowd = dz * view_h / p
                fx = cam_cx + rowd * rdx
                fy = cam_cy + rowd * rdy
                src = None
                if top_px and height > 0:
                    src = top_px.get((int(floor(fx)), int(floor(fy))))
                if src is None:
                    src = floor_px
                if src is None:
                    continue
                pixels, tw, th = src
                tx = int(tw * (fx - floor(fx)))
                ty = int(th * (fy - floor(fy)))
                if tx >= tw:
                    tx = tw - 1
                if ty >= th:
                    ty = th - 1
                si = ((th - 1 - ty) * tw + tx) * 4
                di = (j * sw + i) * 4
                out[di] = pixels[si]
                out[di + 1] = pixels[si + 1]
                out[di + 2] = pixels[si + 2]
        return bytes(out), sw, sh

    def _stairs_floor(self, group, layouts, sf, floor_px, top_px,
                      facing_screen_rad, fov_rad, res):
        from kivy.graphics.texture import Texture
        buf, sw, sh = self._stairs_floor_buffer(layouts, sf, floor_px, top_px,
                                                facing_screen_rad, fov_rad, res)
        tex = Texture.create(size=(sw, sh), colorfmt='rgba')
        tex.blit_buffer(buf, colorfmt='rgba', bufferfmt='ubyte')
        view_h, h = sf['view_h'], sf['h']
        group.add(Color(1, 1, 1, 1))
        group.add(Rectangle(texture=tex, pos=(0, h - view_h), size=(sf['w'], view_h / 2.0),
                            tex_coords=(0, 1, 1, 1, 1, 0, 0, 0)))

    def _stairs_ceiling_buffer(self, layouts, sf, cell_px, ceil_px,
                               facing_screen_rad, fov_rad, res):
        # Port of renderer.cast_ceiling_spans (ceilings plan, C4/C8) into an
        # RGBA buffer, row 0 = the TOP row of the view, fully transparent where
        # nothing is cast. The *_px are (bytes, tw, th) with Kivy's bottom-up rows.
        import math
        w = float(sf['w'])
        view_h = sf['view_h']
        half_h = int(view_h // 2)
        sw = max(1, int(w) // res)
        sh = max(1, half_h // res)
        cell_size = sf['cell_size']
        eye_cells = sf['eye_z'] / cell_size
        cam_cx, cam_cy = sf['cam_x'] / cell_size, sf['cam_y'] / cell_size
        room_top = sf['wall_top_z']
        dir_x, dir_y = math.cos(facing_screen_rad), math.sin(facing_screen_rad)
        plane = math.tan(fov_rad / 2)
        plane_x, plane_y = -dir_y * plane, dir_x * plane
        rdx0, rdy0 = dir_x - plane_x, dir_y - plane_y
        rdx1, rdy1 = dir_x + plane_x, dir_y + plane_y
        cc = sf['ceiling_color']
        flat = (int(cc[0] * 255), int(cc[1] * 255), int(cc[2] * 255))
        out = bytearray(sw * sh * 4)
        floor = math.floor
        ncol = len(layouts)
        painted = False
        for i in range(sw):
            c = int(i * res / sf['col_width'])
            if c >= ncol:
                c = ncol - 1
            spans = [sp for sp in layouts[c].get('ceilings', ()) if sp[2] < room_top]
            if not spans:
                continue
            t = (i * res) / w
            rdx = rdx0 + (rdx1 - rdx0) * t
            rdy = rdy0 + (rdy1 - rdy0) * t
            n = len(spans)
            k = 0
            for j in range(sh):
                y_c = j * res + res - 1
                while k < n and y_c >= spans[k][1]:
                    k += 1
                if k >= n:
                    break
                if y_c < spans[k][0]:
                    continue
                dz = spans[k][2] / cell_size - eye_cells
                if dz <= 0:
                    continue
                p = half_h - (j * res + res)
                if p <= 0:
                    p = 1
                rowd = dz * view_h / p
                fx = cam_cx + rowd * rdx
                fy = cam_cy + rowd * rdy
                src = cell_px.get((int(floor(fx)), int(floor(fy)))) if cell_px else None
                if src is None:
                    src = ceil_px
                di = (j * sw + i) * 4
                if src is not None:
                    pixels, tw, th = src
                    tx = int(tw * (fx - floor(fx)))
                    ty = int(th * (fy - floor(fy)))
                    if tx >= tw:
                        tx = tw - 1
                    if ty >= th:
                        ty = th - 1
                    si = ((th - 1 - ty) * tw + tx) * 4
                    out[di] = pixels[si]
                    out[di + 1] = pixels[si + 1]
                    out[di + 2] = pixels[si + 2]
                else:
                    out[di], out[di + 1], out[di + 2] = flat
                out[di + 3] = 255
                painted = True
        return bytes(out), sw, sh, painted

    def _stairs_ceiling(self, group, layouts, sf, cell_px, ceil_px,
                        facing_screen_rad, fov_rad, res):
        from kivy.graphics.texture import Texture
        buf, sw, sh, painted = self._stairs_ceiling_buffer(
            layouts, sf, cell_px, ceil_px, facing_screen_rad, fov_rad, res)
        if not painted:
            return
        tex = Texture.create(size=(sw, sh), colorfmt='rgba')
        tex.mag_filter = 'nearest'
        tex.min_filter = 'nearest'
        tex.blit_buffer(buf, colorfmt='rgba', bufferfmt='ubyte')
        view_h, h = sf['view_h'], sf['h']
        group.add(Color(1, 1, 1, 1))
        group.add(Rectangle(texture=tex, pos=(0, h - view_h / 2.0),
                            size=(sf['w'], int(view_h // 2)),
                            tex_coords=(0, 1, 1, 1, 1, 0, 0, 0)))

    def _ext_update__raycast_2_5d(self, dt):
        # Climbing (climbing.py), after movement and collisions, before End
        # Step. Kivy has no before-step hook, so moves are measured against
        # the snapshot taken here last frame: every move since is checked.
        cfg = getattr(self, 'raycast_camera', None)
        if not cfg or not cfg.get('enabled'):
            return
        cell_size = int(cfg.get('cell_size', 32))
        wall_h = self._clamp_wall_height(cfg.get('wall_height', self.RAYCAST_WALL_HEIGHT))
        heights, _tex = self._raycast_build_floor_heights(
            cell_size, self._raycast_max_floor_height(cell_size, wall_h))
        room_top = wall_h * cell_size
        eye_px = self.RAYCAST_EYE_HEIGHT * cell_size
        ceilings, _ctex = self._raycast_build_ceiling_heights(
            cell_size, room_top, heights, eye_px)
        try:
            max_step = max(0.0, float(cfg.get('max_step', self.RAYCAST_DEFAULT_MAX_STEP)))
        except (TypeError, ValueError):
            max_step = self.RAYCAST_DEFAULT_MAX_STEP
        room_h = float(self.room_height)

        def floor_at(inst, x, y):
            # The GM-space centre for a Kivy position (x, y): GM y is
            # room_height - y - image_height (see _raycast_gm_xy).
            iw = float(getattr(inst, 'image_width', 0) or 0)
            ih = float(getattr(inst, 'image_height', 0) or 0)
            cx = x + iw / 2.0
            cy = room_h - y - ih + ih / 2.0
            return heights.get((int(cx // cell_size), int(cy // cell_size)), 0.0)

        def ceiling_at(inst, x, y):
            iw = float(getattr(inst, 'image_width', 0) or 0)
            ih = float(getattr(inst, 'image_height', 0) or 0)
            cx = x + iw / 2.0
            cy = room_h - y - ih + ih / 2.0
            return ceilings.get((int(cx // cell_size), int(cy // cell_size)), room_top)

        dead = set(id(i) for i in (getattr(self, 'instances_to_destroy', None) or []))
        prev = self._raycast_step_prev or {}
        movers = [i for i in self.instances
                  if id(i) not in dead and not getattr(i, 'solid', False)
                  and getattr(i, 'raycast_floor_height', None) is None
                  and getattr(i, 'raycast_ceiling_height', None) is None]
        for inst in movers:
            old = prev.get(id(inst))
            blocked = 0
            if old is not None and old[0] is inst:
                ox, oy = old[1], old[2]
                nx, ny = float(inst.x), float(inst.y)
                moved = (nx, ny) != (ox, oy)
                if moved and abs(nx - ox) <= cell_size and abs(ny - oy) <= cell_size:
                    f_old = floor_at(inst, ox, oy)
                    if floor_at(inst, nx, ny) - f_old > max_step:
                        blocked = 1
                        for tx, ty in ((nx, oy), (ox, ny), (ox, oy)):
                            ok = floor_at(inst, tx, ty) - f_old <= max_step
                            if (tx, ty) == (ox, oy) or ok:
                                inst.x, inst.y = tx, ty
                                break
            inst.raycast_step_blocked = blocked
            inst.raycast_floor_z = floor_at(inst, float(inst.x), float(inst.y))
            inst.raycast_ceiling_z = ceiling_at(inst, float(inst.x), float(inst.y))
        self._raycast_step_prev = {id(i): (i, float(i.x), float(i.y)) for i in movers}

        camera = self._find_raycast_camera(cfg)
        if camera is None:
            return
        target = floor_at(camera, float(camera.x), float(camera.y))
        camera.raycast_floor_z = target
        camera.raycast_ceiling_z = ceiling_at(camera, float(camera.x), float(camera.y))
        cur = self._raycast_eye_floor
        vz = self._raycast_eye_vz
        if cur is None:
            cur, vz = target, 0.0
        elif cur < target:
            cur, vz = min(target, cur + self.RAYCAST_CLIMB_SPEED), 0.0
        elif cur > target:
            vz += self.RAYCAST_FALL_GRAVITY
            cur = max(target, cur - vz)
            if cur == target:
                vz = 0.0
        else:
            vz = 0.0
        # The view never rises above the ceiling over the camera (C6).
        eye_limit = camera.raycast_ceiling_z - self.RAYCAST_CEILING_MARGIN - eye_px
        if cur > eye_limit:
            cur, vz = max(target, eye_limit), 0.0
        self._raycast_eye_floor = cur
        self._raycast_eye_vz = vz
'''


# ---------------------------------------------------------------------------
# Kivy action codegen (Stage C2c). code_generator._convert_simple_action's
# DEFAULT branch consults ACTION_CODEGEN for actions it does not enumerate.
# Each fn receives (gen, params, event_type); gen is the ActionCodeGenerator
# (used for gen.sprite_paths). Mirrors the desktop handlers in handlers.py.
# ---------------------------------------------------------------------------

def _cg_set_facing_angle(gen, params, event_type):
    from export.Kivy.code_generator import _num_code, _tofloat, _resolve_instance_names  # noqa
    angle = _num_code(params.get('angle', 0))
    rel = params.get('relative', False)
    if isinstance(rel, str):
        rel = rel.strip().lower() in ('true', '1', 'yes')
    if rel:
        return f"self.facing_angle = (self.facing_angle + {angle}) % 360"
    return f"self.facing_angle = ({angle}) % 360"

def _cg_set_billboard_rotation(gen, params, event_type):
    from export.Kivy.code_generator import _num_code, _tofloat, _resolve_instance_names  # noqa
    frames = _num_code(params.get('frames', 8), 8)
    return f"self.billboard_rotation_frames = max(0, int({frames}))"

def _cg_set_floor_height(gen, params, event_type):
    from export.Kivy.code_generator import _num_code, _tofloat, _resolve_instance_names  # noqa
    # Make this instance a step (execute_set_floor_height_action); the scene's
    # _raycast_build_floor_heights clamps.
    raw = params.get('height', 8)
    height = _num_code(raw, 8) if raw not in (None, '') else '8'
    top = str(params.get('top_texture') or '')
    side = str(params.get('side_texture') or '')
    return (f"self.raycast_floor_height = float({height}); "
            f"self.raycast_step_top_texture = {top!r}; "
            f"self.raycast_step_side_texture = {side!r}")

def _cg_set_ceiling_height(gen, params, event_type):
    from export.Kivy.code_generator import _num_code, _tofloat, _resolve_instance_names  # noqa
    # Lower the ceiling over this instance's cells (execute_set_ceiling_height_action);
    # the scene's _raycast_build_ceiling_heights clamps.
    raw = params.get('height', 40)
    height = _num_code(raw, 0) if raw is not None else '40'
    texture = str(params.get('texture') or '')
    return (f"self.raycast_ceiling_height = float({height}); "
            f"self.raycast_ceiling_texture = {texture!r}")

def _cg_go_to_room_seamlessly(gen, params, event_type):
    # Go to Room Seamlessly (execute_go_to_room_seamlessly_action); the scene's
    # _raycast_go_seamless records the arrival and changes room.
    room = str(params.get('room') or '')
    marker = str(params.get('marker') or '')
    return f"self.scene._raycast_go_seamless({room!r}, {marker!r})"

def _cg_enable_raycast_view(gen, params, event_type):
    from export.Kivy.code_generator import _num_code, _tofloat, _resolve_instance_names  # noqa
    # Configure the scene's Doom-style first-person raycast camera
    # (rendered by the scene; see the raycast render methods). Mirrors
    # execute_enable_raycast_view_action's defaults.
    en = params.get('enable', True)
    if isinstance(en, str):
        en = en.strip().lower() not in ('false', '0', 'no')
    if not en:
        return "self.scene.raycast_camera = {'enabled': False}"
    def _q(v):
        return "''" if v is None else repr(str(v))
    cfg = {
        'enabled': True,
        'camera_object': str(params.get('camera_object') or ''),
        'fov': _tofloat(params.get('fov'), 66),
        'render_distance': int(_tofloat(params.get('render_distance'), 20)),
        'cell_size': int(_tofloat(params.get('cell_size'), 32)),
        'columns': int(_tofloat(params.get('columns'), 320)),
        'wall_color': str(params.get('wall_color') or '#993333'),
        'floor_color': str(params.get('floor_color') or '#464632'),
        'ceiling_color': str(params.get('ceiling_color') or '#87CEEB'),
        'wall_texture': str(params.get('wall_texture') or ''),
        'sky_texture': str(params.get('sky_texture') or ''),
        'floor_texture': str(params.get('floor_texture') or ''),
        'ceiling_texture': str(params.get('ceiling_texture') or ''),
        'wall_textured': not (str(params.get('wall_textured', 'true')).strip().lower()
                              in ('false', '0', 'no')),
        'floor_cast_res': max(1, int(_tofloat(params.get('floor_cast_res'), 4))),
        # DOOM-bar letterbox (0 = full height). The scene renderer
        # reads this; without it here, an exported game would ignore a
        # viewport_height the desktop runtime honours.
        'viewport_height': int(_tofloat(params.get('viewport_height'), 0)),
        # Walls + ceiling height in cells (stairs plan S4); the scene clamps
        # it where it is used (_clamp_wall_height).
        'wall_height': _tofloat(params.get('wall_height'), 1.5),
        # Highest climbable step, room px (stairs S8/S11).
        'max_step': _tofloat(params.get('max_step'), 12),
    }
    if not cfg['camera_object']:
        # No named camera object -> the acting instance IS the camera;
        # store it directly (the generated Kivy object has no
        # object_name attribute to look up by).
        return (f"self.scene.raycast_camera = {cfg!r}; "
                f"self.scene.raycast_camera['camera_instance'] = self")
    return f"self.scene.raycast_camera = {cfg!r}"

def _cg_draw_doom_hud(gen, params, event_type):
    from export.Kivy.code_generator import _num_code, _tofloat, _resolve_instance_names  # noqa
    # DOOM-style status bar. A MACRO action emitting a FIXED, small set
    # of draw-queue commands (unlike the minimap's unbounded wall loop),
    # so it's inline appends, not a call-out — mirrors
    # build_doom_hud_commands() in runtime/action_executor.py, which the
    # parity test compares against. Coordinates are screen-space y-down;
    # the shared draw-queue path flips once for Kivy.
    def _s(key, default):
        return str(params.get(key, default))
    face_path = gen.sprite_paths.get(_s('face_sprite', ''), '')
    lives_path = gen.sprite_paths.get(_s('lives_sprite', ''), '')
    obj_expr = _resolve_instance_names(_s('objective_value', '0'))
    lines = [
        f"_dh_h = {_num_code(params.get('height', 42), 42)}",
        "_dh_scene = getattr(self, 'scene', None)",
        "_dh_win_h = float(getattr(_dh_scene, 'display_height', 0) or 480)",
        "_dh_win_w = float(getattr(_dh_scene, 'display_width', 0) or 640)",
        f"_dh_y = {_num_code(params.get('y', -1), -1)}",
        "_dh_y = (_dh_win_h - _dh_h) if _dh_y < 0 else _dh_y",
        f"_dh_x = {_num_code(params.get('x', 0))}",
        f"_dh_w = {_num_code(params.get('width', 0))} or _dh_win_w",
        "from main import get_game_app as _dh_ga",
        "_dh_app = _dh_ga()",
        "_dh_hp = float(_dh_app.health if _dh_app else 100)",
        "_dh_sc = _dh_app.score if _dh_app else 0",
        "_dh_lv = int(_dh_app.lives if _dh_app else 0)",
        "_dh_pad = 8.0",
        f"_dh_bc = {_s('back_color', '#101010')!r}",
        f"_dh_dv = {_s('divider_color', '#505050')!r}",
        f"_dh_tc = {_s('text_color', '#ffffff')!r}",
        f"_dh_hbw = {_num_code(params.get('health_bar_width', 90), 90)}",
        f"_dh_hbh = {_num_code(params.get('health_bar_height', 14), 14)}",
        "self._draw_queue.append(dict(type='rectangle', x1=_dh_x, y1=_dh_y, "
        "x2=_dh_x + _dh_w, y2=_dh_y + _dh_h, color=_dh_bc, filled=True))",
        "self._draw_queue.append(dict(type='line', x1=_dh_x, y1=_dh_y, "
        "x2=_dh_x + _dh_w, y2=_dh_y, color=_dh_dv))",
        "_dh_hx = _dh_x + _dh_pad",
        "_dh_by = _dh_y + 22",
        f"self._draw_queue.append(dict(type='text', text={_s('health_label', 'Health')!r}, "
        "x=_dh_hx, y=_dh_y + 4, color=_dh_tc))",
        "self._draw_queue.append(dict(type='rectangle', x1=_dh_hx, y1=_dh_by, "
        "x2=_dh_hx + _dh_hbw, y2=_dh_by + _dh_hbh, color=_dh_dv, filled=True))",
        "_dh_frac = min(1.0, max(0.0, _dh_hp / 100.0))",
        "self._draw_queue.append(dict(type='rectangle', x1=_dh_hx, y1=_dh_by, "
        "x2=_dh_hx + _dh_hbw * _dh_frac, y2=_dh_by + _dh_hbh, color="
        f"{_s('bar_color', '#20c020')!r}, filled=True))",
        "self._draw_queue.append(dict(type='text', text=str(int(_dh_hp)), "
        "x=_dh_hx + _dh_hbw + 6, y=_dh_by - 2, color=_dh_tc))",
    ]
    if face_path:
        lines += [
            f"_dh_ff = max(1, {int(float(params.get('face_frames', 4) or 4))})",
            "_dh_frame = min(_dh_ff - 1, int((1.0 - _dh_frac) * _dh_ff))",
            f"self._draw_queue.append(dict(type='sprite', sprite_path={face_path!r}, "
            "x=_dh_x + _dh_w / 2.0 - _dh_h / 2.0, y=_dh_y + 2, subimage=_dh_frame))",
        ]
    lines += [
        "_dh_rx = _dh_x + _dh_w * 2.0 / 3.0 + _dh_pad",
        f"self._draw_queue.append(dict(type='text', text={_s('score_label', 'Score: ')!r} + str(_dh_sc), "
        "x=_dh_rx, y=_dh_y + 4, color=_dh_tc))",
        f"self._draw_queue.append(dict(type='lives', count=_dh_lv, x=_dh_rx, "
        f"y=_dh_y + _dh_h - 20, sprite_path={lives_path!r}, "
        f"scale={_num_code(params.get('lives_scale', 1.0), 1.0)}))",
        f"self._draw_queue.append(dict(type='text', text={_s('objective_label', 'Keys: ')!r} + str({obj_expr}), "
        "x=_dh_x + _dh_w - 96, y=_dh_y + _dh_h / 2.0 - 8, color=_dh_tc))",
    ]
    return "\n".join(lines)

def _cg_draw_minimap(gen, params, event_type):
    from export.Kivy.code_generator import _num_code, _tofloat, _resolve_instance_names  # noqa
    # Emits a CALL, not an inline expression: the minimap needs loops
    # over the room's wall sets. GameObject._draw_minimap is generated
    # into base_object.py — the two halves must stay in step (the M34
    # lesson). See docs/RAYCAST_MINIMAP_PLAN.md.
    x = _num_code(params.get('x', 0))
    y = _num_code(params.get('y', 0))
    size = _num_code(params.get('size', 120))
    back = str(params.get('back_color', '#101018'))
    wall = str(params.get('wall_color', '#8080a0'))
    player = str(params.get('player_color', '#ffd040'))
    mark_obj = str(params.get('mark_object', '') or '')
    mark_col = str(params.get('mark_color', '#40e0ff'))
    mark_obj2 = str(params.get('mark_object_2', '') or '')
    mark_col2 = str(params.get('mark_color_2', '#ff5050'))
    show_trail_raw = params.get('show_trail', False)
    if isinstance(show_trail_raw, str):
        show_trail = show_trail_raw.strip().lower() in ('true', '1', 'yes')
    else:
        show_trail = bool(show_trail_raw)
    trail_col = str(params.get('trail_color', '#406080'))
    return (f"self._draw_minimap({x}, {y}, {size}, "
            f"{back!r}, {wall!r}, {player!r}, "
            f"{mark_obj!r}, {mark_col!r}, {mark_obj2!r}, {mark_col2!r}, "
            f"{show_trail!r}, {trail_col!r})")


ACTION_CODEGEN = {
    'set_facing_angle': _cg_set_facing_angle,
    'set_billboard_rotation': _cg_set_billboard_rotation,
    'set_floor_height': _cg_set_floor_height,
    'set_ceiling_height': _cg_set_ceiling_height,
    'go_to_room_seamlessly': _cg_go_to_room_seamlessly,
    'enable_raycast_view': _cg_enable_raycast_view,
    'draw_doom_hud': _cg_draw_doom_hud,
    'draw_minimap': _cg_draw_minimap,
}


# ---------------------------------------------------------------------------
# Base-object class-body code (Stage C2c). Injected into base_object.py at its
# __PYGM_EXTENSION_BASE_CODE__ marker (post-.format(), so { } are single). The
# draw_minimap action codegen emits a call to this _draw_minimap method.
# ---------------------------------------------------------------------------
BASE_OBJECT_CODE = '''\n    def _draw_minimap(self, x, y, size, back_color, wall_color, player_color,
                      mark_object='', mark_color='#40e0ff',
                      mark_object_2='', mark_color_2='#ff5050',
                      show_trail=False, trail_color='#406080'):
        """Queue a north-up minimap of the raycast room's wall edges.

        A MACRO action: appends ordinary rectangle/line draw-queue commands, so
        this target needed no new renderer. Mirrors build_minimap_commands() in
        runtime/action_executor.py — tests/test_raycast_export_parity.py
        compares the two. The code generator emits a call to this rather than
        an inline expression, since it needs loops.

        Coordinates are SCREEN space with y DOWN like every other draw command;
        the y-flip happens once, later, in the shared draw-queue path.
        """
        self._draw_queue.append(dict(
            type='rectangle', x1=x, y1=y, x2=x + size, y2=y + size,
            color=back_color, filled=True))

        scene = self.scene
        if scene is None:
            return
        span = max(float(getattr(scene, 'room_width', 0) or 0),
                   float(getattr(scene, 'room_height', 0) or 0))
        cs = float(getattr(scene, '_raycast_cell_size', 0) or 0)
        if span <= 0 or not cs:
            return
        scale = float(size) / span

        def _px(wx, wy):
            return x + wx * scale, y + wy * scale

        # Raised floor cells (stairs, hud.build_minimap_commands `raised`):
        # filled squares under the walls, shaded panel -> wall colour by height.
        raised = getattr(scene, '_raycast_floor_heights', None) or {}
        if raised:
            def _hex(c):
                c = c.strip().lstrip('#') if isinstance(c, str) else ''
                if len(c) == 3:
                    c = ''.join(ch * 2 for ch in c)
                try:
                    return tuple(int(c[i:i + 2], 16) for i in (0, 2, 4)) if len(c) == 6 else None
                except ValueError:
                    return None
            ca, cb = _hex(back_color), _hex(wall_color)
            top = max(raised.values())
            for (gx, gy) in sorted(raised):
                t = 0.25 + 0.5 * (raised[(gx, gy)] / top if top > 0 else 1.0)
                if ca is None or cb is None:
                    colour = wall_color
                else:
                    colour = '#%02x%02x%02x' % tuple(
                        int(round(a + (b - a) * t)) for a, b in zip(ca, cb))
                x1, y1 = _px(gx * cs, gy * cs)
                x2, y2 = _px((gx + 1) * cs, (gy + 1) * cs)
                self._draw_queue.append(dict(type='rectangle', x1=x1, y1=y1, x2=x2,
                                             y2=y2, color=colour, filled=True))

        # Wall sets are unordered; sort so every target emits the same picture
        # in the same order (the parity test diffs it).
        for (line_x, row) in sorted(getattr(scene, '_raycast_v_walls', None) or ()):
            x1, y1 = _px(line_x * cs, row * cs)
            x2, y2 = _px(line_x * cs, (row + 1) * cs)
            self._draw_queue.append(dict(type='line', x1=x1, y1=y1, x2=x2,
                                         y2=y2, color=wall_color))
        for (col, line_y) in sorted(getattr(scene, '_raycast_h_walls', None) or ()):
            x1, y1 = _px(col * cs, line_y * cs)
            x2, y2 = _px((col + 1) * cs, line_y * cs)
            self._draw_queue.append(dict(type='line', x1=x1, y1=y1, x2=x2,
                                         y2=y2, color=wall_color))

        # Resolve the camera early (needed by both the trail and the player
        # marker below) -- same ray ORIGIN renderRaycastView casts from.
        cfg = getattr(scene, 'raycast_camera', None) or {}
        camera = None
        finder = getattr(scene, '_find_raycast_camera', None)
        if callable(finder):
            camera = finder(cfg)
        gm_x = gm_y = None
        if camera is not None:
            gm_x, gm_y = scene._raycast_gm_xy(camera)
            gm_x += float(getattr(camera, 'image_width', 0) or 0) / 2.0
            gm_y += float(getattr(camera, 'image_height', 0) or 0) / 2.0

        # Opt-in breadcrumb trail: a faint dot per grid cell the camera has
        # visited, under everything else. Persisted on the scene (survives
        # across frames, naturally bounded by the maze's own cell count) --
        # mirrors handlers._record_trail_cell exactly.
        if show_trail and gm_x is not None:
            visited = getattr(scene, '_raycast_trail', None)
            if visited is None:
                visited = set()
                scene._raycast_trail = visited
            visited.add((int(gm_x // cs), int(gm_y // cs)))
            for (tgx, tgy) in sorted(visited):
                tx, ty = _px(tgx * cs + cs / 2.0, tgy * cs + cs / 2.0)
                self._draw_queue.append(dict(
                    type='rectangle', x1=tx - 1.0, y1=ty - 1.0,
                    x2=tx + 1.0, y2=ty + 1.0, color=trail_color, filled=True))

        # Opt-in object dots, under the player marker so a pickup sharing a
        # cell never hides it. Mirrors hud.py's marks loop.
        def _mark_points(object_name):
            if not object_name:
                return []
            pts = []
            to_gm = getattr(scene, '_raycast_gm_xy', None)
            if not callable(to_gm):
                return []
            for inst in (getattr(scene, 'instances', None) or ()):
                if getattr(inst, 'object_name', None) != object_name:
                    continue
                # Kivy is y-UP; the whole raycast pipeline works in GM's
                # y-down frame, so convert exactly as the camera marker below
                # does. Reading a raw position here would mirror every dot.
                gx, gy = to_gm(inst)
                pts.append((gx + float(getattr(inst, 'image_width', 0) or 0) / 2.0,
                            gy + float(getattr(inst, 'image_height', 0) or 0) / 2.0))
            return sorted(pts)

        for _colour, _pts in ((mark_color, _mark_points(mark_object)),
                              (mark_color_2, _mark_points(mark_object_2))):
            if not _colour or not _pts:
                continue
            for (wx, wy) in _pts:
                mx, my = _px(wx, wy)
                self._draw_queue.append(dict(
                    type='rectangle', x1=mx - 1.5, y1=my - 1.5,
                    x2=mx + 1.5, y2=my + 1.5, color=_colour, filled=True))

        if camera is None:
            return
        cx, cy = _px(gm_x, gm_y)
        _MM_MARK, _MM_HEAD = 2.0, 7.0
        self._draw_queue.append(dict(
            type='line', x1=cx - _MM_MARK, y1=cy, x2=cx + _MM_MARK, y2=cy,
            color=player_color))
        # GM 0=right/90=up vs screen y DOWN -> negate, as the renderers do.
        rad = math.radians(-float(getattr(camera, 'facing_angle', 0) or 0))
        self._draw_queue.append(dict(
            type='line', x1=cx, y1=cy,
            x2=cx + math.cos(rad) * _MM_HEAD,
            y2=cy + math.sin(rad) * _MM_HEAD,
            color=player_color))
'''
