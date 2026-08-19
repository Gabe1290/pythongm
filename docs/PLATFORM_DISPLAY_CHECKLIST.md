# Cross-platform display & export checklist

**For: verifying by hand how PyGameMaker looks and behaves on Linux, Windows
and macOS.** Written 2026-08-17, after the twelve-issue eyeball pass.

> `L [ ]` = Linux `M [ ]` = macOS `W [ ]` = Windows
> Tick each box on each machine you check it on. Same convention as
> `docs/test_checklist.md`, which is a different document — that one is the
> exhaustive feature-regression list; this one is about **what you can see**,
> plus the one thing no test can check for you: that an exported game actually
> plays.

---

## Why this exists, and what it is *not*

The twelve issues behind this checklist were all found by a human looking at
the software, and the suite was green through every one of them. Five of them
(issues 4–8) had a single cause: **the exported `.exe` was built from a
different engine than the one the IDE runs**, so nothing the tests covered
applied to it. That is fixed — desktop exports now freeze the real pygame
engine — but the lesson stands: *building* is not *playing*, and a machine
cannot tell you the layout looks wrong.

So this list deliberately skips anything already automated, and spends your
attention on eyes-only checks.

### Run these first — they do the mechanical half for you

From the repo root, on the machine you are checking:

**On Windows, use `py -3.12` for every command.** Bare `python3` there hits the
Microsoft Store stub ("Python was not found") — and if that stub is disabled it
resolves to an unsupported 3.14 instead, which is worse, because it runs and
then fails oddly.

```
:: Windows
py -3.12 -m pytest tests/ -q
py -3.12 tools/smoke_run_samples.py
py -3.12 tools/verify_desktop_export.py --all --compare
```

```
# Linux / macOS
python3 -m pytest tests/ -q
python3 tools/smoke_run_samples.py
python3 tools/verify_desktop_export.py --all --compare
```

`smoke_run_samples.py` drives every sample's real game loop for 180 frames
under SDL's dummy drivers, so it needs no window and takes seconds.

The last one builds a real export **for this platform**, launches it, and
compares its rendering against the IDE's, sample by sample. It takes about a
minute per sample. Any non-zero exit means stop and read the output — you have
found something before spending your own time on it.

Recorded on Windows, 2026-08-17: `5/5 verified`, four samples pixel-identical
to the IDE and plateforme_3 within its own run-to-run noise.

- L [ ] M [ ] W [ ] Full suite passes (any **failure** count is a real
  regression; the skip count is environment-dependent)
- L [ ] M [ ] W [ ] `smoke_run_samples.py` reports no `LOOP-CRASH`
- L [ ] M [ ] W [ ] `verify_desktop_export.py --all --compare` exits 0

---

## 1. The IDE window itself

Nothing here is testable headlessly — it is all about proportion and clipping,
which differ per platform because each has its own default font metrics and
DPI handling.

- L [ ] M [ ] W [ ] IDE launches with no console error, Welcome tab shown
- L [ ] M [ ] W [ ] Window opens at a sensible size; nothing off-screen
- L [ ] M [ ] W [ ] No **clipped or truncated text** in menus, buttons, tab
  labels or the status bar (the usual failure: a translated string longer than
  its English source)
- L [ ] M [ ] W [ ] Asset tree, editor area and properties panel all visible
  without resizing; splitters draggable
- L [ ] M [ ] W [ ] Toolbar icons render (not blank squares or ✕ placeholders)
- L [ ] M [ ] W [ ] Tools → Preferences: every tab's content fits its panel,
  including **Extensions**
- L [ ] M [ ] W [ ] Dark and light theme both legible — no dark-on-dark text
- L [ ] M [ ] W [ ] High-DPI display: text is sharp, not a blurry upscale
  (Windows relies on the DPI manifest for this; macOS deliberately does *not*
  claim Retina support, so a slightly soft game window is expected there)

## 2. Language and accents

**French must carry its accents** — é è ê à ç ù î ô. This is educational
software for French-speaking students; a stripped accent is a defect, not
cosmetics. Missing accents have shipped before, so this is a real check.

- L [ ] M [ ] W [ ] Tools → Preferences → Language lists all **11** entries
  (English plus de es fr it ja pt ru sl uk zh)
- L [ ] M [ ] W [ ] Switch to French: menus, dialogs and the Welcome tab are
  French, with correct accents and **no mojibake** (`Ã©`, `â€"`)
- L [ ] M [ ] W [ ] Welcome tab lists the 2.5 D samples as
  **`2.5 D — Level 1`** … `Level 4` (French: `2.5 D — Niveau 1`). Anything
  longer or more technical is the pre-rename wording (issue 3)
