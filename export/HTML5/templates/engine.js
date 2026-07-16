
// ============================================================================
// PyGameMaker HTML5 Engine - GAMEMAKER 7.0 COMPATIBLE
// ============================================================================

// Translation strings for game messages (matches Python runtime translations)
const ENGINE_TRANSLATIONS = {
    'en': {
        'score': 'Score',
        'lives': 'Lives',
        'health': 'Health',
        'room': 'Room',
        'game_over': 'Game Over',
        'high_score': 'High Score',
        'yes_or_no': 'Yes or No?'
    },
    'de': {
        'score': 'Punkte',
        'lives': 'Leben',
        'health': 'Gesundheit',
        'room': 'Raum',
        'game_over': 'Spiel vorbei',
        'high_score': 'Highscore',
        'yes_or_no': 'Ja oder Nein?'
    },
    'fr': {
        'score': 'Score',
        'lives': 'Vies',
        'health': 'Santé',
        'room': 'Niveau',
        'game_over': 'Fin de partie',
        'high_score': 'Meilleur score',
        'yes_or_no': 'Oui ou Non?'
    },
    'it': {
        'score': 'Punteggio',
        'lives': 'Vite',
        'health': 'Salute',
        'room': 'Stanza',
        'game_over': 'Fine del gioco',
        'high_score': 'Punteggio più alto',
        'yes_or_no': 'Sì o No?'
    },
    'sl': {
        'score': 'Točke',
        'lives': 'Življenja',
        'health': 'Zdravje',
        'room': 'Soba',
        'game_over': 'Konec igre',
        'high_score': 'Najboljši rezultat',
        'yes_or_no': 'Da ali Ne?'
    },
    'uk': {
        'score': 'Рахунок',
        'lives': 'Життя',
        'health': "Здоров'я",
        'room': 'Кімната',
        'game_over': 'Гра закінчена',
        'high_score': 'Найкращий результат',
        'yes_or_no': 'Так чи Ні?'
    }
};

// Get translated text (falls back to English)
function getTranslation(key, language = 'en') {
    const lang = ENGINE_TRANSLATIONS[language] || ENGINE_TRANSLATIONS['en'];
    return lang[key] || ENGINE_TRANSLATIONS['en'][key] || key;
}

// ============================================================================
// Python bridge (Pyodide) - runs execute_code actions authored in Python.
// Loaded on demand, only when the project actually contains execute_code
// actions; pure-action games keep working fully offline with no download.
// ============================================================================
const PYODIDE_URL = 'https://cdn.jsdelivr.net/pyodide/v0.26.4/full/pyodide.js';

// Python-side runtime: mirrors the IDE's execute_code environment
// (runtime/action_executor.py execute_execute_code_action): `self` with
// persistent attributes, `math`/`random` modules, a `keyboard.check()`
// shim, and exec-locals copied back onto the instance afterwards.
const PY_BOOTSTRAP = `
import json, math, random

class _ExecInstance:
    pass

_instances = {}

def _get_inst(inst_id):
    inst = _instances.get(inst_id)
    if inst is None:
        inst = _ExecInstance()
        inst._draw_queue = []
        # Sounds queued via self._sound_queue.append('snd_x') — no live
        # \`game\` object exists in this exec scope, so execute_code can't
        # call game.sounds[...].play() directly the way the desktop
        # pygame runtime does; the queue is drained into the JSON patch
        # below and actually played on the JS side (real Audio elements).
        inst._sound_queue = []
        _instances[inst_id] = inst
    return inst

class _Keyboard:
    def __init__(self, held):
        self._held = set(held)
    def check(self, key):
        return str(key).lower() in self._held
    is_pressed = check

def run_code(inst_id, code, sync_json):
    self = _get_inst(inst_id)
    sync = json.loads(sync_json)
    for key in ('x', 'y', 'mouse_x', 'mouse_y'):
        if key in sync:
            setattr(self, key, sync[key])
    exec_globals = {
        '__builtins__': __builtins__,
        'self': self,
        'sel': self,
        'instance': self,
        'other': None,
        'game': None,
        'math': math,
        'random': random,
        'keyboard': _Keyboard(sync.get('keys', [])),
    }
    exec_locals = {}
    exec(compile(code, '<execute_code>', 'exec'), exec_globals, exec_locals)
    for key, value in exec_locals.items():
        if not key.startswith('__'):
            setattr(self, key, value)
    patch = {}
    for key in ('x', 'y', 'visible'):
        if key in sync and getattr(self, key, sync.get(key)) != sync.get(key):
            patch[key] = getattr(self, key)
    if self._sound_queue:
        patch['sounds'] = self._sound_queue
        self._sound_queue = []
    return json.dumps(patch)

def run_draw(inst_id, code, sync_json):
    self = _get_inst(inst_id)
    self._draw_queue = []
    code_patch = json.loads(run_code(inst_id, code, sync_json))
    try:
        return json.dumps({'draws': self._draw_queue,
                            'sounds': code_patch.get('sounds', [])}, default=list)
    finally:
        self._draw_queue = []
`;

// Shared with the `play_sound` action handler below (executeAction's
// 'play_sound' case) — one pooled-<audio> acquisition path for both the
// structured action and the execute_code sound-queue primitive.
function acquirePooledAudio(game, name) {
    const src = game.sounds ? game.sounds[name] : null;
    if (!src) return null;
    const pool = game._audioPool[name] || (game._audioPool[name] = []);
    let audio = pool.find(a => a.paused || a.ended);
    if (!audio && pool.length < 8) {
        audio = new Audio(src);
        pool.push(audio);
    }
    return audio || null;
}

// Plays a sound queued by execute_code via self._sound_queue.append(...).
// Entries are either a bare sound name or {sound, volume}. One-shot only
// (no loop) — matches the desktop runtime's ActionExecutor._drain_sound_queue.
function playQueuedSounds(sounds, game) {
    if (!sounds || !sounds.length) return;
    for (const item of sounds) {
        const name = typeof item === 'string' ? item : (item && (item.sound || item.name)) || '';
        const volume = typeof item === 'object' && item ? item.volume : undefined;
        if (!name) continue;
        const audio = acquirePooledAudio(game, name);
        if (!audio) {
            console.warn(`queued sound not found or unsupported format: ${name}`);
            continue;
        }
        try {
            audio.loop = false;
            audio.currentTime = 0;
            if (typeof volume === 'number' && !Number.isNaN(volume)) {
                audio.volume = Math.max(0, Math.min(1, volume));
            }
            const playPromise = audio.play();
            if (playPromise && playPromise.catch) playPromise.catch(() => {});
        } catch (e) {
            console.warn('queued sound play failed:', e);
        }
    }
}

class PythonBridge {
    constructor() {
        this.pyodide = null;
        this.ready = false;
    }

    // Does any object event (top level, nested branches, keyboard sub-maps)
    // contain an execute_code action?
    static projectNeedsPython(gameData) {
        const scanActions = (actions) => (actions || []).some(a => {
            if (!a || typeof a !== 'object') return false;
            if (a.action === 'execute_code' || a.action_type === 'execute_code') return true;
            const p = a.parameters || {};
            return scanActions(p.then_actions) || scanActions(p.else_actions) ||
                   scanActions(p.actions) || scanActions(a.sub_actions);
        });
        const objects = (gameData && gameData.assets && gameData.assets.objects) || {};
        for (const obj of Object.values(objects)) {
            if (!obj || typeof obj !== 'object') continue;
            for (const ev of Object.values(obj.events || {})) {
                if (!ev || typeof ev !== 'object') continue;
                if (scanActions(ev.actions)) return true;
                // keyboard/keyboard_press style sub-event maps
                for (const sub of Object.values(ev)) {
                    if (sub && typeof sub === 'object' && scanActions(sub.actions)) return true;
                }
            }
        }
        return false;
    }

    async init(statusCallback) {
        statusCallback('Loading Python runtime…');
        await new Promise((resolve, reject) => {
            const script = document.createElement('script');
            script.src = PYODIDE_URL;
            script.onload = resolve;
            script.onerror = () => reject(new Error(
                'Could not load the Python runtime (Pyodide) from\n' + PYODIDE_URL +
                '\n\nThis game contains Python code and needs internet access ' +
                'the first time it is opened.'));
            document.head.appendChild(script);
        });
        this.pyodide = await loadPyodide();
        this.pyodide.runPython(PY_BOOTSTRAP);
        this._runCode = this.pyodide.globals.get('run_code');
        this._runDraw = this.pyodide.globals.get('run_draw');
        this.ready = true;
        statusCallback('');
        console.log('✅ Python runtime ready');
    }

    _syncJson(inst, game) {
        const held = Object.keys(game.keys || {})
            .filter(k => game.keys[k])
            .map(k => k.toLowerCase());
        return JSON.stringify({
            x: inst.x, y: inst.y, visible: inst.visible,
            mouse_x: inst.mouse_x || 0, mouse_y: inst.mouse_y || 0,
            keys: held,
        });
    }

    // Run one execute_code action; apply the returned JS-relevant patch.
    runCode(inst, code, game) {
        if (!this.ready) return;
        try {
            const patch = JSON.parse(this._runCode(inst._pyId, code, this._syncJson(inst, game)));
            if ('x' in patch) inst.x = patch.x;
            if ('y' in patch) inst.y = patch.y;
            if ('visible' in patch) inst.visible = patch.visible;
            playQueuedSounds(patch.sounds, game);
        } catch (err) {
            // Log-and-continue, matching the IDE runtime's behaviour for
            // errors inside user code.
            console.error('execute_code error:', err);
        }
    }

    // Run a draw-event execute_code action; returns the draw-command list.
    runDraw(inst, code, game) {
        if (!this.ready) return [];
        try {
            const result = JSON.parse(this._runDraw(inst._pyId, code, this._syncJson(inst, game)));
            playQueuedSounds(result.sounds, game);
            return result.draws || [];
        } catch (err) {
            console.error('draw execute_code error:', err);
            return [];
        }
    }
}

// ---------------------------------------------------------------------------
// Draw-queue rendering: the same command schema the IDE runtime processes in
// GameRunner._process_draw_queue. Canvas 2D is y-down like GameMaker room
// coordinates, so no axis flip is needed (unlike the Kivy export).
// ---------------------------------------------------------------------------
function drawCommandColor(c) {
    if (typeof c === 'string') return c;
    if (Array.isArray(c) && c.length >= 3) {
        const a = c.length > 3 ? c[3] / 255 : 1;
        return `rgba(${c[0]},${c[1]},${c[2]},${a})`;
    }
    return '#FFFFFF';
}

// Parse a numeric action parameter that may be an expression referencing
// the instance ("self.x + 16"). view_* variables default to 0, matching
// the IDE runtime's unresolved-variable fallback (views aren't implemented).
function parseNumParam(value, inst, fallback) {
    if (value === undefined || value === null || value === '') return fallback;
    if (typeof value === 'number') return value;
    const s = String(value).trim();
    const direct = parseFloat(s);
    if (!isNaN(direct) && /^[-+]?[0-9.]+$/.test(s)) return direct;
    try {
        const other = inst._collision_other;
        const expr = s
            .replace(/self\.x/g, `(${inst.x})`)
            .replace(/self\.y/g, `(${inst.y})`)
            .replace(/other\.x/g, `(${other ? other.x : 0})`)
            .replace(/other\.y/g, `(${other ? other.y : 0})`)
            .replace(/view_[a-z]+/g, '0');
        if (/^[-+*/(). 0-9]+$/.test(expr)) {
            const result = Function(`"use strict"; return (${expr});`)();
            if (typeof result === 'number' && isFinite(result)) return result;
        }
    } catch (e) { /* fall through */ }
    return fallback;
}

// Evaluate a GameMaker/Python-style expression against the instance +
// game-state scope, mirroring the IDE runtime's _eval_bool_expression
// (runtime/action_executor.py): Python operators (and/or/not,
// True/False/None) are translated to JS, and the same named scope is
// exposed — self, other, the bare motion/state names (x, y, hspeed,
// vspeed, speed, direction, image_index/speed, score, lives, health,
// room_width/height), abs/min/max/round, plus the instance's own
// primitive custom variables. Returns the raw value; callers coerce
// (test_expression -> bool, check_empty x/y -> number). Returns
// undefined on empty/error so callers apply their own fallback.
function gmExpressionValue(expr, inst, game) {
    if (expr === undefined || expr === null || String(expr).trim() === '') return undefined;
    const js = String(expr)
        .replace(/\bnot\b/g, '!')
        .replace(/\band\b/g, '&&')
        .replace(/\bor\b/g, '||')
        .replace(/\bTrue\b/g, 'true')
        .replace(/\bFalse\b/g, 'false')
        .replace(/\bNone\b/g, 'null');
    const room = game && game.currentRoom;
    const scope = {
        self: inst,
        other: inst._collision_other || null,
        x: inst.x, y: inst.y,
        hspeed: inst.hspeed || 0, vspeed: inst.vspeed || 0,
        speed: inst.speed || 0, direction: inst.direction || 0,
        image_index: inst.image_index || 0, image_speed: inst.image_speed || 0,
        score: game ? game.score : 0,
        lives: game ? game.lives : 0,
        health: game ? game.health : 0,
        room_width: room ? room.width : 0,
        room_height: room ? room.height : 0,
        abs: Math.abs, min: Math.min, max: Math.max, round: Math.round,
    };
    // Expose the instance's own PRIMITIVE custom variables as bare names
    // (mirrors the runtime's instance.__dict__ spread; objects/functions
    // and _private/internal fields are excluded).
    for (const k of Object.keys(inst)) {
        if (k.startsWith('_') || (k in scope)) continue;
        const t = typeof inst[k];
        if (t === 'number' || t === 'string' || t === 'boolean') scope[k] = inst[k];
    }
    try {
        const names = Object.keys(scope);
        const fn = new Function(...names, `"use strict"; return (${js});`);
        return fn(...names.map(n => scope[n]));
    } catch (e) {
        console.warn('expression eval failed:', expr, e);
        return undefined;
    }
}

