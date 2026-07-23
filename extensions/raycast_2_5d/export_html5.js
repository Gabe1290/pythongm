// export_html5.js -- the 2.5D raycast renderer's HTML5 port (Stage C1b of
// docs/RAYCAST_EXTENSION_PLAN.md). The HTML5 exporter concatenates this at
// engine.js's __PYGM_EXTENSION_JS__ marker, AFTER all engine classes are
// defined, so it can augment GameRoom.prototype and register its room renderer.
// engine.js itself no longer names raycast. Mirrors the desktop
// extensions/raycast_2_5d/renderer.py; numeric parity is pinned by
// tests/test_raycast_export_parity.py. GameRoom.spriteTopLeft (the generic
// origin helper, mirrors core _sprite_top_left) stays in engine.js.

// Raycast wall-shading constants — MUST match game_runner.GameRoom's
// RAYCAST_* class attributes and the Kivy scene's, per
// tests/test_raycast_export_parity.py.
const RAYCAST_SIDE_SHADE = 0.85;    // y-face brightness (was a binary 0.5)
const RAYCAST_FOG_STRENGTH = 0.55;  // darkening at max render distance
const RAYCAST_MIN_SHADE = 0.35;     // never fully black
const RAYCAST_WALL_HEIGHT = 1.5;    // walls project this many x taller than a
                                    // cube (walls only, not billboards) -- see
                                    // game_runner RAYCAST_WALL_HEIGHT

