# Block World crafting — Tier 8

Written 2026-09-09, on an explicit ask to plan this out (item 3 of the
session's "still needs resolving" list; `TODO.md`'s inventory work —
Tier 7c, `block_inventory`, a `{block_type: count}` dict on the calling
instance — split crafting out as its own future item on purpose: "smaller
and lower-priority than the other three — write a plan when it's actually
next in line, not speculatively." It's next in line now.

**Closed 2026-09-09 — all 4 units done, same day.** `set_crafting_recipe`/
`craft_item` shipped on desktop + HTML5 + Kivy, translated (10 UI
languages + 8 wiki languages), documented, and fully tested (46 new
tests). See the Units section below for the full account, including two
real gaps found and fixed along the way (the `extension.json` manifest
sync, the live-UI i18n guard) and one found and deliberately not chased
(Kivy's pre-existing `set_block_reward` gap, logged in `TODO.md`).

---

## What already exists (read before designing anything new)

Tier 7c shipped real per-block-type counts on top of the fixed hotbar list
(`extensions/block_world/state.py`'s own docstring on `DEFAULT_HOTBAR`):
`break_block` picks a broken block up into `instance.block_inventory`,
`place_block` consumes from it, both opt-in via `enable_block_world_view`'s
`inventory` parameter (off by default = old unlimited creative placing,
unchanged). Two more register-once-per-type actions already sit on top of
that inventory, and are the direct template for crafting's own action:

- `set_block_protection(block_type, required_key)` — a tool/key gate on
  `break_block`.
- `set_block_reward(block_type, points)` — score on `break_block`.

Both store their registration on the room's camera config
(`peek_camera(room)`, from `enable_block_world_view`), keyed by
`block_type`, e.g. `cfg.setdefault("rewards", {})[block_type] = points`
(`extensions/block_world/handlers.py`). Both are desktop + HTML5 + Kivy
already. Crafting reuses this exact shape.

The block registry (`state.py`'s `BLOCK_TYPES`, ~26 entries: dirt, stone,
the wood/wool/ore families, glass, water, ice, snow, obsidian…) has **no
separate "item" concept** — everything craftable or breakable is a block
type. That constrains the whole design below: crafting stays "N blocks in,
M blocks out," not a new inventory-of-tools system.

---

## Design decisions

Each one is a deliberate cut to keep this a Tier-7c-sized feature, not a
Minecraft crafting-grid rewrite. State the trade-off, don't rediscover it
mid-implementation.

1. **Outputs are block types, not a new "item" asset type.** A crafted
   result goes into the same `block_inventory` dict `break_block` fills.
   No new asset category, no new HUD concept, no icon system beyond the
   block textures already in `extensions/block_world/textures/`. This is
   the single biggest scope cut — it's what keeps crafting an extension of
   Tier 7c instead of a parallel system next to it.
2. **One new action registers a recipe, one new action attempts it** —
   mirroring `set_block_protection`/`set_block_reward` exactly:
   - `set_crafting_recipe(output, output_count, input_1, input_1_count,
     input_2, input_2_count, input_3, input_3_count)` — call once per
     output type (room's create event, right after
     `enable_block_world_view`, same convention as protection/reward).
     **Three fixed input slots**, 2nd/3rd optional (blank = unused) — GM
     action-editor-friendly (dropdown + number pairs, no free-form JSON),
     matching how every other Block World action favours fixed typed
     params over a generic dict. Three slots covers the plan's own worked
     examples (stone+stone→brick is 1 slot; a simple "3 wood_log →
     4 wood_plank" is 1 slot; a torch-style "1 coal_block + 1 wood_log →
     N" is 2) without inventing a scrollable ingredient list.
   - `craft_item(output)` — looks up the recipe registered for `output`,
     checks every required input is present in `instance.block_inventory`
     in sufficient count, and if so consumes them all and adds
     `output_count` of `output`. **All-or-nothing**: a recipe needing 2
     inputs never partially consumes one and fails the other. Silent
     no-op if the recipe doesn't exist, Inventory is off, or any input is
     short — same "holding the build key against a wall is ordinary play"
     precedent `place_block`/`break_block` already established, not an
     error.
3. **No crafting-table proximity, no recipe discovery/unlock progression,
   no shaped (3×3 grid) recipes.** `craft_item` works anywhere, any time,
   same as `break_block`/`place_block` do. A project author who wants
   "near a table" gating can already build it themselves with
   `test_instance_count`/`check_collision` against a table object — that's
   ordinary GameMaker-style authoring, not something the extension needs
   to own.
4. **No dedicated crafting-grid UI.** `craft_item` is an action a project
   binds to a key (or a button `obj_hud` reacts to), the same way
   `set_block_reward` has no UI of its own — score changes, the project
   author decides how to show it. A future `draw_crafting_hud` (mirroring
   `draw_block_world_hud`'s hotbar) is a plausible follow-up, not part of
   this plan: build it only once a real sample author asks for a way to
   browse known recipes, per this repo's own "ship the MVP, don't
   speculate" pattern (see `docs/BLOCK_WORLD_PERF_PLAN.md`'s Phase-2/3
   gating for the same discipline applied to a different Tier).
5. **Requires Inventory on**, same as `break_block`'s pickup /
   `place_block`'s consumption — without it there's no
   `instance.block_inventory` to craft from or into, so `craft_item` is a
   guaranteed no-op. Document this the same way `set_block_protection`'s
   own docstring already warns about the equivalent case, don't silently
   special-case it.
6. **No new export machinery.** This is Tier 8, reusing Tier 7c's
   inventory shape verbatim on all three targets — no new state.py
   storage layer, no new renderer hook, no new HUD compositing pass. Only
   two actions + their handlers, ported the same way protection/reward
   were.
7. **Multiplayer**: nothing extra to build. `block_inventory` is plain
   instance state; `extensions/multiplayer_lan`'s Tier B already
   replicates arbitrary instance vars for an owned/synced instance
   (`docs/MULTIPLAYER_LAN_V2_PLAN.md`). If a networked Block World project
   ever exists, crafting rides along for free — not verified here (no
   sample combines the two extensions today), just noted so nobody
   re-derives it as an open question later.

---

## Recipe storage (exact shape, so units 1–2 don't diverge)

On the room's camera config (`peek_camera(room)`, same object protection/
rewards already live on):

```python
cfg["recipes"] = {
    "brick": {  # output block type
        "output_count": 4,
        "inputs": [("clay", 4)],  # up to 3 (type, count) pairs
    },
    ...
}
```

`set_crafting_recipe` builds this from its five-or-seven fixed params
(drop any input slot whose type is blank); `craft_item` reads it. One call
overwrites any previous recipe for that output, matching
`set_block_reward`'s "each call adds/overwrites one entry" convention.

---

## Units

Small enough for one session, one commit per unit, full-suite gate after
each — the standard workflow this repo uses for every Block World Tier.

- [x] **Unit 1 — schemas + desktop handlers. DONE.** `set_crafting_recipe` +
      `craft_item` added to `extensions/block_world/actions.py` (category
      "3D View", icons 🛠️/⚗️ as suggested) and
      `execute_set_crafting_recipe_action` + `execute_craft_item_action`
      to `handlers.py`, storage exactly as designed above
      (`cfg["recipes"][output] = {"output_count": N, "inputs": [(type,
      count), ...]}`). A new module-level `_valid_input_slot` helper
      (mirroring `_truthy`'s shape) validates one input slot's
      `(block_type, count)` pair; `input_1` is required (blank/unknown/
      non-positive there aborts the whole registration), `input_2`/
      `input_3` are independently well-formed-or-skipped, matching design
      decision 2 exactly — a blank slot 2 with a valid slot 3 still
      registers a 2-input recipe.
      **Real gap the new tests caught, not anticipated in this plan**:
      `extensions/block_world/extension.json`'s `provides_actions` list
      is a separate, hand-maintained manifest from `PLUGIN_ACTIONS` —
      `tests/test_block_world_state.py::test_manifest_provides_actions_matches_the_real_actions`
      failed the moment the two new actions existed in one but not the
      other. Added both to the manifest; every other Block World action
      unit apparently remembered this, this one almost didn't.
      `tests/test_block_world_crafting.py` (22 tests): recipe
      registration (1/2/3-input, blank-slot skipping, missing/unknown/
      non-positive required vs. optional slots, multi-output
      accumulation, overwrite-on-re-register, view-disabled no-op) and
      `craft_item` (successful craft, 2- and 3-input consumption,
      all-or-nothing short-input no-op, output count accumulating onto
      an existing stack, no-recipe no-op, Inventory-off no-op,
      view-disabled no-op). Full `block_world`-keyed suite green (677
      passed).
      **Second real gap, bigger than the manifest one, pulled forward
      from Unit 3 rather than deferred**: `tests/test_extension_action_i18n.py`
      (a repo-wide guard, not Block-World-specific) failed the full-suite
      gate the moment the two actions existed — its own count assertion
      (37→39) and, more substantially,
      `test_every_extension_action_name_resolves` for all 10 shipped
      languages, since neither action's `display_name` had a catalogue
      entry yet. This is exactly the class of bug the LAN multiplayer
      extension shipped with originally (a new extension action landing
      un-translated) — the test exists specifically to catch it before a
      commit lands, not after. Rather than defer to Unit 3 and land Unit 1
      with a known-red suite, translated "Set Crafting Recipe"/
      "Craft Item" into all 10 shipped languages (de/es/fr/it/ja/pt/ru/sl/
      uk/zh) in both Qt contexts the action palette and configure dialog
      use (`ObjectEventsPanel`, `ActionConfigDialog`) via a one-off script
      (same category as the 2026-08-10 Extensions-tab i18n fix's own
      throwaway tool) that inserts `<message>` blocks into the right
      split-vs-monolithic `.ts` file per this repo's documented convention,
      recompiled with `scripts/compile_translations.py`, and live-verified
      all 40 resolutions (10 languages × 2 actions × 2 contexts) through a
      real `QTranslator`, not just presence in the `.ts`. Vocabulary
      leaned on established Minecraft localization terms where memory of
      one existed (zh "合成配方"/"合成", ja "クラフト"/"レシピ", ru/uk
      "крафт"/"скрафтити"), matching the style of existing block-world
      action translations ("Set X" → "X festlegen"/"Definir X"/etc.)
      elsewhere. Test count bumped 37→39 in the same commit.
      **Unrelated pre-existing environment artifact found and cleared en
      route, not caused by this work**: a stray `runtime/action_handlers/
      __pycache__` directory (compiled bytecode surviving the real
      package's deletion in `f3dabc8a`, confirmed git-untracked) tripped
      `tests/test_action_handlers_package_retired.py::test_the_package_is_gone`
      on the full-suite gate. Removed by hand (outside the agent's
      permitted operations) before the gate could go green.
      Full suite: **4,668 passed, 0 failed, 10 skipped** — clean, no
      flakes.
- [x] **Unit 2 — HTML5 + Kivy parity. DONE (2026-09-09).** Both actions
      ported, mirroring the `set_block_protection` precedent (the closest
      structural match — register-once-per-type on the camera config) on
      both targets:
      - **HTML5** (`export_html5.js`): `registerExtensionAction`
        entries for `set_crafting_recipe`/`craft_item`, plus a shared
        `bwCraftingSlot(typeVal, countVal, obj, game)` helper (mirrors
        `handlers._valid_input_slot`) so `input_1`'s required-vs-
        `input_2`/`input_3`'s optional validation can't silently drift
        apart between slots.
      - **Kivy** (`export_kivy.py`): `_bw_crafting_slot`/
        `_bw_set_crafting_recipe`/`_bw_craft_item` scene methods (SCENE_CODE
        — literal braces, not `.format()`-doubled, confirmed against the
        existing `cfg.setdefault('protection', {})` precedent already in
        that string) + `_cg_set_crafting_recipe`/`_cg_craft_item` codegen
        functions (using `_tofloat` at codegen time, matching
        `_cg_place_block`'s `reach` handling, since these are compile-time
        literal params, not runtime expressions) + both registered in
        `ACTION_CODEGEN`.
      `tests/test_kivy_block_world_crafting.py` (15 tests: codegen strings,
      a compile-check that the generated scene source is valid Python, and
      real execution against `_blank_scene` covering the same scenarios as
      the desktop tests) and `tests/test_html5_block_world_crafting.py`
      (7 tests: source-structural, no JS engine in CI, matching this
      extension's established tier for HTML5).
      **`tests/test_block_world_crafting_export_parity.py`** (9 tests, a
      sibling file rather than extending `test_block_world_export_parity.py`
      — that file is specifically DDA/render-math parity, a different shape
      of check than crafting's plain dict/count logic): feeds identical
      recipe-registration and craft-attempt calls to desktop's real
      `PluginExecutor` handlers and Kivy's real `_bw_*` scene methods via
      `_blank_scene`, asserting byte-identical resulting state across 4
      scenarios (single/two/three-input, blank-slot-2-with-valid-slot-3)
      plus an explicit all-or-nothing short-input case.
      **Mutation-tested for real, not just asserted to exist**: temporarily
      changed Kivy's `_bw_craft_item` to consume only the first input (the
      plan's own suggested mutation) — 3 of 4 multi-input parity scenarios
      failed exactly as expected (the single-input one is unaffected by
      construction), confirming the parity test actually catches drift.
      Separately, temporarily dropped HTML5's `cfg.inventory` check —
      `test_craft_item_checks_inventory_flag_and_recipe_presence` failed
      exactly as expected. Both mutations reverted immediately after
      (`git diff --stat` confirmed pure additions, no residual change).
      Also extended `tests/test_export_block_world_ownership.py`'s
      existing (partial, not-fully-exhaustive) action-name lists to
      include the two new actions, so a future regression re-inlining
      crafting code into a core export engine would trip there too.
      **Real, unrelated pre-existing gap found and logged, not fixed
      (out of this plan's scope)**: Kivy has NO `set_block_reward`
      port at all (Tier 7b's mine-to-collect payout) — missing both
      scene method and codegen entry, with no test file to have caught
      it (`tests/test_kivy_block_world_reward.py` doesn't exist). Logged
      in `TODO.md`'s Block World section with the fix shape, not chased
      here.
      Full `block_world`-keyed suite: 708 passed (677 → 708, +31 across
      the three new test files). Full suite: **4,699 passed, 0 failed,
      10 skipped** — clean, no flakes.
- [x] **Unit 3 — action reference + README. DONE (2026-09-09).**
      Confirmed (not assumed) `extensions/block_world/actions.py`'s
      strings read English already — no `EN_OVERRIDES` entries needed for
      the English wiki edition, unlike `multiplayer_lan`'s French-first
      gap. Added `set_crafting_recipe`/`craft_item` `{"display", "desc"}`
      entries to `tools/action_ref_i18n.py`'s `ACTIONS_<LANG>` tables for
      all 8 wiki languages (fr/de/uk/ru/it/es/pt/sl — matching Unit 1's
      note that ja/zh have no wiki translation yet), via a one-off
      insertion script (same category as Unit 1's translation-catalogue
      script — mechanical, not hand-edited XML/dict surgery). Display
      names reused verbatim from Unit 1's own `.ts` translations (same
      source string, same target audience); descriptions newly
      translated, matching the phrasing/quoting conventions
      (`«…»`/`„…"`/`»…«` per language) `set_block_reward`'s own entries
      already established. Re-ran `tools/gen_action_reference.py` for
      English + all 8 languages: **159 → 161 actions**, zero missing
      `action.display`/`action.desc` entries for either new action in any
      language (verified from the tool's own missing-string report, not
      assumed) — the only fallbacks-to-English left are the two new
      actions' 8 PARAMETER notes (`"Which block type this recipe
      produces"` and its 7 siblings), deliberately left to the tool's own
      documented graceful-fallback-with-report mechanism rather than
      translating another ~64 short param-note entries, matching two
      genuinely pre-existing fallbacks (fog-related notes) already
      present before this change — translating every parameter note was
      never this plan's ask, just the action-level display/description.
      Regenerated `wiki/*.md` (126 files touched — every page's shared
      category-count sidebar shifts 159→161 / 16→18 for 3D View, plus the
      3D-View pages' own new content; `git diff` confirms no other
      content moved).
      Added a "Crafting (Tier 8)" section to
      `extensions/block_world/README.md` documenting both actions and the
      three-slot recipe shape, matching the file's existing per-feature
      section style. **Found the surrounding README's "Status" line,
      feature table, and "What's not here yet" list are stale well past
      Tier 7/8** (still claiming "no hotbar action, no collision, no
      gravity," no samples, no export parity — all long since shipped) —
      logged as an explicit callout rather than silently writing new,
      accurate content next to old, false claims, and fixed only the
      specific "What's not here yet" bullets that would have directly
      contradicted the new Crafting section (replaced with Tier 8's own
      real scope cuts and the `set_block_reward`-on-Kivy gap from Unit 2).
      A full README modernization pass is explicitly **not** part of this
      plan and wasn't attempted.
- [x] **Unit 4 — decide on sample integration, don't assume it. DECIDED
      (2026-09-09): stop here, no new sample.** Neither `block_world_1`
      nor `block_world_2` is in the Welcome tab (see `TODO.md`'s Block
      World section — deliberately set aside in favour of `sky_strike_1`,
      and `docs/PROJECT_STATUS.md` item 5's 2026-09-09 update, which
      chose to stop at Phase 1 of the perf plan rather than invest
      further in either sample). Building crafting doesn't require a new
      flagship sample or reversing that decision, so Units 1–3 (handler +
      export parity + docs coverage) ship as pure engine capability and
      Tier 8 stops there — matching the perf plan's own conclusion. This
      was this plan's own default recommendation, carried out rather than
      revisited. If a sample is wanted later, that's a fresh, explicit
      ask, not an assumption baked into this plan.

**All four units are now done. `docs/BLOCK_WORLD_CRAFTING_PLAN.md` is
closed** — `set_crafting_recipe`/`craft_item` are real, tested (46 new
tests across desktop/HTML5/Kivy/cross-engine-parity), exported to all
three targets, translated into 10 UI languages + 8 wiki languages, and
documented in the extension's own README. No further work is implied by
this plan; anything found along the way and deliberately not chased (the
Kivy `set_block_reward` gap) is tracked in `TODO.md` instead.

## Explicitly out of scope (don't re-propose without a fresh ask)

- Tool durability / tiers (wooden vs. stone vs. iron pickaxe-style
  gating) — `set_block_protection`'s tool/key is a possess-check, not a
  consumable, and crafting doesn't change that.
- Shaped (3×3 grid, position-sensitive) recipes — shapeless, fixed-slot
  only (design decision 2).
- A new "item" asset type distinct from blocks (design decision 1).
- Crafting-table proximity gating (design decision 3) — buildable by a
  project author with existing actions if they want it.
- A dedicated crafting-browser HUD (design decision 4).
- Recipe unlock/progression systems.

## How to pick this up

Read design decisions 1–7 above before writing any code — they're the
whole reason this stayed small in the plan; re-deriving them mid-
implementation is how a "smaller and lower-priority" item turns into
another `docs/BLOCK_WORLD_INFINITE_TERRAIN_PLAN.md`-sized effort. Unit 1
first (desktop-only, real feature, real tests); Units 2–3 are the export-
parity and docs follow-through every Block World action needs before it's
"done," not optional polish. Unit 4 is a decision to write down, not code
to write, unless a fresh ask changes it.
