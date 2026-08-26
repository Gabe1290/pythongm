// export_html5.js -- the Block World voxel renderer's HTML5 port (Phase 6
// Unit 8 of docs/VOXEL_WORLD_PLAN.md). Concatenated at engine.js's
// __PYGM_EXTENSION_JS__ marker (Stage-C pattern established by
// extensions/raycast_2_5d/export_html5.js -- see that file's own header for
// the mechanism). engine.js itself names nothing here.
//
// Mirrors extensions/block_world/state.py + renderer.py + handlers.py +
// hud.py. All three face orientations are real per-pixel textures: side
// (wall) faces via ctx.drawImage sub-rect slicing (Tier 4a, mirroring the
// raycast HTML5 wall pass exactly); top/bottom faces via a per-pixel cast
// over the block's quad (Tier 4b -- NOT a literal port of either the wall
// pass or raycast's floor caster, since a block face is a bounded quad, not
// an infinite plane or a flat strip). Both fall back to BLOCK_FACE_COLORS
// (precomputed average colors) whenever a texture hasn't finished loading
// yet, `wall_textured` is off, or (top/bottom only) `top_cast_res` is 0.
// The occlusion early-out (_fully_covers on desktop) is skipped: a pure
// perf shortcut, since the far-to-near painter's-algorithm draw order is
// correct without it.
//
// `load_block_world`'s data file has no filesystem to read from in a
// browser -- see extensions/block_world/export_data.py, whose
// collect_export_data() embeds every referenced file into
// gameData._extension_data.block_world_files at export time. The same
// module embeds every block texture PNG (base64) into
// gameData._extension_data.block_textures; bwTexture() below lazily builds
// an Image() per filename from that data URI.

// Precomputed per-block-type average face colors (see
// tools/generated/block_world_face_colors.json / gen_block_world_face_colors.py
// -- pinned by tests/test_block_world_export_face_colors.py against a live
// recomputation, so this table cannot silently drift from the bundled art).
const BLOCK_FACE_COLORS = {
    brick: { top: [124,78,72], bottom: [124,78,72], side: [124,78,72] },
    clay: { top: [180,162,136], bottom: [180,162,136], side: [180,162,136] },
    coal_block: { top: [55,55,56], bottom: [55,55,56], side: [55,55,56] },
    cobble: { top: [116,127,126], bottom: [116,127,126], side: [116,127,126] },
    desert_sand: { top: [223,213,154], bottom: [223,213,154], side: [223,213,154] },
    diamond_block: { top: [99,143,180], bottom: [99,143,180], side: [99,143,180] },
    dirt: { top: [172,124,68], bottom: [172,124,68], side: [172,124,68] },
    glass: { top: [137,156,168], bottom: [137,156,168], side: [137,156,168] },
    gold_block: { top: [220,145,61], bottom: [220,145,61], side: [220,145,61] },
    grass: { top: [49,141,0], bottom: [172,124,68], side: [46,135,0] },
    gravel: { top: [115,116,112], bottom: [115,116,112], side: [115,116,112] },
    ice: { top: [174,204,225], bottom: [174,204,225], side: [174,204,225] },
    jungle_plank: { top: [102,77,51], bottom: [102,77,51], side: [102,77,51] },
    leaves: { top: [58,136,58], bottom: [58,136,58], side: [58,136,58] },
    mese_block: { top: [152,121,69], bottom: [152,121,69], side: [152,121,69] },
    obsidian: { top: [31,30,30], bottom: [31,30,30], side: [31,30,30] },
    pine_plank: { top: [196,150,93], bottom: [196,150,93], side: [196,150,93] },
    sand: { top: [218,204,171], bottom: [218,204,171], side: [218,204,171] },
    sandstone: { top: [196,173,122], bottom: [196,173,122], side: [196,173,122] },
    snow: { top: [232,231,231], bottom: [232,231,231], side: [232,231,231] },
    stone: { top: [154,154,150], bottom: [154,154,150], side: [154,154,150] },
    water: { top: [92,169,31], bottom: [92,169,31], side: [92,169,31] },
    wood_log: { top: [134,103,78], bottom: [134,103,78], side: [95,62,40] },
    wood_plank: { top: [139,98,50], bottom: [139,98,50], side: [139,98,50] },
    wool_black: { top: [30,30,30], bottom: [30,30,30], side: [30,30,30] },
    wool_blue: { top: [33,29,154], bottom: [33,29,154], side: [33,29,154] },
    wool_green: { top: [50,154,29], bottom: [50,154,29], side: [50,154,29] },
    wool_red: { top: [154,29,29], bottom: [154,29,29], side: [154,29,29] },
    wool_white: { top: [227,227,226], bottom: [227,227,226], side: [227,227,226] },
    wool_yellow: { top: [236,162,0], bottom: [236,162,0], side: [236,162,0] },
};

// Face -> source PNG filename, mirroring state.BLOCK_TYPES's own top/bottom/
// side (or 'all') shorthand (filenames only -- solid/transparent/breakable
// flags aren't needed for rendering). Resolves a filename into
// gameData._extension_data.block_textures for the real Image.
const BLOCK_FACE_FILES = {
    brick: { top: 'default_brick.png', bottom: 'default_brick.png', side: 'default_brick.png' },
    clay: { top: 'default_clay.png', bottom: 'default_clay.png', side: 'default_clay.png' },
    coal_block: { top: 'default_coal_block.png', bottom: 'default_coal_block.png', side: 'default_coal_block.png' },
    cobble: { top: 'default_cobble.png', bottom: 'default_cobble.png', side: 'default_cobble.png' },
    desert_sand: { top: 'default_desert_sand.png', bottom: 'default_desert_sand.png', side: 'default_desert_sand.png' },
    diamond_block: { top: 'default_diamond_block.png', bottom: 'default_diamond_block.png', side: 'default_diamond_block.png' },
    dirt: { top: 'default_dirt.png', bottom: 'default_dirt.png', side: 'default_dirt.png' },
    glass: { top: 'default_glass.png', bottom: 'default_glass.png', side: 'default_glass.png' },
    gold_block: { top: 'default_gold_block.png', bottom: 'default_gold_block.png', side: 'default_gold_block.png' },
    grass: { top: 'default_grass.png', bottom: 'default_dirt.png', side: 'default_grass_side.png' },
    gravel: { top: 'default_gravel.png', bottom: 'default_gravel.png', side: 'default_gravel.png' },
    ice: { top: 'default_ice.png', bottom: 'default_ice.png', side: 'default_ice.png' },
    jungle_plank: { top: 'default_junglewood.png', bottom: 'default_junglewood.png', side: 'default_junglewood.png' },
    leaves: { top: 'default_leaves.png', bottom: 'default_leaves.png', side: 'default_leaves.png' },
    mese_block: { top: 'default_mese_block.png', bottom: 'default_mese_block.png', side: 'default_mese_block.png' },
    obsidian: { top: 'default_obsidian.png', bottom: 'default_obsidian.png', side: 'default_obsidian.png' },
    pine_plank: { top: 'default_pine_wood.png', bottom: 'default_pine_wood.png', side: 'default_pine_wood.png' },
    sand: { top: 'default_sand.png', bottom: 'default_sand.png', side: 'default_sand.png' },
    sandstone: { top: 'default_sandstone.png', bottom: 'default_sandstone.png', side: 'default_sandstone.png' },
    snow: { top: 'default_snow.png', bottom: 'default_snow.png', side: 'default_snow.png' },
    stone: { top: 'default_stone.png', bottom: 'default_stone.png', side: 'default_stone.png' },
    water: { top: 'default_water_source_animated.png', bottom: 'default_water_source_animated.png', side: 'default_water_source_animated.png' },
    wood_log: { top: 'default_tree_top.png', bottom: 'default_tree_top.png', side: 'default_tree.png' },
    wood_plank: { top: 'default_wood.png', bottom: 'default_wood.png', side: 'default_wood.png' },
    wool_black: { top: 'wool_black.png', bottom: 'wool_black.png', side: 'wool_black.png' },
    wool_blue: { top: 'wool_blue.png', bottom: 'wool_blue.png', side: 'wool_blue.png' },
    wool_green: { top: 'wool_green.png', bottom: 'wool_green.png', side: 'wool_green.png' },
    wool_red: { top: 'wool_red.png', bottom: 'wool_red.png', side: 'wool_red.png' },
    wool_white: { top: 'wool_white.png', bottom: 'wool_white.png', side: 'wool_white.png' },
    wool_yellow: { top: 'wool_yellow.png', bottom: 'wool_yellow.png', side: 'wool_yellow.png' },
};

