# Plan: LAN multiplayer **v2** — from "see the other player" to *programming multiplayer games*

Status: **Phases 4–5 DONE (2026-09-02).** Written and executed 2026-09-02.
The full student-facing API — Tier A (shared blackboard: shared variables,
custom messages, player identity, `Réseau` events) and Tier B (networked
instances: `network_spawn` + interpolated ghosts, `sync_instance`,
validated client-owned avatars, named input) — is on `main` and covered
by ~210 tests, including real two-`GameRunner`-over-a-socket coverage for
every replication path. v2 added **zero** core changes on top of v1's
frame-update hook. **Open:** Phase 6 (UDP discovery + built-in French
connect/lobby screen), Phase 7 (HTML5 export parity), Phase 8 (samples
`reseau_1`–`4` + guides). See the checklist near the end.

## Where this comes from

`docs/MULTIPLAYER_LAN_PLAN.md` (v1) is **done**: Phases 0–3 landed
2026-08-15. What exists on `main` today:

- `runtime/extension_hooks.py` — the generic per-frame hook
  (`register_frame_update(func, phase)` with phases `before_step` /
  `after_update`), called unconditionally from `GameRunner.run_game_loop`.
  This is the *only* core-visible trace of multiplayer.
- `extensions/multiplayer_lan/` — a folder extension:
  - `network.py` — `NetworkHost` / `NetworkClient`, TCP, newline-delimited
    JSON, non-blocking, multi-client host, `{"t":"snap","i":[[sync_id,
    x, y, rotation, image_index, visible], ...]}`.
  - `state.py` — per-room state at `room.extension_state["multiplayer_lan"]`,
    `DEFAULT_PORT = 45782`.
  - `handlers.py` — `set_network_mode` action handler + the two frame-update
    functions (`_frame_update_apply_inbound` @ `before_step`,
    `_frame_update_broadcast` @ `after_update`); `PYGM_NET_*` env-var
    fallback.
  - `actions.py` — one action, `set_network_mode` (mode host/client, host
    address, port).
- `runtime/run_game.py` — `--net-host` / `--net-client HOST` /
  `--net-port PORT` flags → `PYGM_NET_*` env vars.
- `samples/multiplayer_lan_1/` — one arrow-key square, no multiplayer
  authoring at all (pure CLI/env-var launch), registered in
  `widgets/welcome_tab.py` and `tools/smoke_run_samples.py`.
- `tests/test_multiplayer_lan.py`, `tests/test_multiplayer_lan_1_sample.py`,
  `tests/test_extension_frame_update_hook.py` — including a real
  two-`GameRunner`-over-`127.0.0.1` loopback test.

**What v1 deliberately does NOT do** (its "Explicitly out of scope"
section), and therefore what "LAN multiplayer game programming" still
needs:

1. The client is a **pure spectator**. Its input never sticks — the next
   snapshot overwrites it. There is no way for a student to make a game
   where *both* players affect the world.
2. Only `x / y / rotation / image_index / visible` sync. No way to share a
   score, a turn counter, a chosen answer, an inventory — none of the
   state a *classroom game* is actually about.
3. No custom events. A student can't react to "a player joined", "a
   message arrived", "the host started the round".
4. No identity. A student can't ask "am I player 1 or player 2?", "how
   many players?", "am I the host?".
5. No spawn/despawn replication. `create_instance` on the host doesn't
   reach clients.
6. No connection UX. Roles come from a command line the student never
   sees; there is no in-game "Host / Join" screen, no server discovery,
   no lobby, no "waiting for players".
7. Desktop only. HTML5 and Kivy exports ignore it.

v2 closes 1–6 for desktop and takes a real run at HTML5 (7). Kivy/Android
stays out of scope (see "Export targets").

## Design principles

- **Extension-only, minimum core.** v1 added exactly one generic core
  hook (`register_frame_update`). v2 adds **zero** — decided in Phase 4.4
  (see "Core changes"). Everything is `extensions/multiplayer_lan/` files
  and `PLUGIN_ACTIONS` / `PLUGIN_EVENTS` (both already supported by
  `events/plugin_loader.py`).
- **Authoritative host, no netcode cleverness.** The host runs the real
  simulation; clients send *intent* (named inputs, message requests) and
  render *interpolated snapshots*. No lockstep, no rollback, no client
  prediction/reconciliation beyond "a client owns its own avatar." On a
  wired school LAN, RTT is ~1 ms — a 20 Hz snapshot stream with 100 ms
  interpolation is smooth and is all this needs. This is the same tier of
  multiplayer as countless simple LAN games and is the right ceiling for
  a teaching tool.
- **Two tiers of student-facing abstraction**, so a 10-year-old and a
  16-year-old both have a level to work at:
  - **Tier A — shared blackboard.** "These variables are the same on
    every machine." Plus custom messages and player identity. Enough to
    build quizzes, turn-based games, draw-together, board games,
    co-op-lite. No notion of "networked instances" at all.
  - **Tier B — networked instances.** Mark an instance synced; the host
    replicates it; a client can *own* its avatar and drive it with input.
    Enough for real-time co-op movement games.
- **Cosmetic runs everywhere, gameplay runs on the host.** The teaching
  mental model, stated in every sample guide: particles, sounds, HUD,
  animations — everywhere. Score changes, collisions that matter, spawns,
  win conditions — `if is_host()`. Samples model the `is_host()` guard
  pattern explicitly.
- **Manual IP always works.** Discovery (UDP broadcast beacon) is a
  convenience. Every connect screen has a "type the host's address" box,
  and every sample guide tells the teacher to write the host IP on the
  board. This is both a reliability fallback (see "School LAN realities")
  and a teachable networking concept.
- **French, accents mandatory** (per `CLAUDE.md`). Action/event
  display names, the built-in connect screen, all sample guides. Sample
  in-game *messages* stay English (student-authored content — per the
  2026-07-20 sample-translation decision); guides are translated.
- **One commit per unit, pushed, full-suite-green gate.** No multi-agent
  workflows. Registry checkboxes in this doc are the resume state.

## School LAN realities (the constraints that shape everything)

These are why the design looks the way it does. None are fixable in
software; the design works *around* them.

- **Wireless AP client isolation.** Many school Wi-Fi APs block
  station-to-station traffic outright — two laptops on the same SSID
  cannot see each other at all, on any port. *Mitigation:* document
  wired labs as the recommended setup; the connect screen shows "this
  machine's IP" and a reachability test so a teacher can diagnose in 10
  seconds; nothing we do makes an isolated AP work.
