# File Exchange — Tic-Tac-Toe (fichier_1)

A two-player Tic-Tac-Toe game played over the **File Exchange
Multiplayer** extension (`extensions/multiplayer_files/`) instead of a
live network connection — moves are exchanged through ordinary files on
a shared folder. See [the wiki page](../../wiki/FileExchange.md) for the
full design and the 1990s history (VGA Planets, Stars!, play-by-mail
Diplomacy) this pattern comes from.

Unlike **reseau_1**–**reseau_4** (`extensions/multiplayer_lan/`, a live
socket connection), this sample never opens a network port at all — it
works through a school firewall that blocks direct machine-to-machine
connections, as long as both machines can already reach the same shared
drive.

## Run it

Two machines that can both reach the same shared folder (a mapped
network drive, a synced Dropbox/OneDrive folder, ...) — or one machine
with two Test Game windows for a quick local check.

1. **Both machines:** open this sample and press **Test Game** (F5).
2. On one machine, press **H** to host — you play **X**.
3. On the other, press **J** to join — you play **O**.
4. Click a cell on your turn. The bottom of the window shows whose turn
   it is.

By default both actions point at a folder named `tictactoe_files`,
created next to wherever the game is run from — fine for a one-machine
test. **For real two-machine play**, open `obj_game`'s `h`/`j` keyboard
events and change the **Shared folder** parameter on both `Host a Game
(File Exchange)` and `Join a Game (File Exchange)` to the *same* real
path both machines can reach (for example a mapped drive letter, or a
UNC path like `\\server\share\tictactoe`).

## How it works

| Object | Role |
|---|---|
| `obj_game` | Everything — the sole instance in the room. Its `h`/`j` keyboard events call `Host a Game (File Exchange)` / `Join a Game (File Exchange)` and fix this machine's mark (host is always X, the joining player always O). Its **Step** event works out whose turn it is from `global.round_number`'s parity and, on the machine that is *not* on turn, calls `End Turn (File Exchange)` with nothing staged — a "pass" — so the round still resolves promptly instead of waiting out the full `round_deadline`. |

The board is nine shared variables (`cell_0_0` … `cell_2_2`, column then
row), each set with `Set a Shared Variable (File Exchange)` and
published to the other machine only once `End Turn (File Exchange)` is
called and the host folds the round together — the file-exchange
extension's whole reason for existing: writes only ever take effect at
the next published round, never instantly, since there is no live
connection to write over.

Both machines evaluate the win check independently against the same
published board (checked for *both* marks, not just "did my own mark
win" — a losing player needs to be told the game ended too), and a full
board with no line evaluates as a draw.

## Things to try

- Add a rematch: on `won == 1`, call `Leave the Game (File Exchange)`
  and reset `won`/`my_mark`/the cell variables, so pressing H/J again
  starts a fresh game without restarting the whole sample.
- Send a custom `Network Message (File Exchange)` when a player wins
  (`target = all`) and have the losing machine react to it with a
  different message than its own board-based loss detection — a taste
  of `send_network_message_files` beyond the shared board itself.
- Widen the board to 4×4 (needs `win a line of 3 anywhere` rather than a
  full row/column/diagonal) as a bigger win-check exercise.

## Notes for teachers

- **No ports, no firewall exception needed** — the whole point of this
  extension. If `reseau_*`'s LAN multiplayer gets blocked by school IT,
  this is the fallback: it only needs read/write access to a shared
  drive the classroom already uses.
- **The shared folder must be real and reachable from both machines** —
  unlike LAN multiplayer's auto-discovery, there is no "auto" option
  here yet (Phase 4 of the plan). Point both machines at the exact same
  path.
- A round can take a few seconds to resolve on a slow or heavily-loaded
  network drive — the extension polls once a second, not every frame,
  by design (see the wiki page's "why this is a different thing from
  LAN Multiplayer").
- Desktop only (no HTML5 / Android export for this extension).