Object.assign(GameRoom.prototype, {
    buildRaycastWalls(cellSize) {
        // Thin wall EDGES from solid instances (wide -> horizontal segment,
        // tall -> vertical, square -> all 4 edges), plus each edge's sprite
        // Image for texturing. Keys are "line,cell" strings.
        const vWalls = new Set(), hWalls = new Set();
        const vSprites = new Map(), hSprites = new Map();
        for (const inst of this.instances) {
            if (!inst.solid) continue;
            const width = inst.boxWidth(), height = inst.boxHeight();
            const spr = inst.sprite;
            if (width >= height * 1.5) {
                const tl = GameRoom.spriteTopLeft(inst);
                const lineY = Math.round((tl.y + height / 2) / cellSize);
                const col = Math.floor(tl.x / cellSize);
                hWalls.add(col + ',' + lineY); hSprites.set(col + ',' + lineY, spr);
            } else if (height >= width * 1.5) {
                const tl2 = GameRoom.spriteTopLeft(inst);
                const lineX = Math.round((tl2.x + width / 2) / cellSize);
                const row = Math.floor(tl2.y / cellSize);
                vWalls.add(lineX + ',' + row); vSprites.set(lineX + ',' + row, spr);
            } else {
                const gx = Math.floor(inst.x / cellSize), gy = Math.floor(inst.y / cellSize);
                vWalls.add(gx + ',' + gy); vWalls.add((gx + 1) + ',' + gy);
                hWalls.add(gx + ',' + gy); hWalls.add(gx + ',' + (gy + 1));
                vSprites.set(gx + ',' + gy, spr); vSprites.set((gx + 1) + ',' + gy, spr);
                hSprites.set(gx + ',' + gy, spr); hSprites.set(gx + ',' + (gy + 1), spr);
            }
        }
        this._vWalls = vWalls; this._hWalls = hWalls;
        this._vWallSprites = vSprites; this._hWallSprites = hSprites;
        this._raycastCellSize = cellSize;
    },

    castRay(px, py, angleRad, cellSize, maxCells) {
        const pxCell = px / cellSize, pyCell = py / cellSize;
        const dx = Math.cos(angleRad), dy = Math.sin(angleRad);
        let mapX = Math.floor(pxCell), mapY = Math.floor(pyCell);
        const deltaX = dx !== 0 ? Math.abs(1 / dx) : 1e30;
        const deltaY = dy !== 0 ? Math.abs(1 / dy) : 1e30;
        let stepX, sideX, stepY, sideY;
        if (dx < 0) { stepX = -1; sideX = (pxCell - mapX) * deltaX; }
        else { stepX = 1; sideX = (mapX + 1 - pxCell) * deltaX; }
        if (dy < 0) { stepY = -1; sideY = (pyCell - mapY) * deltaY; }
        else { stepY = 1; sideY = (mapY + 1 - pyCell) * deltaY; }
        let side = 0, distCells = maxCells;
        for (let i = 0; i < maxCells; i++) {
            let key, hit;
            if (sideX < sideY) {
                sideX += deltaX; mapX += stepX; side = 0;
                const lineX = stepX > 0 ? mapX : mapX + 1;
                key = lineX + ',' + mapY; hit = this._vWalls.has(key);
            } else {
                sideY += deltaY; mapY += stepY; side = 1;
                const lineY = stepY > 0 ? mapY : mapY + 1;
                key = mapX + ',' + lineY; hit = this._hWalls.has(key);
            }
            if (hit) {
                distCells = side === 0 ? (sideX - deltaX) : (sideY - deltaY);
                let wallCoord, sprite;
                if (side === 0) {
                    wallCoord = pyCell + distCells * dy;
                    if (dx > 0) wallCoord = -wallCoord;
                    sprite = this._vWallSprites.get(key);
                } else {
                    wallCoord = pxCell + distCells * dx;
                    if (dy < 0) wallCoord = -wallCoord;
                    sprite = this._hWallSprites.get(key);
                }
                const texU = wallCoord - Math.floor(wallCoord);
                return { dist: Math.max(distCells, 1e-4) * cellSize, side, hit: true, texU, sprite };
            }
        }
        return { dist: Math.max(distCells, 1e-4) * cellSize, side, hit: false, texU: 0, sprite: null };
    },

    _shadeColor(hex, factor) {
        // Multiply a #rrggbb by `factor` (default 0.5, the legacy half-shade).
        const f = (factor === undefined) ? 0.5 : factor;
        const h = String(hex).replace('#', '');
        if (h.length !== 6) return hex;
        const r = Math.round(parseInt(h.slice(0, 2), 16) * f);
        const g = Math.round(parseInt(h.slice(2, 4), 16) * f);
        const b = Math.round(parseInt(h.slice(4, 6), 16) * f);
        return `rgb(${r},${g},${b})`;
    }

    // Wall shading model — MUST match game_runner.GameRoom._wall_shade and the
    // Kivy scene's _wall_shade (pinned by tests/test_raycast_export_parity.py).
    // A subtle side hint + distance falloff; the old binary half-brightness
    // y-face made h/v junctions at equal distance read as false corners.
    wallShade(side, corrected, maxDist) {
        const sideFactor = (side === 1) ? RAYCAST_SIDE_SHADE : 1.0;
        let t = maxDist > 0 ? corrected / maxDist : 0.0;
        if (t < 0) t = 0; else if (t > 1) t = 1;
        const distFactor = 1.0 - RAYCAST_FOG_STRENGTH * t;
        return Math.max(RAYCAST_MIN_SHADE, sideFactor * distFactor);
    },

    renderRaycastView(ctx) {
        const cfg = this.raycastCamera;
        const cellSize = cfg.cell_size || 32;
        if (!this._vWalls || this._raycastCellSize !== cellSize) this.buildRaycastWalls(cellSize);

        const w = ctx.canvas.width, h = ctx.canvas.height;
        // DOOM-bar letterbox: the 3D view occupies only the top viewH px; the
        // band from viewH down to h is filled black and reserved for a status
        // bar. viewport_height 0 => full height, existing games unchanged.
        // Mirrors the desktop _render_raycast_view (game_runner.py).
        let viewH = cfg.viewport_height || h;
        viewH = Math.max(1, Math.min(viewH, h));
        const halfH = Math.floor(viewH / 2);
        // Flat floor/ceiling fills (sky + floor textures land in unit 3).
        ctx.fillStyle = cfg.ceiling_color || '#87CEEB'; ctx.fillRect(0, 0, w, halfH);
        ctx.fillStyle = cfg.floor_color || '#464632'; ctx.fillRect(0, halfH, w, viewH - halfH);

        const camera = this.findFirstInstance(cfg.camera_object || '');
        if (!camera) {
            if (viewH < h) { ctx.fillStyle = '#000000'; ctx.fillRect(0, viewH, w, h - viewH); }
            return;
        }
        const camTL = GameRoom.spriteTopLeft(camera);
        const camX = camTL.x + camera.boxWidth() / 2;
        const camY = camTL.y + camera.boxHeight() / 2;

        const wallColor = cfg.wall_color || '#993333';
        const fovRad = (cfg.fov || 66) * Math.PI / 180;
        const renderDist = cfg.render_distance || 20;
        const numCols = cfg.columns || Math.min(w, 320);
        const colWidth = w / numCols;
        const facingScreenRad = -camera.facing_angle * Math.PI / 180;
        const textured = cfg.wall_textured !== false;
        const sprites = (this._gameRef && this._gameRef.sprites) || {};
        const wallTex = cfg.wall_texture ? sprites[cfg.wall_texture] : null;

        // Sky (Phase 5b port): a panorama over the ceiling, panned by
        // facing_angle, never receding. pano_w = w*360/fov; blit at -pan + wrap.
        const skyTex = cfg.sky_texture ? sprites[cfg.sky_texture] : null;
        if (skyTex && skyTex.complete && skyTex.width > 0) {
            const panoW = Math.max(1, Math.floor(w * 360 / Math.max(1, cfg.fov || 66)));
            const pan = Math.floor((((camera.facing_angle % 360) + 360) % 360) / 360 * panoW);
            ctx.drawImage(skyTex, 0, 0, skyTex.width, skyTex.height, -pan, 0, panoW, halfH);
            if (panoW - pan < w) {
                ctx.drawImage(skyTex, 0, 0, skyTex.width, skyTex.height, panoW - pan, 0, panoW, halfH);
            }
        }

        // Floor (and, indoors, ceiling) texture casting (Phase 5 port). Low-res
        // per-pixel cast + upscale — full-res was ~13x too slow on desktop;
        // res comes from cfg.floor_cast_res (default 4, desktop parity — the
        // browser has ample headroom, timing spike measured res=2 at ~0.4ms).
        // floor_texture casts the floor; ceiling_texture casts the ceiling ONLY
        // when no sky claimed it. Absent both -> the flat fills above stand.
        const castRes = Math.max(1, Math.floor(cfg.floor_cast_res || 4));
        const floorTex = cfg.floor_texture ? this._textureData(sprites[cfg.floor_texture]) : null;
        const camCx = camX / cellSize, camCy = camY / cellSize;
        if (floorTex) {
            this.castFloorPlane(ctx, floorTex, camCx, camCy, facingScreenRad, fovRad, castRes, false, viewH);
        }
        const ceilTex = (cfg.ceiling_texture && !skyTex)
            ? this._textureData(sprites[cfg.ceiling_texture]) : null;
        if (ceilTex) {
            this.castFloorPlane(ctx, ceilTex, camCx, camCy, facingScreenRad, fovRad, castRes, true, viewH);
        }

        // CAMERA-PLANE projection (not uniform-angle) — screen columns are
        // evenly spaced, so rays must be evenly spaced on the camera plane:
        // ray_dir = dir + plane * cameraX, i.e. the off-centre angle is
        // atan(tan(fov/2) * cameraX), NOT a linear ramp. Uniform-angle sampling
        // drawn at uniform screen x isn't a perspective projection and BENDS
        // straight walls (they looked like they had a corner). Matches
        // game_runner and the floor cast.
        const planeTan = Math.tan(fovRad / 2);
        const colWallDist = new Array(numCols).fill(Infinity);  // for billboard occlusion
        for (let col = 0; col < numCols; col++) {
            const cameraX = 2.0 * (col + 0.5) / numCols - 1.0;
            const rayOffset = Math.atan(planeTan * cameraX);
            const r = this.castRay(camX, camY, facingScreenRad + rayOffset, cellSize, renderDist);
            if (!r.hit) continue;  // open sight-line: leave floor/ceiling/sky showing
            const corrected = r.dist * Math.cos(rayOffset);  // fisheye correction
            colWallDist[col] = corrected;
            // TRUE (unclamped) height; the TEXTURE is CROPPED to the visible
            // span rather than the whole texture being squeezed into a
            // screen-clamped strip. Squeezing was the real "bent wall" bug --
            // close columns clamped and compressed the entire brick texture
            // while farther columns didn't, breaking the courses across a flat
            // wall, with the boundary marching along as you moved.
            const fullH = viewH * cellSize * RAYCAST_WALL_HEIGHT / Math.max(corrected, 1e-4);
            const yTop = halfH - fullH / 2;
            const x0 = Math.floor(col * colWidth), x1 = Math.floor((col + 1) * colWidth);
            const stripW = Math.max(1, x1 - x0);
            const y0 = Math.max(0, Math.floor(yTop));
            const y1 = Math.min(viewH, Math.ceil(yTop + fullH));
            const visH = y1 - y0;
            if (visH <= 0) continue;
            // Subtle side hint + distance falloff (see wallShade).
            const shade = this.wallShade(r.side, corrected, renderDist * cellSize);
            const texSprite = wallTex || r.sprite;
            if (textured && texSprite && texSprite.complete && texSprite.width > 0) {
                const tw = texSprite.width, th = texSprite.height;
                const texX = Math.min(tw - 1, Math.max(0, Math.floor(r.texU * tw)));
                // FLOAT source rows — drawImage samples sub-texel, so no
                // per-column snapping to whole texels (which on a close wall,
                // where one texel spans tens of screen px, produced jagged
                // edges). Canvas interpolates for us; nothing to round.
                const v0 = (y0 - yTop) / fullH, v1 = (y1 - yTop) / fullH;
                const srcY = Math.max(0, Math.min(th, v0 * th));
                const srcH = Math.max(1e-3, Math.min(th - srcY, (v1 - v0) * th));
                ctx.drawImage(texSprite, texX, srcY, 1, srcH, x0, y0, stripW, visH);
                if (shade < 1.0) {
                    ctx.fillStyle = `rgba(0,0,0,${(1 - shade).toFixed(3)})`;
                    ctx.fillRect(x0, y0, stripW, visH);
                }
            } else {
                ctx.fillStyle = this._shadeColor(wallColor, shade);
                ctx.fillRect(x0, y0, stripW, visH);
            }
        }

        // Billboard sprites (Phase 6 port): every visible, non-solid, sprited
        // instance as a camera-facing sprite scaled by distance, with real
        // per-column occlusion against colWallDist (farthest-first).
        const billboards = [];
        for (const inst of this.instances) {
            if (inst === camera || !inst.visible || !inst.sprite || inst.solid) continue;
            if (!inst.sprite.complete || inst.sprite.width <= 0) continue;
            const bTL = GameRoom.spriteTopLeft(inst);
            const bx = bTL.x + inst.boxWidth() / 2, by = bTL.y + inst.boxHeight() / 2;
            const ddx = bx - camX, ddy = by - camY;
            const bdist = Math.hypot(ddx, ddy);
            if (bdist < 1e-4) continue;
            let relAngle = Math.atan2(ddy, ddx) - facingScreenRad;
            relAngle = ((relAngle + Math.PI) % (2 * Math.PI) + 2 * Math.PI) % (2 * Math.PI) - Math.PI;
            if (Math.abs(relAngle) > fovRad / 2 + 0.5) continue;  // margin for width
            const bcorr = bdist * Math.cos(relAngle);
            if (bcorr <= 1e-4) continue;
            billboards.push({ corr: bcorr, relAngle: relAngle, inst: inst });
        }
        billboards.sort((a, b) => b.corr - a.corr);  // farthest first (painter's)
        for (const b of billboards) {
            // Unclamped height + a CROPPED (float, sub-texel) source slice —
            // same as the wall pass. Squeezing a walked-into sprite into a
            // screen-clamped height distorted it.
            const fullH = viewH * b.inst.boxHeight() / Math.max(b.corr, 1e-4);
            const spriteW = Math.floor(viewH * b.inst.boxWidth() / Math.max(b.corr, 1e-4));
            if (spriteW < 1 || fullH < 1) continue;
            // Same camera-plane mapping as the wall pass, so billboards line up
            // with the walls instead of drifting toward the screen edges.
            const bCameraX = planeTan ? Math.tan(b.relAngle) / planeTan : 0;
            const colCenter = (bCameraX + 1) * 0.5 * numCols;
            const xLeft = Math.floor(colCenter * colWidth - spriteW / 2);
            const yTopF = halfH - fullH / 2;
            const by0 = Math.max(0, Math.floor(yTopF));
            const by1 = Math.min(viewH, Math.ceil(yTopF + fullH));
            const bVisH = by1 - by0;
            if (bVisH <= 0) continue;
            const img = b.inst.sprite;
            const bv0 = (by0 - yTopF) / fullH, bv1 = (by1 - yTopF) / fullH;
            const bSrcY = Math.max(0, Math.min(img.height, bv0 * img.height));
            const bSrcH = Math.max(1e-3, Math.min(img.height - bSrcY,
                                                  (bv1 - bv0) * img.height));
            for (let sx = 0; sx < spriteW; sx++) {
                const screenX = xLeft + sx;
                if (screenX < 0 || screenX >= w) continue;
                const colIdx = Math.min(numCols - 1, Math.max(0, Math.floor(screenX / colWidth)));
                if (b.corr < colWallDist[colIdx]) {  // unoccluded by a nearer wall
                    const srcX = Math.min(img.width - 1, Math.floor(sx / spriteW * img.width));
                    ctx.drawImage(img, srcX, bSrcY, 1, bSrcH, screenX, by0, 1, bVisH);
                }
            }
        }

        // DOOM-bar letterbox: fill the reserved band below the 3D view black,
        // before the draw-event pass composites the status bar over it. No-op
        // at full height (viewH === h).
        if (viewH < h) { ctx.fillStyle = '#000000'; ctx.fillRect(0, viewH, w, h - viewH); }
    },

    // Cached ImageData for a loaded sprite, for per-pixel floor sampling.
    // Drawn once into an offscreen canvas; returns null for an unloaded or
    // cross-origin-tainted image (the caller then keeps the flat fill).
    _textureData(sprite) {
        if (!sprite || !sprite.complete || !sprite.width) return null;
        if (!this._texDataCache) this._texDataCache = new Map();
        if (this._texDataCache.has(sprite)) return this._texDataCache.get(sprite);
        let data = null;
        try {
            const c = document.createElement('canvas');
            c.width = sprite.width; c.height = sprite.height;
            const g = c.getContext('2d');
            g.drawImage(sprite, 0, 0);
            data = g.getImageData(0, 0, sprite.width, sprite.height);
        } catch (e) {
            data = null;  // tainted canvas — skip textured floor for this sprite
        }
        this._texDataCache.set(sprite, data);
        return data;
    }

    // Low-res floor/ceiling texture casting (faithful port of
    // game_runner._cast_floor_plane). Fills a downsampled ImageData per-pixel
    // by sampling `texData` in CELL units (so the texture tiles once per grid
    // cell and meets the wall bases), then upscales with drawImage. `ceiling`
    // mirrors the same cast into the top half via a vertical flip.
    castFloorPlane(ctx, texData, camCx, camCy, facingScreenRad, fovRad, res, ceiling, viewH) {
        const w = ctx.canvas.width, h = ctx.canvas.height;
        // Letterbox: cast into the shrunk 3D view's floor/ceiling, so the
        // horizon and projection reference are viewH, not the true height.
        // Undefined viewH keeps the legacy full-height behaviour.
        if (viewH === undefined || viewH === null) viewH = h;
        viewH = Math.max(1, Math.min(viewH, h));
        const halfH = Math.floor(viewH / 2);
        const regionH = viewH - halfH;
        if (regionH <= 0) return;
        const tw = texData.width, th = texData.height, src = texData.data;
        if (tw <= 0 || th <= 0) return;
        const dirX = Math.cos(facingScreenRad), dirY = Math.sin(facingScreenRad);
        const plane = Math.tan(fovRad / 2);
        const planeX = -dirY * plane, planeY = dirX * plane;
        const rdx0 = dirX - planeX, rdy0 = dirY - planeY;
        const rdx1 = dirX + planeX, rdy1 = dirY + planeY;
        const posZ = 0.5 * viewH;
        const sw = Math.max(1, Math.floor(w / res));
        const sh = Math.max(1, Math.floor(regionH / res));
        const stepScale = res / w;
        if (!this._floorSmall) this._floorSmall = document.createElement('canvas');
        const small = this._floorSmall;
        if (small.width !== sw || small.height !== sh) { small.width = sw; small.height = sh; }
        const sctx = small.getContext('2d');
        const img = sctx.createImageData(sw, sh);
        const d = img.data;
        for (let j = 0; j < sh; j++) {
            const y = halfH + j * res;
            let p = y - halfH; if (p <= 0) p = 1;
            const rowd = posZ / p;
            const stepx = rowd * (rdx1 - rdx0) * stepScale;
            const stepy = rowd * (rdy1 - rdy0) * stepScale;
            let fx = camCx + rowd * rdx0;
            let fy = camCy + rowd * rdy0;
            let di = j * sw * 4;
            for (let i = 0; i < sw; i++) {
                let tx = (tw * (fx - Math.floor(fx))) | 0;
                let ty = (th * (fy - Math.floor(fy))) | 0;
                if (tx >= tw) tx = tw - 1;
                if (ty >= th) ty = th - 1;
                const si = (ty * tw + tx) * 4;
                d[di] = src[si]; d[di + 1] = src[si + 1]; d[di + 2] = src[si + 2]; d[di + 3] = 255;
                di += 4;
                fx += stepx; fy += stepy;
            }
        }
        sctx.putImageData(img, 0, 0);
        if (ceiling) {
            ctx.save();
            ctx.scale(1, -1);   // flip vertically into the top half
            ctx.drawImage(small, 0, 0, sw, sh, 0, -regionH, w, regionH);
            ctx.restore();
        } else {
            ctx.drawImage(small, 0, 0, sw, sh, 0, halfH, w, regionH);
        }
    }
});