- **Host firewall prompt on first `bind()`/`listen()`.** Windows
  Defender pops "Allow PyGameMaker to accept connections?" — a student
  without admin rights may not be able to click Allow. *Mitigation:*
  document that the teacher/IT pre-approves the app or opens the port
  once; the connect screen surfaces a clear "hosting failed — firewall?"
  message instead of a silent dead end.
- **Broadcast may be filtered.** UDP broadcast to `255.255.255.255`
  usually crosses a wired subnet but is not guaranteed. *Mitigation:*
  discovery is best-effort; manual IP is the load-bearing path.
- **mDNS/zeroconf unreliable and often an extra dependency.**
  *Mitigation:* we do **not** use zeroconf. Discovery is a hand-rolled
  UDP beacon (a dozen lines, no dependency) or nothing.
- **Chromebooks.** Common in schools; they run the **HTML5 export** in a
  browser, not the desktop app. That is the entire reason HTML5 support
  (Phase 7) is worth attempting despite the WebSocket plumbing cost.
- **Managed/locked Python.** The desktop path must not need pip installs
  for multiplayer — `socket` and `selectors` are stdlib. No `msgpack`, no
  `websockets` library (Phase 7 hand-rolls the WS handshake, or is
  deferred — see that phase).

## Networking model (v2)

Still authoritative-host, extended:

```
        ┌─────────────────────────── HOST (player 0) ──────────────────────────┐
        │  runs the real GameRunner simulation                                 │
        │  owns: shared vars, roster, netid allocation, all non-owned insts    │
        │  each frame @ after_update:  build snapshot → broadcast (TCP, 20Hz)  │
        │  each frame @ before_step:   drain client inbox → apply owned-inst   │
        │                              state, named-input state, msg requests  │
        └───────────────▲───────────────────────────────────────▲─────────────┘
                        │ snapshots                              │ snapshots
             intent ────┤                             intent ───┤
        ┌───────────────┴────────────┐          ┌───────────────┴────────────┐
        │  CLIENT (player 1)         │          │  CLIENT (player 2)         │
        │  before_step: apply latest │          │  ...                       │
        │    snapshot to ghosts      │          │                            │
        │    (interpolated)          │          │                            │
        │  simulates ONLY its own    │          │                            │
        │    owned avatar locally    │          │                            │
        │  after_update: send its    │          │                            │
        │    avatar state + named    │          │                            │
        │    input + msg requests    │          │                            │
        └────────────────────────────┘          └────────────────────────────┘
```

- **Player identity.** Host is player `0`. On connect, the host assigns
  the next free slot (`1`, `2`, …) up to `max_players`. Slot is stable
  for the session; a disconnect frees the slot (v2: not reused mid-session
  — keeps things simple; reconnect is Phase 8).
- **Shared variables.** A flat `name → value` dict the host owns. Values
  restricted to JSON scalars + short lists/dicts of scalars, size-capped.
  Host writes apply immediately and go out in the next snapshot's
  `"shared"` delta. Client writes are *requests* sent to the host; the
  host applies and echoes. Last-write-wins; no locking (a classroom is
  not adversarial). Exposed to students as `global.*` reads (no core
  change — `_parse_value` already resolves `global.x`) plus explicit
  get/set actions.
- **Custom messages.** `send_network_message(event, data)` — reliable
  (TCP), broadcast to all peers (or host-only, param). Delivery fires a
  `network_message` event on every instance that handles it, with
  `global.network_event`, `global.network_data`, `global.network_sender`
  readable. Data is scalar/short-collection only, never `eval`'d.
- **Named inputs (Tier B).** A client maps local keys to named inputs
  (`bind_network_input("jump", vk_space)`), and each frame sends the set
  of currently-held names to the host. The host reads them with the
  `remote_input(player, "jump")` condition. The stock arrow keys + space
  are auto-bound so trivial samples need no binding. This teaches input
  abstraction, which is a genuinely good lesson, and it keeps the wire
  payload tiny and safe (a list of short strings).
- **Owned instances (Tier B).** `set_instance_owner(player)` on a synced
  instance. If `player == player_id()` on this machine, the instance is
  simulated locally and its state is sent *up* to the host, which accepts
  it for owned instances and rebroadcasts. "Client-authoritative for your
  own avatar" — responsive, trivial to implement, and cheating is a
  non-issue in a classroom. Everything else is host-authoritative.
- **Spawn / despawn.** `network_spawn(object, x, y)` is host-only; it
  creates the instance, allocates a netid, and the next snapshot carries
  it in a `"spawn"` list so clients create a ghost. A synced instance
  destroyed on the host goes out in `"despawn"`. Client-side
  `network_spawn` is a no-op with a warning (host owns the world).
- **netids.** The host allocates a monotonic `net_id` per synced
  instance, stored as `inst._net_id`, distinct from `id(inst)` and from
  v1's positional `_sync_id`. Clients keep `net_id → ghost instance`.
  **This replaces v1's `_assign_sync_ids` positional scheme** — positional
  ids break the moment either side spawns/destroys anything, which Tier B
  requires. Migration: v1's sample keeps working because the host still
  assigns ids to the initial room instances in enumeration order; the
  difference is the id now travels in the snapshot (`"o"` object name +
  `"nid"`) instead of being implied by list position.