- L [ ] M [ ] W [ ] Spot-check a non-Latin language (日本語 or 中文): glyphs
  render rather than showing boxes — this is a **font availability** question
  and genuinely differs per platform
- L [ ] M [ ] W [ ] Accented characters can be **typed** into a project name,
  object name and a `draw_text` string, and survive save → reopen

## 3. Samples in the IDE (Test Game)

For each sample: open it from the Welcome tab, press Test Game, play far enough
to reach its own goal. Controls responding is the point — several of the twelve
issues were input problems.

- L [ ] M [ ] W [ ] **maze_1** — arrows move; walls block; **all** arrow keys
  keep working after touching a wall (issue 5 was exactly this failing in the
  export)
- L [ ] M [ ] W [ ] **maze_2 / maze_3** — play through
- L [ ] M [ ] W [ ] **maze_4** — starts on Space; finishing the last level
  shows `CONGRATULATIONS` and the following sentence on **two lines**
- L [ ] M [ ] W [ ] **plateforme_1** — jump and land
- L [ ] M [ ] W [ ] **plateforme_2** — **tiles are visible**; Pingus falls, not
  rises; keys do not launch him off the screen (issue 7)
- L [ ] M [ ] W [ ] **plateforme_3** — tiles visible; the bonus objects show
  **different images**, not all image 0; Pingus starts on the ground, not in
  mid-air (issue 8)
- L [ ] M [ ] W [ ] **match3_1**, **match3_2**, **match3_3** — swap, match,
  score
- L [ ] M [ ] W [ ] **views_1** — the window is **800×600 while the room is
  2400×800**, so the camera scrolls as you walk. If you can see the whole room
  at once, the window-sizing fix has regressed (issue 10)
- L [ ] M [ ] W [ ] **views_2** — camera follows
- L [ ] M [ ] W [ ] **2.5 D Level 1–3** — first-person view draws; walls,
  floor, sky, billboard sprites; HUD readable; `M` shows the minimap
- L [ ] M [ ] W [ ] **2.5 D Level 4** — the DOOM status bar renders in the
  bottom band; the **key** and the **gate** look different from each other
  (issue 11 — the gate is now a grey portcullis, the keys gold); collected keys
  appear on the minimap (issue 12); walls block movement (issue 4)
- L [ ] M [ ] W [ ] **block_world_1** — **`H` toggles a 7-line control
  overlay** (issue 9); walls are solid at body height but a one-block step can
  be walked onto; blocks can be placed on top of other blocks; the top face of
  a block is textured like its sides
