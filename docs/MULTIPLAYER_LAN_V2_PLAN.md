# Plan: LAN multiplayer **v2** — from "see the other player" to *programming multiplayer games*

Status: **Phases 4–7 and 8.1/8.2/8.3/8.5/8.6 DONE** (7.4's wiki docs are
complete for English + French; 7 more languages are explicitly deferred
incremental work — see 7.4's own entry). Written and
mostly executed 2026-09-02. The full student-facing API — Tier A (shared
blackboard: shared variables, custom messages, player identity, `Réseau`
events) and Tier B (networked instances: `network_spawn` + interpolated
ghosts, `sync_instance`, validated client-owned avatars, named input) —
is on `main` for desktop, plus UDP discovery + the built-in French
connect/lobby screen (Phase 6), a hand-rolled WebSocket listener so the
host also accepts HTML5-exported browser clients (7.1) with a browser-
side client that joins and plays Tier A + views Tier B ghosts (7.2),
three samples (`reseau_1`–`3`, 8.1–8.3), a real two-subprocess smoke tool
(8.5), and graceful host-loss teardown (8.6). Covered by ~500 tests,
including real two-`GameRunner`-over-a-socket coverage for every
replication path, a real-socket WebSocket protocol-conformance suite,
and HTML5 export structural/parity coverage. v2 added **one** small core
fix (`_eval_bool_expression` gained `global.X` support — a previously-
undiscovered bug the whole "if is_host(): ..." authoring pattern depends
on) plus **one** small generic HTML5-engine addition
(`registerFrameUpdate`, a third extension registry alongside Stage C's
room-renderer/action registries) on top of v1's frame-update hook; the
transport and session layers remain zero-core-change extension code.
**Open:** 7.4's remaining 7 wiki languages (DE/UK/RU/IT/ES/PT/SL, incremental
follow-up work, not blocking), 8.4 (`reseau_4`, optional), 8.7 (close this
doc). See the checklist near the end.

## Where this comes from

The v1 plan (done: Phases 0–3 landed 2026-08-15; its doc was removed
2026-09-02 in a docs cleanup, recoverable via `git log` if ever needed)
produced what exists on `main` today:

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

**ZERO net-new extension surface. One small, real bug fix landed 2026-09-02
while authoring `reseau_2` (Phase 8.2) — see the correction below.** v2
adds no *new extension mechanism* on top of v1's frame-update hook, but
one of this section's own original claims (from Phase 4.4) turned out to
be false and needed a genuine `runtime/action_executor.py` fix, not just
a documentation correction.

