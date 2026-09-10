# Plan: per-tutorial-step screenshots for the 6 build-along wiki tutorials

Status: **Phase 1 DONE (2026-09-11) — Breakout, the proof of concept.**
Written 2026-08-15; picked up on an explicit ask. This was the sole open
item carried over from the wiki completeness effort's Phase 3 (that plan
is otherwise fully closed — Phases 0-3 and 5 done, Phase 4 explicitly
decided against; its own doc has since been removed as closed, but this
plan is self-contained and doesn't depend on it).

**Phase 1 result, answering the plan's own open question**: scripting
the Room Editor specifically turned out to be **no harder than scripting
any other editor** — placing an instance is just an entry in the room's
`instances` list (`{"object_name", "x", "y", "rotation", "scale_x",
"scale_y", "visible"}`), no different in mechanism from creating a
sprite or an object. The premise that this would be the hard, uncertain
part did not hold up; see "What Phase 1 actually found" below for the
full account, including the one real placement bug the screenshots
themselves caught.

## The six tutorials, and why none of them can reuse an existing sample

`wiki/Tutorial-{Pong,Breakout,Sokoban,Maze,Platformer,LunarLander}.md`,
each with 8 translated variants (`_de`/`_es`/`_fr`/`_it`/`_pt`/`_ru`/`_sl`/`_uk`
suffixes) — 54 pages total that would receive screenshots.

**Checked directly, not assumed**: none of the six can borrow screenshots
from an existing bundled sample, even where a same-genre sample exists.
`Tutorial-Maze.md` teaches `obj_player`/`obj_coin`/`obj_key`/`obj_enemy`/
`obj_locked_door`/`obj_exit` with sprites `spr_player`/`spr_coin`/etc. —
completely different names from the bundled `samples/maze_1`
(`obj_person`/`obj_goal`/`obj_wall`). Pong/Breakout/Sokoban/Platformer/
LunarLander have **no bundled sample at all** in `samples/` to check
against. Every one of the six needs a **from-scratch scratch project**,
built by literally following that tutorial's own text step by step, before
any screenshot can be taken — this was already established for Platformer
specifically in the 2026-08-11 investigation (confirmed there against
`samples/plateforme_3`'s mismatched French names); this plan confirms the
same is true for the other five, not just assumed by extension.

## Reusable infrastructure from Phase 1 (don't rebuild this)

Phase 1 of the wiki completeness effort already solved the two hardest
general problems:

- **Headless capture**: `QT_QPA_PLATFORM=offscreen` + `QWidget.grab()` (the
  same technique this session's own i18n spot-checks reused for
  `NewProjectDialog`) — proven against the full IDE window, not just small
  dialogs.
- **The privacy landmine, already found and fixed once**: the Welcome
  tab's recent-projects panel leaks the capturing machine's real project
  history on first render. Phase 1's fix — blank `Config`'s recent-projects
  list and no-op `add_recent_project` before constructing the window — must
  be reapplied here; don't rediscover this the hard way a second time.
- **Never load the bundled `samples/` path directly** for a capture — it
  triggers the real promotion-copy-into-Documents flow. Always operate on
  an explicit scratch copy.

What Phase 1 did NOT need, that this plan does: driving the IDE through a
whole multi-step authoring sequence programmatically (create object → add
sprite → wire an event → add an action → ... → screenshot after each step),
not just opening one static window and grabbing it once. That automation
doesn't exist yet and is the real new work here.

## The actual size of this task, stated plainly

This is **not** "write a script, run it once." Each tutorial's screenshots
require:

1. Reading that tutorial's current wiki text end to end and extracting the
   literal step sequence (what object/sprite/room/event/action to create,
   in what order, with what exact names/values) — the screenshots must
   match what the prose says to click, not an approximation.
2. Either (a) scripting the IDE through that exact sequence
   programmatically (calling the same underlying methods a human click
   would trigger — `AssetManager`/`ProjectManager`/editor APIs directly,
   bypassing real mouse events) and grabbing a frame after each step, or
   (b) a human actually building each tutorial by hand once, screenshotting
   as they go. **(a) is strongly preferred** — it's the only approach that
   stays re-runnable if a tutorial's text changes later (matching how this
   whole session's own screenshot spot-checks were built as reusable
   scripts, not one-off manual captures) — but it means each tutorial's
   step sequence needs translating into real IDE API calls, which is
   nontrivial for anything involving the Room Editor's canvas (placing an
   instance at a specific pixel position isn't just "call a method with an
   object name" the way creating an object is).
