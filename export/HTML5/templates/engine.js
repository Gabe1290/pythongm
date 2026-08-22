
// ============================================================================
// PyGameMaker HTML5 Engine - GAMEMAKER 7.0 COMPATIBLE
// ============================================================================

// ---------------------------------------------------------------------------
// Extension mechanism (docs/RAYCAST_EXTENSION_PLAN.md Stage C). Mirrors the
// desktop runtime/extension_hooks + plugin action registry: an extension ships
// an export_html5.js that the exporter concatenates at the __PYGM_EXTENSION_JS__
// marker near the end of this file, and that code registers room renderers
// and/or action handlers here. engine.js itself names no specific extension.
// ---------------------------------------------------------------------------

// Room renderers: (room, ctx) -> true if the extension drew the room. The
// engine then skips its top-down pass but still composites the HUD/draw events.
const _extRoomRenderers = [];
function registerRoomRenderer(fn) {
    if (typeof fn === 'function' && !_extRoomRenderers.includes(fn)) {
        _extRoomRenderers.push(fn);
    }
}
function renderExtensionRoom(room, ctx) {
    for (const fn of _extRoomRenderers) {
        try {
            if (fn(room, ctx)) return true;   // first claimer wins
        } catch (e) {
            console.error('Extension room renderer failed:', e);
        }
    }
    return false;
}

// Action handlers: name -> (obj, params, game). Consulted by
// GameObject.executeAction's default case, so an extension adds actions without
// engine.js enumerating them.
const _extActions = {};
function registerExtensionAction(name, fn) {
    if (typeof fn === 'function') _extActions[name] = fn;
}

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

// Replaced per-export by HTML5Exporter (TODO.md: "Pyodide loads from the
// jsDelivr CDN") when the offline-bundle option is chosen AND the project
// actually uses execute_code: an object of
// {"pyodide.js": b64, "pyodide.asm.js": b64 (both gzip-then-base64),
//  "pyodide.asm.wasm": b64, "pyodide-lock.json": b64, "python_stdlib.zip": b64
//  (these three plain base64, already-compressed formats)}.
// null (default) keeps the CDN path below, unchanged.
const EMBEDDED_PYODIDE = null; // __PYGM_EMBEDDED_PYODIDE_MARKER__

// Python-side runtime: mirrors the IDE's execute_code environment
// (runtime/action_executor.py execute_execute_code_action): `self` with
// persistent attributes, `math`/`random` modules, a `keyboard.check()`
// shim, a `game` object (score/lives/health — see _Game below), and
// exec-locals copied back onto the instance afterwards.
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
        # JS Audio object exists in this exec scope, so execute_code can't
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

class _Game:
    """'game' object exposed inside execute_code bodies. score/lives/
    health are plain read/write values — matching the desktop runtime's
    actual execute_code semantics exactly: a raw game.lives = X
    assignment there does NOT trigger a caption update or a
    no_more_lives/no_more_health crossing check either; those only fire
    from the set_lives/set_health ACTIONS specifically (see
    executeAction's 'set_lives'/'set_health' cases), never from a bare
    attribute write. There's no live reference back to the JS Game
    object across a Pyodide call, so this is a fresh snapshot built from
    the synced-in values each call; any change is diffed back out in
    run_code's patch, the same way self.x/self.y already work.
    """
    def __init__(self, score, lives, health):
        self.score = score
        self.lives = lives
        self.health = health

