# Plan: per-tutorial-step screenshots for the 6 build-along wiki tutorials

Status: **not started** — one of the few genuinely open initiatives in
the repo; see `docs/PROJECT_STATUS.md` for the current overall picture.
Written 2026-08-15. This was the sole open item carried over from the
wiki completeness effort's Phase 3 (that plan is otherwise fully closed —
Phases 0-3 and 5 done, Phase 4 explicitly decided against; its own doc
has since been removed as closed, but this plan is self-contained and
doesn't depend on it).

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

## Suggested phase breakdown

1. **One tutorial, fully, as the proof of concept.** Pick the shortest
   tutorial (read all six's current step counts first — don't guess which
   is shortest) and build its complete scratch project + capture script +
   embedded screenshots, end to end. This phase answers the real open
   question — "how mechanically painful is scripting the Room Editor
   specifically" — before committing to the approach for the other five.
   If placing instances programmatically turns out to be much harder than
   creating objects/sprites, that finding should reshape the plan for the
   remaining five, not get discovered mid-way through tutorial four.
2. **The remaining five**, applying whatever pattern phase 1 validated.
   Each tutorial is its own scratch project + capture script + embed pass
   — independent units, doable in any order, each its own commit+push
   (matching every other unit of work across this whole effort).
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
