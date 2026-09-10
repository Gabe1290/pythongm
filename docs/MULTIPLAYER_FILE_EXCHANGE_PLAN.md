# Plan: 1990s-style turn-based file-exchange multiplayer

**Status 2026-09-10: Track E Phases 1–2 DONE; Track T DONE and
reconciled against the landed API.** `extensions/multiplayer_files/`
(Track E) now has its
whole first-cut action surface: `host_game_files`/`join_game_files`/
`leave_game_files`/`set_shared_var_files`/`get_shared_var_files`/
`end_turn`/`send_network_message_files`, the join/welcome handshake,
host-authoritative round advancement with a deadline, the identity/status
globals, and all six lifecycle events (`file_session_started`,
`player_joined_files`, `round_resolved`, `player_skipped_round`,
`network_message_files`, `file_session_lost`), with real translated
action names in all 10 shipped languages — plus `samples/fichier_1`, the
finished bundled Tic-Tac-Toe sample exercising the whole loop end to end
(42 new tests across both phases, full suite green). `wiki/FileExchange.md`
+ `_fr.md` plus Tutorial 10 (Track T) were written and committed the same
day, on a second machine, before either track could see the other's work.

**Reconciliation pass — DONE 2026-09-10.** The coupling point flagged when
Track T started was a confirmed, real gap: Track T was written against
this doc's *original* "Proposed action surface" — `set_shared_var`/
`get_shared_var`, four events, no `network_sender`/`network_player_name`
globals, and no `send_network_message_files` at all yet. Track E's actual
implementation renamed the shared-var actions to `..._files` (a real
`plugin_loader` naming-collision bug found via testing — see "Proposed
action surface" below), added the two payload globals, and landed
`send_network_message_files`/`network_message_files` with the same
`..._files` naming. Diffed `wiki/FileExchange.md`/`_fr.md` and Tutorial 10
against the real `extensions/multiplayer_files/` source and
`samples/fichier_1` and fixed every drift — action/event names, the
`global.round_number` starting at **1** not 0, an unset shared variable
reading as **`0`**, and the "non-active player must also call End Turn
(File Exchange) every round" requirement (missed originally, confirmed
real by reading the bundled sample's own `obj_game` Step event). **The
one finding big enough to force a rewrite, not just a rename**:
`set_shared_var_files`'s `name` parameter is always taken **literally**
(`handlers.py`'s `_raw()`, "never run through the expression evaluator")
— Track T's original design (nine `obj_cell` instances computing their
own shared-var name from position) is not buildable against the real
action at all, since names can never be computed expressions. Tutorial
10's Phases 1/3/4 were rearchitected around a single `obj_game` object
with nine literal cell names, matching `fichier_1`'s own proven design
(same board coordinates) rather than inventing a second, incompatible
one. Both tracks' three original deliverables (extension, sample,
Tutorial) are now genuinely finished and consistent with each other.

Originally written on explicit ask (2026-09) after the user described
hitting school-LAN firewall problems with `extensions/multiplayer_lan/`'s
socket-based transport, and asked specifically for a plan for the old
"games exchanged state through a shared file" pattern before deciding
whether to build it. Scope was then widened, on a second explicit ask,
from "just the extension" to three deliverables together: the extension
itself, a bundled sample, and a full in-app Tutorial (with the historical
examples discussed folded in as motivation/context) — so a student
doesn't just get the capability, they get taught how to use it and where
the idea comes from. The user then approved starting both tracks (see
"Splitting the work across two machines" below), one per machine — see
the status paragraphs above for what each landed.

## Why this is a real option, and why it's a *different* thing from `multiplayer_lan`

A shared network drive both machines can already reach is functionally the
same trust boundary a socket connection needs, minus the part that's getting
blocked: school IT commonly locks down direct peer-to-peer connections
(Windows Firewall on the "Public" network profile, or an explicit policy)
while leaving a shared drive both machines already use for their own files
completely open. Routing through the file server as a relay, instead of
connecting machine-to-machine, sidesteps the actual problem.

But it is not a drop-in transport swap under the existing extension. I read
`extensions/multiplayer_lan/session.py`/`network.py` before writing this:
`NetworkSession` assumes a **persistent, always-available bidirectional
connection**, polled via non-blocking socket reads on *every single frame*
(`pump_before_step`/`pump_after_update`, called from `runtime/extension_hooks.py`'s
`before_step`/`after_update` phases, ~60 times a second) — that model has no
sensible equivalent over a file share, where:

- there is no "connection" to hold open, only periodic file reads;
- a real network-drive read/write commonly costs 5–50ms or more (SMB/CIFS
  round-trip to a real file server), so polling every frame would hammer the
  server for no benefit — the honest tick rate here is more like once a
  second, not once a frame;
