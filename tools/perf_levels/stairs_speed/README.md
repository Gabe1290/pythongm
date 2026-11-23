# Stairs speed test level

A hand-test level for the stairs speed test
(`tests/test_raycast_stairs_render.py::test_a_staircase_costs_at_most_a_bit_more_than_a_flat_room`).
It contains the room that test measures, twice:

| Room | Key | Contents |
|---|---|---|
| `salle_escalier` | **S** | 15 × 15 cells, a 5-wide staircase (8, 16, 24, 32 px) up to a 32 px platform |
| `salle_plate` | **F** | the same room without the steps |

Open this folder with **File → Open Project** and press **Test Game**. Arrow keys move and turn.
You start where the test puts its camera, facing the stairs.

The yellow line at the top left shows:

- **ms/image**: the average *work* time per frame over the last 30 frames (update and
  drawing, without the wait that caps the game at 60 frames per second). This is the
  number to compare between the two rooms: the test requires the staircase to cost at
  most 2.5 × the flat room, plus 5 ms (1.6 × until 2026-11-23).
- **i/s**: frames per second (at most 60).

Measured on the dev box (Linux, headless): about 17 ms with the staircase, about 11 ms
without, so ≈ 1.6 ×. On GitHub's CI machines the test measures about 2 ×.

The level is generated from `samples/raycast_5` by `tools/gen_stairs_perf_level.py`; re-run
that script after changing the sample, rather than editing these files by hand.
