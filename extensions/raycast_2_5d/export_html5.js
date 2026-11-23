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
// The vertical model (renderer.py, stairs plan S4), in grid cells: the eye is
// RAYCAST_EYE_HEIGHT above the floor; walls and the ceiling rise to the
// camera's wall_height (default RAYCAST_WALL_HEIGHT); a wall texture covers
// RAYCAST_TEXTURE_HEIGHT and repeats above that, anchored at the floor.
const RAYCAST_EYE_HEIGHT = 0.75;
const RAYCAST_TEXTURE_HEIGHT = 1.5;
const RAYCAST_EYE_FROM_TILE_TOP = (RAYCAST_TEXTURE_HEIGHT - RAYCAST_EYE_HEIGHT) / RAYCAST_TEXTURE_HEIGHT;
const RAYCAST_MIN_WALL_HEIGHT = 1.0;
const RAYCAST_MAX_WALL_HEIGHT = 10.0;

function raycastClampWallHeight(value) {
    const v = Number(value);
    if (value === undefined || value === null || value === '' || !Number.isFinite(v)) {
        return RAYCAST_WALL_HEIGHT;
    }
    return Math.min(RAYCAST_MAX_WALL_HEIGHT, Math.max(RAYCAST_MIN_WALL_HEIGHT, v));
}

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
    },

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
        const wallH = raycastClampWallHeight(cfg.wall_height);
        const wallTiles = wallH / RAYCAST_TEXTURE_HEIGHT;      // 1 for default walls
        const nTiles = Math.max(1, Math.ceil(wallTiles - 1e-9));
        // Rebuilt every frame (parity with the desktop renderer.py fix,
        // 2026-10-06) so a solid instance created/destroyed at runtime shows
        // up immediately instead of only on room re-entry/cell_size change.
        this.buildRaycastWalls(cellSize);
        // Stairs (S10): the floor-height map, rebuilt every frame like the
        // walls. Empty -> the single-hit path below, unchanged.
        const floorMap = this.buildFloorHeights(cellSize, raycastMaxFloorHeight(cellSize, wallH));
        const heights = floorMap.heights;
        // Lowered ceilings (ceilings plan, C3): rebuilt every frame as well; a
        // non-empty map takes the two-clip column walk even without steps.
        const ceilMap = this.buildCeilingHeights(cellSize, wallH * cellSize, heights,
                                                 RAYCAST_EYE_HEIGHT * cellSize);
        const ceilings = ceilMap.ceilings;
        const stairs = heights.size > 0 || ceilings.size > 0;

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
        // Eye height: the floor under the camera (eased by the climbing hook)
        // plus the eye height.
        let floorZ = 0;
        if (stairs) {
            floorZ = (typeof this._raycastEyeFloor === 'number') ? this._raycastEyeFloor
                : (heights.get(Math.floor(camX / cellSize) + ',' + Math.floor(camY / cellSize)) || 0);
        }
        const eyeZ = floorZ + RAYCAST_EYE_HEIGHT * cellSize;
        const eyeCells = eyeZ / cellSize;

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
        if (floorTex && !stairs) {      // stairs rooms: castStairsFloor, below
            this.castFloorPlane(ctx, floorTex, camCx, camCy, facingScreenRad, fovRad, castRes, false, viewH);
        }
        const ceilTex = (cfg.ceiling_texture && !skyTex)
            ? this._textureData(sprites[cfg.ceiling_texture]) : null;
        if (ceilTex) {
            // The ceiling plane is the top of the walls: (wallH - eye) above the eye.
            this.castFloorPlane(ctx, ceilTex, camCx, camCy, facingScreenRad, fovRad, castRes, true, viewH,
                                stairs ? wallH - eyeCells : wallH - RAYCAST_EYE_HEIGHT);
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
        const stairsLayouts = [];
        const sf = stairs ? {
            stepTextures: floorMap.textures, sprites, camX, camY, eyeZ, floorZ,
            cellSize, halfH, viewH, colWidth, textured, wallTex, wallColor,
            floorColor: cfg.floor_color || '#464632', maxDist: renderDist * cellSize,
            wallTopZ: wallH * cellSize, ceilingColor: cfg.ceiling_color || '#87CEEB',
        } : null;
        for (let col = 0; col < numCols; col++) {
            const cameraX = 2.0 * (col + 0.5) / numCols - 1.0;
            const rayOffset = Math.atan(planeTan * cameraX);
            if (stairs) {
                const cosOff = Math.cos(rayOffset);
                let lay;
                if (ceilings.size) {              // lowered ceilings: the two-clip walk (C3)
                    const rs = this.castRaySteps(camX, camY, facingScreenRad + rayOffset, cellSize,
                                                 renderDist, heights, ceilings);
                    const camKey = Math.floor(camX / cellSize) + ',' + Math.floor(camY / cellSize);
                    lay = raycastLayoutColumnCeilings(rs.crossings, rs.hit, floorZ,
                                                      ceilings.has(camKey) ? ceilings.get(camKey) : null,
                                                      eyeZ, wallH * cellSize, cellSize, cosOff, halfH,
                                                      viewH, renderDist);
                } else {
                    const rs = this.castRaySteps(camX, camY, facingScreenRad + rayOffset, cellSize,
                                                 renderDist, heights);
                    lay = raycastLayoutColumn(rs.crossings, rs.hit, floorZ, eyeZ,
                                              wallH * cellSize, cellSize, cosOff, halfH, viewH,
                                              renderDist);
                }
                stairsLayouts.push(lay);
                colWallDist[col] = lay.wallDist;
                continue;
            }
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
            // tileH: one texture tile's projected height (the whole wall for
            // the default wall_height); yTile0: the bottom tile's top. Tiles
            // stack upward from the floor -- same as renderer.py.
            const tileH = viewH * cellSize * RAYCAST_TEXTURE_HEIGHT / Math.max(corrected, 1e-4);
            const yTile0 = halfH - tileH * RAYCAST_EYE_FROM_TILE_TOP;
            const yWallTop = yTile0 - (wallTiles - 1) * tileH;
            const x0 = Math.floor(col * colWidth), x1 = Math.floor((col + 1) * colWidth);
            const stripW = Math.max(1, x1 - x0);
            const y0 = Math.max(0, Math.floor(yWallTop));
            const y1 = Math.min(viewH, Math.ceil(yTile0 + tileH));
            const visH = y1 - y0;
            if (visH <= 0) continue;
            // Subtle side hint + distance falloff (see wallShade).
            const shade = this.wallShade(r.side, corrected, renderDist * cellSize);
            const texSprite = wallTex || r.sprite;
            if (textured && texSprite && texSprite.complete && texSprite.width > 0) {
                const tw = texSprite.width, th = texSprite.height;
                const texX = Math.min(tw - 1, Math.max(0, Math.floor(r.texU * tw)));
                // One cropped drawImage per texture tile, bottom tile first;
                // the top tile is cut at the wall's real top.
                for (let k = 0; k < nTiles; k++) {
                    const segTop = yTile0 - k * tileH;
                    const sy0 = Math.max(0, Math.floor(Math.max(segTop, yWallTop)));
                    const sy1 = Math.min(viewH, Math.ceil(segTop + tileH));
                    if (sy1 - sy0 <= 0) continue;
                    // FLOAT source rows — drawImage samples sub-texel, so no
                    // per-column snapping to whole texels (which on a close
                    // wall, where one texel spans tens of screen px, produced
                    // jagged edges). Canvas interpolates for us.
                    const v0 = (sy0 - segTop) / tileH, v1 = (sy1 - segTop) / tileH;
                    const srcY = Math.max(0, Math.min(th, v0 * th));
                    const srcH = Math.max(1e-3, Math.min(th - srcY, (v1 - v0) * th));
                    ctx.drawImage(texSprite, texX, srcY, 1, srcH, x0, sy0, stripW, sy1 - sy0);
                }
                if (shade < 1.0) {
                    ctx.fillStyle = `rgba(0,0,0,${(1 - shade).toFixed(3)})`;
                    ctx.fillRect(x0, y0, stripW, visH);
                }
            } else {
                ctx.fillStyle = this._shadeColor(wallColor, shade);
                ctx.fillRect(x0, y0, stripW, visH);
            }
        }

        if (stairs) {
            // Floor cast (textured floor or any step top texture), then
            // risers + walls at full resolution on top.
            const topTex = new Map();
            for (const [key, tex] of floorMap.textures) {
                const td = tex[0] ? this._textureData(sprites[tex[0]]) : null;
                if (td) topTex.set(key, td);
            }
            const floorCast = !!floorTex || topTex.size > 0;
            if (floorCast) {
                this.castStairsFloor(ctx, stairsLayouts, sf, floorTex, topTex, facingScreenRad,
                                     fovRad, castRes);
            }
            // Lowered ceilings (C4): cast textured when the camera or any marker has
            // a ceiling texture; otherwise their spans stay crisp flat fills.
            const cellCeilTex = new Map();
            for (const [key, name] of ceilMap.textures) {
                const td = name ? this._textureData(sprites[name]) : null;
                if (td) cellCeilTex.set(key, td);
            }
            const ceilDefault = cfg.ceiling_texture ? this._textureData(sprites[cfg.ceiling_texture]) : null;
            const ceilingCast = ceilings.size > 0 && (cellCeilTex.size > 0 || !!ceilDefault);
            if (ceilingCast) {
                this.castCeilingSpans(ctx, stairsLayouts, sf, cellCeilTex, ceilDefault, facingScreenRad,
                                      fovRad, castRes);
            }
            for (let col = 0; col < stairsLayouts.length; col++) {
                this.drawStairsColumn(ctx, sf, col, stairsLayouts[col], floorCast, ceilingCast);
            }
        }

        // Billboard sprites (Phase 6 port): every visible, non-solid, sprited
        // instance as a camera-facing sprite scaled by distance, with real
        // per-column occlusion against colWallDist (farthest-first).
        const billboards = [];
        for (const inst of this.instances) {
            if (inst === camera || !inst.visible || !inst.sprite || inst.solid) continue;
            if (raycastIsGeometry(inst)) continue;   // a step / ceiling marker is geometry, not a cutout
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
            billboards.push({ corr: bcorr, relAngle: relAngle, inst: inst, bx: bx, by: by });
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
            let yTopF = halfH - fullH / 2;
            if (stairs) {
                // Stands on the floor of its own cell (renderer.py, S7).
                const bFloor = heights.get(Math.floor(b.bx / cellSize) + ',' +
                                           Math.floor(b.by / cellSize)) || 0;
                yTopF += (eyeZ - (bFloor + RAYCAST_EYE_HEIGHT * cellSize)) * viewH /
                    Math.max(b.corr, 1e-4);
            }
            const by0 = Math.max(0, Math.floor(yTopF));
            const by1 = Math.min(viewH, Math.ceil(yTopF + fullH));
            const bVisH = by1 - by0;
            if (bVisH <= 0) continue;
            const img = b.inst.sprite;
            // Which frame of the sprite's horizontal strip to show. A
            // billboard_rotation_frames instance (set_billboard_rotation)
            // picks its frame by viewing angle (Doom/Build actor-rotation
            // trick: a 2D sprite with real "sides" instead of always the
            // same flat cutout) -- see renderer.billboard_rotation_frame
            // for the shared formula. Otherwise the normal animated
            // image_index frame draws, same as before this feature.
            const frames = b.inst.spriteInfo ? (b.inst.spriteInfo.frames || 1) : 1;
            const rotFrames = b.inst.billboard_rotation_frames || 0;
            let frameIdx;
            if (rotFrames > 1) {
                const facingRad = -(b.inst.facing_angle || 0) * Math.PI / 180;
                const viewRad = Math.atan2(camY - b.by, camX - b.bx);
                const relRot = ((viewRad - facingRad) % (2 * Math.PI) + 2 * Math.PI) % (2 * Math.PI);
                const step = (2 * Math.PI) / rotFrames;
                frameIdx = Math.round(relRot / step) % rotFrames;
            } else {
                frameIdx = Math.floor(b.inst.image_index || 0);
            }
            frameIdx = ((frameIdx % frames) + frames) % frames;
            const fw = b.inst.boxWidth(), fh = b.inst.boxHeight();
            const srcXBase = frameIdx * fw;
            const bv0 = (by0 - yTopF) / fullH, bv1 = (by1 - yTopF) / fullH;
            const bSrcY = Math.max(0, Math.min(fh, bv0 * fh));
            const bSrcH = Math.max(1e-3, Math.min(fh - bSrcY, (bv1 - bv0) * fh));
            for (let sx = 0; sx < spriteW; sx++) {
                const screenX = xLeft + sx;
                if (screenX < 0 || screenX >= w) continue;
                const colIdx = Math.min(numCols - 1, Math.max(0, Math.floor(screenX / colWidth)));
                if (b.corr < colWallDist[colIdx]) {  // unoccluded by a nearer wall
                    const srcX = srcXBase + Math.min(fw - 1, Math.floor(sx / spriteW * fw));
                    if (stairs) {
                        // Steps nearer than it hide its lower rows (S7); a lintel
                        // nearer than it hides its upper rows (C5).
                        const lay = stairsLayouts[colIdx];
                        const limit = raycastClipBefore(lay.occluders, b.corr, viewH);
                        let drawY = by0, srcOff = 0, colH = bVisH;
                        if (lay.occludersTop) {
                            const topLim = raycastClipTopBefore(lay.occludersTop, b.corr);
                            if (topLim > by0) {
                                const cut = topLim - by0;
                                drawY = topLim;
                                srcOff = bSrcH * cut / bVisH;
                                colH = Math.max(0, bVisH - cut);
                            }
                        }
                        colH = Math.min(colH, limit - drawY);
                        if (colH > 0) {
                            ctx.drawImage(img, srcX, bSrcY + srcOff, 1, bSrcH * colH / bVisH,
                                          screenX, drawY, 1, colH);
                        }
                    } else {
                        ctx.drawImage(img, srcX, bSrcY, 1, bSrcH, screenX, by0, 1, bVisH);
                    }
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
    },

    // Low-res floor/ceiling texture casting (faithful port of
    // game_runner._cast_floor_plane). Fills a downsampled ImageData per-pixel
    // by sampling `texData` in CELL units (so the texture tiles once per grid
    // cell and meets the wall bases), then upscales with drawImage. `ceiling`
    // mirrors the same cast into the top half via a vertical flip.
    castFloorPlane(ctx, texData, camCx, camCy, facingScreenRad, fovRad, res, ceiling, viewH, planeHeight) {
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
        // planeHeight: the plane's distance from the eye in cells -- the eye
        // height for the floor (default), wallH - eye for the ceiling. Matches
        // the wall pass (desktop cast_floor_plane; stairs plan F1/S4).
        if (planeHeight === undefined || planeHeight === null) planeHeight = RAYCAST_EYE_HEIGHT;
        const posZ = planeHeight * viewH;
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

// ===========================================================================
// Stairs (docs/RAYCAST_STAIRS_PLAN.md, S10): the HTML5 port of renderer.py's
// stairs path, heights.py and climbing.py. Same names, same order, same
// arithmetic -- tests/test_html5_raycast_stairs.py runs this in Chromium
// against the Python originals.
// ===========================================================================

// Room px kept between the eye and the ceiling (heights.CEILING_MARGIN).
const RAYCAST_CEILING_MARGIN = 4.0;
const RAYCAST_DEFAULT_MAX_STEP = 12.0;   // climbing.DEFAULT_MAX_STEP
const RAYCAST_CLIMB_SPEED = 2.0;         // climbing.CLIMB_SPEED
const RAYCAST_FALL_GRAVITY = 0.6;        // climbing.FALL_GRAVITY

function raycastIsStep(inst) {
    return inst.raycast_floor_height !== undefined && inst.raycast_floor_height !== null;
}

// heights.is_ceiling / is_geometry (ceilings plan, C1): a Set Ceiling Height marker.
function raycastIsCeiling(inst) {
    return inst.raycast_ceiling_height !== undefined && inst.raycast_ceiling_height !== null;
}
function raycastIsGeometry(inst) {
    return raycastIsStep(inst) || raycastIsCeiling(inst);
}

function raycastMaxFloorHeight(cellSize, wallH) {
    return Math.max(0, (wallH - RAYCAST_EYE_HEIGHT) * cellSize - RAYCAST_CEILING_MARGIN);
}

// renderer.stairs_y: screen row of world height z at corrected distance d.
function raycastStairsY(z, eyeZ, d, halfH, viewH) {
    return halfH + (eyeZ - z) * viewH / d;
}

// renderer._row: the screen row a float boundary falls on.
function raycastRow(y) {
    return Math.floor(y + 0.5);
}

// renderer.layout_column, verbatim. crossings: [distCells, hNext, side,
// texU, cellKey] arrays; hit: {dist, side, hit, texU, sprite}.
function raycastLayoutColumn(crossings, hit, h0, eyeZ, wallTopZ, cellSize, cosOff,
                             halfH, viewH, maxCells) {
    let clip = viewH;
    const treads = [], risers = [], occluders = [];
    let hCur = h0, dPrev = 0.0;
    for (const c of crossings) {
        const d = Math.max(c[0] * cellSize * cosOff, 1e-4);
        const yCur = raycastStairsY(hCur, eyeZ, d, halfH, viewH);
        if (yCur < clip) {
            treads.push([yCur, clip, hCur, dPrev]);
            clip = yCur;
        }
        if (c[1] > hCur) {
            const yTop = raycastStairsY(c[1], eyeZ, d, halfH, viewH);
            if (yTop < clip) {
                risers.push([yTop, clip, d, c[2], c[3], c[4], hCur, c[1]]);
                clip = yTop;
            }
        }
        occluders.push([d, clip]);
        hCur = c[1];
        dPrev = d;
        if (clip <= 0) {
            return { treads, risers, wall: null, occluders, wallDist: Infinity };
        }
    }
    let d = Math.max(hit.dist * cosOff, 1e-4);
    if (!hit.hit) d = Math.max(maxCells * cellSize * cosOff, 1e-4);
    const yCur = raycastStairsY(hCur, eyeZ, d, halfH, viewH);
    if (yCur < clip) {
        treads.push([yCur, clip, hCur, dPrev]);
        clip = yCur;
    }
    let wall = null;
    if (hit.hit) {
        const yTop = raycastStairsY(wallTopZ, eyeZ, d, halfH, viewH);
        if (yTop < clip) wall = [yTop, clip, d, hit.side, hit.texU, hit.sprite];
        occluders.push([d, Math.min(clip, yTop)]);
    }
    return { treads, risers, wall, occluders, wallDist: hit.hit ? d : Infinity };
}

// renderer.layout_column_ceilings, verbatim (ceilings plan, C3): the two-clip
// walk. crossings carry a sixth item, the entered cell's ceiling (null = the
// room ceiling); c0 is the camera cell's (null = room ceiling).
function raycastLayoutColumnCeilings(crossings, hit, h0, c0, eyeZ, roomTopZ, cellSize,
                                     cosOff, halfH, viewH, maxCells) {
    let bot = viewH, top = 0.0;
    const treads = [], risers = [], ceils = [], lintels = [];
    const occluders = [], occludersTop = [];
    let hCur = h0;
    let cCur = c0 !== null && c0 !== undefined ? c0 : roomTopZ;
    let dPrev = 0.0;
    for (const c of crossings) {
        const cNext = c[5] !== null && c[5] !== undefined ? c[5] : roomTopZ;
        const d = Math.max(c[0] * cellSize * cosOff, 1e-4);
        let yCur = raycastStairsY(hCur, eyeZ, d, halfH, viewH);
        if (yCur < bot) {
            yCur = Math.max(yCur, top);
            treads.push([yCur, bot, hCur, dPrev]);
            bot = yCur;
        }
        let ycCur = raycastStairsY(cCur, eyeZ, d, halfH, viewH);
        if (ycCur > top) {
            ycCur = Math.min(ycCur, bot);
            ceils.push([top, ycCur, cCur, dPrev]);
            top = ycCur;
        }
        if (c[1] > hCur) {
            let yUp = raycastStairsY(c[1], eyeZ, d, halfH, viewH);
            if (yUp < bot) {
                yUp = Math.max(yUp, top);
                risers.push([yUp, bot, d, c[2], c[3], c[4], hCur, c[1]]);
                bot = yUp;
            }
        }
        if (cNext < cCur) {
            let yDn = raycastStairsY(cNext, eyeZ, d, halfH, viewH);
            if (yDn > top) {
                yDn = Math.min(yDn, bot);
                lintels.push([top, yDn, d, c[2], c[3], c[4], cNext, cCur]);
                top = yDn;
            }
        }
        occluders.push([d, bot]);
        occludersTop.push([d, top]);
        hCur = c[1]; cCur = cNext; dPrev = d;
        if (top >= bot) {
            return { treads, risers, wall: null, ceilings: ceils, lintels, occluders,
                     occludersTop, wallDist: Infinity };
        }
    }
    let d = Math.max(hit.dist * cosOff, 1e-4);
    if (!hit.hit) d = Math.max(maxCells * cellSize * cosOff, 1e-4);
    let yCur = raycastStairsY(hCur, eyeZ, d, halfH, viewH);
    if (yCur < bot) {
        yCur = Math.max(yCur, top);
        treads.push([yCur, bot, hCur, dPrev]);
        bot = yCur;
    }
    let ycCur = raycastStairsY(cCur, eyeZ, d, halfH, viewH);
    if (ycCur > top) {
        ycCur = Math.min(ycCur, bot);
        ceils.push([top, ycCur, cCur, dPrev]);
        top = ycCur;
    }
    let wall = null;
    if (hit.hit) {
        if (top < bot) wall = [top, bot, d, hit.side, hit.texU, hit.sprite];
        occluders.push([d, top]);
        occludersTop.push([d, top]);
    }
    return { treads, risers, wall, ceilings: ceils, lintels, occluders, occludersTop,
             wallDist: hit.hit ? d : Infinity };
}

// renderer._clip_top_before (C5): first row NOT hidden from above in one
// column, for something at corrected distance dist.
function raycastClipTopBefore(occludersTop, dist) {
    let limit = 0.0;
    for (const o of occludersTop) {
        if (o[0] >= dist) break;
        limit = o[1];
    }
    return raycastRow(limit);
}

// renderer._clip_before: first hidden row, in one column, for something at
// corrected distance dist.
function raycastClipBefore(occluders, dist, viewH) {
    let limit = viewH;
    for (const o of occluders) {
        if (o[0] >= dist) break;
        limit = o[1];
    }
    return raycastRow(limit);
}

// hud.blend_hex (Python round() is banker's rounding -- mirrored).
function raycastPyRound(x) {
    const f = Math.floor(x), diff = x - f;
    if (diff > 0.5) return f + 1;
    if (diff < 0.5) return f;
    return (f % 2 === 0) ? f : f + 1;
}
function raycastParseHex(colour) {
    if (typeof colour !== 'string') return null;
    let c = colour.trim().replace(/^#+/, '');
    if (c.length === 3) c = c.split('').map(ch => ch + ch).join('');
    if (c.length !== 6 || !/^[0-9a-fA-F]{6}$/.test(c)) return null;
    return [0, 2, 4].map(i => parseInt(c.slice(i, i + 2), 16));
}
function raycastBlendHex(a, b, t) {
    const ca = raycastParseHex(a), cb = raycastParseHex(b);
    if (!ca || !cb) return b;
    return '#' + ca.map((x, i) => raycastPyRound(x + (cb[i] - x) * t)
        .toString(16).padStart(2, '0')).join('');
}

Object.assign(GameRoom.prototype, {
    // heights.build_floor_heights: raised cells from the step instances.
    // Returns {heights: Map key->h, textures: Map key->[top, side]} and keeps
    // the height map on the room (the minimap and climbing read it).
    buildFloorHeights(cellSize, maxHeight) {
        const heights = new Map(), textures = new Map();
        for (const inst of this.instances) {
            if (!raycastIsStep(inst) || inst.solid) continue;
            let hgt = Number(inst.raycast_floor_height);
            if (!isFinite(hgt)) hgt = 0;
            if (hgt < 0 || hgt > maxHeight) {
                const clamped = Math.min(Math.max(hgt, 0), maxHeight);
                if (!inst._raycastHeightWarned) {
                    inst._raycastHeightWarned = true;
                    console.warn('set_floor_height: height ' + hgt + ' clamped to ' + clamped);
                }
                hgt = clamped;
            }
            if (hgt <= 0) continue;
            const tl = GameRoom.spriteTopLeft(inst);
            const bw = inst.boxWidth(), bh = inst.boxHeight();
            const gx0 = Math.floor(tl.x / cellSize), gy0 = Math.floor(tl.y / cellSize);
            const gx1 = bw > 0 ? Math.floor((tl.x + bw) / cellSize - 1e-9) : gx0;
            const gy1 = bh > 0 ? Math.floor((tl.y + bh) / cellSize - 1e-9) : gy0;
            const tex = [inst.raycast_step_top_texture || '', inst.raycast_step_side_texture || ''];
            for (let gx = gx0; gx <= Math.max(gx0, gx1); gx++) {
                for (let gy = gy0; gy <= Math.max(gy0, gy1); gy++) {
                    const key = gx + ',' + gy;
                    if (hgt > (heights.get(key) || 0)) {
                        heights.set(key, hgt);
                        textures.set(key, tex);
                    }
                }
            }
        }
        this._raycastFloorHeights = heights;
        return { heights, textures };
    },

    // heights.build_ceiling_heights (ceilings plan, C1): the lowered-ceiling map
    // from Set Ceiling Height markers. Returns {ceilings, textures}; each cell's
    // ceiling is clamped to [floor + eye + margin, roomCeiling], lowest marker
    // wins, a marker at the room ceiling changes nothing.
    buildCeilingHeights(cellSize, roomCeiling, floorHeights, eyeHeight) {
        const ceilings = new Map(), textures = new Map();
        for (const inst of this.instances) {
            if (!raycastIsCeiling(inst) || inst.solid) continue;
            let raw = Number(inst.raycast_ceiling_height);
            if (!isFinite(raw)) raw = 0;
            const tex = inst.raycast_ceiling_texture || '';
            let clampedTo = null;
            const tl = GameRoom.spriteTopLeft(inst);
            const bw = inst.boxWidth(), bh = inst.boxHeight();
            const gx0 = Math.floor(tl.x / cellSize), gy0 = Math.floor(tl.y / cellSize);
            const gx1 = bw > 0 ? Math.floor((tl.x + bw) / cellSize - 1e-9) : gx0;
            const gy1 = bh > 0 ? Math.floor((tl.y + bh) / cellSize - 1e-9) : gy0;
            for (let gx = gx0; gx <= Math.max(gx0, gx1); gx++) {
                for (let gy = gy0; gy <= Math.max(gy0, gy1); gy++) {
                    const key = gx + ',' + gy;
                    const lowest = (floorHeights.get(key) || 0) + eyeHeight + RAYCAST_CEILING_MARGIN;
                    const height = Math.min(Math.max(raw, lowest), roomCeiling);
                    if (height !== raw) clampedTo = height;
                    if (height >= roomCeiling) continue;
                    const cur = ceilings.has(key) ? ceilings.get(key) : roomCeiling;
                    if (height < cur) {
                        ceilings.set(key, height);
                        textures.set(key, tex);
                    }
                }
            }
            if (clampedTo !== null && !inst._raycastCeilingWarned) {
                inst._raycastCeilingWarned = true;
                console.warn('set_ceiling_height: height ' + raw + ' is outside the range this view allows; using ' + clampedTo);
            }
        }
        this._raycastCeilingHeights = ceilings;
        return { ceilings, textures };
    },

    // renderer.cast_ray_steps: castRay, also recording each change of floor
    // height (and, given a ceilings map, of the ceiling: a sixth item, null =
    // the room ceiling). Its wall result equals castRay's for the same ray.
    castRaySteps(px, py, angleRad, cellSize, maxCells, heights, ceilings) {
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
        const crossings = [];
        let hPrev = heights.get(mapX + ',' + mapY) || 0;
        const withCeilings = ceilings !== undefined && ceilings !== null;
        let cPrev = withCeilings && ceilings.has(mapX + ',' + mapY)
            ? ceilings.get(mapX + ',' + mapY) : null;
        let side = 0;
        for (let i = 0; i < maxCells; i++) {
            let key, hit;
            if (sideX < sideY) {
                sideX += deltaX; mapX += stepX; side = 0;
                key = (stepX > 0 ? mapX : mapX + 1) + ',' + mapY;
                hit = this._vWalls.has(key);
            } else {
                sideY += deltaY; mapY += stepY; side = 1;
                key = mapX + ',' + (stepY > 0 ? mapY : mapY + 1);
                hit = this._hWalls.has(key);
            }
            const dCells = side === 0 ? (sideX - deltaX) : (sideY - deltaY);
            let wallCoord;
            if (side === 0) {
                wallCoord = pyCell + dCells * dy;
                if (dx > 0) wallCoord = -wallCoord;
            } else {
                wallCoord = pxCell + dCells * dx;
                if (dy < 0) wallCoord = -wallCoord;
            }
            const texU = wallCoord - Math.floor(wallCoord);
            if (hit) {
                const sprite = side === 0 ? this._vWallSprites.get(key) : this._hWallSprites.get(key);
                return { crossings, hit: { dist: Math.max(dCells, 1e-4) * cellSize, side,
                                           hit: true, texU, sprite } };
            }
            const cellKey = mapX + ',' + mapY;
            const hNext = heights.get(cellKey) || 0;
            if (!withCeilings) {
                if (hNext !== hPrev) {
                    crossings.push([dCells, hNext, side, texU, cellKey]);
                    hPrev = hNext;
                }
            } else {
                const cNext = ceilings.has(cellKey) ? ceilings.get(cellKey) : null;
                if (hNext !== hPrev || cNext !== cPrev) {
                    crossings.push([dCells, hNext, side, texU, cellKey, cNext]);
                    hPrev = hNext;
                    cPrev = cNext;
                }
            }
        }
        return { crossings, hit: { dist: Math.max(maxCells, 1e-4) * cellSize, side,
                                   hit: false, texU: 0, sprite: null } };
    },

    // renderer.draw_wall_rows: rows [r0, r1) of a wall (or a riser: the slice
    // of a wall between two heights) at corrected distance d; texture tiles
    // anchored at height 0. img null/unloaded -> flat colour.
    drawStairsWallRows(ctx, img, colorHex, texU, x0, stripW, d, eyeZ, cellSize,
                       halfH, viewH, r0, r1, shade) {
        if (r0 < 0) r0 = 0;
        if (r1 > viewH) r1 = viewH;
        if (r1 <= r0) return;
        if (!(img && img.complete && img.width > 0)) {
            ctx.fillStyle = this._shadeColor(colorHex, shade);
            ctx.fillRect(x0, r0, stripW, r1 - r0);
            return;
        }
        const tw = img.width, th = img.height;
        const tileZ = RAYCAST_TEXTURE_HEIGHT * cellSize;
        const tileH = viewH * tileZ / d;
        const texX = Math.min(tw - 1, Math.max(0, Math.floor(texU * tw)));
        const zBot = eyeZ - (r1 - halfH) * d / viewH;
        const zTop = eyeZ - (r0 - halfH) * d / viewH;
        const k0 = Math.max(0, Math.floor(zBot / tileZ));
        const k1 = Math.max(k0, Math.floor(zTop / tileZ));
        for (let k = k0; k <= k1; k++) {
            const segTop = halfH + (eyeZ - (k + 1) * tileZ) * viewH / d;
            const sy0 = Math.max(r0, Math.floor(segTop));
            const sy1 = Math.min(r1, Math.ceil(segTop + tileH));
            if (sy1 <= sy0) continue;
            const v0 = (sy0 - segTop) / tileH, v1 = (sy1 - segTop) / tileH;
            const srcY = Math.max(0, Math.min(th, v0 * th));
            const srcH = Math.max(1e-3, Math.min(th - srcY, (v1 - v0) * th));
            ctx.drawImage(img, texX, srcY, 1, srcH, x0, sy0, stripW, sy1 - sy0);
        }
        if (shade < 1.0) {
            ctx.fillStyle = `rgba(0,0,0,${(1 - shade).toFixed(3)})`;
            ctx.fillRect(x0, r0, stripW, r1 - r0);
        }
    },

    // renderer._draw_stairs_column: flat raised treads (only without a floor
    // cast), then risers and the wall, over the low-res floor.
    drawStairsColumn(ctx, sf, col, lay, floorCast, ceilingCast) {
        const x0 = Math.floor(col * sf.colWidth);
        const stripW = Math.max(1, Math.floor((col + 1) * sf.colWidth) - x0);
        const viewH = sf.viewH;
        if (!floorCast) {
            ctx.fillStyle = sf.floorColor;
            for (const t of lay.treads) {
                if (t[2] <= 0) continue;
                const r0 = Math.max(0, raycastRow(t[0])), r1 = Math.min(viewH, raycastRow(t[1]));
                if (r1 > r0) ctx.fillRect(x0, r0, stripW, r1 - r0);
            }
        }
        for (const r of lay.risers) {
            let img = null;
            if (sf.textured) {
                const tex = sf.stepTextures.get(r[5]);
                const name = tex ? tex[1] : '';
                img = (name && sf.sprites[name]) || sf.wallTex || null;
            }
            this.drawStairsWallRows(ctx, img, sf.wallColor, r[4], x0, stripW, r[2], sf.eyeZ,
                                    sf.cellSize, sf.halfH, viewH, raycastRow(r[0]), raycastRow(r[1]),
                                    this.wallShade(r[3], r[2], sf.maxDist));
        }
        // Lowered ceilings (C3/C4): their spans flat -- unless the cast already
        // painted them textured -- then their lintels, textured like walls.
        if (lay.ceilings && !ceilingCast) {
            ctx.fillStyle = sf.ceilingColor;
            for (const t of lay.ceilings) {
                if (!(t[2] < sf.wallTopZ)) continue;
                const r0 = Math.max(0, raycastRow(t[0])), r1 = Math.min(viewH, raycastRow(t[1]));
                if (r1 > r0) ctx.fillRect(x0, r0, stripW, r1 - r0);
            }
        }
        if (lay.lintels) {
            for (const l of lay.lintels) {
                const img = (sf.textured && sf.wallTex) ? sf.wallTex : null;
                this.drawStairsWallRows(ctx, img, sf.wallColor, l[4], x0, stripW, l[2], sf.eyeZ,
                                        sf.cellSize, sf.halfH, viewH, raycastRow(l[0]), raycastRow(l[1]),
                                        this.wallShade(l[3], l[2], sf.maxDist));
            }
        }
        const wall = lay.wall;
        if (wall) {
            const img = sf.textured ? (sf.wallTex || wall[5] || null) : null;
            this.drawStairsWallRows(ctx, img, sf.wallColor, wall[4], x0, stripW, wall[2], sf.eyeZ,
                                    sf.cellSize, sf.halfH, viewH, raycastRow(wall[0]), raycastRow(wall[1]),
                                    this.wallShade(wall[3], wall[2], sf.maxDist));
        }
    },

    // renderer.cast_stairs_floor: the floor of a room with steps, cast column
    // by column, each low-res pixel at its own tread's height.
    castStairsFloor(ctx, layouts, sf, floorTex, topTex, facingScreenRad, fovRad, res) {
        const w = ctx.canvas.width;
        const viewH = sf.viewH;
        const halfH = Math.floor(viewH / 2);
        const regionH = viewH - halfH;
        if (regionH <= 0) return;
        const cellSize = sf.cellSize;
        const eyeCells = sf.eyeZ / cellSize;
        const camCx = sf.camX / cellSize, camCy = sf.camY / cellSize;
        const dirX = Math.cos(facingScreenRad), dirY = Math.sin(facingScreenRad);
        const plane = Math.tan(fovRad / 2);
        const planeX = -dirY * plane, planeY = dirX * plane;
        const rdx0 = dirX - planeX, rdy0 = dirY - planeY;
        const rdx1 = dirX + planeX, rdy1 = dirY + planeY;
        const sw = Math.max(1, Math.floor(w / res));
        const sh = Math.max(1, Math.floor(regionH / res));
        if (!this._stairsFloorSmall) this._stairsFloorSmall = document.createElement('canvas');
        const small = this._stairsFloorSmall;
        if (small.width !== sw || small.height !== sh) { small.width = sw; small.height = sh; }
        const sctx = small.getContext('2d');
        const img = sctx.createImageData(sw, sh);
        const out = img.data;
        const flat = raycastParseHex(sf.floorColor) || [70, 70, 50];
        for (let i = 0; i < sw * sh; i++) {
            out[i * 4] = flat[0]; out[i * 4 + 1] = flat[1]; out[i * 4 + 2] = flat[2]; out[i * 4 + 3] = 255;
        }
        const ncol = layouts.length;
        for (let i = 0; i < sw; i++) {
            const sx = i * res;
            let c = Math.floor(sx / sf.colWidth);
            if (c >= ncol) c = ncol - 1;
            const spans = layouts[c].treads;
            if (!spans.length) continue;
            const t = sx / w;
            const rdx = rdx0 + (rdx1 - rdx0) * t, rdy = rdy0 + (rdy1 - rdy0) * t;
            let k = 0;
            const n = spans.length;
            for (let j = sh - 1; j >= 0; j--) {
                const y = halfH + j * res;
                while (k < n - 1 && y < spans[k][0]) k++;
                const hgt = spans[k][2];
                const dz = eyeCells - hgt / cellSize;
                if (dz <= 0) continue;
                let p = j * res; if (p <= 0) p = 1;
                const rowd = dz * viewH / p;
                const fx = camCx + rowd * rdx, fy = camCy + rowd * rdy;
                let tex = null;
                if (topTex.size && hgt > 0) tex = topTex.get(Math.floor(fx) + ',' + Math.floor(fy)) || null;
                if (!tex) tex = floorTex;
                const di = (j * sw + i) * 4;
                if (tex) {
                    const tw = tex.width, th = tex.height;
                    let tx = (tw * (fx - Math.floor(fx))) | 0;
                    let ty = (th * (fy - Math.floor(fy))) | 0;
                    if (tx >= tw) tx = tw - 1;
                    if (ty >= th) ty = th - 1;
                    const si = (ty * tw + tx) * 4;
                    out[di] = tex.data[si]; out[di + 1] = tex.data[si + 1]; out[di + 2] = tex.data[si + 2];
                }
            }
        }
        sctx.putImageData(img, 0, 0);
        ctx.drawImage(small, 0, 0, sw, sh, 0, halfH, w, regionH);
    },

    // renderer.cast_ceiling_spans (ceilings plan, C4): the LOWERED ceilings of
    // a room, cast column by column at their own height into a transparent
    // low-res canvas, upscaled over the screen before lintels and walls.
    // cellTex: Map key -> texData; ceilTex: the camera's texData or null.
    castCeilingSpans(ctx, layouts, sf, cellTex, ceilTex, facingScreenRad, fovRad, res) {
        const w = ctx.canvas.width;
        const viewH = sf.viewH;
        const halfH = Math.floor(viewH / 2);
        if (halfH <= 0 || !layouts.length) return;
        const cellSize = sf.cellSize;
        const eyeCells = sf.eyeZ / cellSize;
        const camCx = sf.camX / cellSize, camCy = sf.camY / cellSize;
        const roomTop = sf.wallTopZ;
        const dirX = Math.cos(facingScreenRad), dirY = Math.sin(facingScreenRad);
        const plane = Math.tan(fovRad / 2);
        const planeX = -dirY * plane, planeY = dirX * plane;
        const rdx0 = dirX - planeX, rdy0 = dirY - planeY;
        const rdx1 = dirX + planeX, rdy1 = dirY + planeY;
        const sw = Math.max(1, Math.floor(w / res));
        const sh = Math.max(1, Math.floor(halfH / res));
        if (!this._ceilingSmall) this._ceilingSmall = document.createElement('canvas');
        const small = this._ceilingSmall;
        if (small.width !== sw || small.height !== sh) { small.width = sw; small.height = sh; }
        const sctx = small.getContext('2d');
        const img = sctx.createImageData(sw, sh);       // all transparent
        const out = img.data;
        const flat = raycastParseHex(sf.ceilingColor) || [135, 206, 235];
        const ncol = layouts.length;
        let painted = false;
        for (let i = 0; i < sw; i++) {
            let c = Math.trunc(i * res / sf.colWidth);
            if (c >= ncol) c = ncol - 1;
            const spans = (layouts[c].ceilings || []).filter(sp => sp[2] < roomTop);
            if (!spans.length) continue;
            const t = (i * res) / w;
            const rdx = rdx0 + (rdx1 - rdx0) * t, rdy = rdy0 + (rdy1 - rdy0) * t;
            const n = spans.length;
            let k = 0;
            for (let j = 0; j < sh; j++) {
                const yc = j * res + res - 1;           // the block's row nearest the horizon
                while (k < n && yc >= spans[k][1]) k++;
                if (k >= n) break;
                if (yc < spans[k][0]) continue;         // above this span: the room ceiling
                const dz = spans[k][2] / cellSize - eyeCells;
                if (dz <= 0) continue;
                let p = halfH - (j * res + res);
                if (p <= 0) p = 1;
                const rowd = dz * viewH / p;
                const fx = camCx + rowd * rdx, fy = camCy + rowd * rdy;
                let tex = cellTex.size ? (cellTex.get(Math.floor(fx) + ',' + Math.floor(fy)) || null) : null;
                if (!tex) tex = ceilTex;
                const di = (j * sw + i) * 4;
                if (tex) {
                    const tw = tex.width, th = tex.height;
                    let tx = (tw * (fx - Math.floor(fx))) | 0;
                    let ty = (th * (fy - Math.floor(fy))) | 0;
                    if (tx >= tw) tx = tw - 1;
                    if (ty >= th) ty = th - 1;
                    const si = (ty * tw + tx) * 4;
                    out[di] = tex.data[si]; out[di + 1] = tex.data[si + 1]; out[di + 2] = tex.data[si + 2];
                } else {
                    out[di] = flat[0]; out[di + 1] = flat[1]; out[di + 2] = flat[2];
                }
                out[di + 3] = 255;
                painted = true;
            }
        }
        if (painted) {
            sctx.putImageData(img, 0, 0);
            ctx.drawImage(small, 0, 0, sw, sh, 0, 0, w, halfH);
        }
    },
});

// climbing.before_step / after_collision (the extension's frame hooks).
function raycastClimbCamera(game) {
    const room = game && game.currentRoom;
    const cfg = room && room.raycastCamera;
    if (!cfg || !cfg.enabled) return null;
    return room;
}
function raycastIsMover(inst) {
    return !raycastIsGeometry(inst) && !inst.solid;
}
function raycastCentreOffset(inst) {
    const tl = GameRoom.spriteTopLeft(inst);
    return [tl.x - inst.x + inst.boxWidth() / 2, tl.y - inst.y + inst.boxHeight() / 2];
}
function raycastClimbBefore(game) {
    const room = raycastClimbCamera(game);
    if (!room) return;
    room._raycastStepPrev = room.instances.filter(raycastIsMover)
        .map(inst => [inst, inst.x, inst.y]);
}
function raycastClimbAfter(game) {
    const room = raycastClimbCamera(game);
    if (!room) return;
    const cfg = room.raycastCamera;
    const prev = room._raycastStepPrev || [];
    room._raycastStepPrev = null;
    const cellSize = cfg.cell_size || 32;
    const wallH = raycastClampWallHeight(cfg.wall_height);
    const heights = room.buildFloorHeights(cellSize, raycastMaxFloorHeight(cellSize, wallH)).heights;
    const roomTop = wallH * cellSize;
    const eyePx = RAYCAST_EYE_HEIGHT * cellSize;
    const ceilings = room.buildCeilingHeights(cellSize, roomTop, heights, eyePx).ceilings;
    const ceilingAt = (cx, cy) => {
        const key = Math.floor(cx / cellSize) + ',' + Math.floor(cy / cellSize);
        return ceilings.has(key) ? ceilings.get(key) : roomTop;
    };
    let maxStep = Number(cfg.max_step);
    if (cfg.max_step === undefined || cfg.max_step === null || !isFinite(maxStep)) {
        maxStep = RAYCAST_DEFAULT_MAX_STEP;
    }
    maxStep = Math.max(0, maxStep);
    const floorAt = (cx, cy) => heights.get(Math.floor(cx / cellSize) + ',' + Math.floor(cy / cellSize)) || 0;
    const alive = new Set(room.instances);
    for (const [inst, ox, oy] of prev) {
        if (!alive.has(inst) || inst.toDestroy) continue;
        const off = raycastCentreOffset(inst);
        const nx = inst.x, ny = inst.y;
        let blocked = 0;
        if ((nx !== ox || ny !== oy) && Math.abs(nx - ox) <= cellSize && Math.abs(ny - oy) <= cellSize) {
            const fOld = floorAt(ox + off[0], oy + off[1]);
            if (floorAt(nx + off[0], ny + off[1]) - fOld > maxStep) {
                blocked = 1;
                for (const [tx, ty] of [[nx, oy], [ox, ny], [ox, oy]]) {
                    if ((tx === ox && ty === oy) || floorAt(tx + off[0], ty + off[1]) - fOld <= maxStep) {
                        inst.x = tx; inst.y = ty;
                        break;
                    }
                }
            }
        }
        inst.raycast_step_blocked = blocked;
        inst.raycast_floor_z = floorAt(inst.x + off[0], inst.y + off[1]);
        inst.raycast_ceiling_z = ceilingAt(inst.x + off[0], inst.y + off[1]);
    }
    const camera = room.findFirstInstance(cfg.camera_object || '');
    if (!camera) return;
    const off = raycastCentreOffset(camera);
    const target = floorAt(camera.x + off[0], camera.y + off[1]);
    camera.raycast_floor_z = target;
    camera.raycast_ceiling_z = ceilingAt(camera.x + off[0], camera.y + off[1]);
    let cur = room._raycastEyeFloor;
    let vz = room._raycastEyeVz || 0;
    if (typeof cur !== 'number') { cur = target; vz = 0; }
    else if (cur < target) { cur = Math.min(target, cur + RAYCAST_CLIMB_SPEED); vz = 0; }
    else if (cur > target) {
        vz += RAYCAST_FALL_GRAVITY;
        cur = Math.max(target, cur - vz);
        if (cur === target) vz = 0;
    } else { vz = 0; }
    // The view never rises above the ceiling over the camera (C6).
    const eyeLimit = camera.raycast_ceiling_z - RAYCAST_CEILING_MARGIN - eyePx;
    if (cur > eyeLimit) { cur = Math.max(target, eyeLimit); vz = 0; }
    room._raycastEyeFloor = cur;
    room._raycastEyeVz = vz;
}
// teleport.py (ceilings plan, T1/T2): Go to Room Seamlessly. In the browser the room
// change happens in the middle of a logic step and the NEW room's Create events run
// at the start of ITS first step, so two things differ from desktop: the arrival is
// applied only once that step has consumed room_start (and, like desktop, in the
// after_collision phase, BEFORE climbing's hook), and any frame drawn in between
// shows the pre-change frame (a snapshot) instead of the new room at its authored
// start. Registered before the climbing hooks.
function raycastFindByName(room, name) {
    if (!name) return null;
    for (const inst of room.instances) {
        if (inst.name === name && !inst.toDestroy) return inst;
    }
    return null;
}
function raycastCameraOf(room) {
    const cfg = room && room.raycastCamera;
    if (!cfg || !cfg.enabled) return null;
    return room.findFirstInstance(cfg.camera_object || '');
}
function raycastArrivalAfter(game) {
    const arrival = game._raycastArrival;
    if (!arrival) return;
    const room = game.currentRoom;
    if (!room || room === arrival.fromRoom) return;          // the change has not happened yet
    if (room._pendingRoomStart) return;                      // its Create / Room Start have not run yet
    game._raycastArrival = null;                             // from here on frames draw normally
    if (room.name !== arrival.to) return;
    const camera = raycastCameraOf(room);
    const marker = raycastFindByName(room, arrival.marker);
    if (!camera) { console.warn('go_to_room_seamlessly: the new room has no raycast camera'); return; }
    if (!marker) {
        console.warn('go_to_room_seamlessly: no ' + arrival.marker + ' object in room ' + arrival.to
            + '; arriving at its start');
        return;
    }
    camera.x = marker.x + arrival.dx;
    camera.y = marker.y + arrival.dy;
    camera.facing_angle = arrival.facing;
    camera.hspeed = arrival.hspeed;
    camera.vspeed = arrival.vspeed;
    if (typeof arrival.eyeFloor === 'number') {
        room._raycastEyeFloor = arrival.eyeFloor;
        room._raycastEyeVz = arrival.eyeVz;
    }
}
registerFrameUpdate(raycastArrivalAfter, 'after_collision');
registerFrameUpdate(raycastClimbBefore);
registerFrameUpdate(raycastClimbAfter, 'after_collision');

// The render hook: claim any room whose raycast camera is enabled. Replaces
// engine.js's old inline dispatch -- the engine now gives every room to
// renderExtensionRoom() first (Stage C1a).
registerRoomRenderer(function(room, ctx) {
    // A seamless arrival is pending: until the new room's first step has run
    // and the arrival is applied, show the frame from before the change.
    const gm = room._gameRef;
    const pend = gm && gm._raycastArrival;
    if (pend && pend.snapshot && room !== pend.fromRoom) {
        ctx.drawImage(pend.snapshot, 0, 0);
        return true;
    }
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

                // Raised floor cells (stairs, hud.build_minimap_commands
                // `raised`): filled squares under the walls, shaded by height.
                const mmRaised = room._raycastFloorHeights;
                if (mmRaised && mmRaised.size) {
                    const mmTop = Math.max(...mmRaised.values());
                    for (const [gx, gy] of mmKeys(mmRaised.keys())) {
                        const t = 0.25 + 0.5 * (mmTop > 0 ? mmRaised.get(gx + ',' + gy) / mmTop : 1.0);
                        const [x1, y1] = mmPx(gx * mmCS, gy * mmCS);
                        const [x2, y2] = mmPx((gx + 1) * mmCS, (gy + 1) * mmCS);
                        obj._draw_queue.push({type: 'rectangle', x1, y1, x2, y2,
                            color: raycastBlendHex(backColor, wallColor, t), filled: true});
                    }
                }

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

                // Resolve the camera early (needed by both the trail and the
                // player marker below) -- same ray ORIGIN renderRaycastView
                // casts from, not the sprite corner.
                const mmCfg = room.raycastCamera || {};
                const mmCam = room.findFirstInstance(mmCfg.camera_object || '');
                let camWx = null, camWy = null;
                if (mmCam) {
                    const mmTL = GameRoom.spriteTopLeft(mmCam);
                    camWx = mmTL.x + mmCam.boxWidth() / 2;
                    camWy = mmTL.y + mmCam.boxHeight() / 2;
                }

                // Opt-in breadcrumb trail: a faint dot per grid cell the
                // camera has visited, under everything else. Persisted on
                // the room (survives across frames, naturally bounded by
                // the maze's own cell count) -- mirrors
                // handlers._record_trail_cell exactly.
                const showTrail = params.show_trail === true || params.show_trail === 'true' ||
                                   params.show_trail === 1 || params.show_trail === '1';
                if (showTrail && camWx !== null) {
                    if (!room._raycastTrail) room._raycastTrail = new Set();
                    room._raycastTrail.add(Math.floor(camWx / mmCS) + ',' + Math.floor(camWy / mmCS));
                    const trailColor = params.trail_color || '#406080';
                    const MM_TRAIL_HALF = 1.0;
                    for (const [gx, gy] of mmKeys(room._raycastTrail)) {
                        const [tx, ty] = mmPx(gx * mmCS + mmCS / 2, gy * mmCS + mmCS / 2);
                        obj._draw_queue.push({
                            type: 'rectangle',
                            x1: tx - MM_TRAIL_HALF, y1: ty - MM_TRAIL_HALF,
                            x2: tx + MM_TRAIL_HALF, y2: ty + MM_TRAIL_HALF,
                            color: trailColor, filled: true,
                        });
                    }
                }

                // Opt-in object dots, under the player marker so a pickup
                // sharing a cell never hides it. Mirrors hud.py's marks loop.
                const MM_MARK_HALF = 1.5;
                const mmMarkPoints = (objectName) => {
                    if (!objectName) return [];
                    const pts = [];
                    for (const inst of (room.instances || [])) {
                        if (inst.object_name !== objectName) continue;
                        const tl = GameRoom.spriteTopLeft(inst);
                        pts.push([tl.x + inst.boxWidth() / 2,
                                  tl.y + inst.boxHeight() / 2]);
                    }
                    // Sorted for the same reason the wall sets are.
                    return pts.sort((a, b) => (a[0] - b[0]) || (a[1] - b[1]));
                };
                for (const grp of [
                        {color: params.mark_color || '#40e0ff',
                         points: mmMarkPoints(params.mark_object || '')},
                        {color: params.mark_color_2 || '#ff5050',
                         points: mmMarkPoints(params.mark_object_2 || '')}]) {
                    if (!grp.color || !grp.points.length) continue;
                    for (const [wx, wy] of grp.points) {
                        const [mx, my] = mmPx(wx, wy);
                        obj._draw_queue.push({
                            type: 'rectangle',
                            x1: mx - MM_MARK_HALF, y1: my - MM_MARK_HALF,
                            x2: mx + MM_MARK_HALF, y2: my + MM_MARK_HALF,
                            color: grp.color, filled: true,
                        });
                    }
                }

                if (!mmCam) return;
                const [cx, cy] = mmPx(camWx, camWy);
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

registerExtensionAction('set_billboard_rotation', function(obj, params, game) {
                // Rotation-by-viewing-angle billboard frames (see
                // execute_set_billboard_rotation_action). 0 disables --
                // the billboard draw falls back to image_index.
                const frames = parseNumParam(params.frames, obj, 8);
                obj.billboard_rotation_frames = Math.max(0, Math.floor(frames) || 0);
                return;
            });

registerExtensionAction('set_floor_height', function(obj, params, game) {
                // Make this instance a step (execute_set_floor_height_action):
                // records the height and textures; buildFloorHeights clamps.
                let hgt = 8;
                if (params.height !== undefined && params.height !== null && params.height !== '') {
                    hgt = parseNumParam(params.height, obj, NaN);
                    if (typeof hgt !== 'number' || !isFinite(hgt)) hgt = 0;
                }
                obj.raycast_floor_height = hgt;
                obj.raycast_step_top_texture = params.top_texture ? String(params.top_texture) : '';
                obj.raycast_step_side_texture = params.side_texture ? String(params.side_texture) : '';
                return;
            });

registerExtensionAction('go_to_room_seamlessly', function(obj, params, game) {
                // teleport.request: record the arrival, then an ordinary instant change.
                const target = String(params.room || '').trim();
                if (!target || !game.gameData.assets.rooms[target]) return;
                const room = game.currentRoom;
                const markerName = String(params.marker || '').trim();
                const camera = raycastCameraOf(room);
                const marker = raycastFindByName(room, markerName);
                let arrival = null;
                if (room.name === target) {
                    console.warn('go_to_room_seamlessly: already in room ' + target + '; changing room normally');
                } else if (!camera) {
                    console.warn('go_to_room_seamlessly: no raycast camera in this room; changing room normally');
                } else if (!marker) {
                    console.warn('go_to_room_seamlessly: no ' + markerName + ' object in this room; changing room normally');
                } else {
                    const snap = document.createElement('canvas');
                    snap.width = game.canvas.width; snap.height = game.canvas.height;
                    snap.getContext('2d').drawImage(game.canvas, 0, 0);
                    arrival = {
                        fromRoom: room, to: target, marker: markerName,
                        dx: camera.x - marker.x, dy: camera.y - marker.y,
                        facing: camera.facing_angle, hspeed: camera.hspeed, vspeed: camera.vspeed,
                        eyeFloor: room._raycastEyeFloor, eyeVz: room._raycastEyeVz || 0,
                        snapshot: snap,
                    };
                }
                game._raycastArrival = arrival;
                // changeRoom clears the keyboard state; a held key stays held across the junction.
                const heldKeys = Object.assign({}, game.keys);
                game.changeRoom(target, false, 'none');
                if (arrival) Object.assign(game.keys, heldKeys);
                return;
            });

registerExtensionAction('set_ceiling_height', function(obj, params, game) {
                // Lower the ceiling over this instance's cells
                // (execute_set_ceiling_height_action): records the height and texture;
                // buildCeilingHeights clamps.
                let hgt = 40;
                if (params.height !== undefined && params.height !== null) {
                    hgt = parseNumParam(params.height, obj, NaN);
                    if (typeof hgt !== 'number' || !isFinite(hgt)) hgt = 0;
                }
                obj.raycast_ceiling_height = hgt;
                obj.raycast_ceiling_texture = params.texture ? String(params.texture) : '';
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
                    // Walls + ceiling height in cells (stairs plan S4);
                    // clamped where it is used (raycastClampWallHeight).
                    wall_height: rNum('wall_height', 1.5),
                    // Highest climbable step, room px (stairs S8/S10).
                    max_step: rNum('max_step', 12),
                    // DOOM-bar letterbox (0 = full height). renderRaycastView
                    // reads obj; without it here an exported game ignores a
                    // viewport_height the desktop runtime honours.
                    viewport_height: Math.floor(rNum('viewport_height', 0)),
                };
                game.currentRoom._vWalls = null;  // rebuild wall map next render
                return;
            });