- Windows SMB clients cache reads by default, so "read the file" can return
  stale data unless something forces a fresh read;
- two processes writing the *same* file at the same time is a real corruption
  risk a socket protocol never has to think about.

So this is a **new, additional extension** (`extensions/multiplayer_files/`),
not a change to `multiplayer_lan/` and not a replacement for it. A project
author picks whichever fits: real-time position sync needs sockets; a
turn-based game (a quiz, Tic-Tac-Toe, Battleship, a negotiation game) is a
good fit for files and gets to dodge the firewall entirely.

## What "1990s DOS file-exchange" actually means here

The genre the user is remembering is real: turn-based games (or "hot-seat"/
play-by-mail games) that never needed a live connection at all — each
player's turn was a file, handed to (or shared with) the next player, and
the game read whichever file was current. The core idea worth keeping,
because it is *why* the pattern is safe from corruption: **each writer owns
its own file, forever.** Two processes never write the same filename, so
there is no write race to defend against by construction, not by locking.

Mapped onto a shared classroom drive with both apps running at the same
time (not genuine 1990s sneakernet — closer to how a modern shared drive
actually gets used in a school), the natural shape is:

```
<shared drive>/<game folder>/
  session.json              # host-authoritative: round #, shared vars, roster, status
  join_<client_id>.json     # a client's join request (written once by that client)
  welcome_<client_id>.json  # the host's reply: assigned player slot (written once by host)
  move_p<slot>_r<round>.json  # one player's move for one round -- filename is unique
                               # per (player, round), so it is NEVER rewritten or
                               # contested; a stale/duplicate write just gets ignored
```

Every filename that can be written by more than one "logical writer" over
time is actually written by exactly one writer, once, because the round
number (or client id) is baked into the name. The only file that's ever
*overwritten* is `session.json`, and only the host ever writes it — so the
one place a real write race could happen has exactly one writer, which is
the same "one writer, many readers" shape `core/project_manager.py`'s
`_atomic_write_json` already exists to make safe (see "Reused pieces"
below).

## Design decision: host-authoritative rounds, not fully symmetric mailbox

Two shapes were worth weighing:

- **A. Host-authoritative, turn-based lockstep** (recommended). One machine
  is the host/referee, same role split as `multiplayer_lan`'s host/client.
  Each round: every client writes its move file, the host polls, and once
  it has every expected move (or a deadline passes) it computes the new
  state and publishes an incremented `session.json`. Clients poll
  `session.json` and know their move was accepted once the round number
  moves past what they submitted for.
- **B. Fully symmetric mailbox** — no live host process; a single state
  file is *handed* between players in strict turn order (closer to a
  genuine 1990s play-by-mail game, where only one player's machine is
  even running at a time). More historically faithful, but a poor fit for
  a classroom LAN session where every player's app is already running
  simultaneously — it would mean a player's app sits completely idle,
  polling, for however many players are ahead of them in turn order, with
  no natural place for a "waiting for other players" screen or a host to
  own timeouts/reconnects.

**Recommendation: A.** It mirrors `host_game`/`join_game`'s existing role
split (so the API reads the same way to a student who's already used the
socket version), gives one clear place to own timeouts and round
advancement, and every player's app stays responsive throughout rather than
blocking on turn order.

## Historical grounding: where this idea actually comes from

Discussed and settled in conversation before this doc was written; recorded
here as the specific, checkable content to cite in both the wiki page and
the tutorial's intro (see "Tutorial" below) rather than something to
re-research later:

- **VGA Planets** (1992, Tim Wisseman) — the closest real-world match to
  this plan's own model. Each player's local turn produced a `.TRN` file;
  a separate "host" program (run by one designated player, or a BBS
  robot-host) combined every player's `.TRN` into a fresh `.RST` (result)
  file per player for the next turn. Distributed by BBS door, modem,
  mailed floppy disk, and later FTP/email. The file *was* the protocol —
  essentially the same host/`session.json`/per-player-move-file shape this
  plan proposes, just modernized onto a shared drive instead of a mailbox.
- **Stars!** (1995) — same 4X-strategy genre, same turn-file/host-file
  mechanic, same distribution methods.
