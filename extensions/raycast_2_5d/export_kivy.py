"""Kivy export contribution of the raycast 2.5D extension (Stage C2b).

SCENE_CODE is class-body Python (4-space-indented methods) that
KivyExporter._inject_extension_scene_code drops into every generated scene
class at its __PYGM_EXTENSION_SCENE_CODE__ marker, AFTER .format() -- so the
{ } dict/set literals here are single, not doubled. It overrides the scene's
no-op _init_extensions / _render_extension_overlay hooks and carries the DDA
renderer, a faithful port of extensions/raycast_2_5d/renderer.py. Numeric
parity with desktop + HTML5 is pinned by tests/test_raycast_export_parity.py.
"""

SCENE_CODE = '''\n    def _init_extensions(self):
        # Per-scene raycast state (was in the scene __init__ before Stage C2b).
        self.raycast_camera = None
        self._raycast_group = None
        self._raycast_v_walls = None
        self._raycast_cell_size = None
        self._raycast_tex_cache = {}
        self._raycast_px_cache = {}

    def _render_extension_overlay(self):
        # Claim the frame when the raycast camera is enabled; the scene then
        # composites the HUD over this opaque overlay. Returns True if drawn.
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

    def _billboard_texture(self, inst):
        """Current-frame texture for a billboard instance (or None)."""
        tex = getattr(inst, '_sprite_texture', None)
        if tex is None:
            return self._raycast_texture(getattr(inst, 'sprite_name', None))
        frames = int(getattr(inst, '_sprite_frames', 1) or 1)
        if frames > 1:
            fw = int(getattr(inst, '_frame_w', 0) or tex.width)
            fh = int(getattr(inst, '_frame_h', 0) or tex.height)
            idx = int(getattr(inst, 'image_index', 0)) % frames
            return tex.get_region(idx * fw, 0, fw, fh)
        return tex

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
                      cam_cx, cam_cy, view_h=None):
        """Faithful port of _cast_floor_plane's cast into an RGBA byte buffer
        (returns buf, sw, sh). Camera-plane FOV-edge rays interpolated across
        columns; row distance 0.5*view_h/(y-horizon); texture tiled per grid
        cell. `pixels` is bottom-up (Kivy), so the source row is flipped to
        sample the tile the same way the desktop's top-down get_at does.

        view_h is the DOOM-bar letterbox height (the floor band is view_h/2
        tall and the projection reference is 0.5*view_h); None = full height."""
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
        pos_z = 0.5 * view_h
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
                            cam_cx, cam_cy, w, h, ceiling, view_h=None):
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
                                         cam_cy, view_h)
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
        if getattr(self, '_raycast_v_walls', None) is None \\
                or getattr(self, '_raycast_cell_size', None) != cell_size:
            self._build_raycast_walls(cell_size)

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
        if floor_px is not None:
            self._render_floor_plane(group, floor_px, cast_res, facing_screen_rad,
                                     fov_rad, cam_cx, cam_cy, w, h, False, view_h)
        ceil_name = cfg.get('ceiling_texture', '')
        if ceil_name and sky_tex is None:
            ceil_px = self._raycast_texture_pixels(ceil_name)
            if ceil_px is not None:
                self._render_floor_plane(group, ceil_px, cast_res, facing_screen_rad,
                                         fov_rad, cam_cx, cam_cy, w, h, True, view_h)

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

        for col in range(num_columns):
            camera_x = 2.0 * (col + 0.5) / num_columns - 1.0
            ray_offset = math.atan(plane_tan * camera_x)
            ray_angle = facing_screen_rad + ray_offset
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
            full_h = view_h * cell_size * self.RAYCAST_WALL_HEIGHT / max(corrected, 1e-4)
            y_bot = mid - full_h / 2.0           # y-up: bottom of the full strip
            x0 = int(col * col_width)
            x1 = int((col + 1) * col_width)
            strip_w = max(1, x1 - x0)
            # Clamp to the VIEW bottom, not the window bottom, so a close wall
            # never paints down into the reserved status-bar band.
            y0 = max(view_bottom, y_bot)
            y1 = min(h, y_bot + full_h)
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
                v0 = (y0 - y_bot) / full_h
                v1 = (y1 - y_bot) / full_h
                region = tex.get_region(tex_x, 0, 1, th)
                group.add(Color(shade, shade, shade, 1))
                group.add(Rectangle(texture=region, pos=(x0, y0),
                                    size=(strip_w, vis_h),
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
        billboards = []
        for inst in self.instances:
            if inst is camera or not getattr(inst, 'visible', True):
                continue
            if getattr(inst, 'solid', False):
                continue
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
            billboards.append((corrected_b, rel_angle, inst, iw, ih))

        billboards.sort(key=lambda b: -b[0])
        for corrected_b, rel_angle, inst, iw, ih in billboards:
            tex = self._billboard_texture(inst)
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
                group.add(Rectangle(texture=region, pos=(seg_x0, by0),
                                    size=(seg_x1 - seg_x0, b_vis_h),
                                    tex_coords=(0.0, bv0, 1.0, bv0,
                                                1.0, bv1, 0.0, bv1)))
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
    return (f"self._draw_minimap({x}, {y}, {size}, "
            f"{back!r}, {wall!r}, {player!r})")


ACTION_CODEGEN = {
    'set_facing_angle': _cg_set_facing_angle,
    'enable_raycast_view': _cg_enable_raycast_view,
    'draw_doom_hud': _cg_draw_doom_hud,
    'draw_minimap': _cg_draw_minimap,
}


# ---------------------------------------------------------------------------
# Base-object class-body code (Stage C2c). Injected into base_object.py at its
# __PYGM_EXTENSION_BASE_CODE__ marker (post-.format(), so { } are single). The
# draw_minimap action codegen emits a call to this _draw_minimap method.
# ---------------------------------------------------------------------------
BASE_OBJECT_CODE = '''\n    def _draw_minimap(self, x, y, size, back_color, wall_color, player_color):
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

        cfg = getattr(scene, 'raycast_camera', None) or {}
        camera = None
        finder = getattr(scene, '_find_raycast_camera', None)
        if callable(finder):
            camera = finder(cfg)
        if camera is None:
            return
        # The ray ORIGIN, not the sprite corner. _raycast_gm_xy converts Kivy's
        # y-up instance position back to the GM y-down frame the whole raycast
        # pipeline works in.
        gm_x, gm_y = scene._raycast_gm_xy(camera)
        cx, cy = _px(gm_x + float(getattr(camera, 'image_width', 0) or 0) / 2.0,
                     gm_y + float(getattr(camera, 'image_height', 0) or 0) / 2.0)
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