// Lazily built Image() cache, keyed by filename -- mirrors engine.js's own
// sprite-loading convention (an Image whose .src is a data: URI; callers
// must check .complete && .width>0 before drawing, since decoding is async).
const _bwTexCache = {};
function bwTexture(game, filename) {
    if (!filename) return null;
    if (_bwTexCache[filename]) return _bwTexCache[filename];
    const b64 = game && game.gameData && game.gameData._extension_data
        && game.gameData._extension_data.block_textures
        && game.gameData._extension_data.block_textures[filename];
    if (!b64) return null;
    const img = new Image();
    img.src = 'data:image/png;base64,' + b64;
    _bwTexCache[filename] = img;
    return img;
}

// Cached ImageData for a loaded block texture (Tier 4b: top/bottom
// per-pixel casting needs raw pixel access, not just an Image to
// drawImage). Mirrors raycast_2_5d's own _textureData. Only caches once
// the Image has actually finished loading -- an early call while it's
// still decoding must NOT cache null, or the face would be stuck flat-
// colored forever once the image does load.
const _bwTexDataCache = {};
function bwTextureData(game, filename) {
    if (!filename) return null;
    if (_bwTexDataCache[filename]) return _bwTexDataCache[filename];
    const img = bwTexture(game, filename);
    if (!img || !img.complete || !img.width) return null;
    let data = null;
    try {
        const c = document.createElement('canvas');
        c.width = img.width; c.height = img.height;
        const g = c.getContext('2d');
        g.drawImage(img, 0, 0);
        data = g.getImageData(0, 0, img.width, img.height);
    } catch (e) {
        data = null;   // tainted canvas -- keep the flat-color fallback
    }
    if (data) _bwTexDataCache[filename] = data;
    return data;
}

// Reusable 1xN scratch canvas for bwDrawHorizontalFaceTextured, grown
// (never shrunk) to fit -- mirrors renderer.py's _horizontal_face_scratch
// and raycast_2_5d's own _floorSmall, same reasoning: this runs once per
// exposed top/bottom face per column, so a fresh canvas per call would
// dominate the frame cost.
let _bwFaceScratch = null;
function bwHorizontalFaceScratch(samples) {
    if (!_bwFaceScratch) _bwFaceScratch = document.createElement('canvas');
    if (_bwFaceScratch.width !== 1) _bwFaceScratch.width = 1;
    if (_bwFaceScratch.height < samples) _bwFaceScratch.height = samples;
    return _bwFaceScratch;
}

// Real per-pixel top/bottom face texture (Tier 4b). Faithful port of
// renderer.py's _draw_horizontal_face_textured -- inverting the
// projection gives the distance to the plane_z-height plane directly for
// each screen row, so each sampled row's world point gives a texel;
// sampled every `res` rows into a 1-wide column and upscaled (identical
// trick to the wall pass and to raycast's floor caster). Shading is a
// single black-alpha overlay after the scaled draw, not per-texel.
function bwDrawHorizontalFaceTextured(ctx, x0, stripW, yA, yB, texData,
                                      camX, camY, dirX, dirY, cosOff,
                                      planeZ, eyeZ, horizon, cellSize,
                                      shade, res, H) {
    const y0 = Math.max(0, Math.floor(Math.min(yA, yB)));
    const y1 = Math.min(H, Math.ceil(Math.max(yA, yB)));
    const span = y1 - y0;
    if (span <= 0) return;
    const tw = texData.width, th = texData.height;
    if (tw <= 0 || th <= 0) return;
    const data = texData.data;

    // Same sign top or bottom: looking down, eyeZ > planeZ and the rows
    // sit below the horizon; looking up, both flip. The ratio stays
    // positive either way.
    const k = (eyeZ - planeZ) * H * cellSize;
    const invCell = 1.0 / cellSize;

    function texel(y) {
        let denom = y + 0.5 - horizon;
        if (denom > -1e-6 && denom < 1e-6) denom = denom >= 0 ? 1e-6 : -1e-6;
        const rayDist = (k / denom) / cosOff;
        const gx = (camX + dirX * rayDist) * invCell;
        const gy = (camY + dirY * rayDist) * invCell;
        let tx = Math.floor(tw * (gx - Math.floor(gx)));
        let ty = Math.floor(th * (gy - Math.floor(gy)));
        if (tx >= tw) tx = tw - 1; else if (tx < 0) tx = 0;
        if (ty >= th) ty = th - 1; else if (ty < 0) ty = 0;
        const idx = (ty * tw + tx) * 4;
        return [data[idx], data[idx + 1], data[idx + 2]];
    }

    const samples = Math.max(1, Math.ceil(span / res));
    if (samples === 1) {
        // Most faces are a handful of rows -- a distant deck is hundreds
        // of one-sample slivers. A scaled drawImage for a span this short
        // costs far more than the fill it replaces.
        const [r, g, b] = texel(y0);
        const sh = shade < 1.0 ? shade : 1.0;
        ctx.fillStyle = `rgb(${Math.round(r * sh)},${Math.round(g * sh)},${Math.round(b * sh)})`;
        ctx.fillRect(x0, y0, stripW, span);
        return;
    }

    const small = bwHorizontalFaceScratch(samples);
    const sctx = small.getContext('2d');
    const col = sctx.createImageData(1, samples);
    for (let i = 0; i < samples; i++) {
        const [r, g, b] = texel(y0 + i * res);
        const di = i * 4;
        col.data[di] = r; col.data[di + 1] = g; col.data[di + 2] = b; col.data[di + 3] = 255;
    }
    sctx.putImageData(col, 0, 0);
    ctx.drawImage(small, 0, 0, 1, samples, x0, y0, stripW, span);
    if (shade < 1.0) {
        ctx.fillStyle = `rgba(0,0,0,${(1 - shade).toFixed(3)})`;
        ctx.fillRect(x0, y0, stripW, span);
    }
}

