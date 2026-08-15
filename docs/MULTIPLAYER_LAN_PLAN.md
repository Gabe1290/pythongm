# Plan: LAN multiplayer (folder extension)

Status: **not started.** Written 2026-08-15 per
`docs/REMAINING_WORK_2026-08-15.md` Section F's instruction that this item
needs its own dedicated plan doc before any code lands. Supersedes nothing —
the only prior record was the `multiplayer-network-stash` memory entry,
folded in here.

## Where this comes from

A git stash exists on `main` (`stash@{0}`, message `WIP: multiplayer over
network (resume after stability work)`, created 2026-05-02). `git stash show
-p` reproduces the exact diff. It is a real, working vertical slice — not a
sketch — but it **cannot be reapplied as-is**, for two independent reasons:

1. It imports `from runtime.network import NetworkHost, NetworkClient` and
   `from runtime.network.protocol import DEFAULT_PORT`. `runtime/network/`
   has **zero git history** (`git log --all -- runtime/network/` is empty)
   — its source was never checked in, only ever present on disk as an
   untracked working copy, and that copy (plus its stale `.pyc` files) was
   deleted 2026-08-08. There is nothing to recover; `NetworkHost`/
   `NetworkClient`/the wire protocol need a full rewrite.
2. It bakes `_net_mode`/`_init_network`/`_net_broadcast`/`_net_apply_inbound`
   directly into `GameRunner` (`runtime/game_runner.py`). This repo's
   established pattern since raycast/block_world (see
   `docs/RAYCAST_EXTENSION_PLAN.md`, `[[extensions-and-1.0-compat]]`) is that
   a new capability is a **folder extension**, not a core-engine change —
   core stays runnable and correct with the extension absent, and an
   editor/export without it degrades the same way any missing extension
   does (`not_installed_extensions_for_project` already warns on load).
   Reapplying the stash's diff literally would regress that principle.

**What the stash IS good for**: it's a proven functional spec. Read
verbatim below, then reimplemented against the extension-hook seam this
plan adds (see Phase 1).

### The stash's exact shape (for reference, not reapplication)

- `GameRunner.set_network_mode(mode, host=None, port=0)` — `mode` is
  `"host"` or `"client"`; call before `run()`.
- `_init_network()` — called once, right before `self.running = True` in
  `run_game_loop`: assigns every initial room instance a deterministic
  `_sync_id` (its enumeration index — both sides load the same project, so
  indices match without negotiation), then starts a `NetworkHost` (listen)
  or `NetworkClient` (connect).
- `_net_broadcast()` — host-only, called once per frame **after** the
  update/collision/destroy pass: snapshots `(sync_id, x, y, rotation,
  image_index, visible)` for every synced instance, sends it.
- `_net_apply_inbound()` — client-only, called once per frame **before**
  the begin-step/alarm/step pass: polls for the latest snapshot, overwrites
  the matching instances' x/y/rotation/image_index/visible in place.
- `NetworkHost(port=...)`: `.start()`, `.broadcast_snapshot(rows)`,
  `.close()`. `NetworkClient(host, port=...)`: `.connect()`, `.poll() ->
  None | {"t": "snap", "i": [(sync_id, x, y, rotation, image_index,
  visible), ...]}`, `.close()`. `DEFAULT_PORT` constant.
- `runtime/run_game.py` CLI: `--net-host`, `--net-client HOST`, `--net-port
  PORT` (mutually exclusive host/client), calling `set_network_mode`
  before `run()`.

This is deliberately **not** a full networked-physics model — it's
"authoritative host broadcasts positions, clients render them," the same
tier of multiplayer as countless simple LAN games. That scope is correct
to keep: this plan does not propose expanding it into client prediction,
lag compensation, or rollback — see "Explicitly out of scope" below.

## A real gap this plan depends on closing first