**Correction (2026-09-02): "a condition `global.player_id == 1` just
works" was WRONG for `if_condition`'s "expression" type.** Verified
empirically (not just re-read) while wiring `reseau_2`'s host/client
gating: `global.is_host == 1` as an `if_condition` "expression" silently
evaluated to `False` every time — `_eval_bool_expression` is a real
Python `eval()`, and `global` is a reserved keyword, so `global.X` is a
`SyntaxError` there regardless of the namespace (caught by the function's
own broad `except Exception`, logged, never surfacing to the author).
This is a *different* evaluator from `_parse_value`/`_evaluate_expression`
(action parameter VALUES — `set_variable`'s `value`, `network_spawn`'s
`x`/`y`), whose dotted-global handling is separate and was already
correct; the false claim below conflated the two. No existing sample
before this fix ever exercised the combination — `reseau_1`'s own
`if_condition` expressions are all bare instance-scope names (`"x < 16"`),
never `global.*`. Fixed with a regex substitution (`global.NAME` →
`_global.get('NAME', 0)`, a namespace key bound to
`game_runner.global_variables`) applied only inside
`_eval_bool_expression`, right before `eval()` — matches `_parse_value`'s
own missing-global default of 0, and is not a security-surface change
(that function was already a full Python `eval()` with no quote-based
whitelist to weaken, unlike the arithmetic evaluators the rejected-hook
reasoning below is actually about). `tests/
test_eval_bool_expression_global_vars.py` (10 tests). Full suite 4154 →
4164 passed, 0 failed. This unblocks the exact "if is_host(): gameplay
guard" pattern this whole plan's Design Principles section describes as
the central authoring idiom — every future sample needs it, not just
`reseau_2`.

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
- [x] 7.1 Hand-rolled WebSocket listener in the desktop host (`port+1`),
  same frame protocol. No pip dependency. Loopback test with a minimal
  in-test WS client. **DONE 2026-09-02.** New `ws_transport.py`:
  `WebSocketHost` (RFC 6455 handshake — parses `Sec-WebSocket-Key`,
  computes `Sec-WebSocket-Accept` via SHA-1+base64 — then unfragmented
  text/binary frame read/write, ping/pong/close handling) mirrors
  `NetworkHost`'s exact `start`/`poll`/`send`/`broadcast`/`disconnect`/
  `close`/`connection_ids`/`_listen_sock` surface, so it drops into
  `session.py` with no change to `_host_drain`'s dispatch logic. `DualHost`
  composes the original raw-TCP `NetworkHost` with a `WebSocketHost`,
  offsetting WS connection ids by `1_000_000_000` so `poll()`/`send()`/
  `broadcast()` see one merged id space — `NetworkSession.start()` now
  constructs a `DualHost` when hosting instead of a bare `NetworkHost`.
  The WS listener binds `port+1` for an explicit port (matching
  `DISCOVERY_PORT`'s own "one above" convention — no real collision, TCP
  and UDP are different socket namespaces even at the same port number);
  with the ephemeral `port=0` tests use, it asks the OS for its own
  independent free port instead of `raw_bound_port + 1` (which could just
  as easily already be taken). A WS bind failure is caught and logged,
  disabling browser support for *that* session rather than failing
  hosting outright — the raw-TCP side (every existing sample) is
  unaffected. `CONN_OPENED` fires only once the upgrade handshake
  completes, not on raw accept, since a browser can't send/receive real
  frames before then. New `tests/test_multiplayer_lan_ws_transport.py`
  (12 tests): a pure codec layer checked against RFC 6455's own published
  test vector (`accept("dGhlIHNhbXBsZSBub25jZQ==") ==
  "s3pPLMBiTxaQ9kYGzzhZRbK+xOo="`) plus round-trip/overflow/partial-frame
  cases; `WebSocketHost` driven directly over a real socket by a **from-
  scratch, independently-written** minimal WS client in the test file
  (its own HTTP request text, its own frame masking/parsing — not reusing
  `ws_transport.py`'s encode/decode helpers, so this is a real protocol-
  conformance check, including an assertion the server never masks its
  own frames per spec); `DualHost` merging a raw `NetworkClient` and the
  minimal WS client under one id space with a shared broadcast; and a
  `NetworkSession(mode="host")` end-to-end hello/welcome exchange over a
  real WS connection — the plan's own "loopback test with a minimal
  in-test WS client." Full suite 4201 → 4213 passed, 0 failed.