- **BBS door games** — *Trade Wars 2002*, *Legend of the Red Dragon
  (LORD)*, *Barren Realms Elite*. Not player-to-player file exchange (the
  state lived on the single BBS's own disk, not split across each
  player's machine), but the same "turn recorded to a file, read back by
  whoever needs it next, whenever that is" idea — worth mentioning as the
  asynchronous-state cousin of the pattern, not the direct ancestor.
- **Play-by-mail (PBM) and play-by-email (PBEM) Diplomacy** — genuinely
  where the whole idea originates. A human or DOS-era "judge" program
  processed mailed-in (later emailed) orders from every player together
  and mailed/emailed back results. VGA Planets and Stars! are really PBM
  games with the mail step automated — the direct lineage from "mail your
  move" to "write your move to a file."

**Where this content lives** (a documentation placement decision, not
extension design): the *full* historical section belongs in a wiki
explanation page (`wiki/FileExchange.md` + `wiki/FileExchange_fr.md`,
mirroring `wiki/Network.md`/`_fr.md`'s existing role documenting
`multiplayer_lan` — that extension has no in-folder `README.md` of its own
either, so this matches precedent rather than inventing a new doc
location). The Tutorial gets a short version — a few sentences in its
intro page framed as "this isn't a new idea," not the full essay — matching
how `Tutorials/09_catch_the_coins`'s own intro page stays focused on what's
being built rather than digressing.

## The concrete game: Tic-Tac-Toe over file exchange

Both the sample and the tutorial need one concrete game to build, and it's
worth deciding now rather than leaving it open — **Tic-Tac-Toe** is the
recommendation, for reasons specific to *teaching* this extension rather
than genre appeal:

- **Alternating turns, not simultaneous.** Rock-Paper-Scissors or a quiz
  round (both raised earlier) are *simultaneous*-choice games — every
  player submits before anyone sees the others' answers. That's a fine
  fit for the shared-blackboard model, but it under-demonstrates the part
  that's actually most "1990s turn-based": one player acts, then waits,
  then the other acts. Tic-Tac-Toe's strict alternation is a better
  teaching vehicle for `global.round_number`, "is it my turn yet," and the
  waiting-room UX than a simultaneous game is.
- **Universally known rules.** The tutorial's limited page budget goes
  entirely to the *multiplayer* mechanics (host/join, submit a move, wait,
  see the result) rather than also having to teach a novel game's rules
  from scratch — matching how `09_catch_the_coins` didn't need to explain
  what "catch the falling thing" means either.
- **Minimal state.** A 3x3 grid of cell values is the smallest possible
  "shared game state" a shared var (or nine of them) can hold cleanly, and
  win-checking (three in a row) is a short, self-contained expression —
  nothing here competes for the student's attention with the networking
  concepts being taught.

The bundled **sample** (`samples/`, name and edition-filter prefix TBD at
Phase 2, see "Proposed phases") is the finished, polished version — open
it and play. The **Tutorial** builds an equivalent project from scratch,
incrementally, independent of the sample the way every other Tutorial is
independent of any bundled sample with a similar theme (no bundled sample
matches any of Tutorials 01–09's own build targets either — Pong, Breakout,
Sokoban etc. exist only as what a student builds by following along, never
as a pre-shipped `samples/` entry — confirmed by checking, not assumed).
Building the *same* game twice, independently, means the tutorial can stay
purely pedagogical (small steps, testable after each) without being
constrained to match the sample's exact code shape.

## Proposed action surface

Named and shaped to read as the file-exchange sibling of the existing
`host_game`/`join_game`/`set_shared_var` family (`extensions/multiplayer_lan/actions.py`),
not a reinvention:

- **`host_game_files(folder, max_players, player_name, round_deadline)`** —
  create/claim the game folder on the shared drive, become the host.
  `round_deadline` (seconds, default e.g. 30): how long the host waits for
  every player's move before advancing the round anyway (a disconnected
  player's slot is skipped that round rather than freezing the game
  forever — same "don't let one absence hang everyone" instinct as
  `multiplayer_lan`'s connection-timeout handling).
- **`join_game_files(folder, player_name)`** — write a join request, then
  wait (across ordinary frame polls, not blocking) for the host's
  `welcome_<id>.json` to assign a player slot. Same "if the host cannot be
  reached, carry on single-player" fallback `join_game`'s own docstring
  already promises.
- **`leave_game_files()`** — write a "left" marker file (matches the
  one-writer-per-file rule — even leaving doesn't touch anyone else's
  file) and stop polling.
- **`set_shared_var_files(name, value)` / `get_shared_var_files(name, into)`**
  — the file-exchange counterpart of Tier A's `set_shared_var`/
  `get_shared_var`, readable everywhere as `global.<name>` once published.
  **Built as `..._files`, not the identical name**: `events/plugin_loader.py`'s
  `_load_actions` skips any plugin action whose name already exists in
  `ACTION_TYPES` (the landmine CLAUDE.md documents), and
  `multiplayer_files` sorts before `multiplayer_lan` in the loader's
  alphabetical folder walk — reusing the exact name would have silently
  disabled the already-shipped LAN version's own actions the moment both
  extensions were installed together. Found and fixed during Phase 1
  implementation, not anticipated when this section was first drafted; see
  `extensions/multiplayer_files/actions.py`'s own module docstring. The
  difference from the socket version is *when* a client's write takes
  effect: it's staged in that player's own move file and only becomes
  visible to everyone once the host folds it into the next `session.json`
  — an honest consequence of there being no live connection, and worth
  explaining to a student the first time they hit it (their own
  `global.score = 5` doesn't appear to update immediately on their own
  screen either, matching what the host will actually publish, not an
  optimistic local guess).
- **`end_turn()`** — marks the current round's move file as final and
  ready for the host to consume. Split out from `set_shared_var_files`
  itself (rather than every var-write being an implicit "I'm done") so a
  player can set several variables while composing their move before
  submitting it as one round file. No naming collision with
  `multiplayer_lan` (it has no `end_turn` action), so this one kept its
  plain name.
- **`send_network_message_files(event, data, target)`** (Phase 2, not
  built yet) — same shape as the socket version's custom messages, staged
  the same way `set_shared_var_files` is (delivered on the next round
  boundary, not instantly). Named `..._files` up front this time, for the
  same `plugin_loader` collision reason `set_shared_var_files` was
  renamed to during Phase 1 — no need to rediscover it at Phase 2 time.
- Read-only identity globals: `global.is_host`, `global.player_id`,
  `global.player_count`, `global.round_number`, `global.turn_ready`
  (whether this machine has read or published at least one `session.json`
  — the point at which published state, not just local defaults, is safe
  to act on), `global.waiting_for_players` (for an authored "waiting on
  player 2…" message). Plus, mirroring `multiplayer_lan`'s own
  `network_sender`/`network_player_name` payload globals (not called out
  in the first draft of this section, added during Phase 1 once it was
  clear an author reacting to "who joined" / "who was skipped" needed
  them the same way the socket version's own `player_joined` handler
  does): `global.network_sender` (the slot) is set before
  `player_joined_files` and `player_skipped_round` fire;
  `global.network_player_name` (their name) is set before
  `player_joined_files`.
- Events (mirroring `network_started`/`player_joined`/`network_message`/
  `connection_lost`): `file_session_started`, `player_joined_files`,
  `round_resolved` (fires on every machine once a round's state is
  published and picked up), `player_skipped_round` (a player's deadline
  lapsed this round), `file_session_lost` (the shared folder became
  unreadable — drive disconnected, permissions changed, etc.). A player
  leaving deliberately gets **no** dedicated event — it's visible via
  `global.player_count` dropping, same information without growing the
  event list for something a poll already surfaces.

**Deliberately not proposed**: `network_spawn`/`sync_instance`/
`bind_network_input` (Tier B, live networked instances) have no sensible
file-exchange equivalent — continuous position sync needs the tick rate a
file share can't deliver. A game that needs live movement should use
`multiplayer_lan` instead; this extension is turn-based games only, by
design, not a lesser version of the same thing.

## Reused pieces (do not re-derive these)

- **`core/project_manager.py`'s `_atomic_write_json` pattern** (write to a
  sibling `.tmp`, `os.replace` into place, retry the rename a few times on
  `PermissionError`) is exactly the shape a shared-drive writer needs, down
  to the specific problem it already solves for: that function's own
  docstring notes Dropbox/OneDrive/iCloud hold a transient lock on a file
  while indexing it, which is the same failure mode a school SMB share's
  own indexing/AV scanning can produce. Port the *pattern*, not necessarily
  the function itself (this one is Qt/project-specific).
- **`extensions/multiplayer_lan/state.py`'s `sanitize_value` / `sanitize_name`
  / `is_valid_shared_name` / `RESERVED_SHARED_NAMES`** are pure, already
  battle-tested (including the `global.X` name-collision guard from audit
  M10) and exactly what a JSON-file-based shared var needs too. **DECIDED:
  duplicate, don't import.** Importing directly from `multiplayer_lan.state`
  would create a real (if small) dependency of one extension's *code* on
  another's internals that the extension install/enable-warning system
  (`events/plugin_loader.py`'s `missing_extensions_for_project`/
  `not_installed_extensions_for_project`, see the
  `[[extensions-and-1.0-compat]]` design) doesn't model — it tracks
  dependencies from which *actions* a project uses, not from one
  extension's code importing another's, so a project using only
  `multiplayer_files` would never record `multiplayer_lan` as a
  requirement. Disabling/removing `multiplayer_lan` alone (plausible here
  specifically, since a school that wants the firewall-safe option may
  deliberately not want the socket one enabled) would then break
  `multiplayer_files` with a bare `ImportError` mid-lesson, with none of
  the "missing extension" warning dialogs that exist to catch exactly this
  class of problem. Given the functions are small, pure, and have not
  needed a change since the M10 fix, that risk isn't worth taking for the
  sake of avoiding ~80 duplicated lines: `multiplayer_files/state.py`
  copies them verbatim, with a comment pointing at
  `multiplayer_lan/state.py` as the shared spec to keep them in sync with
  by hand if either ever changes. Revisit only if a third extension needs
  the same sanitizers — at that point a real shared low-level module the
  extension system understands becomes worth building; for two, it isn't.
- **`runtime/extension_hooks.py`'s existing `before_step`/`after_update`
  phases** — no new hook type needed. The extension registers into the
  same two phases `multiplayer_lan` uses; it just gates actual disk I/O
  behind a `time.monotonic()` interval check internally (same pattern
  `discovery.py`'s `BEACON_INTERVAL`-gated UDP beacon already uses), so it
  costs nothing on the 59 frames out of 60 it doesn't touch disk.
- **The connect-screen pattern** (`extensions/multiplayer_lan/connect_screen.py`)
  for eventual UX polish — a modal pygame screen is already proven for
  "type an address, see a waiting room." A file-exchange version needs
  "type or pick a folder path" instead of an IP address; a full in-game
  folder *browser* is real, non-trivial UI work and should be its own
  later phase, not part of the first cut (see Phase 4 below).

## Explicitly out of scope

- **HTML5 / browser export.** A browser cannot write to an arbitrary
  filesystem path at all without the File System Access API, which has
  real gaps in browser support and needs a user gesture per session — a
  fundamentally different, much more limited capability than "write a
  file to a mapped drive letter." Not attempted here; if a real ask for
  it shows up later, it's a separate, smaller-scope design (likely:
  export a "my move" file the student downloads and re-uploads by hand,
  which is barely file-exchange automation at all).
- **Kivy / Android export.** Scoped storage on modern Android makes
  writing to an arbitrary network share from an app a real fight even
  before considering whether the tablet is even on the same LAN as the
  drive. Desktop-only for the same reason as above — revisit only on a
  concrete ask.
- **Live position sync (Tier B equivalent).** Covered above — genuinely
  the wrong transport for it.
- **Network-share auto-discovery / a folder browser UI in Phase 1.** Type
  or configure the path explicitly first; browsing is a UX nicety for a
  later phase, not core functionality.
- **Any merge/conflict resolution beyond "host is authoritative, last
  write wins per named var."** No operational-transform/CRDT-style
  merging — this is turn-based specifically so simultaneous edits to the
  same thing are the exception (two players choosing the same square in
  Tic-Tac-Toe), resolvable with an ordinary "first valid move this round
  wins" host-side rule per game, not a generic merge engine.
- **Encryption.** Same threat model already established for LAN play
  elsewhere in this repo: a shared classroom drive is a trusted
  environment, not a hostile one.

## Tutorial: outline (Tutorial 10, in-app)

The in-app Tutorials panel (`Tutorials/index.json` + one numbered folder of
HTML pages per lesson, `Tutorials/<lang>/<folder>/` for translations) is the
right home, not a new document type — it's where every other "build a game
step by step" lesson already lives (01 through 09, none of which have a
matching bundled sample either, per above). Proposed:

- **Folder**: `Tutorials/10_file_exchange_multiplayer/` (next free number).
- **Title** (working): "Turn-Based Multiplayer: Tic-Tac-Toe by File
  Exchange."
- **Thumbnail**: `Tutorials/thumbnails/10_file_exchange_multiplayer.png`
  (new art, or a simple rendered board — small enough to defer to whoever
  actually builds this).
- **Intro page**: "What We'll Build" (two-player Tic-Tac-Toe, one machine
  hosts, one joins, moves exchanged through a shared folder instead of a
  live connection), the short historical callout from the section above,
  "How This Tutorial Works" phase list, "What You'll Learn" (the action
  names from "Proposed action surface").
- **Phase 1 — The board, no networking yet.** Nine cells' worth of shared
  state as plain instance/global variables, drawn as a 3x3 grid;
  mouse-click marks a cell with `X`. Entirely local and testable alone —
  matching every other Tutorial's own "make the simplest visible piece
  work first, before adding the harder mechanic" phase-1 philosophy.
- **Phase 2 — Host a game / Join a game.** Introduce `host_game_files`/
  `join_game_files`, a "Waiting for opponent…" message gated on
  `global.player_count`, and reading `global.player_id` to know whether
  this machine is `X` or `O`.
- **Phase 3 — Taking real turns.** Gate clicking on whether it's this
  player's turn (`global.round_number` parity, or an explicit shared
  `whose_turn` var), submit the chosen cell via `set_shared_var` +
  `end_turn()`, react to `round_resolved` to redraw the board once the
  host has published the new state — the phase that actually exercises
  the file-exchange round-trip end to end.