// The one block type break_block refuses to remove (state.BLOCK_TYPES'
// single 'breakable': False entry).
const BW_UNBREAKABLE = new Set(['obsidian']);

// Mirrors state.DEFAULT_HOTBAR exactly (order matters -- select_hotbar_slot
// indexes into it).
const BW_DEFAULT_HOTBAR = ['cobble', 'brick', 'wood_plank', 'glass',
                            'wool_red', 'sandstone', 'gold_block', 'leaves'];

// Shading constants -- mirror renderer.py's SIDE_SHADE/FOG_STRENGTH/
// MIN_SHADE/TOP_SHADE/BOTTOM_SHADE/DEFAULT_EYE_HEIGHT/MAX_PITCH_DEGREES
// exactly (deliberately duplicated per block, not shared code, matching
// this extension's own state.py precedent of independent removability).
const BW_SIDE_SHADE = 0.85;
const BW_FOG_STRENGTH = 0.55;
const BW_MIN_SHADE = 0.35;
const BW_TOP_SHADE = 1.15;
const BW_BOTTOM_SHADE = 0.55;
const BW_DEFAULT_EYE_HEIGHT = 1.5;
const BW_MAX_PITCH_DEGREES = 70.0;
// Horizontal faces (top/bottom) are cast every Nth row and upscaled
// (Tier 4b); 0 disables texturing (flat average-color fallback).
const BW_DEFAULT_TOP_CAST_RES = 4;
const BW_DEFAULT_MAX_STEP_UP = 1;

// Jump mechanic (Tier 7a) -- mirror handlers.py's own constants exactly.
const BW_DEFAULT_GRAVITY = 0.04;
const BW_DEFAULT_JUMP_SPEED = 0.35;
const BW_TERMINAL_FALL_SPEED = -0.9;
const BW_JUMP_GROUND_EPS = 1e-6;

// --- state.py port (free functions taking a GameRoom, mirroring the
// desktop module's own free-function style over `room`) -----------------

function bwKey(x, y, z) { return x + ',' + y + ',' + z; }

function bwGetBlock(room, x, y, z) {
    const blocks = room._bwBlocks;
    if (!blocks) return null;
    const v = blocks[bwKey(x, y, z)];
    return v === undefined ? null : v;
}

function bwSetBlock(room, x, y, z, blockType) {
    if (!room._bwBlocks) room._bwBlocks = {};
    room._bwBlocks[bwKey(x, y, z)] = blockType;
    room._bwColumns = null;
    bwMarkChunkPresent(room, x, y);   // see bwGenerateChunk's own guard
}

function bwRemoveBlock(room, x, y, z) {
    if (!room._bwBlocks) return;
    delete room._bwBlocks[bwKey(x, y, z)];
    room._bwColumns = null;
    bwMarkChunkPresent(room, x, y);
}

// --- Tier 7e Phase 2/3 procedural terrain
// (docs/BLOCK_WORLD_INFINITE_TERRAIN_PLAN.md) -- an independent JS port of
// state.py's generate_chunk/ensure_chunks_loaded, NOT required to produce
// numerically identical terrain to desktop or Kivy (the plan's own
// recommendation: internally consistent per-target, not cross-target
// byte-identical). No eviction/unloading here (unlike desktop's
// unload_distant_chunks) -- a deliberate, documented scope cut: an
// exported game has no long-lived IDE session to bound memory for, and a
// typical classroom play session never explores far enough for the
// unbounded _bwBlocks dict to matter. Revisit only if that stops being
// true in practice.

const BW_CHUNK_SIZE = 16;

function bwChunkKey(x, y) {
    return Math.floor(x / BW_CHUNK_SIZE) + ',' + Math.floor(y / BW_CHUNK_SIZE);
}

// Marks a chunk as "has real content" -- set by every direct edit AND by
// generation itself, so generation can never run twice over the same
// chunk and can never silently overwrite a player's edit, even one made
// in a chunk generation hasn't reached yet. Mirrors state.py's own
// `if key in st["chunks"]: return` guard (chunk PRESENCE, not a separate
// touched flag) -- including its one real quirk: a single manual edit in
// an ungenerated chunk permanently opts that whole chunk out of terrain
// generation. Reproducing that quirk here (rather than a subtly different
// rule) is deliberate -- same behaviour as desktop, not just similar.
function bwMarkChunkPresent(room, x, y) {
    if (!room._bwGenerated) room._bwGenerated = {};
    room._bwGenerated[bwChunkKey(x, y)] = true;
}

// Integer-only bit-mixing hash -> a float from 0 up to (not including) 1.
// Deliberately NOT a transliteration
// of state.py's _hash01 (Python's `& 0xFFFFFFFF` unsigned masking has no
// cheap JS equivalent that stays fast; `Math.imul` + `>>> 0` is the
// idiomatic JS version of the same "mix these bits deterministically" goal)
// -- see this section's header for why bit-identical output isn't required.
function bwHash01(seed, x, y) {
    let h = (seed * 374761393 + x * 668265263 + y * 2147483647) | 0;
    h = Math.imul(h ^ (h >>> 13), 1274126177);
    h = (h ^ (h >>> 16)) >>> 0;
    return (h % 100000) / 100000.0;
}

function bwSmoothstep(t) { return t * t * (3.0 - 2.0 * t); }

// Bilinear-interpolated value noise at world cell (x, y), 0 up to (not
// including) 1 --
// mirrors state.py's _value_noise's algorithm shape (not its exact bits).
function bwValueNoise(seed, x, y, scale) {
    const fx = x / scale, fy = y / scale;
    const x0 = Math.floor(fx), y0 = Math.floor(fy);
    const x1 = x0 + 1, y1 = y0 + 1;
    const tx = bwSmoothstep(fx - x0), ty = bwSmoothstep(fy - y0);
    const v00 = bwHash01(seed, x0, y0), v10 = bwHash01(seed, x1, y0);
    const v01 = bwHash01(seed, x0, y1), v11 = bwHash01(seed, x1, y1);
    const top = v00 + tx * (v10 - v00);
    const bottom = v01 + tx * (v11 - v01);
    return top + ty * (bottom - top);
}

// Terrain shape constants -- matches state.py's own (rolling hills, not
// tuned against anything; see that module's comment).
const BW_TERRAIN_BASE_HEIGHT = 3;
const BW_TERRAIN_AMPLITUDE = 6;
const BW_TERRAIN_NOISE_SCALE = 24.0;

function bwTerrainHeight(seed, x, y) {
    const n = bwValueNoise(seed, x, y, BW_TERRAIN_NOISE_SCALE);
    return BW_TERRAIN_BASE_HEIGHT + Math.trunc(n * BW_TERRAIN_AMPLITUDE);
}

