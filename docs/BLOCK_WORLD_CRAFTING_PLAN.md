# Block World crafting — Tier 8

Written 2026-09-09, on an explicit ask to plan this out (item 3 of the
session's "still needs resolving" list; `TODO.md`'s inventory work —
Tier 7c, `block_inventory`, a `{block_type: count}` dict on the calling
instance — split crafting out as its own future item on purpose: "smaller
and lower-priority than the other three — write a plan when it's actually
next in line, not speculatively." It's next in line now.

Not started. No code changes yet — this is the plan to work from.

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

- [ ] **Unit 1 — schemas + desktop handlers.** `set_crafting_recipe` +
      `craft_item` in `extensions/block_world/actions.py` (category
      "3D View", icon suggestion: 🛠️/⚗️); `execute_set_crafting_recipe_action`
      + `execute_craft_item_action` in `handlers.py`, storage as above.
      Unit tests drive the handlers directly (same pattern
      `tests/test_block_world_*.py` already uses for protection/reward):
      all-or-nothing consumption, missing-input no-op, Inventory-off
      no-op, overwrite-on-re-register, 1/2/3-input recipes.
- [ ] **Unit 2 — HTML5 + Kivy parity.** Port both actions into
      `export_html5.js` and `export_kivy.py`, mirroring exactly how Tier
      7c's inventory reads/writes (`obj.block_inventory` /
      `getattr(obj, 'block_inventory', None)`) were ported for
      break/place. Extend `tests/test_block_world_export_parity.py` (or a
      sibling) to pin recipe-storage shape and craft-consumption logic
      identically across all three sources, same discipline as the fog
      parity test from `docs/BLOCK_WORLD_PERF_PLAN.md` 1.4 — mutation-test
      each port (a Kivy version that consumes only the first input, an
      HTML5 version that doesn't check Inventory) to prove the parity
      test actually catches drift, not just that it passes once.
- [ ] **Unit 3 — action reference + README.** Re-run
      `tools/gen_action_reference.py` (both new actions need
      `EN_OVERRIDES`/i18n table entries if this extension is still
      French-first anywhere it matters — check
      `extensions/block_world/actions.py`'s existing strings first,
      they read English already, unlike `multiplayer_lan`'s
      French-first gap noted in `TODO.md`). Add a short "Crafting"
      section to `extensions/block_world/README.md` documenting the
      two actions and the three-slot recipe shape.
- [ ] **Unit 4 — decide on sample integration, don't assume it.** Neither
      `block_world_1` nor `block_world_2` is in the Welcome tab (see
      `TODO.md`'s Block World section — deliberately set aside in favour
      of `sky_strike_1`, and `docs/PROJECT_STATUS.md` item 5's
      2026-09-09 update, which chose to stop at Phase 1 of the perf plan
      rather than invest further in either sample). Building crafting
      doesn't require a new flagship sample or reversing that decision —
      recommend shipping this as pure engine capability with handler +
      parity test coverage (Units 1–3) and stopping there, same as the
      perf plan's own conclusion. If a sample is wanted later, that's a
      fresh, explicit ask, not an assumption baked into this plan.

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
