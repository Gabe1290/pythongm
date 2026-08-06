# Reader-facing docs: AI-slop cleanup registry

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
- [ ] match3_1, match3_2, match3_3
- [ ] maze_1, maze_2, maze_3, maze_4
- [ ] plateforme_1, plateforme_2, plateforme_3
- [ ] raycast_1, raycast_2, raycast_3, raycast_4
- [ ] treasure
- [ ] views_1, views_2

(18 files.)

## D. Sample guides — French (`samples/*/README.fr.md`)

- [ ] match3_1, match3_2, match3_3
- [ ] maze_1, maze_2, maze_3, maze_4
- [ ] plateforme_1, plateforme_2, plateforme_3
- [ ] raycast_1, raycast_2, raycast_3, raycast_4
- [ ] treasure
- [ ] views_1, views_2

(17 files — no top-level `samples/README.fr.md` exists.)

## E. Wiki — English (`wiki/*.md`, no language suffix)

- [x] Home.md *(fixed generic "contributing guidelines" boilerplate that
  pointed at a nonexistent doc)*
- [ ] Getting-Started.md
- [ ] Getting-Started-Breakout.md
- [ ] Creating-Your-First-Game.md
- [ ] Events-and-Actions.md
- [ ] Event-Reference.md
- [ ] Full-Action-Reference.md *(generated — see CLAUDE.md: edit
  `tools/action_ref_i18n.py`, not this file directly, if wording needs to
  change; a slop pass here means fixing the generator template strings)*
- [ ] Visual-Programming.md
- [ ] Object-Editor.md
- [ ] Room-Editor.md
- [ ] 3D-View.md
- [ ] Extensions.md
- [ ] Exporting-Games.md
- [ ] Preset-Guide.md
- [ ] Beginner-Preset.md
- [ ] Intermediate-Preset.md
- [x] FAQ.md *(same contributing-boilerplate pattern as Home.md, plus a
  redundant "How can I contribute?" Q&A duplicating the bug-report entry
  above it; also trimmed a non-sequitur "contributions welcome" aside
  tacked onto the licensing answer)*
- [ ] Tutorials.md
- [ ] Tutorial-Pong.md
- [ ] Tutorial-Breakout.md
- [ ] Tutorial-Sokoban.md
- [ ] Tutorial-Maze.md
- [ ] Tutorial-Platformer.md
- [ ] Tutorial-LunarLander.md

(23 files.)

## F. Wiki — French (`wiki/*_fr.md`)

Filenames don't all mirror the English slugs 1:1 (some pages have French
slugs, e.g. `Demarrage_fr.md` = Getting-Started, `Premier_Jeu_fr.md` =
Creating-Your-First-Game) — match by content, not filename, when pairing
with section E.

- [x] Home_fr.md *(same fix as Home.md)*
- [ ] Demarrage_fr.md
- [ ] Getting-Started-Breakout_fr.md
- [ ] Premier_Jeu_fr.md
- [ ] Evenements_Actions_fr.md
- [ ] Event-Reference_fr.md
- [ ] Full-Action-Reference_fr.md *(generated — same caveat as E)*
- [ ] Programmation_Visuelle_fr.md
- [ ] Editeur_Objets_fr.md
- [ ] Editeur_Salles_fr.md
- [ ] 3D-View_fr.md
- [ ] Extensions_fr.md
- [ ] Exportation_fr.md
- [ ] Preset-Guide_fr.md
- [ ] Beginner-Preset_fr.md
- [ ] Intermediate-Preset_fr.md
- [x] FAQ_fr.md *(same fix as FAQ.md)*
- [ ] Tutorials_fr.md
- [ ] Tutorial-Pong_fr.md
- [ ] Tutorial-Breakout_fr.md
- [ ] Tutorial-Sokoban_fr.md
- [ ] Tutorial-Maze_fr.md
- [ ] Tutorial-Platformer_fr.md
- [ ] Tutorial-LunarLander_fr.md

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