3. Deciding **where each screenshot gets embedded** in the tutorial
   markdown and what size/crop makes sense inline (Phase 1's screenshots
   were full-window; a per-step tutorial screenshot showing "you just added
   this one event" plausibly wants a tighter crop of just the relevant
   panel, which the capture script needs to produce, not just a full-frame
   grab every time).

Phase 1's own retrospective sizing ("comparable to all of Phase 1
combined, for a lower-traffic set of pages") was a reasonable estimate and
this plan doesn't revise it — six tutorials × several steps each × the
scripting-a-full-authoring-sequence problem above is genuinely
comparable in scope to the six pages Phase 1 built from nothing.

## What Phase 1 actually found (2026-09-11)

Read all six tutorials' line counts before picking one, per this plan's
own instruction rather than guessing: Breakout (225 lines) was clearly
shortest — Pong 362, Sokoban 368, Maze 380, Platformer 428,
LunarLander 438. Also re-checked (not just trusted from 2026-08-15) that
no bundled `samples/` folder matches any of the six by name — still
true.

**The capture mechanism, end to end, in one committed script**
(`tools/capture_tutorial_screenshots.py`): construct a real
`PyGameMakerIDE` offscreen, create a scratch project via
`ProjectManager.create_project` (never the bundled `samples/` path
directly), then for each of the tutorial's own "## Step N" headings,
mutate the project directly through the same `AssetManager` calls the
real UI menu actions use (`import_asset` for sprites — origin already
defaults to center on import, matching "Click Center" for free;
`create_asset` for objects/rooms, with `events`/`instances` passed
straight in), sync that into `project_manager.current_project_data` +
refresh the visible asset tree (`AssetManager.save_assets_to_project_data`
+ `AssetTreeWidget.refresh_from_project` — the exact same sync
`ProjectManager.save_project()` already relies on before writing to
disk, reused here instead of re-deriving something new), open the
relevant editor (`open_sprite_editor`/`open_object_editor`/
`open_room_editor`, all three already take `(name, data)` directly), and
grab the window.

**The plan's own flagged open question — "how mechanically painful is
scripting the Room Editor specifically" — is answered: it isn't.**
Placing an instance needed no new mechanism at all: a room's
`instances` list is `{"object_name", "x", "y", "rotation", "scale_x",
"scale_y", "visible"}` dicts, populated directly, then handed to
`open_room_editor` exactly like any other editor's data — the same
"set the data, open the widget that renders it" shape that already
worked for sprites and objects. The screenshot needs to show what the
IDE looks like *after* a step, which depends only on the resulting
project data and which editor is on screen — not on replaying the exact
mouse-drag that a human would have used to get there. This is the
finding the plan itself said should "reshape the plan for the remaining
five" if placement turned out easy, not just if it turned out hard: **no
per-tutorial risk assessment is needed for the Room Editor step in any
of the remaining five** — it's the same mechanism as every other step.

**One real bug the screenshots themselves caught, not assumed correct
from the coordinates alone**: the first placement draft put the ball at
the room's exact grid center, which landed inside the brick rows —
the brick instance at that same cell rendered on top of it, so the ball
was completely invisible in the captured Room Editor screenshot. Only
visible by actually looking at the resulting image (matching this
repo's "verify via a real GameRunner, not just reading code" discipline
applied here to a capture script instead); fixed by moving the ball to
the open gap between the brick rows and the paddle.

**Shipped**: `wiki/images/tutorial-breakout-{01-sprites,
02-paddle-object, 03-ball-object, 04-brick-object, 05-wall-object,
06-room}.png` (6 screenshots), embedded into
`wiki/Tutorial-Breakout.md` at the end of each corresponding "## Step N"
section.

**Phase 2 kickoff (2026-09-10) refined two capture-tool defaults; the
Breakout shots were regenerated to match:**

- **Window is now 1680×980, not 1440×900.** A 640×480-ish tutorial room
  is wider than the room editor's scroll viewport at the old width, so a
  full-window `ide.grab()` silently clipped the room's right edge (right
  wall column, right goal column) out of the frame. Pong's room needs the
  extra width; the others likely will too.
- **Placeholder wall/goal sprites are no longer neutral grey.** A grey
  wall row (150,150,150) is nearly indistinguishable from the IDE's own
  grey chrome in a full-window screenshot — the walls *were* rendering in
  the Phase 1 Breakout room shot, they just read as "window border". Walls
  are now a warm tan; Pong's invisible goals a translucent green (with a
  caption noting they're invisible in-game). Verified by pixel-probing the
  saved PNGs, not just eyeballing the downscaled preview (which is exactly
  what hid the problem the first time).

