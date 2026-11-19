// LAN multiplayer -- HTML5 export, Phase 7.2 (docs/MULTIPLAYER_LAN_V2_PLAN.md).
//
// The browser (HTML5-exported) client half. CLIENT ONLY: a browser page
// cannot accept() incoming connections, so host_game/start_networked_game
// are no-ops here -- only a desktop export can host. This connects to the
// desktop host's hand-rolled WebSocket listener
// (extensions/multiplayer_lan/ws_transport.py, one port above the raw TCP
// port) and speaks the exact same JSON message vocabulary
// (extensions/multiplayer_lan/state.py's MSG_* constants) -- one WebSocket
// text frame per message, no newline framing needed (a WS frame already
// delimits one message).
//
// Scope: full Tier A (shared variables, custom messages, player identity/roster,
// lifecycle events) and Tier B. Other players' network_spawn'd instances render
// and interpolate here exactly like the desktop client; an instance the host
// assigned to THIS player (network_spawn owner=player_id) is promoted from a
// puppet to a locally simulated avatar: its own events run here, this page
// reports its state up to the host every step ("own" frames) and the held named
// inputs ("input" frames, arrows and space by default, bind_network_input to
// change), exactly as the desktop client does. is_instance_owner is true for
// that avatar, and true for everything while not in a session; remote_input is
// host-side only. Still not available in a browser: host_game and
// start_networked_game (a page cannot accept connections), network_spawn
// (host-only), and sync_instance / set_instance_owner (one console warning
// each). The shared-folder actions cannot work in a page at all.

// ---------------------------------------------------------------------------
// Pure helpers: mirror extensions/multiplayer_lan/state.py and replication.py
// exactly enough that tests/test_html5_multiplayer_export.py can pin the
// bounds against the Python source (no JS engine in CI -- see that file).
// ---------------------------------------------------------------------------

const MP_PROTO_VER = 2;
const MP_DEFAULT_PORT = 45782;
const MP_MAX_STR_LEN = 4096;
const MP_MAX_COLLECTION_LEN = 256;
const MP_MAX_VALUE_DEPTH = 3;
const MP_MAX_SHARED_NAME_LEN = 64;
const MP_SHARED_NAME_RE = /^[A-Za-z_][A-Za-z0-9_]*$/;
const MP_BUFFER_LEN = 12;                // per-ghost interpolation sample history
const MP_DEFAULT_INTERP_DELAY_MS = 100;  // matches session.py's _DEFAULT_INTERP_DELAY

function mpIsValidSharedName(name) {
    return typeof name === 'string' && name.length > 0 &&
        name.length <= MP_MAX_SHARED_NAME_LEN && MP_SHARED_NAME_RE.test(name);
}

// Mirrors state.sanitize_value: bounded, JSON-safe, never throws -- an
// unrepresentable value degrades to null in place rather than dropping the
// whole message.
function mpSanitizeValue(value, depth) {
    depth = depth || 0;
    if (value === null || value === undefined) return null;
    const t = typeof value;
    if (t === 'boolean') return value;
    if (t === 'number') return isFinite(value) ? value : null;
    if (t === 'string') return value.length <= MP_MAX_STR_LEN ? value : value.slice(0, MP_MAX_STR_LEN);
    if (depth >= MP_MAX_VALUE_DEPTH) return null;
    if (Array.isArray(value)) {
        return value.slice(0, MP_MAX_COLLECTION_LEN).map(v => mpSanitizeValue(v, depth + 1));
    }
    if (t === 'object') {
        const out = {};
        let count = 0;
        for (const key of Object.keys(value)) {
            if (count >= MP_MAX_COLLECTION_LEN) break;
            if (typeof key !== 'string') continue;
            const k = key.length > MP_MAX_STR_LEN ? key.slice(0, MP_MAX_STR_LEN) : key;
            out[k] = mpSanitizeValue(value[key], depth + 1);
            count += 1;
        }
        return out;
    }
    return null;
}

