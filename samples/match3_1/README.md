# Match-3 — Level 1

A minimal, complete match-3 (three-in-a-row) puzzle game. This is the
first pygm2 sample **authored natively in the IDE's own project format**
— the maze and platform samples were imported from GameMaker 8.x `.gmk`
files; this one was written directly against the pygm2 runtime.

It is deliberately small: one room, one object, no scripts, no sounds.
The whole game lives in four events of a single controller object, which
makes it the reference sample for the `execute_code` action and for
draw-queue rendering. More advanced versions (sprite-based tiles, sound,
levels) are planned as `match3_2` etc. — see *Roadmap* below.

## How to play

- **Click** a tile to select it (white outline), then **click an
  adjacent tile** to swap the two.
- If the swap lines up **3 or more same-colored tiles** in a row or
  column, the matched tiles blink for a moment, are destroyed, and the
  tiles above **slide down** to fill the gap; new tiles drop in from the
  top of the board.
- Chain reactions ("cascades") resolve wave by wave, each with its own
  blink-and-slide animation.
- A swap that produces no match is reverted immediately.
- Every destroyed tile is worth **10 points**; reach **500 points** to
  win.

## Project structure

| File | Purpose |
| ---- | ------- |
| `project.json` | project manifest — 800×800 window, 60 fps (`room_speed`), startup room `rm_match3` |
| `rooms/rm_match3.json` | the single room; contains one instance of `obj_GridManager` at (0, 0) |
| `objects/obj_GridManager.json` | the entire game: four events, each a single `execute_code` action |
| `sprites/spr_red|blue|green|yellow.*` | 32×32 tile squares — **not used yet**; reserved for the sprite-based follow-up (see `CREDITS.txt`) |

There is no player object and no per-tile object: the board is pure
data (a 6×6 list of color indices) owned by one invisible controller
instance, and everything on screen is drawn by that controller's `draw`
event through the runtime draw queue (`self._draw_queue`).

## How the code works

All state lives on the controller instance (`self.…`), created in the
`create` event:

| Attribute | Meaning |
| --------- | ------- |
| `grid` | 6×6 list of ints 0–3 (indices into `palette`); seeded with no pre-existing matches |
| `sel` | currently selected cell `(gx, gy)` or `None` |
| `marked` | set of cells currently matched and blinking |
| `flash` / `flash_total` | frames left of the blink phase / its length (36 frames ≈ 0.6 s at 60 fps) |
| `falling` | dict `(gx, gy) → pixels` — how far above its resting cell each sliding tile currently is |
| `fall_speed` | slide speed in pixels per frame (12 → one 96 px row in ~0.13 s) |
| `score`, `target`, `won` | scoring state (win at 500) |
| `find_matches` | helper function (defined in `create`, stored on the instance) that scans the grid and returns the set of all matched cells |

The game is a small state machine driven by the `step` event:

```
idle ──(click swaps, match found)──▶ FLASH (marked blink, 36 frames)
                                        │ tiles destroyed, score added
                                        ▼
                                      FALL (offsets shrink 12 px/frame)
                                        │ landed → re-scan grid
                             new match ─┴─ no match
                                 │            │
                                 ▼            ▼
                               FLASH        idle
```

- **`create`** — builds the starting grid (rerolling any tile that would
  complete an immediate match), initializes the state above, and defines
  `find_matches`.
- **`mouse_left_press`** — selection/deselection logic; on an adjacent
  swap it applies the swap, and either arms the flash (`marked`,
  `flash`) or reverts. Input is ignored while a flash or fall is in
  progress, and after the game is won.
- **`step`** — counts the flash down; on expiry it credits the score,
  rewrites each affected column to its final layout, and records a pixel
  offset in `falling` for every tile that moved (surviving tiles get
  `rows_dropped × 96`; refill tiles enter from above the board). While
  `falling` is non-empty it shrinks every offset by `fall_speed`; when
  everything has landed it re-scans for cascade matches and either
  re-arms the flash or returns to idle.
- **`draw`** — draws the board panel, then every tile at
  `rest_position − falling_offset`. Tiles above the board's top edge are
  clipped (partially emerged) or skipped (fully hidden), so refills
  appear to slide in from under the header. Marked tiles blink white
  every 6 frames and carry a white outline; the selection, score line,
  instructions, and the win banner are drawn last.

### Things to tweak

- Board size: `self.cols` / `self.rows` (the layout constants `ox`,
  `oy`, `tile` control placement — a 6×6 board of 96 px tiles fits the
  800×800 window).
- Colors / tile kinds: `self.palette` (add a tuple to get a 5th color;
  the reroll logic and renderer pick it up automatically, but update
  `random.randrange(4)` in `create` and `step`).
- Difficulty: `self.target` (points to win), `flash_total`,
  `fall_speed`.

## Roadmap (planned advanced versions)

- **match3_2** — draw the tiles with the bundled sprites instead of
  color rectangles; add sound effects for swap/match/cascade; swap
  animation.
- **match3_3** — move limit or timer, multiple rooms as levels with
  rising targets, special tiles (4/5-in-a-row bonuses).

The versions are meant to mirror the maze_1→3 progression: each one a
readable diff over the previous.

## Export status

- **Test Game (F5) / desktop:** works — the game runs on the standard
  pygame runtime. It is exercised headlessly in CI-style smoke runs via
  `tools/smoke_run_samples.py`.
- **Android (.apk) / Mobile (Kivy):** **supported** (as of 2026-07-03).
  The exported Kivy runtime renders the game's draw queue (rectangles and
  text, with the y-axis converted to Kivy's bottom-up frame), dispatches
  taps as the `mouse_left_press` event with room-coordinate
  `mouse_x`/`mouse_y` on both Android (inverting the fullscreen scaling
  transform) and desktop Kivy, and — since this game has no keyboard
  events — omits the virtual D-pad overlay that would otherwise cover the
  bottom-right of the board. The exported game is exercised headlessly in
  `tests/test_kivy_draw_queue_mouse_export.py`, which plays a full
  swap → flash → slide round through the generated code. Building the
  actual `.apk` additionally requires buildozer (via WSL on Windows) —
  see [`docs/ANDROID_EXPORT.md`](../../docs/ANDROID_EXPORT.md) for the
  full guide (setup, build times, classroom/session caching); remaining
  Kivy-export parity gaps that do *not* affect this game are listed
  under "Kivy/Android export" in the repository `TODO.md`.
- **Other targets (HTML5, standalone zip):** untested with this sample.
