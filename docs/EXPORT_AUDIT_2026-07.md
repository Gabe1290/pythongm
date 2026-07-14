# Export subsystem audit — 2026-07-12

Scoped adversarial audit of the July 2026 export delta, `engine.js` the
priority target (never previously audited). Method: 4 finders × distinct
lenses → adversarial verification → this registry.

**Run reality:** the workflow hit the account session limit during
verification/synthesis (reset 17:50 Europe/Zurich), so a few verify votes
and the auto-synthesis step did not complete. Findings below carry a
**personal-verification** status; per repo methodology *audit findings are
leads, not ground truth* — nothing is fixed until re-verified against the
actual code. Raw: 19 candidates → 5 confirmed / 14 rejected by the
adversarial pass.

Summary: **1 high / 3 medium / 1 low** — where the 3 mediums reduce to 2
root causes (M2/M3 fold into H1). **All confirmed findings CLOSED
2026-07-12** (H1, M1, L1 fixed with regression tests; L1 also fixed a
related name-as-filename crash it surfaced). Full suite 1523 passed;
68 browser checks green across all 9 samples + the focused H1/M1 harnesses.

---

## High

- [x] **H1 — Unrecognized "question" actions don't gate; guarded branches
  run unconditionally.** FIXED — the 7 question actions are now in
  `isConditionalAction` and implemented in `evaluateCondition` (shared
  `gmExpressionValue` + origin-aware `placeMeetsCollision` helpers); no-op
  stubs removed. Browser-verified (11/11) + `tests/test_html5_conditionals.py`. `export/HTML5/templates/engine.js`
  (`isConditionalAction` @746; stubs @1377–1385).
  `isConditionalAction` recognizes only `if_*`, `test_alignment`,
  `test_variable`, `test_score`, `test_instance_count`. Other GM question
  actions — `test_expression`, `check_empty`, `check_collision` — are
  **not** recognized, so the flat skip-next loop treats them as ordinary
  actions and never sets `skipNext`; the action they were meant to guard
  runs regardless of the condition. Worse, `test_expression`/`check_empty`/
  `check_collision` exist in `executeAction` only as **no-op stubs**
  (`// Would need safe evaluation`, `// Collision checking logic`), so the
  condition is never even evaluated.
  **Personal verification: CONFIRMED + LIVE.** Bundled samples use
  `test_expression` (10×) and `check_empty` (6×) — their HTML5 exports run
  these branches unconditionally today. (Merges audit findings #1, #2, #3,
  which are one root cause.)
  **Fix:** add the missing question actions to `isConditionalAction`, and
  implement them in `evaluateCondition` (not as `executeAction` stubs):
  `check_empty`/`check_collision` = "is position (x,y[+offset]) free of /
  colliding with solids?" (reuse the `if_collision_at` box logic);
  `test_expression` = evaluate the expression via the same guarded path
  `parseNumParam` uses (bare instance names → `self.*`, `view_*`→0), truthy
  test. Also confirm the IDE runtime's set of test_* names (`test_lives`,
  `test_health`, `test_chance`, `test_question` per audit #3) and cover any
  a sample or common project uses. Regression: a browser/headless check
  that a false question skips its guarded action.

## Medium

- [x] **M1 — `if_collision` / `if_collision_at` ignore sprite origin.**
  FIXED — the condition now routes through the origin-/frame-aware
  `placeMeetsCollision` helper (shared with check_empty) instead of the
  inline raw-position loop. `checkCollisionAt`/`getObjectAt` were already
  origin-correct; the dead `executeAction` `if_collision_at` case is
  unreachable (all `if_*` route through `evaluateCondition`).
  Browser-verified (3/3, centered-origin sprite) + regression test.
  `engine.js` @960 (and the `if_collision_at` executeAction path @1482).
  The collision test builds the probe rect from raw sprite width/height
  without subtracting the sprite origin, so instances whose sprite origin
  is not (0,0) mis-detect collisions (offset by the origin).
  **Personal verification: CONFIRMED.** @960–961 the probe box uses
  `this.x + myW` as the top-left with no origin subtraction, while
  `getBoundingBox()` (used by the main `checkCollisions` event path) does
  `this.x - originX`. So the main collision events are origin-correct but
  the `if_collision` *condition* is off by the origin — wrong for any
  centered-origin sprite (e.g. origin 16,16 on 32×32, the common case).
  **Fix:** route both through `getBoundingBox`/`boxWidth`/`boxHeight`
  (already origin- and frame-aware) instead of raw positions.

- [ ] **M2 — (folded into H1)** `check_empty` / `check_collision` no-ops.
  Same root cause as H1; tracked there.