// Deterministically fill chunk (cx, cy) from room._bwSeed, if any and if
// this chunk has no content yet (see bwMarkChunkPresent). Grass-on-top,
// dirt-below columns -- "rolling hills with variety," this plan's own
// explicit bar for a first cut.
function bwGenerateChunk(room, cx, cy) {
    const seed = room._bwSeed;
    if (seed === undefined || seed === null) return;
    const key = cx + ',' + cy;
    if (room._bwGenerated && room._bwGenerated[key]) return;
    if (!room._bwBlocks) room._bwBlocks = {};
    for (let lx = 0; lx < BW_CHUNK_SIZE; lx++) {
        for (let ly = 0; ly < BW_CHUNK_SIZE; ly++) {
            const x = cx * BW_CHUNK_SIZE + lx, y = cy * BW_CHUNK_SIZE + ly;
            const height = bwTerrainHeight(seed, x, y);
            for (let z = 0; z < height; z++) {
                room._bwBlocks[bwKey(x, y, z)] = (z === height - 1) ? 'grass' : 'dirt';
            }
        }
    }
    if (!room._bwGenerated) room._bwGenerated = {};
    room._bwGenerated[key] = true;
    room._bwColumns = null;
}

// Generate every chunk within radiusCells (cell units, not pixels) of
// world CELL position (centerX, centerY) that isn't already present. A
// cheap no-op if the room has no seed. Call once per frame from the
// render path, before the column index is fetched.
function bwEnsureChunksLoaded(room, centerX, centerY, radiusCells) {
    if (room._bwSeed === undefined || room._bwSeed === null) return;
    const cx0 = Math.floor((centerX - radiusCells) / BW_CHUNK_SIZE);
    const cy0 = Math.floor((centerY - radiusCells) / BW_CHUNK_SIZE);
    const cx1 = Math.floor((centerX + radiusCells) / BW_CHUNK_SIZE);
    const cy1 = Math.floor((centerY + radiusCells) / BW_CHUNK_SIZE);
    for (let cx = cx0; cx <= cx1; cx++) {
        for (let cy = cy0; cy <= cy1; cy++) {
            bwGenerateChunk(room, cx, cy);
        }
    }
}

// {(x,y): [[z, blockType], ...]} sorted lowest z first, cached until a
// mutator clears room._bwColumns -- mirrors state.column_index.
function bwColumnIndex(room) {
    if (room._bwColumns) return room._bwColumns;
    const index = {};
    const blocks = room._bwBlocks || {};
    for (const key in blocks) {
        const parts = key.split(',');
        const cx = parts[0], cy = parts[1], z = parseInt(parts[2], 10);
        const ck = cx + ',' + cy;
        if (!index[ck]) index[ck] = [];
        index[ck].push([z, blocks[key]]);
    }
    for (const ck in index) index[ck].sort((a, b) => a[0] - b[0]);
    room._bwColumns = index;
    return index;
}

function bwStackTop(room, x, y) {
    const col = bwColumnIndex(room)[x + ',' + y];
    return (col && col.length) ? col[col.length - 1][0] : null;
}

function bwGroundLayer(room, x, y) {
    const top = bwStackTop(room, x, y);
    return top === null ? 0 : top + 1;
}

function bwCanEnter(room, x, y, standingLayer, maxStepUp) {
    if (maxStepUp === undefined) maxStepUp = BW_DEFAULT_MAX_STEP_UP;
    return bwGroundLayer(room, x, y) - standingLayer <= maxStepUp;
}

function bwCellOf(pixelValue, cellSize) {
    return Math.floor((pixelValue + cellSize / 2) / cellSize);
}

function bwHexToRgb(hex) {
    const h = String(hex || '#888888').replace('#', '');
    if (h.length !== 6) return [136, 136, 136];
    return [parseInt(h.slice(0, 2), 16), parseInt(h.slice(2, 4), 16), parseInt(h.slice(4, 6), 16)];
}

// --- renderer.py port ----------------------------------------------------

// The DDA: yields one entry per cell ENTERED, mirroring march_ray. No tex_u
// -- this port never texture-maps, so the wall-coordinate math renderer.py
// derives it from is dead weight here.
function* bwMarchRay(px, py, angleRad, cellSize, maxCells) {
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
    for (let i = 0; i < maxCells; i++) {
        let side, entry;
        if (sideX < sideY) {
            sideX += deltaX; mapX += stepX; side = 0; entry = sideX - deltaX;
        } else {
            sideY += deltaY; mapY += stepY; side = 1; entry = sideY - deltaY;
        }
        const exitCells = sideX < sideY ? sideX : sideY;
        // Texture-U: fractional position along the hit face -- same
        // derivation as march_ray.py / raycast_2_5d's castRay (Tier 4a).
        let wallCoord;
        if (side === 0) {
            wallCoord = pyCell + entry * dy;
            if (dx > 0) wallCoord = -wallCoord;
        } else {
            wallCoord = pxCell + entry * dx;
            if (dy < 0) wallCoord = -wallCoord;
        }
        const texU = wallCoord - Math.floor(wallCoord);
        yield {
            mapX, mapY, side, texU,
            entry: Math.max(entry, 1e-4) * cellSize,
            exit: exitCells * cellSize,
        };
    }
}

function bwEyeZFor(cfg) {
    // Not truncated -- z_layer is a whole number at rest (every project
    // that leaves gravity at 0, the default) but carries sub-layer
    // precision mid-jump/fall once gravity is configured (Tier 7a), the
    // same reasoning as renderer.py's own eye_z_for after that change.
    const eyeHeight = cfg.eye_height !== undefined ? cfg.eye_height : BW_DEFAULT_EYE_HEIGHT;
    return (cfg.z_layer || 0) + eyeHeight;
}

function bwClampPitch(pitchDegrees) {
    return Math.max(-BW_MAX_PITCH_DEGREES, Math.min(BW_MAX_PITCH_DEGREES, pitchDegrees));
}

function bwHorizonFor(screenH, pitchDegrees) {
    const pitch = bwClampPitch(pitchDegrees);
    return screenH * 0.5 + screenH * Math.tan(pitch * Math.PI / 180);
}

function bwScreenRay(sx, sy, facingScreenRad, fovRad, screenW, screenH, cellSize, horizon) {
    const cameraX = 2.0 * sx / screenW - 1.0;
    const offset = Math.atan(Math.tan(fovRad / 2) * cameraX);
    if (horizon === undefined) horizon = screenH * 0.5;
    const zPerPx = -(sy - horizon) * Math.cos(offset) / (screenH * cellSize);
    return { angle: facingScreenRad + offset, zPerPx };
}

// Mirrors pick_voxel exactly (see renderer.py's docstring for the gap/
// placement rules); returns {target, placement}, each [x,y,z] or null.
function bwPickVoxel(room, camX, camY, eyeZ, angleRad, zPerPx, cellSize, reach, zMin, zMax) {
    if (zMin === undefined) zMin = -64;
    if (zMax === undefined) zMax = 256;
    let first = null, prev = null, gap = null;
    for (const hit of bwMarchRay(camX, camY, angleRad, cellSize, reach)) {
        const zEntry = eyeZ + zPerPx * hit.entry;
        const zExit = eyeZ + zPerPx * hit.exit;
        const low0 = zEntry <= zExit ? zEntry : zExit;
        const high0 = zEntry <= zExit ? zExit : zEntry;
        const low = Math.max(Math.floor(low0), zMin);
        const high = Math.min(Math.floor(high0), zMax);
        if (high < low) continue;
        const layers = [];
        if (zPerPx >= 0) { for (let l = low; l <= high; l++) layers.push(l); }
        else { for (let l = high; l >= low; l--) layers.push(l); }
        for (const layer of layers) {
            if (first === null) first = [hit.mapX, hit.mapY, layer];
            if (bwGetBlock(room, hit.mapX, hit.mapY, layer) !== null) {
                if (gap !== null) return { target: [hit.mapX, hit.mapY, layer], placement: gap };
                return { target: [hit.mapX, hit.mapY, layer], placement: prev };
            }
            if (gap === null && bwGetBlock(room, hit.mapX, hit.mapY, layer + 1) !== null) {
                gap = [hit.mapX, hit.mapY, layer];
            }
            prev = [hit.mapX, hit.mapY, layer];
        }
    }
    if (gap !== null) return { target: null, placement: gap };
    return { target: null, placement: first };
}

