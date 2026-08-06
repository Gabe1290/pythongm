# Reader-facing docs: AI-slop cleanup registry

**Update 14 — follow-through from Update 12/Tutorials.md: the 4 individual
tutorial pages (Sokoban/Maze/Platformer/LunarLander) had the same wrong
"Preset: Beginner Preset" header the Tutorials.md fix caught at the index
level.** These were rewritten earlier in this same session (the GML
fixes, Update 10/11) *before* the preset system was understood — the GML
rewrite never touched the Preset line, and at the time nobody knew it was
wrong. Fixed all 4 English pages to Intermediate with a specific reason
each (Sokoban: push mechanic + grid movement; Maze: Execute Code for the
timer; Platformer: the Enhancements section's Execute Code, base tutorial
through Step 10 is genuinely Beginner-compatible; LunarLander: Execute
Code throughout). **Caught a real mistake mid-fix**: initially copied the
same "Intermediate" verdict onto Tutorial-Platformer_fr.md by analogy with
English, but that French page is a shorter variant with NO Enhancements
section and NO Execute Code at all — checked its actual content before
committing and reverted it to Beginner, which is what it genuinely needs.
Sokoban_fr/Maze_fr/LunarLander_fr were checked the same way and do contain
the Intermediate-requiring content, so those three got the real fix.
**Lesson: a French tutorial page derived from an English one is not
guaranteed to need the same preset — check what's actually IN the page,
not what its English counterpart needs.**

**Update 13 — MAJOR, RESOLVED: Visual-Programming.md/`_fr` were mostly
fabricated.** Full details on the checklist entries below (Section E/F).
Short version: cross-checked every block table against the real, complete
`config/blockly_config.py` BLOCK_REGISTRY. No Math/Logic/Text toolbox
category exists (real category: "Control"); no boolean/hexagon reporter
blocks or Repeat block; conditionals are flat GM80-style stack blocks
(If Condition/Test Variable have one "then" slot, paired with separate
Else/Start Block/End Block), not Scratch-style if/else containers —
confirmed against the actual block JS in `blockly_blocks.js`.
`( speed )`/`( direction )` reporter blocks don't exist. Jump to
Start/Random Position, Draw Sprite, Set Drawing Color, per-sound Stop
Sound have no Blockly block at all. Full rewrite, both languages.

**Update 12 — MAJOR, RESOLVED (with a self-correction along the way — read
this before touching Preset-Guide/Beginner-Preset/Intermediate-Preset/
Event-Reference's Preset material again).** Found while fixing
Event-Reference.md's per-event "Preset: Beginner/Intermediate/Advanced"
rows: `config/blockly_config.py`'s `PRESETS` registry has no "Advanced"
preset at all (real names: `full`, `beginner`, `intermediate`,
`platformer`, `grid_rpg`, `sokoban`, `thymio`, `testing`, `code_editor`,
`blockly_editor`), and the per-event tier assignments turned out to be
almost entirely fabricated — cross-checked all 23 non-Thymio events against
`get_available_events()` fed the real `beginner`/`intermediate` presets and
**18 of 23 were wrong** (e.g. Alarm/Draw/Draw GUI/Begin Step/End Step/all
Room+Game+boundary events were labeled "Advanced" but are actually in
`beginner`; Keyboard Press was labeled "Beginner" but is `intermediate`-only).

**First pass got the *scope* of the problem wrong, too — caught and
corrected in the same session.** Initially concluded from
`object_events_panel.py`'s `apply_config()` docstring ("for compatibility")
that presets only gate the Blockly block palette and never filter the
structured Actions/Events panel every tutorial teaches with. **That was
false** — a fuller grep for `self.blockly_config` (not just the string
"preset") in the same file found `show_add_event_menu()` and 4 call sites
of `get_actions_by_category(self.blockly_config)` that genuinely DO filter
the structured "Add Event"/"Add Action" menus, and
`editors/object_editor/object_editor_main.py` loads a project's real
`settings.blockly_preset` from `project.json` and calls
`events_panel.apply_config()` with it. Worse: **`config/editions.py`'s
`DEFAULT_EDITION = "beginner"`** — a fresh install's new projects default to
exactly the restricted `beginner` preset in *both* editors, not "full". The
lesson: a docstring plus one narrow grep is not verification — trace every
call site of the thing you're citing as evidence before asserting "never
consulted." An AskUserQuestion had already gone out on the wrong premise;
told the user directly and proceeded with the corrected facts rather than
letting the wrong framing stand.

**What's actually true, now verified end-to-end:** a project's preset comes
from two places — `Preferences > IDE Edition` sets the default for *new*
projects (Beginner edition -> `beginner` preset; existing projects
untouched by switching edition), and `Tools > Configure Action Blocks...`
changes the *current* project's preset at any time — and that preset
genuinely filters both the Blockly palette and the structured panel.

**Fixed, this update:**
- `tools/gen_preset_docs.py` (new) regenerates
  `Beginner-Preset.md`/`Intermediate-Preset.md` (+ `_fr`) straight from
  `get_available_events()`/`get_actions_by_category()` fed the real preset
  configs — the same functions the app itself calls — so these pages can't
  silently drift again the way the hand-written ones did (they were stuck
  at "4 events, 17 actions" while `get_beginner()` had grown to 19
  events/83 actions across tutorial additions). Usage:
  `py -3.12 tools/gen_preset_docs.py fr` (bare = English only). French
  strings live in `tools/action_ref_i18n.py`'s new `EVENTS_FR` table +
  `CATEGORIES_FR`'s 6 new event-category entries (Object/Input/Collision/
  Step/Drawing/Other) — reuses the same `LANGS` table
  `gen_action_reference.py` already established.
- `Preset-Guide.md`/`_fr` hand-fixed: corrected framing (both editors are
  filtered), explained the Edition-vs-Configure-Action-Blocks distinction,
  replaced the fake "Advanced preset" row with the real Edition -> preset
  mapping, and stopped hardcoding drift-prone counts (links to the now-generated
  pages instead).
