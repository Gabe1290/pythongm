# Plan: working through TODO.md's deferred items

Status: **planned, not started.** Written 2026-07-15, right after the
views/camera plan (`docs/VIEWS_SAMPLES_PLAN.md`) shipped, specifically so
it can be picked up cold on a different machine. This doc triages and
sequences `TODO.md`'s registry — it doesn't replace it. `TODO.md` stays
the source of truth for each item's detail; this doc just says which
order to tackle them in and why.

## Before touching anything: re-verify, don't trust

While drafting this plan, two `TODO.md` claims turned out to be stale —
the Kivy and HTML5 exporters were both claimed to skip `sprite`/`lives`
draw-queue commands, but both actually implement them now (landed
earlier the same day, with the match3_2 sound-queue work and the views
work). Corrected in `TODO.md` directly. **This is exactly the "audit is
a lead, not ground truth" discipline `CLAUDE.md` already documents for
the code-audit work — apply it here too.** Before starting any item
below, grep for the specific claim against current code first; don't
assume the registry is accurate just because it's the most detailed
document available. A chunk of this registry predates several sessions'
worth of shipped work and hasn't been swept since.

## Tier 1 — small, contained, ready to start (no design questions)

Good candidates for a "one task = one commit, verify, push" queue, same
discipline as the match3_2/3 and views sessions:

1. ~~**Generic asset-type editor fallback**~~ **DONE 2026-07-15** —
   `editors/sound_editor.py` / `background_editor.py` / `font_editor.py`,
   following the `scripts` editor's template. Found along the way: the
   font asset's fields aren't consumed by `draw_text` rendering yet
   (new TODO.md entry) — **also DONE 2026-07-16**, see below.
2. ~~**Kivy/HTML5 draw-queue `background`/`health_bar` types**~~ **DONE
   2026-07-15** — `BACKGROUND_PATHS` map + both `_dq_render_cmd` branches
   on Kivy, both `case`s in `engine.js`. Found along the way: structured
   `draw_rectangle`/`circle`/`ellipse`/`line`/`arrow`/`variable`/
   `health_bar`/`background` *actions* (not `execute_code` draw-queue
   dicts) have no codegen on either export target at all — **also DONE
   2026-07-16**, see below.
3. ~~**Object test runner ("Play Object" button)**~~ **DONE 2026-07-15** —
   runs the object in a throwaway temp project through the same
   `_run_project_json` path Test Game now shares (factored out of
   `test_game`). Turned out less "small" than it looked: the refactor
   changed `test_game`'s observable call shape, which broke 3
   pre-existing tests' lightweight `PyGameMakerIDE` stubs (they needed
   the newly-factored-out method added, same convention those stubs
   already used elsewhere) — worth remembering for the remaining tier-1/2
   items: touching a method other tests stub out has a wider blast radius
   than the diff alone suggests.
4. ~~**Room transition effects**~~ **DONE 2026-07-15** — `goto_room`'s
   `transition='fade'` fades to black, switches, fades back in
   (`GameRunner._fade_overlay`). Scoped to desktop only (no sample
   exercises the parameter at all yet, so there was nothing to verify
   Kivy/HTML5 parity against — see the TODO.md entry). Worth noting: the
   first draft's alpha ramp was inverted (screen went black and stayed
   black); a pixel-sampling test plus a 10-frame visual montage caught it
   before it shipped — a "doesn't crash" test alone would have missed it.
   **Tier 1 is now fully closed.**

## Tier 2 — moderate effort, clear scope, one design decision each

5. ~~**Find / Find and Replace**~~ **DONE 2026-07-16** — code-editor-only,
   as recommended below. `dialogs/find_replace_dialog.py` +
   `core/ide_window.py`'s `find`/`find_replace`/`_show_find_dialog`/
   `_find_target_text_edit`. Project-wide search (asset names,
   identifiers) and the `execute_code` action dialog's separate `QTextEdit`
   remain open as a follow-up — see `TODO.md`'s entry.
6. ~~**Background auto-scroll on `set_background`**~~ **DONE 2026-07-16** —
   confirmed smaller than it looked, per the re-scoping note: `GameRoom`
   already had a working `bg_hspeed`/`bg_vspeed`-driven scroll renderer;
   `execute_set_background_action` just never wrote its `hspeed`/`vspeed`
   parameters into it. One small wiring fix — see `TODO.md`'s entry.
7. ~~**Standalone executable build**~~ (Build Game / Build and Run, F7/F8)
   **DONE 2026-07-16 — Tier 2 is now fully closed.** Confirmed the
   prediction exactly: thin shells around the existing
   `export.registry.desktop_exporter_for_host` + `_run_export_with_progress`
   machinery, no new export infrastructure. See `TODO.md`'s entry.

## Tier 3 — larger, needs its own finder→verify→fix pass

