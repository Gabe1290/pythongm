# Réseau — Salle partagée (Test Game) — reseau_4

The same idea as **reseau_1** (a shared room where every player drives
their own square and everyone sees everyone move), but you start it
**straight from the IDE's Test Game button** — no command line, no
environment variables.

## Run it

Two machines on the same **wired** LAN (or two Test Game windows on one
machine for a quick check).

1. **Both machines:** open this sample and press **Test Game** (F5).
2. On the machine that will host, press **H**. A small "waiting for
   players" screen appears — press **Démarrer / Start** when everyone
   has joined.
3. On every other machine, press **J**. Pick the host from the list (or
   type its LAN address), then connect.
4. Move your square with the **arrow keys**. The window title shows the
   connection state.

If nothing appears in the server list on step 3, type the host's address
by hand — it's shown on the host's window title (or run `ip addr` /
`ipconfig`). One-machine test: connect to `127.0.0.1`.

## How it works

| Object | Role |
|---|---|
| `obj_ctrl` | Invisible controller, placed in the room. Its **keyboard `h`** event calls `host_game` with **Salon d'attente** (`show_lobby: true`); **keyboard `j`** calls `join_game` with **Adresse de l'hôte = `auto`** (the built-in connect screen). On **Partie réseau démarrée** (`network_game_started`) it `network_spawn`s the host's avatar (owner `0`, guarded by `global.is_host == 1`); on **Joueur connecté** (`player_joined`) it spawns one for the new player, owner = `global.network_sender`. It also draws the H/J menu until connected. |
| `obj_person` | The avatar. Its **Step** event is guarded by **Si je pilote cette instance** (`is_instance_owner`): only the owning machine reads the arrow keys. On every other machine the same instance is a smooth interpolated *ghost* driven by the host's snapshots. |

The spawn is on `network_game_started`, **not** `game_start` — in this
menu-driven flow the network session doesn't exist yet when the room
starts, only after the player has pressed H or J.

## Notes for teachers

- Ports: **45782/TCP** (game) and **45783/UDP** (discovery). Ask IT
  before using on a managed network.
- **Wired labs work best.** Many school Wi-Fi access points block
  device-to-device traffic, which stops LAN multiplayer entirely.
- The first time you host, the OS firewall will likely ask to "allow
  incoming connections" — a teacher/admin may need to approve it once.
- Desktop only (no HTML5 / Android export for LAN multiplayer).