function mpLerp(a, b, t) { return a + (b - a) * t; }

// Shortest-arc angle interpolation (350 -> 10 goes forward through 0, not
// backward through 180) -- mirrors replication._lerp_angle. JS's % keeps the
// sign of its left operand, unlike Python's, so the double-mod is needed to
// get an always-positive result before shifting back into [-180, 180].
function mpLerpAngle(a, b, t) {
    const d = (((b - a + 180) % 360) + 360) % 360 - 180;
    return a + d * t;
}

// A bare "global.<name>" reference or a numeric/self-attribute expression
// resolves like parseNumParam already does elsewhere in engine.js; anything
// else is passed through as a literal (HTML5's params are narrower than
// desktop's full _parse_value expression support -- see draw_text's own
// resolution a few hundred lines up for the same convention).
function mpResolveValue(value, inst, game) {
    if (typeof value !== 'string') return value;
    const trimmed = value.trim();
    const gmatch = trimmed.match(/^global\.(\w+)$/);
    if (gmatch) {
        return (game.globalVariables && gmatch[1] in game.globalVariables)
            ? game.globalVariables[gmatch[1]] : 0;
    }
    const asNum = parseNumParam(value, inst, null);
    return asNum !== null ? asNum : value;
}

// ---------------------------------------------------------------------------
// MultiplayerClient -- one browser page's connection to a desktop host.
// ---------------------------------------------------------------------------

class MultiplayerClient {
    constructor(game) {
        this.game = game;
        this.ws = null;
        this.connectionLost = false;
        this.playerId = -1;
        this.playerCount = 0;
        this.playerName = 'Joueur';
        this.shared = {};
        this.roster = [];
        this.started = false;
        this.interpDelayMs = MP_DEFAULT_INTERP_DELAY_MS;
        this._events = [];         // queued [name, ...payload]
        this.ghosts = new Map();   // nid -> {obj, vars, owner, samples, inst, local}
        // Named inputs reported to the host: name -> key name (as inputKeyName gives).
        this.bindings = { left: 'left', right: 'right', up: 'up', down: 'down', space: 'space' };
        this._lastInput = null;
        this._lastInputAt = 0;
        this._lastOwnAt = 0;
    }

    // The bound named inputs whose key is held right now.
    heldInputs() {
        const down = new Set();
        const keys = this.game ? this.game.keys : null;
        if (keys) {
            for (const k of Object.keys(keys)) {
                if (keys[k]) down.add(inputKeyName(k));
            }
        }
        const held = [];
        for (const name of Object.keys(this.bindings)) {
            if (down.has(this.bindings[name])) held.push(name);
        }
        return held.sort();
    }

    // Report the held inputs when they change, and again every half second: the host
    // drops frames past about 60 a second, and a change lost that way would leave an
    // input stuck until the next change.
    sendInput(held) {
        const key = held.join(',');
        const now = performance.now();
        if (key === this._lastInput && now - this._lastInputAt < 500) return;
        this._lastInput = key;
        this._lastInputAt = now;
        this._send({ t: 'input', held: held });
    }

    // Report the instances this player owns, up to the host, at most 30 times a second
    // (the game steps 60 times a second, right at the host's inbound ceiling).
    sendOwn(rows) {
        const now = performance.now();
        if (!rows.length || now - this._lastOwnAt < 1000 / 30 - 2) return;
        this._lastOwnAt = now;
        this._send({ t: 'own', i: rows });
    }

