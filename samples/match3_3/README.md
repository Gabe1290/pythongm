# Match-3 — Level 3

The move-limit / multi-level / special-tile follow-up to
[`match3_2`](../match3_2/README.md) promised in match3_1's original
Roadmap — the last of the three planned match3 versions. Same
architecture throughout: no scripts, the whole game is still four
`execute_code` events on a single controller object, just placed in three
rooms instead of one.

**Where this fits:** part of the `match3_*` family — pure-script
`execute_code`, no built-in actions, no room-level tiles, closing the
progression described in
[`../README.md`](../README.md#progression-how-each-family-is-built-not-just-how-it-plays).

**Sound & music:** 5 sound files — the 3 from `match3_2`
(`snd_swap`/`match`/`cascade`) plus 2 new ones (`snd_special`,
`snd_level_up`), all actively used via `self._sound_queue`.

## How to play

Same swap/match/cascade rules as match3_1 and match3_2, plus:

- You have a **limited number of moves** per level. A move is only spent
  on a swap that actually produces a match — an invalid swap (which
  slides back out) is free to attempt again.
- Reach the level's **target score** before you run out of moves to
  advance to the next room. Run out first and the level ends — **click
  anywhere to retry** the same level from scratch.
- **Match 4 in a row** (exactly 4) and one of the four tiles becomes a
  **line-clear special**: a white bar marks it. Match it again later
  (as part of any other match) and it clears its **entire row or
  column** — whichever direction the original 4-run ran in.
- **Match 5 or more in a row** and one tile becomes a **color-bomb
  special**: a white ring marks it. Match it again later and it clears
  **every tile of one color** across the whole board.
- There are **3 levels**, each its own room with a higher target and a
  tighter move limit. Clear level 3 to win the game.

## What's different from match3_2

| match3_2 | match3_3 |
| -------- | -------- |
| One room, unlimited moves, win at a fixed score | **3 rooms** (one per level), a **move limit** per level, and a **rising target** per level |
| A match is always fully destroyed | A run of **4** or **5+** leaves behind a **special tile** instead of destroying every cell |
| No level-to-level progression | Reaching the target calls `self.advance_level()`, which sets `self.goto_room_target` to the next room (or `self.won` on the last level) |

The core swap/flash/fall/cascade state machine, the sprite-tile drawing,
and the sound-queue triggers are otherwise unchanged from match3_2 — see
that sample's README for the full write-up of `swap_off`/`falling`/
`find_matches`.

## Project structure

| File | Purpose |
| ---- | ------- |
| `project.json` | project manifest — 800×800 window, 60 fps, startup room `rm_level1`, `room_order` = all 3 levels |
| `rooms/rm_level1\|2\|3.json` | one room per level, each containing its own instance of `obj_GridManager` at (0, 0) |
| `objects/obj_GridManager.json` | the entire game: four events, each a single `execute_code` action |
| `sprites/`, `sounds/` | gem tiles + effects, mostly copied from match3_2 (see `CREDITS.txt`); `snd_special` and `snd_level_up` are new |

There is still no per-tile object and no scripts — one controller
instance per room, created fresh (via GameMaker's usual "each room has
its own instances" rule) every time a room is entered, which is what
gives each level a clean slate for free.

## How the code works

### Level setup (new in `create`)

```python
self.room_order = ['rm_level1', 'rm_level2', 'rm_level3']
level_config = {
    'rm_level1': (300, 20),   # (target score, move limit)
    'rm_level2': (500, 18),
    'rm_level3': (800, 16),
}
```

`create` reads `game.current_room.name`, stores it on `self.room_name`
(needed because a plain local variable defined in one `execute_code`
event does **not** survive into a later event — see the landmine note
below), and sets `self.target`/`self.moves`/`self.level_num` from the
table above.

### Moves and losing (new in `mouse_left_press`)

A swap only consumes a move if `find_matches` says it will actually
match (`if marks: self.moves = self.moves - 1`), so a rejected swap that
slides back out is free. When `self.moves` reaches 0 without hitting the
target, `step` sets `self.lost = True`; `mouse_left_press` checks that
flag **first**, before the normal input guard, and turns any click into
`self.restart_room_flag = True` (the same flag `restart_room` uses),
which rebuilds the room — and with it, a fresh `obj_GridManager` instance
whose `create` event resets everything.

### Special tiles (new in `step`)

`find_matches` now returns `(marks, runs)` instead of just `marks` — each
run is `(cells_in_order, 'h' or 'v')`. At flash-expiry, **before**
scoring:

1. For every run of length ≥ 4, the **middle cell** becomes a special
   tile instead of being destroyed: length-4 runs get `('row',)` or
   `('col',)` (matching the run's orientation); length-5+ runs get
   `('color', <color index>)`.
2. For every already-marked cell that has an entry in `self.special`
   (i.e. a special tile just got caught in *this* match), its effect
   fires once: a `row`/`col` special adds its whole row/column to the
   cells being cleared; a `color` special adds every cell on the board
   of its stored color. This is a **single, non-recursive pass** — if
   one special's blast catches another special, that one is destroyed
   but does **not** chain-trigger its own effect. (A simplification, not
   a bug — keeps the effect bounded and easy to reason about.)
3. Newly-created special cells are protected from being destroyed in the
   same wave, even if a blast from step 2 would have caught them.
4. `self.special` is rebuilt from scratch each wave, following surviving
   tiles as they fall (the per-column fall loop now carries a third
   tuple element — the tile's special kind, or `None` — alongside its
   row and color) so a special tile that hasn't been matched yet slides
   down with gravity like anything else.

### Level advance (new in `create`, used from `step`)

```python
def advance_level():
    idx = self.room_order.index(self.room_name)
    if idx + 1 < len(self.room_order):
        self.goto_room_target = self.room_order[idx + 1]
        self._sound_queue.append('snd_level_up')
    else:
        self.won = True
self.advance_level = advance_level
```

`self.goto_room_target` is the same instance flag the built-in
`goto_room` action sets — the main game loop already polls it every
frame, so setting it directly from `execute_code` is enough to trigger a
real room transition, no structured action needed. `step` calls
`self.advance_level()` as soon as `self.score >= self.target`, and skips
any cascade re-scan for the rest of that frame if a room switch (or a
final win) is now pending, so a departing room doesn't keep animating.

### Landmine: closures over plain locals don't survive across events

`execute_code`'s exec environment passes **separate** globals and locals
dicts (`exec(code, exec_globals, exec_locals)`), which means it behaves
like the inside of a function: a plain top-level assignment
(`room_name = ...`) lands in the *locals* dict, but a `def` defined at
that same top level resolves its free variables through the *globals*
dict when it's later **called** — which, for a nested helper stored on
`self` (like `find_matches`, `arm_swap`, and now `advance_level`) always
happens from a **different** `execute_code` call with its own fresh
locals dict. A bare local referenced by such a helper raises `NameError`
the first time the helper is actually invoked from another event — it
looks fine in the defining event and fails silently-until-triggered
later. The fix is the one match3_1's `find_matches`/match3_2's
`arm_swap` already modeled without saying so explicitly: only close over
`self` (always present in every event's globals) or **instance
attributes** (`self.room_name`, not a bare `room_name`) — never a bare
local. Caught by the standalone-harness validation step during
development (see the audit-methodology notes in the repo's `CLAUDE.md`);
there's a regression test for it now (`tests/test_match3_3_sample.py`).

### `draw`

Same panel/board/selection/score-line/win-banner drawing as match3_2,
plus: an HUD line for level number and moves remaining, a white bar or
ring overlay on top of a special tile's sprite (skipped while the tile
is mid-blink), and an "OUT OF MOVES — click to retry" banner when
`self.lost`.

### Things to tweak

- Per-level difficulty: the `level_config` table in `create` (target
  score, move limit) — add a fourth entry and a fourth room to extend
  the sequence.
- Special-tile blast radius: the `row`/`col`/`color` branches in `step`'s
  activation loop.
- Everything match3_2 already exposed (board size, swap/fall speed,
  sound volumes).

## Roadmap

This closes match3_1's original three-part roadmap (match3_1 → match3_2
→ match3_3). No further planned versions.

## Export status

- **Test Game (F5) / desktop:** works — verified end-to-end with a real
  `GameRunner` run injecting an actual mouse click through the standard
  pygame event path: forced 4-in-a-row match → special tile created →
  target reached → **the room actually switched to `rm_level2`** with a
  fresh instance (`level_num == 2`, reset score/moves).
- **Android (.apk) / Mobile (Kivy):** relies on the same `asset_paths.py`
  / `_drain_sound_queue` / sprite-by-name fallback machinery match3_2
  added and verified — this sample doesn't exercise anything new on that
  front (no new draw-command types, no new action types; `goto_room`-via-
  flag works identically in the Kivy-exported scene loop, which already
  polls the same instance flags every frame). Building the actual `.apk`
  additionally requires buildozer (via WSL on Windows) — see
  [`docs/ANDROID_EXPORT.md`](../../docs/ANDROID_EXPORT.md).
- **Web (HTML5):** same reasoning — no new draw-queue or sound-queue
  primitives beyond what match3_2 already proved out on this target.
- **Standalone zip:** untested with this sample.
