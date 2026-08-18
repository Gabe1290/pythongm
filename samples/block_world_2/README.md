# Block World — Infinite Terrain

A voxel world with no edges, built on the **Block World** extension's
procedural terrain generation (Tier 7e,
`docs/BLOCK_WORLD_INFINITE_TERRAIN_PLAN.md`). There is no map boundary —
walk in any direction and rolling grass-and-dirt hills keep generating
around you, forever.

**The goal:** there isn't one. This is a sandbox, not a level — walk, dig,
build, and watch your **Distance** score (shown top-left via the
score display) climb as you wander further from where you started. Come
back near your starting point and the terrain there is exactly the same
as when you left — nothing is regenerated once it's been visited.

## Controls

| | |
|---|---|
| `W` `A` `S` `D` | Move (north/south/west/east — see note below) |
| Left / Right arrow | Turn to look left/right |
| Up / Down arrow | Look up/down |
| `Space` | Break the block you're aiming at |
| `Shift` | Place a block from your hotbar |
| `Q` / `E` | Cycle your hotbar selection |

**Movement is map-direction, not look-direction** — the same deliberate
simplification `block_world_1`'s guide explains in full.

## What it demonstrates

- **Procedural terrain, not a hand-built or loaded world.** The room's
  `create` event calls `enable_block_world_view` with `Generate Terrain`
  on and a fixed `Seed` — no `load_block_world` action anywhere in this
  project. Every hill you see was computed on the fly from that one
  number, the moment you got close enough to see it.
- **A world with no memory cost for what you haven't touched.** Walk far
  away and the terrain behind you is quietly forgotten (it isn't lost —
  see below); walk back and it regenerates identically, because it's a
  pure function of the seed and where you are, not something stored.
- **Digging and building still work exactly like `block_world_1`.**
  Break a block out of a generated hillside, or place one — that specific
  edit IS remembered from then on (even for a hill far behind you that
  later gets "forgotten" and later regenerated: your edit reappears
  correctly, only the untouched parts around it regenerate fresh).

## Engine status

**Desktop, HTML5, and Kivy (Android/desktop app export) all generate
real terrain.** One difference between targets, both deliberate and
documented in `docs/BLOCK_WORLD_INFINITE_TERRAIN_PLAN.md`: only the
desktop build forgets far-away untouched terrain to bound memory during a
long play session — the exported HTML5/Kivy builds keep everything
they've generated for the lifetime of that browser tab or app session,
which is intentionally scoped as fine for how long a typical play session
actually runs. Nothing about the terrain itself, or what you can dig and
build, differs between targets.