## Suggested phase breakdown

1. **DONE (2026-09-11) — One tutorial, fully, as the proof of concept.**
   Breakout; see "What Phase 1 actually found" above for the full
   account. If placing instances programmatically turns out to be much
   harder than creating objects/sprites, that finding should reshape the
   plan for the remaining five, not get discovered mid-way through
   tutorial four — moot now; it turned out to be no harder at all.
2. **The remaining five**, applying whatever pattern phase 1 validated.
   Each tutorial is its own scratch project + capture script + embed pass
   — independent units, doable in any order, each its own commit+push
   (matching every other unit of work across this whole effort).
   - **Pong — DONE (2026-09-10).** `capture_pong` in the capture tool; 7
     shots (`tutorial-pong-02-sprites` … `-08-room`) at Steps 2–8 (Step 1
     is a planning table, Step 9 is "run it" — no screenshot), embedded in
     `wiki/Tutorial-Pong.md`. No surprises: the goal objects are invisible
     in-game so their placeholder is drawn translucent-green purely for
     the room shot, noted in that caption. `Tutorial-Pong_*` translated
     variants still untouched (Phase 3).
   - **Sokoban — DONE (2026-09-10).** `capture_sokoban`; 7 shots
     (`tutorial-sokoban-02-sprites` … `-07-controller-object`, `-09-room`
     — the tutorial numbers its steps 1,2,…,7,9,10, no step 8), embedded
     in `wiki/Tutorial-Sokoban.md`. The room is the tutorial's own
     "Example Level Layout" ASCII translated cell-for-cell. Conditional
     actions (the crate's `if_collision`, the player's `if_can_push`)
     serialize as `then_actions`/`else_actions` nested in `parameters`,
     matching the bundled samples.
   - **Maze — DONE (2026-09-10).** `capture_maze`; 7 shots
     (`tutorial-maze-02-sprites` … `-07-controller-object`, `-08-room`),
     embedded in `wiki/Tutorial-Maze.md` at Steps 2–8. Confirmed again
     that the tutorial's `obj_player`/`obj_coin`/`obj_exit` names don't
     match `samples/maze_1` (`obj_person`/`obj_goal`/`obj_wall`), so this
     is its own scratch project. Room is the tutorial's own "Example Maze
     Layout" ASCII transcribed verbatim (`.split()` per row). Uses the
     `keyboard_no_key` event for the stop-on-release behaviour.
   - **Platformer — DONE (2026-09-10).** `capture_platformer`; 9 shots
     (`tutorial-platformer-02-sprites` … `-09-controller-object`,
     `-10-room`), embedded in `wiki/Tutorial-Platformer.md` at Steps 2–10.
     Uses `set_gravity` in Create, `keyboard_press` for the jump impulse,
     `keyboard_no_key` for horizontal-only stop. The room is a clean
     25×15 grid reading of the tutorial's loose "Example Level Layout"
     art (ground with two pits, four platforms, coins, spikes, flag).
     **New tool helper `_fit_window_to_room`**: the 800-wide room is
     wider than the room editor's scroll viewport even at 1680px, so this
     grows the window until the canvas fits before grabbing (a no-op for
     the four narrower tutorials, so their shots are unchanged).
   - LunarLander — not started.
3. **Translated variants.** Decide once phase 1-2 land: do the 8
   translated copies of each tutorial get the SAME English-captured
   screenshots (the IDE's own UI chrome would still be English unless the
   capture script also switches language per screenshot — matching this
   session's own `get_language_manager().set_language()` pattern), or
   does each language get its own captures? **Recommendation: same
   screenshots across all languages for v1** (matching how Phase 1's
   original English-only images were embedded with no per-language
   variants planned) — recapturing 54 pages × per-step screenshots in 8
   languages each is a multiplicative cost this plan should not take on
   speculatively. A future pass can add language-matched captures if it
   turns out to matter to actual readers.

## Explicitly out of scope

- **Video walkthroughs.** Screenshots only, matching the rest of this
  wiki's existing style.
- **Screenshotting every tutorial in every language** (see Phase 3 above —
  deliberately deferred, not forgotten).
- **Rewriting tutorial prose.** This plan only adds images to existing
  text; if a tutorial's steps turn out to be stale/wrong while building the
  scratch project to screenshot it (a real risk — nobody has rebuilt these
  from scratch recently), fix that as its own small, separate finding, not
  bundled silently into an image-adding commit.