    join(host, port, playerName) {
        if (this.ws) return;       // already connecting/connected
        this.playerName = playerName || 'Joueur';
        let ws;
        try {
            // Built by concatenation, never as a literal "ws://..." template
            // -- tests/test_export_html5_extension_syntax.py's brace-balance
            // guard strips "//" as a line comment with no awareness of
            // string/template context, so a raw "//" anywhere in this file's
            // source (even inside quotes) desyncs its bracket count.
            ws = new WebSocket('ws:' + '/' + '/' + host + ':' + port);
        } catch (e) {
            console.error('multiplayer: could not open a WebSocket to', host, port, e);
            return;
        }
        this.ws = ws;
        ws.onopen = () => {
            this._send({ t: 'hello', name: this.playerName, proto_ver: MP_PROTO_VER });
        };
        ws.onmessage = (ev) => this._onMessage(ev);
        ws.onclose = () => this._flagLost('connection closed');
        ws.onerror = () => { /* onclose always follows; nothing extra to do here */ };
    }

    leave() {
        if (this.ws) {
            try { this.ws.close(); } catch (e) { /* already closing/closed */ }
        }
        this._teardownGhosts();
        this.ws = null;
        this.connectionLost = false;
        this.playerId = -1;
        this.playerCount = 0;
        this.shared = {};
        this.roster = [];
        this.started = false;
    }

    get connected() {
        return this.playerId >= 0 && !this.connectionLost;
    }

    _send(obj) {
        if (this.ws && this.ws.readyState === WebSocket.OPEN) {
            try { this.ws.send(JSON.stringify(obj)); } catch (e) { /* dropped, same as a stalled desktop peer */ }
        }
    }

    setShared(name, value) {
        if (!mpIsValidSharedName(name)) return;
        // A client write is only a request up to the host -- it is NOT
        // mirrored locally here, matching session.py's NetworkSession
        // (the host's next snapshot echoes it back once accepted).
        this._send({ t: 'shared_set', name, value: mpSanitizeValue(value) });
    }

    getShared(name, fallback) {
        return Object.prototype.hasOwnProperty.call(this.shared, name) ? this.shared[name] : fallback;
    }

    sendMessage(event, data, target) {
        target = (target === 'all' || target === 'host') ? target : 'all';
        this._send({
            t: 'msg', event: String(event).slice(0, MP_MAX_STR_LEN),
            data: mpSanitizeValue(data), sender: this.playerId, target,
        });
    }

    takeEvents() {
        const out = this._events;
        this._events = [];
        return out;
    }

    _queueEvent(name, ...payload) {
        this._events.push([name, ...payload]);
    }

    _flagLost(reason) {
        if (this.connectionLost) return;
        this.connectionLost = true;
        console.log('multiplayer: connection lost (' + reason + ')');
        this._queueEvent('connection_lost', reason);
        this._teardownGhosts(true);
    }

    _onMessage(ev) {
        let msg;
        try { msg = JSON.parse(ev.data); } catch (e) { return; }
        if (!msg || typeof msg !== 'object' || !msg.t) return;
        switch (msg.t) {
            case 'welcome':
                this.playerId = typeof msg.player_id === 'number' ? msg.player_id : -1;
                this.playerCount = typeof msg.player_count === 'number' ? msg.player_count : 1;
                this.shared = {};
                for (const key of Object.keys(msg.shared || {})) {
                    this.shared[key] = mpSanitizeValue(msg.shared[key]);
                }
                this.roster = Array.isArray(msg.roster) ? msg.roster : [];
                this._queueEvent('network_started');
                break;
            case 'join':
                this.playerCount += 1;
                this._queueEvent('player_joined', msg.player_id, msg.name || '');
                break;
            case 'leave':
                this.playerCount = Math.max(1, this.playerCount - 1);
                this._queueEvent('player_left', msg.player_id, msg.name || '');
                break;
            case 'shared_set':
                if (mpIsValidSharedName(msg.name)) {
                    this.shared[msg.name] = mpSanitizeValue(msg.value);
                }
                break;
            case 'msg':
                this._queueEvent('network_message', String(msg.event || ''),
                    mpSanitizeValue(msg.data), typeof msg.sender === 'number' ? msg.sender : -1);
                break;
            case 'snap':
                this._ingestSnapshot(msg);
                break;
            case 'game_start':
                if (!this.started) {
                    this.started = true;
                    this._queueEvent('network_game_started');
                }
                break;
            case 'bye':
                this._flagLost(msg.reason || '');
                break;
            // 'input' / 'own' are client->host only; a browser never
            // receives them back, so no case is needed here.
        }
    }