function renderDrawCommands(ctx, cmds, game) {
    for (const cmd of (cmds || [])) {
        const color = drawCommandColor(cmd.color);
        switch (cmd.type) {
            case 'rectangle': {
                const x1 = cmd.x1 || 0, y1 = cmd.y1 || 0;
                const x2 = cmd.x2 !== undefined ? cmd.x2 : 100;
                const y2 = cmd.y2 !== undefined ? cmd.y2 : 100;
                if (cmd.filled !== false) {
                    ctx.fillStyle = color;
                    ctx.fillRect(x1, y1, x2 - x1, y2 - y1);
                } else {
                    ctx.strokeStyle = color;
                    ctx.lineWidth = 1;
                    ctx.strokeRect(x1 + 0.5, y1 + 0.5, x2 - x1 - 1, y2 - y1 - 1);
                }
                break;
            }
            case 'ellipse': {
                const x1 = cmd.x1 || 0, y1 = cmd.y1 || 0;
                const x2 = cmd.x2 !== undefined ? cmd.x2 : 100;
                const y2 = cmd.y2 !== undefined ? cmd.y2 : 100;
                ctx.beginPath();
                ctx.ellipse((x1 + x2) / 2, (y1 + y2) / 2,
                            Math.abs(x2 - x1) / 2, Math.abs(y2 - y1) / 2, 0, 0, Math.PI * 2);
                if (cmd.filled !== false) { ctx.fillStyle = color; ctx.fill(); }
                else { ctx.strokeStyle = color; ctx.lineWidth = 1; ctx.stroke(); }
                break;
            }
            case 'circle': {
                ctx.beginPath();
                ctx.arc(cmd.x || 0, cmd.y || 0, cmd.radius !== undefined ? cmd.radius : 10, 0, Math.PI * 2);
                if (cmd.filled !== false) { ctx.fillStyle = color; ctx.fill(); }
                else { ctx.strokeStyle = color; ctx.lineWidth = 1; ctx.stroke(); }
                break;
            }
            case 'line': {
                ctx.strokeStyle = color;
                ctx.lineWidth = 1;
                ctx.beginPath();
                ctx.moveTo(cmd.x1 || 0, cmd.y1 || 0);
                ctx.lineTo(cmd.x2 !== undefined ? cmd.x2 : 100, cmd.y2 !== undefined ? cmd.y2 : 100);
                ctx.stroke();
                break;
            }
            case 'arrow': {
                // Shaft + two tip segments, pre-computed by the draw_arrow
                // executeAction handler the same way the pygame runtime's
                // execute_draw_arrow_action pre-computes them.
                const x1 = cmd.x1 || 0, y1 = cmd.y1 || 0;
                const x2 = cmd.x2 !== undefined ? cmd.x2 : 100;
                const y2 = cmd.y2 !== undefined ? cmd.y2 : 100;
                const t1x = cmd.tip1_x !== undefined ? cmd.tip1_x : x2;
                const t1y = cmd.tip1_y !== undefined ? cmd.tip1_y : y2;
                const t2x = cmd.tip2_x !== undefined ? cmd.tip2_x : x2;
                const t2y = cmd.tip2_y !== undefined ? cmd.tip2_y : y2;
                ctx.strokeStyle = color;
                ctx.lineWidth = 1;
                ctx.beginPath();
                ctx.moveTo(x1, y1);
                ctx.lineTo(x2, y2);
                ctx.moveTo(x2, y2);
                ctx.lineTo(t1x, t1y);
                ctx.moveTo(x2, y2);
                ctx.lineTo(t2x, t2y);
                ctx.stroke();
                break;
            }
            case 'text':
            case 'scaled_text': {
                ctx.fillStyle = color;
                ctx.font = '18px Arial';
                ctx.textAlign = 'left';
                ctx.textBaseline = 'top';
                const tx = cmd.x || 0, ty = cmd.y || 0;
                if (cmd.type === 'scaled_text' && (cmd.xscale !== 1 || cmd.yscale !== 1)) {
                    ctx.save();
                    ctx.translate(tx, ty);
                    ctx.scale(cmd.xscale || 1, cmd.yscale || 1);
                    ctx.fillText(String(cmd.text !== undefined ? cmd.text : ''), 0, 0);
                    ctx.restore();
                } else {
                    ctx.fillText(String(cmd.text !== undefined ? cmd.text : ''), tx, ty);
                }
                break;
            }
            case 'sprite': {
                // {'type':'sprite','sprite_name':...,'x':...,'y':...} — the
                // runtime's _draw_sprite schema (subimage ignored: HTML5
                // sprites are single-frame for now).
                const img = game && game.sprites ? game.sprites[cmd.sprite_name] : null;
                if (img && img.complete) {
                    ctx.drawImage(img, cmd.x || 0, cmd.y || 0);
                }
                break;
            }
            case 'lives': {
                // Runtime _draw_lives: one sprite per remaining life,
                // left-to-right; text fallback when no usable sprite.
                const img = (cmd.sprite && game && game.sprites)
                    ? game.sprites[cmd.sprite] : null;
                const count = Math.max(0, cmd.count || 0);
                const lx = cmd.x || 0, ly = cmd.y || 0;
                if (img && img.complete && img.width) {
                    for (let i = 0; i < count; i++) {
                        ctx.drawImage(img, lx + i * img.width, ly);
                    }
                } else {
                    ctx.fillStyle = '#FFFFFF';
                    ctx.font = '18px Arial';
                    ctx.textAlign = 'left';
                    ctx.textBaseline = 'top';
                    ctx.fillText(`Lives: ${count}`, lx, ly);
                }
                break;
            }
            case 'background': {
                // {'type':'background','background_name':...,'x':...,'y':...,
                // 'tiled':...} — backgrounds are embedded into the same
                // game.sprites map as sprites by the exporter's
                // encode_sprites (background/sprite names can't collide
                // since they're separate project asset categories).
                const img = game && game.sprites ? game.sprites[cmd.background_name] : null;
                if (!img || !img.complete) break;
                const bx = cmd.x || 0, by = cmd.y || 0;
                if (cmd.tiled) {
                    const bw = img.width, bh = img.height;
                    if (bw > 0 && bh > 0) {
                        const screenW = ctx.canvas.width, screenH = ctx.canvas.height;
                        let startX = bx < 0 ? (bx % bw) - bw : bx % bw;
                        if (startX > 0) startX -= bw;
                        let startY = by < 0 ? (by % bh) - bh : by % bh;
                        if (startY > 0) startY -= bh;
                        for (let cy = startY; cy < screenH; cy += bh) {
                            for (let cx = startX; cx < screenW; cx += bw) {
                                ctx.drawImage(img, cx, cy);
                            }
                        }
                    }
                } else {
                    ctx.drawImage(img, bx, by);
                }
                break;
            }
            case 'health_bar': {
                // Runtime _draw_health_bar: filled back rect, filled
                // health-proportion rect on top, unfilled border.
                const x1 = cmd.x1 || 0, y1 = cmd.y1 || 0;
                const x2 = cmd.x2 !== undefined ? cmd.x2 : 100;
                const y2 = cmd.y2 !== undefined ? cmd.y2 : 20;
                const health = cmd.health !== undefined ? cmd.health : 100;
                const barW = x2 - x1, barH = y2 - y1;
                ctx.fillStyle = drawCommandColor(cmd.back_color || '#FF0000');
                ctx.fillRect(x1, y1, barW, barH);
                const healthW = barW * Math.max(0, Math.min(100, health)) / 100;
                if (healthW > 0) {
                    ctx.fillStyle = drawCommandColor(cmd.bar_color || '#00FF00');
                    ctx.fillRect(x1, y1, healthW, barH);
                }
                ctx.strokeStyle = '#000000';
                ctx.lineWidth = 1;
                ctx.strokeRect(x1 + 0.5, y1 + 0.5, barW - 1, barH - 1);
                break;
            }
            // Unknown command types are skipped, matching the IDE runtime's
            // dispatch-table behaviour.
        }
    }
}

// Sentinel thrown by exit_event to abort the rest of the current event's
// actions (mirrors the IDE runtime's _ExitEvent exception). Absorbed by
// GameObject.executeActions; recursive branch/repeat execution propagates it.
const EXIT_EVENT_SENTINEL = Symbol('exit_event');

console.log('🎮 Game engine loading...');

class GameObject {
    constructor(name, x, y, data, objectData) {
        this.name = name;
        // Stable id keying this instance's Python-side state (execute_code)
        this._pyId = ++GameObject._nextInstanceId;
        this.mouse_x = 0;
        this.mouse_y = 0;
        // Draw-event state: draw_* actions queue commands (runtime schema);
        // onDraw renders and clears the queue each frame.
        this._draw_queue = [];
        this._inDrawEvent = false;
        this.draw_color = null;   // set_draw_color; null = target default
        this.draw_font = null;    // set_draw_font (stored; renderer uses one font, like the runtime)

        // Sprite-strip animation (GM semantics: image_index advances by
        // image_speed per game step; wrap fires animation_end)
        this.image_index = 0.0;
        this.image_speed = 1.0;
        this.x = x;
        this.y = y;
        this.sprite = null;
        // Sprite metadata (origin, dimensions) - set when sprite is assigned
        this.spriteInfo = null;
        // Instance visibility starts from instance data
        this.visible = data.visible !== false;
        // Apply object-level visibility: if object has visible=false, instance is invisible
        if (objectData && objectData.visible === false) {
            this.visible = false;
        }
        this.solid = objectData ? (objectData.solid || false) : false;
        this.objectData = objectData;
        this.toDestroy = false;
        this.events = objectData ? (objectData.events || {}) : {};

        // GAMEMAKER 7.0: Movement properties with bidirectional sync
        this._hspeed = 0.0;
        this._vspeed = 0.0;
        this._speed = 0.0;
        this._direction = 0;
        this._friction = 0;
        this._gravity = 0;
        this._gravity_direction = 270;

        // GAMEMAKER 7.0: 12 alarm clocks per instance
        this.alarms = new Array(12).fill(-1);  // -1 = inactive, >= 0 = countdown

        // Depth-based rendering (lower = back, higher = front)
        this.depth = this.getDepthForObject(name);

        // Grid movement helpers
        this.targetX = null;
        this.targetY = null;
        this.gridMoveSpeed = 8;

        // Collision tracking
        this._collision_other = null;
        this._collision_speeds = null; // Stores speeds at moment of collision

        // Store game reference for later
        this._pendingCreateEvent = true;

        // Transformation properties
        this.rotation = data.rotation || 0;
        this.scale_x = data.scale_x || 1.0;
        this.scale_y = data.scale_y || 1.0;
    }

    // GAMEMAKER 7.0: Bidirectional speed/direction property synchronization
    get hspeed() { return this._hspeed; }
    set hspeed(value) {
        this._hspeed = value;
        this.syncSpeedDirectionFromComponents();
    }

    get vspeed() { return this._vspeed; }
    set vspeed(value) {
        this._vspeed = value;
        this.syncSpeedDirectionFromComponents();
    }

    get speed() { return this._speed; }
    set speed(value) {
        this._speed = value;
        this.syncComponentsFromSpeedDirection();
    }

    get direction() { return this._direction; }
    set direction(value) {
        this._direction = value;
        this.syncComponentsFromSpeedDirection();
    }

    get friction() { return this._friction; }
    set friction(value) { this._friction = value; }

    get gravity() { return this._gravity; }
    set gravity(value) { this._gravity = value; }

    get gravity_direction() { return this._gravity_direction; }
    set gravity_direction(value) { this._gravity_direction = value; }

    syncSpeedDirectionFromComponents() {
        // Update speed/direction when hspeed/vspeed change (GM 7.0 behavior)
        if (this._hspeed !== 0 || this._vspeed !== 0) {
            this._speed = Math.sqrt(this._hspeed**2 + this._vspeed**2);
            this._direction = Math.atan2(-this._vspeed, this._hspeed) * 180 / Math.PI;
        } else {
            this._speed = 0;
        }
    }

    syncComponentsFromSpeedDirection() {
        // Update hspeed/vspeed when speed/direction change (GM 7.0 behavior)
        if (this._speed !== 0) {
            const rad = this._direction * Math.PI / 180;
            this._hspeed = this._speed * Math.cos(rad);
            this._vspeed = -this._speed * Math.sin(rad);
        } else {
            this._hspeed = 0;
            this._vspeed = 0;
        }
    }

    getDepthForObject(name) {
        name = name || '';
        // Define rendering order layers
        if (name.includes('store') && !name.includes('box')) {
            return 0;  // Floor/store tiles at the bottom
        } else if (name.includes('ground') || name.includes('floor')) {
            return 0;
        } else if (name.includes('wall')) {
            return 5;
        } else if (name.includes('box')) {
            return 10;
        } else if (name.includes('soko') || name.includes('player')) {
            return 20;
        } else {
            return 10;
        }
    }

    // GAMEMAKER 7.0: Alarm processing
    processAlarms() {
        for (let i = 0; i < 12; i++) {
            if (this.alarms[i] > 0) {
                this.alarms[i]--;
                if (this.alarms[i] === 0) {
                    this.alarms[i] = -1;
                    this.triggerEvent(`alarm_${i}`);
                }
            }
        }
    }

    triggerEvent(eventName) {
        if (this.events && this.events[eventName]) {
            const event = this.events[eventName];
            const actions = event.actions || [];
            this.executeActions(actions, this._gameRef);
        }
    }

    // GAMEMAKER 7.0: Event handlers
    onBeginStep(game) {
        if (this.events && this.events.begin_step) {
            const event = this.events.begin_step;
            const actions = event.actions || [];
            this.executeActions(actions, game);
        }
    }

    onStep(game) {
        if (this.events && this.events.step) {
            const event = this.events.step;
            const actions = event.actions || [];
            this.executeActions(actions, game);
        }
    }

    onEndStep(game) {
        if (this.events && this.events.end_step) {
            const event = this.events.end_step;
            const actions = event.actions || [];
            this.executeActions(actions, game);
        }
    }

    onDraw(ctx) {
        // Sprite first, then the draw event's queue on top — same order as
        // the IDE runtime (GameRunner draws the sprite, then processes the
        // instance's draw queue). The draw event runs through the normal
        // action executor (so conditionals like test_lives work inside it);
        // draw_* actions queue runtime-schema commands, rendered at the end.
        this.render(ctx);
        if (!this.events || !this.events.draw) return;
        const game = this._gameRef;
        this._draw_queue = [];
        this._inDrawEvent = true;
        try {
            this.executeActions(this.events.draw.actions || [], game);
        } finally {
            this._inDrawEvent = false;
        }
        renderDrawCommands(ctx, this._draw_queue, game);
        this._draw_queue = [];
    }

    onKeyboardPress(key, game) {
        if (!this.events) return;

        // NEW: Handle keyboard_press events (fires once when key first pressed)
        if (this.events.keyboard_press) {
            this.handleKeyboardEvent(key, this.events.keyboard_press, game);
        }

        // OLD: Support legacy keyboard events
        if (this.events.keyboard) {
            const keyboardEvents = this.events.keyboard;
            const keyMap = {
                'ArrowLeft': ['left'],
                'ArrowRight': ['right'],
                'ArrowUp': ['up'],
                'ArrowDown': ['down']
            };

            const directions = keyMap[key];
            if (directions) {
                for (const dirName of directions) {
                    if (keyboardEvents[dirName] && keyboardEvents[dirName].actions) {
                        const actions = keyboardEvents[dirName].actions;
                        this.executeActions(actions, game);
                        break;
                    }
                }
            }
        }
    }

    onKeyboardHeld(key, game) {
        if (!this.events || !this.events.keyboard) return;

        // NEW: Handle keyboard events (fires continuously while key is held)
        this.handleKeyboardEvent(key, this.events.keyboard, game);
    }

    onKeyboardRelease(key, game) {
        if (!this.events || !this.events.keyboard_release) return;

        // NEW: Handle keyboard_release events (fires once when key is released)
        this.handleKeyboardEvent(key, this.events.keyboard_release, game);
    }

    onNoKey(game) {
        // Handle nokey event (fires when no arrow keys are pressed)
        if (!this.events || !this.events.keyboard || !this.events.keyboard.nokey) return;

        const nokeyEvent = this.events.keyboard.nokey;
        const actions = nokeyEvent.actions || [];
        this.executeActions(actions, game);
    }

    handleKeyboardEvent(key, eventData, game) {
        // Map browser keys to event key names (both formats)
        const keyMap = {
            'ArrowLeft': ['LEFT', 'left'],
            'ArrowRight': ['RIGHT', 'right'],
            'ArrowUp': ['UP', 'up'],
            'ArrowDown': ['DOWN', 'down'],
            ' ': ['SPACE', 'space'],
            'Enter': ['ENTER', 'enter'],
            'Escape': ['ESCAPE', 'escape'],
            'Backspace': ['BACKSPACE', 'backspace'],
            'Tab': ['TAB', 'tab'],
            'Delete': ['DELETE', 'delete']
        };

        // Handle letter keys (a-z)
        if (key.length === 1 && /[a-zA-Z]/.test(key)) {
            const upperKey = key.toUpperCase();
            const lowerKey = key.toLowerCase();
            if (eventData[upperKey] && eventData[upperKey].actions) {
                this.executeActions(eventData[upperKey].actions, game);
            } else if (eventData[lowerKey] && eventData[lowerKey].actions) {
                this.executeActions(eventData[lowerKey].actions, game);
            }
            return;
        }

        // Handle number keys (0-9)
        if (key.length === 1 && /[0-9]/.test(key)) {
            if (eventData[key] && eventData[key].actions) {
                this.executeActions(eventData[key].actions, game);
            }
            return;
        }

        // Handle special keys - try all possible formats
        const mappedKeys = keyMap[key] || [key];
        for (const mappedKey of mappedKeys) {
            if (eventData[mappedKey] && eventData[mappedKey].actions) {
                this.executeActions(eventData[mappedKey].actions, game);
                return;  // Execute only once
            }
        }
    }