// The render hook: claim any room whose raycast camera is enabled. Replaces
// engine.js's old inline dispatch -- the engine now gives every room to
// renderExtensionRoom() first (Stage C1a).
registerRoomRenderer(function(room, ctx) {
    if (room.raycastCamera && room.raycastCamera.enabled) {
        room.renderRaycastView(ctx);
        return true;
    }
    return false;
});

// ---------------------------------------------------------------------------
// Raycast ACTIONS (Stage C1c). Registered into engine.js's action switch
// via its default case (registerExtensionAction), so engine.js's
// executeAction no longer enumerates any raycast action. Each mirrors the
// desktop handler in extensions/raycast_2_5d/handlers.py; the (obj, params,
// game) args are the acting instance / action params / the Game.
// ---------------------------------------------------------------------------

registerExtensionAction('draw_doom_hud', function(obj, params, game) {
                // DOOM-style bottom status bar. A MACRO action: emits ordinary
                // rectangle/line/text/sprite/lives commands, so obj target
                // needs no new renderer. Mirrors build_doom_hud_commands() in
                // runtime/action_executor.py — parity-tested against it.
                const dhHeight = parseNumParam(params.height, obj, 42);
                const winH = (game && game.canvas) ? game.canvas.height : 480;
                const winW = (game && game.canvas) ? game.canvas.width : 640;
                let dhY = parseNumParam(params.y, obj, -1);
                if (dhY < 0) dhY = winH - dhHeight;
                const dhX = parseNumParam(params.x, obj, 0);
                const dhW = parseNumParam(params.width, obj, 0) || winW;
                const dhHealth = game ? game.health : 100;
                const dhScore = game ? game.score : 0;
                const dhLives = game ? game.lives : 0;
                const backColor = params.back_color || '#101010';
                const dividerColor = params.divider_color || '#505050';
                const textColor = params.text_color || '#ffffff';
                const barColor = params.bar_color || '#20c020';
                const hbw = parseNumParam(params.health_bar_width, obj, 90);
                const hbh = parseNumParam(params.health_bar_height, obj, 14);
                const pad = 8;
                // back panel + top divider
                obj._draw_queue.push({type: 'rectangle', x1: dhX, y1: dhY,
                    x2: dhX + dhW, y2: dhY + dhHeight, color: backColor, filled: true});
                obj._draw_queue.push({type: 'line', x1: dhX, y1: dhY,
                    x2: dhX + dhW, y2: dhY, color: dividerColor});
                // health readout (left third)
                const dhHx = dhX + pad, dhBarY = dhY + 22;
                obj._draw_queue.push({type: 'text', text: String(params.health_label || 'Health'),
                    x: dhHx, y: dhY + 4, color: textColor});
                obj._draw_queue.push({type: 'rectangle', x1: dhHx, y1: dhBarY,
                    x2: dhHx + hbw, y2: dhBarY + hbh, color: dividerColor, filled: true});
                const dhFrac = Math.min(1, Math.max(0, dhHealth / 100));
                obj._draw_queue.push({type: 'rectangle', x1: dhHx, y1: dhBarY,
                    x2: dhHx + hbw * dhFrac, y2: dhBarY + hbh, color: barColor, filled: true});
                obj._draw_queue.push({type: 'text', text: String(Math.floor(dhHealth)),
                    x: dhHx + hbw + 6, y: dhBarY - 2, color: textColor});
                // face icon (centre)
                const faceSprite = params.face_sprite || '';
                if (faceSprite) {
                    const dhFrames = Math.max(1, parseNumParam(params.face_frames, obj, 4));
                    const dhFrame = Math.min(dhFrames - 1, Math.floor((1 - dhFrac) * dhFrames));
                    obj._draw_queue.push({type: 'sprite', sprite_name: faceSprite,
                        x: dhX + dhW / 2 - dhHeight / 2, y: dhY + 2, subimage: dhFrame});
                }
                // score + lives (right third)
                const dhRx = dhX + dhW * 2 / 3 + pad;
                obj._draw_queue.push({type: 'text',
                    text: String(params.score_label || 'Score: ') + dhScore,
                    x: dhRx, y: dhY + 4, color: textColor});
                obj._draw_queue.push({type: 'lives', count: dhLives, x: dhRx,
                    y: dhY + dhHeight - 20, sprite: params.lives_sprite || '',
                    scale: parseNumParam(params.lives_scale, obj, 1)});
                // objective (far-right edge)
                obj._draw_queue.push({type: 'text',
                    text: String(params.objective_label || 'Keys: ') +
                          gmExpressionValue(params.objective_value, obj, game),
                    x: dhX + dhW - 96, y: dhY + dhHeight / 2 - 8, color: textColor});
                return;
            });

