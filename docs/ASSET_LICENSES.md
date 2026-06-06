# Asset Licenses

This file records the copyright and license status of the **image, sound, and
other media assets** bundled with PyGameMaker (pygm2).

It is deliberately separate from the project's two code/doc licenses:

- **Source code** → MIT (see [`LICENSE`](../LICENSE)).
- **Documentation** → CC BY 4.0 (see [`LICENSE-docs`](../LICENSE-docs)).

Neither of those covers the bundled game art. The entries below do. Where an
asset is third-party, its own license governs that file — **not** the project's
MIT license.

---

## Platform samples — sprites & backgrounds (Pingus, GPLv3+)

**Scope:** all image files under

- `samples/plateforme_1/`
- `samples/plateforme_2/`
- `samples/plateforme_3/`
- `samples/plateforme_4/`
- `samples/plateforme_5/`

(76 PNGs total — penguin/walker sprites such as `spr_pingus_*`, monsters,
flyers, ladders, blocks, bonuses, markers, and the snow/sky backgrounds.)

**Origin:** these graphics are taken from **Pingus**, the free/libre
Lemmings-style game by Ingo Ruhnke and contributors. They were brought into
these samples via the GameMaker `.gmk` teaching projects (`samples/plateforme_*.gmk`)
and then converted to native pygm2 projects by `importers/gmk_importer.py`.
Some sprites were resized, recoloured, or re-exported in that process, so the
bundled PNGs are **derivative works** of the original Pingus art.

- Project home: https://pingus.seul.org/
- Source repository: https://github.com/Pingus/

**License:** **GNU General Public License, version 3 or later (GPL-3.0-or-later).**
Pingus ships its code *and* its data/artwork under the GPL; there is no separate,
more-permissive asset license upstream. Upstream `LICENSE.txt` contains the
GPLv3 text and its README states "GPLv3+".

**Credited Pingus graphics artists** (from the upstream `AUTHORS` file):

- **Joel Fauche** — most of the pingus (floater, walker, …)
- **Ingo Ruhnke** — lots of gfx (project maintainer)
- **Michael Mestre** — rock tile, weed, traps
- **Craig Timpany** — digger, tumbler, bridger
- **David M. Turner**, **Tom Flavel** — additional gfx
- **Mark Collinson** — title picture

Copyright © the Pingus contributors. Original art © its respective authors above.

### What this means for redistribution (copyleft)

GPL is a **copyleft** license, so these specific files carry obligations that the
MIT-licensed IDE code does not:

1. **These files stay GPLv3+.** Converting/resizing them does not relicense them
   to MIT. They may not be relicensed under MIT or CC.
2. **Bundling is fine (mere aggregation).** Shipping GPL art alongside the
   MIT-licensed pygm2 IDE in the same repository/installer does not make the IDE
   GPL — they are aggregated, not combined into one work.
3. **Anyone redistributing the platform samples** (including a game *exported*
   from one of them) distributes GPL art and must therefore: keep these
   attribution/notice files, include the GPL license text, and make the art's
   source / preferred-editable form available on request, per the GPL.
4. Each `samples/plateforme_*/` folder carries a `CREDITS.txt` so this notice
   travels with the assets when the IDE copies a sample into a user's projects
   folder.

> **Heads-up for the project:** because exporting a platform sample produces a
> game containing GPL art, those exported games inherit GPL obligations for the
> art. If that is undesirable for classroom/redistribution use, the alternative
> is to replace the Pingus sprites with permissively-licensed or original art in
> the shipped samples. Documenting the status (this file) is step one; swapping
> the art would be a separate decision.

---

## Maze samples — sprites & backgrounds

**Status: TODO.** Origin of the image files under `samples/maze_1/`,
`samples/maze_2/`, and `samples/maze_3/` is not yet documented. To be completed
in a follow-up (these were also imported from GameMaker 8.x `.gmk` projects).

---

## Other bundled images (status not yet audited)

- `resources/flags/*.png` — language-selector flag icons (8 files). Source not
  yet recorded; flag *designs* are generally not copyrightable, but the specific
  raster files have no stated provenance.
- `Tutorials/**/*.png` — tutorial thumbnails and lesson art. Source not yet
  recorded.
