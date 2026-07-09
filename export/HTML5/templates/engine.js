
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
    return json.dumps(patch)

def run_draw(inst_id, code, sync_json):
    self = _get_inst(inst_id)
    self._draw_queue = []
    run_code(inst_id, code, sync_json)
    try:
        return json.dumps(self._draw_queue, default=list)
    finally:
        self._draw_queue = []
`;

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
            return JSON.parse(this._runDraw(inst._pyId, code, this._syncJson(inst, game)));
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

function renderDrawCommands(ctx, cmds) {
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
            // Unknown command types are skipped, matching the IDE runtime's
            // dispatch-table behaviour.
        }
    }
}

console.log('🎮 Game engine loading...');

class GameObject {
    constructor(name, x, y, data, objectData) {
        this.name = name;
        // Stable id keying this instance's Python-side state (execute_code)
        this._pyId = ++GameObject._nextInstanceId;
        this.mouse_x = 0;
        this.mouse_y = 0;
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
        // instance's draw queue).
        this.render(ctx);
        if (this.events && this.events.draw) {
            const actions = this.events.draw.actions || [];
            const game = this._gameRef;
            for (const action of actions) {
                if (!action || action.action !== 'execute_code') continue;
                const code = (action.parameters || {}).code || '';
                if (code.trim() && game && game.python && game.python.ready) {
                    renderDrawCommands(ctx, game.python.runDraw(this, code, game));
                }
            }
        }
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
    executeActions(actions, game) {
        let i = 0;
        while (i < actions.length) {
            const action = actions[i];
            const actionType = action.action;
            const params = action.parameters || {};

            // Check if this is a conditional action. test_alignment is a
            // GM question action ("is the instance snapped to the grid?")
            // and gates the following block like any if_*.
            if (actionType && (actionType.startsWith('if_') || actionType === 'test_alignment')) {
                // Check if this conditional uses NESTED then_actions/else_actions (legacy format)
                // If so, delegate to executeAction which handles nested format
                if (params.then_actions || params.else_actions) {
                    this.executeAction(action, game);
                    i++;
                    continue;
                }

                // Otherwise, use SEQUENTIAL block-based format (if_xxx, actions, else_block, actions)
                // Evaluate the condition
                const conditionResult = this.evaluateCondition(action, game);

                // Find the else_block position (if any) and end of block
                let elseIndex = -1;
                let endIndex = actions.length;

                for (let j = i + 1; j < actions.length; j++) {
                    const nextAction = actions[j].action;
                    if (nextAction === 'else_block' || nextAction === 'else_action') {
                        elseIndex = j;
                        break;
                    }
                    // If we hit another if_* at the same level, that's the end
                    if (nextAction && nextAction.startsWith('if_')) {
                        endIndex = j;
                        break;
                    }
                }

                if (conditionResult) {
                    // Condition is TRUE: execute actions from i+1 to elseIndex (or endIndex)
                    const trueEndIndex = elseIndex >= 0 ? elseIndex : endIndex;
                    for (let j = i + 1; j < trueEndIndex; j++) {
                        this.executeAction(actions[j], game);
                    }
                    // Skip past the else block content
                    if (elseIndex >= 0) {
                        i = endIndex;  // Jump to end
                    } else {
                        i = trueEndIndex;
                    }
                } else {
                    // Condition is FALSE: skip to else_block and execute from there
                    if (elseIndex >= 0) {
                        for (let j = elseIndex + 1; j < endIndex; j++) {
                            this.executeAction(actions[j], game);
                        }
                        i = endIndex;
                    } else {
                        // No else block, skip the whole if block
                        i = endIndex;
                    }
                }
            } else if (actionType === 'else_block' || actionType === 'else_action') {
                // Else blocks handled by if_* processing, skip if encountered standalone
                i++;
            } else {
                // Regular action, execute normally
                this.executeAction(action, game);
                i++;
            }
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

                // Check for collision at position
                let hasCollision = false;
                for (const inst of game.instances) {
                    if (inst === this || inst.toDestroy) continue;

                    // Check if positions overlap
                    const myW = this.sprite ? this.sprite.width : 32;
                    const myH = this.sprite ? this.sprite.height : 32;
                    const otherW = inst.sprite ? inst.sprite.width : 32;
                    const otherH = inst.sprite ? inst.sprite.height : 32;

                    if (collCheckX < inst.x + otherW && collCheckX + myW > inst.x &&
                        collCheckY < inst.y + otherH && collCheckY + myH > inst.y) {
                        // Collision detected - check if it matches the filter
                        if (collObjectType === 'any') {
                            hasCollision = true;
                            break;
                        } else if (collObjectType === 'solid' && inst.solid) {
                            hasCollision = true;
                            break;
                        } else if (inst.objectName === collObjectType || inst.name === collObjectType) {
                            hasCollision = true;
                            break;
                        }
                    }
                }

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

            case 'if_question':
                // Show a yes/no dialog and return result
                const question = params.message || params.question || game.translate('yes_or_no');
                return confirm(question);

            default:
                console.warn(`Unknown conditional action: ${actionType}`);
                return false;
        }
    }

    executeAction(action, game) {
        const actionType = action.action;
        const params = action.parameters || {};

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
            case 'test_expression':
                const expr = params.expression || 'false';
                // Would need safe evaluation
                break;

            case 'check_empty':
            case 'check_collision':
                // Collision checking logic
                break;

            case 'repeat':
                const times = params.times || 1;
                const repeatActions = params.actions || [];
                for (let i = 0; i < times; i++) {
                    this.executeActions(repeatActions, game);
                }
                break;

            case 'exit_event':
                return; // Exit current event

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

            case 'set_lives':
                if (params.relative) {
                    game.lives += parseFloat(params.value) || 0;
                } else {
                    game.lives = parseFloat(params.value) || 0;
                }
                console.log(`❤️ Lives: ${game.lives}`);
                // Check for no more lives
                if (game.lives <= 0 && this.events && this.events.no_more_lives) {
                    const noLivesEvent = this.events.no_more_lives;
                    this.executeActions(noLivesEvent.actions || [], game);
                }
                break;

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
                game.running = false;
                alert(game.translate('game_over'));
                break;

            case 'show_highscore':
                alert(`${game.translate('high_score')}: ${game.score}`);
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

            case 'execute_code': {
                // Python code, executed via the Pyodide bridge with the IDE
                // runtime's execute_code semantics. Draw events route through
                // onDraw/runDraw instead (they return a draw-command queue).
                const pyCode = params.code || '';
                if (pyCode.trim() && game.python && game.python.ready) {
                    game.python.runCode(this, pyCode, game);
                } else if (pyCode.trim()) {
                    if (!this._warnedNoPython) {
                        this._warnedNoPython = true;
                        console.warn('execute_code skipped: Python runtime not available');
                    }
                }
                break;
            }

            default:
                console.warn(`Unknown action: ${actionType}`);
        }
    }

    checkCollisionAt(x, y, game) {
        // Get my bounding box dimensions and origin
        const myW = this.sprite ? this.sprite.width : 32;
        const myH = this.sprite ? this.sprite.height : 32;
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
        const myW = this.sprite ? this.sprite.width : 32;
        const myH = this.sprite ? this.sprite.height : 32;
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
    getBoundingBox() {
        const w = this.sprite ? this.sprite.width : 32;
        const h = this.sprite ? this.sprite.height : 32;
        const originX = this.spriteInfo ? this.spriteInfo.origin_x : 0;
        const originY = this.spriteInfo ? this.spriteInfo.origin_y : 0;
        return {
            x: this.x - originX,
            y: this.y - originY,
            width: w,
            height: h
        };
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
            ctx.drawImage(this.sprite, -originX, -originY);
            ctx.restore();
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

        // 4. Step events
        this.instances.forEach(inst => {
            if (!inst.toDestroy) inst.onStep(game);
        });

        // 5. Movement
        this.instances.forEach(inst => {
            if (!inst.toDestroy) inst.processMovement(game);
        });

        // 6. Collision events
        this.instances.forEach(inst => {
            if (!inst.toDestroy) inst.checkCollisions(game);
        });

        // 7. End Step events
        this.instances.forEach(inst => {
            if (!inst.toDestroy) inst.onEndStep(game);
        });

        // 8. Cleanup destroyed instances
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
        ctx.fillStyle = this.bgColor;
        ctx.fillRect(0, 0, this.width, this.height);

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

        // Language for translations (default English, can be set from gameData)
        this.language = 'en';

        // Python bridge for execute_code actions (set up in initPython)
        this.python = null;
        this.pythonError = null;

        this.setupKeyboard();
        this.setupMouse();
        this.loadGame();
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

        const roomsData = gameData.assets.rooms;
        console.log(`Loading ${Object.keys(roomsData).length} rooms...`);

        for (const [roomName, roomData] of Object.entries(roomsData)) {
            const room = new GameRoom(roomData);

            if (room.bgImage && sprites[room.bgImage]) {
                room.backgroundSprite = sprites[room.bgImage];
            }

            const instancesData = roomData.instances || [];
            instancesData.forEach(instData => {
                const objectData = gameData.assets.objects[instData.object_name];
                const inst = new GameObject(
                    instData.object_name,
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
                    // Also store sprite metadata (origin, dimensions) from gameData
                    const spriteMetadata = gameData.assets.sprites[objectData.sprite];
                    if (spriteMetadata) {
                        inst.spriteInfo = {
                            origin_x: spriteMetadata.origin_x || 0,
                            origin_y: spriteMetadata.origin_y || 0,
                            width: spriteMetadata.width || inst.sprite.width,
                            height: spriteMetadata.height || inst.sprite.height
                        };
                    }
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

        if (!this.paused) {
            this.processKeyboard();
            this.processKeyboardRelease();
            if (this.currentRoom) {
                this.currentRoom.step(this);
            }
        }

        if (this.currentRoom) {
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