    triggerCreateEvent(game) {
        if (this._pendingCreateEvent && this.events && this.events.create) {
            const createEvent = this.events.create;
            const actions = createEvent.actions || [];
            this.executeActions(actions, game);
            this._pendingCreateEvent = false;
        }
    }

    // GAMEMAKER 7.0: Movement processing
    processMovement(game) {
        // Apply gravity (GM 7.0: adds to speed each step)
        if (this._gravity !== 0) {
            const gravRad = this._gravity_direction * Math.PI / 180;
            this._hspeed += this._gravity * Math.cos(gravRad);
            this._vspeed += -this._gravity * Math.sin(gravRad);
            this.syncSpeedDirectionFromComponents();
        }

        // Apply friction (GM 7.0: reduces speed towards zero)
        if (this._friction !== 0) {
            if (Math.abs(this._hspeed) > this._friction) {
                this._hspeed -= this._friction * Math.sign(this._hspeed);
            } else {
                this._hspeed = 0;
            }

            if (Math.abs(this._vspeed) > this._friction) {
                this._vspeed -= this._friction * Math.sign(this._vspeed);
            } else {
                this._vspeed = 0;
            }
            this.syncSpeedDirectionFromComponents();
        }

        // Handle grid-based movement
        if (this.targetX !== null && this.targetY !== null) {
            const dx = this.targetX - this.x;
            const dy = this.targetY - this.y;
            const distance = Math.sqrt(dx * dx + dy * dy);

            if (distance < this.gridMoveSpeed) {
                this.x = this.targetX;
                this.y = this.targetY;
                this.targetX = null;
                this.targetY = null;
            } else {
                this.x += (dx / distance) * this.gridMoveSpeed;
                this.y += (dy / distance) * this.gridMoveSpeed;
            }
        }

        // Apply hspeed/vspeed - always move, collision events will handle response
        if (this._hspeed !== 0 || this._vspeed !== 0) {
            this.x += this._hspeed;
            this.y += this._vspeed;
        }
    }

    /**
     * Execute an array of actions with block-based conditional support.
     * Handles if_xxx/else_block patterns where actions are sequential siblings.
     */
    // GM "question" actions gate the next action/block (flat form) or run
    // their then/else branch (nested form). Any name here is routed through
    // evaluateCondition; anything NOT here that is really a question falls
    // through to executeAction as a plain action and silently fails to gate
    // (the H1 defect: test_expression / check_empty etc. were missing).
    static isConditionalAction(actionType) {
        return !!actionType && (actionType.startsWith('if_') ||
                                actionType === 'test_alignment' ||
                                actionType === 'test_variable' ||
                                actionType === 'test_score' ||
                                actionType === 'test_instance_count' ||
                                actionType === 'test_expression' ||
                                actionType === 'test_lives' ||
                                actionType === 'test_health' ||
                                actionType === 'test_chance' ||
                                actionType === 'test_question' ||
                                actionType === 'check_empty' ||
                                actionType === 'check_collision');
    }

    executeActions(actions, game) {
        // Public entry point: absorbs the exit_event sentinel so callers
        // (event dispatchers) don't need to know about it. Recursive sites
        // (repeat, nested then/else branches) call _executeActionsInner so
        // exit_event unwinds the WHOLE event, matching the IDE runtime.
        try {
            this._executeActionsInner(actions, game);
        } catch (e) {
            if (e !== EXIT_EVENT_SENTINEL) throw e;
        }
    }

    _executeActionsInner(actions, game) {
        // GM80 flat conditional semantics, mirroring the IDE runtime's
        // _execute_action_list_inner (runtime/action_executor.py): a
        // question action that evaluates false sets skipNext, which skips
        // the SINGLE next action or the next start_block..end_block group;
        // else_action inverts based on how the condition went. The previous
        // implementation treated everything up to the next if_/else as the
        // branch, which both over-ran then-branches and executed the tail
        // after an else unconditionally.
        let i = 0;
        let skipNext = false;
        let conditionWasFalse = false;

        while (i < actions.length) {
            const action = actions[i];
            const actionType = action.action;
            const params = action.parameters || {};

            if (actionType === 'else_action' || actionType === 'else_block' || actionType === 'else') {
                skipNext = !conditionWasFalse;
                i++;
                continue;
            }

            if (actionType === 'start_block' || actionType === 'start') {
                if (skipNext) {
                    let depth = 1;
                    i++;
                    while (i < actions.length && depth > 0) {
                        const t = actions[i].action;
                        if (t === 'start_block' || t === 'start') depth++;
                        else if (t === 'end_block' || t === 'end') depth--;
                        i++;
                    }
                    skipNext = false;
                    conditionWasFalse = true;
                    continue;
                }
                i++;
                continue;
            }

            if (actionType === 'end_block' || actionType === 'end') {
                skipNext = false;
                conditionWasFalse = false;
                i++;
                continue;
            }

            if (skipNext) {
                skipNext = false;
                i++;
                continue;
            }

            if (GameObject.isConditionalAction(actionType) &&
                !(params.then_actions && params.then_actions.length) &&
                !(params.else_actions && params.else_actions.length)) {
                // Flat question action: gate the next action/block.
                const result = this.evaluateCondition(action, game);
                if (result === false) {
                    skipNext = true;
                    conditionWasFalse = true;
                } else {
                    conditionWasFalse = false;
                }
                i++;
                continue;
            }

            // Regular action — or a nested-format conditional, which
            // executeAction routes through its then/else branch handler.
            this.executeAction(action, game);
            i++;
        }
    }

    /**
     * Evaluate a conditional action and return true/false.
     */
    evaluateCondition(action, game) {
        const actionType = action.action;
        const params = action.parameters || {};

        switch (actionType) {
            case 'test_alignment': {
                // Snapped to the grid? (GM "if aligned with grid" question)
                const hsnap = parseInt(params.hsnap) || 32;
                const vsnap = parseInt(params.vsnap) || 32;
                return (this.x % hsnap === 0) && (this.y % vsnap === 0);
            }

            case 'if_next_room_exists':
                const roomNamesNext = Object.keys(game.rooms);
                const currentIdxNext = roomNamesNext.indexOf(game.currentRoom.name);
                return currentIdxNext >= 0 && currentIdxNext < roomNamesNext.length - 1;

            case 'if_previous_room_exists':
                const roomNamesPrev = Object.keys(game.rooms);
                const currentIdxPrev = roomNamesPrev.indexOf(game.currentRoom.name);
                return currentIdxPrev > 0;

            case 'if_on_grid':
                const checkGridSize = params.grid_size || 32;
                const nearestGridX = Math.round(this.x / checkGridSize) * checkGridSize;
                const nearestGridY = Math.round(this.y / checkGridSize) * checkGridSize;
                const gridTolerance = Math.max(Math.abs(this._hspeed), Math.abs(this._vspeed), 4) + 1;
                return Math.abs(this.x - nearestGridX) <= gridTolerance &&
                       Math.abs(this.y - nearestGridY) <= gridTolerance;

            case 'if_collision':
            case 'if_collision_at':
                // Check collision at specified position (supports 'any', 'solid', or specific object name)
                // X and Y can be expressions like "other.hspeed*8" or plain numbers
                let collXOffset = 0;
                let collYOffset = 0;

                // Parse X expression
                if (params.x !== undefined) {
                    const xStr = params.x.toString();
                    if (xStr.includes('other.') || xStr.includes('self.') || xStr.includes('*') || xStr.includes('+') || xStr.includes('-')) {
                        // Expression - evaluate it
                        // Use stored collision speeds if available, otherwise current speeds
                        const selfHspeed = this._collision_speeds ? this._collision_speeds.selfHspeed : (this.hspeed || 0);
                        const selfVspeed = this._collision_speeds ? this._collision_speeds.selfVspeed : (this.vspeed || 0);
                        const otherHspeed = this._collision_speeds ? this._collision_speeds.otherHspeed : (this._collision_other ? this._collision_other.hspeed : 0);
                        const otherVspeed = this._collision_speeds ? this._collision_speeds.otherVspeed : (this._collision_other ? this._collision_other.vspeed : 0);
                        try {
                            const xExpr = xStr
                                .replace(/self\.x/g, this.x.toString())
                                .replace(/self\.y/g, this.y.toString())
                                .replace(/self\.hspeed/g, selfHspeed.toString())
                                .replace(/self\.vspeed/g, selfVspeed.toString())
                                .replace(/other\.hspeed/g, otherHspeed.toString())
                                .replace(/other\.vspeed/g, otherVspeed.toString())
                                .replace(/other\.x/g, (this._collision_other ? this._collision_other.x : 0).toString())
                                .replace(/other\.y/g, (this._collision_other ? this._collision_other.y : 0).toString());
                            collXOffset = eval(xExpr);
                        } catch(e) {
                            collXOffset = parseFloat(xStr) || 0;
                        }
                    } else {
                        collXOffset = parseFloat(xStr) || 0;
                    }
                }

                // Parse Y expression
                if (params.y !== undefined) {
                    const yStr = params.y.toString();
                    if (yStr.includes('other.') || yStr.includes('self.') || yStr.includes('*') || yStr.includes('+') || yStr.includes('-')) {
                        // Expression - evaluate it
                        // Use stored collision speeds if available, otherwise current speeds
                        const selfHspeed = this._collision_speeds ? this._collision_speeds.selfHspeed : (this.hspeed || 0);
                        const selfVspeed = this._collision_speeds ? this._collision_speeds.selfVspeed : (this.vspeed || 0);
                        const otherHspeed = this._collision_speeds ? this._collision_speeds.otherHspeed : (this._collision_other ? this._collision_other.hspeed : 0);
                        const otherVspeed = this._collision_speeds ? this._collision_speeds.otherVspeed : (this._collision_other ? this._collision_other.vspeed : 0);
                        try {
                            const yExpr = yStr
                                .replace(/self\.x/g, this.x.toString())
                                .replace(/self\.y/g, this.y.toString())
                                .replace(/self\.hspeed/g, selfHspeed.toString())
                                .replace(/self\.vspeed/g, selfVspeed.toString())
                                .replace(/other\.hspeed/g, otherHspeed.toString())
                                .replace(/other\.vspeed/g, otherVspeed.toString())
                                .replace(/other\.x/g, (this._collision_other ? this._collision_other.x : 0).toString())
                                .replace(/other\.y/g, (this._collision_other ? this._collision_other.y : 0).toString());
                            collYOffset = eval(yExpr);
                        } catch(e) {
                            collYOffset = parseFloat(yStr) || 0;
                        }
                    } else {
                        collYOffset = parseFloat(yStr) || 0;
                    }
                }

                const collCheckX = this.x + collXOffset;
                const collCheckY = this.y + collYOffset;
                const collObjectType = params.object || 'any';
                const notFlag = params.not_flag || false;

                // Origin- and frame-aware overlap via the shared helper (M1:
                // the old inline loop used raw this.x/inst.x as box corners,
                // ignoring sprite origin, so centered-origin sprites
                // mis-detected — while the main collision-event path already
                // applied origin via getBoundingBox). excludePartner=false
                // preserves this condition's original all-instances scope.
                const hasCollision = this.placeMeetsCollision(
                    collCheckX, collCheckY, collObjectType, game, false);

                return notFlag ? !hasCollision : hasCollision;

            case 'if_variable':
                // Compare a variable to a value
                const varName = params.variable;
                const compareValue = params.value;
                const op = params.operation || '==';
                const currentValue = this[varName];
                switch (op) {
                    case '==': return currentValue == compareValue;
                    case '!=': return currentValue != compareValue;
                    case '<': return currentValue < compareValue;
                    case '>': return currentValue > compareValue;
                    case '<=': return currentValue <= compareValue;
                    case '>=': return currentValue >= compareValue;
                    default: return currentValue == compareValue;
                }

            case 'test_variable': {
                // IDE runtime semantics (execute_test_variable_action):
                // scope sel/self (instance), other (collision), global;
                // named operations; numeric comparison when both parse.
                const name = params.variable || params.variable_name || '';
                if (!name) return false;
                const scope = params.scope || 'sel';
                let current;
                if (scope === 'global') {
                    current = game.globalVariables[name];
                } else if (scope === 'other') {
                    current = this._collision_other ? this._collision_other[name] : undefined;
                } else {
                    current = this[name];
                }
                if (current === undefined) current = 0;
                let expected = params.value;
                const cf = parseFloat(current), ef = parseFloat(expected);
                const numeric = !isNaN(cf) && !isNaN(ef);
                const a = numeric ? cf : String(current);
                const b = numeric ? ef : String(expected);
                switch (params.operation || 'equal') {
                    case 'equal': case '==': return a == b;
                    case 'not_equal': case '!=': return a != b;
                    case 'less': case '<': return a < b;
                    case 'greater': case '>': return a > b;
                    case 'less_equal': case '<=': return a <= b;
                    case 'greater_equal': case '>=': return a >= b;
                    default: return a == b;
                }
            }

            case 'test_score': {
                // Compare the game score (runtime execute_test_score_action)
                const value = parseInt(params.value) || 0;
                const score = game.score;
                switch (params.operation || 'equal') {
                    case 'equal': return score === value;
                    case 'not_equal': return score !== value;
                    case 'less': return score < value;
                    case 'greater': return score > value;
                    case 'less_equal': return score <= value;
                    case 'greater_equal': return score >= value;
                    default: return score === value;
                }
            }

            case 'test_instance_count': {
                // Count live instances of a type and compare (runtime
                // execute_test_instance_count_action)
                const objectType = params.object || '';
                if (!objectType || !game.currentRoom) return false;
                const count = game.currentRoom.instances.filter(
                    inst => inst.name === objectType && !inst.toDestroy).length;
                const target = parseInt(params.number) || 0;
                switch (params.operation || 'equal') {
                    case 'equal': return count === target;
                    case 'not_equal': return count !== target;
                    case 'less': return count < target;
                    case 'greater': return count > target;
                    case 'less_equal': return count <= target;
                    case 'greater_equal': return count >= target;
                    default: return count === target;
                }
            }

            case 'if_object_exists': {
                // Any live instance of the object type in the room?
                const objectType = params.object || '';
                if (!objectType || !game.currentRoom) return false;
                const exists = game.currentRoom.instances.some(
                    inst => inst.name === objectType && !inst.toDestroy);
                return params.not_flag ? !exists : exists;
            }

            case 'if_question':
                // Show a yes/no dialog and return result
                const question = params.message || params.question || game.translate('yes_or_no');
                return confirm(question);

            case 'test_expression': {
                // Evaluate a Python/GML boolean expression (runtime
                // _eval_bool_expression). Empty/error -> false.
                const val = gmExpressionValue(params.expression, this, game);
                return val === undefined ? false : !!val;
            }

            case 'check_empty':
            case 'check_collision': {
                // check_empty: true when the instance placed at (x, y) hits
                // NO matching object; check_collision: the inverse. objects
                // "solid" -> solids only, else "all". x/y are expressions,
                // offsets from the instance when relative (runtime
                // execute_check_empty_action).
                const ex = gmExpressionValue(params.x, this, game);
                const ey = gmExpressionValue(params.y, this, game);
                let px = (ex === undefined || isNaN(Number(ex))) ? 0 : Number(ex);
                let py = (ey === undefined || isNaN(Number(ey))) ? 0 : Number(ey);
                if (params.relative) { px += this.x; py += this.y; }
                const objects = params.objects || (params.only_solid === false ? 'all' : 'solid');
                const filter = objects === 'solid' ? 'solid' : 'all';
                const hit = this.placeMeetsCollision(px, py, filter, game);
                return actionType === 'check_collision' ? hit : !hit;
            }

            case 'test_lives': {
                // Compare game lives (runtime execute_test_lives_action)
                const value = parseInt(params.value) || 0;
                const lives = game.lives;
                switch (params.operation || 'equal') {
                    case 'equal': return lives === value;
                    case 'not_equal': return lives !== value;
                    case 'less': return lives < value;
                    case 'greater': return lives > value;
                    case 'less_equal': return lives <= value;
                    case 'greater_equal': return lives >= value;
                    default: return lives === value;
                }
            }

            case 'test_health': {
                // Compare game health (runtime execute_test_health_action)
                const value = parseFloat(params.value) || 0;
                const health = game.health;
                switch (params.operation || 'equal') {
                    case 'equal': return health === value;
                    case 'not_equal': return health !== value;
                    case 'less': return health < value;
                    case 'greater': return health > value;
                    case 'less_equal': return health <= value;
                    case 'greater_equal': return health >= value;
                    default: return health === value;
                }
            }

            case 'test_chance': {
                // 1-in-N roll (runtime execute_test_chance_action)
                let sides = parseInt(params.sides);
                if (isNaN(sides) || sides < 1) sides = 6;
                return Math.floor(Math.random() * sides) === 0;
            }

            case 'test_question':
                // Yes/No dialog (runtime execute_test_question_action)
                return confirm(params.question || params.message || game.translate('yes_or_no'));

            default:
                console.warn(`Unknown conditional action: ${actionType}`);
                return false;
        }
    }

