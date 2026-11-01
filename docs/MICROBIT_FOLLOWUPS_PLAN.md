# micro:bit follow-ups — the small coding work that remains

Written 2026-11-01. Everything here is optional and small; nothing needs hardware. It is the
"Open" list at the bottom of `TODO.md` → "micro:bit extension — follow-ups", turned into units.
Resume state = the checkboxes. **One unit = one commit** (fix + regression test + full-suite
gate, nothing excluded), pushed to `main` straight away (session-limit rule in `CLAUDE.md`).

Order is by value to a student/teacher, then by risk. M1–M2 are what a user sees; M3–M5 are
correctness edges; M6 is a spare-time sweep; M7 only if a teacher asks.

Ground rules that apply to every unit
- Re-verify the claim against current code first (a TODO line is a lead, not ground truth) and
  write what you found in the unit's commit body.
- Mutation-check each new test (a test that survives its own removal of the fix is not a test).
- French text keeps its accents. New UI strings go into all 10 shipped `.ts` files (see
  `tests/test_microbit_export_ui_translations.py` for the pattern that proves they resolve).
- The Kivy scene template is `.format()`-based: literal braces in core template code are doubled
  (extension `SCENE_CODE` is injected after, so it is not).

---

## M1. Blocks drawn in the micro:bit's own colour — [ ]

**Problem.** The extension's generated Blockly action blocks draw grey (`#888888`). In
`blockly_workspace.html` (~line 3687) the colour is
`TOOLBOX_GROUP_COLORS[toolboxGroupOf(d.category)] || categoryColors[d.category] || '#888888'`,
and `categoryColors` is a hard-coded core table that has no entry for an extension's category.
(The code comment there already calls this out: "an extension's own category".)

**Design (generic seam, ~20 lines).** Let an extension declare a category colour the same way it
already declares categories, presets and translations: a new optional module attribute
`PLUGIN_BLOCK_CATEGORY_COLORS = {"micro:bit": "#...", ...}` read in
`events/plugin_loader.py` next to `PLUGIN_BLOCK_CATEGORY_TRANSLATIONS`, stored in a small
registry in `config/blockly_config.py` (`register_block_category_colors`, first name wins, plus
an `unregister_` for tests, mirroring `register_block_categories`), and pushed to the page with
the other lists in `editors/object_editor/blockly_widget.py` (`blocklyApi.setCategoryColors`,
merged into `categoryColors` before blocks are created). The same table must also colour the
extension's toolbox `<category colour=…>` (line ~3586) so a block matches its drawer.
Use every extension that has a category (microbit, multiplayer_lan, multiplayer_files, thymio,
block_world), not just micro:bit — otherwise it is not a seam.

**Check first.** Order of operations: are `registerCustomBlocks(defs)` and the colour push
ordered so the colours exist when blocks are built? Read how `setAssetLists` /
`setExtensionEvents` are sequenced in `blockly_widget.py` (~line 384) before choosing where to
push.

**Tests.** Pure: registry round-trip + loader reads the attribute + the JSON pushed to the page
contains the colour. Page-level (QtWebEngine, skipped without it — and note the A1 crash flake
lives in these files, so reuse the module-scoped `round_tripped` fixture, do not add a new
`QWebEngineView`): a generated micro:bit block reports the declared colour. Mutation: drop the
merge, the block goes grey.

**Done when:** micro:bit blocks and its drawer share a colour and no core category colour moved.
Needs a human glance afterwards (QA checklist §11a) — say so in the commit.

## M2. Extension-event drop-down labels translated — [ ]

**Problem.** `event_extension`'s drop-down (`EXTENSION_EVENT_MENU`, pairs of
`[label, value]`) is built in Python and the labels are English ("Player joined"). Everything
else on the block is translated through `getBlockMessage`.

**Design.** Find where the menu is built in `blockly_widget.py` (the `setExtensionEvents`
payload) and resolve each label through the same translation path the action blocks use. The
data side already exists for actions: `PLUGIN_GENERATED_BLOCK_TRANSLATIONS`
(`config/blockly_generated_block_i18n.py::register_generated_block_translations`). Add an
`"events": {event_name: {lang: label}}` key to that mapping (first entry wins, same as actions),
fill it for micro:bit's 24 events and the two multiplayer extensions, and have the widget look
the label up for the IDE language, falling back to the English label. Keep event *values*
untouched (they are the literal event names the loader compares).

**Open question to settle in the unit:** which languages. French is mandatory (it is the
user-facing language of the classes this is for); the other nine get English fallback unless
cheap. One language ≈ 24+ short strings for micro:bit — do FR only first, commit, then decide.

**Tests.** The label resolves per language; unknown language/event falls back to English; the
value is unchanged; a French label keeps its accents. Mutation: remove the lookup, label reverts.

## M3. Generated-block text for the other nine languages — [ ]

**Problem.** `PLUGIN_GENERATED_BLOCK_TRANSLATIONS` for micro:bit carries French only; the other
nine IDE languages show English block text. Same shape for the multiplayer extensions (their
`actions.py` is French-first, which is a separate wrinkle: the English text the live IDE shows
is already French — see `TODO.md` "micro:bit/Network i18n gap").

