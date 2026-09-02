# Réseau — Récolte en équipe (reseau_3)

A networked-instances (Tier B) LAN multiplayer game: **everyone drives
their own avatar, collects shared gems for a team score, and dodges a
host-simulated monster.** Builds directly on `reseau_1`'s avatar pattern,
adding host-authoritative collectibles and a simple enemy.

## Run it

You need **two or more machines on the same wired LAN** (or two windows
on one machine for a quick test). Launch the game, then:

- **Host**: press **H**. A lobby appears — wait for players, then click
  "Démarrer". Hosting also spawns the host's own avatar, the monster,
  and 5 gems.
- **Each other player**: press **J** to open the server browser (or type
  the host's address directly).

Move with the **arrow keys**. Walk into a gem to collect it (+1 to the
shared team score); walking into the monster costs the team a point.

## How it works

| Object | Role |
|---|---|
| `obj_ctrl` | Invisible controller. Spawns the host's avatar + the monster + 5 gems once hosting starts; spawns a new avatar for each player who joins (`player_joined`). Draws the team score and instructions. |
| `obj_person` | The avatar — same **Si je pilote cette instance** movement pattern as `reseau_1`. Its gem/monster collision handlers are guarded by `global.is_host == 1`: only the host's own simulation destroys a gem or docks a point, since collisions on a client's local ghost copies don't count. |
| `obj_gem` | Passive — no events of its own. Destroyed by `obj_person`'s collision handler (`destroy_instance`, target `other`). |
| `obj_monster` | Host-simulated left/right patrol (`step`, guarded by `global.is_host == 1`) — clients never run its AI locally; they just see the host's broadcast position, interpolated like any other synced instance. |

- **The host owns the world**, same principle as `reseau_1`: only the
  host calls `network_spawn`, and every gameplay-affecting action
  (destroying a gem, adjusting the score, moving the monster) is guarded
  by `global.is_host == 1`. Movement stays responsive for everyone
  because each player's own avatar is simulated locally on their own
  machine (client-authoritative for your own avatar only).
- **Why the monster doesn't teleport a hit player back to start**: on
  the host, a *client-owned* avatar's position is still reported up from
  that client every frame — the host teleporting it locally would just
  get overwritten by the client's next report. Docking a shared score
  point sidesteps that fight entirely while still making contact feel
  costly.

## Things to try

- Add more gems, or respawn a collected gem after a delay instead of
  destroying it permanently.
- Give the monster a second patrol axis (up/down as well as left/right),
  or have it chase the nearest avatar instead of pacing a fixed route.
- Add a win condition: once `global.team_score` reaches a target,
  `send_network_message` a `"victoire"` event to celebrate on every
  screen.

## Notes for teachers

- Ports used: **45782/TCP** (game) and **45783/UDP** (discovery). Ask IT
  before using on a managed network.
- **Wired labs work best.** Many school Wi-Fi access points block
  device-to-device traffic, which stops LAN multiplayer entirely.
- This is the more action-oriented of the `reseau_*` samples — a good
  second session once `reseau_1` (movement) and `reseau_2` (no movement
  at all, most Wi-Fi-tolerant) have both gone well.