function bwWallShade(side, corrected, maxDist) {
    const sideFactor = side === 1 ? BW_SIDE_SHADE : 1.0;
    let t = maxDist > 0 ? corrected / maxDist : 0.0;
    t = Math.max(0, Math.min(1, t));
    const distFactor = 1.0 - BW_FOG_STRENGTH * t;
    return Math.max(BW_MIN_SHADE, sideFactor * distFactor);
}

function bwFaceShade(corrected, maxDist, facing) {
    let t = maxDist > 0 ? corrected / maxDist : 0.0;
    t = Math.max(0, Math.min(1, t));
    return Math.max(BW_MIN_SHADE, Math.min(1.0, facing * (1.0 - BW_FOG_STRENGTH * t)));
}

function bwShadeColor(rgb, shade) {
    return `rgb(${Math.round(rgb[0] * shade)},${Math.round(rgb[1] * shade)},${Math.round(rgb[2] * shade)})`;
}

// Mirrors _has_neighbor: is there a stack entry at stack[index]'s z + delta?
function bwHasNeighbor(stack, index, delta) {
    const j = index + (delta > 0 ? 1 : -1);
    return j >= 0 && j < stack.length && stack[j][0] === stack[index][0] + delta;
}

// Mirrors render_block_world_view (see that docstring for the full
// projection derivation) minus texture mapping and the _fully_covers
// early-out -- see this file's header comment for why both are scoped out.
function bwRenderView(room, ctx) {
    const cfg = room.blockWorldCamera;
    const cellSize = cfg.cell_size || 32;
    const w = ctx.canvas.width, h = ctx.canvas.height;
    const horizon = bwHorizonFor(h, cfg.pitch || 0.0);

    ctx.fillStyle = cfg.ceiling_color || '#87CEEB';
    ctx.fillRect(0, 0, w, Math.trunc(horizon));
    ctx.fillStyle = cfg.floor_color || '#3a2f1c';
    ctx.fillRect(0, Math.trunc(horizon), w, h - Math.trunc(horizon));

    const camera = room.findFirstInstance(cfg.camera_object || '');
    if (!camera) return;   // flat floor/ceiling only

    // Ray origin is the camera's sprite CENTRE, not its raw x/y -- avoids
    // the exact-grid-line DDA hazard a grid-aligned body at rest would
    // otherwise hit (see renderer.py's identical comment).
    const camTL = GameRoom.spriteTopLeft(camera);
    const camX = camTL.x + camera.boxWidth() / 2;
    const camY = camTL.y + camera.boxHeight() / 2;
    const eyeZ = bwEyeZFor(cfg);

    const wallColorRgb = bwHexToRgb(cfg.wall_color || '#8a8a8a');
    const fovRad = (cfg.fov || 66) * Math.PI / 180;
    const renderDistanceCells = cfg.render_distance || 20;
    const maxDist = renderDistanceCells * cellSize;
    const numColumns = cfg.columns || Math.min(w, 320);
    const colWidth = w / numColumns;
    const facingScreenRad = -camera.facing_angle * Math.PI / 180;
    const planeTan = Math.tan(fovRad / 2);
    const textured = cfg.wall_textured !== false;
    // Top/bottom per-pixel cast resolution (Tier 4b) -- 0 disables
    // texturing (flat average-color fallback), matching desktop exactly.
    const topRes = cfg.top_cast_res !== undefined ? cfg.top_cast_res : BW_DEFAULT_TOP_CAST_RES;
    const topTextured = textured && topRes >= 1;

    // Tier 7e Phase 2/3: generate chunks around the camera before marching
    // rays through them, so a chunk exists by the time a ray reaches it.
    // No-op entirely for a room with no seed (every pre-Phase-2 project).
    bwEnsureChunksLoaded(room, camX / cellSize, camY / cellSize,
                         renderDistanceCells + BW_CHUNK_SIZE);

    const columns = bwColumnIndex(room);

    for (let col = 0; col < numColumns; col++) {
        const cameraX = 2.0 * (col + 0.5) / numColumns - 1.0;
        const rayOffset = Math.atan(planeTan * cameraX);
        const rayAngle = facingScreenRad + rayOffset;
        const cosOff = Math.cos(rayOffset);   // fisheye correction
        const dirX = Math.cos(rayAngle), dirY = Math.sin(rayAngle);
        const x0 = Math.floor(col * colWidth), x1 = Math.floor((col + 1) * colWidth);
        const stripW = Math.max(1, x1 - x0);

        // Collect near->far, paint far->near (painter's algorithm).
        const hits = [];
        for (const hit of bwMarchRay(camX, camY, rayAngle, cellSize, renderDistanceCells)) {
            const stack = columns[hit.mapX + ',' + hit.mapY];
            if (!stack || !stack.length) continue;   // air column
            const near = Math.max(hit.entry * cosOff, 1e-4);
            const far = Math.max(hit.exit * cosOff, near);
            const pxPerCell = h * cellSize / near;
            hits.push({ near, far, side: hit.side, texU: hit.texU, stack, pxPerCell });
        }

        for (let hi = hits.length - 1; hi >= 0; hi--) {
            const hitInfo = hits[hi];
            const near = hitInfo.near, far = hitInfo.far, side = hitInfo.side, stack = hitInfo.stack;
            const pxPerCell = hitInfo.pxPerCell;
            const pxPerCellFar = h * cellSize / far;
            const shade = bwWallShade(side, near, maxDist);
            const mid = (near + far) / 2.0;

            for (let i = 0; i < stack.length; i++) {
                const z = stack[i][0], blockType = stack[i][1];
                const colorSet = textured ? BLOCK_FACE_COLORS[blockType] : null;
                const sideColor = colorSet ? colorSet.side : wallColorRgb;

                const yTop = horizon + (eyeZ - (z + 1)) * pxPerCell;
                const y0v = Math.max(0, Math.floor(yTop));
                const y1v = Math.min(h, Math.ceil(yTop + pxPerCell));
                if (y1v > y0v) {
                    // Real per-pixel texture (Tier 4a) when loaded; flat
                    // average-color fallback otherwise -- mirrors the
                    // raycast HTML5 wall pass's own drawImage sub-rect
                    // technique exactly.
                    const fileSet = textured ? BLOCK_FACE_FILES[blockType] : null;
                    const tex = fileSet ? bwTexture(room._gameRef, fileSet.side) : null;
                    if (tex && tex.complete && tex.width > 0) {
                        const tw = tex.width, th = tex.height;
                        const texX = Math.min(tw - 1, Math.max(0, Math.floor(hitInfo.texU * tw)));
                        const v0 = (y0v - yTop) / pxPerCell, v1 = (y1v - yTop) / pxPerCell;
                        const srcY = Math.max(0, Math.min(th, v0 * th));
                        const srcH = Math.max(1e-3, Math.min(th - srcY, (v1 - v0) * th));
                        ctx.drawImage(tex, texX, srcY, 1, srcH, x0, y0v, stripW, y1v - y0v);
                        if (shade < 1.0) {
                            ctx.fillStyle = `rgba(0,0,0,${(1 - shade).toFixed(3)})`;
                            ctx.fillRect(x0, y0v, stripW, y1v - y0v);
                        }
                    } else {
                        ctx.fillStyle = bwShadeColor(sideColor, shade);
                        ctx.fillRect(x0, y0v, stripW, y1v - y0v);
                    }
                }

                const above = bwHasNeighbor(stack, i, 1);
                const below = bwHasNeighbor(stack, i, -1);

                if (eyeZ > z + 1 && !above) {
                    const lit = bwFaceShade(mid, maxDist, BW_TOP_SHADE);
                    const yFar = horizon + (eyeZ - (z + 1)) * pxPerCellFar;
                    const yNear = horizon + (eyeZ - (z + 1)) * pxPerCell;
                    const fileSet = topTextured ? BLOCK_FACE_FILES[blockType] : null;
                    const texData = fileSet ? bwTextureData(room._gameRef, fileSet.top) : null;
                    if (texData) {
                        bwDrawHorizontalFaceTextured(ctx, x0, stripW, yFar, yNear, texData,
                            camX, camY, dirX, dirY, cosOff, z + 1, eyeZ, horizon,
                            cellSize, lit, topRes, h);
                    } else {
                        const color = colorSet ? colorSet.top : wallColorRgb;
                        const fy0 = Math.max(0, Math.floor(Math.min(yFar, yNear)));
                        const fy1 = Math.min(h, Math.ceil(Math.max(yFar, yNear)));
                        if (fy1 > fy0) {
                            ctx.fillStyle = bwShadeColor(color, lit);
                            ctx.fillRect(x0, fy0, stripW, fy1 - fy0);
                        }
                    }
                } else if (eyeZ < z && !below) {
                    const lit = bwFaceShade(mid, maxDist, BW_BOTTOM_SHADE);
                    const yNear = horizon + (eyeZ - z) * pxPerCell;
                    const yFar = horizon + (eyeZ - z) * pxPerCellFar;
                    const fileSet = topTextured ? BLOCK_FACE_FILES[blockType] : null;
                    const texData = fileSet ? bwTextureData(room._gameRef, fileSet.bottom) : null;
                    if (texData) {
                        bwDrawHorizontalFaceTextured(ctx, x0, stripW, yNear, yFar, texData,
                            camX, camY, dirX, dirY, cosOff, z, eyeZ, horizon,
                            cellSize, lit, topRes, h);
                    } else {
                        const color = colorSet ? colorSet.bottom : wallColorRgb;
                        const fy0 = Math.max(0, Math.floor(Math.min(yNear, yFar)));
                        const fy1 = Math.min(h, Math.ceil(Math.max(yNear, yFar)));
                        if (fy1 > fy0) {
                            ctx.fillStyle = bwShadeColor(color, lit);
                            ctx.fillRect(x0, fy0, stripW, fy1 - fy0);
                        }
                    }
                }
            }
        }
    }
}