**Cost (measured before, `CLAUDE.md` 2026-07-20):** ~40 % of a session per language for a large
corpus; this one is 16 micro:bit actions + their parameter labels + (after M2) 24 event labels,
so roughly a tenth of that per language. **Do one language per commit**, most-used first (ask
which; German and Spanish are the largest of the shipped set), and stop whenever the budget
says so — the English fallback makes any stopping point safe.

**Not in scope:** the multiplayer extensions' French-first display text. If wanted it is its own
unit (needs an English source of truth added to `actions.py` first), not part of M3.

**Tests.** Extend the pattern of `tests/test_extension_ui_translations.py`: every source has a
non-empty translation in the language, differs from English except a documented cognate list,
and resolves through the live path. Accents checked for fr/de/es/it/pt/ru/uk/sl.

## M4. Boards and clicks in a room with a scrolling view — [ ]

**Problem.** `extensions/microbit/input.py::mouse_down` hit-tests in screen space, and the
overlay (`renderer.py`) draws in screen space. In a room with views enabled (camera scrolling)
that is consistent *with itself* — the board is a HUD-like overlay — but the object that owns
the board still has room coordinates, so the board's placement and hit area can disagree with
where the author put the object, and the Kivy twin has the same assumption.

**Step 0 — decide whether it is a bug at all.** Read how `layout_for(instance)` places the
board (from `instance.x/y`?) and how views translate room → screen elsewhere in the runtime
(`runtime/` view code; samples `views_1`, `views_2`). Build a 10-line repro: a micro:bit object
at room (500, 300), a view scrolled to x = 400. Two honest outcomes:
- the board draws at its *screen* position regardless of the view → document that "a board is a
  screen overlay by design", pin it with a test, close the unit with no engine change;
- it draws at room position but is hit-tested at screen position (or vice versa) → fix the
  mismatch with the runtime's own view transform, on all three targets (desktop `renderer.py` +
  `input.py`, HTML5 `export_html5.js`, Kivy `kivy_draw.py` + `kivy_touch.py`), with the
  Python-oracle differential tests the HTML5/Kivy ports already have.

**Why this is last of the correctness items:** the answer may be "by design", and the fix, if
needed, touches three renderers that have no way to be eyeballed here.

## M5. Two boards sounding at once — [ ]

**Problem.** `extensions/microbit/audio.py` reserves pygame mixer channel 0 for "the speaker", so
a second board's note replaces the first board's. Documented as a limit, never a bug report.

**Design.** Key the channel by board: reserve N channels (N = number of micro:bit instances in
the room, capped, e.g. 4), map `simulator_of(instance)` → channel index, keep `play`/`stop`
signatures taking an optional `channel_id` defaulting to 0 so the current single-board path and
its tests are byte-identical. Constraints already learned the hard way: **never cache pygame
`Channel`/`Sound` across calls** (dangles after `pygame.quit()`), so the board → index map holds
integers only, and the channel is fetched fresh each call. `set_num_channels(8)` is already
done; make sure the reserved count never exceeds it.

**Parity.** HTML5 uses WebAudio (a new oscillator per note — check whether two boards already
overlap there; if so desktop is the only one to fix). Kivy: `kivy_audio.py` — read before
deciding; it may already play on independent `SoundLoader` instances.

**Tests.** Two boards play two notes and both are audible (two reserved channels busy); stopping
one leaves the other; one board behaves exactly as before; mutation: collapse back to channel 0
and the two-board test fails.

## M6. Kivy export against REAL Kivy — a bounded sweep — [ ]

**Why.** A9 showed real Kivy 2.3.1 runs headless here (`tests/_real_kivy_render.py`, subprocess,
skips where Kivy/GL are missing). Most Kivy export tests still use the stub harness, which cannot
catch a wrong Kivy API call. One A9 bug class (the unconditional `Triangle` import) was found
only this way.

**Scope it hard** or it never ends: add a *second* worker scenario per area, each in its own
commit, in this order of likely yield — (1) a generated `main.py` for `samples/plateforme_3`
imports and builds its first scene; (2) the raycast scene overlay renders a frame with a non-black
pixel; (3) the draw queue's `sprite` command with `subimage` crops. Stop after the three; each
either passes (record it) or exposes a real bug (fix it in that commit).

**Constraints.** Creating a graphics instruction without a window segfaults — always the
subprocess worker; the worker must exit on its own with a hard timeout so it cannot hang CI.

## M7. "New micro:bit project" template — [ ] (only if a teacher asks)

Dropped in S10 because templates are core (`resources/templates/<id>` plus a fixed combo in the
New Project dialog; see `docs/MICROBIT_EXTENSION_PLAN.md` "Decided in S10"). Revisit only on
request. If done: the smallest change is a template that copies `samples/microbit_1`'s
structure with the extension pre-activated, via an extension-contributed template hook rather
than editing the combo by hand — which is itself a new core seam, so confirm demand first.

---

## Order and cost

| Unit | Rough size | Risk | Needs a human glance after |
|---|---|---|---|
| M1 colours | small (one seam, 3 files + test) | low | yes (QA §11a) |
| M2 event labels | small | low | no |
| M3 other languages | one language per commit | none (fallback) | no |
| M4 scrolling views | unknown until Step 0 | medium if real | yes |
| M5 per-board speaker | small–medium | low | by ear |
| M6 real-Kivy sweep | three small scenarios | low | no |
| M7 template | only on request | — | — |

Start with M1 (the only item a student would notice), then M2, then M3 in the language order the
user picks. M4 starts with its Step 0, which may close it in minutes.
