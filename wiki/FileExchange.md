# File Exchange Multiplayer

*[Home](Home) | [Network](Network) | [Extensions](Extensions)*

---

> **Not shipped yet.** This page documents the planned design
> (`docs/MULTIPLAYER_FILE_EXCHANGE_PLAN.md`) so it's ready the moment the
> extension lands. **Do not publish this page (or the cross-links to it on
> Home/Extensions/Network) to the live wiki until `extensions/multiplayer_files/`
> actually exists and this note is removed.**

---

PyGameMaker can also turn a project into a **turn-based multiplayer game
that exchanges state through files on a shared drive**, instead of a live
network connection. This is a good fit for a school where [LAN
Multiplayer](Network)'s direct machine-to-machine connection is blocked by
a firewall (common on a managed "Public" network profile), but the
classroom's shared drive is already open to every machine. This is
provided by the **File Exchange Multiplayer** [extension](Extensions).

The bundled sample **Tic-Tac-Toe by File Exchange** is a complete, playable
example: two players take alternating turns, each move written to a file on
the shared drive and picked up by the other machine.

Supported today: the **desktop** (pygame) export only, as host or client.
See "Why not every export" below for why HTML5 and Kivy/Android don't have
this extension.

---

## How it's different from LAN Multiplayer

[LAN Multiplayer](Network) polls a live socket connection roughly 60 times
a second — perfect for a shared avatar moving smoothly around a room, but
it needs a direct connection between machines that some school networks
block outright.

File Exchange Multiplayer instead reads and writes small files on a shared
network drive — the same drive both machines already use for their own
files, which is almost always left open even when direct peer-to-peer
connections aren't. It checks for a new turn roughly once a second, not
once a frame, because a real network-drive read/write can take anywhere
from a few milliseconds to much longer depending on the school's server —
smooth continuous movement isn't possible this way, only **turn-based**
play: a quiz, Tic-Tac-Toe, Battleship, a negotiation game — anything where
one player acts, then waits for the others.

**Use LAN Multiplayer when** you want avatars moving around live. **Use
File Exchange Multiplayer when** turns are fine and you need to work
around a school firewall.

---

## Where this idea comes from

Exchanging a game's state through files, instead of a live connection, is
not a new idea — it's how a whole genre of multiplayer games worked before
always-on internet connections were common:

- **Play-by-mail (and later play-by-email) games**, going back decades,
  are the true origin: a human or computer "judge" collected every
  player's mailed-in move, processed them together, and mailed back the
  results. Nobody needed to be online — or even awake — at the same time.
- **VGA Planets** (1992) and **Stars!** (1995), two classic DOS/Windows
  strategy games, automated exactly that process: each player's turn
  produced a small file, a "host" program combined everyone's files into
  a result for the next turn, and players exchanged files by floppy disk,
  modem, or later email — the file *was* the whole protocol.
- Dial-up bulletin board (BBS) door games like *Trade Wars 2002* and
  *Legend of the Red Dragon* used a related idea — each player's turn was
  recorded and read back later by whoever needed it, whenever that was,
  rather than everyone needing to be connected at once.

File Exchange Multiplayer modernizes the same core idea onto a shared
classroom drive, with both players' games already running at the same
time: **each player's move is its own file, and no two players ever write
the same file** — so there's never a race to worry about, the same
protection the original play-by-mail games got for free by only ever
being read one letter at a time.

---

## How it works

- One player calls **Host Game (Files)**, pointing it at a shared folder
  both machines can reach. This machine becomes the **host** and referee
  for the game.
- Other players call **Join Game (Files)** with the same folder. If the
  host can't be reached, **the game keeps running single-player**, the
  same promise [LAN Multiplayer](Network) makes.
- Each round, every player writes their move to their own file and calls
  **End Turn**. Once the host has every player's move (or a wait limit
  passes), it publishes the new game state for everyone to read.
- Player identity and round status are always readable as globals:
  `global.is_host`, `global.player_id`, `global.player_count`,
  `global.round_number`, `global.turn_ready`, `global.waiting_for_players`.
- A shared variable set with **Set Shared Variable** becomes readable
  *everywhere* as `global.<name>` — but only once the host publishes the
  next round, not instantly the way [LAN Multiplayer](Network)'s version
  is. Your own change doesn't jump ahead on your own screen either.

---

## The actions

| Action | What it does |
|--------|--------------|
| **Host Game (Files)** | Become the host; create/claim the shared game folder. |
| **Join Game (Files)** | Connect to a host's shared folder. |
| **Leave Game (Files)** | Stop playing; leaves the other players' files untouched. |
| **Set Shared Variable** | Stage a variable to publish with your next turn. |
| **Get Shared Variable** | Copy a shared variable into a global (for use in a calculation). |
| **End Turn** | Submit everything staged this round as your move. |
| **Send Network Message** | Attach a small custom event to your next turn. |

See the [Full Action Reference](Full-Action-Reference) for every parameter.

## The events

| Event | Fires when |
|-------|------------|
| **File Session Started** | A client finishes connecting to the host's shared folder. |
| **Player Joined (Files)** | A new player's join request is accepted. |
| **Round Resolved** | The host has published a new round's state and this machine picked it up. |
| **Player Skipped Round** | A player's turn wasn't submitted before the round's wait limit passed. |
| **File Session Lost** | The shared folder became unreadable (drive disconnected, permissions changed). |

---

## A minimal Tic-Tac-Toe turn (host-authoritative rounds)

In a room-controller object:

- **Create:** `Host Game (Files)` pointing at the shared folder, if this is
  the teacher's machine, else `Join Game (Files)` with the same folder.
- On a cell click, gated on `global.turn_ready` and it being this player's
  turn: `Set Shared Variable` recording the chosen cell, then `End Turn`.
- **Round Resolved:** redraw the board from the published shared
  variables, and check for a win.

---

## Why not every export

**HTML5** — a browser page can't write to an arbitrary shared drive path
at all without extra permissions a school computer lab is unlikely to have
granted, so this extension doesn't attempt it there.

**Kivy/Android** — writing to a network share from a phone or tablet app
runs into the same modern storage restrictions, and a mobile device is
often not even on the same local network as the shared drive in the first
place.

Both restrictions are the same shape [LAN Multiplayer](Network) already
has for its own export limits — see [Network](Network)'s own "Supported
today" note.

---

## Notes and limits

- **A shared network drive both machines can already write to** — no
  internet, no server, no port to open, but it does need that shared drive
  to actually be reachable and writable from both machines.
- **Turn-based only.** There's no way to move something smoothly with
  this extension — that's what [LAN Multiplayer](Network) is for.
- **The host is authoritative.** If two players' moves genuinely conflict
  (choosing the same square, say), the host's game logic decides — the
  same "first valid move wins" rule an ordinary hot-seat game would use.
- If the File Exchange Multiplayer extension is **disabled**, these
  actions and events simply do nothing — see [Extensions](Extensions).

---

## See Also

- [Network](Network) — the live-connection sibling, for games that need
  smooth real-time movement
- [Extensions](Extensions) — how File Exchange Multiplayer ships and how
  to turn it off
- [Full Action Reference](Full-Action-Reference) — every action and
  parameter
- [Event Reference](Event-Reference) — the File Exchange events in context