    // -- Tier B: ghost viewing (receive-only) ----------------------------

    _ingestSnapshot(frame) {
        for (const key of Object.keys(frame.shared || {})) {
            this.shared[key] = mpSanitizeValue(frame.shared[key]);
        }
        for (const spec of frame.spawn || []) {
            const nid = spec.nid;
            if (nid === undefined || nid === null || this.ghosts.has(nid)) continue;
            this._createGhost(nid, spec.o || '');
        }
        for (const nid of frame.despawn || []) {
            const g = this.ghosts.get(nid);
            if (g) {
                if (g.inst) g.inst.toDestroy = true;
                this.ghosts.delete(nid);
            }
        }
        const now = performance.now();
        for (const row of frame.i || []) {
            const nid = row.nid;
            if (nid === undefined || nid === null) continue;
            let g = this.ghosts.get(nid);
            if (!g) {
                // A position row for a ghost never explicitly spawned (joined
                // mid-game, missed the spawn frame) -- adopt it, matching
                // replication.SnapshotApplier.ingest.
                g = this._createGhost(nid, row.o || '');
            }
            g.samples.push([
                now, Number(row.x) || 0, Number(row.y) || 0,
                Number(row.r) || 0, row.f || 0, row.v === undefined ? true : !!row.v,
            ]);
            if (g.samples.length > MP_BUFFER_LEN) g.samples.shift();
            if (row.vars && typeof row.vars === 'object') {
                Object.assign(g.vars, row.vars);
            }
            if ('own' in row) g.owner = row.own;
        }
    }

    _createGhost(nid, objectName) {
        const g = { obj: objectName, vars: {}, owner: null, samples: [], inst: null };
        this.ghosts.set(nid, g);
        this._spawnGhostInstance(nid, g);
        return g;
    }

    _spawnGhostInstance(nid, g) {
        if (!this.game || !this.game.currentRoom) return;
        const objectData = (this.game.gameData.assets.objects || {})[g.obj];
        if (!objectData) {
            console.warn('multiplayer: ghost object not in this project:', g.obj);
            return;
        }
        const inst = new GameObject(g.obj, 0, 0, {}, objectData);
        inst._gameRef = this.game;
        inst.xstart = 0;
        inst.ystart = 0;
        inst._startX = 0;
        inst._startY = 0;
        if (objectData.sprite && this.game.sprites[objectData.sprite]) {
            inst.sprite = this.game.sprites[objectData.sprite];
            inst.spriteInfo = this.game.makeSpriteInfo(objectData.sprite);
        }
        // A ghost is driven entirely by snapshots, not its own authored
        // logic -- its create event never runs (matches handlers.py's
        // _spawn_ghost / inst._create_fired = True on desktop).
        inst._pendingCreateEvent = false;
        inst._netGhost = nid;
        this.game.currentRoom.instances.push(inst);
        g.inst = inst;
    }

    sampleGhost(nid, renderTime) {
        const g = this.ghosts.get(nid);
        if (!g || !g.samples.length) return null;
        const buf = g.samples;
        if (buf.length === 1 || renderTime <= buf[0][0]) {
            const s = buf[0];
            return [s[1], s[2], s[3], s[4], s[5]];
        }
        const last = buf[buf.length - 1];
        if (renderTime >= last[0]) {
            return [last[1], last[2], last[3], last[4], last[5]];
        }
        for (let i = 0; i < buf.length - 1; i++) {
            const s0 = buf[i], s1 = buf[i + 1];
            if (s0[0] <= renderTime && renderTime <= s1[0]) {
                const span = s1[0] - s0[0];
                const alpha = span <= 0 ? 0 : (renderTime - s0[0]) / span;
                return [
                    mpLerp(s0[1], s1[1], alpha),
                    mpLerp(s0[2], s1[2], alpha),
                    mpLerpAngle(s0[3], s1[3], alpha),
                    s0[4],      // discrete: hold the earlier bracket
                    s0[5],
                ];
            }
        }
        return [last[1], last[2], last[3], last[4], last[5]];   // unreachable, but safe
    }