- `Event-Reference.md`/`_fr`: all 18 wrong per-event Preset rows corrected
  by line-targeted script (verified against the same real data), plus the
  "Events by Preset" summary table rebuilt with accurate counts and a link
  to Preset Guide instead of restating the framing.
- Full-Action-Reference.md's generator (`tools/gen_action_reference.py`)
  still has an imprecise "which actions each preset/edition exposes"
  see-also line — not yet touched; low-risk (just a see-also blurb, not
  a data table), left for a future pass.

**Update 11 — Update 10's GML-fabrication crisis is RESOLVED for all 4
pages, English + French.** User chose "rewrite English + French now" over
deferring or just flagging. Each page's ```gml blocks were replaced with
verified real API calls (checked against `events/action_types.py` +
`runtime/action_executor.py` for every action name/param, and every Python
snippet compiled via `compile()` before commit):
- `Tutorial-Sokoban.md`/`_fr.md` — `6c825d9`
- `Tutorial-Maze.md`/`_fr.md` — `90db80b`
- `Tutorial-Platformer.md`/`_fr.md` — `cde99fd`
- `Tutorial-LunarLander.md`/`_fr.md` — this commit. The hardest of the
  four: fuel/thrust/velocity-landing physics isn't covered by any other
  tutorial's precedent, so this one leans on `execute_code` more than the
  others do (real Python, wrapped in `if not self.landed and not
  self.crashed:` since there's no GML-style `exit` mid-event). Two
  landmines worth remembering for future engine work: (1) `self.speed` on
  an instance is the **sprite animation rate**, not movement magnitude —
  velocity magnitude has to be computed by hand from
  `hspeed`/`vspeed` (Pythagoras); (2) `Set Gravity` applies every frame
  unconditionally once set, independent of any per-frame Step-event
  gating, so a "landed" instance needs an explicit `Set Gravity`
  (`gravity=0`) or its stored vertical speed keeps climbing even though a
  Solid landing pad visibly holds it in place.
- Only the German/Italian/Spanish/Portuguese/Slovenian/Ukrainian/Russian
  translations of these 4 pages still carry the fabricated GML (out of
  scope for this pass — English + French only, per standing project
  convention).

**Update 10 — MAJOR, STOP AND READ BEFORE TOUCHING Tutorial-{Maze,
Platformer,LunarLander,Sokoban}.md: these wiki pages teach fabricated
GameMaker Language (GML) code that does not run in this engine at all.**
Found while reading `wiki/Tutorial-Sokoban.md`'s "Execute Code" steps —
they use `place_meeting()`, `instance_place()`, C-style `if (...) { }`,
semicolons. Checked the other Tutorial-*.md pages: `Tutorial-Maze.md` (7
fenced ```gml blocks), `Tutorial-Platformer.md` (13), `Tutorial-
LunarLander.md` (8) are FULL of extensive GML — `keyboard_check(vk_up)`,
`place_meeting`, `instance_place`, `draw_set_color`/`c_white`/`c_red` (GM
color constants), `room_restart()`/`room_goto_next()`, `show_message()`,
`instance_destroy()`, `with (other) { }`, `lengthdir_x/y()`, `clamp()`,
`variable_global_exists()`, `noone`, `vk_left`/`vk_right` — **none of
which exist in this engine.** This project's `execute_code` action runs
**real Python** (confirmed: `runtime/action_executor.py:3089`
`execute_execute_code_action`; the actual collision-check equivalent is
`game.check_collision_at_position(instance, x, y, object_name)` —
`runtime/game_runner.py:4118`, already used correctly in
`samples/treasure/README.md`). A student pasting any of these ```gml
blocks into the IDE's Execute Code action gets an immediate Python
`SyntaxError` (C-style `{ }`/`;`/`!`, `vk_up`, undefined functions) —
this is not a wording problem, the tutorials are **teaching code that
cannot work**, likely drafted from generic "how to make X in GameMaker"
knowledge and never adapted to this project's actual Python-based
scripting.

**Scope, checked before flagging:** confirmed via `grep -c gml` that this
is systemic, not a one-off — `Tutorial-Maze.md` has the identical 7 GML
blocks in **all 9 languages** (en/fr/de/es/it/pt/ru/sl/uk), and
`Tutorial-Platformer_fr.md`/`Tutorial-LunarLander_fr.md` have their own
(smaller) subsets, meaning this was propagated by translation, not
independently authored per language. `Tutorial-Pong.md` and `Tutorial-
Breakout.md` are unaffected (they never drop into raw code, staying
entirely in the Actions-panel instruction style) — only the 4
Sokoban/Maze/Platformer/LunarLander pages are affected, but across up to
9 languages each.

**Not fixing this without checking in first** — a real fix needs each
GML block individually rewritten against the verified real API (`self`/
`game`/`game.check_collision_at_position`/the `keyboard.check()` shim
noted elsewhere in this doc's CLAUDE.md context), which is a substantial,
technically-precise rewrite, not a wording pass, and doing it wrong would
plant new bugs instead of fixing old ones. Flagging for the user before
investing in it.

**Update 9: Section C (all 18 English sample READMEs) is 100% read.**
`samples/README.md` + match3_1/2/3 + maze_1/2/3/4 + plateforme_1/2/3 +
raycast_1/2/3/4 + treasure + views_1/2. Verdict holds from the first
batch: this is exceptionally good documentation — dense, specific,
technical, with real instance counts, hardcoded values, honest
"undocumented licensing" caveats, and no AI-slop patterns anywhere.
**One real fix**: `raycast_2/README.md` quoted the in-game exit-gate
message as *"Ramasse toutes les gemmes !"* (French) when the actual
`show_message` action in `project.json` says *"Collect all the gems
before you leave!"* (English — sample games stay English by convention,
only guides get translated). The French README already had this right
(quoted the correct English message) — only the English README had the
mixed-up quote. Fixed to match reality.

Sections A + C are now fully done (59/59 files). Section B (French
Tutorials) has structural parity fully verified for all 41 pairs but not
a full prose read of files that structurally matched (lower priority per
the earlier finding that translation quality is solid where content
exists — no accent-stripping found). Remaining: Section D (17 French
sample READMEs), Sections E/F (47 wiki pages, ~2 read so far).

**Update 8: the fr/04_breakout/07_game_controller.html gap from Update 7
is FIXED.** Translated the missing "Fin de partie et meilleurs scores"
section (Plus de vies event, Afficher un message/Afficher le tableau des
meilleurs scores/Terminer le jeu blocks, the ordering warning) and added
it in the same position English has it. Terms verified against the
actual shipped IDE translations rather than invented (grepped
`translations/pygm2_fr_editors.ts`/`pygm2_fr_actions.ts` for the exact
strings the French UI uses): "No More Lives" → "Plus de vies", "Show
Message" → "Afficher un message", "Show Highscore Table" → "Afficher le
tableau des meilleurs scores", "End Game" → "Terminer le jeu", "Game" →
"Jeu". Added the missing `.block-game`/`.block-output` CSS rules
(matching English's colors). Also fixed the "Challenge Ideas" list's last
item, which had stood in a workaround challenge ("end the game at 0
lives") for the missing feature — replaced with the real translation of
English's actual 4th challenge ("play a sound when the game ends").
Verified: structural diff against English is now byte-for-byte identical
(tag/class structure), tutorial-related tests pass.

**Update 7 (Section B start) — found a real content gap, not a slop issue.**
Structural diff of all 41 EN/FR pairs (tag+class structure, ignoring text)
found 9 mismatches. Investigated each:
- **`04_breakout/07_game_controller.html` (fr): missing the entire "Game
  Over and Highscore" section** — the `No More Lives` event, the Show
  message/Show Highscore/End Game block sequence, and the "Order
  matters!" warning. French learners following this tutorial never learn
  to add a working game-over screen; the French "Challenge Ideas" list
  even still references "Terminez le jeu quand les vies atteignent zéro"
  (end the game at 0 lives) as a *challenge*, even though ending the game
  was supposed to already be taught content. **Needs a real fix (translate
  the missing section), not a polish edit — flagging for the user rather
  than unilaterally drafting French teaching prose.**
- The other 8 mismatches (`01_getting_started/03_first_project`,
  `05_sokoban/02_player_and_walls`, `05_sokoban/04_targets_and_controller`,
  `06_maze/02_player_and_maze`, `07_platformer/01_introduction`,
  `07_platformer/02_jumping_player`, `08_lunar_lander/01_introduction`,
  `08_lunar_lander/02_flying_lander`) checked and are **not content gaps**:
  either a single extra/missing `<strong>` tag (cosmetic), or the French
  file restructures one `<p>` into a `<h2>` + list covering the same
  content (verified via full tail-to-tail diff on the sokoban case —
  identical ending content, just organized differently). Lower-priority
  note: `07_platformer/01_introduction` and `08_lunar_lander/01_introduction`
  (fr) use an older bullet-list "What We'll Create" layout instead of the
  numbered `.phase` boxes every other intro (EN and FR) uses — content is
  complete, just an inconsistent template/format, and
  `07_platformer/01_introduction`'s French time estimate ("30-40 minutes")
  doesn't match English's ("25-30 minutes"). Neither blocks learning like
  the breakout gap does.

No accent-stripping found in any French Tutorials file (checked ~25 common
words that would be conspicuously wrong unaccented, e.g. "deplacer" vs
"déplacer") — translation quality itself is solid where content exists.

**Update 6: Section A (all 41 live English Tutorials files) is 100% read.**
Every lesson across all 9 tutorials read in full for paragraph-level
polish, not just grep. Overall verdict holds from the earlier updates:
this is genuinely good, human-written teaching content — clear
cause/effect explanations ("why Solid", "why two wall types", "why 0.05
gravity", parent-object payoff), consistent ASCII room-layout diagrams,
sensible non-generic challenge ideas per tutorial, appropriately-varied
encouragement, and closing summaries that recap *specific* things built
rather than generic "in conclusion" filler. Two small real fixes found
along the way (both already committed): the 07_platformer block-output/
block-room class mismatch, and the emoji-consistency batch from Update
3. Nothing else needed changing across all 41 files.
Next: Section B (French Tutorials, 41 files) — diff against the
now-confirmed-clean English rather than reading cold, per the "diff, not
duplicate" note already in Section B below.

**Update 5 (same day): the 78 orphans from Update 4 are DELETED.**
Investigated git history before asking the user: `f1c8d42` ("Rewrite all
tutorials with progressive play-early approach", 2026-03-26) replaced the
old step-by-step tutorial format — it correctly deleted the old English
files for `07_platformer`/`08_lunar_lander` but missed it for
`02_first_game`/`03_pong`/`04_breakout`/`05_sokoban`/`06_maze`. The French
translations (added earlier, on the old format) were properly migrated to
the new content in later commits (`a701c9d`, `c2e2641`) but the old French
files were never removed either. Confirmed genuine completed-migration
leftovers, not an in-progress or intentional dual-track state — user
approved deletion. All 78 removed via `git rm`; tutorial-related tests
(`test_audit_tutorial_panel_links.py`, `test_tutorial_empty_placeholder.py`,
`test_audit_editions_tutorial_fallback.py`) and the full suite (2191
passed, 0 failed) confirm nothing referenced them. **`Tutorials/` is now
160 → 82 files, all of them live.** Sections A/B below are stale (list the
pre-deletion folder file counts) — the live-file lists per folder now
exactly match each `index.json`'s `pages` array; use that as the
authoritative list going forward instead of re-deriving it.

**Update 4 (same day, MAJOR — read this before touching any more
`Tutorials/` files): 78 of the 160 Tutorials HTML files are dead,
unreferenced orphans (32 English + 46 French).** Found while reading
through `02_first_game/`: the folder has two parallel, differently-named
sets of lesson files covering the same content — an older numbered-circle
`.step` style (`02_create_sprites.html`, `03_create_objects.html`, ...)
and a newer Blockly-block-diagram `.phase` style (`02_moving_player.html`,
`03_falling_stars.html`, ...). Checked `Tutorials/index.json` and
`Tutorials/fr/index.json` (the actual manifests the app reads) against
what's on disk in every folder: **every tutorial entry in both index.json
files has an explicit `pages` list naming only the newer set.** Verified
against the loader code itself
(`widgets/tutorial_panel.py:260-269` and `widgets/tutorial_dialog.py`'s
equivalent): `open_tutorial_by_data` reads `tutorial_data.get('pages',
[])`; the `folder.glob("*.html")` fallback only runs when a tutorial has
**no** `pages` key at all, which never happens here — so the older-style
files are **structurally unreachable through the IDE's tutorial UI**, in
both languages. This is a repo-hygiene finding, not a prose-quality one:
I nearly kept "polishing" some of these (spent one earlier edit today,
the emoji fix on `06_maze/02_create_sprites.html`, on a file that turns
out to be orphaned — harmless since it's still correct if the file is
ever revived, but wasted effort).

**Full orphan list, by folder** (English; the `fr/` folders have the same
list plus `07_platformer`/`08_lunar_lander` each add their extra 6-7 files
— matches the anomaly noted at the top of this doc originally, now
explained: those aren't "more complete French lessons," they're orphans
too):
- `02_first_game/`: 02_create_sprites, 03_create_objects, 04_add_movement, 05_add_star, 06_scoring, 07_finishing
- `03_pong/`: 02_create_sprites, 03_create_objects, 04_paddle_movement, 05_ball_movement, 06_scoring, 07_score_display, 08_room_setup
- `04_breakout/`: 02_create_sprites, 03_create_objects, 04_paddle_movement, 05_ball_movement, 06_lives_system, 07_score_display, 08_room_setup
- `05_sokoban/`: 02_create_sprites, 03_create_objects, 04_crate_behavior, 05_player_movement, 06_win_condition, 07_room_setup
- `06_maze/`: 02_create_sprites, 03_create_objects, 04_player_movement, 05_collectibles, 06_game_controller, 07_room_setup
- `fr/07_platformer/` + `fr/08_lunar_lander/` also each have 7 additional orphans beyond the above pattern (see the anomaly note, now superseded by this finding)

**STOP reading/editing prose in any file not listed in the relevant
`index.json`'s `pages` array before checking this section — verify
against index.json first.** Live files needing further paragraph-level
read-through: `01_getting_started/` (4, all read/clean), `02_first_game/`
(5 live pages: 01_introduction✓read, 02_moving_player✓read,
03_falling_stars✓read, 04_scoring — not yet read, 05_finishing — not yet
read), and all of 03_pong/04_breakout/05_sokoban/06_maze/07_platformer/
08_lunar_lander/09_catch_the_coins's live pages per their `pages` lists
(most not yet individually read — only intro pages and a couple of
game_controller pages checked so far).

**Decision needed from the user before any deletion:** this doc doesn't
delete the 78 orphans — that's a real, if easily-reversible (git history),
destructive action affecting the repo's file count, and I don't know
whether they're intentionally kept (e.g. as source material for a planned
rework, or a deliberate "detailed alternate track" someone might wire up
later) or just forgotten leftovers from restructuring the tutorial format.
Flagging for the user to decide.

**Update 3 (same day, follow-up sweep):** the H1-only entity grep in
Update 2 missed emoji in `<h2>` and inline body text. A broader sweep
(raw Unicode ranges + all HTML numeric entities, whole `Tutorials/` tree,
both languages) found two more isolated spots, both confirmed
inconsistent by comparing against sibling files that cover the same
content: `06_maze/02_create_sprites.html` had emoji on all 4 of its `<h2>`
sprite headings plus inline on "Create New Sprite"/"Import Image..."/
"Tip:" — no other `create_sprites.html` (checked `04_breakout`,
`05_sokoban`) uses any; and `08_lunar_lander/04_game_controller.html`
(+ its French pair) bookended its final "Congratulations!" with 🚀/🌕 —
the only 1 of 14 "Congratulations!" messages across all English tutorials
to have emoji at all. Fixed both (6 files total this update). The
`.game-preview` box's one big themed emoji per game (🏓 Pong, 🧱 Breakout,
etc.) is untouched — that one IS consistent across all 9 tutorials and all
9 languages, so it's a deliberate design element, not slop.

Confirmed via repo-wide sweep (Unicode ranges + entities, all of
`Tutorials/`) that no more emoji exist outside the `.game-preview` boxes.
**This closes out the emoji-consistency thread** — future work on this
registry should focus on the paragraph-level read-through, not more emoji
hunting.

**Update 2 (same day, deeper read pass):** read 9 more Tutorials HTML
files in full (intro pages across `03_pong`/`04_breakout`/`06_maze`/
`07_platformer`, plus `07_platformer/04_game_controller.html` end to
end) and one full French sample README (`raycast_1/README.fr.md` —
exceptionally dense, precise technical writing, real benchmark numbers,
nothing to fix). Found what the earlier grep sweep missed: it only
checked literal Unicode emoji characters in `wiki/*.md`, not HTML numeric
entities (`&#128640;` etc.) in `Tutorials/*.html`. A follow-up grep for
`<h1>...&#N;...</h1>` across the whole `Tutorials/` tree found exactly 3
hits — `08_lunar_lander/01_introduction.html` (🚀) and
`06_maze/01_introduction.html` + `fr/06_maze/01_introduction.html` (🧭) —
inconsistent with the other 6 of 8 intro pages, which have plain-text H1s
(the big emoji in the `.game-preview` box below already carries that
decoration). Removed all 3 for consistency; confirmed via repo-wide grep
that no more `<h1>`/`<h2>`/`<h3>` + entity combinations exist anywhere in
`Tutorials/`. Otherwise all 9 files read clean — consistent template,
varied and appropriately-placed encouragement ("Press F5 to play!" far
outnumbers "Congratulations!", not repetitive), no rhetorical padding.

**Update 1 (same day):** ran a targeted grep sweep across the ENTIRE English
wiki (all 23 files) plus every `samples/*/README*.md` and every
`Tutorials/**/*.html` (EN+FR) for: the full banned-word list, empty
filler phrases, emoji headings, "not X, it's Y" binary contrasts, and
summary-recap endings ("In conclusion"/"Overall"/"Ultimately"). Result:
**zero real hits** beyond the contributing-boilerplate template already
fixed in batch 1 (the 4 `harness` matches in sample READMEs are the
"test harness" noun, not the AI-slop verb — checked in context). Combined
with 4 full manual reads (`samples/README.md`, two Tutorials HTML files,
plus `Getting-Started`/`Creating-Your-First-Game`/`Visual-Programming`/
`Events-and-Actions`' closing sections all spot-checked and clean), this
is strong evidence the corpus is **already largely free of classic
AI-slop patterns** — dense, specific, technical writing throughout, with
navigation-link endings rather than fake-profound kickers.

**Conclusion: don't grind through all 242 files expecting to find more of
what batch 1 found.** The recurring boilerplate template is fixed
everywhere it appeared (confirmed via repo-wide grep, zero remaining
hits). What's left in the queue below is genuinely optional deeper
reading — plausible remaining candidates, in priority order: (1) the
`Tutorials/` lesson bodies not yet individually read (only 2 of 160 files
were actually opened; the grep sweep covers vocabulary/pattern-level slop
but not paragraph-level awkwardness, wordiness, or voice inconsistency a
human read would catch), (2) sample READMEs beyond the ones spot-checked,
(3) remaining wiki pages' body prose (headers/nav were checked, full
bodies of Room-Editor/Object-Editor/3D-View/Extensions/Exporting-Games/
Preset-Guide/Beginner-Preset/Intermediate-Preset weren't individually
read). Treat the registry below as a "read if you have budget, not
because slop is expected" list rather than a confirmed backlog.

Started 2026-08-06, using the `no-ai-slop` skill (edit workflow —
`~/.claude/skills/no-ai-slop/SKILL.md` + `eval.md`). Scope decided with the
user: **Tutorials/ + samples/*/README.md + wiki/**, **English + French**
only for now (the skill's word/pattern list is English-specific; the other
7 wiki/sample languages and the other 6 Tutorials languages are a later,
separate follow-up once this pass proves out the process — same reasoning
`docs/I18N_SAMPLE_GUIDES_2026-07-15.md` used for scoping languages).

**Finding from the first batch (6 files: `Home`/`Home_fr`, `FAQ`/`FAQ_fr`,
`samples/README.md`, two Tutorials HTML files) — recalibrate expectations
before working the rest of the queue.** Most of this content is already
clean: `samples/README.md` and the Tutorials HTML checked so far are dense,
specific, and direct, with none of the classic AI-slop rhetorical patterns
(no banned words, no binary contrasts, no fake-profound kickers, no
summary-recap endings). Expect most files to need **no changes** — don't
force edits to hit a quota. The one real, *recurring* issue found so far: a
generic "Contributions are welcome! See our contributing guidelines
for: / bug reports / code / translations / docs" boilerplate block,
templated near-verbatim across at least `Home.md`, `Home_fr.md`, `FAQ.md`,
and `FAQ_fr.md` — pointing at a `CONTRIBUTING.md` that doesn't exist and
listing categories generically instead of just linking the issue tracker.
Fixed in all four; **grep for this pattern in any new file before reading
it in full** (`Contributions are welcome`, `contributions sont les
bienvenues`, `Consultez.*contribution`) — it may recur in files not yet
checked (Getting-Started.md, Tutorials.md, and their `_fr` counterparts are
plausible next hits since they're similarly high-traffic entry pages).

**Process per file:** Read → identify the core point + 3–5 voice signals to
preserve (per SKILL.md step 2) → make the minimum effective edit → check
against `eval.md` → commit. Batch related files (e.g. one sample's EN+FR
README pair, or a handful of small wiki pages) into one commit rather than
one-commit-per-file — 242 files is too many commits otherwise — but keep
batches small enough to review, per the standing one-task-per-commit
discipline. Flip `[ ]` → `[x]` with the commit hash as each batch lands.

**Known pre-existing anomaly, NOT in scope to fix here** (noted so it isn't
mistaken for cleanup work): `Tutorials/07_platformer/` and
`Tutorials/08_lunar_lander/` have only 4 English lesson files each but 10
French ones (`Tutorials/fr/07_platformer/`, `Tutorials/fr/08_lunar_lander/`)
— the French versions are more granular/complete, not just translations of
the English files. Content-completeness parity is a separate job; this
registry only tracks *prose quality* of whatever exists in each file.

## A. In-app Tutorials (English) — `Tutorials/<NN_name>/*.html`

Post-deletion (Update 5): 41 live files, exactly matching `index.json`'s
`pages` arrays. `[x]` = read in full; `[~]` = edited (emoji/boilerplate,
already committed); `[ ]` = not yet read for paragraph-level polish.

- [x] 01_getting_started/01_welcome
- [x] 01_getting_started/02_interface
- [x] 01_getting_started/03_first_project
- [x] 01_getting_started/04_next_steps
- [x] 02_first_game/01_introduction
- [x] 02_first_game/02_moving_player
- [x] 02_first_game/03_falling_stars
- [x] 02_first_game/04_scoring
- [x] 02_first_game/05_finishing
- [x] 03_pong/01_introduction
- [x] 03_pong/02_paddles_and_ball
- [x] 03_pong/03_goals_and_scoring
- [x] 03_pong/04_score_display
- [x] 04_breakout/01_introduction
- [x] 04_breakout/02_sprites_basic
- [x] 04_breakout/03_paddle_and_ball
- [x] 04_breakout/04_first_room
- [x] 04_breakout/05_first_bricks
- [x] 04_breakout/06_more_bricks
- [x] 04_breakout/07_game_controller
- [x] 05_sokoban/01_introduction
- [x] 05_sokoban/02_player_and_walls
- [x] 05_sokoban/03_pushing_crates
- [x] 05_sokoban/04_targets_and_controller
- [x] 06_maze/01_introduction
- [x] 06_maze/02_player_and_maze
- [x] 06_maze/03_coins_and_exit
- [x] 06_maze/04_game_controller
- [x] 07_platformer/01_introduction
- [x] 07_platformer/02_jumping_player
- [~] 07_platformer/03_coins_and_hazards *(fixed a Show-message block's
  category color/class — labeled block-room, should be block-output per
  its own explanatory text; same fix applied to the French pair)*
- [x] 07_platformer/04_game_controller
- [~] 08_lunar_lander/01_introduction *(emoji removed from H1)*
- [x] 08_lunar_lander/02_flying_lander
- [x] 08_lunar_lander/03_landing_and_crashing
- [~] 08_lunar_lander/04_game_controller *(emoji removed from congrats)*
- [x] 09_catch_the_coins/01_introduction
- [x] 09_catch_the_coins/02_moving_player
- [x] 09_catch_the_coins/03_coins_and_enemy
- [x] 09_catch_the_coins/04_catching_and_crashing
- [x] 09_catch_the_coins/05_winning

**Section A: 41/41 done.**

## B. In-app Tutorials (French) — `Tutorials/fr/<NN_name>/*.html`

Same 41-file list as section A (post-deletion, both languages match
exactly). Not tracking per-file here to avoid duplicating the whole list —
once an English file's paragraph-level content is confirmed clean/fixed,
diff its French counterpart against it for the same issue rather than
re-reading French cold each time (translations of already-fixed English
should inherit the fix; translations of already-clean English are a
lower-priority read). Exceptions already touched:
- [~] fr/06_maze/01_introduction *(emoji removed from H1)*
- [~] fr/06_maze/02_create_sprites *(deleted — was an orphan)*
- [~] fr/08_lunar_lander/04_game_controller *(emoji removed from congrats)*

## C. Sample guides — English (`samples/*/README.md`)

- [x] samples/README.md (top-level index) *(reviewed, no changes — dense,
  specific, already reads like a careful human wrote it: real numbers,
  named commits, honest caveats about what was dropped and why)*
- [x] match3_1, match3_2, match3_3
- [x] maze_1, maze_2, maze_3, maze_4
- [x] plateforme_1, plateforme_2, plateforme_3
- [x] raycast_1, raycast_2 *(fixed a wrong quoted in-game message —
  French text where the actual message is English)*, raycast_3, raycast_4
- [x] treasure
- [x] views_1, views_2

(18 files. Section C: 18/18 done.)

## D. Sample guides — French (`samples/*/README.fr.md`)

- [x] match3_1, match3_2, match3_3
- [x] maze_1, maze_2, maze_3, maze_4
- [x] plateforme_1, plateforme_2, plateforme_3
- [x] raycast_1, raycast_2, raycast_3, raycast_4
- [x] treasure
- [x] views_1, views_2

**Review method note (lighter-touch than Sections E/F):** given Section
C's finding that the English originals are exceptionally accurate
already, this pass checked (a) an accent-completeness heuristic grep
across all 17 files for common unaccented-word patterns — clean, (b) every
quoted string (« ... » and "...") across all 17 for language-mismatch bugs
like the one already fixed in raycast_2 — found 2 English-in-French
quotes, both verified legitimate (match3_3's in-game message, which stays
English per the established "sample messages aren't auto-translated"
convention; maze_2/maze_3's literal cross-reference to
`docs/ASSET_LICENSES.md`'s English-only "### Remaining maze assets"
heading, confirmed to exist verbatim), and (c) one full spot-check
(match3_1) with its Android/HTML5 support dates cross-checked against the
English README.md — exact match. This did **not** re-derive every
technical claim against source code the way the wiki pages in Sections
E/F got (that would mean re-verifying ~17 files' worth of engine/export
internals already covered once for their English originals) — if a future
session has reason to distrust a specific French sample guide's technical
claim, verify that claim specifically rather than assuming this pass covered it.

(17 files — no top-level `samples/README.fr.md` exists.)

## E. Wiki — English (`wiki/*.md`, no language suffix)

- [x] Home.md *(fixed generic "contributing guidelines" boilerplate that
  pointed at a nonexistent doc)*
- [x] Getting-Started.md *(3 accuracy fixes, not wording: the real menu
  bar is File/Edit/Assets/Build/Tools/Help — not "Resources, Run"; language
  switching is Tools > Language, not a Preferences dropdown (Preferences
  has no language option at all); the Linux troubleshooting apt line named
  `python3-pyqt6` for a PySide6 project and was missing several of the
  actually-required xcb libs — replaced with docs/BUILDING.md's real list)*
- [x] Getting-Started-Breakout.md *(dropped a redundant "you are now
  initiated..." closing sentence restating the See Also section above it)*
- [x] Creating-Your-First-Game.md *(2 accuracy fixes: "Jump to Random
  Position (horizontal only)" isn't a real mode of that action — it always
  randomizes both X and Y across the whole room (checked
  execute_jump_to_random_action) — swapped for Jump To Position with
  X `irandom(600)`, Y `20`, which actually does what the tutorial wants;
  and "Run > Run Game" doesn't exist as a menu — real path is Build > Test
  Game)*
- [x] Events-and-Actions.md *(this hand-written action reference had never
  been cross-checked against events/action_types.py: fixed wrong/nonexistent
  action names — "If Variable"/"If Expression" don't exist (real: Test
  Variable/Test Expression), "Show Info" (real: Show Game Info), "If Sound
  Playing" (real: Check Sound Playing); merged the fabricated separate "Set
  Font"/"Set Alignment" actions into the one real action that covers both
  (Set Draw Font), and disambiguated "Set Color" (real: two DIFFERENT
  actions — Set Draw Color for text/shapes, Set Color for sprite tint —
  the table conflated them into one); fixed Draw Lives/Draw Health Bar's
  wrong parameter lists; fixed "Jump to Random" to note it randomizes BOTH
  axes (same misconception that broke Creating-Your-First-Game.md, see that
  commit); most importantly fixed the `speed` built-in variable — the table
  claimed "Total movement speed" but it's the sprite's *animation* rate
  (confirmed: game_runner.py's `self.speed = 10.0  # Animation FPS`) —
  there is no built-in movement-magnitude variable, a real landmine also
  documented in the LunarLander tutorial fix)*
- [x] Event-Reference.md *(see Update 12: execution-order fix + 18/23
  wrong per-event Preset rows corrected + Events-by-Preset table rebuilt)*
- [x] Full-Action-Reference.md *(generated — see CLAUDE.md: edit
  `tools/action_ref_i18n.py`/`tools/gen_action_reference.py`, not this file
  directly. The see-also line Update 12 left imprecise is now fixed
  (`gen_action_reference.py`'s `sa_preset` chrome string) and regenerated)*
- [x] Visual-Programming.md *(MAJOR: cross-checked every block table against
  the real, complete `config/blockly_config.py` BLOCK_REGISTRY — most of the
  page was fabricated. No Math/Logic/Text toolbox category exists at all;
  the real category is "Control". No boolean/hexagon reporter blocks, no
  Repeat block, no comparison/and-or-not blocks — conditionals are flat
  GM80-style stack blocks (If Condition/Test Variable have ONE "then" slot,
  paired with separate Else/Start Block/End Block blocks), not Scratch-style
  if/else containers, confirmed against the actual block JS in
  `blockly_blocks.js`. `( speed )`/`( direction )` reporter blocks don't
  exist (only 9 real Values reporters: X/Y Position, H/V Speed, Score,
  Lives, Health, Mouse X/Y). Jump to Start/Random Position, Draw Sprite,
  Set Drawing Color, per-sound Stop Sound have no Blockly block at all
  (structured-panel-only actions). Full rewrite from the verified block
  list; also links to Preset-Guide.md now that Update 12 established
  presets gate the Blockly palette too. En route, verified `set_speed`/
  `set_direction` (initially suspected dead — no `execute_set_speed_action`
  method) are real, implemented via the modular
  `runtime/action_handlers/movement_handlers.py` registration path, and
  correctly derive movement magnitude from hspeed/vspeed rather than the
  animation-rate `speed` attribute — not a bug, false alarm caught before
  writing it down as one.)*
- [x] Object-Editor.md *(4 wrong action names fixed: Draw Health -> Draw
  Health Bar; If Score/If Lives/If Health -> Test Score/Test Lives/Test
  Health; If Variable -> Test Variable; Move Toward Point -> Move Towards
  Point. Depth/Persistent claims verified accurate against game_runner.py)*
- [x] Room-Editor.md *(2 incomplete-not-wrong claims filled in: background
  layers capped at 8 (widgets/enhanced_properties_panel.py), views capped
  at 8 (game_runner.py `for i in range(8)`) — both verified against code.
  Depth/room-order/persistent claims spot-checked and already accurate)*
- [x] 3D-View.md *(reviewed, no changes — spot-checked the highest-risk
  claims (facing_angle 0=right/90=up convention, cell_size default 32)
  against extensions/raycast_2_5d/actions.py and both matched exactly;
  this page was clearly written with direct engineering knowledge of the
  feature, consistent with the extensive raycast session-notes history)*
- [x] Extensions.md *(reviewed, no changes — verified config key
  "extensions", project.json's requires_extensions field, extension.json's
  provides_actions manifest field, and the raycast_2_5d folder listing all
  match the real code exactly)*
- [x] Exporting-Games.md *(reviewed, no changes — verified File > Export
  Project.../Export as HTML5.../Export to Kivy... menu paths and Ctrl+E
  shortcut against core/ide_window.py, all exact matches; consistent with
  the export-guide accuracy pass already noted in CLAUDE.md's 2026-07-19 entry)*
- [x] Preset-Guide.md *(see Update 12: corrected framing + Edition-vs-preset
  mapping, dropped hardcoded drift-prone counts)*
- [x] Beginner-Preset.md *(see Update 12: now generated by
  tools/gen_preset_docs.py — never edit by hand)*
- [x] Intermediate-Preset.md *(see Update 12: same, generated)*
- [x] FAQ.md *(same contributing-boilerplate pattern as Home.md, plus a
  redundant "How can I contribute?" Q&A duplicating the bug-report entry
  above it; also trimmed a non-sequitur "contributions welcome" aside
  tacked onto the licensing answer)*
- [x] Tutorials.md *(real finding: claimed all 6 listed tutorials "use the
  Beginner Preset", but config/blockly_config.py's get_beginner()/
  get_intermediate() docstrings say plainly that Sokoban/Maze/Platformer/
  LunarLander need Intermediate (grid movement, if_can_push aren't in
  Beginner) — only Pong/Breakout are genuinely Beginner. Split into two
  sections and fixed the "Set Your Preset" getting-started step. Given
  Update 12, this was actively misleading: new projects default to
  Beginner, so a reader following this page's old advice into Sokoban
  would find Move Grid/If Can Push missing from both editors)*
- [x] Tutorial-Pong.md *(real finding: the whole scoring system was built
  on a fabricated capability — "Set Score" with a "Variable:" field
  pointing at global.p1score/p2score. The real Set Score action
  (events/action_types.py) has only value/relative params; it always
  writes the single built-in score, no variable selector. Replaced with
  the real Set Variable action (variable/value/scope/relative) in all 4
  places. Also fixed "Bounce Against Objects... Select 'Against solid
  objects'" (real Bounce action has zero parameters, no selection step),
  "Start Moving in Direction" -> "Start Moving (Direction)" (real display
  name), and the Speed Increase enhancement's `speed + 0.5` expression —
  same `speed`-is-animation-rate landmine as Events-and-Actions.md/
  LunarLander, would have silently used the wrong baseline; replaced with
  a tracked `ball_speed` custom variable)*
- [x] Tutorial-Breakout.md *(2 fixes: "Reverse Vertical (applied to
  other)" for the brick-bounces-ball step doesn't work — Reverse Vertical
  takes zero parameters, no applies-to option (confirmed against
  events/action_types.py, same class of bug as the Object-Editor/Pong
  finds) — the tutorial's own fallback alternative (put it on the ball's
  own collision event) was already correct, kept that and dropped the
  broken option; "Move in Direction" -> "Start Moving (Direction)" (real
  display name). "Add Score"/"Add Lives"/"Add Health" verified as real
  legacy aliases for set_score/set_lives/set_health(relative=True) — not
  a bug, left as-is)*
- [x] Tutorial-Sokoban.md *(GML-fabrication rewrite, see Update 11 — `6c825d9`)*
- [x] Tutorial-Maze.md *(GML-fabrication rewrite, see Update 11 — `90db80b`)*
- [x] Tutorial-Platformer.md *(GML-fabrication rewrite, see Update 11 — `cde99fd`)*
- [x] Tutorial-LunarLander.md *(GML-fabrication rewrite, see Update 11)*

(23 files.)

## F. Wiki — French (`wiki/*_fr.md`)

Filenames don't all mirror the English slugs 1:1 (some pages have French
slugs, e.g. `Demarrage_fr.md` = Getting-Started, `Premier_Jeu_fr.md` =
Creating-Your-First-Game) — match by content, not filename, when pairing
with section E.

- [x] Home_fr.md *(same fix as Home.md)*
- [x] Demarrage_fr.md *(same 2 menu-accuracy fixes as Getting-Started.md;
  no Linux troubleshooting section in this shorter French version)*
- [x] Getting-Started-Breakout_fr.md *(same fix as Getting-Started-Breakout.md)*
- [x] Premier_Jeu_fr.md *(shorter than English — no Jump to Random Position
  step exists here to fix; just the "Exécuter > Lancer le jeu" menu fix,
  same as English's Run > Run Game issue)*
- [x] Evenements_Actions_fr.md *(same accuracy fixes as Events-and-Actions.md;
  French display names sourced from tools/action_ref_i18n.py's ACTIONS_FR
  table — the project's one authoritative French action-name catalog,
  confirmed the ONLY one that actually ships: pygm2_fr_actions.ts's
  translations are all `type="vanished"` and there is no compiled
  pygm2_fr_actions.qm at all, so the in-app Actions panel shows English
  action names in every language regardless of the selected UI language —
  this is a known, accepted state (CLAUDE.md's ".ts files are useless for
  this" note), not a new bug, and translating wiki action names anyway
  matches the project's own generated Full-Action-Reference convention)*
- [x] Event-Reference_fr.md *(same fixes as Event-Reference.md, see Update 12)*
- [x] Full-Action-Reference_fr.md *(generated — same fix as Full-Action-Reference.md, regenerated)*
- [x] Programmation_Visuelle_fr.md *(same fixes as Visual-Programming.md, see Update 13)*
- [x] Editeur_Objets_fr.md *(shorter than English — none of the wrong-name
  issues fixed in Object-Editor.md are present here; no changes needed)*
- [x] Editeur_Salles_fr.md *(shorter than English — no Background Layers or
  Views sections exist here to need the same fix; no changes needed)*
- [x] 3D-View_fr.md *(reviewed, no changes — accurate mirror of 3D-View.md)*
- [x] Extensions_fr.md *(reviewed, no changes — accurate mirror of Extensions.md)*
- [x] Exportation_fr.md *(reviewed, no changes — accurate, complete translation)*
- [x] Preset-Guide_fr.md *(same fixes as Preset-Guide.md, see Update 12)*
- [x] Beginner-Preset_fr.md *(generated by tools/gen_preset_docs.py, see Update 12)*
- [x] Intermediate-Preset_fr.md *(same, generated)*
- [x] FAQ_fr.md *(same fix as FAQ.md)*
- [x] Tutorials_fr.md *(same fix as Tutorials.md)*
- [x] Tutorial-Pong_fr.md *(same fixes as Tutorial-Pong.md)*
- [x] Tutorial-Breakout_fr.md *(same fixes as Tutorial-Breakout.md)*
- [x] Tutorial-Sokoban_fr.md *(GML-fabrication rewrite, see Update 11 — `6c825d9`)*
- [x] Tutorial-Maze_fr.md *(GML-fabrication rewrite, see Update 11 — `90db80b`)*
- [x] Tutorial-Platformer_fr.md *(GML-fabrication rewrite, see Update 11 — `cde99fd`)*
- [x] Tutorial-LunarLander_fr.md *(GML-fabrication rewrite, see Update 11)*

(24 files.)

## Publishing note

Wiki edits live in `wiki/*.md` in this repo and only reach the live GitHub
wiki via `scripts/sync_wiki.sh push` (see CLAUDE.md's 2026-07-29 entry) —
that's an outward-facing publish step requiring explicit approval, separate
from committing the edits here. Don't run it as part of this cleanup queue
without asking first.

## Progress

Total: 242 files across 6 categories. Work top to bottom within each
category, batching a few files per commit. Nothing fixed yet — this is the
starting registry.
