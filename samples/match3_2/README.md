# Match-3 — Level 2

The sprite-based, animated follow-up to [`match3_1`](../match3_1/README.md)
promised in that sample's Roadmap: the same board and scoring, now drawn
with real gem sprites instead of color rectangles, with a swap slide
animation, and sound effects for swap / match / cascade. Still one room,
one object, no scripts — the whole game is still four `execute_code`
events on a single controller object.

**Where this fits:** part of the `match3_*` family — pure-script
`execute_code`, no built-in actions, no room-level tiles. See
[`../README.md`](../README.md#progression-how-each-family-is-built-not-just-how-it-plays)
for how this differs from `maze_*`/`plateforme_*`'s built-in-action,
multi-object approach.

**Sound & music:** 3 sound files (`snd_swap`, `snd_match`, `snd_cascade`),
all actively used — queued from `execute_code` via `self._sound_queue`
(see below), not the `play_sound` action.

## How to play

Same as match3_1:

- **Click** a tile to select it (white outline), then **click an
  adjacent tile** to swap the two. The swap now **slides** into place
  instead of snapping instantly.
- If the swap lines up **3 or more same-colored tiles** in a row or
  column, the matched tiles blink for a moment, are destroyed, and the
  tiles above **slide down** to fill the gap; new tiles drop in from the
  top of the board. Chain reactions ("cascades") resolve wave by wave.
- A swap that produces no match **slides back** to its original position
  instead of snapping back.
- Every destroyed tile is worth **10 points**; reach **500 points** to
  win.
- Every swap attempt plays a click; a successful match plays a chime, and
  each additional cascade in the same combo plays a brighter, rising
  chime.

## What's different from match3_1

| match3_1 | match3_2 |
| -------- | -------- |
| Tiles drawn as filled color rectangles | Tiles drawn as gem **sprites** (`draw_sprite`-style draw-queue command), one shape per color for colorblind accessibility |
| Swap applies instantly, matches evaluate immediately | Swap **slides** into place first (~4 frames); a non-matching swap slides back out instead of snapping |
| No audio | **Sound effects** for swap / match / cascade, queued from `execute_code` via the new `self._sound_queue` primitive (see below) |

The board logic itself (grid model, match-finding, cascade fall, scoring,
win condition) is unchanged from match3_1 — this is a genuinely readable
diff, not a rewrite.

## Project structure

| File | Purpose |
| ---- | ------- |
| `project.json` | project manifest — 800×800 window, 60 fps, startup room `rm_match3` |
| `rooms/rm_match3.json` | the single room; contains one instance of `obj_GridManager` at (0, 0) |
| `objects/obj_GridManager.json` | the entire game: four events, each a single `execute_code` action |
| `sprites/spr_gem_red\|blue\|green\|yellow.png` | 88×88 gem tiles (see `CREDITS.txt`) — sized to drop in exactly where match3_1's rectangle fill used to be, since `draw_sprite` blits at native size with no scaling |
| `sounds/snd_swap\|match\|cascade.wav` | short synthesized tones (see `CREDITS.txt`) |

## How the code works

State and the `step` state machine are the same as match3_1 (`grid`,
`sel`, `marked`, `flash`/`flash_total`, `falling`/`fall_speed`, `score`,
`target`, `won`, `find_matches`) — see that README for the full write-up.
New state added for this version:

| Attribute | Meaning |
| --------- | ------- |
| `sprite_names` | `['spr_gem_red', 'spr_gem_blue', 'spr_gem_green', 'spr_gem_yellow']`, indexed the same way `palette` was in match3_1 |
| `swap_off` | dict `(gx, gy) → (dx, dy)` pixel offset for the in-progress swap slide; decays to `(0, 0)` at `swap_speed` px/frame, same shrink-to-rest technique `falling` already uses for cascades, generalized to two axes |
| `swap_phase` | `None` / `'forward'` (sliding into the swapped position) / `'back'` (a rejected swap sliding back to its original cells) |
| `last_swap` | `(gx, gy, sx, sy)` — the two cells involved in the in-flight swap, so `step` can revert them without needing closure state |
| `pending_marks` | the match set computed right after a swap, held until the slide-in animation finishes so the flash doesn't start mid-slide |
| `arm_swap(a, b)` | helper (defined in `create`, stored on the instance like `find_matches`) that sets `swap_off` for both cells from their positions alone — calling it again with the same two cells produces the reverse animation, which is what powers the revert-slide for free |

Updated flow:

```
click adjacent tile
  → grid swapped immediately (data), pending_marks computed
  → swap_off armed (forward) — tiles slide into their new cells
       │
       ▼ (slide settles)
  pending_marks?
    yes → arm flash (blink → destroy → fall → rescan, as in match3_1)
    no  → swap grid back, re-arm swap_off with the SAME two cells (phase='back')
             │
             ▼ (slide settles)
          idle
```

- **`create`** — same grid seeding as match3_1, plus `sprite_names`,
  `swap_off`/`swap_speed`/`swap_phase`/`last_swap`/`pending_marks`, and
  the `arm_swap` helper.
- **`mouse_left_press`** — selection logic is unchanged; a valid adjacent
  swap now applies the grid swap, computes `pending_marks`, arms the
  forward slide, and queues `snd_swap`.
- **`step`** — the flash/fall blocks are unchanged from match3_1 (still
  queue `snd_cascade` on a chained rematch); a new `elif self.swap_off:`
  block decays the slide and, once settled, either arms the flash (queuing
  `snd_match`) or kicks off the revert slide.
- **`draw`** — same panel/board/selection/score/instructions/win-banner
  drawing as match3_1, but each tile is now a
  `{'type': 'sprite', 'sprite_name': ..., 'x': ..., 'y': ...}` draw-queue
  command instead of a filled rectangle (still swapped for a plain white
  filled rectangle during the marked-tile blink, exactly as match3_1 did),
  offset by `swap_off` combined with `falling`.

### The `self._sound_queue` primitive

`execute_code` has a live `game` object only on the desktop pygame
runtime — the Kivy-exported runtime and the Web/Pyodide runtime both bind
`game = None` in that scope, so `game.sounds[...].play()` (the obvious
thing to reach for) only works on desktop. This sample is what motivated
adding a proper cross-platform primitive instead: any event's
`execute_code` can do

```python
self._sound_queue.append('snd_swap')
# or, for a non-default volume:
self._sound_queue.append({'sound': 'snd_swap', 'volume': 0.5})
```

and it plays identically on all three targets:

- **Desktop** — `ActionExecutor.execute_event` drains and plays it (via
  `game.sounds[...]`) right after every event, not just `draw`.
- **Kivy export** — `GameObject._drain_sound_queue` (generated into
  `base_object.py`) resolves the name via a generated `asset_paths.py`
  (`SOUND_PATHS`) and calls the existing `play_sound()` helper; drained
  once per frame per live instance from the scene's `update()` loop, so it
  works even for objects with no `draw` event.
- **Web (Pyodide)** — the Python bootstrap returns any queued sounds in
  the JSON patch alongside the draw queue; `engine.js` plays them as real
  `<audio>` elements through the same pooled-audio path the structured
  `play_sound` action already used.

The same by-name resolution gap existed for `draw_sprite`-style commands
pushed from raw `execute_code` (this sample's tile rendering) — Kivy's
draw-queue renderer previously only resolved a sprite from a `sprite_path`
baked in at code-generation time for *structured* actions, so a
hand-authored `{'type': 'sprite', 'sprite_name': ...}` dict silently
failed to render there. Fixed the same way: `asset_paths.py` also carries
`SPRITE_PATHS`, and the Kivy draw-queue's `'sprite'` case falls back to it
by name when no pre-resolved path is present.

### Things to tweak

Same knobs as match3_1 (`self.cols`/`self.rows`, `self.palette`,
`self.target`, `flash_total`, `fall_speed`), plus:

- Swap animation speed: `self.swap_speed` (px/frame; 24 → ~4 frames per
  slide at `tile=96`).
- Sound volume: pass a `{'sound': ..., 'volume': ...}` dict instead of a
  bare name to `self._sound_queue.append(...)`.

## Roadmap

**[match3_3](../match3_3/README.md)** — done: a move limit, three rooms
as rising-target levels, and special tiles (4/5-in-a-row bonuses). Closes
match3_1's original roadmap.

## Export status

- **Test Game (F5) / desktop:** works — verified end-to-end with a real
  `GameRunner` run injecting an actual mouse click through the standard
  pygame event path (swap → match → cascade → score, with real
  `pygame.mixer.Sound.play()` calls observed).
- **Android (.apk) / Mobile (Kivy):** **supported.** Verified the export
  compiles cleanly, `asset_paths.py` carries the right `SPRITE_PATHS`/
  `SOUND_PATHS`, and the sprite images / sound files are copied into
  `assets/images` / `assets/sounds`. Building the actual `.apk`
  additionally requires buildozer (via WSL on Windows) — see
  [`docs/ANDROID_EXPORT.md`](../../docs/ANDROID_EXPORT.md).
- **Web (HTML5):** **supported.** The exported page's Pyodide bootstrap
  drains `self._sound_queue` into the same JSON round-trip as the draw
  queue; verified the generated bootstrap compiles and round-trips both
  draw commands and queued sounds correctly under plain CPython (no
  browser needed for that check — the in-browser Pyodide boot itself
  isn't exercised by the automated suite, same caveat as match3_1). Needs
  internet access on first load (Pyodide loads from a CDN).
- **Standalone zip:** untested with this sample.