- **Interpolation.** Clients render ghosts at `render_time = now − 100 ms`,
  lerping between the two most recent snapshots. Applied in the
  `before_step` hook by setting `x/y` to the interpolated value each
  frame. Owned instances are never interpolated (they're local). Default
  delay tunable via `set_sync_rate` / a second param; 100 ms is the
  starting value, tuned against `reseau_1`.

## Student-facing API

New action category **"Réseau"** (display) / `network` (internal). New
event category **"Réseau"**.

### Actions — Tier A (shared blackboard)

| Action | Params | Effect |
|---|---|---|
| `host_game` | `game_name`, `max_players` (dflt 8), `port` (dflt 45782), `show_lobby` (bool) | Start hosting. Sets `global.network_role="host"`, `global.player_id=0`. Optionally shows the built-in connect/lobby screen until the host starts the game. |
| `join_game` | `host` (`"auto"` = show server browser, or an IP), `port` | Connect. Sets role/id from the host's WELCOME. `"auto"` opens the built-in connect screen. |
| `leave_game` | — | Disconnect / stop hosting; clears network globals. |
| `set_shared_var` | `name`, `value` | Write a shared variable (host: immediate; client: request). |
| `get_shared_var` | `name`, `into` (a variable name) | Read a shared variable into a local/instance/global variable. (Avoids needing an expression function.) |
| `send_network_message` | `event` (string), `data` (value), `target` (`all` / `host`) | Broadcast a custom event. |
| `start_networked_game` | — | Host-only: tell all clients to leave the lobby and begin (fires `network_game_started` everywhere). |

### Actions — Tier B (networked instances)

| Action | Params | Effect |
|---|---|---|
| `sync_instance` | `vars` (optional comma list of instance-var names to also replicate) | Mark **this** instance network-synced. Host replicates `x/y/rotation/image_index/visible` + any whitelisted vars. Call in Create. |
| `set_instance_owner` | `player` (number or `<self_player>`) | Assign authority for this instance to a player slot. |
| `network_spawn` | `object`, `x`, `y` | Host-only replicated create. |
| `bind_network_input` | `name` (string), `key` (key constant) | Map a local key to a named input (client side). |
| `set_sync_rate` | `hz` (dflt 20), `interp_ms` (dflt 100) | Tune snapshot rate / interpolation delay. |

### Conditions

| Condition | Meaning |
|---|---|
| `is_host` | This machine is the host. |
| `is_client` | This machine is a client. |
| `network_connected` | A session is live (host with ≥1 client, or a connected client). |
| `remote_input(player, name)` | That player is currently holding that named input (host-side read). |
| `is_instance_owner` | `player_id()` owns this instance (so "my avatar" branches work). |

### Readable globals (no core change — `_parse_value` already does `global.*`)

`global.player_id`, `global.player_count`, `global.network_role`
(`"host"`/`"client"`/`""`), `global.network_event`, `global.network_data`,
`global.network_sender`, plus every shared variable mirrored as
`global.<shared name>` (read-only mirror; writes go through
`set_shared_var`).

### Events (`PLUGIN_EVENTS`)

| Event | Fires on | Notes |
|---|---|---|
| `network_started` | host + client | Session is up. |
| `player_joined` | host (and rebroadcast → all) | `global.network_sender` = new slot. |
| `player_left` | host (and → all) | |
| `network_message` | everyone handling it | `global.network_event/_data/_sender` set. |
| `network_game_started` | everyone | `start_networked_game` fired. |
| `connection_lost` | client | Host went away / socket died. |
| `became_host` | (Phase 8, host-migration) | Deferred. |

## Core changes

**ZERO. Decided in Phase 4.4 (2026-09-02).** v2 adds no core change on top
of v1's frame-update hook.

1. **Expression-name resolver hook — REJECTED, not built.** The idea was a
   generic `extension_hooks.register_expression_names` so `is_host()` /
   `shared("score")` could appear *inside* an arithmetic expression. On
   reading `runtime/action_executor.py`:
   - `is_host` / `is_client` / `network_connected` / `remote_input(...)` /
     `is_instance_owner` are **conditions**, and the extension exposes
     them through the conditional-editor mechanism (`test_instance_count`
     is the model) — no core change.
   - `global.player_id`, `global.player_count`, `global.network_role`, and
     **every shared variable mirrored as `global.<name>`** already resolve
     with zero core change: `_parse_value` / `_get_variable_value` handle
     `global.*` and bare globals today. So `draw_text` at
     `global.score_p1` and a condition `global.player_id == 1` just work.
   - The only thing genuinely lost is a *string-literal-argument* function
     like `shared("score_p1")` mid-expression — and the `global.<name>`
     mirror makes it redundant. Supporting it would mean widening the
     evaluator's `re.match(r'^[\d\s\+\-\*\/\%\(\)\.\,a-zA-Z_]+$', ...)`
     safety whitelist to allow quotes, i.e. a security-surface change to a
     shared, audited subsystem (three evaluators: `_evaluate_expression`,
     `_eval_bool_expression`, HTML5 `gmExpressionValue`) for near-zero
     benefit. Not worth it.
   - `get_shared_var name into var` (Phase 5.2) covers the rare case where
     the `global.` prefix is awkward.
2. **Nothing else.** `PLUGIN_EVENTS`, `PLUGIN_ACTIONS`,
   `PLUGIN_FRAME_UPDATES`, `room.extension_state`, and the built-in
   connect screen (drawn via the existing `PLUGIN_ROOM_RENDERERS` hook, or
   as a plain pygame overlay blitted from a frame-update hook) are all
   already-supported extension surfaces.

The v1 frame-update hook's two phases are sufficient: client snapshot
apply + interpolation + inbound message drain @ `before_step`; host
snapshot build/send + client intent send @ `after_update`.

## Wire protocol v2

Still TCP, still newline-delimited JSON (debuggable in a capture; LAN
bandwidth was never the constraint). All frames `{"t": <type>, ...}`.
4 KB soft cap per frame, 64 KB hard cap (drop + log). Client→host rate
limit: 60 msg/s.

Control (reliable, any time):

- `hello`  `{t, name, proto_ver}` — client → host on connect.
- `welcome` `{t, player_id, player_count, shared, roster, tick}` — host → client.
- `join` / `leave` `{t, player_id, name}` — host → all.
- `msg` `{t, event, data, sender, target}` — custom message, either way.
- `shared_set` `{t, name, value}` — client → host (request) / host → all (echo).
- `input` `{t, held: ["jump","left"]}` — client → host, only on change.
- `bye` `{t}` — graceful disconnect.
- `game_start` `{t}` — host → all.

State (host → all, 20 Hz):

```json
{"t":"snap","tick":1234,"time":98123,
 "shared":{"score_p1":3},                       // delta since last snap
 "spawn":[{"nid":7,"o":"obj_bullet","x":40,"y":60}],
 "i":[{"nid":1,"x":100.0,"y":50.0,"r":0,"f":0,"v":1,"vars":{"hp":3}},
      {"nid":2,"x":220.5,"y":88.0,"r":90,"f":2,"v":1}],
 "despawn":[5,6]}
```

Client → host, once per frame (`after_update`), for its owned instances:

```json
{"t":"own","i":[{"nid":2,"x":221.0,"y":88.0,"r":90,"f":2,"v":1}]}
```

- `state.py` holds the message-type constants and a
  `sanitize_value(v, depth)` used on **every** inbound `data` / `value` /
  `vars` field — scalars, `list`/`dict` of scalars to depth 2, length and
  string-size caps, everything else dropped. Nothing from the wire ever
  reaches `_parse_value` / `eval`.
- A `PROTO_VER` int; `hello`/`welcome` exchange it; mismatch → host
  refuses with a `bye` carrying a reason, client shows "version mismatch".
- Partial-read framing: `NetworkClient`/host per-connection buffer keeps
  bytes until a full `\n`-terminated frame is present; unit-tested by
  feeding one byte at a time.

## Connection UX

- **Built-in connect screen.** `join_game host="auto"` or
  `host_game show_lobby=true` shows an overlay (drawn from a frame-update
  hook, on top of whatever room is loaded, or as its own pseudo-room):
  - client: discovered servers list (name, host IP, players/max) +
    "Adresse :" manual entry + "Se connecter" + "Cette machine : <ip>".
  - host: "En attente de joueurs…", roster, "Démarrer" (calls
    `start_networked_game`).
  - Both: a reachability line and, on failure, a plain-language reason
    ("pare-feu ?", "hôte introuvable", "isolation Wi-Fi ?").
  - Fully French, keyboard + mouse.
- **Discovery beacon.** Host UDP-broadcasts
  `{"pygm":"lan","name":..., "port":..., "players":n, "max":m}` to
  `255.255.255.255:45783` every 1 s on a daemon thread. Client listens on
  a daemon thread, maintains a server list with a 5 s TTL per entry.
  Best-effort; the manual box is always there.
- **Lobby vs. game.** The connect screen handles *connection*. The
  *lobby* (ready-up, team pick, character select) is author-built with
  ordinary actions/events on top of `player_joined` / shared vars — same
  split as raycast (extension provides the renderer, samples build the
  game).
- **IDE "Test Game (2 players)".** A button / menu item next to Test Game
  that launches the current project twice: one `--net-host`, one
  `--net-client 127.0.0.1`, tiled left/right. Env var
  `PYGM_NET_AUTOJOIN=127.0.0.1` lets a second manually-launched Test Game
  auto-join. Its own Phase (7 is HTML5; this is Phase 6).
- **Runner window caption.** Append `[Hôte : 3 joueurs]` /
  `[Client : connecté]` / `[Client : déconnecté]`, same mechanism
  score/lives already use.

## Security & safety (school context)

- Bind to LAN/loopback only; never a routable external bind. No
  STUN/TURN/relay, no internet path — LAN by name and design.
- **No code over the wire.** All inbound `data`/`value`/`vars` go through
  `sanitize_value` (scalars + shallow collections, size-capped). Never
  `eval`'d, never routed to `_parse_value`, never used as a variable
  *name* (shared-var names are validated `^[A-Za-z_][A-Za-z0-9_]*$` so a
  name containing an operator can't reach the expression path — the
  `CLAUDE.md` `_parse_value` landmine).
- Frame size caps (4 KB soft / 64 KB hard); client→host message rate
  limit; `max_players` cap (hard ceiling 16) bounds host per-frame work.
- Player names sanitized (length-capped, control chars stripped, display
  only).
- Host drops a client that floods, sends malformed frames, or stalls a
  broadcast past its 200 ms timeout — a bad client can't take the host
  down (v1 already does this for stalls).
- Sample guides carry a teacher note: ports used (45782 TCP, 45783 UDP),
  "ask IT before using on a managed network", wired-lab recommendation.

## Export targets

- **Desktop (pygame)** — full v2 support. Primary and the bulk of this
  plan.
- **HTML5** — Phase 7, real attempt, may slip to its own plan. A browser
  cannot `accept()` raw TCP, so the **desktop host also opens a WebSocket
  listener** on `port+1`, same frame protocol over both transports; an
  exported HTML5 game connects to `ws://<host>:<port+1>`. The host's WS
  handshake is hand-rolled (~40 lines: parse the `Sec-WebSocket-Key`,
  SHA-1 + base64 the accept, then RFC 6455 frame read/write for text
  frames) so there is **no `websockets` pip dependency**. `engine.js`
  gets an extension client (`export_html5.js`, injected via the
  `// __PYGM_EXTENSION_JS__` marker the raycast Stage C work added). A
  browser client can only be a *client*, never a host. Parity test:
  desktop `sanitize_value` / snapshot builder vs. the JS equivalents over
  a fixed state matrix (structural — no JS engine in CI), matching the
  raycast parity pattern.
- **Kivy / Android** — **out of scope.** School Wi-Fi station isolation +
  Android networking permission friction + no terminal for flags makes
  this low-value until someone has a concrete classroom asking for it.
  `export_kivy.py` stays a placeholder that no-ops the network actions
  (so a Kivy export of a multiplayer project still runs single-player,
  degrading like any missing extension).

## Testing strategy

Everything except "two humans watch two windows" is automatable and must
be automated.

- **Protocol units** (`tests/test_multiplayer_lan_protocol.py`):
  frame codec round-trip, byte-at-a-time partial reads, oversize-frame
  rejection, `sanitize_value` (deep/oversized/non-scalar → dropped),
  shared-var name validation, `PROTO_VER` mismatch handling.
- **Transport loopback** (extend `tests/test_multiplayer_lan.py`):
  host + 2 clients on `127.0.0.1:0`, threads inside one process; join
  assigns distinct slots; `bye` frees a slot; a flooding/malformed client
  is dropped without disturbing the others.
- **Session loopback** (`tests/test_multiplayer_lan_session.py`): two/three
  real headless `GameRunner`s (`SDL_VIDEODRIVER=dummy`), driven frame by
  frame through the actual `before_step`/`after_update` hooks:
  - shared var set on host → readable as `global.x` on both clients within
    N frames;
  - `send_network_message` → `network_message` event fires on the peers
    with correct `global.network_*`;
  - client with an owned avatar + `remote_input` → host sees the input and
    the avatar's authoritative position round-trips back to the other
    client's ghost, converging within tolerance after settle (assert
    *convergence*, not frame-exact — host is authoritative, clients
    interpolate);
  - `network_spawn` on host → ghost appears on clients; host destroy →
    ghost removed;
  - `player_joined` / `player_left` events fire with the right slot.
