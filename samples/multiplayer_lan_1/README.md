# LAN Multiplayer — Demo

A minimal demo of the **LAN Multiplayer** extension
(`extensions/multiplayer_lan/`) — a blue square you move with the arrow
keys, and a second, separate launch of the exact same project that watches
it move live over your local network.

## Controls

| | |
|---|---|
| Arrow keys | Move the square around the room |

## What it demonstrates

This project's own `obj_player` has **no multiplayer authoring in it at
all** — no `set_network_mode` action, nothing. That's the point: run it
normally (`python3 runtime/run_game.py samples/multiplayer_lan_1/project.json`,
or Test Game from the IDE) and it's an ordinary single-player square-mover
with no networking. LAN play is switched on purely from the command line,
with two separate launches of the same project:

```bash
# Terminal 1 — the host (this one controls the square with the arrow keys)
python3 runtime/run_game.py samples/multiplayer_lan_1/project.json en --net-host

# Terminal 2 — a client on the same machine or LAN (127.0.0.1 for the same machine)
python3 runtime/run_game.py samples/multiplayer_lan_1/project.json en --net-client 127.0.0.1
```

The client window mirrors the host's square in real time. **The client is
a pure spectator in this first version** — its own arrow-key presses don't
move anything permanently, since every network snapshot from the host
overwrites the synced instance's position again the very next frame. That
matches the extension's own documented scope (see
`docs/MULTIPLAYER_LAN_PLAN.md`'s "Explicitly out of scope"): this is "see
where the other player is," not a two-way authoritative simulation —
turning the client into a second controllable player is real future scope,
not a corner cut here.

If you'd rather wire up an in-game "Host" / "Join" menu instead of the
command line, the same functionality is available as the `set_network_mode`
action (`mode`: host/client, `host`, `port`) — call it from a menu object's
own logic instead of relying on the CLI flags.

## Engine status

**Desktop only.** LAN multiplayer has no HTML5 or Kivy (Android) export
support yet — see `docs/MULTIPLAYER_LAN_PLAN.md`'s scope notes. This
sample is not included in the HTML5/Kivy export test matrix for that
reason.