    // keepLocal: a lost host never sends another snapshot, so the puppets of other
    // players go, but this player's own avatar keeps running single player.
    _teardownGhosts(keepLocal) {
        for (const [nid, g] of Array.from(this.ghosts.entries())) {
            if (keepLocal && g.local) continue;
            if (g.inst) g.inst.toDestroy = true;
            this.ghosts.delete(nid);
        }
    }
}

function _mpClient(game) {
    if (!game._multiplayerClient) game._multiplayerClient = new MultiplayerClient(game);
    return game._multiplayerClient;
}

function _mpFireEvent(game, eventName) {
    if (!game.currentRoom) return;
    for (const inst of game.currentRoom.instances) {
        if (inst.toDestroy) continue;
        inst.triggerEvent(eventName);
    }
}

// -- per-frame: mirror identity/shared globals, fire queued events, --------
// -- interpolate ghosts. A no-op every frame until join_game is called. ----

registerFrameUpdate(function mpFrameUpdate(game) {
    const client = game._multiplayerClient;
    if (!client) return;
    const gv = game.globalVariables;
    gv.player_id = client.playerId;
    gv.player_count = client.playerCount;
    gv.network_role = 'client';
    gv.is_host = 0;
    gv.is_client = 1;
    gv.network_connected = client.connected ? 1 : 0;
    for (const key of Object.keys(client.shared)) gv[key] = client.shared[key];

    for (const [name, ...payload] of client.takeEvents()) {
        if (name === 'network_message') {
            gv.network_event = payload[0];
            gv.network_data = payload[1];
            gv.network_sender = payload[2];
        } else if (name === 'player_joined' || name === 'player_left') {
            gv.network_sender = payload[0];
            gv.network_player_name = payload[1];
        } else if (name === 'connection_lost') {
            gv.network_connected = 0;
        }
        _mpFireEvent(game, name);
    }

    const renderTime = performance.now() - client.interpDelayMs;
    const ownRows = [];
    for (const [nid, g] of client.ghosts) {
        if (!g.inst) continue;
        g.inst._netOwner = (g.owner === null || g.owner === undefined) ? 0 : g.owner;
        if (client.connected && g.owner === client.playerId) {
            // Mine: promoted from a puppet to a locally simulated avatar. Its
            // own events move it; this page is the authority for it now.
            g.local = true;
            ownRows.push({
                nid: nid, x: g.inst.x, y: g.inst.y, r: g.inst.rotation || 0,
                f: g.inst.image_index || 0, v: g.inst.visible !== false,
            });
            continue;
        }
        if (g.local) continue;           // lost the host: still mine, keep it running
        const pos = client.sampleGhost(nid, renderTime);
        if (!pos) continue;
        const [x, y, r, f, v] = pos;
        g.inst.x = x;
        g.inst.y = y;
        g.inst.rotation = r;
        g.inst.image_index = f;
        g.inst.visible = v;
        for (const key of Object.keys(g.vars)) {
            const val = g.vars[key];
            if (typeof val === 'number' || typeof val === 'string' || typeof val === 'boolean') {
                g.inst[key] = val;
            }
        }
    }
    if (client.connected) {
        client.sendOwn(ownRows);
        client.sendInput(client.heldInputs());
    }
});

// -- actions -----------------------------------------------------------