- **Discovery** (`tests/test_multiplayer_lan_discovery.py`): beacon
  encode/decode; listener parses a directed datagram and ages entries out
  after TTL. (Real broadcast isn't exercised in CI.)
- **Extension ownership** (`tests/test_multiplayer_lan_ownership.py`,
  mirroring `test_export_raycast_ownership.py`): the `network` actions/
  events exist only after `load_all_plugins()`, never in the static
  `ACTION_TYPES` / `EVENT_TYPES`; `game_runner.py` names nothing
  network-specific beyond the two generic hook call sites; `engine.js` /
  `kivy_exporter.py` name no network code (it lives in `export_*.*`).
- **Samples**: each `reseau_*` gets a standalone single-player test (no
  networking triggered) + a two-`GameRunner`-loopback test over the real
  shipped project. Smoke: `tools/smoke_run_samples.py` runs each new
  sample single-player; a dedicated `tools/smoke_run_multiplayer.py`
  launches host + client headless with `PYGM_MAX_FRAMES` and asserts both
  exit 0 and the client saw ≥1 snapshot.
- **CI notes**: loopback sockets on ephemeral ports (`bind :0`) are fine;
  no broadcast; generous timeouts; deterministic thread teardown
  (sentinel + `join(timeout=...)`); mark the multi-`GameRunner` tests
  `slow` if they push suite time.
- **Landmine**: plugin actions/events are invisible to
  `get_action_type()` / `EVENT_TYPES` before `load_all_plugins()` —
  every test loads plugins first.

## Samples (French guides; in-game messages stay English)

1. **`reseau_1` — "Salle partagée".** 2–8 players, each drives a coloured
   square (colour from `player_id`), arrow keys, everyone sees everyone
   move in real time. Teaches `host_game`/`join_game`, the built-in
   connect screen, `sync_instance`, `set_instance_owner` +
   `is_instance_owner`, `player_id` colouring. The Tier B "hello world".
   *(Replaces the spectator-only `multiplayer_lan_1` as the showcase;
   `multiplayer_lan_1` stays as the minimal CLI-launch example.)*
2. **`reseau_2` — "Quiz de classe".** Host cycles through a question list,
   players pick A/B/C/D, host scores, shared scoreboard drawn on every
   screen. Teaches shared variables, `send_network_message`, round flow,
   `if is_host()` gameplay guard. **No fast action — robust on flaky
   Wi-Fi; the best pure classroom fit.**
3. **`reseau_3` — "Récolte en équipe".** Shared world, gems, a team score,
   a monster the host simulates and broadcasts. Teaches `network_spawn` /
   replicated destroy, `is_host()` for collision/scoring,
   host-authoritative enemies with client-owned avatars.
4. **`reseau_4` — "Dessine ensemble"** *(optional / stretch).* Shared
   canvas, each player a cursor, strokes broadcast as `msg` events. Pure
   message-passing, zero instance sync — a gentle Tier A intro; good
   candidate to build *before* `reseau_2` if a simpler first sample is
   wanted.

Each: Welcome-tab entry + `pygm2_fr.ts` display string, `README.md` +
`README.fr.md` guide (guide translated, per the 2026-07-20 decision),
smoke registration, the two test files above.

## Phasing — one commit per unit, push each, full suite green

Sequencing mirrors v1: infra → protocol → session → API → UX → samples,
each phase self-contained.

### Phase 4 — protocol v2 + netid + sanitize (no student-visible change yet)
- [x] 4.1 `state.py`: v2 message-type constants, `PROTO_VER`,
  `sanitize_value`, `is_valid_shared_name`, `sanitize_name`. Unit tests
  in `tests/test_multiplayer_lan_protocol.py` (27). `SNAPSHOT_MSG_TYPE`
  kept as an alias of `MSG_SNAP` so v1 stays green. Landed `d18d2dcf`.
- [x] 4.2a `framing.py` (new, pure — no socket import): `encode_frame`,
  `FrameBuffer` (partial reads, multi-frame chunks, malformed-line skip,
  `FrameOverflow` past the hard cap), `RateLimiter` (token bucket).
  Frame-size caps + `INBOUND_FRAME_RATE` added to `state.py`. Unit tests
  in `tests/test_multiplayer_lan_framing.py` (24). Landed `c06e8432`.
- [x] 4.2b `network.py`: `NetworkHost`/`NetworkClient` are now
  bidirectional and framed on `framing.py`. Host: `poll()` is the single
  pump (accept + per-conn `FrameBuffer` read + `RateLimiter` gate +
  outbuf flush) returning `[(conn_id, frame), ...]` incl. synthetic
  `__open__`/`__close__`; `send(cid, msg)`, `broadcast(msg, exclude=)`,
  `disconnect(cid)`, `connection_ids`; a client past `_MAX_OUTBUF_BYTES`
  or that trips `FrameOverflow` is dropped with a `__close__` reason.
  Client: `send(msg)`, `take_frames()` (all frames, for the session),
  `connected`; `poll()` keeps the exact v1 contract (latest snapshot or
  `None`, non-snapshot frames left for `take_frames`) so `handlers.py`
  and the shipped sample needed **no** change. `PROTO_VER` handshake and
  conn_id→player-slot mapping deferred to Phase 5.1 (they're session
  state, not transport). 6 new loopback tests in
  `tests/test_multiplayer_lan.py` (open event + addr, client→host,
  host→one client, broadcast exclude, oversize-drop, rate-limit bound).
  Full suite **4015 passed, 9 skipped, 0 failed**. Landed `bfc04f40`.
- [x] 4.3 `replication.py` (new, pure): `NetIdAllocator` (monotonic, no
  reuse); `SnapshotBuilder.build(instances, shared, tick, time_ms)` —
  delta-compressed `snap` (only-changed `shared` incl. removed→`None`,
  `spawn` for new netids, `despawn` for gone ones, full `i` position
  list), `reset()` for room change; `SnapshotApplier` — `ingest(frame,
  now)` → `(to_create, to_destroy)` + per-ghost interp buffer
  (`deque(maxlen=12)`) + `shared` mirror + adopt-on-unknown-row safety
  net, `sample(nid, render_time)` → position lerped between the two
  bracketing states (shortest-arc for angle; discrete `f`/`v` hold the
  earlier bracket; clamp before first / hold last after — no
  extrapolation). Caller owns the `render_time = now − interp_delay`
  policy. `tests/test_multiplayer_lan_replication.py` (27). Landed `866965bc`. Note for 5.1: a client joining mid-game misses the
  delta-only `spawn` frames, so the session must send it one full
  snapshot on connect (per-client `SnapshotBuilder` or a full-build
  path) — the applier's adopt path is only a fallback.
- [x] 4.4 Expression-name hook: **rejected — v2 ships with ZERO core
  changes.** `global.player_id` / `global.player_count` /
  `global.network_role` / `global.<shared-var>` already resolve with no
  core change; identity/ownership/`remote_input` are conditions via the
  conditional editor; `get_shared_var … into …` covers the awkward-prefix
  case. Supporting `shared("literal")` mid-expression would need widening
  the eval safety whitelist across three evaluators for redundant benefit.
  Full rationale in "Core changes" above (decided 2026-09-02, doc-only).

### Phase 5 — session layer + student API
- [x] 5.1 `session.py` (new): `NetworkSession` (Tier A core) —
  **GameRunner-agnostic** so it's testable over a real `127.0.0.1`
  socket with no engine. Owns: host slot assignment (host=0, clients 1..N
  up to `max_players`≤16) + roster, `PROTO_VER` handshake (mismatch →
  `bye`), a shared-var blackboard (host-authoritative; client writes are
  `shared_set` requests; values through `sanitize_value`, names through
  `is_valid_shared_name`), custom messages (`send_message`, server-
  assigned sender, `target=all` relayed to other clients), `start_game`,
  and a `take_events()` queue of `(name, *payload)` for the engine glue
  to fire (`player_joined/left`, `network_started/game_started`,
  `network_message`, `connection_lost`). `pump_before_step()` drains
  inbound; `pump_after_update()` sends a host snapshot every `_SNAP_EVERY`
  (≈20 Hz) or immediately on a shared-var change. `NetworkClient.flush()`
  added (one line). INPUT/OWN frames accepted and ignored (Tier B).
  `tests/test_multiplayer_lan_session.py` (16, real loopback). The
  handlers glue + `_frame_update_*` delegation is 5.2, not here. Landed `f3fe6d95`.
- [x] 5.2 + 5.3 (landed together — the handlers glue *is* the event
  dispatcher). `actions.py`: Tier A actions `host_game` / `join_game` /
  `leave_game` / `start_networked_game` / `set_shared_var` /
  `get_shared_var` / `send_network_message`, all French, category
  `Réseau`; `set_network_mode` kept for back-compat. `__init__.py`:
  `PLUGIN_EVENTS` for the six `Réseau` lifecycle events. `handlers.py`:
  `host_game`/`join_game` create a `NetworkSession` in `st["session"]`;
  when present it takes over both frame-update hooks, and
  `_apply_session_state` (before_step) mirrors `player_id` /
  `player_count` / `network_role` / `is_host` / `is_client` /
  `network_connected` + every shared var into `game_runner.
  global_variables`, then drains `session.take_events()` and fires each
  on the room's instances via `execute_event` (setting `network_event` /
  `network_data` / `network_sender` / `network_player_name` first).
  `leave_game` closes the session and clears the network globals.
  **Name/label params (`name`, `into`, `event`, `host`, `player_name`)
  are read literally, NOT through `_parse_value`** — the bare word
  `score` evaluates to `0` (CLAUDE.md landmine); only `value` / `data`
  go through the evaluator. v1 `set_network_mode` + `PYGM_NET_*` path
  untouched (a v2 session and the v1 raw host/client are mutually
  exclusive per room). `state.py` `_fresh()` gains `"session": None`.
  `tests/test_multiplayer_lan_tier_a.py` (17, real loopback through the
  real `ActionExecutor` + `execute_event`). Landed `c395e927`.