`runtime/extension_hooks.py` today has exactly one hook kind: room
renderers (`register_room_renderer`, called once per frame **only during
the draw pass**, and only for the room that's currently being drawn). There
is **no per-frame "always run this, regardless of what actions the game
author wrote" hook** — confirmed by reading the file in full while building
Tier 7a's Block World gravity feature this session (see
`docs/DEFERRED_GAPS_2026_PLAN.md` Tier 7a's notes): that feature worked
around the gap by requiring the author to bind an `apply_gravity` action in
their object's Step event, which is workable for a per-object physics
feature but does **not** work for multiplayer. Broadcasting/applying
network state must happen exactly once per frame, unconditionally, at a
specific point in the frame (client-apply before Step, host-broadcast after
collision/destroy) — it cannot depend on whether any particular object
happens to have the right action bound, and it must run even in a project
that has no objects with a Step event at all.

**Phase 0 of this plan is therefore building that hook**, once, generically
— not a multiplayer-specific mechanism, so any future extension needing
"run code every frame, not gated on authored actions" (this is the second
extension that would have wanted it; expect a third) can register for it
too.

## Phase 0 — generic per-frame extension hook (small, core change)

This is the one piece of this plan that touches core, and it's
infrastructure, not multiplayer logic — keep the commit scoped to exactly
this.

- `runtime/extension_hooks.py` gains a second hook list, mirroring the
  existing room-renderer one exactly:
  - `register_frame_update(func)` / `get_frame_updates()` /
    `clear_frame_updates()`, storing `(func, phase)` where `phase` is
    `"before_step"` or `"after_update"` (the two points the stash's
    `_net_apply_inbound`/`_net_broadcast` needed — generalizing to named
    phases rather than hardcoding "network" avoids baking multiplayer's
    own two-point model into the generic mechanism).
  - `run_frame_updates(game_runner, phase)`: calls every registered
    `func(game_runner)` whose phase matches, catching and logging
    exceptions per-function (same "a broken extension must not take the
    game down" contract `render_room` already has).
- `runtime/game_runner.py`'s `run_game_loop` (currently starting line 2562;
  re-check the line number before editing, this file has grown across this
  whole session's work) gains two call sites:
  - `extension_hooks.run_frame_updates(self, "before_step")` — first thing
    inside `while self.running:`, before the begin-step/alarm pass.
  - `extension_hooks.run_frame_updates(self, "after_update")` — right
    after the destroyed-instance cleanup block, before `self.screen.fill(...)`.
- `events/plugin_loader.py` gains a `PLUGIN_FRAME_UPDATES` loader,
  mechanically identical to `_load_room_renderers`/`PLUGIN_ROOM_RENDERERS`
  (same three call sites: the two `hasattr(module, ...)` checks in the
  loader plus the one in the shared-loader fallback).
- Tests: a synthetic extension module registering a counter function at
  each phase, run through a real `GameRunner`/`run_game_loop` for a few
  frames (matching this session's own "verify against a real GameRunner,
  not a hand-rolled harness" discipline for engine-loop changes), asserting
  call counts and phase ordering (`before_step` fires before any Step
  event; `after_update` fires after destroy cleanup). Also: an extension
  whose frame-update function raises must not stop the game loop (mirrors
  `render_room`'s existing crash-isolation test).

## Phase 1 — `extensions/multiplayer_lan/` skeleton + wire protocol

New folder extension, mirroring `extensions/block_world/`'s file layout:

- `extension.json` — `provides_actions: ["set_network_mode"]` (see Phase 2),
  no room renderer.
- `state.py` — pure data: `DEFAULT_PORT`, the wire-message shape as a
  plain dict contract (no pygame/socket import, matching every other
  extension's `state.py` staying import-light so the IDE can load it for
  schemas alone).
- `network.py` — the actual rewrite of what `runtime/network/` used to be.
  **Design decision needed before writing this file**: TCP (stash's own
  implied choice — a single persistent socket, simplest to get right) vs.
  UDP (lower latency, more correct fit for "send the latest snapshot,
  stale ones don't matter," but needs its own minimal reliability handling
  for the initial handshake). **Recommendation: keep TCP for the first cut.**
  Position snapshots are small and infrequent enough (one per frame, a
  handful of instances) that TCP's head-of-line blocking is unlikely to
  matter at LAN scale, and it avoids writing packet-loss/reordering
  handling from scratch. Revisit only if latency actually proves to be a
  problem once there's something real to measure it against.
  - `NetworkHost(port)`: binds and listens, accepts one or more client
    connections (the stash's own model is implicitly single-client;
    **decide multi-client now, even if v1 only supports one**, since
    retrofitting a broadcast-to-N-sockets loop later is a bigger change
    than designing the send path around a list from day one).
    `.broadcast_snapshot(rows)`, `.close()`.
  - `NetworkClient(host, port)`: `.connect()`, `.poll()` (non-blocking —
    critical: this is called once per frame from inside the game loop, so
    it must never block waiting on the socket), `.close()`.
  - Wire format: JSON lines (simplest to implement/debug, matches the
    stash's own `{"t": "snap", "i": [...]}` shape) over the TCP stream,
    newline-delimited. Not the most bandwidth-efficient choice available,
    but LAN bandwidth was never the constraint here; readability while
    debugging a first cut is worth more.
- `handlers.py` — `PluginExecutor.execute_set_network_mode_action`,
  mirroring the `_init_network`/host-or-client branch from the stash, but
  storing state under `game_runner` (a new small attribute, or reuse the
  existing per-room `extension_state` dict pattern if the state is more
  naturally room-scoped than runner-scoped — **check this**: sync IDs are
  assigned per current-room instance list, so network state plausibly
  belongs on `room.extension_state["multiplayer_lan"]` the same way
  raycast/block_world camera config does, NOT as new `GameRunner`
  attributes; this also sidesteps needing `GameRunner` to know anything
  about networking at all, keeping Phase 0's hook the *only* core-visible
  trace of this extension existing).
- The two Phase-0 frame-update hooks:
  `_frame_update_apply_inbound(game_runner)` (phase `before_step`,
  mirrors `_net_apply_inbound`) and `_frame_update_broadcast(game_runner)`
  (phase `after_update`, mirrors `_net_broadcast`), both no-ops when no
  room has active network state.

## Phase 2 — `set_network_mode` action + how a player actually launches host/client

**Open design question, needs a decision before this phase starts**: every
other extension is configured entirely by in-project **actions** (author
writes `enable_block_world_view` into `create`), a design-time choice baked
into the project. Multiplayer is fundamentally different — "who hosts, who
joins, at what address" is a **per-launch, per-player** choice, not
something the game's author can bake in (two players running the identical
exported game need to end up in different roles). An action alone can't
express that.

Three ways to reconcile this, roughty in order of how much they touch
outside this extension:

1. **CLI flags only** (the stash's own choice): `run_game.py --net-host` /
   `--net-client HOST`. Simplest for a player to use for an exported
   desktop build (`.exe`/binary + a flag). Doesn't help HTML5 (no CLI for
   a page load) or Kivy/Android (no terminal a typical player has) at all
   — **desktop-only** by construction, which may be an acceptable v1 scope
   given LAN play between desktop instances is the most natural first
   target anyway.
2. **In-game UI the author builds themselves** using ordinary actions (a
   "Host" / "Join" menu screen calling `set_network_mode` with a
   player-entered IP) — works on every export target uniformly, costs
   nothing new in the engine, but pushes UI-building work onto every game
   author who wants multiplayer, and doesn't fit the CLI-launch case at
   all.
3. **Both**: `set_network_mode` action exists for option 2 either way (an
   author-built menu needs *some* action to call); CLI flags are an
   *additional*, desktop-only convenience layered on top, implemented as
   `run_game.py` setting environment variables (`PYGM_NET_MODE`,
   `PYGM_NET_HOST_ADDR`, `PYGM_NET_PORT`) rather than importing the
   extension directly — keeping `run_game.py` (a generic bootstrap script
   every exported/tested game uses, not multiplayer-specific) unaware of
   this extension's existence. The extension's own init code checks those
   env vars as a fallback when no `set_network_mode` action ever ran.

**Recommendation: option 3.** It's not meaningfully more work than option 1
alone (the env-var indirection is a handful of lines), and it's the only
one of the three that doesn't foreclose either the "quick desktop LAN test"
use case or eventual HTML5/Kivy support.

- `actions.py`: `set_network_mode` — `mode` (choice: host/client),
  `host` (string, required only for client), `port` (number, default
  `DEFAULT_PORT`).
- `handlers.py`: reads the action params, falling back to the
  `PYGM_NET_*` env vars when the action was never called (so a game with
  zero authored multiplayer UI still works purely from the CLI flags for
  quick testing).
- `runtime/run_game.py`: add `--net-host` / `--net-client HOST` /
  `--net-port PORT` (mutually exclusive host/client group, matching the
  stash's own argparse shape) that set the three env vars before
  `runner.run()` — no import of the extension, no new GameRunner method.

## Phase 3 — sample + manual playtest

- A minimal two-instance sample (or a `multiplayer_lan_1` sample folder,
  matching this repo's convention of shipping a sample alongside a new
  engine capability — see `block_world_1`, `raycast_1`) that moves a synced
  instance with arrow keys, enough to visually confirm host and client see
  the same position.
- **This phase needs a real second machine or a second process on the same
  machine talking over `localhost`** — same "manual QA, not code" category
  as everything in `docs/REMAINING_WORK_2026-08-15.md` Section C. The
  automatable parts (Phase 0's hook mechanism, Phase 1's protocol framing,
  Phase 2's action/env-var plumbing) can and must be unit-tested without a
  real second process; the actual "two players, two machines/processes, do
  they converge" check cannot.
- Test plan for what CAN be automated: a loopback test spinning up a real
  `NetworkHost` and `NetworkClient` against `127.0.0.1` in the same test
  process (two threads or two `multiprocessing` processes), confirming a
  broadcast snapshot round-trips and `poll()` returns it — this proves the
  wire protocol works without needing a second physical machine, and is
  the strongest automated guard available.

## Explicitly out of scope (don't creep into this during implementation)

- **Client-side prediction / interpolation.** Raw snapshot application (the
  stash's own model) will look visually jittery at anything above LAN-grade
  latency. Smoothing is a legitimate, separate follow-up once the basic
  sync works and someone can actually feel the jitter to tune against —
  don't build smoothing speculatively.
- **More than position/rotation/frame/visible sync.** No custom-variable
  sync, no authoritative collision resolution across the wire, no
  server-side input validation/anti-cheat. This is "see where the other
  player is," not a competitive-integrity netcode model — matches the
  stash's own scope exactly and this is software for students building
  games together in a classroom, not a product needing cheat-resistance.
- **NAT traversal / internet play.** LAN only, by name and by design —
  `NetworkHost`/`NetworkClient` binding to a local address is sufficient;
  no STUN/TURN/relay infrastructure.
- **HTML5/Kivy export support.** Phase 2's CLI-flag path is desktop-only by
  construction; extending multiplayer to the other two export targets is a
  new, separately-sized follow-up once desktop is proven, not part of this
  plan.
- **Reworking Phase 0's hook into something Block World's gravity feature
  retroactively adopts.** `apply_gravity`'s "bind it in Step" pattern
  already ships and works; there's no value in circling back to migrate it
  onto the new generic hook just because the hook now exists.

## Suggested sequencing

Phase 0 (small, core, one commit) → Phase 1 (network.py + skeleton, needs
the loopback test from Phase 3 to prove itself, so pull that test forward
to land with Phase 1 rather than waiting) → Phase 2 (action + CLI/env-var
plumbing) → Phase 3's sample + manual two-machine playtest last. Each
phase is its own commit+push, full-suite-green gate, matching every other
tier this repo has worked through.
