# Réseau — Salle partagée (reseau_1)

A first LAN multiplayer game: **every player drives their own square, and
everyone sees everyone move in real time.**

## Run it

You need **two machines on the same wired LAN** (or two terminals on one
machine for a quick test).

**Host** (player 0):

```
PYGM_NET_AUTOHOST=1 python runtime/run_game.py samples/reseau_1/project.json
```

**Each other player** — replace `<HOST-IP>` with the host machine's LAN
address (shown in the host's window title, or `ipconfig` / `ip addr`):

```
PYGM_NET_AUTOJOIN=<HOST-IP> python runtime/run_game.py samples/reseau_1/project.json
```

For a one-machine test use `PYGM_NET_AUTOJOIN=127.0.0.1`.

Move with the **arrow keys**. The window title shows the connection state.

## How it works

| Object | Role |
|---|---|
| `obj_ctrl` | Invisible controller. On **Game Start** it `network_spawn`s the host's avatar (owner `0`); on **Joueur connecté** (`player_joined`) it spawns one for the new player, owner = `global.network_sender`. Also draws the instruction line. |
| `obj_person` | The avatar. Its **Step** event is guarded by **Si je pilote cette instance** (`is_instance_owner`): only the owning machine reads the arrow keys and moves it. On every other machine the same instance is a smooth interpolated *ghost* driven by the host's snapshots. |

The key idea — **the host owns the world**. Only the host runs
`network_spawn`; it assigns each avatar to a player with the `owner`
parameter. A client whose id matches an avatar's owner simulates that
avatar locally (so it feels responsive) and reports its position back to
the host, which relays it to everyone else.

## Things to try

- Add a **collision_with_obj_person** event on `obj_person`, guarded by
  `global.is_host == 1`, that pushes players apart — collisions only
  matter on the host.
- In **Joueur connecté**, `set_shared_var "scores_" + player_id` to 0, then
  give each player a point for something and `draw_text` the shared
  scoreboard on every screen.
- Give each player a colour: in `obj_person` **Create**, guarded by
  `is_instance_owner`, tint by `global.player_id`.

## Notes for teachers

- Ports used: **45782/TCP** (game) and **45783/UDP** (discovery). Ask IT
  before using on a managed network.
- **Wired labs work best.** Many school Wi-Fi access points block
  device-to-device traffic, which stops LAN multiplayer entirely — no
  software can work around that.
- If hosting fails, it is almost always the OS firewall asking to "allow
  incoming connections" — a teacher/admin may need to approve it once.
