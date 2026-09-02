# Network (LAN Multiplayer)

*[Home](Home) | [Full Action Reference](Full-Action-Reference-Network-Actions) | [Extensions](Extensions)*

---

PyGameMaker can turn a project into a **LAN multiplayer game**: one machine
hosts, others join over the local network, and players share state — a
scoreboard, custom messages, and even each other's on-screen avatars — with
no server, no account, and no internet required. This is provided by the
built-in **LAN Multiplayer** [extension](Extensions), which ships enabled.

The bundled samples **`reseau_1`–`reseau_3`** are complete, playable
examples: a shared room where two players move around together, a classroom
quiz with a live scoreboard, and a two-player co-op treasure hunt.

Supported today: the **desktop** (pygame) export, both as host and client,
and the **HTML5** export as a client (a browser page joins a desktop host;
it can't host itself). A **Kivy/Android** export runs the game
single-player — the network actions safely do nothing there.

---

## Two tiers

**Tier A — shared blackboard.** No avatars, just shared state: variables
every player can read and write, custom messages, and who's connected. This
is the simplest way to add multiplayer to a project — a quiz, a shared
scoreboard, a "first to answer" buzzer game.

**Tier B — networked instances.** Host-spawned instances (players, enemies,
pickups) that automatically appear and move on every machine, plus
player-owned avatars that each player controls locally while everyone else
sees a smoothly interpolated copy.

---

## How it works

- One player calls **Host Game**, usually from a room controller object's
  Create event. This machine becomes the **host** — every other player's
  machine connects to it. `global.player_id` becomes `0`.
- Other players call **Join Game** with the host's LAN IP address (or
  `"auto"` to show a built-in connect screen that finds hosts on the
  network automatically). `global.player_id` is assigned by the host
  (`1`, `2`, ...).
- If the host can't be reached, **the game keeps running single-player** —
  joining never blocks or crashes a game.
- Player identity and connection status are always readable as globals:
  `global.is_host`, `global.player_id`, `global.player_count`,
  `global.network_role`, `global.network_connected`.
- **Author your game logic with an ordinary "If" action**, e.g.
  `global.is_host == 1`, to gate host-only setup (like spawning enemies) —
  no special "network condition" actions are needed.
- A shared variable set with **Set Shared Variable** is readable *everywhere*
  as `global.<name>` — including on the machine that set it.
- **Custom messages** (**Send Network Message**) let you signal an event by
  name with any small piece of data attached — a buzzer press, a chosen
  answer, a "ready" flag.

---

## The actions (category **Network**)

| Action | What it does |
|--------|--------------|
| **Host Game** | Become the host. Optionally shows a waiting-room lobby with a Start button. |
| **Join Game** | Connect to a host by address (or `"auto"` for the built-in connect screen). |
| **Leave Game** | Disconnect (or stop hosting) and clear the network globals. |
| **Start Networked Game** | Host only: end the lobby and tell everyone to begin. |
| **Set Shared Variable** | Write a variable every machine can read as `global.<name>`. |
| **Get Shared Variable** | Copy a shared variable into a global (for use in a calculation). |
| **Send Network Message** | Broadcast a custom named message with data. |
| **Create Networked Instance** | Host only: spawn an instance that appears on every client. |
| **Sync This Instance** | Mark the acting instance as replicated across machines. |
| **Set Instance Owner** | Give a specific player local control of a synced instance. |
| **If I Own This Instance** | Condition: guard control logic so it only runs on the owning machine. |
| **Bind Network Input** | Map a local key to a named input the host can read. |
| **If Player Presses** | Condition (host): is a given player holding a named input? |
| **Set Sync Rate** | Tune the host's snapshot rate and clients' interpolation delay. |

See the [Full Action Reference](Full-Action-Reference-Network-Actions) for every parameter.

---

## The events (category **Network**)

Fired on every instance whose object handles them, on every relevant
machine:

| Event | Fires when |
|-------|------------|
| **Network Ready** | A client finishes connecting to the host (host does not fire this for itself). |
| **Player Joined** | A new player connects. `global.network_sender` / `global.network_player_name` name them. |
| **Player Left** | A player disconnects. |
| **Network Message** | A **Send Network Message** arrives — `global.network_event` / `global.network_data` / `global.network_sender`. |
| **Network Game Started** | The host calls **Start Networked Game**. |
| **Connection Lost** | A client's connection to the host drops. The game keeps running — only that player's ghosts are removed. |

---

## A minimal shared-room example (Tier A)

In an invisible room-controller object:

- **Create:** `Host Game` if this is the teacher's machine, else `Join Game`
  with the teacher's IP (or `"auto"`).
- **Create:** `Set Shared Variable` `round = 1` (host only, guarded by
  `global.is_host == 1`).
- Anywhere: `draw_text` showing `global.round` — every player sees the same
  value.

## A minimal shared-avatar example (Tier B)

In the player object's Create event:

- `Sync This Instance` — this instance now replicates.
- On the **host**: `Network Spawn` one player instance per connecting
  player (in a **Player Joined** handler), then `Set Instance Owner` with
  that player's number.
- Movement code guarded by `If I Own This Instance` runs only on the owning
  player's machine; everywhere else the instance is a smoothly interpolated
  ghost.

---

## Notes and limits

- **TCP, LAN only.** No NAT traversal, no internet play — both machines
  must be reachable on the same local network (a classroom Wi-Fi or wired
  lab). Client-isolated Wi-Fi (common on managed school networks) blocks
  discovery and direct connection alike; a wired lab is the most reliable
  setup.
- **Ports 45782 (TCP)** and **45783 (UDP, discovery)** — ask your school's
  IT before using this on a managed network, and expect a firewall prompt
  the first time you host.
- A browser (HTML5 export) client connects one port above the host's, e.g.
  `45783` if the host uses the default — this happens automatically.
- Host loss is graceful: a client's own gameplay continues; only other
  players' ghosts disappear, and `Connection Lost` fires so you can show a
  message.
- If the LAN Multiplayer extension is **disabled**, these actions and
  events simply do nothing — see [Extensions](Extensions).

---

## See Also

- [Extensions](Extensions) — how LAN Multiplayer ships and how to turn it off
- [Full Action Reference](Full-Action-Reference-Network-Actions) — every action and parameter
- [Event Reference](Event-Reference) — the six Network events in context