- [x] 5.4a `session.py` Tier B **session-layer plumbing** (no engine
  wiring yet): `next_netid()`, `push_local_instances(rows)` (host feeds
  the snapshot its synced-instance rows), `take_ghost_changes()` →
  `(to_create, to_destroy)` accumulated from `SnapshotApplier.ingest`,
  `ghost_ids()` / `ghost_vars(nid)` / `sample_ghost(nid)` (interpolated
  at `now − interp_delay`), `set_sync_rate(hz, interp_ms)` (→ whole
  60 fps frames per snapshot). `_maybe_send_snapshot` now builds with
  the pushed instance rows (still `[]` by default, so Tier A / v1
  unchanged). `tests/test_multiplayer_lan_session.py` +6 (loopback:
  ghost create/despawn, position flow-through, vars, sync-rate).
  Landed `000d80b9`.
- [x] 5.4b **GameRunner ghost wiring + Tier B actions.** `network_spawn`
  (host-only; reuses `execute_create_instance_action` so the host copy is
  a fully normal instance, then tags it with `next_netid()` into
  `st["synced"]`; no-op + debug log on a client). `set_sync_rate` action.
  `_frame_update_broadcast` (host) calls `_collect_synced_rows` (prunes
  destroyed) → `session.push_local_instances`. `_frame_update_apply_inbound`
  (client) calls `_apply_ghosts`: `_spawn_ghost` builds the puppet the
  same way as create-instance but with `_create_fired = True` +
  `_net_ghost = nid` (open Q#3 decision: **create suppressed**), then each
  frame sets x/y/rotation/image_index/visible from
  `session.sample_ghost(nid)` and copies whitelisted `ghost_vars`.
  `leave_game` marks ghosts `to_destroy` and clears `synced`/`ghosts`.
  `tests/test_multiplayer_lan_ghosts.py` (6, **two real GameRunners** over
  `multiplayer_lan_1` on a real socket: spawn→ghost, ghost tracks a moving
  host instance, host destroy→ghost gone, client `network_spawn` no-op,
  create suppressed, `set_sync_rate` tunes the session). Full suite
  **4087 passed, 0 failed**. Landed `c5b34146`.
- [x] 5.4c-1 **`sync_instance` + ownership.** `sync_instance` gives a
  room-placed instance the deterministic netid `<object>#<ordinal>`
  (per-room per-type call order — same on every machine, no
  coordination); host registers it in `st["synced"]`, client in
  `st["synced_local"]`. `set_instance_owner(player)` sets `_net_owner`;
  the owner slot rides on every `i` row (`replication.py` `_Ghost.owner`
  + `SnapshotApplier.ghost_owner`). `is_instance_owner` is a bool-returning
  action (works as an `if_condition` gate via the generic `result is
  False` path — no `_QUESTION_ACTIONS` core edit). **Client-authoritative
  avatar path:** the owning client's `_apply_synced_local` leaves the
  instance under local sim and `_send_owned` reports it up in an `own`
  frame each `after_update`; the host's `_apply_host_own_state` folds
  that into its copy **only if the claiming client is the recorded
  owner** (a client can't grab an instance the host owns — the snapshot's
  `own` field always wins on the client too). `vars` param replicates
  named instance variables. `tests/test_multiplayer_lan_ghosts.py` +6
  (two real GameRunners: matching netid, host-owned drives client copy,
  client-owned drives host copy, `is_instance_owner` both sides, forged
  claim refused, `vars` replicate). Full suite **4093 passed, 0 failed**.
  Landed `156eaa63`.
  **Authoring rule this exposed:** for per-player avatars the *host* must
  assign a non-host slot (`set_instance_owner(global.network_sender)` in
  `player_joined`, or after `network_spawn`) — `set_instance_owner(
  player_id())` in a shared create event can't work, since one shared
  instance can't be owned by two machines at once.
- [x] 5.4c-2 **named input.** `bind_network_input(name, key)` writes
  `st["input_binds"][name] = <pygame key>` (`_name_to_key` resolves
  "space"/"left"/"a"/"lshift"/…); `left`/`right`/`up`/`down`/`space`
  auto-bound when a session starts. Each frame `_poll_held_inputs` reads
  `pygame.key.get_pressed()` for the bound keys; the client sends an
  `input` frame **only on change** (`session.send_input` dedups via
  `_last_input_sent`), the host records its own as player 0
  (`set_local_input`). Host `_on_client_input` stores each slot's held
  set (capped 32×64 chars); `remote_input(player, name)` action returns
  the bool (an `if_condition` gate). `tests/test_multiplayer_lan_ghosts.py`
  +6 (default binds, `bind_network_input`, client input → host
  `remote_input`, release, the action, host-own-input, dedup — the
  wire-path tests monkeypatch `_poll_held_inputs` on the *loaded* module
  since keys can't be held headless). Full suite **4099 passed, 0
  failed**. Landed `14b038ab`.
- [x] 5.5 Back-compat: `set_network_mode` + `PYGM_NET_*` + `run_game.py`
  flags all still work. v2 sessions and the v1 raw host/client are
  mutually exclusive per room; `set_network_mode` no-ops if a session
  owns the room. `multiplayer_lan_1` test + smoke green through all 13
  units of this session. **Phase 5 complete — both tiers usable.**

### Phase 6 — connection UX
- [x] 6.1 `discovery.py` (new, standalone — not wired into `__init__.py`
  until 6.2). `encode_beacon` / `decode_beacon` (clamps/sanitizes every
  field — untrusted UDP input; rejects non-magic, bad port, oversized).
  `DiscoveryBeacon` (host: one daemon thread, `SO_BROADCAST`, sends
  `{m,name,port,players,max}` to `255.255.255.255:45783` every
  `BEACON_INTERVAL`; `update()` refreshes counts; `target`/`interval`
  params for tests). `DiscoveryListener` (client: daemon thread,
  `SO_REUSEADDR`/`SO_REUSEPORT`, 0.5 s socket timeout so `stop()` is
  prompt; `servers()` returns the list newest-first, entries older than
  `ttl` pruned). `tests/test_multiplayer_lan_discovery.py` (12: codec
  round-trip/sanitize/reject, listener collect + TTL prune + garbage
  ignore, beacon→listener integration + `update`, clean idempotent
  `stop`). Landed `8241941a`.
- [x] 6.2a `connect_screen.py` (new, standalone until 6.2b). `ConnectScreen`
  is a **modal** pygame screen (the game freezes while it's up — right UX
  for picking a server, and it sidesteps threading input through the
  frame hook). Client: discovered-server list (from a `DiscoveryListener`),
  digit/`.`/`:`-filtered manual address field, Se connecter, Enter/second-
  click = connect, "Cette machine : <ip>" (`local_ip()` via a UDP-connect
  trick, loopback fallback), Annuler, error line on empty input. Host:
  "En attente de joueurs…" + roster (via injected `roster_fn`), Démarrer,
  per-loop `tick_fn` so joins appear live. `run()` degrades to "just
  connect / just start" when there's no `screen` (headless). Decoupled
  from `NetworkSession` (roster/tick are callables) so it's tested with
  plain surfaces + synthetic events. `tests/test_multiplayer_lan_connect_screen.py`
  (20). Landed `15917e53`.
- [x] 6.2b Wired in. **Every `host_game` starts a `DiscoveryBeacon`**
  (stored in `st["beacon"]`, refreshed with the live player count each
  frame in `_frame_update_broadcast`, stopped by `leave_game`) — so a
  game is discoverable whether or not it shows a lobby. `host_game
  show_lobby=true` also runs the modal host `ConnectScreen`; `"start"` →
  `session.start_game()`, `"cancel"` → full teardown. `join_game
  host="auto"` starts a `DiscoveryListener`, runs the modal client
  `ConnectScreen`, parses `"connect:<ip>:<port>"` → connects there,
  `"cancel"` → no session (game continues single-player), then stops the
  listener. All connect-screen construction goes through
  `_run_connect_flow` (a module fn tests monkeypatch on the *loaded*
  handlers copy); headless runners get `ConnectScreen.run()`'s
  short-circuit. `leave_game` refactored to a single `_teardown` that
  stops session + beacon + listener and clears all `st` keys. `new
  show_lobby` param on `host_game`. `tests/test_multiplayer_lan_ghosts.py`
  +5 (beacon start/stop, `join auto` headless → loopback, `join auto`
  cancel, `show_lobby` start, `show_lobby` cancel). Full suite **4136
  passed, 0 failed**. Landed `6f20ec3d`.
- [ ] 6.3 Runner caption status string.
- [x] 6.3 Runner caption. `_update_network_caption` (called from
  `_apply_session_state`) writes `game_runner.window_caption` — which
  `GameRunner.update_caption` already prepends and caches, so no flicker
  and no core change. Host shows `🌐 Hôte — N joueur(s)`, client
  `🌐 Client — connecté (joueur N)` / `— déconnecté` / `— connexion…`;
  an author-set caption is preserved as the prefix and **restored by
  `leave_game`** (`st["_orig_caption"]`). 2 tests.
- [x] 6.4 (env-var half). `PYGM_NET_AUTOHOST` (any value → this game
  hosts a v2 session) / `PYGM_NET_AUTOJOIN=<ip>` (→ joins as a v2
  client), read in `_resolve_state` *before* the v1 `PYGM_NET_MODE`
  path, so a project with zero multiplayer authoring runs networked
  purely from the environment — the mechanism the IDE "Test Game
  (2 players)" button and quick two-process iteration need. 2 tests
  (real `GameRunner`s: `AUTOHOST` starts a host session; `AUTOJOIN`
  connects to it). **IDE button deferred** — `core/ide_window.py`'s
  Test-Game path has carefully-guarded single-process supervision
  (QTimer poll, stderr temp-file, `closeEvent` teardown); a parallel
  two-launch path is worth doing separately rather than risking that.
  6.3+6.4 landed `7e1d39ad`; full suite **4140 passed, 0 failed**.

### Phase 7 — HTML5 (own plan if it grows)
- [ ] 7.1 Hand-rolled WebSocket listener in the desktop host (`port+1`),
  same frame protocol. No pip dependency. Loopback test with a minimal
  in-test WS client.
- [ ] 7.2 `export_html5.js`: the browser client (client-only), injected
  via the existing extension-JS marker. Structural parity test
  (`sanitize_value` + snapshot shape desktop vs. JS).
- [ ] 7.3 `export_kivy.py`: no-op placeholder for the network actions so a
  Kivy export still runs single-player.
- [ ] 7.4 Wiki: `Network` / `Réseau` page in all 9 languages;
  `tools/gen_action_reference.py` regen picks up the new plugin actions
  automatically; add the strings to `tools/action_ref_i18n.py`.

### Phase 8 — samples + polish
- [x] 8.1 `reseau_1` — "Salle partagée". `obj_ctrl` (invisible, depth
  -100): `game_start` → `network_spawn("obj_person", 320, 240, owner=0)`;
  `player_joined` → `network_spawn(... owner=global.network_sender)` at a
  slot-spaced x; a `draw_text` instruction line. `obj_person`: Step
  guarded by `is_instance_owner` → arrow movement + room clamp, so only
  the owner drives it (everyone else sees the interpolated ghost).
  Registered in `welcome_tab.SAMPLE_PROJECTS` ("Réseau — Salle
  partagée") + `smoke_run_samples.SAMPLES`; the beginner edition
  correctly hides `reseau_*` (same two-machine reasoning as
  `multiplayer_lan_*` — `test_edition_sample_filter` prefix list
  updated). `README.md` + `README.fr.md`. `tests/test_reseau_1_sample.py`
  (4: single-player runs with no session, registration, guides exist,
  two-real-`GameRunner` networked → host spawns owner-0 + owner-1
  avatars, client materialises both). **Engine improvements this needed,
  landed with it:** `network_spawn` gained an `owner` param;
  `_apply_ghosts` **promotes** a host-spawned instance whose snapshot
  `own` == this player into `synced_local` (local sim + `_send_owned`),
  so the "host spawns per-player avatars, each client drives its own"
  pattern works; `is_instance_owner` returns True with no session
  (single-player owns everything). Full suite **4149 passed, 0 failed**;
  `reseau_1` smoke [OK]. `multiplayer_lan_1` kept as the minimal
  CLI-launch example. Landed `d0311633`.
- [ ] 8.2 `reseau_2` (quiz).
- [ ] 8.3 `reseau_3` (co-op).
- [ ] 8.4 `reseau_4` (draw-together) — optional.
- [ ] 8.5 `tools/smoke_run_multiplayer.py` + CI wiring.
- [ ] 8.6 Graceful host-loss: `connection_lost` event + clean client
  teardown. (Host *migration* stays deferred.)
- [ ] 8.7 `CLAUDE.md` "Recent agent-session notes" entry; close this doc.

### Manual QA (cannot be automated — needs displays/machines)
- [ ] Two real machines on a wired school LAN: host + join by typed IP;
  square moves in both windows (`reseau_1`).
- [ ] Discovery beacon actually shows the host in the browser on that LAN.
- [ ] Windows Defender firewall prompt behaviour on a locked-down student
  account; confirm the connect screen's failure message is accurate.
- [ ] `reseau_2` with 4+ real clients; scoreboard stays consistent.
- [ ] HTML5 export (Phase 7) joining a desktop host from a Chromebook.
- [ ] Kivy export of a multiplayer project still runs single-player.

## Open questions

1. **Expression-name hook** — **RESOLVED (Phase 4.4, 2026-09-02): not
   built, v2 stays zero-core-change.** `global.*` reads (including the
   `global.<shared-var>` mirror) + conditions + `get_shared_var` cover
   every case; widening the eval safety whitelist for `shared("literal")`
   isn't worth the security surface. See "Core changes".
2. **First sample**: `reseau_2` (quiz) or `reseau_4` (draw-together) as
   the gentlest Tier A intro? *Recommendation: `reseau_2` — a quiz is the
   single most-requested classroom multiplayer shape; `reseau_4` is a
   nice-to-have.*
3. **Ghost create event**: run a client ghost's `create` event (with an
   `is_ghost` condition available to guard it) or suppress it entirely?
   *Recommendation: suppress by default, expose `is_ghost` so an author
   can opt a cosmetic-only create in.*
4. **Transport**: stay TCP-only, or add UDP for `snap` once there's a
   fast sample to measure jitter against? *Recommendation: TCP-only for
   v2; revisit with real numbers from `reseau_1`/`reseau_3`.*
5. **HTML5 in v2 or its own plan?** *Recommendation: attempt Phase 7 in
   this plan; split it out the moment the WS handshake or parity work
   exceeds ~2 commits.*
6. **Interpolation default**: 75 / 100 / 150 ms? *Start at 100; tune
   against `reseau_1` on real hardware during manual QA.*

## Risks & landmines

- **AP client isolation** — the #1 real blocker; unfixable in software.
  Mitigate with docs, wired-lab guidance, the connect screen's
  this-machine-IP + reachability line. Do not over-promise in guides.
- **Firewall prompt** without admin rights — document teacher/IT
  pre-approval; surface a clear failure reason, never a silent dead end.
- **Threading — the transport is single-threaded (decided in 4.2b).**
  `NetworkHost`/`NetworkClient` use **non-blocking sockets pumped once per
  frame** from the `before_step`/`after_update` hooks, on the game thread.
  No net thread, no queues, no lock — `poll()` accepts/reads/flushes and
  returns; nothing touches `GameRunner` off-thread because nothing runs
  off-thread. The **only** daemon thread in the extension is the Phase 6.1
  UDP discovery beacon listener, which owns just its own server-list dict.
- **Blocking the game loop** — `poll()` + snapshot serialization run
  in-frame, so a huge room could stall a frame. Cap synced instances;
  `SnapshotBuilder` already takes *primitive* dicts, not live instances
  (the session does the cheap extraction); measure with `reseau_3`. A
  slow client can't stall the host — its unwritten output is queued and
  it's dropped past `_MAX_OUTBUF_BYTES`.
- **Determinism drift on clients** — never run gameplay for synced
  non-owned objects on a client; ghosts are apply-only + interpolated.
  Samples state the `is_host()` rule explicitly.
- **Positional `_sync_id` → `net_id`** — v2's netids must travel in the
  snapshot; the moment Tier B spawns anything, v1's "enumeration index"
  scheme is wrong. Keep `multiplayer_lan_1` green through the switch.
- **Partial TCP reads** — classic bug; unit-test the framing buffer with
  byte-at-a-time feeding on both sides.
- **Clock skew** — interpolate by snapshot arrival order / host `tick`,
  never by comparing wall clocks across machines.
- **`_parse_value` eval landmine** — shared-var names validated against a
  strict identifier regex; inbound `data`/`value` never reach
  `_parse_value` or `eval`; any on-screen text in samples stays quoted
  (the `W A S D - Move` → `0` bug).
- **Plugin visibility** — actions/events only exist post
  `load_all_plugins()`; tests and the action-reference generator must
  load plugins first.
- **Kivy `.format()` templates** — N/A while Kivy is a no-op placeholder;
  becomes relevant only if Kivy support is ever picked up. Doubled
  `{{ }}` rule applies then.
- **`git commit -F`** for messages with quotes/parens on the Windows box
  (PowerShell 5.1 mangles inline quoting).
- **Test flakiness** — ephemeral ports, generous timeouts,
  poll-until-converged with a cap, deterministic thread teardown.
- **HTML5 (Phase 7)** — no Node in CI; verify JS by structure/parity +
  ad-hoc Playwright + a manual Chromebook join, matching the
  `engine.js`/raycast precedent.