- [ ] **M3 — (folded into H1)** `test_lives`/`test_health`/`test_chance`/
  `test_question` unrecognized. Same root cause as H1; verify which (if
  any) the runtime defines and samples use, then cover in the H1 fix.

## Low

- [x] **L1 — Project name interpolated unescaped into the exported HTML.**
  FIXED — `html.escape` at the `{game_name}` interpolation (both the
  `<title>` and title `<div>`). The fix also surfaced a related crash: the
  name was used as the output FILENAME too, so a name with `:`/`<>` (legal
  in a project name, illegal on Windows) crashed the export — now sanitized
  via `_sanitize_filename` while the in-page title keeps the real name.
  `tests/test_html5_export_escaping.py`.
  `export/HTML5/html5_exporter.py` @107 (`template_html.replace(
  '{game_name}', project_data['name'])`).
  A project name containing `<`, `&`, or a quote lands unescaped in the
  page `<title>`/heading, corrupting the markup (and in principle injecting
  script). Same threat model the repo has repeatedly weighed for
  self-authored project data (low, not a security boundary — the author
  owns the project), but a legitimate name with an ampersand still renders
  wrong.
  **Personal verification: CONFIRMED** (by inspection — the interpolation
  has no escaping).
  **Fix:** `html.escape` the name at the interpolation site (and audit the
  other `{...}` template substitutions for the same).

---

## Rejected (14)

Fourteen candidates were rejected by the adversarial verification pass
(did not survive refutation). Not re-listed individually — the verifier
notes are in the workflow journal
(`subagents/workflows/wf_f00e794b-ed5/journal.jsonl`) if a specific one
needs revisiting.

## Not covered by this run

The scope was `engine.js` (+ its exporter). The Kivy code generator /
templates, the Android/WSL build pipeline, and the registry were part of
the original full-audit plan but were **not** audited here — a separate
scoped pass (see the prepared full script) still owes them a review.

---

## Kivy / Android / IO pass — INCOMPLETE (2026-07-14)

Second scoped audit (Kivy codegen/templates + Android/WSL pipeline +
registry/IO). **Ran only partially** — the account session limit stopped
it after 2 of 4 finders (`kivy-codegen` and `exporter-io-registry` never
ran) and before any verification/synthesis. The 9 candidates below are
therefore **UNVERIFIED leads** from the `kivy-templates` and
`android-pipeline` finders only, preserved so the work isn't lost.
Coverage gap: the Kivy code generator and the exporter IO/registry were
NOT audited. Re-run after the limit resets (script:
`scratchpad/kivy_android_audit.js`).

### Confirmed by personal code-reading

- [x] **KA-H1 — Kivy room names are not sanitized (invalid Python).**
  `export/Kivy/kivy_exporter.py:3575` (`_get_room_class_name`) + scene
  filename `:1702` + imports `:270`. A room named `level 1` / `1_intro`
  emits `class Level 1(Widget):`, `scenes/level 1.py`, and
  `from scenes.level 1 import ...` — the whole export fails to import.
  Same class as the object-name bug already fixed; rooms were overlooked.
  Not live in a bundled sample (clean room names) but real for
  GMK-imported/user projects. **FIXED** (see below).

### Unverified leads (pending re-audit / personal verification)

- [ ] **KA-M1** `kivy_exporter.py:916` — project name interpolated
  unescaped into a Python string literal in main.py; a quote/backslash
  yields invalid main.py. (Kivy analog of the HTML5 L1.)
- [ ] **KA-M2** `android_exporter.py:629` — WSL cancel/timeout kills
  `wsl.exe` but not the Linux-side buildozer/gradle/gcc processes.
- [ ] **KA-M3** `android_exporter.py:553` — native cancel/timeout kills
  the buildozer parent but orphans child compilers (gradle/gcc/p4a).
- [ ] **KA-L1** `kivy_exporter.py:3592` — object-name sanitization can
  collide two distinct objects onto one module (silent overwrite) or
  produce an empty class name. (Known edge; noted when the sanitizer was
  written.)
- [ ] **KA-L2** `kivy_exporter.py:1001` — Kivy export doesn't clamp room
  dimensions; a 0-width/height room → ZeroDivisionError at Android
  startup (the pygame runtime clamps; Kivy doesn't).
- [ ] **KA-L3** `wsl_bridge.py:346` — `set -e` aborts the WSL build
  script before its self-delete, leaking `/tmp/pygm_buildozer_run.*.sh`
  on every failed build.
- [ ] **KA-L4** `wsl_bridge.py:329` — Windows username interpolated into
  the WSL bash script; a crafted account name (backtick/`$(...)`) enables
  command substitution. (Very low: attacker-controlled local username.)
- [ ] **KA-L5** `wsl_bridge.py:389` — mktemp/tee results unchecked; a full
  or read-only WSL /tmp yields an empty script and a confusing failure.