registerExtensionAction('join_game', (inst, params, game) => {
    const client = _mpClient(game);
    if (client.ws) return;   // already networked
    const rawHost = params.host;
    const host = (rawHost !== undefined && rawHost !== null && rawHost !== '') ? String(rawHost) : '127.0.0.1';
    if (host === 'auto') {
        console.warn('multiplayer: join_game(host="auto") LAN discovery is not '
            + 'available in the HTML5 export -- pass the host address explicitly.');
        return;
    }
    const rawPort = parseNumParam(params.port, inst, MP_DEFAULT_PORT);
    const port = Math.trunc(rawPort) + 1;   // the desktop host's WS listener is one port above the raw TCP one
    const rawName = params.player_name;
    const playerName = (rawName !== undefined && rawName !== null && rawName !== '') ? String(rawName) : 'Joueur';
    client.join(host, port, playerName);
});

registerExtensionAction('leave_game', (inst, params, game) => {
    if (game._multiplayerClient) game._multiplayerClient.leave();
});

registerExtensionAction('host_game', () => {
    console.warn('multiplayer: host_game is not available in the HTML5 export '
        + '-- a browser page cannot accept incoming connections. Host from a desktop export instead.');
});

registerExtensionAction('start_networked_game', () => {
    // host-only on every target; a no-op here for the same reason as host_game.
});

registerExtensionAction('set_shared_var', (inst, params, game) => {
    const client = game._multiplayerClient;
    if (!client || !params.name) return;
    client.setShared(params.name, mpResolveValue(params.value, inst, game));
});

registerExtensionAction('get_shared_var', (inst, params, game) => {
    if (!params.into) return;
    const client = game._multiplayerClient;
    game.globalVariables[params.into] = client ? client.getShared(params.name, 0) : 0;
});

registerExtensionAction('send_network_message', (inst, params, game) => {
    const client = game._multiplayerClient;
    if (!client || !params.event) return;
    client.sendMessage(params.event, mpResolveValue(params.data, inst, game), params.target);
});

registerExtensionAction('bind_network_input', (inst, params, game) => {
    const name = params.name ? String(params.name).trim() : '';
    if (!name) return;
    let key = String(params.key || '').trim().toLowerCase();
    if (key.indexOf('k_') === 0) key = key.slice(2);
    const aliases = { return: 'enter', ctrl: 'control', esc: 'escape' };
    _mpClient(game).bindings[name] = aliases[key] || key;
});

registerExtensionAction('set_sync_rate', (inst, params, game) => {
    // Only the interpolation delay matters to a client; the snapshot rate is the host's.
    const ms = Number(params.interp_ms);
    if (isFinite(ms) && ms >= 0) _mpClient(game).interpDelayMs = ms;
});

// True for the avatar the host assigned to this player. With no session you own
// everything, so control logic guarded by it still runs single player.
registerExtensionCondition('is_instance_owner', (inst, params, game) => {
    const client = game._multiplayerClient;
    if (!client || !client.ws) return true;
    return inst._netOwner !== undefined && inst._netOwner === client.playerId;
});

// Host-side question: a browser never hosts, so nobody is ever reported here.
registerExtensionCondition('remote_input', () => false);

const _mpUnsupportedWarned = new Set();
function _mpWarnOnce(name, why) {
    if (_mpUnsupportedWarned.has(name)) return;
    _mpUnsupportedWarned.add(name);
    console.warn('multiplayer: ' + name + ' is not available in the HTML5 export. ' + why);
}
for (const name of ['network_spawn', 'sync_instance', 'set_instance_owner']) {
    registerExtensionAction(name, () => _mpWarnOnce(name,
        'Only the host creates and assigns networked instances; a browser player '
        + 'controls the avatar the host gave it.'));
}
// The shared-folder extension: a page cannot read or write a shared folder.
for (const name of ['host_game_files', 'join_game_files', 'leave_game_files',
    'set_shared_var_files', 'get_shared_var_files', 'send_network_message_files', 'end_turn']) {
    registerExtensionAction(name, () => _mpWarnOnce(name,
        'A browser page cannot use a shared folder; use a desktop or Android export for file exchange.'));
}