8. **GMK importer hardening** — the biggest-value item here: reintroduces
   two dropped samples (`treasure`, `maze_4`) and has unusually good
   groundwork already (specific root-cause hypotheses cataloged in
   `TODO.md`'s "GMK importer hardening" section: `if_previous_room_exists`
   swapped with `if_next_room_exists`, `visible: false` defaulting wrong,
   `action_play_sound` mis-mapped to `set_sprite`, missing
   `(1, 223)` → `restart_room` mapping — several sibling bugs in
   maze_1/maze_3 were already found and hand-fixed this way). Treat as
   its own multi-session project: regenerate both samples from their
   `.gmk` sources, catalog every parameter that didn't survive
   conversion, fix each in `importers/gmk_mappings.py` /
   `gmk_converter.py` with a dedicated regression test under
   `tests/test_importers/`, following the exact recipe `TODO.md` already
   lays out. Don't start this inside a single session that's also doing
   other Tier 1/2 items — it has its own investigation phase.
9. **Kivy `execute_code` environment parity** — `game` is `None` on Kivy
   (confirmed this session, same root cause the sound-queue primitive
   worked around) and locals aren't copied back onto the instance after
   `execute_code` runs, unlike desktop/HTML5. Needs a design decision
   first: build a `game` proxy object exposing score/lives (mirroring
   what HTML5's bridge still lacks too — see `TODO.md`'s HTML5 section),
   or accept the gap and document which patterns `execute_code` samples
   must avoid on Kivy. Don't start without deciding that first.
10. **Asset Manager** (`Tools → Asset Manager...`) — bulk rename/move/
    delete, usage tracking ("which rooms/objects use this sprite?"),
    unused-asset cleanup. No small starting subset documented; needs its
    own scoping pass before estimating.
11. **Clean Project** — scope is genuinely vague in `TODO.md` ("remove
    temporary files, delete unused assets, clean build artifacts") and
    overlaps with #10's unused-asset detection. Worth scoping *after*
    Asset Manager, not before — building unused-asset detection twice
    would be wasted work.

## Explicitly not now (already scheduled or deliberately deferred)

- **Manifest-ify objects & sprites in `project.json`** — its own note
  says to do this "carefully... just before the final validation pass
  before the 1.0 release." Don't move it earlier; it changes the on-disk
  save format for every project.
- **ja/pt/zh translation migration** — explicitly post-1.0 in `TODO.md`.
- **Particle system / timelines / save_game / load_game / show_video /
  execute_script UI metadata** — `TODO.md` explicitly says "do NOT add UI
  yet" pending a functional check of the underlying handlers.
- **Splash text/image/video/webpage placeholders, Execute file/shell
  command** — no urgency signal, and the file/shell ones are
  intentionally security-restricted; don't expose without a real
  sandboxing story.
- **Thymio "play sound" placeholder** — niche (Thymio-specific), low
  general priority relative to everything else here.
- **Pyodide offline bundle, right/middle mouse export, Kivy long-tail
  action coverage, on-device Android/buildozer end-to-end test** — real
  but each is either open-ended ("port actions as we hit them") or needs
  infrastructure this repo doesn't have in a headless CI sense (a real
  phone, a real buildozer build). Pick up opportunistically, not as a
  scheduled item.

## Suggested starting point when resuming

**Tier 1 is fully closed (2026-07-15, items 1-4).** Two follow-up items
it surfaced along the way are now **also DONE (2026-07-16)**: font assets
are consumed by `draw_text`/`draw_scaled_text` rendering
(`GameInstance._resolve_draw_font`/`_align_text_pos`,
`tests/test_draw_font_rendering.py`), and structured `draw_*` actions
(rectangle/circle/ellipse/line/arrow/variable/health_bar/background) now
have codegen on both Kivy (`export/Kivy/code_generator.py`) and HTML5
(`export/HTML5/templates/engine.js`'s `executeAction` + a new `'arrow'`
case in `renderDrawCommands`), plus a genuine desktop `_DRAW_HANDLERS`
gap for `'arrow'` that surfaced along the way — see `TODO.md`'s matching
entries for detail; `tests/test_draw_action_codegen.py` covers all three.

**Tier 2 is now fully closed (2026-07-16, items 5-7).** Find/Replace
(code-editor scope, `dialogs/find_replace_dialog.py`), the
`set_background` `hspeed`/`vspeed` scroll wiring (one-line-per-axis fix in
`execute_set_background_action`, confirmed smaller than it looked), and
Build Game/Build and Run (F7/F8 — thin shells around the existing
`export.registry.desktop_exporter_for_host`/`_run_export_with_progress`
machinery, confirmed no new export infrastructure needed as predicted).

Next: start scoping Tier 3. GMK importer hardening is the
highest-value item there, but budget it as its own multi-session project
per the note above (its own investigation phase, regenerate both samples
from `.gmk` sources, catalog every parameter that didn't survive
conversion) — not a single continuation of this session's rhythm. Kivy
`execute_code` environment parity (item 9) needs a design decision first
(build a `game` proxy vs. document the gap) before any code. Asset
Manager / Clean Project (items 10-11) have no small starting subset
documented yet — scope Asset Manager first since Clean Project's
unused-asset detection overlaps it. Re-verify each item's `TODO.md` claim
against current code before starting it, per the discipline above.
