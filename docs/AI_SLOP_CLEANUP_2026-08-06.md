# Reader-facing docs: AI-slop cleanup registry

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

- [ ] 01_getting_started/ (4 files: 01_welcome, 02_interface, 03_first_project, 04_next_steps)
- [ ] 02_first_game/ (11 files: 01_introduction … 07_finishing)
- [ ] 03_pong/ (10 files: 01_introduction … 08_room_setup)
- [ ] 04_breakout/ (10 files: 01_introduction … 08_room_setup)
- [ ] 05_sokoban/ (9 files: 01_introduction … 07_room_setup)
- [ ] 06_maze/ (9 files: 01_introduction … 07_room_setup)
- [ ] 07_platformer/ (4 files: 01_introduction … 04_game_controller)
- [ ] 08_lunar_lander/ (4 files: 01_introduction … 04_game_controller)
- [ ] 09_catch_the_coins/ (5 files: 01_introduction … 05_winning)

(73 files total; `find Tutorials -maxdepth 2 -iname "*.html" -not -path
"*/fr/*"` reproduces the exact list.)

## B. In-app Tutorials (French) — `Tutorials/fr/<NN_name>/*.html`

- [ ] fr/01_getting_started/ (4 files)
- [ ] fr/02_first_game/ (11 files)
- [ ] fr/03_pong/ (10 files)
- [ ] fr/04_breakout/ (10 files)
- [ ] fr/05_sokoban/ (9 files)
- [ ] fr/06_maze/ (9 files)
- [ ] fr/07_platformer/ (10 files — see anomaly note above)
- [ ] fr/08_lunar_lander/ (10 files — see anomaly note above)
- [ ] fr/09_catch_the_coins/ (5 files)

(87 files total; `find Tutorials/fr -iname "*.html"` reproduces the list.)

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