registerExtensionAction('draw_minimap', function(obj, params, game) {
                // North-up minimap of the raycast room's wall edges. A MACRO
                // action: it emits ordinary rectangle/line commands, so obj
                // target needed no new renderer. Mirrors
                // build_minimap_commands() in runtime/action_executor.py —
                // tests/test_raycast_export_parity.py compares the two.
                const room = game.currentRoom;
                if (!room) return;
                const mmX = parseNumParam(params.x, obj, 0);
                const mmY = parseNumParam(params.y, obj, 0);
                const mmSize = parseNumParam(params.size, obj, 120);
                const backColor = params.back_color || '#101018';
                const wallColor = params.wall_color || '#8080a0';
                const playerColor = params.player_color || '#ffd040';

                obj._draw_queue.push({
                    type: 'rectangle',
                    x1: mmX, y1: mmY, x2: mmX + mmSize, y2: mmY + mmSize,
                    color: backColor, filled: true,
                });

                const mmSpan = Math.max(room.width || 0, room.height || 0);
                const mmCS = room._raycastCellSize || 0;
                if (mmSpan <= 0 || !mmCS) return;
                const mmScale = mmSize / mmSpan;
                const mmPx = (wx, wy) => [mmX + wx * mmScale, mmY + wy * mmScale];

                // Wall sets are unordered; sort so all three targets emit the
                // same picture in the same order (the parity test diffs it).
                const mmKeys = (set) => [...(set || [])]
                    .map(k => k.split(',').map(Number))
                    .sort((a, b) => (a[0] - b[0]) || (a[1] - b[1]));

                for (const [lineX, row] of mmKeys(room._vWalls)) {
                    const [x1, y1] = mmPx(lineX * mmCS, row * mmCS);
                    const [x2, y2] = mmPx(lineX * mmCS, (row + 1) * mmCS);
                    obj._draw_queue.push({type: 'line', x1, y1, x2, y2, color: wallColor});
                }
                for (const [col, lineY] of mmKeys(room._hWalls)) {
                    const [x1, y1] = mmPx(col * mmCS, lineY * mmCS);
                    const [x2, y2] = mmPx((col + 1) * mmCS, lineY * mmCS);
                    obj._draw_queue.push({type: 'line', x1, y1, x2, y2, color: wallColor});
                }

                const mmCfg = room.raycastCamera || {};
                const mmCam = room.findFirstInstance(mmCfg.camera_object || '');
                if (!mmCam) return;
                // The ray ORIGIN, not the sprite corner — same point
                // renderRaycastView casts from.
                const mmTL = GameRoom.spriteTopLeft(mmCam);
                const [cx, cy] = mmPx(mmTL.x + mmCam.boxWidth() / 2,
                                      mmTL.y + mmCam.boxHeight() / 2);
                const MM_MARK = 2.0, MM_HEAD = 7.0;
                obj._draw_queue.push({
                    type: 'line', x1: cx - MM_MARK, y1: cy, x2: cx + MM_MARK, y2: cy,
                    color: playerColor,
                });
                // GM 0=right/90=up vs screen y DOWN -> negate, as the
                // renderers do.
                const mmRad = -(mmCam.facing_angle || 0) * Math.PI / 180;
                obj._draw_queue.push({
                    type: 'line', x1: cx, y1: cy,
                    x2: cx + Math.cos(mmRad) * MM_HEAD,
                    y2: cy + Math.sin(mmRad) * MM_HEAD,
                    color: playerColor,
                });
                return;
            });