registerRoomRenderer(function(room, ctx) {
    if (room.blockWorldCamera && room.blockWorldCamera.enabled) {
        bwRenderView(room, ctx);
        return true;
    }
    return false;
});

// --- hud.py port -----------------------------------------------------------

function bwBuildHudCommands(screenWidth, screenHeight, hotbar, selectedIndex,
                             slotSize, gap, marginBottom, backColor, borderColor,
                             selectedColor, textColor, crosshairSize, crosshairColor,
                             counts) {
    const cmds = [];
    const ccx = screenWidth / 2.0, ccy = screenHeight / 2.0;
    const half = crosshairSize / 2.0;
    cmds.push({ type: 'line', x1: ccx - half, y1: ccy, x2: ccx + half, y2: ccy, color: crosshairColor });
    cmds.push({ type: 'line', x1: ccx, y1: ccy - half, x2: ccx, y2: ccy + half, color: crosshairColor });

    const n = hotbar.length;
    if (n === 0) return cmds;
    const totalW = n * slotSize + (n - 1) * gap;
    const x0 = (screenWidth - totalW) / 2.0;
    const y0 = screenHeight - marginBottom - slotSize;
    for (let i = 0; i < n; i++) {
        const blockType = hotbar[i];
        const sx = x0 + i * (slotSize + gap);
        const fill = i === selectedIndex ? selectedColor : backColor;
        cmds.push({ type: 'rectangle', x1: sx, y1: y0, x2: sx + slotSize, y2: y0 + slotSize, color: fill, filled: true });
        cmds.push({ type: 'rectangle', x1: sx, y1: y0, x2: sx + slotSize, y2: y0 + slotSize, color: borderColor, filled: false });
        cmds.push({ type: 'text', text: blockType.slice(0, 4), x: sx + 2, y: y0 + slotSize - 14, color: textColor });
        if (counts) {
            const c = counts[blockType] || 0;
            cmds.push({ type: 'text', text: String(c), x: sx + 2, y: y0 + 2, color: textColor });
        }
    }
    return cmds;
}

// ---------------------------------------------------------------------------
// Block World ACTIONS. Registered into engine.js's action switch via its
// default case (registerExtensionAction), mirroring extensions/raycast_2_5d/
// export_html5.js's own action-registration block. Each handler's (obj,
// params, game) args are the acting instance / action params / the Game.
// ---------------------------------------------------------------------------

function bwPick(obj, params, game) {
    if (!game || !game.currentRoom) return null;
    const room = game.currentRoom;
    const cfg = room.blockWorldCamera;
    if (!cfg || !cfg.enabled) return null;
    const camera = room.findFirstInstance(cfg.camera_object || '');
    if (!camera) return null;

    let reach = Math.trunc(parseNumParam(params.reach, obj, 5));
    reach = Math.max(1, reach);
    const cellSize = cfg.cell_size || 32;
    const camTL = GameRoom.spriteTopLeft(camera);
    const eyeZ = bwEyeZFor(cfg);

    const screenW = (game.canvas && game.canvas.width) || 640;
    const screenH = (game.canvas && game.canvas.height) || 480;
    const fovRad = (cfg.fov || 66) * Math.PI / 180;
    const horizon = bwHorizonFor(screenH, cfg.pitch || 0.0);
    const facingScreenRad = -camera.facing_angle * Math.PI / 180;
    const ray = bwScreenRay(screenW / 2.0, screenH / 2.0, facingScreenRad,
                             fovRad, screenW, screenH, cellSize, horizon);

    const camX = camTL.x + camera.boxWidth() / 2;
    const camY = camTL.y + camera.boxHeight() / 2;
    const picked = bwPickVoxel(room, camX, camY, eyeZ, ray.angle, ray.zPerPx, cellSize, reach);
    return { room, target: picked.target, placement: picked.placement };
}