- L [ ] M [ ] W [ ] **block_world_2** — terrain generates and is walkable
- L [ ] M [ ] W [ ] With the IDE set to **French**, a sample's messages appear
  in French (issue 2 — e.g. 2.5 D Level 4's
  *« La porte est verrouillée. Trouve d'abord toutes les clés ! »*)

## 4. Desktop export — it built **and** it plays

Two separate ticks per target, on purpose. "It built" is what the automated
tests check, and is exactly how five issues shipped.

Export is only possible **on** the platform you are targeting (PyInstaller
cannot cross-compile) and needs `pyinstaller`, `pygame` and `pillow` in the
same Python that runs the IDE.

- L [ ] M [ ] W [ ] Build → the platform's own export completes with no error
- L [ ] M [ ] W [ ] The artifact appears where the dialog said it would
  (single `.exe` on Windows, single binary on Linux, `.app` on macOS)
- L [ ] M [ ] W [ ] **Double-click it.** It opens a window and the game is
  playable, with sound
- L [ ] M [ ] W [ ] Controls behave the same as Test Game did
- L [ ] M [ ] W [ ] No `game_error.log` appears next to the executable (the
  launcher writes one if the game crashed; a frozen game has no console, so
  this file is the only trace)
- L [ ] M [ ] W [ ] A game with a high-score table keeps scores **after
  quitting and relaunching** (`highscores.json` should appear next to the
  executable, not vanish with the bundle)
- L [ ] M [ ] W [ ] Exported from a French IDE, the game's messages are French
- L [ ] M [ ] W [ ] Copy the artifact to **another machine of the same OS**
  with no Python installed, and run it there. This is how a student receives a
  game
- L [ ] &nbsp;&nbsp;&nbsp;&nbsp;&nbsp; Linux: the copied binary is still
  **executable** after travelling via a USB stick (FAT drops the permission
  bit; the exporter restores it on copy, but check it survived)
- &nbsp;&nbsp;&nbsp; M [ ] &nbsp;&nbsp; macOS: the `.app` opens without
  "damaged and can't be opened". Quarantine is stripped at export, but a
  download re-applies it: `xattr -cr /path/App.app` is the fix
- &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp; W [ ] Windows: note whether SmartScreen
  warns ("unknown publisher" is expected for an unsigned build — it should
  still run via *More info → Run anyway*)

## 5. HTML5 export — in a real browser

The priority path: it needs nothing installed and works on a locked-down school
machine. Issue 1 was **every** HTML5 export showing a black window, so check
more than one sample.

- L [ ] M [ ] W [ ] Export a sample to HTML5; a single `.html` file is written
- L [ ] M [ ] W [ ] Open it by **double-clicking** (a `file://` URL) — the game
  draws and plays, no black window
- L [ ] M [ ] W [ ] Open it from a **served** directory
  (`python3 -m http.server`, or `py -3.12 -m http.server` on Windows) —
  same result
- L [ ] M [ ] W [ ] Browser console shows **no** JavaScript error (a syntax
  error in the injected extension code is what caused issue 1, and it broke
  every export at once)
- L [ ] M [ ] W [ ] Repeat for **maze_1** (no extension), **2.5 D Level 4**
  (extension renderer + status bar) and **block_world_1**
- L [ ] M [ ] W [ ] Second browser: Firefox *and* a Chromium-based one
- L [ ] M [ ] W [ ] Keyboard works, including arrows (the page should not
  scroll instead of the player moving)
- L [ ] M [ ] W [ ] Sound plays after the first click (browsers block audio
  until the user interacts)
- L [ ] M [ ] W [ ] Accented text renders in the game canvas

## 6. Mobile (Kivy) — newly repaired, never yet played

Desktop export moved off Kivy, but **Android and iOS still use it**, and its
four known gaps — tiles, keyboard handling, collision, and physics /
sub-images — were all fixed on 2026-08-17. Every fix was verified by executing
the generated code, because Kivy cannot run in CI, so **nobody has actually
played an exported mobile build**. This section is where that gets found out.

Each row names what specifically used to be wrong, so a regression is
recognisable rather than a vague feeling.

- L [ ] M [ ] W [ ] Build → Mobile export produces a project/APK without
  crashing the IDE
- L [ ] M [ ] W [ ] **Tiles are visible** in plateforme_2 and plateforme_3
  (they used to be absent entirely — the tile layer was never exported)
- L [ ] M [ ] W [ ] **The player falls, not rises**, and lands ON the ground
  rather than hovering above it
- L [ ] M [ ] W [ ] **Jump works** — it needs the ground probe below the
  player, which used to check above
- L [ ] M [ ] W [ ] **Walls block** the player, and you can still walk while
  standing on the ground
- L [ ] M [ ] W [ ] **Each arrow moves its own way** — up goes up. All four
  used to move right, and vertical was inverted on top of that
- L [ ] M [ ] W [ ] **maze_4 starts** when you press a key (its start screen
  advances on "any key", which never fired)
- L [ ] M [ ] W [ ] **plateforme_3's bonuses show different pictures**, not all
  the same one
- L [ ] M [ ] W [ ] Anything still wrong: note it here rather than filing it as
  new, and say which of the eight rows above it belongs to

## 7. Per-platform gotchas worth knowing

**Linux** — Debian is what most of the school labs run, so it matters more
than its download count suggests. If a game window fails to open, the SDL
video driver is the first suspect (`SDL_VIDEODRIVER`); Wayland and X11 differ.
Check that the IDE runs on the **distribution's own Python**, not only a venv.

**macOS** — Gatekeeper *silently* kills an unsigned quarantined `.app`:
nothing happens at all on double-click, which reads as "the export is broken".
`xattr -cr` clears it. The `.app` is a directory, so copying it to an exFAT
volume can flatten its symlinks.

**Windows** — the console codepage is cp1252, so run from a terminal at least
once and check that log output is readable rather than encoding errors. Use
`py -3.12`, never bare `python3` (which resolves to an unsupported 3.14 here).

---

## Recording what you find

One line per problem: **platform, sample or screen, what you expected, what you
saw.** A screenshot beats a description for anything about layout. Add them to
a dated `docs/EYEBALL_FIXES_<date>.md` in the same shape as
`docs/EYEBALL_FIXES_2026-08-16.md`, which turned twelve loose observations into
a worked plan.

Two things worth checking twice, because they are the ones automation cannot
reach at all:

1. **Does an exported game feel right to play?** The tests now prove it renders
   the same pixels as the IDE. They do not prove it responds well to a human
   holding a key down.
2. **Does the layout look right at the machine's real resolution?** Every
   automated check runs offscreen at a fixed size.

### Also available

- `docs/test_checklist.md` — the exhaustive feature-regression list (1.0.0)
- `docs/PyGameMaker_Test_Linux.pdf`, `_Windows.pdf`, `_macOS.pdf` — printable
  per-platform PDFs generated by `scripts/generate_platform_test_pdfs.py`