def run_code(inst_id, code, sync_json):
    self = _get_inst(inst_id)
    sync = json.loads(sync_json)
    for key in ('x', 'y', 'mouse_x', 'mouse_y'):
        if key in sync:
            setattr(self, key, sync[key])
    game = _Game(sync.get('score', 0), sync.get('lives', 0), sync.get('health', 100))
    exec_globals = {
        '__builtins__': __builtins__,
        'self': self,
        'sel': self,
        'instance': self,
        'other': None,
        'game': game,
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
    for key in ('score', 'lives', 'health'):
        if getattr(game, key) != sync.get(key):
            patch[key] = getattr(game, key)
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

    _b64ToBytes(b64) {
        const bin = atob(b64);
        const bytes = new Uint8Array(bin.length);
        for (let i = 0; i < bin.length; i++) bytes[i] = bin.charCodeAt(i);
        return bytes;
    }

    // pyodide.js/pyodide.asm.js are gzip-then-base64'd by the exporter
    // (plain JS text, compresses well); inflate then UTF-8-decode -- NOT
    // a naive atob()-as-string, which mangles any non-ASCII byte.
    _b64GzipToText(b64) {
        const inflated = pako.inflate(this._b64ToBytes(b64));
        return new TextDecoder('utf-8').decode(inflated);
    }

    async init(statusCallback) {
        statusCallback('Loading Python runtime…');
        if (EMBEDDED_PYODIDE) {
            await this._initEmbedded();
        } else {
            await this._initFromCDN();
        }
        this.pyodide.runPython(PY_BOOTSTRAP);
        this._runCode = this.pyodide.globals.get('run_code');
        this._runDraw = this.pyodide.globals.get('run_draw');
        this.ready = true;
        statusCallback('');
        console.log('✅ Python runtime ready');
    }

    async _initFromCDN() {
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
    }

    // Offline path: every file needed to boot Pyodide is embedded in this
    // very .html, so no network request happens at all. pyodide.js/
    // pyodide.asm.js run as inline <script> text instead of being
    // fetched -- loadPyodide() already skips its own dynamic
    // pyodide.asm.js fetch once `_createPyodideModule` exists globally
    // (its own source comment: "If the pyodide.asm.js script has been
    // imported, we can skip the dynamic import"). pyodide.asm.wasm has
    // no direct loadPyodide() option, so it's the one file window.fetch
    // is temporarily intercepted for (matched by filename, not the exact
    // indexURL, since indexURL is just a placeholder here);
    // pyodide-lock.json/python_stdlib.zip go through loadPyodide()'s own
    // documented lockFileURL/stdLibURL options as data: URIs -- fetch()
    // supports data: natively, no interception needed for those two.
    async _initEmbedded() {
        const files = EMBEDDED_PYODIDE;

        const loaderScript = document.createElement('script');
        loaderScript.textContent = this._b64GzipToText(files['pyodide.js']);
        document.head.appendChild(loaderScript);

        const asmScript = document.createElement('script');
        asmScript.textContent = this._b64GzipToText(files['pyodide.asm.js']);
        document.head.appendChild(asmScript);

        const wasmBytes = this._b64ToBytes(files['pyodide.asm.wasm']);
        // Not .bind(window) -- fetch doesn't need a `this`, and binding
        // would produce a wrapper !== the original reference, so
        // restoring below couldn't put window.fetch literally back the
        // way it was found.
        const originalFetch = window.fetch;
        window.fetch = (input, init) => {
            const url = typeof input === 'string' ? input : (input && input.url) || '';
            if (url.endsWith('pyodide.asm.wasm')) {
                return Promise.resolve(new Response(wasmBytes, {
                    status: 200, headers: { 'Content-Type': 'application/wasm' }
                }));
            }
            return originalFetch(input, init);
        };
        try {
            this.pyodide = await loadPyodide({
                indexURL: 'pygm-embedded-pyodide/',
                lockFileURL: 'data:application/json;base64,' + files['pyodide-lock.json'],
                stdLibURL: 'data:application/zip;base64,' + files['python_stdlib.zip'],
            });
        } finally {
            window.fetch = originalFetch;
        }
    }

    _syncJson(inst, game) {
        const held = Object.keys(game.keys || {})
            .filter(k => game.keys[k])
            .map(k => k.toLowerCase());
        return JSON.stringify({
            x: inst.x, y: inst.y, visible: inst.visible,
            mouse_x: inst.mouse_x || 0, mouse_y: inst.mouse_y || 0,
            keys: held,
            score: game.score, lives: game.lives, health: game.health,
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
            // Plain writes, matching the desktop runtime's actual
            // execute_code semantics (see PY_BOOTSTRAP's _Game docstring)
            // — no caption update, no no_more_lives/no_more_health
            // crossing check here; those only fire from the set_lives/
            // set_health ACTIONS (executeAction's switch cases below).
            if ('score' in patch) game.score = patch.score;
            if ('lives' in patch) game.lives = patch.lives;
            if ('health' in patch) game.health = patch.health;
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
    // A bare instance attribute name (e.g. "direction", "speed",
    // "image_index"), matching desktop's _parse_value
    // (hasattr(instance, value_str) -> getattr(...)), checked before the
    // expression path below — move_to_contact's own `direction: "direction"`
    // parameter (GameMaker's "current direction of travel" keyword) needs
    // this to resolve to the instance's live direction getter, not fall
    // through to parseFloat("direction") === NaN -> the caller's fallback
    // (0 here always meant "move right", regardless of which way the
    // instance actually approached the obstacle it collided with).
    if (/^[a-zA-Z_]\w*$/.test(s) && typeof inst[s] === 'number' && isFinite(inst[s])) {
        return inst[s];
    }
    try {
        const other = inst._collision_other;
        const expr = s
            .replace(/self\.x/g, `(${inst.x})`)
            .replace(/self\.y/g, `(${inst.y})`)
            .replace(/other\.x/g, `(${other ? other.x : 0})`)
            .replace(/other\.y/g, `(${other ? other.y : 0})`)
            // facing_angle (raycast camera look direction) as a bare variable,
            // so set_direction_speed(direction="facing_angle"[+180]) — the
            // raycast_1 FPS controls — resolves, matching the desktop runtime.
            .replace(/facing_angle/g, `(${inst.facing_angle || 0})`)
            .replace(/view_[a-z]+/g, '0')
            // GameMaker-style random calls (irandom/random/choose), matching
            // runtime/action_executor.py's _evaluate_expression — e.g. a
            // spawn action's `x: "irandom(444) + 4"`. Only the bare token is
            // substituted; the call's own opening paren is left as literal
            // text right after it, so the real gmIrandom/gmRandom/gmChoose
            // function names reach the whitelist check below unambiguously —
            // it strips exactly those three names, not arbitrary
            // identifiers, so this can't become a general eval().
            .replace(/\birandom\b/g, 'gmIrandom')
            .replace(/\brandom\b/g, 'gmRandom')
            .replace(/\bchoose\b/g, 'gmChoose');
        const stripped = expr.replace(/\bgmIrandom\b|\bgmRandom\b|\bgmChoose\b/g, '');
        if (/^[-+*/(). ,0-9]+$/.test(stripped)) {
            const result = Function(
                'gmIrandom', 'gmRandom', 'gmChoose',
                `"use strict"; return (${expr});`
            )(gmIrandom, gmRandom, gmChoose);
            if (typeof result === 'number' && isFinite(result)) return result;
        }
    } catch (e) { /* fall through */ }
    return fallback;
}

// Particle system (Tier 5.1/5.3, docs/DEFERRED_GAPS_2026_PLAN.md). Spawns
// `number` particles from `emitter` using `ptype`'s random ranges --
// mirrors runtime/action_executor.py's ActionExecutor._spawn_particles,
// shared by burst_particles (once) and the per-frame streaming-emitter
// update in GameRoom.step (continuous) so both paths sample identically.
function spawnParticles(system, emitter, ptype, number) {
    for (let i = 0; i < number; i++) {
        let px, py;
        if (emitter.shape === 'rectangle') {
            px = emitter.x + (Math.random() * emitter.width - emitter.width / 2);
            py = emitter.y + (Math.random() * emitter.height - emitter.height / 2);
        } else if (emitter.shape === 'ellipse') {
            const angle = Math.random() * 360;
            const radiusX = Math.random() * emitter.width / 2;
            const radiusY = Math.random() * emitter.height / 2;
            px = emitter.x + radiusX * Math.cos(angle * Math.PI / 180);
            py = emitter.y + radiusY * Math.sin(angle * Math.PI / 180);
        } else if (emitter.shape === 'diamond') {
            const t = Math.random() * 2 - 1;
            const s = (Math.random() * 2 - 1) * (1 - Math.abs(t));
            px = emitter.x + t * emitter.width / 2;
            py = emitter.y + s * emitter.height / 2;
        } else {  // line
            const t = Math.random() - 0.5;
            px = emitter.x + t * emitter.width;
            py = emitter.y;
        }

        const size = ptype.sizeMin + Math.random() * (ptype.sizeMax - ptype.sizeMin);
        const speed = ptype.speedMin + Math.random() * (ptype.speedMax - ptype.speedMin);
        const direction = ptype.directionMin + Math.random() * (ptype.directionMax - ptype.directionMin);
        const life = Math.floor(ptype.lifeMin + Math.random() * (ptype.lifeMax - ptype.lifeMin + 1));

        system.particles.push({
            x: px, y: py, size, sizeIncrease: ptype.sizeIncrease, speed, direction,
            life, maxLife: life, sprite: ptype.sprite, color: ptype.color, alpha: ptype.alpha,
        });
    }
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

// Symbol ("==", "<", ...) AND word ("equal", "less", ...) operators, mirroring
// runtime/action_executor.py's ActionExecutor._compare -- if_condition's own
// condition-type branches (variable_compare/instance_count/position_check)
// use the symbol form.
function gmCompareOp(left, operator, right) {
    const lf = parseFloat(left), rf = parseFloat(right);
    if (!isNaN(lf) && !isNaN(rf)) { left = lf; right = rf; }
    switch (operator) {
        case '==': case 'equal': return left == right;
        case '!=': case 'not_equal': return left != right;
        case '<': case 'less': return left < right;
        case '>': case 'greater': return left > right;
        case '<=': case 'less_equal': return left <= right;
        case '>=': case 'greater_equal': return left >= right;
        default: return false;
    }
}

// GameMaker-style random functions, mirroring
// runtime/action_executor.py's _evaluate_expression (gm_random/gm_irandom/
// gm_choose): irandom(n) is a random INTEGER 0..n inclusive, random(n) a
// random FLOAT 0..n exclusive, choose(a,b,...) one of its arguments.
// Referenced (as gmIrandom/gmRandom/gmChoose) from parseNumParam below —
// the numeric-parameter path was the one place these authored calls
// (e.g. create_instance's `x: "irandom(444) + 4"`) silently always
// evaluated to the caller's fallback, since parseNumParam's own
// expression whitelist has no letters in it at all.
function gmIrandom(n) {
    n = Math.trunc(Number(n));
    if (!isFinite(n) || n < 0) return 0;
    return Math.floor(Math.random() * (n + 1));
}

function gmRandom(n) {
    n = Number(n);
    return isFinite(n) ? Math.random() * n : 0;
}

function gmChoose(...args) {
    if (!args.length) return 0;
    return args[Math.floor(Math.random() * args.length)];
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
                // GameMaker's draw_set_halign/valign promise (mirrors
                // desktop's set_draw_font + _align_text_pos): x/y become
                // the alignment anchor, not always the top-left corner.
                // Canvas's own textAlign/textBaseline do the measurement,
                // so no manual width/height math is needed here.
                const halign = cmd.halign || 'left';
                ctx.textAlign = (halign === 'center' || halign === 'right') ? halign : 'left';
                const valign = cmd.valign || 'top';
                ctx.textBaseline = (valign === 'middle' || valign === 'bottom') ? valign : 'top';
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
                // {'type':'sprite','sprite_name':...,'x':...,'y':...,'subimage':N}
                // — the runtime's _draw_sprite schema. A multi-frame sprite is a
                // horizontal strip; crop the requested frame, mirroring instance
                // rendering (~line 2728). Single-frame sprites draw whole.
                const img = game && game.sprites ? game.sprites[cmd.sprite_name] : null;
                if (img && img.complete) {
                    const info = game.makeSpriteInfo ? game.makeSpriteInfo(cmd.sprite_name) : null;
                    const frames = info ? (info.frames || 1) : 1;
                    const scale = cmd.scale || 1;
                    if (frames > 1) {
                        const fw = info.width, fh = info.height;
                        const srcX = ((Math.floor(cmd.subimage || 0) % frames) + frames) % frames * fw;
                        ctx.drawImage(img, srcX, 0, fw, fh, cmd.x || 0, cmd.y || 0, fw * scale, fh * scale);
                    } else if (scale !== 1) {
                        ctx.drawImage(img, cmd.x || 0, cmd.y || 0, img.width * scale, img.height * scale);
                    } else {
                        ctx.drawImage(img, cmd.x || 0, cmd.y || 0);
                    }
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
        // Raycast (first-person) camera look direction, GM angle convention
        // (0=right, 90=up), independent of movement — see set_facing_angle.
        this.facing_angle = 0;

        // GAMEMAKER 7.0: 12 alarm clocks per instance
        this.alarms = new Array(12).fill(-1);  // -1 = inactive, >= 0 = countdown

        // Depth-based rendering: the authored value from the object's own
        // data, matching runtime/game_runner.py's GameInstance.set_object_data
        // (object_data.get('depth', 0)). Lower depth draws in front, higher
        // draws behind (see GameRoom._renderContents's sort). This used to
        // call a hardcoded name-substring heuristic (getDepthForObject,
        // matching "wall"/"box"/"soko"/etc. — leftover from an early
        // Sokoban-style prototype) that never read objectData.depth at all,
        // silently overriding every project's authored depth with whichever
        // bucket its object NAME happened to fall into. E.g. obj_quit (no
        // matching substring, default bucket 10) drew behind mz_obj_wall
        // (substring "wall", bucket 5) regardless of their real authored
        // depths (-1000 and 0), so a maze level's "Quitter" overlay button
        // rendered underneath the maze walls.
        this.depth = (objectData && objectData.depth !== undefined) ? objectData.depth : 0;

        // Grid movement helpers
        this.targetX = null;
        this.targetY = null;
        this.gridMoveSpeed = 8;

        // Collision tracking
        this._collision_other = null;
        this._collision_speeds = null; // Stores speeds at moment of collision
        // Which (otherInstanceId, eventName) pairs were overlapping LAST
        // frame, and a short post-fire cooldown per pair -- matches desktop's
        // GameRunner.detect_collisions_for_instance (_active_collisions /
        // _collision_cooldowns). Without this, checkCollisions() re-fires a
        // collision_with_X handler every single frame the overlap persists,
        // not just once when it starts.
        this._activeCollisions = new Set();
        this._collisionCooldowns = new Map();

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
        // Particles draw even when this instance is invisible -- an
        // invisible "particle controller" instance holding only emitters is
        // a common pattern (Tier 5.1). Sprite first, then the draw event's
        // queue on top — same order as the IDE runtime (GameRunner draws
        // the sprite, then processes the instance's draw queue). The draw
        // event runs through the normal action executor (so conditionals
        // like test_lives work inside it); draw_* actions queue
        // runtime-schema commands, rendered at the end.
        this.renderParticles(ctx);
        this.render(ctx);
        this.runDrawEvent(ctx);
    }

    runDrawEvent(ctx) {
        // Split out of onDraw so the raycast HUD pass can composite draw
        // actions (draw_score / draw_lives / draw_text / draw_health_bar)
        // over the finished first-person frame without also drawing sprites.
        // See GameRoom.render and docs/RAYCAST_HUD_PLAN.md.
        //
        // GameMaker: an invisible instance does not run its draw event at all
        // (the desktop runtime gets this via render()'s early return on
        // `not self.visible`). Until 2026-07-20 this file ran the draw event
        // regardless of visible — only the sprite blit was skipped — so a
        // HUD/controller hidden with visible=false kept drawing on the web
        // export while correctly drawing nothing on desktop.
        if (!this.visible) return;
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

        // Apply hspeed/vspeed, blocked by solid instances the way the desktop
        // and Kivy engines already do: an object marked `solid` with a
        // collision event registered against this object type (in EITHER
        // direction — an empty actions list still counts) stops movement
        // into it. Resolved per axis independently, matching
        // GameRunner.check_movement_collision_with_blocker /
        // GameObject._movement_blocker (Kivy) — this used to always move
        // unconditionally and rely entirely on the object's own collision
        // ACTIONS to stop itself, which left samples that lean on the
        // implicit "solid blocks movement" rule (e.g. the raycast_1..4
        // player, whose wall collision events are deliberately empty) able
        // to walk straight through walls only on this export target.
        // Scaled by roomSpeed/60 (set_room_speed) — see GameRoom's roomSpeed
        // comment for what this does and doesn't cover (gravity/friction
        // accumulation above is NOT scaled, only this final delta).
        if (this._hspeed !== 0 || this._vspeed !== 0) {
            const roomSpeedFactor = (game && game.currentRoom) ? game.currentRoom.roomSpeed / 60 : 1;
            const newX = this.x + this._hspeed * roomSpeedFactor;
            const newY = this.y + this._vspeed * roomSpeedFactor;

            if (!game || !game.currentRoom) {
                // No room context to check blockers against (shouldn't
                // normally happen) — fall back to the old unconditional move.
                this.x = newX;
                this.y = newY;
            } else {
                const blockers = [];

                if (newX !== this.x) {
                    const blocker = this._movementBlocker(newX, this.y, game);
                    if (blocker === null) {
                        this.x = newX;
                    } else {
                        blockers.push(blocker);
                    }
                }

                if (newY !== this.y) {
                    const blocker = this._movementBlocker(this.x, newY, game);
                    if (blocker === null) {
                        this.y = newY;
                    } else {
                        blockers.push(blocker);
                    }
                }

                // The desktop/Kivy engines fire the pair's collision events
                // from the blocked branch: blocking prevents the overlap, so
                // the normal per-frame checkCollisions() overlap scan never
                // sees this pair, and a handler like "stop + snap_to_grid"
                // would otherwise never run. Deduplicated by identity — a
                // corner collision blocks both axes against the same wall,
                // and the handler should fire once.
                const fired = [];
                for (const blocker of blockers) {
                    if (fired.indexOf(blocker) !== -1) continue;
                    fired.push(blocker);
                    this._fireBlockedCollision(blocker, game);
                }
            }
        }
    }

    // The first instance that would stop this one occupying (x, y).
    //
    // Blocking rule (matches GameMaker 7.0, ported from the desktop/Kivy
    // engines): a collision event must be registered between the two object
    // types (in either direction), AND at least one of them must be `solid`.
    // Two non-solid objects never block each other — they overlap and fire
    // their collision events afterwards instead (e.g. a maze monster running
    // through the player rather than getting stuck on top of it).
    _movementBlocker(x, y, game) {
        if (!game || !game.currentRoom) return null;
        const originX = this.spriteInfo ? this.spriteInfo.origin_x : 0;
        const originY = this.spriteInfo ? this.spriteInfo.origin_y : 0;
        const testRect = {
            x: x - originX + this.bboxLeft(), y: y - originY + this.bboxTop(),
            width: this.collisionWidth(), height: this.collisionHeight()
        };
        const curRect = this.getBoundingBox();

        for (const other of game.currentRoom.instances) {
            if (other === this || other.toDestroy) continue;
            if (!(this.solid || other.solid)) continue;
            if (!this._collisionEventExistsWith(other)) continue;

            const otherRect = other.getBoundingBox();
            if (!this.rectsCollide(testRect, otherRect)) continue;

            // Already overlapping at the current position: let it escape
            // rather than freezing in place (e.g. right after spawning).
            if (this.rectsCollide(curRect, otherRect)) continue;

            return other;
        }
        return null;
    }

    // True if a collision event is defined between this object type and
    // other's, in either direction. Existence only — an empty actions list
    // still counts, since a wall's own collision handler is often
    // intentionally empty and blocks purely through the `solid` flag.
    _collisionEventExistsWith(other) {
        if (this.events && this.events['collision_with_' + other.name]) return true;
        if (other.events && other.events['collision_with_' + this.name]) return true;
        return false;
    }

    // Runs the pair's collision handlers directly after a blocked move,
    // since blocking prevents the overlap checkCollisions() would otherwise
    // have detected this frame. Mirrors checkCollisions()'s own
    // _collision_other/_collision_speeds context so action handlers that
    // read `other` behave identically whether they fired via a blocked move
    // or a normal overlap.
    _fireBlockedCollision(other, game) {
        const selfHspeed = this.hspeed || 0;
        const selfVspeed = this.vspeed || 0;
        const otherHspeed = other.hspeed || 0;
        const otherVspeed = other.vspeed || 0;

        const mine = this.events && this.events['collision_with_' + other.name];
        if (mine) {
            this._collision_other = other;
            this._collision_speeds = { selfHspeed, selfVspeed, otherHspeed, otherVspeed };
            this.executeActions(mine.actions || [], game);
            this._collision_speeds = null;
        }

        const theirs = other.events && other.events['collision_with_' + this.name];
        if (theirs) {
            other._collision_other = this;
            other._collision_speeds = {
                selfHspeed: otherHspeed, selfVspeed: otherVspeed,
                otherHspeed: selfHspeed, otherVspeed: selfVspeed
            };
            other.executeActions(theirs.actions || [], game);
            other._collision_speeds = null;
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
                // A skipped QUESTION takes its own guarded unit down with
                // it too (recursively -- question chains skip as one
                // unit), matching the IDE runtime's
                // _execute_action_list_inner. Without this, a chain of 2+
                // consecutive flat questions gating one action (e.g. a
                // bounding-box click test: 4 test_variable checks ANDed
                // before a goto_room) "used up" the skip on the first
                // skipped question and let a LATER question in the same
                // chain re-arm/execute independently -- found via a real
                // click test where every one of several bounding-box
                // buttons fired on the same click, the last-processed
                // instance always winning regardless of which box the
                // click actually landed in.
                if (GameObject.isConditionalAction(actionType)) {
                    skipNext = true;
                }
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
            case 'if_condition':
            case 'if_variable': {
                // Was a no-op (no case matched -> fell through to the
                // switch's end, implicitly returning undefined/falsy), so
                // every if_condition (a first-class registered action;
                // runtime/action_executor.py's execute_if_condition_action
                // fully implements it) silently always took the else
                // branch on this export target only -- condition_type was
                // never read at all. Mirrors ActionExecutor.
                // _evaluate_if_condition's dispatch; key_pressed/
                // mouse_check are the two condition_types NOT ported here
                // (no held-key-set or mouse-button state tracked anywhere
                // in this engine) -- they fall through to false, same as
                // every condition_type did before this fix.
                const conditionType = params.condition_type || 'instance_count';
                switch (conditionType) {
                    case 'expression': {
                        const val = gmExpressionValue(params.expression, this, game);
                        return val === undefined ? false : !!val;
                    }
                    case 'variable_compare': {
                        const variable = params.variable || '';
                        if (!variable) return false;
                        const current = this[variable] !== undefined ? this[variable] : 0;
                        return gmCompareOp(current, params.operator || '==', params.value);
                    }
                    case 'instance_count': {
                        const objectName = params.object_name || '';
                        if (!objectName || !game.currentRoom) return false;
                        const count = game.currentRoom.instances.filter(
                            inst => inst.name === objectName && !inst.toDestroy).length;
                        return gmCompareOp(count, params.operator || '==', parseInt(params.value) || 0);
                    }
                    case 'position_check': {
                        const checkType = (params.check_type || 'x position').toLowerCase();
                        const current = checkType.includes('x') ? this.x : this.y;
                        return gmCompareOp(current, params.operator || '==', parseInt(params.value) || 0);
                    }
                    case 'random_chance': {
                        const chance = parseInt(params.chance) || 50;
                        return (Math.random() * 100) < chance;
                    }
                    case 'collision_check': {
                        const obj = params.object || '';
                        if (!obj || !game.currentRoom) return false;
                        const checkX = this.x + (parseFloat(params.offset_x) || 0);
                        const checkY = this.y + (parseFloat(params.offset_y) || 0);
                        return this.placeMeetsCollision(checkX, checkY, obj, game, false);
                    }
                    default:
                        return false;
                }
            }

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
                // parseNumParam (not a bare parseFloat): supports
                // self.x/other.x/facing_angle and irandom()/random()/
                // choose() expressions, and — critically — never returns
                // NaN the way parseFloat("irandom(2) - 1") silently did
                // (NaN hspeed poisons this.x on the very next movement
                // step and never recovers, rendering the instance nowhere
                // — sky_strike_1's enemy planes, whose hspeed is exactly
                // such an expression, were invisible for this reason).
                this.hspeed = parseNumParam(params.hspeed ?? params.speed ?? params.value, this, 0);
                break;

            case 'set_vspeed':
                this.vspeed = parseNumParam(params.vspeed ?? params.speed ?? params.value, this, 0);
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
                // Unreachable in practice: the nested-format branch at the
                // top of executeAction (isConditionalAction + non-empty
                // then_actions/else_actions) intercepts this action and
                // calls evaluateCondition directly before this switch is
                // ever reached. The real condition_type dispatch lives
                // there, not here.
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
                // Restart current room. forceRebuild=true: see changeRoom's
                // comment — the target IS the current room, so the normal
                // persistent-reuse check would otherwise reuse the very
                // instance being discarded.
                game.changeRoom(game.currentRoom.name, true);
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

            case 'set_room_speed': {
                // See GameRoom's roomSpeed comment: scales hspeed/vspeed's
                // final position delta, not the game loop's call rate.
                let speed = parseInt(params.speed, 10);
                if (isNaN(speed)) speed = 30;
                speed = Math.max(1, Math.min(240, speed));
                if (game.currentRoom) game.currentRoom.roomSpeed = speed;
                break;
            }

            case 'set_room_persistent': {
                // Same defensive true/false-as-string coercion as enable_views
                // above (params come straight from project JSON, which can
                // hold either JS booleans or the string "true"/"false").
                const p = params.persistent;
                const flag = !(p === false || p === 'false' || p === 0 || p === '0');
                if (game.currentRoom) game.currentRoom.persistent = flag;
                break;
            }

            case 'set_background_color': {
                if (game.currentRoom) {
                    game.currentRoom.bgColor = params.color || '#000000';
                    const sc = params.show_color;
                    game.currentRoom.showBackgroundColor =
                        !(sc === false || sc === 'false' || sc === 0 || sc === '0');
                }
                break;
            }

            case 'set_background': {
                if (game.currentRoom) {
                    const room = game.currentRoom;
                    const vis = params.visible;
                    const visible = !(vis === false || vis === 'false' || vis === 0 || vis === '0');
                    const isTruthy = (v) => v === true || v === 'true' || v === 1 || v === '1';
                    room.dynamicBgName = params.background || '';
                    room.dynamicBgVisible = visible;
                    room.dynamicBgForeground = isTruthy(params.foreground);
                    room.dynamicBgTileH = isTruthy(params.tiled_h);
                    room.dynamicBgTileV = isTruthy(params.tiled_v);
                    room.dynamicBgHspeed = parseFloat(params.hspeed) || 0;
                    room.dynamicBgVspeed = parseFloat(params.vspeed) || 0;
                    if (!visible) room.dynamicBgName = '';
                }
                break;
            }

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
                // Display a message dialog. Desktop's equivalent
                // (_show_or_queue_message, runtime/action_executor.py) has
                // NO side effects beyond showing the dialog — this used to
                // also zero hspeed/vspeed/speed and snap x/y to a hardcoded
                // 32px grid ("prevents drifting off-grid during collision
                // events"), which only ever made sense for a grid-based
                // game like the maze sample. Applied unconditionally to
                // EVERY show_message call on every exported game, it
                // silently teleported any free-movement instance up to 16px
                // toward the nearest grid line — the promo game's
                // side-scroller hit this at the very first frame (its intro
                // show_message, fired from create, snapped the player 16px
                // down, deep enough to land it inside/through the ground).
                const message = params.message || params.text || '';
                if (message) alert(message);
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

            case 'set_health': {
                const oldHealth = game.health;
                if (params.relative) {
                    game.health += parseFloat(params.value) || 0;
                } else {
                    game.health = parseFloat(params.value) || 0;
                }
                game.health = Math.max(0, Math.min(100, game.health));
                console.log(`💚 Health: ${game.health}`);
                // IDE-runtime semantics, mirroring set_lives above: when
                // health crosses from >0 to <=0, fire no_more_health once on
                // EVERY instance that defines it. Missing until 2026-07-20,
                // so a health-based lose condition never fired on this target.
                if (oldHealth > 0 && game.health <= 0 && game.currentRoom) {
                    [...game.currentRoom.instances].forEach(inst => {
                        if (!inst.toDestroy && inst.events && inst.events.no_more_health) {
                            inst.executeActions(inst.events.no_more_health.actions || [], game);
                        }
                    });
                }
                break;
            }

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
                // Built-in game-state readouts (score/lives/health) as a bare
                // token — matches desktop's _parse_value, which resolves
                // these off game_runner. Lets a level copy its final score
                // into a global (e.g. the promo hub's per-level totals)
                // without a new dedicated action.
                if (value === 'score' || value === 'lives' || value === 'health') {
                    value = game[value];
                } else {
                    const num = parseFloat(value);
                    if (!isNaN(num) && String(num) === String(value).trim()) value = num;
                }
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
                // max_distance — the platformer landing action. parseNumParam
                // (not a bare parseFloat): a project commonly authors
                // `direction: "direction"` (GameMaker's own convention for
                // "my current direction of travel"), which parseFloat cannot
                // parse at all (NaN -> the old `|| 0` fallback silently
                // meant "always push right", REGARDLESS of which way the
                // instance actually approached whatever it collided with —
                // walking left, up, or down into a solid all got pushed
                // further right instead of separated, eventually punching
                // straight through it one blocked frame at a time).
                const dirDeg = parseNumParam(params.direction, this, 0);
                const maxDist = parseNumParam(params.max_distance ?? params.maximum, this, 1000);
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
                    inst.depth = (objectData && objectData.depth !== undefined) ? objectData.depth : 0;
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

            case 'draw_text': {
                // A bare "global.<name>" reference resolves to that global's
                // value (matching desktop's _parse_value, which routes
                // draw_text's text through the same dotted-scope resolution
                // every other action gets) — e.g. the promo hub's per-level
                // score readouts. Anything else (including any string with
                // its own dots/operators) is drawn as literal text, same as
                // before; this is deliberately narrower than desktop's full
                // expression support to avoid changing existing samples'
                // rendered text.
                let text = params.text !== undefined ? params.text : '';
                if (typeof text === 'string') {
                    const trimmed = text.trim();
                    const gmatch = trimmed.match(/^global\.(\w+)$/);
                    if (gmatch && game.globalVariables && gmatch[1] in game.globalVariables) {
                        text = game.globalVariables[gmatch[1]];
                    } else if (/^global\.\w+(\s*\+\s*global\.\w+)+$/.test(trimmed)) {
                        // A "+"-joined sum of bare global references (e.g. the
                        // promo hub's cross-level total) — still no general
                        // expression evaluator, just this one safe shape.
                        text = trimmed.split('+').reduce((sum, term) => {
                            const name = term.trim().slice('global.'.length);
                            const v = game.globalVariables && name in game.globalVariables
                                ? game.globalVariables[name] : 0;
                            return sum + v;
                        }, 0);
                    } else if (text.length >= 2 && text.startsWith('"') && text.endsWith('"')) {
                        // Desktop's _parse_value routes any text containing an
                        // operator character (+ - * / %) through its arithmetic
                        // expression evaluator UNLESS it's wrapped in quotes —
                        // authors quote text like "W A S D - Move" to keep it
                        // literal (this repo's own documented landmine).
                        // engine.js never evaluates plain draw_text, so it never
                        // needed the workaround, but it must still strip the
                        // quotes an author added FOR desktop's sake, or the
                        // literal quote characters render on screen.
                        text = text.slice(1, -1);
                    }
                }
                this._draw_queue.push({
                    type: 'text',
                    text: String(text),
                    x: parseNumParam(params.x, this, this.x),
                    y: parseNumParam(params.y, this, this.y),
                    // runtime: active draw colour, defaulting to black
                    color: this.draw_color || game.draw_color || [0, 0, 0],
                    halign: this.draw_halign || 'left',
                    valign: this.draw_valign || 'top',
                });
                break;
            }

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
                    subimage: parseNumParam(params.subimage, this, 0),
                    scale: parseNumParam(params.scale, this, 1.0),
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

            case 'set_draw_font': {
                // Font is stored for parity only (the canvas renderer uses
                // one font); halign/valign ARE applied, by draw_text's
                // render case below — matching desktop's set_draw_font +
                // _align_text_pos (GameMaker's draw_set_halign/valign
                // promise: x/y become the alignment anchor, not always the
                // top-left corner). GM's numeric `align` (0/1/2) fallback,
                // same mapping as _GM_FONT_ALIGN_FALLBACK on desktop.
                this.draw_font = params.font || null;
                const alignFallback = { 0: 'left', 1: 'center', 2: 'right' };
                let halign = params.halign;
                if (halign === undefined && params.align !== undefined) {
                    halign = alignFallback[params.align] || 'left';
                }
                this.draw_halign = ['left', 'center', 'right'].includes(halign) ? halign : 'left';
                const valign = params.valign;
                this.draw_valign = ['top', 'middle', 'bottom'].includes(valign) ? valign : 'top';
                break;
            }

            // ---- Instance creation / destruction cluster ----

            case 'create_instance': {
                // Matches the desktop runtime's execute_create_instance_action
                // (runtime/action_executor.py): object/x/y, with x/y relative
                // to the caller when `relative` is set. Spawning goes through
                // game.spawnInstance, which marks the new instance's create
                // event pending -- it fires on the main loop's next pass over
                // instances (the same path create_moving_instance relies on),
                // not synchronously here.
                const relative = params.relative === true || params.relative === 'true';
                let px = parseNumParam(params.x, this, 0);
                let py = parseNumParam(params.y, this, 0);
                if (relative) { px += this.x; py += this.y; }
                game.spawnInstance(params.object || '', px, py);
                break;
            }

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

            // --- Particle system + timelines (Tier 5.1/5.3) -----------------
            // Mirrors runtime/action_executor.py's Particles-tab and
            // Timing-tab actions exactly. updateParticleSystem/
            // updateTimeline (called every step from GameRoom.step, not
            // gated on any action here) and renderParticles (called from
            // onDraw, before the visibility check) do the per-frame work --
            // see those methods for the read side.

            case 'create_particle_system': {
                const depth = Math.trunc(parseNumParam(params.depth, this, 0));
                this._particleSystem = {
                    depth, particleTypes: {}, emitters: {}, particles: [],
                    nextTypeId: 0, nextEmitterId: 0,
                };
                break;
            }

            case 'destroy_particle_system':
                this._particleSystem = null;
                break;

            case 'clear_particles':
                if (this._particleSystem) this._particleSystem.particles = [];
                break;

            case 'create_particle_type': {
                if (!this._particleSystem) { this._lastParticleTypeId = -1; break; }
                const sizeMin = parseNumParam(params.size_min, this, 1.0);
                const sizeMax = parseNumParam(params.size_max, this, 1.0);
                const sizeIncrease = parseNumParam(params.size_increase, this, 0);
                const colorParam = params.color !== undefined ? String(params.color) : '#FFFFFF';
                const alpha = parseNumParam(params.alpha, this, 1.0);
                const speedMin = parseNumParam(params.speed_min, this, 0);
                const speedMax = parseNumParam(params.speed_max, this, 0);
                const directionMin = parseNumParam(params.direction_min, this, 0);
                const directionMax = parseNumParam(params.direction_max, this, 360);
                const lifeMin = Math.trunc(parseNumParam(params.life_min, this, 100));
                const lifeMax = Math.trunc(parseNumParam(params.life_max, this, 100));
                let color = [255, 255, 255];
                if (colorParam.startsWith('#') && colorParam.length >= 7) {
                    const r = parseInt(colorParam.slice(1, 3), 16);
                    const g = parseInt(colorParam.slice(3, 5), 16);
                    const b = parseInt(colorParam.slice(5, 7), 16);
                    if (!isNaN(r) && !isNaN(g) && !isNaN(b)) color = [r, g, b];
                }
                const typeId = this._particleSystem.nextTypeId++;
                this._particleSystem.particleTypes[typeId] = {
                    sprite: params.sprite || null, sizeMin, sizeMax, sizeIncrease, color, alpha,
                    speedMin, speedMax, directionMin, directionMax, lifeMin, lifeMax,
                };
                this._lastParticleTypeId = typeId;
                break;
            }

            case 'create_emitter': {
                if (!this._particleSystem) { this._lastEmitterId = null; break; }
                const x = Math.trunc(parseNumParam(params.x, this, 0));
                const y = Math.trunc(parseNumParam(params.y, this, 0));
                const width = Math.trunc(parseNumParam(params.width, this, 0));
                const height = Math.trunc(parseNumParam(params.height, this, 0));
                let shape = params.shape !== undefined ? String(params.shape) : 'rectangle';
                if (!['rectangle', 'ellipse', 'diamond', 'line'].includes(shape)) shape = 'rectangle';
                const emitterId = this._particleSystem.nextEmitterId++;
                this._particleSystem.emitters[emitterId] = {
                    x, y, width, height, shape, streamType: null, streamCount: 0,
                };
                this._lastEmitterId = emitterId;
                break;
            }

            case 'destroy_emitter':
                if (this._particleSystem && this._lastEmitterId !== null &&
                    this._lastEmitterId !== undefined) {
                    delete this._particleSystem.emitters[this._lastEmitterId];
                    this._lastEmitterId = null;
                }
                break;

            case 'burst_particles': {
                if (!this._particleSystem) break;
                const particleType = Math.trunc(parseNumParam(params.particle_type, this, 0));
                const number = Math.trunc(parseNumParam(params.number, this, 10));
                const ptype = this._particleSystem.particleTypes[particleType];
                if (!ptype) break;
                if (this._lastEmitterId === null || this._lastEmitterId === undefined) break;
                const emitter = this._particleSystem.emitters[this._lastEmitterId];
                if (!emitter) break;
                spawnParticles(this._particleSystem, emitter, ptype, number);
                break;
            }

            case 'stream_particles': {
                if (!this._particleSystem) break;
                const particleType = Math.trunc(parseNumParam(params.particle_type, this, 0));
                const number = Math.trunc(parseNumParam(params.number, this, 1));
                if (!this._particleSystem.particleTypes[particleType]) break;
                if (this._lastEmitterId === null || this._lastEmitterId === undefined) break;
                const emitter = this._particleSystem.emitters[this._lastEmitterId];
                if (!emitter) break;
                emitter.streamType = particleType;
                emitter.streamCount = number;
                break;
            }

            case 'set_timeline':
                this.timelineIndex = params.timeline !== undefined ? params.timeline : null;
                this.timelinePosition = 0;
                if (this.timelineSpeed === undefined) this.timelineSpeed = 1.0;
                if (this.timelineRunning === undefined) this.timelineRunning = false;
                break;

            case 'set_timeline_position': {
                const position = Math.trunc(parseNumParam(params.position, this, 0));
                const relative = params.relative === true || params.relative === 'true' ||
                                  params.relative === 1 || params.relative === '1';
                if (this.timelinePosition === undefined) this.timelinePosition = 0;
                this.timelinePosition = relative ? this.timelinePosition + position : position;
                if (this.timelinePosition < 0) this.timelinePosition = 0;
                break;
            }

            case 'set_timeline_speed':
                this.timelineSpeed = parseNumParam(params.speed, this, 1.0);
                break;

            case 'start_timeline':
                this.timelineRunning = true;
                break;

            case 'pause_timeline':
                this.timelineRunning = false;
                break;

            case 'stop_timeline':
                this.timelineRunning = false;
                this.timelinePosition = 0;
                break;

            default:
                if (_extActions[actionType]) {
                    // An extension-contributed action (Stage C). Same (obj,
                    // params, game) shape a switch case had via this/params/game.
                    _extActions[actionType](this, params, game);
                } else {
                    console.warn(`Unknown action: ${actionType}`);
                }
        }
    }

    checkCollisionAt(x, y, game) {
        // Get my collision box dimensions and origin
        const myW = this.collisionWidth();
        const myH = this.collisionHeight();
        const originX = this.spriteInfo ? this.spriteInfo.origin_x : 0;
        const originY = this.spriteInfo ? this.spriteInfo.origin_y : 0;
        // Test rect at position (x, y) accounting for origin + bbox offset
        const testRect = {
            x: x - originX + this.bboxLeft(), y: y - originY + this.bboxTop(),
            width: myW, height: myH
        };
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

        // Get my collision box dimensions and origin
        const myW = this.collisionWidth();
        const myH = this.collisionHeight();
        const originX = this.spriteInfo ? this.spriteInfo.origin_x : 0;
        const originY = this.spriteInfo ? this.spriteInfo.origin_y : 0;
        // Test rect at position (x, y) accounting for origin + bbox offset
        const testRect = {
            x: x - originX + this.bboxLeft(), y: y - originY + this.bboxTop(),
            width: myW, height: myH
        };
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

    // Collision box, distinct from the render/frame box above: bbox_left/
    // top/right/bottom (Game.makeSpriteInfo), in sprite-local pixel coords,
    // defaulting to the full frame when a sprite has no explicit override
    // (matches runtime/game_runner.py's Sprite bbox fields). A sprite like
    // spr_person defines an 8x8 collision box centered in its 16x16 frame —
    // using the full frame here made the HTML5 player's effective collision
    // footprint twice desktop's, which was enough to start a level already
    // overlapping a nearby wall and trigger the "already overlapping, let
    // it escape" rule in _movementBlocker below, walking the player through
    // the wall with no way back in.
    bboxLeft() {
        return this.spriteInfo ? (this.spriteInfo.bbox_left || 0) : 0;
    }

    bboxTop() {
        return this.spriteInfo ? (this.spriteInfo.bbox_top || 0) : 0;
    }

    collisionWidth() {
        if (this.spriteInfo && this.spriteInfo.bbox_right !== undefined) {
            return this.spriteInfo.bbox_right - this.bboxLeft();
        }
        return this.boxWidth();
    }

    collisionHeight() {
        if (this.spriteInfo && this.spriteInfo.bbox_bottom !== undefined) {
            return this.spriteInfo.bbox_bottom - this.bboxTop();
        }
        return this.boxHeight();
    }

    getBoundingBox() {
        const originX = this.spriteInfo ? this.spriteInfo.origin_x : 0;
        const originY = this.spriteInfo ? this.spriteInfo.origin_y : 0;
        return {
            x: this.x - originX + this.bboxLeft(),
            y: this.y - originY + this.bboxTop(),
            width: this.collisionWidth(),
            height: this.collisionHeight()
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
        const left = atX - originX + this.bboxLeft(), top = atY - originY + this.bboxTop();
        const w = this.collisionWidth(), h = this.collisionHeight();
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

    // Per-frame particle update (Tier 5.1): spawn from streaming emitters,
    // then age/move/cull every live particle. Mirrors
    // GameInstance.update_particle_system in runtime/game_runner.py.
    updateParticleSystem() {
        const ps = this._particleSystem;
        if (!ps) return;

        for (const emitter of Object.values(ps.emitters)) {
            if (emitter.streamType === null || emitter.streamType === undefined) continue;
            if (!(emitter.streamCount > 0)) continue;
            const ptype = ps.particleTypes[emitter.streamType];
            if (!ptype) continue;
            spawnParticles(ps, emitter, ptype, emitter.streamCount);
        }

        const surviving = [];
        for (const p of ps.particles) {
            p.life -= 1;
            if (p.life <= 0) continue;
            const angleRad = p.direction * Math.PI / 180;
            p.x += Math.cos(angleRad) * p.speed;
            p.y -= Math.sin(angleRad) * p.speed;
            p.size = Math.max(0.0, p.size + p.sizeIncrease);
            surviving.push(p);
        }
        ps.particles = surviving;
    }

    // Advance timelinePosition by timelineSpeed while timelineRunning is
    // set. Mirrors GameInstance.update_timeline -- see that method's
    // docstring for why there is no separate "moments" table: an author
    // reacts to a specific position with an ordinary conditional in Step.
    updateTimeline() {
        if (this.timelineRunning) {
            const speed = this.timelineSpeed !== undefined ? this.timelineSpeed : 1.0;
            this.timelinePosition = (this.timelinePosition || 0) + speed;
        }
    }

    // Draw this instance's live particles. Called from onDraw BEFORE the
    // visibility check (mirrors render_particles in runtime/game_runner.py)
    // so an invisible "particle controller" instance still shows its
    // particles.
    renderParticles(ctx) {
        const ps = this._particleSystem;
        if (!ps || !ps.particles.length) return;

        for (const p of ps.particles) {
            const x = p.x, y = p.y;
            const alpha = Math.max(0, Math.min(1, p.alpha !== undefined ? p.alpha : 1.0));
            const sprite = p.sprite && this._gameRef && this._gameRef.sprites
                ? this._gameRef.sprites[p.sprite] : null;
            if (sprite && sprite.complete) {
                const scale = Math.max(0.01, p.size || 1.0);
                const w = Math.max(1, sprite.width * scale);
                const h = Math.max(1, sprite.height * scale);
                ctx.save();
                ctx.globalAlpha = alpha;
                ctx.drawImage(sprite, x - w / 2, y - h / 2, w, h);
                ctx.restore();
            } else {
                const radius = Math.max(1, p.size || 1.0);
                const color = p.color || [255, 255, 255];
                ctx.save();
                ctx.globalAlpha = alpha;
                ctx.fillStyle = `rgb(${color[0]},${color[1]},${color[2]})`;
                ctx.beginPath();
                ctx.arc(x, y, radius, 0, Math.PI * 2);
                ctx.fill();
                ctx.restore();
            }
        }
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

        // Decrement cooldowns (mirrors desktop's per-frame pass).
        for (const [key, frames] of this._collisionCooldowns) {
            if (frames <= 1) this._collisionCooldowns.delete(key);
            else this._collisionCooldowns.set(key, frames - 1);
        }

        // First pass: Detect all collisions and capture speeds BEFORE any events run
        const collisionsToProcess = [];
        const currentCollisions = new Set();

        for (const other of game.currentRoom.instances) {
            if (other === this || other.toDestroy) continue;

            const otherRect = other.getBoundingBox();

            if (this.rectsCollide(myRect, otherRect)) {
                const collisionKey = `collision_with_${other.name}`;

                if (this.events[collisionKey]) {
                    // Fire only on a NEW overlap (not every frame it
                    // persists), matching desktop's _active_collisions —
                    // otherwise a handler that nudges position on contact
                    // (e.g. move_to_contact, which moves a step before it
                    // checks for contact) re-fires every frame the pair
                    // keeps touching and walks the instance further in each
                    // time, since starting already-overlapping it never
                    // sees a fresh "just touched" transition to stop at.
                    const pairKey = `${other._pyId}:${collisionKey}`;
                    currentCollisions.add(pairKey);
                    const isNew = !this._activeCollisions.has(pairKey);
                    const inCooldown = this._collisionCooldowns.has(pairKey);
                    if (isNew && !inCooldown) {
                        collisionsToProcess.push({
                            event: this.events[collisionKey],
                            other: other,
                            // Capture speeds at moment of collision detection
                            selfHspeed: this.hspeed || 0,
                            selfVspeed: this.vspeed || 0,
                            otherHspeed: other.hspeed || 0,
                            otherVspeed: other.vspeed || 0
                        });
                        this._collisionCooldowns.set(pairKey, 5);
                    }
                }
            }
        }
        this._activeCollisions = currentCollisions;

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

        // Room-level state the "Room" category actions mutate at runtime
        // (set_room_persistent / set_room_speed / set_background_color /
        // set_background). `persistent` decides whether Game.changeRoom
        // reuses this exact GameRoom on a revisit instead of rebuilding
        // fresh (see Game.changeRoom/buildRoom below — HTML5 previously
        // always reused every room forever, the opposite default from
        // Kivy, and the same bug shape the desktop runtime had before its
        // own fix). `roomSpeed` scales hspeed/vspeed's final per-tick
        // position delta (GameObject.processMovement) — NOT the game loop's
        // call rate, which stays uncapped/rAF-driven — so this is a
        // documented approximation of the desktop runtime's true
        // step-rate model: gravity/friction accumulation is unaffected by
        // roomSpeed here, only the resulting hspeed/vspeed's translation
        // into position.
        this.persistent = !!data.persistent;
        this.roomSpeed = 60;
        this.showBackgroundColor = true;

        // room_start fires once per room ENTRY (not once per room object,
        // unlike create's per-instance _pendingCreateEvent) -- consumed at
        // the top of step() and re-armed by Game.changeRoom on every visit,
        // including a persistent-room reuse where no instance gets a fresh
        // create at all. See step()'s "0c" block.
        this._pendingRoomStart = true;

        // set_background's dynamic background image. Drawn directly each
        // frame from this state (immediate-mode canvas rendering, unlike
        // Kivy's retained instruction graph — no separate group/instruction
        // bookkeeping needed). The room's baked bgImage/backgroundSprite (if
        // any) keeps drawing underneath; for the common stretched/opaque
        // case this dynamic one fully occludes it once set, matching
        // GameMaker's "replace" semantics visually.
        this.dynamicBgName = '';
        this.dynamicBgVisible = false;
        this.dynamicBgForeground = false;
        this.dynamicBgTileH = false;
        this.dynamicBgTileV = false;
        this.dynamicBgHspeed = 0;
        this.dynamicBgVspeed = 0;
        this.dynamicBgScrollX = 0;
        this.dynamicBgScrollY = 0;

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

    // spriteTopLeft is the one generic helper kept in engine.js (mirrors core
    // _sprite_top_left); the raycast renderer itself lives in the raycast_2_5d
    // extension's export_html5.js (Stage C).

    // The instance's true sprite top-left. Rendering and collision both use
    // x - origin_x, so raycast geometry must too -- a sprite with a centred
    // origin was otherwise placed half a sprite off, putting billboards on the
    // grid lines where walls sit (they got sliced in half by the occlusion
    // test). Mirrors game_runner._sprite_top_left.
    static spriteTopLeft(inst) {
        const info = inst.spriteInfo;
        const ox = info && info.origin_x ? info.origin_x : 0;
        const oy = info && info.origin_y ? info.origin_y : 0;
        return { x: inst.x - ox, y: inst.y - oy };
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
        this._advanceDynamicBgScroll();

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

        // 0c. room_start fires every time this room becomes active, after
        // create (and after game_start on the very first room) — matching
        // runtime/game_runner.py's trigger_room_start_event. Unlike
        // create's per-instance _pendingCreateEvent flag, this is a
        // per-ROOM flag re-armed by Game.changeRoom on every entry, so it
        // also fires for a persistent room reused wholesale (whose
        // instances never got a fresh create at all in the loop above).
        if (this._pendingRoomStart) {
            this._pendingRoomStart = false;
            [...this.instances].forEach(inst => {
                if (!inst.toDestroy && inst.events && inst.events.room_start) {
                    inst.executeActions(inst.events.room_start.actions || [], game);
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

        // 3d. Particles & timeline (Tier 5.1)
        this.instances.forEach(inst => {
            if (inst.toDestroy) return;
            inst.updateParticleSystem();
            inst.updateTimeline();
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
        // Extensions get first refusal on drawing this room (Stage C mechanism,
        // mirrors the desktop extension_hooks seam). A claim replaces the
        // top-down pass; the HUD/draw-event pass still composites on top.
        if (renderExtensionRoom(this, ctx)) {
            const hudInstances = [...this.instances].sort((a, b) => b.depth - a.depth);
            hudInstances.forEach(inst => inst.runDrawEvent(ctx));
            return;
        }
        // Fill the whole canvas with the bg color once; areas outside any
        // view port then show the bg color rather than stale pixels.
        // showBackgroundColor=false fills black instead of skipping the
        // fill (this canvas redraws every frame; skipping would smear the
        // previous frame) — matches the desktop runtime's fallback.
        ctx.fillStyle = this.showBackgroundColor ? this.bgColor : '#000000';
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

        if (!this.dynamicBgForeground) this._drawDynamicBackground(ctx);

        // GAMEMAKER 7.0: Draw events (sort by depth first)
        // GameMaker depth: HIGHER depth is drawn FIRST (further back), so a
        // LOWER depth ends up in front. That means descending order — matching
        // the desktop runtime (GameRoom._render_room). This sorted ASCENDING
        // until 2026-07-20, which inverted sprite z-order on every export whose
        // objects use more than one depth (maze_3, maze_4, plateforme_3,
        // treasure): plateforme_3's player (depth -100) drew BEHIND the exit
        // (depth 100) instead of in front.
        const sortedInstances = [...this.instances].sort((a, b) => b.depth - a.depth);
        sortedInstances.forEach(inst => inst.onDraw(ctx));

        if (this.dynamicBgForeground) this._drawDynamicBackground(ctx);
    }

    // set_background's dynamic image, tiled the same way as the baked
    // bgImage/backgroundSprite above (start one tile before the scroll
    // offset so a partial tile still covers the edge, wrapping via
    // dynamicBgScrollX/Y) — mirrors the desktop runtime's
    // GameRoom._render_legacy_background tiling math.
    _drawDynamicBackground(ctx) {
        if (!this.dynamicBgVisible || !this.dynamicBgName) return;
        const sprites = this._gameRef ? this._gameRef.sprites : null;
        const img = sprites ? sprites[this.dynamicBgName] : null;
        if (!img || !img.complete) return;

        const doTileH = this.dynamicBgTileH || this.dynamicBgHspeed !== 0;
        const doTileV = this.dynamicBgTileV || this.dynamicBgVspeed !== 0;
        if (!doTileH && !doTileV) {
            ctx.drawImage(img, 0, 0, this.width, this.height);
            return;
        }
        const iw = img.width, ih = img.height;
        const ox = doTileH ? this.dynamicBgScrollX : 0;
        const oy = doTileV ? this.dynamicBgScrollY : 0;
        const startX = doTileH ? ox - iw : 0;
        const startY = doTileV ? oy - ih : 0;
        const stepX = doTileH ? iw : this.width;
        const stepY = doTileV ? ih : this.height;
        for (let x = startX; x < this.width; x += stepX) {
            for (let y = startY; y < this.height; y += stepY) {
                ctx.drawImage(img, x, y);
            }
        }
    }

    // Advances the dynamic background's scroll offset one tick, scaled by
    // roomSpeed/60 — same scale factor GameObject.processMovement applies
    // to hspeed/vspeed, so a faster roomSpeed scrolls the background
    // faster too.
    _advanceDynamicBgScroll() {
        if (this.dynamicBgHspeed === 0 && this.dynamicBgVspeed === 0) return;
        const sprites = this._gameRef ? this._gameRef.sprites : null;
        const img = sprites ? sprites[this.dynamicBgName] : null;
        if (!img || !img.complete) return;
        const factor = this.roomSpeed / 60;
        const iw = img.width || 1, ih = img.height || 1;
        this.dynamicBgScrollX = ((this.dynamicBgScrollX + this.dynamicBgHspeed * factor) % iw + iw) % iw;
        this.dynamicBgScrollY = ((this.dynamicBgScrollY + this.dynamicBgVspeed * factor) % ih + ih) % ih;
    }
}

class Game {
    constructor() {
        console.log('🎮 Initializing game...');
        this.canvas = document.getElementById('gameCanvas');
        this.ctx = this.canvas.getContext('2d');
        this.rooms = {};
        this.currentRoom = null;
        // set_room_persistent support: which room indices/names have been
        // entered before this playthrough — see buildRoom/changeRoom.
        this._visitedRooms = new Set();
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
        // Collision box (bbox_left/top/right/bottom): an explicit override
        // in the sprite data when all four are present, else the full
        // frame -- matches runtime/game_runner.py's Sprite bbox fields
        // (Sprite._resolve_bbox's "no override" fallback). A sprite like
        // spr_person can define an 8x8 box centered in a 16x16 frame, which
        // desktop's collision math already honors; without this the
        // collision box here silently defaulted to the full frame.
        const hasBbox = ['bbox_left', 'bbox_top', 'bbox_right', 'bbox_bottom']
            .every(k => meta[k] !== undefined && meta[k] !== null);
        return {
            origin_x: meta.origin_x || 0,
            origin_y: meta.origin_y || 0,
            width: fw,
            height: fh,
            frames: frames,
            bbox_left: hasBbox ? parseInt(meta.bbox_left) : 0,
            bbox_top: hasBbox ? parseInt(meta.bbox_top) : 0,
            bbox_right: hasBbox ? parseInt(meta.bbox_right) : fw,
            bbox_bottom: hasBbox ? parseInt(meta.bbox_bottom) : fh,
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
        // xstart/ystart: GameMaker's own (and the desktop runtime's,
        // runtime/game_runner.py's GameInstance.xstart/ystart) canonical
        // names for these, so an authored expression referencing
        // self.xstart/self.ystart resolves identically on both export
        // targets — unlike _startX/_startY, an HTML5-only internal
        // convention gmExpressionValue's scope never exposed as a bare
        // name anyway (its leading underscore excludes it), so no
        // existing authored content could have relied on that name.
        inst.xstart = x;
        inst.ystart = y;
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
        const RIGHT_PRESS_KEYS = ['mouse_right_press', 'mouse_right_button', 'mouse_right_down'];
        const RIGHT_RELEASE_KEYS = ['mouse_right_release'];
        const MIDDLE_PRESS_KEYS = ['mouse_middle_press', 'mouse_middle_button', 'mouse_middle_down'];
        const MIDDLE_RELEASE_KEYS = ['mouse_middle_release'];

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

        // DOM MouseEvent.button: 0=left, 1=middle, 2=right.
        this.canvas.addEventListener('mousedown', (e) => {
            if (e.button === 0) dispatch(e.clientX, e.clientY, PRESS_KEYS);
            else if (e.button === 2) dispatch(e.clientX, e.clientY, RIGHT_PRESS_KEYS);
            else if (e.button === 1) dispatch(e.clientX, e.clientY, MIDDLE_PRESS_KEYS);
        });
        this.canvas.addEventListener('mouseup', (e) => {
            if (e.button === 0) dispatch(e.clientX, e.clientY, RELEASE_KEYS);
            else if (e.button === 2) dispatch(e.clientX, e.clientY, RIGHT_RELEASE_KEYS);
            else if (e.button === 1) dispatch(e.clientX, e.clientY, MIDDLE_RELEASE_KEYS);
        });
        // Without this, a right-click opens the browser's context menu
        // instead of (or as well as) reaching mouse_right_press.
        this.canvas.addEventListener('contextmenu', (e) => e.preventDefault());
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

        for (const roomName of Object.keys(roomsData)) {
            this.rooms[roomName] = this.buildRoom(roomName);
            console.log(`✓ Loaded room: ${roomName} (${this.rooms[roomName].instances.length} instances)`);
        }

        const firstRoom = Object.keys(this.rooms)[0];
        if (firstRoom) {
            this.currentRoom = this.rooms[firstRoom];
            this._visitedRooms.add(firstRoom);
            console.log(`🚀 Starting with room: ${firstRoom}`);
        }
    }

    // Builds a fresh GameRoom (with fresh instances) from this.gameData —
    // the one place a room is constructed, called both at startup (loadGame,
    // once per room) and by changeRoom on a non-persistent revisit (set_room_
    // persistent's whole point: reproduce the room's authored layout again,
    // discarding whatever state the previous visit left it in).
    buildRoom(roomName) {
        const roomData = this.gameData.assets.rooms[roomName];
        const sprites = this.sprites;
        const room = new GameRoom(roomData);
        room._gameRef = this;  // so renderRaycastView can resolve textures

        // Desktop's GameRunner reads settings.room_speed ONCE, globally, into
        // self.fps -- the pygame clock's real tick rate, so hspeed/vspeed
        // apply at exactly that many real steps per second (no per-tick
        // scaling there). HTML5's game loop is uncapped/rAF-driven instead,
        // so GameRoom.roomSpeed exists purely to reproduce the same real-
        // world speed by scaling the per-frame position delta (see its
        // constructor comment) -- but it was hardcoded to 60 regardless of
        // what the project actually configured, so any project with
        // room_speed != 60 played at the wrong real-world speed on this
        // target only (e.g. the promo game's room_speed: 30 made HTML5 run
        // exactly 2x desktop's real speed). set_room_speed can still change
        // it at runtime same as before; this only fixes the STARTING value.
        const configuredSpeed = parseFloat(this.gameData.settings && this.gameData.settings.room_speed);
        room.roomSpeed = (!isNaN(configuredSpeed) && configuredSpeed > 0) ? configuredSpeed : 60;

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
            const objectData = this.gameData.assets.objects[objName];
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
            // xstart/ystart: GameMaker's/desktop's canonical names for the
            // same thing, so an authored expression works identically on
            // both export targets — see spawnInstance's matching comment.
            inst.xstart = instData.x;
            inst.ystart = instData.y;

            if (objectData && objectData.sprite && sprites[objectData.sprite]) {
                inst.sprite = sprites[objectData.sprite];
                inst.spriteInfo = this.makeSpriteInfo(objectData.sprite);
            }

            room.instances.push(inst);
        });

        return room;
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

    // forceRebuild=true (restart_room) always builds fresh and skips the
    // reuse check entirely — needed because restart_room's target IS the
    // current room name, so the normal "reuse if already visited and
    // persistent" check would otherwise reuse the very room instance being
    // discarded (its persistent flag hasn't changed just because a restart
    // was requested).
    changeRoom(roomName, forceRebuild = false) {
        if (this.gameData.assets.rooms[roomName]) {
            // Clear keyboard state
            for (const key in this.keys) {
                this.keys[key] = false;
            }
            this.keysPressed = {};
            this.keysReleased = {};

            const existing = this.rooms[roomName];
            const reuse = !forceRebuild && this._visitedRooms.has(roomName)
                          && existing && existing.persistent;
            if (!reuse) {
                this.rooms[roomName] = this.buildRoom(roomName);
            }
            this._visitedRooms.add(roomName);
            this.currentRoom = this.rooms[roomName];
            // Re-arm room_start on every entry, including a persistent-room
            // reuse (a freshly built room already has this true from its own
            // constructor, but re-asserting it here is harmless and covers
            // the reuse branch, which skips buildRoom entirely).
            this.currentRoom._pendingRoomStart = true;

            // Resize canvas
            this.canvas.width = this.currentRoom.width;
            this.canvas.height = this.currentRoom.height;

            console.log(`📍 Changed to room: ${roomName}`);
        } else {
            console.warn(`⚠️ Room not found: ${roomName}`);
        }
    }
}

// __PYGM_EXTENSION_JS__
// (The exporter concatenates each enabled extension's export_html5.js above,
// after all engine classes are defined, so it can augment prototypes and call
// registerRoomRenderer / registerExtensionAction. Left as a comment when there
// are no extensions, so engine.js stays valid on its own.)

window.addEventListener('load', async () => {
    try {
        window.game = new Game();
        // Loads Pyodide (only for projects that contain execute_code
        // actions) in the BACKGROUND rather than blocking start() on it --
        // a project mixing Python and non-Python rooms would otherwise
        // show a black screen on EVERY room, including ones that never
        // call execute_code at all, until a CDN fetch of the ~10MB+
        // runtime finishes. execute_code already no-ops gracefully with a
        // one-time console.warn (see the 'execute_code' case) when
        // game.python isn't ready yet, so this is safe: non-Python rooms
        // are unaffected, and a room whose CREATE event needs Python
        // should re-check readiness on a later frame (e.g. a step-event
        // lazy-init guard) rather than assume the very first frame has it.
        window.game.initPython().catch(err =>
            console.error('❌ Python runtime failed to load:', err));
        window.game.start();
        console.log('✅ Game started!');
    } catch (error) {
        console.error('❌ Failed to start:', error);
    }
});