registerExtensionAction('set_look_pitch', function(obj, params, game) {
    if (!game || !game.currentRoom) return;
    const cfg = game.currentRoom.blockWorldCamera;
    if (!cfg) return;
    let pitch = parseNumParam(params.pitch, obj, 0);
    const rel = params.relative === true || params.relative === 'true' ||
                params.relative === 1 || params.relative === '1';
    if (rel) pitch += (cfg.pitch || 0);
    cfg.pitch = bwClampPitch(pitch);
});

registerExtensionAction('select_hotbar_slot', function(obj, params, game) {
    let index = Math.trunc(parseNumParam(params.index, obj, 0));
    const rel = params.relative === true || params.relative === 'true' ||
                params.relative === 1 || params.relative === '1';
    if (rel) index += Math.trunc(obj.hotbar_index || 0);
    const n = BW_DEFAULT_HOTBAR.length;
    index = ((index % n) + n) % n;
    obj.hotbar_index = index;
    obj.hotbar_block = BW_DEFAULT_HOTBAR[index];
});

registerExtensionAction('move_and_collide', function(obj, params, game) {
    if (!game || !game.currentRoom) return;
    const room = game.currentRoom;
    const cfg = room.blockWorldCamera;
    if (!cfg || !cfg.enabled) return;

    const dx = parseNumParam(params.dx, obj, 0);
    const dy = parseNumParam(params.dy, obj, 0);
    const collide = !(params.collide === false || params.collide === 'false' ||
                       params.collide === 0 || params.collide === '0');
    const cellSize = cfg.cell_size || 32;

    const camera = room.findFirstInstance(cfg.camera_object || '');
    const isCamera = camera === obj;
    const gravityOn = isCamera && (cfg.gravity || 0) > 0;

    const tl = GameRoom.spriteTopLeft(obj);
    let tlX = tl.x, tlY = tl.y;
    let ground = bwGroundLayer(room, bwCellOf(tlX, cellSize), bwCellOf(tlY, cellSize));
    // can_enter's step-up gate compares against where the mover actually
    // IS. Grounded (legacy mode, or gravity mode at rest) that's the
    // ground below it; airborne in gravity mode it's the camera's own
    // tracked height instead -- see handlers.py's own comment on why.
    const standing = gravityOn ? (cfg.z_layer !== undefined ? cfg.z_layer : ground) : ground;

    const nx = tlX + dx;
    if (!collide || bwCanEnter(room, bwCellOf(nx, cellSize), bwCellOf(tlY, cellSize), standing)) {
        obj.x += dx; tlX = nx;
    }
    const ny = tlY + dy;
    if (!collide || bwCanEnter(room, bwCellOf(tlX, cellSize), bwCellOf(ny, cellSize), standing)) {
        obj.y += dy; tlY = ny;
    }

    if (!isCamera) return;

    ground = bwGroundLayer(room, bwCellOf(tlX, cellSize), bwCellOf(tlY, cellSize));
    if (!gravityOn) {
        cfg.z_layer = ground;
        return;
    }
    if ((cfg.vz || 0) === 0 && ground > standing) {
        cfg.z_layer = ground;
    }
    // Otherwise: airborne, or grounded with lower/equal footing ahead --
    // the apply_gravity action (bound in Step) owns z_layer from here.
});

registerExtensionAction('apply_gravity', function(obj, params, game) {
    if (!game || !game.currentRoom) return;
    const room = game.currentRoom;
    const cfg = room.blockWorldCamera;
    if (!cfg || !cfg.enabled) return;
    const gravity = cfg.gravity || 0;
    if (gravity <= 0) return;
    const camera = room.findFirstInstance(cfg.camera_object || '');
    if (camera !== obj) return;

    const cellSize = cfg.cell_size || 32;
    const tl = GameRoom.spriteTopLeft(obj);
    const ground = bwGroundLayer(room, bwCellOf(tl.x, cellSize), bwCellOf(tl.y, cellSize));

    let z = cfg.z_layer !== undefined ? cfg.z_layer : ground;
    let vz = (cfg.vz || 0) - gravity;
    vz = Math.max(vz, BW_TERMINAL_FALL_SPEED);
    z += vz;
    if (z <= ground) { z = ground; vz = 0; }

    cfg.z_layer = z;
    cfg.vz = vz;
});

registerExtensionAction('jump', function(obj, params, game) {
    if (!game || !game.currentRoom) return;
    const room = game.currentRoom;
    const cfg = room.blockWorldCamera;
    if (!cfg || !cfg.enabled) return;
    if ((cfg.gravity || 0) <= 0) return;
    const camera = room.findFirstInstance(cfg.camera_object || '');
    if (camera !== obj) return;

    const cellSize = cfg.cell_size || 32;
    const tl = GameRoom.spriteTopLeft(obj);
    const ground = bwGroundLayer(room, bwCellOf(tl.x, cellSize), bwCellOf(tl.y, cellSize));
    const z = cfg.z_layer !== undefined ? cfg.z_layer : ground;
    const vz = cfg.vz || 0;
    if (vz !== 0 || z > ground + BW_JUMP_GROUND_EPS) return;  // already airborne

    const speed = parseNumParam(params.speed, obj, BW_DEFAULT_JUMP_SPEED);
    cfg.vz = (typeof speed === 'number' && isFinite(speed)) ? speed : BW_DEFAULT_JUMP_SPEED;
});

registerExtensionAction('place_block', function(obj, params, game) {
    const picked = bwPick(obj, params, game);
    if (!picked || !picked.placement) return;
    let block = params.block !== undefined ? String(params.block) : 'stone';
    if (!BLOCK_FACE_COLORS.hasOwnProperty(block)) {
        // Not a literal block-type id -- try it as an instance-variable
        // reference (e.g. "hotbar_block", select_hotbar_slot's own
        // convention -- mirrors handlers.execute_place_block_action's
        // ae._parse_value resolving a bare instance attribute name).
        const resolved = gmExpressionValue(params.block, obj, game);
        if (resolved !== undefined && resolved !== null) block = String(resolved);
    }
    if (!BLOCK_FACE_COLORS.hasOwnProperty(block)) return;

    const cfg = picked.room.blockWorldCamera;
    if (cfg && cfg.inventory) {
        const inv = obj.block_inventory || {};
        if (!(inv[block] > 0)) return;
        inv[block] -= 1;
        obj.block_inventory = inv;
    }

    bwSetBlock(picked.room, picked.placement[0], picked.placement[1], picked.placement[2], block);
});

registerExtensionAction('break_block', function(obj, params, game) {
    const picked = bwPick(obj, params, game);
    if (!picked || !picked.target) return;
    const bt = bwGetBlock(picked.room, picked.target[0], picked.target[1], picked.target[2]);
    if (bt !== null && BW_UNBREAKABLE.has(bt)) return;

    const cfg = picked.room.blockWorldCamera;
    const protection = (cfg && cfg.protection) || {};
    const requiredKey = protection[bt];
    if (requiredKey) {
        const inv = obj.block_inventory || {};
        if (!(inv[requiredKey] > 0)) return;
    }

    bwRemoveBlock(picked.room, picked.target[0], picked.target[1], picked.target[2]);

    if (cfg && cfg.inventory) {
        const inv = obj.block_inventory || {};
        inv[bt] = (inv[bt] || 0) + 1;
        obj.block_inventory = inv;
    }

    const rewards = (cfg && cfg.rewards) || {};
    const points = rewards[bt];
    if (points) {
        game.score += points;
    }
});