    executeAction(action, game) {
        const actionType = action.action;
        const params = action.parameters || {};

        // Nested-format conditionals (then_actions/else_actions inside
        // parameters): evaluate and run the matching branch. The old
        // switch stub for this format silently dropped both branches.
        if (GameObject.isConditionalAction(actionType) &&
            ((params.then_actions && params.then_actions.length) ||
             (params.else_actions && params.else_actions.length))) {
            const branch = this.evaluateCondition(action, game)
                ? params.then_actions : params.else_actions;
            // inner: exit_event inside a branch aborts the whole event
            if (branch && branch.length) this._executeActionsInner(branch, game);
            return;
        }

        switch(actionType) {
            // GAMEMAKER 7.0: Movement actions
            case 'set_hspeed':
                this.hspeed = parseFloat(params.hspeed ?? params.speed ?? params.value ?? 0);
                break;

            case 'set_vspeed':
                this.vspeed = parseFloat(params.vspeed ?? params.speed ?? params.value ?? 0);
                break;

            case 'set_speed':
                this.speed = params.speed || params.value || 0;
                break;

            case 'set_direction':
                this.direction = params.direction || params.value || 0;
                break;

            case 'move_fixed':
                // GameMaker's 8-way movement
                const directions = params.directions || ['right'];
                const speed = params.speed || 4;
                const dirMap = {
                    'right': 0, 'up-right': 45, 'up': 90, 'up-left': 135,
                    'left': 180, 'down-left': 225, 'down': 270, 'down-right': 315,
                    'stop': -1
                };
                if (directions.includes('stop')) {
                    this.speed = 0;
                } else if (directions.length === 1) {
                    this.direction = dirMap[directions[0]] || 0;
                    this.speed = speed;
                } else {
                    // Random direction from multiple choices
                    const validDirs = directions.filter(d => d !== 'stop').map(d => dirMap[d] || 0);
                    this.direction = validDirs[Math.floor(Math.random() * validDirs.length)];
                    this.speed = speed;
                }
                break;

            case 'move_free':
                this.direction = params.direction || 0;
                this.speed = params.speed || 4;
                break;

            case 'move_towards':
                const targetX = params.x || 0;
                const targetY = params.y || 0;
                const moveSpeed = params.speed || 4;
                this.direction = Math.atan2(-(targetY - this.y), targetX - this.x) * 180 / Math.PI;
                this.speed = moveSpeed;
                break;

            case 'set_gravity':
                this.gravity_direction = params.direction || 270;
                this.gravity = params.gravity || 0.5;
                break;

            case 'set_friction':
                this.friction = params.friction || 0.1;
                break;

            case 'reverse_horizontal':
                this.hspeed = -this.hspeed;
                break;

            case 'reverse_vertical':
                this.vspeed = -this.vspeed;
                break;

            case 'bounce':
                // GAMEMAKER 7.0: Bounce off solid objects
                // Use movement direction to determine bounce axis
                if (this._collision_other) {
                    const other = this._collision_other;
                    // Use bounding boxes for collision calculation
                    const myBox = this.getBoundingBox();
                    const otherBox = other.getBoundingBox();

                    // Store original speeds before reversing
                    const origHspeed = this._hspeed;
                    const origVspeed = this._vspeed;

                    // Determine bounce direction based on current speed
                    const movingHorizontal = Math.abs(origHspeed) > 0.1;
                    const movingVertical = Math.abs(origVspeed) > 0.1;

                    // Get my origin for position adjustment
                    const myOriginX = this.spriteInfo ? this.spriteInfo.origin_x : 0;
                    const myOriginY = this.spriteInfo ? this.spriteInfo.origin_y : 0;

                    if (movingHorizontal && !movingVertical) {
                        // Moving purely horizontally - bounce horizontally
                        this._hspeed = -origHspeed;
                        // Push out based on ORIGINAL direction (before bounce)
                        if (origHspeed > 0) {
                            // Was moving right, push left - set my right edge to other's left edge
                            this.x = otherBox.x - myBox.width + myOriginX;
                        } else {
                            // Was moving left, push right - set my left edge to other's right edge
                            this.x = otherBox.x + otherBox.width + myOriginX;
                        }
                    } else if (movingVertical && !movingHorizontal) {
                        // Moving purely vertically - bounce vertically
                        this._vspeed = -origVspeed;
                        if (origVspeed > 0) {
                            this.y = otherBox.y - myBox.height + myOriginY;
                        } else {
                            this.y = otherBox.y + otherBox.height + myOriginY;
                        }
                    } else if (movingHorizontal && movingVertical) {
                        // Moving diagonally - use overlap to determine which axis
                        const overlapX = Math.min(
                            myBox.x + myBox.width - otherBox.x,
                            otherBox.x + otherBox.width - myBox.x
                        );
                        const overlapY = Math.min(
                            myBox.y + myBox.height - otherBox.y,
                            otherBox.y + otherBox.height - myBox.y
                        );

                        if (overlapX < overlapY) {
                            this._hspeed = -origHspeed;
                            if (origHspeed > 0) {
                                this.x = otherBox.x - myBox.width + myOriginX;
                            } else {
                                this.x = otherBox.x + otherBox.width + myOriginX;
                            }
                        } else {
                            this._vspeed = -origVspeed;
                            if (origVspeed > 0) {
                                this.y = otherBox.y - myBox.height + myOriginY;
                            } else {
                                this.y = otherBox.y + otherBox.height + myOriginY;
                            }
                        }
                    } else {
                        // Not moving - just push out based on overlap
                        const overlapLeft = (myBox.x + myBox.width) - otherBox.x;
                        const overlapRight = (otherBox.x + otherBox.width) - myBox.x;
                        const overlapTop = (myBox.y + myBox.height) - otherBox.y;
                        const overlapBottom = (otherBox.y + otherBox.height) - myBox.y;
                        const minOverlap = Math.min(overlapLeft, overlapRight, overlapTop, overlapBottom);

                        if (minOverlap === overlapLeft) this.x = otherBox.x - myBox.width + myOriginX;
                        else if (minOverlap === overlapRight) this.x = otherBox.x + otherBox.width + myOriginX;
                        else if (minOverlap === overlapTop) this.y = otherBox.y - myBox.height + myOriginY;
                        else this.y = otherBox.y + otherBox.height + myOriginY;
                    }
                    this.syncSpeedDirectionFromComponents();
                } else {
                    // No collision other - just reverse both
                    this._hspeed = -this._hspeed;
                    this._vspeed = -this._vspeed;
                    this.syncSpeedDirectionFromComponents();
                }
                break;

            case 'stop_movement':
                // Push out of collision first if we have collision info
                if (this._collision_other) {
                    const other = this._collision_other;
                    // Use bounding boxes for collision calculation
                    const myBox = this.getBoundingBox();
                    const otherBox = other.getBoundingBox();

                    // Get my origin for position adjustment
                    const myOriginX = this.spriteInfo ? this.spriteInfo.origin_x : 0;
                    const myOriginY = this.spriteInfo ? this.spriteInfo.origin_y : 0;

                    // Calculate overlaps using bounding boxes
                    const overlapLeft = (myBox.x + myBox.width) - otherBox.x;
                    const overlapRight = (otherBox.x + otherBox.width) - myBox.x;
                    const overlapTop = (myBox.y + myBox.height) - otherBox.y;
                    const overlapBottom = (otherBox.y + otherBox.height) - myBox.y;

                    // Find smallest overlap to push out
                    const minOverlap = Math.min(overlapLeft, overlapRight, overlapTop, overlapBottom);

                    if (minOverlap === overlapLeft && overlapLeft > 0) {
                        this.x = otherBox.x - myBox.width + myOriginX;
                    } else if (minOverlap === overlapRight && overlapRight > 0) {
                        this.x = otherBox.x + otherBox.width + myOriginX;
                    } else if (minOverlap === overlapTop && overlapTop > 0) {
                        this.y = otherBox.y - myBox.height + myOriginY;
                    } else if (minOverlap === overlapBottom && overlapBottom > 0) {
                        this.y = otherBox.y + otherBox.height + myOriginY;
                    }
                }

                this.hspeed = 0;
                this.vspeed = 0;
                this.speed = 0;
                this.targetX = null;
                this.targetY = null;
                // Don't snap to grid - it can push player back into walls
                break;

            case 'jump_to_position':
                // Jump to position - supports expressions and relative mode
                let jumpX = 0;
                let jumpY = 0;
                const jumpRelative = params.relative || false;

                // Parse X expression
                if (params.x !== undefined) {
                    const xStr = params.x.toString();
                    if (xStr.includes('other.') || xStr.includes('self.') || xStr.includes('*') || xStr.includes('+') || xStr.includes('-')) {
                        // Use stored collision speeds if available, otherwise current speeds
                        const selfHspeedJump = this._collision_speeds ? this._collision_speeds.selfHspeed : (this.hspeed || 0);
                        const selfVspeedJump = this._collision_speeds ? this._collision_speeds.selfVspeed : (this.vspeed || 0);
                        const otherHspeedJump = this._collision_speeds ? this._collision_speeds.otherHspeed : (this._collision_other ? this._collision_other.hspeed : 0);
                        const otherVspeedJump = this._collision_speeds ? this._collision_speeds.otherVspeed : (this._collision_other ? this._collision_other.vspeed : 0);
                        try {
                            const xExpr = xStr
                                .replace(/self\.x/g, this.x.toString())
                                .replace(/self\.y/g, this.y.toString())
                                .replace(/self\.hspeed/g, selfHspeedJump.toString())
                                .replace(/self\.vspeed/g, selfVspeedJump.toString())
                                .replace(/other\.hspeed/g, otherHspeedJump.toString())
                                .replace(/other\.vspeed/g, otherVspeedJump.toString())
                                .replace(/other\.x/g, (this._collision_other ? this._collision_other.x : 0).toString())
                                .replace(/other\.y/g, (this._collision_other ? this._collision_other.y : 0).toString());
                            jumpX = eval(xExpr);
                        } catch(e) {
                            jumpX = parseFloat(xStr) || 0;
                        }
                    } else {
                        jumpX = parseFloat(xStr) || 0;
                    }
                }

                // Parse Y expression
                if (params.y !== undefined) {
                    const yStr = params.y.toString();
                    if (yStr.includes('other.') || yStr.includes('self.') || yStr.includes('*') || yStr.includes('+') || yStr.includes('-')) {
                        // Use stored collision speeds if available, otherwise current speeds
                        const selfHspeedJumpY = this._collision_speeds ? this._collision_speeds.selfHspeed : (this.hspeed || 0);
                        const selfVspeedJumpY = this._collision_speeds ? this._collision_speeds.selfVspeed : (this.vspeed || 0);
                        const otherHspeedJumpY = this._collision_speeds ? this._collision_speeds.otherHspeed : (this._collision_other ? this._collision_other.hspeed : 0);
                        const otherVspeedJumpY = this._collision_speeds ? this._collision_speeds.otherVspeed : (this._collision_other ? this._collision_other.vspeed : 0);
                        try {
                            const yExpr = yStr
                                .replace(/self\.x/g, this.x.toString())
                                .replace(/self\.y/g, this.y.toString())
                                .replace(/self\.hspeed/g, selfHspeedJumpY.toString())
                                .replace(/self\.vspeed/g, selfVspeedJumpY.toString())
                                .replace(/other\.hspeed/g, otherHspeedJumpY.toString())
                                .replace(/other\.vspeed/g, otherVspeedJumpY.toString())
                                .replace(/other\.x/g, (this._collision_other ? this._collision_other.x : 0).toString())
                                .replace(/other\.y/g, (this._collision_other ? this._collision_other.y : 0).toString());
                            jumpY = eval(yExpr);
                        } catch(e) {
                            jumpY = parseFloat(yStr) || 0;
                        }
                    } else {
                        jumpY = parseFloat(yStr) || 0;
                    }
                }

                // Apply position (relative or absolute)
                if (jumpRelative) {
                    this.x += jumpX;
                    this.y += jumpY;
                } else {
                    this.x = jumpX;
                    this.y = jumpY;
                }
                break;

            // GAMEMAKER 7.0: Alarm actions
            case 'set_alarm':
                const alarmNum = params.alarm_number || 0;
                const steps = params.steps || 30;
                if (alarmNum >= 0 && alarmNum < 12) {
                    this.alarms[alarmNum] = steps;
                }
                break;

            // GAMEMAKER 7.0: Control actions
            // NOTE: test_expression / check_empty / check_collision are
            // conditionals (isConditionalAction) and are handled by
            // evaluateCondition — they no longer fall through to here as
            // no-op stubs (the H1 fix).

            case 'repeat':
                const times = params.times || 1;
                const repeatActions = params.actions || [];
                for (let i = 0; i < times; i++) {
                    // inner: an exit_event inside the block aborts the whole
                    // event AND the remaining iterations (IDE runtime M43)
                    this._executeActionsInner(repeatActions, game);
                }
                break;

            case 'exit_event':
                // Abort the rest of this event's actions (the old `return`
                // only left executeAction, so the event kept running).
                throw EXIT_EVENT_SENTINEL;

            // Grid movement (existing)
            case 'grid_move':
            case 'move_grid':
                const dir = params.direction;
                const gridSize = params.grid_size || 32;

                let newX = this.x;
                let newY = this.y;
                let deltaX = 0;
                let deltaY = 0;

                switch(dir) {
                    case 'left': newX -= gridSize; deltaX = -gridSize; break;
                    case 'right': newX += gridSize; deltaX = gridSize; break;
                    case 'up': newY -= gridSize; deltaY = -gridSize; break;
                    case 'down': newY += gridSize; deltaY = gridSize; break;
                }

                const objectAtTarget = this.getObjectAt(newX, newY, game);

                if (objectAtTarget && objectAtTarget.name.includes('box')) {
                    const boxNewX = objectAtTarget.x + deltaX;
                    const boxNewY = objectAtTarget.y + deltaY;
                    const canPushBox = !objectAtTarget.checkCollisionAt(boxNewX, boxNewY, game);

                    if (canPushBox) {
                        objectAtTarget.targetX = boxNewX;
                        objectAtTarget.targetY = boxNewY;
                        this.targetX = newX;
                        this.targetY = newY;
                    }
                } else {
                    const canMove = !this.checkCollisionAt(newX, newY, game);
                    if (canMove) {
                        this.targetX = newX;
                        this.targetY = newY;
                    }
                }
                break;

            case 'snap_to_grid':
                const snapGridSize = params.grid_size || 32;
                this.x = Math.round(this.x / snapGridSize) * snapGridSize;
                this.y = Math.round(this.y / snapGridSize) * snapGridSize;
                break;

            case 'if_on_grid':
                const checkGridSize = params.grid_size || 32;
                // Use tolerance-based grid check (handles floating point positions)
                const nearestGridX = Math.round(this.x / checkGridSize) * checkGridSize;
                const nearestGridY = Math.round(this.y / checkGridSize) * checkGridSize;
                const gridTolerance = Math.max(Math.abs(this._hspeed), Math.abs(this._vspeed), 4) + 1;
                const isOnGrid = Math.abs(this.x - nearestGridX) <= gridTolerance &&
                                 Math.abs(this.y - nearestGridY) <= gridTolerance;

                if (isOnGrid) {
                    if (params.then_actions) {
                        this.executeActions(params.then_actions, game);
                    }
                } else if (params.else_actions) {
                    this.executeActions(params.else_actions, game);
                }
                break;

            case 'stop_if_no_keys':
                // Check if any arrow keys are currently pressed
                const arrowKeys = ['ArrowLeft', 'ArrowRight', 'ArrowUp', 'ArrowDown'];
                const anyArrowKeyPressed = arrowKeys.some(key => game.keys[key]);

                if (!anyArrowKeyPressed) {
                    // No arrow keys pressed - stop movement
                    this.hspeed = 0;
                    this.vspeed = 0;
                    this.speed = 0;
                    this.targetX = null;
                    this.targetY = null;
                }
                // If keys ARE pressed, do nothing (keep moving)
                break;

            case 'if_collision_at':
                let checkX = this.x;
                let checkY = this.y;

                if (params.x) {
                    const xExpr = params.x.toString()
                        .replace('self.x', this.x.toString())
                        .replace('self.y', this.y.toString());
                    try { checkX = eval(xExpr); } catch(e) {}
                }

                if (params.y) {
                    const yExpr = params.y.toString()
                        .replace('self.x', this.x.toString())
                        .replace('self.y', this.y.toString());
                    try { checkY = eval(yExpr); } catch(e) {}
                }

                const objectType = params.object_type || params.object_types;
                const targetObject = this.getObjectAt(checkX, checkY, game);

                let collisionFound = false;
                if (targetObject) {
                    if (objectType === 'solid' && targetObject.solid) {
                        collisionFound = true;
                    } else if (objectType === 'any' || targetObject.name === objectType ||
                        (Array.isArray(objectType) && objectType.includes(targetObject.name))) {
                        collisionFound = true;
                    }
                }

                if (collisionFound && params.then_actions) {
                    this.executeActions(params.then_actions, game);
                } else if (!collisionFound && params.else_actions) {
                    this.executeActions(params.else_actions, game);
                }
                break;

            case 'if_condition':
            case 'if_variable':
                // Variable checking logic (existing code)
                break;

            case 'destroy_instance':
                const target = params.target || 'self';
                if (target === 'other' && this._collision_other) {
                    this._collision_other.toDestroy = true;
                } else {
                    this.toDestroy = true;
                }
                break;

            case 'next_room':
            case 'room_goto_next':
                // Go to next room in the room order
                const roomNamesNext = Object.keys(game.rooms);
                const currentIndexNext = roomNamesNext.indexOf(game.currentRoom.name);
                if (currentIndexNext >= 0 && currentIndexNext < roomNamesNext.length - 1) {
                    const nextRoomName = roomNamesNext[currentIndexNext + 1];
                    game.changeRoom(nextRoomName);
                } else {
                    console.log('Already at last room');
                }
                break;

            case 'previous_room':
                // Go to previous room in the room order
                const roomNamesPrev = Object.keys(game.rooms);
                const currentIndexPrev = roomNamesPrev.indexOf(game.currentRoom.name);
                if (currentIndexPrev > 0) {
                    const prevRoomName = roomNamesPrev[currentIndexPrev - 1];
                    game.changeRoom(prevRoomName);
                } else {
                    console.log('Already at first room');
                }
                break;

            case 'restart_room':
                // Restart current room
                game.changeRoom(game.currentRoom.name);
                break;

            case 'change_room':
            case 'go_to_room':
            case 'goto_room':
                let roomName = params.room_name || params.room;

                if (roomName === '__next__') {
                    const roomNames = Object.keys(game.rooms);
                    const currentIndex = roomNames.indexOf(game.currentRoom.name);
                    if (currentIndex >= 0 && currentIndex < roomNames.length - 1) {
                        roomName = roomNames[currentIndex + 1];
                    } else {
                        return;
                    }
                } else if (roomName === '__previous__') {
                    const roomNames = Object.keys(game.rooms);
                    const currentIndex = roomNames.indexOf(game.currentRoom.name);
                    if (currentIndex > 0) {
                        roomName = roomNames[currentIndex - 1];
                    } else {
                        return;
                    }
                } else if (roomName === '__restart__') {
                    roomName = game.currentRoom.name;
                }

                if (roomName && game.rooms[roomName]) {
                    game.changeRoom(roomName);
                }
                break;

            case 'if_next_room_exists':
                // Note: Block-based if/else handling is done in executeActions()
                // This case handles legacy nested then_actions/else_actions format
                const roomNamesForNext = Object.keys(game.rooms);
                const currentIdxForNext = roomNamesForNext.indexOf(game.currentRoom.name);
                const nextRoomExists = currentIdxForNext >= 0 && currentIdxForNext < roomNamesForNext.length - 1;

                if (nextRoomExists && params.then_actions) {
                    this.executeActions(params.then_actions, game);
                } else if (!nextRoomExists && params.else_actions) {
                    this.executeActions(params.else_actions, game);
                }
                break;

            case 'if_previous_room_exists':
                // Note: Block-based if/else handling is done in executeActions()
                // This case handles legacy nested then_actions/else_actions format
                const roomNamesForPrev = Object.keys(game.rooms);
                const currentIdxForPrev = roomNamesForPrev.indexOf(game.currentRoom.name);
                const prevRoomExists = currentIdxForPrev > 0;

                if (prevRoomExists && params.then_actions) {
                    this.executeActions(params.then_actions, game);
                } else if (!prevRoomExists && params.else_actions) {
                    this.executeActions(params.else_actions, game);
                }
                break;

            case 'else_block':
            case 'else_action':
                // Else blocks are handled by their parent if_* actions
                // They should not be executed directly
                break;

            case 'display_message':
            case 'show_message':
                // Display a message dialog
                const message = params.message || params.text || '';
                if (message) {
                    // Stop movement and snap to grid before showing message
                    // This prevents the player from drifting off-grid during collision events
                    this.hspeed = 0;
                    this.vspeed = 0;
                    this.speed = 0;
                    const msgGridSize = 32;
                    this.x = Math.round(this.x / msgGridSize) * msgGridSize;
                    this.y = Math.round(this.y / msgGridSize) * msgGridSize;

                    // Also stop and snap the collision "other" object if applicable
                    if (this._collision_other) {
                        this._collision_other.hspeed = 0;
                        this._collision_other.vspeed = 0;
                        this._collision_other.speed = 0;
                        this._collision_other.x = Math.round(this._collision_other.x / msgGridSize) * msgGridSize;
                        this._collision_other.y = Math.round(this._collision_other.y / msgGridSize) * msgGridSize;
                    }

                    alert(message);
                }
                break;

            // GAMEMAKER 7.0: Score, Lives, Health actions
            case 'set_score':
                if (params.relative) {
                    game.score += parseFloat(params.value) || 0;
                } else {
                    game.score = parseFloat(params.value) || 0;
                }
                console.log(`📊 Score: ${game.score}`);
                break;

            case 'set_lives': {
                const oldLives = game.lives;
                if (params.relative) {
                    game.lives += parseFloat(params.value) || 0;
                } else {
                    game.lives = parseFloat(params.value) || 0;
                }
                console.log(`❤️ Lives: ${game.lives}`);
                // IDE-runtime semantics: when lives cross from >0 to <=0,
                // fire no_more_lives once on EVERY instance that defines it
                // (not just the instance whose action decremented lives).
                if (oldLives > 0 && game.lives <= 0 && game.currentRoom) {
                    [...game.currentRoom.instances].forEach(inst => {
                        if (!inst.toDestroy && inst.events && inst.events.no_more_lives) {
                            inst.executeActions(inst.events.no_more_lives.actions || [], game);
                        }
                    });
                }
                break;
            }

            case 'set_health':
                if (params.relative) {
                    game.health += parseFloat(params.value) || 0;
                } else {
                    game.health = parseFloat(params.value) || 0;
                }
                game.health = Math.max(0, Math.min(100, game.health));
                console.log(`💚 Health: ${game.health}`);
                break;

            case 'jump_to_start':
                // Return to starting position
                if (this._startX !== undefined && this._startY !== undefined) {
                    this.x = this._startX;
                    this.y = this._startY;
                }
                this.hspeed = 0;
                this.vspeed = 0;
                this.speed = 0;
                break;

            case 'restart_game':
                // Reload the page to restart
                window.location.reload();
                break;

            case 'end_game':
            case 'game_end':
                game.running = false;
                alert(game.translate('game_over'));
                break;

            case 'show_highscore':
                alert(`${game.translate('high_score')}: ${game.score}`);
                break;

            case 'comment':
                // Authoring-time annotation; no runtime effect.
                break;

            case 'start_moving_direction': {
                // Set motion toward one of the named directions (random pick
                // when several are given), or stop. Mirrors the IDE runtime's
                // execute_start_moving_direction_action, including tolerating
                // the stringified-list form "['down', 'up']" (see TODO.md,
                // maze_3 list-param note).
                let dirs = params.directions;
                const moveSpeed = parseFloat(params.speed) || 0;
                if (typeof dirs === 'string' && dirs.trim().startsWith('[')) {
                    dirs = dirs.replace(/[\[\]'"\s]/g, '').split(',').filter(Boolean);
                }
                if (typeof dirs === 'string') dirs = [dirs];
                if (!Array.isArray(dirs) || dirs.length === 0) break;
                const choice = String(dirs[Math.floor(Math.random() * dirs.length)]).toLowerCase();
                if (choice === 'stop' || choice === 'none') {
                    this.hspeed = 0;
                    this.vspeed = 0;
                    break;
                }
                // GM angles (0=right, 90=up); diagonals move at `speed`
                // magnitude along the angle, matching the IDE runtime.
                const angles = {
                    'right': 0, 'up-right': 45, 'upright': 45, 'up': 90,
                    'up-left': 135, 'upleft': 135, 'left': 180,
                    'down-left': 225, 'downleft': 225, 'down': 270,
                    'down-right': 315, 'downright': 315,
                };
                const angle = angles[choice];
                if (angle === undefined) break;
                const rad = angle * Math.PI / 180;
                this.hspeed = moveSpeed * Math.cos(rad);
                this.vspeed = -moveSpeed * Math.sin(rad);  // screen y is down
                break;
            }

            case 'set_variable': {
                // scope sel/self (instance), other (collision), global;
                // relative adds to the current value.
                const name = params.variable || params.variable_name || '';
                if (!name) break;
                let value = params.value;
                const num = parseFloat(value);
                if (!isNaN(num) && String(num) === String(value).trim()) value = num;
                const scope = params.scope || 'sel';
                const target = scope === 'global' ? game.globalVariables
                    : (scope === 'other' ? this._collision_other : this);
                if (!target) break;
                if (params.relative) {
                    const current = parseFloat(target[name]) || 0;
                    value = current + (parseFloat(value) || 0);
                }
                target[name] = value;
                break;
            }

            case 'set_window_caption':
                // Caption display settings; on the web the caption is the
                // document title (the HUD bar shows score/lives already).
                game.showScoreInCaption = params.show_score !== false;
                game.showLivesInCaption = params.show_lives !== false;
                game.showHealthInCaption = params.show_health === true;
                if (params.caption) document.title = params.caption;
                break;

            case 'enable_views': {
                // Turn the room's camera system on/off (mirrors the desktop
                // execute_enable_views_action).
                if (!game.currentRoom) break;
                const v = params.enable !== undefined ? params.enable : params.enabled;
                game.currentRoom.viewsEnabled = !(v === false || v === 'false' || v === 0);
                break;
            }

            case 'set_view': {
                // Configure one of the 8 views (mirrors set_view: only the
                // provided fields change; others keep their current value).
                if (!game.currentRoom) break;
                let vi = parseInt(params.view);
                if (isNaN(vi) || vi < 0 || vi > 7) vi = 0;
                const view = game.currentRoom.views[vi];
                const setNum = (k) => {
                    if (params[k] !== undefined) {
                        const n = parseNumParam(params[k], this, view[k]);
                        view[k] = Math.trunc(n);
                    }
                };
                if (params.visible !== undefined) {
                    const vis = params.visible;
                    view.visible = !(vis === false || vis === 'false' || vis === 0 ||
                                     (typeof vis === 'string' && vis.toLowerCase() === 'no'));
                }
                ['view_x', 'view_y', 'view_w', 'view_h',
                 'port_x', 'port_y', 'port_w', 'port_h',
                 'hborder', 'vborder', 'hspeed', 'vspeed'].forEach(setNum);
                if (params.follow !== undefined) {
                    view.follow = params.follow || null;
                }
                break;
            }

            case 'move_to_contact': {
                // Move pixel-by-pixel toward `direction` (degrees, 0=right,
                // 90=up) until touching `object` ("all"/"solid"/<name>) or
                // max_distance — the platformer landing action.
                const dirDeg = parseFloat(params.direction) || 0;
                const maxDist = parseFloat(params.max_distance ?? params.maximum ?? 1000) || 1000;
                const target = params.object || 'all';
                const rad = dirDeg * Math.PI / 180;
                const dx = Math.cos(rad), dy = -Math.sin(rad);
                const boxesOverlap = (a, b) =>
                    a.x < b.x + b.width && a.x + a.width > b.x &&
                    a.y < b.y + b.height && a.y + a.height > b.y;
                const touches = () => {
                    if (!game.currentRoom) return false;
                    const myBox = this.getBoundingBox();
                    for (const other of game.currentRoom.instances) {
                        if (other === this || other.toDestroy) continue;
                        if (target === 'solid' && !other.solid) continue;
                        if (target !== 'all' && target !== 'solid' && other.name !== target) continue;
                        if (boxesOverlap(myBox, other.getBoundingBox())) return true;
                    }
                    return false;
                };
                for (let i = 0; i < Math.floor(maxDist); i++) {
                    this.x += dx;
                    this.y += dy;
                    if (touches()) break;
                }
                break;
            }

            case 'play_sound': {
                // Sounds are embedded as data URLs (soundsData); a small
                // per-sound pool lets overlapping plays coexist. Autoplay
                // policy may reject play() before the first user gesture —
                // swallowed, matching a muted-until-interaction browser.
                const soundName = params.sound || '';
                if (!soundName) break;
                const audio = acquirePooledAudio(game, soundName);
                if (!audio) {
                    console.warn(`play_sound: sound not found or unsupported format: ${soundName}`);
                    break;
                }
                try {
                    audio.loop = params.loop === true || params.loop === 'true';
                    audio.currentTime = 0;
                    const playPromise = audio.play();
                    if (playPromise && playPromise.catch) playPromise.catch(() => {});
                } catch (e) {
                    console.warn('play_sound failed:', e);
                }
                break;
            }

            case 'stop_all_sounds':
                for (const pool of Object.values(game._audioPool || {})) {
                    for (const audio of pool) {
                        audio.pause();
                        audio.currentTime = 0;
                    }
                }
                break;

            case 'set_sprite': {
                // sprite "<self>" keeps the current sprite; subimage/speed
                // of -1 leave animation state untouched (runtime semantics).
                const spriteName = params.sprite || '<self>';
                if (spriteName && spriteName !== '<self>') {
                    const img = game.sprites ? game.sprites[spriteName] : null;
                    if (img) {
                        this.sprite = img;
                        this.spriteInfo = game.makeSpriteInfo(spriteName);
                    } else {
                        console.warn(`set_sprite: sprite not found: ${spriteName}`);
                    }
                }
                const subimage = params.subimage !== undefined
                    ? parseInt(params.subimage) : -1;
                if (!isNaN(subimage) && subimage >= 0) this.image_index = subimage;
                const animSpeed = params.speed !== undefined
                    ? parseFloat(params.speed) : -1;
                if (!isNaN(animSpeed) && animSpeed >= 0) this.image_speed = animSpeed;
                break;
            }

            case 'change_instance': {
                // Become a different object type in place (IDE runtime:
                // target self/other/object, perform_events runs the old
                // object's destroy event and the new object's create event).
                const newName = params.object || '';
                if (!newName) break;
                const objectData = game.gameData.assets.objects[newName];
                if (!objectData) {
                    console.warn(`change_instance: unknown object: ${newName}`);
                    break;
                }
                const performEvents = params.perform_events !== false;
                let targets = [this];
                if (params.target === 'other' && this._collision_other) {
                    targets = [this._collision_other];
                } else if (params.target === 'object' && params.target_object && game.currentRoom) {
                    targets = game.currentRoom.instances.filter(
                        i => i.name === params.target_object && !i.toDestroy);
                }
                for (const inst of targets) {
                    if (performEvents) inst.triggerEvent('destroy');
                    inst.name = newName;
                    inst.objectData = objectData;
                    inst.events = objectData.events || {};
                    inst.solid = objectData.solid || false;
                    inst.visible = objectData.visible !== false;
                    inst.depth = inst.getDepthForObject(newName);
                    const sprName = objectData.sprite;
                    inst.sprite = (sprName && game.sprites[sprName]) || null;
                    inst.spriteInfo = sprName ? game.makeSpriteInfo(sprName) : null;
                    inst.image_index = 0.0;
                    if (performEvents) inst.triggerEvent('create');
                }
                break;
            }

            case 'sleep': {
                // The IDE runtime blocks for the duration (sounds keep
                // playing). A browser can't block, so stepping is suspended
                // while rendering continues — same observable effect.
                const ms = parseInt(params.milliseconds ?? params.ms ?? params.duration ?? 1000) || 0;
                if (ms > 0) game._sleepUntil = Date.now() + Math.min(ms, 10000);
                break;
            }

            case 'execute_code': {
                // Python code, executed via the Pyodide bridge with the IDE
                // runtime's execute_code semantics. In a draw event the
                // Python-side draw queue is returned and merged into this
                // instance's queue (rendered by onDraw).
                const pyCode = params.code || '';
                if (pyCode.trim() && game.python && game.python.ready) {
                    if (this._inDrawEvent) {
                        this._draw_queue.push(...game.python.runDraw(this, pyCode, game));
                    } else {
                        game.python.runCode(this, pyCode, game);
                    }
                } else if (pyCode.trim()) {
                    if (!this._warnedNoPython) {
                        this._warnedNoPython = true;
                        console.warn('execute_code skipped: Python runtime not available');
                    }
                }
                break;
            }

            // ---- Draw actions: queue runtime-schema commands; onDraw
            // renders the queue after the draw event finishes ----

            case 'draw_score':
                this._draw_queue.push({
                    type: 'text',
                    text: `${params.caption !== undefined ? params.caption : 'Score: '}${game.score}`,
                    x: parseNumParam(params.x, this, 0),
                    y: parseNumParam(params.y, this, 0),
                    // runtime: active draw colour, defaulting to white
                    color: this.draw_color || game.draw_color || [255, 255, 255],
                });
                break;

            case 'draw_text':
                this._draw_queue.push({
                    type: 'text',
                    text: String(params.text !== undefined ? params.text : ''),
                    x: parseNumParam(params.x, this, this.x),
                    y: parseNumParam(params.y, this, this.y),
                    // runtime: active draw colour, defaulting to black
                    color: this.draw_color || game.draw_color || [0, 0, 0],
                });
                break;

            case 'draw_lives':
                this._draw_queue.push({
                    type: 'lives',
                    count: Math.max(0, Math.trunc(game.lives)),
                    x: parseNumParam(params.x, this, 0),
                    y: parseNumParam(params.y, this, 0),
                    sprite: params.sprite || '',
                });
                break;

            case 'draw_sprite':
                this._draw_queue.push({
                    type: 'sprite',
                    sprite_name: params.sprite || params.sprite_name || '',
                    x: parseNumParam(params.x, this, this.x),
                    y: parseNumParam(params.y, this, this.y),
                });
                break;

            case 'draw_rectangle':
            case 'draw_ellipse':
                this._draw_queue.push({
                    type: actionType === 'draw_rectangle' ? 'rectangle' : 'ellipse',
                    x1: parseNumParam(params.x1, this, 0),
                    y1: parseNumParam(params.y1, this, 0),
                    x2: parseNumParam(params.x2, this, 100),
                    y2: parseNumParam(params.y2, this, 100),
                    filled: params.filled !== false,
                    color: this.draw_color || game.draw_color || [0, 0, 0],
                });
                break;

            case 'draw_circle':
                this._draw_queue.push({
                    type: 'circle',
                    x: parseNumParam(params.x, this, 0),
                    y: parseNumParam(params.y, this, 0),
                    radius: parseNumParam(params.radius, this, 50),
                    filled: params.filled !== false,
                    color: this.draw_color || game.draw_color || [0, 0, 0],
                });
                break;

            case 'draw_line':
                this._draw_queue.push({
                    type: 'line',
                    x1: parseNumParam(params.x1, this, 0),
                    y1: parseNumParam(params.y1, this, 0),
                    x2: parseNumParam(params.x2, this, 100),
                    y2: parseNumParam(params.y2, this, 100),
                    color: this.draw_color || game.draw_color || [0, 0, 0],
                });
                break;

            case 'draw_arrow': {
                // Pre-compute the tip segments once, mirroring the pygame
                // runtime's execute_draw_arrow_action — the draw-queue
                // renderer just draws three lines, it has no arrow concept.
                const ax1 = parseNumParam(params.x1, this, 0);
                const ay1 = parseNumParam(params.y1, this, 0);
                const ax2 = parseNumParam(params.x2, this, 100);
                const ay2 = parseNumParam(params.y2, this, 100);
                const ats = parseNumParam(params.tip_size, this, 10);
                const aang = Math.atan2(ay2 - ay1, ax2 - ax1);
                this._draw_queue.push({
                    type: 'arrow',
                    x1: ax1, y1: ay1, x2: ax2, y2: ay2,
                    tip1_x: ax2 - ats * Math.cos(aang - Math.PI / 6),
                    tip1_y: ay2 - ats * Math.sin(aang - Math.PI / 6),
                    tip2_x: ax2 - ats * Math.cos(aang + Math.PI / 6),
                    tip2_y: ay2 - ats * Math.sin(aang + Math.PI / 6),
                    color: this.draw_color || game.draw_color || [0, 0, 0],
                });
                break;
            }

            case 'draw_variable': {
                const value = gmExpressionValue(params.variable, this, game);
                this._draw_queue.push({
                    type: 'text',
                    text: String(value !== undefined ? value : ''),
                    x: parseNumParam(params.x, this, 0),
                    y: parseNumParam(params.y, this, 0),
                    color: this.draw_color || game.draw_color || [0, 0, 0],
                });
                break;
            }

            case 'draw_health_bar':
                this._draw_queue.push({
                    type: 'health_bar',
                    x1: parseNumParam(params.x1, this, 0),
                    y1: parseNumParam(params.y1, this, 0),
                    x2: parseNumParam(params.x2, this, 100),
                    y2: parseNumParam(params.y2, this, 20),
                    health: game ? game.health : 100,
                    back_color: params.back_color || '#FF0000',
                    bar_color: params.bar_color || '#00FF00',
                });
                break;

            case 'draw_background':
                // Backgrounds are embedded into the same game.sprites map as
                // sprites by the exporter's encode_sprites — see the
                // matching 'background' case in renderDrawCommands.
                this._draw_queue.push({
                    type: 'background',
                    background_name: params.background || params.background_name || '',
                    x: parseNumParam(params.x, this, 0),
                    y: parseNumParam(params.y, this, 0),
                    tiled: params.tiled === true || params.tiled === 'true',
                });
                break;

            case 'set_draw_color':
                // Stored as-is ('#RRGGBB'); the command renderer accepts hex
                // strings and rgb arrays alike. Mirrors runtime: instance
                // colour + global fallback.
                this.draw_color = params.color || '#000000';
                game.draw_color = this.draw_color;
                break;

            case 'set_draw_font':
                // Stored for parity; the canvas renderer uses one font, the
                // same as the pygame runtime's _draw_text (alignment is
                // stored there too but never applied).
                this.draw_font = params.font || null;
                break;

            // ---- Instance creation / destruction cluster ----

            case 'create_moving_instance': {
                const inst = game.spawnInstance(
                    params.object || '',
                    parseNumParam(params.x, this, 0),
                    parseNumParam(params.y, this, 0));
                if (inst) {
                    inst.direction = parseNumParam(params.direction, this, 0);
                    inst.speed = parseNumParam(params.speed, this, 0);
                }
                break;
            }

            case 'create_random_instance': {
                const choices = [];
                for (let n = 1; n <= 4; n++) {
                    const name = params[`object${n}`];
                    if (name) choices.push(name);
                }
                if (!choices.length) break;
                game.spawnInstance(
                    choices[Math.floor(Math.random() * choices.length)],
                    parseNumParam(params.x, this, 0),
                    parseNumParam(params.y, this, 0));
                break;
            }

            case 'jump_to_random': {
                // Random room position, snapped; a few attempts to avoid
                // landing inside a solid (best effort, like the runtime).
                const snapH = Math.max(1, parseInt(params.snap_h) || 1);
                const snapV = Math.max(1, parseInt(params.snap_v) || 1);
                const room = game.currentRoom;
                if (!room) break;
                const myW = this.spriteInfo ? this.spriteInfo.width : 32;
                const myH = this.spriteInfo ? this.spriteInfo.height : 32;
                for (let attempt = 0; attempt < 20; attempt++) {
                    const rx = Math.floor(Math.random() * Math.max(1, room.width - myW) / snapH) * snapH;
                    const ry = Math.floor(Math.random() * Math.max(1, room.height - myH) / snapV) * snapV;
                    this.x = rx;
                    this.y = ry;
                    const solidHit = room.instances.some(o =>
                        o !== this && !o.toDestroy && o.solid &&
                        rx < o.x + (o.spriteInfo ? o.spriteInfo.width : 32) &&
                        rx + myW > o.x &&
                        ry < o.y + (o.spriteInfo ? o.spriteInfo.height : 32) &&
                        ry + myH > o.y);
                    if (!solidHit) break;
                }
                break;
            }

            case 'destroy_at_position': {
                // Destroy matching instances within `radius` px of (x, y);
                // relative offsets from the caller (IDE runtime semantics).
                const relative = params.relative === true || params.relative === 'true';
                let px = parseNumParam(params.x, this, 0);
                let py = parseNumParam(params.y, this, 0);
                if (relative) { px += this.x; py += this.y; }
                const radius = parseNumParam(params.radius, this, 32);
                const filter = params.object || 'all';
                if (!game.currentRoom) break;
                for (const other of game.currentRoom.instances) {
                    if (other.toDestroy) continue;
                    if (filter === 'solid' && !other.solid) continue;
                    if (filter === 'non-solid' && other.solid) continue;
                    if (filter !== 'all' && filter !== 'any' &&
                        filter !== 'solid' && filter !== 'non-solid' &&
                        other.name !== filter) continue;
                    const dx = other.x - px, dy = other.y - py;
                    const inRange = radius > 0
                        ? (dx * dx + dy * dy) <= radius * radius
                        : (dx === 0 && dy === 0);
                    if (inRange) other.toDestroy = true;
                }
                break;
            }

            case 'set_direction_speed':
                // GM angles: 0=right, 90=up. The direction/speed setters
                // sync hspeed/vspeed with the y-down screen convention.
                this.direction = parseNumParam(params.direction, this, 0);
                this.speed = parseNumParam(params.speed, this, 4);
                break;

            default:
                console.warn(`Unknown action: ${actionType}`);
        }
    }

    checkCollisionAt(x, y, game) {
        // Get my bounding box dimensions and origin
        const myW = this.boxWidth();
        const myH = this.boxHeight();
        const originX = this.spriteInfo ? this.spriteInfo.origin_x : 0;
        const originY = this.spriteInfo ? this.spriteInfo.origin_y : 0;
        // Test rect at position (x, y) accounting for origin
        const testRect = { x: x - originX, y: y - originY, width: myW, height: myH };
        if (!game.currentRoom) return false;

        for (const other of game.currentRoom.instances) {
            if (other === this || !other.solid) continue;
            const otherRect = other.getBoundingBox();
            if (this.rectsCollide(testRect, otherRect)) {
                return true;
            }
        }
        return false;
    }

    getObjectAt(x, y, game) {
        if (!game.currentRoom) return null;

        // Get my bounding box dimensions and origin
        const myW = this.boxWidth();
        const myH = this.boxHeight();
        const originX = this.spriteInfo ? this.spriteInfo.origin_x : 0;
        const originY = this.spriteInfo ? this.spriteInfo.origin_y : 0;
        // Test rect at position (x, y) accounting for origin
        const testRect = { x: x - originX, y: y - originY, width: myW, height: myH };
        const colliding = [];

        for (const other of game.currentRoom.instances) {
            if (other === this) continue;
            const otherRect = other.getBoundingBox();
            if (this.rectsCollide(testRect, otherRect)) {
                colliding.push(other);
            }
        }

        if (colliding.length === 0) return null;

        colliding.sort((a, b) => {
            if (a.solid && !b.solid) return -1;
            if (!a.solid && b.solid) return 1;
            return b.depth - a.depth;
        });

        return colliding[0];
    }

    rectsCollide(r1, r2) {
        return r1.x < r2.x + r2.width && r1.x + r1.width > r2.x &&
               r1.y < r2.y + r2.height && r1.y + r1.height > r2.y;
    }

    // Get bounding box accounting for sprite origin
    // Collision/render size of one FRAME. spriteInfo.width/height are
    // per-frame (Game.makeSpriteInfo); falling back to the raw image is
    // only correct for single-frame sprites, where they coincide.
    boxWidth() {
        if (this.spriteInfo && this.spriteInfo.width) return this.spriteInfo.width;
        return this.sprite ? this.sprite.width : 32;
    }

    boxHeight() {
        if (this.spriteInfo && this.spriteInfo.height) return this.spriteInfo.height;
        return this.sprite ? this.sprite.height : 32;
    }

    getBoundingBox() {
        const originX = this.spriteInfo ? this.spriteInfo.origin_x : 0;
        const originY = this.spriteInfo ? this.spriteInfo.origin_y : 0;
        return {
            x: this.x - originX,
            y: this.y - originY,
            width: this.boxWidth(),
            height: this.boxHeight()
        };
    }

    // Would my bounding box, placed with my ORIGIN at (atX, atY), overlap a
    // matching instance? filter: 'solid' (solids only), 'all'/'any' (any
    // instance), or an object name. Origin- and frame-aware (both boxes via
    // getBoundingBox geometry). excludePartner drops the current collision
    // partner (check_empty semantics — the runtime excludes it); pass false
    // to check every instance (if_collision semantics).
    placeMeetsCollision(atX, atY, filter, game, excludePartner = true) {
        const originX = this.spriteInfo ? this.spriteInfo.origin_x : 0;
        const originY = this.spriteInfo ? this.spriteInfo.origin_y : 0;
        const left = atX - originX, top = atY - originY;
        const w = this.boxWidth(), h = this.boxHeight();
        const exclude = excludePartner ? (this._collision_other || null) : null;
        const insts = game.currentRoom ? game.currentRoom.instances : [];
        for (const inst of insts) {
            if (inst === this || inst === exclude || inst.toDestroy) continue;
            const b = inst.getBoundingBox();
            if (left < b.x + b.width && left + w > b.x &&
                top < b.y + b.height && top + h > b.y) {
                if (filter === 'all' || filter === 'any') return true;
                if (filter === 'solid') { if (inst.solid) return true; }
                else if (inst.name === filter || inst.objectName === filter) return true;
            }
        }
        return false;
    }

    render(ctx) {
        // Don't render if not visible or no sprite assigned
        if (!this.visible) return;
        if (!this.sprite || !this.sprite.complete) return;

        // Get sprite origin (default to 0,0 if not set - top-left)
        const originX = this.spriteInfo ? this.spriteInfo.origin_x : 0;
        const originY = this.spriteInfo ? this.spriteInfo.origin_y : 0;

        // Draw position: x,y is where the origin is, so top-left is (x - originX, y - originY)
        const drawX = Math.floor(this.x - originX);
        const drawY = Math.floor(this.y - originY);

        // Multi-frame strips draw only the current frame (sliced from the
        // horizontal strip by image_index); single frames draw whole.
        const frames = this.spriteInfo ? (this.spriteInfo.frames || 1) : 1;
        const fw = this.boxWidth();
        const fh = this.boxHeight();
        const srcX = frames > 1
            ? ((Math.floor(this.image_index) % frames + frames) % frames) * fw
            : 0;

        if (this.rotation !== 0 || this.scale_x !== 1.0 || this.scale_y !== 1.0) {
            ctx.save();
            // Translate to the origin point (where x,y is)
            ctx.translate(Math.floor(this.x), Math.floor(this.y));

            if (this.rotation !== 0) {
                ctx.rotate((this.rotation * Math.PI) / 180);
            }

            if (this.scale_x !== 1.0 || this.scale_y !== 1.0) {
                ctx.scale(this.scale_x, this.scale_y);
            }

            // Draw with origin offset
            if (frames > 1) {
                ctx.drawImage(this.sprite, srcX, 0, fw, fh, -originX, -originY, fw, fh);
            } else {
                ctx.drawImage(this.sprite, -originX, -originY);
            }
            ctx.restore();
        } else if (frames > 1) {
            ctx.drawImage(this.sprite, srcX, 0, fw, fh, drawX, drawY, fw, fh);
        } else {
            ctx.drawImage(this.sprite, drawX, drawY);
        }
    }

    checkCollisions(game) {
        if (!game.currentRoom || !this.events) return;

        // Use bounding box that accounts for sprite origin
        const myRect = this.getBoundingBox();

        // First pass: Detect all collisions and capture speeds BEFORE any events run
        const collisionsToProcess = [];

        for (const other of game.currentRoom.instances) {
            if (other === this || other.toDestroy) continue;

            const otherRect = other.getBoundingBox();

            if (this.rectsCollide(myRect, otherRect)) {
                const collisionKey = `collision_with_${other.name}`;

                if (this.events[collisionKey]) {
                    // Store collision data with speeds captured NOW
                    collisionsToProcess.push({
                        event: this.events[collisionKey],
                        other: other,
                        // Capture speeds at moment of collision detection
                        selfHspeed: this.hspeed || 0,
                        selfVspeed: this.vspeed || 0,
                        otherHspeed: other.hspeed || 0,
                        otherVspeed: other.vspeed || 0
                    });
                }
            }
        }

        // Second pass: Process all collision events with stored speeds
        for (const collision of collisionsToProcess) {
            const actions = collision.event.actions || [];
            this._collision_other = collision.other;
            // Store collision speeds so they can be accessed via other.hspeed etc.
            this._collision_speeds = {
                selfHspeed: collision.selfHspeed,
                selfVspeed: collision.selfVspeed,
                otherHspeed: collision.otherHspeed,
                otherVspeed: collision.otherVspeed
            };
            this.executeActions(actions, game);
            this._collision_speeds = null;
        }
    }
}

// Class field syntax is avoided for broad browser compatibility.
GameObject._nextInstanceId = 0;

class GameRoom {
    constructor(data) {
        this.name = data.name;
        this.width = data.width || 1024;
        this.height = data.height || 768;
        this.bgColor = data.background_color || '#87CEEB';
        this.bgImage = data.background_image || '';
        this.tileHorizontal = data.tile_horizontal || false;
        this.tileVertical = data.tile_vertical || false;
        this.instances = [];
        this.backgroundSprite = null;

        // GameMaker-style 8-view camera system (mirrors the desktop runtime's
        // GameRoom in game_runner.py). When enabled, the room can be larger
        // than the window and the renderer scrolls/clips per view.
        this.viewsEnabled = data.views_enabled || data.enable_views || false;
        this.currentViewIndex = -1;  // active view during render, else -1
        this.views = [];
        const viewsRaw = (data.views && !Array.isArray(data.views)) ? data.views : {};
        for (let i = 0; i < 8; i++) {
            const v = viewsRaw['view_' + i] || {};
            this.views.push({
                visible: v.visible !== undefined ? v.visible : (i === 0),
                view_x: v.view_x || 0, view_y: v.view_y || 0,
                view_w: v.view_w || this.width, view_h: v.view_h || this.height,
                port_x: v.port_x || 0, port_y: v.port_y || 0,
                port_w: v.port_w || this.width, port_h: v.port_h || this.height,
                follow: v.follow || null,
                hborder: v.hborder !== undefined ? v.hborder : 32,
                vborder: v.vborder !== undefined ? v.vborder : 32,
                hspeed: v.hspeed !== undefined ? v.hspeed : -1,
                vspeed: v.vspeed !== undefined ? v.vspeed : -1,
            });
        }
    }

    findFirstInstance(objectName) {
        for (const inst of this.instances) {
            if (!inst.toDestroy && inst.name === objectName) return inst;
        }
        return null;
    }

    // Per-frame camera follow + clamp, mirroring game_runner.update_views().
    updateViews() {
        if (!this.viewsEnabled) return;
        for (const view of this.views) {
            if (!view.visible || !view.follow) continue;
            const target = this.findFirstInstance(view.follow);
            if (!target) continue;
            const vw = Math.trunc(view.view_w), vh = Math.trunc(view.view_h);
            const hb = Math.trunc(view.hborder), vb = Math.trunc(view.vborder);
            const oldVx = Math.trunc(view.view_x), oldVy = Math.trunc(view.view_y);
            let newVx = oldVx, newVy = oldVy;
            if (target.x < oldVx + hb) newVx = Math.trunc(target.x - hb);
            else if (target.x > oldVx + vw - hb) newVx = Math.trunc(target.x - vw + hb);
            if (target.y < oldVy + vb) newVy = Math.trunc(target.y - vb);
            else if (target.y > oldVy + vh - vb) newVy = Math.trunc(target.y - vh + vb);
            // Per-axis speed limit (-1 = no limit)
            const hsl = Math.trunc(view.hspeed), vsl = Math.trunc(view.vspeed);
            if (hsl >= 0) {
                const dx = newVx - oldVx;
                if (dx > hsl) newVx = oldVx + hsl; else if (dx < -hsl) newVx = oldVx - hsl;
            }
            if (vsl >= 0) {
                const dy = newVy - oldVy;
                if (dy > vsl) newVy = oldVy + vsl; else if (dy < -vsl) newVy = oldVy - vsl;
            }
            // Clamp to room bounds
            newVx = vw < this.width ? Math.max(0, Math.min(newVx, this.width - vw)) : 0;
            newVy = vh < this.height ? Math.max(0, Math.min(newVy, this.height - vh)) : 0;
            view.view_x = newVx;
            view.view_y = newVy;
        }
    }

    _activeViews() {
        const out = [];
        this.views.forEach((v, i) => { if (v.visible) out.push([i, v]); });
        return out;
    }

    step(game) {
        // 0. Pending create events fire BEFORE any step event touches the
        // instance (IDE-runtime order: create runs at room load). Firing
        // them at the END of the first frame let step events run against
        // un-initialized instances (an AttributeError for execute_code
        // games whose state is built in create).
        this.instances.forEach(inst => {
            if (inst._pendingCreateEvent) {
                inst.triggerCreateEvent(game);
            }
        });

        // 0b. game_start fires once per game, after the first room's create
        // events (IDE-runtime order) — authored startup setup like lives /
        // caption lives here (runtime fix 5f09b1d).
        if (game && !game._gameStartFired) {
            game._gameStartFired = true;
            [...this.instances].forEach(inst => {
                if (!inst.toDestroy && inst.events && inst.events.game_start) {
                    inst.executeActions(inst.events.game_start.actions || [], game);
                }
            });
        }

        // GAMEMAKER 7.0 EVENT ORDER:
        // 1. Begin Step events
        this.instances.forEach(inst => {
            if (!inst.toDestroy) inst.onBeginStep(game);
        });

        // 2. Alarm events
        this.instances.forEach(inst => {
            if (!inst.toDestroy) inst.processAlarms();
        });

        // 3. Keyboard events (handled separately in game.processKeyboard)
        // 3b. NoKey events - only fire when no arrow keys pressed AND object is moving
        // This prevents constant stop_movement calls when already stationary
        const arrowKeysForNoKey = ['ArrowLeft', 'ArrowRight', 'ArrowUp', 'ArrowDown'];
        const anyArrowKeyHeld = arrowKeysForNoKey.some(key => game.keys[key]);
        if (!anyArrowKeyHeld) {
            this.instances.forEach(inst => {
                // Only trigger nokey if the instance is actually moving
                if (!inst.toDestroy && (inst._hspeed !== 0 || inst._vspeed !== 0)) {
                    inst.onNoKey(game);
                }
            });
        }

        // 3c. Sprite animation: image_index advances by image_speed per
        // game step (GM semantics, mirroring GameInstance.step in
        // runtime/game_runner.py); wrapping fires animation_end.
        this.instances.forEach(inst => {
            if (inst.toDestroy || !inst.spriteInfo) return;
            const frames = inst.spriteInfo.frames || 1;
            if (frames <= 1 || inst.image_speed === 0) return;
            inst.image_index += inst.image_speed;
            let wrapped = false;
            if (inst.image_index >= frames) {
                inst.image_index = inst.image_index % frames;
                wrapped = true;
            } else if (inst.image_index < 0) {
                inst.image_index = frames + (inst.image_index % frames);
                wrapped = true;
            }
            if (wrapped && inst.events && inst.events.animation_end) {
                inst.executeActions(inst.events.animation_end.actions || [], game);
            }
        });

        // 4. Step events
        this.instances.forEach(inst => {
            if (!inst.toDestroy) inst.onStep(game);
        });

        // 5. Movement
        this.instances.forEach(inst => {
            if (!inst.toDestroy) inst.processMovement(game);
        });

        // 5b. outside_room events — fires while the instance's box is
        // entirely outside the room (GM behaviour; e.g. plateforme_5
        // despawns off-screen projectiles with it)
        this.instances.forEach(inst => {
            if (inst.toDestroy || !inst.events || !inst.events.outside_room) return;
            const w = inst.spriteInfo ? inst.spriteInfo.width : 32;
            const h = inst.spriteInfo ? inst.spriteInfo.height : 32;
            if (inst.x + w < 0 || inst.x > this.width ||
                inst.y + h < 0 || inst.y > this.height) {
                inst.executeActions(inst.events.outside_room.actions || [], game);
            }
        });

        // 6. Collision events
        this.instances.forEach(inst => {
            if (!inst.toDestroy) inst.checkCollisions(game);
        });

        // 7. End Step events
        this.instances.forEach(inst => {
            if (!inst.toDestroy) inst.onEndStep(game);
        });

        // 8. Cleanup destroyed instances — firing their destroy event first
        // (IDE-runtime order; maze_2's diamonds award score on destroy).
        this.instances.forEach(inst => {
            if (inst.toDestroy && !inst._destroyEventFired) {
                inst._destroyEventFired = true;
                inst.triggerEvent('destroy');
            }
        });
        this.instances = this.instances.filter(inst => !inst.toDestroy);

        // Create events for instances spawned DURING this frame fire here
        // (next frame's step-0 pass would also catch them; this keeps the
        // old same-frame timing for dynamically created instances).
        this.instances.forEach(inst => {
            if (inst._pendingCreateEvent) {
                inst.triggerCreateEvent(game);
            }
        });
    }

    render(ctx) {
        // Fill the whole canvas with the bg color once; areas outside any
        // view port then show the bg color rather than stale pixels.
        ctx.fillStyle = this.bgColor;
        const cw = ctx.canvas ? ctx.canvas.width : this.width;
        const ch = ctx.canvas ? ctx.canvas.height : this.height;
        ctx.fillRect(0, 0, cw, ch);

        const active = this.viewsEnabled ? this._activeViews() : [];
        if (active.length === 0) {
            // Legacy no-view path: draw at room origin.
            this.currentViewIndex = -1;
            this._renderContents(ctx);
            return;
        }
        // For each visible view: clip to its port and translate so the
        // view's top-left maps to the port's top-left (mirrors the desktop
        // runtime's per-view render loop; offset = port - view).
        for (const [i, view] of active) {
            ctx.save();
            ctx.beginPath();
            ctx.rect(view.port_x, view.port_y, view.port_w, view.port_h);
            ctx.clip();
            ctx.translate(view.port_x - view.view_x, view.port_y - view.view_y);
            this.currentViewIndex = i;
            this._renderContents(ctx);
            ctx.restore();
        }
        this.currentViewIndex = -1;
    }

    // Room contents in ROOM coordinates (the caller applies any camera
    // translate/clip). Background image + depth-sorted instance draws.
    _renderContents(ctx) {
        if (this.backgroundSprite && this.backgroundSprite.complete) {
            if (this.tileHorizontal || this.tileVertical) {
                const imgWidth = this.backgroundSprite.width;
                const imgHeight = this.backgroundSprite.height;
                const xCount = this.tileHorizontal ? Math.ceil(this.width / imgWidth) + 1 : 1;
                const yCount = this.tileVertical ? Math.ceil(this.height / imgHeight) + 1 : 1;

                for (let x = 0; x < xCount; x++) {
                    for (let y = 0; y < yCount; y++) {
                        const xPos = this.tileHorizontal ? x * imgWidth : 0;
                        const yPos = this.tileVertical ? y * imgHeight : 0;
                        if (xPos < this.width && yPos < this.height) {
                            ctx.drawImage(this.backgroundSprite, xPos, yPos);
                        }
                    }
                }
            } else {
                ctx.drawImage(this.backgroundSprite, 0, 0, this.width, this.height);
            }
        }

        // GAMEMAKER 7.0: Draw events (sort by depth first)
        const sortedInstances = [...this.instances].sort((a, b) => a.depth - b.depth);
        sortedInstances.forEach(inst => inst.onDraw(ctx));
    }
}

class Game {
    constructor() {
        console.log('🎮 Initializing game...');
        this.canvas = document.getElementById('gameCanvas');
        this.ctx = this.canvas.getContext('2d');
        this.rooms = {};
        this.currentRoom = null;
        this.running = false;
        this.paused = false;
        this.keys = {};
        this.keysPressed = {};
        this.keysReleased = {};
        this.fps = 0;
        this.frameCount = 0;
        this.lastFpsUpdate = Date.now();

        // GAMEMAKER 7.0: Game state variables
        this.score = 0;
        this.lives = 3;
        this.health = 100;
        this.globalVariables = {};  // set_variable/test_variable global scope
        this.sounds = {};           // sound name -> data URL (loadGame)
        this._audioPool = {};       // sound name -> [Audio] (play_sound)
        this._sleepUntil = 0;       // sleep action deadline
        this._gameStartFired = false;

        // Language for translations (default English, can be set from gameData)
        this.language = 'en';

        // Python bridge for execute_code actions (set up in initPython)
        this.python = null;
        this.pythonError = null;

        this.setupKeyboard();
        this.setupMouse();
        this.loadGame();
    }

    // Build the per-frame sprite metadata block every instance carries.
    // width/height are FRAME dimensions: the project's sprite 'width' is
    // the full strip width for multi-frame art (importer convention), so
    // frame_width (or strip/frames) is what collision and rendering use.
    makeSpriteInfo(spriteName) {
        const img = this.sprites ? this.sprites[spriteName] : null;
        if (!img) return null;
        const meta = (this.gameData.assets.sprites || {})[spriteName] || {};
        const frames = Math.max(1, parseInt(meta.frames) || 1);
        const stripW = meta.width || img.width || 32;
        const fw = parseInt(meta.frame_width) ||
                   (frames > 1 ? Math.floor(stripW / frames) : stripW);
        const fh = parseInt(meta.frame_height) || meta.height || img.height || 32;
        return {
            origin_x: meta.origin_x || 0,
            origin_y: meta.origin_y || 0,
            width: fw,
            height: fh,
            frames: frames,
        };
    }

    // Create an instance of an object type at (x, y) in the current room.
    // The create event fires via the pending-create pass in GameRoom.step.
    spawnInstance(objName, x, y) {
        if (!objName || !this.currentRoom) return null;
        const objectData = this.gameData.assets.objects[objName];
        if (!objectData) {
            console.warn(`spawnInstance: unknown object: ${objName}`);
            return null;
        }
        const inst = new GameObject(objName, x, y, {}, objectData);
        inst._gameRef = this;
        inst._startX = x;
        inst._startY = y;
        if (objectData.sprite && this.sprites[objectData.sprite]) {
            inst.sprite = this.sprites[objectData.sprite];
            inst.spriteInfo = this.makeSpriteInfo(objectData.sprite);
        }
        this.currentRoom.instances.push(inst);
        return inst;
    }

    // Load the Python runtime if (and only if) the project uses execute_code.
    async initPython() {
        if (!PythonBridge.projectNeedsPython(this.gameData)) return;
        this.python = new PythonBridge();
        const statusEl = document.getElementById('fps');
        try {
            await this.python.init(msg => {
                if (statusEl && msg) statusEl.textContent = msg;
            });
        } catch (err) {
            console.error('❌ Python runtime failed to load:', err);
            this.pythonError = String(err && err.message ? err.message : err);
        }
    }

    setupMouse() {
        // Dispatch clicks/taps as GameMaker mouse events, matching the IDE
        // runtime (game_runner.handle_mouse_press): the event fires on EVERY
        // instance that defines it (no hit-test), with mouse_x/mouse_y set
        // in room coordinates. Canvas CSS scaling is inverted.
        const PRESS_KEYS = ['mouse_left_press', 'mouse_left_button', 'mouse_left_down'];
        const RELEASE_KEYS = ['mouse_left_release'];

        const dispatch = (clientX, clientY, eventKeys) => {
            if (!this.currentRoom || this.paused) return;
            const rect = this.canvas.getBoundingClientRect();
            // clientWidth/clientLeft exclude the canvas border, which
            // getBoundingClientRect includes.
            const cw = this.canvas.clientWidth, ch = this.canvas.clientHeight;
            if (!cw || !ch) return;
            const mx = (clientX - rect.left - this.canvas.clientLeft) * this.canvas.width / cw;
            const my = (clientY - rect.top - this.canvas.clientTop) * this.canvas.height / ch;
            [...this.currentRoom.instances].forEach(inst => {
                if (inst.toDestroy || !inst.events) return;
                for (const key of eventKeys) {
                    const ev = inst.events[key];
                    if (ev && ev.actions) {
                        inst.mouse_x = mx;
                        inst.mouse_y = my;
                        inst.executeActions(ev.actions, this);
                        break;  // aliases map to the same runtime event
                    }
                }
            });
        };

        this.canvas.addEventListener('mousedown', (e) => {
            if (e.button === 0) dispatch(e.clientX, e.clientY, PRESS_KEYS);
        });
        this.canvas.addEventListener('mouseup', (e) => {
            if (e.button === 0) dispatch(e.clientX, e.clientY, RELEASE_KEYS);
        });
        this.canvas.addEventListener('touchstart', (e) => {
            e.preventDefault();
            const t = e.changedTouches[0];
            if (t) dispatch(t.clientX, t.clientY, PRESS_KEYS);
        }, { passive: false });
        this.canvas.addEventListener('touchend', (e) => {
            e.preventDefault();
            const t = e.changedTouches[0];
            if (t) dispatch(t.clientX, t.clientY, RELEASE_KEYS);
        }, { passive: false });
    }

    // Get translated text for the current language
    translate(key) {
        return getTranslation(key, this.language);
    }

    setupKeyboard() {
        console.log('⌨️ Setting up keyboard...');

        window.addEventListener('keydown', (e) => {
            if (['ArrowLeft', 'ArrowRight', 'ArrowUp', 'ArrowDown'].includes(e.key)) {
                e.preventDefault();
            }

            if (!this.keys[e.key]) {
                this.keysPressed[e.key] = true;
            }
            this.keys[e.key] = true;
        });

        window.addEventListener('keyup', (e) => {
            this.keys[e.key] = false;
            this.keysReleased[e.key] = true;
        });
    }

    loadGame() {
        console.log('📦 Loading game data...');

        if (typeof gameData === 'undefined') {
            console.error('❌ gameData is undefined!');
            return;
        }

        this.sprites = {};
        this.gameData = gameData;

        // Load game settings
        const settings = gameData.settings || {};
        this.score = settings.starting_score || 0;
        this.lives = settings.starting_lives || 3;
        this.health = settings.starting_health || 100;
        this.showScoreInCaption = settings.show_score_in_caption !== false;
        this.showLivesInCaption = settings.show_lives_in_caption !== false;
        this.showHealthInCaption = settings.show_health_in_caption || false;
        console.log(`⚙️ Settings: score=${this.score}, lives=${this.lives}, health=${this.health}`);

        const sprites = this.sprites;
        const spriteNames = Object.keys(spritesData);
        console.log(`Loading ${spriteNames.length} sprites...`);

        spriteNames.forEach(name => {
            const img = new Image();
            img.onload = () => console.log(`✓ Loaded sprite: ${name}`);
            img.onerror = () => console.error(`❌ Failed sprite: ${name}`);
            img.src = spritesData[name];
            sprites[name] = img;
        });

        // Embedded sounds (data URLs). Guarded so pages exported before the
        // sound blob existed keep working.
        this.sounds = (typeof soundsData !== 'undefined' && soundsData) ? soundsData : {};
        if (Object.keys(this.sounds).length) {
            console.log(`Loaded ${Object.keys(this.sounds).length} sounds`);
        }

        const roomsData = gameData.assets.rooms;
        console.log(`Loading ${Object.keys(roomsData).length} rooms...`);

        for (const [roomName, roomData] of Object.entries(roomsData)) {
            const room = new GameRoom(roomData);

            if (room.bgImage && sprites[room.bgImage]) {
                room.backgroundSprite = sprites[room.bgImage];
            }

            const instancesData = roomData.instances || [];
            instancesData.forEach(instData => {
                // Rooms written at different times use different keys for
                // the object reference (same tolerance as the Android
                // exporter): plateforme_* uses 'object', newer rooms use
                // 'object_name'.
                const objName = instData.object_name || instData.object ||
                                instData.object_type || instData.type || '';
                if (!objName) {
                    console.warn('Skipping instance with no object reference:', instData);
                    return;
                }
                const objectData = gameData.assets.objects[objName];
                const inst = new GameObject(
                    objName,
                    instData.x,
                    instData.y,
                    instData,
                    objectData
                );

                inst._gameRef = this;
                // Store starting position for jump_to_start
                inst._startX = instData.x;
                inst._startY = instData.y;

                if (objectData && objectData.sprite && sprites[objectData.sprite]) {
                    inst.sprite = sprites[objectData.sprite];
                    inst.spriteInfo = this.makeSpriteInfo(objectData.sprite);
                }

                room.instances.push(inst);
            });

            this.rooms[roomName] = room;
            console.log(`✓ Loaded room: ${roomName} (${room.instances.length} instances)`);
        }

        const firstRoom = Object.keys(this.rooms)[0];
        if (firstRoom) {
            this.currentRoom = this.rooms[firstRoom];
            console.log(`🚀 Starting with room: ${firstRoom}`);
        }
    }

    start() {
        console.log('▶️ Starting game loop...');
        this.running = true;

        if (this.currentRoom) {
            this.canvas.width = this.currentRoom.width;
            this.canvas.height = this.currentRoom.height;
            console.log(`📐 Canvas initialized to: ${this.currentRoom.width}x${this.currentRoom.height}`);
        }

        this.gameLoop();
    }

    gameLoop() {
        if (!this.running) return;

        this.frameCount++;
        const now = Date.now();
        if (now - this.lastFpsUpdate >= 1000) {
            this.fps = this.frameCount;
            this.frameCount = 0;
            this.lastFpsUpdate = now;
            document.getElementById('fps').textContent = `FPS: ${this.fps}`;
        }

        if (!this.paused && Date.now() >= this._sleepUntil) {
            this.processKeyboard();
            this.processKeyboardRelease();
            if (this.currentRoom) {
                this.currentRoom.step(this);
            }
        }

        if (this.currentRoom) {
            // Camera follow/clamp before drawing (desktop order: update_views
            // runs in render() before the room is drawn).
            this.currentRoom.updateViews();
            this.currentRoom.render(this.ctx);
        }

        // Draw score, lives, health HUD
        this.drawHUD();

        if (this.paused) {
            this.ctx.fillStyle = 'rgba(0, 0, 0, 0.5)';
            this.ctx.fillRect(0, 0, this.canvas.width, this.canvas.height);
            this.ctx.fillStyle = 'white';
            this.ctx.font = 'bold 48px Arial';
            this.ctx.textAlign = 'center';
            this.ctx.fillText('PAUSED', this.canvas.width / 2, this.canvas.height / 2);
        }

        if (this.pythonError) {
            // The game needs Python but the runtime could not load — say so
            // instead of showing a silently dead game.
            this.ctx.fillStyle = 'rgba(0, 0, 0, 0.75)';
            this.ctx.fillRect(0, 0, this.canvas.width, this.canvas.height);
            this.ctx.fillStyle = 'white';
            this.ctx.font = '16px Arial';
            this.ctx.textAlign = 'center';
            const lines = this.pythonError.split('\n');
            lines.forEach((line, i) => {
                this.ctx.fillText(line, this.canvas.width / 2,
                                  this.canvas.height / 2 - lines.length * 10 + i * 20);
            });
        }

        requestAnimationFrame(() => this.gameLoop());
    }

    drawHUD() {
        // Update HTML HUD elements instead of drawing on canvas
        const scoreEl = document.getElementById('scoreValue');
        const livesEl = document.getElementById('livesValue');
        const healthEl = document.getElementById('healthValue');
        const healthDisplay = document.getElementById('healthDisplay');

        if (scoreEl) scoreEl.textContent = this.score;
        if (livesEl) livesEl.textContent = this.lives;
        if (healthEl) healthEl.textContent = this.health;

        // Show/hide health based on settings
        if (healthDisplay) {
            healthDisplay.style.display = this.showHealthInCaption ? 'flex' : 'none';
        }
    }

    processKeyboard() {
        if (!this.currentRoom) return;

        // Process keyboard press events (fires once when key first pressed)
        for (const key in this.keysPressed) {
            if (this.keysPressed[key]) {
                this.currentRoom.instances.forEach(inst => {
                    if (!inst.toDestroy && inst.events) {
                        inst.onKeyboardPress(key, this);
                    }
                });
            }
        }

        // Clear pressed keys for next frame
        this.keysPressed = {};

        // Process keyboard held events (fires continuously while key is held)
        for (const key in this.keys) {
            if (this.keys[key]) {
                this.currentRoom.instances.forEach(inst => {
                    if (!inst.toDestroy && inst.events) {
                        inst.onKeyboardHeld(key, this);
                    }
                });
            }
        }
    }

    processKeyboardRelease() {
        if (!this.currentRoom) return;

        // Process keyboard release events
        for (const key in this.keysReleased) {
            if (this.keysReleased[key]) {
                this.currentRoom.instances.forEach(inst => {
                    if (!inst.toDestroy && inst.events) {
                        inst.onKeyboardRelease(key, this);
                    }
                });
            }
        }

        // Clear released keys for next frame
        this.keysReleased = {};
    }

    togglePause() {
        this.paused = !this.paused;
        document.getElementById('pauseBtn').textContent = this.paused ? '▶️ Resume' : '⏸️ Pause';
        console.log(this.paused ? '⏸️ Paused' : '▶️ Resumed');
    }

    restart() {
        window.location.reload();
    }

    changeRoom(roomName) {
        if (this.rooms[roomName]) {
            // Clear keyboard state
            for (const key in this.keys) {
                this.keys[key] = false;
            }
            this.keysPressed = {};
            this.keysReleased = {};

            this.currentRoom = this.rooms[roomName];

            // Resize canvas
            this.canvas.width = this.currentRoom.width;
            this.canvas.height = this.currentRoom.height;

            console.log(`📍 Changed to room: ${roomName}`);
        } else {
            console.warn(`⚠️ Room not found: ${roomName}`);
        }
    }
}

window.addEventListener('load', async () => {
    try {
        window.game = new Game();
        // Loads Pyodide only for projects that contain execute_code actions,
        // so create events written in Python run on the very first frame.
        await window.game.initPython();
        window.game.start();
        console.log('✅ Game started!');
    } catch (error) {
        console.error('❌ Failed to start:', error);
    }
});