- [x] 7.2 `export_html5.js`: the browser client (client-only), injected
  via the existing extension-JS marker. Structural parity test
  (`sanitize_value` + snapshot shape desktop vs. JS). **DONE 2026-09-02.**
  New `extensions/multiplayer_lan/export_html5.js`: a `MultiplayerClient`
  class wrapping the browser's native `WebSocket` (fully event-driven —
  `onopen`/`onmessage`/`onclose`, no per-frame socket pump needed the way
  desktop's non-blocking sockets require), connecting to the desktop
  host's Phase-7.1 WS listener at `ws://<host>:<port+1>`. Implements full
  Tier A (`join_game`/`leave_game`/`set_shared_var`/`get_shared_var`/
  `send_network_message`, identity globals, the `Réseau` lifecycle
  events via a new `inst.triggerEvent(name)` generic dispatch already
  used for alarms) and Tier B ghost **viewing** (spawn/despawn/
  interpolate other players' `network_spawn`'d/`sync_instance`'d
  instances, byte-for-byte the same lerp/lerp-angle math as
  `replication.py`). **Scoped out, deliberately** (see the file's own
  docstring): a browser page can't host (`host_game`/
  `start_networked_game` warn and no-op — a browser can't `accept()`
  connections) and can't yet register/own a synced instance itself
  (`sync_instance`/`set_instance_owner`/`bind_network_input`/
  `set_sync_rate` warn once and no-op; `is_instance_owner`/`remote_input`
  need no code at all — they already fall through to `evaluateCondition`'s
  existing `default: return false` for an unrecognized condition action,
  since HTML5 has no per-condition extension registry yet) — full
  browser-owned-avatar control needs a periodic "own" frame report this
  pass didn't build.
  - **New generic engine.js infrastructure**: `registerFrameUpdate(fn)` /
    `runExtensionFrameUpdates(game)`, a third extension registry
    alongside Stage C's `registerRoomRenderer`/`registerExtensionAction`,
    called once per `gameLoop()` iteration right before
    `currentRoom.step()`. Needed because ghost interpolation is
    continuous over time (must update every rendered frame), not just in
    response to a WS message — the one thing a purely event-driven
    WebSocket client can't cover on its own.
  - **Landmine hit and fixed**: `tests/test_export_html5_extension_syntax.py`
    (a repo-wide guard against a broken extension JS silently blacking
    out every HTML5 export) does brace-balance checking via a regex
    comment-stripper with **no string/template awareness** — a literal
    `` `ws://${host}:${port}` `` template literal's `//` was
    misinterpreted as starting a line comment, truncating everything
    after it and desyncing the bracket count for the *whole file*.
    Fixed by building the URL through concatenation
    (`'ws:' + '/' + '/' + host + ':' + port`) so no two `/` characters
    are ever adjacent in the raw source — worth remembering for any
    future JS carrying a `://` literal in this repo's export files.
  - `tests/test_html5_multiplayer_export.py` (18 tests): the
    `registerFrameUpdate` addition and its call site are bracket-balanced
    and ordered before the room step; every client-only/host-only/
    unsupported action is registered with the right warn-vs-silent
    behaviour; `join_game` connects one port above the raw port and
    refuses `host="auto"` (no LAN discovery in a browser) instead of
    connecting somewhere wrong; ghost interpolation updates position/
    rotation/frame/visibility and never fires a ghost's create event;
    three-way parity pins (`MAX_STR_LEN`/`MAX_COLLECTION_LEN`/
    `MAX_VALUE_DEPTH`/`MAX_SHARED_NAME_LEN`/`PROTO_VER`/`DEFAULT_PORT`/
    the shared-name regex/the `MSG_*` wire strings) extracted from the JS
    source by regex and compared against the live `state.py` constants,
    so a future drift on either side fails a test instead of only
    surfacing in a manual browser session; a real `HTML5Exporter().export()`
    of `reseau_3` (the sample that actually authors `host_game`/
    `join_game`/`network_spawn`, unlike `reseau_1` which launches purely
    via env vars) embeds the multiplayer JS and every authored action
    name survives the JSON round-trip. Full suite 4213 → 4234 passed, 0
    failed.
  - **Still needs a browser**: nobody has watched an exported HTML5 game
    actually join a desktop host and render another player's ghost —
    same standing caveat as every other HTML5/Kivy export arc in this
    repo (no JS engine in CI). Worth a manual pass alongside the plan's
    other Manual QA items.