registerExtensionAction('set_block_reward', function(obj, params, game) {
    if (!game || !game.currentRoom) return;
    const cfg = game.currentRoom.blockWorldCamera;
    if (!cfg || !cfg.enabled) return;

    const blockType = params.block_type !== undefined ? String(params.block_type) : '';
    if (!BLOCK_FACE_COLORS.hasOwnProperty(blockType)) return;
    const points = parseNumParam(params.points, obj, 0);
    if (typeof points !== 'number' || !isFinite(points)) return;

    if (!cfg.rewards) cfg.rewards = {};
    cfg.rewards[blockType] = points;
});

registerExtensionAction('set_block_protection', function(obj, params, game) {
    if (!game || !game.currentRoom) return;
    const cfg = game.currentRoom.blockWorldCamera;
    if (!cfg || !cfg.enabled) return;

    const blockType = params.block_type !== undefined ? String(params.block_type) : '';
    const requiredKey = params.required_key !== undefined ? String(params.required_key) : '';
    if (!BLOCK_FACE_COLORS.hasOwnProperty(blockType) ||
        !BLOCK_FACE_COLORS.hasOwnProperty(requiredKey)) return;

    if (!cfg.protection) cfg.protection = {};
    cfg.protection[blockType] = requiredKey;
});

registerExtensionAction('enable_block_world_view', function(obj, params, game) {
    if (!game || !game.currentRoom) return;
    const enable = !(params.enable === false || params.enable === 'false' ||
                      params.enable === 0 || params.enable === '0');
    const room = game.currentRoom;
    if (!enable) { room.blockWorldCamera = { enabled: false }; return; }

    const num = (k, d) => {
        const n = parseNumParam(params[k], obj, d);
        return (typeof n === 'number' && isFinite(n)) ? n : d;
    };
    // Truthy-string coercion for a boolean parameter that defaults to
    // FALSE (mirrors the `rel`/`relative` pattern above -- absent/anything
    // else reads as false, only an explicit true/'true'/1/'1' flips it).
    const boolTrue = (v) => v === true || v === 'true' || v === 1 || v === '1';

    room.blockWorldCamera = {
        enabled: true,
        camera_object: params.camera_object || obj.name,
        // A float from Tier 7a on (see bwEyeZFor) -- still a clean whole
        // number at rest, unchanged for every project that leaves gravity
        // at 0.
        z_layer: num('z_layer', 0),
        fov: num('fov', 66),
        render_distance: Math.trunc(num('render_distance', 20)),
        cell_size: Math.trunc(num('cell_size', 32)),
        columns: Math.trunc(num('columns', 320)),
        wall_color: params.wall_color || '#8a8a8a',
        floor_color: params.floor_color || '#3a2f1c',
        ceiling_color: params.ceiling_color || '#87CEEB',
        wall_textured: !(params.wall_textured === false || params.wall_textured === 'false'),
        pitch: bwClampPitch(num('pitch', 0)),
        eye_height: num('eye_height', BW_DEFAULT_EYE_HEIGHT),
        // Top/bottom per-pixel cast resolution (Tier 4b) -- 0 disables
        // texturing (flat average-color fallback), matching desktop's
        // top_cast_res semantics exactly.
        top_cast_res: Math.trunc(num('top_cast_res', BW_DEFAULT_TOP_CAST_RES)),
        // Tier 7a jump mechanic. 0 (default) = move_and_collide's original
        // instant-footing behaviour, completely unchanged. >0 switches on
        // real gravity/falling -- see the apply_gravity/jump actions.
        gravity: num('gravity', 0.0),
        vz: 0.0,
        // Tier 7c inventory-with-counts. Off (default) = unlimited
        // creative-mode placing/breaking, completely unchanged.
        inventory: boolTrue(params.inventory),
    };
    room._bwColumns = null;

    // Tier 7e Phase 2/3 procedural terrain. Off (default) = every project
    // that predates Tier 7e: room._bwSeed stays null, so
    // bwEnsureChunksLoaded/bwGenerateChunk are permanent no-ops. Stored
    // OUTSIDE room.blockWorldCamera (which this action wholesale replaces
    // every call) so generated terrain survives toggling the view off and
    // back on -- mirrors state.py's _fresh() docstring on the same point.
    room._bwSeed = boolTrue(params.generate) ? Math.trunc(num('seed', 0)) : null;
});

registerExtensionAction('load_block_world', function(obj, params, game) {
    if (!game || !game.currentRoom) return;
    const dataFile = String(params.data_file || '');
    if (!dataFile) return;

    const extData = (game.gameData && game.gameData._extension_data) || {};
    const files = extData.block_world_files || {};
    const fileData = files[dataFile];

    // Tier 7e Phase 2/3: a seeded-world save is {"seed":, "blocks":[...]}
    // instead of a bare list -- same format detection as
    // extensions/block_world/handlers.py's load_block_world action and
    // editors/block_world_editor/io.py.
    let seed = null, blockList;
    if (Array.isArray(fileData)) {
        blockList = fileData;
    } else if (fileData && typeof fileData === 'object' && Array.isArray(fileData.blocks)) {
        seed = (fileData.seed === undefined) ? null : fileData.seed;
        blockList = fileData.blocks;
    } else {
        return;   // missing/unbundled/malformed file -- no-op
    }

    // Atomic: an unknown block type rejects the WHOLE file, mirroring
    // state.load_block_list's KeyError (which the desktop action's own
    // no-op-on-bad-input handling then swallows).
    const blocks = {};
    const generated = {};
    for (const entry of blockList) {
        const bt = entry && entry.type;
        if (!BLOCK_FACE_COLORS.hasOwnProperty(bt)) return;
        blocks[entry.x + ',' + entry.y + ',' + entry.z] = bt;
        generated[bwChunkKey(entry.x, entry.y)] = true;
    }
    game.currentRoom._bwBlocks = blocks;
    // Loaded (touched) chunks must never be regenerated over -- mirrors
    // bwMarkChunkPresent's own guard.
    game.currentRoom._bwGenerated = generated;
    game.currentRoom._bwColumns = null;
    game.currentRoom._bwSeed = seed;
});

registerExtensionAction('draw_block_world_hud', function(obj, params, game) {
    if (!obj._draw_queue) obj._draw_queue = [];
    const screenW = (game && game.canvas && game.canvas.width) || 640;
    const screenH = (game && game.canvas && game.canvas.height) || 480;
    const num = (k, d) => {
        const n = parseNumParam(params[k], obj, d);
        return (typeof n === 'number' && isFinite(n)) ? n : d;
    };
    const cmds = bwBuildHudCommands(
        screenW, screenH, BW_DEFAULT_HOTBAR, Math.trunc(obj.hotbar_index || 0),
        num('slot_size', 40), num('gap', 6), num('margin_bottom', 16),
        params.back_color || '#202020', params.border_color || '#ffffff',
        params.selected_color || '#ffd040', params.text_color || '#ffffff',
        num('crosshair_size', 12), params.crosshair_color || '#ffffff',
        obj.block_inventory || null);
    obj._draw_queue.push(...cmds);
});