- **Phase 4 — Winning and playing again.** A short win-check expression
  (three in a row, any of 8 lines), an announcement via `show_message`,
  and `leave_game_files` / starting a fresh round.
- **Translation — DECIDED: French ships on day one, not deferred.**
  This repo's established bar is an English + French guide at minimum
  for anything bundled (matching every sample's `README.md`/
  `README.fr.md` and the "guides get translated, authored in-game
  *messages* don't" split from the 2026-07-20 session note); the user
  has now confirmed Tutorial 10 follows that bar from the start rather
  than trailing English the way some other languages have. A full
  Tutorial is markedly more prose than a sample README, so budget it
  as real, sizeable effort — the 09_catch_the_coins-scale precedent
  plus the documented "~40% of a session per language" cost from the
  i18n arc — folded into Phase 3 itself (see below) rather than a
  follow-up phase.
- **Edition whitelist**: `config/editions.py`'s beginner edition currently
  whitelists Tutorials 1–4 only. Given every other multiplayer sample
  (`multiplayer_lan_1`, `reseau_1`–`4`) is deliberately excluded from the
  beginner edition as advanced material, Tutorial 10 should be excluded
  the same way rather than added to that whitelist — a decision to make
  explicitly at Phase 3, not a default to silently fall into.

## Proposed phases

Sized the same way `docs/MULTIPLAYER_LAN_V2_PLAN.md` was: one phase per
review/commit boundary, full suite green after each, matching this repo's
"one task ≈ one commit" discipline throughout.

1. **DONE (2026-09-10) — Core session + shared blackboard, desktop only,
   no UX polish.** `extensions/multiplayer_files/{state,fileio,session,
   handlers,actions}.py` (a `fileio.py` transport module, not anticipated
   in the original file list, split out the atomic-write/read primitives
   from the protocol logic in `session.py` — the same split
   `multiplayer_lan/network.py` vs `session.py` already uses).
   `host_game_files`/`join_game_files`/`leave_game_files`, join/welcome
   handshake, `set_shared_var_files`/`get_shared_var_files`/`end_turn`
   (renamed from the originally-proposed `set_shared_var`/
   `get_shared_var` — see "Proposed action surface" above), round
   advancement with a deadline, the identity/status globals, all five
   events above (not four — the doc text above this phase historically
   undercounted; all five cost nothing extra to implement together).
   Folder path is an explicit action parameter (a plain string) — no
   picker yet. Action display names translated into all 10 shipped
   languages in the same commit
   (`tests/test_extension_action_i18n.py`), matching the bar
   `multiplayer_lan` and Block World's crafting actions were already
   held to.
   **Testing**: `tests/test_multiplayer_files_session.py` (17 tests,
   pure protocol against a real `tempfile.TemporaryDirectory()` — join/
   welcome, multi-client, round resolution, last-write-wins merge order,
   deadline skip, leave, file_session_lost, a slow-filesystem simulation
   via a monkeypatched I/O delay, and the poll-interval gate) +
   `tests/test_multiplayer_files_tier_a.py` (12 tests, the full action/
   event/globals wiring through a real `ActionExecutor` and room-change
   migration). 29 new tests; full suite 4731 passed / 10 skipped (two
   raycast timing-sensitive smoke tests flaked under the full-suite load
   and passed clean in isolation — CLAUDE.md's own documented flake
   class for that file, not a regression).
2. **DONE (2026-09-10) — `send_network_message_files` + the bundled
   sample.** `send_network_message_files(event, data, target)` staged
   the same way `set_shared_var_files` is, folded into the round the
   same way, and fired on every machine as a new event --
   `network_message_files`, not `network_message`, for the identical
   plugin_loader collision reason the two `..._files` actions were
   renamed in Phase 1 (see "Proposed action surface" above).
   `samples/fichier_1` ("File Exchange — Tic-Tac-Toe"): the finished,
   polished Tic-Tac-Toe sample, host is X, joiner is O, `h`/`j`
   keyboard-press hosts/joins straight from Test Game (the reseau_4
   pattern), turn order from `global.round_number`'s parity, the
   non-active player calls `end_turn()` every round with nothing staged
   so the round resolves promptly instead of idling out the deadline.
   Registered in `tools/smoke_run_samples.py` and `widgets/welcome_tab.py`
   `SAMPLE_PROJECTS` (English source label, translated into all 10
   shipped languages in the same commit — this extension's Welcome-tab
   entry does NOT repeat the French-first mistake `multiplayer_lan`'s
   own actions originally shipped with); `fichier` added to the
   advanced-prefix tuple in `tests/test_edition_sample_filter.py` to
   keep it out of the beginner edition. README.md + README.fr.md.
   **Two real bugs found by actually playing a full game through two
   real `GameRunner` instances (not by reading the code), both fixed
   rather than worked around:**
   - `FileSession` never republished `session.json` when a player
     joined outside of a round resolving — a client's own
     `global.waiting_for_players` stayed stuck at "still waiting" even
     after it had already joined itself, which deadlocks completely the
     moment gameplay (reasonably) gates on that global reaching 0,
     since the round that would have refreshed it never gets permission
     to start. Fixed in `session.py`'s `_host_poll`: a join/leave now
     publishes immediately, not just at the next round resolve.
   - The sample's first win-check only tested "did *my own* mark win",
     so the *losing* player's own instance never learned the game had
     ended at all — the winner's message showed correctly and the
     loser's screen simply never said anything. Fixed by checking both
     marks' win lines on every machine regardless of `my_mark`, mirrored
     in the README's "How it works" section as a worked design note.
   `tests/test_fichier_1_sample.py` (13 tests): the H/J authoring is
   present and correctly assigns marks, a full game played to an X win
   with both machines agreeing on the outcome, a full game played to a
   draw, and an out-of-turn click correctly ignored — all driven through
   two real `GameRunner` instances over a real
   `tempfile.TemporaryDirectory()`, the same "real engine, not mocked
   classes" discipline `test_reseau_4_sample.py` established.
3. **Tutorial 10** (see "Tutorial: outline" above): the four build phases
   as HTML pages, the intro page (including the short historical callout),
   `Tutorials/index.json` entry, a thumbnail, **and the French
   (`Tutorials/fr/10_file_exchange_multiplayer/`) translation shipped in
   the same phase, not a follow-up** — decided, not deferred; budget the
   phase accordingly (see "Effort estimate"). Exclude from the beginner
   edition's `tutorial_folders` whitelist, matching the sample's own
   exclusion in the same phase. Regression coverage mirrors
   `tests/test_tutorial_panel_i18n_verification.py`'s existing pattern:
   drive the real `TutorialPanel` through every page of the new lesson
   **in both languages** and assert none of the widget's own error/
   placeholder branches fire.
4. **Connect-screen UX**: a pygame folder-path entry + waiting-room
   screen, mirroring `connect_screen.py`'s shape. Still no folder
   *browsing* (out of scope above) — typed/pasted path, validated for
   existence and writability with a clear on-screen error if not.
5. **Manual QA on real hardware**: two machines against a real school (or
   at least a real Windows-share-mounted) drive, not just a local temp
   directory — the specific risks this whole plan exists to catch
   (SMB caching staleness, transient lock retries under real contention,
   actual round-trip latency) can't be proven by a fast local filesystem
   test alone. This mirrors every other multiplayer arc's own "still
   needs human eyes on real hardware" standing caveat.

Export parity (HTML5/Kivy) and a folder browser are explicitly **not**
phases here — see "Explicitly out of scope."

## Effort estimate

Smaller than `multiplayer_lan` v2 was on the *extension* side, on account
of no wire-protocol class of bug to chase (JSON files, not raw
sockets/framing) and testing being markedly easier (a real temp directory
beats mocking a network stack) — but the added Tutorial phase is real,
separate writing effort on top of that, not a rounding error. A rough
guess, in the same spirit as v2's own estimate table but not to be trusted
more than that: Phase 1 a session or two, Phase 2 (sample) a session,
Phase 3 (Tutorial) a session for English plus close to a full additional
session for French shipping alongside it on day one (matching the
documented ~40%-of-a-session-per-language cost from the i18n arc, applied
to a lesson roughly `09_catch_the_coins`-sized) — call it two sessions for
Phase 3 as currently scoped, not one, Phase 4 (UX) a session, Phase 5
(real hardware) needs the user and a second machine, not just agent time.

## Splitting the work across two machines

The five phases above split cleanly into two independent tracks — an
**Engine track** (the extension + sample + UX) and a **Teaching track**
(the wiki page + Tutorial 10) — because the plan already made the two
concrete deliverables independent of each other on purpose (see "The
concrete game" above: sample and Tutorial each build Tic-Tac-Toe from
scratch, neither depending on the other's code). That same independence
is what lets two computers work at once without stepping on each other.

- **Track E (Engine)** — Phase 1 (core session + blackboard) → Phase 2
  (`send_network_message` + the bundled sample) → Phase 4 (connect-screen
  UX), then joins Track T for Phase 5.
- **Track T (Teaching)** — `wiki/FileExchange.md` + `wiki/FileExchange_fr.md`
  (the historical-grounding content, plus whatever `Home.md`/`Network.md`/
  `Extensions.md` cross-links point at it) → Tutorial 10, English pages
  first, then the French folder shipping alongside them (see "Effort
  estimate" — budget it as its own two sessions' worth, not one), then
  joins Track E for Phase 5.

**Why Track T doesn't have to wait on Track E.** The Tutorial's HTML pages
are static teaching content, not code that imports the extension — writing
them, and the wiki page, only needs the **"Proposed action surface"**
section above as a stable name/parameter contract to write examples
against, not working code. `tests/test_tutorial_panel_i18n_verification.py`'s
pattern (extended for Tutorial 10) drives the `TutorialPanel` widget
through every page and checks none of its own error/placeholder branches
fire — it never executes a sample project's actions, so it can go green
before Track E's implementation exists at all.

**The one real coupling point, and how to handle it.** If Track E's actual
implementation ends up wanting a different action name or parameter than
what's written in "Proposed action surface" (a realistic outcome — the
real shape of an API is often clearer once it's half-built), that changes
what Track T is teaching too. Handle it the same way a two-machine session
handles any shared decision: whichever track changes the surface edits
this doc's "Proposed action surface" section in the same commit as the
code change and says so when the two sessions next sync, and Track T does
one deliberate pass reconciling the Tutorial's code snippets against the
real landed API before treating Phase 3 as done — not a running
line-by-line sync the whole time.

**File ownership, to keep both tracks pushing straight to `main` (no
feature branches, per this repo's standing convention) without fighting
over the same file:**

| Track E owns | Track T owns |
|---|---|
| `extensions/multiplayer_files/**` | `wiki/FileExchange.md` + `_fr.md` (+ cross-links in other wiki pages) |
| `samples/<name>/**` + its generator script | `Tutorials/10_file_exchange_multiplayer/**` + `Tutorials/fr/10_file_exchange_multiplayer/**` |
| the sample's `README.md`/`README.fr.md` | `Tutorials/thumbnails/10_file_exchange_multiplayer.png` |
| its own addition to `tools/smoke_run_samples.py` | its own addition to `Tutorials/index.json` |
| its own addition to `tests/test_edition_sample_filter.py`'s advanced-prefix tuple | its own exclusion added to `config/editions.py`'s `tutorial_folders` whitelist |
| — | its extension to `tests/test_tutorial_panel_i18n_verification.py` |

No file above is written by both tracks, so ordinary frequent
commit-and-push (this repo's existing "one task ≈ one commit, push after
each" discipline, applied per-track rather than per-session) should merge
without conflicts — each machine should still `git pull` before starting
a work unit and push right after finishing it, the same discipline either
track would follow solo.

## How to decide

This is genuinely optional, scoped work with a real, if narrower, use
case than the existing socket-based extension — a turn-based classroom
game that needs to survive a firewall the LAN extension can't get through,
now explicitly paired with the teaching material (Tutorial + historical
context) to go with it, not just the raw capability. It does **not**
replace anything and risks nothing in what already ships. Both design
questions that were open at the start are now decided: the sanitizers got
**duplicated**, not imported, into `multiplayer_files/state.py` (see
"Reused pieces" above), and **French for Tutorial 10 shipped on day one**
(Track T, Phase 3). Track E (Phases 1–2, the extension + sample) and
Track T (the wiki page + Tutorial) are both individually done — the one
remaining item is the **reconciliation pass**: Track T's content still
describes the `..._files`-unrenamed action surface and doesn't mention
`send_network_message_files`/`network_message_files` at all, so before
either the wiki page or Tutorial 10 can be considered finished, someone
needs to diff them against `extensions/multiplayer_files/actions.py` /
`__init__.py` (the actual, current source of truth) and fix the drift —
smaller than either track's own original work, and doesn't need two
machines, just one pass reading both sides. After that: Phase 4
(connect-screen UX) and Phase 5 (real-hardware QA) are what's left on
Track E; see "Proposed phases" and "Splitting the work across two
machines" above for the full breakdown.
