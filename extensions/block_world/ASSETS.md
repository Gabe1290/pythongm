# Block World — texture asset audit

Phase 0 of `docs/VOXEL_WORLD_PLAN.md`. This file is the provenance record —
every texture file under `textures/` must have a line here before it ships.

## Primary source: Hand Painted Pack Expanded

- **ContentDB listing:** https://content.luanti.org/packages/shaft/hand_painted_expanded/
- **Author:** shaft (current maintainer), originally by Miloslav Číž
  (drummyfish)
- **License:** CC0-1.0, confirmed three ways, not just the ContentDB listing
  text:
  1. `texture_pack.conf` inside the downloaded package states
     "128x128 CC0 (public domain) hand painted cartoony texture pack".
  2. The package ships a full CC0 1.0 Universal legal-code file (copied here
     as `textures/source_hand_painted_expanded/LICENSE_CC0_1.0.txt`).
  3. The package's own `sources.txt` (copied here as
     `textures/source_hand_painted_expanded/upstream_sources.txt`) documents
     per-file upstream provenance for the textures that aren't the authors'
     original work, and every cited source is itself public-domain/CC0
     (opengameart.org CC0 submissions, rawpixel.com "free public domain CC0"
     photos, publicdomainpictures.net, freesvg.org). The maintainers' own
     stated policy in that file: *"The textures are largely my own work, but
     a lot of them are taken out of other CC0 works."* No CC-BY, CC-BY-SA, or
     "all rights reserved" source was found anywhere in that file (checked by
     grep, not just skimmed).
- **Downloaded:** 2026-08-12, via ContentDB's direct package download
  (`https://content.luanti.org/packages/shaft/hand_painted_expanded/download/`),
  14.9 MB zip, 128×128 hand-painted cartoony style, covers all of Minetest
  Game plus many mods.
- **Files imported into this repo:** 32 PNGs, curated subset (not the whole
  14.9 MB pack — most of it is mod-specific art we have no use for: rifles,
  mesecons, cart rails, bed furniture, etc.). See the table below.

### Files imported

All under `textures/source_hand_painted_expanded/`, filenames unchanged from
upstream so they stay traceable back to `upstream_sources.txt` if needed.

| File | Intended use |
|---|---|
| `default_dirt.png` | dirt block |
| `default_grass.png` | grass block, top face |
| `default_grass_side.png` | grass block, side face |
| `default_stone.png` | stone block |
| `default_cobble.png` | cobblestone block |
| `default_sand.png` | sand block |
| `default_desert_sand.png` | desert sand variant |
| `default_sandstone.png` | sandstone block |
| `default_gravel.png` | gravel block |
| `default_clay.png` | clay block |
| `default_tree.png` | log, side face |
| `default_tree_top.png` | log, top/end face |
| `default_wood.png` | wood plank block |
| `default_junglewood.png` | plank variant |
| `default_pine_wood.png` | plank variant |
| `default_leaves.png` | leaves block |
| `default_glass.png` | glass block |
| `default_water_source_animated.png` | water (static use only for now — no animation support planned before Phase 2c) |
| `default_ice.png` | ice block |
| `default_snow.png` | snow block |
| `default_coal_block.png` | coal ore/block |
| `default_gold_block.png` | gold block |
| `default_diamond_block.png` | diamond block |
| `default_brick.png` | brick block |
| `default_obsidian.png` | obsidian block |
| `default_mese_block.png` | glowing/decorative block |
| `wool_red.png`, `wool_blue.png`, `wool_green.png`, `wool_yellow.png`, `wool_white.png`, `wool_black.png` | six solid-color "paint" blocks for building variety |

This is a **starter set**, not the full pack. The source pack has already
been through the licensing audit above, so pulling additional files from the
same downloaded copy later (more wool colors, stairs, doors, etc.) does not
need a new license check — just add a row to this table when a file is
copied in, and keep it in the `source_hand_painted_expanded/` folder so
provenance stays traceable.

## Other CC0 packs evaluated, not used

Recorded so a future session doesn't re-spend time re-evaluating these from
scratch.

| Pack | ContentDB link | License | Verdict |
|---|---|---|---|
| 7px | [ekl/7px](https://content.luanti.org/packages/ekl/7px/) | CC0-1.0 | Rejected — explicitly work-in-progress, only tool textures are complete, most node/block textures still fall back to Minetest Game defaults (not usable standalone). |
| The Pixel Pack | [isaiah658/the_pixel_pack](https://content.luanti.org/packages/isaiah658/the_pixel_pack/) | CC0-1.0 | Backup candidate, not primary. 16px "candy-like" bright style, decent Minetest Game coverage, but reviewers note colors clash without shader support and it wasn't shipped with a `sources.txt`-equivalent per-file provenance file the way Hand Painted Pack Expanded was. Worth a second look if the hand-painted style turns out to read poorly at low res. |
| c64 16px | [wsor4035/c64_16px](https://content.luanti.org/packages/wsor4035/c64_16px/) | CC0-1.0 | Rejected — reviewers report roughly half of default game blocks are unmodified/inconsistent, plus texture-tearing complaints. |
| Dungeon Soup (32px) | via [sirrobzeroone](https://github.com/sirrobzeroone/DungeonSoup) | CC0 (repo states CC0 32x) | Not evaluated in depth — GitHub description says "Initially based off of textures by Dungeon Crawl Stone Soup," which is exactly the kind of "based off of" wording Phase 0 flags as needing a closer per-file check before trusting. Skipped in favor of the already-thoroughly-documented Hand Painted Pack Expanded rather than spending time verifying DCSS's own texture licensing chain. Could be revisited for a dungeon-crawler-style sample later if someone does that verification. |

## Fallback if more block types are needed later

If Phase 5's sample needs a block type not covered by the imported set (e.g.
a specific ore, a door, a stair), prefer pulling it from this same already-
audited pack (checking the file exists and is genuinely covered, not a
default-texture fallback) before sourcing a second pack — that avoids
re-doing a full license audit for one or two files. Only fall back to
drawing original art (per the main plan doc's Phase 0 fallback) if the pack
genuinely doesn't have something needed.
