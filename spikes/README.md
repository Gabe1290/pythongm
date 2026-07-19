# Throwaway spikes — raycast floor casting (units 3b / 5b)

These two files exist to answer ONE question before writing the deferred
floor-casting units: **is the desktop low-res floor cast
(`runtime/game_runner._cast_floor_plane`) fast enough to port to HTML5 and
Kivy, and at what `res` downsample factor?** They must be run on real
hardware — the timing can't be measured in the headless test environment,
which is exactly why units 3b/5b were deferred.

Delete this whole `spikes/` directory once the numbers are recorded in
`docs/RAYCAST_2_5D_PLAN.md`.

## What they measure

Both faithfully port the desktop algorithm (camera-plane ray interpolation,
`rowDistance = 0.5·h / (y − horizon)`, texture tiled once per grid cell) and
time the per-frame cost of filling a low-res buffer + uploading/upscaling it,
across `res ∈ {1, 2, 4, 8}`. Defaults match `raycast_1`: 480×480 display,
240-px floor region, 32×32 floor texture.

Decision rule: the floor is **one of ~4 passes per frame** (walls, sky, floor,
billboards), so pick the smallest `res` whose median is comfortably **under
~8 ms** (half a 60 fps frame) — that becomes the export default. If even `res=8`
can't hit budget, the unit ships a **flat `floor_color` fill** on that target
(the documented fallback) and leaves textured floor desktop-only.

## Running

### HTML5 (unit 3b)
Open `floor_cast_html5.html` in the target browser (Chrome/Firefox/Safari — run
it in each you care about) and click **Run benchmark**. Results render in a
table with PASS/FAIL against the 8 ms and 33 ms budgets, plus the UA string.
"Toggle live render" shows the cast animating so you can confirm it looks right,
not just that it's fast.

### Kivy (unit 5b)
On a real desktop with Kivy installed:

```
py -3.12 spikes/floor_cast_kivy.py        # Windows
python3 spikes/floor_cast_kivy.py         # Linux/macOS
```

It opens a Kivy window (needed for a GL context so `Texture.blit_buffer` is
real), prints a table for both a **naive** Python port and a **numpy**
vectorised cast, then quits. If numpy is absent it times naive only.

## Sanity check already done (headless, CPU-only)

The naive cast's CPU-only cost (no GL upload) on the dev box already reproduces
the desktop plan's figures — `res=1 ≈ 64 ms` (unusable), `res=4 ≈ 3.5 ms`,
`res=8 ≈ 1 ms` — confirming the port is faithful. The spikes add the real
`blit_buffer`/`putImageData`+`drawImage` upload cost on top, which is what the
on-hardware run measures.