registerExtensionAction('set_facing_angle', function(obj, params, game) {
                // Raycast camera look direction (see execute_set_facing_angle_action).
                const fa = parseNumParam(params.angle, obj, 0);
                const rel = params.relative === true || params.relative === 'true' ||
                            params.relative === 1 || params.relative === '1';
                obj.facing_angle = rel
                    ? ((obj.facing_angle + fa) % 360 + 360) % 360
                    : ((fa % 360) + 360) % 360;
                return;
            });

registerExtensionAction('enable_raycast_view', function(obj, params, game) {
                // Switch the room to / from the Doom-style first-person raycast
                // view (mirrors execute_enable_raycast_view_action). Config
                // lives on the room, like views; the renderer is GameRoom
                // .renderRaycastView.
                if (!game || !game.currentRoom) return;
                const rEnable = !(params.enable === false || params.enable === 'false' ||
                                  params.enable === 0 || params.enable === '0');
                if (!rEnable) {
                    game.currentRoom.raycastCamera = { enabled: false };
                    return;
                }
                const rNum = (k, d) => {
                    const n = parseNumParam(params[k], obj, d);
                    return (typeof n === 'number' && isFinite(n)) ? n : d;
                };
                game.currentRoom.raycastCamera = {
                    enabled: true,
                    camera_object: params.camera_object || obj.name,
                    fov: rNum('fov', 66),
                    render_distance: Math.floor(rNum('render_distance', 20)),
                    cell_size: Math.floor(rNum('cell_size', 32)),
                    columns: Math.floor(rNum('columns', 320)),
                    wall_color: params.wall_color || '#993333',
                    floor_color: params.floor_color || '#464632',
                    ceiling_color: params.ceiling_color || '#87CEEB',
                    wall_texture: params.wall_texture || '',
                    wall_textured: !(params.wall_textured === false ||
                                     params.wall_textured === 'false'),
                    sky_texture: params.sky_texture || '',
                    floor_texture: params.floor_texture || '',
                    ceiling_texture: params.ceiling_texture || '',
                    floor_cast_res: Math.max(1, Math.floor(rNum('floor_cast_res', 4))),
                    // DOOM-bar letterbox (0 = full height). renderRaycastView
                    // reads obj; without it here an exported game ignores a
                    // viewport_height the desktop runtime honours.
                    viewport_height: Math.floor(rNum('viewport_height', 0)),
                };
                game.currentRoom._vWalls = null;  // rebuild wall map next render
                return;
            });