- [x] 7.3 `export_kivy.py`: no-op placeholder for the network actions so a
  Kivy export still runs single-player. **DONE 2026-09-02 — smaller than
  planned, real blocker found by testing rather than assumed.** Exported
  `reseau_1`/`2`/`3` via `KivyExporter` and compiled every generated `.py`
  file for real before writing any code: the 15 network actions
  (`host_game`/`join_game`/`set_shared_var`/`network_spawn`/...) already
  fall through cleanly to `code_generator.py`'s existing generic
  unsupported-action fallback (`pass  # TODO: <name>`, tracked in
  `get_unsupported_actions()` and surfaced in a real post-export warning
  naming them) — that's a correctly-scoped no-op placeholder already, and
  a dedicated `extensions/multiplayer_lan/export_kivy.py` mimicking it
  with silent `ACTION_CODEGEN` entries would only *hide* the limitation
  from the exporting teacher, which this repo's "stop lying to users"
  stance argues against. **What actually crashed the export**: reseau_3's
  `obj_ctrl` authors `if global.network_connected != 1: ...` (the
  `global.X` mirror Phase 4.4 gave desktop/HTML5) — `global` is a
  reserved Python keyword, so `global.network_connected != 1` isn't even
  parseable Python; `code_generator._resolve_instance_names`'s
  `ast.parse()` raised `SyntaxError` and (silently) returned the literal
  unparseable text unchanged, landing verbatim in the generated file: `if
  global.network_connected != 1:` is a real `SyntaxError`, so the WHOLE
  exported module failed to import — not a "runs weird", a total crash.
  Not multiplayer-specific either: ANY project authoring a `global.X`
  condition hits this on Kivy. Fixed with a `_strip_global_refs` regex
  pre-pass (`\bglobal\.[A-Za-z_]\w*\b` → literal `0`) ahead of
  `_resolve_instance_names`'s `ast.parse` call — the single shared entry
  point all 9 of its call sites go through. Kivy has no global-variable
  storage at all (unlike desktop's `global_variables` dict or HTML5's
  `game.globalVariables`), so there's no real value to route a read to;
  reading `0` is also the *semantically correct* answer specifically for
  every multiplayer identity global (`is_host`, `network_connected`,
  `player_id`, ...) — they really are always 0/false on a target that can
  never network at all. An unrelated author-defined global degrades from
  "crashes the whole export" to "reads 0", matching this file's existing
  graceful-degradation convention for everything else it can't represent.
  `is_instance_owner`/`remote_input` (used as GUARD conditions, not plain
  actions) need no fix at all: Kivy's guard-action dispatch already
  treats an unrecognized guard as `if True:` (verified — no `SyntaxError`,
  unlike HTML5's `evaluateCondition` which defaults to `false`), and since
  a Kivy export can never actually network, "always true" is the *correct*
  behaviour too — the single local player genuinely does always own their
  own instance, there being no other player who ever could.
  `tests/test_kivy_global_expression_export.py` (13 tests):
  `_strip_global_refs` unit coverage including a false-positive guard (an
  identifier merely *containing* "global", e.g. `self.globalscore`, must
  not be mangled — no literal dot follows "global" there);
  `_resolve_instance_names` on the exact `global.network_connected != 1`
  expression the sample authors; and a real `KivyExporter().export()` +
  `py_compile.compile(..., doraise=True)` of all three `reseau_*` samples'
  every generated file, confirmed zero compile failures (previously: an
  immediate crash). Also confirmed (not fixed — a separate, narrower,
  pre-existing display-only gap, explicitly out of scope here): Kivy's
  `draw_text` never resolves a bare `global.X` text-param reference the
  way desktop/HTML5 do, so reseau_2's score readout renders the literal
  string `"global.team_score"` rather than its value on this target —
  logged in `TODO.md` rather than fixed, since it's cosmetic (no crash)
  and unrelated to this fix's actual scope (conditions/expressions, not
  draw_text's own separate string-literal handling). Full suite 4234 →
  4247 passed, 0 failed.
- [x] 7.4 Wiki: `Network` / `Réseau` page; `tools/gen_action_reference.py`
  regen; strings added to `tools/action_ref_i18n.py`. **DONE 2026-09-02/03
  for English + French; DE/UK/RU/IT/ES/PT/SL explicitly deferred** — see
  below for why partial is the correct stopping point here, not a gap.
  - **"Regen picks up the new actions automatically" was wrong — a real,
    pre-existing architecture assumption broke, found by actually running
    the regen rather than trusting the plan text.** Two independent bugs,
    both fixed:
    1. `extensions/multiplayer_lan/actions.py` is authored **French-first**
       (its `display_name`/`description`/`ActionParameter.description` ARE
       the live French UI text — confirmed via `object_events_panel.py`'s
       `self.tr(action_type.display_name)` call sites, so this is also a
       live-app i18n quirk, not just a doc-generator one), unlike every
       other category in the codebase (English-sourced). `gen_action_
       reference.py`'s `Tr` class hardcoded `lang == "en"` as a pure
       pass-through of the source text with no override path — so an "en"
       regen would have shown French text under English headings for all
       15 Réseau actions. Fixed with a new `EN_OVERRIDES` table in
       `action_ref_i18n.py` (real English translations for all 15 actions
       + their ~27 parameter notes + the "Réseau"→"Network" category
       label), consulted by `Tr.display`/`Tr.desc`/`Tr.note`/`Tr.category`
       only when `lang == "en"` — every other (English-sourced) action is
       completely unaffected. `Tr.note()`'s signature changed from a bare
       source-text key to `(action_name, param_name, source_text)`, since
       a French source string has no natural English key the way an
       English one does for every other language's lookup table.
    2. `FILE_KEY[cat]` was a bare dict subscript with no fallback — a
       category added to `ACTION_TYPES` without a matching `FILE_KEY`
       entry crashed the **entire** generator run (not just that
       category). This wasn't only about Réseau: `Particles` (Block
       World's particle-system actions) was ALSO missing and hit the same
       crash — the reference had silently gone unregenerated since before
       either category existed. New `_file_key()` helper falls back to an
       ASCII-safe slug instead of crashing; explicit `FILE_KEY` entries
       added for both `Particles` and `Réseau` (→ `Network-Actions`, an
       English-stable filename independent of the French display text).
    3. Discovered en route, NOT fixed (would need a project-wide i18n
       pass, well beyond this doc's scope): the live IDE's action picker
       renders `self.tr(action_type.display_name)` for every action — for
       Réseau specifically this means a non-French IDE language shows
       French action names/descriptions unless a `.ts` catalog entry
       happens to translate that French source string, which none do.
       Logged in `TODO.md` rather than silently left undiscovered.
  - **The regen itself was badly overdue independent of Réseau**: it
    caught the count up from 113 to **159** actions (Timing 2→8, Game
    20→25, 3D View 4→16, plus the wholly-new Particles and Network
    categories) — Block World's Tier 5+ particle/timeline actions had
    never been in the reference at all. Every category's content diff is
    additive (new actions), not corrupted (verified via `git diff
    --stat`) — this was a stale reference catching up, not a regression.
    `wiki/Home.md`/`Home_fr.md`'s hardcoded "109 actions" figures (also
    stale, unrelated to Réseau) corrected to 159 in passing.
  - **New `wiki/Network.md` + `wiki/Network_fr.md`** (matching
    `wiki/3D-View.md`'s established template exactly): what it is, the
    Tier A/Tier B split, how host/join/identity-globals work, the action
    and event tables (cross-checked against the LIVE `PLUGIN_ACTIONS`/
    `PLUGIN_EVENTS` source dicts, not invented — this caught a real
    mistake in the first draft: the `network_started` event's actual
    French display name is "Réseau prêt" — "Network Ready" — not the
    "Network Started"/"Partie réseau démarrée" guessed before checking),
    two minimal worked examples (Tier A shared room, Tier B shared
    avatar), and the LAN/port/firewall caveats already established
    elsewhere in this doc. `wiki/Event-Reference.md`/`_fr.md` gained a
    "Network Events" section (six events, not part of any preset);
    `wiki/Extensions.md`/`_fr.md` gained a second worked-example mention
    and nav links; `wiki/Home.md`/`_fr.md` gained a features-table row, an
    Actions-list bullet, and an Advanced-Features link — all cross-checked
    for zero dangling internal links.
  - **DE/UK/RU/IT/ES/PT/SL deliberately NOT done this pass** — same
    session-budget discipline as the ja/pt/zh UI-translation arc
    (`CLAUDE.md`'s "~40% of a session per language" precedent): the regen
    mechanism is proven correct (falls back to the French source text with
    an honest "missing" report for every un-translated language, same as
    the pre-existing Particles/Block-World gap those languages already
    have), so finishing the remaining 7 is now pure, safe, incremental
    translation work — add `ACTIONS_XX`/`NOTES_XX`/`CATEGORIES_XX` entries
    for the 15 actions + write `Network_<lang>.md`, one language at a
    time, verified by re-running the regen and confirming its "missing"
    report drops to zero for that language.

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
- [x] 8.2 `reseau_2` (quiz). **DONE 2026-09-02.** "Quiz de classe":
  Tier A only, one object (`obj_quiz`) branching on `global.is_host`/
  `global.is_client`. Host publishes each round's full question/option
  text as shared vars (composed once at round-setup time, not
  concatenated at draw time — see the landmine below), runs an 8-second
  `set_alarm` per question, and awards points via a `network_message`
  ("reponse") handler comparing the answer against a per-machine secret
  instance variable (`self.correct` — never published as a shared var,
  so it can't be read off another machine). Clients answer with A/B/C/D,
  each sending `send_network_message(event="reponse", data=<letter>,
  target="host")`. In-game text is French (matching `reseau_1`'s own
  precedent — the plan's general "sample messages stay English" rule is
  for the older, pre-existing samples; these `Réseau`-branded ones are
  French-native throughout, action names included). `README.md` +
  `README.fr.md`, Welcome-tab entry, smoke registration.
  `tests/test_reseau_2_sample.py` (9 tests: single-player/registration/
  guides, and 6 real two-`GameRunner`-loopback tests covering round
  publish, correct/wrong scoring, the alarm-driven round advance fired
  directly rather than waiting 8 real seconds, and the quiz ending after
  the last round). Visually verified via 3 real rendered frames (title,
  live question, final scores) — accents render correctly throughout.
  **Two real bugs found and fixed while building this, both logged in
  their own sections above/below:**
  1. `_eval_bool_expression` (if_condition's "expression" type) silently
     no-op'd on `global.X` — see "Core changes" above, the actual reason
     this sample needed a real (small) core fix.
  2. `set_shared_var`'s `value` param goes through `_parse_value`, which
     routes any string containing an operator character (`+-*/%`) to the
     arithmetic evaluator unless quoted — French text routinely contains
     a hyphen (`utilise-t-il`) or trails off with `...`/`?`, so every
     human-authored shared-var value in this sample is now wrapped in
     escaped quotes (the same documented `CLAUDE.md` landmine `draw_text`
     already had to work around, just not previously hit for
     `set_shared_var`). No core fix needed here — purely an authoring
     discipline, now documented in the sample's own generator script for
     next time.
  Full suite 4164 → 4178 passed, 0 failed.
- [x] 8.3 `reseau_3` (co-op). **DONE 2026-09-02.** "Récolte en équipe":
  Tier B, built directly on `reseau_1`'s owned-avatar pattern, adding a
  host-simulated patrolling monster and 5 host-authoritative gems.
  `obj_person`'s `collision_with_obj_gem`/`collision_with_obj_monster`
  are both guarded by `global.is_host == 1`; picking up a gem calls
  `destroy_instance(target="other")` + increments a shared
  `team_score`, touching the monster docks a point (`max(...,0)`
  floored). New sprites (`spr_gem`, `spr_monster`) generated
  procedurally via PIL — no hand-drawn art needed for simple flat
  shapes. `README.md` + `README.fr.md`, Welcome-tab entry, smoke
  registration.
  **Real design bug found and fixed while building this, not just a
  test artifact:** the spawn logic (avatar + monster + 5 gems) was
  first written inline in the "h" keyboard handler's action list, right
  after `host_game`. Since `host_game(show_lobby=true)` is a *blocking*
  call that shows "En attente de joueurs…" and only returns once
  "Démarrer" is clicked, spawning inline there means everything appears
  the instant hosting starts — before any player has joined or the
  round has actually begun. Moved to `network_game_started` (guarded by
  `is_host==1`), matching `reseau_2`'s own pattern exactly — "the game
  actually begins" is what that event means. A monster-teleport-back-
  to-start-on-hit design was also considered and dropped: on the host, a
  *client-owned* avatar's position keeps arriving from that client every
  frame, so a host-side teleport would just get overwritten by the
  client's next report — docking a shared score point sidesteps that
  ownership conflict entirely.
  `tests/test_reseau_3_sample.py` (9 tests: single-player/registration/
  guides, plus 6 real two-`GameRunner`-loopback tests — spawn on game
  start, `player_joined` spawns a second avatar, the client materialises
  gem/monster ghosts, gem collision scores and destroys the gem
  (mirrored to the client), monster collision docks a point without
  going negative, and the monster's `step` AI is confirmed genuinely
  host-only by firing it directly on a client's ghost copy and checking
  it doesn't move). Visually verified via a rendered HUD frame — accents
  render correctly. Full suite 4178 → 4192 passed, 0 failed.
- [ ] 8.4 `reseau_4` (draw-together) — optional.
- [x] 8.5 `tools/smoke_run_multiplayer.py` + CI wiring. **DONE
  2026-09-02.** Launches a real host subprocess + a real client
  subprocess over a real `127.0.0.1` socket via `runtime/run_game.py`
  (the actual CLI/subprocess deployment path — two real OS processes,
  not the in-process `GameRunner` pytest coverage). New `GameRunner.
  _print_net_status` (called alongside the existing `PYGM_FRAMES_
  COMPLETED` marker) prints a grep-able `PYGM_NET_STATUS=role=...
  connected=... player_id=...` line so an external harness can verify
  the client actually received a WELCOME (only fires when a v2 session
  mirrored `network_role` into globals — an ordinary single-player run's
  stdout is unaffected). **Scoped to `reseau_1` only** — the one bundled
  sample launched purely via env vars (`PYGM_NET_AUTOHOST`/
  `PYGM_NET_AUTOJOIN`), which a headless subprocess with no display can
  receive; `reseau_2`/`reseau_3` need an in-game "h"/"j" keypress
  instead (already thoroughly covered by their own real two-`GameRunner`
  pytest suites) and `multiplayer_lan_1` (v1) has no identity/globals
  mirroring at all, so the marker this tool checks for never fires for
  it (it has its own existing in-process networked smoke test).
  **Real bug caught and fixed while building this**: the host and
  client were both given the same frame budget and the host started
  0.5s earlier, so the host's process (and its listening socket) could
  exit *before* the client finished its own run — the client then
  correctly detected `connection_lost` right at the end (Phase 8.6's
  new teardown behavior working exactly as designed) and reported
  `connected=0` despite having been genuinely connected the whole time
  that mattered. Fixed by giving the host double the client's frame
  budget so it reliably outlives it.
  **"CI wiring"**: `tools/smoke_run_samples.py` itself isn't directly
  invoked by `.github/workflows/`  either — it's a manual dev tool: the
  actual CI-relevant coverage is the structural pytest checks (does the
  tool exist, compile, and name the right samples), which run in the
  normal suite every time. Matched that same pattern here rather than
  inventing new CI infrastructure with no sibling precedent. The real
  two-subprocess run is opt-in behind `PYGM_E2E_MULTIPLAYER=1` (mirrors
  `test_desktop_export_end_to_end.py`'s `PYGM_E2E_EXPORT=1`), verified
  to actually pass, not just wired.
  `tests/test_game_runner_net_status_print.py` (4 tests),
  `tests/test_smoke_run_multiplayer.py` (6 tests, including the real
  opt-in end-to-end run). Full suite 4192 → 4201 passed, 0 failed.
- [x] 8.6 Graceful host-loss. **DONE 2026-09-02.** The `connection_lost`
  event + `network_connected=0` mirroring already existed (Phase 5.2);
  what was missing was "clean client teardown" — a lost host will never
  send another snapshot, so a ghost frozen in its last position read as
  a stuck phantom player. `_destroy_ghosts_on_connection_lost` (called
  from `_apply_session_state` right where the event is queued) marks
  every ghost `to_destroy` and clears `st["ghosts"]`. The client's own
  locally-owned avatar (`synced_local`) is deliberately left running —
  same "the game continues single-player" precedent as `join_game
  host="auto"` cancel. No automatic full `leave_game`-style reset:
  identity globals stay readable so an author's own `connection_lost`
  handler can react with context; a full reset only happens if the
  author calls `leave_game` explicitly. (Host *migration* stays
  deferred.) `tests/test_multiplayer_lan_ghosts.py::TestConnectionLostTeardown`
  (3 tests, real two-`GameRunner` loopback: ghosts destroyed, the
  client's own avatar untouched, the event fires exactly once not every
  frame). Full suite 4151 → 4154 passed, 0 failed.
  **Landmine hit and fixed while landing this**: a first draft inserted
  the new module-level function in the middle of the `PluginExecutor`
  class body by mistake — Python's indentation-based syntax accepted it
  silently (no SyntaxError), but it truncated the class early, orphaning
  every method after the insertion point (`network_spawn` and everything
  alphabetically after it vanished from `action_handlers`). Caught by
  the full-suite gate, not by the new tests themselves — a reminder that
  "the new tests pass" isn't sufficient; the *existing* suite must also
  stay green after any edit to a large class-based module like this one.
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
